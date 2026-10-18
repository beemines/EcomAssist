from dataclasses import replace
from app.tools.catalog import ToolCatalog
from app.tools.types import ToolContext
from app.workflow.controls import stable_tool_schema
from app.workflow.intent import has_explicit_ticket_request
from tests.tool_system_fakes import make_registration, allow_policy
from tests.test_context_budget import settings
from app.workflow.context_budget import workflow_budget
import pytest


def test_dynamic_schema_counts_actual_definition_and_preserves_control_protocol():
    small = make_registration('new_read')
    large = replace(small, definition=replace(small.definition, description='查询业务信息。'*300))
    def bound(item):
        catalog = ToolCatalog()
        catalog.register(item)
        return catalog.snapshot(policy=allow_policy(item)).bind(ToolContext('1', 2, 'hi'))
    schema = stable_tool_schema(bound(large))
    assert [t['function']['name'] for t in schema] == ['new_read', 'internal_response_control']
    assert workflow_budget(settings(model_context_window=36000), bound(large)).history < workflow_budget(settings(model_context_window=36000), bound(small)).history


@pytest.mark.parametrize('question,expected', [
    ('帮我建个工单', True), ('我要投诉，请帮我提交售后工单', True),
    ('不要给我建工单', False), ('怎么建工单', False), ('只转人工，别建单', False),
    ('我要投诉', False), ('我不建工单，只查物流', False),
    ('我没有要求创建工单', False), ('可以帮我建个工单吗', True),
])
def test_ticket_authority_requires_explicit_positive_customer_request(question, expected):
    assert has_explicit_ticket_request(question) is expected


async def test_prepare_acquires_once_and_reuses_schema_before_and_after_sql(tmp_path):
    from types import SimpleNamespace
    from tests.test_workflow_api import workflow_app
    first, second = make_registration('first'), make_registration('second')
    catalog = ToolCatalog()
    catalog.register(first)
    local = allow_policy(first, second)
    class Provider:
        policies = SimpleNamespace(load=lambda: local)
        calls = 0
        async def acquire(self):
            self.calls += 1
            snapshot = catalog.snapshot(policy=local)
            catalog.register(second)
            return snapshot
    async with workflow_app(tmp_path) as app:
        service = app.state.chat_service
        service.catalog_provider = provider = Provider()
        prepared = await service.prepare('1', '你好')
        try:
            assert provider.calls == 1
            assert set(prepared.runtime.registry) == {'first'}
            assert [tool['name'] for tool in prepared.state['tool_manifest']['tools']] == ['first']
        finally:
            service.release(prepared)
