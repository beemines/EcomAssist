"""Factory activation, actual packet budgets and provider calibration remain observable."""
import importlib
import pytest
from langchain_core.messages import HumanMessage
from app.context.tokens import estimate_payload


def factory():
    try:
        return importlib.import_module('app.workflow.context_budget')
    except ImportError:
        pytest.fail('Actual workflow context budget factory missing')


def production_registry():
    """Construct production schemas with SQL owner binding; never execute a read."""
    from app.orders.demo import DemoOrderProvider
    from app.repositories.conversations import ConversationRepository
    from app.repositories.faq import FAQRepository
    from app.repositories.tickets import TicketRepository
    from app.tools.registry import build_registry
    from app.tools.types import ToolContext
    return build_registry(FAQRepository(None, None, None), TicketRepository(None),
        ToolContext('1', 1, ''), order_provider=DemoOrderProvider(),
        owner_resolver=ConversationRepository(None).get_user_id)


def test_effective_name_fallback_is_charged_even_empty_primary():
    for name in (None, ''):
        assert estimate_payload([HumanMessage('x', name=name, additional_kwargs={'name':'fallback'})]) == \
               estimate_payload([HumanMessage('x', name='fallback')])


def test_actual_default_and_demo_budgets_keep_output_and_peak_separate():
    from app.config import Settings
    for options, window, output, steps in [({},128000,512,4),
            (dict(model_context_window=18000,max_output_tokens=2000,max_agent_steps=3,rerank_top_k=5),18000,2000,3)]:
        settings = Settings(_env_file=None, llm_base_url='https://offline.invalid', llm_model='offline',
                            llm_api_key='offline', **options)
        budget = factory().workflow_budget(settings, production_registry())
        assert budget.window == window and budget.phases['final']['O'] == output
        assert budget.phases['decision']['P'] >= steps * settings.tool_result_max_tokens
        assert budget.history > 0 and budget.layer1 + budget.layer2 == budget.history
        assert factory().turn_token_limit(settings, budget) > 32000


@pytest.mark.asyncio
async def test_actual_decision_http_body_is_logged_and_has_fixed_four_fields(tmp_path):
    import json
    import httpx
    from langchain_openai import ChatOpenAI
    from langgraph.runtime import Runtime
    from app.context.logging import ContextLogger
    from app.workflow.agent import llm_call
    from tests.test_workflow_agent import setup
    from tests.test_context_budget import settings
    bodies = []
    packets, samples = [], []
    path = tmp_path / 'app.log'
    logger = ContextLogger(path)
    def respond(request):
        body = json.loads(request.content)
        bodies.append(body)
        logs = [json.loads(line) for line in path.read_text(encoding='utf-8').splitlines()]
        sent = next(row for row in logs if row['event'] == 'model_ctx')
        assert sent['messages'] == body['messages'] and sent['tools'] == body['tools']
        args = {'reply_mode':'clarification','suggested_actions':[], 'refund_decision':None,'decision_reason':None}
        return httpx.Response(200, json={'id':'offline','object':'chat.completion','created':0,'model':'offline',
            'choices':[{'index':0,'finish_reason':'stop','message':{'role':'assistant','content':json.dumps(args)}}],
            'usage':{'prompt_tokens':400,'completion_tokens':40,'total_tokens':440}})
    context, state = setup([], question='查订单')
    context.context_logger = logger
    context.context_packet_observer = packets.append
    context.context_calibration_observer = samples.append
    context.settings = settings()
    async with httpx.AsyncClient(transport=httpx.MockTransport(respond)) as client:
        model = ChatOpenAI(model='offline', api_key='offline', base_url='https://offline.invalid/v1',
            http_async_client=client, max_retries=0, use_responses_api=False)
        context.decision_model = model
        try:
            result = await llm_call(state, Runtime(context=context))
        finally:
            await model.root_async_client.close()
            model.root_client.close()
            logger.close()
    assert result['reply_mode'] == 'clarification' and len(bodies) == 1
    logs = [json.loads(line) for line in path.read_text(encoding='utf-8').splitlines()]
    sample = next(row for row in logs if row['event'] == 'token_calibration')
    assert sample['prompt_tokens'] == 400 and sample['calibrated'] is False
    from langchain_openai.chat_models.base import _convert_message_to_dict
    assert [_convert_message_to_dict(m) for m in packets[0].messages] == bodies[0]['messages']
    assert list(packets[0].tools) == bodies[0]['tools'] and samples[0]['prompt_tokens'] == 400
    untouched, _ = setup([])
    assert untouched.context_packet_observer is None and untouched.context_calibration_observer is None
    packets[0].messages[0].content = 'mutated local copy'
    assert [_convert_message_to_dict(m) for m in packets[0].messages] == bodies[0]['messages']


@pytest.mark.asyncio
async def test_oversized_business_result_stops_without_truncating_sql():
    import json
    from langchain_core.messages import ToolMessage
    from tests.test_workflow_agent import setup, run
    from tests.workflow_fakes import workflow_call
    from app.agent.bare import UNFINISHED_ANSWER
    context, state = setup([], question='订单1001状态')
    text = json.dumps({'order_id':'1001', 'mock':True, 'details':'巨量' * 4000}, ensure_ascii=False)
    state['messages'] += [workflow_call('query_order', {'order_id':'1001'}), ToolMessage(text, tool_call_id='call_1')]
    from app.core.errors import ServiceError
    with pytest.raises(ServiceError) as caught:
        await run(context, state)
    assert caught.value.code == 'input_too_long'
    assert state['messages'][-1].content == text
    assert context.decision_model.decisions == context.model.streams == 0


@pytest.mark.asyncio
async def test_unfittable_faq_is_capacity_error_before_agent_call():
    import json
    from langchain_core.messages import ToolMessage
    from tests.test_workflow_agent import setup, run
    from tests.workflow_fakes import workflow_call
    from tests.test_context_evidence import faq
    from app.core.errors import ServiceError
    context, state = setup([], question='退货政策')
    payload = faq(1)
    payload['matches'][0]['answer'] = '完整政策' * 3000
    text = json.dumps(payload, ensure_ascii=False)
    state['messages'] += [workflow_call('query_faq', {'keyword':'退货'}), ToolMessage(text, tool_call_id='call_1')]
    with pytest.raises(ServiceError) as caught:
        await run(context, state)
    assert caught.value.code == 'input_too_long'
    assert state['messages'][-1].content == text
    assert context.decision_model.decisions == context.model.streams == 0


@pytest.mark.asyncio
async def test_business_faq_uses_resolved_plan_top_five_and_raw_keyword_guard():
    import json
    from langgraph.runtime import Runtime
    from app.workflow.agent import tool_node
    from app.repositories.faq import FAQRepository
    from app.orders.demo import DemoOrderProvider
    from app.tools.business import contextual_tools
    from app.tools.registry import build_registry
    from app.tools.types import ToolContext
    from app.knowledge.types import ChunkRecord, VectorHit
    from app.retrieval.types import RerankHit
    from tests.test_retrieval_service import service_parts
    from tests.test_workflow_agent import setup
    from tests.workflow_fakes import workflow_call
    from tests.test_context_budget import settings
    service, _, repo, embedder, index, planner, reranker = service_parts(
        [VectorHit(i,.9) for i in range(12)],
        [ChunkRecord('售后',f'问题{i}',f'政策{i}',id=i,vectorize_status='done') for i in range(12)],
        [RerankHit(index=i,score=1-i/100) for i in range(12)])
    raw, resolved = '它可以退吗？', '订单1001的台灯可以退吗？'
    context, state = setup([],question=raw)
    context.settings = settings(rerank_top_k=5,rerank_min_score=.5)
    context.faq_repository = FAQRepository(None,None,None,retriever=service)
    owner_calls=[]
    async def owner(cid):
        owner_calls.append(cid)
        return 'different-owner'
    tc=ToolContext('session',1,raw)
    context.registry=build_registry(context.faq_repository,None,tc,
        order_provider=DemoOrderProvider(),owner_resolver=owner)
    state.update(resolved_question=resolved,selected=workflow_call('query_faq',{'keyword':'可以退'},'faq'))
    result=await tool_node(state,Runtime(context=context,stream_writer=lambda event:None))
    assert planner.calls == []
    assert embedder.texts == [resolved] and reranker.calls[-1][0] == resolved
    assert reranker.calls[-1][2] == 5 and len(repo.calls[-1]) == 12
    assert len(json.loads(result['messages'][-1].content)['matches']) == 5
    assert state['raw_question'] == raw and context.repository.messages[0].tool_calls[0]['args']=={'keyword':'可以退'}
    # Same raw-substring guard and owner closures remain outside model control.
    rejected=await context.registry['query_faq'].ainvoke({'keyword':'不存在片段'})
    assert rejected['error']['code']=='invalid_keyword' and len(embedder.texts)==1
    missing=await context.registry['query_order'].ainvoke({'order_id':'1001'})
    assert missing['error']['code']=='not_found' and owner_calls==['session']


@pytest.mark.asyncio
@pytest.mark.parametrize('options', [{}, dict(model_context_window=18000, max_output_tokens=2000,
                                           max_agent_steps=3, rerank_top_k=5)])
async def test_default_lifespan_activates_real_factory_without_provider(tmp_path, options):
    import json
    from app.main import create_app
    from app.context.logging import ContextLogger
    from app.context.types import ContextAnchors
    from tests.fakes import fake_settings, FAQStub, decode_sse
    from tests.test_workflow_api import Store, request
    from tests.workflow_fakes import ScriptedWorkflowModel
    class EmptyContext:
        async def load(self, cid):
            return ContextAnchors(None, None), ()
        async def list_downgraded(self, **kwargs):
            return []
    path = tmp_path / 'app.log'
    logger = ContextLogger(path)
    class LifecycleModel(ScriptedWorkflowModel):
        def bind(self, **kwargs):
            return self
    config = fake_settings(workflow_checkpoint_path=tmp_path/'root.sqlite', **options)
    app = create_app(config,
        model=LifecycleModel(), repository=Store(), faq_repository=FAQStub(),
        context_repository=EmptyContext(), context_logger=logger)
    async with app.router.lifespan_context(app):
        frames = decode_sse((await request(app, '你好')).text)
        assert frames[-1][0] == 'done'
        service = app.state.chat_service
        assert service.context_coordinator is not None
        assert service.context_budget_provider is not None
    logger.close()
    records = [json.loads(line) for line in path.read_text(encoding='utf-8').splitlines()]
    from app.context.logging import budget_fields
    actual = next(row['budget'] for row in records if row['event']=='context_budget')
    assert actual == budget_fields(factory().workflow_budget(config, production_registry()))
    assert any(row['event']=='history_ctx' and row['sent'] is False for row in records)


@pytest.mark.asyncio
@pytest.mark.parametrize('stage', ['expansion', 'sufficiency', 'query_planner'])
async def test_remaining_stage_records_actual_http_before_failure(tmp_path, stage):
    import json
    import httpx
    from langchain_openai import ChatOpenAI
    from app.context.logging import ContextLogger
    from app.core.errors import ServiceError
    from app.workflow.expansion import QueryExpander
    from app.core.sufficiency import SufficiencyService
    from app.retrieval.query import QueryPlanner
    from tests.test_context_evidence import faq
    from app.core.evidence import prepare_workflow_evidence
    from app.orders.demo import DemoOrderProvider
    path = tmp_path/'app.log'
    logger, bodies, captured = ContextLogger(path), [], []
    def respond(request):
        body = json.loads(request.content)
        bodies.append(body)
        records = [json.loads(line) for line in path.read_text(encoding='utf-8').splitlines()]
        assert records[-1]['messages'] == body['messages']
        assert records[-1]['phase'] == stage
        return httpx.Response(500, json={'error':{'message':'offline failure'}})
    async with httpx.AsyncClient(transport=httpx.MockTransport(respond)) as client:
        model = ChatOpenAI(model='offline', api_key='offline', base_url='https://offline.invalid/v1',
            http_async_client=client, max_retries=0, use_responses_api=False)
        kwargs = dict(context_logger=logger, on_packet=captured.append)
        try:
            with pytest.raises(ServiceError):
                if stage == 'expansion':
                    order = await DemoOrderProvider().get_order(user_id='demo-user',order_id='1001')
                    await QueryExpander(model,input_budget=18000,timeout_seconds=2).expand('订单1001能退吗',order,**kwargs)
                elif stage == 'sufficiency':
                    await SufficiencyService(model,input_budget=18000,minimum_rerank_score=.5).check(
                        '退货政策是什么',prepare_workflow_evidence([faq()],top_k=5,token_budget=2250),**kwargs)
                else:
                    await QueryPlanner(model,18000).plan('退款咋办',**kwargs)
        finally:
            model.root_client.close()
            await model.root_async_client.close()
            logger.close()
    assert len(bodies) == len(captured) == 1


@pytest.mark.asyncio
async def test_agent_earliest_summary_uses_validated_source_before_fresh_read():
    from dataclasses import replace
    from datetime import datetime, timezone
    from langgraph.runtime import Runtime
    from app.context.types import ContextAnchors, SummarySegment
    from app.repositories.records import MessageRecord
    from app.workflow.entities import snapshot_provenance
    from app.workflow.agent import llm_call
    from tests.test_context_view import snapshot
    from tests.test_workflow_agent import setup, control
    context, state = setup([control('clarification')],question='最开始那个订单状态',intent='订单')
    rows = [MessageRecord(1,'user','订单1001状态',None,None), MessageRecord(2,'assistant','请核实',None,None),
            MessageRecord(3,'user','订单1002状态',None,None), MessageRecord(4,'assistant','请核实',None,None)]
    frozen = snapshot(anchors=ContextAnchors(4,4),segments=(SummarySegment(1,1,2,'订单1001查状态',datetime.now(timezone.utc)),
        SummarySegment(2,3,4,'订单1002查状态',datetime.now(timezone.utc))))
    from tests.test_context_budget import settings
    from app.workflow.context_budget import workflow_budget
    context.settings = settings()
    context.context_snapshot = replace(frozen,user_message_id=state['user_message_id'],
                                      budget=workflow_budget(context.settings,context.registry))
    context.context_provenance = snapshot_provenance(frozen,rows)
    state['resolved_question']='订单1001状态'
    result=await llm_call(state,Runtime(context=context))
    assert result['selected'].tool_calls[0]['args']=={'order_id':'1001'}
    assert result['selected_origin']=='workflow' and context.repository.messages==[]


@pytest.mark.asyncio
async def test_resume_preflights_current_native_peak_before_any_model():
    from dataclasses import replace
    from types import SimpleNamespace
    from langchain_core.messages import ToolMessage
    from app.context.service import serialize_snapshot
    from app.workflow.service import WorkflowChatService
    from app.core.errors import ServiceError
    from tests.test_workflow_agent import setup
    from tests.workflow_fakes import workflow_call
    from tests.test_context_budget import settings
    from app.workflow.context_budget import runtime_snapshot
    context,state=setup([],question='订单1001状态')
    context.settings=settings()
    frozen=runtime_snapshot(state,context)
    state['context_snapshot']=serialize_snapshot(frozen)
    state['messages'] += [workflow_call('query_order',{'order_id':'1001'}),
        ToolMessage('{"order_id":"1001","mock":true,"details":"'+'巨量'*300+'"}',tool_call_id='call_1')]
    context.settings=settings(tool_result_max_tokens=100)
    service=object.__new__(WorkflowChatService)
    service.context_coordinator=SimpleNamespace()
    service.context_budget_provider=lambda registry: frozen.budget
    service.context_logger=None
    service.settings=context.settings
    with pytest.raises(ServiceError) as caught:
        await service._prepare_context(state,context,[],resume=True)
    assert caught.value.code=='context_configuration_conflict' and caught.value.status_code==409
    assert context.decision_model.decisions==context.model.streams==0


@pytest.mark.asyncio
async def test_long_current_text_is_preserved_but_oversize_rewrite_stops_before_call():
    from langgraph.runtime import Runtime
    from app.workflow.agent import llm_call
    from app.core.errors import ServiceError
    from tests.test_workflow_agent import setup,control
    raw='请核实商品信息。'*150
    context,state=setup([control('clarification')],question=raw)
    result=await llm_call(state,Runtime(context=context))
    assert result['reply_mode']=='clarification'
    assert any(m.content==raw for m in context.decision_model.tool_inputs[0])
    assert state['messages'][0].content==raw
    context,state=setup([],question='它还有哪些信息')
    state['resolved_question']='商品信息待确认。'*100
    with pytest.raises(ServiceError) as caught:
        await llm_call(state,Runtime(context=context))
    assert caught.value.code=='input_too_long'
    assert context.decision_model.decisions==0 and context.repository.messages==[]
    assert state['messages'][0].content=='它还有哪些信息'
    raw='查订单'*800
    context,state=setup([],question=raw)
    with pytest.raises(ServiceError) as caught:
        await llm_call(state,Runtime(context=context))
    assert caught.value.status_code==422
    assert state['messages'][0].content==raw and context.decision_model.decisions==0


def test_calibration_missing_usage_stays_unknown_and_version_unvalidated():
    from langchain_core.messages import AIMessage
    from app.context.tokens import calibration_sample
    from app.workflow.context_budget import standalone_packet
    packet=standalone_packet([HumanMessage('完整输入')],output_tokens=2000)
    absent=calibration_sample(packet,AIMessage('response'))
    assert absent['prompt_tokens'] is absent['absolute_error'] is absent['relative_error'] is None
    assert absent['calibrated'] is False
    present=calibration_sample(packet,AIMessage('response',usage_metadata={
        'input_tokens':10,'output_tokens':2,'total_tokens':12}))
    assert present['prompt_tokens']==10 and present['absolute_error']==packet.estimated_tokens-10


@pytest.mark.parametrize('observed', [1, 1000])
def test_calibration_absolute_error_for_over_and_under_estimates(observed):
    from langchain_core.messages import AIMessage
    from app.context.tokens import calibration_sample
    from app.workflow.context_budget import standalone_packet
    packet = standalone_packet([HumanMessage('完整输入')], output_tokens=512)
    sample = calibration_sample(packet, AIMessage('ok', usage_metadata={
        'input_tokens': observed, 'output_tokens': 1, 'total_tokens': observed + 1}))
    assert sample['absolute_error'] == abs(packet.estimated_tokens - observed)
    assert sample['relative_error'] == (packet.estimated_tokens - observed) / observed


@pytest.mark.parametrize('case', ['missing','version'])
def test_factory_rejects_missing_or_incompatible_normative_turn_data(monkeypatch,case):
    from pathlib import Path
    from tests.test_context_budget import settings
    from tests.test_workflow_agent import setup
    import json
    original=Path.read_text
    def read(path,*args,**kwargs):
        if path.name=='steady_turns.json':
            if case=='missing':
                raise FileNotFoundError()
            value=json.loads(original(path,*args,**kwargs))
            value['estimator_version']='not-current'
            return json.dumps(value)
        return original(path,*args,**kwargs)
    monkeypatch.setattr(Path,'read_text',read)
    with pytest.raises(ValueError,match='Missing|version mismatch'):
        factory().workflow_budget(settings(),setup([])[0].registry)


@pytest.mark.asyncio
async def test_actual_sufficiency_usage_reduces_remaining_final_budget():
    import json
    from langgraph.runtime import Runtime
    from langchain_core.messages import ToolMessage
    from app.core.errors import ServiceError
    from app.workflow.agent import finalize_answer
    from tests.test_workflow_agent import setup
    from tests.workflow_fakes import workflow_call
    from tests.test_context_budget import settings
    from tests.test_context_evidence import faq
    context,state=setup([],question='退货政策',intent='商品咨询',answer='完整政策0[1]。')
    context.settings=settings(agent_total_token_budget=10000,rerank_min_score=.5)
    context.sufficiency.usage={'actual':9000,'estimated':0,'actual_calls':1,'estimated_calls':0}
    state.update(route='knowledge',reply_mode='answer')
    state['messages'] += [workflow_call('query_faq',{'keyword':'退货'},'faq'),
                         ToolMessage(json.dumps(faq(1)),tool_call_id='faq')]
    with pytest.raises(ServiceError) as caught:
        await finalize_answer(state,Runtime(context=context,stream_writer=lambda event:None))
    assert caught.value.code=='token_budget'
    assert context.model.streams==0


@pytest.mark.asyncio
@pytest.mark.parametrize('stage', ['understanding','classification'])
@pytest.mark.parametrize('failure', [None,'error','cancel'])
async def test_snapshot_stage_usage_matches_packet_and_custom_output(tmp_path,stage,failure):
    import asyncio,json
    from langchain_core.messages import AIMessage
    from app.context.logging import ContextLogger
    from app.workflow.understanding import QueryUnderstanding
    from app.workflow.intent import IntentClassifier
    from app.workflow.context_budget import runtime_snapshot
    from tests.test_context_budget import settings
    from tests.test_workflow_agent import setup
    from tests.workflow_fakes import ScriptedWorkflowModel
    context,state=setup([],question='查订单')
    context.settings=settings()
    frozen=runtime_snapshot(state,context)
    response=AIMessage('{"query":"查订单"}' if stage=='understanding' else '{"intent":"订单","confidence":0.95}',
                       response_metadata={'finish_reason':'stop'})
    if failure:
        response=RuntimeError('controlled') if failure=='error' else asyncio.CancelledError()
    model=ScriptedWorkflowModel(intent_replies=[response])
    service=(QueryUnderstanding(model,input_budget=100,timeout_seconds=2) if stage=='understanding'
             else IntentClassifier(model,input_budget=100,timeout_seconds=2))
    path=tmp_path/'app.log'
    logger=ContextLogger(path)
    kwargs=dict(snapshot=frozen,context_logger=logger,output_tokens=128)
    operation=(lambda:service.resolve('查订单',[],**kwargs)) if stage=='understanding' else (lambda:service.classify('查订单',**kwargs))
    try:
        if failure:
            with pytest.raises(BaseException):
                await operation()
        else:
            await operation()
    finally:
        logger.close()
    records=[json.loads(line) for line in path.read_text(encoding='utf-8').splitlines()]
    sent=next(row for row in records if row['event']=='model_ctx')
    assert service.usage['estimated']==sent['estimated_tokens']+128
    assert service.usage['estimated_calls']==1
    assert next(row for row in records if row['event']=='token_calibration')['prompt_tokens'] is None
