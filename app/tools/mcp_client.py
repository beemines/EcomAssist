"""Official multi-server adapter discovery with local authority and per-turn snapshots."""
import asyncio
from dataclasses import dataclass
import logging

from langchain_mcp_adapters.client import MultiServerMCPClient
from app.tools.catalog import validate_definition
from app.tools.catalog_types import ToolDefinition, ToolRegistration, fingerprint
from app.tools.plugins import PluginLoader

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class DiscoveryResult:
    registrations: tuple[ToolRegistration, ...]
    errors: dict[str, str]


class MCPDiscovery:
    def __init__(self, client: MultiServerMCPClient | None = None):
        self._supplied_client = client
        self._client = client
        self._connections_version = None

    async def discover(self, policy) -> DiscoveryResult:
        connections = policy.servers
        version = fingerprint(connections)
        if self._supplied_client is None and (self._client is None or version != self._connections_version):
            self._client = MultiServerMCPClient(connections, tool_name_prefix=False, handle_tool_errors=True)
            self._connections_version = version
        client = self._client
        registrations, errors = [], {}

        async def discover_one(server_name):
            try:
                connection = connections[server_name]
                async with asyncio.timeout(float(connection.get('timeout', 3)) + 1):
                    tools = await client.get_tools(server_name=server_name)
                items = []
                for tool in tools:
                    # Annotations and text are never sources of authorization.
                    definition = ToolDefinition(name=tool.name, description=tool.description,
                        input_schema=tool.args_schema, source='mcp:' + server_name,
                        remote_name=tool.name, operation='read')
                    if not policy.allows(definition.source, definition.name):
                        continue
                    validate_definition(definition)
                    items.append(ToolRegistration(definition, lambda context, adapted=tool: adapted))
                return items, None
            except asyncio.CancelledError:
                raise
            except Exception as exc:
                logger.warning('stage=mcp_discovery server=%s status=unavailable type=%s', server_name, type(exc).__name__)
                return [], type(exc).__name__

        results = await asyncio.gather(*(discover_one(name) for name in connections))
        for name, (items, error) in zip(connections, results):
            registrations.extend(items)
            if error:
                errors[name] = error
        return DiscoveryResult(tuple(registrations), errors)


class ToolCatalogProvider:
    def __init__(self, catalog, policies, discovery):
        self.catalog, self.policies, self.discovery = catalog, policies, discovery
        self.plugins = PluginLoader()
        self.errors = {}

    async def _current(self):
        policy = self.policies.load()
        self.plugins.load(self.catalog, policy.plugins)
        discovered = await self.discovery.discover(policy)
        self.errors = discovered.errors
        return policy, discovered.registrations

    async def acquire(self):
        policy, discovered = await self._current()
        return self.catalog.snapshot(policy=policy, discovered=discovered)

    async def restore(self, manifest, *, required=None):
        if required is not None and required == {'create_ticket'}:
            # Deterministic ticket continuation needs no remote discovery or new plugins.
            return self.catalog.restore(manifest, policy=self.policies.load(), required=required)
        policy, discovered = await self._current()
        return self.catalog.restore(manifest, policy=policy, discovered=discovered, required=required)
