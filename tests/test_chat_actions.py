"""确认动作通过真实图、官方 SQLite 与工具执行器，只替换 SQL 边界。"""
from contextlib import asynccontextmanager
from dataclasses import replace
from types import SimpleNamespace

import httpx
import pytest
from langchain_core.messages import AIMessage

from app.core.errors import ServiceError
from app.db.models import Conversation, Message, Ticket
from app.repositories.tickets import TicketRepository
from app.tools.registry import build_registry
from app.workflow.persistence import checkpoint_config
from tests.fakes import FAQStub, decode_sse
from tests.test_workflow_api import Store, intent, workflow_app
from tests.workflow_fakes import ScriptedWorkflowModel


class Tickets:
    """模拟外部 SQL 幂等边界，执行器与工具闭包保持真实。"""
    def __init__(self):
        """记录可信工单字段与稳定调用身份。"""
        self.rows = {}
        self.status = '进行中'
        self.calls = []

    async def create(self, **fields):
        """复用同一调用身份，仅在尚无工单时拒绝已结束会话。"""
        self.calls.append(fields)
        key = fields['tool_call_id']
        if key not in self.rows:
            if self.status == '已结束':
                raise ServiceError('conversation_ended', '会话已经结束。', 409)
            self.rows[key] = {'ticket_no': 'T00000000000000000000000000000001', 'status': '待处理'}
        return self.rows[key]


@asynccontextmanager
async def offered_app(tmp_path, *, question=' 我要投诉，商品坏了。 ', intent_name='投诉', **settings):
    """真实 Workflow 产生完成动作，注册表仅替换外部工单 SQL。"""
    tickets, store = Tickets(), Store()
    model = ScriptedWorkflowModel(intent_replies=[intent(intent_name)])
    async with workflow_app(tmp_path, model=model, store=store, **settings) as app:
        # 生命周期建立完成后仍从同一个服务注册表读取，避免动作另建闭包。
        app.state.chat_service.registry_factory = lambda context: build_registry(FAQStub(), tickets, context)
        async with httpx.AsyncClient(transport=httpx.ASGITransport(app), base_url='http://127.0.0.1:8000') as client:
            reply = await client.post('/api/chat', json={'conversation_id': '1', 'message': question})
            actions = next(data for name, data in decode_sse(reply.text) if name == 'actions')
            payload = {key: actions[key] for key in ('assistant_message_id', 'checkpoint_id')}
            payload.update(ticket_type='投诉', description=question[:2000])
            yield app, client, tickets, store, payload


async def confirm(client, payload, *, conversation_id='1', **kwargs):
    """经完整 HTTP 入口提交回复定位与用户手填工单内容。"""
    return await client.post(f'/api/conversations/{conversation_id}/actions/ticket', json=payload, **kwargs)


async def test_suggestion_creates_nothing(tmp_path):
    """建议出现时不执行工具，只有明确确认后才产生一张工单。"""
    async with offered_app(tmp_path) as (_, client, tickets, _, payload):
        assert tickets.rows == {} and tickets.calls == []
        response = await confirm(client, payload)
        assert response.status_code == 200
        assert len(tickets.rows) == 1


async def test_old_completed_offer_after_new_message(tmp_path):
    """新的无动作问候不能覆盖旧完成快照的原话或 SQL 用户身份。"""
    async with offered_app(tmp_path) as (app, client, tickets, _, payload):
        await client.post('/api/chat', json={'conversation_id': '1', 'message': '你好'})
        calls, original = [], app.state.chat_service.executor.execute

        async def record_execute(call, registry):
            """观察真实执行器边界的申请，随后仍执行既有工具。"""
            calls.append(call)
            return await original(call, registry)

        app.state.chat_service.executor.execute = record_execute
        response = await confirm(client, payload)
        assert response.status_code == 200
        assert calls[0].name == 'create_ticket' and calls[0].id == 'ui_ticket:2'
        assert calls[0].args == {'description': ' 我要投诉，商品坏了。 ', 'ticket_type': '投诉'}
        assert tickets.calls[-1] == {'conversation_id': '1', 'user_message_id': 1,
            'tool_call_id': 'ui_ticket:2', 'description': ' 我要投诉，商品坏了。 ', 'ticket_type': '投诉'}


async def test_cross_conversation_checkpoint_denied(tmp_path):
    """其他会话不能使用旧会话的完成快照创建工单。"""
    async with offered_app(tmp_path) as (_, client, tickets, _, payload):
        response = await confirm(client, payload, conversation_id='2')
        assert response.status_code in (403, 404, 409, 422)
        assert tickets.rows == {} and tickets.calls == []


async def test_duplicate_confirmation_returns_one_ticket(tmp_path):
    """完成后重复确认（包括已结束会话）返回原编号且不重复创建。"""
    async with offered_app(tmp_path) as (_, client, tickets, _, payload):
        first = await confirm(client, payload)
        tickets.status = '已结束'
        second = await confirm(client, payload)
        assert first.status_code == second.status_code == 200
        assert first.json()['ticket_no'] == second.json()['ticket_no'] and len(tickets.rows) == 1


@pytest.mark.parametrize('mutation', [
    {'description': ' '}, {'question': '伪造'}, {'ticket_type': '其他'}, {'user_message_id': '1'},
    {'tool_name': 'create_ticket'}, {'assistant_message_id': 2}, {'assistant_message_id': '02'},
    {'assistant_message_id': '18446744073709551616'}, {'checkpoint_id': 'x' * 129},
    {'checkpoint_id': 'not-a-uuid'}, {'assistant_message_id': '1'},
])
async def test_extra_or_bad_identity_writes_nothing(tmp_path, mutation):
    """非法业务输入、额外字段和伪造定位字段均在工具执行前失败。"""
    async with offered_app(tmp_path) as (_, client, tickets, _, payload):
        response = await confirm(client, {**payload, **mutation})
        assert response.status_code == 422
        assert tickets.rows == {} and tickets.calls == []
        assert '伪造' not in response.text


@pytest.mark.parametrize('origin', ['https://external.invalid', 'null', 'http://localhost:8000'])
async def test_extra_or_bad_origin_writes_nothing(tmp_path, origin):
    """跨源或 null 来源必须拒绝，且不得执行工单工具。"""
    async with offered_app(tmp_path) as (_, client, tickets, _, payload):
        response = await confirm(client, payload, headers={'Origin': origin})
        assert response.status_code == 403
        assert tickets.calls == [] and tickets.rows == {}


async def test_valid_same_origin_and_busy_lease(tmp_path):
    """同源合法确认与聊天共用 lease，忙碌失败后仍能成功确认。"""
    async with offered_app(tmp_path) as (app, client, tickets, _, payload):
        lease = app.state.chat_service.locks.acquire('1')
        response = await confirm(client, payload)
        lease.release()
        assert response.status_code == 409 and tickets.calls == []
        response = await confirm(client, payload, headers={'Origin': 'http://127.0.0.1:8000'})
        assert response.status_code == 200


async def test_untrusted_host_and_non_json_denied(tmp_path):
    """无 Origin 仅接受明确 loopback Host，写接口拒绝非 JSON。"""
    async with offered_app(tmp_path) as (_, client, tickets, _, payload):
        response = await confirm(client, payload, headers={'Host': 'attacker.invalid'})
        assert response.status_code == 403
        response = await confirm(client, payload, headers={'Host': 'attacker.invalid', 'Origin': 'http://attacker.invalid'})
        assert response.status_code == 403
        response = await client.post('/api/conversations/1/actions/ticket', content='{}', headers={'content-type': 'text/plain'})
        assert response.status_code == 415 and tickets.calls == []


async def test_localhost_and_ipv6_same_origin(tmp_path):
    """明确的 localhost 和 IPv6 loopback 同源来源也允许确认。"""
    async with offered_app(tmp_path) as (_, client, tickets, _, payload):
        for host in ('localhost:8000', '[::1]:8000'):
            response = await confirm(client, payload, headers={'Host': host, 'Origin': f'http://{host}'})
            assert response.status_code == 200
        assert len(tickets.rows) == 1


@pytest.mark.parametrize('patch', [
    {'turn_status': 'pending'}, {'turn_status': 'failed'}, {'suggested_actions': ['handoff']},
    {'suggested_actions': []}, {'final_message_id': '100'}, {'user_message_id': '100'},
    {'conversation_id': '2'},
])
async def test_ineligible_checkpoint_writes_nothing(tmp_path, patch):
    """存在的根快照也必须完成且提供工单选项，所有身份必须匹配。"""
    async with offered_app(tmp_path) as (app, client, tickets, _, payload):
        config = await app.state.chat_service.graph.aupdate_state(checkpoint_config('1'), patch)
        response = await confirm(client, {**payload, 'checkpoint_id': config['configurable']['checkpoint_id']})
        assert response.status_code == 422 and tickets.calls == []


async def test_pending_root_checkpoint_writes_nothing(tmp_path):
    """真正的待执行旧根检查点不能借完成回复 ID 获得创建权限。"""
    async with offered_app(tmp_path) as (app, client, tickets, _, payload):
        graph = app.state.chat_service.graph
        async for snapshot in graph.aget_state_history(checkpoint_config('1')):
            if snapshot.next:
                response = await confirm(client, {**payload,
                    'checkpoint_id': snapshot.config['configurable']['checkpoint_id']})
                assert response.status_code == 422 and tickets.calls == []
                break
        else:
            pytest.fail('真实 Workflow 应保留待执行根快照')


@pytest.mark.parametrize('intent_name', ['投诉', '退款退货', '售后', '订单'])
async def test_user_selected_ticket_type_overrides_intent(tmp_path, intent_name):
    """可信意图只参与路由，用户所选的合法工单类别不得被自动覆盖。"""
    async with offered_app(tmp_path) as (app, client, tickets, _, payload):
        config = await app.state.chat_service.graph.aupdate_state(checkpoint_config('1'), {'intent': intent_name})
        response = await confirm(client, {**payload, 'ticket_type': '咨询',
            'checkpoint_id': config['configurable']['checkpoint_id']})
        assert response.status_code == 200 and tickets.calls[-1]['ticket_type'] == '咨询'


async def test_long_original_question_does_not_override_manual_description(tmp_path):
    """原话即使超长，也应保存用户重新填写的描述而不擅自截断原话建单。"""
    # 此例验证原话与手填描述的绑定；为旧注入路径的完整系统提示和2104字符原话留足输入空间。
    async with offered_app(tmp_path, question='我要投诉' + 'broken ' * 300,
                           tool_input_token_budget=9000) as (_, client, tickets, _, payload):
        response = await confirm(client, {**payload, 'description': '设备故障，请协助维修。'})
        assert response.status_code == 200
        description = tickets.calls[-1]['description']
        assert description == '设备故障，请协助维修。'


async def test_ended_conversation_cannot_create_new_ticket(tmp_path):
    """已结束会话尚无幂等结果时拒绝首次确认，并释放同一 lease。"""
    async with offered_app(tmp_path) as (app, client, tickets, _, payload):
        tickets.status = '已结束'
        response = await confirm(client, payload)
        assert response.status_code == 409 and tickets.rows == {}
        app.state.chat_service.locks.acquire('1').release()


async def test_snapshot_failure_is_sanitized(tmp_path, monkeypatch):
    """持久化异常不泄露原文，且失败后归还会话占用。"""
    async with offered_app(tmp_path) as (app, client, tickets, _, payload):
        async def fail_read(*args, **kwargs):
            """只替换失败的外部检查点读取边界。"""
            raise RuntimeError('SECRET checkpoint path')

        monkeypatch.setattr(app.state.chat_service.graph, 'aget_state', fail_read)
        response = await confirm(client, payload)
        assert response.status_code == 503 and 'SECRET' not in response.text and tickets.calls == []
        app.state.chat_service.locks.acquire('1').release()


async def test_assistant_sql_row_belongs_to_original_turn(tmp_path):
    """原最终答复删除或原轮中插入新用户时均拒绝，避免用户身份错绑。"""
    async with offered_app(tmp_path) as (app, client, tickets, store, payload):
        original = list(store.rows['1'])
        store.rows['1'] = [original[0]]
        assert (await confirm(client, payload)).status_code == 422
        store.rows['1'] = [original[0], replace(original[0], id=2), replace(original[1], id=3)]
        config = await app.state.chat_service.graph.aupdate_state(checkpoint_config('1'), {'final_message_id': '3'})
        changed = {**payload, 'assistant_message_id': '3', 'checkpoint_id': config['configurable']['checkpoint_id']}
        assert (await confirm(client, changed)).status_code == 422
        assert tickets.calls == []


async def test_sql_ownership_and_original_question_checked(tmp_path):
    """SQL 中原用户和最终回复必须完整匹配，不能仅凭快照创建工单。"""
    async with offered_app(tmp_path) as (_, client, tickets, store, payload):
        store.rows['1'][0] = replace(store.rows['1'][0], content='被替换的原话')
        response = await confirm(client, payload)
        assert response.status_code == 422 and tickets.calls == []


async def test_ticket_does_not_transfer_conversation():
    """真实仓储建工单不得改变会话状态；仅替换 SQL 连接与持久化边界。"""
    conversation = Conversation(id=1, user_id='offline', status='进行中')
    user = Message(id=1, conversation_id=1, role='user', content='损坏')
    rows = {}

    class Session:
        """镜像仓储使用的短事务与 ORM 对象行为。"""
        async def __aenter__(self):
            """提供可重复进入的事务上下文。"""
            return self

        async def __aexit__(self, *args):
            """结束离线事务，异常按正常上下文协议传播。"""
            return False

        def begin(self):
            """提供短事务入口。"""
            return self

        async def scalar(self, statement):
            """返回锁定的本会话 ORM 对象。"""
            return conversation

        async def get(self, entity, key):
            """读取真实用户或已存工单对象。"""
            return user if entity is Message else rows.get(key)

        def add(self, row):
            """保留仓储新增的真实 ORM 工单对象。"""
            rows[row.ticket_no] = row

        async def flush(self):
            """镜像无额外副作用的刷新边界。"""
            return None

        async def refresh(self, row, **kwargs):
            """镜像 MySQL 服务端默认工单状态。"""
            row.status = '待处理'

    repository = TicketRepository(SimpleNamespace(session=Session))
    result = await repository.create(conversation_id='1', user_message_id=1, tool_call_id='ui_ticket:2',
        description='损坏', ticket_type='售后')
    assert result['status'] == '待处理' and len(rows) == 1
    assert conversation.status == '进行中'


async def test_failed_final_root_cannot_authorize_ticket(tmp_path):
    """即使最新aget_state投影pending writes为completed，历史定位仍不可创建工单。"""
    from langgraph.checkpoint.sqlite.aio import AsyncSqliteSaver
    class Saver(AsyncSqliteSaver):
        """实际saver只拒绝最终completed写入。"""
        async def aput(self, config, checkpoint, metadata, new_versions):
            """SQL提交之后留下真实pending writes，复现许可危险边界。"""
            if checkpoint['channel_values'].get('turn_status') == 'completed':
                raise OSError('controlled final save failure')
            return await super().aput(config, checkpoint, metadata, new_versions)
    tickets, store = Tickets(), Store()
    async with Saver.from_conn_string(str(tmp_path / 'failed-ticket.sqlite')) as saver:
        async with workflow_app(tmp_path, model=ScriptedWorkflowModel(intent_replies=[intent('投诉')]),
                store=store, saver=saver) as app:
            service = app.state.chat_service
            service.registry_factory = lambda context: build_registry(FAQStub(), tickets, context)
            async with httpx.AsyncClient(transport=httpx.ASGITransport(app), base_url='http://localhost') as client:
                response = await client.post('/api/chat', json={'conversation_id': '1', 'message': '我要投诉'})
                assert decode_sse(response.text)[-1][0] == 'error'
                projected = await service.graph.aget_state(checkpoint_config('1'))
                assert projected.values['turn_status'] == 'completed'
                result = await confirm(client, {'assistant_message_id': projected.values['final_message_id'],
                    'checkpoint_id': projected.config['configurable']['checkpoint_id'],
                    'ticket_type': '投诉', 'description': '投诉'})
                assert result.status_code == 422 and tickets.rows == {} and tickets.calls == []
