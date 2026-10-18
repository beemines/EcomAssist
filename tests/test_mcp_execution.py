from langchain_mcp_adapters.client import MultiServerMCPClient
from app.tools.catalog import ToolCatalog
from app.tools.mcp_client import MCPDiscovery
from app.tools.policies import PolicySnapshot
from app.tools.executor import ToolExecutor
from app.tools.types import ToolContext, ToolCall, ExecutionContext
from tests.mcp_processes import server_process
from tests.test_mcp_discovery import policy
from tests.test_tool_execution_policy import AuditSink


async def test_real_adapter_runs_through_engine_with_identity_guard_and_source_audit(tmp_path):
    async with server_process('business_mcp.logistics', tmp_path) as (_, connection):
        local = PolicySnapshot.from_dict(policy({'logistics': connection}))
        discovery = await MCPDiscovery(MultiServerMCPClient(local.servers)).discover(local)
        catalog = ToolCatalog().snapshot(policy=local, discovered=discovery.registrations).bind(ToolContext('1', 2, '查物流1001'))
        async def owner(order_id):
            return order_id == '1001'
        audit = AuditSink()
        context = ExecutionContext('1', 2, '物流', '查物流1001', policy=local, order_authorizer=owner)
        executor = ToolExecutor(audit_sink=audit)
        result = await executor.execute(ToolCall('call', 'query_logistics', {'order_id': '1001'}), catalog, context=context)
        assert result.status == 'success' and result.content['mock'] and result.content['order_id'] == '1001'
        assert audit.records[-1].source == 'mcp:logistics'
        rejected = await executor.execute(ToolCall('other', 'query_logistics', {'order_id': 'someone_else'}), catalog, context=context)
        assert rejected.attempts == 0 and audit.records[-1].status == 'permission_denied'


async def test_actual_remote_iserror_remains_failure(tmp_path):
    async with server_process('business_mcp.logistics', tmp_path) as (_, connection):
        from app.tools.results import normalize_result
        client = MultiServerMCPClient({'logistics': connection})
        tool = (await client.get_tools(server_name='logistics'))[0]
        # Empty ID reaches the server validation and produces protocol isError.
        raw = await tool.ainvoke({'type': 'tool_call', 'name': tool.name, 'args': {'order_id': ''}, 'id': 'bad'})
        assert raw.status == 'error'
        local = PolicySnapshot.from_dict(policy({'logistics': connection}))
        found = await MCPDiscovery(client).discover(local)
        definition = found.registrations[0].definition
        assert normalize_result(raw, definition).status == 'error'


async def test_remote_transport_failure_retries_once_and_is_audited(tmp_path):
    import asyncio
    async with server_process('business_mcp.logistics', tmp_path) as (process, connection):
        local = PolicySnapshot.from_dict(policy({'logistics': connection}))
        found = await MCPDiscovery(MultiServerMCPClient(local.servers)).discover(local)
        catalog = ToolCatalog().snapshot(policy=local, discovered=found.registrations).bind(ToolContext('1', 2, '查物流1001'))
        process.terminate()
        await asyncio.to_thread(process.wait, timeout=5)
        async def owner(order_id): return order_id == '1001'
        audit = AuditSink()
        context = ExecutionContext('1', 2, '物流', '查物流1001', policy=local, order_authorizer=owner)
        result = await ToolExecutor(audit_sink=audit).execute(
            ToolCall('down', 'query_logistics', {'order_id': '1001'}), catalog, context=context)
        assert result.content['error']['code'] == 'tool_connection_error'
        assert result.attempts == 2 and audit.records[-1].retry_count == 1
