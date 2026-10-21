"""Actual MySQL JSON accounting, using only an owned 3308 schema and fixture versions."""
from datetime import datetime,timezone
from types import SimpleNamespace
import hashlib
import json
import pytest
from sqlalchemy import text

from app.topics.migration import migrate_topics
from app.topics.repository import TopicRepository
from app.topics.statistics import TopicFilters,TopicStatisticsService
from tests.test_topic_batch import identity


async def seed(database):
    await migrate_topics(database,preview=False)
    async with database.session() as session,session.begin():
        for identifier,source in [(41,'user_feedback'),(42,'self_check'),(43,'retrieval_low_conf'),(44,'self_check')]:
            await session.execute(text('INSERT INTO low_confidence_questions(id,raw_question,source,created_at) '
                'VALUES(:id,:question,:source,:created)'),dict(id=identifier,question='手机号13800138000,运费多少?',
                source=source,created=datetime(2026,10,21,12)))
            values=dict(id=identifier,labels=json.dumps(['物流','运费'],ensure_ascii=False),
                model='old-model' if identifier==42 else None if identifier==43 else identity().model_version,
                taxonomy=identity().taxonomy_version,
                hashed='c'*64 if identifier==44 else hashlib.sha256('手机号13800138000,运费多少?'.encode()).hexdigest())
            await session.execute(text('INSERT INTO topic_classifications(question_id,labels,model_version,'
                'taxonomy_version,input_hash) VALUES(:id,:labels,:model,:taxonomy,:hashed)'),values)


async def test_sql_counts_multilabel_without_counting_stale_null_or_edited_inputs(flywheel_database):
    await seed(flywheel_database)
    service=TopicStatisticsService(TopicRepository(flywheel_database),None,None,identity_provider=identity)
    result=await service.summary(TopicFilters())
    assert result.pool_total==4 and result.effective==1 and result.stale==2 and result.unknown==1
    assert {row.name:row.count for row in result.topics}['运费']==1
    page=await service.questions('运费',TopicFilters(),limit=20)
    assert page.total==1 and page.items[0].question_id=='41'
    assert '13800138000' not in page.items[0].text and page.items[0].matched_review_id is None


async def test_source_and_half_open_utc_filters_match_existing_naive_timestamp_convention(flywheel_database):
    await seed(flywheel_database)
    service=TopicStatisticsService(TopicRepository(flywheel_database),None,None,identity_provider=identity)
    filtered=await service.summary(TopicFilters(source='user_feedback',since=datetime(2026,10,21,12,tzinfo=timezone.utc),
        until=datetime(2026,10,21,13,tzinfo=timezone.utc)))
    assert filtered.pool_total==1 and filtered.effective==1
    excluded=await service.summary(TopicFilters(until=datetime(2026,10,21,12,tzinfo=timezone.utc)))
    assert excluded.pool_total==0 and excluded.effective==0


async def test_model_identity_is_case_sensitive_despite_mysql_table_collation(flywheel_database):
    await seed(flywheel_database)
    async with flywheel_database.session() as session,session.begin():
        await session.execute(text('UPDATE topic_classifications SET model_version=:version WHERE question_id=41'),
                              {'version':identity().model_version.upper()})
    repo=TopicRepository(flywheel_database)
    selected=await repo.preview_pending(from_id=41,to_id=41,limit=1,identity=identity(),reclassify=True)
    assert tuple(item.id for item in selected.items)==('41',)
    summary=await TopicStatisticsService(repo,None,None,identity_provider=identity).summary(TopicFilters())
    assert summary.effective==0 and summary.stale==3
