"""Real Agent graph/executor and two real MCP processes; model decisions are scripted."""
from langchain_mcp_adapters.client import MultiServerMCPClient
from app.tools.catalog import ToolCatalog
from app.tools.mcp_client import MCPDiscovery
from app.tools.policies import PolicySnapshot
from app.tools.types import ToolContext, ExecutionContext
from app.tools.executor import ToolExecutor
from tests.mcp_processes import server_process
from tests.test_mcp_discovery import policy
from tests.test_tool_execution_policy import AuditSink
from tests.test_workflow_agent import setup, run, control
from tests.workflow_fakes import workflow_call


async def test_three_mcp_reads_produce_paired_history_audit_and_final_answer(tmp_path):
    async with server_process('business_mcp.logistics', tmp_path) as (_, logistics):
        async with server_process('business_mcp.aftersales', tmp_path) as (_, aftersales):
            local = PolicySnapshot.from_dict(policy({'logistics': logistics, 'aftersales': aftersales}))
            found = await MCPDiscovery(MultiServerMCPClient(local.servers)).discover(local)
            names = ['query_logistics', 'query_warranty', 'query_return_progress']
            context, state = setup([*[workflow_call(name, {'order_id': '1001'}, name) for name in names], control()],
                question='查询订单1001的物流、在保状态和退货进度', intent='订单', answer='以上为订单1001的模拟查询结果。')
            context.registry = ToolCatalog().snapshot(policy=local, discovered=found.registrations).bind(ToolContext('1', 2, state['raw_question']))
            async def owner(order_id): return order_id == '1001'
            context.execution_context = ExecutionContext('1', 2, '订单', state['raw_question'], policy=local, order_authorizer=owner)
            audit = AuditSink(); context.executor = ToolExecutor(audit_sink=audit)
            result, _ = await run(context, state)
            assert result['tool_call_count'] == 3 and result['final_answer'].endswith('以上为订单1001的模拟查询结果。')
            assert [row.tool_name for row in audit.records] == names
            assert [row.source for row in audit.records] == ['mcp:logistics', 'mcp:aftersales', 'mcp:aftersales']
            assert all(row.status == 'success' for row in audit.records)
