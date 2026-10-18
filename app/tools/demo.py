"""Ordinary demo by default. The explicit page batch has a durable, fixed cap."""
import os
from pathlib import Path
from app.config import load_settings
from app.context.acceptance import AcceptanceCallCap


def create_tool_system_app():
    from app.main import create_app
    settings = load_settings()
    cap = None
    run_id = os.environ.get('TOOL_SYSTEM_ACCEPTANCE')
    if run_id:
        if run_id != 'ch08-page-20261018':
            raise ValueError('Unknown authorized page acceptance batch')
        cap = AcceptanceCallCap(run_id, {'glm': 40, 'embedding': 12, 'rerank': 6},
            Path(__file__).resolve().parents[2] / 'runtime/tool-system-evidence/call-ledger.sqlite')
    return create_app(settings, acceptance_call_cap=cap)
