"""运行文件存储行为测试，验证恢复、边界与私有数据隔离。"""

import asyncio
import importlib
import json
import os
from pathlib import Path

import pytest


def api():
    """缺失实现以功能断言失败，避免导入错误掩盖 RED。"""
    assert importlib.util.find_spec("app.rag_evaluation.store"), "尚未实现运行文件存储"
    return importlib.import_module("app.rag_evaluation.store")


def config():
    """构造完整冻结配置，不读取真实密钥也不调用上游。"""
    return dict(dataset_id="merchant-rag-300-v1", scope="pilot", fingerprint="a" * 64,
        mode="content_ablation", models={k: "local-test" for k in
            ("answer", "rewrite", "self_check", "judge", "embedding", "rerank")},
        budgets=dict(candidate_k=50, final_k=10, chunk_target_chars=1200, chunk_overlap_chars=120,
            case_concurrency=2, answer_output_tokens=512, rewrite_output_tokens=2048,
            self_check_output_tokens=2048, judge_input_tokens=16000, judge_output_tokens=2048,
            tool_input_tokens=8000, rewrite_timeout_s=60, self_check_timeout_s=20,
            faq_timeout_s=90, chat_timeout_s=240, judge_timeout_s=60,
            embedding_timeout_s=20, rerank_timeout_s=20, milvus_timeout_s=5, model_retries=0),
        prompt_versions={k: "v2" for k in ("rewrite", "self_check", "answer", "judge")},
        upstream_summary={k: "https://example.test" for k in ("llm", "embedding", "rerank")})


def record(eval_id="E1", strategy="dense", *, status="not_attempted"):
    """提供 report.py 的完整金标题目，未执行阶段全部保持空值。"""
    result = dict(eval_id=eval_id, strategy=strategy, bucket="E_multi", difficulty="multi",
        category=None, should_refuse=False, refused=None, status=status, stage="rewrite",
        query="退货规则", query_plan=None, mapped_groups=[{"group_id": "g1", "alternatives": [[1]]}],
        candidate_ids=None, final_ids=None, prompt_citations=None, decision=None, answer=None,
        point_verdicts=None, claim_verdicts=None, metrics=None, error=None, elapsed_ms=None,
        judge_snapshot=None)
    if status == "rewrite_error":
        result["error"] = {"code": "rewrite_failed", "type": "TimeoutError", "message": "PRIVATE-EXCEPTION"}
    return result


async def test_atomic_snapshot_failure_preserves_previous(tmp_path, monkeypatch):
    """替换失败不能截断已有 manifest，失败前的状态仍是有效 JSON。"""
    module = api()
    store = module.RunStore(tmp_path)
    run_id = await store.create(config(), [("E1", "dense")])
    before = (tmp_path / run_id / "manifest.json").read_bytes()
    def fail_replace(src, dst):
        """只注入文件系统发布失败，保留真实序列化和临时文件行为。"""
        raise OSError("磁盘发布失败")
    monkeypatch.setattr(module.os, "replace", fail_replace)
    with pytest.raises(module.StoreError):
        await store.update(run_id, {"state": "running", "stage": "prepare"})
    assert (tmp_path / run_id / "manifest.json").read_bytes() == before
    assert json.loads(before)["state"] == "queued"
    assert sorted(p.name for p in (tmp_path / run_id).iterdir()) == ["manifest.json", "records"]


async def test_case_checkpoint_reconciles_counts_after_restart(tmp_path, monkeypatch):
    """记录发布后 manifest 失败，重新打开仍从计划文件恢复准确计数。"""
    module = api()
    store = module.RunStore(tmp_path)
    run_id = await store.create(config(), [("E1", "dense"), ("E2", "bm25")])
    original = module.os.replace
    def fail_manifest(src, dst):
        """仅破坏第二步 manifest 发布，留下真实逐题检查点。"""
        if Path(dst).name == "manifest.json":
            raise OSError("manifest 发布失败")
        return original(src, dst)
    with monkeypatch.context() as patcher:
        patcher.setattr(module.os, "replace", fail_manifest)
        with pytest.raises(module.StoreError):
            await store.put_case(run_id, record(status="rewrite_error"))
    assert (await store.get(run_id))["counts"]["errors"] == 1
    resumed = module.RunStore(tmp_path)
    manifest = await resumed.get(run_id)
    assert manifest["counts"]["total"] == 2
    assert manifest["counts"]["errors"] == 1
    assert manifest["counts"]["not_attempted"] == 1
    assert len(await resumed.records(run_id)) == 1
    assert json.loads((tmp_path / run_id / "manifest.json").read_text("utf-8"))["counts"] == manifest["counts"]


async def test_path_escape_and_unknown_fields_rejected(tmp_path):
    """路径逃逸、任意对象与扩展私有字段必须在写盘前拒绝。"""
    module = api()
    store = module.RunStore(tmp_path)
    run_id = await store.create(config(), [("E1", "dense")])
    for bad_id in ("../outside", str(tmp_path), "g" * 32, "a" * 31):
        with pytest.raises(module.StoreError):
            await store.get(bad_id)
    for patch in ({"model_requests": "SECRET"}, {"config": config()}, {"counts": {}}, {"api_key": "SECRET"}):
        with pytest.raises(module.StoreError):
            await store.update(run_id, patch)
    bad = record()
    bad["generation_input"] = "SECRET"
    with pytest.raises(module.StoreError):
        await store.put_case(run_id, bad)
    with pytest.raises(module.StoreError):
        await store.put_case(run_id, record("UNPLANNED"))
    with pytest.raises(module.StoreError):
        await store.create(dict(config(), api_key="SECRET"), [("E1", "dense")])


async def test_create_freezes_plan_without_fabricating_gold(tmp_path):
    """初始化没有物理金标时仍保存计划数，但不制造不完整记录。"""
    module = api()
    value = config()
    store = module.RunStore(tmp_path)
    run_id = await store.create(value, [("E1", "dense"), ("E1", "bm25")])
    value["models"]["answer"] = "changed"
    initial = await store.get(run_id)
    assert len(run_id) == 32 and int(run_id, 16) >= 0
    assert (initial["planned_cases"], initial["planned_strategies"], initial["planned_records"]) == (1, 2, 2)
    assert initial["config"]["models"]["answer"] == "local-test"
    assert initial["counts"]["not_attempted"] == 2
    assert await store.records(run_id) == []
    await store.update(run_id, {"state": "failed", "outcome": "failed", "stage": "prepare",
        "error": {"code": "prepare_failed", "type": "RuntimeError", "message": "SECRET"}})
    public = module.public_run_metadata(await store.get(run_id))
    assert "SECRET" not in json.dumps(public) and "ownership" not in public and "case_keys" not in public
    assert public["counts"]["not_attempted"] == 2
    assert all(value == 0 for value in public["request_counts"].values())


@pytest.mark.parametrize("section,key,value", [
    ("budgets", "case_concurrency", 3), ("budgets", "case_concurrency", True),
    ("budgets", "model_retries", 1), ("budgets", "answer_output_tokens", 1024),
    ("budgets", "milvus_timeout_s", float("nan")), ("models", "api_key", "SECRET"),
    ("upstream_summary", "llm", "https://user:secret@example.test"),
    ("upstream_summary", "llm", "https://example.test/v1?secret=bad"),
    ("upstream_summary", "llm", "https://example.test/#secret"),
])
async def test_config_rejects_unsafe_or_unbounded_fields(tmp_path, section, key, value):
    """无界预算、伪整数及含凭据地址不能成为冻结运行配置。"""
    module = api()
    value_config = config()
    value_config[section][key] = value
    with pytest.raises(module.StoreError):
        await module.RunStore(tmp_path).create(value_config, [("E1", "dense")])
    assert list(tmp_path.iterdir()) == []


async def test_ownership_registration_is_strict_and_private(tmp_path):
    """预提交主键须与摘要共同登记，公共 DTO 永不公开私有归属。"""
    module = api()
    store = module.RunStore(tmp_path)
    run_id = await store.create(config(), [("E1", "dense")])
    owned = dict(database={"host": "localhost", "port": 3308, "name": "customer_service_test"},
        collection="knowledge_test_" + run_id, owned_ids=[1, 2], pending_ids=[2],
        content_hashes={"1": "a" * 64, "2": "b" * 64})
    await store.update(run_id, {"ownership": owned})
    manifest = await store.get(run_id)
    assert manifest["ownership"]["database"]["host"] == "127.0.0.1"
    assert "content_hashes" not in json.dumps(module.public_run_metadata(manifest))
    for update in ({"collection": "knowledge_hybrid"}, {"owned_ids": [1]},
                   {"content_hashes": {"1": "a" * 64}}, {"pending_ids": [3]},
                   {"database": {"host": "127.0.0.1", "port": 3307, "name": "customer_service_test"}}):
        with pytest.raises(module.StoreError):
            await store.update(run_id, {"ownership": dict(owned, **update)})


async def test_parallel_checkpoints_listing_and_cancellation(tmp_path):
    """不同 store 实例并发发布不丢计数，等待者取消不影响已发布快照。"""
    module = api()
    store = module.RunStore(tmp_path)
    other = module.RunStore(tmp_path / ".")
    run_id = await store.create(config(), [("E1", "dense"), ("E2", "bm25")])
    await asyncio.gather(store.put_case(run_id, record(status="rewrite_error")),
        other.put_case(run_id, record("E2", "bm25", status="rewrite_error")))
    assert (await store.get(run_id))["counts"]["errors"] == 2
    assert len(await store.list_runs()) == 1
    assert await store.list_runs(offset=1) == []
    with pytest.raises(module.StoreError):
        await store.list_runs(limit=1000)
    async with store._writer():
        task = asyncio.create_task(store.update(run_id, {"state": "running"}))
        await asyncio.sleep(0)
        assert not task.done()
        task.cancel()
        with pytest.raises(asyncio.CancelledError):
            await task
    assert (await store.get(run_id))["state"] == "queued"


async def test_record_schema_and_tampered_checkpoint_are_rejected(tmp_path):
    """复用报告完整阶段契约；磁盘上非计划题与伪造成功也必须报错。"""
    module = api()
    store = module.RunStore(tmp_path)
    run_id = await store.create(config(), [("E1", "dense")])
    bad = record()
    bad["answer"] = "伪造尚未生成的答案"
    with pytest.raises(module.StoreError):
        await store.put_case(run_id, bad)
    (tmp_path / run_id / "records" / "E2--dense.json").write_text(json.dumps(record("E2")), encoding="utf-8")
    with pytest.raises(module.StoreError):
        await store.get(run_id)


async def test_symlink_record_directory_cannot_escape_root(tmp_path):
    """恶意 records 落点不得写出根目录；系统无法建链接时显式跳过。"""
    module = api()
    root = tmp_path / "runs"
    outside = tmp_path / "outside"
    outside.mkdir()
    store = module.RunStore(root)
    run_id = await store.create(config(), [("E1", "dense")])
    records = root / run_id / "records"
    records.rmdir()
    try:
        records.symlink_to(outside, target_is_directory=True)
    except OSError:
        records.mkdir()
        pytest.skip("本机没有创建目录符号链接权限")
    with pytest.raises(module.StoreError):
        await store.put_case(run_id, record())
    assert list(outside.iterdir()) == []


async def test_restart_rejects_conflicting_frozen_case_metadata(tmp_path):
    """重启不能接受四路题面或物理金标已经分歧的计划检查点。"""
    module = api()
    store = module.RunStore(tmp_path)
    run_id = await store.create(config(), [("E1", "dense"), ("E1", "bm25")])
    await store.put_case(run_id, record())
    other = record(strategy="bm25")
    other["query"] = "已被改动的题面"
    (tmp_path / run_id / "records" / "E1--bm25.json").write_text(json.dumps(other), encoding="utf-8")
    with pytest.raises(module.StoreError):
        await module.RunStore(tmp_path).records(run_id)


async def test_private_snapshot_projection_nested_fields_and_cleanup_outcome(tmp_path):
    """私有原文只在本地，嵌套未知字段拒绝；清理失败保留原评估 outcome。"""
    module = api()
    from app.rag_evaluation.report import public_report
    store = module.RunStore(tmp_path)
    run_id = await store.create(config(), [("E1", "dense")])
    row = record()
    row.update(status="judge_error", stage="judgment", refused=False,
        query_plan={"standard": "退货规则", "expansions": []}, candidate_ids=[1], final_ids=[1],
        prompt_citations=[{"n": 1, "chunk_id": "1", "section_path": None, "question": "问", "answer": "答"}],
        decision={"useful": True, "reason": "充分", "response_kind": "knowledge", "source": "self_check"},
        answer="七天内退货", judge_snapshot={"prompt_version": "v2", "finish_reason": "length", "raw_response": "PRIVATE-JUDGE"},
        error={"code": "judge_failed", "type": "JudgeError", "message": "PRIVATE-ERROR"})
    row["query_plan"]["api_key"] = "SECRET"
    with pytest.raises(module.StoreError):
        await store.put_case(run_id, row)
    del row["query_plan"]["api_key"]
    await store.put_case(run_id, row)
    local = await store.records(run_id)
    assert local[0]["judge_snapshot"]["raw_response"] == "PRIVATE-JUDGE"
    assert "PRIVATE" not in json.dumps(public_report({"schema_version": 2, "records": local}))
    await store.update(run_id, {"state": "completed_with_errors", "outcome": "completed_with_errors"})
    await store.update(run_id, {"state": "failed", "stage": "cleanup", "cleanup":
        {"ok": False, "errors": ["PRIVATE-SQL-EXCEPTION"], "unverified": ["PRIVATE-RESOURCE"]}})
    public = module.public_run_metadata(await store.get(run_id))
    assert public["state"] == "failed" and public["outcome"] == "completed_with_errors"
    assert "PRIVATE" not in json.dumps(public)


async def test_cumulative_ownership_requests_and_tampered_manifest(tmp_path):
    """预提交登记不可撤回或改摘要；非白名单磁盘 manifest 必须拒绝。"""
    module = api()
    store = module.RunStore(tmp_path)
    run_id = await store.create(config(), [("E1", "dense")])
    owned = dict(database={"host": "127.0.0.1", "port": 3308, "name": "customer_service_test"},
        collection="knowledge_test_" + run_id, owned_ids=[1], pending_ids=[1], content_hashes={"1": "a" * 64})
    await store.update(run_id, {"ownership": owned})
    await store.update(run_id, {"ownership": dict(owned, pending_ids=[])})
    for changed in (dict(owned, owned_ids=[], pending_ids=[], content_hashes={}),
                    dict(owned, content_hashes={"1": "b" * 64})):
        with pytest.raises(module.StoreError):
            await store.update(run_id, {"ownership": changed})
    requests = (await store.get(run_id))["request_counts"]
    requests["milvus"] = 1
    await store.update(run_id, {"request_counts": requests})
    requests["milvus"] = 0
    with pytest.raises(module.StoreError):
        await store.update(run_id, {"request_counts": requests})
    path = tmp_path / run_id / "manifest.json"
    manifest = json.loads(path.read_text("utf-8"))
    manifest["model_requests"] = "SECRET"
    path.write_text(json.dumps(manifest), encoding="utf-8")
    with pytest.raises(module.StoreError):
        await module.RunStore(tmp_path).get(run_id)


async def test_repeated_checkpoints_do_not_reload_all_case_json(tmp_path, monkeypatch):
    """稳定态小批量更新必须避免累计重读所有逐题JSON，两个实例共享最新快照。"""
    module = api()
    store = module.RunStore(tmp_path)
    other = module.RunStore(tmp_path / ".")
    keys = [(f"E{index}", "dense") for index in range(1, 9)]
    run_id = await store.create(config(), keys)
    for eval_id, strategy in keys:
        await store.put_case(run_id, record(eval_id, strategy))
    await other.get(run_id)
    await store.get(run_id)
    reads = []
    real_open = Path.open
    def count_case_reads(path, mode="r", *args, **kwargs):
        """记录真实文件打开次数，保持文件内容、JSON解析和发布行为完整。"""
        if "records" in path.parts and path.suffix == ".json" and "r" in mode:
            reads.append(path)
        return real_open(path, mode, *args, **kwargs)
    monkeypatch.setattr(Path, "open", count_case_reads)
    for index, (eval_id, strategy) in enumerate(keys):
        writer = store if index % 2 == 0 else other
        await writer.update(run_id, {"state": "preparing"})
        await writer.put_case(run_id, record(eval_id, strategy, status="rewrite_error"))
        assert (await other.get(run_id))["counts"]["errors"] == index + 1
    assert len(await store.records(run_id)) == 8
    assert len(await other.list_runs()) == 1
    assert reads == []


@pytest.mark.skipif(os.name != "nt", reason="本用例核验Windows大小写不敏感文件名")
async def test_windows_planned_filename_case_alias_is_rejected(tmp_path):
    """语义不同的题号大小写别名不能在Windows成为同一个检查点文件。"""
    module = api()
    with pytest.raises(module.StoreError):
        await module.RunStore(tmp_path).create(config(), [("E1", "dense"), ("e1", "dense")])
    assert list(tmp_path.iterdir()) == []


async def test_shared_cache_keeps_ownership_counters_and_returned_copies_independent(tmp_path):
    """旧实例不得撤回其他实例新增归属或请求数，返回值修改不污染缓存。"""
    module = api()
    store = module.RunStore(tmp_path)
    other = module.RunStore(tmp_path)
    run_id = await store.create(config(), [("E1", "dense")])
    await other.get(run_id)
    first = dict(database={"host": "127.0.0.1", "port": 3308, "name": "customer_service_test"},
        collection="knowledge_test_" + run_id, owned_ids=[1], pending_ids=[1], content_hashes={"1": "a" * 64})
    await store.update(run_id, {"ownership": first})
    await other.update(run_id, {"ownership": dict(first, owned_ids=[1, 2], pending_ids=[2],
        content_hashes={"1": "a" * 64, "2": "b" * 64})})
    with pytest.raises(module.StoreError):
        await store.update(run_id, {"ownership": first})
    requests = (await other.get(run_id))["request_counts"]
    requests["milvus"] = 5
    await other.update(run_id, {"request_counts": requests})
    requests["milvus"] = 4
    with pytest.raises(module.StoreError):
        await store.update(run_id, {"request_counts": requests})
    view = await store.get(run_id)
    view["ownership"]["owned_ids"].clear()
    view["request_counts"]["milvus"] = 0
    assert (await other.get(run_id))["ownership"]["owned_ids"] == [1, 2]
    assert (await other.get(run_id))["request_counts"]["milvus"] == 5
    await store.put_case(run_id, record())
    rows = await store.records(run_id)
    rows[0]["query"] = "调用方改动的副本"
    assert (await other.records(run_id))[0]["query"] == "退货规则"


async def test_new_instance_revalidates_in_place_corrupted_case_despite_shared_cache(tmp_path):
    """新实例必须重新校验磁盘，不能沿用其他实例缓存而遗漏原位文件损坏。"""
    module = api()
    store = module.RunStore(tmp_path)
    run_id = await store.create(config(), [("E1", "dense")])
    await store.put_case(run_id, record())
    await store.get(run_id)
    damaged = record()
    damaged["answer"] = "尚未生成的伪造答案"
    (tmp_path / run_id / "records" / "E1--dense.json").write_text(json.dumps(damaged), encoding="utf-8")
    with pytest.raises(module.StoreError):
        await module.RunStore(tmp_path).get(run_id)
