"""Keep actionable upstream failure categories without logging provider bodies."""
import json

import httpx
from openai import InternalServerError

from app.context import logging as context_logging
from app.core.errors import ServiceError


class EvidenceSink:
    def __init__(self):
        self.records = []

    def event(self, name, fields):
        self.records.append({'event': name, **fields})


def emit(sink, error):
    recorder = getattr(context_logging, 'log_model_failure', None)
    assert callable(recorder), 'model failures need a bounded diagnostic recorder'
    return recorder(sink, error, conversation_id='84', user_message_id='789', phase='understanding')


def test_http_failure_keeps_status_and_numeric_code_without_private_message_or_request():
    request = httpx.Request('POST', 'https://provider.invalid/private', headers={'Authorization': 'Bearer SECRET_KEY'})
    provider = InternalServerError('PRIVATE_PROVIDER_BODY', response=httpx.Response(503, request=request),
                                   body={'code': '1302', 'message': 'PRIVATE_PROVIDER_BODY'})
    error = ServiceError('upstream_error', 'safe user error', 502)
    error.__cause__ = provider
    sink = EvidenceSink()
    assert emit(sink, error)
    assert sink.records == [{'event': 'model_call_failed', 'conversation_id': '84', 'user_message_id': '789',
        'phase': 'understanding', 'causes': [
            {'exception_type': 'ServiceError', 'status_code': 502, 'code': 'upstream_error'},
            {'exception_type': 'InternalServerError', 'status_code': 503, 'code': '1302'}]}]
    rendered = json.dumps(sink.records)
    assert all(secret not in rendered for secret in ('SECRET_KEY', 'PRIVATE_PROVIDER_BODY', 'provider.invalid', 'private'))


def test_untrusted_exception_codes_and_cycles_are_bounded():
    error = RuntimeError('PRIVATE')
    error.code = 'SECRET_KEY'
    error.__cause__ = error
    sink = EvidenceSink()
    assert emit(sink, error)
    assert sink.records[0]['causes'] == [{'exception_type': 'RuntimeError'}]


def test_failed_optional_evidence_never_replaces_model_failure():
    class BrokenSink:
        def event(self, *args):
            raise OSError('disk full')
    error = RuntimeError('PRIVATE')
    assert emit(BrokenSink(), error) is False
    assert emit(None, error) is False
