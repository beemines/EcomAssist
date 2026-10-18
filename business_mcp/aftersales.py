import argparse
from typing import Any
from mcp.server.fastmcp import FastMCP
from business_mcp.mock_data import warranty, return_progress


def create_aftersales_server(*, port: int) -> FastMCP:
    server = FastMCP('演示售后', host='127.0.0.1', port=port,
        streamable_http_path='/mcp', stateless_http=True, json_response=True)

    @server.tool()
    def query_warranty(order_id: str) -> dict[str, Any]:
        """查询订单商品在保信息，返回随机mock数据。"""
        return warranty(order_id)

    @server.tool()
    def query_return_progress(order_id: str) -> dict[str, Any]:
        """查询订单退货处理进度，返回随机mock数据，不执行退款。"""
        return return_progress(order_id)

    return server


def main():
    parser = argparse.ArgumentParser(description='Mock aftersales MCP, no database')
    parser.add_argument('--port', type=int, default=8102)
    args = parser.parse_args()
    create_aftersales_server(port=args.port).run(transport='streamable-http')


if __name__ == '__main__':
    main()
