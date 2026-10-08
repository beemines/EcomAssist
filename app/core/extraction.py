from typing import Any

import httpx
from langchain_core.messages import AIMessage
from openai import APITimeoutError
from pydantic import BaseModel, ValidationError

from app.core.errors import InputTooLong, ServiceError
from app.core.memory import estimate_tokens
from app.core.prompts import build_extract_messages
from app.schemas.extract import AfterSalesResult


def invalid_output() -> ServiceError:
    return ServiceError(
        "invalid_structured_output", "模型返回的结构化结果无效，请稍后重试。", 502,
    )


def validate_structured_output(output: Any, schema: type[BaseModel]) -> BaseModel:
    """Validate the untouched response as well as LangChain's parsed result."""
    if not isinstance(output, dict) or output.get("parsing_error") is not None:
        raise invalid_output()
    raw, parsed = output.get("raw"), output.get("parsed")
    if (not isinstance(raw, AIMessage) or not isinstance(parsed, schema)
            or raw.response_metadata.get("finish_reason") == "length"):
        raise invalid_output()
    # The LangChain JSON parser can repair a missing closing bracket.
    try:
        result = schema.model_validate_json(raw.text)
    except ValidationError as exc:
        raise invalid_output() from exc
    if result != parsed:
        raise invalid_output()
    return result


class ExtractionService:
    def __init__(self, model: Any, input_budget: int):
        self.structured_model = model.with_structured_output(
            AfterSalesResult, method="json_mode", include_raw=True,
        )
        self.input_budget = input_budget

    async def extract(self, text: str) -> AfterSalesResult:
        messages = build_extract_messages(text)
        if estimate_tokens(messages) > self.input_budget:
            raise InputTooLong()
        try:
            output = await self.structured_model.ainvoke(messages)
        except (TimeoutError, httpx.TimeoutException, APITimeoutError) as exc:
            raise ServiceError(
                "upstream_timeout", "模型响应超时，请稍后重试。", 504,
            ) from exc
        except Exception as exc:
            raise ServiceError(
                "upstream_error", "模型服务暂时不可用，请稍后重试。", 502,
            ) from exc

        result = validate_structured_output(output, AfterSalesResult)
        if any(
            value is not None and value not in text
            for value in (result.order_id, result.expected_solution)
        ):
            raise invalid_output()
        return result
