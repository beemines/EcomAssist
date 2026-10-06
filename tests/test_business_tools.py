import pytest

from app.tools.executor import ToolExecutor
from app.tools.registry import build_registry
from app.tools.types import ToolCall, ToolContext


class FAQStub:
    def __init__(self, matches=None):
        self.matches = matches or []
        self.keywords = []

    async def search(self, keyword, limit=3):
        self.keywords.append(keyword)
        return self.matches


class TicketStub:
    def __init__(self):
        self.inputs = []

    async def create(self, **kwargs):
        self.inputs.append(kwargs)
        return {"ticket_no": "T123", "status": "待处理"}


@pytest.mark.asyncio
async def test_registry_hides_context_and_injects_actual_call_id():
    tickets = TicketStub()
    registry = build_registry(FAQStub(), tickets, ToolContext("10", 42, "请转人工"))
    assert set(registry) == {"query_order", "query_product", "query_logistics", "query_faq", "create_ticket"}
    properties = registry["create_ticket"].tool_call_schema.model_json_schema()["properties"]
    assert set(properties) == {"description", "ticket_type"}
    outcome = await ToolExecutor().execute(ToolCall("call-1", "create_ticket", {"description": "订单损坏", "ticket_type": "售后"}), registry)
    assert outcome.content == {"ticket_no": "T123", "status": "待处理"}
    assert outcome.status == "success"
    assert tickets.inputs == [{"conversation_id": "10", "user_message_id": 42, "tool_call_id": "call-1", "description": "订单损坏", "ticket_type": "售后"}]


@pytest.mark.asyncio
@pytest.mark.parametrize("name,args", [("query_order", {"order_id": "001"}), ("query_product", {"product_id": "p1"}), ("query_logistics", {"order_id": "o1"})])
async def test_mock_tools_preserve_identifiers_and_mark_demo_data(name, args):
    registry = build_registry(FAQStub(), TicketStub(), ToolContext("10", 42, "查询"))
    outcome = await ToolExecutor().execute(ToolCall("call", name, args), registry)
    assert outcome.status == "success"
    assert outcome.content.items() >= args.items()
    assert outcome.content["mock"] is True
    assert len(outcome.content) > 2


@pytest.mark.asyncio
async def test_faq_requires_literal_question_fragment_and_empty_match_is_success():
    faq = FAQStub()
    registry = build_registry(faq, TicketStub(), ToolContext("10", 42, "邮费是多少"))
    rejected = await ToolExecutor().execute(ToolCall("bad", "query_faq", {"keyword": "运费"}), registry)
    assert rejected.status == "error"
    assert rejected.content["error"]["code"] == "invalid_keyword"
    assert faq.keywords == []
    missing = await ToolExecutor().execute(ToolCall("ok", "query_faq", {"keyword": "邮费"}), registry)
    assert missing.status == "success" and missing.content == {"found": False, "matches": []}
    assert faq.keywords == ["邮费"]


@pytest.mark.asyncio
async def test_faq_matches_return_question_answer_category():
    rows = [{"id": 1, "question": "退货政策", "answer": "七天", "category": "售后"}]
    registry = build_registry(FAQStub(rows), TicketStub(), ToolContext("10", 42, "退货政策是什么"))
    outcome = await ToolExecutor().execute(ToolCall("ok", "query_faq", {"keyword": "退货"}), registry)
    assert outcome.content == {"found": True, "matches": rows}


@pytest.mark.asyncio
@pytest.mark.parametrize("name,args", [
    ("query_order", {"order_id": ""}), ("query_order", {"order_id": "a" * 65}),
    ("query_product", {"product_id": 1}), ("query_logistics", {"order_id": "x", "extra": 1}),
    ("query_faq", {"keyword": "x" * 129}), ("create_ticket", {"description": "", "ticket_type": "售后"}),
    ("create_ticket", {"description": "x" * 2001, "ticket_type": "咨询"}),
    ("create_ticket", {"description": "x", "ticket_type": "退款"}),
    ("create_ticket", {"description": "x", "ticket_type": "咨询", "tool_call_id": "forged"}),
    ("create_ticket", {"description": "x", "ticket_type": "咨询", "conversation_id": "20"}),
])
async def test_business_arguments_reject_bad_lengths_types_and_extra_fields(name, args):
    tickets = TicketStub()
    registry = build_registry(FAQStub(), tickets, ToolContext("10", 42, "x"))
    outcome = await ToolExecutor().execute(ToolCall("call", name, args), registry)
    assert outcome.status == "error" and outcome.attempts == 0
    assert outcome.content["error"]["code"] == "invalid_arguments"
    assert tickets.inputs == []
