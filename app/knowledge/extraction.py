# 模型抽取保留完整会话输入，输出必须满足 QA 结构且引用本批次的合法来源。
import json
from dataclasses import asdict
from typing import Any

import httpx
from openai import APITimeoutError, LengthFinishReasonError
from pydantic import BaseModel, ConfigDict, Field

from app.core.errors import InputTooLong, ServiceError
from app.core.extraction import invalid_output, validate_structured_output
from app.core.memory import estimate_tokens
from app.core.prompts import build_qa_messages
from app.knowledge.types import ConversationTranscript, ExtractedQA


class QASchema(BaseModel):
    model_config = ConfigDict(extra='forbid', strict=True, hide_input_in_errors=True)
    source_ref: str = Field(min_length=1, max_length=255)
    question: str = Field(min_length=1)
    answer: str = Field(min_length=1)


class QAResult(BaseModel):
    model_config = ConfigDict(extra='forbid', strict=True, hide_input_in_errors=True)
    qas: list[QASchema]


# 用会话 id 与最后消息 id 构造来源标识，供模型回包和后续溯源核验。
def source_ref(conversation: ConversationTranscript) -> str:
    return f'conversation:{conversation.id}:message:{conversation.last_message_id}'


# 序列化各会话的全部消息及来源标识，构造 QA 抽取提示输入。
def _messages(conversations):
    payload = [{'source_ref': source_ref(c), 'messages': [asdict(m) for m in c.messages]} for c in conversations]
    return build_qa_messages(json.dumps(payload, ensure_ascii=False, separators=(',', ':')))


class QAExtractor:
    # 校验输入预算并配置严格 QA 结构的模型输出，同时保留原始回包供统一校验。
    def __init__(self, model: Any, input_budget: int):
        if type(input_budget) is not int or input_budget < 1:
            raise ValueError('input budget must be positive')
        self.structured_model = model.with_structured_output(QAResult, method='json_mode', include_raw=True)
        self.input_budget = input_budget

    # 先按完整会话校验和分批，再抽取 QA；检查结构、批内来源及非空问答后返回结果。
    async def extract(self, conversations: list[ConversationTranscript]) -> list[ExtractedQA]:
        # 先检查所有会话的完整提示输入；任一单会话超预算就失败，不截断历史来凑预算。
        batches, batch = [], []
        for conversation in conversations:
            if estimate_tokens(_messages([conversation])) > self.input_budget:
                raise InputTooLong()
            if batch and estimate_tokens(_messages([*batch, conversation])) > self.input_budget:
                batches.append(batch)
                batch = []
            batch.append(conversation)
        if batch:
            batches.append(batch)
        results = []
        for batch in batches:
            try:
                output = await self.structured_model.ainvoke(_messages(batch))
            except LengthFinishReasonError as exc:
                raise invalid_output() from exc
            except (TimeoutError, httpx.TimeoutException, APITimeoutError) as exc:
                raise ServiceError('upstream_timeout', '模型响应超时，请稍后重试。', 504) from exc
            except Exception as exc:
                raise ServiceError('upstream_error', '模型服务暂时不可用，请稍后重试。', 502) from exc
            parsed = validate_structured_output(output, QAResult)
            # 仅允许引用当前批次来源，空白问答或超出存储限制的结果统一视为模型输出无效。
            allowed = {source_ref(c) for c in batch}
            for qa in parsed.qas:
                if qa.source_ref not in allowed or not qa.question.strip() or not qa.answer.strip():
                    raise invalid_output()
                try:
                    results.append(ExtractedQA(qa.source_ref, qa.question, qa.answer))
                except ValueError as exc:
                    raise invalid_output() from exc
        return results
