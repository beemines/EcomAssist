"""600 is another append-only limit, not a new or reset budget."""
from contextlib import closing
import sqlite3
import pytest
from tests.test_topic_coverage_budget import previous,amend
from tests.test_topic_budget_amendment import prepared
from app.topics.budget import BudgetError,initialize_budget,APPROVAL_ID


def recover(path):
    from app.topics.budget import amend_recovery_limit,RECOVERY_APPROVAL_ID
    return amend_recovery_limit(path,revision_id=RECOVERY_APPROVAL_ID,
        approval_text='批准600次、仍10元、训练次数不增加')


def test_600_keeps_old_bytes_money_and_unknown_and_stops_at_600(tmp_path):
    path,ledger=prepared(tmp_path);previous(path);amend(path)
    a=ledger.reserve('label','a'*64);ledger.mark_unknown(a.attempt_id,'fixture')
    before={p:p.read_bytes() for p in tmp_path.iterdir() if p.is_file()}
    result=recover(path)
    assert (result.attempt_limit,result.attempts,result.used_micro,result.unknown_attempts,result.limit_micro)==(600,1,1205863,1,10000000)
    assert all(p.read_bytes()==value for p,value in before.items())
    assert recover(path)==result
    with closing(sqlite3.connect(path)) as connection:
        connection.executemany("INSERT INTO attempts(id,stage,payload_hash,reserved_micro,charged_micro,state,created_at) VALUES(?,'label',?,1205863,1,'settled','fixture')",[(f'old-{i}','b'*64) for i in range(1,600)])
        connection.commit()
    with pytest.raises(BudgetError):ledger.reserve('label','c'*64)


@pytest.mark.parametrize('case',['prior','tampered','money','orphan'])
def test_600_refuses_missing_or_changed_authority(tmp_path,case):
    if case=='orphan':
        path=tmp_path/'budget.sqlite3';path.with_suffix('.recovery-approval.json').write_text('{}',encoding='utf-8')
        with pytest.raises(BudgetError):initialize_budget(path,APPROVAL_ID)
        return
    path,ledger=prepared(tmp_path);previous(path)
    if case=='prior':
        with pytest.raises(BudgetError):recover(path)
        return
    amend(path);recover(path)
    if case=='tampered':
        marker=path.with_suffix('.coverage-approval.json');marker.write_bytes(marker.read_bytes()+b' ')
    else:
        marker=path.with_suffix('.recovery-approval.json');marker.write_text(marker.read_text(encoding='utf-8').replace('10000000','20000000'),encoding='utf-8')
    with pytest.raises(BudgetError):ledger.reserve('generate','d'*64)
