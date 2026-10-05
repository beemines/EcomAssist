import pytest
from pydantic import ValidationError

from app.schemas.chat import ChatRequest
from app.schemas.extract import AfterSalesResult, ExtractRequest, RequestType


def test_chat_request_accepts_exact_character_boundaries():
    request = ChatRequest(session_id="会" * 128, message="问" * 20000)
    assert len(request.session_id) == 128
    assert len(request.message) == 20000


@pytest.mark.parametrize("field,value", [
    ("session_id", "s" * 129), ("session_id", ""), ("session_id", " \t\n"),
    ("message", "m" * 20001), ("message", ""), ("message", " \t\n"),
])
def test_chat_request_rejects_blank_and_over_limit_fields(field, value):
    payload = {"session_id": "s", "message": "help"}
    payload[field] = value
    with pytest.raises(ValidationError):
        ChatRequest(**payload)


@pytest.mark.parametrize("missing", ["session_id", "message"])
def test_chat_request_requires_both_fields(missing):
    payload = {"session_id": "s", "message": "help"}
    payload.pop(missing)
    with pytest.raises(ValidationError):
        ChatRequest(**payload)


def test_chat_request_preserves_valid_text():
    assert ChatRequest(session_id=" s ", message=" help ").model_dump() == {
        "session_id": " s ", "message": " help ",
    }


def test_extract_request_accepts_exact_character_boundary():
    assert len(ExtractRequest(text="问" * 20000).text) == 20000


@pytest.mark.parametrize("text", ["", " \t\n", "x" * 20001])
def test_extract_request_rejects_blank_and_over_limit_text(text):
    with pytest.raises(ValidationError):
        ExtractRequest(text=text)


def test_extract_request_requires_text():
    with pytest.raises(ValidationError):
        ExtractRequest()


def test_nullable_output_keys_are_retained():
    assert AfterSalesResult(order_id=None, request_type="unknown", expected_solution=None).model_dump(mode="json") == {
        "order_id": None, "request_type": "unknown", "expected_solution": None,
    }


@pytest.mark.parametrize("missing", ["order_id", "request_type", "expected_solution"])
def test_output_requires_all_three_keys(missing):
    payload = {"order_id": None, "request_type": "unknown", "expected_solution": None}
    payload.pop(missing)
    with pytest.raises(ValidationError):
        AfterSalesResult(**payload)


@pytest.mark.parametrize("request_type", ["refund", "return_refund", "exchange", "repair", "logistics", "other", "unknown"])
def test_all_supported_request_types_serialize_to_their_values(request_type):
    result = AfterSalesResult(order_id="123", request_type=request_type, expected_solution="原文短语")
    assert isinstance(result.request_type, RequestType)
    assert result.model_dump(mode="json")["request_type"] == request_type


@pytest.mark.parametrize("request_type", ["REFUND", "cancel", "", None])
def test_output_rejects_invalid_request_types(request_type):
    with pytest.raises(ValidationError):
        AfterSalesResult(order_id=None, request_type=request_type, expected_solution=None)


@pytest.mark.parametrize("field", ["order_id", "expected_solution"])
@pytest.mark.parametrize("value", ["", " \t\n"])
def test_output_rejects_blank_nullable_strings(field, value):
    payload = {"order_id": None, "request_type": "unknown", "expected_solution": None}
    payload[field] = value
    with pytest.raises(ValidationError):
        AfterSalesResult(**payload)


def test_output_preserves_original_expected_solution_phrase():
    result = AfterSalesResult(order_id=" 123 ", request_type="refund", expected_solution=" 请原路退款 ")
    assert result.order_id == " 123 "
    assert result.expected_solution == " 请原路退款 "


@pytest.mark.parametrize("model,payload", [
    (ChatRequest, {"session_id": "s", "message": "help"}),
    (ExtractRequest, {"text": "help"}),
    (AfterSalesResult, {"order_id": None, "request_type": "unknown", "expected_solution": None}),
])
def test_schemas_reject_extra_keys(model, payload):
    with pytest.raises(ValidationError):
        model(**payload, extra="unexpected")
