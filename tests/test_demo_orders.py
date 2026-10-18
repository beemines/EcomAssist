# 稳定订单与可信身份读取的离线回归。
import json
from types import SimpleNamespace

import pytest
from pydantic import ValidationError
from sqlalchemy import text
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from app.orders.demo import DemoOrderProvider
from app.repositories.conversations import ConversationRepository
from app.tools.executor import ToolExecutor
from app.tools.registry import build_registry
from app.tools.types import ToolCall, ToolContext
from tests.fakes import FAQStub
from tests.test_business_tools import TicketStub


# 捕获订单列表与重复查询使用不同事实或不可序列化日期的回归。
@pytest.mark.asyncio
async def test_list_and_query_return_same_snapshot():
    provider = DemoOrderProvider()
    orders = await provider.list_orders(user_id='demo-user')
    assert len(orders) == 5
    first = await provider.get_order(user_id='demo-user', order_id='1001')
    second = await provider.get_order(user_id='demo-user', order_id='1001')
    assert first.model_dump() == second.model_dump() == orders[0].model_dump()
    assert first.as_of.isoformat() == '2026-10-15' and first.mock is True
    assert first.model == 'MH-LP200' and first.amount_cents > 0
    assert (first.as_of - first.signed_at).days == 2
    assert 'user_id' not in first.to_card()
    assert first.to_card()['signed_at'] == '2026-10-13'
    json.dumps(first.model_dump(mode='json'))
    assert (orders[1].as_of - orders[1].signed_at).days > 7
    assert orders[2].signed_at is None and orders[2].status == '待发货'
    assert orders[3].category == '个人定制商品'


# 捕获注入事实绕过固定演示日期、导致下游资格判断时间口径漂移的回归。
@pytest.mark.asyncio
async def test_fixture_rejects_different_business_date(tmp_path):
    order = await DemoOrderProvider().get_order(user_id='demo-user', order_id='1001')
    wrong_date = order.model_dump(mode='json')
    wrong_date['as_of'] = '2026-10-16'
    fixture = tmp_path / 'wrong-date.json'
    fixture.write_text(json.dumps({'orders': [wrong_date]}), encoding='utf-8')
    with pytest.raises(ValidationError, match='2026-10-15'):
        DemoOrderProvider(fixture)


# 捕获任意订单号被伪造为成功演示订单的回归。
@pytest.mark.asyncio
async def test_unknown_order_is_not_random_success():
    provider = DemoOrderProvider()
    assert await provider.get_order(user_id='demo-user', order_id='unknown') is None
    registry = build_registry(FAQStub(), TicketStub(), ToolContext('10', 42, '查询'),
                              order_provider=provider, owner_resolver=demo_owner)
    for name in ('query_order', 'query_logistics'):
        outcome = await ToolExecutor().execute(ToolCall('missing', name, {'order_id': 'unknown'}), registry)
        assert outcome.status == 'error' and outcome.content['error']['code'] == 'not_found'


# 返回测试会话的已知身份，代替此用例不涉及的 SQL 外部边界。
async def demo_owner(conversation_id):
    return 'demo-user'


@pytest.mark.asyncio
async def test_reference_order_has_fixed_snapshot_and_unshipped_logistics():
    """截图演示订单缺失或事实漂移不能生成错误金额、运单或到达时间。"""
    provider = DemoOrderProvider()
    registry = build_registry(FAQStub(), TicketStub(), ToolContext('10', 42, '查询'),
                              order_provider=provider, owner_resolver=demo_owner)
    outcome = await ToolExecutor().execute(
        ToolCall('reference-order', 'query_order', {'order_id': '2002'}), registry)
    assert outcome.status == 'success'
    assert outcome.content == {
        'user_id': 'demo-user', 'order_id': '2002', 'product_id': 'DEMO-WD2002',
        'product_name': '自动饮水机', 'model': 'DEMO-WD2002', 'category': '电子商品',
        'status': '待付款', 'amount_cents': 155700, 'currency': 'CNY',
        'signed_at': None, 'as_of': '2026-10-15', 'mock': True,
        'fixture_version': '2026-10-18-reference-v1',
    }
    logistics = await ToolExecutor().execute(
        ToolCall('reference-logistics', 'query_logistics', {'order_id': '2002'}), registry)
    assert logistics.status == 'success'
    assert logistics.content['logistics_status'] == '未发货'
    assert logistics.content['tracking_no'] is None
    assert logistics.content['estimated_delivery_days'] is None
    assert await provider.get_order(user_id='other-owner', order_id='2002') is None


# 捕获提供器漏掉 owner 条件而泄露私有订单的回归。
@pytest.mark.asyncio
async def test_other_owner_order_not_visible(tmp_path):
    fixture = tmp_path / 'private.json'
    fixture.write_text(json.dumps({'orders': [{
        'user_id': 'private-user', 'order_id': 'private-1', 'product_id': 'p1',
        'product_name': '私有台灯', 'model': 'PRIVATE', 'category': '电子商品',
        'status': '已签收', 'amount_cents': 12345, 'currency': 'CNY',
        'signed_at': '2026-10-13', 'as_of': '2026-10-15', 'mock': True,
        'fixture_version': 'test-v1',
    }]}), encoding='utf-8')
    provider = DemoOrderProvider(fixture)
    assert await provider.list_orders(user_id='demo-user') == []
    assert await provider.get_order(user_id='demo-user', order_id='private-1') is None
    assert await provider.get_order(user_id='other-owner', order_id='1001') is None
    assert (await provider.get_order(user_id='private-user', order_id='private-1')).amount_cents == 12345
    assert await DemoOrderProvider().list_orders(user_id='unknown-owner') == []


# 捕获工具接受模型 owner 或忽略 SQL 会话归属的回归。
@pytest.mark.asyncio
async def test_order_tool_uses_sql_owner_not_model_arg(tmp_path):
    engine = create_async_engine('sqlite+aiosqlite:///' + str(tmp_path / 'owners.sqlite'))
    try:
        async with engine.begin() as connection:
            await connection.execute(text('CREATE TABLE conversations (id INTEGER PRIMARY KEY, user_id TEXT, status TEXT, summary TEXT, summary_upto_msg_id BIGINT, layer1_from_msg_id BIGINT, created_at DATETIME, updated_at DATETIME)'))
            await connection.execute(text("INSERT INTO conversations (id,user_id,status) VALUES (10,'demo-user','进行中'),(20,'other-owner','进行中')"))
        repository = ConversationRepository(SimpleNamespace(session=async_sessionmaker(engine)))
        assert await repository.get_user_id('10') == 'demo-user'
        provider = DemoOrderProvider()
        registry = build_registry(FAQStub(), TicketStub(), ToolContext('10', 42, '查询'), order_provider=provider, owner_resolver=repository.get_user_id)
        assert set(registry['query_order'].args_schema.model_fields) == {'order_id'}
        rejected = await ToolExecutor().execute(ToolCall('forged', 'query_order', {'order_id': '1001', 'user_id': 'other-owner'}), registry)
        assert rejected.status == 'error' and rejected.attempts == 0
        order = await registry['query_order'].ainvoke({'order_id': '1001'})
        assert order == (await provider.get_order(user_id='demo-user', order_id='1001')).model_dump(mode='json')
        first = await registry['query_logistics'].ainvoke({'order_id': '1001'})
        assert first == await registry['query_logistics'].ainvoke({'order_id': '1001'})
        assert first['model'] == order['model'] and first['mock'] is True
        other = build_registry(FAQStub(), TicketStub(), ToolContext('20', 42, '查询'), order_provider=provider, owner_resolver=repository.get_user_id)
        assert (await other['query_order'].ainvoke({'order_id': '1001'}))['error']['code'] == 'not_found'
    finally:
        await engine.dispose()

# 捕获仅配置单侧依赖时意外回退随机工具的回归。
@pytest.mark.parametrize('dependency', ['provider', 'resolver'])
def test_scoped_dependencies_must_be_paired(dependency):
    kwargs = {'order_provider': DemoOrderProvider()} if dependency == 'provider' else {'owner_resolver': demo_owner}
    with pytest.raises(ValueError):
        build_registry(FAQStub(), TicketStub(), ToolContext('10', 42, '查询'), **kwargs)
