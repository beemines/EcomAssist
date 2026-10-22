"""Test/error review roots are separate from the already submitted real pilot."""
import json
import httpx
import pytest
from fastapi import FastAPI
from app.api.topics import router
from app.topics.reviews import make_review_pack
from app.topics.review_submission import TopicReviewService
from tests.test_topic_review_submission import prepared,payload


@pytest.mark.parametrize('purpose,endpoint,attribute',[('test','test-review','topic_test_review_service'),('errors','error-review','topic_error_review_service')])
async def test_each_review_endpoint_saves_only_its_bound_pack(tmp_path,purpose,endpoint,attribute):
    (tmp_path/'pilot').mkdir()
    original,pilot=prepared(tmp_path/'pilot')
    pack=make_review_pack(original.samples,snapshot_hash='1'*64,teacher_receipts=(),purpose=purpose)
    root=tmp_path/endpoint;root.mkdir();(root/'pack.json').write_text(pack.model_dump_json(),encoding='utf-8')
    application=FastAPI();application.state.chat_action_allowed_origins=[]
    application.state.topic_review_service=pilot
    setattr(application.state,attribute,TopicReviewService(root));application.include_router(router)
    async with httpx.AsyncClient(transport=httpx.ASGITransport(application),base_url='http://127.0.0.1:8007') as client:
        result=await client.post('/api/topics/'+endpoint,json=payload(pack))
        assert result.status_code==200
        assert (root/'review-receipt.json').exists()
        assert not (tmp_path/'pilot/review-receipt.json').exists()
        bad=await client.post('/api/topics/'+endpoint,json=payload(pack),headers={'Origin':'https://foreign.invalid'})
        assert bad.status_code==403
