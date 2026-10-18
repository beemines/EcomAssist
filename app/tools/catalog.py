from dataclasses import replace
import re

from jsonschema.validators import validator_for
from jsonschema.exceptions import SchemaError
from app.tools.catalog_types import CatalogSnapshot, ToolDefinition, ToolRegistration, fingerprint
from app.tools.policies import PolicySnapshot

HIDDEN_PARAMETERS = {'conversation_id', 'user_message_id', 'user_id', 'tool_call_id',
    'confirmed', 'approved', 'confirmation', 'confirmation_id', 'grant'}


def validate_definition(definition: ToolDefinition) -> None:
    if not re.fullmatch(r'[A-Za-z0-9_-]{1,64}', definition.name) or definition.name == 'internal_response_control':
        raise ValueError('Invalid or reserved tool name.')
    if not definition.description.strip() or definition.operation not in ('read', 'write'):
        raise ValueError('Invalid tool definition.')
    schema = definition.input_schema
    if not isinstance(schema, dict) or schema.get('type') != 'object':
        raise ValueError('Tool parameters must be an object schema.')
    def check_refs(value):
        if isinstance(value, dict):
            if '$ref' in value and not str(value['$ref']).startswith('#/'):
                raise ValueError('Nonlocal schema references are forbidden.')
            for v in value.values():
                check_refs(v)
        elif isinstance(value, list):
            for v in value:
                check_refs(v)
    check_refs(schema)
    if HIDDEN_PARAMETERS.intersection(schema.get('properties', {})):
        raise ValueError('Hidden parameters may not be model arguments.')
    try:
        validator_for(schema).check_schema(schema)
    except SchemaError as exc:
        raise ValueError('Invalid tool parameter schema.') from exc


class ToolCatalog:
    def __init__(self):
        self._registrations = {}

    def register(self, registration: ToolRegistration) -> None:
        validate_definition(registration.definition)
        name = registration.definition.name
        if name in self._registrations:
            raise ValueError('Duplicate public tool name: ' + name)
        if registration.definition.source != 'builtin':
            raise ValueError('External tools must be dynamically discovered.')
        self._registrations[name] = registration

    def snapshot(self, *, policy: PolicySnapshot, discovered=()) -> CatalogSnapshot:
        effective = {}
        for registration in [*self._registrations.values(), *discovered]:
            definition = registration.definition
            rule = policy.rule(definition.source, definition.name)
            if rule is None:
                continue
            validate_definition(definition)
            updates = {k: v for k, v in rule.items() if k not in ('source', 'name')}
            for key in ('allowed_intents', 'output_fields'):
                if key in updates:
                    updates[key] = tuple(updates[key])
            if definition.operation == 'write' and rule['operation'] != 'write':
                raise ValueError('Policy cannot disguise a write handler as read.')
            definition = replace(definition, **updates)
            if definition.operation == 'write' and (definition.source != 'builtin' or definition.name != 'create_ticket'):
                raise ValueError('External writes are forbidden.')
            if definition.name in effective:
                raise ValueError('Conflicting public tool name: ' + definition.name)
            effective[definition.name] = replace(registration, definition=definition)
        return CatalogSnapshot(effective)

    def restore(self, manifest: dict, *, policy: PolicySnapshot, discovered=()) -> CatalogSnapshot:
        if not isinstance(manifest, dict) or set(manifest) != {'tools', 'version'} or fingerprint({'tools': manifest['tools']}) != manifest['version']:
            raise ValueError('Invalid persisted catalog manifest.')
        current = self.snapshot(policy=policy, discovered=discovered)
        selected = {}
        for raw in manifest['tools']:
            definition = ToolDefinition(**raw)
            registration = current._registrations.get(definition.name)
            if registration is None or registration.definition.fingerprint != definition.fingerprint:
                raise ValueError('Persisted tool contract changed or was revoked.')
            selected[definition.name] = registration
        return CatalogSnapshot(selected)
