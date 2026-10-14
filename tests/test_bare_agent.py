"""裸 Agent 的真实执行器、多步回灌与硬停止行为。"""
import ast
import asyncio
from pathlib import Path

import pytest
from langchain_core.messages import HumanMessage, SystemMessage, ToolMessage

from app.agent.bare import run_bare_agent
from app.agent.controls import AgentLimits
from app.core.errors import ServiceError
from app.tools.business import query_logistics, query_order, query_product
from app.tools.executor import ToolExecutor
from tests.workflow_fakes import ScriptedWorkflowModel, workflow_call, workflow_stop


class CountingExecutor(ToolExecutor):
    """仍执行真实工具，只记录逻辑调用次数。"""

    def __init__(self):
        """关闭重试以隔离循环行为。"""
        super().__init__(max_retries=0)
        self.calls = 0

    async def execute(self, call, registry):
        """记录逻辑申请并交给实际 Schema 校验和执行。"""
        self.calls += 1
        return await super().execute(call, registry)


def inputs():
    """返回独立的当前问题与系统提示。"""
    return [SystemMessage('查询工具后回答。'), HumanMessage('查询 A-42 订单和物流')]


def registry():
    """仅开放无需数据库的三个查询工具。"""
    return {tool.name: tool for tool in (query_order, query_logistics, query_product)}


@pytest.mark.asyncio
async def test_bare_two_calls_then_answer():
    """缺少第二轮回灌或最终收敛会丢失轨迹和答案。"""
    model = ScriptedWorkflowModel([workflow_call(), workflow_call('query_logistics', identifier='call_2'), workflow_stop()])
    result = await run_bare_agent(model, registry(), CountingExecutor(), inputs(), limits=AgentLimits())
    assert result.calls == ['query_order', 'query_logistics']
    assert len(model.tool_inputs[-1]) == 6
    assert [m.tool_call_id for m in model.tool_inputs[-1] if isinstance(m, ToolMessage)] == ['call_1', 'call_2']
    assert result.answer == '受控物流答案'
    assert result.stop_reason == 'completed'
    assert model.streams == 0
    assert model.bind_options[0]['parallel_tool_calls'] is False


@pytest.mark.asyncio
async def test_repeat_call_never_executes_twice():
    """相同工具与参数即使不同 ID 也不能再次执行。"""
    model = ScriptedWorkflowModel([workflow_call(), workflow_call(identifier='call_2')])
    executor = CountingExecutor()
    result = await run_bare_agent(model, registry(), executor, inputs(), limits=AgentLimits())
    assert result.stop_reason == 'repeat_call' and executor.calls == 1
    assert result.answer and result.answer != '受控物流答案'


@pytest.mark.asyncio
async def test_four_call_limit():
    """第五个不同申请不得执行，也不另加最终生成。"""
    model = ScriptedWorkflowModel([workflow_call(args={'order_id': f'A-{i}'}, identifier=f'call_{i}') for i in range(5)])
    executor = CountingExecutor()
    result = await run_bare_agent(model, registry(), executor, inputs(), limits=AgentLimits())
    assert executor.calls == 4 and result.stop_reason == 'step_limit'
    assert model.decisions <= 5 and model.streams == 0


@pytest.mark.asyncio
async def test_invalid_args_returns_matched_tool_message():
    """Schema 错误也必须回灌紧邻且匹配 ID 的工具失败结果。"""
    model = ScriptedWorkflowModel([workflow_call(args={'order_id': 42}), workflow_stop()])
    result = await run_bare_agent(model, registry(), CountingExecutor(), inputs(), limits=AgentLimits())
    message = model.tool_inputs[-1][-1]
    assert message.tool_call_id == 'call_1' and message.status == 'error'
    assert 'invalid_arguments' in message.content
    assert result.trace[0].outcome.attempts == 0


@pytest.mark.asyncio
async def test_insufficient_budget_prevents_decision_and_tool():
    """预算不足先于上游请求与执行器，不能把最终回答预算吃掉。"""
    model, executor = ScriptedWorkflowModel([workflow_call()]), CountingExecutor()
    result = await run_bare_agent(model, registry(), executor, inputs(), limits=AgentLimits(total_token_budget=100))
    assert result.stop_reason == 'token_budget'
    assert model.decisions == executor.calls == model.streams == 0


@pytest.mark.asyncio
async def test_reused_call_id_is_protocol_error():
    """不同参数也不能重用当前轮次的调用 ID。"""
    model = ScriptedWorkflowModel([workflow_call(), workflow_call('query_logistics')])
    executor = CountingExecutor()
    with pytest.raises(ServiceError):
        await run_bare_agent(model, registry(), executor, inputs(), limits=AgentLimits())
    assert executor.calls == 1


@pytest.mark.asyncio
async def test_cancel_propagates_before_tool():
    """取消等待模型时不执行任何工具且原样传播取消。"""
    model, executor = ScriptedWorkflowModel([workflow_call()], block=asyncio.Event()), CountingExecutor()
    task = asyncio.create_task(run_bare_agent(model, registry(), executor, inputs(), limits=AgentLimits()))
    await asyncio.sleep(0)
    task.cancel()
    with pytest.raises(asyncio.CancelledError):
        await task
    assert executor.calls == 0


def test_bare_has_no_langgraph_dependency():
    """裸循环不能偷偷依赖框架，限制只针对该模块导入。"""
    import app.agent.bare as bare
    tree = ast.parse(Path(bare.__file__).read_text(encoding='utf-8'))
    imported_by_bare = [node.module for node in ast.walk(tree) if isinstance(node, ast.ImportFrom)]
    imported_by_bare += [alias.name for node in ast.walk(tree) if isinstance(node, ast.Import) for alias in node.names]
    assert not any(name and name.startswith('langgraph') for name in imported_by_bare)


@pytest.mark.asyncio
@pytest.mark.parametrize('content,reason', [('', 'stop'), ('被截断答案', 'length'), ('正常答案', 'tool_calls')])
async def test_incomplete_final_text_is_rejected(content, reason):
    """空答案与非 stop 结束不能冒充已完成答案。"""
    from langchain_core.messages import AIMessage
    model = ScriptedWorkflowModel([AIMessage(content, response_metadata={'finish_reason': reason})])
    with pytest.raises(ServiceError):
        await run_bare_agent(model, registry(), CountingExecutor(), inputs(), limits=AgentLimits())


@pytest.mark.asyncio
async def test_excess_actual_usage_stops_before_execution():
    """上游实际计量超出预估时不得继续执行工具。"""
    reply = workflow_call()
    reply.usage_metadata = {'input_tokens': 32000, 'output_tokens': 1, 'total_tokens': 32001}
    model, executor = ScriptedWorkflowModel([reply]), CountingExecutor()
    result = await run_bare_agent(model, registry(), executor, inputs(), limits=AgentLimits())
    assert result.stop_reason == 'token_budget' and executor.calls == 0
    assert result.usage.spent == 32001 and result.usage.remaining == 0


def test_default_demo_has_two_steps_and_no_live_setup(capsys, monkeypatch):
    """默认 CLI 不能加载真实模型配置，输出受控两步答案。"""
    from app.agent import cli
    def forbidden_live_setup():
        """默认命令触及真实配置时立即暴露错误路径。"""
        raise AssertionError('default demo attempted live setup')
    monkeypatch.setattr(cli, 'load_settings', forbidden_live_setup)
    assert cli.main(['demo']) == 0
    output = capsys.readouterr().out
    assert '1. query_order' in output and '2. query_logistics' in output
    assert '受控物流答案' in output and 'completed' in output


def test_live_requires_explicit_question():
    """真实演示缺问题时必须在加载模型配置前拒绝。"""
    from app.agent import cli
    with pytest.raises(SystemExit) as error:
        cli.main(['demo', '--live'])
    assert error.value.code == 2


@pytest.mark.asyncio
async def test_actual_usage_cannot_spend_final_reserve():
    """实际 usage 吃掉最终保留额度时不再执行工具。"""
    reply = workflow_call()
    reply.usage_metadata = {'input_tokens': 31900, 'output_tokens': 0, 'total_tokens': 31900}
    executor = CountingExecutor()
    result = await run_bare_agent(ScriptedWorkflowModel([reply]), registry(), executor, inputs(), limits=AgentLimits())
    assert executor.calls == 0 and result.stop_reason == 'token_budget'


@pytest.mark.asyncio
async def test_overbudget_no_tool_reply_is_not_completed():
    """实际超预算的无工具回复不能标成正常完成。"""
    reply = workflow_stop()
    reply.usage_metadata = {'input_tokens': 32000, 'output_tokens': 1, 'total_tokens': 32001}
    result = await run_bare_agent(ScriptedWorkflowModel([reply]), registry(), CountingExecutor(), inputs(), limits=AgentLimits())
    assert result.stop_reason == 'token_budget' and result.answer != '受控物流答案'


@pytest.mark.asyncio
async def test_whole_loop_has_240_second_timeout(monkeypatch):
    """阻塞模型也必须由整轮期限终止，不需要真实等待四分钟。"""
    original_timeout = asyncio.timeout
    configured = []
    def short_timeout(seconds):
        """保留真实 asyncio 期限语义，只缩短测试钟。"""
        configured.append(seconds)
        return original_timeout(0.01)
    monkeypatch.setattr(asyncio, 'timeout', short_timeout)
    model = ScriptedWorkflowModel([workflow_call()], block=asyncio.Event())
    task = asyncio.create_task(run_bare_agent(model, registry(), CountingExecutor(), inputs(), limits=AgentLimits()))
    done, _ = await asyncio.wait({task}, timeout=0.1)
    if not done:
        task.cancel()
        await asyncio.gather(task, return_exceptions=True)
    assert done and configured == [240]
    with pytest.raises(TimeoutError):
        await task
@pytest.mark.parametrize('limit_field', ['max_tokens', 'max_completion_tokens'])
async def test_live_demo_serializes_visible_final_ceiling(monkeypatch, limit_field):
    """live入口只用离线HTTP传输，直接收敛请求必须限512且不能追加最终调用。"""
    import json
    import httpx
    from app.agent import cli
    from tests.fakes import fake_settings
    settings = fake_settings(llm_token_limit_field=limit_field)
    monkeypatch.setattr(cli, 'load_settings', lambda: settings)
    payloads = []
    def respond(request):
        """观察真实模型序列化报文，返回合法无工具最终响应。"""
        payloads.append(json.loads(request.content))
        return httpx.Response(200, json={'id': 'offline-final', 'object': 'chat.completion',
            'created': 1, 'model': settings.llm_model,
            'choices': [{'index': 0, 'finish_reason': 'stop',
                'message': {'role': 'assistant', 'content': '请提供订单号。'}}]})
    client_type = httpx.AsyncClient
    class OfflineClient(client_type):
        """保持真实客户端类型，仅将网络传输替换为离线响应。"""
        def __init__(self, *args, **kwargs):
            """禁止触碰实际端点及.env，兼容模型工厂的客户端类型检查。"""
            super().__init__(*args, **{**kwargs, 'transport': httpx.MockTransport(respond), 'trust_env': False})
    monkeypatch.setattr(httpx, 'AsyncClient', OfflineClient)
    result = await cli._demo(True, '请查订单')
    assert result.answer == '请提供订单号。' and result.stop_reason == 'completed'
    assert len(payloads) == 1 and payloads[0][limit_field] == 512
    assert payloads[0]['parallel_tool_calls'] is False
    assert result.usage.estimated >= 2048
