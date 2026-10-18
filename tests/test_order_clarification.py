"""缺失订单身份应完成必要追问，不让自由生成的措辞变成服务错误。"""
import pytest
from langchain_core.messages import AIMessageChunk

from app.workflow.persistence import checkpoint_config
from tests.fakes import decode_sse
from tests.test_workflow_agent import control
from tests.test_workflow_api import Store, intent, request, workflow_app
from tests.workflow_fakes import ScriptedWorkflowModel


@pytest.mark.parametrize('name,question', [
    ('物流', '我买的恒温猫窝2002一直没发货，什么时候到'),
    ('订单', '恒温猫窝2002这单现在是什么状态'),
])
async def test_missing_order_identity_completes_safe_question_without_guessing(tmp_path, name, question):
    """真实父图/SSE/持久化：裸数字不是订单锚点，也不索取工具不支持的手机号。"""
    model = ScriptedWorkflowModel([control('clarification')], intent_replies=[intent(name)],
        final_chunks=[AIMessageChunk('您好，麻烦您提供一下订单号或下单手机号，我帮您查询发货和配送进度。'),
                      AIMessageChunk('', response_metadata={'finish_reason': 'stop'})])
    store = Store()
    async with workflow_app(tmp_path, model=model, store=store) as app:
        frames = decode_sse((await request(app, question)).text)
        snapshot = await app.state.chat_service.graph.aget_state(checkpoint_config('1'))
    assert frames[-1][0] == 'done'
    answer = ''.join(data['delta'] for event, data in frames if event == 'delta')
    assert '订单号' in answer and '2002' not in answer and '手机号' not in answer
    assert not any(event in ('error', 'actions', 'refund_offer') for event, _ in frames)
    assert snapshot.values['raw_question'] == question
    assert snapshot.values['turn_status'] == 'completed'
    assert snapshot.values['final_answer'] == answer
    assert snapshot.values['tool_call_count'] == 0 and store.commits == 1
    assert model.decisions == 1 and model.streams == 0
