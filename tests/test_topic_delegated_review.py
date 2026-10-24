"""Delegated AI decisions cannot masquerade as an actual human receipt."""
from datetime import datetime, timezone
import json
import re
import pytest
from app.topics.reviews import ReviewDecision, make_review_pack
from app.topics.review_submission import TopicReviewService
from tests.test_topic_review_receipts import pack


def prepared(tmp_path, purpose='test'):
    source = pack()
    frozen = make_review_pack(source.samples, snapshot_hash='a'*64, teacher_receipts=[], purpose=purpose)
    (tmp_path/'pack.json').write_text(frozen.model_dump_json(), encoding='utf-8')
    now = datetime.now(timezone.utc).isoformat()
    authority = dict(schema_version=1, kind='user_authorized_ai', human_status='not_performed',
        user_instruction='你全部确认就行了', recorded_at=now, reviewer='Codex AI（用户授权代审，非人工）',
        model_version='b'*64, dataset_hash='a'*64, test_pack_hash=frozen.pack_hash,
        error_pack_hash=None)
    decisions = [ReviewDecision(sample_id=row.id, pack_hash=frozen.pack_hash, decision='accept',
        final_labels=row.labels, reviewer=authority['reviewer'], reviewed_at=now, notes='逐条 AI 复核，测试夹具')
        for row in frozen.samples]
    return TopicReviewService(tmp_path), authority, decisions


def test_delegated_save_is_separate_idempotent_and_never_human_attestation(tmp_path):
    service, authority, decisions = prepared(tmp_path)
    result = service.save_delegated(decisions, authority=authority)
    assert result['human_status'] == 'not_performed'
    assert result['review_status'] == 'ai_delegated'
    assert result['receipt']['samples'][0]['labels'] == ['发票']
    assert service.state() is None
    assert not (tmp_path/'review-receipt.json').exists()
    before = (tmp_path/'ai-review.json').read_bytes()
    assert service.save_delegated(decisions, authority=authority) == result
    assert (tmp_path/'ai-review.json').read_bytes() == before
    assert service.delegated_state() == result
    page=service.render()
    data=json.loads(re.search(r'<script type="application/json" id="reviewData">(.*?)</script>',page,re.S).group(1))
    assert data['review_kind']=='delegated_ai'
    assert data['submitted']['receipt_hash']==result['receipt']['receipt_hash']
    assert data['human_status']=='not_performed'


@pytest.mark.parametrize('bad', ['pack', 'dataset', 'reviewer', 'missing', 'pilot'])
def test_delegated_review_refuses_wrong_scope_or_incomplete_decisions(tmp_path, bad):
    service, authority, decisions = prepared(tmp_path, purpose='pilot' if bad=='pilot' else 'test')
    if bad=='pack': authority['test_pack_hash']='c'*64
    if bad=='dataset': authority['dataset_hash']='d'*64
    if bad=='reviewer': decisions[0]=decisions[0].model_copy(update={'reviewer':'human-looking name'})
    if bad=='missing': decisions.pop()
    with pytest.raises(ValueError):service.save_delegated(decisions, authority=authority)
    assert not (tmp_path/'ai-review.json').exists()
    assert service.state() is None


def test_delegated_review_detects_mutation_and_refuses_silent_overwrite(tmp_path):
    service, authority, decisions = prepared(tmp_path)
    service.save_delegated(decisions, authority=authority)
    changed=decisions.copy()
    changed[0]=changed[0].model_copy(update={'decision':'correct','final_labels':('物流',)})
    with pytest.raises(ValueError):service.save_delegated(changed, authority=authority)
    path=tmp_path/'ai-review.json'
    value=json.loads(path.read_text(encoding='utf-8'))
    value['authority']['user_instruction']='altered'
    path.write_text(json.dumps(value),encoding='utf-8')
    with pytest.raises(ValueError):service.delegated_state()
