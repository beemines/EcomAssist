"""评估低思考配置的真实请求、出处兼容与试运行门槛回归。"""

import asyncio
from collections import Counter
import copy
import json
from pathlib import Path

import httpx
from pydantic import ValidationError
import pytest

from app.config import Settings
from app.core.llm import create_model, model_with_output_budget
from app.rag_evaluation.manager import build_run_config
from app.rag_evaluation.resources import OwnedResources, RequestCounter
from app.rag_evaluation.runner import EvaluationRunner
from app.rag_evaluation.store import RunStore, StoreError, public_run_metadata, validate_config
from tests.test_rag_api import PREFIX, application, client_for
from tests.test_rag_manager import DATASET_ID, Harness
from tests.test_rag_metrics import record as completed_record
from tests.test_rag_resources import settings
from tests.test_rag_runner import Retrieval, frozen


@pytest.mark.parametrize('effort', [None, 'low', 'high', 'max'])
def test_dedicated_effort_accepts_only_provider_values(effort):
    """缺失专属配置字段或改变允许值会阻断明确的评估配置。"""
    value = Settings(_env_file=None, llm_base_url='https://example.test/v1',
        llm_model='local-test', llm_api_key='test', RAG_EVALUATION_REASONING_EFFORT=effort)
    assert value.rag_evaluation_reasoning_effort == effort
    assert settings().rag_evaluation_reasoning_effort is None


@pytest.mark.parametrize('effort', [True, False, '', ' ', 'medium', 'unknown', 1])
def test_dedicated_effort_rejects_unsafe_values(effort):
    """布尔、空白和未知枚举不能偷偷回退为低思考。"""
    with pytest.raises(ValidationError):
        Settings(_env_file=None, llm_base_url='https://example.test/v1',
            llm_model='local-test', llm_api_key='test', rag_evaluation_reasoning_effort=effort)


@pytest.mark.parametrize('token_field', ['max_tokens', 'max_completion_tokens'])
async def test_real_evaluation_consumers_send_low_without_touching_online(tmp_path, monkeypatch, token_field):
    """漏传拥有者配置或预算副本丢参会在四阶段真实SDK正文上暴露。"""
    online_settings = settings().model_copy(update={'llm_token_limit_field': token_field})
    configuration = online_settings.model_copy(update={'rag_evaluation_reasoning_effort': 'low'})
    online_before = online_settings.model_dump()
    data, store = frozen(), RunStore(tmp_path)
    config = build_run_config(data, configuration, 'pilot')
    run_id = await store.create(config, [(data.cases[0].eval_id, s)
        for s in ('dense', 'bm25', 'hybrid', 'hybrid_rerank')])
    owner = OwnedResources(configuration, store, run_id)
    owner.requests = RequestCounter(store, run_id, (await store.get(run_id))['request_counts'])
    requests, closed = [], Counter()

    async def respond(request):
        """只替换HTTP传输；工厂、规划、自检、流回答和联合裁判均执行生产代码。"""
        body = json.loads(request.content)
        requests.append(body)
        if body.get('stream'):
            events = [dict(id='chatcmpl-test', object='chat.completion.chunk', created=0,
                model='local-test', choices=[dict(index=0, delta=dict(role='assistant', content='七天退货。[1]'),
                    finish_reason=None)]),
                dict(id='chatcmpl-test', object='chat.completion.chunk', created=0, model='local-test',
                    choices=[dict(index=0, delta={}, finish_reason='stop')])]
            return httpx.Response(200, headers={'Content-Type': 'text/event-stream'},
                content=''.join('data: ' + json.dumps(event, ensure_ascii=False) + '\n\n' for event in events)
                    + 'data: [DONE]\n\n')
        messages = body['messages']
        if 'coverage_rubric' in messages[-1]['content']:
            reply = dict(points=[dict(point_id='p1', covered=True, reason='覆盖')],
                claims=[dict(claim='七天退货', supported=True, reason='证据支持')])
        elif 'response_format' in body and 'expansions' in messages[0]['content']:
            reply = dict(standard='HX-600可以退货吗？', expansions=[])
        elif 'response_format' in body:
            reply = dict(useful=True, reason='正文支持', response_kind='knowledge')
        else:
            reply = '完成'
        return httpx.Response(200, json=dict(id='chatcmpl-test', object='chat.completion', created=0,
            model='local-test', choices=[dict(index=0, message=dict(role='assistant',
                content=json.dumps(reply, ensure_ascii=False) if isinstance(reply, dict) else reply), finish_reason='stop')]))

    def local_http(hook):
        """注册实际HTTP客户端的一次关闭，网络仅能进入进程内MockTransport。"""
        client = httpx.AsyncClient(transport=httpx.MockTransport(respond), event_hooks={'request': [hook]})
        original = client.aclose
        async def close():
            """保留真实关闭行为并记录拥有者有无重复关闭。"""
            closed[id(client)] += 1
            await original()
        owner._http_clients.append(client)
        owner._closers.append(('http', close))
        return client

    monkeypatch.setattr(owner, '_http', local_http)
    async with httpx.AsyncClient(transport=httpx.MockTransport(respond)) as online_http:
        online = create_model(online_settings, http_async_client=online_http)
        try:
            owner._models()
            for model in (owner.model, owner.judge_model):
                original = model.root_client.close
                def close_model(original=original, identity=id(model)):
                    """只观察拥有者的真实SDK关闭，不改变客户端所有权。"""
                    closed[identity] += 1
                    original()
                monkeypatch.setattr(model.root_client, 'close', close_model)
            budget = model_with_output_budget(owner.model, configuration, 2048)
            assert budget.extra_body is not owner.model.extra_body
            assert budget.root_client is owner.model.root_client and budget.root_async_client is owner.model.root_async_client
            budget.extra_body['test_only'] = True
            assert 'test_only' not in owner.model.extra_body
            assert owner.model.extra_body == {token_field: 512}
            assert owner.judge_model.extra_body == {token_field: 2048}
            assert owner.model.max_retries == owner.judge_model.max_retries == 0
            assert owner.model.request_timeout == owner.judge_model.request_timeout == 60
            # 本测试跳过外部资料导入，检索边界替身接管缺失的仓储。
            owner.repository = None
            runner = EvaluationRunner(owner, store, run_id, configuration)
            runner.retrieval = Retrieval()
            assert await runner.run_cases(data, {'one': 1, 'two': 2}, data.pilot_ids, asyncio.Event()) == 'completed'
            counts = (await store.get(run_id))['request_counts']
            assert [counts[s] for s in ('rewrite', 'self_check', 'answer', 'judge')] == [1, 4, 4, 4]
            assert len(requests) == 13
            assert all(body.get('reasoning_effort') == 'low' for body in requests)
            assert Counter(body[token_field] for body in requests) == {512: 4, 2048: 9}
            other_field = 'max_completion_tokens' if token_field == 'max_tokens' else 'max_tokens'
            assert all(other_field not in body and 'extra_body' not in body for body in requests)
            assert config['provenance']['llm_reasoning_effort'] == owner.model.reasoning_effort == owner.judge_model.reasoning_effort == budget.reasoning_effort == 'low'
            # 相同配置有评估低思考时，普通工厂仍不会自行使用该专属字段。
            await online.ainvoke('测试')
            default_from_eval = create_model(configuration, http_async_client=online_http)
            try:
                await default_from_eval.ainvoke('测试')
            finally:
                default_from_eval.root_client.close()
            assert all('reasoning_effort' not in body for body in requests[-2:])
            assert online.reasoning_effort is None and online_settings.model_dump() == online_before
        finally:
            online.root_client.close()
            assert (await owner.cleanup()).ok
            assert (await owner.cleanup()).ok
        assert set(closed.values()) == {1} and len(closed) == 5
        assert all(client.is_closed for client in owner._http_clients)


def test_effective_effort_changes_fingerprint_but_scope_does_not():
    """漏捕获实际努力等级会让其他配置试运行错误授权全量。"""
    # 题库读取走生产冻结加载入口，不构造假指纹。
    from app.rag_evaluation.dataset import load_dataset
    data = load_dataset(DATASET_ID, root=Path(__file__).resolve().parents[1] / 'evals/datasets')
    configs = [build_run_config(data, settings().model_copy(update={'rag_evaluation_reasoning_effort': effort}), 'pilot')
        for effort in (None, 'low', 'high', 'max')]
    assert [c['provenance'].get('llm_reasoning_effort', 'missing') for c in configs] == [None, 'low', 'high', 'max']
    assert len({c['fingerprint'] for c in configs}) == 4
    for effort, config in zip((None, 'low', 'high', 'max'), configs):
        full = build_run_config(data, settings().model_copy(update={'rag_evaluation_reasoning_effort': effort}), 'full')
        assert full['fingerprint'] == config['fingerprint']
        assert config['models'] == configs[0]['models'] and config['budgets'] == configs[0]['budgets']
        assert config['provenance']['llm_timeout_s'] == 60 and config['budgets']['model_retries'] == 0


@pytest.mark.parametrize('effort', [None, 'low', 'high', 'max'])
def test_provenance_effort_is_optional_strict_and_does_not_invent_history(effort):
    """新安全字段可显式为空；旧字段缺失必须保持缺失，任意私有扩展仍拒绝。"""
    config = build_run_config(frozen(), settings(), 'pilot')
    old = copy.deepcopy(config)
    old['provenance'].pop('llm_reasoning_effort', None)
    assert 'llm_reasoning_effort' not in validate_config(old)['provenance']
    config['provenance']['llm_reasoning_effort'] = effort
    assert validate_config(config)['provenance']['llm_reasoning_effort'] == effort
    for invalid in (True, False, '', 'medium', 'private', [], {}):
        bad = copy.deepcopy(config)
        bad['provenance']['llm_reasoning_effort'] = invalid
        with pytest.raises(StoreError):
            validate_config(bad)
    bad = copy.deepcopy(config)
    bad['provenance']['raw_request'] = 'PRIVATE-SECRET'
    with pytest.raises(StoreError):
        validate_config(bad)


@pytest.mark.parametrize('effort', ['absent', None, 'low'])
async def test_legacy_and_null_provenance_survive_public_pair_without_rewrite(tmp_path, effort):
    """GET补造努力等级或重写配对导出会破坏旧证据字节及文件时钟。"""
    from app.rag_evaluation.export import publish_reports
    app, manager = application(tmp_path)
    config = build_run_config(frozen(), settings(), 'pilot')
    if effort == 'absent':
        config['provenance'].pop('llm_reasoning_effort', None)
    else:
        config['provenance']['llm_reasoning_effort'] = effort
    run_id = await manager.store.create(config, [('E1', 'dense')])
    await manager.store.put_case(run_id, completed_record('E1', 'dense'))
    final = dict(await manager.store.get(run_id), state='completed', outcome='completed', stage='complete',
        cleanup={'ok': True, 'errors': [], 'unverified': []})
    publish_reports(tmp_path, final, await manager.store.records(run_id))
    await manager.store.update(run_id, {key: final[key] for key in ('state', 'outcome', 'stage', 'cleanup')})
    before = {p: (p.read_bytes(), p.stat().st_mtime_ns) for p in (tmp_path / run_id).rglob('*') if p.is_file()}
    async with client_for(app) as client:
        detail = await client.get(f'{PREFIX}/runs/{run_id}')
        downloads = [await client.get(f'{PREFIX}/runs/{run_id}/export?format={kind}') for kind in ('json', 'markdown')]
    assert detail.status_code == 200 and [r.status_code for r in downloads] == [200, 200]
    projections = [public_run_metadata(await manager.store.get(run_id))['config'], detail.json()['run']['config'],
        downloads[0].json()['run']['config']]
    for projection in projections:
        if effort == 'absent':
            assert 'llm_reasoning_effort' not in projection['provenance']
        else:
            assert projection['provenance']['llm_reasoning_effort'] == effort
    assert downloads[0].content == before[tmp_path / run_id / 'report.json'][0]
    assert downloads[1].content == before[tmp_path / run_id / 'report.md'][0]
    assert before == {p: (p.read_bytes(), p.stat().st_mtime_ns) for p in (tmp_path / run_id).rglob('*') if p.is_file()}


@pytest.mark.parametrize('previous_effort', ['absent', None, 'high', 'max'])
async def test_legal_old_or_different_pilot_cannot_authorize_low_full(tmp_path, monkeypatch, previous_effort):
    """保留真实40条审计与源映射门槛，只改努力等级就必须拒绝旧试运行。"""
    h = Harness(monkeypatch, tmp_path)
    original = h.module.build_run_config
    if previous_effort == 'absent':
        def old_config(data, configuration, scope):
            """模拟已捕获出处但尚无努力字段的历史构建结果。"""
            config = original(data, configuration, scope)
            config['provenance'].pop('llm_reasoning_effort', None)
            config['fingerprint'] = h.module._digest({k: v for k, v in config.items() if k not in ('scope', 'fingerprint')})
            return config
        monkeypatch.setattr(h.module, 'build_run_config', old_config)
    else:
        h.manager.settings = settings().model_copy(update={'rag_evaluation_reasoning_effort': previous_effort})
    pilot = await h.manager.start(DATASET_ID, 'pilot')
    result = await h.manager.wait(pilot)
    assert result['counts']['completed'] == 40 and result['cleanup']['ok']
    assert await h.store.source_map(pilot) is not None
    monkeypatch.setattr(h.module, 'build_run_config', original)
    h.manager.settings = settings().model_copy(update={'rag_evaluation_reasoning_effort': 'low'})
    assert not await h.manager.pilot_ready(DATASET_ID)
    with pytest.raises(h.module.PilotRequired):
        await h.manager.start(DATASET_ID, 'full')
    assert h.calls == 1
    same = await h.manager.start(DATASET_ID, 'pilot')
    assert (await h.manager.wait(same))['counts']['completed'] == 40
    assert await h.manager.pilot_ready(DATASET_ID)
    assert h.calls == 2
    # 同低思考完整试运行通过真正 full 启动门槛；立即取消避免多跑离线替身。
    full = await h.manager.start(DATASET_ID, 'full')
    await h.manager.cancel(full)
    assert (await h.manager.wait(full))['planned_records'] == 1200
