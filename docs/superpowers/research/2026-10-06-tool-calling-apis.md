# 第二步：工具调用与数据库 API 核对

日期：2026-10-06（北京时间）。阶段：设计前研究，尚未实施。

## 现有应用接口

- `/api/chat` 仍是聊天页使用的入口，请求字段为 `session_id`、`message`。
- 当前 SSE 仅支持 `delta`、`done`、`error`。`ManagedChatResponse` 把所有非 `delta` 事件视为终止事件；新增状态帧时必须改为只把 `done`、`error` 视为终止。
- 当前内存历史只接受交替的 user/assistant 完整消息对。工具申请及 ToolMessage 不能直接塞进现有验证器，需按完整对话轮次重新定义持久化、回放和裁剪边界。
- 客服 System Prompt 目前明确禁止查询订单；增加工具后需同步更新为仅依据工具返回的数据回答。
- 第一阶段已固定的 LangChain/OpenAI 依赖先保留，新增 SQLAlchemy 和 MySQL 驱动前再锁版本并核对接口。

## Context7：LangChain

已查询 `/websites/langchain_oss_python` 与 `/websites/reference_langchain`。

- `@tool` 可通过 `args_schema` 指定 Pydantic 参数模型；工具说明与字段说明进入模型的工具定义。
- `ChatOpenAI.bind_tools` 可绑定工具，`tool_choice` 支持自动选择，`parallel_tool_calls=False` 用于限制并行申请。应用仍必须校验实际工具申请数量，不能仅依赖请求参数。
- 工具申请通过 `AIMessage.tool_calls` 表示；返回结果的 `ToolMessage.tool_call_id` 必须匹配申请中的 id。
- 收敛阶段使用不绑定工具的模型实例生成最终回复，应用不再执行下一轮工具申请。

官方来源：[工具定义](https://docs.langchain.com/oss/python/langchain/tools)、[模型与工具调用](https://docs.langchain.com/oss/python/langchain/models)、[ChatOpenAI](https://reference.langchain.com/python/langchain-openai/ChatOpenAI)。

2026-10-06 在现有 `.venv` 中用 `inspect.signature` 核对：`ChatOpenAI.bind_tools` 实际包含 `tool_choice`、`strict`、`parallel_tool_calls`；`tool` 实际包含 `args_schema`；`ToolMessage` 实际包含 `tool_call_id`、`status`。仅导入和检查本地接口，没有调用真实模型。

## Context7：SQLAlchemy

已查询 `/websites/sqlalchemy_en_20`。

- MySQL 异步访问支持 `mysql+aiomysql://` 配合 `create_async_engine`。
- 使用 `async_sessionmaker` 创建短生命周期的 `AsyncSession`；不同并发任务不能共享同一 Session。
- 事务用 Session 的 `begin` 管理，服务关闭时释放异步 Engine。
- FAQ 可使用绑定参数的 `contains(..., autoescape=True)` 构造 LIKE；转义 `%`、`_` 等通配符，不把输入拼接到 SQL。
- 通用 JSON 类型可用于存储工具申请和参数，SQLAlchemy 在 MySQL 上采用对应 JSON 类型。
- 用户随后提供权威 DDL 后补查 BIGINT UNSIGNED、MySQL 自动更新时间与既有表映射；不能仅设置 ORM 的 server_onupdate 就认为已经生成了 ON UPDATE DDL，建表仍以用户 SQL 为准。

官方来源：[异步 ORM](https://docs.sqlalchemy.org/en/20/orm/extensions/asyncio.html)、[MySQL 方言](https://docs.sqlalchemy.org/en/20/dialects/mysql.html)、[字符串操作](https://docs.sqlalchemy.org/en/20/core/sqlelement.html)。

## Context7：FastAPI 与 Docker Compose

已查询 `/websites/fastapi_tiangolo` 与 `/docker/compose`。

- 流式响应与 `yield` 依赖具有相应资源生命周期；设计采用短事务读写数据库，避免模型生成和 SSE 推送期间持续占用数据库连接。
- Compose 支持具名数据卷、仅绑定 `127.0.0.1` 的端口发布和健康检查；`up --wait` 可等待服务健康。
- 补充核对 MySQL 官方镜像说明：数据库及用户配置由镜像初始化环境变量提供，已有数据目录不会因再次启动而重新初始化。演示建表和种子数据应做成独立、可重复执行且不清空现有数据的命令。

官方来源：[FastAPI 流式响应依赖](https://fastapi.tiangolo.com/advanced/advanced-dependencies/)、[Compose](https://github.com/docker/compose)、[MySQL 官方镜像](https://hub.docker.com/_/mysql/)。

## 环境与模型验收待核实事项

- 当前 Docker CLI 为 29.8.1，Compose 为 v5.5.1；`docker version` 的 Server 为 null，Docker Desktop Linux Engine 管道不存在。MySQL 尚未启动。
- Context7 的 `/websites/bigmodel_cn_cn` 未匹配到 `glm-5.3-flash` 的具体 Function Calling 查询；限定智谱官方域名的补充搜索也未找到相应模型页。这不证明模型不支持，需要在实现和验收阶段用现有标准端点配置核对。
- 当前模型配置沿用已选择的 `glm-5.3-flash`。若实测不支持所需工具调用参数或响应结构，按用户要求暂停确认，不自动换模型、上游或协议。
- 用户随后回复“确认”批准所展示的设计；每条用户消息最多执行一个逻辑工具调用，执行重试不启动新的模型决策轮。
- 输入预算需计入工具 Schema、参数、调用申请与返回结果；收敛阶段需重新核对预算，不能裁断必需的 tool_call/ToolMessage 组合。
