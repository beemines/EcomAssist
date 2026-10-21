import json
from collections import deque
import pytest
from langchain_core.messages import AIMessage
from app.core.errors import ServiceError
from app.flywheel.types import NormalizedDraft, ReviewCandidate


class JsonModel:
    """Only the external model is scripted; use the real strict response parser."""
    def __init__(self, replies):
        self.replies, self.calls = deque(replies), []

    def with_structured_output(self, schema, **kwargs):
        owner = self
        class Bound:
            def with_config(self, **config):
                return self
            async def ainvoke(self, messages):
                owner.calls.append(messages)
                raw = owner.replies.popleft()
                try:
                    parsed, error = schema.model_validate_json(raw.text), None
                except ValueError as exc:
                    parsed, error = None, exc
                return {'raw': raw, 'parsed': parsed, 'parsing_error': error}
        return Bound()


def raw(value, finish='stop'):
    return AIMessage(json.dumps(value, ensure_ascii=False), response_metadata={'finish_reason': finish})


def question():
    return {'raw_question': '运费怎么算', 'retrieved_chunks': None, 'snapshot_status': 'not_retrieved'}


async def test_prompt_client_accepts_only_raw_complete_strict_json():
    from app.flywheel.processing import PromptClient
    model = JsonModel([raw({'normalized_question': '运费如何计算？', 'ai_suggested_answer': '待人工补充政策。'})])
    result = await PromptClient(model).normalize(question())
    assert result.normalized_question == '运费如何计算？' and len(model.calls) == 1


@pytest.mark.parametrize('value,finish', [
    ({'normalized_question': '运费', 'ai_suggested_answer': '待审核', 'status': '通过'}, 'stop'),
    ({'normalized_question': '运费', 'ai_suggested_answer': '待审核'}, 'length'),
    ({'normalized_question': ' ', 'ai_suggested_answer': '待审核'}, 'stop'),
])
async def test_normalization_never_repairs_or_trusts_extra_control_fields(value, finish):
    from app.flywheel.processing import PromptClient
    model = JsonModel([raw(value, finish)])
    with pytest.raises(ServiceError, match='结构化'):
        await PromptClient(model).normalize(question())
    assert len(model.calls) == 1


@pytest.mark.parametrize('value', [
    {'matched_review_id': False}, {'matched_review_id': 'false'},
    {'matched_review_id': None, 'confidence': 1}, {'matched_review_id': '9999'},
])
async def test_dedup_cannot_return_bool_extra_fields_or_out_of_batch_id(value):
    from app.flywheel.processing import PromptClient
    model = JsonModel([raw(value)])
    with pytest.raises(ServiceError):
        await PromptClient(model).deduplicate(NormalizedDraft(normalized_question='运费如何计算',
            ai_suggested_answer='待核准'), [ReviewCandidate(id='1', normalized_question='运费规则')])
    assert len(model.calls) == 1


async def test_oversized_original_question_never_reaches_model():
    from app.flywheel.processing import PromptClient
    model = JsonModel([])
    with pytest.raises(ValueError, match='budget'):
        await PromptClient(model).normalize({**question(), 'raw_question': '中' * 20000})
    assert model.calls == []


def test_labeled_material_has_twelve_groups_and_explicit_case_fact_boundaries():
    from evals.evaluate_flywheel import load_cases
    cases = load_cases('evals/flywheel_cases.jsonl')
    assert len(cases) == 12 and len({case['id'] for case in cases}) == 12
    realtime = next(case for case in cases if case['id'] == 'F05')
    assert '1001' in realtime['raw_question']
    assert '1001' not in realtime['example_normalized_question']
    assert next(case for case in cases if case['id'] == 'F06')['long_input_variant']['expected'] == 'input_budget_rejected_without_model'
