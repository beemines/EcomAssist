"""从实际阶段前缀及显式预留倒推共享历史；纯计算，启动不请求上游。"""
from collections.abc import Mapping, Sequence
from typing import TYPE_CHECKING

from langchain_core.messages import HumanMessage, SystemMessage

from app.context.tokens import ESTIMATOR_VERSION, estimate_payload
from app.context.types import ContextBudget, PhaseOverheads

if TYPE_CHECKING:
    from app.config import Settings


def derive_budget(settings: 'Settings', phases: Sequence[PhaseOverheads], *,
                  steady_turn_tokens: int, minimum_turn_tokens: int) -> ContextBudget:
    """T取固定完整业务轮次最大值，最低轮次取最小值，由调用方提供。"""
    if (type(steady_turn_tokens) is not int or type(minimum_turn_tokens) is not int
            or not 0 < minimum_turn_tokens <= steady_turn_tokens):
        raise ValueError('Business fixture costs must be positive ordered integers.')
    if not phases or len({phase.name for phase in phases}) != len(phases):
        raise ValueError('Context requires uniquely named complete phases.')
    window = settings.model_context_window
    evidence = min(6000, (window + 7) // 8)
    summary = min(2000, (window + 31) // 32)
    safety = max(256, (window * 3 + 99) // 100)
    costs = {}
    for phase in phases:
        deductions = {
            'F': estimate_payload([SystemMessage(phase.system)], phase.tools),
            'U': settings.max_user_input_tokens + estimate_payload([HumanMessage('')]),
            'E': evidence if phase.uses_evidence else 0,
            'G': summary,
            'V': phase.attachment_tokens,
            'O': phase.output_tokens,
            'M': safety,
            'P': settings.max_agent_steps * phase.tool_peak_tokens,
        }
        deductions['A'] = window - sum(deductions.values())
        costs[phase.name] = deductions
    desired = settings.context_target_rounds * steady_turn_tokens
    history = min(desired, min(phase['A'] for phase in costs.values()))
    layer1 = history * 70 // 100
    if history <= 0 or layer1 < minimum_turn_tokens:
        raise ValueError(f'上下文预算不足：层1无法容纳一轮完整业务对话；W={window}, phases={costs}')
    return ContextBudget(window, costs, desired, history, layer1, history - layer1,
                         evidence, summary, safety, ESTIMATOR_VERSION)


def derive_turn_token_limit(budget: ContextBudget, *, call_limits: Mapping[str, int]) -> int:
    """累计费用保护额度来自各阶段最大调用次数；M是余量，不计已花费用。

    必须显式列全阶段，允许某阶段最大次数为0，不能漏项或拼错阶段名称。
    P 已经是当前轮次瞬时峰值，不再乘工具次数。
    """
    if (set(call_limits) != set(budget.phases)
            or any(type(count) is not int or count < 0 for count in call_limits.values())
            or not any(call_limits.values())):
        raise ValueError('Call limits must cover all phases with nonnegative integer counts.')
    return sum(call_limits[name] * (budget.history + sum(cost[key] for key in ('F', 'U', 'E', 'G', 'V', 'O', 'P')))
               for name, cost in budget.phases.items())
