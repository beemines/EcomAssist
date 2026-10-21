import asyncio
from types import SimpleNamespace
import pytest
from app.flywheel.worker import FlywheelWorker
from tests.fakes import fake_settings, decode_sse
from tests.test_flywheel_processing import JsonModel


async def test_runtime_does_not_close_explicitly_borrowed_model_or_database():
    from app.flywheel.runtime import FlywheelRuntime
    class Database:
        closed = False
        async def dispose(self): self.closed = True
    database, model = Database(), JsonModel([])
    runtime = await FlywheelRuntime.create(fake_settings(), database=database, model=model)
    await runtime.close()
    await runtime.close()
    assert not database.closed and not model.calls


async def test_runtime_closes_owned_clients_before_owned_database(monkeypatch):
    from app.flywheel import runtime as module
    events = []
    class Database:
        def __init__(self, url): pass
        async def dispose(self): events.append('database')
    class Model(JsonModel):
        def __init__(self):
            super().__init__([])
            self.root_client = SimpleNamespace(close=lambda: events.append('model-sync'))
            async def close(): events.append('model-async')
            self.root_async_client = SimpleNamespace(close=close)
    monkeypatch.setattr(module, 'Database', Database)
    monkeypatch.setattr(module, 'create_model', lambda settings, **kwargs: Model())
    runtime = await module.FlywheelRuntime.create(fake_settings(mysql_password='owned-test'))
    await runtime.close()
    assert events == ['model-async', 'model-sync', 'database']


async def test_two_chat_conversations_do_not_wait_for_background_model(tmp_path):
    from tests.test_workflow_api import workflow_app, Store, request
    from app.main import create_app
    from unittest.mock import patch
    started, cancelled = asyncio.Event(), asyncio.Event()
    class Repo:
        async def next_pending_id(self, now): return '1'
    class Processor:
        repository = Repo()
        async def recover(self): return True
        async def process(self, identifier):
            started.set()
            try: await asyncio.Event().wait()
            finally: cancelled.set()
    worker = FlywheelWorker(Processor(), poll_seconds=.01)
    class Runtime:
        def start(self): worker.start()
        async def close(self): await worker.close(timeout_seconds=.01)
    # Keep the existing test factory's resources and actual Workflow lifecycle.
    def app_factory(*args, **kwargs):
        return create_app(*args, flywheel_runtime=Runtime(), **kwargs)
    store = Store()
    store.users['2'] = 'test'
    with patch('tests.test_workflow_api.create_app', app_factory):
        async with workflow_app(tmp_path, store=store, flywheel_enabled=True) as app:
            await asyncio.wait_for(started.wait(), 2)
            async with asyncio.timeout(3):
                first = await request(app, '你好')
                import httpx
                async with httpx.AsyncClient(transport=httpx.ASGITransport(app), base_url='http://test') as client:
                    second = await client.post('/api/chat', json={'conversation_id': '2', 'message': '你好'})
            assert decode_sse(first.text)[-1][0] == decode_sse(second.text)[-1][0] == 'done'
            assert not cancelled.is_set()
    assert cancelled.is_set() and not worker.tasks
