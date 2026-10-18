"""Rejected controls remain invalid while dedicated content logs retain evidence."""
import json
import logging

import pytest
from langchain_core.messages import AIMessage
from langgraph.runtime import Runtime

from app.context.logging import ContextLogger
from app.core.errors import ServiceError
from app.workflow import agent
from tests.test_workflow_agent import setup, control
from tests.workflow_fakes import workflow_call


def rejected_reply(transport, reason='SECRET_SENTINEL 原始原因'):
    args = {'reply_mode': 'answer', 'suggested_actions': [],
            'refund_decision': None, 'decision_reason': reason}
    if transport == 'native_control':
        # Missing required reply_mode makes the native schema itself invalid.
        del args['reply_mode']
        reply = workflow_call('internal_response_control', args)
    else:
        reply = AIMessage('  ' + json.dumps(args, ensure_ascii=False) + '\n',
                          response_metadata={'finish_reason': 'stop'})
    reply.usage_metadata = {'input_tokens': 10, 'output_tokens': 5, 'total_tokens': 15}
    reply.additional_kwargs['reasoning_content'] = 'REASONING_MUST_STAY_PRIVATE'
    reply.response_metadata['unrelated'] = 'METADATA_MUST_STAY_PRIVATE'
    return reply, args


@pytest.mark.parametrize('transport', ['json_control', 'native_control'])
@pytest.mark.parametrize('large', [False, True])
async def test_rejected_control_evidence_is_private_bounded_and_does_not_execute(
        transport, large, tmp_path, caplog, capsys):
    reason = 'SECRET_SENTINEL 原始原因' + ('😀' * 8300 if large else '')
    reply, args = rejected_reply(transport, reason)
    context, state = setup([reply], question='查物流', intent='物流')
    # These tests isolate one rejected attempt after the shared allowance is spent.
    context.model_recovery_used = True
    path = tmp_path / 'content.jsonl'
    content_logger = ContextLogger(path)
    context.context_logger = content_logger
    observed = []
    context.usage_observer = observed.append
    try:
        with caplog.at_level(logging.INFO), pytest.raises(ServiceError) as caught:
            await agent.llm_call(state, Runtime(context=context))
    finally:
        content_logger.close()
    assert caught.value.code == 'invalid_structured_output'
    assert context.decision_model.decisions == 1 and context.model.streams == 0
    assert not context.repository.messages
    assert observed[-1]['usage'] == {'actual': 15, 'estimated': 0,
                                     'actual_calls': 1, 'estimated_calls': 0}
    assert 'SECRET_SENTINEL' not in caplog.text + capsys.readouterr().err
    assert any('control_schema' in record.message for record in caplog.records)
    events = [json.loads(line) for line in path.read_text(encoding='utf-8').splitlines()]
    rejection, = [event for event in events if event['event'] == 'decision_control_rejected']
    assert rejection['conversation_id'] == state['conversation_id']
    assert rejection['user_message_id'] == state['user_message_id']
    assert rejection['transport'] == transport
    assert rejection['finish_reason'] == ('tool_calls' if transport == 'native_control' else 'stop')
    original = reply.text
    assert rejection['control_text'] == original[:8192]
    assert rejection['control_text_length'] == len(original)
    assert rejection['control_text_truncated'] is (len(original) > 8192)
    if transport == 'native_control':
        original_args = json.dumps(args, ensure_ascii=False, allow_nan=False)
        assert rejection['arguments_text'] == original_args[:8192]
        assert rejection['arguments_text_length'] == len(original_args)
        assert rejection['arguments_text_truncated'] is (len(original_args) > 8192)
        if not large:
            assert json.loads(rejection['arguments_text']) == args
    assert 'REASONING_MUST_STAY_PRIVATE' not in json.dumps(rejection)
    assert 'METADATA_MUST_STAY_PRIVATE' not in json.dumps(rejection)


@pytest.mark.parametrize('has_logger', [False, True])
async def test_optional_rejection_logger_failure_preserves_original_error_and_usage(
        has_logger, monkeypatch, tmp_path):
    reply, _ = rejected_reply('json_control')
    context, state = setup([reply], question='查物流', intent='物流')
    context.model_recovery_used = True
    errors, observed = [], []
    original_parse = agent.parse_control

    def track_parse(*args, **kwargs):
        try:
            return original_parse(*args, **kwargs)
        except ServiceError as exc:
            errors.append(exc)
            raise

    monkeypatch.setattr(agent, 'parse_control', track_parse)
    context.usage_observer = observed.append
    content_logger = ContextLogger(tmp_path / 'content.jsonl') if has_logger else None
    context.context_logger = content_logger
    if content_logger:
        original_event = content_logger.event

        def failing_event(name, fields):
            if name == 'decision_control_rejected':
                raise OSError('optional content log unavailable')
            original_event(name, fields)

        monkeypatch.setattr(content_logger, 'event', failing_event)
    try:
        with pytest.raises(ServiceError) as caught:
            await agent.llm_call(state, Runtime(context=context))
    finally:
        if content_logger:
            content_logger.close()
    assert caught.value is errors[0]
    assert caught.value.code == 'invalid_structured_output'
    assert observed[-1]['usage']['actual'] == 15
    assert observed[-1]['usage']['actual_calls'] == 1
    assert observed[-1]['usage']['estimated_calls'] == 0
    assert context.decision_model.decisions == 1 and not context.repository.messages


async def test_valid_control_does_not_emit_rejection_event(tmp_path):
    context, state = setup([control('clarification')], question='查物流', intent='物流')
    path = tmp_path / 'content.jsonl'
    content_logger = ContextLogger(path)
    context.context_logger = content_logger
    try:
        result = await agent.llm_call(state, Runtime(context=context))
    finally:
        content_logger.close()
    assert result['reply_mode'] == 'clarification'
    assert 'decision_control_rejected' not in path.read_text(encoding='utf-8')
