# 第八步：官方接口与版本核对

核对日期：2026-10-18。用户明确批准本章使用官方文档与对应版本源码代替当前不可调用的Context7。此文件记录设计阶段只读核对，不代表依赖已经安装或完整解析通过。

## 1. 版本与用户确认

| 包 | 官方查询结果 | 本章选择 |
| --- | --- | --- |
| mcp | 最新正式版2.3.0；最新1.x正式版1.30.0 | 用户选择1.30.0 |
| langchain-mcp-adapters | 最新正式版0.3.2，要求mcp>=1.24.0,<2.0.0 | 用户选择0.3.2 |
| langchain-core | 适配器要求>=1.3.3,<2.0.0 | 保持仓库1.6.6 |
| LangGraph | 仓库1.2.15 | 保持 |
| FastAPI / SQLAlchemy | 仓库0.142.2 / 2.0.54 | 保持 |

MCP1.30.0要求Python>=3.10、httpx>=0.27.1,<1.0.0、Python<3.14时pydantic>=2.11.0,<3.0.0、pydantic-settings>=2.5.2；仓库Python3.13、httpx0.28.1、pydantic2.13.5、settings2.15.0满足对应声明。仍需实施时完整解析锁文件，不能用局部范围检查冒充解析成功。

官方元数据：

- [MCP最新元数据](https://pypi.org/pypi/mcp/json)
- [MCP1.30.0元数据](https://pypi.org/pypi/mcp/1.30.0/json)
- [适配器0.3.2元数据](https://pypi.org/pypi/langchain-mcp-adapters/0.3.2/json)
- [官方SDK v2迁移说明](https://github.com/modelcontextprotocol/python-sdk/blob/main/docs/migration.md)

发现2.x与适配器的明确不兼容后先询问用户；用户选择“锁定mcp1.30.0 + adapters0.3.2”，未自行换方案或忽略依赖约束。

## 2. MCP官方SDK 1.30.0

来源：[v1.30.0 FastMCP源码](https://github.com/modelcontextprotocol/python-sdk/blob/v1.30.0/src/mcp/server/fastmcp/server.py)。

核对项：

- 导入路径为 mcp.server.fastmcp.FastMCP。
- FastMCP构造器接受host、port、streamable_http_path、json_response、stateless_http等设置；本章路径默认/mcp。
- `run(self, transport: Literal['stdio','sse','streamable-http']='stdio', mount_path: str | None=None) -> None` 是同步入口。
- `streamable_http_app(self) -> Starlette` 使用构造器设置，创建并管理Streamable HTTP会话组件。
- 不使用SDK2.x的MCPServer导入路径，也不把2.x中运行方法的关键字参数照搬给1.x。
- 本章Server独立运行；若选择ASGI启动入口，必须核对该应用自身lifespan，不能误以为挂载子应用自动运行lifespan。

上面的Server传输字符串为带短横线的 `streamable-http`；下面的适配器连接配置为带下划线的 `streamable_http`，不得混淆。

## 3. MultiServerMCPClient 0.3.2

来源为PyPI官方发布的0.3.2 wheel。只在内存读取ZIP源码，未安装、未执行包代码；下载内容SHA256与官方元数据一致：`094e6b3096dbcc408417d5722f6915f164772e50c502ae3d8989405bf12c3c84`。

核对文件：langchain_mcp_adapters/client.py、tools.py、sessions.py。

- MultiServerMCPClient从connections创建客户端，提供callbacks、tool_interceptors、tool_name_prefix、handle_tool_errors等选项。
- `async get_tools(self, *, server_name: str | None=None) -> list[BaseTool]`，支持按Server分别发现；None发现全部。
- StreamableHttpConnection中`transport: Literal['streamable_http']`、url以及可选timeout、sse_read_timeout等字段。会话/传输超时要和执行器总超时协调。
- tools适配的args_schema直接使用工具inputSchema，可为JSON Schema字典；不能继续假设所有get_input_schema结果都具有Pydantic的model_fields。
- 结果适配采用content_and_artifact，MCP的structuredContent进入artifact.structured_content；正文可为content块。现有执行器只接受字符串JSON，需要显式适配这些形态。
- 工具执行错误isError可成为error ToolMessage，但传输/会话故障仍可能抛异常，不能只判断result.status。

参考文档：[客户端API](https://reference.langchain.com/python/langchain-mcp-adapters/client/MultiServerMCPClient)、[LangChain MCP说明](https://docs.langchain.com/oss/python/langchain/mcp)。文档按当前版本演进，实施仍以安装后的0.3.2源码/签名为准。

初次尝试按GitHub v0.3.2标签读取适配器源码未成功，随后改用官方发布wheel按哈希核验，不将读取失败当成接口不存在。

## 4. 协议与LangGraph

- [MCP工具协议](https://modelcontextprotocol.io/specification/2025-11-25/server/tools)：tools/list负责发现，tools/call负责调用；工具元数据不构成本地授权；不能把通知当作刷新清单的唯一保证。
- [LangGraph interrupt官方文档](https://docs.langchain.com/oss/python/langgraph/interrupts)：同一thread恢复，Command(resume=...)提供interrupt返回值；中断节点会从开头重跑，因此副作用不能放在中断前，不能用普通异常捕获吞掉暂停。
- 仓库已有 app/workflow/selection.py、order_actions.py、service.py、persistence.py 体现本项目1.2.15上的根检查点、会话锁和受控恢复口径；第八步复用并测试，不切换到文档中新增的另一套streaming接口。

后续凡修改SQLAlchemy表/事务、FastAPI接口或其他具体API，继续先核对该框架官方文档与本项目锁定源码，并在此文件追加实际使用的签名；当前不提前声称尚未核对的接口已核对。
