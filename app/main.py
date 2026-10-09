# FastAPI 应用工厂：组装模型、仓储与工具服务，挂载接口和静态聊天页。
from contextlib import AsyncExitStack, asynccontextmanager
from pathlib import Path
import math
from typing import Any

from fastapi import FastAPI, Request
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles

from app.api.chat import router as chat_router
from app.api.conversations import router as conversations_router
from app.api.extract import router as extract_router
from app.config import Settings, load_settings
from app.core.tool_chat import ToolChatService
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
) -> FastAPI:
    settings = settings if settings is not None else load_settings()
    owns_database = database is None and repository is None
    if not owns_database and database is None:
        database = getattr(repository, "database", None)
        if database is None:
            database = _UnavailableDatabase()
    owns_model = model is None

    # 将仓储、工具对话服务和结构化抽取服务注入应用状态。
    def configure(app: FastAPI):
        app.state.repository = repository
        app.state.database = database
        tickets = TicketRepository(database)
        assessment = sufficiency_service if sufficiency_service is not None else SufficiencyService(
            model_with_output_budget(model, settings, settings.sufficiency_max_output_tokens),
            input_budget=settings.tool_input_token_budget, timeout=settings.sufficiency_timeout_seconds,
            minimum_rerank_score=settings.rerank_min_score)
        app.state.chat_service = ToolChatService(model, repository,
            lambda context: build_registry(faq_repository, tickets, context), ConversationLocks(), settings,
            sufficiency_service=assessment, quality_repository=quality_repository)
        app.state.extraction_service = ExtractionService(model, settings.input_token_budget)

    # 在应用启动时准备依赖，并在退出时按注册顺序的逆序释放资源。
    @asynccontextmanager
    async def lifespan(app: FastAPI):
        nonlocal database, repository, model, faq_repository, sufficiency_service, quality_repository
        async with AsyncExitStack() as resources:
            if settings.rerank_min_score is None or not math.isfinite(settings.rerank_min_score):
                raise ValueError('online hybrid retrieval requires a calibrated finite threshold')
            if owns_database:
                database = Database(settings.database_url)
                resources.push_async_callback(database.dispose)
            if repository is None:
                repository = ConversationRepository(database)
            if owns_model:
                model = create_model(settings)
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
            configure(app)
            yield

    app = FastAPI(lifespan=lifespan)
    # 支持已注入依赖但刻意不启动 lifespan 的 HTTPX 调用方。
    if repository is None and database is not None:
        repository = ConversationRepository(database)
    if model is not None and repository is not None and faq_repository is not None:
        configure(app)
    app.include_router(conversations_router)
    app.include_router(chat_router)
    app.include_router(extract_router)
    static_dir = Path(__file__).resolve().parent / "static"
    app.mount("/static", StaticFiles(directory=static_dir), name="static")

    # 返回静态聊天页面，作为应用首页。
    @app.get("/", response_class=FileResponse, include_in_schema=False)
    async def chat_page():
        return FileResponse(static_dir / "index.html")

    # 将业务异常转换为统一的错误码、提示和 HTTP 状态。
    @app.exception_handler(ServiceError)
    async def service_error(request: Request, exc: ServiceError):
        return JSONResponse(status_code=exc.status_code, content={"code": exc.code, "message": exc.message})

    # 返回进程存活状态，供健康检查使用。
    @app.get("/health")
    async def health():
        return {"status": "ok"}

    return app
