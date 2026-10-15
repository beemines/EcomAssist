"""选单 HTTP 请求拒绝注入、非法来源和错误候选。"""
import pytest
from tests.test_order_resume_lifecycle import app_context, pause, selection


@pytest.mark.parametrize('patch', [{'turn_id': 1}, {'order_id': '01001'}, {'owner': 'demo-user'},
    {'amount_cents': 1}, {'category': '电子商品'}, {'selection_id': 'bad'}])
async def test_selection_rejects_untrusted_fields(tmp_path, patch):
    """严格四字段验证在图/SQL恢复之前完成。"""
    async with app_context(tmp_path) as (_, client):
        card, _ = await pause(client)
        response = await client.post('/api/conversations/1/actions/select-order', json=selection(card) | patch)
        assert response.status_code == 422
        assert response.json()['code'] == 'invalid_request'


async def test_busy_candidate_and_origin_preflight(tmp_path):
    """冲突、伪候选及跨来源失败均留在HTTP预检并释放占用。"""
    async with app_context(tmp_path) as (app, client):
        card, _ = await pause(client)
        lease = app.state.chat_service.locks.acquire('1')
        try:
            busy = await client.post('/api/conversations/1/actions/select-order', json=selection(card))
            assert busy.status_code == 409
        finally:
            lease.release()
        invalid = await client.post('/api/conversations/1/actions/select-order', json=selection(card, '9999'))
        assert invalid.status_code == 409
        origin = await client.post('/api/conversations/1/actions/select-order', json=selection(card),
            headers={'Origin': 'http://attacker.invalid'})
        assert origin.status_code == 403
        assert (await client.get('/api/conversations/1/pending-order')).status_code == 200
