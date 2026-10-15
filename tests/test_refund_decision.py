"""售后控制与不可变许可的业务边界。"""
import importlib
import json

import pytest
from langchain_core.messages import AIMessage, HumanMessage

from app.core.errors import ServiceError
from app.workflow.state import new_turn_state


def module():
    """缺实现用可读断言表示，导入错误不算行为RED。"""
    try:
        return importlib.import_module('app.workflow.after_sales')
    except ImportError:
        pytest.fail('after-sales control/offer behavior missing')


def ready(intent='退款退货', mode='answer', decision='needs_review'):
    """独立构造已提交答案及本轮证据，不根据正文猜入口。"""
    state = new_turn_state(conversation_id='1', user_message_id=7, raw_question='能退吗', category=None, messages=[HumanMessage('能退吗')])
    state.update(intent=intent, route='after_sales', order_snapshot={'order_id': '1001', 'mock': True},
        quality={'useful': True}, final_message_id='101', final_answer='待核验商品完好条件。',
        reply_mode=mode, refund_decision=decision, decision_reason='商品完好条件需审核',
        evidence_payload={'matches': [{'id': '100'}]}, turn_status='completed')
    return state


def test_conditional_answer_can_offer_application():
    """未知二次销售条件允许needs_review入口且快照不受State后改影响。"""
    state = ready()
    offer = module().make_refund_offer(state)
    assert offer['refund_decision'] == 'needs_review' and offer['assistant_message_id'] == '101'
    state['order_snapshot']['order_id'] = '1002'
    assert offer['order_snapshot']['order_id'] == '1001'


@pytest.mark.parametrize('changes', [{'intent': '售后'}, {'reply_mode': 'clarification'},
    {'quality': {'useful': False}}, {'refund_decision': 'ineligible'}, {'refund_decision': 'not_applicable'},
    {'final_message_id': None}, {'order_snapshot': None}])
def test_no_offer_without_complete_permission(changes):
    """任一必要条件不成立，不因答案含退款词发许可。"""
    state = ready()
    state.update(changes)
    assert module().make_refund_offer(state) is None


@pytest.mark.parametrize('intent,mode,decision', [('售后','answer','eligible'),
    ('退款退货','clarification','needs_review'), ('退款退货','answer','not_applicable')])
def test_contradictory_controls_are_errors(intent, mode, decision):
    """维修退款许可、澄清许可及退款不适用都不能被静默纠正。"""
    reply = AIMessage(json.dumps({'reply_mode': mode, 'suggested_actions': [],
        'refund_decision': decision, 'decision_reason': '待人工审核'}), response_metadata={'finish_reason': 'stop'})
    with pytest.raises(ServiceError):
        module().parse_after_sales_control(reply, intent)


@pytest.mark.parametrize('raw,resolved,expected', [('订单1001能退吗', '订单1001能退吗', '1001'),
    ('订单1001和订单1002能退吗', '订单1001和订单1002能退吗', None), ('MH-LP200能退吗', 'MH-LP200能退吗', None),
    ('199元能退吗', '199元能退吗', None)])
def test_anchor_requires_one_explicit_order(raw, resolved, expected):
    """型号、金额和多单不能冒充唯一明确订单。"""
    assert module().resolve_order_anchor(raw, resolved, []) == expected


def test_anchor_cannot_trust_assistant_invented_order():
    """助手正文和理解输出不构成订单来源。"""
    with pytest.raises(ServiceError):
        module().resolve_order_anchor('它能退吗', '订单1001能退吗', [HumanMessage('你好'), AIMessage('订单1001')])


def test_coordinated_orders_remain_ambiguous_in_current_and_history():
    """一个订单前缀下并列两个编号，不得只认第一个并自动办理。"""
    from app.workflow.entities import explicit_order_ids
    question = '订单1001和1002这两单哪个能退？'
    assert explicit_order_ids(question) == {'1001', '1002'}
    assert module().resolve_order_anchor(question, question, []) is None
    with pytest.raises(ServiceError):
        module().resolve_order_anchor('它能退吗', '订单1001能退吗', [HumanMessage(question), AIMessage('请明确订单')])
