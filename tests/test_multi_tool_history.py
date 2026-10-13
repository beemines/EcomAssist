# 多步历史回放测试：保护严格顺序、全轮唯一标识及整轮预算裁剪。
from dataclasses import replace

import pytest
from langchain_core.messages import AIMessage, HumanMessage, SystemMessage, ToolMessage

from app.core.errors import InputTooLong
from app.core.tool_history import build_tool_messages, completed_turns
from app.repositories.records import MessageRecord, record_from_message
from tests.tool_fakes import selected_call


# 构造两步或四步真实消息，参数和结果均经过应用转换器。
def multi_turn(steps=2, *, content="question", result_size=1):
    messages = [HumanMessage(content)]
    for index in range(1, steps + 1):
        identifier = f"call_{index}"
        messages.extend([
            selected_call("query_order", {"order_id": f"order_{index}"}, identifier=identifier),
            ToolMessage("r" * result_size, tool_call_id=identifier),
        ])
    return [*messages, AIMessage("answer")]


# 按持久化协议创建主键递增记录，独立验证回放消费端。
def rows_from(messages):
    return [record_from_message(message, identifier=index) for index, message in enumerate(messages, 1)]


# 捕获第二组结果后的历史截断，并核对恢复顺序、参数和调用标识。
@pytest.mark.parametrize("steps,types,ids", [
    (2, ["human", "ai", "tool", "ai", "tool", "ai"], ["call_1", "call_2"]),
    (4, ["human", "ai", "tool", "ai", "tool", "ai", "tool", "ai", "tool", "ai"],
     ["call_1", "call_2", "call_3", "call_4"]),
])
def test_replay_complete_multi_tool_turn(steps, types, ids):
    turns = completed_turns(list(reversed(rows_from(multi_turn(steps)))))
    assert len(turns) == 1
    assert [message.type for message in turns[0]] == types
    assert [message.tool_call_id for message in turns[0] if isinstance(message, ToolMessage)] == ids
    assert turns[0][3].tool_calls[0]["args"] == {"order_id": "order_2"}


# 捕获第二组错配、重复标识、非法参数、角色、缺结果及并发申请被接受的漏洞。
@pytest.mark.parametrize("damage", ["wrong_id", "duplicate_id", "json", "role", "missing_result", "parallel", "missing_final"])
def test_invalid_multi_tool_turn_stops_until_next_user(damage):
    rows = rows_from(multi_turn())
    if damage == "wrong_id":
        rows[4] = replace(rows[4], tool_call_id="wrong")
    elif damage == "duplicate_id":
        calls = [{**rows[3].tool_calls[0], "id": "call_1"}]
        rows[3] = replace(rows[3], tool_calls=calls)
        rows[4] = replace(rows[4], tool_call_id="call_1")
    elif damage == "json":
        call = rows[3].tool_calls[0]
        rows[3] = replace(rows[3], tool_calls=[{**call, "function": {**call["function"], "arguments": "{broken"}}])
    elif damage == "role":
        rows[3] = MessageRecord(4, "system", "invalid", None, None)
    elif damage == "missing_result":
        del rows[2]
    elif damage == "parallel":
        rows[3] = replace(rows[3], tool_calls=rows[3].tool_calls * 2)
    else:
        rows.pop()
    assert completed_turns(rows) == []
    later = [MessageRecord(20, "user", "later", None, None), MessageRecord(21, "assistant", "ok", None, None)]
    turns = completed_turns([*rows, *later])
    assert [[message.content for message in turn] for turn in turns] == [["later", "ok"]]


# 捕获预算裁掉部分多步轮次或误删当前必需工具交互的问题。
def test_budget_drops_old_multi_tool_turn_and_preserves_current_pairs():
    old = multi_turn(4, content="old turn", result_size=1000)
    recent = [HumanMessage("recent"), AIMessage("ok")]
    pending = multi_turn()[1:-1]
    result = build_tool_messages(SystemMessage("s"), [old, recent], HumanMessage("q"), 1000,
                                 tool_schema=[], current_tool_messages=pending)
    assert all(message.content != "old turn" for message in result)
    assert [message.type for message in result] == ["system", "human", "ai", "human", "ai", "tool", "ai", "tool"]
    assert [message.tool_call_id for message in result if isinstance(message, ToolMessage)] == ["call_1", "call_2"]
    assert [message.content for message in result[1:4]] == ["recent", "ok", "q"]


# 捕获忽略后续工具结果预算的错误，必需数据超限必须拒绝而非裁断。
def test_current_multi_tool_results_over_budget_are_rejected():
    pending = multi_turn()[1:-1]
    pending[-1] = ToolMessage("中" * 3000, tool_call_id="call_2")
    with pytest.raises(InputTooLong):
        build_tool_messages(SystemMessage("s"), [], HumanMessage("q"), 8000,
                            tool_schema=[], current_tool_messages=pending)


# 捕获当前交互校验绕过全轮唯一标识或相邻配对约束的问题。
@pytest.mark.parametrize("damage", ["duplicate", "wrong_id", "missing_result", "final"])
def test_invalid_current_multi_tool_pairs_are_rejected(damage):
    pending = multi_turn()[1:-1]
    if damage == "duplicate":
        pending[2] = selected_call(identifier="call_1")
        pending[3] = ToolMessage("duplicate", tool_call_id="call_1")
    elif damage == "wrong_id":
        pending[3] = ToolMessage("wrong", tool_call_id="call_1")
    elif damage == "missing_result":
        pending.pop()
    else:
        pending.append(AIMessage("answer"))
    with pytest.raises(ValueError):
        build_tool_messages(SystemMessage("s"), [], HumanMessage("q"), 8000,
                            tool_schema=[], current_tool_messages=pending)
