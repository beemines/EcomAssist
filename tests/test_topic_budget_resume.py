"""A diagnosed circuit pause may be rearmed explicitly, without refunding history."""
import json
import sqlite3
import pytest
from app.topics.budget import BudgetError,Usage
from tests.test_topic_teacher import ledger_for


def pause(ledger):
    ids=[]
    for _ in range(3):
        row=ledger.reserve('label','a'*64);ids.append(row.attempt_id)
        ledger.settle(row.attempt_id,Usage(prompt_tokens=1000,completion_tokens=200,total_tokens=1200))
        ledger.record_outcome(row.attempt_id,success=False)
    return tuple(reversed(ids))


def test_explicit_diagnosis_rearms_once_without_changing_attempts_or_money(tmp_path):
    ledger=ledger_for(tmp_path);ids=pause(ledger);before=ledger.summary()
    with sqlite3.connect(ledger.path) as db:prior=db.execute('SELECT * FROM attempts ORDER BY id').fetchall()
    ledger.resume_after_diagnosis(expected_failure_ids=ids,reason='Fixed per-item isolation; all local regressions green',evidence_sha256='b'*64)
    after=ledger.summary()
    assert after.attempts==before.attempts==3 and after.used_micro==before.used_micro
    assert after.remaining_micro==before.remaining_micro and not after.paused and after.consecutive_failures==0
    with sqlite3.connect(ledger.path) as db:
        assert db.execute('SELECT * FROM attempts ORDER BY id').fetchall()==prior
        event=db.execute('SELECT failure_ids,prior_failures,used_micro,evidence_sha256 FROM diagnostic_resumes').fetchone()
        assert json.loads(event[0])==list(ids) and event[1:]==(3,before.used_micro,'b'*64)
    with pytest.raises(BudgetError):
        ledger.resume_after_diagnosis(expected_failure_ids=ids,reason='Same event cannot be replayed',evidence_sha256='b'*64)
    ledger.reserve('generate','c'*64)


@pytest.mark.parametrize('kind',['stale_ids','active_request','no_pause','empty_reason','bad_evidence','money_exhausted','attempts_exhausted'])
def test_diagnosis_cannot_reset_spending_caps_or_ignore_active_requests(tmp_path,kind):
    ledger=ledger_for(tmp_path)
    active=ledger.reserve('generate','d'*64) if kind=='active_request' else None
    ids=pause(ledger) if kind!='no_pause' else ('1'*32,'2'*32,'3'*32)
    reason='Diagnosed fixture failure';evidence='b'*64
    if kind=='stale_ids':ids=('0'*32,)+ids[1:]
    elif kind=='empty_reason':reason=' '
    elif kind=='bad_evidence':evidence='not-a-hash'
    elif kind=='money_exhausted':
        with sqlite3.connect(ledger.path) as db:
            for i in range(8):
                db.execute("INSERT INTO attempts(id,stage,payload_hash,reserved_micro,charged_micro,state,outcome,created_at,finished_at) VALUES(?,?,?,?,?,'settled',1,?,?)",
                    (f'money{i}','label','a'*64,1205863,1205863,'2020-01-01','2020-01-01'))
    elif kind=='attempts_exhausted':
        with sqlite3.connect(ledger.path) as db:
            for i in range(297):
                db.execute("INSERT INTO attempts(id,stage,payload_hash,reserved_micro,charged_micro,state,outcome,created_at,finished_at) VALUES(?,?,?,?,?,'settled',1,?,?)",
                    (f'cap{i}','label','a'*64,1205863,0,'2020-01-01','2020-01-01'))
    before=ledger.summary()
    with pytest.raises(BudgetError):ledger.resume_after_diagnosis(expected_failure_ids=ids,reason=reason,evidence_sha256=evidence)
    assert ledger.summary()==before
