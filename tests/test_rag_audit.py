"""来源、金标与带分数排序必须在资源清理后独立公开复核。"""

import asyncio
from dataclasses import replace, asdict
import copy
import json

import pytest

from app.rag_evaluation.contracts import GoldGroup, AnswerPoint
from app.rag_evaluation.export import report_envelope, publish_reports
from app.rag_evaluation.report import public_report
from app.rag_evaluation.store import RunStore, StoreError
from tests.test_rag_runner import setup
from tests.test_rag_api import application, client_for, ManagerDouble


async def test_missing_group_and_nonprompt_candidate_resolve_after_cleanup(tmp_path, monkeypatch):
    """删除借用资源后只凭磁盘公开封套还原遗漏组、原文、准确要点及两级分数。"""
    runner, resources, store, data, run_id, http = await setup(tmp_path)
    case = replace(data.cases[0], groups=(GoldGroup('g1', (('one',),)), GoldGroup('g2', (('two',),))),
        points=(AnswerPoint('p1', '精确金标秘密', '仅限未拆封', ('原封',)),))
    data = replace(data, cases=(case,))
    from tests.test_rag_resources import local_owner, api, settings, all_rows, MemoryIndex
    _, _, database = await local_owner(api(), tmp_path/'isolated', monkeypatch)
    owner = api().OwnedResources(settings(), store, run_id)
    mapping = await owner.prepare(data)
    try:
        assert await runner.run_cases(data, mapping, data.pilot_ids, asyncio.Event()) == 'completed'
    finally:
        await http.aclose()
        assert (await owner.cleanup()).ok
    assert await all_rows(database) == [] and owner.collection not in MemoryIndex.collections
    assert all('精确金标秘密' not in str(messages) for stage, messages in resources.model.inputs if stage != 'judge')
    del runner, resources, data
    app, _ = application(tmp_path, manager=ManagerDouble(RunStore(tmp_path)))
    async with client_for(app) as client:
        response = await client.get(f'/api/rag-evaluations/runs/{run_id}/cases/E0/hybrid_rerank')
    assert response.status_code == 200
    row = response.json()
    assert row.get('audit') is not None, '公开记录丢失来源/要点/排序审计'
    audit = row['audit']
    assert audit['audit_version'] == 1
    assert audit['gold_groups'][1] == {'group_id': 'g2', 'alternatives': [['two']]}
    assert audit['answer_points'] == [{'point_id': 'p1', 'text': '精确金标秘密', 'condition': '仅限未拆封', 'aliases': ['原封']}]
    assert audit['candidate_ranking'] == [dict(chunk_id=1, score=.9, score_kind='rrf'), dict(chunk_id=2, score=.8, score_kind='rrf')]
    assert audit['final_ranking'] == [dict(chunk_id=1, score=.9, score_kind='rerank')]
    assert row['metrics']['prompt_group_coverage'] == .5
    missing = next(item for item in row['source_map']['sources'] if item['chunk_id'] == 2)
    assert missing['chunk_key'] == 'two' and missing['document'] == 'two.md'
    assert missing['draft']['answer'] == '满99元包邮'
    assert row['source_map']['source_map_id'] == audit['source_map_id']
    assert all(item['chunk_id'] != '2' for item in row['prompt_citations'])


async def test_captured_audit_cannot_be_hidden_as_preaudit_export(tmp_path):
    """新记录已经捕获审计时，删除导出字段不能冒充历史未采集以绕过一致性检查。"""
    from app.rag_evaluation.export import render_markdown
    runner, _, store, data, run_id, http = await setup(tmp_path)
    try:
        await runner.run_cases(data, {'one': 1, 'two': 2}, data.pilot_ids, asyncio.Event())
    finally:
        await http.aclose()
    await store.update(run_id, dict(state='completed', outcome='completed', stage='complete',
        cleanup=dict(ok=True, errors=[], unverified=[])))
    saved = report_envelope(await store.get(run_id), await store.records(run_id), await store.source_map(run_id))
    saved.pop('source_map')
    for row in saved['records']:
        row.pop('audit')
    (tmp_path/run_id/'report.json').write_bytes(json.dumps(saved, ensure_ascii=False, separators=(',', ':')).encode('utf-8'))
    (tmp_path/run_id/'report.md').write_bytes(render_markdown(saved).encode('utf-8'))
    app, _ = application(tmp_path, manager=ManagerDouble(RunStore(tmp_path)))
    before = {path: (path.read_bytes(), path.stat().st_mtime_ns) for path in (tmp_path/run_id).rglob('*') if path.is_file()}
    async with client_for(app) as client:
        responses = [await client.get(f'/api/rag-evaluations/runs/{run_id}/export?format={kind}') for kind in ('json', 'markdown')]
    assert [response.status_code for response in responses] == [409, 409]
    assert before == {path: (path.read_bytes(), path.stat().st_mtime_ns) for path in (tmp_path/run_id).rglob('*') if path.is_file()}


async def test_audit_map_immutable_and_bad_ranking_rejected(tmp_path):
    """换源、重复分数、非有限分数与错映射均不能落盘成为审计事实。"""
    runner, _, store, data, run_id, http = await setup(tmp_path)
    try:
        await runner.run_cases(data, {'one': 1, 'two': 2}, data.pilot_ids, asyncio.Event())
    finally:
        await http.aclose()
    rows = await store.records(run_id)
    assert rows[0].get('audit') is not None, '缺失审计'
    source_map = await store.source_map(run_id)
    from app.rag_evaluation.audit import build_source_map
    changed_chunk = replace(data.chunks[0], draft=replace(data.chunks[0].draft, answer='篡改'))
    altered = build_source_map(replace(data, chunks=(changed_chunk, data.chunks[1])), {'one': 1, 'two': 2})
    path = tmp_path/run_id/'source-map.json'
    original_bytes, original_mtime = path.read_bytes(), path.stat().st_mtime_ns
    await store.put_source_map(run_id, source_map)
    assert path.read_bytes() == original_bytes and path.stat().st_mtime_ns == original_mtime
    with pytest.raises((ValueError, StoreError)):
        await store.put_source_map(run_id, altered)
    for change in ('score', 'identity', 'rubric', 'mapping', 'private'):
        invalid = copy.deepcopy(rows[0])
        if change == 'score':
            invalid['audit']['candidate_ranking'][0]['score'] = float('nan')
        elif change == 'identity':
            invalid['audit']['source_map_id'] = 'f' * 64
        elif change == 'rubric':
            invalid['audit']['answer_points'][0]['point_id'] = 'wrong'
        elif change == 'mapping':
            invalid['audit']['gold_groups'][0]['alternatives'] = [['two']]
        else:
            invalid['audit']['candidate_ranking'][0]['request_body'] = 'PRIVATE'
        with pytest.raises((ValueError, StoreError)):
            await store.put_case(run_id, invalid)
    assert path.read_bytes() == original_bytes


def test_historical_uncaptured_audit_is_explicitly_unavailable():
    """历史已存数据不能从当前语料伪造新捕获字段。"""
    from tests.test_rag_store import record
    report = public_report({'schema_version': 2, 'records': [record()]})
    assert 'source_map' in report and report['source_map'] is None
    assert 'audit' in report['records'][0] and report['records'][0]['audit'] is None


async def test_full_public_1200_records_preserve_complete_sources_within_bounds(tmp_path, monkeypatch):
    """真实300题原文与1200条受控已保存记录经过实际公开下载，无付费或新质量结论。"""
    from tests.test_rag_manager import Harness, DATASET_ID
    from app.rag_evaluation.audit import build_source_map
    from app.rag_evaluation.runner import _seed
    from app.rag_evaluation.report import STRATEGIES, case_metrics
    from app.rag_evaluation.manager import build_run_config
    from tests.test_rag_resources import settings
    from app.rag_evaluation.store import MAX_JSON_BYTES
    from app.rag_evaluation.export import MAX_EXPORT_BYTES
    h = Harness(monkeypatch, tmp_path)
    data = h.dataset
    store = h.store
    run_id = await store.create(build_run_config(data, settings(), 'full'),
        [(case.eval_id, strategy) for case in data.cases for strategy in STRATEGIES])
    mapping = {chunk.chunk_key: index + 1 for index, chunk in enumerate(data.chunks)}
    source_map = build_source_map(data, mapping)
    await store.put_source_map(run_id, source_map)
    for case in data.cases:
        for strategy in STRATEGIES:
            row = _seed(case, strategy, mapping, source_map['source_map_id'])
            candidate_kind = {'dense': 'cosine', 'bm25': 'bm25', 'hybrid': 'rrf', 'hybrid_rerank': 'rrf'}[strategy]
            row['audit'].update(candidate_ranking=[dict(chunk_id=i, score=1/i, score_kind=candidate_kind) for i in range(1, 51)],
                final_ranking=[dict(chunk_id=i, score=1/i, score_kind='rerank' if strategy == 'hybrid_rerank' else candidate_kind) for i in range(1, 11)])
            row.update(status='completed', stage='complete', refused=True,
                query_plan={'standard': case.query, 'expansions': []}, candidate_ids=list(range(1, 51)),
                final_ids=list(range(1, 11)), prompt_citations=[dict(n=i, chunk_id=str(i),
                    section_path=chunk.draft.section_path, question=chunk.draft.questions, answer=chunk.draft.answer)
                    for i, chunk in enumerate(data.chunks[:10], 1)],
                decision=dict(useful=False, reason='受控离线规模数据', response_kind='knowledge', source='self_check'),
                answer='受控规模验证拒答，不代表实际模型判断。',
                point_verdicts=[dict(point_id=point.point_id, covered=False, reason='受控缺覆盖') for point in case.points],
                claim_verdicts=[], elapsed_ms=1,
                judge_snapshot=dict(prompt_version='controlled-scale', finish_reason='stop', raw_response='PRIVATE-SCALE-RAW'))
            row['metrics'] = case_metrics(row)
            await store.put_case(run_id, row)
    await store.update(run_id, dict(state='completed', outcome='completed', stage='complete',
        cleanup=dict(ok=True, errors=[], unverified=[])))
    publish_reports(tmp_path, await store.get(run_id), await store.records(run_id), await store.source_map(run_id))
    app, _ = application(tmp_path, manager=ManagerDouble(RunStore(tmp_path)))
    async with client_for(app) as client:
        exported = await client.get(f'/api/rag-evaluations/runs/{run_id}/export')
        markdown = await client.get(f'/api/rag-evaluations/runs/{run_id}/export?format=markdown')
        listing = await client.get(f'/api/rag-evaluations/runs/{run_id}/cases?offset=1100&limit=100')
    assert exported.status_code == markdown.status_code == listing.status_code == 200
    public = exported.json()
    assert len(public['records']) == 1200 and listing.json()['total'] == 1200 and len(listing.json()['items']) == 100
    assert len(public['source_map']['sources']) == 50
    assert all(row['audit']['candidate_ranking'] and len(row['audit']['candidate_ranking']) == 50 for row in public['records'])
    assert [source['draft'] for source in public['source_map']['sources']] == [asdict(chunk.draft) for chunk in data.chunks]
    assert exported.content.count(b'"sources":') == markdown.content.count(b'"sources":') == 1
    assert b'PRIVATE-SCALE-RAW' not in exported.content and b'PRIVATE-SCALE-RAW' not in markdown.content
    sizes = dict(source_map=(tmp_path/run_id/'source-map.json').stat().st_size,
        max_record=max(path.stat().st_size for path in (tmp_path/run_id/'records').glob('*.json')),
        json=len(exported.content), markdown=len(markdown.content))
    assert sizes['source_map'] <= MAX_JSON_BYTES and sizes['max_record'] <= MAX_JSON_BYTES
    assert sizes['json'] < MAX_EXPORT_BYTES and sizes['markdown'] < MAX_EXPORT_BYTES
    print('AUDIT_SCALE_BYTES=' + json.dumps(sizes))


async def test_old_matching_pilot_without_captured_audit_cannot_unlock_full(tmp_path, monkeypatch):
    """同配置但未捕获审计的40条旧完成记录不能授权新全量费用。"""
    from tests.test_rag_manager import Harness, DATASET_ID
    from app.rag_evaluation.manager import PilotRequired
    h = Harness(monkeypatch, tmp_path)
    run_id = await h.manager.start(DATASET_ID, 'pilot')
    await h.manager.wait(run_id)
    assert await h.manager.pilot_ready(DATASET_ID)
    for path in (tmp_path/run_id/'records').glob('*.json'):
        row = json.loads(path.read_text(encoding='utf-8'))
        row.pop('audit')
        path.write_text(json.dumps(row, ensure_ascii=False), encoding='utf-8')
    (tmp_path/run_id/'source-map.json').unlink()
    fresh = type(h.manager)(RunStore(tmp_path), h.manager.settings, h.manager.dataset_root)
    assert await fresh.pilot_ready(DATASET_ID) is False
    with pytest.raises(PilotRequired):
        await fresh.start(DATASET_ID, 'full')


async def test_pilot_source_text_must_match_frozen_dataset(tmp_path, monkeypatch):
    """自洽但原文被换的来源映射不能靠保留出处摘要取得全量资格。"""
    from tests.test_rag_manager import Harness, DATASET_ID
    from app.rag_evaluation.audit import build_source_map
    h = Harness(monkeypatch, tmp_path)
    run_id = await h.manager.start(DATASET_ID, 'pilot')
    await h.manager.wait(run_id)
    data = h.dataset
    source_map = await h.store.source_map(run_id)
    mapping = {source['chunk_key']: source['chunk_id'] for source in source_map['sources']}
    altered = replace(data, chunks=(replace(data.chunks[0], draft=replace(data.chunks[0].draft,
        answer='不是冻结原文')), *data.chunks[1:]))
    forged = build_source_map(altered, mapping)
    (tmp_path/run_id/'source-map.json').write_text(json.dumps(forged), encoding='utf-8')
    for path in (tmp_path/run_id/'records').glob('*.json'):
        row = json.loads(path.read_text(encoding='utf-8'))
        row['audit']['source_map_id'] = forged['source_map_id']
        path.write_text(json.dumps(row), encoding='utf-8')
    fresh = type(h.manager)(RunStore(tmp_path), h.manager.settings, h.manager.dataset_root)
    assert await fresh.pilot_ready(DATASET_ID) is False
