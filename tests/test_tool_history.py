# 工具历史回放与预算测试，覆盖孤立流水、完整工具轮次、参数格式及会话凭证。
import json

import pytest
from langchain_core.messages import AIMessage, HumanMessage, SystemMessage, ToolMessage


# 把角色、内容及工具关联规格转换为递增主键的审计记录。
def records(spec):
    from app.repositories.records import MessageRecord

    return [MessageRecord(i, role, content, calls, call_id) for i, (role, content, calls, call_id) in enumerate(spec, 1)]


CALL = [{"id": "call-1", "type": "function", "function": {"name": "search_faq", "arguments": '{"keyword":"退货"}'}}]
GOOD = [("user", "如何退货", None, None), ("assistant", None, CALL, None), ("tool", "退货规则", None, "call-1"), ("assistant", "请按照规则退货", None, None)]
TEXT = [("user", "谢谢", None, None), ("assistant", "不客气", None, None)]


# 验证完整工具轮次可回放，孤立结果和半轮不污染后续普通完整轮次。
def test_complete_turns_skip_partial_and_orphan():
    from app.core.tool_history import completed_turns

    rows = records(GOOD + [("tool", "孤立结果", None, "orphan"), ("user", "半轮次", None, None), ("assistant", None, CALL, None)] + TEXT)
    # 独立孤立结果不污染已经结束的轮次。
    turns = completed_turns(rows)
    assert len(turns) == 2
    turn = turns[0]
    assert [m.type for m in turn] == ["human", "ai", "tool", "ai"]
    assert turn[2].tool_call_id == turn[1].tool_calls[0]['id']
    assert turn[1].tool_calls[0]["args"] == {"keyword": "退货"}
    assert turns[1][1].content == "不客气"


# 验证参数损坏、关联错误、重复结果、角色或长度非法的轮次被跳过，后续合法轮次仍保留。
@pytest.mark.parametrize("bad", [
    [("user", "q", None, None)],
    GOOD[:-1],
    [("user", "q", None, None), ("assistant", "", None, None)],
    [GOOD[0], ("assistant", None, [{"id": "call-1", "type": "function", "function": {"name": "search_faq", "arguments": "{broken"}}], None), *GOOD[2:]],
    [GOOD[0], ("assistant", None, [{"id": "call-1", "type": "function", "function": {"name": "search_faq", "arguments": "[]"}}], None), *GOOD[2:]],
    [*GOOD[:2], ("tool", "规则", None, "wrong-id"), GOOD[3]],
    [*GOOD[:3], GOOD[2], GOOD[3]],
    [GOOD[0], ("assistant", None, CALL * 2, None), *GOOD[2:]],
    [("user", "x" * 20001, None, None), GOOD[3]],
    [GOOD[0], ("assistant", "x" * 20001, None, None)],
    [("user", "q", None, "unexpected"), GOOD[3]],
    [GOOD[0], ("tool", "orphan", None, "call-1"), GOOD[3]],
    [GOOD[0], ("system", "invalid", None, None), GOOD[3]],
    [GOOD[0], ("assistant", None, {"bad": "shape"}, None), *GOOD[2:]],
])
def test_invalid_turn_is_skipped_and_later_text_turn_survives(bad):
    from app.core.tool_history import completed_turns

    turns = completed_turns(records(bad + TEXT))
    assert len(turns) == 1
    assert [m.content for m in turns[0]] == ["谢谢", "不客气"]


# 验证回放按记录主键排序，并且修改恢复消息不会改变原工具 JSON。
def test_replay_orders_records_by_id_and_does_not_mutate_json():
    from app.core.tool_history import completed_turns

    rows = records(GOOD)
    original = json.dumps(rows[1].tool_calls, ensure_ascii=False)
    turn = completed_turns(list(reversed(rows)))[0]
    turn[1].tool_calls[0]["args"]["keyword"] = "改动"
    assert json.dumps(rows[1].tool_calls, ensure_ascii=False) == original


# 构造完整工具轮次，并可放大参数与结果以制造预算边界。
def tool_turn(size=10):
    return [HumanMessage("old"), AIMessage("", tool_calls=[{"id": "call-1", "name": "search_faq", "args": {"keyword": "x" * size}, "type": "tool_call"}]), ToolMessage("y" * size, tool_call_id="call-1"), AIMessage("answer")]


# 验证预算不足时整轮删除旧工具交互，保留最近普通轮次与原当前消息。
def test_budget_drops_whole_tool_turn():
    from app.core.tool_history import build_tool_messages

    system, current = SystemMessage("s"), HumanMessage("q")
    old, recent = tool_turn(300), [HumanMessage("new"), AIMessage("ok")]
    messages = build_tool_messages(system, [old, recent], current, 100, tool_schema=[])
    assert [m.content for m in messages] == ["s", "new", "ok", "q"]
    assert messages[0] is system and messages[-1] is current
    assert len(old) == 4


# 验证工具结构、调用参数、结果、当前输入及系统提示均计入预算。
@pytest.mark.parametrize("where", ["schema", "arguments", "result", "current", "system"])
def test_schema_and_result_count_toward_budget(where):
    from app.core.errors import InputTooLong
    from app.core.tool_history import build_tool_messages

    system = SystemMessage("s" if where != "system" else "中" * 3000)
    current = HumanMessage("q" if where != "current" else "中" * 3000)
    schema = [{"description": "中" * 3000}] if where == "schema" else []
    pending = tool_turn(9000)[1:3] if where == "arguments" else tool_turn(1)[1:3]
    if where == "arguments":
        pending[1] = ToolMessage("ok", tool_call_id="call-1")
    if where == "result":
        pending[1] = ToolMessage("中" * 3000, tool_call_id="call-1")
    with pytest.raises(InputTooLong):
        build_tool_messages(system, [], current, 8000, tool_schema=schema, current_tool_messages=pending)


# 验证空工具结构的序列化开销也计入精确预算，少一字节便拒绝。
def test_budget_counts_serialized_schema_and_calls_at_exact_boundary():
    from app.core.errors import InputTooLong
    from app.core.tool_history import build_tool_messages

    # 纯文本 s/q 为 26 字节；空 schema JSON [] 为 2 字节。
    assert len(build_tool_messages(SystemMessage("s"), [], HumanMessage("q"), 28, tool_schema=[])) == 2
    with pytest.raises(InputTooLong):
        build_tool_messages(SystemMessage("s"), [], HumanMessage("q"), 27, tool_schema=[])


# 验证裁剪旧历史时完整保留当前工具调用与匹配结果。
def test_current_tool_exchange_is_preserved_while_history_is_trimmed():
    from app.core.tool_history import build_tool_messages

    pending = tool_turn(1)[1:3]
    messages = build_tool_messages(SystemMessage("s"), [tool_turn(300)], HumanMessage("q"), 500, tool_schema=[], current_tool_messages=pending)
    assert [m.type for m in messages] == ["system", "human", "ai", "tool"]
    assert messages[-1].tool_call_id == messages[-2].tool_calls[0]["id"]


# 验证预算构造入口拒绝半轮、孤立助手或系统角色等不合法历史。
@pytest.mark.parametrize("turn", [[HumanMessage("partial")], [AIMessage("orphan")], [SystemMessage("bad"), AIMessage("reply")]])
def test_budget_rejects_invalid_history(turn):
    from app.core.tool_history import build_tool_messages

    with pytest.raises(ValueError):
        build_tool_messages(SystemMessage("s"), [turn], HumanMessage("q"), 8000, tool_schema=[])


# 验证当前工具交互缺结果、编号错配或结果重复时不能构造模型输入。
@pytest.mark.parametrize("pending", [
    [AIMessage("", tool_calls=[{"id": "call-1", "name": "search_faq", "args": {}, "type": "tool_call"}])],
    [*tool_turn(1)[1:2], ToolMessage("wrong", tool_call_id="wrong")],
    [*tool_turn(1)[1:3], ToolMessage("duplicate", tool_call_id="call-1")],
])
def test_budget_rejects_unmatched_current_tool_exchange(pending):
    from app.core.tool_history import build_tool_messages

    with pytest.raises(ValueError):
        build_tool_messages(SystemMessage("s"), [], HumanMessage("q"), 8000, tool_schema=[], current_tool_messages=pending)


# 验证同会话互斥、不同会话独立，旧租约释放不能解开新租约。
def test_locks_are_exclusive_and_old_release_cannot_unlock_new_lease():
    from app.core.conversation_locks import ConversationLocks
    from app.core.errors import SessionBusy

    locks = ConversationLocks()
    first = locks.acquire("1")
    independent = locks.acquire("2")
    with pytest.raises(SessionBusy):
        locks.acquire("1")
    first.release()
    second = locks.acquire("1")
    first.release()
    with pytest.raises(SessionBusy):
        locks.acquire("1")
    second.release()
    independent.release()
    locks.acquire("1").release()


# 验证非法、非规范或越界会话编号在真实仓储数据库访问前统一拒绝。
@pytest.mark.parametrize("identifier", ["", "0", "01", "-1", "+1", "1.0", " 1", "1 ", "1\n", "１", "abc", "18446744073709551616", 1, 1.0, True, None])
@pytest.mark.asyncio
async def test_repository_rejects_invalid_identifiers_before_database(identifier):
    from app.core.errors import ServiceError
    from app.repositories.conversations import ConversationRepository

    repository = ConversationRepository(None)
    for operation in (repository.require_open, repository.load_messages):
        with pytest.raises(ServiceError) as caught:
            await operation(identifier)
        assert caught.value.code == "invalid_conversation_id"
        assert caught.value.status_code == 422
    with pytest.raises(ServiceError):
        await repository.append_message(identifier, HumanMessage("q"))


# 验证错误角色、超长或块状文本、孤立结果及非法调用在落库前拒绝。
@pytest.mark.parametrize("message", [SystemMessage("bad"), HumanMessage("x" * 20001), HumanMessage([{"type": "text", "text": "bad"}]), ToolMessage("orphan", tool_call_id=""), AIMessage("", invalid_tool_calls=[{"name": "search_faq", "args": "broken", "id": "x", "error": "broken", "type": "invalid_tool_call"}])])
@pytest.mark.asyncio
async def test_repository_rejects_invalid_messages_before_database(message):
    from app.repositories.conversations import ConversationRepository

    with pytest.raises(ValueError):
        await ConversationRepository(None).append_message("1", message)


# 验证空白、超长或非字符串用户标识在创建数据库会话前被拒绝。
@pytest.mark.parametrize("user_id", ["", "  ", "x" * 65, None, 1])
@pytest.mark.asyncio
async def test_create_rejects_invalid_user_identifier_before_database(user_id):
    from app.repositories.conversations import ConversationRepository

    with pytest.raises(ValueError):
        await ConversationRepository(None).create(user_id)
