# 最终回答验证必须基于当前证据，社会性答复不能夹带业务事实。
import importlib

import pytest

from app.core.errors import ServiceError
from tests.test_evidence import build, payload


# 延迟加载真实验证模块，并使用正式决定类型。
def api():
    try:
        return importlib.import_module('app.core.answer_validation'), importlib.import_module('app.core.sufficiency').QualityDecision
    except ImportError:
        pytest.fail('answer grounding validation is missing')


# 构造完整合法决定，避免测试替身代替 Schema 校验。
def decision(kind='knowledge', useful=True):
    _, cls = api()
    return cls(useful=useful, reason='测试决定', response_kind=kind, source=None if useful else 'self_check')


# 本轮已选知识引用可用于正常完整回答。
def test_current_knowledge_citation_validates():
    module, _ = api()
    module.validate_answer('请按完整规则办理[1]。也可参考[2]。', {'stop'}, build(), decision())


@pytest.mark.parametrize('answer', ['规则可以直接办理。', '规则[99]。', '规则[0]。', '规则[1][99]。', '规则[01]。',
    '规则[1]，另见[1,99]。', '规则[1]，另见[ 99 ]。'])
# 无引用、未知编号、列表和非规范写法不能混过引用校验。
def test_missing_foreign_or_noncanonical_citation_rejected(answer):
    module, _ = api()
    with pytest.raises(ServiceError):
        module.validate_answer(answer, {'stop'}, build(), decision())


@pytest.mark.parametrize('finish', [set(), {'length'}, {'stop', 'length'}, {'tool_calls'}, {'stop', 'tool_calls'}])
# 非stop、混合结束原因及再次工具申请结束均不能提交。
def test_nonstop_and_second_tool_finish_rejected(finish):
    module, _ = api()
    with pytest.raises(ServiceError):
        module.validate_answer('规则[1]。', finish, build(), decision())


# 历史编号不能证明本轮空证据事实。
def test_old_citation_cannot_ground_current_empty_evidence():
    module, _ = api()
    with pytest.raises(ServiceError):
        module.validate_answer('旧资料说可退[1]。', {'stop'}, build(payload(())), decision())


@pytest.mark.parametrize('kind,answer', [('social', '你好！退款明天到账。'), ('clarification', '请提供订单号，包裹明天会送到。'),
    ('social', '不客气，已经为您退款。'), ('clarification', '请问商品型号？拆封也能退货。')])
# 问候或追问后追加业务事实/承诺必须拒绝。
def test_nonknowledge_kind_cannot_emit_business_fact(kind, answer):
    module, _ = api()
    with pytest.raises(ServiceError):
        module.validate_answer(answer, {'stop'}, build(payload(())), decision(kind))


@pytest.mark.parametrize('kind,answer', [('social', '你好，请问有什么可以帮助您？'), ('social', '不客气！'),
    ('clarification', '请提供订单号。'), ('clarification', '请问商品型号和购买时间？')])
# 正常问候致谢与缺必要条件的请求允许无知识引用。
def test_pure_social_or_missing_information_request_can_pass_without_citation(kind, answer):
    module, _ = api()
    module.validate_answer(answer, {'stop'}, build(payload(())), decision(kind))


# 合法拒答仅能采用固定文字，禁止追加事实。
def test_false_decision_only_accepts_exact_fixed_refusal():
    module, _ = api()
    module.validate_answer(module.REFUSAL_TEXT, {'stop'}, build(), decision(useful=False))
    with pytest.raises(ServiceError):
        module.validate_answer('目前无法确认，但肯定可以退款[1]。', {'stop'}, build(), decision(useful=False))


# 真实合成输出中的正常服务邀请与致谢不包含事实，不能因为措辞不同被拒绝。
@pytest.mark.parametrize('answer', [
    '您好！很高兴为您服务。请问有什么可以帮您的吗？例如查询订单、物流进度，或了解售后流程等。',
    '不客气，很高兴能帮到您！😊\n\n如后续还有订单、物流或其他售后方面的疑问，欢迎随时联系我们。祝您购物愉快！',
])
def test_recorded_benign_social_invitation_and_thanks_are_valid(answer):
    module, _ = api()
    module.validate_answer(answer, {'stop'}, build(payload(())), decision('social'))


# 与正常服务措辞近似但增加业务断言的变体，必须仍然拒绝。
@pytest.mark.parametrize('answer', [
    '您好！很高兴为您服务。请问有什么可以帮您的吗？退款保证明天到账。',
    '不客气，很高兴能帮到您！😊\n\n您的订单已发货，欢迎随时联系我们。祝您购物愉快！',
    '您好！例如查询订单、物流进度，或了解售后流程等。拆封后也能退货。',
    '不客气，很高兴能帮到您！😊待处理工单表示已经完成退款。',
])
def test_social_invitation_factual_near_neighbors_are_rejected(answer):
    module, _ = api()
    with pytest.raises(ServiceError):
        module.validate_answer(answer, {'stop'}, build(payload(())), decision('social'))


# 重测批次的缺订单号答复只有查询目的和必要信息请求，应作为合法澄清。
def test_recorded_missing_order_identifier_request_is_valid():
    module, _ = api()
    module.validate_answer('您好！为了帮您查询订单的物流情况，请提供一下您的订单号，谢谢～',
                           {'stop'}, build(payload(())), decision('clarification'))


# 合法查询目的不能让附加配送保证通过，也不能单独代替必要信息追问。
@pytest.mark.parametrize('answer', [
    '您好！为了帮您查询订单的物流情况，请提供一下您的订单号，包裹保证明天送到，谢谢～',
    '您好！为了帮您查询订单的物流情况，谢谢～',
])
def test_clarification_context_cannot_hide_delivery_promise_or_replace_request(answer):
    module, _ = api()
    with pytest.raises(ServiceError):
        module.validate_answer(answer, {'stop'}, build(payload(())), decision('clarification'))


@pytest.mark.parametrize('tail', ['', '可以退货', '已发货', '三天到账'])
def test_recorded_step_question_particle_accepts_only_clarification(tail):
    """真实带呢追问可通过，但追加政策、状态或到账承诺仍拒绝。"""
    module, _ = api()
    answer = '可以的，您买的是什么商品或型号？具体在哪一步不会操作呢？' + tail
    if tail:
        with pytest.raises(ServiceError) as error:
            module.validate_answer(answer, {'stop'}, build(payload(())), decision('clarification'))
        assert error.value.code == 'invalid_answer'
    else:
        module.validate_answer(answer, {'stop'}, build(payload(())), decision('clarification'))
