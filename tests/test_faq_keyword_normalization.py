"""真实聊天编排/工具/FAQ仓储回归，仅替换外部模型与检索边界。"""
import asyncio
import json
import logging

from langchain_core.messages import AIMessageChunk
import pytest

from app.core.conversation_locks import ConversationLocks
from app.core.errors import ServiceError
from app.core.tool_chat import ToolChatService
from app.knowledge.types import ChunkRecord
from app.repositories.faq import FAQRepository
from app.retrieval.types import QueryPlan, RetrievalBundle, ScoredChunk
from app.tools.registry import build_registry
from tests.fakes import fake_settings
from tests.tool_fakes import Tickets, ToolModel, ToolRepository, collect, selected_call


QUESTION = '普通地区买80元商品，邮费多少？'


class Retrieval:
    """记录完整检索原话，返回独立手写的权威证据或指定故障。"""
    def __init__(self, failure=None, entered=None):
        self.calls, self.failure, self.entered = [], failure, entered
    async def retrieve(self, question, *, category=None):
        self.calls.append((question, category))
        if self.entered is not None:
            self.entered.set()
            await asyncio.Event().wait()
        if self.failure is not None:
            raise self.failure
        row = ChunkRecord('配送', '普通地区邮费', '邮费8元。', id=7, vectorize_status='done')
        return RetrievalBundle(QueryPlan(standard=question, expansions=[]), 'hybrid_rerank', [],
            [ScoredChunk(row, .9, 'rerank')])


def application(args=None, *, failure=None, entered=None):
    """保留真实上下文工具、执行器和仓储入口，避免替身绕过原片段保护。"""
    request = selected_call('query_faq', {'keyword': '运费'} if args is None else args)
    request.additional_kwargs['tool_calls'] = [{
        'id': 'call_1', 'type': 'function', 'function': {
            'name': 'query_faq', 'arguments': json.dumps(request.tool_calls[0]['args'], ensure_ascii=False)}}]
    model = ToolModel(request, [AIMessageChunk('邮费8元。[1]', response_metadata={'finish_reason': 'stop'})])
    repository, retrieval = ToolRepository(), Retrieval(failure, entered)
    faq = FAQRepository(None, None, None, retriever=retrieval)
    service = ToolChatService(model, repository, lambda context: build_registry(faq, Tickets(), context),
        ConversationLocks(), fake_settings(tool_max_retries=0))
    return service, model, repository, retrieval


@pytest.mark.parametrize('question', [QUESTION,
    'MH-W40金额80元，未拆封且不接受换货，邮费多少？',
    '中' * 150 + 'MH-W40金额80元，未拆封且不接受换货，邮费多少？',
    ' ' * 140 + QUESTION])
async def test_rewritten_keyword_normalizes_effective_request_and_preserves_full_question(question, caplog):
    """邮费/运费同义改写不能终止聊天；复制后的审计申请与实际工具执行必须一致。"""
    service, model, repository, retrieval = application()
    original = model.selected.model_dump()
    with caplog.at_level(logging.WARNING):
        events = await collect(service, await service.prepare('42', question, category='配送'))
    assert events[-1].event == 'done' and not any(event.event == 'error' for event in events)
    assert ''.join(event.data['delta'] for event in events if event.event == 'delta') == '邮费8元。[1]'
    assert retrieval.calls == [(question, '配送')]
    request = next(row for row in repository.rows if row.tool_calls)
    args = json.loads(request.tool_calls[0]['function']['arguments'])
    assert args == {'keyword': question.lstrip()[:128]}
    assert 1 <= len(args['keyword']) <= 128 and args['keyword'] in question
    effective = model.final_input[-2]
    assert effective.tool_calls[0]['args'] == args
    assert json.loads(effective.additional_kwargs['tool_calls'][0]['function']['arguments']) == args
    assert model.final_input[-1].tool_call_id == request.tool_calls[0]['id'] == 'call_1'
    assert next(row.content for row in repository.rows if row.role == 'tool') == model.final_input[-1].content
    assert model.selected.model_dump() == original
    assert model.selection_requests == model.final_stream_requests == 1
    messages = [record.getMessage() for record in caplog.records if record.name == 'app.core.tool_chat']
    assert messages == ['status=normalized code=faq_keyword_normalized tool=query_faq']
    assert question not in caplog.text and '80' not in caplog.text and 'MH-W40' not in caplog.text
    assert all(record.exc_info is None for record in caplog.records)


async def test_original_fragment_is_preserved_without_normalization_log(caplog):
    """合法原片段包含空白也应原样进入审计与执行，不任意扩写。"""
    service, model, repository, retrieval = application({'keyword': ' 邮费 '})
    question = '普通地区80元商品 邮费 多少？'
    with caplog.at_level(logging.WARNING):
        events = await collect(service, await service.prepare('42', question))
    assert events[-1].event == 'done' and retrieval.calls == [(question, None)]
    request = next(row for row in repository.rows if row.tool_calls)
    assert json.loads(request.tool_calls[0]['function']['arguments']) == {'keyword': ' 邮费 '}
    assert model.final_input[-2].tool_calls[0]['args'] == {'keyword': ' 邮费 '}
    assert not any(record.name == 'app.core.tool_chat' for record in caplog.records)


@pytest.mark.parametrize('args', [dict(keyword=''), dict(keyword=' '), dict(keyword=1),
    dict(keyword=True), dict(keyword='x' * 129), dict(keyword='运费', extra='private'), {}])
async def test_invalid_schema_is_not_repaired_or_executed(args, caplog):
    """非法类型、空白、超长和额外参数必须由既有严格工具校验拒绝。"""
    service, model, repository, retrieval = application(args)
    with caplog.at_level(logging.WARNING):
        events = await collect(service, await service.prepare('42', QUESTION))
    assert events[-1].event == 'error' and events[-1].data['code'] == 'invalid_arguments'
    assert retrieval.calls == [] and model.final_stream_requests == 0
    assert not any(event.event == 'done' for event in events)
    request = next(row for row in repository.rows if row.tool_calls)
    assert json.loads(request.tool_calls[0]['function']['arguments']) == args
    assert not any(record.name == 'app.core.tool_chat' for record in caplog.records)


async def test_normalization_does_not_turn_dependency_failure_into_done():
    """参数归一不能吞掉真实检索故障或启动最终模型回答。"""
    service, model, _, retrieval = application(failure=ServiceError('upstream_timeout', '固定提示', 504))
    events = await collect(service, await service.prepare('42', QUESTION))
    assert events[-1].event == 'error' and events[-1].data['code'] == 'upstream_timeout'
    assert retrieval.calls == [(QUESTION, None)] and model.final_stream_requests == 0
    assert not any(event.event == 'done' for event in events)


async def test_normalization_does_not_swallow_cancellation():
    """真实工具执行期间取消仍应退出，归一后的参数不能授权成功提交。"""
    entered = asyncio.Event()
    service, model, repository, retrieval = application(entered=entered)
    task = asyncio.create_task(collect(service, await service.prepare('42', QUESTION)))
    # 未实现归一时先返回invalid_keyword，不能等永不发生的外部进入信号。
    waiter = asyncio.create_task(entered.wait())
    done, _ = await asyncio.wait([task, waiter], timeout=2, return_when=asyncio.FIRST_COMPLETED)
    if task in done:
        waiter.cancel()
        await asyncio.gather(waiter, return_exceptions=True)
        pytest.fail('chat stopped before normalized FAQ dependency')
    assert waiter in done
    task.cancel()
    with pytest.raises(asyncio.CancelledError):
        await task
    assert retrieval.calls == [(QUESTION, None)] and model.final_stream_requests == 0
    assert not any(row.role == 'assistant' and not row.tool_calls for row in repository.rows)
