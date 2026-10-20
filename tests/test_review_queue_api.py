import httpx
import pytest
from fastapi import FastAPI


def review_app():
    from app.api.review_queue import router
    from app.flywheel.types import PublicationReceipt
    class Service:
        async def list_reviews(self,**kwargs): return {'items':[],'total':0}
        async def approve(self, identifier, **kwargs):
            return PublicationReceipt(review_id=identifier, knowledge_chunk_id='9007199254740993', status='pending')
        async def reject(self, identifier, **kwargs): pass
        async def retry_publication(self, identifier):
            return PublicationReceipt(review_id=identifier, knowledge_chunk_id='9007199254740993', status='pending')
    app = FastAPI()
    app.state.review_service, app.state.chat_action_allowed_origins = Service(), []
    app.include_router(router)
    return app


@pytest.mark.parametrize('body', [{}, {'approved_answer': ''}, {'approved_answer': ' '},
    {'approved_answer': '人工答案', 'knowledge_chunk_id': '1'},
    {'approved_answer': '人工答案', 'publication': {'status': 'ready'}}])
async def test_review_requires_human_answer_and_forbids_server_owned_fields(body):
    async with httpx.AsyncClient(transport=httpx.ASGITransport(review_app()), base_url='http://127.0.0.1:8006') as client:
        response = await client.post('/api/review-queue/1/approve', json=body)
    assert response.status_code == 422


async def test_review_confirmation_is_same_origin_and_preserves_bigint():
    async with httpx.AsyncClient(transport=httpx.ASGITransport(review_app()), base_url='http://127.0.0.1:8006') as client:
        bad = await client.post('/api/review-queue/1/approve', json={'approved_answer': '核准答案'},
            headers={'origin': 'https://untrusted.invalid'})
        good = await client.post('/api/review-queue/1/approve', json={'approved_answer': '核准答案'})
    assert bad.status_code == 403 and good.status_code == 200
    assert good.json()['knowledge_chunk_id'] == '9007199254740993'


async def test_disabled_review_does_not_pretend_to_publish():
    app = review_app(); app.state.review_service = None
    async with httpx.AsyncClient(transport=httpx.ASGITransport(app), base_url='http://127.0.0.1:8006') as client:
        response = await client.post('/api/review-queue/1/approve', json={'approved_answer': '核准答案'})
    assert response.status_code == 503


async def test_server_metadata_contract_failure_is_not_blame_on_user_input():
    app = review_app()
    class Broken:
        async def approve(self, *args, **kwargs): raise ValueError('unknown server state version; secret-sentinel')
    app.state.review_service = Broken()
    async with httpx.AsyncClient(transport=httpx.ASGITransport(app), base_url='http://127.0.0.1:8006') as client:
        damaged = await client.post('/api/review-queue/1/approve', json={'approved_answer': '核准答案'})
        invalid_id = await client.post('/api/review-queue/01/approve', json={'approved_answer': '核准答案'})
    assert damaged.status_code == 503 and 'secret-sentinel' not in damaged.text
    assert invalid_id.status_code == 422


async def test_retry_paths_match_approved_spec_and_keep_state_server_owned():
    app = review_app()
    calls = []
    class Pool:
        async def manage_processing(self, pool_id, *, action, now):
            calls.append((pool_id, action))
            return {'id': pool_id, 'processing': {'status': 'pending', 'attempt_count': 1}}
    app.state.flywheel_repository = Pool()
    async with httpx.AsyncClient(transport=httpx.ASGITransport(app), base_url='http://127.0.0.1:8006') as client:
        publication = await client.post('/api/review-queue/1/retry-publication', json={})
        processing = await client.post('/api/low-confidence-questions/2/retry', json={})
        forged = await client.post('/api/low-confidence-questions/2/retry', json={'attempt_count': 0})
    assert publication.status_code == processing.status_code == 200
    assert forged.status_code == 422 and calls == [('2', 'retry')]


async def test_review_read_cannot_bypass_local_admin_host_boundary():
    async with httpx.AsyncClient(transport=httpx.ASGITransport(review_app()),base_url='http://127.0.0.1:8006') as client:
        good=await client.get('/api/review-queue')
        bad=await client.get('/api/review-queue',headers={'host':'evil.invalid'})
    assert good.status_code==200 and bad.status_code==403
