import httpx
import pytest
from fastapi import FastAPI


def app_for_feedback(*, fail=False):
    from app.api.feedback import router
    from app.flywheel.types import PoolReceipt
    class Service:
        async def submit(self, conversation_id, *, user_id, assistant_message_id, checkpoint_id=None):
            if fail:
                raise RuntimeError('secret-test-sentinel')
            return PoolReceipt(id='9007199254740993', created=True)
    app = FastAPI()
    app.state.feedback_service = Service()
    app.state.chat_action_allowed_origins = []
    app.include_router(router)
    return app


async def test_feedback_json_accepts_only_original_assistant_locator():
    app = app_for_feedback()
    async with httpx.AsyncClient(transport=httpx.ASGITransport(app), base_url='http://127.0.0.1:8006') as client:
        response = await client.post('/api/conversations/1/feedback', json={'assistant_message_id': '20'})
    assert response.status_code == 200
    assert response.json() == {'id': '9007199254740993', 'created': True}


@pytest.mark.parametrize('body', [
    {'assistant_message_id': 20}, {'assistant_message_id': '020'},
    {'assistant_message_id': '20', 'raw_question': '伪造原话'},
    {'assistant_message_id': '20', 'retrieved_chunks': []},
    {'assistant_message_id': '20', 'user_id': 'someone-else'},
    {'assistant_message_id': '20', 'checkpoint_id': 'not-a-uuid'},
])
async def test_feedback_boundary_rejects_forged_metadata(body):
    app = app_for_feedback()
    async with httpx.AsyncClient(transport=httpx.ASGITransport(app), base_url='http://127.0.0.1:8006') as client:
        response = await client.post('/api/conversations/1/feedback', json=body)
    assert response.status_code == 422


async def test_feedback_cross_origin_and_storage_error_cannot_return_success():
    app = app_for_feedback(fail=True)
    async with httpx.AsyncClient(transport=httpx.ASGITransport(app), base_url='http://127.0.0.1:8006') as client:
        origin = await client.post('/api/conversations/1/feedback', json={'assistant_message_id': '20'},
                                  headers={'origin': 'https://untrusted.invalid'})
        storage = await client.post('/api/conversations/1/feedback', json={'assistant_message_id': '20'})
    assert origin.status_code == 403 and storage.status_code == 503
    assert 'secret-test-sentinel' not in storage.text
