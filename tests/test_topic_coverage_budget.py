"""The approved560 revision adds a marker, never resets money or earlier calls."""
from contextlib import closing
import json
import sqlite3
import pytest
from app.topics.budget import BudgetError,initialize_budget,APPROVAL_ID
from tests.test_topic_budget_amendment import prepared,with_450


def previous(path):
    from app.topics.budget import amend_negation_limit,NEGATION_APPROVAL_ID,NEGATION_APPROVAL_TEXT
    with_450(path)
    amend_negation_limit(path,revision_id=NEGATION_APPROVAL_ID,approval_text=NEGATION_APPROVAL_TEXT)


def amend(path):
    from app.topics.budget import amend_coverage_limit,COVERAGE_APPROVAL_ID
    return amend_coverage_limit(path,revision_id=COVERAGE_APPROVAL_ID,
        approval_text='批准该修复，累计560次、仍10元、一次重训')


def test_560_preserves_500_marker_money_unknown_and_sql_bytes(tmp_path):
    path,ledger=prepared(tmp_path);previous(path)
    a=ledger.reserve('label','a'*64);ledger.mark_unknown(a.attempt_id,'fixture_unknown')
    before=path.read_bytes()
    markers={s:path.with_suffix(s).read_bytes() for s in ('.approval.json','.attempt-approval.json','.remediation-approval.json','.negation-approval.json')}
    result=amend(path)
    assert (result.attempt_limit,result.limit_micro,result.attempts,result.unknown_attempts,result.used_micro)==(560,10_000_000,1,1,1205863)
    assert path.read_bytes()==before
    assert all(path.with_suffix(s).read_bytes()==b for s,b in markers.items())
    assert amend(path)==result
    with closing(sqlite3.connect(path)) as c:
        c.executemany("INSERT INTO attempts(id,stage,payload_hash,reserved_micro,charged_micro,state,created_at) VALUES(?,'label',?,1205863,1,'settled','fixture')",[(f'fixture-{i}','b'*64) for i in range(1,560)])
        c.commit()
    assert ledger.summary().attempts==560
    with pytest.raises(BudgetError):ledger.reserve('generate','c'*64)


@pytest.mark.parametrize('change',['missing_previous','changed_previous','money','wrong_text'])
def test_560_rejects_wrong_authorization_or_broken_chain(tmp_path,change):
    from app.topics.budget import amend_coverage_limit,COVERAGE_APPROVAL_ID
    path,ledger=prepared(tmp_path)
    if change=='missing_previous':
        with pytest.raises(BudgetError):amend(path)
        return
    previous(path)
    if change=='wrong_text':
        with pytest.raises(BudgetError):amend_coverage_limit(path,revision_id=COVERAGE_APPROVAL_ID,approval_text='继续')
        return
    amend(path)
    if change=='changed_previous':
        p=path.with_suffix('.negation-approval.json');p.write_bytes(p.read_bytes()+b' ')
    else:
        p=path.with_suffix('.coverage-approval.json');v=json.loads(p.read_text(encoding='utf-8'));v['limit_micro']='20000000';p.write_text(json.dumps(v),encoding='utf-8')
    with pytest.raises(BudgetError):ledger.reserve('label','d'*64)


def test_orphan_560_marker_never_creates_a_new_budget(tmp_path):
    path=tmp_path/'budget.sqlite3';path.with_suffix('.coverage-approval.json').write_text('{}',encoding='utf-8')
    with pytest.raises(BudgetError):initialize_budget(path,APPROVAL_ID)
