"""退款表单只允许四个定位/原因字段，服务器草稿不受外部字典变更影响。"""
import importlib
from dataclasses import FrozenInstanceError

import pytest
from pydantic import ValidationError


def types():
    """缺失功能以明确断言呈现，避免仅依赖导入报错。"""
    try:
        return importlib.import_module('app.refunds.types')
    except ImportError:
        pytest.fail('refund contracts are not implemented')


def payload():
    """四字段是浏览器唯一可写协议。"""
    return {'assistant_message_id': '2', 'checkpoint_id': '00000000-0000-0000-0000-000000000001',
        'offer_id': '00000000-0000-0000-0000-000000000002', 'reason': 'quality'}


@pytest.mark.parametrize('patch', [{'amount_cents': 1}, {'status': '已退款'}, {'order_id': '1001'},
    {'user_id': 'other'}, {'reason': 'unknown'}, {'reason': ''}, {'reason': None},
    {'assistant_message_id': 2}, {'assistant_message_id': '02'}, {'checkpoint_id': 'child:root'},
    {'offer_id': 'bad'}])
def test_untrusted_form_fields_rejected(patch):
    """缺严格校验会允许浏览器伪造身份、金额或原因。"""
    with pytest.raises(ValidationError):
        types().RefundActionRequest.model_validate(payload() | patch)


def test_reason_required_and_valid_form_accepted():
    """原因必须由用户显式选择，不能默认。"""
    body = payload()
    assert types().RefundActionRequest.model_validate(body).reason == 'quality'
    del body['reason']
    with pytest.raises(ValidationError):
        types().RefundActionRequest.model_validate(body)


def test_draft_is_deeply_immutable():
    """后续代码修改来源或读取副本不能篡改已验证草稿。"""
    order = {'amount_cents': 19900, 'currency': 'CNY'}
    draft = types().RefundDraft(conversation_id='1', user_message_id='1', assistant_message_id='2',
        checkpoint_id=payload()['checkpoint_id'], offer_id=payload()['offer_id'], user_id='demo-user',
        order_id='1001', amount_cents=19900, currency='CNY', order_snapshot=order,
        policy_snapshot={'matches': [{'answer': '原文'}]}, decision_snapshot={'refund_decision': 'needs_review'},
        raw_question='退货', final_answer='待审核')
    order['amount_cents'] = 1
    draft.policy_snapshot['matches'][0]['answer'] = '篡改'
    assert draft.order_snapshot['amount_cents'] == 19900
    assert draft.policy_snapshot == {'matches': [{'answer': '原文'}]}
    with pytest.raises(FrozenInstanceError):
        draft.amount_cents = 1


async def test_lifespan_real_database_only_verifies_refunds(tmp_path, monkeypatch):
    """真实DB注入启动仍只调用verify；核验故障直接阻止启动。"""
    from types import SimpleNamespace
    import app.main as main
    from tests.fakes import FAQStub, fake_settings
    from tests.test_order_resume_lifecycle import OwnerStore
    from tests.workflow_fakes import ScriptedWorkflowModel
    calls = []
    async def quality(database):
        """隔离无关旧schema核验。"""
        calls.append('quality')
    async def refunds(database):
        """启动核验失败必须向上层传播而不能自动迁移。"""
        calls.append('refunds')
        raise RuntimeError('refund schema missing')
    monkeypatch.setattr(main, 'verify_quality', quality)
    monkeypatch.setattr(main, 'verify_refunds', refunds)
    store = OwnerStore()
    app = main.create_app(fake_settings(workflow_checkpoint_path=tmp_path / 'unused.sqlite'),
        database=SimpleNamespace(engine=object()), repository=store, model=ScriptedWorkflowModel(),
        faq_repository=FAQStub(), quality_repository=store)
    with pytest.raises(RuntimeError, match='refund schema missing'):
        async with app.router.lifespan_context(app):
            pytest.fail('unverified database started')
    assert calls == ['quality', 'refunds']


def test_cli_invalid_command_does_not_open_database(monkeypatch):
    """误写命令在创建连接之前即非零退出。"""
    from app.refunds import cli
    def unexpected(*args):
        """非法命令不应触达配置或数据库。"""
        pytest.fail('database opened for invalid CLI input')
    monkeypatch.setattr(cli, 'Database', unexpected)
    with pytest.raises(SystemExit) as exc:
        cli.main(['migrate'])
    assert exc.value.code == 2
