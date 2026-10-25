"""One approved physical-call allowance shared by every step09 entry point."""
from pathlib import Path
from app.context.acceptance import AcceptanceCallCap

RUN_ID = 'ch09-local-20261019'


def acceptance_cap(run_id, *, root=None):
    if run_id != RUN_ID:
        raise ValueError('Use the single approved Ch09 acceptance run')
    root = Path(root) if root is not None else Path(__file__).resolve().parents[2]
    return AcceptanceCallCap(RUN_ID, {'glm': 280, 'embedding': 450, 'rerank': 450},
        root / 'runtime/ch09-evidence/call-ledger.sqlite')
