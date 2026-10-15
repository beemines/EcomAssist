"""验证每轮状态隔离与 SQL 消息身份，不把运行依赖写入状态。"""
from langchain_core.messages import AIMessage, HumanMessage

from app.workflow.state import new_turn_state


def test_state_reset_does_not_keep_evidence_or_actions():
    """上一轮证据、动作、计数与结果不得进入下一轮。"""
    previous = new_turn_state(conversation_id='c1', user_message_id=101,
                              raw_question='订单在哪', category=None,
                              messages=[HumanMessage('订单在哪')])
    previous.update(evidence_payload={'answer': '旧证据'}, quality={'sufficient': True},
                    citations=[{'id': 'old'}], suggested_actions=['handoff', 'create_ticket'],
                    decision_count=3, tool_call_count=2, final_answer='旧回答',
                    final_message_id='104', usage={'actual': 99}, turn_status='completed')
    fresh = new_turn_state(conversation_id='c1', user_message_id=105,
                          raw_question='另一问题', category='家电',
                          messages=[HumanMessage('另一问题')])
    assert fresh.get('evidence_payload') == {} and fresh.get('suggested_actions') == []
    assert fresh['tool_call_count'] == 0 and fresh['final_message_id'] is None
    assert fresh['quality'] == {} and fresh['citations'] == [] and fresh['tool_trace'] == []
    assert fresh['decision_count'] == 0 and fresh['final_answer'] is None
    assert fresh['intent'] is None and fresh['route'] is None and fresh['reply_mode'] is None
    assert fresh['usage'] == {'actual': 0, 'estimated': 0, 'actual_calls': 0, 'estimated_calls': 0}
    assert fresh['turn_status'] == 'pending'
    assert fresh['resolved_question'] == '另一问题' and fresh['category'] == '家电'
    assert previous['evidence_payload'] == {'answer': '旧证据'}


def test_sql_message_identity_is_stable_without_mutating_prepared_history():
    """当前 SQL ID 转为字符串；历史身份保留，输入消息与列表不被改写。"""
    messages = [HumanMessage('旧问题', id='100'), AIMessage('旧回答', id='104'),
                HumanMessage('当前问题', id='generated-id')]
    state = new_turn_state(conversation_id='c1', user_message_id=105,
                           raw_question='当前问题', category=None, messages=messages)
    assert state.get('user_message_id') == '105'
    assert [message.id for message in state['messages']] == ['100', '104', '105']
    assert [message.id for message in messages] == ['100', '104', 'generated-id']
    state['messages'].append(AIMessage('新回答'))
    assert len(messages) == 3


def test_turns_have_independent_mutable_containers():
    """修改一轮结果不得污染另一轮初始容器。"""
    first = new_turn_state(conversation_id='c1', user_message_id=1,
                           raw_question='你好', category=None, messages=[HumanMessage('你好')])
    second = new_turn_state(conversation_id='c1', user_message_id=2,
                            raw_question='谢谢', category=None, messages=[HumanMessage('谢谢')])
    assert first.get('suggested_actions') == []
    first['suggested_actions'].append('handoff')
    first['evidence_payload']['old'] = True
    assert second['suggested_actions'] == [] and second['evidence_payload'] == {}


def test_v2_turn_containers_do_not_share_order_or_stage_data():
    """新增列表和审计账本也必须每轮独立，防止跨轮事实污染。"""
    first = new_turn_state(conversation_id='c1', user_message_id=1,
        raw_question='退货', category=None, messages=[HumanMessage('退货')])
    second = new_turn_state(conversation_id='c1', user_message_id=2,
        raw_question='政策', category=None, messages=[HumanMessage('政策')])
    first['retrieval_queries'].append('第一轮查询')
    first['retrieval_audit']['source'] = 'first'
    first['stage_usage']['understanding'] = {'actual': 12}
    assert second['retrieval_queries'] == []
    assert second['retrieval_audit'] == {} and second['stage_usage'] == {}
