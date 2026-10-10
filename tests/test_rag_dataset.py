"""离线冻结输入的边界测试，防止坏标注进入任何收费或数据库流程。"""

from collections import Counter
from dataclasses import FrozenInstanceError, replace
import hashlib
import importlib
import json
from pathlib import Path
import shutil
import socket

import pytest

ROOT = Path(__file__).resolve().parents[1] / "evals" / "datasets"


def api():
    """缺失实现时给出明确 RED 断言，不用导入错误掩盖测试意图。"""
    assert importlib.util.find_spec("app.rag_evaluation") is not None, "尚未实现离线数据集加载器"
    return importlib.import_module("app.rag_evaluation.dataset")


def rehash(folder, filename):
    """只更新被篡改文件的外层哈希，确保测试能触达语义校验。"""
    path = folder / "manifest.json"
    manifest = json.loads(path.read_text(encoding="utf-8"))
    manifest["files"][filename] = hashlib.sha256((folder / filename).read_bytes()).hexdigest()
    path.write_text(json.dumps(manifest, ensure_ascii=False), encoding="utf-8")


def mutate_jsonl(folder, filename, mutate):
    """修改一条真实冻结记录并保持文件哈希一致，模拟错误审标。"""
    path = folder / filename
    rows = [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines()]
    mutate(rows)
    path.write_text("\n".join(json.dumps(row, ensure_ascii=False) for row in rows) + "\n", encoding="utf-8")
    rehash(folder, filename)


def test_300_unique_cases_and_five_buckets():
    """丢题、重复题、桶错配和错误试运行抽样都会破坏可运行集合。"""
    data = api().load_dataset("merchant-rag-300-v1", root=ROOT)
    assert len(data.cases) == len({case.eval_id for case in data.cases}) == 300
    assert Counter(case.bucket for case in data.cases) == {
        "A_policy": 60, "B_model": 60, "C_colloquial": 60, "D_unanswerable": 60, "E_multi": 60,
    }
    assert len(data.chunks) == 50
    assert data.pilot_ids == ("A21", "A43", "B3", "B54", "C5", "C35", "D1", "D3", "E2", "E19")
    assert len({case.ledger_eval_id for case in data.cases}) == 300
    assert all(case.should_refuse == (case.bucket == "D_unanswerable") for case in data.cases)
    with pytest.raises(FrozenInstanceError):
        data.cases[0].query = "覆盖题面"


def test_group_alternative_requires_complete_bundle():
    """误把 AND 组合扁平化为 OR 会让只取到第一块被误判为完整证据。"""
    mod = api()
    from app.rag_evaluation.contracts import GoldGroup
    base = mod.load_dataset("merchant-rag-300-v1", root=ROOT).cases[0]
    case = replace(base, groups=(GoldGroup("g1", (("a", "b"), ("c",))),))
    group, = mod.map_groups(case, {"a": 11, "b": 12, "c": 13})
    assert group.alternatives == ((11, 12), (13,))
    assert not any(set(bundle) <= {11} for bundle in group.alternatives)
    assert any(set(bundle) <= {11, 12} for bundle in group.alternatives)
    assert any(set(bundle) <= {13} for bundle in group.alternatives)
    for invalid in ({"a": 11}, {"a": 11, "b": 11, "c": 13}, {"a": True, "b": 12, "c": 13}):
        with pytest.raises(mod.DatasetError):
            mod.map_groups(case, invalid)


def test_ledger_key_changes_with_query_and_fits_16():
    """题位换题必须分离历史台账，同时满足既有数据库字段长度。"""
    mod = api()
    old = mod.ledger_key("D3", "能不能开纸质发票邮寄给我")
    new = mod.ledger_key("D3", "纸质发票遗失后能申请挂失证明吗")
    assert old != new
    assert new == mod.ledger_key("D3", "纸质发票遗失后能申请挂失证明吗")
    assert len(mod.ledger_key("E60", "任意中文题面")) <= 16
    with pytest.raises(mod.DatasetError):
        mod.ledger_key("../../escape", "问题")


@pytest.mark.parametrize("damage", ["hash", "gold", "category", "reason", "source", "duplicate", "e_duplicate", "refusal", "utf8"])
def test_freeze_rejects_bad_hash_empty_gold_unknown_category_and_missing_reason(tmp_path, monkeypatch, damage):
    """即使外层哈希被重算，非法金标和缺失理由仍须在零网络调用时拒绝。"""
    mod = api()
    folder = tmp_path / "merchant-rag-300"
    shutil.copytree(ROOT / "merchant-rag-300", folder)
    calls = []

    def deny_network(*args, **kwargs):
        """记录意外网络访问并立刻使测试失败，覆盖云模型和数据库连接。"""
        calls.append(args)
        raise AssertionError("离线加载器禁止网络访问")

    monkeypatch.setattr(socket, "socket", deny_network)
    if damage == "hash":
        with (folder / "cases.jsonl").open("a", encoding="utf-8") as stream:
            stream.write(" ")
    elif damage == "utf8":
        (folder / "audit.jsonl").write_bytes(b"\xff")
        rehash(folder, "audit.jsonl")
    else:
        filename = "audit.jsonl" if damage == "reason" else "cases.jsonl"

        def damage_row(rows):
            """按参数制造具有具体业务后果的单项错误。"""
            if damage == "gold":
                rows[0]["groups"] = []
            elif damage == "category":
                rows[0]["category"] = "未知品类"
            elif damage == "reason":
                rows[0]["reason"] = ""
            elif damage == "source":
                rows[0]["point_sources"]["p1"][0]["quote"] = "资料里不存在的承诺"
            elif damage == "duplicate":
                rows[1]["eval_id"] = rows[0]["eval_id"]
            elif damage == "e_duplicate":
                row = next(row for row in rows if row["eval_id"] == "E1")
                row["groups"][1]["alternatives"] = row["groups"][0]["alternatives"]
            elif damage == "refusal":
                row = next(row for row in rows if row["eval_id"] == "D1")
                row["points"] = rows[0]["points"]

        mutate_jsonl(folder, filename, damage_row)
    reasons = {
        "hash": "哈希不匹配", "gold": "正例金标为空", "category": "非法品类条件",
        "reason": "理由缺失", "source": "引文无法映射", "duplicate": "台账题面键不一致",
        "e_duplicate": "重复使用同一小节", "refusal": "库外题含正例金标", "utf8": "UnicodeDecodeError",
    }
    with pytest.raises(mod.DatasetError, match=reasons[damage]):
        mod.load_dataset("merchant-rag-300-v1", root=tmp_path)
    assert calls == []


@pytest.mark.parametrize("dataset_id", ["../merchant-rag-300", "merchant-rag-300", "other", "/tmp/data"])
def test_unknown_dataset_never_accepts_a_path(dataset_id):
    """客户端输入只能选择服务端登记版本，不能变成文件路径。"""
    mod = api()
    with pytest.raises(mod.DatasetError):
        mod.load_dataset(dataset_id, root=ROOT)


def test_audited_scope_regressions_are_preserved():
    """人工审核关键纠偏可从实际运行输入追溯，防止旧错误标签复活。"""
    data = api().load_dataset("merchant-rag-300-v1", root=ROOT)
    cases = {case.eval_id: case for case in data.cases}
    for eval_id in ("B54", "B55", "B56", "B57"):
        assert len(cases[eval_id].groups) == 2
    for case in data.cases:
        if case.bucket == "E_multi":
            assert len(case.groups) >= 2
            supports = [{key for bundle in group.alternatives for key in bundle} for group in case.groups]
            assert all(left.isdisjoint(right) for index, left in enumerate(supports) for right in supports[index + 1:])
    assert "累计" in " ".join(point.text for point in cases["A21"].points)
    assert "未知" in " ".join(point.text for point in cases["E22"].points)
    assert "48 小时" not in " ".join(point.text for point in cases["E13"].points)
    regressions = [json.loads(line) for line in (ROOT / "merchant-rag-300" / "regressions.jsonl").read_text(encoding="utf-8").splitlines()]
    assert {row["original_eval_id"] for row in regressions} == {"D3", "D30"}
    assert all(not row["case"]["should_refuse"] and row["case"]["groups"] for row in regressions)
