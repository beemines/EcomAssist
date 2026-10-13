"""运行期依赖接口，与检查点状态分离。"""
from collections.abc import Mapping
from dataclasses import dataclass
from typing import Any

from langchain_core.tools import BaseTool

from app.config import Settings


@dataclass
class WorkflowRuntime:
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
