"""A bare write request cannot borrow an issue outside its trusted request scope."""
import pytest
from langchain_core.messages import HumanMessage, AIMessage

from tests.fakes import decode_sse
from tests.test_ticket_confirmation_lifecycle import ticket_app, decision
from tests.test_workflow_api import Store, intent
from tests.workflow_fakes import ScriptedWorkflowModel, workflow_call


@pytest.mark.parametrize('question', ['帮我建个工单', '请帮我建工单', '给我开一个工单',
                                      '请您帮我建个工单', '帮忙建个工单'])
async def test_bare_request_after_order_chat_clarifies_before_any_tool_or_decision(tmp_path, question):
    store = Store()
    await store.seed('1', [HumanMessage('2002物流信息异常'), AIMessage('已查询模拟物流，需要工单可告知。')])
    model = ScriptedWorkflowModel([workflow_call('create_ticket',
        {'ticket_type': '售后', 'description': '2002物流信息异常'})],
        intent_replies=[intent('工单'), intent('工单')])
    async with ticket_app(tmp_path, model=model, store=store) as (app, client, tickets):
        for _ in range(2):
            response = await client.post('/api/chat', json={'conversation_id': '1', 'message': question})
            frames = decode_sse(response.text)
            assert frames[-1][0] == 'done', frames
            assert ''.join(data['delta'] for name, data in frames if name == 'delta') == '请补充问题描述。'
            assert not any(name in ('ticket_confirmation', 'paused', 'error') for name, _ in frames)
        assert model.decisions == model.streams == tickets.calls == 0
        assert app.state.chat_service.executor.audit_sink.records == []


@pytest.mark.parametrize('choice', ['cancel', 'confirm'])
async def test_clarification_then_user_issue_still_reaches_native_confirmation(tmp_path, choice):
    model = ScriptedWorkflowModel([workflow_call('create_ticket',
        {'ticket_type': '售后', 'description': '2002物流信息异常'})],
        intent_replies=[intent('工单'), intent('工单')])
    async with ticket_app(tmp_path, model=model) as (app, client, tickets):
        first = decode_sse((await client.post('/api/chat', json={'conversation_id': '1', 'message': '帮我建个工单'})).text)
        assert first[-1][0] == 'done', first
        second = decode_sse((await client.post('/api/chat', json={'conversation_id': '1', 'message': '2002物流信息异常'})).text)
        assert second[-1][0] == 'paused', second
        preview = next(data for name, data in second if name == 'ticket_confirmation')
        assert preview['description'] == '2002物流信息异常' and tickets.calls == 0
        result = decode_sse((await client.post('/api/conversations/1/actions/confirm-ticket',
            json=decision(preview, choice))).text)
        assert result[-1][0] == 'done', result
        assert tickets.calls == (1 if choice == 'confirm' else 0)
        audit, = app.state.chat_service.executor.audit_sink.records
        assert audit.status == ('success' if choice == 'confirm' else 'permission_denied')
        assert audit.retry_count == 0
