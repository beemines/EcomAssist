"""Local administrator policy is the sole source of tool authority."""
from copy import deepcopy
from dataclasses import dataclass, field
import json
import math
from pathlib import Path

from app.tools.catalog_types import fingerprint


@dataclass(frozen=True)
class PolicySnapshot:
    version: str
    _rules: dict = field(repr=False)
    _servers: dict = field(default_factory=dict, repr=False)
    plugins: tuple[str, ...] = ()

    @classmethod
    def from_dict(cls, data: dict) -> 'PolicySnapshot':
        if not isinstance(data, dict) or set(data) - {'tools', 'servers', 'plugins'}:
            raise ValueError('Invalid local tool policy.')
        rules = {}
        for raw in data.get('tools', []):
            if not isinstance(raw, dict) or set(raw) - {'source', 'name', 'operation',
                    'allowed_intents', 'order_id_arg', 'output_fields', 'status_map',
                    'timeout_seconds', 'max_retries'}:
                raise ValueError('Invalid tool authorization rule.')
            rule = deepcopy(raw)
            source, name, operation = rule.get('source'), rule.get('name'), rule.get('operation')
            if not isinstance(source, str) or not isinstance(name, str) or operation not in ('read', 'write'):
                raise ValueError('Invalid tool authority.')
            if operation == 'write' and (source != 'builtin' or name != 'create_ticket'):
                raise ValueError('Only builtin create_ticket may write.')
            if (source, name) in rules:
                raise ValueError('Duplicate policy rule.')
            for key in ('allowed_intents', 'output_fields'):
                if key in rule and (not isinstance(rule[key], list) or not all(isinstance(v, str) for v in rule[key])):
                    raise ValueError('Invalid rule list.')
            if 'timeout_seconds' in rule and (type(rule['timeout_seconds']) not in (int, float)
                    or not math.isfinite(rule['timeout_seconds']) or rule['timeout_seconds'] <= 0):
                raise ValueError('Invalid timeout.')
            if 'max_retries' in rule and (type(rule['max_retries']) is not int or rule['max_retries'] not in (0, 1)):
                raise ValueError('Invalid retry limit.')
            if 'status_map' in rule and (not isinstance(rule['status_map'], dict)
                    or not all(isinstance(k, str) and isinstance(v, str) for k, v in rule['status_map'].items())):
                raise ValueError('Invalid result mapping.')
            if 'order_id_arg' in rule and not isinstance(rule['order_id_arg'], str):
                raise ValueError('Invalid order identity constraint.')
            rules[source, name] = rule
        servers = data.get('servers', {})
        if not isinstance(servers, dict):
            raise ValueError('Invalid MCP servers.')
        for name, connection in servers.items():
            if not isinstance(name, str) or not isinstance(connection, dict) or connection.get('transport') != 'streamable_http':
                raise ValueError('Only Streamable HTTP servers are supported.')
            if set(connection) - {'transport', 'url', 'timeout', 'sse_read_timeout'} or not isinstance(connection.get('url'), str):
                raise ValueError('Invalid MCP connection.')
        plugins = data.get('plugins', [])
        if not isinstance(plugins, list) or not all(isinstance(v, str) and v for v in plugins):
            raise ValueError('Invalid local plugin entry.')
        return cls(fingerprint(data), rules, deepcopy(servers), tuple(plugins))

    @property
    def servers(self) -> dict:
        return deepcopy(self._servers)

    def rule(self, source: str, name: str) -> dict | None:
        return deepcopy(self._rules.get((source, name)))

    def allows(self, source: str, name: str) -> bool:
        return (source, name) in self._rules


class PolicyStore:
    def __init__(self, path: Path):
        self.path = path

    def load(self) -> PolicySnapshot:
        # No cached partially parsed policy and no fallback that retains revoked rights.
        return PolicySnapshot.from_dict(json.loads(self.path.read_text(encoding='utf-8-sig')))
