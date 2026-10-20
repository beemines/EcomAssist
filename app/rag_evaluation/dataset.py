"""白名单评估材料的离线加载、逐项校验和逻辑证据到物理主键映射。"""

from collections import Counter
from dataclasses import asdict
import csv
import hashlib
import io
import json
from pathlib import Path
import re
from typing import Mapping

from app.knowledge.chunking import chunk_markdown
from app.knowledge.types import ChunkDraft, validate_id
from app.rag_evaluation.contracts import AnswerPoint, CorpusChunk, EvalCase, FrozenDataset, GoldGroup, MappedGroup

DATASET_ID = "merchant-rag-300-v1"
_DIRECTORY = "merchant-rag-300"
_DOCUMENTS = {
    "after-sales-manual.md": "manual", "product-faq.md": "faq", "product-specs.md": "manual",
    "returns-policy.md": "policy", "membership-benefits.md": "policy", "integral-rules.md": "policy",
    "invoice-policy.md": "policy", "cat-bed-care.md": "manual",
}
_FILES = frozenset({"original.csv", "reviewed.csv", "cases.jsonl", "audit.jsonl", "regressions.jsonl", "chunks.jsonl"} | {f"corpus/{name}" for name in _DOCUMENTS})
_BUCKETS = {"A": "A_policy", "B": "B_model", "C": "C_colloquial", "D": "D_unanswerable", "E": "E_multi"}
_PILOT = ("A21", "A43", "B3", "B54", "C5", "C35", "D1", "D3", "E2", "E19")
_CSV_FIELDS = ["id", "桶(bucket)", "问题(query)", "期望章节(expect_section)", "标准要点(expect_points)", "应拒答(should_refuse)"]


class DatasetError(ValueError):
    """材料身份、完整性或金标语义校验失败；消息不包含外部请求或密钥。"""


def _require(condition: bool, message: str) -> None:
    """统一离线拒绝条件，避免坏输入以默认值继续进入收费流程。"""
    if not condition:
        raise DatasetError(message)


def _text(value: object) -> bool:
    """只接受非空文本，拒绝隐式数字转换及纯空白标签。"""
    return isinstance(value, str) and bool(value.strip())


def _canonical(value: object) -> bytes:
    """稳定序列化结构，供逻辑块与整套配置的版本标识使用。"""
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"), allow_nan=False).encode("utf-8")


def _hash(value: bytes) -> str:
    """对字节计算完整 SHA-256，不改变换行和编码。"""
    return hashlib.sha256(value).hexdigest()


def ledger_key(eval_id: str, query: str) -> str:
    """原题号加题面哈希前十位，换题不复用旧台账且适合16字符字段。"""
    _require(isinstance(eval_id, str) and re.fullmatch(r"[A-ER](?:[1-9]|[1-5][0-9]|60)", eval_id) is not None, "非法题号")
    _require(_text(query), "空题面")
    return f"{eval_id}-{_hash(query.encode('utf-8'))[:10]}"


def _read_file(folder: Path, name: str) -> bytes:
    """仅读取冻结白名单内且真实路径仍位于数据集目录中的文件。"""
    _require(name in _FILES or name == "manifest.json", "文件不在白名单")
    path = (folder / name).resolve(strict=True)
    _require(path.is_relative_to(folder) and path.is_file(), "冻结文件越出数据集目录")
    return path.read_bytes()


def _json(value: bytes) -> object:
    """严格解码UTF-8并拒绝重复键，防止不同读取器解释同一资产有歧义。"""
    def unique_pairs(pairs):
        """同一JSON对象重复字段直接失败，不采取最后一个值覆盖。"""
        result = {}
        for key, item in pairs:
            _require(key not in result, "JSON重复字段")
            result[key] = item
        return result

    return json.loads(value.decode("utf-8"), object_pairs_hook=unique_pairs)


def _jsonl(value: bytes) -> list[dict]:
    """逐行解析记录并拒绝空行或非对象，保留一题一行的审计约定。"""
    lines = value.splitlines()
    _require(bool(lines) and all(line.strip() for line in lines), "JSONL为空或含空行")
    rows = [_json(line) for line in lines]
    _require(all(isinstance(row, dict) for row in rows), "JSONL记录必须为对象")
    return rows


def _csv(value: bytes) -> list[dict[str, str]]:
    """按标准CSV引号规则读取，并拒绝多列、缺列和错误表头。"""
    reader = csv.DictReader(io.StringIO(value.decode("utf-8"), newline=""), strict=True)
    _require(reader.fieldnames == _CSV_FIELDS, "CSV表头错误")
    rows = list(reader)
    _require(all(set(row) == set(_CSV_FIELDS) and all(isinstance(v, str) for v in row.values()) for row in rows), "CSV字段数量错误")
    return rows


def _chunks(files: dict[str, bytes], manifest: dict) -> tuple[CorpusChunk, ...]:
    """由冻结原文重新切分并逐块比较，入库前验证稳定键与所有草稿字段。"""
    docs = manifest["documents"]
    _require(isinstance(docs, list) and len(docs) == 8, "语料须为八篇白名单文档")
    _require({doc["name"]: doc["content_type"] for doc in docs} == _DOCUMENTS, "语料白名单或类型错误")
    rows = _jsonl(files["chunks.jsonl"])
    expected = []
    for doc in docs:
        name = doc["name"]
        raw = files[f"corpus/{name}"]
        _require(doc["sha256"] == _hash(raw), "原文哈希错误")
        drafts = chunk_markdown(raw.decode("utf-8"), document_name=name, content_type=doc["content_type"], target_chars=1200, overlap_chars=120)
        for ordinal, draft in enumerate(drafts, 1):
            key = f"{name}:{ordinal:03}:{_hash(_canonical(asdict(draft)))}"
            expected.append(dict(chunk_key=key, document=name, ordinal=ordinal, draft=asdict(draft)))
    _require(rows == expected and len(rows) == manifest["chunk_count"] == 50, "切分结果或稳定标识错误")
    return tuple(CorpusChunk(row["chunk_key"], row["document"], row["ordinal"], ChunkDraft(**row["draft"])) for row in rows)


def _references(refs: object, allowed: set[str], chunks: dict[str, CorpusChunk]) -> None:
    """每个来源必须指向审定组内的真实原文；未知只标范围边界，不伪造引文。"""
    _require(isinstance(refs, list) and bool(refs), "答案要点缺来源")
    for ref in refs:
        _require(isinstance(ref, dict) and ref.get("chunk_key") in allowed, "要点来源不在审定证据组")
        chunk = chunks[ref["chunk_key"]]
        _require(ref.get("document") == chunk.document and ref.get("section_path") == chunk.draft.section_path, "来源文档或章节错误")
        _require(_text(ref.get("quote")) and ref["quote"] in chunk.draft.answer, "来源引文无法映射原文")
        _require(ref.get("support_kind") in {"direct", "derived", "bounded_unknown"}, "来源支持类型错误")


def _case(row: dict, chunks: dict[str, CorpusChunk], *, regression: bool = False) -> EvalCase:
    """逐项验证桶、条件、证据组和标准点，返回不可变运行输入。"""
    eval_id = row["eval_id"]
    key = ledger_key(eval_id, row["query"])
    _require(row["ledger_eval_id"] == key, "台账题面键不一致")
    _require(row["bucket"] in _BUCKETS.values(), "未知题桶")
    _require((regression and eval_id in {"R3", "R30"} and row["bucket"] == "A_policy") or (not regression and row["bucket"] == _BUCKETS.get(eval_id[0])), "题号和题桶不匹配")
    _require(row["difficulty"] in {"policy", "model", "colloquial", "absent", "multi", "regression"}, "非法难度标签")
    _require(type(row["should_refuse"]) is bool, "拒答标签必须为布尔值")
    _require(row["should_refuse"] == (row["bucket"] == "D_unanswerable"), "拒答标签与题桶冲突")
    category = row["category"]
    _require(category is None or (_text(category) and category in {chunk.draft.category for chunk in chunks.values()}), "非法品类条件")
    _require(isinstance(row["groups"], list) and isinstance(row["points"], list) and isinstance(row["point_sources"], dict), "金标结构错误")
    if row["should_refuse"]:
        _require(not row["groups"] and not row["points"] and not row["point_sources"], "库外题含正例金标")
    else:
        _require(bool(row["groups"]) and bool(row["points"]), "正例金标为空")
    groups, supports, group_ids = [], [], set()
    for group in row["groups"]:
        group_id = group["group_id"]
        _require(_text(group_id) and group_id not in group_ids, "证据组标识为空或重复")
        group_ids.add(group_id)
        alternatives = group["alternatives"]
        _require(isinstance(alternatives, list) and bool(alternatives), "证据组替代组合为空")
        alternatives_seen, members = set(), set()
        for bundle in alternatives:
            _require(isinstance(bundle, list) and bool(bundle) and all(_text(key) and key in chunks for key in bundle), "证据块无法映射")
            _require(len(bundle) == len(set(bundle)), "证据组合含重复块")
            identity = frozenset(bundle)
            _require(identity not in alternatives_seen, "重复替代组合")
            alternatives_seen.add(identity)
            members.update(bundle)
            _require(category is None or all(chunks[key].draft.category == category for key in bundle), "品类过滤排除了必需证据")
        groups.append(GoldGroup(group_id, tuple(tuple(bundle) for bundle in alternatives)))
        supports.append(members)
    if row["bucket"] == "E_multi":
        _require(len(groups) >= 2, "E题不足两个独立组")
        sections = [{(chunks[key].document, chunks[key].draft.section_path) for key in members} for members in supports]
        _require(all(left.isdisjoint(right) for index, left in enumerate(sections) for right in sections[index + 1:]), "E题重复使用同一小节")
    all_keys = set().union(*supports) if supports else set()
    points, point_ids = [], set()
    for point in row["points"]:
        point_id = point["point_id"]
        _require(_text(point_id) and point_id not in point_ids and _text(point["text"]), "答案要点为空或重复")
        point_ids.add(point_id)
        _require(point["condition"] is None or _text(point["condition"]), "要点适用条件错误")
        _require(isinstance(point["aliases"], list) and all(_text(alias) for alias in point["aliases"]), "同义表达必须为文本数组")
        _references(row["point_sources"].get(point_id), all_keys, chunks)
        points.append(AnswerPoint(point_id, point["text"], point["condition"], tuple(point["aliases"])))
    _require(set(row["point_sources"]) == point_ids, "要点来源不完整或包含多余标识")
    referenced = {ref["chunk_key"] for refs in row["point_sources"].values() for ref in refs}
    _require(all(members & referenced for members in supports), "证据组未支持任何要点")
    return EvalCase(eval_id, row["bucket"], row["difficulty"], row["query"], category, row["should_refuse"], tuple(groups), tuple(points), key)


def _audit(files: dict[str, bytes], rows: list[dict], chunks: dict[str, CorpusChunk]) -> None:
    """将原CSV、修订CSV、运行金标及逐题理由相互对照，禁止静默替换题目。"""
    original, reviewed, audit = _csv(files["original.csv"]), _csv(files["reviewed.csv"]), _jsonl(files["audit.jsonl"])
    _require(len(original) == len(reviewed) == len(audit) == len(rows) == 300, "逐题材料数量不完整")
    for before, after, note, row in zip(original, reviewed, audit, rows, strict=True):
        _require(before["id"] == after["id"] == note["eval_id"] == row["eval_id"], "逐题材料顺序或题号不一致")
        _require(note["before"] == before and note["after"] == after, "审计未保留准确前后记录")
        _require(_text(note["reason"]), "逐题修改或保持理由缺失")
        _require(after["问题(query)"] == row["query"] and after["应拒答(should_refuse)"] == ("是" if row["should_refuse"] else "否"), "修订题面或拒答标签不一致")
        _require(after["桶(bucket)"] == ("D_absent" if row["bucket"] == "D_unanswerable" else row["bucket"]), "修订题桶不一致")
        _require(after["标准要点(expect_points)"] == " | ".join(point["text"] for point in row["points"]), "修订答案要点不一致")
        sections = " + ".join(" | ".join(" & ".join(chunks[key].draft.section_path for key in bundle) for bundle in group["alternatives"]) for group in row["groups"])
        _require(after["期望章节(expect_section)"] == sections, "修订章节不一致")
        _require(note["point_sources"] == row["point_sources"], "审计要点来源不一致")
        _require(len(note["checked_documents"]) == 8 and set(note["checked_documents"]) == set(_DOCUMENTS), "未记录八篇资料审阅范围")
        refs = {ref["chunk_key"]: ref for values in row["point_sources"].values() for ref in values}
        _require(note["source_refs"] == list(refs.values()), "审计来源摘要不一致")


def load_dataset(dataset_id: str, *, root: Path) -> FrozenDataset:
    """从固定版本白名单加载并完整离线验证；root为服务端evals/datasets目录。"""
    _require(dataset_id == DATASET_ID, "未知数据集版本")
    try:
        base = Path(root).resolve(strict=True)
        folder = (base / _DIRECTORY).resolve(strict=True)
        _require(folder.is_relative_to(base), "数据集目录越界")
        manifest = _json(_read_file(folder, "manifest.json"))
        _require(isinstance(manifest, dict) and manifest["schema_version"] == 1 and manifest["dataset_id"] == dataset_id, "冻结清单版本错误")
        _require(manifest["chunking"] == {"target_chars": 1200, "overlap_chars": 120}, "切分参数不是批准值")
        _require(set(manifest["files"]) == _FILES, "清单文件白名单不完整")
        files = {name: _read_file(folder, name) for name in _FILES}
        for name, raw in files.items():
            _require(_hash(raw) == manifest["files"][name], f"冻结文件哈希不匹配: {name}")
            raw.decode("utf-8")
        chunks = _chunks(files, manifest)
        chunk_map = {chunk.chunk_key: chunk for chunk in chunks}
        rows = _jsonl(files["cases.jsonl"])
        cases = tuple(_case(row, chunk_map) for row in rows)
        expected_ids = {f"{prefix}{number}" for prefix in _BUCKETS for number in range(1, 61)}
        _require(len(cases) == 300 and {case.eval_id for case in cases} == expected_ids, "题数、题号或唯一性错误")
        _require(Counter(case.bucket for case in cases) == {bucket: 60 for bucket in _BUCKETS.values()}, "五桶须各60题")
        _require(len({case.ledger_eval_id for case in cases}) == 300, "台账键碰撞")
        _require(tuple(manifest["pilot_ids"]) == _PILOT, "试运行抽样被改动")
        _audit(files, rows, chunk_map)
        regressions = _jsonl(files["regressions.jsonl"])
        _require(len(regressions) == 2 and {row["original_eval_id"] for row in regressions} == {"D3", "D30"}, "原库外误标题缺少可答回归")
        originals = {row["id"]: row for row in _csv(files["original.csv"])}
        regression_links = []
        for row in regressions:
            case = _case(row["case"], chunk_map, regression=True)
            _require(case.eval_id == "R" + row["original_eval_id"][1:] and _text(row["reason"]), "回归题标识或理由错误")
            _require(case.query == originals[row["original_eval_id"]]["问题(query)"] and not case.should_refuse, "回归未保留原可答题面")
            regression_links.append((case.eval_id, row['original_eval_id']))
        corpus_hash = _hash(_canonical({"documents": manifest["documents"], "chunking": manifest["chunking"], "chunks_sha256": manifest["files"]["chunks.jsonl"]}))
        return FrozenDataset(dataset_id, _hash(_canonical(manifest)), corpus_hash, _hash(files["cases.jsonl"]), _hash(files["audit.jsonl"]), chunks, cases, _PILOT, tuple(regression_links))
    except DatasetError:
        raise
    except (OSError, ValueError, TypeError, KeyError, AttributeError, csv.Error) as exc:
        raise DatasetError(f"冻结数据结构无法验证（{type(exc).__name__}）") from exc


def map_groups(case: EvalCase, id_map: Mapping[str, int]) -> tuple[MappedGroup, ...]:
    """只映射已审定逻辑块；缺块、重复物理ID或非法主键直接失败。"""
    keys = {key for group in case.groups for bundle in group.alternatives for key in bundle}
    try:
        ids = {key: id_map[key] for key in keys}
        for value in ids.values():
            validate_id(value)
        _require(len(set(ids.values())) == len(ids), "不同逻辑块映射到同一物理主键")
    except (KeyError, TypeError, ValueError) as exc:
        raise DatasetError("证据物理主键映射缺失或非法") from exc
    return tuple(MappedGroup(group.group_id, tuple(tuple(ids[key] for key in bundle) for bundle in group.alternatives)) for group in case.groups)
