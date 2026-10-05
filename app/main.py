from contextlib import asynccontextmanager
from pathlib import Path
from typing import Any

from fastapi import FastAPI, Request
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles

from app.api.chat import router as chat_router
from app.api.extract import router as extract_router
from app.config import Settings, load_settings
from app.core.chat import ChatService
from app.core.errors import ServiceError
from app.core.extraction import ExtractionService
from app.core.llm import create_model
from app.core.memory import SessionStore


def create_app(
    settings: Settings | None = None, *, model: Any | None = None,
    memory: SessionStore | None = None,
) -> FastAPI:
    settings = settings if settings is not None else load_settings()
    owns_model = model is None
    model = create_model(settings) if owns_model else model
    memory = memory if memory is not None else SessionStore()

    @asynccontextmanager
    async def lifespan(app: FastAPI):
        try:
            yield
        finally:
            if owns_model:
                try:
                    await model.root_async_client.close()
                finally:
                    model.root_client.close()

    app = FastAPI(lifespan=lifespan)
    app.state.chat_service = ChatService(model, memory, settings.input_token_budget)
    app.state.extraction_service = ExtractionService(model, settings.input_token_budget)
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
