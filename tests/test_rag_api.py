"""工作台 HTTP 边界：真实存储投影、收费入口防护与生命周期资源责任。"""

import asyncio
import importlib
import json
from pathlib import Path

import httpx
import pytest

from app.rag_evaluation.locking import RunBusy, RunLock
from app.rag_evaluation.store import RunStore
from tests.fakes import ConversationStore, FAQStub, StreamingModel, fake_settings
from tests.test_rag_store import config, record, stale_checkpoint

PREFIX = '/api/rag-evaluations'
PAYLOAD = {'dataset_id': 'merchant-rag-300-v1', 'scope': 'pilot'}


class ManagerDouble:
    """只替代运行入口，实际 HTTP 校验与磁盘 DTO 不使用替身。"""

    def __init__(self, store):
        """记录入口调用以证明 GET 与非法请求未触发收费运行。"""
        self.store = store
        self.starts = []
        self.cancels = []
        self.started = self.closed = False
        self.failure = None

    async def start(self, dataset_id, scope):
        """首个请求真实创建 manifest，后续请求模拟共享锁立即拒绝。"""
        if self.failure:
            raise self.failure
        if self.starts:
            raise RunBusy('PRIVATE-SECRET')
        self.starts.append((dataset_id, scope))
        return await self.store.create(config(), [('E1', 'dense')])

    async def cancel(self, run_id):
        """使用实际 manifest 记录取消，保留终态幂等语义。"""
        from app.rag_evaluation.store import OUTCOMES, public_run_metadata
        self.cancels.append(run_id)
        value = await self.store.get(run_id)
        if value['state'] not in OUTCOMES:
            await self.store.update(run_id, {'state': 'cancelling'})
        return public_run_metadata(await self.store.get(run_id))

    async def startup(self):
        """标记应用所属管理器已执行恢复入口。"""
        self.started = True

    async def pilot_ready(self, dataset_id):
        """借用真实公开只读门槛，不由测试替身猜测 pilot 合法性。"""
        from app.rag_evaluation.manager import DATASET_ROOT, RunManager
        return await RunManager(self.store, fake_settings(), DATASET_ROOT).pilot_ready(dataset_id)

    async def shutdown(self):
        """标记关闭可与只读 HTTP 请求并行完成。"""
        await asyncio.sleep(0)
        self.closed = True


def application(tmp_path, *, enabled=False, manager=None, **overrides):
    """注入所有在线依赖，测试绝不构造模型或连接业务库。"""
    assert importlib.util.find_spec('app.api.rag_evaluations'), '尚未实现工作台 API'
    from app.main import create_app
    manager = manager or ManagerDouble(RunStore(tmp_path))
    app = create_app(fake_settings(rag_evaluation_enabled=enabled, **overrides),
        model=StreamingModel(), repository=ConversationStore(), faq_repository=FAQStub(),
        evaluation_manager=manager)
    return app, manager


def client_for(app, *, base_url='http://127.0.0.1:8001'):
    """通过真实 ASGI 路由发请求，默认地址与本机白名单一致。"""
    return httpx.AsyncClient(transport=httpx.ASGITransport(app), base_url=base_url)


async def test_readonly_rejects_start(tmp_path):
    """默认配置只读，页面和历史可读而启动不进入管理器。"""
    app, manager = application(tmp_path)
    async with client_for(app) as client:
        assert (await client.get('/rag-eval')).status_code == 200
        assert (await client.get(PREFIX + '/runs')).status_code == 200
        result = await client.post(PREFIX + '/runs', json=PAYLOAD)
    assert result.status_code == 403
    assert result.json()['code'] == 'evaluation_disabled'
    assert manager.starts == manager.cancels == []


async def test_start_202_and_busy_409(tmp_path):
    """合法本机 JSON 创建一次运行，重复点击不能隐式收费排队。"""
    app, manager = application(tmp_path, enabled=True)
    async with client_for(app) as client:
        first = await client.post(PREFIX + '/runs', json=PAYLOAD)
        second = await client.post(PREFIX + '/runs', json=PAYLOAD)
    assert first.status_code == 202
    assert len(first.json()['run_id']) == 32
    assert second.status_code == 409
    assert second.json()['code'] == 'run_busy'
    assert manager.starts == [('merchant-rag-300-v1', 'pilot')]


@pytest.mark.parametrize('path,payload', [
    ('/runs', dict(PAYLOAD, dataset_id='../PRIVATE-SECRET')),
    ('/runs', dict(PAYLOAD, scope='unknown')),
    ('/runs', dict(PAYLOAD, api_key='PRIVATE-SECRET')),
    ('/runs?output=PRIVATE-SECRET', PAYLOAD),
])
async def test_bad_dataset_strategy_filter_and_path_rejected(tmp_path, path, payload):
    """未知题库、范围及额外字段在运行入口之前安全拒绝。"""
    app, manager = application(tmp_path, enabled=True)
    async with client_for(app) as client:
        result = await client.post(PREFIX + path, json=payload)
    assert result.status_code == 422
    assert 'PRIVATE-SECRET' not in result.text
    assert manager.starts == []


@pytest.mark.parametrize('headers,body', [
    ({'Origin': 'http://evil.test'}, json.dumps(PAYLOAD)),
    ({'Origin': 'null'}, json.dumps(PAYLOAD)),
    ({'Origin': 'http://localhost:8002'}, json.dumps(PAYLOAD)),
    ({'Host': 'evil.test'}, json.dumps(PAYLOAD)),
    ({'Host': '127.0.0.1:8002'}, json.dumps(PAYLOAD)),
    ({'Content-Type': 'text/plain'}, json.dumps(PAYLOAD)),
    ({'Content-Type': 'application/x-www-form-urlencoded'}, 'dataset_id=x'),
])
async def test_cross_origin_or_nonjson_start_rejected(tmp_path, headers, body):
    """浏览器跨源、Host 重绑定和非 JSON 均不能启动收费运行。"""
    app, manager = application(tmp_path, enabled=True)
    async with client_for(app) as client:
        result = await client.post(PREFIX + '/runs', content=body,
            headers={'Content-Type': 'application/json', **headers})
    assert result.status_code in (403, 415)
    assert manager.starts == []


async def test_public_error_does_not_expose_secret(tmp_path):
    """校验输入、JSON 解析错误及未知内部异常统一为固定安全消息。"""
    app, manager = application(tmp_path, enabled=True)
    async with client_for(app) as client:
        results = [await client.post(PREFIX + '/runs', content='{"PRIVATE-SECRET":',
            headers={'Content-Type': 'application/json'})]
        manager.failure = RuntimeError('PRIVATE-SECRET https://key@host')
        results.append(await client.post(PREFIX + '/runs', json=PAYLOAD))
    assert [value.status_code for value in results] == [422, 500]
    for value in results:
        assert set(value.json()) == {'code', 'message'}
        assert 'PRIVATE-SECRET' not in value.text
    assert manager.starts == []


async def test_public_active_snapshot_paging_filters_and_no_fake_ids(tmp_path):
    """实际检查点对外投影并可分页；缺席计划不伪造逐题详情。"""
    app, manager = application(tmp_path)
    run_id = await manager.store.create(config(), [('E1', 'dense'), ('E2', 'bm25')])
    await manager.store.put_case(run_id, record(status='rewrite_error'))
    async with client_for(app) as client:
        detail = await client.get(f'{PREFIX}/runs/{run_id}')
        rows = await client.get(f'{PREFIX}/runs/{run_id}/cases?bucket=E_multi&strategy=dense&status=rewrite_error&query=退货&limit=1')
        case = await client.get(f'{PREFIX}/runs/{run_id}/cases/E1/dense')
        absent = await client.get(f'{PREFIX}/runs/{run_id}/cases/E2/bm25')
        legacy = await client.get(PREFIX + '/runs/legacy-30-v1')
    assert detail.status_code == rows.status_code == case.status_code == legacy.status_code == 200
    assert detail.json()['run']['counts']['not_attempted'] == 1
    assert 'ownership' not in detail.json()['run']
    assert 'case_keys' not in detail.json()['run']
    assert rows.json()['total'] == 1
    assert len(rows.json()['items']) == 1
    assert case.json()['eval_id'] == 'E1'
    assert 'PRIVATE-EXCEPTION' not in case.text
    assert absent.status_code == 404
    assert legacy.json()['run']['read_only'] is True
    assert manager.starts == []


@pytest.mark.parametrize('query', ['offset=-1', 'limit=0', 'limit=101', 'bucket=bad',
    'strategy=vector', 'status=bad', 'query=' + 'x' * 513, 'path=PRIVATE-SECRET'])
async def test_invalid_read_filters_are_safe_and_free(tmp_path, query):
    """分页和枚举边界由 HTTP 校验，错误无回显且不调用运行器。"""
    app, manager = application(tmp_path)
    run_id = await manager.store.create(config(), [('E1', 'dense')])
    async with client_for(app) as client:
        value = await client.get(f'{PREFIX}/runs/{run_id}/cases?{query}')
    assert value.status_code == 422
    assert 'PRIVATE-SECRET' not in value.text
    assert manager.starts == []


async def test_cancel_is_json_guarded_and_legacy_readonly(tmp_path):
    """取消同样需要启用、白名单及空 JSON；旧历史永不能取消。"""
    app, manager = application(tmp_path, enabled=True)
    run_id = await manager.store.create(config(), [('E1', 'dense')])
    async with client_for(app) as client:
        blocked = await client.post(f'{PREFIX}/runs/{run_id}/cancel', json={}, headers={'Origin': 'http://evil.test'})
        extra = await client.post(f'{PREFIX}/runs/{run_id}/cancel', json={'secret': 'PRIVATE-SECRET'})
        old = await client.post(PREFIX + '/runs/legacy-30-v1/cancel', json={})
        valid = await client.post(f'{PREFIX}/runs/{run_id}/cancel', json={})
    assert [value.status_code for value in (blocked, extra, old, valid)] == [403, 422, 409, 200]
    assert valid.json()['state'] == 'cancelling'
    assert manager.cancels == [run_id]


async def test_export_requires_terminal_commit_and_matching_public_identity(tmp_path):
    """存在单个导出文件不是提交成功；终态和当前公开封套必须一致。"""
    from app.rag_evaluation.export import publish_reports
    app, manager = application(tmp_path)
    run_id = await manager.store.create(config(), [('E1', 'dense')])
    manifest = await manager.store.get(run_id)
    final = dict(manifest, state='failed', outcome='failed', stage='complete',
        cleanup={'ok': True, 'errors': [], 'unverified': []})
    publish_reports(tmp_path, final, [])
    async with client_for(app) as client:
        premature = await client.get(f'{PREFIX}/runs/{run_id}/export?format=json')
        await manager.store.update(run_id, {key: final[key] for key in ('state', 'outcome', 'stage', 'cleanup')})
        # manager 实际发布时更新时间最终会变化，比较封套须忽略该发布时钟差。
        good = await client.get(f'{PREFIX}/runs/{run_id}/export?format=json')
        md = await client.get(f'{PREFIX}/runs/{run_id}/export?format=markdown')
        bad_format = await client.get(f'{PREFIX}/runs/{run_id}/export?format=../../manifest')
        saved = json.loads((tmp_path / run_id / 'report.json').read_text(encoding='utf-8'))
        saved['run_id'] = '0' * 32
        (tmp_path / run_id / 'report.json').write_text(json.dumps(saved), encoding='utf-8')
        mismatch = await client.get(f'{PREFIX}/runs/{run_id}/export?format=json')
    assert premature.status_code == 409
    assert good.status_code == md.status_code == 200
    assert 'attachment' in good.headers['content-disposition']
    assert good.json()['run_id'] == run_id
    assert bad_format.status_code == 422
    assert mismatch.status_code == 409


async def test_datasets_get_is_readonly_actual_frozen_counts(tmp_path):
    """数据集 GET 全量离线核验后返回真实 300题/50块，不构造运行。"""
    app, manager = application(tmp_path)
    async with client_for(app) as client:
        result = await client.get(PREFIX + '/datasets')
    assert result.status_code == 200
    item = result.json()['items'][0]
    assert item['dataset_id'] == PAYLOAD['dataset_id']
    assert item['case_count'] == 300 and item['chunk_count'] == 50
    assert item['matching_pilot'] is False
    assert item['available_scopes'] == []
    assert manager.starts == []


async def test_owned_manager_lifespan_and_injected_manager_is_borrowed(tmp_path, monkeypatch):
    """应用自建管理器负责恢复/关闭；外部注入资源保留调用方责任。"""
    application(tmp_path)
    import app.main
    owned = ManagerDouble(RunStore(tmp_path))
    monkeypatch.setattr(app.main, 'RunManager', lambda *args: owned)
    app = app.main.create_app(fake_settings(rag_evaluation_enabled=True), model=StreamingModel(),
        repository=ConversationStore(), faq_repository=FAQStub())
    async with app.router.lifespan_context(app):
        assert owned.started and not owned.closed
        async with client_for(app) as client:
            assert (await client.get(PREFIX + '/runs')).status_code == 200
    assert owned.closed
    borrowed_app, borrowed = application(tmp_path, enabled=True)
    async with borrowed_app.router.lifespan_context(borrowed_app):
        pass
    assert not borrowed.started and not borrowed.closed


async def test_router_factory_can_be_mounted_without_create_app_state(tmp_path):
    """公开路由工厂自身拥有防护配置，挂在普通 FastAPI 也保持相同边界。"""
    from fastapi import FastAPI
    from app.api.rag_evaluations import create_router
    store = RunStore(tmp_path)
    manager = ManagerDouble(store)
    app = FastAPI()
    app.include_router(create_router(manager, store, fake_settings(rag_evaluation_enabled=True)))
    async with client_for(app) as client:
        blocked = await client.post(PREFIX + '/runs', json=PAYLOAD, headers={'Origin': 'http://evil.test'})
        valid = await client.post(PREFIX + '/runs', json=PAYLOAD)
    assert blocked.status_code == 403
    assert valid.status_code == 202


async def test_actual_manager_foreign_cli_startup_busy_does_not_recover(tmp_path, monkeypatch):
    """真实 OS 租约阻挡 startup/HTTP，外来活跃运行不能被恢复或清理。"""
    from app.rag_evaluation.manager import DATASET_ROOT, RunManager
    import app.rag_evaluation.manager as module
    store = RunStore(tmp_path)
    run_id = await store.create(config(), [('E1', 'dense')])
    manager = RunManager(store, fake_settings(), DATASET_ROOT)
    def forbidden(*args, **kwargs):
        """任何建资源动作表明错误触碰其他 CLI 所有者。"""
        raise AssertionError('foreign owner was touched')
    monkeypatch.setattr(module, 'OwnedResources', forbidden)
    before = (tmp_path / run_id / 'manifest.json').read_bytes()
    lease = RunLock(tmp_path).acquire()
    try:
        await manager.startup()
        app, _ = application(tmp_path, enabled=True, manager=manager)
        async with client_for(app) as client:
            response = await client.post(PREFIX + '/runs', json=PAYLOAD)
            readable = await client.get(f'{PREFIX}/runs/{run_id}')
        assert response.status_code == 409
        assert readable.status_code == 200
        assert manager._task is None and manager._lease is None
        assert (tmp_path / run_id / 'manifest.json').read_bytes() == before
    finally:
        lease.close()
        await manager.shutdown()


async def test_disabled_owned_lifespan_does_not_recover_or_write(tmp_path, monkeypatch):
    """默认只读应用不执行 manager 恢复，即使历史残留为非终态。"""
    application(tmp_path)
    import app.main
    owned = ManagerDouble(RunStore(tmp_path))
    run_id = await owned.store.create(config(), [('E1', 'dense')])
    before = (tmp_path / run_id / 'manifest.json').read_bytes()
    monkeypatch.setattr(app.main, 'RunManager', lambda *args: owned)
    app = app.main.create_app(fake_settings(), model=StreamingModel(),
        repository=ConversationStore(), faq_repository=FAQStub())
    async with app.router.lifespan_context(app):
        async with client_for(app) as client:
            response = await client.get(f'{PREFIX}/runs/{run_id}')
    assert response.status_code == 200
    assert not owned.started and not owned.closed
    assert (tmp_path / run_id / 'manifest.json').read_bytes() == before


async def test_manager_shutdown_and_public_read_can_run_together(tmp_path, monkeypatch):
    """实际管理器关闭与轮询并发，使用独立存储快照且保持 owner 清理。"""
    from tests.test_rag_manager import Harness
    harness = Harness(monkeypatch, tmp_path)
    harness.block = True
    run_id = await harness.manager.start(PAYLOAD['dataset_id'], 'pilot')
    await harness.entered.wait()
    app, _ = application(tmp_path, enabled=True, manager=harness.manager)
    async with client_for(app) as client:
        shutdown = asyncio.create_task(harness.manager.shutdown())
        values = await asyncio.gather(*(client.get(f'{PREFIX}/runs/{run_id}') for _ in range(6)))
        await shutdown
        final = await client.get(f'{PREFIX}/runs/{run_id}')
    assert all(value.status_code == 200 for value in values)
    assert final.json()['run']['state'] == 'cancelled'
    assert harness.cleanup_calls == 1
    assert harness.manager._lease is None


@pytest.mark.parametrize('origin', ['http://evil.test:8001', 'http://127.0.0.1:8001/',
    'http://127.0.0.1', 'http://user@localhost:8001', '*'])
def test_origin_configuration_rejects_noncanonical_nonloopback(origin):
    """启动白名单严格本机显式端口，配置错误不成为泛域名授权。"""
    from pydantic import ValidationError
    with pytest.raises(ValidationError):
        fake_settings(rag_evaluation_allowed_origins=(origin,))


async def test_custom_port_explicit_same_origin_and_cancel_idempotence(tmp_path):
    """新端口须启动时配置，合法同源请求及终态重复取消不触发重跑。"""
    app, manager = application(tmp_path, enabled=True,
        rag_evaluation_allowed_origins=('http://localhost:8123',))
    async with client_for(app, base_url='http://localhost:8123') as client:
        started = await client.post(PREFIX + '/runs', json=PAYLOAD,
            headers={'Origin': 'http://localhost:8123'})
        run_id = started.json()['run_id']
        await manager.store.update(run_id, {'state': 'cancelled', 'outcome': 'cancelled'})
        first = await client.post(f'{PREFIX}/runs/{run_id}/cancel', json={})
        second = await client.post(f'{PREFIX}/runs/{run_id}/cancel', json={})
    assert started.status_code == 202
    assert first.json()['state'] == second.json()['state'] == 'cancelled'
    assert len(manager.starts) == 1


async def test_unknown_ids_rejected_and_legacy_exports_projected(tmp_path):
    """未知 ID 安全拒绝；旧 JSON/Markdown 经白名单不输出原始模型请求。"""
    app, manager = application(tmp_path, enabled=True)
    async with client_for(app) as client:
        missing = await client.get(PREFIX + '/runs/' + '0' * 32)
        invalid = await client.get(PREFIX + '/runs/PRIVATE-SECRET')
        legacy = await client.get(PREFIX + '/runs/legacy-30-v1/cases?status=ok&limit=1')
        downloads = [await client.get(PREFIX + '/runs/legacy-30-v1/export?format=' + value)
                     for value in ('json', 'markdown')]
    assert missing.status_code == 404 and invalid.status_code == 422
    assert 'PRIVATE-SECRET' not in invalid.text
    assert legacy.json()['total'] > 0 and len(legacy.json()['items']) == 1
    for value in downloads:
        assert value.status_code == 200
        assert 'model_requests' not in value.text and 'generation_input' not in value.text
        assert 'raw_response' not in value.text
    assert manager.starts == []


async def test_actual_manager_terminal_exports_and_pilot_projection(tmp_path, monkeypatch):
    """真实 manager 发布后所有格式可下载，GET 保留证据且不再次执行评估。"""
    from tests.test_rag_manager import Harness
    harness = Harness(monkeypatch, tmp_path)
    run_id = await harness.manager.start(PAYLOAD['dataset_id'], 'pilot')
    await harness.manager.wait(run_id)
    app, _ = application(tmp_path, enabled=True, manager=harness.manager)
    async with client_for(app) as client:
        downloads = [await client.get(f'{PREFIX}/runs/{run_id}/export?format={value}')
                     for value in ('json', 'markdown')]
        dataset = await client.get(PREFIX + '/datasets')
        detail = await client.get(f'{PREFIX}/runs/{run_id}/cases/{harness.dataset.pilot_ids[0]}/dense')
        await client.post(f'{PREFIX}/runs/{run_id}/cancel', json={})
    assert all(value.status_code == 200 for value in downloads)
    assert downloads[0].json()['run']['state'] == 'completed'
    assert len(downloads[0].json()['records']) == 40
    assert dataset.json()['items'][0]['matching_pilot'] is True
    assert dataset.json()['items'][0]['available_scopes'] == ['pilot', 'full']
    assert detail.json()['answer'] == '资料不足'
    assert detail.json()['point_verdicts'] is not None
    assert harness.calls == 1 and harness.cleanup_calls == 1


async def test_completed_public_case_and_large_exports_keep_evidence_hide_private(tmp_path):
    """HTTP 完整证据聚合超过2MiB仍可下载，私有裁判原文从所有公开读取剔除。"""
    from app.rag_evaluation.export import publish_reports
    from tests.test_rag_metrics import record as completed_record
    app, manager = application(tmp_path)
    plans = [(f'E{i}', strategy) for i in range(10) for strategy in ('dense', 'bm25', 'hybrid', 'hybrid_rerank')]
    run_id = await manager.store.create(config(), plans)
    for eval_id, strategy in plans:
        value = completed_record(eval_id, strategy)
        value['prompt_citations'][0]['answer'] = '公开完整证据' * 4000
        await manager.store.put_case(run_id, value)
    final = dict(await manager.store.get(run_id), state='completed', outcome='completed', stage='complete',
        cleanup={'ok': True, 'errors': [], 'unverified': []})
    publish_reports(tmp_path, final, await manager.store.records(run_id))
    await manager.store.update(run_id, {key: final[key] for key in ('state', 'outcome', 'stage', 'cleanup')})
    async with client_for(app) as client:
        case = await client.get(f'{PREFIX}/runs/{run_id}/cases/E0/dense')
        downloaded = await client.get(f'{PREFIX}/runs/{run_id}/export')
        markdown = await client.get(f'{PREFIX}/runs/{run_id}/export?format=markdown')
    assert case.status_code == downloaded.status_code == markdown.status_code == 200
    assert len(downloaded.content) > 2 * 1024 * 1024
    assert len(downloaded.json()['records']) == 40
    assert case.json()['prompt_citations'][0]['answer'] == '公开完整证据' * 4000
    assert 'raw_response' not in case.json()['judge_snapshot']
    assert all('PRIVATE-JUDGE' not in value.text for value in (case, downloaded, markdown))
    # JSON 仍一致但 MD 已被替换，不能把未验证的任意正文作为公开下载。
    (tmp_path / run_id / 'report.md').write_text('PRIVATE-JUDGE', encoding='utf-8')
    async with client_for(app) as client:
        corrupt = await client.get(f'{PREFIX}/runs/{run_id}/export?format=markdown')
    assert corrupt.status_code == 409
    assert 'PRIVATE-JUDGE' not in corrupt.text


@pytest.mark.parametrize('target', ['/runs?offset=-1', '/runs?limit=101', '/datasets?model=PRIVATE-SECRET',
    '/runs/legacy-30-v1/cases/E1/vector', '/runs/legacy-30-v1/cases/bad--id/dense'])
async def test_history_dataset_detail_parameter_boundaries(tmp_path, target):
    """各 GET 入口执行同样字段白名单，不能借详情策略或未知键绕过校验。"""
    app, manager = application(tmp_path)
    async with client_for(app) as client:
        result = await client.get(PREFIX + target)
    assert result.status_code == 422
    assert set(result.json()) == {'code', 'message'}
    assert 'PRIVATE-SECRET' not in result.text
    assert manager.starts == []


async def test_duplicate_filters_and_mismatched_loopback_origin_are_rejected(tmp_path):
    """重复 URL 字段与另一白名单 Host 的 Origin 也不能混淆请求解释。"""
    app, manager = application(tmp_path, enabled=True)
    async with client_for(app) as client:
        duplicate = await client.get(PREFIX + '/runs?limit=1&limit=2')
        mismatch = await client.post(PREFIX + '/runs', json=PAYLOAD,
            headers={'Origin': 'http://localhost:8001'})
    assert duplicate.status_code == 422
    assert mismatch.status_code == 403
    assert manager.starts == []


@pytest.mark.parametrize('tamper', ['publication_clock', 'duplicate_json_key', 'boolean_count'])
async def test_export_cannot_hide_secret_in_ignored_clock_or_duplicate_keys(tmp_path, tamper):
    """只容忍合法发布时钟差，文件原文不能藏入被 JSON 解析忽略的私密内容。"""
    from app.rag_evaluation.export import publish_reports, render_markdown
    app, manager = application(tmp_path)
    run_id = await manager.store.create(config(), [('E1', 'dense')])
    final = dict(await manager.store.get(run_id), state='failed', outcome='failed', stage='complete',
        cleanup={'ok': True, 'errors': [], 'unverified': []})
    publish_reports(tmp_path, final, [])
    await manager.store.update(run_id, {key: final[key] for key in ('state', 'outcome', 'stage', 'cleanup')})
    path = tmp_path / run_id / 'report.json'
    content = path.read_text(encoding='utf-8')
    if tamper != 'duplicate_json_key':
        value = json.loads(content)
        if tamper == 'publication_clock':
            value['run']['updated_at'] = 'PRIVATE-SECRET'
        else:
            value['run']['planned_records'] = True
        path.write_text(json.dumps(value, ensure_ascii=False, separators=(',', ':')), encoding='utf-8')
        (tmp_path / run_id / 'report.md').write_bytes(render_markdown(value).encode('utf-8'))
    else:
        path.write_text('{"schema_version":"PRIVATE-SECRET",' + content[1:], encoding='utf-8')
    async with client_for(app) as client:
        result = await client.get(f'{PREFIX}/runs/{run_id}/export')
    assert result.status_code == 409
    assert 'PRIVATE-SECRET' not in result.text


@pytest.mark.parametrize('endpoint', ['detail', 'history', 'datasets', 'cases', 'case', 'export'])
async def test_disabled_get_stale_checkpoint_never_repairs_foreign_manifest(tmp_path, monkeypatch, endpoint):
    """禁用工作台读取真实陈旧计数并保持磁盘字节，外来租约不授予HTTP写权限。"""
    app, manager = application(tmp_path)
    run_id = await manager.store.create(config(), [('E1', 'dense')])
    before = await stale_checkpoint(manager.store, run_id, record(status='rewrite_error'), monkeypatch)
    paths = {'detail': f'/runs/{run_id}', 'history': '/runs', 'datasets': '/datasets',
        'cases': f'/runs/{run_id}/cases', 'case': f'/runs/{run_id}/cases/E1/dense',
        'export': f'/runs/{run_id}/export'}
    lease = RunLock(tmp_path).acquire()
    try:
        async with client_for(app) as client:
            value = await client.get(PREFIX + paths[endpoint])
        assert value.status_code == (409 if endpoint == 'export' else 200)
        if endpoint == 'detail':
            assert value.json()['run']['counts']['errors'] == 1
            assert value.json()['run']['updated_at'] == json.loads(before)['updated_at']
        elif endpoint == 'history':
            assert value.json()['items'][0]['counts']['errors'] == 1
        elif endpoint == 'datasets':
            assert value.json()['items'][0]['matching_pilot'] is False
        assert (tmp_path / run_id / 'manifest.json').read_bytes() == before
        assert manager.starts == manager.cancels == []
    finally:
        lease.close()


async def test_actual_manager_foreign_cancel_reads_stale_counts_without_repair(tmp_path, monkeypatch):
    """启用后的取消请求也不能仅因读取另一个运行而修复对方manifest。"""
    from app.rag_evaluation.manager import DATASET_ROOT, RunManager
    store = RunStore(tmp_path)
    manager = RunManager(store, fake_settings(), DATASET_ROOT)
    run_id = await store.create(config(), [('E1', 'dense')])
    before = await stale_checkpoint(store, run_id, record(status='rewrite_error'), monkeypatch)
    app, _ = application(tmp_path, enabled=True, manager=manager)
    lease = RunLock(tmp_path).acquire()
    try:
        async with client_for(app) as client:
            result = await client.post(f'{PREFIX}/runs/{run_id}/cancel', json={})
        assert result.status_code == 200
        assert result.json()['counts']['errors'] == 1 and result.json()['state'] == 'queued'
        assert (tmp_path / run_id / 'manifest.json').read_bytes() == before
        assert manager._lease is None and manager._task is None
    finally:
        lease.close()
