# 接口 Schema 测试，覆盖长度、空白、未知字段、枚举和可空输出的边界。
import pytest
from pydantic import ValidationError

from app.schemas.chat import ChatRequest
from app.schemas.extract import AfterSalesResult, ExtractRequest, RequestType


# 验证聊天请求接受最大无符号 BIGINT 会话字符串与恰好两万字符的消息。
def test_chat_request_accepts_exact_character_boundaries():
    request = ChatRequest(conversation_id="18446744073709551615", message="问" * 20000)
    assert request.conversation_id == "18446744073709551615"
    assert len(request.message) == 20000


# 验证空白或超长度的会话编号和聊天消息被拒绝。
@pytest.mark.parametrize("field,value", [
    ("conversation_id", "1" * 21), ("conversation_id", ""), ("conversation_id", " \t\n"),
    ("message", "m" * 20001), ("message", ""), ("message", " \t\n"),
])
def test_chat_request_rejects_blank_and_over_limit_fields(field, value):
    payload = {"conversation_id": "1", "message": "help"}
    payload[field] = value
    with pytest.raises(ValidationError):
        ChatRequest(**payload)


# 验证聊天请求必须同时包含会话编号与消息。
@pytest.mark.parametrize("missing", ["conversation_id", "message"])
def test_chat_request_requires_both_fields(missing):
    payload = {"conversation_id": "1", "message": "help"}
    payload.pop(missing)
    with pytest.raises(ValidationError):
        ChatRequest(**payload)


# 验证合法聊天消息的首尾空白原样保留。
def test_chat_request_preserves_valid_text():
    assert ChatRequest(conversation_id="1", message=" help ").model_dump() == {
        "conversation_id": "1", "message": " help ",
    }


# 验证抽取描述恰好达到两万字符上限时仍合法。
def test_extract_request_accepts_exact_character_boundary():
    assert len(ExtractRequest(text="问" * 20000).text) == 20000


# 验证抽取描述不能是空串、纯空白或超过字符上限。
@pytest.mark.parametrize("text", ["", " \t\n", "x" * 20001])
def test_extract_request_rejects_blank_and_over_limit_text(text):
    with pytest.raises(ValidationError):
        ExtractRequest(text=text)


# 验证抽取请求缺失 text 字段时校验失败。
def test_extract_request_requires_text():
    with pytest.raises(ValidationError):
        ExtractRequest()


# 验证值为空的订单与诉求仍在输出中保留对应键。
def test_nullable_output_keys_are_retained():
    assert AfterSalesResult(order_id=None, request_type="unknown", expected_solution=None).model_dump(mode="json") == {
        "order_id": None, "request_type": "unknown", "expected_solution": None,
    }


# 验证抽取输出即使允许空值也必须显式包含三个字段。
@pytest.mark.parametrize("missing", ["order_id", "request_type", "expected_solution"])
def test_output_requires_all_three_keys(missing):
    payload = {"order_id": None, "request_type": "unknown", "expected_solution": None}
    payload.pop(missing)
    with pytest.raises(ValidationError):
        AfterSalesResult(**payload)


# 验证各支持类别解析为枚举，并按原协议值序列化。
@pytest.mark.parametrize("request_type", ["refund", "return_refund", "exchange", "repair", "logistics", "other", "unknown"])
def test_all_supported_request_types_serialize_to_their_values(request_type):
    result = AfterSalesResult(order_id="123", request_type=request_type, expected_solution="原文短语")
    assert isinstance(result.request_type, RequestType)
    assert result.model_dump(mode="json")["request_type"] == request_type


# 验证未知、大小写错误、空串或空值请求类别被拒绝。
@pytest.mark.parametrize("request_type", ["REFUND", "cancel", "", None])
def test_output_rejects_invalid_request_types(request_type):
    with pytest.raises(ValidationError):
        AfterSalesResult(order_id=None, request_type=request_type, expected_solution=None)


# 验证可空字符串字段可以为 null，但不能使用空串或纯空白。
@pytest.mark.parametrize("field", ["order_id", "expected_solution"])
@pytest.mark.parametrize("value", ["", " \t\n"])
def test_output_rejects_blank_nullable_strings(field, value):
    payload = {"order_id": None, "request_type": "unknown", "expected_solution": None}
    payload[field] = value
    with pytest.raises(ValidationError):
        AfterSalesResult(**payload)


# 验证合法订单号和诉求短语的原始首尾空白不被裁剪。
def test_output_preserves_original_expected_solution_phrase():
    result = AfterSalesResult(order_id=" 123 ", request_type="refund", expected_solution=" 请原路退款 ")
    assert result.order_id == " 123 "
    assert result.expected_solution == " 请原路退款 "


# 验证聊天请求、抽取请求与抽取输出均拒绝额外字段。
@pytest.mark.parametrize("model,payload", [
    (ChatRequest, {"conversation_id": "1", "message": "help"}),
    (ExtractRequest, {"text": "help"}),
    (AfterSalesResult, {"order_id": None, "request_type": "unknown", "expected_solution": None}),
])
def test_schemas_reject_extra_keys(model, payload):
    with pytest.raises(ValidationError):
        model(**payload, extra="unexpected")
