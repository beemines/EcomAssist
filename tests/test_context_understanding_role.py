"""Saved provider negative + annotated contrasts, not a model-quality claim.

The HTTP transport replays labelled outputs to verify unchanged strictness and
lossless history through the actual SDK. Only live evaluation can judge a prompt.
"""
import hashlib
import json
from pathlib import Path

import httpx
import pytest
from langchain_openai import ChatOpenAI
from langchain_openai.chat_models.base import _convert_dict_to_message, _convert_message_to_dict

from app.context.layers import plan_layers
from app.context.types import ContextAnchors
from app.context.view import build_snapshot
from app.core.errors import ServiceError
from app.repositories.records import record_from_message
from app.workflow.context_budget import workflow_budget
from app.workflow.entities import snapshot_provenance
from app.workflow.understanding import QueryUnderstanding
from tests.test_context_agent import production_registry
from tests.test_context_budget import settings

FIXTURE = json.loads((Path(__file__).parent / 'fixtures/context/understanding_role_regression.json').read_text(encoding='utf-8-sig'))
CASES = [{'id': 'actual-negative', 'history': 'actual', 'question': FIXTURE['expected_query'],
          'response': FIXTURE['observed_response'], 'reject': True},
         {'id': 'annotated-repair', 'history': 'actual', 'question': FIXTURE['expected_query'],
          'query': FIXTURE['expected_query']}, *FIXTURE['contrasts']]


@pytest.mark.parametrize('case', CASES, ids=lambda case: case['id'])
async def test_role_regression_keeps_raw_history_and_strict_query_contract(case):
    original = FIXTURE['request']['messages']
    assert hashlib.sha256(original[0]['content'].encode()).hexdigest() == FIXTURE['original_system_sha256']
    history = original[1:-2] if case['history'] == 'actual' else []
    rows = [record_from_message(_convert_dict_to_message(message), identifier=index)
            for index, message in enumerate(history, 1)]
    budget = workflow_budget(settings(), production_registry())
    plan = plan_layers(rows, ContextAnchors(None, None), budget, current_user_id=100)
    snapshot = build_snapshot(plan, (), conversation_id='1', user_message_id='100', budget=budget)
    provenance = snapshot_provenance(snapshot, rows)
    requests = []
    def respond(request):
        requests.append(json.loads(request.content))
        body = case.get('response') or json.dumps({'query': case['query']}, ensure_ascii=False)
        return httpx.Response(200, json={'id': 'offline', 'object': 'chat.completion', 'created': 0,
            'model': 'offline', 'choices': [{'index': 0, 'finish_reason': 'stop',
                'message': {'role': 'assistant', 'content': body}}],
            'usage': {'prompt_tokens': 2505, 'completion_tokens': 43, 'total_tokens': 2548}})
    async with httpx.AsyncClient(transport=httpx.MockTransport(respond)) as client:
        model = ChatOpenAI(model='offline', api_key='offline', base_url='https://offline.invalid/v1',
            http_async_client=client, max_retries=0, use_responses_api=False)
        service = QueryUnderstanding(model, input_budget=128000, timeout_seconds=5)
        try:
            if case.get('reject'):
                with pytest.raises(ServiceError) as error:
                    await service.resolve(case['question'], [], snapshot=snapshot, provenance=provenance)
                assert error.value.code == 'invalid_structured_output'
            else:
                result = await service.resolve(case['question'], [], snapshot=snapshot, provenance=provenance)
                assert result.query == case['query']
        finally:
            model.root_client.close()
            await model.root_async_client.close()
    assert len(requests) == 1, 'invalid protocol must not cause a hidden retry'
    assert requests[0]['response_format'] == {'type': 'json_object'}
    assert not requests[0].get('tools')
    # SDK normalizes content=None on native requests, so compare the same wire boundary.
    assert requests[0]['messages'][1:-2] == [_convert_message_to_dict(_convert_dict_to_message(row)) for row in history]
    assert requests[0]['messages'][-2]['content'] == case['question']
    assert service.usage['actual'] == 2548
