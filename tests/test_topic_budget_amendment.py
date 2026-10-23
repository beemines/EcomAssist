"""A human-approved attempt amendment never raises money or resets prior history."""
from contextlib import closing
import json
import sqlite3
import pytest
from app.topics.budget import (APPROVAL_ID,ATTEMPT_EXTENSION_ID,BudgetLedger,BudgetError,
    initialize_budget,amend_budget_attempt_limit)


TEXT='允许400次，费用仍最多10元'


def prepared(tmp_path,name='budget'):
    path=tmp_path/(name+'.sqlite3');initialize_budget(path,APPROVAL_ID)
    return path,BudgetLedger(path,APPROVAL_ID)


def test_amendment_is_additive_idempotent_and_does_not_clear_money_or_unknowns(tmp_path):
    path,ledger=prepared(tmp_path)
    attempt=ledger.reserve('label','a'*64);ledger.mark_unknown(attempt.attempt_id,'fixture_unknown')
    before=ledger.summary();marker=path.with_suffix('.approval.json').read_bytes()
    with closing(sqlite3.connect(path)) as connection:
        records=connection.execute('SELECT * FROM attempts').fetchall()
        metadata=connection.execute('SELECT * FROM metadata ORDER BY key').fetchall()
    after=amend_budget_attempt_limit(path,revision_id=ATTEMPT_EXTENSION_ID,approval_text=TEXT)
    assert after.attempt_limit==400 and after.limit_micro==10_000_000
    assert (after.attempts,after.unknown_attempts,after.used_micro)==(before.attempts,before.unknown_attempts,before.used_micro)
    assert path.with_suffix('.approval.json').read_bytes()==marker
    with closing(sqlite3.connect(path)) as connection:
        assert connection.execute('SELECT * FROM attempts').fetchall()==records
        assert connection.execute('SELECT * FROM metadata ORDER BY key').fetchall()==metadata
    extension=path.with_suffix('.attempt-approval.json').read_bytes()
    assert amend_budget_attempt_limit(path,revision_id=ATTEMPT_EXTENSION_ID,approval_text=TEXT)==after
    assert path.with_suffix('.attempt-approval.json').read_bytes()==extension


def test_current_300_count_halts_before_amendment_and_new_cap_is_400(tmp_path):
    path,ledger=prepared(tmp_path)
    with closing(sqlite3.connect(path)) as connection:
        connection.executemany("INSERT INTO attempts(id,stage,payload_hash,reserved_micro,charged_micro,state,created_at) "
            "VALUES(?,'label',?,1205863,1,'settled','fixture')",[(f'fixture-{i}','a'*64) for i in range(300)])
        connection.commit()
    assert ledger.summary().paused and ledger.summary().attempt_limit==300
    with pytest.raises(BudgetError):ledger.reserve('label','b'*64)
    amend_budget_attempt_limit(path,revision_id=ATTEMPT_EXTENSION_ID,approval_text=TEXT)
    assert not ledger.summary().paused
    reservation=ledger.reserve('label','b'*64)
    assert ledger.summary().attempts==301
    with closing(sqlite3.connect(path)) as connection:
        connection.executemany("INSERT INTO attempts(id,stage,payload_hash,reserved_micro,charged_micro,state,created_at) "
            "VALUES(?,'label',?,1205863,1,'settled','fixture')",[(f'fixture-{i}','a'*64) for i in range(301,400)])
        connection.commit()
    assert ledger.summary().attempts==400
    with pytest.raises(BudgetError):ledger.reserve('label','c'*64)


@pytest.mark.parametrize('kind',['wrong_ledger','money','count','revision'])
def test_wrong_or_tampered_extension_fails_closed(tmp_path,kind):
    path,ledger=prepared(tmp_path)
    amend_budget_attempt_limit(path,revision_id=ATTEMPT_EXTENSION_ID,approval_text=TEXT)
    extension=path.with_suffix('.attempt-approval.json')
    value=json.loads(extension.read_text(encoding='utf-8'))
    key,changed={'wrong_ledger':('ledger_id','0'*32),'money':('limit_micro','20000000'),
        'count':('attempt_limit','401'),'revision':('revision_id','unapproved')}[kind]
    value[key]=changed;extension.write_text(json.dumps(value),encoding='utf-8')
    with pytest.raises(BudgetError):ledger.reserve('label','a'*64)


def test_second_human_amendment_binds_first_without_mutating_any_history(tmp_path):
    from app.topics.budget import amend_remediation_limit,REMEDIATION_APPROVAL_ID,REMEDIATION_APPROVAL_TEXT
    path,ledger=prepared(tmp_path)
    with pytest.raises(BudgetError):amend_remediation_limit(path,revision_id=REMEDIATION_APPROVAL_ID,approval_text=REMEDIATION_APPROVAL_TEXT)
    amend_budget_attempt_limit(path,revision_id=ATTEMPT_EXTENSION_ID,approval_text=TEXT)
    attempt=ledger.reserve('label','a'*64);ledger.mark_unknown(attempt.attempt_id,'fixture_unknown')
    first=path.with_suffix('.attempt-approval.json').read_bytes();original=path.with_suffix('.approval.json').read_bytes()
    before=path.read_bytes()
    after=amend_remediation_limit(path,revision_id=REMEDIATION_APPROVAL_ID,approval_text=REMEDIATION_APPROVAL_TEXT)
    assert after.attempt_limit==450 and after.attempts==1 and after.used_micro==1205863 and after.unknown_attempts==1
    assert after.limit_micro==10000000 and path.read_bytes()==before
    assert path.with_suffix('.attempt-approval.json').read_bytes()==first and path.with_suffix('.approval.json').read_bytes()==original
    assert amend_remediation_limit(path,revision_id=REMEDIATION_APPROVAL_ID,approval_text=REMEDIATION_APPROVAL_TEXT)==after
    first_value=json.loads(first);first_value['approved_at']='2026-10-23T00:00:00+00:00'
    path.with_suffix('.attempt-approval.json').write_text(json.dumps(first_value),encoding='utf-8')
    with pytest.raises(BudgetError):ledger.reserve('generate','b'*64)


def with_450(path):
    from app.topics.budget import amend_remediation_limit,REMEDIATION_APPROVAL_ID,REMEDIATION_APPROVAL_TEXT
    amend_budget_attempt_limit(path,revision_id=ATTEMPT_EXTENSION_ID,approval_text=TEXT)
    return amend_remediation_limit(path,revision_id=REMEDIATION_APPROVAL_ID,approval_text=REMEDIATION_APPROVAL_TEXT)


def test_500_amendment_preserves_all_history_and_enforces_the_new_physical_ceiling(tmp_path):
    from app.topics.budget import amend_negation_limit,NEGATION_APPROVAL_ID,NEGATION_APPROVAL_TEXT
    path,ledger=prepared(tmp_path)
    with pytest.raises(BudgetError):amend_negation_limit(path,revision_id=NEGATION_APPROVAL_ID,approval_text=NEGATION_APPROVAL_TEXT)
    with_450(path)
    attempt=ledger.reserve('label','a'*64);ledger.mark_unknown(attempt.attempt_id,'fixture_unknown')
    before=path.read_bytes()
    markers={suffix:path.with_suffix(suffix).read_bytes() for suffix in ('.approval.json','.attempt-approval.json','.remediation-approval.json')}
    after=amend_negation_limit(path,revision_id=NEGATION_APPROVAL_ID,approval_text=NEGATION_APPROVAL_TEXT)
    assert after.attempt_limit==500 and after.limit_micro==10_000_000
    assert (after.attempts,after.unknown_attempts,after.used_micro)==(1,1,1205863)
    assert path.read_bytes()==before
    assert all(path.with_suffix(suffix).read_bytes()==content for suffix,content in markers.items())
    assert amend_negation_limit(path,revision_id=NEGATION_APPROVAL_ID,approval_text=NEGATION_APPROVAL_TEXT)==after
    with closing(sqlite3.connect(path)) as connection:
        connection.executemany("INSERT INTO attempts(id,stage,payload_hash,reserved_micro,charged_micro,state,created_at) "
            "VALUES(?,'label',?,1205863,1,'settled','fixture')",[(f'fixture-{i}','b'*64) for i in range(498)])
        connection.commit()
    ledger.reserve('generate','c'*64)
    assert ledger.summary().attempts==500
    with pytest.raises(BudgetError):ledger.reserve('generate','d'*64)


@pytest.mark.parametrize('change',['wrong_text','money','deleted_prior','prior_bytes'])
def test_500_approval_never_accepts_changed_money_or_broken_authorization_chain(tmp_path,change):
    from app.topics.budget import amend_negation_limit,NEGATION_APPROVAL_ID,NEGATION_APPROVAL_TEXT
    path,ledger=prepared(tmp_path);with_450(path)
    if change=='wrong_text':
        with pytest.raises(BudgetError):amend_negation_limit(path,revision_id=NEGATION_APPROVAL_ID,approval_text='继续')
        return
    amend_negation_limit(path,revision_id=NEGATION_APPROVAL_ID,approval_text=NEGATION_APPROVAL_TEXT)
    if change=='money':
        target=path.with_suffix('.negation-approval.json');value=json.loads(target.read_text(encoding='utf-8'))
        value['limit_micro']='20000000';target.write_text(json.dumps(value),encoding='utf-8')
    elif change=='deleted_prior':path.with_suffix('.remediation-approval.json').unlink()
    else:
        target=path.with_suffix('.remediation-approval.json');target.write_bytes(target.read_bytes()+b' ')
    with pytest.raises(BudgetError):ledger.reserve('label','e'*64)
