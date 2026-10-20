"""Managed background resources; injected clients remain caller-owned."""
from contextlib import AsyncExitStack
import asyncio
import httpx
from app.core.llm import create_model, model_with_output_budget
from app.db.session import Database
from app.flywheel.repository import FlywheelRepository
from app.flywheel.processing import FlywheelProcessor, PromptClient
from app.flywheel.worker import FlywheelWorker


class FlywheelRuntime:
    def __init__(self, database, model, settings, *, observability=None, publication_jobs=None):
        self.database, self.model, self._resources = database, model, None
        self.repository = FlywheelRepository(database)
        handler = getattr(observability, 'handler', None)
        prompt_model = model_with_output_budget(model, settings, min(settings.max_output_tokens, 2000))
        prompts = PromptClient(prompt_model, callbacks=[handler] if handler else None)
        self.processor = FlywheelProcessor(self.repository, prompts, observability=observability)
        self.worker = FlywheelWorker(self.processor)
        from app.flywheel.publication import PublicationWorker
        self.publication_worker = (PublicationWorker(self.repository, publication_jobs, observability=observability)
            if publication_jobs is not None else None)

    @classmethod
    async def create(cls, settings, *, database=None, model=None, observability=None, acceptance_call_cap=None,
                     publication_jobs=None, enable_publication=True):
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
            if publication_jobs is None and enable_publication and getattr(database, 'engine', None) is not None:
                from app.knowledge.embeddings import SiliconFlowEmbedder
                from app.retrieval.milvus import HybridMilvusIndex
                from app.repositories.knowledge import KnowledgeRepository
                from app.knowledge.hybrid_jobs import HybridKnowledgeJobs
                hooks = [acceptance_call_cap.async_hook('embedding')] if acceptance_call_cap else []
                http = await resources.enter_async_context(httpx.AsyncClient(event_hooks={'request': hooks}))
                embedder = SiliconFlowEmbedder(settings, http_client=http)
                index = HybridMilvusIndex(str(settings.milvus_uri), collection=settings.milvus_collection,
                    timeout=settings.milvus_timeout_seconds)
                resources.push_async_callback(index.aclose)
                await index.ensure_collection(create_if_missing=False)
                publication_jobs = HybridKnowledgeJobs(KnowledgeRepository(database), embedder, index)
            runtime = cls(database, model, settings, observability=observability, publication_jobs=publication_jobs)
            runtime._resources = resources
            return runtime
        except BaseException:
            await resources.aclose()
            raise

    def start(self):
        self.worker.start()
        if self.publication_worker is not None:
            self.publication_worker.start()

    async def close(self):
        workers = [self.worker, *([self.publication_worker] if self.publication_worker else [])]
        results = await asyncio.gather(*(worker.close(timeout_seconds=30) for worker in workers), return_exceptions=True)
        failures = [result for result in results if isinstance(result, BaseException)]
        if failures:
            # Keep client ownership until every background task is drained.
            raise failures[0]
        if self._resources is not None:
            resources, self._resources = self._resources, None
            await resources.aclose()
