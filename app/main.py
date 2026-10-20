# FastAPI 应用工厂：组装模型、仓储与工具服务，挂载接口和静态聊天页。
from contextlib import AsyncExitStack, asynccontextmanager
from pathlib import Path
import math
import httpx
from typing import Any

from fastapi import FastAPI, Request
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles

from app.api.chat import router as chat_router
from app.api.chat_actions import router as chat_actions_router
from app.api.order_actions import router as order_actions_router
from app.api.ticket_confirmation import router as ticket_confirmation_router
from app.workflow.ticket_actions import TicketConfirmationService
from app.api.refunds import router as refunds_router
from app.api.conversations import router as conversations_router
from app.api.extract import router as extract_router
from app.api.rag_evaluations import create_router as evaluation_router
from app.rag_evaluation.manager import DATASET_ROOT, RUNTIME_ROOT, RunManager
from app.rag_evaluation.store import RunStore
from app.config import Settings, load_settings
from app.workflow.service import WorkflowChatService
from app.workflow.actions import TicketActionService
from app.workflow.order_actions import OrderActionService
from app.orders.demo import DemoOrderProvider
from app.retrieval.multi import WorkflowRetriever
from app.workflow.agent import build_agent_graph
from app.workflow.graph import build_workflow_graph
from app.workflow.persistence import open_checkpointer, checkpoint_path
from app.core.conversation_locks import ConversationLocks
from app.db.session import Database
from app.repositories.conversations import ConversationRepository
from app.repositories.faq import FAQRepository
from app.knowledge.embeddings import SiliconFlowEmbedder
from app.retrieval.milvus import HybridMilvusIndex
from app.retrieval.query import QueryPlanner
from app.retrieval.rerank import SiliconFlowReranker
from app.retrieval.service import RetrievalService
from app.repositories.knowledge import KnowledgeRepository
from app.core.sufficiency import SufficiencyService
from app.quality.repository import QualityRepository
from app.quality.migration import verify_quality
from app.refunds.migration import verify_refunds
from app.refunds.repository import RefundRepository
from app.refunds.service import RefundActionService
from app.repositories.tickets import TicketRepository
from app.tools.registry import build_registry
from app.tools.registry import build_catalog
from app.tools.policies import PolicyStore
from app.tools.mcp_client import MCPDiscovery, ToolCatalogProvider
from app.tools.executor import ToolExecutor
from app.tool_audit.repository import ToolAuditRepository, BestEffortAuditSink
from app.core.errors import ServiceError
from app.core.extraction import ExtractionService
from app.core.llm import create_model, model_with_output_budget
from app.context.logging import ContextLogger, budget_fields
from app.context.manager import SummaryManager
from app.context.summarizer import SummaryGenerator
from app.context.service import ContextCoordinator
from app.context.history_reader import HistoryReader
from app.context.migration import verify_context
from app.repositories.context import ContextRepository
from app.tools.types import ToolContext


class _UnavailableDatabase:
    """仅仓储注入时不创建连接池；误用数据库工具时安全失败。"""

    # 在未注入数据库时明确拒绝工具访问，返回可展示的服务错误。
    def session(self):
        raise ServiceError("database_unavailable", "数据库工具暂时不可用。", 503)


# 组装 HTTP 应用，按注入情况决定数据库与模型资源的创建和释放责任。
def create_app(
    settings: Settings | None = None, *, model: Any | None = None,
    database: Database | None = None,
    repository: ConversationRepository | None = None,
    faq_repository: FAQRepository | None = None,
    sufficiency_service: SufficiencyService | None = None,
    quality_repository: QualityRepository | None = None,
    evaluation_manager: RunManager | None = None,
    chat_service: Any | None = None,
    checkpointer: Any | None = None,
    order_provider: Any | None = None,
    workflow_retriever: Any | None = None,
    context_coordinator: Any | None = None,
    context_logger: Any | None = None,
    context_repository: Any | None = None,
    context_budget_provider: Any | None = None,
    acceptance_call_cap: Any | None = None,
    acceptance_profile: str | None = None,
    tool_catalog_provider: Any | None = None,
    observability_runtime: Any | None = None,
    flywheel_repository: Any | None = None,
    flywheel_runtime: Any | None = None,
    confidence_rule: Any | None = None,
) -> FastAPI:
    settings = settings if settings is not None else load_settings()
    if acceptance_call_cap is not None and settings.rag_evaluation_enabled:
        raise ValueError('Acceptance cap requires evaluation jobs disabled')
    order_provider = order_provider if order_provider is not None else DemoOrderProvider()
    owns_database = database is None and repository is None
    if not owns_database and database is None:
        database = getattr(repository, "database", None)
        if database is None:
            database = _UnavailableDatabase()
    owns_model = model is None
    owns_checkpointer = chat_service is None and checkpointer is None
    owns_evaluation_manager = evaluation_manager is None
    owns_observability = observability_runtime is None
    owns_flywheel = flywheel_runtime is None
    if (context_budget_provider is None and chat_service is None
            and (owns_database or getattr(database, 'engine', None) is not None or context_repository is not None)):
        from app.workflow.context_budget import workflow_budget
        context_budget_provider = lambda registry: workflow_budget(settings, registry)
    owns_context = context_budget_provider is not None and context_coordinator is None
    owns_context_logger = context_budget_provider is not None and context_logger is None
    if context_coordinator is not None and context_budget_provider is None:
        raise ValueError('Injected context requires an actual budget provider.')
    evaluation_settings = settings.model_copy(deep=True)
    if evaluation_manager is None:
        evaluation_manager = RunManager(RunStore(RUNTIME_ROOT), evaluation_settings, DATASET_ROOT)

    # 注入显式聊天服务，或在官方 saver 就绪后建立默认 Workflow。
    def configure(app: FastAPI):
        app.state.repository = repository
        app.state.database = database
        tickets = TicketRepository(database)
        assessment = sufficiency_service if sufficiency_service is not None else SufficiencyService(
            model_with_output_budget(model, settings, settings.sufficiency_max_output_tokens),
            input_budget=settings.tool_input_token_budget, timeout=settings.sufficiency_timeout_seconds,
            minimum_rerank_score=settings.rerank_min_score,
            mode='content_ablation' if confidence_rule is not None else 'calibrated_score')
        if chat_service is not None:
            app.state.chat_service = chat_service
        elif checkpointer is not None:
            retrieval = workflow_retriever
            if retrieval is None and getattr(faq_repository, 'retriever', None) is not None:
                retrieval = WorkflowRetriever(faq_repository.retriever)
            provider = tool_catalog_provider
            if provider is None and getattr(database, 'engine', None) is not None:
                path = settings.tool_policy_path
                if not path.is_absolute():
                    path = Path(__file__).resolve().parents[1] / path
                provider = ToolCatalogProvider(build_catalog(faq_repository, tickets,
                    order_provider=order_provider, owner_resolver=repository.get_user_id),
                    PolicyStore(path), MCPDiscovery())
            def registry_factory(context):
                if provider is not None:
                    return provider.catalog.snapshot(policy=provider.policies.load()).bind(context)
                return build_registry(faq_repository, tickets, context, order_provider=order_provider,
                    owner_resolver=repository.get_user_id)
            executor = ToolExecutor(settings.tool_timeout_seconds, settings.tool_max_retries,
                overrides={'query_faq': (settings.faq_timeout_seconds, 0)},
                audit_sink=BestEffortAuditSink(ToolAuditRepository(database))) if provider is not None else None
            app.state.chat_service = WorkflowChatService(model, repository,
                registry_factory, ConversationLocks(), settings,
                graph=build_workflow_graph(build_agent_graph(), checkpointer=checkpointer,
                    callbacks=[observability_runtime.handler] if observability_runtime and observability_runtime.handler else None), checkpointer=checkpointer,
                faq_repository=faq_repository, sufficiency_service=assessment, quality_repository=quality_repository,
                order_provider=order_provider, workflow_retriever=retrieval,
                context_coordinator=context_coordinator, context_logger=context_logger,
                context_budget_provider=context_budget_provider, catalog_provider=provider, executor=executor,
                observability=observability_runtime, confidence_rule=confidence_rule)
        service = getattr(app.state, 'chat_service', None)
        app.state.history_reader = HistoryReader(checkpointer if checkpointer is not None else
            getattr(service, 'checkpointer', None), repository)
        from app.flywheel.feedback import FeedbackService
        from app.flywheel.repository import FlywheelRepository
        pool = flywheel_repository
        if pool is None and settings.flywheel_enabled and getattr(database, 'engine', None) is not None:
            pool = FlywheelRepository(database)
        app.state.feedback_service = (FeedbackService(checkpointer if checkpointer is not None else
            getattr(service, 'checkpointer', None), repository, pool) if pool is not None else None)
        from app.flywheel.publication import ReviewService
        app.state.review_service = ReviewService(pool) if settings.flywheel_enabled and pool is not None else None
        # 动作读取同一服务的当前注册表工厂，保留注入与测试的外部资源归属。
        def action_registry(context):
            """按原轮可信上下文复用聊天服务的既有业务工具。"""
            return service.registry_factory(context)

        app.state.ticket_action_service = (TicketActionService(service.graph, service.repository,
            action_registry, service.executor, service.locks)
            if isinstance(service, WorkflowChatService) else None)
        app.state.order_action_service = OrderActionService(service) if isinstance(service, WorkflowChatService) else None
        app.state.ticket_confirmation_service = TicketConfirmationService(service) if isinstance(service, WorkflowChatService) else None
        app.state.refund_action_service = (RefundActionService(service.graph, service.repository,
            RefundRepository(database), service.checkpointer, service.locks)
            if isinstance(service, WorkflowChatService) else None)
        app.state.extraction_service = ExtractionService(model, settings.input_token_budget)

    # 在应用启动时准备依赖，并在退出时按注册顺序的逆序释放资源。
    @asynccontextmanager
    async def lifespan(app: FastAPI):
        nonlocal database, repository, model, faq_repository, sufficiency_service, quality_repository, checkpointer
        nonlocal context_coordinator, context_logger, context_repository
        nonlocal observability_runtime, flywheel_runtime, confidence_rule
        async with AsyncExitStack() as resources:
            if owns_observability:
                from app.observability.runtime import LangfuseRuntime
                observability_runtime = LangfuseRuntime.from_settings(settings)
                resources.push_async_callback(observability_runtime.close)
            app.state.observability_runtime = observability_runtime
            from app.observability.intent_usage import IntentUsageReader
            app.state.intent_usage_reader = IntentUsageReader(observability_runtime.client)
            if owns_context_logger:
                context_logger = ContextLogger(Path(__file__).resolve().parents[1] / 'log' / 'app.log')
                resources.callback(context_logger.close)
            if settings.evidence_confidence_rule_path is not None:
                from app.quality.evidence_confidence import load_online_rule, evidence_budget_fingerprint
                confidence_rule = load_online_rule(settings.evidence_confidence_rule_path,
                    top_k=settings.rerank_top_k, rerank_model=settings.rerank_model,
                    budget_fingerprint=evidence_budget_fingerprint(top_k=settings.rerank_top_k,
                        token_budget=min(6000, (settings.model_context_window + 7)//8)))
            if confidence_rule is None and (settings.rerank_min_score is None or not math.isfinite(settings.rerank_min_score)):
                raise ValueError('online hybrid retrieval requires a calibrated finite threshold')
            if owns_database:
                database = Database(settings.database_url)
                resources.push_async_callback(database.dispose)
            if repository is None:
                repository = ConversationRepository(database)
            if settings.flywheel_enabled and getattr(database, 'engine', None) is not None:
                from app.flywheel.migration import verify_flywheel
                await verify_flywheel(database)
            if owns_model:
                clients = {}
                if acceptance_call_cap is not None:
                    clients['http_client'] = resources.enter_context(httpx.Client(
                        event_hooks={'request': [acceptance_call_cap.sync_hook('glm')]}))
                    clients['http_async_client'] = await resources.enter_async_context(httpx.AsyncClient(
                        event_hooks={'request': [acceptance_call_cap.async_hook('glm')]}))
                # 缺省保持原工厂调用形状；仅在线显式启用低思考时传入额外参数。
                model = (create_model(settings, **clients) if settings.online_reasoning_effort is None else
                         create_model(settings, reasoning_effort=settings.online_reasoning_effort, **clients))
                # 资源按后进先出关闭：异步模型客户端、同步客户端，最后是数据库。
                resources.callback(model.root_client.close)
                resources.push_async_callback(model.root_async_client.close)
            if faq_repository is None:
                embedding_client = rerank_client = None
                if acceptance_call_cap is not None:
                    embedding_client = await resources.enter_async_context(httpx.AsyncClient(
                        event_hooks={'request': [acceptance_call_cap.async_hook('embedding')]}))
                    rerank_client = await resources.enter_async_context(httpx.AsyncClient(
                        event_hooks={'request': [acceptance_call_cap.async_hook('rerank')]}))
                embedder = SiliconFlowEmbedder(settings, **({'http_client': embedding_client} if embedding_client else {}))
                resources.push_async_callback(embedder.aclose)
                index = HybridMilvusIndex(str(settings.milvus_uri), collection=settings.milvus_collection,
                                          timeout=settings.milvus_timeout_seconds)
                resources.push_async_callback(index.aclose)
                await index.ensure_collection(create_if_missing=False)
                reranker = SiliconFlowReranker(settings, **({'http_client': rerank_client} if rerank_client else {}))
                resources.push_async_callback(reranker.aclose)
                planner = QueryPlanner(model_with_output_budget(model, settings, settings.query_max_output_tokens),
                    settings.model_context_window - settings.query_max_output_tokens - max(256, (settings.model_context_window*3+99)//100),
                    timeout=settings.query_timeout_seconds, context_logger=context_logger,
                    output_tokens=settings.query_max_output_tokens)
                retriever = RetrievalService(KnowledgeRepository(database), embedder, index, planner, reranker)
                faq_repository = FAQRepository(database, embedder, index, retriever=retriever)
            if sufficiency_service is None:
                sufficiency_service = SufficiencyService(model_with_output_budget(model, settings, settings.sufficiency_max_output_tokens),
                    input_budget=settings.tool_input_token_budget,
                    timeout=settings.sufficiency_timeout_seconds, minimum_rerank_score=settings.rerank_min_score,
                    mode='content_ablation' if confidence_rule is not None else 'calibrated_score')
            if quality_repository is None:
                quality_repository = QualityRepository(database)
            # 真实数据库即使注入仍核验；纯仓储注入不凭空创建连接池。
            if getattr(database, 'engine', None) is not None:
                await verify_quality(database)
                await verify_refunds(database)
                await verify_context(database)
                # 审计为尽力留痕；只读核验提醒显式迁移，不因审计库故障阻断业务。
                from app.tool_audit.migration import verify_tool_audit
                try:
                    await verify_tool_audit(database)
                except Exception as exc:
                    import logging
                    logging.getLogger(__name__).warning('stage=tool_audit_schema status=unavailable type=%s', type(exc).__name__)
            # 默认禁用不恢复或写历史；注入管理器与注入模型一样由调用方持有。
            if owns_evaluation_manager and evaluation_settings.rag_evaluation_enabled:
                resources.push_async_callback(evaluation_manager.shutdown)
                await evaluation_manager.startup()
            if owns_checkpointer:
                checkpointer = await resources.enter_async_context(open_checkpointer(
                    checkpoint_path(settings, Path(__file__).resolve().parents[1])))
            if owns_context:
                if context_repository is None:
                    if isinstance(database, _UnavailableDatabase):
                        raise ValueError('Injected conversation storage requires an explicit context repository.')
                    context_repository = ContextRepository(database)
                # The default factory and explicit injection share one lifecycle.
                # Registry construction is local; recovery does not execute tools.
                def recovery_budget():
                    registry = app.state.chat_service.registry_factory(ToolContext('0', 0, '', None))
                    return context_budget_provider(registry)
                manager = SummaryManager(context_repository,
                    SummaryGenerator(model, settings, context_logger=context_logger,
                        observability=observability_runtime),
                    budget_provider=recovery_budget, event_logger=context_logger.event if context_logger else None,
                    isolate_task_context=bool(observability_runtime.client))
                context_coordinator = ContextCoordinator(context_repository, manager, settings, context_logger=context_logger)
                resources.push_async_callback(manager.aclose)
            configure(app)
            if chat_service is None:
                # 图任务必须先结束，后进先出的资源栈随后才关闭官方 saver。
                resources.push_async_callback(app.state.chat_service.shutdown)
            app.state.flywheel_runtime = flywheel_runtime
            if settings.flywheel_enabled and (flywheel_runtime is not None or getattr(database, 'engine', None) is not None):
                if owns_flywheel:
                    from app.flywheel.runtime import FlywheelRuntime
                    flywheel_runtime = await FlywheelRuntime.create(settings,
                        database=None if owns_database else database,
                        model=None if owns_model else model, observability=observability_runtime,
                        acceptance_call_cap=acceptance_call_cap)
                app.state.flywheel_runtime = flywheel_runtime
                resources.push_async_callback(flywheel_runtime.close)
                flywheel_runtime.start()
            if owns_context:
                from app.workflow.context_budget import fee_cap_diagnostic
                startup_registry = app.state.chat_service.registry_factory(ToolContext('0', 0, '', None))
                startup_budget = context_budget_provider(startup_registry)
                context_logger.event('context_budget', {'budget': budget_fields(startup_budget),
                    'fee_cap': fee_cap_diagnostic(settings, startup_budget, startup_registry),
                    'config': {key: getattr(settings, key) for key in ('model_context_window',
                        'max_user_input_tokens', 'max_agent_steps', 'tool_result_max_tokens', 'rerank_top_k', 'context_target_rounds')}})
                await manager.startup()
            yield

    app = FastAPI(lifespan=lifespan)
    from app.api.observability import router as observability_router
    app.include_router(observability_router)
    from app.api.feedback import router as feedback_router
    app.include_router(feedback_router)
    from app.api.review_queue import router as review_router
    app.include_router(review_router)
    from app.observability.intent_usage import IntentUsageReader
    app.state.intent_usage_reader = IntentUsageReader(
        observability_runtime.client if observability_runtime else None)
    app.include_router(ticket_confirmation_router)
    app.state.rag_evaluation_settings = evaluation_settings
    app.state.evaluation_manager = evaluation_manager
    app.state.chat_action_allowed_origins = settings.rag_evaluation_allowed_origins
    app.include_router(evaluation_router(evaluation_manager, evaluation_manager.store, evaluation_settings))
    # 支持已注入依赖但刻意不启动 lifespan 的 HTTPX 调用方。
    if repository is None and database is not None:
        repository = ConversationRepository(database)
    if model is not None and repository is not None and faq_repository is not None and not owns_context:
        configure(app)
    app.include_router(conversations_router)
    app.include_router(chat_router)
    app.include_router(chat_actions_router)
    app.include_router(order_actions_router)
    app.include_router(refunds_router)
    app.include_router(extract_router)
    static_dir = Path(__file__).resolve().parent / "static"
    app.mount("/static", StaticFiles(directory=static_dir), name="static")

    # 聊天入口不持久缓存，配合有版本的资源地址避免改版后继续加载旧交互。
    @app.get("/", response_class=FileResponse, include_in_schema=False)
    async def chat_page():
        return FileResponse(static_dir / "index.html", headers={"Cache-Control": "no-store"})

    # 将业务异常转换为统一的错误码、提示和 HTTP 状态。
    @app.exception_handler(ServiceError)
    async def service_error(request: Request, exc: ServiceError):
        return JSONResponse(status_code=exc.status_code, content={"code": exc.code, "message": exc.message})

    # 返回进程存活状态，供健康检查使用。
    @app.get("/health")
    async def health():
        result = {"status": "ok"}
        if acceptance_profile is not None:
            result['context_profile'] = acceptance_profile
        if acceptance_call_cap is not None:
            result['acceptance'] = acceptance_call_cap.status()
        return result

    return app
