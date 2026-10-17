"""Offline acceptance driver: production HTTP/graph/SQL repository/saver/context.

Only external model and retrieval responses are controlled. This proves plumbing
and capacity, never provider semantics. No manually seeded anchors or summaries.
"""
import asyncio
from dataclasses import asdict
import hashlib
import json
from pathlib import Path
import re
from types import SimpleNamespace

import httpx
from langchain_core.messages import AIMessage, AIMessageChunk
from sqlalchemy import text
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from app.context.acceptance import profile_settings, profile_budget
from app.context.logging import ContextLogger
from app.context.manager import SummaryManager
from app.context.service import ContextCoordinator
from app.context.summarizer import SummaryGenerator, required_entities
from app.context.types import SummaryBatch, FrozenMessage
from app.main import create_app
from app.repositories.context import ContextRepository
from app.repositories.conversations import ConversationRepository
from app.repositories.records import record_from_message
from app.retrieval.multi import WorkflowRetrieval
from app.workflow.context_budget import workflow_budget
from app.workflow.persistence import checkpoint_config

FIXTURE = Path(__file__).resolve().parents[2] / 'tests/fixtures/context/long_conversation.json'


def trajectory():
    data = json.loads(FIXTURE.read_text(encoding='utf-8'))
    digest = hashlib.sha256('\n'.join(row['question'] for row in data['turns']).encode()).hexdigest()
    if data.get('sha256') != digest:
        raise ValueError('Frozen trajectory hash mismatch')
    return data


class OfflineModel:
    """Deterministic model boundary; recall is possible only from supplied text."""
    def __init__(self, summary_chars):
        self.turn = None
        self.summary_chars = summary_chars
        self.calls, self.summary_sources = [], []
        self.recall = {}
        self.final_entered, self.final_release = asyncio.Event(), asyncio.Event()
        self.final_release.set()

    def with_structured_output(self, schema, **kwargs):
        parent = self
        class Structured:
            async def ainvoke(self, messages, **kwargs):
                parent.calls.append((parent.turn['turn'], schema.__name__, messages))
                if schema.__name__ == '_UnderstandingOutput':
                    query = parent.turn['question']
                    if parent.turn['turn'] == 21:
                        parent.recall = recall_from_packet(messages)
                        if parent.recall['source_present']:
                            query = f"订单{parent.recall['order_id']}后来状态如何？当时没找到包裹，只查物流，未申请退款。"
                    data = {'query': query}
                elif schema.__name__ == '_IntentOutput':
                    data = {'intent': parent.turn['intents'][0], 'confidence': .99}
                elif schema.__name__ == '_Assessment':
                    data = {'useful': True, 'reason': '受控固定证据', 'response_kind': 'knowledge'}
                else:
                    raise AssertionError('Unexpected expansion or model schema: '+schema.__name__)
                return {'raw': reply(data), 'parsed': schema.model_validate(data), 'parsing_error': None}
        return Structured()

    def bind(self, **kwargs):
        return self

    def bind_tools(self, tools, **kwargs):
        return self

    async def ainvoke(self, messages, **kwargs):
        body = json.loads(messages[-1].content) if messages[-1].content.startswith('{') else {}
        if body.get('kind') == 'summary_source':
            self.summary_sources.append(body)
            # External summary latency is event-controlled. Its response is
            # released only after the same graph reaches a blocked final stream.
            await self.final_entered.wait()
            rows = tuple(FrozenMessage(**row) for row in body['source_rows'])
            batch = SummaryBatch(body['conversation_id'], None, 0, int(body['from_msg_id']),
                                 int(body['upto_msg_id']), rows, '')
            users = '；'.join(row.content or '' for row in rows if row.role == 'user')
            entities = sorted(required_entities(batch))
            orders = list(dict.fromkeys(re.findall(r'订单\s*(\d+)', users)))
            content = ('曾' + '，后'.join('查订单'+order for order in orders) + '。') if orders else '曾咨询。'
            content += '、'.join(entity for entity in entities if entity not in orders) + '。'
            if '没找到包裹' in users:
                content += '用户没找到包裹，只查物流，未申请退款。'
            content += '当时模拟记录供查询参考，后续尚待核实。'
            if len(content) < self.summary_chars:
                # Controlled verbosity variant of the SAME batch; never old segments.
                extra = '以上为当时咨询记录，未推断后续结果。'
                content += (extra * 12)[:self.summary_chars-len(content)]
            return reply({'content': content})
        self.calls.append((self.turn['turn'], 'decision', messages))
        # Native current-turn tools follow the context attachment.
        attachment = max(i for i, row in enumerate(messages) if row.type == 'human')
        has_current_result = any(row.type == 'tool' for row in messages[attachment+1:])
        business = self.turn['intents'][0] in ('物流', '订单')
        order_id = (self.turn['entities'][0] if business and self.turn['entities'] else None) if self.turn['turn'] != 21 else self.recall.get('order_id')
        if business and order_id and not has_current_result:
            return AIMessage('', tool_calls=[{'id': f"offline-{self.turn['turn']}",
                'name': self.turn['actions'][0], 'args': {'order_id': order_id}}],
                response_metadata={'finish_reason': 'tool_calls'})
        return reply({'reply_mode': 'answer' if not business or order_id else 'clarification',
                      'suggested_actions': [], 'refund_decision': None, 'decision_reason': None})

    async def astream(self, messages, **kwargs):
        self.calls.append((self.turn['turn'], 'final', messages))
        self.final_entered.set()
        await self.final_release.wait()
        if self.turn['turn'] == 21:
            # Recheck final packet too; the understanding result alone cannot create memory.
            if self.recall.get('source_present'):
                assert recall_from_packet(messages)['order_id'] == self.recall['order_id']
                content = f"最开始是订单{self.recall['order_id']}。当时没找到包裹，只要求查询物流，未申请退款。模拟结果仅表示当时记录，不能证明后来已找到包裹。"
            else:
                content = '请提供订单号。'
        else:
            content = self.turn['summary_facts'] + '本次为离线受控演示，具体适用条件应以当前订单及正式政策为准。查询信息仅供核对，不代表已经提交任何售后业务。请保留购买凭证，核对商品型号、订单状态以及相关时间；如果信息仍有疑问，可以继续说明需要核实的部分。此处不承诺未核实的处理结果，也不会将咨询等同于已受理申请。'
            if self.turn['intents'] == ['商品咨询']:
                content += '[1]'
        yield AIMessageChunk(content)
        yield AIMessageChunk('', response_metadata={'finish_reason': 'stop'})


def reply(data):
    return AIMessage(json.dumps(data, ensure_ascii=False), response_metadata={'finish_reason': 'stop'})


def recall_from_packet(messages):
    """Inspect chronological *injected* summaries/users, never a fixture/global memory."""
    summaries, users = [], []
    for row in messages[1:]:
        if row.type != 'human':
            continue
        try:
            body = json.loads(row.content)
        except (ValueError, TypeError):
            users.append(row.content)
            continue
        if body.get('kind') == 'context_data':
            summaries.extend(segment['content'] for segment in body['summaries'])
    for source_kind, source in [('summary', text) for text in summaries] + [('user', text) for text in users]:
        if '没找到包裹' in source and ('不申请退款' in source or '未申请退款' in source):
            match = re.search(r'(?:订单)?(\d{4})(?!\d)', source)
            if match:
                return dict(order_id=match[1], source_present=True, unresolved=True, no_refund=True, source=source, source_kind=source_kind)
    return dict(order_id=None, source_present=False, unresolved=False, no_refund=False)


class OfflineRetrieval:
    async def retrieve(self, *, question, queries, category, top_k=10):
        assert queries == (question,), 'Complete general questions must not expand'
        match = dict(id='501', question=question, answer='这是离线固定政策样例，咨询不代表已提交任何申请。',
                     section_path='受控政策', score=.95, score_kind='rerank')
        return WorkflowRetrieval({'found': True, 'matches': [match],
            'retrieval': {'strategy': 'hybrid_rerank', 'match_count': 1}}, {})


async def replay(profile, output_dir, *, summary_chars=50):
    data = trajectory()
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    # Each invocation gets owned SQLite; no reuse of old checkpoints or seeding.
    from uuid import uuid4
    directory = output_dir / uuid4().hex
    directory.mkdir()
    engine = create_async_engine('sqlite+aiosqlite:///:memory:')
    logger = ContextLogger(directory/'app.log')
    manager = request = model = None
    try:
        async with engine.begin() as conn:
            for ddl in (
                "CREATE TABLE conversations (id INTEGER PRIMARY KEY,user_id TEXT NOT NULL,status TEXT DEFAULT '进行中',summary TEXT,summary_upto_msg_id INTEGER,layer1_from_msg_id INTEGER,created_at DATETIME DEFAULT CURRENT_TIMESTAMP,updated_at DATETIME DEFAULT CURRENT_TIMESTAMP)",
                "CREATE TABLE messages (id INTEGER PRIMARY KEY,conversation_id INTEGER NOT NULL,role TEXT,content TEXT,tool_calls JSON,tool_call_id TEXT,created_at DATETIME DEFAULT CURRENT_TIMESTAMP)",
                "CREATE TABLE conversation_summaries (id INTEGER PRIMARY KEY AUTOINCREMENT,conversation_id INTEGER NOT NULL,seq INTEGER,from_msg_id INTEGER,upto_msg_id INTEGER,content TEXT,created_at DATETIME DEFAULT CURRENT_TIMESTAMP,UNIQUE(conversation_id,seq))",
            ):
                await conn.execute(text(ddl))
        database = SimpleNamespace(session=async_sessionmaker(engine, expire_on_commit=False))
        repo, context_repo = ConversationRepository(database), ContextRepository(database)
        cid = await repo.create('demo-user')
        settings = profile_settings(profile, offline=True, workflow_checkpoint_path=directory/'checkpoints.sqlite')
        model = OfflineModel(summary_chars)
        generator = SummaryGenerator(model, settings, context_logger=logger)
        event_changed = asyncio.Event()
        events = []
        def event(name, fields):
            nonlocal blocked_proof
            events.append(name)
            logger.event(name, fields)
            if name == 'summary_done' and model.final_entered.is_set() and not model.final_release.is_set():
                blocked_proof = True
            event_changed.set()
        manager = SummaryManager(context_repo, generator, budget_provider=lambda: budget, event_logger=event)
        coordinator = ContextCoordinator(context_repo, manager, settings, context_logger=logger)
        quality = SimpleNamespace(commit_refusal=lambda *args, **kwargs: (_ for _ in ()).throw(AssertionError('Unexpected refusal')))
        app = create_app(settings, model=model, repository=repo, faq_repository=SimpleNamespace(),
            quality_repository=quality, workflow_retriever=OfflineRetrieval(), context_coordinator=coordinator,
            context_logger=logger, context_budget_provider=lambda registry: workflow_budget(settings, registry))
        from app.tools.types import ToolContext
        from app.tools.registry import build_registry
        from app.orders.demo import DemoOrderProvider
        budget = workflow_budget(settings, build_registry(None, None, ToolContext(cid, 0, '', None),
            order_provider=DemoOrderProvider(), owner_resolver=repo.get_user_id))
        turns, blocked_proof = [], False
        async with app.router.lifespan_context(app):
            async with httpx.AsyncClient(transport=httpx.ASGITransport(app), base_url='http://offline') as client:
                for turn in data['turns']:
                    model.turn = turn
                    model.final_entered.clear()
                    model.final_release.clear()
                    request = asyncio.create_task(client.post('/api/chat', json={'conversation_id': cid, 'message': turn['question']}))
                    waiter = asyncio.create_task(model.final_entered.wait())
                    done, _ = await asyncio.wait((request, waiter), timeout=20, return_when=asyncio.FIRST_COMPLETED)
                    if not done:
                        raise AssertionError('Offline graph did not reach final')
                    if waiter in done:
                        # Holding final response must not prevent admitted background work.
                        async with asyncio.timeout(10):
                            while manager._running:
                                event_changed.clear()
                                await event_changed.wait()
                    waiter.cancel()
                    await asyncio.gather(waiter, return_exceptions=True)
                    model.final_release.set()
                    response = await request
                    if response.status_code != 200 or 'event: done' not in response.text:
                        raise AssertionError(f"Turn {turn['turn']} did not complete: {response.text}")
                    root = await app.state.chat_service.graph.aget_state(checkpoint_config(cid))
                    turns.append(dict(turn=turn['turn'], intent=root.values['intent'], route=root.values['route'],
                        resolved_question=root.values['resolved_question'], user_message_id=root.values['user_message_id']))
                    assert root.values['intent'] in turn['intents']
                    if turn['intents'] == ['商品咨询']:
                        assert root.values.get('order_selection') is None
                        assert not any(t == turn['turn'] and phase == '_ExpansionOutput' for t, phase, _ in model.calls)
                sql = await repo.load_messages(cid)
                actual = [record_from_message(message, identifier=int(message.id)) for message in root.values['messages']]
                equal = sql == actual
                saved_snapshot = root.values['context_snapshot']
        await manager.aclose()
        anchors, segments = await context_repo.load(cid)
        log = [json.loads(line) for line in (directory/'app.log').read_text(encoding='utf-8').splitlines()]
        calls = [dict(phase=row['phase'], estimated_tokens=row['estimated_tokens'], output_tokens=row['output_tokens'],
                      within_budget=row['estimated_tokens']+row['output_tokens']+budget.safety<=budget.window)
                 for row in log if row['event'] == 'model_ctx']
        return dict(profile=profile, fixture_sha256=data['sha256'], mode='offline-controlled-real-graph',
            budget=profile_budget(profile), turns=turns, sql_checkpoint_equal=equal,
            final_recall=model.recall, events=[row['event'] for row in log], calls=calls,
            history_turn_ids=sorted({row['user_message_id'] for row in log if row['event']=='history_ctx'}, key=int),
            business_turns=[row['turn'] for row in turns if row['route']=='business'], general_no_expansion_or_selection=True,
            first_order_in_summary=any('1001' in segment.content and '没找到包裹' in segment.content for segment in segments),
            summary_completed_while_final_blocked=blocked_proof, summary_chars=summary_chars,
            omitted_summary_seqs=saved_snapshot['omitted_summary_seqs'],
            summaries=[asdict(segment) | {'created_at': segment.created_at.isoformat()} for segment in segments],
            anchors=asdict(anchors), summary_source_ranges=[(item['from_msg_id'],item['upto_msg_id']) for item in model.summary_sources],
            log_path=str(directory/'app.log'), checkpoint_path=str(directory/'checkpoints.sqlite'),
            original_rows=[asdict(row) for row in sql])
    finally:
        if model is not None:
            model.final_release.set()
        if request is not None and not request.done():
            request.cancel()
            await asyncio.gather(request, return_exceptions=True)
        if manager is not None:
            await manager.aclose()
        logger.close()
        await engine.dispose()
