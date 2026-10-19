"""Event-gated scheduling against temporary SQLite, with actual repository commits."""
import asyncio
import json
from dataclasses import replace
from types import SimpleNamespace

import pytest
import pytest_asyncio
from sqlalchemy import text
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from app.context.tokens import ESTIMATOR_VERSION
from app.context.types import ContextBudget
from app.repositories.context import ContextRepository
from tests.test_context_summarizer import ReplyModel, settings


def budget(**changes):
    values = dict(window=12000, phases={}, desired=6000, history=6000, layer1=4200,
                  layer2=10, evidence=1000, summary=1000, safety=360, estimator_version=ESTIMATOR_VERSION)
    values.update(changes)
    return ContextBudget(**values)


@pytest_asyncio.fixture
async def repository(tmp_path):
    engine = create_async_engine('sqlite+aiosqlite:///' + (tmp_path/'context.sqlite').as_posix())
    async with engine.begin() as connection:
        for ddl in (
            "CREATE TABLE conversations (id INTEGER PRIMARY KEY,user_id TEXT NOT NULL,status TEXT DEFAULT '进行中',summary TEXT,summary_upto_msg_id INTEGER,layer1_from_msg_id INTEGER,created_at DATETIME DEFAULT CURRENT_TIMESTAMP,updated_at DATETIME DEFAULT CURRENT_TIMESTAMP)",
            "CREATE TABLE messages (id INTEGER PRIMARY KEY,conversation_id INTEGER NOT NULL,role TEXT,content TEXT,tool_calls JSON,tool_call_id TEXT,created_at DATETIME DEFAULT CURRENT_TIMESTAMP)",
            "CREATE TABLE conversation_summaries (id INTEGER PRIMARY KEY AUTOINCREMENT,conversation_id INTEGER NOT NULL,seq INTEGER,from_msg_id INTEGER,upto_msg_id INTEGER,content TEXT,created_at DATETIME DEFAULT CURRENT_TIMESTAMP,UNIQUE(conversation_id,seq))",
        ):
            await connection.execute(text(ddl))
    repo = ContextRepository(SimpleNamespace(session=async_sessionmaker(engine, expire_on_commit=False)))
    yield repo
    await engine.dispose()


async def seed(repo, identifiers=(1,), *, turns=1, size=0, downgraded=True):
    async with repo.database.session() as session, session.begin():
        for identifier in identifiers:
            base = identifier*100
            await session.execute(text('INSERT INTO conversations (id,user_id,layer1_from_msg_id) VALUES (:id,\'test\',:l)'),
                                  {'id':identifier,'l':base+turns*2 if downgraded else None})
            for turn in range(turns):
                await session.execute(text('INSERT INTO messages (id,conversation_id,role,content) VALUES (:id,:cid,:role,:content)'),
                    [{'id':base+turn*2+1,'cid':identifier,'role':'user','content':f'订单 O-{identifier} 的包裹未找到。'+'补充说明'*size},
                     {'id':base+turn*2+2,'cid':identifier,'role':'assistant','content':'请等待核实。'}])


class Events:
    def __init__(self):
        self.items = []
        self.changed = asyncio.Event()

    def __call__(self, name, fields):
        self.items.append((name, fields))
        self.changed.set()

    async def wait(self, name, count=1):
        async with asyncio.timeout(5):
            while sum(event == name for event, _ in self.items) < count:
                self.changed.clear()
                await self.changed.wait()


class GatedGenerator:
    def __init__(self):
        self.entered = Events()
        self.release = asyncio.Event()
        self.active = self.maximum = 0
        self.batches = []
        self.cancelled = asyncio.Event()

    async def summarize(self, batch):
        self.batches.append(batch)
        self.active += 1
        self.maximum = max(self.maximum, self.active)
        self.entered('entered', {})
        try:
            await self.release.wait()
            return f'订单 O-{batch.conversation_id} 的包裹未找到。'
        except asyncio.CancelledError:
            self.cancelled.set()
            raise
        finally:
            self.active -= 1


async def test_event_blocked_summary_does_not_block_caller(repository):
    from app.context.manager import SummaryManager
    await seed(repository)
    generator, events = GatedGenerator(), Events()
    manager = SummaryManager(repository, generator, budget_provider=budget, event_logger=events)
    reply_done = asyncio.Event()
    assert manager.notify('1', layer2_tokens=100, budget=budget()) is True
    reply_done.set()  # Ordinary reply is not awaiting the background generator.
    await generator.entered.wait('entered')
    assert reply_done.is_set() and not generator.release.is_set()
    # A separate DB transaction can proceed while the model remains gated.
    async with repository.database.session() as session, session.begin():
        await session.execute(text("UPDATE conversations SET status='已结束' WHERE id=1"))
    assert (await repository.load('1'))[0].summary_upto is None
    generator.release.set()
    await events.wait('summary_done')
    await manager.aclose()
    assert (await repository.load('1'))[0].summary_upto == 102


async def test_isolated_background_task_does_not_inherit_request_callbacks(repository):
    from langchain_core.runnables.config import var_child_runnable_config
    from app.context.manager import SummaryManager
    await seed(repository)
    seen = []

    class Generator:
        async def summarize(self, batch):
            seen.append(var_child_runnable_config.get())
            return '订单 O-1 的包裹未找到。'

    events = Events()
    manager = SummaryManager(repository, Generator(), budget_provider=budget,
        event_logger=events, isolate_task_context=True)
    token = var_child_runnable_config.set({'metadata': {'request_marker': 'must-not-inherit'}})
    try:
        assert manager.notify('1', layer2_tokens=100, budget=budget())
        await events.wait('summary_done')
        assert seen == [None]
    finally:
        var_child_runnable_config.reset(token)
        await manager.aclose()


async def test_two_running_eight_waiting_one_per_conversation(repository):
    from app.context.manager import SummaryManager
    await seed(repository, range(1,12))
    generator, events = GatedGenerator(), Events()
    manager = SummaryManager(repository, generator, budget_provider=budget, event_logger=events)
    assert all(manager.notify(str(i), layer2_tokens=100, budget=budget()) for i in range(1,11))
    assert not manager.notify('11', layer2_tokens=100, budget=budget())
    assert not manager.notify('1', layer2_tokens=100, budget=budget())
    assert not any(event == 'summary_trigger' for event, _ in events.items)
    await generator.entered.wait('entered', 2)
    assert generator.maximum == 2 and len(generator.batches) == 2
    assert max(fields['waiting'] for _, fields in events.items) == 8
    triggers = [fields for event, fields in events.items if event == 'summary_trigger']
    assert {(item['conversation_id'], item['from_msg_id'], item['upto_msg_id'], item['target_l']) for item in triggers} == {
        ('1','101','102','102'), ('2','201','202','202')}
    generator.release.set()
    await events.wait('summary_done', 10)
    await manager.aclose()
    assert generator.maximum == 2
    assert {batch.conversation_id for batch in generator.batches} == {str(i) for i in range(1,11)}
    assert (await repository.load('11'))[0].summary_upto is None


@pytest.mark.parametrize('response', ['bad json', '{"content":"订单 O-999 的包裹未找到。"}', json.dumps({'content':'甲'*201})])
async def test_invalid_json_entities_or_length_does_not_advance(repository, response):
    from app.context.manager import SummaryManager
    from app.context.summarizer import SummaryGenerator
    await seed(repository)
    before = await repository.load('1')
    model, events = ReplyModel(response), Events()
    manager = SummaryManager(repository, SummaryGenerator(model, settings()), budget_provider=budget, event_logger=events)
    manager.notify('1', layer2_tokens=100, budget=budget())
    await events.wait('summary_failed')
    await manager.aclose()
    assert await repository.load('1') == before
    assert len(model.calls) == 1


async def test_boundary_conflict_and_restart(repository):
    from app.context.manager import SummaryManager
    await seed(repository, (1,), turns=2)
    await seed(repository, (2,), downgraded=False)
    generator, events = GatedGenerator(), Events()
    manager = SummaryManager(repository, generator, budget_provider=budget, event_logger=events)
    manager.notify('1', layer2_tokens=100, budget=budget())
    await generator.entered.wait('entered')
    contender = await repository.load_batch('1', target_upto=102)
    await repository.append_segment(contender, '订单 O-1 的包裹未找到。', summary_budget=1000)
    generator.release.set()
    await events.wait('summary_skipped')
    await manager.aclose()
    anchors, old = await repository.load('1')
    assert anchors.summary_upto == 102 and len(old) == 1
    next_generator, next_events = GatedGenerator(), Events()
    restarted = SummaryManager(repository, next_generator, budget_provider=budget, event_logger=next_events)
    await restarted.startup()  # Must return while a model call is gated.
    await next_generator.entered.wait('entered')
    assert not next_generator.release.is_set()
    assert [(b.from_msg_id,b.upto_msg_id) for b in next_generator.batches] == [(103,104)]
    next_generator.release.set()
    await next_events.wait('summary_done')
    await restarted.aclose()
    anchors, segments = await repository.load('1')
    assert anchors.summary_upto == 104 and segments[0] == old[0] and len(segments) == 2
    assert (await repository.load('2'))[0].summary_upto is None


async def test_frozen_target_splits_contiguous_complete_raw_turns(repository):
    from app.context.manager import SummaryManager
    from app.context.summarizer import SUMMARY_OUTPUT_TOKENS, summary_input_tokens
    await seed(repository, turns=3, size=180)
    generator, events = GatedGenerator(), Events()
    manager = SummaryManager(repository, generator, budget_provider=budget, event_logger=events)
    # Derive capacity from the real model view; prompt size and projection may
    # change, while the complete raw turns and their SQL coverage stay fixed.
    one_turn = await repository.load_batch('1', target_upto=102)
    two_turns = await repository.load_batch('1', target_upto=104)
    limited = budget(window=summary_input_tokens(one_turn) + SUMMARY_OUTPUT_TOKENS + 256, safety=256)
    assert summary_input_tokens(two_turns) + SUMMARY_OUTPUT_TOKENS + limited.safety > limited.window
    manager.notify('1', layer2_tokens=5000, budget=limited)
    await generator.entered.wait('entered')
    async with repository.database.session() as session, session.begin():
        await session.execute(text("INSERT INTO messages (id,conversation_id,role,content) VALUES (107,1,'user','后续消息'),(108,1,'assistant','后续答复')"))
        await session.execute(text('UPDATE conversations SET layer1_from_msg_id=108 WHERE id=1'))
    generator.release.set()
    await events.wait('summary_done', 3)
    await manager.aclose()
    assert [(b.from_msg_id,b.upto_msg_id) for b in generator.batches] == [(101,102),(103,104),(105,106)]
    assert all(len(b.source_rows) == 2 and '补充说明'*180 in b.source_rows[0].content for b in generator.batches)
    anchors, segments = await repository.load('1')
    assert (anchors.summary_upto, anchors.layer1_from) == (106,108)
    assert [s.seq for s in segments] == [1,2,3]
    completions = [fields for event,fields in events.items if event == 'summary_done']
    assert [(item['seq'],item['from_msg_id'],item['upto_msg_id']) for item in completions] == [(1,'101','102'),(2,'103','104'),(3,'105','106')]
    triggers = [fields for event,fields in events.items if event == 'summary_trigger']
    assert len(triggers) == 1 and triggers[0]['upto_msg_id'] == '106' and triggers[0]['target_l'] == '106'


@pytest.mark.parametrize('answer', ['您好', '您好！有什么可以帮您的吗？'])
async def test_empty_greeting_segment_covers_range_and_is_not_recovered_again(repository, answer):
    from app.context.manager import SummaryManager
    from app.context.summarizer import SummaryGenerator
    await seed(repository)
    async with repository.database.session() as session, session.begin():
        await session.execute(text("UPDATE messages SET content=CASE role WHEN 'user' THEN '你好' ELSE :answer END WHERE conversation_id=1"), {'answer':answer})
    model, events = ReplyModel('{"content":""}'), Events()
    manager = SummaryManager(repository, SummaryGenerator(model, settings()), budget_provider=budget, event_logger=events)
    manager.notify('1', layer2_tokens=100, budget=budget())
    try:
        await events.wait('summary_done')
    finally:
        await manager.aclose()
    anchors, segments = await repository.load('1')
    assert anchors.summary_upto == 102 and len(segments) == 1 and segments[0].content == ''
    restarted = SummaryManager(repository, SummaryGenerator(model, settings()), budget_provider=budget)
    await restarted.startup()
    await restarted.aclose()
    assert len(model.calls) == 1


@pytest.mark.parametrize('separate_turns', [False, True])
async def test_explicit_distinct_orders_commit_without_ambiguity_marker(repository, separate_turns):
    from app.context.manager import SummaryManager
    from app.context.summarizer import SummaryGenerator
    await seed(repository, turns=2 if separate_turns else 1)
    async with repository.database.session() as session, session.begin():
        await session.execute(text('UPDATE messages SET content=:content WHERE id=101'),
            {'content':'请查订单 O-101 的物流。' if separate_turns else '请查订单 O-101 的物流；另外订单 O-202 我要申请退款。'})
        await session.execute(text('UPDATE messages SET content=:content WHERE id=103'),
            {'content':'订单 O-202 我要申请退款。'})
    expected = '用户查询订单 O-101 的物流，另希望针对订单 O-202 申请退款；两项诉求分别对应已明确的订单，物流和退款均尚无处理结果。'
    model, events = ReplyModel(json.dumps({'content':expected}, ensure_ascii=False)), Events()
    manager = SummaryManager(repository, SummaryGenerator(model, settings()), budget_provider=budget, event_logger=events)
    manager.notify('1', layer2_tokens=100, budget=budget())
    try:
        await events.wait('summary_done')
    finally:
        await manager.aclose()
    anchors, segments = await repository.load('1')
    assert anchors.summary_upto == (104 if separate_turns else 102)
    assert len(segments) == 1 and segments[0].from_msg_id == 101 and segments[0].content == expected
    assert len(model.calls) == 1


@pytest.mark.parametrize('explicit_selection,tentative_selection', [(False, False), (True, False), (False, True)])
async def test_cross_turn_uncertainty_only_commits_after_source_selection(repository, explicit_selection, tentative_selection):
    from app.context.manager import SummaryManager
    from app.context.summarizer import SummaryGenerator
    await seed(repository, turns=3 if explicit_selection else 2)
    async with repository.database.session() as session, session.begin():
        await session.execute(text('UPDATE messages SET content=:content WHERE id=:id'), [
            {'id':101,'content':'订单 O-101 和 O-202 都买过，帮我看看那个到哪里了。' if tentative_selection else '订单 O-101 和 O-202 都买过。'},
            {'id':102,'content':'请问需要查询哪一单？'},
            {'id':103,'content':'可能就是订单 O-101。' if tentative_selection else '帮我看看那个到哪里了。'},
            {'id':104,'content':'请确认具体订单。'},
            {'id':105,'content':'我选择订单 O-101，请查这单物流。'},
            {'id':106,'content':'会按您选定的订单核实。'}])
    candidate = '用户查询订单 O-101 的物流，订单 O-202 是其另一笔订单。'
    model, events = ReplyModel(json.dumps({'content':candidate}, ensure_ascii=False)), Events()
    manager = SummaryManager(repository, SummaryGenerator(model, settings()), budget_provider=budget, event_logger=events)
    manager.notify('1', layer2_tokens=100, budget=budget())
    try:
        await events.wait('summary_done' if explicit_selection else 'summary_failed')
    finally:
        await manager.aclose()
    anchors, segments = await repository.load('1')
    assert anchors.summary_upto == (106 if explicit_selection else None)
    assert [segment.content for segment in segments] == ([candidate] if explicit_selection else [])
    assert len(model.calls) == 1


async def test_definite_selection_with_order_state_uncertainty_commits(repository):
    from app.context.manager import SummaryManager
    from app.context.summarizer import SummaryGenerator
    await seed(repository, turns=2)
    async with repository.database.session() as session, session.begin():
        await session.execute(text('UPDATE messages SET content=:content WHERE id=:id'), [
            {'id':101,'content':'订单 O-101 和 O-202 都买过，帮我看看那个到哪里了。'},
            {'id':102,'content':'请确认具体订单。'},
            {'id':103,'content':'我选订单 O-101，请查物流，可能是订单还没发货。'},
            {'id':104,'content':'会按您确认的订单核实。'}])
    candidate = '用户提及订单 O-101 和 O-202，随后确认查询订单 O-101 的物流，尚无查询结果。'
    model, events = ReplyModel(json.dumps({'content':candidate}, ensure_ascii=False)), Events()
    manager = SummaryManager(repository, SummaryGenerator(model, settings()), budget_provider=budget, event_logger=events)
    manager.notify('1', layer2_tokens=100, budget=budget())
    try:
        await events.wait('summary_done')
    finally:
        await manager.aclose()
    anchors, segments = await repository.load('1')
    assert anchors.summary_upto == 104
    assert [(segment.from_msg_id, segment.upto_msg_id, segment.content) for segment in segments] == [(101, 104, candidate)]
    assert len(model.calls) == 1


async def test_entity_dense_batches_split_before_generation_without_losing_identities(repository):
    from app.context.manager import SummaryManager
    await seed(repository, turns=2)
    async with repository.database.session() as session, session.begin():
        await session.execute(text('UPDATE messages SET content=:content WHERE id=:id'), [
            {'id':101,'content':'订单 '+ '、'.join(f'ORD-{i}' for i in range(1001,1016))+' 都需要查询，尚未区分。'},
            {'id':103,'content':'订单 '+ '、'.join(f'ORD-{i}' for i in range(1016,1031))+' 都需要查询，尚未区分。'}])
    seen, events = [], Events()
    class Dense:
        async def summarize(self, batch):
            seen.append(batch)
            return batch.source_rows[0].content + '待确认具体订单。'
    manager = SummaryManager(repository, Dense(), budget_provider=budget, event_logger=events)
    manager.notify('1', layer2_tokens=1000, budget=budget())
    await events.wait('summary_done', 2)
    await manager.aclose()
    assert [(b.from_msg_id,b.upto_msg_id) for b in seen] == [(101,102),(103,104)]
    _, segments = await repository.load('1')
    assert len(segments) == 2 and all(f'ORD-{i}' in ''.join(s.content for s in segments) for i in range(1001,1031))


async def test_single_oversized_turn_fails_before_model(repository):
    from app.context.manager import SummaryManager
    await seed(repository, size=1000)
    generator, events = GatedGenerator(), Events()
    manager = SummaryManager(repository, generator, budget_provider=budget, event_logger=events)
    manager.notify('1', layer2_tokens=9000, budget=budget(window=3000, safety=256))
    await events.wait('summary_failed')
    await manager.aclose()
    assert not generator.batches and (await repository.load('1'))[0].summary_upto is None
    failure = next(fields for event,fields in events.items if event == 'summary_failed')
    assert (failure['from_msg_id'], failure['upto_msg_id'], failure['reason']) == ('101','102','capacity_error')


async def test_failed_upstream_has_safe_reason_and_next_notification_can_retry(repository):
    from app.context.manager import SummaryManager
    await seed(repository)
    events = Events()
    class Failure:
        async def summarize(self, batch):
            raise TimeoutError('private upstream secret must not be logged')
    manager = SummaryManager(repository, Failure(), budget_provider=budget, event_logger=events)
    manager.notify('1', layer2_tokens=100, budget=budget())
    await events.wait('summary_failed')
    failure = next(fields for event,fields in events.items if event == 'summary_failed')
    assert failure['reason'] == 'timeout' and 'secret' not in json.dumps(events.items)
    assert (await repository.load('1'))[0].summary_upto is None
    generator = GatedGenerator()
    generator.release.set()
    manager.generator = generator
    assert manager.notify('1', layer2_tokens=100, budget=budget())
    await events.wait('summary_done')
    await manager.aclose()
    assert (await repository.load('1'))[0].summary_upto == 102


async def test_reverse_completion_does_not_cross_conversations(repository):
    from app.context.manager import SummaryManager
    await seed(repository, (1,2))
    gates = {'1':asyncio.Event(), '2':asyncio.Event()}
    entered, events = Events(), Events()
    class Reverse:
        async def summarize(self, batch):
            entered('entered', {})
            await gates[batch.conversation_id].wait()
            return f'订单 O-{batch.conversation_id} 的包裹未找到。'
    manager = SummaryManager(repository, Reverse(), budget_provider=budget, event_logger=events)
    for identifier in ('1','2'):
        manager.notify(identifier, layer2_tokens=100, budget=budget())
    await entered.wait('entered', 2)
    gates['2'].set()
    await events.wait('summary_done')
    assert (await repository.load('1'))[0].summary_upto is None
    assert (await repository.load('2'))[1][0].content == '订单 O-2 的包裹未找到。'
    gates['1'].set()
    await events.wait('summary_done', 2)
    await manager.aclose()
    assert (await repository.load('1'))[1][0].content == '订单 O-1 的包裹未找到。'


async def test_shutdown_waits_five_seconds_then_cancels_and_cleans_up(repository):
    from app.context.manager import SummaryManager
    await seed(repository, (1,2,3))
    generator, events = GatedGenerator(), Events()
    manager = SummaryManager(repository, generator, budget_provider=budget, event_logger=events)
    for identifier in ('1','2','3'):
        manager.notify(identifier, layer2_tokens=100, budget=budget())
    await generator.entered.wait('entered', 2)
    started = asyncio.get_running_loop().time()
    await manager.aclose()
    assert asyncio.get_running_loop().time() - started >= 4.9
    assert generator.cancelled.is_set() and generator.active == 0 and len(generator.batches) == 2
    assert not manager.notify('1', layer2_tokens=100, budget=budget())
    assert all([(await repository.load(str(i)))[0].summary_upto is None for i in (1,2,3)])


async def test_recovery_query_pages_only_downgraded_uncovered_conversations(repository):
    await seed(repository, range(1,7))
    async with repository.database.session() as session, session.begin():
        await session.execute(text('UPDATE conversations SET layer1_from_msg_id=NULL WHERE id=2'))
        await session.execute(text('UPDATE conversations SET summary_upto_msg_id=layer1_from_msg_id WHERE id=3'))
        await session.execute(text('UPDATE conversations SET layer1_from_msg_id=0 WHERE id=4'))
        await session.execute(text('UPDATE conversations SET summary_upto_msg_id=501 WHERE id=5'))
    assert await repository.list_downgraded(limit=2) == ('1','5')
    assert await repository.list_downgraded(after_id=5, limit=2) == ('6',)
    assert await repository.list_downgraded(after_id=6, limit=2) == ()
    for kwargs in ({'limit':0},{'limit':101},{'after_id':-1},{'after_id':True},{'limit':1.5}):
        with pytest.raises(ValueError):
            await repository.list_downgraded(**kwargs)


async def test_startup_recalculates_threshold_and_uses_pages(repository):
    from app.context.manager import SummaryManager
    await seed(repository, range(1,103))
    generator, events = GatedGenerator(), Events()
    provider_calls = []
    def current_budget():
        provider_calls.append(True)
        return budget(layer2=10000)
    manager = SummaryManager(repository, generator, budget_provider=current_budget, event_logger=events)
    await manager.startup()
    await manager.aclose()
    assert provider_calls and not generator.batches
    assert {fields['conversation_id'] for event,fields in events.items if event=='summary_skipped'} == {str(i) for i in range(1,103)}
