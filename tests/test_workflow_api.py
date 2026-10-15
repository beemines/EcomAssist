"""默认聊天入口的真实图、SQLite 和 SSE 契约。"""
import importlib
import json
from contextlib import asynccontextmanager
from unittest.mock import patch

import httpx
import pytest
from langchain_core.messages import AIMessage, AIMessageChunk, HumanMessage

from app.main import create_app
from app.workflow.persistence import checkpoint_config
from tests.fakes import ConversationStore, FAQStub, fake_settings, decode_sse
from tests.workflow_fakes import ScriptedWorkflowModel


def service_type():
    """生产入口缺失时明确断言功能尚未实现，避免收集错误。"""
    try:
        return importlib.import_module('app.workflow.service').WorkflowChatService
    except ImportError:
        pytest.fail('WorkflowChatService is not implemented')


def intent(name):
    """构造严格分类响应，只替换收费模型边界。"""
    return AIMessage(json.dumps({'intent': name, 'confidence': 0.95}, ensure_ascii=False), response_metadata={'finish_reason': 'stop'})


class Store(ConversationStore):
    """保留实际审计与提交顺序的离线 SQL 边界。"""
    def __init__(self, trace=None):
        """初始化提交轨迹以及质量拒答记录。"""
        super().__init__()
        self.trace = trace if trace is not None else []
        self.refusals = []

    async def append_message(self, conversation_id, message):
        """真实保存后才记录提交，便于检查 checkpoint 与 done 顺序。"""
        identifier = await super().append_message(conversation_id, message)
        if isinstance(message, AIMessage) and not message.tool_calls:
            self.trace.append('commit_final')
        return identifier

    async def commit_refusal(self, conversation_id, answer, **kwargs):
        """镜像质量仓储原子接口，保存拒答及审核信息。"""
        self.refusals.append(kwargs)
        return await self.append_message(conversation_id, answer)


@asynccontextmanager
async def workflow_app(tmp_path, *, model=None, store=None, faq=None, saver=None, **settings):
    """应用真实拥有 SQLite 生命周期，模型与 SQL 使用离线注入。"""
    service_type()
    store = store if store is not None else Store()
    app = create_app(fake_settings(workflow_checkpoint_path=tmp_path / 'checkpoints.sqlite', **settings),
        model=model if model is not None else ScriptedWorkflowModel(),
        repository=store if store is not None else Store(), faq_repository=faq or FAQStub(),
        quality_repository=store if store is not None else Store(), **({'checkpointer': saver} if saver else {}))
    from app.workflow.runtime import WorkflowRuntime
    from app.retrieval.multi import WorkflowRetrieval
    from tests.workflow_fakes import workflow_runtime
    def runtime(*args, **kwargs):
        """Task5新增依赖在测试边界明确提供，生产接线留Task6。"""
        result = WorkflowRuntime(*args, **kwargs)
        result.understanding = workflow_runtime().understanding
        class Retrieve:
            async def retrieve(self, *, question, queries, category):
                """复用已注入FAQ边界，保留真实图及检查点。"""
                assert queries == (question,)
                return WorkflowRetrieval(await result.faq_repository.retrieve(question[:128],
                    raw_question=question, category=category), {})
        result.workflow_retriever = Retrieve()
        return result
    with patch('app.workflow.service.WorkflowRuntime', runtime):
        async with app.router.lifespan_context(app):
            yield app


async def request(app, message):
    """通过完整 ASGI 入口消费响应，保留真实托管清理行为。"""
    async with httpx.AsyncClient(transport=httpx.ASGITransport(app), base_url='http://test') as client:
        return await client.post('/api/chat', json={'conversation_id': '1', 'message': message})


async def test_default_app_uses_workflow(tmp_path):
    """默认路径若仍使用旧单次服务，将缺失真实根检查点。"""
    async with workflow_app(tmp_path) as app:
        assert isinstance(app.state.chat_service, service_type())
        frames = decode_sse((await request(app, '你好')).text)
        snapshot = await app.state.chat_service.graph.aget_state(checkpoint_config('1'))
        assert frames[-1] == ('done', {'conversation_id': '1', 'message_id': '2'})
        assert snapshot.next == () and snapshot.values['turn_status'] == 'completed'
    assert (tmp_path / 'checkpoints.sqlite').exists()


async def test_chat_html_is_not_stored_by_browser_cache(tmp_path):
    """聊天入口每次取新HTML，避免改版后仍使用旧脚本地址和动作交互。"""
    async with workflow_app(tmp_path) as app:
        async with httpx.AsyncClient(transport=httpx.ASGITransport(app), base_url='http://test') as client:
            response = await client.get('/')
    assert response.status_code == 200
    assert response.headers.get('cache-control') == 'no-store'


async def test_social_zero_model_calls(tmp_path):
    """问候若误分类或生成会消费空模型队列并失去正常完成。"""
    model = ScriptedWorkflowModel()
    async with workflow_app(tmp_path, model=model) as app:
        frames = decode_sse((await request(app, '你好')).text)
    assert model.intents + model.decisions + model.streams == 0
    assert frames[-1][0] == 'done'
    assert [name for name, _ in frames].count('citations') == 1
    assert [name for name, _ in frames].index('citations') < [name for name, _ in frames].index('delta')


async def test_sql_commit_then_checkpoint_then_done(tmp_path):
    """未经持久化完成就发送按钮或 done 会破坏最后快照断言。"""
    from langgraph.checkpoint.sqlite.aio import AsyncSqliteSaver
    trace = []
    class Saver(AsyncSqliteSaver):
        """只观察官方磁盘写入完成，不替代持久化。"""
        async def aput(self, config, checkpoint, metadata, new_versions):
            """实际持久化 completed 后才记完成边界。"""
            result = await super().aput(config, checkpoint, metadata, new_versions)
            if checkpoint['channel_values'].get('turn_status') == 'completed':
                trace.append('checkpoint_complete')
            return result
    model, store = ScriptedWorkflowModel(intent_replies=[intent('投诉')]), Store(trace)
    async with Saver.from_conn_string(str(tmp_path / 'official.sqlite')) as saver:
        async with workflow_app(tmp_path, model=model, store=store, saver=saver) as app:
            frames = decode_sse((await request(app, '我要投诉')).text)
            trace.extend(name for name, _ in frames if name == 'done')
            actions = next(data for name, data in frames if name == 'actions')
            snapshot = await app.state.chat_service.graph.aget_state(checkpoint_config('1', checkpoint_id=actions['checkpoint_id']))
            assert actions == {'assistant_message_id': '2', 'checkpoint_id': snapshot.config['configurable']['checkpoint_id'],
                'options': [{'action': 'handoff', 'label': '转人工'}, {'action': 'create_ticket', 'label': '建工单'}]}
            assert snapshot.next == () and snapshot.values['final_message_id'] == '2'
    assert trace.index('commit_final') < trace.index('checkpoint_complete') < trace.index('done')


async def test_sql_success_checkpoint_failure_no_done(tmp_path):
    """SQL 成功 SQLite 失败必须明确失败，不能给出可执行旧按钮。"""
    from langgraph.checkpoint.sqlite.aio import AsyncSqliteSaver
    class Saver(AsyncSqliteSaver):
        """只在根完成写盘处注入故障，其余仍用官方文件。"""
        async def aput(self, config, checkpoint, metadata, new_versions):
            """模拟最终检查点写入故障。"""
            if checkpoint['channel_values'].get('turn_status') == 'completed':
                raise OSError('controlled checkpoint failure')
            return await super().aput(config, checkpoint, metadata, new_versions)
    store = Store()
    async with Saver.from_conn_string(str(tmp_path / 'fault.sqlite')) as saver:
        async with workflow_app(tmp_path, model=ScriptedWorkflowModel(intent_replies=[intent('投诉')]), store=store, saver=saver) as app:
            frames = decode_sse((await request(app, '我要投诉')).text)
    names = [name for name, _ in frames]
    assert store.commits == 1
    assert 'done' not in names and 'actions' not in names and names[-1] == 'error'


async def test_preflight_budget_and_stable_history_ids(tmp_path):
    """预检错误不写用户记录；重复原文历史仍按 SQL 身份区分。"""
    store = Store()
    await store.seed('1', [HumanMessage('你好'), AIMessage('您好')])
    async with workflow_app(tmp_path, store=store) as app:
        service = app.state.chat_service
        prepared = await service.prepare('1', '你好')
        assert [message.id for message in prepared.state['messages']] == ['1', '2', '3']
        assert prepared.runtime.deadline == prepared.deadline
        service.release(prepared)
    async with workflow_app(tmp_path, store=Store(), tool_input_token_budget=1) as app:
        response = await request(app, '你好')
        assert response.status_code == 422
        assert app.state.repository.rows == {}
        app.state.chat_service.locks.acquire('1').release()


async def test_forced_faq_running_arrives_before_retrieval_finishes(tmp_path):
    """强制检索等待期间必须可见带独立身份的 running，不能等检索完成后补发。"""
    import asyncio
    class FAQ(FAQStub):
        """阻塞检索边界，保留强制图节点和实际服务。"""
        async def retrieve(self, *args, **kwargs):
            """未解除门禁时工具完成事件不得出现。"""
            await gate.wait()
            return await super().retrieve(*args, **kwargs)
    gate, store = asyncio.Event(), Store()
    async with workflow_app(tmp_path, model=ScriptedWorkflowModel(intent_replies=[intent('商品咨询')]), store=store, faq=FAQ()) as app:
        service = app.state.chat_service
        prepared = await service.prepare('1', '商品参数')
        events = service.stream(prepared)
        assert (await anext(events)).data['phase'] == 'selecting'
        running = await asyncio.wait_for(anext(events), 2)
        assert running.data['phase'] == 'tool_running' and running.data['origin'] == 'workflow'
        assert not gate.is_set() and store.commits == 0
        gate.set()
        rest = [event async for event in events]
        service.release(prepared)
    completed = next(event for event in rest if event.data.get('phase') == 'tool_completed')
    assert completed.data['tool_call_id'] == running.data['tool_call_id']
    assert rest[-1].event == 'done'


@pytest.mark.parametrize('fails', [False, True])
async def test_forced_faq_public_completion_reports_actual_result(tmp_path, fails):
    """真实 HTTP 完成帧必须含成功结果及同一工具身份，失败检索不得伪报成功。"""
    faq = FAQStub(failure=RuntimeError('controlled retrieval failure') if fails else None)
    model = ScriptedWorkflowModel(intent_replies=[intent('商品咨询')])
    async with workflow_app(tmp_path, model=model, store=Store(), faq=faq) as app:
        frames = decode_sse((await request(app, '商品参数')).text)
    running = next(data for name, data in frames if name == 'status' and data.get('phase') == 'tool_running')
    completed = [data for name, data in frames if name == 'status' and data.get('phase') == 'tool_completed']
    assert running['tool_name'] == 'query_faq' and running['origin'] == 'workflow'
    assert running['tool_call_id'].startswith('workflow_faq_')
    if fails:
        assert completed == [] and frames[-1][0] == 'error'
    else:
        assert completed == [{'phase': 'tool_completed', 'tool_name': 'query_faq',
            'tool_call_id': running['tool_call_id'], 'origin': 'workflow', 'status': 'success'}]
        assert frames[-1][0] == 'done'


async def test_citations_match_final_packet_and_precede_live_delta(tmp_path):
    """最终知识引用必须在首正文前仅一次出现，并与完成快照精确相同。"""
    from app.core.sufficiency import QualityDecision
    from tests.test_workflow_agent import control
    class Assessment:
        """只替换外部充分性模型。"""
        async def check(self, question, packet):
            """返回达标结论，保留真实证据组装。"""
            return QualityDecision(useful=True, reason='覆盖', response_kind='knowledge', source=None)
    faq = FAQStub([{'id': 7, 'question': '运费规则', 'answer': '八元', 'category': '配送'}])
    model = ScriptedWorkflowModel([control()], intent_replies=[intent('商品咨询')], final_chunks=[
        AIMessageChunk('运费八元[1]。'), AIMessageChunk('', response_metadata={'finish_reason': 'stop'})])
    async with workflow_app(tmp_path, model=model, faq=faq) as app:
        app.state.chat_service.sufficiency_service = Assessment()
        frames = decode_sse((await request(app, '运费规则')).text)
        snapshot = await app.state.chat_service.graph.aget_state(checkpoint_config('1'))
    names = [name for name, _ in frames]
    assert names[-1] == 'done' and names.count('citations') == 1
    assert names.index('citations') < names.index('delta')
    citations = next(data['citations'] for name, data in frames if name == 'citations')
    assert citations == snapshot.values['citations']
    assert citations[0]['answer'] == '八元' and citations[0]['chunk_id'] == '7'
    assert all('reply_mode' not in str(data) and 'intent' not in data for _, data in frames)


@pytest.mark.parametrize('bad', [[{}], [{'n': 0, 'chunk_id': '7', 'section_path': None, 'question': 'q', 'answer': 'a'}]])
async def test_invalid_custom_citations_never_reach_public_delta(tmp_path, monkeypatch, bad):
    """图自定义载荷也经过服务边界校验，无效引用不能作为公开可信证据。"""
    from app.workflow import nodes
    original = nodes.social_response
    async def noisy(state, runtime):
        """只在真实社交节点前插入无效载荷以检验公开边界。"""
        runtime.stream_writer({'event': 'citations', 'data': {'citations': bad}})
        return await original(state, runtime)
    monkeypatch.setattr(nodes, 'social_response', noisy)
    async with workflow_app(tmp_path) as app:
        frames = decode_sse((await request(app, '你好')).text)
    assert frames[-1][0] == 'error'
    assert not any(name in ('delta', 'citations', 'done', 'actions') for name, _ in frames)


async def test_custom_phase_whitelist_and_citation_dedup(tmp_path, monkeypatch):
    """内部消息、未知阶段及二次引用不得越过公开 SSE 边界。"""
    from app.workflow import nodes
    original = nodes.social_response
    async def noisy(state, runtime):
        """插入内部日志和重复引用，保留真实节点输出与最终提交。"""
        runtime.stream_writer({'event': 'messages', 'data': {'text': 'private control'}})
        runtime.stream_writer({'event': 'status', 'data': {'phase': 'classify_intent', 'origin': 'unknown'}})
        runtime.stream_writer({'event': 'citations', 'data': {'citations': []}})
        return await original(state, runtime)
    monkeypatch.setattr(nodes, 'social_response', noisy)
    async with workflow_app(tmp_path) as app:
        frames = decode_sse((await request(app, '你好')).text)
    assert frames[-1][0] == 'done'
    assert [name for name, _ in frames].count('citations') == 1
    assert all(data['phase'] in {'selecting', 'checking', 'answering', 'tool_running', 'tool_completed'}
        for name, data in frames if name == 'status')
    assert 'private control' not in str(frames) and 'classify_intent' not in str(frames)


async def test_sql_failure_never_announces_completed_checkpoint(tmp_path):
    """最终 SQL 提交失败即使已有正文，也不得发布动作或 done。"""
    store = Store()
    store.fail_final = True
    async with workflow_app(tmp_path, store=store) as app:
        frames = decode_sse((await request(app, '你好')).text)
        snapshot = await app.state.chat_service.graph.aget_state(checkpoint_config('1'))
    assert frames[-1][0] == 'error' and store.commits == 0
    assert not any(name in ('done', 'actions') for name, _ in frames)
    assert snapshot.values['turn_status'] != 'completed'


async def test_unfinished_reply_drops_prior_evidence_citations():
    """安全停止的空引用必须同时清空最终状态，不能让后续按钮快照携带旧证据。"""
    from types import SimpleNamespace
    from app.workflow.agent import finalize_answer
    from app.workflow.state import new_turn_state
    from tests.workflow_fakes import workflow_runtime
    state = new_turn_state(conversation_id='1', user_message_id=1, raw_question='商品',
        category=None, messages=[HumanMessage('商品')])
    state.update(stop_reason='step_limit', citations=[{'n': 1, 'chunk_id': 'old',
        'question': 'q', 'answer': 'a', 'section_path': None}])
    events = []
    update = await finalize_answer(state, SimpleNamespace(context=workflow_runtime(), stream_writer=events.append))
    final = {**state, **update}
    assert final['citations'] == []
    assert [event['data']['citations'] for event in events if event['event'] == 'citations'] == [[]]
async def test_service_waits_for_intermediate_sqlite_write(tmp_path, monkeypatch):
    """真实服务下一节点必须等待官方SQLite中间检查点写完，默认async会反转轨迹。"""
    import asyncio
    from langgraph.checkpoint.sqlite.aio import AsyncSqliteSaver
    from tests.workflow_fakes import ScriptedIntentModel
    trace = []
    original = ScriptedIntentModel.ainvoke
    async def classify(self, messages, **kwargs):
        """仅观察离线模型入口，不替代生产图或检查点实现。"""
        trace.append('classify')
        return await original(self, messages, **kwargs)
    monkeypatch.setattr(ScriptedIntentModel, 'ainvoke', classify)
    class DelayedSaver(AsyncSqliteSaver):
        """只延迟引用解析之后的官方真实写入。"""
        async def aput(self, config, checkpoint, metadata, new_versions):
            """完成磁盘持久化后记录，证明下个节点不能提前进入。"""
            state = checkpoint['channel_values']
            delayed = state.get('turn_status') == 'running' and state.get('intent') is None
            if delayed:
                await asyncio.sleep(.1)
            result = await super().aput(config, checkpoint, metadata, new_versions)
            if delayed:
                trace.append('intermediate_saved')
            return result
    async with DelayedSaver.from_conn_string(str(tmp_path / 'sync.sqlite')) as saver:
        async with workflow_app(tmp_path, saver=saver,
                model=ScriptedWorkflowModel(intent_replies=[intent('投诉')])) as app:
            frames = decode_sse((await request(app, '我要投诉')).text)
            assert frames[-1][0] == 'done'
            snapshot = await app.state.chat_service.graph.aget_state(checkpoint_config('1'))
            assert not snapshot.next and snapshot.values['turn_status'] == 'completed'
    assert trace == ['intermediate_saved', 'classify']
