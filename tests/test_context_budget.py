"""上下文口径与预算：独立字面算例保护扣项和旧配置兼容边界。"""
import json
from dataclasses import FrozenInstanceError
from pathlib import Path

import pytest
from langchain_core.messages import AIMessage, HumanMessage, SystemMessage, ToolMessage
from pydantic import ValidationError

from app.agent.controls import UsageLedger, record_usage, resolve_turn_token_limit
from app.config import Settings
from app.context.budget import derive_budget, derive_turn_token_limit
from app.context.tokens import ESTIMATOR_VERSION, estimate_payload
from app.context.types import PhaseOverheads


@pytest.fixture(autouse=True)
def isolate_context_environment(monkeypatch):
    for name in ('MODEL_CONTEXT_WINDOW', 'MAX_USER_INPUT_TOKENS', 'MAX_AGENT_STEPS',
                 'TOOL_RESULT_MAX_TOKENS', 'RERANK_TOP_K', 'CONTEXT_TARGET_ROUNDS',
                 'AGENT_MAX_TOOL_CALLS', 'AGENT_TOTAL_TOKEN_BUDGET', 'MAX_OUTPUT_TOKENS'):
        monkeypatch.delenv(name, raising=False)


def settings(**overrides):
    return Settings(_env_file=None, llm_base_url='https://example.test/',
                    llm_model='fake', llm_api_key='fake', **overrides)


def phases():
    # 1400 is already the FULL per-step request/result/argument/wrapper bound.
    return (PhaseOverheads('agent', 's', (), 2000, 100, 1400, True),
            PhaseOverheads('understanding', 's', (), 512, 20, 0, False))


def test_same_counter_covers_cjk_json_schema_and_call_ids():
    # Removing Chinese accounting, schemas, args or call IDs must fail this test.
    assert estimate_payload([]) == 0
    assert estimate_payload([HumanMessage('')]) == 10
    assert estimate_payload([HumanMessage('中文abc')]) == 14
    assert estimate_payload([HumanMessage('{"n":1}')]) == 13
    base = [HumanMessage('订单1001物流')]
    schema = [{'type': 'function', 'function': {'name': 'query_logistics',
        'parameters': {'type': 'object', 'properties': {'order_id': {'type': 'string', 'maxLength': 64}}}}}]
    assert estimate_payload(base, schema) > estimate_payload(base)
    request = AIMessage('', tool_calls=[{'id': 'a', 'name': 'query_logistics', 'args': {'order_id': '1001'}}])
    longer = request.model_copy(deep=True)
    longer.tool_calls[0]['args']['order_id'] = '订单' * 32
    assert estimate_payload([longer]) > estimate_payload([request]) > estimate_payload([AIMessage('')])
    assert estimate_payload([ToolMessage('{}', tool_call_id='a' * 64)]) > estimate_payload([ToolMessage('{}', tool_call_id='a')])
    # Provider usage, SQL identity and duplicate SDK raw mirrors are not prompt text.
    mirrored = request.model_copy(deep=True)
    mirrored.id = 'sql-id'
    mirrored.additional_kwargs['tool_calls'] = [{'ignored': 'mirror' * 100}]
    mirrored.usage_metadata = {'input_tokens': 100, 'output_tokens': 1, 'total_tokens': 101}
    assert estimate_payload([mirrored]) == estimate_payload([request])


def test_tool_arguments_match_actual_json_string_shape():
    # Pinned ChatOpenAI serializes arguments with JSON's default separator spaces.
    # Compacting parsed args only would silently disagree with equivalent raw wire JSON.
    parsed = AIMessage('', tool_calls=[{'id': 'a', 'name': 'query_order',
        'args': {'a': 1, 'b': 2, 'c': 3, 'd': 4}}])
    raw = AIMessage('', additional_kwargs={'tool_calls': [{'id': 'a', 'type': 'function',
        'function': {'name': 'query_order', 'arguments': '{"a": 1, "b": 2, "c": 3, "d": 4}'}}]})
    # AIMessage auto-parses raw tool_calls; retain only the actual raw representation.
    raw.tool_calls = []
    assert estimate_payload([parsed]) == estimate_payload([raw])


def test_phase_schema_is_counted_and_frozen_before_derivation():
    tools = [{'type': 'function', 'function': {'name': 'query_order', 'description': '订单查询' * 20}}]
    phase = PhaseOverheads('agent', 's', tools, 2000, 100, 1400, True)
    tools[0]['function']['description'] = ''
    budget = derive_budget(settings(), [phase], steady_turn_tokens=1000, minimum_turn_tokens=250)
    assert budget.phases['agent']['F'] > 100
    with pytest.raises(TypeError):
        phase.tools[0]['function']['description'] = ''


def test_budget_formula_has_no_unaccounted_attachment():
    config = settings(model_context_window=18000, max_output_tokens=2000, max_agent_steps=3, rerank_top_k=5)
    budget = derive_budget(config, phases(), steady_turn_tokens=1000, minimum_turn_tokens=250)
    # Hand computed: 18000-11-2010-2250-563-100-2000-540-4200=6326.
    assert dict(budget.phases['agent']) == {'F': 11, 'U': 2010, 'E': 2250, 'G': 563,
        'V': 100, 'O': 2000, 'M': 540, 'P': 4200, 'A': 6326}
    assert budget.phases['understanding']['A'] == 14344
    assert (budget.desired, budget.history, budget.layer1, budget.layer2) == (40000, 6326, 4428, 1898)
    assert budget.history == min(budget.desired, min(p['A'] for p in budget.phases.values()))
    assert budget.layer1 == budget.history * 70 // 100
    assert budget.layer1 + budget.layer2 == budget.history
    assert (budget.evidence, budget.summary, budget.safety) == (2250, 563, 540)
    assert budget.estimator_version == ESTIMATOR_VERSION
    # Per-call phase reservation includes H once and excludes unspent safety.
    # Agent=17460; understanding=6326+(18000-540-14344)=9442.
    assert derive_turn_token_limit(budget, call_limits={'agent': 4, 'understanding': 1}) == 79282


def test_default_window_has_literal_budget_and_twenty_steady_turns_fit():
    phase = PhaseOverheads('agent', 's', (), 512, 100, 1400, True)
    budget = derive_budget(settings(), [phase], steady_turn_tokens=1000, minimum_turn_tokens=250)
    assert dict(budget.phases['agent']) == {'F': 11, 'U': 2010, 'E': 6000, 'G': 2000,
        'V': 100, 'O': 512, 'M': 3840, 'P': 5600, 'A': 107927}
    assert (budget.history, budget.layer1, budget.layer2) == (40000, 28000, 12000)
    assert 20 * 1000 <= budget.layer1


def test_alias_conflict_and_explicit_total_limit(tmp_path, monkeypatch):
    with pytest.raises(ValidationError, match='MAX_AGENT_STEPS.*AGENT_MAX_TOOL_CALLS'):
        settings(MAX_AGENT_STEPS=3, AGENT_MAX_TOOL_CALLS=4)
    assert settings(MAX_AGENT_STEPS=3).agent_max_tool_calls == 3
    assert settings(AGENT_MAX_TOOL_CALLS=3).max_agent_steps == 3
    assert settings(MAX_AGENT_STEPS=3, AGENT_MAX_TOOL_CALLS=3).max_agent_steps == 3
    config = settings()
    budget = derive_budget(config, phases(), steady_turn_tokens=1000, minimum_turn_tokens=250)
    counts = {'agent': 5, 'understanding': 1}
    derived = derive_turn_token_limit(budget, call_limits=counts)
    assert derived > 32000
    assert config.agent_total_token_budget == 32000  # Existing consumers remain valid.
    assert not config.agent_total_token_budget_explicit
    assert resolve_turn_token_limit(config, budget, call_limits=counts) == derived
    explicit = settings(AGENT_TOTAL_TOKEN_BUDGET=32000)
    assert explicit.agent_total_token_budget_explicit
    assert resolve_turn_token_limit(explicit, budget, call_limits=counts) == 32000
    env = tmp_path / 'settings.env'
    env.write_text('MAX_AGENT_STEPS=3\nAGENT_MAX_TOOL_CALLS=4\n', encoding='utf-8')
    with pytest.raises(ValidationError):
        Settings(_env_file=env, llm_base_url='https://example.test/', llm_model='fake', llm_api_key='fake')
    monkeypatch.setenv('AGENT_TOTAL_TOKEN_BUDGET', '32000')
    assert settings().agent_total_token_budget_explicit


def test_no_full_turn_fails_without_paid_startup():
    with pytest.raises(ValueError, match='上下文预算不足.*agent'):
        derive_budget(settings(model_context_window=6000), phases(), steady_turn_tokens=1000, minimum_turn_tokens=250)
    # Positive history is still insufficient if a complete minimum turn cannot fit layer 1.
    with pytest.raises(ValueError, match='上下文预算不足.*完整'):
        derive_budget(settings(context_target_rounds=1), phases(), steady_turn_tokens=4000, minimum_turn_tokens=2801)


@pytest.mark.parametrize('field', ['model_context_window', 'max_user_input_tokens', 'max_agent_steps',
    'tool_result_max_tokens', 'rerank_top_k', 'context_target_rounds'])
@pytest.mark.parametrize('value', [True, False, 0, -1, 1.5, float('inf'), float('nan'), 'nan'])
def test_context_settings_reject_invalid_numbers(field, value):
    with pytest.raises(ValidationError):
        settings(**{field: value})


@pytest.mark.parametrize('overrides', [{'max_agent_steps': 5}, {'rerank_top_k': 11}])
def test_context_settings_reject_unsupported_steps_and_top_k(overrides):
    with pytest.raises(ValidationError):
        settings(**overrides)


def test_steady_turn_fixture_contains_complete_business_shapes():
    fixture = json.loads((Path(__file__).parent / 'fixtures/context/steady_turns.json').read_text(encoding='utf-8'))
    assert fixture['estimator_version'] == ESTIMATOR_VERSION
    assert fixture['calibration']['provider_usage'] is None
    costs = []
    for turn in fixture['turns']:
        rows = turn['messages']
        assert [r['role'] for r in rows] == ['user', 'assistant', 'tool', 'assistant']
        assert rows[1]['tool_calls'][0]['id'] == rows[2]['tool_call_id']
        messages = [HumanMessage(rows[0]['content']), AIMessage(rows[1]['content'], tool_calls=rows[1]['tool_calls']),
                    ToolMessage(rows[2]['content'], tool_call_id=rows[2]['tool_call_id']), AIMessage(rows[3]['content'])]
        costs.append(estimate_payload(messages))
    faq = next(t for t in fixture['turns'] if t['name'] == 'faq_top_10')
    assert len(json.loads(faq['messages'][2]['content'])['matches']) == 10
    assert min(costs) > 50
    budget = derive_budget(settings(), phases(), steady_turn_tokens=max(costs), minimum_turn_tokens=min(costs))
    assert budget.desired == 40 * max(costs)
    assert 20 * max(costs) <= budget.layer1


def test_derived_limit_is_capacity_not_usage_and_actual_usage_wins():
    config = settings()
    budget = derive_budget(config, phases(), steady_turn_tokens=1000, minimum_turn_tokens=250)
    ledger = UsageLedger(resolve_turn_token_limit(config, budget, call_limits={'agent': 5, 'understanding': 1}))
    assert ledger.spent == 0
    record_usage(AIMessage('', usage_metadata={'input_tokens': 10, 'output_tokens': 5, 'total_tokens': 15}),
                 ledger, estimated_input=9999, output_limit=2000)
    assert ledger.actual == ledger.spent == 15 and ledger.estimated == 0


def test_budget_is_immutable_and_rejects_incomplete_call_counts():
    budget = derive_budget(settings(), phases(), steady_turn_tokens=1000, minimum_turn_tokens=250)
    with pytest.raises(FrozenInstanceError):
        budget.history = 1
    with pytest.raises(TypeError):
        budget.phases['agent']['V'] = 0
    for limits in ({'agent': 1}, {'agent': True, 'understanding': 1}, {'agent': -1, 'understanding': 1},
                   {'agent': 0, 'understanding': 0}, {'agent': 1, 'understanding': 1, 'extra': 1}):
        with pytest.raises(ValueError):
            derive_turn_token_limit(budget, call_limits=limits)


@pytest.mark.parametrize('kwargs', [{'steady_turn_tokens': True}, {'steady_turn_tokens': 0},
    {'minimum_turn_tokens': -1}, {'minimum_turn_tokens': 1001}])
def test_budget_rejects_invalid_fixture_costs(kwargs):
    values = {'steady_turn_tokens': 1000, 'minimum_turn_tokens': 250, **kwargs}
    with pytest.raises(ValueError):
        derive_budget(settings(), phases(), **values)


def test_budget_requires_unique_complete_phases():
    for invalid in ([], [phases()[0], phases()[0]]):
        with pytest.raises(ValueError):
            derive_budget(settings(), invalid, steady_turn_tokens=1000, minimum_turn_tokens=250)


@pytest.mark.parametrize('field,value', [('output_tokens', True), ('output_tokens', 0),
    ('attachment_tokens', -1), ('tool_peak_tokens', float('inf')), ('uses_evidence', 1)])
def test_phase_overheads_reject_uncomputable_costs(field, value):
    values = {'name': 'agent', 'system': 's', 'tools': (), 'output_tokens': 512,
        'attachment_tokens': 100, 'tool_peak_tokens': 1400, 'uses_evidence': True, field: value}
    with pytest.raises(ValueError):
        PhaseOverheads(**values)
