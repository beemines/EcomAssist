"""Opt-in only: restart logistics with --plugin-module examples.mcp_extra_tools."""
from typing import Any
def register(mcp):
    @mcp.tool()
    def query_pickup_hours(order_id: str) -> dict[str, Any]:
        """查询订单演示取件点营业时段；mock信息。"""
        return {'order_id': order_id, 'pickup_hours': '09:00–18:00',
            'mock': True, 'source': 'mcp:logistics'}
