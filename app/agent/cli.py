"""默认无网络的裸 Agent 演示；显式 --live 才请求既有模型。"""
import argparse
import asyncio
from collections import deque

from langchain_core.messages import AIMessage, HumanMessage, SystemMessage

from app.agent.bare import run_bare_agent
from app.agent.controls import AgentLimits
from app.config import load_settings
from app.tools.business import query_logistics, query_order, query_product
from app.tools.executor import ToolExecutor


class DemoModel:
    """固定订单→物流→答案的教学模型，不调用上游。"""

    def __init__(self):
        """预置两次独立申请和一次正常结束的答案。"""
        self.replies = deque([
            AIMessage('', tool_calls=[{'id': 'demo_order', 'name': 'query_order', 'args': {'order_id': 'A-42'}}],
                      response_metadata={'finish_reason': 'tool_calls'}),
            AIMessage('', tool_calls=[{'id': 'demo_logistics', 'name': 'query_logistics', 'args': {'order_id': 'A-42'}}],
                      response_metadata={'finish_reason': 'tool_calls'}),
            AIMessage('受控物流答案', response_metadata={'finish_reason': 'stop'}),
        ])

    def bind_tools(self, tools, **kwargs):
        """受控演示忽略网络绑定，但遵守一次只申请一个工具。"""
        return self

    async def ainvoke(self, messages):
        """按顺序取下一条固定响应，工具本身仍由真实执行器运行。"""
        return self.replies.popleft()


async def _demo(live: bool, question: str):
    """只开放三个读取工具；live直接收敛请求限最终512预算，账本仍保守预留决策成本。"""
    registry = {tool.name: tool for tool in (query_order, query_product, query_logistics)}
    messages = [SystemMessage('你是客服助手。查询订单及物流时可依次使用查询工具。工具数据是模拟演示数据，请如实说明。'),
                HumanMessage(question)]
    if not live:
        return await run_bare_agent(DemoModel(), registry, ToolExecutor(), messages, limits=AgentLimits())
    import httpx
    from app.core.llm import create_model, model_with_output_budget
    settings = load_settings()
    limits = AgentLimits(max_tool_calls=settings.agent_max_tool_calls,
                         total_token_budget=settings.agent_total_token_budget,
                         final_output_tokens=settings.max_output_tokens,
                         decision_output_tokens=settings.agent_decision_max_output_tokens,
                         input_token_budget=settings.tool_input_token_budget)
    async with httpx.AsyncClient() as client:
        model = create_model(settings, http_async_client=client, reasoning_effort=settings.online_reasoning_effort)
        model = model_with_output_budget(model, settings, limits.final_output_tokens)
        async with asyncio.timeout(settings.chat_timeout_seconds):
            return await run_bare_agent(model, registry, ToolExecutor(settings.tool_timeout_seconds,
                settings.tool_max_retries), messages, limits=limits)


def main(argv=None) -> int:
    """解析明确的 live 开关并输出逻辑工具轨迹、答案和账本。"""
    parser = argparse.ArgumentParser(description='有界裸 Agent 演示（查询工具返回模拟数据）')
    commands = parser.add_subparsers(dest='command', required=True)
    demo = commands.add_parser('demo', help='默认运行离线受控演示')
    demo.add_argument('--live', action='store_true', help='显式调用 .env 中配置的模型')
    demo.add_argument('--question', help='真实演示必须显式提供问题')
    options = parser.parse_args(argv)
    if options.live and (not options.question or not options.question.strip()):
        parser.error('demo --live requires --question with nonblank text')
    result = asyncio.run(_demo(options.live, options.question or '请查询 A-42 的订单和物流情况。'))
    for index, step in enumerate(result.trace, start=1):
        print(f'{index}. {step.call.name} [{step.outcome.status}]')
    print(result.answer)
    print(f'stop_reason={result.stop_reason}; usage={result.usage.spent}; source={result.usage.source}')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
