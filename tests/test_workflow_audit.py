"""独立默认 Uvicorn 进程验证可见审计，避免测试框架 INFO 配置掩盖缺陷。"""
import asyncio
import json
import logging
from pathlib import Path
import subprocess
import sys
import tempfile

from app.core.errors import ServiceError
from tests.fakes import decode_sse
from tests.test_chat_actions import offered_app, confirm
from tests.test_workflow_api import Store, workflow_app, request, intent
from tests.test_workflow_lifecycle import BlockedModel, blocked_clarification_app
from tests.workflow_fakes import ScriptedWorkflowModel


def test_default_uvicorn_visible_safe_audit():
    """默认配置若隐藏 INFO、漏记终态/工单或泄漏内容，真实控制台断言必须失败。"""
    result = subprocess.run([sys.executable, str(Path(__file__).resolve())],
        capture_output=True, text=True, encoding='utf-8', timeout=60)
    assert result.returncode == 0, result.stderr
    records = [json.loads(line) for line in result.stderr.splitlines() if line.startswith('{')]
    assert any(r.get('node') == 'retrieve_knowledge' for r in records)
    assert any(r.get('node') == 'confidence_gate' and r.get('reason_code') == 'retrieval_low_conf' for r in records)
    terminals = [r for r in records if r.get('phase') == 'terminal']
    assert [r['outcome'] for r in terminals] == [
        'success', 'success', 'error', 'timeout', 'timeout', 'error', 'disconnected', 'cancelled', 'disconnected', 'success', 'success']
    assert all(r['conversation_id'] == '1' and r['user_message_id'] for r in terminals)
    assert any(r.get('decision_count') == 1 for r in terminals if r['outcome'] in ('disconnected', 'cancelled'))
    actions = [r for r in records if r.get('event') == 'workflow_ticket']
    assert [r['phase'] for r in actions] == ['confirmed', 'result'] * 3
    assert [r.get('outcome') for r in actions if r['phase'] == 'result'] == ['success', 'success', 'error']
    assert all(r['user_message_id'] == '1' and r['assistant_message_id'] == '2'
        and r['action'] == 'create_ticket' for r in actions)
    assert all(r['ticket_no'] == 'T00000000000000000000000000000001'
        for r in actions if r.get('outcome') == 'success')
    assert 'SECRET_SENTINEL' not in result.stderr
    assert 'structured_control' not in result.stderr and 'raw_question' not in result.stderr


def test_setup_preserves_external_capture_handler():
    """重复安装不能改写测试框架或调用方提供的捕获流和格式器。"""
    import io
    from app.workflow.logging import logger, configure_workflow_logging, log_audit
    stream = io.StringIO()
    handler = logging.StreamHandler(stream)
    formatter = logging.Formatter('%(message)s')
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    try:
        configure_workflow_logging()
        configure_workflow_logging()
        log_audit('workflow_node', node='resolve_reference')
        assert handler.stream is stream and handler.formatter is formatter
        assert stream.getvalue() == 'workflow_node\n'
    finally:
        logger.removeHandler(handler)


async def audit_scenarios(root):
    """真实服务与官方 SQLite 执行成功、故障、取消、重复确认，收费边界均替换。"""
    from uvicorn import Config
    Config('app.main:create_app', factory=True).configure_logging()
    root_handlers = list(logging.getLogger().handlers)
    root_level = logging.getLogger().level
    async with workflow_app(root / 'social') as app:
        assert decode_sse((await request(app, '你好')).text)[-1][0] == 'done'
    async with workflow_app(root / 'knowledge', model=ScriptedWorkflowModel(intent_replies=[intent('商品咨询')])) as app:
        await request(app, 'SECRET_SENTINEL 政策')
    for name, failure in [('service', ServiceError('invalid_structured_output', 'SECRET_SENTINEL', 502)),
            ('timeout', TimeoutError('SECRET_SENTINEL'))]:
        model = ScriptedWorkflowModel(intent_replies=[failure])
        async with workflow_app(root / name, model=model) as app:
            assert decode_sse((await request(app, 'SECRET_SENTINEL')).text)[-1][0] == 'error'
    async with blocked_clarification_app(root / 'deadline', model=BlockedModel()) as app:
        service = app.state.chat_service
        prepared = await service.prepare('1', 'SECRET_SENTINEL 商品怎么使用')
        prepared.deadline = asyncio.get_running_loop().time() + .05
        events = [event async for event in service.stream(prepared)]
        service.release(prepared)
        assert events[-1].event == 'error' and events[-1].data['code'] == 'upstream_timeout'
    class FailedStore(Store):
        """模型外故障保留通用异常分支，绝不能记录异常文本。"""
        async def append_message(self, conversation_id, message):
            """最终SQL提交注入离线故障，用户消息仍正常保存。"""
            if message.type == 'ai':
                raise RuntimeError('SECRET_SENTINEL')
            return await super().append_message(conversation_id, message)
    async with workflow_app(root / 'unexpected', store=FailedStore()) as app:
        await request(app, '你好')
    for name in ('disconnect', 'shutdown'):
        model = BlockedModel()
        async with blocked_clarification_app(root / name, model=model) as app:
            service = app.state.chat_service
            prepared = await service.prepare('1', 'SECRET_SENTINEL 商品怎么使用')
            events = service.stream(prepared)
            async for event in events:
                if event.event == 'citations':
                    break
            await asyncio.wait_for(model.waiting.wait(), 3)
            if name == 'shutdown':
                await service.shutdown()
            await events.aclose()
            service.release(prepared)
            service.release(prepared)
    async with workflow_app(root / 'unstarted') as app:
        service = app.state.chat_service
        prepared = await service.prepare('1', '你好')
        service.release(prepared)
        service.release(prepared)
    async with offered_app(root / 'ticket', question='SECRET_SENTINEL 投诉') as (app, client, tickets, _, payload):
        await request(app, '你好')
        assert (await confirm(client, payload)).status_code == 200
        assert (await confirm(client, payload)).status_code == 200
        tickets.rows.clear()
        tickets.status = '已结束'
        assert (await confirm(client, payload)).status_code != 200
    from app.workflow.nodes import log_node
    log_node({'conversation_id': '1', 'user_message_id': '1', 'intent': '订单', 'route': 'business'},
        'llm_call', raw_question='SECRET_SENTINEL', structured_control='SECRET_SENTINEL',
        tool_call_id='SECRET_SENTINEL', reason_code='SECRET_SENTINEL', usage={'actual': 1, 'secret': 'SECRET_SENTINEL'})
    assert logging.getLogger().handlers == root_handlers and logging.getLogger().level == root_level
    audit = logging.getLogger('app.workflow.audit')
    assert len(audit.handlers) == 1 and not audit.propagate
    from app.workflow.logging import safe_fields
    assert safe_fields({'ticket_no': 'T' + 'a' * 31}) == {'ticket_no': 'T' + 'a' * 31}


if __name__ == '__main__':
    with tempfile.TemporaryDirectory() as directory:
        asyncio.run(audit_scenarios(Path(directory)))
