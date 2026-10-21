"""Task-local execution observations. Instrumentation never owns business errors."""
from __future__ import annotations

import asyncio
import logging
from contextlib import ExitStack, contextmanager
from contextvars import ContextVar
from dataclasses import dataclass

logger = logging.getLogger(__name__)
_CURRENT = ContextVar('ch09_execution', default=None)


def _degraded(stage, exc):
    logger.warning('langfuse stage=%s degraded error_type=%s', stage, type(exc).__name__)


@dataclass(frozen=True)
class ExecutionIdentity:
    conversation_id: str
    user_message_id: str
    execution_id: str
    purpose: str
    replay: bool = False


class ExecutionTrace:
    def __init__(self, runtime, identity, *, input=None):
        self.identity = identity
        self.input=input
        self.client = getattr(runtime, 'client', None)
        self._stack, self._span, self._token = ExitStack(), None, None
        self._finished = False
        self.metadata = {'ch09_execution': True, 'conversation_id': identity.conversation_id,
            'user_message_id': identity.user_message_id,
            'logical_turn_id': f'{identity.conversation_id}:{identity.user_message_id}',
            'execution_id': identity.execution_id, 'purpose': identity.purpose,
            'replay': identity.replay, 'intent': '未识别','source_kind':getattr(runtime,'source_kind','unknown')}

    def __enter__(self):
        self._token = _CURRENT.set(self)
        if self.client is None or self.identity.replay:
            return self
        try:
            from opentelemetry import context as otel_context
            token = otel_context.attach(otel_context.Context())
            self._stack.callback(otel_context.detach, token)
            from langfuse import propagate_attributes
            self._stack.enter_context(propagate_attributes(
                session_id=self.identity.conversation_id,
                metadata={'purpose': self.identity.purpose,
                          'execution_id': self.identity.execution_id}))
            self._span = self._stack.enter_context(self.client.start_as_current_observation(
                name='ch09.execution', input=self.input, metadata=dict(self.metadata)))
        except Exception as exc:
            _degraded('begin', exc)
            try:
                self._stack.close()
            except Exception as close_error:
                _degraded('begin_cleanup', close_error)
        return self

    def set_intent(self, intent: str, confidence: float | None, route: str):
        self.metadata.update(intent=intent or '未识别', confidence=confidence, route=route)
        if self._span is None:
            return
        try:
            from langfuse import propagate_attributes
            # SDK v5 also writes trace-level metadata from the initial graph root.
            # Its initial intent must not override the completed observation when
            # the local server combines those two dimensions on read-back.
            with propagate_attributes(tags=[f'intent:{intent}'],metadata={'intent': intent, 'route': route}):
                self._span.update(metadata=dict(self.metadata))
        except Exception as exc:
            _degraded('intent', exc)

    def finish(self, outcome: str, *, output=None):
        if self._finished:
            return
        self._finished = True
        self.metadata['outcome'] = outcome
        if self._span is not None:
            try:
                self._span.update(metadata=dict(self.metadata),
                    **({'output':output} if output is not None else {}),
                    level='ERROR' if outcome in ('error', 'timeout') else 'DEFAULT')
            except Exception as exc:
                _degraded('finish', exc)

    def __exit__(self, exc_type, exc, traceback):
        try:
            if not self._finished:
                outcome = ('cancelled' if isinstance(exc, asyncio.CancelledError)
                           else 'error' if exc is not None else 'success')
                self.finish(outcome)
            try:
                # Close without passing provider/business exception text to SDK serialization.
                self._stack.close()
            except Exception as close_error:
                _degraded('close', close_error)
        finally:
            _CURRENT.reset(self._token)
        return False

    @contextmanager
    def operation(self, name: str, *, input: dict, metadata: dict):
        step = _Operation()
        scope = ExitStack()
        if self._span is not None and not self.identity.replay:
            try:
                kind = metadata.get('observation_type', 'span')
                if kind not in ('span', 'tool', 'retriever', 'chain'):
                    kind = 'span'
                step.span = scope.enter_context(self.client.start_as_current_observation(
                    name=name, as_type=kind, input=input, metadata=metadata))
            except Exception as exc:
                _degraded('operation_begin', exc)
        try:
            yield step
        except BaseException as exc:
            step.update(level='ERROR', status_message=type(exc).__name__)
            raise
        finally:
            try:
                scope.close()
            except Exception as exc:
                _degraded('operation_close', exc)


class _Operation:
    span = None

    def update(self, **kwargs):
        if self.span is not None:
            try:
                self.span.update(**kwargs)
            except Exception as exc:
                _degraded('operation_update', exc)


def current_execution():
    return _CURRENT.get()


def create_callback_handler(*, public_key, priced_model=None):
    from langfuse.langchain import CallbackHandler

    def enrich(kwargs):
        trace = current_execution()
        metadata = dict(kwargs.get('metadata') or {})
        if trace is not None:
            for key in ('conversation_id', 'user_message_id', 'logical_turn_id', 'execution_id',
                        'purpose', 'intent', 'confidence', 'route'):
                if key in trace.metadata:
                    metadata[key] = trace.metadata[key]
        return {**kwargs, 'metadata': metadata}

    class ExecutionCallbackHandler(CallbackHandler):
        # Read the shared execution record at each start: LangGraph nodes run in
        # separate Contexts, so a classifier's new ContextVar token cannot publish
        # the final intent to sibling tasks. The root remains the usage authority.
        def on_chain_start(self, *args, **kwargs):
            return super().on_chain_start(*args, **enrich(kwargs))

        def on_chat_model_start(self, *args, **kwargs):
            return super().on_chat_model_start(*args, **enrich(kwargs))

        def on_llm_end(self,response,*,run_id,parent_run_id=None,**kwargs):
            try:
                from langfuse.langchain.CallbackHandler import _parse_model,_parse_usage
                from app.observability.pricing import estimate_cost
                generation=self._runs.get(run_id)
                model=_parse_model(response) or priced_model
                price=estimate_cost(model,_parse_usage(response)) if priced_model else None
                if generation is not None and price is not None:
                    generation.update(cost_details=price['usd_details'],metadata={'pricing':{
                        key:value for key,value in price.items() if key!='usd_details'}})
            except Exception as exc:
                _degraded('pricing',exc)
            return super().on_llm_end(response,run_id=run_id,parent_run_id=parent_run_id,**kwargs)

        def on_tool_start(self, *args, **kwargs):
            return super().on_tool_start(*args, **enrich(kwargs))

        def on_retriever_start(self, *args, **kwargs):
            return super().on_retriever_start(*args, **enrich(kwargs))

    return ExecutionCallbackHandler(public_key=public_key)


def begin_execution(runtime, identity, *, input=None):
    return ExecutionTrace(runtime, identity,input=input)


@contextmanager
def operation(name: str, *, input: dict, metadata: dict):
    trace = current_execution()
    if trace is None:
        yield _Operation()
    else:
        with trace.operation(name, input=input, metadata=metadata) as step:
            yield step
