"""Feedback is bound to a durable completed root and its original SQL pair."""
from contextlib import aclosing
from uuid import UUID

from app.core.errors import ServiceError
from app.flywheel.snapshots import snapshot_from_state
from app.flywheel.types import PoolInput, database_id
from app.workflow.persistence import completed_history_roots


class FeedbackService:
    def __init__(self, checkpointer, conversations, pool):
        self.checkpointer, self.conversations, self.pool = checkpointer, conversations, pool

    async def submit(self, conversation_id, *, user_id, assistant_message_id, checkpoint_id=None):
        try:
            database_id(conversation_id)
            database_id(assistant_message_id)
            if checkpoint_id is not None and str(UUID(checkpoint_id)) != checkpoint_id:
                raise ValueError('Invalid checkpoint')
        except (ValueError, TypeError, AttributeError):
            raise ServiceError('invalid_request', '反馈定位参数无效。', 422) from None
        if await self.conversations.get_user_id(conversation_id) != user_id:
            raise ServiceError('conversation_not_found', '会话不存在。', 404)
        original = None
        # Finish and close the saver cursor before any other operation. In
        # particular, never reenter aget_tuple while alist holds its lock.
        if self.checkpointer is not None:
            async with aclosing(completed_history_roots(self.checkpointer, conversation_id)) as roots:
                async for identifier, state in roots:
                    if (state.get('final_message_id') == assistant_message_id
                            and (checkpoint_id is None or checkpoint_id == identifier)):
                        original = state
                        break
        if original is None:
            raise ServiceError('feedback_conflict', '原轮完成记录无法核验，暂不能提交反馈。', 409)
        try:
            user_message_id = int(database_id(original.get('user_message_id')))
        except ValueError:
            raise ServiceError('feedback_conflict', '原轮消息身份无法核验。', 409) from None
        rows = await self.conversations.load_messages(conversation_id)
        user = next((row for row in rows if row.id == user_message_id), None)
        assistant_id = int(assistant_message_id)
        assistant = next((row for row in rows if row.id == assistant_id), None)
        if (user is None or user.role != 'user' or not isinstance(user.content, str) or not user.content.strip()
                or user.content != original.get('raw_question') or assistant is None
                or assistant.role != 'assistant' or assistant.tool_calls is not None
                or not isinstance(assistant.content, str) or not assistant.content.strip()
                or assistant.content != original.get('final_answer') or user.id >= assistant_id
                or any(row.role == 'user' and user.id < row.id < assistant_id for row in rows)):
            raise ServiceError('feedback_conflict', '原轮问答与持久化消息不匹配。', 409)
        try:
            snapshot = snapshot_from_state(original)
        except (ValueError, TypeError, KeyError):
            raise ServiceError('feedback_conflict', '原轮证据版本无法核验。', 409) from None
        return await self.pool.enqueue(PoolInput(conversation_id=conversation_id,
            user_message_id=str(user.id), assistant_message_id=assistant_message_id,
            raw_question=user.content, source='user_feedback', reason='用户反馈本轮未解决', snapshot=snapshot))
