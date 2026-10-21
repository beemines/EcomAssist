"""Owned3308 schema tests; no real customer pool or model is touched."""

import json

import pytest
from sqlalchemy import event, text
from sqlalchemy.exc import IntegrityError

from app.topics.migration import contracts, migrate_topics, verify_topics


async def seed(database):
    assert database.engine.url.port == 3308
    assert database.engine.url.database.startswith('ch03_migration_')
    async with database.session() as session, session.begin():
        await session.execute(text("INSERT INTO low_confidence_questions(id,raw_question,source) VALUES(41,'合成结构测试','self_check')"))


async def test_missing_schema_preview_is_read_only_and_migration_repeats_safely(flywheel_database):
    database = flywheel_database
    await seed(database)
    statements = []
    def capture(connection, cursor, statement, parameters, context, executemany):
        statements.append(statement.lstrip().upper())
    event.listen(database.engine.sync_engine, 'before_cursor_execute', capture)
    try:
        preview = await migrate_topics(database, preview=True)
    finally:
        event.remove(database.engine.sync_engine, 'before_cursor_execute', capture)
    assert preview.stage == 'missing' and not preview.complete and preview.preview
    assert all(statement.startswith('SELECT') for statement in statements)
    assert (await migrate_topics(database, preview=False)).complete
    assert (await migrate_topics(database, preview=True)).stage == 'complete'
    assert (await migrate_topics(database, preview=False)).applied_count == 0
    await verify_topics(database)
    async with database.session() as session:
        assert await session.scalar(text('SELECT COUNT(*) FROM low_confidence_questions')) == 1


async def test_base_rows_keep_null_tracking_and_original_fk_and_unique_behavior(flywheel_database):
    database = flywheel_database
    await seed(database)
    _, _, original, _ = contracts()
    async with database.engine.begin() as connection:
        for statement in original:
            await connection.exec_driver_sql(statement)
        await connection.execute(text('INSERT INTO topic_classifications(question_id,labels) VALUES(41,:labels)'),
                                 {'labels': json.dumps(['物流', '运费'], ensure_ascii=False)})
    await migrate_topics(database, preview=False)
    async with database.session() as session:
        row = (await session.execute(text('SELECT * FROM topic_classifications'))).mappings().one()
        assert all(row[key] is None for key in ('model_version', 'taxonomy_version', 'input_hash', 'batch_id'))
        assert json.loads(row['labels']) == ['物流', '运费']
    with pytest.raises(IntegrityError):
        async with database.session() as session, session.begin():
            await session.execute(text('DELETE FROM low_confidence_questions WHERE id=41'))
    with pytest.raises(IntegrityError):
        async with database.session() as session, session.begin():
            await session.execute(text("INSERT INTO topic_classifications(question_id,labels) VALUES(41,'[\"物流\"]')"))
    async with database.session() as session:
        assert await session.scalar(text('SELECT COUNT(*) FROM topic_classifications')) == 1


async def test_unknown_partial_schema_is_not_repaired(flywheel_database):
    await migrate_topics(flywheel_database, preview=False)
    async with flywheel_database.engine.begin() as connection:
        await connection.exec_driver_sql('ALTER TABLE topic_classifications ADD COLUMN unexpected INT NULL')
    for preview in (True, False):
        with pytest.raises(RuntimeError):
            await migrate_topics(flywheel_database, preview=preview)


async def test_sqlalchemy_mapping_round_trips_multilabel_and_version(flywheel_database):
    from app.db.models import TopicClassification
    await seed(flywheel_database)
    await migrate_topics(flywheel_database, preview=False)
    async with flywheel_database.session() as session, session.begin():
        row = TopicClassification(question_id=41, labels=['物流', '运费'], model_version='fixture-v1',
            taxonomy_version='ch10-topics-v1', input_hash='a'*64, batch_id='00000000-0000-0000-0000-000000000001')
        session.add(row)
        await session.flush()
        await session.refresh(row)
        assert row.id and row.classified_at
    async with flywheel_database.session() as session:
        saved = await session.get(TopicClassification, row.id)
        assert saved.labels == ['物流', '运费'] and saved.input_hash == 'a'*64


async def test_batch_commit_and_replay_skip_existing_rows_without_more_inference(flywheel_database, tmp_path):
    from app.topics.batch import BatchRunner
    from app.topics.repository import TopicRepository
    from app.topics.receipts import ReceiptStore
    from tests.test_topic_batch import identity, prediction
    await seed(flywheel_database)
    await migrate_topics(flywheel_database,preview=False)
    repo=TopicRepository(flywheel_database)
    preview=await repo.preview_pending(from_id=41,to_id=41,limit=100,identity=identity())
    ReceiptStore.initialize(tmp_path/'receipts.sqlite3',database_identity=preview.database_identity)
    records=ReceiptStore(tmp_path/'receipts.sqlite3',database_identity=preview.database_identity)
    class LocalFixtureClient:
        calls=0
        async def health(self): return identity()
        async def classify(self,items,expected,*,request_id):
            self.calls+=1
            return (prediction(),)
    client=LocalFixtureClient()
    runner=BatchRunner(repo,client,records)
    result=await runner.run_once(preview)
    assert result.written==('41',) and client.calls==1
    replay=await runner.run_once(preview)
    assert not replay.written and client.calls==1
    async with flywheel_database.session() as session:
        row=(await session.execute(text('SELECT * FROM topic_classifications'))).mappings().one()
        import hashlib
        assert row['input_hash']==hashlib.sha256('合成结构测试'.encode()).hexdigest()
        assert json.loads(row['labels'])==['运费']


async def test_source_edit_and_lost_lock_prevent_commit(flywheel_database):
    from app.flywheel.leases import processing_lease, LeaseLost
    from app.topics.repository import TopicRepository, PreviewChanged
    from tests.test_topic_batch import identity, prediction
    await seed(flywheel_database)
    await migrate_topics(flywheel_database,preview=False)
    repo=TopicRepository(flywheel_database)
    preview=await repo.preview_pending(from_id=41,to_id=41,limit=1,identity=identity())
    async with flywheel_database.session() as session, session.begin():
        await session.execute(text("UPDATE low_confidence_questions SET raw_question='已改写的合成题' WHERE id=41"))
    async with processing_lease(flywheel_database,prefix='ch10-topic:') as lease:
        with pytest.raises(PreviewChanged):
            await repo.commit_predictions(preview,[prediction()],lease)
        refreshed=await repo.preview_pending(from_id=41,to_id=41,limit=1,identity=identity())
        await lease.connection.scalar(text('SELECT RELEASE_LOCK(:name)'),{'name':lease.name})
        await lease.connection.commit()
        with pytest.raises(LeaseLost):
            await repo.commit_predictions(refreshed,[prediction()],lease)
    async with flywheel_database.session() as session:
        assert await session.scalar(text('SELECT COUNT(*) FROM topic_classifications'))==0


async def test_stale_results_require_explicit_reclassify_and_preserve_previous_result(flywheel_database,tmp_path):
    from app.flywheel.leases import processing_lease
    from app.topics.repository import TopicRepository
    from tests.test_topic_batch import identity, prediction
    await seed(flywheel_database)
    await migrate_topics(flywheel_database,preview=False)
    async with flywheel_database.session() as session, session.begin():
        await session.execute(text('INSERT INTO topic_classifications(question_id,labels) VALUES(41,:labels)'),
                              {'labels':json.dumps(['物流'])})
    repo=TopicRepository(flywheel_database,runtime_root=tmp_path)
    assert not (await repo.preview_pending(from_id=41,to_id=41,limit=1,identity=identity())).items
    preview=await repo.preview_pending(from_id=41,to_id=41,limit=1,identity=identity(),reclassify=True)
    async with processing_lease(flywheel_database,prefix='ch10-topic:') as lease:
        result=await repo.commit_predictions(preview,[prediction()],lease)
    assert result.written==('41',) and result.previous['41']['labels']==['物流']


async def test_uncertainty_and_transient_retry_have_durable_receipts(flywheel_database,tmp_path):
    from app.topics.batch import BatchRunner
    from app.topics.repository import TopicRepository
    from app.topics.receipts import ReceiptStore, FailureKey
    from app.topics.client import TopicClientError
    from tests.test_topic_batch import identity, prediction
    await seed(flywheel_database)
    await migrate_topics(flywheel_database,preview=False)
    repo=TopicRepository(flywheel_database)
    preview=await repo.preview_pending(from_id=41,to_id=41,limit=1,identity=identity())
    ReceiptStore.initialize(tmp_path/'receipts.sqlite3',database_identity=preview.database_identity)
    records=ReceiptStore(tmp_path/'receipts.sqlite3',database_identity=preview.database_identity)
    class FixtureClient:
        calls=0
        fail=True
        async def health(self): return identity()
        async def classify(self,items,expected,*,request_id):
            self.calls+=1
            if self.fail: raise TopicClientError('topic_network_failure',temporary=True)
            return (prediction(labels=[],status='needs_review'),)
    client=FixtureClient()
    runner=BatchRunner(repo,client,records,clock=lambda:100.)
    await runner.run_once(preview)
    assert client.calls==2  # Only one immediate network retry in the round.
    await runner.run_once(preview)
    assert client.calls==2  # Persisted backoff, rather than repeated inference.
    key=FailureKey(question_id='41',input_hash=preview.items[0].input_hash,model_version=identity().model_version)
    assert records.states([key])[0].failures==1
    records.retry(key,now=101.)
    client.fail=False
    await runner.run_once(preview)
    assert client.calls==3 and records.states([key])[0].status=='needs_review'
    await runner.run_once(preview)
    assert client.calls==3
    async with flywheel_database.session() as session:
        assert await session.scalar(text('SELECT COUNT(*) FROM topic_classifications'))==0
