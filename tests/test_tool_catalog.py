"""Catalog mutation, authorization and durable contracts at the consumer boundary."""
import json
from dataclasses import replace

import pytest

from app.tools.catalog import ToolCatalog
from app.tools.catalog_types import ToolDefinition, ToolRegistration
from app.tools.policies import PolicyStore
from tests.tool_system_fakes import make_registration, allow_policy
from app.tools.types import ToolContext


def test_registration_snapshot_is_immutable_and_next_turn_sees_addition():
    catalog = ToolCatalog()
    first = make_registration('first')
    second = make_registration('second')
    catalog.register(first)
    old = catalog.snapshot(policy=allow_policy(first, second))
    catalog.register(second)
    current = catalog.snapshot(policy=allow_policy(first, second))
    assert list(old.definitions) == ['first']
    assert list(current.bind(ToolContext('1', 2, 'hi'))) == ['first', 'second']
    assert current.to_manifest()['version'] == current.version
    with pytest.raises(TypeError):
        old.definitions['second'] = second.definition


def test_unknown_external_and_external_write_cannot_grant_themselves_access():
    remote = make_registration('remote', source='mcp:logistics')
    catalog = ToolCatalog()
    assert not catalog.snapshot(policy=allow_policy(), discovered=[remote]).definitions
    write = replace(remote, definition=replace(remote.definition, operation='write'))
    with pytest.raises(ValueError):
        catalog.snapshot(policy=allow_policy(write), discovered=[write])


@pytest.mark.parametrize('changes', [
    {'name': 'internal_response_control'}, {'description': ''},
    {'name': 'create_ticket', 'source': 'mcp:evil'},
    {'input_schema': {'type': 'object', 'properties': {'x': {'type': 'bogus'}}}},
    {'input_schema': {'type': 'object', 'properties': {'x': {'$ref': 'https://evil/x'}}}},
    {'input_schema': {'type': 'object', 'properties': {'x': {'$dynamicRef': 'https://evil/x'}}}},
    {'input_schema': {'type': 'object', 'properties': {'confirmed': {'type': 'boolean'}}}},
])
def test_invalid_registration_is_rejected(changes):
    registration = make_registration('safe')
    with pytest.raises(ValueError):
        ToolCatalog().register(replace(registration, definition=replace(registration.definition, **changes)))


def test_duplicate_name_is_never_overwritten():
    catalog = ToolCatalog()
    item = make_registration('safe')
    catalog.register(item)
    with pytest.raises(ValueError):
        catalog.register(item)


def test_dangling_local_reference_is_rejected_before_publication():
    item = make_registration('broken')
    schema = {'type': 'object', 'properties': {'value': {'$ref': '#/$defs/missing'}}}
    with pytest.raises(ValueError):
        ToolCatalog().register(replace(item, definition=replace(item.definition, input_schema=schema)))


def test_valid_local_reference_stays_supported_and_invalid_runtime_schema_settles():
    from app.tools.validation import validate_arguments
    item = make_registration('reference')
    schema = {'type': 'object', '$defs': {'value': {'type': 'integer'}},
              'properties': {'value': {'$ref': '#/$defs/value'}}}
    valid = replace(item.definition, input_schema=schema)
    ToolCatalog().register(replace(item, definition=valid))
    assert validate_arguments(valid, {'value': 3}) == {'value': 3}
    malformed = replace(valid, input_schema={'type': 'object', '$ref': '#/$defs/gone'})
    assert validate_arguments(malformed, {}).content['error']['code'] == 'tool_execution_error'


def test_manifest_does_not_expand_and_detects_contract_change():
    catalog = ToolCatalog()
    first, second = make_registration('first'), make_registration('second')
    catalog.register(first)
    manifest = json.loads(json.dumps(catalog.snapshot(policy=allow_policy(first)).to_manifest()))
    catalog.register(second)
    restored = catalog.restore(manifest, policy=allow_policy(first, second), discovered=[])
    assert list(restored.definitions) == ['first']
    with pytest.raises(ValueError):
        catalog.restore(manifest, policy=allow_policy(second), discovered=[])


def test_policy_hot_reload_is_atomic_and_rejects_unknown_keys(tmp_path):
    path = tmp_path / 'policy.json'
    path.write_text(json.dumps({'tools': [{'source': 'builtin', 'name': 'safe', 'operation': 'read'}]}))
    store = PolicyStore(path)
    assert store.load().allows('builtin', 'safe')
    path.write_text('{"tools": [{"source":"builtin", "name":"safe", "operation":"read"}], "approved": true}')
    with pytest.raises(ValueError):
        store.load()
    path.write_text('{"tools": []}')
    assert not store.load().allows('builtin', 'safe')
