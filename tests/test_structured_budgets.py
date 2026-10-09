# 真实HTTP序列化验证独立预算；浅副本只借用同一客户端，来源模型不变。
import json
import httpx
import pytest
from langchain_core.messages import HumanMessage
from app.core.llm import create_model
from app.retrieval.query import QueryPlanner
from app.core.sufficiency import SufficiencyService
from tests.fakes import fake_settings
from tests.test_evidence import build


@pytest.mark.parametrize('field',['max_tokens','max_completion_tokens'])
async def test_query_self_check_and_final_send_independent_budgets_and_share_owned_clients(field):
    """通过实际HTTP序列化验证三个预算独立且浅副本不改变最终模型所有权。"""
    import app.core.llm as llm
    requests=[]
    def handle(request):
        """模拟完整上游HTTP响应，保留真实请求序列化和结构化解析。"""
        body=json.loads(request.content); requests.append(body)
        prompt=body['messages'][0]['content']
        content='{"standard":"邮费？","expansions":[]}' if '只整理本轮原话' in prompt else (
            '{"useful":true,"reason":"覆盖","response_kind":"knowledge"}' if '直接判断当前证据' in prompt else '答案')
        return httpx.Response(200,json={'id':'synthetic','object':'chat.completion','created':0,'model':'fake-chat',
            'choices':[{'index':0,'finish_reason':'stop','message':{'role':'assistant','content':content}}]})
    settings=fake_settings(llm_token_limit_field=field,query_max_output_tokens=2048,sufficiency_max_output_tokens=1777)
    async with httpx.AsyncClient(transport=httpx.MockTransport(handle)) as http:
        final=create_model(settings,http_async_client=http)
        try:
            query=llm.model_with_output_budget(final,settings,settings.query_max_output_tokens)
            self_check=llm.model_with_output_budget(final,settings,settings.sufficiency_max_output_tokens)
            assert query.root_async_client is self_check.root_async_client is final.root_async_client
            assert query.root_client is self_check.root_client is final.root_client
            await QueryPlanner(query,8000).plan('邮费？')
            await SufficiencyService(self_check,input_budget=8000,minimum_rerank_score=.5).check('邮费？',build())
            await final.ainvoke([HumanMessage('final')])
            assert [r[field] for r in requests]==[2048,1777,512]
            assert final.extra_body[field]==512 and query.extra_body[field]==2048
            other='max_tokens' if field=='max_completion_tokens' else 'max_completion_tokens'
            assert all(other not in r for r in requests)
            assert query.max_retries==self_check.max_retries==final.max_retries==0
        finally:
            await final.root_async_client.close()
            final.root_client.close()


async def test_injected_application_without_lifespan_still_uses_independent_self_check_budget():
    """验证提前注入的应用装配也使用独立自评预算，借用模型仍保持开放。"""
    from app.main import create_app
    from tests.fakes import ConversationStore, FAQStub
    requests=[]
    def handle(request):
        """模拟完整上游HTTP响应，保留真实请求序列化和结构化解析。"""
        requests.append(json.loads(request.content))
        return httpx.Response(200,json={'id':'synthetic','object':'chat.completion','created':0,'model':'fake',
            'choices':[{'index':0,'finish_reason':'stop','message':{'role':'assistant',
             'content':'{"useful":true,"reason":"覆盖","response_kind":"knowledge"}'}}]})
    settings=fake_settings()
    async with httpx.AsyncClient(transport=httpx.MockTransport(handle)) as http:
        model=create_model(settings,http_async_client=http)
        try:
            app=create_app(settings,model=model,repository=ConversationStore(),faq_repository=FAQStub())
            await app.state.chat_service.sufficiency_service.check('邮费？',build())
            assert requests[0]['max_tokens']==2048 and model.extra_body['max_tokens']==512
            assert not model.root_async_client.is_closed()
        finally:
            await model.root_async_client.close()
            model.root_client.close()


@pytest.mark.parametrize('use_settings',[False,True])
async def test_default_rewrite_deadline_allows_valid_response_after_old_fifteen_seconds(monkeypatch,use_settings):
    """用缩放后的真实取消计时器验证新的改写期限允许旧边界后的合法响应。"""
    import asyncio
    import app.retrieval.query as module
    from langchain_core.messages import AIMessage
    timeout=asyncio.timeout
    # 将秒同比缩短1000倍，真实取消感知deadline仍运行，避免测试等待25秒。
    monkeypatch.setattr(module.asyncio,'timeout',lambda seconds:timeout(seconds/1000))
    class Slow:
        def with_structured_output(self,schema,**kwargs):
            """按被测服务实际Schema绑定受控解析输出。"""
            self.schema=schema; return self
        async def ainvoke(self,messages):
            """返回经实际Schema校验的受控JSON，保留真实原文及结束状态。"""
            await asyncio.sleep(.025)
            raw='{"standard":"邮费？","expansions":[]}'
            return dict(raw=AIMessage(raw,response_metadata={'finish_reason':'stop'}),
                        parsed=self.schema.model_validate_json(raw),parsing_error=None)
    options={'timeout':fake_settings().query_timeout_seconds} if use_settings else {}
    plan=await module.QueryPlanner(Slow(),8000,**options).plan('邮费？')
    assert plan.standard=='邮费？'


def test_query_deadline_cap_rejects_more_than_sixty_without_changing_other_caps():
    """验证改写期限超过批准上限被拒绝，其他期限不随之变化。"""
    from pydantic import ValidationError
    from tests.test_retrieval_evaluation import Model
    with pytest.raises(ValidationError):
        fake_settings(query_timeout_seconds=61)
    with pytest.raises(ValueError):
        QueryPlanner(Model(),8000,timeout=61)
    settings=fake_settings()
    assert settings.sufficiency_timeout_seconds==20 and settings.chat_timeout_seconds==240
