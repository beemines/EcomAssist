"""Explicit 8007 demo factory; never starts classification or paid recovery jobs."""
import os
from pathlib import Path

from app.config import load_settings
from app.topics.profile import load_profile

ROOT=Path(__file__).resolve().parents[2]


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
    return application(settings,topic_profile=profile,background_tasks_enabled=False,context_recover_backlog=False)
