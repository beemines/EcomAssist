"""Managed background resources; injected clients remain caller-owned."""
from contextlib import AsyncExitStack
import httpx
from app.core.llm import create_model, model_with_output_budget
from app.db.session import Database
from app.flywheel.repository import FlywheelRepository
from app.flywheel.processing import FlywheelProcessor, PromptClient
from app.flywheel.worker import FlywheelWorker


class FlywheelRuntime:
    def __init__(self, database, model, settings, *, observability=None):
        self.database, self.model, self._resources = database, model, None
        self.repository = FlywheelRepository(database)
        handler = getattr(observability, 'handler', None)
        prompt_model = model_with_output_budget(model, settings, min(settings.max_output_tokens, 2000))
        prompts = PromptClient(prompt_model, callbacks=[handler] if handler else None)
        self.processor = FlywheelProcessor(self.repository, prompts, observability=observability)
        self.worker = FlywheelWorker(self.processor)

    @classmethod
    async def create(cls, settings, *, database=None, model=None, observability=None, acceptance_call_cap=None):
        resources = AsyncExitStack()
        await resources.__aenter__()
        try:
            if observability is None:
                from app.observability.runtime import LangfuseRuntime
                observability = LangfuseRuntime.from_settings(settings)
                resources.push_async_callback(observability.close)
            if database is None:
                database = Database(settings.database_url)
                resources.push_async_callback(database.dispose)
            if getattr(database, 'engine', None) is not None:
                from app.flywheel.migration import verify_flywheel
                await verify_flywheel(database)
            if model is None:
                clients = {}
                if acceptance_call_cap is not None:
                    clients['http_client'] = resources.enter_context(httpx.Client(
                        event_hooks={'request': [acceptance_call_cap.sync_hook('glm')]}))
                    clients['http_async_client'] = await resources.enter_async_context(httpx.AsyncClient(
                        event_hooks={'request': [acceptance_call_cap.async_hook('glm')]}))
                if settings.online_reasoning_effort is not None:
                    clients['reasoning_effort'] = settings.online_reasoning_effort
                model = create_model(settings, **clients)
                resources.callback(model.root_client.close)
                resources.push_async_callback(model.root_async_client.close)
            runtime = cls(database, model, settings, observability=observability)
            runtime._resources = resources
            return runtime
        except BaseException:
            await resources.aclose()
            raise

    def start(self):
        self.worker.start()

    async def close(self):
        try:
            await self.worker.close(timeout_seconds=30)
        finally:
            if self._resources is not None:
                resources, self._resources = self._resources, None
                await resources.aclose()
