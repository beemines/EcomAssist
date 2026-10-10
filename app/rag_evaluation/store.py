"""本地运行快照 v2：显式白名单、原子发布与计划驱动的检查点恢复。

配置与计划只在 create 冻结；update 仅接受 MUTABLE_FIELDS，计数由 records
推导。get/records 是本地私有接口，HTTP/export 必须另用 public_run_metadata
与 report.public_report。文件名固定，不接受调用方指定任意路径或序列化器。
"""

import asyncio
from collections import Counter
from collections.abc import Mapping, Sequence
import copy
from datetime import datetime, timezone
import json
import math
import os
from pathlib import Path
import re
import tempfile
from urllib.parse import urlsplit
from uuid import uuid4
from weakref import WeakValueDictionary

from app.rag_evaluation.contracts import Strategy
from app.rag_evaluation.report import CASE_FIELDS, STATUSES, STRATEGIES, safe_error, validate_case_record

CONFIG_FIELDS = ("dataset_id", "scope", "fingerprint", "mode", "models", "budgets", "prompt_versions", "upstream_summary")
MODEL_FIELDS = ("answer", "rewrite", "self_check", "judge", "embedding", "rerank")
PROMPT_FIELDS = ("rewrite", "self_check", "answer", "judge")
UPSTREAM_FIELDS = ("llm", "embedding", "rerank")
FIXED_BUDGETS = dict(candidate_k=50, final_k=10, chunk_target_chars=1200, chunk_overlap_chars=120,
    answer_output_tokens=512, rewrite_output_tokens=2048, self_check_output_tokens=2048,
    judge_input_tokens=16000, judge_output_tokens=2048, model_retries=0)
TIMEOUT_FIELDS = ("rewrite_timeout_s", "self_check_timeout_s", "faq_timeout_s", "chat_timeout_s",
                  "judge_timeout_s", "embedding_timeout_s", "rerank_timeout_s", "milvus_timeout_s")
BUDGET_FIELDS = tuple(FIXED_BUDGETS) + ("case_concurrency", "tool_input_tokens") + TIMEOUT_FIELDS
REQUEST_FIELDS = ("rewrite", "self_check", "answer", "judge", "embedding", "rerank", "milvus")
OUTCOMES = ("completed", "completed_with_errors", "failed", "cancelled", "interrupted")
STATES = ("queued", "preparing", "running", "cancelling") + OUTCOMES
RUN_STAGES = ("prepare", "rewrite", "retrieval", "self_check", "answer", "judgment", "cleanup", "complete")
MUTABLE_FIELDS = ("state", "outcome", "stage", "request_counts", "ownership", "cleanup", "started_at", "finished_at", "error")
MANIFEST_FIELDS = ("schema_version", "run_id", "config", "case_keys", "state", "outcome", "stage",
    "planned_cases", "planned_strategies", "planned_records", "counts", "request_counts", "ownership",
    "cleanup", "created_at", "updated_at", "started_at", "finished_at", "error")
PUBLIC_FIELDS = tuple(field for field in MANIFEST_FIELDS if field not in ("ownership", "case_keys"))
COUNT_FIELDS = tuple(dict.fromkeys(("total", "attempted", "completed", "errors", "not_attempted") + STATUSES))
MAX_JSON_BYTES = 2 * 1024 * 1024
_ROOT_STATES = WeakValueDictionary()


class _RootState:
    """同根同循环实例共同持有发布锁及最新运行缓存，防止实例间旧状态覆盖。"""

    def __init__(self):
        """缓存生命周期由存活的 RunStore 强引用限定，不创建后台任务。"""
        self.lock = asyncio.Lock()
        self.runs = {}


class _RunState:
    """已经完整验证的运行快照与按计划键索引的逐题产物。"""

    def __init__(self, manifest: dict, rows: list[dict], signature: tuple):
        """一次恢复建立索引；正常检查点只更新单题及其计数差量。"""
        self.manifest = manifest
        self.rows = {(row["eval_id"], row["strategy"]): row for row in rows}
        self.identities = {row["eval_id"]: _identity(row) for row in rows}
        self.plan = {tuple(key) for key in manifest["case_keys"]}
        self.signature = signature


class StoreError(ValueError):
    """路径、快照结构或本地文件发布失败，消息不夹带私有字段。"""


def _require(condition: bool, message: str) -> None:
    """字段级守卫只给出固定原因，不打印调用方数据。"""
    if not condition:
        raise StoreError(message)


def _object(value: object, fields: Sequence[str]) -> dict:
    """要求完整且无扩展字段的对象，不对任意对象调用 JSON 转换。"""
    _require(isinstance(value, Mapping) and set(value) == set(fields), "对象字段不符合白名单")
    return dict(value)


def _text(value: object, limit: int, *, blank: bool = False) -> bool:
    """严格限定字符串长度和空白策略，拒绝隐式转换。"""
    return type(value) is str and len(value) <= limit and (blank or bool(value.strip()))


def _identifier(value: object, limit: int = 128) -> bool:
    """题号及版本标识仅允许文件名安全字符，不能形成路径或连接串。"""
    return _text(value, limit) and re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9_.-]*", value) is not None


def _hash(value: object) -> bool:
    """摘要必须是小写 SHA-256，不接受任意私有内容代替。"""
    return type(value) is str and re.fullmatch(r"[0-9a-f]{64}", value) is not None


def _integer(value: object, minimum: int, maximum: int) -> bool:
    """整数不接受 bool，所有计数和 ID 都有明确边界。"""
    return type(value) is int and minimum <= value <= maximum


def canonical_root(root: Path) -> Path:
    """根路径规范化前拒绝符号链接或 Windows junction，避免外部落点。"""
    _require(isinstance(root, Path), "root 须为 Path")
    try:
        raw = root.absolute()
        for part in (raw, *raw.parents):
            _require(not part.is_symlink() and not part.is_junction(), "根路径含链接落点")
        return raw.resolve()
    except OSError as exc:
        raise StoreError("根路径无法规范化") from exc


def guarded_path(root: Path, *parts: str) -> Path:
    """逐级检查固定相对落点，拒绝链接与规范化后的根目录逃逸。"""
    try:
        current = root
        _require(not root.is_symlink() and not root.is_junction(), "根目录成为链接")
        for part in parts:
            _require(type(part) is str and part not in ("", ".", "..") and
                     not Path(part).is_absolute() and "/" not in part and "\\" not in part, "非法文件落点")
            current = current / part
            _require(not current.is_symlink() and not current.is_junction(), "文件落点含链接")
        _require(current.resolve().is_relative_to(root), "文件落点越过根目录")
        return current
    except OSError as exc:
        raise StoreError("文件落点无法检查") from exc


def validate_config(config: Mapping[str, object]) -> dict[str, object]:
    """冻结模型、预算和安全 origin 摘要，禁止密钥与完整连接地址。"""
    value = _object(config, CONFIG_FIELDS)
    _require(value["dataset_id"] == "merchant-rag-300-v1" and value["scope"] in ("pilot", "full") and
             value["mode"] == "content_ablation" and _hash(value["fingerprint"]), "数据集配置非法")
    models = _object(value["models"], MODEL_FIELDS)
    _require(all(_text(name, 128) and re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9_./-]*", name)
                 for name in models.values()), "模型名非法")
    prompts = _object(value["prompt_versions"], PROMPT_FIELDS)
    _require(all(_identifier(version) for version in prompts.values()), "Prompt 版本非法")
    budgets = _object(value["budgets"], BUDGET_FIELDS)
    _require(all(type(budgets[key]) is int and budgets[key] == amount for key, amount in FIXED_BUDGETS.items()), "冻结预算不一致")
    _require(_integer(budgets["case_concurrency"], 1, 2) and _integer(budgets["tool_input_tokens"], 1, 1000000), "并发或输入预算非法")
    for key in TIMEOUT_FIELDS:
        number = budgets[key]
        _require(type(number) in (int, float) and math.isfinite(number) and 0 < number <= 3600, "超时预算非法")
    upstream = _object(value["upstream_summary"], UPSTREAM_FIELDS)
    for address in upstream.values():
        _require(_text(address, 256) and not any(char.isspace() for char in address), "上游摘要非法")
        try:
            parsed = urlsplit(address)
            _require(parsed.scheme in ("http", "https") and bool(parsed.hostname) and parsed.username is None and
                     parsed.password is None and parsed.path in ("", "/") and not parsed.query and not parsed.fragment
                     and "?" not in address and "#" not in address, "上游只接受安全 origin")
            _require(parsed.port is None or _integer(parsed.port, 1, 65535), "上游端口非法")
        except ValueError as exc:
            raise StoreError("上游 origin 非法") from exc
    return copy.deepcopy(value)


def _plan(case_keys: object) -> list[list[str]]:
    """最多1200条唯一计划键，题号不含用于文件名分隔的双连字符。"""
    _require(isinstance(case_keys, Sequence) and not isinstance(case_keys, (str, bytes)) and 0 < len(case_keys) <= 1200,
             "计划记录数非法")
    result, seen, filenames = [], set(), set()
    for key in case_keys:
        _require(isinstance(key, (list, tuple)) and len(key) == 2 and _identifier(key[0], 64) and
                 "--" not in key[0] and key[1] in STRATEGIES, "计划题号或策略非法")
        _require(tuple(key) not in seen, "计划题号策略重复")
        filename = os.path.normcase(f"{key[0]}--{key[1]}.json")
        _require(filename not in filenames, "计划检查点文件名冲突")
        seen.add(tuple(key))
        filenames.add(filename)
        result.append(list(key))
    return result


def _error(value: object) -> dict | None:
    """公共错误仅保留安全标识与固定文本，拒绝扩展请求信息。"""
    if value is None:
        return None
    error = _object(value, ("code", "type", "message"))
    _require(_text(error["message"], 2048, blank=True), "错误文本越界")
    try:
        return safe_error(error)
    except ValueError as exc:
        raise StoreError("错误标识非法") from exc


def _cleanup(value: object) -> dict | None:
    """清理结果保留有界本地审计，未知归属不能标成成功。"""
    if value is None:
        return None
    result = _object(value, ("ok", "errors", "unverified"))
    _require(type(result["ok"]) is bool, "清理成功标记非法")
    for key in ("errors", "unverified"):
        _require(isinstance(result[key], list) and len(result[key]) <= 1200 and
                 all(_text(item, 256) for item in result[key]), "清理审计越界")
    _require(not result["ok"] or not result["errors"] and not result["unverified"], "清理成功仍有未核验资源")
    return copy.deepcopy(result)


def _ownership(value: object, run_id: str) -> dict | None:
    """归属必须绑定隔离库和本次精确集合，预提交 ID 与摘要不可分离。"""
    if value is None:
        return None
    result = _object(value, ("database", "collection", "owned_ids", "content_hashes", "pending_ids"))
    database = _object(result["database"], ("host", "port", "name"))
    _require(database["host"] in ("127.0.0.1", "localhost", "::1") and type(database["port"]) is int and
             database["port"] == 3308 and database["name"] == "customer_service_test", "数据库归属身份非法")
    database["host"] = "127.0.0.1"
    result["database"] = database
    _require(result["collection"] == "knowledge_test_" + run_id, "集合归属不属于本次运行")
    for field in ("owned_ids", "pending_ids"):
        ids = result[field]
        _require(isinstance(ids, list) and len(ids) <= 10000 and all(_integer(i, 1, 2**63 - 1) for i in ids)
                 and len(set(ids)) == len(ids), "归属主键非法或重复")
    _require(set(result["pending_ids"]) <= set(result["owned_ids"]), "待提交主键未登记归属")
    hashes = result["content_hashes"]
    _require(isinstance(hashes, Mapping) and set(hashes) == {str(i) for i in result["owned_ids"]} and
             all(_hash(digest) for digest in hashes.values()), "内容摘要必须覆盖全部登记主键")
    return copy.deepcopy(result)


def _time(value: object, *, nullable: bool = False) -> bool:
    """时间必须是有时区的 ISO 文本，空阶段时间可明确为 null。"""
    if value is None:
        return nullable
    if not _text(value, 40):
        return False
    try:
        return datetime.fromisoformat(value).utcoffset() is not None
    except ValueError:
        return False


def _now() -> str:
    """快照写入统一使用 UTC ISO 时间，便于历史稳定排序。"""
    return datetime.now(timezone.utc).isoformat()


def _history_key(manifest: dict) -> tuple[str, str]:
    """历史按 UTC 创建时间及唯一标识稳定排序，不依赖目录枚举顺序。"""
    return manifest["created_at"], manifest["run_id"]


def validate_manifest(manifest: Mapping[str, object]) -> dict[str, object]:
    """完整验证磁盘 manifest，冻结计划计数与私有资源身份。"""
    result = _object(manifest, MANIFEST_FIELDS)
    _require(type(result["schema_version"]) is int and result["schema_version"] == 2 and
             type(result["run_id"]) is str and re.fullmatch(r"[0-9a-f]{32}", result["run_id"]), "运行版本或标识非法")
    result["config"] = validate_config(result["config"])
    result["case_keys"] = _plan(result["case_keys"])
    plan = result["case_keys"]
    expected = (len({key[0] for key in plan}), len({key[1] for key in plan}), len(plan))
    for field, count in zip(("planned_cases", "planned_strategies", "planned_records"), expected):
        _require(type(result[field]) is int and result[field] == count, "计划计数不一致")
    _require(result["state"] in STATES and result["outcome"] in (None, *OUTCOMES) and result["stage"] in RUN_STAGES,
             "运行状态非法")
    counts = _object(result["counts"], COUNT_FIELDS)
    _require(all(_integer(count, 0, 1200) for count in counts.values()) and counts["total"] == len(plan) and
             sum(counts[status] for status in STATUSES) == len(plan) and
             counts["attempted"] == len(plan) - counts["not_attempted"] and
             counts["errors"] == sum(counts[status] for status in STATUSES if status.endswith("_error")), "逐题计数非法")
    requests = _object(result["request_counts"], REQUEST_FIELDS)
    _require(all(_integer(count, 0, 1000000) for count in requests.values()), "实际请求计数非法")
    result["ownership"] = _ownership(result["ownership"], result["run_id"])
    result["cleanup"] = _cleanup(result["cleanup"])
    result["error"] = _error(result["error"])
    _require(all(_time(result[field]) for field in ("created_at", "updated_at")) and
             all(_time(result[field], nullable=True) for field in ("started_at", "finished_at")), "快照时间非法")
    return copy.deepcopy(result)


def public_run_metadata(manifest: Mapping[str, object]) -> dict[str, object]:
    """独立公共白名单排除归属与计划，清理失败文本换成安全固定消息。"""
    checked = validate_manifest(manifest)
    result = {field: checked[field] for field in PUBLIC_FIELDS}
    if result["cleanup"] is not None:
        result["cleanup"]["errors"] = ["资源清理失败" for _ in result["cleanup"]["errors"]]
        result["cleanup"]["unverified"] = ["资源归属未核验" for _ in result["cleanup"]["unverified"]]
    return result


def _case(record: Mapping[str, object]) -> dict[str, object]:
    """存储边界拒绝嵌套扩展字段，再复用报告的完整阶段与金标契约。"""
    value = _object(record, CASE_FIELDS)
    _require(_identifier(value["eval_id"], 64) and "--" not in value["eval_id"], "题号不适合作为检查点文件名")
    nested = {"query_plan": ("standard", "expansions"), "decision": ("useful", "reason", "response_kind", "source"),
              "error": ("code", "type", "message")}
    for field, fields in nested.items():
        if value[field] is not None:
            _object(value[field], fields)
    lists = {"mapped_groups": ("group_id", "alternatives"),
        "prompt_citations": ("n", "chunk_id", "section_path", "question", "answer"),
        "point_verdicts": ("point_id", "covered", "reason"), "claim_verdicts": ("claim", "supported", "reason")}
    for field, fields in lists.items():
        if value[field] is not None:
            _require(isinstance(value[field], list) and len(value[field]) <= 1200, "逐题列表越界")
            for item in value[field]:
                _object(item, fields)
    snapshot = value["judge_snapshot"]
    if snapshot is not None:
        _require(isinstance(snapshot, Mapping), "裁判快照非法")
        _object(snapshot, ("prompt_version", "finish_reason", "raw_response") if "raw_response" in snapshot else
                ("prompt_version", "finish_reason"))
        _require(_text(snapshot["prompt_version"], 128) and _text(snapshot["finish_reason"], 64) and
                 ("raw_response" not in snapshot or _text(snapshot["raw_response"], 16384, blank=True)), "裁判快照越界")
    try:
        return validate_case_record(value)
    except (ValueError, TypeError, KeyError) as exc:
        raise StoreError("逐题阶段契约非法") from exc


def _identity(row: dict) -> list:
    """同题所有策略共享完整题面和物理金标，缓存不降低冻结元数据校验。"""
    return [row[field] for field in ("bucket", "difficulty", "category", "should_refuse", "query", "mapped_groups")]


class RunStore:
    """单事件循环内同根实例共用异步发布锁，跨进程运行由 RunLock 排他。"""

    def __init__(self, root: Path):
        """只规范化根目录；无效 create 不提前产生运行文件。"""
        self.root = canonical_root(root)
        self._states = {}
        self._loaded = set()

    def _state(self) -> _RootState:
        """各实例强持有同根同循环共享状态，弱注册表不积累已释放的根缓存。"""
        loop = asyncio.get_running_loop()
        if loop not in self._states:
            key = (os.path.normcase(str(self.root)), loop)
            shared = _ROOT_STATES.get(key)
            if shared is None:
                shared = _RootState()
                _ROOT_STATES[key] = shared
            self._states[loop] = shared
        return self._states[loop]

    def _writer(self) -> asyncio.Lock:
        """同规范根与事件循环共享锁，避免实例间检查点计数覆盖。"""
        return self._state().lock

    def _path(self, run_id: str, *parts: str) -> Path:
        """运行 ID 必须是 UUID32hex，其后只接收内部固定文件名。"""
        _require(type(run_id) is str and re.fullmatch(r"[0-9a-f]{32}", run_id), "运行标识非法")
        return guarded_path(self.root, run_id, *parts)

    def _write(self, path: Path, value: Mapping[str, object]) -> None:
        """同目录独占临时文件写完 fsync 再 replace，异常保留已有快照。"""
        temporary = None
        try:
            encoded = json.dumps(value, ensure_ascii=False, allow_nan=False, separators=(",", ":")).encode("utf-8")
            _require(len(encoded) <= MAX_JSON_BYTES, "JSON 快照越界")
            relative = path.relative_to(self.root)
            guarded_path(self.root, *relative.parts)
            descriptor, name = tempfile.mkstemp(prefix=".snapshot-", suffix=".tmp", dir=path.parent)
            temporary = Path(name)
            with os.fdopen(descriptor, "wb") as stream:
                stream.write(encoded)
                stream.flush()
                os.fsync(stream.fileno())
            guarded_path(self.root, *relative.parts)
            os.replace(temporary, path)
        except (OSError, ValueError, TypeError) as exc:
            self._state().runs.pop(path.relative_to(self.root).parts[0], None)
            raise StoreError("快照原子发布失败") from exc
        finally:
            if temporary is not None and temporary.exists():
                temporary.unlink()

    def _read(self, path: Path) -> dict:
        """只读取根内有界 JSON 对象，损坏快照作为可见存储错误。"""
        try:
            guarded_path(self.root, *path.relative_to(self.root).parts)
            with path.open("rb") as stream:
                content = stream.read(MAX_JSON_BYTES + 1)
            _require(len(content) <= MAX_JSON_BYTES, "JSON 快照越界")
            value = json.loads(content)
            _require(type(value) is dict, "JSON 快照须为对象")
            return value
        except (OSError, ValueError, UnicodeError) as exc:
            raise StoreError("快照读取失败") from exc

    def _records(self, manifest: dict) -> list[dict]:
        """计划键唯一决定文件集合；磁盘上的非计划文件和身份不符均拒绝。"""
        run_id = manifest["run_id"]
        folder = self._path(run_id, "records")
        expected = {f"{eval_id}--{strategy}.json": (eval_id, strategy) for eval_id, strategy in manifest["case_keys"]}
        try:
            for path in folder.iterdir():
                guarded_path(self.root, run_id, "records", path.name)
                if path.name.startswith(".snapshot-") and path.suffix == ".tmp":
                    continue
                _require(path.name in expected and path.is_file(), "存在非计划检查点")
            rows, identities = [], {}
            for name, key in expected.items():
                path = self._path(run_id, "records", name)
                if path.exists():
                    row = _case(self._read(path))
                    _require((row["eval_id"], row["strategy"]) == key, "检查点身份不匹配")
                    identity = _identity(row)
                    _require(row["eval_id"] not in identities or identities[row["eval_id"]] == identity,
                             "四路检查点题面与金标不一致")
                    identities[row["eval_id"]] = identity
                    rows.append(row)
            return rows
        except OSError as exc:
            raise StoreError("检查点目录读取失败") from exc

    def _counts(self, manifest: dict, rows: list[dict]) -> dict:
        """缺少的计划文件算未执行，不能用虚构 CaseRecord 补齐。"""
        counts = Counter(row["status"] for row in rows)
        counts["not_attempted"] += manifest["planned_records"] - len(rows)
        result = {status: counts[status] for status in STATUSES}
        result.update(total=manifest["planned_records"], attempted=manifest["planned_records"] - counts["not_attempted"],
                      errors=sum(counts[status] for status in STATUSES if status.endswith("_error")))
        return result

    def _signature(self, run_id: str) -> tuple:
        """每次访问仍守卫关键落点，仅比较manifest与记录目录的常数次stat。"""
        try:
            manifest = self._path(run_id, "manifest.json").stat()
            records = self._path(run_id, "records").stat()
            return (manifest.st_dev, manifest.st_ino, manifest.st_size, manifest.st_mtime_ns,
                    records.st_dev, records.st_ino, records.st_mtime_ns)
        except OSError as exc:
            raise StoreError("运行快照签名读取失败") from exc

    def _remember(self, run_id: str, manifest: dict, rows: list[dict]) -> _RunState:
        """完整恢复后共享索引；当前实例标记首次验证已完成。"""
        cached = _RunState(manifest, rows, self._signature(run_id))
        self._state().runs[run_id] = cached
        self._loaded.add((asyncio.get_running_loop(), run_id))
        return cached

    def _load(self, run_id: str) -> _RunState:
        """首次访问或签名变化完整恢复，稳定态复用共享已验证索引。"""
        shared = self._state()
        try:
            signature = self._signature(run_id)
            cached = shared.runs.get(run_id)
            if ((asyncio.get_running_loop(), run_id) in self._loaded and cached is not None and
                    signature == cached.signature):
                return cached
            shared.runs.pop(run_id, None)
            manifest = validate_manifest(self._read(self._path(run_id, "manifest.json")))
            _require(manifest["run_id"] == run_id, "manifest 运行身份不匹配")
            rows = self._records(manifest)
            counts = self._counts(manifest, rows)
            if manifest["counts"] != counts:
                manifest["counts"] = counts
                manifest["updated_at"] = _now()
                self._write(self._path(run_id, "manifest.json"), manifest)
            return self._remember(run_id, manifest, rows)
        except StoreError:
            shared.runs.pop(run_id, None)
            raise

    async def create(self, config: dict[str, object], case_keys: Sequence[tuple[str, Strategy]]) -> str:
        """冻结配置与计划；准备完成前不创建任何金标题目记录。"""
        frozen, plan = validate_config(config), _plan(case_keys)
        async with self._writer():
            run_id, now = uuid4().hex, _now()
            manifest = dict(schema_version=2, run_id=run_id, config=frozen, case_keys=plan, state="queued",
                outcome=None, stage="prepare", planned_cases=len({key[0] for key in plan}),
                planned_strategies=len({key[1] for key in plan}), planned_records=len(plan),
                counts={}, request_counts=dict.fromkeys(REQUEST_FIELDS, 0), ownership=None, cleanup=None,
                created_at=now, updated_at=now, started_at=None, finished_at=None, error=None)
            manifest["counts"] = self._counts(manifest, [])
            validate_manifest(manifest)
            try:
                self._path(run_id, "records").mkdir(parents=True, exist_ok=False)
            except OSError as exc:
                raise StoreError("运行目录创建失败") from exc
            self._write(self._path(run_id, "manifest.json"), manifest)
            self._remember(run_id, manifest, [])
            return run_id

    async def update(self, run_id: str, patch: Mapping[str, object]) -> None:
        """仅更新明确可变字段；归属累积登记不可撤销，实际请求数不可倒退。"""
        _require(isinstance(patch, Mapping) and set(patch) <= set(MUTABLE_FIELDS), "运行更新含未知或冻结字段")
        async with self._writer():
            cached = self._load(run_id)
            before = cached.manifest
            manifest = dict(before, **copy.deepcopy(dict(patch)))
            manifest["updated_at"] = _now()
            checked = validate_manifest(manifest)
            _require(all(checked["request_counts"][key] >= before["request_counts"][key] for key in REQUEST_FIELDS), "请求计数不得倒退")
            old, new = before["ownership"], checked["ownership"]
            if old is not None:
                _require(new is not None and set(old["owned_ids"]) <= set(new["owned_ids"]) and
                         all(new["content_hashes"].get(key) == digest for key, digest in old["content_hashes"].items()),
                         "已登记归属与摘要不可撤销")
            self._write(self._path(run_id, "manifest.json"), checked)
            cached.signature = self._signature(run_id)
            cached.manifest = checked

    async def put_case(self, run_id: str, record: Mapping[str, object]) -> None:
        """逐题原子发布，再发布派生计数；取消只能发生在进入发布锁之前。"""
        row = _case(record)
        async with self._writer():
            cached = self._load(run_id)
            manifest = copy.deepcopy(cached.manifest)
            key = (row["eval_id"], row["strategy"])
            _require(key in cached.plan, "题目策略不在冻结计划内")
            identity = _identity(row)
            _require(row["eval_id"] not in cached.identities or cached.identities[row["eval_id"]] == identity,
                     "题面与金标不得改变")
            self._write(self._path(run_id, "records", f"{row['eval_id']}--{row['strategy']}.json"), row)
            previous = cached.rows.get(key)
            counts = manifest["counts"]
            counts[previous["status"] if previous is not None else "not_attempted"] -= 1
            counts[row["status"]] += 1
            counts["attempted"] = counts["total"] - counts["not_attempted"]
            counts["errors"] = sum(counts[status] for status in STATUSES if status.endswith("_error"))
            manifest["updated_at"] = _now()
            self._write(self._path(run_id, "manifest.json"), manifest)
            cached.signature = self._signature(run_id)
            cached.manifest = manifest
            cached.rows[key] = row
            cached.identities[row["eval_id"]] = identity

    async def get(self, run_id: str) -> dict[str, object]:
        """返回独立本地 manifest 快照，自动修复逐题计数而不续跑模型。"""
        async with self._writer():
            return copy.deepcopy(self._load(run_id).manifest)

    async def records(self, run_id: str) -> list[dict[str, object]]:
        """按冻结计划顺序返回已有本地完整记录，包括私有裁判原文。"""
        async with self._writer():
            cached = self._load(run_id)
            return copy.deepcopy([cached.rows[tuple(key)] for key in cached.manifest["case_keys"]
                                  if tuple(key) in cached.rows])

    async def list_runs(self, offset: int = 0, limit: int = 20) -> list[dict[str, object]]:
        """按创建时间倒序分页本地历史，隐藏半创建目录但拒绝损坏 manifest。"""
        _require(_integer(offset, 0, 1000000) and _integer(limit, 1, 100), "分页参数非法")
        async with self._writer():
            if not self.root.exists():
                return []
            guarded_path(self.root)
            result = []
            for path in self.root.iterdir():
                if re.fullmatch(r"[0-9a-f]{32}", path.name):
                    manifest_path = self._path(path.name, "manifest.json")
                    if manifest_path.exists():
                        result.append(copy.deepcopy(self._load(path.name).manifest))
            result.sort(key=_history_key, reverse=True)
            return result[offset:offset + limit]
