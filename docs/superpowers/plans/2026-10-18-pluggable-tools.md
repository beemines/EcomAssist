# 即插即用工具系统 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [x]`) syntax for tracking.

**Goal:** 内置与两个业务 MCP Server 的工具热注册后可被 Agent 使用，统一校验、授权、执行、审计，聊天建单经过持久化预览确认才写入 tickets。

**Architecture:** 每轮加载本地策略并发现 MCP 工具，固定本轮目录、参数定义与预算；所有真正工具调用通过同一执行器。工单提案、原生暂停与实际写入分节点，两个确认入口生成可信服务端凭据，沿用原仓储幂等性。

**Tech Stack:** Python3.13、现有 FastAPI0.142.2 / SQLAlchemy2.0.54 / MySQL、LangGraph1.2.15与现有SQLite checkpoint、langchain-core1.6.6、mcp==1.30.0、langchain-mcp-adapters==0.3.2、jsonschema；原生HTML/CSS/JavaScript。

**Spec:** [2026-10-18-pluggable-tools-design.md](../specs/2026-10-18-pluggable-tools-design.md)，用户已明确批准书面设计及本计划，选择Native本会话顺序实现；任务1–8完成，任务9自动化及2026-10-19截图主流程、两个失败原句复验已通过，实际版本/范围见[最新复验报告](../reports/2026-10-19-pluggable-tools-reacceptance.md)。用户整合选择尚未提出。

## Global Constraints

- 唯一可写工具为内置 create_ticket；外部声明、模型参数、工具名称均不能授予写权限。写重试上限强制0，只读暂时故障默认最多重试1次。
- 固定 mcp==1.30.0、langchain-mcp-adapters==0.3.2，不升级已有核心框架来迁就依赖。完整解析如有矛盾按用户要求先停下说明，不自行换栈。
- 使用 Streamable HTTP；SDK1.x运行传输名streamable-http，适配器配置传输名streamable_http。两个Server独立进程、随机mock、不连接数据库或真实系统。
- 本地逐工具授权与策略热加载已获用户确认；新增工具允许注册本地策略，不改客服核心源码、不重启客服服务。未知工具只发现不开放。
- 原内置query_logistics从模型清单移除，不能保留重名竞争或作为MCP故障的伪成功回退。旧历史原文及工具名展示保留。
- 保留原投诉按钮的自填表单和POST接口；原表单提交已是确认，不再增加预览。新聊天建单必须原生interrupt/resume，取消不写tickets、审计permission_denied。
- tool_audit_logs无外键；失败不能影响原工具结果或回滚已成功工单。一次逻辑调用结算一条，内部重试汇总。
- 继续SQL原文、add_messages、完整checkpoint与三层模型视图；动态Schema按实际估算，暂停不重置费用/决策次数/恢复额度。
- Context7替代方式已获本章授权；每个实际使用的框架API先核对官方文档和安装后的锁定源码，追加[API记录](../references/2026-10-18-pluggable-tools-apis.md)。不要照抄SDK2.x或新文档的另一套streaming接口。
- 后端TDD，Prompt用标注集验证；前端按用户Vibe Coding例外，不写前端TDD、不安排前端code review，以页面操作和像素效果核验。
- 每个任务完成就追加dev-notes/ch08.md的原话、产出/实际结果、纠偏、翻车与返工，和任务一起提交，不在结尾集中补写。
- 保留8004及其工作树/检查点/原始证据。新客服默认8005，两Server8101/8102；占用先核验，只停自己创建且身份再次核对的进程，后台启动用Hidden。
- 本计划批准前不安装依赖、改产品、迁移表或启动服务。实施时使用using-git-worktrees建立新章节隔离工作树，不复用正在服务8004的工作树。

## Review Focus

1. 目录在预检和执行之间变化，或待确认时新工具加入/旧工具撤权：本轮定义保持，撤权仍生效，不能执行新Schema。由任务1、5、6、7固定测试。
2. 外部工具假冒只读、隐藏身份/确认参数夹带、别名撞create_ticket：不越过本地授权，拒绝也审计。由任务1、3、5固定测试。
3. 确认双击、响应丢失、提交后checkpoint失败/重启、旧卡片确认：最多一张工单，回执匹配原申请，写零自动重试。由任务7固定测试。
4. 工具成功但审计数据库断开，或MCP以content/artifact/isError返回：成功不被审计故障反转，错误不变成成功。由任务2、3、5固定测试。
5. 一台Server失联、工具Schema变大、超时层叠、会话暂停：其他工具可用，预算真实、不重放写入、不把等用户时间算执行超时。由任务3、5、6、7、9固定测试。

## 文件与接口约定

现有app/tools/executor.py、registry.py是扩展入口，原app/workflow/service.py仅保留生命周期和事件胶水；目录、MCP、审计、工单暂停各有独立文件。禁止把本章所有逻辑塞进service.py或agent.py。

| 单元 | 责任与文件 |
| --- | --- |
| 目录与策略 | app/tools/catalog_types.py、catalog.py、policies.py、plugins.py；config/tool-policy.json |
| 审计 | app/tool_audit/types.py、repository.py、migration.py、cli.py；sql/ch08-tool-audit.sql；app/db/models.py |
| 执行 | 扩展app/tools/types.py、executor.py；新增validation.py、authorization.py、results.py |
| MCP | business_mcp/logistics.py、aftersales.py、mock_data.py；app/tools/mcp_client.py |
| Agent桥接 | app/workflow/controls.py、agent.py、nodes.py、runtime.py、service.py、state.py、context_budget.py；必要的只读工具桥放tool_calls.py |
| 工单 | app/workflow/ticket_confirmation.py、ticket_actions.py；app/schemas/ticket_confirmation.py；app/api/ticket_confirmation.py；既有actions.py |
| 前端与交付 | app/static/ticket-confirmation.js、chat.js、chat.css、index.html；scripts/start-tool-system-demo.ps1；docs/tool-system-demo.md |

跨任务类型统一使用以下名称，定义在任务1/3并保持一致：

- ToolDefinition：公开name、description、input_schema、source、remote_name、operation、allowed_intents、order_id_arg、output_fields、status_map、timeout_seconds、max_retries、fingerprint。
- ToolRegistration：definition与本地factory；factory接收ToolContext、返回BaseTool。MCP工厂返回已经适配的BaseTool，权限仍取本地definition。
- PolicySnapshot：已校验策略版本、Server连接、逐工具规则和插件入口；不包含由模型提供的字段。
- CatalogSnapshot：version、definitions、注册工厂；`bind(context: ToolContext) -> BoundCatalog`，`to_manifest() -> dict`只输出纯数据。
- BoundCatalog：实现Mapping[str, BaseTool]，提供`definition(name: str) -> ToolDefinition`、`subset(names: Iterable[str]) -> BoundCatalog`，过滤不丢元数据。
- ExecutionContext：可信conversation_id、user_message_id、intent、raw_question、deadline、显式建单请求证据、确认凭据、订单归属检查器；不入模型参数或checkpoint。
- ConfirmationGrant：服务端构造，source为chat_preview或legacy_form，绑定会话、原消息、tool_call_id和规范化参数指纹；不接受模型传入的confirmed/approved替代。
- ToolOutcome沿用content/status/attempts；status仍为success/error，attempts=0表示执行前拦截。审计状态单独映射，不能把权限拒绝变成API成功创建。

所有pytest命令在新工作树执行，使用`./.venv/Scripts/python.exe -m pytest`；依赖通过uv锁文件管理。只在必要时窄提权调用原虚拟环境，避免此前Windows启动器无输出问题。不更换解释器来绕过失败。

---

### Task 1: 统一目录、本地策略与内置热注册

**Files:** Create app/tools/catalog_types.py、app/tools/catalog.py、app/tools/policies.py、app/tools/plugins.py、config/tool-policy.json、tests/tool_system_fakes.py、tests/test_tool_catalog.py；Modify app/tools/registry.py、pyproject.toml、uv.lock。

**Interfaces:**
- `PolicyStore(path: Path).load() -> PolicySnapshot`：完整读取/校验后返回新快照。
- `ToolCatalog.register(registration: ToolRegistration) -> None`。
- `ToolCatalog.snapshot(*, policy: PolicySnapshot, discovered: Sequence[ToolRegistration]=()) -> CatalogSnapshot`。
- `ToolCatalog.restore(manifest: dict, *, policy: PolicySnapshot, discovered: Sequence[ToolRegistration]) -> CatalogSnapshot`：恢复原名单并核验契约，不增加后来工具。
- 测试公共构造器`make_registration(name, *, source='builtin', operation='read', handler=None)`与`allow_policy(*registrations)`分别生成ToolRegistration和PolicySnapshot，不自动放权给任意生产工具。

- [x] **Step 1 — 准备隔离与依赖：** 按using-git-worktrees检查已附加工作树、创建本章隔离分支；保留8004。核对jsonschema官方draft校验API与锁定源码，加入两项已批准固定依赖和直接使用的jsonschema>=4.20,<5，生成uv.lock、uv sync --locked；原有固定依赖版本不变。记录依赖解析与原工具/Workflow/上下文基线结果，不运行第七步付费长批。
- [x] **Step 2 — 写失败测试：** tests/test_tool_catalog.py覆盖新增注册、策略修改热加载、坏配置不部分发布、未知工具不开放、重名/保留名拒绝、隐藏参数不可伪造、manifest可JSON序列化及恢复不扩大清单。核心断言：

```python
def test_new_registration_is_in_next_snapshot(catalog):
    registration = make_registration('new_read')
    catalog.register(registration)
    snapshot = catalog.snapshot(policy=allow_policy(registration))
    assert 'new_read' in snapshot.definitions
    assert snapshot.to_manifest()['version'] == snapshot.version
```

- [x] **Step 3 — 确认RED：** `./.venv/Scripts/python.exe -m pytest tests/test_tool_catalog.py -q`，预期新接口/行为缺失而失败，保存原输出。
- [x] **Step 4 — 最小实现：** 按本节接口实现不可变目录和本地插件入口加载；新增模块通过注册导入，不原地reload执行中的模块。启动登记现有工具，暂保持旧工厂调用兼容；冲突与策略错误不默默授予权限。
- [x] **Step 5 — GREEN与范围检查：** 跑test_tool_catalog.py及现有test_business_tools.py、test_tool_llm_payload.py；确认模型参数没有会话身份/确认字段。按实际失败修正接缝，不在测试中全局关闭权限。
- [x] **Step 6 — 留痕与提交：** 追加ch08，提交`feat(tools): add policy-backed hot tool catalog`，只暂存本任务文件。

### Task 2: 独立审计表、仓储和显式迁移

**Files:** Create app/tool_audit/__init__.py、app/tool_audit/types.py、app/tool_audit/repository.py、app/tool_audit/migration.py、app/tool_audit/cli.py、sql/ch08-tool-audit.sql、tests/test_tool_audit.py、tests/integration/test_tool_audit_storage.py；Modify app/db/models.py。

**Interfaces:**
- `ToolAuditRecord`包含设计第7节全部字段，时间/耗时明确，安全错误不含连接凭据。
- `ToolAuditRepository(database).append(record: ToolAuditRecord) -> None`：独立Session/短事务。
- `BestEffortAuditSink(repository, *, timeout_seconds: float).write(record: ToolAuditRecord) -> None`：失败仅日志，不抛业务错误。
- `migrate_tool_audit(database: Database) -> None`、`verify_tool_audit(database: Database) -> None`；CLI命令`python -m app.tool_audit.cli init|verify`。

- [x] **Step 1 — 核对再写RED：** 先读SQLAlchemy2.0官方JSON/AsyncSession事务文档和2.0.54安装源码，追记API记录。测试完整字段中文JSON、五种状态、无外键、会话不存在也能记录拒绝、重复tool_call_id跨会话不冲突、审计失败/超时不向调用方抛出。
- [x] **Step 2 — 运行RED：** `./.venv/Scripts/python.exe -m pytest tests/test_tool_audit.py -q`，预期新仓储/迁移契约缺失；集成测试默认skip不算通过。
- [x] **Step 3 — 实现：** ORM与DDL逐字段一致，设计中的五种status原样；按会话时间和tool_call_id建普通索引、零外键。verify只读，init只在目标匹配时补表，已有结构漂移明确拒绝；不用现有仅解析旧DDL子集的正则勉强解析新JSON/ENUM定义。
- [x] **Step 4 — GREEN/独立SQL验证：** `./.venv/Scripts/python.exe -m pytest tests/test_tool_audit.py -q`；显式`./.venv/Scripts/python.exe -m pytest --run-mysql tests/integration/test_tool_audit_storage.py -q`只用现有fixture拥有的测试库/随机schema。断言information_schema无外键，审计事务回滚不影响独立工单事务。
- [x] **Step 5 — 留痕与提交：** 记录实际PASS/SKIP与目标身份核验，提交`feat(audit): persist best-effort tool invocation records`。不在该任务迁移演示库或清理历史表。

### Task 3: 统一校验、授权、结果与执行审计

**Files:** Modify app/tools/types.py、app/tools/executor.py；Create app/tools/validation.py、app/tools/authorization.py、app/tools/results.py、tests/test_tool_execution_policy.py、tests/test_tool_result_normalization.py；Modify tests/test_tool_executor.py及共享fakes。

**Interfaces:**
- `ToolExecutor.execute(call: ToolCall, registry: BoundCatalog, *, context: ExecutionContext) -> ToolOutcome`，保留已有调用取消/期限口径，生产调用者在任务6/7迁移。
- `validate_arguments(definition: ToolDefinition, arguments: dict) -> dict | ToolOutcome`。
- `authorize_call(definition: ToolDefinition, call: ToolCall, context: ExecutionContext) -> ToolOutcome | None`；None表示允许继续。
- `normalize_result(raw: object, definition: ToolDefinition) -> ToolOutcome`，MCP形态适配由任务5补齐实包验证。

- [x] **Step 1 — 写RED：** 严格类型/缺参/越界/额外身份参数；无确认写入、伪approved、外部write、撤权均拒绝并审计；读临时故障两尝试、空结果一尝试、写超时一尝试；审计坏掉不改变返回结果；取消传播。用毫秒级可控超时与调用计数，不增加多组60秒等待。

```python
async def test_unconfirmed_write_never_reaches_handler(executor, write_call, bound_catalog, unconfirmed_context, spy, audit_sink):
    result = await executor.execute(write_call, bound_catalog, context=unconfirmed_context)
    assert result.content['error']['code'] == 'permission_denied'
    assert spy.calls == 0
    assert audit_sink.records[-1].status == 'permission_denied'
    assert audit_sink.records[-1].retry_count == 0
```

- [x] **Step 2 — 运行RED：** `./.venv/Scripts/python.exe -m pytest tests/test_tool_execution_policy.py tests/test_tool_result_normalization.py -q`。
- [x] **Step 3 — 实现：** 业务参数Schema校验后才注入可信信息；确认凭据逐项匹配调用和参数指纹。只读暂时错误最多一次重试，query_faq沿用既有零重试覆盖，永久错误/空结果/取消不重试，写重试强制0。结果白名单、枚举映射、ensure_ascii=False，失败仍为error ToolMessage；finally中的审计有独立短时限。
- [x] **Step 4 — GREEN与对照：** 运行本任务及旧executor测试；核对attempts到retry_count映射，最终超时status=timeout；第一次超时后成功为success/retry_count=1。旧工具直接调用测试可保留，但不能用旧接口绕过新生产写门禁。
- [x] **Step 5 — 留痕与提交：** 记录RED/GREEN、审计故障及物理尝试计数，提交`feat(tools): enforce unified execution and write confirmation`。

### Task 4: 两个独立 Streamable HTTP mock Server

**Files:** Create business_mcp/__init__.py、business_mcp/logistics.py、business_mcp/aftersales.py、business_mcp/mock_data.py、tests/test_business_mcp_servers.py、examples/mcp_extra_tools.py。

**Interfaces:**
- `create_logistics_server(*, port: int, plugin_module: str | None=None) -> FastMCP`，导出query_logistics(order_id: str)。
- `create_aftersales_server(*, port: int) -> FastMCP`，导出query_warranty(order_id: str)、query_return_progress(order_id: str)。
- CLI：`python -m business_mcp.logistics --port 8101`、`python -m business_mcp.aftersales --port 8102`；默认/mcp、stateless_http=True、json_response=True。
- examples/mcp_extra_tools.py提供可选的`register(mcp: FastMCP) -> None`，新增query_pickup_hours(order_id: str)，默认不加载，供任务9真实Server扩展演示。

- [x] **Step 1 — 先核对已安装源码再写RED：** 核对FastMCP1.30构造器、tool注册、run/ASGI lifespan与StreamableHTTP测试客户端签名；不能采用2.x MCPServer。测试清单、输入Schema、mock标记、中文JSON、随机值合法范围、无数据库访问与导入副作用。
- [x] **Step 2 — 运行RED：** `./.venv/Scripts/python.exe -m pytest tests/test_business_mcp_servers.py -q`，缺少Server/协议行为失败。
- [x] **Step 3 — 实现：** 两个模块分别启动，随机mock只存在Server端，测试可注入随机种子。额外插件模块只由本地启动配置指定；没有注册的样例不暴露。采用Server自身ASGI lifespan，避免Mount丢失session_manager。
- [x] **Step 4 — GREEN与真实HTTP：** 测试以独立本地进程走initialize/tools/list/tools/call，断言不同PID、正确工具名、结构化结果；测试结束只回收fixture拥有的进程。零GLM、零SQL。
- [x] **Step 5 — 留痕与提交：** 保存协议/PID结果、核对mock范围，提交`feat(mcp): add logistics and aftersales mock servers`。

### Task 5: 多 Server 发现、热策略与 MCP 结果适配

**Files:** Create app/tools/mcp_client.py、tests/test_mcp_discovery.py、tests/test_mcp_execution.py；Modify app/tools/catalog.py、app/tools/policies.py、app/tools/results.py、config/tool-policy.json、app/config.py、.env.example。

**Interfaces:**
- `MCPDiscovery(client: MultiServerMCPClient).discover(policy: PolicySnapshot) -> DiscoveryResult`（async），结果含registrations与按Server区分的安全错误。
- `ToolCatalogProvider(catalog: ToolCatalog, policies: PolicyStore, discovery: MCPDiscovery).acquire() -> CatalogSnapshot`（async），每轮只调用一次。
- 配置固定两Server的Streamable HTTP地址、连接/读取时限、本地逐工具条目；MCP公开query_logistics，旧内置同名项不进入有效目录。

- [x] **Step 1 — 写RED：** 使用真实0.3.2适配器/本地SDK Server，分别发现两来源；一台断开另一台和内置仍可用；Server新增工具+本地授权下一次可见；未知工具/假只读声明不开放；重名拒绝、撤权生效；content/artifact/isError/传输异常不误判。
- [x] **Step 2 — 运行RED：** `./.venv/Scripts/python.exe -m pytest tests/test_mcp_discovery.py tests/test_mcp_execution.py -q`，不发模型请求。
- [x] **Step 3 — 实现：** get_tools(server_name=...)分Server并发发现；固定公开名/原始名映射，权限来自本地规则，不根据description/annotations推断；按任务1一次发布目录。实际工具调用仍调用MultiServerMCPClient适配工具，不重写成普通HTTP查询或改用另一客户端替代。
- [x] **Step 4 — GREEN与形态核验：** 真实SDK结果优先读取已验证structured_content，明确处理文本content块和isError；MCP调用外层/连接时限协调，业务tools/call无隐藏额外重试。工具结果过任务3同一整理/审计，订单参数先经可信归属检查。
- [x] **Step 5 — 留痕与提交：** 保存目录版本、来源、Server重启前后PID和错误隔离结果，提交`feat(mcp): discover and authorize tools per conversation turn`。

### Task 6: Agent、确定性工具节点与第七步上下文接入

**Files:** Modify app/main.py、app/tools/registry.py、app/workflow/agent.py、app/workflow/controls.py、app/workflow/runtime.py、app/workflow/service.py、app/workflow/state.py、app/workflow/nodes.py、app/workflow/context_budget.py、app/workflow/intent.py、app/workflow/prompts.py、app/agent/bare.py、app/agent/controls.py；Create app/workflow/tool_calls.py（仅用于已有强制工具节点桥接）、tests/test_dynamic_agent_tools.py、tests/test_dynamic_tool_context.py、tests/fixtures/tool_system/ticket_intents.json；Modify相关workflow/context fakes与测试。

**Interfaces:**
- Runtime.registry使用BoundCatalog，新增可信ExecutionContext；State新增tool_catalog_version、纯数据tool_manifest和可追溯ticket_request，不持久化客户端/工厂。
- `stable_tool_schema(catalog: BoundCatalog, *, intent: str | None=None, ticket_requested: bool=False) -> list[dict]`，保留internal_response_control协议，模型只看到允许的业务参数。
- `run_workflow_tool(call: ToolCall, registered: ToolRegistration, *, context: ExecutionContext, executor: ToolExecutor) -> ToolOutcome`（async）：让已生成SQL工具流水的强制订单/FAQ节点也经统一校验/执行/审计，内部身份查询和嵌入/重排不伪计成额外业务工具。
- `has_explicit_ticket_request(text: str) -> bool`用于写授权证据，不替代LLM意图分类；工单意图含多轮补描述，明确否定/问如何办理不授权。

- [x] **Step 1 — 写RED与标注集：** 用脚本模型要求调用新注册名称，断言真实绑定Schema含该名、实际handler执行、正确来源审计；强制订单/FAQ也有对应审计。test_unknown_native_tool_reaches_denial_audit固定未知原生工具的拒绝审计，正文假JSON仍不执行。测试预检/执行只用同一snapshot、工具变大预算按实际计、manifest可恢复、SQL/tool配对及旧checkpoint缺字段兼容。标注集包括明确建单、未讲问题、补描述、否定、仅转人工、投诉但未要求建单；离线协议测试不冒充真实分类准确率。
- [x] **Step 2 — 运行RED：** `./.venv/Scripts/python.exe -m pytest tests/test_dynamic_agent_tools.py tests/test_dynamic_tool_context.py -q`。
- [x] **Step 3 — 实现目录贯穿：** prepare获取一次CatalogSnapshot，预检与append后绑定复用它；替换硬编码白名单/READ_TOOLS对扩展的阻碍，过滤用BoundCatalog.subset保留元数据。合法原生协议中的未知/未授权工具交引擎拒绝并审计，不在协议解析前提前抛掉而漏审计。模型与Workflow强制工具都走Task3；既有workflow_tool的订单/FAQ闭包包装成可信只读ToolRegistration，不允许模型指定闭包或覆盖处理器，不改变退款订单/政策事实顺序。
- [x] **Step 4 — 实现工单入口与预算：** LLM分类新增“工单”，沿用intent/confidence严格JSON；正在补描述的请求证据从SQL与前一有效澄清根核验，切换业务或否定即失效。新工具Schema进入原上下文预算，manifest在恢复时限制旧清单，撤权执行前检查。历史模拟提示、原生tool_calls协议、一次模型恢复和最终流保护不放宽。
- [x] **Step 5 — GREEN与范围：** `./.venv/Scripts/python.exe -m pytest tests/test_dynamic_agent_tools.py tests/test_dynamic_tool_context.py tests/test_workflow_agent.py tests/test_workflow_agent_limits.py tests/test_workflow_agent_quality.py tests/test_after_sales_workflow.py tests/test_context_agent.py tests/test_context_budget.py tests/test_context_prefix.py tests/test_context_state_history.py tests/test_context_workflow.py tests/test_workflow_recovery.py -q`。用实际测试输出记录契约更新，不能为过旧测试全局关闭权限/恢复。
- [x] **Step 6 — 留痕与提交：** 记录真实Schema token、来源与SQL流水，提交`feat(agent): consume dynamic tools with bounded context`。纯Prompt质量留到任务9少量页面标注验收，不额外直接外发批量分类。

### Task 7: 工单提案、原生暂停恢复与双入口授权

**Files:** Create app/workflow/ticket_confirmation.py、app/workflow/ticket_actions.py、app/schemas/ticket_confirmation.py、app/api/ticket_confirmation.py、tests/test_ticket_confirmation_state.py、tests/test_ticket_confirmation_api.py、tests/test_ticket_confirmation_lifecycle.py；Modify app/workflow/graph.py、app/workflow/state.py、app/workflow/service.py、app/workflow/actions.py、app/main.py、app/api/chat_actions.py、app/context/history_reader.py、tests/test_chat_actions.py、tests/integration/test_workflow_actions.py。

**Interfaces:**
- 状态ticket_confirmation包含confirmation_id、原turn_id、tool_call_id、参数/指纹、暂停根回执与决策；turn_status增加awaiting_ticket，原v2缺字段按None兼容。
- 父图节点`prepare_ticket_confirmation`、`await_ticket_confirmation`、`execute_ticket_confirmation`和`ticket_confirmation_response`；准备/等待节点不写tickets。
- `TicketConfirmationService(service).pending(conversation_id: str) -> dict`和`confirm(conversation_id: str, payload: TicketConfirmationRequest) -> PreparedWorkflowChat`（async）。
- `TicketConfirmationRequest`定义在app/schemas/ticket_confirmation.py：turn_id为合法SQL消息ID字符串，confirmation_id/checkpoint_id为UUID字符串，decision为Literal['confirm','cancel']；严格类型、拒绝额外字段。
- GET /api/conversations/{id}/pending-ticket；POST /api/conversations/{id}/actions/confirm-ticket，body仅turn_id、confirmation_id、checkpoint_id、decision=confirm|cancel。POST复用ManagedChatResponse。

- [x] **Step 1 — 写RED：** 无描述先澄清，不出现空预览；一轮提案只有一次SQL工具申请。confirm写1张、返回真实号；cancel零写入、permission_denied审计、正常done；无确认execute拒绝；原投诉表单继续成功且审计齐。
- [x] **Step 2 — 写恢复反例并运行RED：** stale/跨会话/改参数/伪确认字段、双击、丢回包、提交后checkpoint失败、重启恢复、同轮撤权、新消息替代、用户等待不耗活动预算、费用不重置。`./.venv/Scripts/python.exe -m pytest tests/test_ticket_confirmation_state.py tests/test_ticket_confirmation_api.py tests/test_ticket_confirmation_lifecycle.py -q`。
- [x] **Step 3 — 实现暂停与确认：** Agent合法提案返回父图，不在会被重跑的Agent包装节点先写库；准备节点持久化参数，独立节点interrupt，公开恢复入口锁内核对最新根/SQL/原manifest/相关契约/当前权限。确认凭据只在这些检查后构造。
- [x] **Step 4 — 执行与回执：** confirm走同一引擎/原TicketRepository稳定幂等编号，cancel不调用仓储；配对ToolMessage和审计。成功固定回执`工单已提交，工单号：{ticket_no}。`；取消固定回执`已取消，本次未创建工单。`，不得被社交/澄清词法守卫误拒。写超时如实说明结果未确认且未自动重试，不用新call_id自动再建。
- [x] **Step 5 — 保留旧入口并GREEN：** TicketActionService原表单核验后传legacy_form凭据，同一引擎不再加预览；旧payload与返回字段保持。跑本任务、原test_chat_actions.py/test_ticket_form.py及显式独立MySQL的工单集成测试；断言确认/取消、旧入口、审计失败、提交边界与待办回载真实一致。
- [x] **Step 6 — 留痕与提交：** 保存中断/恢复位置、物理仓储调用次数和工单差量，提交`feat(tickets): require durable preview confirmation for agent writes`。

### Task 8: 主题工单预览卡片（Vibe Coding例外）

**Files:** Create app/static/ticket-confirmation.js；Modify app/static/chat.js、app/static/chat.css、app/static/index.html。

**Interfaces:**
- `window.MewTicketConfirmationUI.render({container, preview, onDecision})`，由chat.js注入confirm/cancel回调；业务定位按Task7接口，不自造checkpoint或提交description覆盖预览。
- chat.js支持ticket_confirmation事件和paused.reason=ticket_confirmation；刷新/切换会话读取pending-ticket，恢复有效卡片。

- [x] **Step 1 — 直接实现效果：** 浅绿主题卡片展示类型/描述，两个独立确认/取消按钮；提交中禁用、防连点，取消有正常回执。所有用户/工具文本用textContent，不把描述拼进HTML；原投诉表单不改。
- [x] **Step 2 — 事件与回载：** 复用ManagedChatResponse，卡片只渲染来自实际暂停根的载荷；切换会话、旧卡片失效、HTTP冲突/断网可恢复。后端成功已写入但客户端丢回包时读取回执，不生成新提案。
- [x] **Step 3 — 页面核验：** 用真实浏览器打开8005，检查窄屏、长描述、确认/取消/刷新/旧卡片、旧投诉表单；保存实际截图和对应checkpoint/审计。分别执行`node --check app/static/chat.js`与`node --check app/static/ticket-confirmation.js`；不为前端写TDD或派code review。
- [x] **Step 4 — 留痕与提交：** 记录用户视觉纠偏及实际操作结果，提交`feat(ui): add themed ticket confirmation cards`。

### Task 9: 整体接通、六项验收与交付

**Files:** Create scripts/start-tool-system-demo.ps1、scripts/tool-system-process-ownership.ps1、scripts/tool-system-storage-evidence.py、tests/test_tool_system_demo_ownership.py、docs/tool-system-demo.md、docs/superpowers/reports/2026-10-18-pluggable-tools-acceptance.md、examples/builtin_dispatch_site.py；Modify .gitignore、README.md、dev-notes/ch08.md及必要后端契约测试。

**Interfaces:**
- `pwsh -NoProfile -File scripts/start-tool-system-demo.ps1`：按身份核验独立启动三个普通演示进程，不携带付费验收cap；单个Server的重启可单独执行，不停止客服。
- `examples/builtin_dispatch_site.py`为可注册新模块，导出query_demo_dispatch_site(order_id: str)，返回带mock标记的演示处理中心；初始策略不注册它。
- 证据存runtime/tool-system-evidence/，加入现有忽略规则，含版本/SHA/PID、页面/SQL/审计对应，不保存密钥或认证头。

- [x] **Step 1 — 先无模型联调：** 为新启动器写未知监听PID绝不停止、目录/创建时间/解释器/祖先不符拒绝接管的后端测试，RED后实现Hidden启动，再验证显式init/verify审计表、三进程健康、两种工具来源、既有订单/RAG流水、确认/取消以及审计数据库故障。演示DDL先核对当前数据库/主机/端口和容器身份；只读verify成功不冒称执行过迁移。普通启动不重跑DDL。
- [x] **Step 2 — 后端整分支检查：** 依据Review Focus和已批准执行方式做一次后端整分支独立审查，不审前端；必要修复按一个归因修复波和范围复审处理。不要无新变化重新派已通过任务或重审整章。
- [x] **Step 3 — 少量页面验收：** 用生成的测试问句和演示订单，通过页面执行设计第9节全部六项；包含两个Server三种读工具、缺描述补齐、确认、取消、否定/仅转人工、原投诉表单。沿用用户小额页面GLM/BGE授权，整批计划上限40次GLM/12次嵌入/6次重排，含后台摘要和失败请求，自动重试规则不变。达到上限就报告未完成项，不增加新批次。不开新非页面付费诊断，不修改SDK/sitecustomize做临时注入。执行补充：此前未验的组合查询/仅转人工/窄屏于用户2026-10-19新请求后有界复验通过；原热注册与投诉表单等证据按其实际版本保留。
- [x] **Step 4 — 动态注册与故障证据：** 在本地登记新的内置模块，实际Agent调用query_demo_dispatch_site；在Server侧加载Task4样例并登记本地权限，仅重启该Server，实际Agent调用query_pickup_hours。保存客服PID/core SHA未变、目录变化和审计来源。受控毫秒级读/写超时在独立测试调用中验证物理尝试和审计，不靠供应商真的出故障；确认1张、取消0张及写retry_count=0分别查库。
- [x] **Step 5 — 最终冻结回归：** 页面问题如需修复，先保留失败、完成相关回归/审查再冻结源码；`./.venv/Scripts/python.exe -m pytest -q`运行一次完整最终回归，显式独立MySQL集成结果与skip分开。真实模型定点结果不能由单元测试代替，旧第七步长验收状态不倒改。最终5acd974：2930通过188跳过；本章SQL专项4通过。
- [ ] **Step 6 — 交付与finish：** 报告逐项PASS/FAIL/未执行、最终版本、所有用量及演示命令；普通8005无验收cap，两个Server可独立重启，8004未操作。本地证据和工作树保留。按verification-before-completion与finishing-a-development-branch执行本章最终用户整合选择，未获本章整合选择前不沿用第七步推送授权；提交`docs(ch08): record tool system acceptance and delivery`。

任务9执行补充：初批实用38次GLM；用户另行明确批准最多20次页面定点，追加实用20，累计58，嵌入/重排0。两个简单热工具完整答案、否定建单、原确认/取消与投诉表单已取得页面证据；组合在保/退货进度修复后仅离线复验，Step3保持未完成，未自动追加第三批或宣称整章finish。实际状态优先以验收报告为准。

2026-10-19更新：用户主动要求先测试再给步骤，另行有界复验28/30次GLM，截图主流程、两个组合失败原句、转人工和319px窄屏均通过，相关离线34通过、无产品变更。见[本次报告](../reports/2026-10-19-pluggable-tools-reacceptance.md)与[用户验收步骤](../../ch08-manual-acceptance.md)。此前未复验的主要缺口已补齐；热注册/PID和受控故障按各自实际证据版本记录，本章整合选择仍未提出。

## 计划自检与执行交接

已逐项自检：功能1由任务1/5/6承接，功能2由任务3/6承接，功能3由任务3/7承接，功能4由任务3/5承接，功能5由任务2/3/6承接，功能6由任务4/5承接，功能7由任务6/7/8承接，六项实际验收统一在任务9核验。五项Review Focus均有归属测试；共享类型/签名、现有测试路径和本地文档链接已核对。计划约235行，与约205行设计的比例相当，没有用实现函数体替代计划。

设计及本计划已分别审批，用户明确选择Native本会话顺序实现。实际实现和独立后端整分支审查已执行，任务9保留未通过/未执行的真实页面项；不据自动化通过宣称全部页面验收完成。

本章已按用户选择执行Native：根代理顺序实现，最后一次独立后端整分支审查，修复由根代理按反例验证，没有第二次整分支审查；前端沿用用户Vibe Coding例外。
