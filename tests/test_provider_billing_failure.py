"""A permanent GLM billing rejection is distinct from a transient HTTP429."""
import json

import httpx
import pytest
from langchain_core.messages import AIMessage, HumanMessage
from langgraph.runtime import Runtime
from openai import RateLimitError

from app.core.errors import ServiceError
from app.core.llm import create_model
from app.workflow.agent import llm_call
from app.workflow.logging import safe_fields
from app.workflow.nodes import resolve_reference
from tests.fakes import decode_sse, fake_settings
from tests.test_order_resume_lifecycle import OwnerStore, app_context
from tests.test_workflow_agent import control
from tests.test_workflow_recovery import prepared, reply, understanding


def provider_error(code='1113', host='open.bigmodel.cn'):
    return RateLimitError('PRIVATE_PROVIDER_BODY', response=httpx.Response(429,
        request=httpx.Request('POST', f'https://{host}/api/paas/v4/chat/completions')),
        body={'code': code, 'message': 'PRIVATE_PROVIDER_BODY'})


@pytest.mark.parametrize('stage', ['understanding', 'decision'])
@pytest.mark.parametrize('code', ['1113', 1113])
async def test_glm_billing_rejection_never_claims_model_recovery(stage, code):
    failure = provider_error(code)
    context, state = prepared([failure, control()])
    model = understanding(context, [failure, reply({'query': '订单1001状态'})])
    with pytest.raises(ServiceError):
        await (resolve_reference(state, Runtime(context=context)) if stage == 'understanding'
               else llm_call(state, Runtime(context=context)))
    assert (model.intents if stage == 'understanding' else context.decision_model.decisions) == 1
    assert context.model_recovery_used is False
    assert context.repository.messages == []


@pytest.mark.parametrize('code,host', [
    ('1302', 'open.bigmodel.cn'), ('rate_limit_exceeded', 'open.bigmodel.cn'),
    ('1113', 'other-provider.invalid'), ('1113', 'open.bigmodel.cn.evil.invalid'),
])
async def test_other_429_failures_retain_the_existing_bounded_recovery(code, host):
    context, state = prepared()
    model = understanding(context, [provider_error(code, host), reply({'query': '订单1001状态'})])
    result = await resolve_reference(state, Runtime(context=context))
    assert result['resolved_question'] == '订单1001状态'
    assert model.intents == 2 and context.model_recovery_used is True


async def test_real_sdk_billing_response_reaches_public_sse_once_without_side_effects(tmp_path):
    requests = []
    def respond(request):
        requests.append(json.loads(request.content))
        return httpx.Response(429, json={'error': {'code': '1113', 'message': 'PRIVATE_PROVIDER_BODY'}})

    store = OwnerStore()
    await store.seed('1', [HumanMessage('物流信息异常'), AIMessage('请提供订单号。'),
                           HumanMessage('1001'), HumanMessage('1001')])
    config = fake_settings().model_copy(update={'llm_base_url': 'https://open.bigmodel.cn/api/paas/v4/'})
    async with httpx.AsyncClient(transport=httpx.MockTransport(respond)) as http_client:
        model = create_model(config, http_async_client=http_client)
        async with app_context(tmp_path, store=store, model=model) as (app, client):
            response = await client.post('/api/chat', json={'conversation_id': '1', 'message': '1001'})
            frames = decode_sse(response.text)
            assert frames[-1] == ('error', {'code': 'upstream_quota_exhausted',
                'message': '模型服务账户余额不足或无可用资源包，请联系管理员处理后再试。'})
            assert len(requests) == 1
            assert requests[0]['messages'][-1]['content'] == '1001'
            assert not {'done', 'actions', 'delta', 'ticket_confirmation'} & {name for name, _ in frames}
            assert not any(data.get('phase', '').startswith('tool_') for name, data in frames if name == 'status')
            assert app.state.chat_service._tasks == set()
    assert len(store.rows['1']) == 5 and store.commits == 0
    assert 'PRIVATE_PROVIDER_BODY' not in response.text and 'fake-test-key' not in response.text


def test_quota_error_survives_terminal_audit_projection():
    assert safe_fields({'code': 'upstream_quota_exhausted'}) == {'code': 'upstream_quota_exhausted'}


def test_quota_detection_ignores_provider_text_and_terminates_on_cycles():
    from app.core.provider_errors import is_bigmodel_quota_failure
    fake = RuntimeError('1113 余额不足')
    fake.status_code, fake.code = 429, '1113'
    fake.__cause__ = fake
    assert is_bigmodel_quota_failure(fake) is False
    nested = ServiceError('upstream_error', 'safe', 502)
    nested.__cause__ = ExceptionGroup('safe group', [provider_error()])
    assert is_bigmodel_quota_failure(nested) is True
