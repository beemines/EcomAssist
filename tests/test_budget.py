import pytest
from langchain_core.messages import AIMessage, BaseMessage, HumanMessage, SystemMessage


# 按消息内容的 UTF-8 字节数计费，让预算边界测试可精确预测。
def text_counter(messages: list[BaseMessage]) -> int:
    return sum(len(m.content.encode("utf-8")) for m in messages)


# 验证估算包含中文和表情字节及每条消息的固定开销。
def test_estimate_counts_utf8_bytes_and_per_message_overhead():
    from app.core.memory import estimate_tokens

    assert estimate_tokens([]) == 0
    assert estimate_tokens([HumanMessage("中🙂"), AIMessage("a")]) == 32
    assert estimate_tokens([HumanMessage("")]) == 12


# 验证系统与当前用户消息恰好满足预算时通过，预算少一单位时返回输入超限。
@pytest.mark.parametrize("system,current,budget", [("s", "q", 2), ("中", "🙂", 7)])
def test_required_messages_fit_exact_budget_and_fail_one_below(system, current, budget):
    from app.core.errors import InputTooLong
    from app.core.memory import prepare_messages

    prepared = prepare_messages(system, [], current, budget, counter=text_counter)
    assert [(m.type, m.content) for m in prepared] == [("system", system), ("human", current)]
    with pytest.raises(InputTooLong) as caught:
        prepare_messages(system, [], current, budget - 1, counter=text_counter)
    assert caught.value.status_code == 422
    assert caught.value.code == "input_too_long"


# 验证裁剪优先保留最近完整轮次与当前原文，并且不修改调用方历史。
@pytest.mark.parametrize("budget,expected", [
    (19, ["s", "old", "reply", "new", "answer", "q"]),
    (11, ["s", "new", "answer", "q"]),
    (8, ["s", "q"]),
    (2, ["s", "q"]),
])
def test_trimming_keeps_recent_whole_turns_and_current_original(budget, expected):
    from app.core.memory import prepare_messages

    history = [HumanMessage("old"), AIMessage("reply"), HumanMessage("new"), AIMessage("answer")]
    prepared = prepare_messages("s", history, "q", budget, counter=text_counter)
    assert [m.content for m in prepared] == expected
    assert text_counter(prepared) <= budget
    assert [m.type for m in prepared[1:-1]] == ["human", "ai"] * ((len(prepared) - 2) // 2)
    assert [m.content for m in history] == ["old", "reply", "new", "answer"]


# 验证默认估算裁剪历史时保留当前中文、表情与空白内容。
def test_default_estimator_preserves_chinese_emoji_and_whitespace():
    from app.core.memory import estimate_tokens, prepare_messages

    history = [HumanMessage("旧问题"), AIMessage("旧回答")]
    prepared = prepare_messages("中", history, " 🙂 ", 33)
    assert [(m.type, m.content) for m in prepared] == [("system", "中"), ("human", " 🙂 ")]
    assert estimate_tokens(prepared) == 33


# 验证孤立或不完整轮次及错误角色历史被拒绝，原历史仍保持不变。
@pytest.mark.parametrize("history", [[AIMessage("orphan")], [HumanMessage("half")], [SystemMessage("bad"), AIMessage("bad")]])
def test_budget_rejects_invalid_history_without_mutating_it(history):
    from app.core.memory import prepare_messages

    original = [(m.type, m.content) for m in history]
    with pytest.raises(ValueError):
        prepare_messages("s", history, "q", 100, counter=text_counter)
    assert [(m.type, m.content) for m in history] == original
