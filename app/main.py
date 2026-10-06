from contextlib import asynccontextmanager
from pathlib import Path
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
from app.repositories.tickets import TicketRepository
from app.tools.registry import build_registry
from app.core.errors import ServiceError
from app.core.extraction import ExtractionService
from app.core.llm import create_model


class _UnavailableDatabase:
    """仅仓储注入时不创建连接池；误用数据库工具时安全失败。"""

    def session(self):
        raise ServiceError("database_unavailable", "数据库工具暂时不可用。", 503)


def create_app(
    settings: Settings | None = None, *, model: Any | None = None,
    database: Database | None = None,
    repository: ConversationRepository | None = None,
) -> FastAPI:
    settings = settings if settings is not None else load_settings()
    owns_database = database is None and repository is None
    if owns_database:
        database = Database(settings.database_url)
    elif database is None:
        database = getattr(repository, "database", None)
        if database is None:
            database = _UnavailableDatabase()
    repository = repository if repository is not None else ConversationRepository(database)
    owns_model = model is None
    model = create_model(settings) if owns_model else model

    @asynccontextmanager
    async def lifespan(app: FastAPI):
        try:
            yield
        finally:
            try:
                if owns_model:
                    try:
                        await model.root_async_client.close()
                    finally:
                        model.root_client.close()
            finally:
                if owns_database:
                    await database.dispose()

    app = FastAPI(lifespan=lifespan)
    app.state.repository = repository
    app.state.database = database
    faq, tickets = FAQRepository(database), TicketRepository(database)
    app.state.chat_service = ToolChatService(model, repository,
        lambda context: build_registry(faq, tickets, context), ConversationLocks(), settings)
    app.state.extraction_service = ExtractionService(model, settings.input_token_budget)
    app.include_router(conversations_router)
    app.include_router(chat_router)
    app.include_router(extract_router)
    static_dir = Path(__file__).resolve().parent / "static"
    app.mount("/static", StaticFiles(directory=static_dir), name="static")

    @app.get("/", response_class=FileResponse, include_in_schema=False)
    async def chat_page():
        return FileResponse(static_dir / "index.html")

    @app.exception_handler(ServiceError)
    async def service_error(request: Request, exc: ServiceError):
        return JSONResponse(status_code=exc.status_code, content={"code": exc.code, "message": exc.message})

    @app.get("/health")
    async def health():
        return {"status": "ok"}

    return app
