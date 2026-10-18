import pytest
from langchain_core.messages import AIMessage, ToolMessage
from app.tools.catalog import ToolCatalog
from app.tools.types import ToolContext, ExecutionContext
from app.tools.executor import ToolExecutor
from tests.tool_system_fakes import make_registration, allow_policy
from tests.test_tool_execution_policy import AuditSink
from tests.test_workflow_agent import setup, run, control
from tests.workflow_fakes import workflow_call


def dynamic_runtime(replies):
    context, state = setup(replies, intent='其他', question='演示站点在哪里', answer='演示站点位于成都。')
    async def handler():
        return {'site': '成都', 'mock': True}
    item = make_registration('query_demo_site', handler=handler)
    catalog = ToolCatalog()
    catalog.register(item)
    context.registry = catalog.snapshot(policy=allow_policy(item)).bind(ToolContext('1', 2, state['raw_question']))
    context.execution_context = ExecutionContext('1', 2, '其他', state['raw_question'])
    audit = AuditSink()
    context.executor = ToolExecutor(audit_sink=audit)
    return context, state, audit


async def test_newly_registered_tool_is_bound_executed_and_audited_by_real_agent():
    context, state, audit = dynamic_runtime([workflow_call('query_demo_site', {}), control()])
    result, _ = await run(context, state)
    assert result['tool_call_count'] == 1 and '成都' in result['final_answer']
    names = {t['function']['name'] for t in context.decision_model.bound_tools[0]}
    assert 'query_demo_site' in names
    assert audit.records[0].tool_name == 'query_demo_site' and audit.records[0].source == 'builtin'
    assert any(isinstance(message, ToolMessage) and '成都' in message.content for message in result['messages'])


async def test_unknown_native_tool_reaches_denial_audit():
    context, state, audit = dynamic_runtime([workflow_call('not_authorized', {}), control('clarification')])
    context.model.final_chunks[0].content = '请提供订单号。'
    result, _ = await run(context, state)
    assert audit.records[0].tool_name == 'not_authorized' and audit.records[0].status == 'permission_denied'
    assert result['tool_call_count'] == 1


async def test_body_json_cannot_become_tool_execution():
    from app.core.errors import ServiceError
    context, state, audit = dynamic_runtime([AIMessage('{"name":"query_demo_site","args":{}}', response_metadata={'finish_reason': 'stop'})])
    context.model_recovery_used = True
    with pytest.raises(ServiceError):
        await run(context, state)
    assert audit.records == []


async def test_forced_order_and_policy_reads_use_same_audit_engine():
    from app.tools.registry import build_catalog
    from app.tools.policies import PolicyStore
    from pathlib import Path
    from tests.test_after_sales_workflow import context, invoke
    ctx = context()
    async def owner(cid):
        return 'demo-user'
    catalog = build_catalog(ctx.faq_repository, object(), order_provider=ctx.order_provider, owner_resolver=owner)
    ctx.registry = catalog.snapshot(policy=PolicyStore(Path('config/tool-policy.json')).load()).bind(ToolContext('1', 7, '订单1001能退吗？'))
    audit = AuditSink()
    ctx.executor = ToolExecutor(audit_sink=audit)
    _, result = await invoke(ctx, '订单1001能退吗？')
    assert result['order_snapshot']['order_id'] == '1001'
    assert [row.tool_name for row in audit.records] == ['query_order', 'query_faq']
    assert all(row.source == 'builtin' and row.status == 'success' for row in audit.records)


def test_ticket_description_requires_user_issue_and_verified_clarification_source():
    from app.workflow.ticket_requests import ticket_request_for_turn, grounded_description
    first = ticket_request_for_turn(1, '帮我建个工单', {})
    previous = {'intent': '工单', 'reply_mode': 'clarification', 'ticket_request': first}
    assert not grounded_description('帮我建个工单', first)
    assert ticket_request_for_turn(3, '饮水机漏水', previous) is None
    continued = ticket_request_for_turn(3, '饮水机漏水', previous, previous_verified=True)
    assert grounded_description('饮水机漏水', continued)
    assert not grounded_description('已确认设备损坏需要赔偿', continued)
    assert ticket_request_for_turn(4, '不要建单，只查物流', previous, previous_verified=True) is None
