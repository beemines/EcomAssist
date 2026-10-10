"""最终审查四个真实边界的独立回归；外部收费传输始终隔离。"""

import asyncio
from dataclasses import replace
import json

import pytest

from app.rag_evaluation.manager import build_run_config
from app.rag_evaluation.resources import OwnedResources
from app.rag_evaluation.store import RunStore
from tests.test_rag_resources import api, dataset, settings, local_owner, all_rows
from tests.test_hybrid_chat import hybrid_service
from tests.test_rag_api import application, client_for
from tests.tool_fakes import collect


async def test_production_config_reaches_real_prepare(tmp_path, monkeypatch):
    """真实配置生产者与真实准备预检必须衔接，配置摘要不可替换成资料摘要。"""
    owner, store, database = await local_owner(api(), tmp_path, monkeypatch)
    saved = (await store.get(owner.run_id))['config']
    assert saved['fingerprint'] != dataset().fingerprint
    mapping = await owner.prepare(dataset())
    assert len(await all_rows(database)) == 2 and set(mapping) == {'one', 'two'}
    assert (await owner.cleanup()).ok and await all_rows(database) == []


@pytest.mark.parametrize('mutation', ['missing', 'dataset_fingerprint', 'corpus_hash', 'cases_hash', 'annotation_hash'])
async def test_provenance_mismatch_rejected_before_database(tmp_path, monkeypatch, mutation):
    """缺历史出处或任意资料摘要不匹配时，不得构造外部资源。"""
    config = build_run_config(dataset(), settings(), 'pilot')
    if mutation == 'missing':
        config.pop('provenance')
    else:
        config['provenance'][mutation] = 'f' * 64
    store = RunStore(tmp_path)
    run_id = await store.create(config, [('E1', 'dense')])
    def forbidden(*args, **kwargs):
        """任何数据库构造都是预检边界失效。"""
        pytest.fail('database constructed before provenance validation')
    monkeypatch.setattr(api(), 'Database', forbidden)
    with pytest.raises(ValueError, match='mismatch'):
        await OwnedResources(settings(), store, run_id).prepare(dataset())


@pytest.mark.parametrize('boundary', ['decision', 'delta'])
@pytest.mark.parametrize('uncancel', [False, True])
async def test_refusal_expired_loop_clock_never_commits(tmp_path, monkeypatch, boundary, uncancel):
    """真实绝对时钟越期而超时回调尚未调度，拒答不可变成成功或入池。"""
    service, _, repository, quality, _ = hybrid_service(useful=False)
    prepared = await service.prepare('42', '退货规则')
    loop = asyncio.get_running_loop()
    real_time = loop.time
    original = service.sufficiency_service.check
    def expire():
        """只推进循环时钟，保留原定240秒期限与超时调度。"""
        monkeypatch.setattr(loop, 'time', lambda: prepared.deadline + 1)
    async def check(*args):
        """可控依赖吞取消并清零，验证独立绝对期限仍能挡住迟到结果。"""
        decision = await original(*args)
        if uncancel:
            task = asyncio.current_task()
            task.cancel()
            try:
                await asyncio.sleep(0)
            except asyncio.CancelledError:
                task.uncancel()
        if boundary == 'decision':
            expire()
        return decision
    monkeypatch.setattr(service.sufficiency_service, 'check', check)
    events = []
    stream = service.stream(prepared)
    try:
        async for event in stream:
            events.append(event)
            if boundary == 'delta' and event.event == 'delta':
                expire()
    finally:
        monkeypatch.setattr(loop, 'time', real_time)
        await stream.aclose()
        service.release(prepared)
    assert events[-1].event == 'error' and events[-1].data['code'] == 'upstream_timeout'
    assert not any(event.event == 'done' for event in events)
    if boundary == 'decision':
        assert not any(event.event == 'delta' for event in events)
    assert quality.pool == []
    assert not any(row.role == 'assistant' and not row.tool_calls for row in repository.rows)


async def test_refusal_commit_return_after_deadline_does_not_publish_done(monkeypatch):
    """原子提交已完成但依赖迟到返回，保留事务事实且不得宣称期限内成功。"""
    service, _, repository, quality, _ = hybrid_service(useful=False)
    prepared = await service.prepare('42', '退货规则')
    loop, original = asyncio.get_running_loop(), quality.commit_refusal
    real_time = loop.time
    async def late_commit(*args, **kwargs):
        """提交内部确有悬挂点，完成后模拟阻塞循环直至期限之外。"""
        await asyncio.sleep(0)
        identifier = await original(*args, **kwargs)
        monkeypatch.setattr(loop, 'time', lambda: prepared.deadline + 1)
        return identifier
    monkeypatch.setattr(quality, 'commit_refusal', late_commit)
    try:
        events = await collect(service, prepared)
    finally:
        monkeypatch.setattr(loop, 'time', real_time)
    assert events[-1].event == 'error' and not any(event.event == 'done' for event in events)
    assert len(quality.pool) == 1 and repository.rows[-1].content


@pytest.mark.parametrize('path', [
    '/static/rag-evaluation-history.json', '/static/RAG-EVALUATION-HISTORY.JSON',
    '/static/./rag-evaluation-history.json', '/static/%72ag-evaluation-history.json',
    '/static/sub/../rag-evaluation-history.json', '/static/rag-evaluation-history.json.',
    '/static/rag-evaluation-history.json%20',
    '/api/rag-evaluations/runs/legacy-30-v1',
    '/api/rag-evaluations/runs/legacy-30-v1/cases?limit=100',
    '/api/rag-evaluations/runs/legacy-30-v1/export',
    '/api/rag-evaluations/runs/legacy-30-v1/export?format=markdown'])
async def test_actual_public_legacy_routes_cannot_leak_raw(tmp_path, path):
    """真实应用静态路径及Windows别名均不能绕过历史白名单。"""
    app, _ = application(tmp_path)
    async with client_for(app) as client:
        response = await client.get(path)
    assert response.status_code in (200, 404)
    if response.status_code == 200:
        text = response.text
        leaked = [field for field in ('"raw"', '"raw_response"', '"request_body"', '"private_snapshot"') if field in text]
        assert leaked == []
