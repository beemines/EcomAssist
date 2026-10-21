import json
from types import SimpleNamespace
import pytest
from langchain_core.messages import HumanMessage, ToolMessage
from tests.workflow_fakes import workflow_runtime, workflow_call, apply_workflow_update
from tests.flywheel_confidence_fakes import payload, rule
from app.workflow.state import new_turn_state


def setup_gate(scores=(.9, .8)):
    from app.workflow.context_budget import runtime_snapshot, runtime_settings
    from app.quality.evidence_confidence import evidence_budget_fingerprint
    context = workflow_runtime(payload=payload(scores))
    context.settings = runtime_settings(context.settings).model_copy(update={'rerank_min_score': 100., 'rerank_top_k': 2})
    from app.retrieval.multi import WorkflowRetrieval
    class Retrieve:
        async def retrieve(self, **kwargs): return WorkflowRetrieval(payload(scores), {})
    context.workflow_retriever = Retrieve()
    state = new_turn_state(conversation_id='1', user_message_id=1, raw_question='商品如何保养？',
        category=None, messages=[HumanMessage('商品如何保养？', id='1')])
    state.update(intent='商品咨询', route='knowledge')
    budget = runtime_snapshot(state, context).budget.evidence
    context.confidence_rule = rule(budget_fingerprint=evidence_budget_fingerprint(top_k=2, token_budget=budget))
    events = []
    runtime = SimpleNamespace(context=context, stream_writer=events.append)
    return state, context, runtime


async def test_workflow_calibrated_gate_does_not_repeat_legacy_top1_threshold():
    from app.workflow.nodes import retrieve_knowledge, confidence_gate
    state, context, runtime = setup_gate()
    apply_workflow_update(state, await retrieve_knowledge(state, runtime))
    result = await confidence_gate(state, runtime)
    assert result['quality']['useful']
    assert len(context.sufficiency.calls) == 1
    assert result['retrieval_audit']['evidence_confidence']['rule_version'] == context.confidence_rule.rule_version


async def test_formal_low_gate_stops_before_content_model_and_has_audit():
    from app.workflow.nodes import retrieve_knowledge, confidence_gate
    state, context, runtime = setup_gate((.1,))
    apply_workflow_update(state, await retrieve_knowledge(state, runtime))
    result = await confidence_gate(state, runtime)
    assert not result['quality']['useful'] and result['quality']['source'] == 'retrieval_low_conf'
    assert not context.sufficiency.calls
    assert result['retrieval_audit']['evidence_confidence']['features']['has_top2'] is False


@pytest.mark.parametrize('code', ['upstream_error', 'tool_result_too_large'])
async def test_retrieval_engine_failure_is_not_a_knowledge_refusal(code):
    from app.core.errors import ServiceError
    from app.workflow.nodes import retrieve_knowledge
    state, context, runtime = setup_gate()
    # Exercise the forced BoundCatalog engine, including its normalized empty placeholder.
    from pathlib import Path
    from app.tools.registry import build_catalog
    from app.tools.policies import PolicyStore
    from app.tools.types import ToolContext
    from app.tools.executor import ToolExecutor
    from app.retrieval.multi import WorkflowRetrieval
    async def owner(cid): return 'demo-user'
    class Retrieve:
        async def retrieve(self, **kwargs):
            if code == 'upstream_error': raise ServiceError(code, '服务故障', 502)
            data = payload()
            data['matches'][0]['answer'] = '长' * 23000
            return WorkflowRetrieval(data, {})
    context.workflow_retriever = Retrieve()
    from app.orders.demo import DemoOrderProvider
    catalog = build_catalog(context.faq_repository, object(), owner_resolver=owner, order_provider=DemoOrderProvider())
    context.registry = catalog.snapshot(policy=PolicyStore(Path('config/tool-policy.json')).load()).bind(
        ToolContext('1', 1, state['raw_question']))
    context.executor = ToolExecutor()
    with pytest.raises(ServiceError):
        await retrieve_knowledge(state, runtime)
    assert not context.repository.refusals


@pytest.mark.parametrize('real_engine', [False, True])
async def test_agent_business_empty_is_refused_and_captured_not_service_failure(real_engine):
    from app.workflow.agent import tool_node
    from app.tools.types import ToolOutcome
    state, context, runtime = setup_gate(())
    state.update(route='business', intent='其他')
    context.settings = context.settings.model_copy(update={'flywheel_enabled': True})
    from langchain_core.tools import StructuredTool
    async def empty(keyword: str): return payload(())
    context.registry = {'query_faq': StructuredTool.from_function(coroutine=empty, name='query_faq', description='FAQ')}
    class Executor:
        async def execute(self, *args):
            return ToolOutcome(content={**payload(()), 'error': {'code': 'not_found', 'message': '无结果'}},
                status='error', attempts=1)
    context.executor = Executor()
    if real_engine:
        from pathlib import Path
        from app.tools.registry import build_catalog
        from app.tools.policies import PolicyStore
        from app.tools.executor import ToolExecutor
        from app.tools.types import ToolContext
        from app.orders.demo import DemoOrderProvider
        async def owner(cid): return 'demo-user'
        catalog = build_catalog(context.faq_repository, object(), order_provider=DemoOrderProvider(), owner_resolver=owner)
        context.registry = catalog.snapshot(policy=PolicyStore(Path('config/tool-policy.json')).load()).bind(
            ToolContext('1', 1, state['raw_question']))
        context.executor = ToolExecutor()
    state.update(selected=workflow_call('query_faq', {'keyword': '商品'}), selected_origin='agent')
    result = await tool_node(state, runtime)
    assert not result.get('tool_error')
    assert result['quality']['source'] == 'retrieval_low_conf'
    assert result['retrieval_performed'] is True
    assert result['retrieval_snapshot']['status'] == 'captured'


def test_fixture_rule_cannot_be_loaded_as_online_artifact(tmp_path):
    from app.quality.evidence_confidence import load_online_rule
    selected = rule()
    path = tmp_path / 'rule.json'
    path.write_text(selected.model_dump_json(), encoding='utf-8')
    with pytest.raises(ValueError, match='actual'):
        load_online_rule(path, top_k=2, budget_fingerprint=selected.source.budget_fingerprint,
            rerank_model=selected.source.rerank_model)
