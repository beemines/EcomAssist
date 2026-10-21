"""Read-only distribution accounting keeps unavailable evidence distinct from zero."""
from datetime import datetime,timezone,timedelta
from types import SimpleNamespace
from unittest.mock import AsyncMock
import pytest

from app.topics.statistics import TopicFilters,TopicStatisticsService
from tests.test_topic_batch import identity


def repository(**changes):
    data=dict(pool_total=3,effective=1,stale=1,unknown=1,missing=0,latest=None,
        label_counts={'物流':1,'运费':1},pending_inputs=[])
    data.update(changes)
    return SimpleNamespace(read_summary=AsyncMock(return_value=data),read_questions=AsyncMock(
        return_value=dict(total=0,items=[])))


async def test_multilabel_uses_question_denominator_and_keeps_all_17_classes():
    result=await TopicStatisticsService(repository(),None,None,identity_provider=identity).summary(TopicFilters())
    assert result.effective==1 and result.pool_total==3 and result.unclassified==2
    counts={row.name:row for row in result.topics}
    assert len(counts)==17 and counts['物流'].count==counts['运费'].count==1
    assert counts['物流'].share==counts['运费'].share==1.0 and counts['尺码'].count==0
    assert result.pending_review is None and result.receipts_status=='unknown'


async def test_missing_manifest_is_unconfigured_instead_of_fake_empty_model_counts(tmp_path):
    profile=SimpleNamespace(manifest_path=tmp_path/'missing.json')
    result=await TopicStatisticsService(repository(),profile,None).summary(TopicFilters())
    assert result.status=='unconfigured' and result.pool_total==3
    assert result.identity is None and result.effective is None and all(row.count is None for row in result.topics)


async def test_database_failure_propagates_instead_of_zeroes():
    repo=repository()
    repo.read_summary.side_effect=RuntimeError('test database unavailable')
    with pytest.raises(RuntimeError):
        await TopicStatisticsService(repo,None,None).summary(TopicFilters())


@pytest.mark.parametrize('change',[dict(source='not-a-source'),dict(since=datetime(2026,10,21)),
    dict(since=datetime(2026,10,22,tzinfo=timezone.utc),until=datetime(2026,10,21,tzinfo=timezone.utc))])
def test_filters_reject_ambiguous_dates_unknown_sources_and_reversed_ranges(change):
    with pytest.raises(ValueError): TopicFilters(**change)


async def test_question_validation_precedes_database_and_receipts_unavailable_remains_unknown():
    repo=repository()
    service=TopicStatisticsService(repo,None,None,identity_provider=identity)
    for label,offset,limit in [('unknown',0,20),('物流',-1,20),('物流',0,101)]:
        with pytest.raises(ValueError):
            await service.questions(label,TopicFilters(),offset=offset,limit=limit)
    assert not repo.read_questions.called
