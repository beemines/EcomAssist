# 内存会话测试，检查并发占用、不可变快照、完整轮次提交及过期凭证的隔离。
from dataclasses import FrozenInstanceError

import pytest
from langchain_core.messages import AIMessage, HumanMessage, SystemMessage


# 验证不同会话的已完成轮次相互隔离，新会话历史为空。
def test_sessions_keep_independent_completed_turns():
    from app.core.memory import SessionStore

    store = SessionStore()
    first = store.acquire("first")
    second = store.acquire("second")
    store.commit(first, [HumanMessage("问"), AIMessage("答")])
    assert [m.content for m in store.snapshot("first")] == ["问", "答"]
    assert second.history == ()
    assert store.snapshot("second") == ()


# 验证同一会话租约未释放时返回忙碌错误，释放后可重新取得。
def test_same_session_is_busy_until_release():
    from app.core.errors import SessionBusy
    from app.core.memory import SessionStore

    store = SessionStore()
    lease = store.acquire("session")
    with pytest.raises(SessionBusy) as caught:
        store.acquire("session")
    assert caught.value.status_code == 409
    assert caught.value.code == "session_busy"
    store.release(lease)
    assert store.acquire("session").history == ()


# 验证未提交就释放的新轮次不会覆盖之前的完整历史。
def test_release_without_commit_preserves_previous_history():
    from app.core.memory import SessionStore

    store = SessionStore()
    lease = store.acquire("session")
    store.commit(lease, [HumanMessage("one"), AIMessage("answer")])
    store.release(lease)
    abandoned = store.acquire("session")
    store.release(abandoned)
    assert [m.content for m in store.snapshot("session")] == ["one", "answer"]


# 验证提交可以用裁剪后的完整轮次加新轮次替换历史。
def test_commit_replaces_history_with_retained_completed_turns():
    from app.core.memory import SessionStore

    store = SessionStore()
    lease = store.acquire("session")
    store.commit(lease, [HumanMessage("old"), AIMessage("0"), HumanMessage("one"), AIMessage("1")])
    store.release(lease)
    next_lease = store.acquire("session")
    store.commit(next_lease, [*next_lease.history[2:], HumanMessage("two"), AIMessage("2")])
    assert [m.content for m in store.snapshot("session")] == ["one", "1", "two", "2"]


# 验证输入消息、租约历史与快照均隔离拷贝，租约身份也不可修改。
def test_lease_and_snapshots_cannot_change_stored_history():
    from app.core.memory import SessionStore

    store = SessionStore()
    lease = store.acquire("session")
    messages = [HumanMessage("question"), AIMessage("answer")]
    store.commit(lease, messages)
    messages[0].content = "changed input"
    store.release(lease)
    current = store.acquire("session")
    assert isinstance(current.history, tuple)
    with pytest.raises(FrozenInstanceError):
        current.session_id = "other"
    current.history[0].content = "changed lease copy"
    snapshot = store.snapshot("session")
    snapshot[1].content = "changed snapshot copy"
    assert [m.content for m in store.snapshot("session")] == ["question", "answer"]


# 验证旧租约重复释放幂等，且不能误释放同会话的新租约。
def test_old_release_is_idempotent_and_cannot_release_new_lease():
    from app.core.errors import SessionBusy
    from app.core.memory import SessionStore

    store = SessionStore()
    old = store.acquire("session")
    store.release(old)
    current = store.acquire("session")
    store.release(old)
    store.release(old)
    with pytest.raises(SessionBusy):
        store.acquire("session")
    store.release(current)
    store.acquire("session")


# 验证过期或其他存储实例的租约不能提交并改变历史。
def test_stale_and_foreign_commits_cannot_change_history():
    from app.core.memory import SessionStore

    store = SessionStore()
    old = store.acquire("session")
    store.release(old)
    store.acquire("session")
    foreign = SessionStore().acquire("session")
    for lease in (old, foreign):
        with pytest.raises(ValueError):
            store.commit(lease, [HumanMessage("bad"), AIMessage("bad")])
    assert store.snapshot("session") == ()


# 验证半轮、孤立回答、错误角色或顺序的消息批次整批拒绝，不部分提交。
@pytest.mark.parametrize("messages", [
    [HumanMessage("half")],
    [AIMessage("orphan"), HumanMessage("wrong order")],
    [SystemMessage("system"), AIMessage("answer")],
    [HumanMessage("one"), HumanMessage("two")],
    [HumanMessage("valid"), AIMessage("answer"), HumanMessage("half")],
])
def test_invalid_completed_messages_do_not_partially_commit(messages):
    from app.core.memory import SessionStore

    store = SessionStore()
    lease = store.acquire("session")
    with pytest.raises(ValueError):
        store.commit(lease, messages)
    assert store.snapshot("session") == ()
