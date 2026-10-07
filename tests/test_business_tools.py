import pytest

from app.tools.executor import ToolExecutor
from app.repositories.tickets import TicketRepository
from app.tools.registry import build_registry
from app.tools.types import ToolCall, ToolContext
from tests.fakes import FAQStub


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
@pytest.mark.parametrize("name,args", [
    ("query_order", {"order_id": "001"}), ("query_product", {"product_id": "p1"}), ("query_logistics", {"order_id": "o1"}),
    ("query_order", {"order_id": " \t001\n"}), ("query_product", {"product_id": "\u3000p1 "}), ("query_logistics", {"order_id": " o1\t"}),
])
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
    ("query_faq", {"keyword": 1}), ("query_faq", {"keyword": True}),
    ("query_faq", {"keyword": "x", "limit": 10}),
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


@pytest.mark.asyncio
@pytest.mark.parametrize("blank", ["   ", "\t", "\n", "\u3000\u00a0"])
@pytest.mark.parametrize("name,field", [
    ("query_order", "order_id"), ("query_product", "product_id"),
    ("query_logistics", "order_id"), ("query_faq", "keyword"),
    ("create_ticket", "description"),
])
async def test_blank_business_text_is_rejected_before_any_execution(blank, name, field, monkeypatch):
    faq, tickets = FAQStub(), TicketStub()
    registry = build_registry(faq, tickets, ToolContext("10", 42, "问题" + blank + "详情"))
    invocations = []
    original_invoke = type(registry[name]).ainvoke

    async def record_invoke(tool, *args, **kwargs):
        invocations.append(tool.name)
        return await original_invoke(tool, *args, **kwargs)

    monkeypatch.setattr(type(registry[name]), "ainvoke", record_invoke)
    args = {field: blank}
    if name == "create_ticket":
        args["ticket_type"] = "咨询"
    outcome = await ToolExecutor().execute(ToolCall("call", name, args), registry)
    assert outcome.status == "error" and outcome.content["error"]["code"] == "invalid_arguments"
    assert outcome.attempts == 0
    assert invocations == [] and faq.keywords == [] and tickets.inputs == []


@pytest.mark.asyncio
@pytest.mark.parametrize("description", ["   ", "\t", "\n", "\u3000\u00a0"])
async def test_direct_blank_ticket_description_is_rejected_before_database_access(description):
    class NoDatabaseAccess:
        def session(self):
            raise AssertionError("空白描述不得打开数据库会话")

    with pytest.raises(ValueError, match="Invalid ticket arguments"):
        await TicketRepository(NoDatabaseAccess()).create(
            conversation_id="10", user_message_id=42, tool_call_id="call",
            description=description, ticket_type="咨询",
        )


@pytest.mark.asyncio
async def test_nonblank_faq_and_ticket_text_preserve_surrounding_whitespace():
    faq, tickets = FAQStub(), TicketStub()
    registry = build_registry(faq, tickets, ToolContext("10", 42, "请问 \t退货\n 政策"))
    faq_outcome = await ToolExecutor().execute(ToolCall("faq", "query_faq", {"keyword": " \t退货\n "}), registry)
    ticket_outcome = await ToolExecutor().execute(ToolCall("ticket", "create_ticket", {"description": "\u3000损坏\t\n", "ticket_type": "售后"}), registry)
    assert faq_outcome.status == "success" and faq_outcome.attempts == 1
    assert faq.keywords == [" \t退货\n "]
    assert ticket_outcome.status == "success" and ticket_outcome.attempts == 1
    assert tickets.inputs == [{"conversation_id": "10", "user_message_id": 42, "tool_call_id": "ticket", "description": "\u3000损坏\t\n", "ticket_type": "售后"}]


@pytest.mark.asyncio
async def test_surrounding_whitespace_cannot_turn_keyword_into_a_question_fragment():
    faq = FAQStub()
    registry = build_registry(faq, TicketStub(), ToolContext("10", 42, "退货政策是什么"))
    outcome = await ToolExecutor().execute(ToolCall("faq", "query_faq", {"keyword": " 退货 "}), registry)
    assert outcome.status == "error" and outcome.content["error"]["code"] == "invalid_keyword"
    assert faq.keywords == []
