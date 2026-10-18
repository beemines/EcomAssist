"""Shared summary source authority; the original frozen batch stays intact."""
import json
from dataclasses import replace

from app.repositories.records import decode_tool_calls


def summary_source_rows(batch):
    """User originals and adjacent matched successful tool pairs, in source order.

    Request metadata establishes the pair, not facts. Its prose and unrelated
    arguments are excluded from the model view along with ordinary replies.
    """
    rows = []
    for index, request in enumerate(batch.source_rows):
        if request.role == 'user':
            rows.append(request)
        if (request.role != 'assistant' or not request.tool_calls_json
                or index + 1 == len(batch.source_rows)):
            continue
        result = batch.source_rows[index + 1]
        if result.role != 'tool':
            continue
        try:
            calls = decode_tool_calls(json.loads(request.tool_calls_json))
            payload = json.loads(result.content)
        except (ValueError, TypeError, KeyError):
            continue
        if (len(calls) != 1 or calls[0]['id'] != result.tool_call_id or not isinstance(payload, dict)
                or 'error' in payload or payload.get('success') is False or payload.get('status') == 'error'):
            continue
        asked = calls[0]['args'].get('order_id')
        if asked is not None and payload.get('order_id') != asked:
            continue
        call = calls[0]
        arguments = {'order_id': asked} if asked is not None else {}
        metadata = [{'id': call['id'], 'type': 'function', 'function': {
            'name': call['name'], 'arguments': json.dumps(arguments, ensure_ascii=False)}}]
        rows.extend((replace(request, content=None, tool_calls_json=json.dumps(metadata, ensure_ascii=False)),
                     replace(result, tool_calls_json=None)))
    return tuple(rows)
