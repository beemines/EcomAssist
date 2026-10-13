"""确认动作真实 MySQL 与官方 SQLite 验收，显式 --run-mysql 才运行。"""
from uuid import uuid4

import pytest
import pytest_asyncio
from langchain_core.messages import AIMessage, HumanMessage
from langgraph.graph import END, START, StateGraph
from sqlalchemy import delete, func, select

from app.core.conversation_locks import ConversationLocks
from app.core.errors import ServiceError
from app.db.models import Conversation, Message, Ticket
from app.repositories.conversations import ConversationRepository
from app.repositories.tickets import TicketRepository
from app.schemas.chat_actions import TicketActionRequest
from app.tools.executor import ToolExecutor
from app.tools.registry import build_registry
from app.workflow.actions import TicketActionService
from app.workflow.persistence import checkpoint_config, open_checkpointer
from app.workflow.state import WorkflowState, new_turn_state
from tests.fakes import FAQStub


def completed_node(state):
    """保存测试已提交的完整状态，不调用模型或额外业务节点。"""
    return state


@pytest_asyncio.fixture
async def action_context(mysql_database, tmp_path):
    """创建独立真实会话和完成根快照，只清理当前夹具拥有的数据。"""
    repository = ConversationRepository(mysql_database)
    conversation_id = await repository.create('task7-test-' + uuid4().hex)
    try:
        user_id = await repository.append_message(conversation_id, HumanMessage('原用户投诉：商品损坏'))
        assistant_id = await repository.append_message(conversation_id, AIMessage('可以确认创建投诉工单。'))
        async with open_checkpointer(tmp_path / 'actions.sqlite') as saver:
            builder = StateGraph(WorkflowState)
            builder.add_node('completed', completed_node)
            builder.add_edge(START, 'completed')
            builder.add_edge('completed', END)
            graph = builder.compile(checkpointer=saver)
            state = new_turn_state(conversation_id=conversation_id, user_message_id=user_id,
                raw_question='原用户投诉：商品损坏', category=None, messages=[])
            state.update(intent='投诉', turn_status='completed', final_message_id=str(assistant_id),
                final_answer='可以确认创建投诉工单。', suggested_actions=['handoff', 'create_ticket'])
            await graph.ainvoke(state, checkpoint_config(conversation_id), durability='sync')
            snapshot = await graph.aget_state(checkpoint_config(conversation_id))
            tickets = TicketRepository(mysql_database)

            def registry(context):
                """使用真实工单工具闭包与执行器，仅 FAQ 使用无需调用的离线依赖。"""
                return build_registry(FAQStub(), tickets, context)

            service = TicketActionService(graph, repository, registry, ToolExecutor(), ConversationLocks())
            payload = TicketActionRequest(assistant_message_id=str(assistant_id),
                checkpoint_id=snapshot.config['configurable']['checkpoint_id'])
            yield conversation_id, user_id, graph, repository, service, payload
    finally:
        async with mysql_database.session() as session, session.begin():
            await session.execute(delete(Ticket).where(Ticket.conversation_id == int(conversation_id)))
            await session.execute(delete(Message).where(Message.conversation_id == int(conversation_id)))
            await session.execute(delete(Conversation).where(Conversation.id == int(conversation_id)))


async def test_old_completed_offer_is_idempotent_and_never_transfers(mysql_database, action_context):
    """新轮之后旧按钮仍取原SQL问题，多次确认仅一单且会话仍进行中。"""
    conversation_id, user_id, graph, repository, service, payload = action_context
    async with mysql_database.session() as session:
        assert await session.scalar(select(func.count()).select_from(Ticket).where(Ticket.conversation_id == int(conversation_id))) == 0
    new_user_id = await repository.append_message(conversation_id, HumanMessage('你好'))
    new_assistant_id = await repository.append_message(conversation_id, AIMessage('你好。'))
    fresh = new_turn_state(conversation_id=conversation_id, user_message_id=new_user_id,
        raw_question='你好', category=None, messages=[])
    fresh.update(turn_status='completed', final_message_id=str(new_assistant_id), final_answer='你好。')
    await graph.ainvoke(fresh, checkpoint_config(conversation_id), durability='sync')
    first = await service.create_ticket(conversation_id, payload)
    second = await service.create_ticket(conversation_id, payload)
    assert first == second
    async with mysql_database.session() as session, session.begin():
        assert await session.scalar(select(func.count()).select_from(Ticket).where(Ticket.conversation_id == int(conversation_id))) == 1
        row = await session.get(Ticket, first['ticket_no'])
        assert row.description == '原用户投诉：商品损坏' and row.ticket_type == '投诉'
        conversation = await session.get(Conversation, int(conversation_id))
        assert conversation.status == '进行中'
        conversation.status = '已结束'
    assert await service.create_ticket(conversation_id, payload) == first


async def test_ended_conversation_and_foreign_snapshot_write_nothing(mysql_database, action_context):
    """跨会话快照与结束后的首次确认均不能新增真实工单。"""
    conversation_id, _, _, _, service, payload = action_context
    with pytest.raises(ServiceError) as denied:
        await service.create_ticket(str(int(conversation_id) + 1), payload)
    assert denied.value.code == 'action_not_found'
    async with mysql_database.session() as session, session.begin():
        conversation = await session.get(Conversation, int(conversation_id))
        conversation.status = '已结束'
    with pytest.raises(ServiceError) as ended:
        await service.create_ticket(conversation_id, payload)
    assert ended.value.code == 'conversation_ended'
    async with mysql_database.session() as session:
        assert await session.scalar(select(func.count()).select_from(Ticket).where(Ticket.conversation_id == int(conversation_id))) == 0
