"""SQL owns audit history; checkpoint normalization never writes old roots."""
from collections.abc import Mapping, Sequence

from langchain_core.messages import BaseMessage, HumanMessage
from langgraph.types import Overwrite

from app.core.tool_history import _validate_turn
from app.repositories.records import MessageRecord, message_from_record, record_from_message


def sql_messages(rows: Sequence[MessageRecord]) -> list[BaseMessage]:
    """Restore every raw SQL row, including cancelled tool envelopes."""
    ordered = sorted(rows, key=lambda row: row.id)
    ids = [row.id for row in ordered]
    if any(type(identifier) is not int or identifier <= 0 for identifier in ids) or len(set(ids)) != len(ids):
        raise ValueError('SQL history requires unique positive message IDs')
    return [message_from_record(row).model_copy(update={'id': str(row.id)}, deep=True) for row in ordered]


def prepare_history_update(previous: Mapping, rows: Sequence[MessageRecord], *,
                           current_user_id: int) -> tuple[list[BaseMessage] | Overwrite, bool]:
    """Append a matching SQL suffix; bootstrap only when canonical history differs."""
    messages = sql_messages(rows)
    current = next((m for m in messages if m.id == str(current_user_id)), None)
    if not isinstance(current, HumanMessage) or any(isinstance(m, HumanMessage) and int(m.id) > current_user_id for m in messages):
        raise ValueError('current SQL user message identity missing or stale')
    canonical = {m.id: record_from_message(m) for m in messages}
    prior = previous.get('messages', [])
    # Missing SQL cannot be reconstructed from a summary or an anonymous model ID.
    for message in prior:
        raw = record_from_message(message)
        if message.id and str(message.id).isdecimal():
            if str(message.id) not in canonical:
                raise ValueError('checkpoint message has no recoverable SQL original')
        elif raw not in canonical.values():
            raise ValueError('anonymous checkpoint message has no recoverable SQL original')
    prefix = len(prior) <= len(messages) and all(
        old.id == fresh.id and record_from_message(old) == record_from_message(fresh)
        for old, fresh in zip(prior, messages))
    if previous.get('context_version') == 1 and prefix:
        return messages[len(prior):], False
    return Overwrite(value=messages), True


def replay_turns(messages: Sequence[BaseMessage]) -> list[list[BaseMessage]]:
    """Temporary legacy consumer view: only valid complete turns, never audit tails.

    Full raw messages stay in State. Tasks 6/7 replace this compatibility view with
    the context snapshot projection, including its counted interrupted archive.
    """
    turns, group = [], []
    for message in messages:
        if isinstance(message, HumanMessage) and group:
            try:
                _validate_turn(group)
            except ValueError:
                pass
            else:
                turns.append(group)
            group = []
        group.append(message)
    if group:
        try:
            _validate_turn(group)
        except ValueError:
            pass
        else:
            turns.append(group)
    return turns
