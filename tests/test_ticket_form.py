"""手填工单经真实HTTP、完成快照与工具执行器验证，SQL仅替换为外部边界。"""
import pytest

from tests.test_chat_actions import confirm, offered_app


async def test_manual_ticket_fields_replace_inference_without_changing_owner(tmp_path):
    """用户选咨询并补充描述时写入手填内容，后续聊天不改变旧回复归属。"""
    async with offered_app(tmp_path) as (_, client, tickets, _, identity):
        await client.post('/api/chat', json={'conversation_id': '1', 'message': '你好'})
        payload = {**identity, 'ticket_type': '咨询', 'description': '请说明如何更换饮水机滤芯，不是原投诉内容。'}
        response = await confirm(client, payload)
        assert response.status_code == 200, response.text
        assert tickets.calls[-1] == {'conversation_id': '1', 'user_message_id': 1,
            'tool_call_id': 'ui_ticket:2', 'ticket_type': '咨询',
            'description': '请说明如何更换饮水机滤芯，不是原投诉内容。'}


@pytest.mark.parametrize('fields', [
    {}, {'ticket_type': '投诉'}, {'description': '我的问题'},
    {'ticket_type': '其他', 'description': '我的问题'},
    {'ticket_type': '售后', 'description': ' \n\t '},
    {'ticket_type': '售后', 'description': '字' * 2001},
    {'ticket_type': None, 'description': '我的问题'},
    {'ticket_type': '咨询', 'description': 123},
])
async def test_manual_ticket_requires_valid_category_and_description(tmp_path, fields):
    """缺填、空白、超长或非法类别不执行工单工具，也不回显输入内容。"""
    async with offered_app(tmp_path) as (_, client, tickets, _, identity):
        payload = {key: identity[key] for key in ('assistant_message_id', 'checkpoint_id')}
        response = await confirm(client, {**payload, **fields})
        assert response.status_code == 422
        assert tickets.rows == {} and tickets.calls == []
        assert '我的问题' not in response.text


async def test_manual_ticket_accepts_maximum_description_and_rejects_forged_identity(tmp_path):
    """两千字描述可提交，但可编辑业务字段不允许夹带归属或工具身份。"""
    async with offered_app(tmp_path) as (_, client, tickets, _, identity):
        payload = {**identity, 'ticket_type': '售后', 'description': '字' * 2000}
        denied = await confirm(client, {**payload, 'user_message_id': '99'})
        assert denied.status_code == 422 and tickets.calls == []
        accepted = await confirm(client, payload)
        assert accepted.status_code == 200
        assert tickets.calls[-1]['description'] == '字' * 2000
