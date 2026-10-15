"""最新根待选投影及受控恢复入口，不执行历史根。"""
from copy import deepcopy

from app.core.errors import ServiceError
from app.repositories.conversations import _conversation_id
from app.workflow.persistence import checkpoint_config


def pending_selection(snapshot, conversation_id):
    """仅投影实际持久化的根中断，禁止把失败节点当作待办。"""
    state = snapshot.values
    selection = state.get('order_selection') or {}
    config = snapshot.config.get('configurable', {})
    interrupts = [item for task in snapshot.tasks for item in task.interrupts]
    if (state.get('state_version') != 2 or state.get('turn_status') != 'awaiting_order'
            or state.get('conversation_id') != conversation_id
            or config.get('thread_id') != conversation_id or config.get('checkpoint_ns') != ''
            or tuple(snapshot.next) != ('await_order_selection',) or len(interrupts) != 1
            or selection.get('selected_order_id') is not None or not selection.get('cards')
            or selection.get('turn_id') != state.get('user_message_id')
            or interrupts[0].value != {key: selection.get(key) for key in ('turn_id', 'selection_id', 'cards')}):
        return None
    return deepcopy({'turn_id': selection['turn_id'], 'selection_id': selection['selection_id'],
        'checkpoint_id': config['checkpoint_id'], 'prompt': '请选择本次需要办理的演示订单。',
        'cards': selection['cards']})


class OrderActionService:
    """复用聊天服务的锁、SQL权威、图和托管响应生命周期。"""
    def __init__(self, service):
        """保存应用拥有的同一聊天服务。"""
        self.service = service

    async def pending(self, conversation_id: str) -> dict:
        """刷新只读当前根，GET不要求JSON请求体。"""
        _conversation_id(conversation_id)
        await self.service.repository.require_open(conversation_id)
        snapshot = await self.service.graph.aget_state(checkpoint_config(conversation_id))
        return {'pending': pending_selection(snapshot, conversation_id)}

    async def select(self, conversation_id, payload):
        """SSE开始前执行完整恢复预检，异常交给HTTP错误投影。"""
        return await self.service.prepare_resume(conversation_id, payload)
