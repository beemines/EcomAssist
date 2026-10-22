"""Local UI submissions still need actual, complete, pack-bound human decisions."""
import json
from datetime import datetime
from pathlib import Path
import httpx
import pytest
from fastapi import FastAPI

from app.topics.review_submission import ReviewSubmission,ReviewSubmissionConflict,TopicReviewService
from app.topics.reviews import ReviewReceipt,load_decisions,apply_review
from tests.test_topic_review_receipts import pack


def prepared(tmp_path):
    original=pack()
    (tmp_path/'pack.json').write_text(original.model_dump_json(),encoding='utf-8')
    return original,TopicReviewService(tmp_path)


def payload(original,**change):
    return dict(pack_hash=original.pack_hash,reviewer='自动化测试fixture，并非实际人审',attested=True,
        items=[dict(sample_id=row.id,decision='accept',final_labels=list(row.labels),notes='')
               for row in original.samples]) | change


def test_saves_real_decision_contract_and_duplicate_submit_is_idempotent(tmp_path):
    original,service=prepared(tmp_path)
    value=payload(original)
    value['items'][1].update(decision='correct',final_labels=['运费'])
    first=service.save(ReviewSubmission.model_validate(value))
    stored=ReviewReceipt.model_validate_json((tmp_path/'review-receipt.json').read_text(encoding='utf-8'))
    decisions=load_decisions(tmp_path/'decisions.jsonl')
    assert first['receipt_hash']==stored.receipt_hash
    assert stored.samples[1].labels==('运费',) and first['corrected']==1
    assert all(datetime.fromisoformat(row.reviewed_at).utcoffset() is not None for row in decisions)
    assert apply_review(original,decisions).samples==stored.samples
    before=(tmp_path/'review-receipt.json').read_bytes()
    assert service.save(ReviewSubmission.model_validate(value))==first
    assert (tmp_path/'review-receipt.json').read_bytes()==before


@pytest.mark.parametrize('bad',['missing','duplicate','changed_accept','wrong_pack','unattested','numeric_attestation','blank_reviewer'])
def test_invalid_or_unreviewed_rows_cannot_create_a_receipt(tmp_path,bad):
    original,service=prepared(tmp_path)
    value=payload(original)
    if bad=='missing': value['items'].pop()
    if bad=='duplicate': value['items'][1]=value['items'][0]
    if bad=='changed_accept': value['items'][0]['final_labels']=['物流']
    if bad=='wrong_pack': value['pack_hash']='0'*64
    if bad=='unattested': value['attested']=False
    if bad=='numeric_attestation': value['attested']=1
    if bad=='blank_reviewer': value['reviewer']=' '
    with pytest.raises(ValueError): service.save(ReviewSubmission.model_validate(value))
    assert not (tmp_path/'review-receipt.json').exists()


def test_cannot_silently_replace_submitted_decisions_and_corruption_is_not_pending(tmp_path):
    original,service=prepared(tmp_path)
    value=payload(original)
    service.save(ReviewSubmission.model_validate(value))
    original_receipt=(tmp_path/'review-receipt.json').read_bytes()
    value['items'][0].update(decision='exclude',final_labels=[],notes='fixture exclusion')
    with pytest.raises(ReviewSubmissionConflict): service.save(ReviewSubmission.model_validate(value))
    assert (tmp_path/'review-receipt.json').read_bytes()==original_receipt
    (tmp_path/'review-receipt.json').write_text('{}',encoding='utf-8')
    with pytest.raises(ValueError): service.state()


def test_receipt_survives_materialization_failure_and_same_submit_repairs_files(tmp_path,monkeypatch):
    original,service=prepared(tmp_path)
    value=ReviewSubmission.model_validate(payload(original))
    actual=service._publish_decisions
    monkeypatch.setattr(service,'_publish_decisions',lambda receipt:(_ for _ in ()).throw(OSError('controlled fixture failure')))
    with pytest.raises(OSError): service.save(value)
    stored=ReviewReceipt.model_validate_json((tmp_path/'review-receipt.json').read_text(encoding='utf-8'))
    monkeypatch.setattr(service,'_publish_decisions',actual)
    result=service.save(value)
    assert result['receipt_hash']==stored.receipt_hash
    assert len(load_decisions(tmp_path/'decisions.jsonl'))==len(original.samples)
    assert not (tmp_path/'.review-submit.lock').exists()


async def test_api_keeps_local_origin_guard_and_never_needs_a_training_worker(tmp_path):
    from app.api.topics import router
    original,service=prepared(tmp_path)
    application=FastAPI()
    application.state.topic_review_service=service
    application.state.chat_action_allowed_origins=[]
    application.state.background_tasks_enabled=False
    application.include_router(router)
    async with httpx.AsyncClient(transport=httpx.ASGITransport(application),base_url='http://127.0.0.1:8007') as client:
        bad=await client.post('/api/topics/pilot-review',json=payload(original),headers={'Origin':'null'})
        assert bad.status_code==403 and not (tmp_path/'review-receipt.json').exists()
        incomplete=payload(original); incomplete['items'].pop()
        assert (await client.post('/api/topics/pilot-review',json=incomplete)).status_code==422
        response=await client.post('/api/topics/pilot-review',json=payload(original))
        assert response.status_code==200 and response.json()['accepted']==2
        assert response.headers['cache-control']=='no-store'
