"""运行期依赖接口，与检查点状态分离。"""
from collections.abc import Mapping
from dataclasses import dataclass
from typing import Any

from langchain_core.tools import BaseTool

from app.config import Settings
from app.orders.types import OrderProvider


@dataclass
class WorkflowRuntime:
    """父图拥有模型与仓储；决策模型用于2048控制，model用于512最终流，upstream由收敛节点回收。"""
    model: Any
    decision_model: Any
    intent_model: Any
    repository: Any
    faq_repository: Any
    sufficiency: Any
    quality_repository: Any
    registry: Mapping[str, BaseTool]
    executor: Any
    settings: Settings
    deadline: float
    upstream: Any = None
    order_provider: OrderProvider | None = None
    workflow_retriever: Any = None
    understanding: Any = None
    expander: Any = None
    user_id: str | None = None
    # 单调钟仅留Runtime；State只保存累计活动秒数，不计用户等候。
    active_started_at: float | None = None
    active_elapsed_baseline: float = 0.0
    # 同步接收已观测计数，外层流取消也不依赖异步事件排空；每轮独立安装。
    usage_observer: Any = None
