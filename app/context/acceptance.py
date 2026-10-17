"""Explicit acceptance-only profiles and durable physical HTTP allowances."""
from contextlib import closing
from collections.abc import Mapping
from pathlib import Path
import re
import sqlite3
from typing import Literal

from app.config import Settings

PROVIDERS = ('glm', 'embedding', 'rerank')
PROFILE_VALUES = {
    'default': dict(model_context_window=128000, max_output_tokens=512, max_user_input_tokens=2000,
                    max_agent_steps=4, agent_max_tool_calls=4, tool_result_max_tokens=1200,
                    rerank_top_k=10, context_target_rounds=40),
    'demo': dict(model_context_window=18000, max_output_tokens=2000, max_user_input_tokens=2000,
                 max_agent_steps=3, agent_max_tool_calls=3, tool_result_max_tokens=1200,
                 rerank_top_k=5, context_target_rounds=40),
}


class AcceptanceLimitExceeded(RuntimeError):
    """No dispatch is permitted after the run's allowance is exhausted."""


class AcceptanceCallCap:
    def __init__(self, run_id: str, limits: Mapping[str, int], ledger_path: Path):
        if not isinstance(run_id, str) or not re.fullmatch(r'[A-Za-z0-9][A-Za-z0-9_-]{0,79}', run_id):
            raise ValueError('Invalid acceptance run id')
        if set(limits) != set(PROVIDERS) or any(type(v) is not int or v < 0 for v in limits.values()):
            raise ValueError('All three nonnegative integer limits are required')
        self.run_id, self.ledger_path = run_id, Path(ledger_path)
        from types import MappingProxyType
        self.limits = MappingProxyType(dict(limits))
        self.ledger_path.parent.mkdir(parents=True, exist_ok=True)
        with closing(self._connect()) as db, db:
            db.execute('CREATE TABLE IF NOT EXISTS acceptance_calls '
                '(run_id TEXT NOT NULL, provider TEXT NOT NULL, ceiling INTEGER NOT NULL, '
                'used INTEGER NOT NULL DEFAULT 0, PRIMARY KEY(run_id, provider))')
            db.execute('BEGIN IMMEDIATE')
            existing = dict(db.execute('SELECT provider,ceiling FROM acceptance_calls WHERE run_id=?', (run_id,)))
            if existing and existing != dict(limits):
                raise ValueError('Existing run limits differ; refusing reset or increase')
            if not existing:
                db.executemany('INSERT INTO acceptance_calls(run_id,provider,ceiling) VALUES (?,?,?)',
                    [(run_id, provider, limits[provider]) for provider in PROVIDERS])

    def _connect(self):
        return sqlite3.connect(self.ledger_path, timeout=10)

    def reserve(self, provider: Literal['glm', 'embedding', 'rerank']) -> None:
        if provider not in PROVIDERS:
            raise ValueError('Unknown provider')
        with closing(self._connect()) as db, db:
            db.execute('BEGIN IMMEDIATE')
            changed = db.execute('UPDATE acceptance_calls SET used=used+1 '
                'WHERE run_id=? AND provider=? AND used<ceiling', (self.run_id, provider)).rowcount
            if changed != 1:
                raise AcceptanceLimitExceeded(f'Acceptance {provider} allowance exhausted')

    def sync_hook(self, provider):
        def hook(request):
            self.reserve(provider)
        return hook

    def async_hook(self, provider):
        async def hook(request):
            # A short atomic local transaction only; never invokes a model.
            self.reserve(provider)
        return hook

    def status(self):
        with closing(self._connect()) as db:
            counts = dict(db.execute('SELECT provider,used FROM acceptance_calls WHERE run_id=?', (self.run_id,)))
        return dict(run_id=self.run_id, limits=dict(self.limits), counts=counts)


def profile_settings(profile: str, *, offline=False, **overrides):
    if profile not in PROFILE_VALUES:
        raise ValueError('Unknown context profile')
    # Init source outranks environment and dotenv, including both step aliases.
    values = dict(PROFILE_VALUES[profile], agent_total_token_budget=32000, **overrides)
    if offline:
        # Explicit fields suppress every env setting: offline replay never loads secrets.
        defaults = {name: field.get_default(call_default_factory=True) for name, field in Settings.model_fields.items()
                    if not field.is_required()}
        values = {**defaults, **values, 'llm_model': 'offline', 'llm_api_key': 'offline',
                  'llm_base_url': 'https://offline.invalid/v1/', 'rerank_min_score': .5}
    config = Settings(_env_file=None if offline else '.env', **values)
    # Acceptance profiles explicitly select the derived cumulative capacity instead
    # of the legacy .env fee. Ordinary load_settings() is unchanged.
    config.__pydantic_fields_set__.discard('agent_total_token_budget')
    return config


def profile_budget(profile):
    from app.context.logging import budget_fields
    from app.workflow.context_budget import workflow_budget, turn_token_limit
    from app.tools.registry import build_registry
    from app.tools.types import ToolContext
    from app.orders.demo import DemoOrderProvider
    settings = profile_settings(profile, offline=True)
    async def owner(conversation_id):
        return 'demo-user'
    registry = build_registry(None, None, ToolContext('1', 0, '', None),
                              order_provider=DemoOrderProvider(), owner_resolver=owner)
    budget = workflow_budget(settings, registry)
    return dict(profile=profile, overrides=PROFILE_VALUES[profile], cumulative_fee='derived; legacy override disabled',
                budget=budget_fields(budget), turn_token_limit=turn_token_limit(settings, budget))


def create_demo_app():
    """Explicit uvicorn factory used only by start-context-demo.ps1."""
    import os
    from app.main import create_app
    profile = os.environ['CONTEXT_DEMO_PROFILE']
    settings = profile_settings(profile, rag_evaluation_enabled=False)
    names = ('CONTEXT_RUN_ID', 'CONTEXT_MAX_GLM_CALLS', 'CONTEXT_MAX_EMBEDDING_CALLS', 'CONTEXT_MAX_RERANK_CALLS')
    values = [os.environ.get(name) for name in names]
    cap = None
    if any(value is not None for value in values):
        if any(value is None for value in values):
            raise ValueError('Acceptance run and all three limits must appear together')
        root = Path(__file__).resolve().parents[2]
        cap = AcceptanceCallCap(values[0], dict(zip(PROVIDERS, map(int, values[1:]))),
                                root/'runtime/context-evidence/call-ledger.sqlite')
    return create_app(settings, acceptance_call_cap=cap, acceptance_profile=profile)
