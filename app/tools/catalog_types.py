"""Pure-data tool contracts; runtime handlers never enter checkpoints."""
from collections.abc import Callable, Iterable, Iterator, Mapping
from copy import deepcopy
from dataclasses import asdict, dataclass, field
import hashlib
import json
from types import MappingProxyType

from langchain_core.tools import BaseTool
from app.tools.types import ToolContext


def fingerprint(value: object) -> str:
    return hashlib.sha256(json.dumps(value, ensure_ascii=False, sort_keys=True,
        separators=(',', ':'), allow_nan=False).encode()).hexdigest()


@dataclass(frozen=True)
class ToolDefinition:
    name: str
    description: str
    input_schema: dict
    source: str = 'builtin'
    remote_name: str | None = None
    operation: str = 'read'
    allowed_intents: tuple[str, ...] = ()
    order_id_arg: str | None = None
    output_fields: tuple[str, ...] = ()
    status_map: dict[str, str] = field(default_factory=dict)
    timeout_seconds: float | None = None
    max_retries: int | None = None

    @property
    def fingerprint(self) -> str:
        return fingerprint(asdict(self))


@dataclass(frozen=True)
class ToolRegistration:
    definition: ToolDefinition
    factory: Callable[[ToolContext], BaseTool]


class BoundCatalog(Mapping[str, BaseTool]):
    def __init__(self, registrations: Mapping[str, ToolRegistration], context: ToolContext,
                 *, version: str = ''):
        self._registrations = dict(registrations)
        self._context = context
        self._tools = {name: r.factory(context) for name, r in registrations.items()}
        self.version = version

    def __getitem__(self, key: str) -> BaseTool:
        return self._tools[key]

    def __iter__(self) -> Iterator[str]:
        return iter(self._tools)

    def __len__(self) -> int:
        return len(self._tools)

    def definition(self, name: str) -> ToolDefinition:
        return deepcopy(self._registrations[name].definition)

    def subset(self, names: Iterable[str]) -> 'BoundCatalog':
        selected = set(names)
        result = object.__new__(BoundCatalog)
        result._registrations = {k: v for k, v in self._registrations.items() if k in selected}
        result._tools = {k: v for k, v in self._tools.items() if k in selected}
        result._context, result.version = self._context, self.version
        return result

    def with_tool(self, name: str, tool: BaseTool) -> 'BoundCatalog':
        """Trusted local binding options only; never change the public contract."""
        schema = tool.tool_call_schema
        schema = schema if isinstance(schema, dict) else schema.model_json_schema()
        definition = self.definition(name)
        if tool.name != name or schema != definition.input_schema:
            raise ValueError('Runtime binding changed its tool contract.')
        result = self.subset(self)
        result._tools[name] = tool
        return result


class CatalogSnapshot:
    def __init__(self, registrations: Mapping[str, ToolRegistration]):
        self._registrations = {name: ToolRegistration(deepcopy(r.definition), r.factory)
            for name, r in sorted(registrations.items())}
        self.version = fingerprint(self.to_manifest(include_version=False))

    @property
    def definitions(self) -> Mapping[str, ToolDefinition]:
        return MappingProxyType({k: deepcopy(v.definition) for k, v in self._registrations.items()})

    def bind(self, context: ToolContext) -> BoundCatalog:
        return BoundCatalog(self._registrations, context, version=self.version)

    def to_manifest(self, *, include_version: bool = True) -> dict:
        data = {'tools': [asdict(r.definition) for r in self._registrations.values()]}
        if include_version:
            data['version'] = self.version
        return data
