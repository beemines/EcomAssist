import json
from langchain_mcp_adapters.client import MultiServerMCPClient
from app.tools.catalog import ToolCatalog
from app.tools.mcp_client import MCPDiscovery, ToolCatalogProvider
from app.tools.policies import PolicySnapshot, PolicyStore
from tests.mcp_processes import server_process


def policy(connections, *, extra=False):
    tools = [dict(source='mcp:logistics', name='query_logistics', operation='read', order_id_arg='order_id'),
        dict(source='mcp:aftersales', name='query_warranty', operation='read', order_id_arg='order_id'),
        dict(source='mcp:aftersales', name='query_return_progress', operation='read', order_id_arg='order_id')]
    if extra:
        tools.append(dict(source='mcp:logistics', name='query_pickup_hours', operation='read', order_id_arg='order_id'))
    return {'servers': connections, 'tools': tools}


async def test_discovery_isolates_dead_server_and_does_not_authorize_unknown(tmp_path):
    async with server_process('business_mcp.logistics', tmp_path, plugin='examples.mcp_extra_tools') as (_, connection):
        config = policy({'logistics': connection, 'aftersales': {**connection, 'url': 'http://127.0.0.1:1/mcp'}})
        local = PolicySnapshot.from_dict(config)
        discovery = MCPDiscovery(MultiServerMCPClient(local.servers))
        found = await discovery.discover(local)
        assert 'aftersales' in found.errors and 'logistics' not in found.errors
        snapshot = ToolCatalog().snapshot(policy=local, discovered=found.registrations)
        assert set(snapshot.definitions) == {'query_logistics'}
        assert snapshot.definitions['query_logistics'].source == 'mcp:logistics'
        assert snapshot.definitions['query_logistics'].order_id_arg == 'order_id'


async def test_hot_local_permission_exposes_existing_new_remote_tool_next_turn(tmp_path):
    async with server_process('business_mcp.logistics', tmp_path, plugin='examples.mcp_extra_tools') as (_, connection):
        config = policy({'logistics': connection})
        path = tmp_path / 'policy.json'
        path.write_text(json.dumps(config))
        provider = ToolCatalogProvider(ToolCatalog(), PolicyStore(path), MCPDiscovery())
        first = await provider.acquire()
        assert set(first.definitions) == {'query_logistics'}
        path.write_text(json.dumps(policy({'logistics': connection}, extra=True)))
        second = await provider.acquire()
        assert set(second.definitions) == {'query_logistics', 'query_pickup_hours'}
        assert first.version != second.version
        restored = await provider.restore(first.to_manifest())
        assert set(restored.definitions) == {'query_logistics'}
