"""Actual selected FAQ bodies belong to one attachment; native receipts remain paired."""
import copy
import pytest
from app.core import evidence
from app.core.errors import InputTooLong


def prepare(payloads, **kwargs):
    assert hasattr(evidence, 'prepare_workflow_evidence'), 'WorkflowEvidence is missing'
    return evidence.prepare_workflow_evidence(payloads, **kwargs)


def faq(count=12):
    return {'found': True, 'matches': [dict(id=str(i), question=f'问题{i}', answer=f'完整政策{i}',
        score=1-i/100, score_kind='rerank') for i in range(count)],
        'retrieval': {'strategy': 'hybrid_rerank', 'match_count': count}}


@pytest.mark.parametrize('top_k', [5, 10])
def test_top_k_whole_selection_and_edge_numbering(top_k):
    original = faq()
    source = copy.deepcopy(original)
    result = prepare([source], top_k=top_k, token_budget=6000)
    assert len(result.citations) == top_k
    assert [c.n for c in result.citations][::len(result.citations)-1] == [1, 2]
    assert {c.chunk_id for c in result.citations} == {str(i) for i in range(top_k)}
    assert result.best_score == 1
    assert source == original
    assert '完整政策' not in str(result.tool_receipts)
    assert not hasattr(result, 'messages')


def test_oversized_first_block_does_not_hide_fitting_actual_evidence():
    data = faq(2)
    data['matches'][0]['answer'] = '巨量' * 20000
    result = prepare([data], top_k=5, token_budget=1000)
    assert [c.chunk_id for c in result.citations] == ['1']
    assert result.best_score == .99
    with pytest.raises(InputTooLong):
        prepare([data], top_k=5, token_budget=1)


def test_business_receipt_is_complete_typed_copy():
    data = {'order_id': '1001', 'mock': True, 'amount_cents': 12900,
            'items': [{'count': 2}], 'found': False}
    result = prepare([data], top_k=5, token_budget=2250)
    assert result.tool_receipts == (data,)
    result.tool_receipts[0]['items'][0]['count'] = 99
    assert data['items'][0]['count'] == 2


@pytest.mark.asyncio
@pytest.mark.parametrize('count', [1, 2])
async def test_online_top_five_reaches_retrieval_without_reducing_recall(count):
    from tests.test_retrieval_service import service_parts
    from app.knowledge.types import ChunkRecord, VectorHit
    from app.retrieval.types import RerankHit
    from app.retrieval.multi import WorkflowRetriever
    service, _, repo, _, index, planner, reranker = service_parts(
        [VectorHit(i,.9) for i in range(12)],
        [ChunkRecord('售后',f'问题{i}',f'政策{i}',id=i,vectorize_status='done') for i in range(12)],
        [RerankHit(index=i,score=1-i/100) for i in range(12)])
    result = await WorkflowRetriever(service).retrieve(question='退货政策',
        queries=('退货政策',) if count==1 else ('退货政策','退款要求'), category=None, top_k=5)
    assert len(result.payload['matches']) == 5
    assert len(repo.calls[-1]) == 12 and len(index.calls) == count
    assert reranker.calls[-1][2] == 5 and planner.calls == []
