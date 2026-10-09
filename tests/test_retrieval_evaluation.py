import importlib
from dataclasses import replace
import pytest
from app.knowledge.types import ChunkRecord, VectorHit
from app.retrieval.types import QueryPlan, RetrievalBundle, ScoredChunk
from tests.fakes import fake_settings


def api():
    """加载被测评估接口，缺实现时给出明确的行为失败。"""
    try:
        return importlib.import_module('evals.evaluate_retrieval')
    except ImportError:
        pytest.fail('retrieval evaluator is missing')


def case(identifier='A01'):
    """构造可人工核对的配送金标，隔离真实数据和模型费用。"""
    return dict(eval_id=identifier, bucket='A_policy', difficulty='easy', query='邮费？', category=None,
                required_facts=['8元'], gold_chunk_refs=[{'section_path':'配送', 'questions':'邮费？', 'answer':'8元'}],
                expected_refusal=False)


def test_gold_maps_exact_triples_and_all_physical_duplicates():
    """验证同标题不同问题不误算相关，重复三元组保留全部物理块。"""
    row = ChunkRecord('配送', '邮费？', '8元', section_path='配送', id=10, vectorize_status='done')
    mapped = api().map_gold([case()], [row, replace(row, id=11), replace(row, id=12, questions='退款？')])
    assert mapped['A01']['ids'] == [10, 11]
    assert mapped['A01']['duplicates'] == 1
    with pytest.raises(ValueError, match='gold'):
        api().map_gold([case()], [replace(row, questions='不同问题')])


class Planner:
    def __init__(self):
        """初始化受控依赖，隔离真实资源并记录行为供生命周期校验。"""
        self.ordinal=0
    async def plan(self, query):
        """产生受控合法计划或改写故障，并用变化内容检测重复改写。"""
        if query == 'bad':
            raise ValueError('rewrite failed')
        self.ordinal+=1
        return QueryPlan(standard=query if self.ordinal==1 else query+'改写', expansions=[])


class Retrieval:
    async def retrieve(self, question, *, strategy, query_plan, category=None):
        """提供固定候选和权威块，隔离真实Milvus及嵌入费用。"""
        row = ChunkRecord('配送', '邮费？', '8元', section_path='配送', id=10, vectorize_status='done')
        return RetrievalBundle(query_plan, strategy, [VectorHit(99,.9), VectorHit(10,.8)],
            [ScoredChunk(row, .8, {'dense':'cosine', 'bm25':'bm25', 'hybrid':'rrf','hybrid_rerank':'rerank'}[strategy])])


class Judge:
    async def judge(self, *args):
        """返回预设裁判结论或模拟非法上游，隔离付费请求。"""
        return {'claims':[{'claim':'8元','support':False,'reason':'controlled contradiction'}], 'score':0.}


class Ledger:
    def __init__(self):
        """初始化受控依赖，隔离真实资源并记录行为供生命周期校验。"""
        self.cases=[]
    async def record_fabrication(self, case):
        """捕获有效编造输入，供断言必需持久化副作用和题号归属。"""
        self.cases.append(case)


class Model:
    def with_structured_output(self, schema, **kwargs):
        """按被测服务实际Schema绑定受控解析输出。"""
        self.schema=schema
        return self
    async def ainvoke(self, messages):
        """返回经实际Schema校验的受控JSON，保留真实原文及结束状态。"""
        from langchain_core.messages import AIMessage
        raw='{"useful":true,"reason":"覆盖","response_kind":"knowledge"}'
        return dict(raw=AIMessage(raw,response_metadata={'finish_reason':'stop'}),
                    parsed=self.schema.model_validate_json(raw),parsing_error=None)
    async def astream(self, messages):
        """提供受控最终流式片段或异常工具申请，验证生成错误边界。"""
        from langchain_core.messages import AIMessageChunk
        yield AIMessageChunk('邮费8元[1]。', response_metadata={'finish_reason':'stop'})


async def test_four_strategies_freeze_plan_and_persist_every_valid_fabrication(tmp_path):
    """验证一次改写四策略共享，全部有效编造必须按测试题号写入台账。"""
    ledger=Ledger()
    report=await api().evaluate_cases([case()], gold={'A01':{'ids':[10], 'duplicates':0}},
        planner=Planner(), retrieval=Retrieval(), model=Model(), judge=Judge(), quality=ledger,
        settings=fake_settings(), database_mode='test', output=tmp_path/'controlled.json', kind='controlled')
    assert (report['attempted'],report['not_attempted'],report['errors']) == (4,0,0)
    assert len(ledger.cases)==4 and {c.eval_id for c in ledger.cases}=={'TA01'}
    assert {r['standard'] for r in report['records']}=={'邮费？'}
    assert all(r['recall_at_50']==1 and r['mrr_at_10']==1 for r in report['records'])
    assert (tmp_path/'controlled.md').exists()


async def test_failed_query_preserves_not_attempted_and_continues_independent_queries(tmp_path):
    """验证改写失败留下四条未执行且其他独立问题继续完成。"""
    bad=case('A02'); bad['query']='bad'
    report=await api().evaluate_cases([bad,case()], gold={i:{'ids':[10],'duplicates':0} for i in ['A01','A02']},
        planner=Planner(),retrieval=Retrieval(),model=Model(),judge=Judge(),quality=Ledger(),
        settings=fake_settings(),database_mode='test',output=tmp_path/'partial.json',kind='controlled')
    assert (report['attempted'],report['not_attempted'])==(4,4)
    assert len(report['query_errors'])==1 and not report['passed']
    assert all(r['status']=='not_attempted' for r in report['records'] if r['eval_id']=='A02')


async def test_judge_error_never_writes_fabrication(tmp_path):
    """验证裁判外部故障只记错误，不冒充编造证据。"""
    class BadJudge:
        async def judge(self,*args):
            """返回预设裁判结论或模拟非法上游，隔离付费请求。"""
            raise ValueError('invalid raw json')
    ledger=Ledger()
    report=await api().evaluate_cases([case()], gold={'A01':{'ids':[10],'duplicates':0}},planner=Planner(),
        retrieval=Retrieval(),model=Model(),judge=BadJudge(),quality=ledger,settings=fake_settings(),
        database_mode='test',output=tmp_path/'controlled.json',kind='controlled')
    assert report['errors']==4 and not ledger.cases
    assert all(r['error_stage']=='judge' for r in report['records'])


async def test_final_tool_request_rejected_even_with_stop_and_judge_not_reached(tmp_path):
    """验证最终流即使stop也拒绝工具申请，并避免无效答案写账。"""
    class ToolModel(Model):
        async def astream(self,messages):
            """提供受控最终流式片段或异常工具申请，验证生成错误边界。"""
            from langchain_core.messages import AIMessageChunk
            yield AIMessageChunk('邮费8元[1]。',response_metadata={'finish_reason':'stop'},
                tool_calls=[dict(name='query_faq',args={},id='unexpected')])
    ledger=Ledger()
    report=await api().evaluate_cases([case()],gold={'A01':{'ids':[10],'duplicates':0}},planner=Planner(),
        retrieval=Retrieval(),model=ToolModel(),judge=Judge(),quality=ledger,settings=fake_settings(),
        database_mode='test',output=tmp_path/'tools.json',kind='controlled')
    assert report['errors']==4 and not ledger.cases
    assert all(r['error_stage']=='generation' for r in report['records'])


async def test_partial_calibration_never_recommends_a_threshold(tmp_path):
    """验证少于八份有效样本不能生成门槛，保留未执行数量。"""
    cases=[case('K'+str(i)) for i in range(8)]; cases[0]['query']='bad'
    for c in cases:
        c['evidence_sufficient']=True
    gold={c['eval_id']:{'ids':[10],'duplicates':0} for c in cases}
    report=api().initial_report(cases,gold,database_mode='test',kind='controlled',mode='calibrate')
    await api().calibrate_cases(cases,gold=gold,planner=Planner(),retrieval=Retrieval(),
                               output=tmp_path/'calibration.json',report=report)
    assert report['calibration'] is None and not report['passed']
    assert (report['attempted'],report['not_attempted'])==(7,1)


def test_summary_has_metric_denominators_and_errors_not_perfect_scores():
    """验证失败与空有效分母不被汇总为满分忠实度或拒答率。"""
    row=dict(eval_id='X',bucket='D_unanswerable',strategy='dense',status='error',gold_ids=[])
    summary=api().summarize([row])
    overall=next(r for r in summary if r['bucket']=='overall' and r['strategy']=='dense')
    assert (overall['errors'],overall['completed'],overall['faithfulness_n'])==(1,0,0)
    assert overall['refusal_accuracy'] is None and overall['faithfulness'] is None


def test_judge_output_budget_is_independent_and_rejects_bool():
    """验证裁判配置独立于最终回答预算，并拒绝布尔伪整数。"""
    from pydantic import ValidationError
    settings=fake_settings(faith_judge_max_output_tokens=2048,faith_judge_input_token_budget=16000)
    assert settings.max_output_tokens==512 and settings.faith_judge_max_output_tokens==2048
    with pytest.raises(ValidationError):
        fake_settings(faith_judge_max_output_tokens=True)


def test_failure_diagnostics_preserve_cause_types_without_exception_text():
    """验证安全诊断保留异常因果而不泄漏异常原文。"""
    from app.core.errors import ServiceError
    try:
        try:
            raise ValueError('private secret must never be printed')
        except ValueError as cause:
            raise ServiceError('invalid_structured_output','safe',502) from cause
    except ServiceError as exc:
        result=api().failure_details(exc)
    assert result=={'error_type':'ServiceError','error_code':'invalid_structured_output',
                    'cause_types':['ValueError']}


async def test_missing_calibration_blocks_compare_before_any_models_or_database(tmp_path, monkeypatch):
    """验证缺有效校准时比较保存全部未执行且不发送模型请求。"""
    module=api()
    monkeypatch.setattr(module,'test_settings',lambda:fake_settings(rerank_min_score=None))
    report=await module.evaluate([case()],mode='compare',database_mode='test',output=tmp_path/'blocked.json')
    assert report['error_code']=='missing_calibrated_threshold'
    assert (report['attempted'],report['not_attempted'],report['model_request_count'])==(0,4,{})


async def test_configured_ledger_uses_dataset_id_without_test_prefix(tmp_path):
    """验证显式业务库台账保留原评估题号，不加测试前缀。"""
    ledger=Ledger()
    report=await api().evaluate_cases([case()],gold={'A01':{'ids':[10],'duplicates':0}},planner=Planner(),
        retrieval=Retrieval(),model=Model(),judge=Judge(),quality=ledger,settings=fake_settings(),
        database_mode='configured',output=tmp_path/'configured-controlled.json',kind='controlled')
    assert report['passed'] and {c.eval_id for c in ledger.cases}=={'A01'}


async def test_model_metadata_keeps_finish_usage_and_lengths_without_content_or_headers():
    """验证模型结束元数据可复核，而凭据和隐藏思考原文不会保存。"""
    import httpx,json
    report={'model_request_count':{}}
    hooks=api().model_http_hooks(report)
    async with httpx.AsyncClient(event_hooks=hooks,transport=httpx.MockTransport(lambda request:httpx.Response(200,json={
        'model':'fake','usage':{'completion_tokens':512},'choices':[{'finish_reason':'length',
        'message':{'content':'','reasoning_content':'hidden'}}]}))) as http:
        await http.post('https://synthetic.invalid',headers={'authorization':'secret'},json={'model':'fake','stream':False,'max_tokens':2048})
    assert report['model_request_count']=={'fake':1}
    row=report['model_requests'][0]
    assert row['response_metadata']['choices']==[{'finish_reason':'length','content_characters':0,'reasoning_characters':6}]
    assert row['response_metadata']['usage']=={'completion_tokens':512}
    assert 'secret' not in json.dumps(report) and 'hidden' not in json.dumps(report)


async def test_model_response_metadata_hook_does_not_buffer_streaming_answers():
    """验证安全响应钩子不提前读取最终SSE正文。"""
    import httpx
    reads=[]
    class Bytes(httpx.AsyncByteStream):
        async def __aiter__(self):
            """记录正文实际被消费的时刻，检测响应钩子是否提前缓冲SSE。"""
            reads.append(True)
            yield b'data: [DONE]\n\n'
    report={'model_request_count':{}}
    async with httpx.AsyncClient(event_hooks=api().model_http_hooks(report),transport=httpx.MockTransport(
        lambda request:httpx.Response(200,stream=Bytes()))) as http:
        async with http.stream('POST','https://synthetic.invalid',json={'model':'fake','stream':True}) as response:
            assert reads==[]
            await response.aread()
    assert reads==[True]


@pytest.mark.parametrize('fail_judge',[False,True])
async def test_evaluator_closes_borrowed_http_once_and_all_owned_sync_clients_on_initialization_failure(tmp_path,monkeypatch,fail_judge):
    """验证导入或第二模型构造失败时共享HTTP只关一次、已拥有客户端均回收。"""
    import httpx
    from types import SimpleNamespace
    module=api(); closed=[]; created=[]
    class CountingHTTP(httpx.AsyncClient):
        async def aclose(self):
            """记录受控资源关闭次数，检测泄漏或重复关闭。"""
            closed.append('http')
            await super().aclose()
    class Database:
        def __init__(self,url):
            """初始化受控依赖，隔离真实资源并记录行为供生命周期校验。"""
            pass
        async def dispose(self):
            """记录受控数据库释放，验证其他清理失败不阻断回收。"""
            closed.append('database')
    class Index:
        def __init__(self,*args,**kwargs):
            """初始化受控依赖，隔离真实资源并记录行为供生命周期校验。"""
            self.timeout=5
        async def _call(self,*args):
            """返回不存在的受控集合，避免生命周期测试访问真实Milvus。"""
            return False
        async def aclose(self):
            """记录受控资源关闭次数，检测泄漏或重复关闭。"""
            closed.append('index')
    def create(settings,*,http_async_client):
        """构造借用HTTP的受控模型，模拟第二实例初始化失败。"""
        created.append(True)
        if fail_judge and len(created)==2:
            raise RuntimeError('controlled judge initialization failure')
        async def close():
            """模拟SDK关闭借用HTTP，检测错误的重复资源所有权。"""
            await http_async_client.aclose()
        return SimpleNamespace(root_async_client=SimpleNamespace(close=close),
            root_client=SimpleNamespace(close=lambda:closed.append('sync_model')))
    async def import_failure(*args):
        """模拟临时知识导入失败，验证后续资源仍逐项回收。"""
        raise RuntimeError('controlled owned import failure')
    monkeypatch.setattr(module.httpx,'AsyncClient',CountingHTTP)
    monkeypatch.setattr(module,'test_settings',lambda:fake_settings(mysql_password='fake'))
    monkeypatch.setattr(module,'Database',Database)
    monkeypatch.setattr(module,'HybridMilvusIndex',Index)
    monkeypatch.setattr(module,'create_model',create)
    monkeypatch.setattr(module,'import_document',import_failure)
    report=await module.evaluate([case()],mode='calibrate',database_mode='test',output=tmp_path/'init-failure.json')
    assert closed.count('http')==1 and closed.count('sync_model')==(1 if fail_judge else 2)
    assert 'index' in closed and 'database' in closed
    assert not report['passed']
    assert report['cleanup']==('owned_temporary_resources_removed_ledger_preserved' if fail_judge else 'failed')


@pytest.mark.parametrize('stage',['retrieval','generation'])
async def test_shared_rewrite_latency_is_charged_to_every_strategy_deadline(tmp_path,monkeypatch,stage):
    """用真实缩放取消边界验证共享改写耗时计入每种策略的FAQ和总期限。"""
    import asyncio
    module=api(); clock={'now':0.}; timeout=asyncio.timeout
    rewrite=30. if stage=='retrieval' else 50.
    monkeypatch.setattr(module,'monotonic',lambda:clock['now'])
    monkeypatch.setattr(module.asyncio,'timeout',lambda seconds:timeout(seconds/100))
    class SlowPlan(Planner):
        async def plan(self,query):
            """冻结一次合法计划并模拟已消耗的改写时间，不增加模型请求。"""
            plan=await super().plan(query)
            clock['now']=rewrite
            return plan
    class SlowRetrieval(Retrieval):
        async def retrieve(self,*args,**kwargs):
            """模拟旧FAQ期限内但扣减改写后超时的真实异步等待。"""
            if stage=='retrieval':
                await asyncio.sleep(.75)
            return await super().retrieve(*args,**kwargs)
    class SlowFinal(Model):
        async def astream(self,messages):
            """模拟旧总期限内但扣减改写后超时的最终流。"""
            if stage=='generation':
                await asyncio.sleep(2.15)
            async for chunk in super().astream(messages):
                yield chunk
    ledger=Ledger()
    report=await module.evaluate_cases([case()],gold={'A01':{'ids':[10],'duplicates':0}},planner=SlowPlan(),
        retrieval=SlowRetrieval(),model=SlowFinal(),judge=Judge(),quality=ledger,settings=fake_settings(),
        database_mode='test',output=tmp_path/'charged.json',kind='controlled')
    assert report['errors']==4 and not ledger.cases
    assert all(r['error_stage']==stage and r['rewrite_latency_seconds']==rewrite for r in report['records'])
    assert all(r['faq_remaining_seconds']==90-rewrite and r['chat_remaining_seconds']==240-rewrite for r in report['records'])
