# 质量台账输入按原 DDL 容量校验，保留这一轮完整证据快照。
from dataclasses import dataclass
import json
from typing import Literal

from app.knowledge.types import validate_text


CaseStatus = Literal["未解决", "已解决", "无需解决"]
CASE_STATUSES = ("未解决", "已解决", "无需解决")
RefusalSource = Literal["retrieval_low_conf", "self_check"]


# 校验题号与必填文本，在写入前拒绝空白及字段长度越界。
def require_text(name: str, value: str, limit: int, *, utf8: bool = False) -> None:
    validate_text(name, value, limit, utf8=utf8)
    if not value.strip():
        raise ValueError(f"{name} must be nonempty")


# 统一检查状态和处置说明；退回未解决时显式清空说明。
def resolution_value(status: str, resolution: str | None) -> str | None:
    if status not in CASE_STATUSES:
        raise ValueError("invalid case status")
    if status == "未解决":
        return None
    require_text("resolution", resolution, 300)
    return resolution


@dataclass(frozen=True)
class FaithCaseInput:
    """一条裁判判定的编造，citations 保存本轮证据全集而非仅被引用项。"""

    eval_id: str
    bucket: str
    query: str
    strategy: str
    answer: str
    reason: str
    citations: list[dict]
    judge_model: str | None

    # 根据原表字段容量及 JSON 规则验证台账输入，避免部分写入。
    def __post_init__(self) -> None:
        for name, limit in (("eval_id", 16), ("bucket", 24), ("query", 512), ("strategy", 24)):
            require_text(name, getattr(self, name), limit)
        require_text("answer", self.answer, 65535, utf8=True)
        require_text("reason", self.reason, 65535, utf8=True)
        validate_text("judge_model", self.judge_model, 64, nullable=True)
        if not isinstance(self.citations, list) or any(not isinstance(item, dict) for item in self.citations):
            raise ValueError("citations must be a list of evidence objects")
        try:
            json.dumps(self.citations, ensure_ascii=False, allow_nan=False)
        except (TypeError, ValueError) as exc:
            raise ValueError("citations must be finite JSON") from exc
