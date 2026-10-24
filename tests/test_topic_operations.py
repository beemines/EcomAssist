"""Operational writes require both explicit execute and a frozen reviewed scope."""
import pytest
from app.topics.repository import verify_preview
from tests.test_topic_batch import preview

def test_operational_parser_defaults_to_preview_and_requires_database_and_profile():
    from app.topics.cli import parser
    arguments=parser().parse_args(['run-once','--database','test','--profile','p.json','--preview-file','f.json'])
    assert arguments.execute is False
    with pytest.raises(SystemExit):parser().parse_args(['run-once','--profile','p.json','--preview-file','f.json'])

def test_retry_requires_explicit_reclassification_scope_flag():
    from app.topics.cli import parser
    args=parser().parse_args(['retry','--database','test','--profile','p.json','--preview-file','r.json','--reclassify'])
    assert args.reclassify is True and args.execute is False

def test_saved_operation_scope_cannot_silently_become_reclassification(tmp_path):
    from app.topics.operations import read_scope
    frozen=preview();path=tmp_path/'preview.json';path.write_text(frozen.model_dump_json(),encoding='utf-8')
    assert read_scope(path,frozen.identity,database_identity=frozen.database_identity,reclassify=False)==frozen
    with pytest.raises(ValueError):read_scope(path,frozen.identity,database_identity=frozen.database_identity,reclassify=True)
    with pytest.raises(ValueError):read_scope(path,frozen.identity,database_identity='0'*64,reclassify=False)

def test_durable_round_pause_requires_explicit_retry(tmp_path):
    from app.topics.receipts import ReceiptStore,ReceiptError
    path=tmp_path/'receipts.sqlite3';ReceiptStore.initialize(path,database_identity='a'*64)
    store=ReceiptStore(path,database_identity='a'*64)
    assert store.round_failures()==0
    for expected in (1,2,3):assert store.record_round(success=False,now=1.)==expected
    reopened=ReceiptStore(path,database_identity='a'*64)
    assert reopened.round_failures()==3
    with pytest.raises(ReceiptError):store.record_round(success=False,now=2.)
    reopened.retry_rounds(now=3.)
    assert store.round_failures()==0
    store.record_round(success=False,now=4.);store.record_round(success=True,now=5.)
    assert store.round_failures()==0


async def test_run_once_without_execute_does_not_initialize_receipts_or_contact_model(tmp_path,monkeypatch):
    import app.topics.operations as module
    from types import SimpleNamespace
    frozen=preview();scope=tmp_path/'scope.json';scope.write_text(frozen.model_dump_json(),encoding='utf-8')
    profile=SimpleNamespace(service_url='http://127.0.0.1:8103',manifest_path=tmp_path/'model',runtime_root=tmp_path/'runtime')
    monkeypatch.setattr(module,'load_profile',lambda path:profile)
    monkeypatch.setattr(module,'verify_release',lambda path:frozen.identity)
    async def schema(database,**kwargs):return SimpleNamespace(complete=True,database_identity=frozen.database_identity)
    monkeypatch.setattr(module,'migrate_topics',schema)
    def forbidden(*args,**kwargs):pytest.fail('dry-run reached an executing dependency')
    monkeypatch.setattr(module.ReceiptStore,'initialize',forbidden)
    monkeypatch.setattr(module,'TopicClient',forbidden)
    result=await module.operate(SimpleNamespace(command='run-once',profile=tmp_path/'p.json',preview_file=scope,execute=False),None)
    assert result['mode']=='preview' and not profile.runtime_root.exists()
