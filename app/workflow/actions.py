"""确认工单服务：只读历史完成快照，复用既有受控工具执行。"""
from app.core.errors import ServiceError
from app.repositories.conversations import _conversation_id
from app.schemas.chat_actions import TicketActionRequest
from app.tools.types import ToolCall, ToolContext
from app.workflow.persistence import checkpoint_config


class TicketActionService:
    """与聊天共用会话占用，业务身份仅来自快照和 SQL 记录。"""
    def __init__(self, graph, repository, registry_factory, executor, locks):
        """保存外部持有的图、仓储、工具执行器和同一会话锁服务。"""
        self.graph, self.repository, self.registry_factory = graph, repository, registry_factory
        self.executor, self.locks = executor, locks

    async def create_ticket(self, conversation_id: str, payload: TicketActionRequest) -> dict:
        """核对指定根完成快照及原轮 SQL 所属关系，执行稳定幂等确认。"""
        _conversation_id(conversation_id)
        lease = self.locks.acquire(conversation_id)
        try:
            snapshot = await self.graph.aget_state(checkpoint_config(conversation_id, checkpoint_id=payload.checkpoint_id))
            state = snapshot.values
            saved_config = snapshot.config.get('configurable', {})
            if (not state or saved_config.get('thread_id') != conversation_id
                    or saved_config.get('checkpoint_ns') != ''
                    or saved_config.get('checkpoint_id') != payload.checkpoint_id):
                raise ServiceError('action_not_found', '完成快照不存在。', 404)
            if (snapshot.next or state.get('turn_status') != 'completed'
                    or state.get('conversation_id') != conversation_id
                    or state.get('final_message_id') != payload.assistant_message_id
                    or 'create_ticket' not in state.get('suggested_actions', [])):
                raise ServiceError('invalid_action', '该回复不允许创建工单。', 422)
            try:
                user_id = _conversation_id(state.get('user_message_id'))
            except ServiceError:
                raise ServiceError('invalid_action', '该回复不允许创建工单。', 422) from None
            # load_messages 的 SQL WHERE 会话过滤确保两条记录均归属当前会话。
            rows = await self.repository.load_messages(conversation_id)
            user = next((row for row in rows if row.id == user_id), None)
            assistant_id = int(payload.assistant_message_id)
            assistant = next((row for row in rows if row.id == assistant_id), None)
            if (user is None or user.role != 'user' or user.content != state.get('raw_question')
                    or not isinstance(user.content, str) or not user.content.strip()
                    or assistant is None or assistant.role != 'assistant' or assistant.tool_calls is not None
                    or assistant.content != state.get('final_answer') or user_id >= assistant_id
                    or any(row.role == 'user' and user_id < row.id < assistant_id for row in rows)):
                raise ServiceError('invalid_action', '回复与原用户消息不匹配。', 422)
            description = user.content
            marker = '…[原文已截取]'
            if len(description) > 2000:
                description = description[:2000 - len(marker)] + marker
            intent = state.get('intent')
            ticket_type = '投诉' if intent == '投诉' else '售后' if intent in ('退款退货', '售后') else '咨询'
            registry = self.registry_factory(ToolContext(conversation_id, user_id, user.content, state.get('category')))
            outcome = await self.executor.execute(ToolCall(f'ui_ticket:{payload.assistant_message_id}', 'create_ticket',
                {'description': description, 'ticket_type': ticket_type}), registry)
            if outcome.status != 'success':
                code = outcome.content.get('error', {}).get('code', 'tool_execution_error')
                raise ServiceError(code, '工单暂时无法创建，请稍后重试。', 503)
            result = outcome.content
            if (not isinstance(result.get('ticket_no'), str) or result.get('status') not in ('待处理', '已处理')):
                raise ServiceError('tool_execution_error', '工单暂时无法创建，请稍后重试。', 503)
            return {'ticket_no': result['ticket_no'], 'status': result['status']}
        finally:
            lease.release()
