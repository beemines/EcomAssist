"""真实MySQL事务/唯一键测试；所有数据位于3308随机自有库。"""
import asyncio
import hashlib
from uuid import uuid4

import pytest
from langchain_core.messages import AIMessage, HumanMessage
from sqlalchemy import event, text
from sqlalchemy.exc import IntegrityError

from app.core.errors import ServiceError
from app.repositories.conversations import ConversationRepository
from tests.integration.test_refund_migration import refund_schema


async def draft_for(db, *, owner='demo-user', order='1001', offer=None, policy=None):
    """由真实SQL消息和演示事实构造独立服务器草稿。"""
    from app.orders.demo import DemoOrderProvider
    from app.refunds.types import RefundDraft
    repo = ConversationRepository(db)
    cid = await repo.create(owner)
    uid = await repo.append_message(cid, HumanMessage('订单退货'))
    aid = await repo.append_message(cid, AIMessage('需审核'))
    snapshot = (await DemoOrderProvider().get_order(user_id='demo-user', order_id='1001')).model_dump(mode='json')
    snapshot.update(user_id=owner, order_id=order)
    return RefundDraft(conversation_id=cid, user_message_id=str(uid), assistant_message_id=str(aid),
        checkpoint_id=str(uuid4()), offer_id=offer or str(uuid4()), user_id=owner, order_id=order,
        amount_cents=19900, currency='CNY', order_snapshot=snapshot,
        policy_snapshot=policy or {'matches': [{'answer': '完整政策原文', 'section_path': '退货/规则'}]},
        decision_snapshot={'refund_decision': 'needs_review', 'decision_reason': '完好待核验'},
        raw_question='订单退货', final_answer='需审核')


async def ready(db):
    """仅在随机schema显式迁移。"""
    from app.refunds.migration import migrate_refunds
    from app.refunds.repository import RefundRepository
    await migrate_refunds(db)
    assert db.engine.url.host == '127.0.0.1' and db.engine.url.port == 3308
    assert db.engine.url.database.startswith('ch03_migration_')
    return RefundRepository(db)


async def test_retries_keep_receipt_snapshots_and_business_state(refund_schema):
    """重复与响应丢失重试不新增，改原因409且不修改历史内容/人工状态。"""
    repo = await ready(refund_schema)
    draft = await draft_for(refund_schema)
    first = await repo.create_pending(draft, 'quality')
    # 此处忽略第一次返回值即模拟SQL提交后HTTP响应丢失，随后重新提交。
    retried = await repo.create_pending(draft, 'quality')
    assert first == retried and first.status == '待审核'
    assert first.amount_cents == 19900 and first.currency == 'CNY'
    with pytest.raises(ServiceError) as exc:
        await repo.create_pending(draft, 'damaged')
    assert exc.value.status_code == 409
    await __import__('app.refunds.migration', fromlist=['migrate_refunds']).migrate_refunds(refund_schema)
    async with refund_schema.session() as session:
        rows = (await session.execute(text('SELECT reason,status,amount_cents,policy_snapshot,created_at FROM refund_requests'))).all()
        assert len(rows) == 1 and rows[0].reason == 'quality' and rows[0].created_at is not None
        assert await session.scalar(text('SELECT COUNT(*) FROM tickets')) == 0
        assert await session.scalar(text('SELECT status FROM conversations WHERE id=:id'), {'id': int(draft.conversation_id)}) == '进行中'
        assert await session.scalar(text('SELECT pending_key FROM refund_requests')) == hashlib.sha256(b'["demo-user","1001"]').hexdigest()
    async with refund_schema.session() as session, session.begin():
        await session.execute(text("UPDATE conversations SET status='已结束' WHERE id=:id"), {'id': int(draft.conversation_id)})
    assert await repo.create_pending(draft, 'quality') == first


async def test_concurrent_same_offer_is_one_receipt(refund_schema):
    """同会话行锁串行提交，同offer重试始终相同单号。"""
    repo = await ready(refund_schema)
    draft = await draft_for(refund_schema)
    receipts = await asyncio.gather(*(repo.create_pending(draft, 'quality') for _ in range(4)))
    assert len({r.request_no for r in receipts}) == 1


async def test_cross_conversation_race_enforced_by_unique_pending_key(refund_schema, monkeypatch):
    """不同会话互不共锁，最终数据库唯一键只准一条待审核申请。"""
    repo = await ready(refund_schema)
    drafts = await asyncio.gather(*(draft_for(refund_schema) for _ in range(4)))
    original, arrived, release, duplicates, reads = repo._existing, [], asyncio.Event(), [], []
    async def synchronized_read(session, draft, reason):
        """让四个真实事务都读到缺失，再同时争唯一键以确定覆盖1062恢复。"""
        reads.append(session)
        result = await original(session, draft, reason)
        if result is None:
            arrived.append(session)
            if len(arrived) == 4:
                release.set()
            await asyncio.wait_for(release.wait(), timeout=5)
        return result
    def observe_error(context):
        """记录真实MySQL驱动的1062，不模拟数据库异常。"""
        if getattr(context.original_exception, 'args', (None,))[0] == 1062:
            duplicates.append(context.original_exception.args[0])
    monkeypatch.setattr(repo, '_existing', synchronized_read)
    event.listen(refund_schema.engine.sync_engine, 'handle_error', observe_error)
    try:
        results = await asyncio.wait_for(asyncio.gather(*(repo.create_pending(d, 'quality') for d in drafts),
            return_exceptions=True), timeout=15)
    finally:
        event.remove(refund_schema.engine.sync_engine, 'handle_error', observe_error)
    assert sum(not isinstance(r, Exception) for r in results) == 1
    assert all(isinstance(r, ServiceError) and r.status_code == 409 for r in results if isinstance(r, Exception))
    assert len(duplicates) == 3
    assert len(reads) == 7 and all(session not in arrived for session in reads[4:])
    async with refund_schema.session() as session:
        assert await session.scalar(text('SELECT COUNT(*) FROM refund_requests')) == 1


async def test_same_numeric_order_different_users_and_foreign_offer(refund_schema):
    """pending身份包含用户；复用别人的offer不可返回其收据信息。"""
    repo = await ready(refund_schema)
    a = await draft_for(refund_schema)
    b = await draft_for(refund_schema, owner='other-user')
    ra, rb = await asyncio.gather(repo.create_pending(a, 'quality'), repo.create_pending(b, 'quality'))
    assert ra.request_no != rb.request_no
    forged = await draft_for(refund_schema, owner='third-user', offer=a.offer_id)
    with pytest.raises(ServiceError) as exc:
        await repo.create_pending(forged, 'quality')
    assert exc.value.status_code == 409 and ra.request_no not in exc.value.message


async def test_non_duplicate_integrity_error_propagates(refund_schema):
    """非1062错误绝不能被当作成功或重复申请。"""
    repo = await ready(refund_schema)
    draft = await draft_for(refund_schema)
    def reject_insert(conn, cursor, statement, parameters, context, executemany):
        """在真实引擎INSERT边界注入不可恢复完整性错误。"""
        if statement.startswith('INSERT INTO refund_requests'):
            from pymysql.err import IntegrityError as DriverError
            raise IntegrityError(statement, parameters, DriverError(1452, 'controlled failure'))
    event.listen(refund_schema.engine.sync_engine, 'before_cursor_execute', reject_insert)
    try:
        with pytest.raises(IntegrityError):
            await repo.create_pending(draft, 'quality')
    finally:
        event.remove(refund_schema.engine.sync_engine, 'before_cursor_execute', reject_insert)
    async with refund_schema.session() as session:
        assert await session.scalar(text('SELECT COUNT(*) FROM refund_requests')) == 0


@pytest.mark.parametrize('fault', ['answer', 'owner', 'user_role', 'intervening_user'])
async def test_transaction_rechecks_owner_and_sql_turn(refund_schema, fault):
    """服务检查后的SQL变化在短事务再次核对，失效草稿不能写入。"""
    repo = await ready(refund_schema)
    draft = await draft_for(refund_schema)
    async with refund_schema.session() as session, session.begin():
        if fault == 'owner':
            await session.execute(text("UPDATE conversations SET user_id='changed-owner' WHERE id=:id"), {'id': int(draft.conversation_id)})
        elif fault == 'user_role':
            await session.execute(text("UPDATE messages SET role='assistant' WHERE id=:id"), {'id': int(draft.user_message_id)})
        elif fault == 'intervening_user':
            # 在已有用户消息与下一条助手之间的自有整数ID中插入新的用户记录。
            await session.execute(text('UPDATE messages SET id=id+1 WHERE id=:id'), {'id': int(draft.assistant_message_id)})
            await session.execute(text("INSERT INTO messages(id,conversation_id,role,content) VALUES(:id,:cid,'user','新的问题')"),
                {'id': int(draft.assistant_message_id), 'cid': int(draft.conversation_id)})
        else:
            await session.execute(text('UPDATE messages SET content=:content WHERE id=:id'),
                {'content': '后来被更改', 'id': int(draft.assistant_message_id)})
    with pytest.raises(ServiceError) as exc:
        await repo.create_pending(draft, 'quality')
    assert exc.value.status_code == 422
    async with refund_schema.session() as session:
        assert await session.scalar(text('SELECT COUNT(*) FROM refund_requests')) == 0


async def test_cli_explicit_init_and_verify_on_owned_schema(refund_schema, monkeypatch, capsys):
    """实际CLI分派只按显式init创建；目标强制替换为随机自有schema。"""
    import argparse
    from types import SimpleNamespace
    from app.refunds import cli
    monkeypatch.setattr(cli, 'load_settings', lambda: SimpleNamespace(database_url=refund_schema.engine.url))
    with pytest.raises(RuntimeError, match='missing'):
        await cli.run(argparse.Namespace(command='verify'))
    await cli.run(argparse.Namespace(command='init'))
    await cli.run(argparse.Namespace(command='verify'))
    assert capsys.readouterr().out.count('Refund schema ready') == 2


async def test_real_rerank_score_json_roundtrip_keeps_same_root_retry(refund_schema):
    """真实MySQL浮点JSON往返后的响应丢失重试必须仍返回同一收据。"""
    import json
    from app.refunds.types import RefundDraft
    repo = await ready(refund_schema)
    policy = {'matches': [{'id': '119', 'n': 1, 'answer': '商品完好需核验', 'score': 0.014654727652668953},
                          {'id': '120', 'n': 2, 'answer': '退款需审核', 'score': 0.011466585099697113}],
              'retrieval': {'candidate_count': 50}}
    draft = await draft_for(refund_schema, policy=policy)
    first = await repo.create_pending(draft, 'quality')
    # 第一次HTTP结果丢失；客户端同一原始完成根、offer和原因重发。
    assert await repo.create_pending(draft, 'quality') == first
    async with refund_schema.session() as session:
        before = await session.scalar(text('SELECT policy_snapshot FROM refund_requests'))
        assert len((await session.execute(text('SELECT id FROM refund_requests'))).all()) == 1
    names = ('conversation_id', 'user_message_id', 'assistant_message_id', 'checkpoint_id', 'offer_id',
             'user_id', 'order_id', 'amount_cents', 'currency', 'order_snapshot', 'policy_snapshot',
             'decision_snapshot', 'raw_question', 'final_answer')
    for mutation in ('policy_text', 'policy_structure', 'amount', 'decision', 'non_score_float', 'score_two_ulps'):
        values = {name: getattr(draft, name) for name in names}
        if mutation == 'policy_text':
            values['policy_snapshot']['matches'][0]['answer'] = '不同政策'
        elif mutation == 'policy_structure':
            values['policy_snapshot']['matches'].reverse()
        elif mutation == 'amount':
            values['amount_cents'] += 1
        elif mutation == 'decision':
            values['decision_snapshot']['refund_decision'] = 'eligible'
        elif mutation == 'non_score_float':
            values['policy_snapshot']['retrieval']['candidate_count'] = 50.0
        else:
            import math
            stored_score = json.loads(before)['matches'][0]['score']
            values['policy_snapshot']['matches'][0]['score'] = math.nextafter(math.nextafter(stored_score, math.inf), math.inf)
        with pytest.raises(ServiceError) as exc:
            await repo.create_pending(RefundDraft(**values), 'quality')
        assert exc.value.status_code == 409
    async with refund_schema.session() as session:
        assert await session.scalar(text('SELECT COUNT(*) FROM refund_requests')) == 1
        assert await session.scalar(text('SELECT policy_snapshot FROM refund_requests')) == before


def test_policy_score_equivalence_is_only_one_finite_ulp_at_exact_score_path():
    """仅已观察到的一个ULP存储偏差等价；任意其他字段、类型、结构都严格。"""
    from app.refunds import repository
    compare = getattr(repository, 'same_policy_snapshot', lambda a, b: a == b)
    original = {'matches': [{'score': 0.014654727652668953, 'answer': '全文'}], 'amount': 19900}
    assert compare(original, {'matches': [{'score': 0.014654727652668951, 'answer': '全文'}], 'amount': 19900})
    for changed in [
        {'matches': [{'score': 0.014654727652668950, 'answer': '全文'}], 'amount': 19900},
        {'matches': [{'score': float('nan'), 'answer': '全文'}], 'amount': 19900},
        {'matches': [{'score': 0.014654727652668951, 'answer': '改文'}], 'amount': 19900},
        {'matches': [{'score': 0.014654727652668951, 'answer': '全文', 'extra': 1}], 'amount': 19900},
        {'matches': [{'score': 0.014654727652668951, 'answer': '全文'}], 'amount': 19900.0},
    ]:
        assert not compare(original, changed)
