"""One stable decision protocol; business permissions are enforced separately."""
from collections.abc import Mapping
from typing import Literal

from langchain_core.messages import AIMessage
from langchain_core.tools import BaseTool
from langchain_core.utils.function_calling import convert_to_openai_tool
from pydantic import BaseModel, ConfigDict, Field, ValidationError, field_validator

from app.core.extraction import invalid_output, validate_structured_output

INTERNAL_RESPONSE_CONTROL = 'internal_response_control'
READ_TOOLS = ('query_order', 'query_logistics', 'query_product', 'query_faq')


class UnifiedAgentControl(BaseModel):
    model_config = ConfigDict(extra='forbid', strict=True)
    reply_mode: Literal['answer', 'clarification']
    suggested_actions: list[Literal['handoff', 'create_ticket']] = Field(max_length=2)
    refund_decision: Literal['eligible', 'needs_review', 'ineligible', 'not_applicable'] | None
    decision_reason: str | None = Field(min_length=1, max_length=256)

    @field_validator('suggested_actions')
    @classmethod
    def unique_actions(cls, value):
        return list(dict.fromkeys(value))

    @field_validator('decision_reason')
    @classmethod
    def nonblank_reason(cls, value):
        if value is not None and not value.strip():
            raise ValueError('decision reason must be nonblank')
        return value


def validate_control(control: UnifiedAgentControl, *, route: str, intent: str) -> UnifiedAgentControl:
    if route != 'after_sales':
        if control.refund_decision is not None or control.decision_reason is not None:
            raise invalid_output()
    elif (control.refund_decision is None or control.decision_reason is None
            or intent == '售后' and control.refund_decision != 'not_applicable'
            or intent == '退款退货' and control.refund_decision == 'not_applicable'
            or control.reply_mode == 'clarification' and control.refund_decision in ('eligible', 'needs_review')):
        raise invalid_output()
    return control


def parse_control(reply: AIMessage, *, route: str, intent: str) -> UnifiedAgentControl:
    if (not isinstance(reply, AIMessage) or reply.response_metadata.get('finish_reason') != 'stop'
            or reply.tool_calls or reply.invalid_tool_calls or reply.additional_kwargs.get('tool_calls')):
        raise invalid_output()
    try:
        parsed = UnifiedAgentControl.model_validate_json(reply.text)
    except ValidationError as exc:
        raise invalid_output() from exc
    parsed = validate_structured_output({'raw': reply, 'parsed': parsed, 'parsing_error': None}, UnifiedAgentControl)
    return validate_control(parsed, route=route, intent=intent)


def stable_read_schema(registry: Mapping[str, BaseTool]) -> list[dict]:
    if INTERNAL_RESPONSE_CONTROL in registry:
        raise ValueError('Internal response control conflicts with business registry')
    control = convert_to_openai_tool(UnifiedAgentControl)
    control['function'].update(name=INTERNAL_RESPONSE_CONTROL,
        description='内部响应控制：证据已足够或需要澄清时选择，只设置最终回复模式与建议，不执行业务动作。')
    return [convert_to_openai_tool(registry[name]) for name in READ_TOOLS if name in registry] + [control]


def stable_tool_schema(catalog, *, intent=None, ticket_requested=False):
    from app.tools.catalog_types import BoundCatalog
    if not isinstance(catalog, BoundCatalog):
        return stable_read_schema(catalog)
    control = stable_read_schema({})[-1]
    schemas = []
    for name in sorted(catalog):
        definition = catalog.definition(name)
        if definition.allowed_intents and intent is not None and intent not in definition.allowed_intents:
            continue
        if definition.operation == 'write' and not ticket_requested:
            continue
        schemas.append({'type': 'function', 'function': {'name': name,
            'description': definition.description, 'parameters': definition.input_schema}})
    return [*schemas, control]
