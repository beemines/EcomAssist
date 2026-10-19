"""Copy authoritative evidence before projection; never fetch current knowledge."""
import json
from datetime import datetime, timezone

from langchain_core.messages import AIMessage, HumanMessage, ToolMessage

from app.core.evidence import _matches
from app.flywheel.types import RetrievalSnapshot, RetrievedChunk, SnapshotPayload


def capture_retrieval_snapshot(payload, *, prompt_ids, strategy, retrieved_at):
    selected = set(prompt_ids)
    matches = _matches(payload)
    matches.sort(key=lambda row: (row['score_kind'] == 'rerank', row['score']), reverse=True)
    return RetrievalSnapshot(status='captured', payload=SnapshotPayload(strategy=strategy,
        retrieved_at=retrieved_at, chunks=[RetrievedChunk(chunk_id=row['id'],
            question=row['question'], answer=row['answer'], section_path=row.get('section_path'),
            score=float(row['score']), score_kind=row['score_kind'], rank=rank,
            in_prompt=row['id'] in selected) for rank, row in enumerate(matches[:10], 1)]))


def capture_turn_retrieval(state, payload, *, prompt_ids):
    previous = state.get('retrieval_snapshot')
    merged = {}
    if previous is not None:
        old = RetrievalSnapshot.model_validate_json(json.dumps(previous, ensure_ascii=False))
        for chunk in old.payload.chunks if old.payload else []:
            merged[chunk.chunk_id] = {'id': chunk.chunk_id, 'question': chunk.question,
                'answer': chunk.answer, 'section_path': chunk.section_path,
                'score': chunk.score, 'score_kind': chunk.score_kind}
    for row in _matches(payload):
        if row['id'] not in merged or row['score'] > merged[row['id']]['score']:
            merged[row['id']] = row
    return capture_retrieval_snapshot({'matches': list(merged.values())}, prompt_ids=prompt_ids,
        strategy=payload.get('retrieval', {}).get('strategy', 'hybrid_rerank'),
        retrieved_at=datetime.now(timezone.utc))


def _original_payloads(state):
    messages = state.get('messages', [])
    if not isinstance(messages, list):
        return []
    start = next((i for i, message in enumerate(messages) if isinstance(message, HumanMessage)
                  and message.id == state.get('user_message_id')), None)
    if start is None:
        return []
    result = []
    for request, reply in zip(messages[start+1:], messages[start+2:]):
        if isinstance(request, HumanMessage) or isinstance(reply, HumanMessage):
            break
        if (isinstance(request, AIMessage) and len(request.tool_calls) == 1
                and request.tool_calls[0].get('name') == 'query_faq'
                and isinstance(reply, ToolMessage) and reply.status != 'error'
                and reply.tool_call_id == request.tool_calls[0].get('id')):
            try:
                payload = json.loads(reply.content)
            except (TypeError, ValueError):
                continue
            if isinstance(payload, dict) and isinstance(payload.get('matches'), list):
                result.append(payload)
    return result


def snapshot_from_state(state):
    if state.get('retrieval_snapshot') is not None:
        return RetrievalSnapshot.model_validate_json(json.dumps(state['retrieval_snapshot'], ensure_ascii=False))
    payloads = _original_payloads(state)
    shown = state.get('evidence_payload')
    shown = shown if isinstance(shown, dict) else {}
    if not payloads and isinstance(shown, dict) and isinstance(shown.get('matches'), list):
        payloads = [shown]
    if payloads:
        try:
            prompt_ids = [str(row['id']) for row in shown.get('matches', [])]
            snapshot = None
            for payload in payloads:
                snapshot = capture_turn_retrieval({'retrieval_snapshot': snapshot.model_dump(mode='json')}
                    if snapshot else {}, payload, prompt_ids=prompt_ids)
        except (ValueError, TypeError, KeyError, AttributeError):
            return _unavailable()
        # Legacy roots do not contain an original capture timestamp. Be explicit
        # that this timestamp describes recovery, not the original retrieval.
        snapshot.payload.versions['timestamp_basis'] = 'legacy_recovery'
        return snapshot
    if state.get('retrieval_performed') is False:
        return RetrievalSnapshot(status='not_retrieved', payload=None)
    traces = state.get('tool_trace')
    known_trace = isinstance(traces, list) and all(isinstance(trace, dict)
        and isinstance(trace.get('name'), str) for trace in traces)
    trace_items = traces if isinstance(traces, list) else []
    had_retrieval = (state.get('retrieval_performed') is True or state.get('route') in ('knowledge', 'after_sales')
        or bool(state.get('retrieval_queries')) or bool(state.get('retrieval_audit'))
        or any(trace.get('name') == 'query_faq' for trace in trace_items if isinstance(trace, dict)))
    if had_retrieval:
        return _unavailable()
    if not known_trace and state.get('route') not in ('social', 'complaint', 'other'):
        return _unavailable()
    return RetrievalSnapshot(status='not_retrieved', payload=None)


def _unavailable():
    return RetrievalSnapshot(status='unavailable', payload=SnapshotPayload(strategy='unknown',
        retrieved_at=datetime.now(timezone.utc), versions={'timestamp_basis': 'legacy_recovery'},
        chunks=[], reason='legacy_payload_missing'))
