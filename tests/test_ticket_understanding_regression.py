"""Captured wrong-stage outputs remain rejected; prompt quality needs live evaluation."""
import json
from pathlib import Path

import pytest
from langchain_core.messages import AIMessage, HumanMessage

from app.core.errors import ServiceError
from app.workflow.understanding import QueryUnderstanding
from tests.workflow_fakes import ScriptedWorkflowModel

FIXTURE = json.loads((Path(__file__).parent / 'fixtures/context/ticket_understanding_regression.json').read_text(encoding='utf-8'))


def reply(value):
    return AIMessage(json.dumps(value, ensure_ascii=False), response_metadata={'finish_reason': 'stop'})


@pytest.mark.parametrize('value', FIXTURE['captured_invalid_outputs'])
async def test_captured_ticket_arguments_are_not_repaired_into_query_output(value):
    model = ScriptedWorkflowModel(intent_replies=[reply(value)])
    service = QueryUnderstanding(model, input_budget=20000, timeout_seconds=1)
    with pytest.raises(ServiceError) as caught:
        await service.resolve(FIXTURE['question'], [HumanMessage(FIXTURE['history_question']), AIMessage('已查询模拟物流。')])
    assert caught.value.code == 'invalid_structured_output' and model.intents == 1


@pytest.mark.parametrize('query', FIXTURE['labelled_valid_queries'])
async def test_labelled_explicit_ticket_request_passes_through_unchanged(query):
    model = ScriptedWorkflowModel(intent_replies=[reply({'query': query})])
    service = QueryUnderstanding(model, input_budget=20000, timeout_seconds=1)
    result = await service.resolve(query, [HumanMessage(FIXTURE['history_question']), AIMessage('已查询模拟物流。')])
    assert result.query == query and not result.changed and model.intents == 1
