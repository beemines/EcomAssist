"""Bounded recovery at real workflow nodes; only model/SQL boundaries are fake."""
import asyncio
import json
import time

import pytest
from langchain_core.messages import AIMessage
from langgraph.runtime import Runtime

from app.core.errors import ServiceError
from app.context.logging import ContextLogger
from app.workflow.agent import llm_call, tool_node
from app.workflow.nodes import resolve_reference, classify_intent
from app.workflow.understanding import QueryUnderstanding
from app.workflow.context_budget import runtime_snapshot
from tests.test_context_budget import settings
from tests.test_workflow_agent import setup, control, run
from tests.workflow_fakes import ScriptedWorkflowModel


def reply(body, finish='stop'):
    return AIMessage(json.dumps(body, ensure_ascii=False) if isinstance(body, dict) else body,
        response_metadata={'finish_reason': finish},
        usage_metadata={'input_tokens': 10, 'output_tokens': 5, 'total_tokens': 15})


def prepared(replies=()):
    context, state = setup(list(replies), question='订单1001状态')
    context.settings = settings()
    context.context_snapshot = runtime_snapshot(state, context)
    return context, state


def understanding(context, replies):
    model = ScriptedWorkflowModel(intent_replies=replies)
    context.understanding = QueryUnderstanding(model, input_budget=128000, timeout_seconds=1)
    return model


async def test_understanding_recovery_accumulates_and_shares_allowance(tmp_path):
    context, state = prepared()
    model = understanding(context, [reply('PRIVATE_BAD'), reply({'query': '订单1001状态'})])
    context.intent_model = ScriptedWorkflowModel(intent_replies=[reply('invalid'), reply({'intent':'订单','confidence':.9})])
    observations, events = [], []
    context.usage_observer = observations.append
    path = tmp_path/'context.jsonl'
    context.context_logger = ContextLogger(path)
    runtime = Runtime(context=context, stream_writer=events.append)
    try:
        update = await resolve_reference(state, runtime)
        assert update['resolved_question'] == '订单1001状态'
        assert update['usage'] == {'actual':30,'estimated':0,'actual_calls':2,'estimated_calls':0}
        assert update['stage_usage']['understanding']['actual'] == 30
        assert observations[-1]['usage'] == update['usage']
        with pytest.raises(ServiceError):
            await classify_intent({**state, **update}, runtime)
    finally:
        context.context_logger.close()
    assert model.intents == 2 and context.intent_model.intents == 1
    assert model.intent_inputs[0] == model.intent_inputs[1]
    records = [json.loads(line) for line in path.read_text(encoding='utf-8').splitlines()]
    assert [r['call_index'] for r in records if r['event']=='model_ctx' and r['phase']=='understanding'] == [1,2]
    recovery, = [r for r in records if r['event']=='model_recovery']
    assert recovery['stage']=='understanding' and recovery['attempt']==1
    assert recovery['usage']['actual']==15 and 'PRIVATE_BAD' not in json.dumps(recovery)
    assert context.repository.messages == []


async def test_classification_recovers_at_node_only():
    context, state = prepared()
    model = ScriptedWorkflowModel(intent_replies=[reply('invalid'), reply({'intent':'订单','confidence':.9})])
    context.intent_model = model
    update = await classify_intent(state, Runtime(context=context))
    assert update['intent']=='订单' and update['route']=='business'
    assert update['usage']['actual']==30 and model.intents==2
    assert model.intent_inputs[0]==model.intent_inputs[1]


@pytest.mark.parametrize('failure', [TimeoutError(), reply('bad control')])
async def test_agent_recovery_charges_decisions_before_current_read(failure):
    context, state = prepared([failure, reply(json.loads(control().text))])
    observations=[]
    context.usage_observer=observations.append
    result = await llm_call(state, Runtime(context=context))
    assert result['decision_count']==2 and state['decision_count']==0
    assert result['usage']['actual_calls']+result['usage']['estimated_calls']==2
    assert result['usage']['actual'] == (15 if isinstance(failure, BaseException) else 30)
    assert observations[-1]['usage']==result['usage']
    assert context.decision_model.tool_inputs[0]==context.decision_model.tool_inputs[1]
    assert context.repository.messages==[]
    update=await tool_node({**state, **result},Runtime(context=context))
    assert update['tool_call_count']==1
    assert [m.type for m in context.repository.messages]==['ai','tool']


async def test_aux_and_agent_share_single_extra_generation():
    context, state=prepared([reply('bad'), control()])
    model=understanding(context,[reply('bad'),reply({'query':'订单1001状态'})])
    update=await resolve_reference(state,Runtime(context=context))
    with pytest.raises(ServiceError):
        await llm_call({**state,**update},Runtime(context=context))
    assert model.intents==2 and context.decision_model.decisions==1


@pytest.mark.parametrize('stage', ['understanding','decision'])
async def test_double_invalid_is_terminal_at_two_attempts(stage):
    context,state=prepared([reply('bad'),reply('still bad'),control()])
    model=understanding(context,[reply('bad'),reply('still bad'),reply({'query':'订单1001状态'})])
    observed=[]
    context.usage_observer=observed.append
    with pytest.raises(ServiceError):
        await (resolve_reference(state,Runtime(context=context)) if stage=='understanding'
               else llm_call(state,Runtime(context=context)))
    assert (model.intents if stage=='understanding' else context.decision_model.decisions)==2
    assert observed[-1]['usage']['actual']==30


@pytest.mark.parametrize('stage', ['understanding','decision'])
@pytest.mark.parametrize('finish', ['length','content_filter'])
async def test_nonrecoverable_finish_never_retries(stage,finish):
    context,state=prepared([reply('bad',finish),control()])
    model=understanding(context,[reply('bad',finish),reply({'query':'订单1001状态'})])
    with pytest.raises(ServiceError):
        await (resolve_reference(state,Runtime(context=context)) if stage=='understanding'
               else llm_call(state,Runtime(context=context)))
    assert (model.intents if stage=='understanding' else context.decision_model.decisions)==1


@pytest.mark.parametrize('stage',['understanding','decision'])
async def test_second_attempt_cancellation_preserves_both_costs(stage):
    context,state=prepared([reply('bad'),asyncio.CancelledError()])
    model=understanding(context,[reply('bad'),asyncio.CancelledError()])
    observations=[]
    context.usage_observer=observations.append
    with pytest.raises(asyncio.CancelledError):
        await (resolve_reference(state,Runtime(context=context)) if stage=='understanding'
               else llm_call(state,Runtime(context=context)))
    assert (model.intents if stage=='understanding' else context.decision_model.decisions)==2
    usage=observations[-1]['usage']
    assert usage['actual']==15 and usage['actual_calls']==1 and usage['estimated_calls']==1


async def test_exhausted_decision_steps_never_start_recovery():
    context,state=prepared([reply('bad'),control()])
    state['decision_count']=4
    with pytest.raises(ServiceError):
        await llm_call(state,Runtime(context=context))
    assert context.decision_model.decisions==1


async def test_understanding_direct_service_keeps_one_attempt():
    context,_=prepared()
    model=understanding(context,[reply('bad'),reply({'query':'订单1001状态'})])
    with pytest.raises(ServiceError):
        await context.understanding.resolve('订单1001状态',[])
    assert model.intents==1


@pytest.mark.parametrize('kind',['raw','schema','entity'])
async def test_understanding_private_rejection_evidence_is_bounded(kind,tmp_path):
    context,state=prepared()
    body={'raw':reply('bad',finish='tool_calls'),
          'schema':reply('PRIVATE_SCHEMA'+'X'*9000),
          'entity':reply({'query':'订单9999状态'})}[kind]
    body.additional_kwargs['reasoning_content']='SECRET_REASONING'
    body.response_metadata['headers']={'authorization':'SECRET_HEADER'}
    understanding(context,[body])
    path=tmp_path/'content.jsonl'
    logger=ContextLogger(path)
    try:
        with pytest.raises(ServiceError):
            await context.understanding.resolve('订单1001状态',[],snapshot=context.context_snapshot,context_logger=logger)
    finally:
        logger.close()
    records=[json.loads(line) for line in path.read_text(encoding='utf-8').splitlines()]
    row,=[r for r in records if r['event']=='understanding_control_rejected']
    assert row['rejection']==kind and len(row['control_text'])<=8192
    assert 'SECRET_REASONING' not in json.dumps(row) and 'SECRET_HEADER' not in json.dumps(row)


async def test_expired_turn_never_calls_model():
    context,state=prepared([control()])
    model=understanding(context,[reply({'query':'订单1001状态'})])
    context.deadline=time.monotonic()-1
    with pytest.raises(ServiceError):
        await resolve_reference(state,Runtime(context=context))
    assert model.intents==0
    with pytest.raises((ServiceError, TimeoutError)):
        await llm_call(state,Runtime(context=context))
    assert context.decision_model.decisions==0


@pytest.mark.parametrize('stage',['understanding','decision'])
@pytest.mark.parametrize('status',[400,401,403,404,422])
async def test_permanent_provider_http_error_never_retries(stage,status):
    import httpx
    from openai import APIStatusError
    failure=APIStatusError('PRIVATE_PROVIDER_BODY', response=httpx.Response(status,
        request=httpx.Request('POST','https://offline.invalid/v1/chat/completions')), body=None)
    context,state=prepared([failure,control()])
    model=understanding(context,[failure,reply({'query':'订单1001状态'})])
    with pytest.raises(ServiceError):
        await (resolve_reference(state,Runtime(context=context)) if stage=='understanding'
               else llm_call(state,Runtime(context=context)))
    assert (model.intents if stage=='understanding' else context.decision_model.decisions)==1


async def test_recovery_allowance_survives_durable_order_pause_and_resume(tmp_path):
    from tests.test_order_resume_lifecycle import app_context, pause, selection
    from tests.fakes import decode_sse
    from app.workflow.persistence import checkpoint_config
    from app.schemas.order_actions import OrderSelectionRequest
    model=ScriptedWorkflowModel(intent_replies=[reply('bad'),reply({'query':'这个能退吗？'}),
        reply({'intent':'退款退货','confidence':.95}),reply('bad expansion'),
        reply({'queries':['这个能退吗？','MH-LP200退货政策']})])
    async with app_context(tmp_path,model=model) as (app,client):
        card,_=await pause(client)
        service=app.state.chat_service
        root=await service.graph.aget_state(checkpoint_config('1'))
        assert root.values.get('model_recovery_used') is True
        prepared=await service.prepare_resume('1',OrderSelectionRequest(**selection(card)))
        try:
            assert prepared.runtime.model_recovery_used is True
        finally:
            service.release(prepared)
        response=await client.post('/api/conversations/1/actions/select-order',json=selection(card))
        assert decode_sse(response.text)[-1][0]=='error'
        assert model.intents==4, 'resume must not acquire another extra generation'
        fresh=await service.prepare('1','你好')
        try:
            assert fresh.runtime.model_recovery_used is False
            assert fresh.state['model_recovery_used'] is False
        finally:
            service.release(fresh)


@pytest.mark.parametrize('stage',['understanding','decision'])
async def test_consumed_budget_cannot_fit_recovery(stage):
    expensive=reply('bad')
    expensive.usage_metadata={'input_tokens':100000000,'output_tokens':5,'total_tokens':100000005}
    context,state=prepared([expensive,control()])
    model=understanding(context,[expensive,reply({'query':'订单1001状态'})])
    with pytest.raises(ServiceError):
        await (resolve_reference(state,Runtime(context=context)) if stage=='understanding'
               else llm_call(state,Runtime(context=context)))
    assert (model.intents if stage=='understanding' else context.decision_model.decisions)==1


@pytest.mark.parametrize('stage',['understanding','decision'])
async def test_deadline_expiring_on_first_rejection_blocks_recovery(stage):
    context,state=prepared([reply('bad'),control()])
    model=understanding(context,[reply('bad'),reply({'query':'订单1001状态'})])
    seam=context.understanding.model if stage=='understanding' else context.decision_model
    invoke=seam.ainvoke
    async def expire(messages,**kwargs):
        result=await invoke(messages,**kwargs)
        context.deadline=time.monotonic()-1
        return result
    seam.ainvoke=expire
    with pytest.raises((ServiceError,TimeoutError)):
        await (resolve_reference(state,Runtime(context=context)) if stage=='understanding'
               else llm_call(state,Runtime(context=context)))
    assert (model.intents if stage=='understanding' else context.decision_model.decisions)==1


async def test_outer_stage_timeout_recovers_without_swallowing_cancel():
    context,state=prepared()
    context.settings=settings(llm_timeout_seconds=.01)
    model=understanding(context,[reply({'query':'订单1001状态'})])
    invoke=context.understanding.model.ainvoke
    calls=0
    async def timeout_first(messages,**kwargs):
        nonlocal calls
        calls+=1
        if calls==1:
            await asyncio.Event().wait()
        return await invoke(messages,**kwargs)
    context.understanding.model.ainvoke=timeout_first
    result=await resolve_reference(state,Runtime(context=context))
    assert calls==2 and result['resolved_question']=='订单1001状态'
    assert result['usage']['estimated_calls']==1 and result['usage']['actual_calls']==1


def test_audit_keeps_decision_costs_but_drops_unknown_payloads():
    from app.workflow.logging import safe_fields
    projected=safe_fields({'stage_usage':{'decision':{'actual':30,'estimated':0,'actual_calls':2,
        'estimated_calls':0,'elapsed_seconds':.5,'response':'PRIVATE_BODY'}},'response':'PRIVATE_BODY'})
    assert projected=={'stage_usage':{'decision':{'actual':30,'estimated':0,'actual_calls':2,
        'estimated_calls':0,'elapsed_seconds':.5}}}


async def test_expansion_recovery_uses_same_packet_and_distinct_call_index(tmp_path):
    from app.orders.demo import DemoOrderProvider
    from app.workflow.expansion import QueryExpander
    from app.workflow.nodes import expand_queries
    context,state=prepared()
    order=await DemoOrderProvider().get_order(user_id='demo-user',order_id='1001')
    state['order_snapshot']=order.model_dump(mode='json')
    model=ScriptedWorkflowModel(intent_replies=[reply('bad'),reply({'queries':['订单1001状态','订单1001退货政策']})])
    context.expander=QueryExpander(model,input_budget=128000,timeout_seconds=1)
    path=tmp_path/'content.jsonl'
    logger=ContextLogger(path)
    context.context_logger=logger
    try:
        result=await expand_queries(state,Runtime(context=context))
    finally:
        logger.close()
    assert model.intents==2 and result['usage']['actual']==30
    assert result['retrieval_queries']==['订单1001状态','订单1001退货政策']
    assert model.intent_inputs[0]==model.intent_inputs[1]
    records=[json.loads(line) for line in path.read_text(encoding='utf-8').splitlines()]
    assert [r['call_index'] for r in records if r['event']=='model_ctx']==[1,2]


async def test_agent_real_per_call_timeout_is_recoverable_with_turn_time_left():
    context,state=prepared([reply(json.loads(control().text))])
    context.settings=settings(llm_timeout_seconds=.01)
    invoke=context.decision_model.ainvoke
    calls=0
    async def timeout_first(messages,**kwargs):
        nonlocal calls
        calls+=1
        if calls==1:
            await asyncio.Event().wait()
        return await invoke(messages,**kwargs)
    context.decision_model.ainvoke=timeout_first
    result=await llm_call(state,Runtime(context=context))
    assert calls==2 and result['decision_count']==2
    assert result['usage']['estimated_calls']==1 and result['usage']['actual_calls']==1
