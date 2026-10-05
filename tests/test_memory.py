from dataclasses import FrozenInstanceError

import pytest
from langchain_core.messages import AIMessage, HumanMessage, SystemMessage


def test_sessions_keep_independent_completed_turns():
    from app.core.memory import SessionStore

    store = SessionStore()
    first = store.acquire("first")
    second = store.acquire("second")
    store.commit(first, [HumanMessage("问"), AIMessage("答")])
    assert [m.content for m in store.snapshot("first")] == ["问", "答"]
    assert second.history == ()
    assert store.snapshot("second") == ()


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


def test_release_without_commit_preserves_previous_history():
    from app.core.memory import SessionStore

    store = SessionStore()
    lease = store.acquire("session")
    store.commit(lease, [HumanMessage("one"), AIMessage("answer")])
    store.release(lease)
    abandoned = store.acquire("session")
    store.release(abandoned)
    assert [m.content for m in store.snapshot("session")] == ["one", "answer"]


def test_commit_replaces_history_with_retained_completed_turns():
    from app.core.memory import SessionStore

    store = SessionStore()
    lease = store.acquire("session")
    store.commit(lease, [HumanMessage("old"), AIMessage("0"), HumanMessage("one"), AIMessage("1")])
    store.release(lease)
    next_lease = store.acquire("session")
    store.commit(next_lease, [*next_lease.history[2:], HumanMessage("two"), AIMessage("2")])
    assert [m.content for m in store.snapshot("session")] == ["one", "1", "two", "2"]


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
