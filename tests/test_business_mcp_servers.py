import json
from langchain_mcp_adapters.client import MultiServerMCPClient
from tests.mcp_processes import server_process


async def test_separate_servers_discover_and_call_three_real_http_tools(tmp_path):
    async with server_process('business_mcp.logistics', tmp_path) as (logistics, one), server_process('business_mcp.aftersales', tmp_path) as (aftersales, two):
        assert logistics.pid != aftersales.pid
        client = MultiServerMCPClient({'logistics': one, 'aftersales': two})
        tools = {tool.name: tool for tool in await client.get_tools()}
        assert set(tools) == {'query_logistics', 'query_warranty', 'query_return_progress'}
        for name, tool in tools.items():
            assert tool.args_schema['properties']['order_id']['type'] == 'string'
            result = await tool.ainvoke({'type': 'tool_call', 'name': name, 'args': {'order_id': '1001'}, 'id': 'call'})
            assert result.status == 'success'
            data = result.artifact['structured_content']
            assert data['mock'] is True and data['order_id'] == '1001'
            assert data['source'] in ('mcp:logistics', 'mcp:aftersales')
            if name == 'query_logistics':
                assert data['status'] in ('已揽收', '运输中', '派送中', '已签收')
                assert isinstance(data['events'], list) and data['tracking_no'].startswith('MOCK')
            elif name == 'query_warranty':
                assert data['warranty_status'] in ('在保', '已过保')
            else:
                assert data['return_status'] in ('待寄回', '仓库验收中', '审核中', '已完成')


async def test_local_server_plugin_adds_tool_without_database(tmp_path):
    async with server_process('business_mcp.logistics', tmp_path, plugin='examples.mcp_extra_tools') as (_, connection):
        tools = await MultiServerMCPClient({'logistics': connection}).get_tools(server_name='logistics')
        extra = next(tool for tool in tools if tool.name == 'query_pickup_hours')
        result = await extra.ainvoke({'type': 'tool_call', 'name': extra.name, 'args': {'order_id': '1001'}, 'id': 'extra'})
        assert result.artifact['structured_content']['pickup_hours'] == '09:00–18:00'
