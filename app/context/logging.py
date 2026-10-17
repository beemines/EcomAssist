"""Dedicated UTF-8 content log. Never accepts a runtime/client or request headers."""
from collections.abc import Mapping
from dataclasses import asdict
from datetime import datetime, timezone
import json
from pathlib import Path
from threading import Lock

from langchain_openai.chat_models.base import _convert_message_to_dict

from app.context.tokens import _plain_json


def budget_fields(budget):
    return _plain_json({name: getattr(budget, name) for name in budget.__dataclass_fields__})


class ContextLogger:
    def __init__(self, path: Path):
        path = Path(path)
        path.parent.mkdir(parents=True, exist_ok=True)
        self._file = path.open('a', encoding='utf-8', newline='\n')
        self._lock = Lock()

    def event(self, name: str, fields: Mapping):
        # Explicit payloads only: no repr/default=str fallback for arbitrary clients.
        payload = {'event': name, 'time': datetime.now(timezone.utc).isoformat(), **_plain_json(fields)}
        line = json.dumps(payload, ensure_ascii=False, allow_nan=False, separators=(',', ':'))
        with self._lock:
            self._file.write(line + '\n')
            self._file.flush()

    def history(self, snapshot, *, consumer, packet, sent):
        self.event('history_ctx', dict(conversation_id=snapshot.conversation_id,
            user_message_id=snapshot.user_message_id, snapshot_id=snapshot.snapshot_id,
            consumer=consumer, sent=sent,
            anchors={key: str(value) if value is not None else None for key, value in asdict(snapshot.anchors).items()},
            summaries=[dict(seq=segment.seq, from_msg_id=str(segment.from_msg_id),
                upto_msg_id=str(segment.upto_msg_id), content=segment.content) for segment in snapshot.summaries],
            omitted_summary_seqs=snapshot.omitted_summary_seqs,
            layer1=[asdict(row) for row in snapshot.layer1], layer2=[asdict(row) for row in snapshot.layer2],
            layer1_count=len(snapshot.layer1), layer2_count=len(snapshot.layer2), budget=budget_fields(snapshot.budget),
            messages=[_convert_message_to_dict(message) for message in packet.messages] if packet else None,
            estimated_tokens=packet.estimated_tokens if packet else None))

    def model(self, packet, *, conversation_id, user_message_id, phase, call_index):
        self.event('model_ctx', dict(conversation_id=conversation_id, user_message_id=user_message_id,
            snapshot_id=packet.snapshot_id, phase=phase, call_index=call_index,
            messages=[_convert_message_to_dict(message) for message in packet.messages], tools=packet.tools,
            estimated_tokens=packet.estimated_tokens, output_tokens=packet.output_tokens, prefix_hash=packet.prefix_hash))

    def close(self):
        with self._lock:
            self._file.close()
