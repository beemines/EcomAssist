"""Rejected intent replies retain bounded private evidence without changing validation."""
import json
import logging

import pytest
from langchain_core.messages import AIMessage

from app.context.logging import ContextLogger
from app.core.errors import ServiceError
from app.workflow import intent
from tests.test_context_view import snapshot
from tests.workflow_fakes import ScriptedWorkflowModel


VALID = '{"intent":"物流","confidence":0.93}'
USAGE = {'actual': 15, 'estimated': 0, 'actual_calls': 1, 'estimated_calls': 0}


def reply_for(body, *, finish='stop', **kwargs):
    reply = AIMessage(body, response_metadata={'finish_reason': finish,
        'headers': {'authorization': 'HEADER_PRIVATE'}, 'other': 'METADATA_PRIVATE'}, **kwargs)
    reply.additional_kwargs['reasoning_content'] = 'REASONING_PRIVATE'
    reply.usage_metadata = {'input_tokens': 10, 'output_tokens': 5, 'total_tokens': 15}
    return reply


def classifier(reply):
    model = ScriptedWorkflowModel(intent_replies=[reply])
    return intent.IntentClassifier(model, input_budget=8000, timeout_seconds=1), model


def events(path):
    return [json.loads(line) for line in path.read_text(encoding='utf-8').splitlines()]


@pytest.mark.parametrize('body,extra', [
    ('  {"intent":"PRIVATE_BAD_LABEL","confidence":0.9}\n', {}),
    ('{"intent":"物流"}', {}),
    ('{"intent":"物流","confidence":"0.9"}', {}),
    ('{"intent":"物流","confidence":1.1}', {}),
    ('{"intent":"物流","confidence":0.9,"extra":"PRIVATE_EXTRA"}', {}),
    ('{"intent":"物流","confidence":0.9', {}),
    (VALID, {'tool_calls': [{'id': 'native', 'name': 'query_logistics', 'args': {}}]}),
    (VALID, {'invalid_tool_calls': [{'id': 'invalid', 'name': 'query_logistics',
        'args': 'broken', 'error': 'TOOL_ERROR_PRIVATE'}]}),
    (VALID, {'additional_kwargs': {'tool_calls': [{'id': 'opaque', 'private': 'TOOL_PRIVATE'}]}}),
])
async def test_actual_classifier_logs_original_rejected_body_only(body, extra, tmp_path, caplog, capsys):
    service, model = classifier(reply_for(body, **extra))
    frozen = snapshot()
    path = tmp_path / 'content.jsonl'
    logger = ContextLogger(path)
    try:
        with caplog.at_level(logging.INFO), pytest.raises(ServiceError) as caught:
            await service.classify('查订单1001物流', snapshot=frozen, context_logger=logger)
    finally:
        logger.close()
    assert caught.value.code == 'invalid_structured_output'
    assert model.intents == 1 and model.decisions == model.streams == 0
    assert service.usage == USAGE
    event, = [row for row in events(path) if row['event'] == 'intent_control_rejected']
    assert event == {'event': 'intent_control_rejected', 'time': event['time'],
        'conversation_id': '42', 'user_message_id': '99', 'snapshot_id': frozen.snapshot_id,
        'finish_reason': 'stop', 'control_text': body, 'control_text_length': len(body),
        'control_text_truncated': False}
    public = caplog.text + capsys.readouterr().err + str(caught.value)
    for marker in ('PRIVATE_BAD_LABEL', 'PRIVATE_EXTRA', 'TOOL_ERROR_PRIVATE', 'TOOL_PRIVATE',
                   'HEADER_PRIVATE', 'METADATA_PRIVATE', 'REASONING_PRIVATE'):
        assert marker not in public


@pytest.mark.parametrize('large', [False, True])
async def test_rejected_text_preserves_whitespace_and_unicode_with_explicit_bound(large, tmp_path):
    body = '  {"intent":"原始😀' + ('😀' * 8300 if large else '') + '","confidence":0.93}\n'
    service, model = classifier(reply_for(body))
    path = tmp_path / 'content.jsonl'
    logger = ContextLogger(path)
    try:
        with pytest.raises(ServiceError):
            await service.classify('查物流', snapshot=snapshot(), context_logger=logger)
    finally:
        logger.close()
    event, = [row for row in events(path) if row['event'] == 'intent_control_rejected']
    assert event['control_text'] == body[:8192]
    assert event['control_text_length'] == len(body)
    assert event['control_text_truncated'] is large
    assert len(event['control_text']) == (8192 if large else len(body))
    assert '😀' in event['control_text'] and '😀' in path.read_text(encoding='utf-8')
    assert service.usage == USAGE and model.intents == 1


@pytest.mark.parametrize('finish,safe', [('length', 'length'), ('content_filter', 'content_filter'),
    ('tool_calls', 'tool_calls'), ('UNSAFE_FINISH_PRIVATE', None), ({'secret': 'FINISH_PRIVATE'}, None),
    (None, None)])
async def test_finish_reason_is_allowlisted_in_rejection_payload(finish, safe, tmp_path, caplog, capsys):
    service, _ = classifier(reply_for(VALID, finish=finish))
    path = tmp_path / 'content.jsonl'
    logger = ContextLogger(path)
    try:
        with pytest.raises(ServiceError) as caught:
            await service.classify('查物流', snapshot=snapshot(), context_logger=logger)
    finally:
        logger.close()
    event, = [row for row in events(path) if row['event'] == 'intent_control_rejected']
    assert event['finish_reason'] == safe
    assert 'PRIVATE' not in json.dumps(event) + caplog.text + capsys.readouterr().err + str(caught.value)
    assert caught.value.finish_reason == (finish if finish in ('length', 'content_filter') else None)
    assert service.usage == USAGE


@pytest.mark.parametrize('source', ['guard', 'validator'])
@pytest.mark.parametrize('logger_mode', ['present', 'absent', 'failing'])
async def test_logging_preserves_exact_original_exception_and_usage(source, logger_mode, monkeypatch, tmp_path):
    service, model = classifier(reply_for(VALID if source == 'guard' else '{"intent":"物流"}',
                                          finish='length' if source == 'guard' else 'stop'))
    errors = []
    if source == 'guard':
        original = intent.invalid_output

        def track_error(**kwargs):
            error = original(**kwargs)
            errors.append(error)
            return error

        monkeypatch.setattr(intent, 'invalid_output', track_error)
    else:
        original = intent.validate_structured_output

        def track_error(*args, **kwargs):
            try:
                return original(*args, **kwargs)
            except ServiceError as error:
                errors.append(error)
                raise

        monkeypatch.setattr(intent, 'validate_structured_output', track_error)
    logger = ContextLogger(tmp_path / 'content.jsonl') if logger_mode != 'absent' else None
    if logger_mode == 'failing':
        original_event = logger.event

        def failing_event(name, fields):
            if name == 'intent_control_rejected':
                raise OSError('LOG_FAILURE_PRIVATE')
            return original_event(name, fields)

        monkeypatch.setattr(logger, 'event', failing_event)
    try:
        with pytest.raises(ServiceError) as caught:
            await service.classify('查物流', snapshot=snapshot(), context_logger=logger)
    finally:
        if logger:
            logger.close()
    assert errors == [caught.value] and caught.value is errors[0]
    assert caught.value.code == 'invalid_structured_output'
    assert service.usage == USAGE and model.intents == 1


async def test_missing_raw_message_is_rejected_without_serializing_arbitrary_output(tmp_path):
    service, model = classifier({'raw': {'secret': 'RAW_PRIVATE'}, 'parsed': None,
        'parsing_error': ValueError('PARSING_PRIVATE')})
    path = tmp_path / 'content.jsonl'
    logger = ContextLogger(path)
    try:
        with pytest.raises(ServiceError) as caught:
            await service.classify('查物流', snapshot=snapshot(), context_logger=logger)
    finally:
        logger.close()
    event, = [row for row in events(path) if row['event'] == 'intent_control_rejected']
    assert event['control_text'] == '' and event['control_text_length'] == 0
    assert event['control_text_truncated'] is False and event['finish_reason'] is None
    assert 'PRIVATE' not in json.dumps(event)
    assert caught.value.code == 'invalid_structured_output'
    assert service.usage['estimated_calls'] == 1 and service.usage['actual_calls'] == 0
    assert model.intents == 1


async def test_rejection_without_snapshot_has_no_event_and_keeps_rejection(tmp_path):
    service, _ = classifier(reply_for('{"intent":"物流"}'))
    path = tmp_path / 'content.jsonl'
    logger = ContextLogger(path)
    try:
        with pytest.raises(ServiceError) as caught:
            await service.classify('查物流', context_logger=logger)
    finally:
        logger.close()
    assert events(path) == [] and caught.value.code == 'invalid_structured_output'
    assert service.usage == USAGE


async def test_valid_control_emits_no_rejection_and_preserves_result_and_usage(tmp_path):
    service, model = classifier(reply_for(VALID))
    path = tmp_path / 'content.jsonl'
    logger = ContextLogger(path)
    try:
        result = await service.classify('查物流', snapshot=snapshot(), context_logger=logger)
    finally:
        logger.close()
    assert (result.raw_intent, result.intent, result.confidence) == ('物流', '物流', 0.93)
    assert not any(row['event'] == 'intent_control_rejected' for row in events(path))
    assert service.usage == USAGE and model.intents == 1
