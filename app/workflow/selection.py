"""订单选择暂停接口；运行依赖不写入检查点。"""
import math
import time
from copy import deepcopy
from uuid import UUID, uuid4

from langgraph.runtime import Runtime
from langgraph.types import interrupt

from app.workflow.runtime import WorkflowRuntime
from app.workflow.state import OrderSelection, WorkflowState


async def prepare_order_selection(state: WorkflowState, runtime: Runtime[WorkflowRuntime]) -> dict:
    """准备固定候选，独立于会被恢复重放的暂停节点。"""
    context = runtime.context
    if not isinstance(context.user_id, str) or not context.user_id.strip():
        raise ValueError('trusted user_id is required for order selection')
    if context.order_provider is None:
        raise ValueError('order provider is required for order selection')
    orders = await context.order_provider.list_orders(user_id=context.user_id)
    selection: OrderSelection = {
        'selection_id': str(uuid4()),
        'turn_id': state['user_message_id'],
        'cards': [order.to_card() for order in orders],
        'selected_order_id': None,
        # 此处还没有暂停根快照，禁止预造checkpoint_id。
        'pause_checkpoint_id': None,
    }
    return {'order_selection': selection, 'turn_status': 'awaiting_order',
            'active_elapsed_seconds': active_elapsed(state, context)}


def active_elapsed(state, context):
    """将当前活动段与已消费基线合并；无运行计时的私有调用保留原值。"""
    if context.active_started_at is None:
        return state.get('active_elapsed_seconds', 0.0)
    return context.active_elapsed_baseline + max(0.0, time.monotonic() - context.active_started_at)


def await_order_selection(state: WorkflowState, runtime: Runtime[WorkflowRuntime]) -> dict:
    """暂停并接受本轮候选内的选择。"""
    selection = state.get('order_selection')
    if (state.get('state_version') != 2 or state.get('turn_status') != 'awaiting_order'
            or not isinstance(selection, dict)
            or not isinstance(selection.get('turn_id'), str) or not selection['turn_id'].strip()
            or selection.get('turn_id') != state.get('user_message_id')
            or not isinstance(selection.get('selection_id'), str)
            or selection.get('selected_order_id') is not None):
        raise ValueError('invalid pending order selection identity')
    # UUID检查只涉及已存纯数据，不产生新的选择身份或外部副作用。
    UUID(selection['selection_id'])
    cards = selection.get('cards')
    if (not isinstance(cards, list) or any(not isinstance(card, dict)
            or not isinstance(card.get('order_id'), str) or not card['order_id'] for card in cards)):
        raise ValueError('invalid pending order selection cards')
    response = interrupt({
        'turn_id': selection['turn_id'],
        'selection_id': selection['selection_id'],
        'cards': deepcopy(cards),
    })
    if (not isinstance(response, dict) or not isinstance(response.get('order_id'), str)
            or response['order_id'] not in {card['order_id'] for card in cards}):
        raise ValueError('order_id must belong to the saved selection candidates')
    pause_id = response.get('pause_checkpoint_id')
    if pause_id is not None and (not isinstance(pause_id, str) or not pause_id.strip()):
        raise ValueError('pause_checkpoint_id must be nonempty text')
    # 公开服务已核验的实际根身份仅作为回执保存；不修改执行配置。
    return {'order_selection': {**deepcopy(selection), 'selected_order_id': response['order_id'],
                               'pause_checkpoint_id': pause_id}, 'turn_status': 'running'}


def remaining_active_seconds(state: WorkflowState, *, limit: float = 240) -> float:
    """由已消费活动时长计算余量，不依赖墙钟。"""
    elapsed = state.get('active_elapsed_seconds', 0.0)
    if type(elapsed) not in (int, float) or not math.isfinite(elapsed) or elapsed < 0:
        raise ValueError('active elapsed seconds must be finite and nonnegative')
    if type(limit) not in (int, float) or not math.isfinite(limit) or limit < 0:
        raise ValueError('active time limit must be finite and nonnegative')
    return max(0.0, float(limit) - elapsed)
