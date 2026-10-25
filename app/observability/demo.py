"""Explicit step09 factory: local tracing, real calibrated rule, ordinary mode by default."""
import json
import os
from pathlib import Path
from dotenv import dotenv_values
from app.config import Settings
from app.flywheel.acceptance import acceptance_cap
from app.eval_pipeline.cli import rule_for_settings
from app.observability.runtime import validate_local_langfuse_url

ROOT=Path(__file__).resolve().parents[2]


def load_ch09_settings(root):
    sdk=dict(dotenv_values(root/'runtime/langfuse/sdk.env'))
    required={'LANGFUSE_ENABLED','LANGFUSE_BASE_URL','LANGFUSE_PUBLIC_KEY','LANGFUSE_SECRET_KEY'}
    if set(sdk)!=required or any(not sdk[key] for key in required):
        raise ValueError('Prepare the local Langfuse stack first; SDK configuration is incomplete')
    validate_local_langfuse_url(sdk['LANGFUSE_BASE_URL'])
    path=Path(os.environ.get('CH09_SETTINGS_FILE') or root/'.env')
    if not path.is_absolute(): path=root/path
    rule_path=root/'runtime/ch09-evidence/reference-calibration/rule.json'
    if not rule_path.is_file(): rule_path=root/'runtime/ch09-evidence/calibration/rule.json'
    return Settings(_env_file=path,**sdk,flywheel_enabled=True,eval_pipeline_enabled=True,
        eval_schedule_enabled=False,rag_evaluation_enabled=False,
        workflow_checkpoint_path=root/'runtime/workflow/observability-8006.sqlite',
        evidence_confidence_rule_path=rule_path)


def guard_acceptance_jobs(root):
    manifest=root/'runtime/ch09-evidence/acceptance-owned-jobs.json'
    if manifest.exists():
        data=json.loads(manifest.read_text(encoding='utf-8'))
        if data.get('closed') is not True:
            raise ValueError('Acceptance has unfinished owned jobs; terminalize only those IDs before ordinary mode')


def create_observability_app():
    run_id=os.environ.get('CH09_ACCEPTANCE')
    if not run_id: guard_acceptance_jobs(ROOT)
    cap=acceptance_cap(run_id,root=ROOT) if run_id else None
    settings=load_ch09_settings(ROOT)
    rule=rule_for_settings(settings)
    from app.main import create_app
    return create_app(settings,acceptance_call_cap=cap,confidence_rule=rule,
        context_recover_backlog=False)
