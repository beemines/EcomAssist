# FastAPI 应用工厂：组装模型、仓储与工具服务，挂载接口和静态聊天页。
from contextlib import AsyncExitStack, asynccontextmanager
from pathlib import Path
import math
from typing import Any

from fastapi import FastAPI, Request
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles

from app.api.chat import router as chat_router
from app.api.chat_actions import router as chat_actions_router
from app.api.conversations import router as conversations_router
from app.api.extract import router as extract_router
from app.api.rag_evaluations import create_router as evaluation_router
from app.rag_evaluation.manager import DATASET_ROOT, RUNTIME_ROOT, RunManager
from app.rag_evaluation.store import RunStore
from app.config import Settings, load_settings
from app.workflow.service import WorkflowChatService
from app.workflow.actions import TicketActionService
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
from app.repositories.tickets import TicketRepository
from app.tools.registry import build_registry
from app.core.errors import ServiceError
from app.core.extraction import ExtractionService
from app.core.llm import create_model, model_with_output_budget


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
) -> FastAPI:
    settings = settings if settings is not None else load_settings()
    owns_database = database is None and repository is None
    if not owns_database and database is None:
        database = getattr(repository, "database", None)
        if database is None:
            database = _UnavailableDatabase()
    owns_model = model is None
    owns_checkpointer = chat_service is None and checkpointer is None
    owns_evaluation_manager = evaluation_manager is None
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
            minimum_rerank_score=settings.rerank_min_score)
        if chat_service is not None:
            app.state.chat_service = chat_service
        elif checkpointer is not None:
            app.state.chat_service = WorkflowChatService(model, repository,
                lambda context: build_registry(faq_repository, tickets, context), ConversationLocks(), settings,
                graph=build_workflow_graph(build_agent_graph(), checkpointer=checkpointer), checkpointer=checkpointer,
                faq_repository=faq_repository, sufficiency_service=assessment, quality_repository=quality_repository)
        service = getattr(app.state, 'chat_service', None)
        # 动作读取同一服务的当前注册表工厂，保留注入与测试的外部资源归属。
        def action_registry(context):
            """按原轮可信上下文复用聊天服务的既有业务工具。"""
            return service.registry_factory(context)

        app.state.ticket_action_service = (TicketActionService(service.graph, service.repository,
            action_registry, service.executor, service.locks)
            if isinstance(service, WorkflowChatService) else None)
        app.state.extraction_service = ExtractionService(model, settings.input_token_budget)

    # 在应用启动时准备依赖，并在退出时按注册顺序的逆序释放资源。
    @asynccontextmanager
    async def lifespan(app: FastAPI):
        nonlocal database, repository, model, faq_repository, sufficiency_service, quality_repository, checkpointer
        async with AsyncExitStack() as resources:
            if settings.rerank_min_score is None or not math.isfinite(settings.rerank_min_score):
                raise ValueError('online hybrid retrieval requires a calibrated finite threshold')
            if owns_database:
                database = Database(settings.database_url)
                resources.push_async_callback(database.dispose)
            if repository is None:
                repository = ConversationRepository(database)
            if owns_model:
                # 缺省保持原工厂调用形状；仅在线显式启用低思考时传入额外参数。
                model = (create_model(settings) if settings.online_reasoning_effort is None else
                         create_model(settings, reasoning_effort=settings.online_reasoning_effort))
                # 资源按后进先出关闭：异步模型客户端、同步客户端，最后是数据库。
                resources.callback(model.root_client.close)
                resources.push_async_callback(model.root_async_client.close)
            if faq_repository is None:
                embedder = SiliconFlowEmbedder(settings)
                resources.push_async_callback(embedder.aclose)
                index = HybridMilvusIndex(str(settings.milvus_uri), collection=settings.milvus_collection,
                                          timeout=settings.milvus_timeout_seconds)
                resources.push_async_callback(index.aclose)
                await index.ensure_collection(create_if_missing=False)
                reranker = SiliconFlowReranker(settings)
                resources.push_async_callback(reranker.aclose)
                planner = QueryPlanner(model_with_output_budget(model, settings, settings.query_max_output_tokens),
                    settings.tool_input_token_budget, timeout=settings.query_timeout_seconds)
                retriever = RetrievalService(KnowledgeRepository(database), embedder, index, planner, reranker)
                faq_repository = FAQRepository(database, embedder, index, retriever=retriever)
            if sufficiency_service is None:
                sufficiency_service = SufficiencyService(model_with_output_budget(model, settings, settings.sufficiency_max_output_tokens),
                    input_budget=settings.tool_input_token_budget,
                    timeout=settings.sufficiency_timeout_seconds, minimum_rerank_score=settings.rerank_min_score)
            if quality_repository is None:
                quality_repository = QualityRepository(database)
            # 真实数据库即使注入仍核验；纯仓储注入不凭空创建连接池。
            if getattr(database, 'engine', None) is not None:
                await verify_quality(database)
            # 默认禁用不恢复或写历史；注入管理器与注入模型一样由调用方持有。
            if owns_evaluation_manager and evaluation_settings.rag_evaluation_enabled:
                resources.push_async_callback(evaluation_manager.shutdown)
                await evaluation_manager.startup()
            if owns_checkpointer:
                checkpointer = await resources.enter_async_context(open_checkpointer(
                    checkpoint_path(settings, Path(__file__).resolve().parents[1])))
            configure(app)
            if chat_service is None:
                # 图任务必须先结束，后进先出的资源栈随后才关闭官方 saver。
                resources.push_async_callback(app.state.chat_service.shutdown)
            yield

    app = FastAPI(lifespan=lifespan)
    app.state.rag_evaluation_settings = evaluation_settings
    app.state.evaluation_manager = evaluation_manager
    app.state.chat_action_allowed_origins = settings.rag_evaluation_allowed_origins
    app.include_router(evaluation_router(evaluation_manager, evaluation_manager.store, evaluation_settings))
    # 支持已注入依赖但刻意不启动 lifespan 的 HTTPX 调用方。
    if repository is None and database is not None:
        repository = ConversationRepository(database)
    if model is not None and repository is not None and faq_repository is not None:
        configure(app)
    app.include_router(conversations_router)
    app.include_router(chat_router)
    app.include_router(chat_actions_router)
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
        return {"status": "ok"}

    return app
