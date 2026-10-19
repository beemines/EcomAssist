"""Context dependencies are explicit; injected resources remain caller-owned."""

async def test_injected_context_resources_are_not_closed_or_connected(tmp_path):
    from app.main import create_app
    from tests.fakes import fake_settings, FAQStub
    from tests.test_workflow_api import Store
    from tests.workflow_fakes import ScriptedWorkflowModel
    from tests.test_context_workflow import Notifications
    from tests.test_context_manager import budget
    from app.context.logging import ContextLogger
    from app.context.service import ContextCoordinator

    class NoDatabase:
        async def load(self, cid):
            raise AssertionError('startup must not read an injected context repository')
    manager = Notifications()
    logger = ContextLogger(tmp_path / 'app.log')
    coordinator = ContextCoordinator(NoDatabase(), manager, fake_settings())
    app = create_app(fake_settings(workflow_checkpoint_path=tmp_path / 'checkpoint.sqlite'),
        model=ScriptedWorkflowModel(), repository=Store(), faq_repository=FAQStub(),
        context_coordinator=coordinator, context_logger=logger, context_budget_provider=lambda registry: budget())
    async with app.router.lifespan_context(app):
        assert app.state.chat_service.context_coordinator is coordinator
    logger.event('context_error', {'reason': 'caller_still_owns_logger'})
    logger.close()


async def test_owned_manager_closes_before_model_database_logger(tmp_path, monkeypatch):
    import app.main as main
    from types import SimpleNamespace
    from tests.fakes import fake_settings, FAQStub
    from tests.test_workflow_api import Store
    from tests.workflow_fakes import ScriptedWorkflowModel
    from tests.test_context_manager import budget
    trace = []

    class Database:
        engine = object()
        def __init__(self, url):
            pass
        async def dispose(self):
            trace.append('database')
    class Logger:
        def __init__(self, path):
            assert path.name == 'app.log' and path.parent.name == 'log'
        def event(self, name, fields):
            pass
        def close(self):
            trace.append('logger')
    class Manager:
        def __init__(self, repository, generator, **kwargs):
            self.provider = kwargs['budget_provider']
        async def startup(self):
            assert self.provider().window == 12000
            trace.append('startup')
        async def aclose(self):
            assert app.state.chat_service._closing is True
            trace.append('manager')
    class Generator:
        def __init__(self, model, settings, *, context_logger, observability=None):
            assert context_logger is not None
            assert observability is not None and observability.client is None
    model = ScriptedWorkflowModel()
    async def close_async():
        trace.append('model_async')
    model.root_client = SimpleNamespace(close=lambda: trace.append('model_sync'))
    model.root_async_client = SimpleNamespace(close=close_async)
    monkeypatch.setattr(main, 'Database', Database)
    monkeypatch.setattr(main, 'ConversationRepository', lambda db: Store())
    monkeypatch.setattr(main, 'create_model', lambda settings: model)
    monkeypatch.setattr(main, 'ContextLogger', Logger)
    monkeypatch.setattr(main, 'SummaryManager', Manager)
    monkeypatch.setattr(main, 'SummaryGenerator', Generator)
    async def verify(db):
        trace.append('verify')
    monkeypatch.setattr(main, 'verify_quality', verify)
    monkeypatch.setattr(main, 'verify_refunds', verify)
    monkeypatch.setattr(main, 'verify_context', verify)
    app = main.create_app(fake_settings(workflow_checkpoint_path=tmp_path / 'root.sqlite', mysql_password='test-only'),
        faq_repository=FAQStub(), context_budget_provider=lambda registry: budget())
    async with app.router.lifespan_context(app):
        assert not app.state.chat_service._closing
    assert app.state.chat_service._closing is True
    assert trace == ['verify', 'verify', 'verify', 'startup', 'manager', 'model_async', 'model_sync', 'database', 'logger']


async def test_restart_paused_snapshot_ignores_new_summary_and_rechecks_smaller_budget(tmp_path):
    import httpx
    from app.main import create_app
    from app.context.service import ContextCoordinator
    from app.context.types import ContextAnchors
    from app.repositories.records import MessageRecord
    from app.workflow.persistence import checkpoint_config
    from tests.test_context_manager import budget
    from tests.test_context_workflow import Notifications
    from tests.test_order_resume_lifecycle import OwnerStore, reply, pause, selection, Retrieve
    from tests.test_workflow_api import intent
    from tests.workflow_fakes import ScriptedWorkflowModel
    from tests.fakes import fake_settings, FAQStub, decode_sse
    store = OwnerStore()
    store.rows['1'] = [MessageRecord(1, 'user', '以前问过使用方法', None, None),
                       MessageRecord(2, 'assistant', '历史正文' * 500, None, None)]
    class Context:
        changed = False
        async def load(self, cid):
            assert not self.changed, 'resume must restore persisted snapshot, not new summary rows'
            return ContextAnchors(None, None), ()
    context = Context()
    coordinator = ContextCoordinator(context, Notifications(), None)
    from app.workflow.context_budget import workflow_budget
    def application(model, **overrides):
        config = fake_settings(workflow_checkpoint_path=tmp_path / 'resume.sqlite', agent_total_token_budget=100000, **overrides)
        return create_app(config,
            model=model, repository=store, faq_repository=FAQStub(), quality_repository=store,
            context_coordinator=coordinator, context_budget_provider=lambda registry: workflow_budget(config, registry),
            workflow_retriever=Retrieve())
    first = application(ScriptedWorkflowModel(intent_replies=[reply({'query': '这个能退吗？'}), intent('退款退货')]),
                        model_context_window=25000)
    async with first.router.lifespan_context(first):
        async with httpx.AsyncClient(transport=httpx.ASGITransport(first), base_url='http://localhost') as client:
            card, _ = await pause(client)
        original = await first.state.chat_service.graph.aget_state(checkpoint_config('1'))
        saved_view = original.values['context_snapshot']
    context.changed = True
    failed_model = ScriptedWorkflowModel()
    small = application(failed_model, model_context_window=18000,max_agent_steps=3,max_output_tokens=2000,rerank_top_k=5)
    async with small.router.lifespan_context(small):
        async with httpx.AsyncClient(transport=httpx.ASGITransport(small), base_url='http://localhost') as client:
            response = await client.post('/api/conversations/1/actions/select-order', json=selection(card))
        assert response.status_code == 409 and response.json()['code'] == 'context_configuration_conflict'
        unchanged = await small.state.chat_service.graph.aget_state(checkpoint_config('1'))
        assert unchanged.config == original.config and unchanged.values['context_snapshot'] == saved_view
        assert failed_model.intents == failed_model.decisions == 0
    resumed = application(ScriptedWorkflowModel(intent_replies=[reply({'queries': ['这个能退吗？', '退货政策']})]),
                          model_context_window=26000)
    async with resumed.router.lifespan_context(resumed):
        async with httpx.AsyncClient(transport=httpx.ASGITransport(resumed), base_url='http://localhost') as client:
            response = await client.post('/api/conversations/1/actions/select-order', json=selection(card))
        assert decode_sse(response.text)[-1][0] == 'done', response.text
        final = await resumed.state.chat_service.graph.aget_state(checkpoint_config('1'))
        assert final.values['context_snapshot_id'] == original.values['context_snapshot_id']
        assert final.values['context_snapshot']['layer1'] == saved_view['layer1']
        assert final.values['context_budget']['window'] == 26000
        before_calls = resumed.state.chat_service.model.intents
        async with httpx.AsyncClient(transport=httpx.ASGITransport(resumed), base_url='http://localhost') as client:
            replay = await client.post('/api/conversations/1/actions/select-order', json=selection(card))
        assert decode_sse(replay.text)[-1][0] == 'done'
        replayed = await resumed.state.chat_service.graph.aget_state(checkpoint_config('1'))
        assert replayed.config == final.config and replayed.values['context_snapshot'] == final.values['context_snapshot']
        assert resumed.state.chat_service.model.intents == before_calls


async def test_legacy_pause_without_snapshot_is_established_only_for_resume(tmp_path):
    import httpx
    import sqlite3
    from app.main import create_app
    from app.context.service import ContextCoordinator
    from app.context.types import ContextAnchors
    from app.workflow.persistence import checkpoint_config
    from tests.test_context_manager import budget
    from tests.test_context_workflow import Notifications
    from tests.test_order_resume_lifecycle import OwnerStore, app_context, pause, selection, reply, Retrieve
    from tests.workflow_fakes import ScriptedWorkflowModel
    from tests.fakes import fake_settings, FAQStub, decode_sse
    store = OwnerStore()
    async with app_context(tmp_path, store=store) as (first, client):
        card, _ = await pause(client)
        original = await first.state.chat_service.graph.aget_state(checkpoint_config('1'))
        assert original.values['context_snapshot'] is None
        with sqlite3.connect(tmp_path / 'resume.sqlite') as sql:
            original_bytes = sql.execute('SELECT checkpoint,metadata FROM checkpoints WHERE thread_id=? AND checkpoint_id=?',
                ('1', original.config['configurable']['checkpoint_id'])).fetchone()
    class EmptyContext:
        async def load(self, cid):
            return ContextAnchors(None, None), ()
    from app.workflow.context_budget import workflow_budget
    config = fake_settings(workflow_checkpoint_path=tmp_path / 'resume.sqlite')
    app = create_app(config,
        model=ScriptedWorkflowModel(intent_replies=[reply({'queries': ['这个能退吗？', '退货政策']})]),
        repository=store, faq_repository=FAQStub(), quality_repository=store, workflow_retriever=Retrieve(),
        context_coordinator=ContextCoordinator(EmptyContext(), Notifications(), None),
        context_budget_provider=lambda registry: workflow_budget(config, registry))
    async with app.router.lifespan_context(app):
        async with httpx.AsyncClient(transport=httpx.ASGITransport(app), base_url='http://localhost') as client:
            response = await client.post('/api/conversations/1/actions/select-order', json=selection(card))
        assert decode_sse(response.text)[-1][0] == 'done'
        final = await app.state.chat_service.graph.aget_state(checkpoint_config('1'))
        assert final.values['context_snapshot_id']
        # LangGraph's state snapshot overlays NULL_TASK_ID pending writes even
        # for an explicit paused checkpoint. Verify the original stored blob.
        old = await app.state.chat_service.checkpointer.aget_tuple(original.config)
        assert old.checkpoint['channel_values']['context_snapshot'] is None
        assert old.checkpoint['channel_values']['messages'] == original.values['messages']
        projected = await app.state.chat_service.graph.aget_state(original.config)
        assert projected.values['context_snapshot_id'] == final.values['context_snapshot_id']
        assert projected.values['messages'] == original.values['messages']
        with sqlite3.connect(tmp_path / 'resume.sqlite') as sql:
            assert sql.execute('SELECT checkpoint,metadata FROM checkpoints WHERE thread_id=? AND checkpoint_id=?',
                ('1', original.config['configurable']['checkpoint_id'])).fetchone() == original_bytes
