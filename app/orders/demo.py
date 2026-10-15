# 演示事实从本地 JSON 一次载入，不访问网络或写入业务数据库。
from pathlib import Path

from pydantic import BaseModel, ConfigDict

from app.orders.types import OrderSnapshot


class _DemoFixture(BaseModel):
    model_config = ConfigDict(strict=True, frozen=True, extra="forbid")
    orders: list[OrderSnapshot]


class DemoOrderProvider:
    # 接受可选事实文件，测试可注入独立私有身份样本。
    def __init__(self, fixture_path: Path | str | None = None):
        path = Path(fixture_path) if fixture_path is not None else Path(__file__).with_name("demo_orders.json")
        self._orders = tuple(_DemoFixture.model_validate_json(path.read_text(encoding="utf-8")).orders)

    # 按身份列出演示订单。
    async def list_orders(self, *, user_id: str) -> list[OrderSnapshot]:
        return [order for order in self._orders if order.user_id == user_id]

    # 按身份查询演示订单。
    async def get_order(self, *, user_id: str, order_id: str) -> OrderSnapshot | None:
        return next((order for order in self._orders if order.user_id == user_id and order.order_id == order_id), None)
