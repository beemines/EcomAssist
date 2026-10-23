"""Explicit 8007 demo factory; never starts classification or paid recovery jobs."""
import os
import asyncio
from pathlib import Path
from fastapi import Request
from fastapi.responses import HTMLResponse

from app.config import load_settings
from app.topics.profile import load_profile
from app.topics.budget import EVIDENCE_ROOT
from app.topics.review_submission import TopicReviewService
from app.api.review_queue import guard_read

ROOT=Path(__file__).resolve().parents[2]


def select_review_root(value):
    base=EVIDENCE_ROOT.resolve();selected=Path(value).resolve() if value else base
    if selected not in (base,base/'remediation-v2',base/'negation-v4'):raise ValueError('Unknown review evidence root')
    return selected


def create_review_app():
    """An isolated human-review surface: no settings, model, DB or background jobs."""
    from fastapi import FastAPI,APIRouter
    from app.api.topics import router as topic_routes
    from app.api.review_queue import ReviewRoute
    root=select_review_root(os.environ.get('CH10_REVIEW_ROOT'))
    app=FastAPI(docs_url=None,redoc_url=None,openapi_url=None)
    app.state.chat_action_allowed_origins=[]
    app.state.background_tasks_enabled=False
    app.state.topic_test_review_service=TopicReviewService(root/'test-review')
    app.state.topic_error_review_service=TopicReviewService(root/'error-review')
    if root.name=='negation-v4':app.state.topic_review_service=TopicReviewService(root/'train-review')
    app.include_router(topic_routes)
    pages=APIRouter(route_class=ReviewRoute)
    @pages.get('/health')
    async def health():return dict(kind='local-topic-human-review',database_connections=0,paid_background=False)
    def register(path,attribute,purpose):
        async def page(request:Request):
            service=getattr(app.state,attribute)
            try:
                if (await asyncio.to_thread(service.pack)).purpose!=purpose:raise ValueError('Wrong pack purpose')
                html=await asyncio.to_thread(service.render)
            except FileNotFoundError:
                return HTMLResponse('<meta charset="utf-8"><p>本轮样本尚未生成。</p>',status_code=404)
            return HTMLResponse(html,headers={'Cache-Control':'no-store','X-Content-Type-Options':'nosniff'})
        pages.add_api_route(path,page,response_class=HTMLResponse,name=attribute)
    register('/topics/test-review','topic_test_review_service','test')
    register('/topics/error-review','topic_error_review_service','errors')
    if root.name=='negation-v4':register('/topics/pilot-review','topic_review_service','pilot')
    app.include_router(pages)
    return app


def create_app():
    path=os.environ.get('CH10_ENV_FILE')
    if not path:
        raise ValueError('CH10_ENV_FILE must explicitly select the existing application configuration')
    settings=load_settings(env_file=Path(path)).model_copy(update=dict(flywheel_enabled=True,eval_pipeline_enabled=False,
        eval_schedule_enabled=False,rag_evaluation_enabled=False,
        workflow_checkpoint_path=ROOT/'runtime/workflow/ch10-checkpoints.sqlite'))
    profile_path=os.environ.get('CH10_TOPIC_PROFILE')
    profile=load_profile(Path(profile_path)) if profile_path else None
    from app.main import create_app as application
    app = application(settings,topic_profile=profile,background_tasks_enabled=False,context_recover_backlog=False)
    app.state.topic_review_service = TopicReviewService(EVIDENCE_ROOT / 'pilot')
    review_root=select_review_root(os.environ.get('CH10_REVIEW_ROOT'))
    app.state.topic_test_review_service = TopicReviewService(review_root / 'test-review')
    app.state.topic_error_review_service = TopicReviewService(review_root / 'error-review')

    @app.get('/topics/pilot-review', response_class=HTMLResponse)
    async def pilot_review(request: Request):
        guard_read(request)
        html = await asyncio.to_thread(app.state.topic_review_service.render)
        return HTMLResponse(html, headers={'Cache-Control': 'no-store', 'X-Content-Type-Options': 'nosniff'})

    def register_review_page(path,attribute,purpose):
        async def page(request:Request):
            guard_read(request)
            service=getattr(app.state,attribute)
            try:
                if (await asyncio.to_thread(service.pack)).purpose!=purpose:
                    raise ValueError('Wrong review-pack purpose')
                html=await asyncio.to_thread(service.render)
            except FileNotFoundError:
                return HTMLResponse('<meta charset="utf-8"><p>复核样本尚未生成，请等实际训练与评测完成。</p>',status_code=404)
            return HTMLResponse(html,headers={'Cache-Control':'no-store','X-Content-Type-Options':'nosniff'})
        app.add_api_route(path,page,response_class=HTMLResponse,name=attribute)
    register_review_page('/topics/test-review','topic_test_review_service','test')
    register_review_page('/topics/error-review','topic_error_review_service','errors')

    return app
