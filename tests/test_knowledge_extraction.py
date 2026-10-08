# 历史对话抽问答测试，覆盖整会话批次预算、来源限定、结构校验及正常结束要求。
import importlib
import json

import pytest
from langchain_core.messages import AIMessage

from app.core.errors import InputTooLong, ServiceError
from app.knowledge.types import ConversationTranscript, ExtractedQA
from app.repositories.records import MessageRecord


# 加载会话问答抽取模块，缺失实现时报告明确失败。
def extraction():
    try:
        return importlib.import_module('app.knowledge.extraction')
    except ImportError:
        pytest.fail('QA extraction is missing')


# 构造带会话和最后消息编号的完整合成客服轮次。
def conversation(identifier=1, content='标准配送多少钱？'):
    return ConversationTranscript(identifier, identifier * 10 + 1, [
        MessageRecord(identifier * 10, 'user', content, None, None),
        MessageRecord(identifier * 10 + 1, 'assistant', '标准配送8元。', None, None),
    ])


class Model:
    # 预设问答输出或故障，并记录模型输入以核对批次与原文。
    def __init__(self, data=None, *, fault=None):
        self.data = data if data is not None else {'qas': []}
        self.fault = fault
        self.calls = []

    # 核对 JSON 模式及原始响应选项，并保存用于生成解析结果的结构。
    def with_structured_output(self, schema, *, method, include_raw):
        assert (method, include_raw) == ('json_mode', True)
        self.schema = schema
        return self

    # 返回真实结构校验后的响应包，并按场景模拟残缺 JSON、截断或上游异常。
    async def ainvoke(self, messages):
        self.calls.append(messages)
        if isinstance(self.fault, Exception):
            raise self.fault
        raw = json.dumps(self.data, ensure_ascii=False)
        parsed = self.schema.model_validate(self.data)
        return {'raw': AIMessage(raw if self.fault != 'incomplete' else raw[:-1],
            response_metadata={'finish_reason': 'length' if self.fault == 'length' else 'stop'}),
            'parsed': parsed, 'parsing_error': None}


# 验证合法来源问答正确抽取，无可用问答时允许空结果。
async def test_extracts_qa_and_empty_result_without_inventing_sources():
    model = Model({'qas': [{'source_ref': 'conversation:1:message:11', 'question': '标准配送多少钱？', 'answer': '标准配送8元。'}]})
    result = await extraction().QAExtractor(model, 10000).extract([conversation()])
    assert result == [ExtractedQA('conversation:1:message:11', '标准配送多少钱？', '标准配送8元。')]
    assert await extraction().QAExtractor(Model(), 10000).extract([conversation()]) == []


# 验证残缺、截断、模型故障或超时均中止抽取并转为明确服务错误。
@pytest.mark.parametrize('fault', ['incomplete', 'length', RuntimeError('private provider detail'), TimeoutError()])
async def test_fails_closed_for_incomplete_truncated_or_failed_upstream(fault):
    with pytest.raises(ServiceError) as caught:
        await extraction().QAExtractor(Model(fault=fault), 10000).extract([conversation()])
    assert caught.value.code in ('invalid_structured_output', 'upstream_error', 'upstream_timeout')


# 验证模型返回的来源标识必须属于当前输入批次。
async def test_rejects_source_ref_not_in_current_input_batch():
    model = Model({'qas': [{'source_ref': 'conversation:999:message:11', 'question': '问', 'answer': '答'}]})
    with pytest.raises(ServiceError) as caught:
        await extraction().QAExtractor(model, 10000).extract([conversation()])
    assert caught.value.code == 'invalid_structured_output'


# 验证预算按完整会话拆批，单会话过长时提前拒绝而不截断原文。
async def test_budget_splits_whole_conversations_and_never_truncates_one():
    model = Model()
    await extraction().QAExtractor(model, 2500).extract([conversation(1, '甲' * 250), conversation(2, '乙' * 250)])
    assert len(model.calls) == 2
    assert '甲' * 250 in model.calls[0][-1].content
    assert '乙' * 250 in model.calls[1][-1].content
    model = Model()
    with pytest.raises(InputTooLong):
        await extraction().QAExtractor(model, 2500).extract([conversation(1, '甲' * 2000)])
    assert model.calls == []


# 验证空会话输入直接返回空列表且不发模型请求。
async def test_empty_input_does_not_invoke_model():
    model = Model()
    assert await extraction().QAExtractor(model, 10000).extract([]) == []
    assert model.calls == []


# 验证 SDK 的长度截断异常归类为结构化输出无效。
async def test_sdk_length_exception_is_invalid_output_not_generic_upstream_failure():
    from openai import LengthFinishReasonError
    from openai.types.chat import ChatCompletion
    failure = LengthFinishReasonError(completion=ChatCompletion(id='synthetic', model='synthetic', object='chat.completion', created=0, choices=[]))
    with pytest.raises(ServiceError) as caught:
        await extraction().QAExtractor(Model(fault=failure), 10000).extract([conversation()])
    assert caught.value.code == 'invalid_structured_output'


# 验证离线问答输出预算拒绝非正数、布尔值、小数与非法文本。
@pytest.mark.parametrize('invalid', [0, -1, True, 1.5, 'invalid'])
def test_offline_qa_output_budget_rejects_invalid_values(invalid):
    from pydantic import ValidationError
    from tests.fakes import fake_settings
    with pytest.raises(ValidationError):
        fake_settings(qa_max_output_tokens=invalid)


# 验证实际请求使用独立问答输出预算并保留在线设置的输出上限。
@pytest.mark.parametrize('budget', [None, '3072'])
async def test_eval_wire_uses_dedicated_output_budget_without_mutating_online_settings(monkeypatch, budget):
    from pathlib import Path
    import httpx
    import evals.evaluate_qa as evaluation
    from app.core.llm import create_model
    from tests.fakes import fake_settings
    monkeypatch.delenv('QA_MAX_OUTPUT_TOKENS', raising=False)
    if budget is not None:
        monkeypatch.setenv('QA_MAX_OUTPUT_TOKENS', budget)
    settings = fake_settings(max_output_tokens=512)
    payloads = []
    # 记录模型线上协议请求并返回合法空问答，核对预算字段与模型配置。
    def transport(request):
        payloads.append(json.loads(request.content))
        return httpx.Response(200, json={'id': 'synthetic', 'object': 'chat.completion', 'created': 0, 'model': 'synthetic',
            'choices': [{'index': 0, 'finish_reason': 'stop', 'message': {'role': 'assistant', 'content': '{"qas":[]}'}}]})
    async with httpx.AsyncClient(transport=httpx.MockTransport(transport)) as http:
        monkeypatch.setattr(evaluation, 'load_settings', lambda: settings)
        monkeypatch.setattr(evaluation, 'create_model', lambda s: create_model(s, http_async_client=http))
        result = await evaluation.evaluate(Path('evals/qa_extraction_cases.jsonl'), case_ids=['injection'])
    assert result['passed'] == 1
    assert payloads[0]['max_tokens'] == (2048 if budget is None else 3072)
    assert payloads[0]['model'] == settings.llm_model
    assert settings.max_output_tokens == 512
