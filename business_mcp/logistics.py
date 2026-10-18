import argparse
from typing import Any
from importlib import import_module
from mcp.server.fastmcp import FastMCP
from business_mcp.mock_data import logistics


def create_logistics_server(*, port: int, plugin_module: str | None = None) -> FastMCP:
    server = FastMCP('演示物流', host='127.0.0.1', port=port,
        streamable_http_path='/mcp', stateless_http=True, json_response=True)

    @server.tool()
    def query_logistics(order_id: str) -> dict[str, Any]:
        """查询订单物流轨迹；返回随机mock数据，不能作为真实到货承诺。"""
        return logistics(order_id)

    if plugin_module:
        import_module(plugin_module).register(server)
    return server


def main():
    parser = argparse.ArgumentParser(description='Mock logistics MCP, no database')
    parser.add_argument('--port', type=int, default=8101)
    parser.add_argument('--plugin-module')
    args = parser.parse_args()
    create_logistics_server(port=args.port, plugin_module=args.plugin_module).run(transport='streamable-http')


if __name__ == '__main__':
    main()
