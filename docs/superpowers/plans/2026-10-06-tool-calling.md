# 客服单轮工具调用 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 在现有 SSE 客服聊天中接通五个业务工具，保存完整工具流水，并演示 FAQ 的预期漏召回。

**Architecture:** MySQL 原生执行用户 SQL，SQLAlchemy 只映射和访问既有四表。应用每轮先选择至多一个工具，执行并回灌后使用不绑定工具的模型流式回答；短事务保存事实，完整消息组负责历史恢复和预算裁剪。后端采用已选择的 Subagent-Driven，聊天页面按用户例外直接 Vibe Coding。

**Tech Stack:** 现有 Python、FastAPI、LangChain、ChatOpenAI；新增 `sqlalchemy[asyncio]==2.0.54`、`aiomysql==0.3.2`、Docker MySQL `8.4`，不升级已有依赖。

**Spec:** [正式设计](../specs/2026-10-06-tool-calling-design.md)。接口资料见 [Context7 研究记录](../research/2026-10-06-tool-calling-apis.md)。

## Global Constraints

- `sql/schema.sql` 是权威 DDL，原样执行；仅 faq/conversations/messages/tickets 四表，不添加字段，不调用 create_all/drop_all。
- 单条用户消息最多一个逻辑工具、一次选择请求及一次最终流式请求；工具超时默认 5 秒，最多一次重试，取消后不重试。
- `conversation_id` 使用无前导零的正整数十进制字符串，范围 `1..18446744073709551615`；拒绝 UUID、数字 JSON、浮点、布尔及空串。消息最多 20000 字符。
- `TOOL_INPUT_TOKEN_BUDGET=8000`；提取接口继续 `INPUT_TOKEN_BUDGET=2000`，输出上限沿用已有配置。工具定义、调用参数及结果计入预算。
- FAQ 只查问题列，关键词为当前用户问题中的连续片段，最多 3 条；不做同义词扩展。“邮费是多少”查不到是预期结果。
- 工单编号为 `T` 加 `sha256(f"{conversation_id}:{user_message_id}:{tool_call_id}").hexdigest()[:31]`；同次重试复用，不同用户消息不复用。
- 数据库提交最终回答后才能发送 done；仅正常 EOF、明确 stop、非空且未截断的最终回答可提交。失败流水保留审计但不能回放。
- 单 worker、会话占用锁；所有 SQLAlchemy Session 都是短生命周期，模型生成及 SSE 等待期间不持有事务。
- 使用中文注释、UTF-8；产品及 Git 分支/提交不使用章节前缀，保留用户指定的 `dev-notes/ch02.md` 和原 SQL 注释。
- 不加入 Agent Loop、RAG、向量库、登录系统、订单/商品/物流表。模型与协议保持既定选型，实测不兼容时报告证据并询问用户。

## Review Focus

1. 上游在不同轮次复用同一个 tool_call_id：新用户消息必须创建新工单（任务 3）。
2. 工单已提交但工具结果超时：重试仍只有一张工单，会话状态与工单一致（任务 3）。
3. 大于 2^53 的会话 ID：往返必须保持字符串；越界或旧 UUID 在模型请求前拒绝（任务 2、5）。
4. 孤立 tool、坏 JSON 或断开的流水夹在历史中：排除坏轮次，后续完整轮次仍可恢复（任务 2）。
5. 状态帧后取消、提交失败或 done 发送失败：资源释放，失败不能伪装成功，已提交事实不回滚（任务 5）。

---

## 执行准备与文件边界

- [ ] 用户审阅本计划后，按 using-git-worktrees 创建隔离工作区：先检查附着工作树，再优先使用原生工具以 master 为起点；必要时回退到 `.worktrees/tool-calling`，分支 `feat/tool-calling`。不改动旧运行服务。
- [ ] 核对隔离区 HEAD 与工作状态，运行已有 `uv sync --locked`、`uv run pytest -q`，记录基线；失败先诊断，不把旧失败归入新功能。
- [ ] 主代理将现有本地 .env 复制到隔离区的忽略路径，仅补缺失的 MySQL 配置；不打印密钥，不把真实配置放入提交。
- [ ] 每个后端任务由新实现子代理执行，规格与代码评审通过后主代理即时追加四项过程记录，再提交该任务的明确文件。页面任务不派代码评审，不套 TDD。

文件职责：`app/db/` 管连接及 ORM；`app/repositories/` 管短事务；`app/tools/` 管工具与执行；`app/core/tool_history.py` 管完整轮次和预算；`app/core/tool_chat.py` 管单轮流程；`app/api/streaming.py` 管 SSE/取消生命周期。保留旧文本预算与提取功能，避免无关重构。

### Task 1: 启动 MySQL 并核对权威四表

**Files:** 创建 `compose.yaml`、`sql/seed.sql`、`app/db/__init__.py`、`app/db/models.py`、`app/db/session.py`；修改 `app/config.py`、`.env.example`、`pyproject.toml`、`uv.lock`。测试 `tests/conftest.py`、`tests/test_db_config.py`、`tests/test_db_mapping.py`、`tests/integration/test_mysql_schema.py`；`sql/schema.sql` 只读。

**Interfaces:** `Settings.database_url -> sqlalchemy.engine.URL`；`Database(url: URL)` 提供 `session() -> AsyncSession`、`async dispose() -> None`；模型 `Conversation`、`Message`、`FAQ`、`Ticket`。测试注册 `--run-mysql` 与 `mysql_database` fixture：只接独立 customer_service_test 库，明确请求集成测试却未就绪时失败，不能跳过后宣称通过。

- [x] **写失败测试：** 在 `test_db_defaults_and_secret_url` 中核对：

```python
settings = fake_settings(mysql_password='a@:/b', mysql_root_password='root-test')
assert settings.mysql_host == '127.0.0.1'
assert settings.mysql_port == 3307
assert settings.database_url.drivername == 'mysql+aiomysql'
assert settings.database_url.password == 'a@:/b'
assert settings.tool_input_token_budget == 8000
assert settings.tool_timeout_seconds == 5
assert settings.tool_max_retries == 1
assert 'a@:/b' not in repr(settings)
```

  上例消费已有 `tests.fakes.fake_settings`，保留模型测试配置。`test_mysql_schema_matches_supplied_ddl` 从 information_schema 核对四表集合、UNSIGNED 主键、两个外键、中文 ENUM、JSON、索引、默认/更新时间、InnoDB/utf8mb4；`test_seed_is_complete_and_postage_misses` 检查四表种子和 FAQ 问题不含“邮费”。缺失实现的导入放在测试函数内，失败来自缺少功能，不能依赖收集错误。
- [x] **确认红灯：** `uv run pytest tests/test_db_config.py tests/test_db_mapping.py -q`，预期因缺少数据库配置/映射断言失败。
- [x] **实现配置与映射：** 新字段 MYSQL_HOST/PORT/DATABASE/USER/PASSWORD/ROOT_PASSWORD，默认库与用户 customer_service；密码 SecretStr，可在纯单元测试中缺省，获取数据库 URL 时必须提供。用 URL.create，枚举持久化中文值，映射全部用户字段。工具重试只允许 0/1，超时和预算为正。
- [x] **实现 Docker/种子：** mysql 服务本机 3307，mysql-test 在 test profile 使用本机 3308、独立库/卷。两者以 01-schema.sql、02-seed.sql 挂载用户 DDL/种子；增加健康检查。种子包含完整普通对话、关联工单、退货及“运费” FAQ，不能干扰新 demo-user 会话。
- [x] **验证：** `uv run pytest tests/test_db_config.py tests/test_db_mapping.py -q`；`docker compose --profile test up -d --wait --wait-timeout 120`；`uv run pytest tests/integration/test_mysql_schema.py --run-mysql -q`。预期全部通过，SQL 实际执行并核对；再次 up 不重置数据。Docker Engine 若未运行，先尝试启动本机 Docker Desktop，仍不能运行则保留证据并报告，不替换数据库。
- [x] **评审/留痕/提交：** 记录真实建表结果及结构评审，提交上述任务文件，`feat: add MySQL runtime and schema mappings`。

### Task 2: 持久化会话并恢复完整工具轮次

**Files:** 创建 `app/repositories/__init__.py`、`app/repositories/conversations.py`、`app/repositories/records.py`、`app/core/tool_history.py`、`app/core/conversation_locks.py`；测试 `tests/test_tool_history.py`、`tests/integration/test_conversation_repository.py`。

**Interfaces:** 消费任务 1 的 Database/models。`MessageRecord(id: int, role: str, content: str | None, tool_calls: list[dict] | None, tool_call_id: str | None)`；`ConversationRepository(database: Database)` 的异步方法 `create(user_id: str) -> str`、`require_open(conversation_id: str) -> None`、`append_message(conversation_id: str, message: BaseMessage) -> int`、`load_messages(conversation_id: str) -> list[MessageRecord]`。`completed_turns(rows: Sequence[MessageRecord]) -> list[list[BaseMessage]]`；`build_tool_messages(system: SystemMessage, turns: Sequence[Sequence[BaseMessage]], current: HumanMessage, budget: int, *, tool_schema: list[dict], current_tool_messages: Sequence[BaseMessage] = ()) -> list[BaseMessage]`。`ConversationLocks.acquire(conversation_id: str) -> Lease`，`Lease.release() -> None` 同步且可重复调用。

- [x] **写失败测试：** `test_complete_turns_skip_partial_and_orphan` 的固定输入为完整工具轮次、孤立结果、半轮次及之后完整文本轮次；断言 `assert len(completed_turns(rows)) == 2`，工具组的 `assert turn[2].tool_call_id == turn[1].tool_calls[0]['id']`。`test_budget_drops_whole_tool_turn` 断言旧申请/结果一起移除，当前用户、system 保留；`test_schema_and_result_count_toward_budget` 断言必需输入超过 8000 时抛预算异常。补坏 JSON/错 id/多结果/越界历史测试。
- [x] **确认红灯：** `uv run pytest tests/test_tool_history.py -q`，预期缺少完整工具历史功能而失败。
- [x] **实现仓储与回放：** 消息按 id 排序，assistant 调用持久化为 Chat Completions tool_calls JSON，tool 结果必须匹配。遇新 user 划分轮次，完整且合法才回放；跳过坏组，继续下一组。一次数据库操作一个短事务，保存 user 返回 message.id 供工单使用。预算延用现有保守计数策略，加入序列化 schema/申请/结果，只裁剪旧完整组；不存在/已结束及重复占用分别抛明确错误。
- [x] **验证：** `uv run pytest tests/test_tool_history.py -q`；`uv run pytest tests/integration/test_conversation_repository.py --run-mysql -q`。测试新仓储实例仍读到完整消息；插入 `9007199254740993` 会话后断言 `assert returned_id == '9007199254740993'`；已转人工仍可继续，已结束被拒绝。预期全通过。
- [x] **评审/留痕/提交：** `feat: persist conversations and replay complete tool turns`。

### Task 3: 五个业务工具、参数校验和有限重试

**Files:** 创建 `app/repositories/faq.py`、`app/repositories/tickets.py`、`app/tools/__init__.py`、`app/tools/types.py`、`app/tools/schemas.py`、`app/tools/business.py`、`app/tools/registry.py`、`app/tools/executor.py`；测试 `tests/test_business_tools.py`、`tests/test_tool_executor.py`、`tests/integration/test_business_repositories.py`。

**Interfaces:** `ToolContext(conversation_id: str, user_message_id: int, user_question: str)`、`ToolCall(id: str, name: str, args: dict)`、`ToolOutcome(content: dict, status: Literal['success','error'], attempts: int)`。`FAQRepository(database).async search(keyword: str, limit: int = 3) -> list[dict]`；`TicketRepository(database).async create(*, conversation_id: str, user_message_id: int, tool_call_id: str, description: str, ticket_type: str) -> dict`。`build_registry(faq: FAQRepository, tickets: TicketRepository, context: ToolContext) -> dict[str, BaseTool]`。`ToolExecutor(timeout_seconds: float = 5, max_retries: int = 1).async execute(call: ToolCall, registry: Mapping[str, BaseTool]) -> ToolOutcome`。

- [x] **写失败测试：** `test_timeout_retries_once` 的受控工具第一次 TimeoutError、第二次成功，`assert outcome.attempts == 2`；`test_invalid_args_do_not_execute` 断言 `assert calls == 0`。`test_ticket_retry_is_same_but_next_user_message_is_new` 断言 `assert first['ticket_no'] == retry['ticket_no']`、`assert next_turn['ticket_no'] != first['ticket_no']`，两轮故意使用同一 tool_call_id。
  `test_ticket_commit_then_timeout_keeps_one_row` 在实际仓储提交后注入一次超时，再执行重试，断言 `assert ticket_count == 1`、`assert conversation.status == '已转人工'`；取消时 `assert calls == 1`，不再发起尝试。
- [x] **确认红灯：** `uv run pytest tests/test_business_tools.py tests/test_tool_executor.py -q`，预期因缺少注册工具/执行器失败。
- [x] **实现业务及注册：** 五个名称固定；@tool + args_schema 禁止额外参数。订单/商品号 1..64 字符，keyword 1..128，description 1..2000，ticket_type 仅售后/投诉/咨询。三个 mock 返回原参数、随机数据与 `mock: true`。FAQ 使用 question.contains(keyword, autoescape=True) 与绑定参数，keyword 不在原问题中则拒绝；返回 `{'found': bool, 'matches': list[dict]}`，无命中不算异常。工单返回包含 ticket_no、status 的对象；错误结果为 `{'error': {'code': str, 'message': str}}`。上下文通过每请求注册表闭包注入，不暴露模型可填写的会话/消息 id。
- [x] **实现工单与执行器：** 按全局摘要算法生成工单号；插入工单与转人工同事务，重试先核对已有行，主键冲突后读取并校验业务字段，不能覆盖。create_ticket 用 `Annotated[str, InjectedToolCallId]` 接收隐藏的调用 id，加入其 args_schema；执行器拒绝模型提供该隐藏参数，先校验业务参数，再用完整 `{'type':'tool_call','name':call.name,'args':dict(call.args),'id':call.id}` 调用 BaseTool.ainvoke，使 LangChain 注入 id；每次尝试拷贝参数，避免注入修改重试输入。ToolMessage 的 JSON 内容和状态归一为 ToolOutcome，状态只表业务执行成功/失败。只重试临时超时/连接故障，取消向上传播；固定安全错误码/说明，不回灌堆栈、SQL、凭据。
- [x] **验证：** 上述单元测试及 `uv run pytest tests/integration/test_business_repositories.py --run-mysql -q`。实际 LIKE 验证退货命中、邮费不命中、`%`/`_` 按字面查找，工单仅写本会话。预期全通过。
- [x] **评审/留痕/提交：** `feat: add validated business tools and bounded execution`。

### Task 4: 单次选工具与真实流式收敛

**Files:** 创建 `app/core/tool_chat.py`、`tests/tool_fakes.py`、`tests/test_tool_chat_service.py`、`tests/test_tool_llm_payload.py`、`evals/tool_cases.jsonl`；修改 `app/core/prompts.py`、`app/core/chat.py`（共享事件类型）、`app/core/errors.py`（必要的领域错误）。

**Interfaces:** 消费任务 2/3。`StreamEvent(event: Literal['status','delta','done','error'], data: dict[str, Any])`；`PreparedToolChat` 保存 conversation_id、lease、user_message_id、模型消息和当前迭代器。`ToolChatService(model, repository: ConversationRepository, registry_factory: Callable[[ToolContext], Mapping[str, BaseTool]], locks: ConversationLocks, settings: Settings, *, executor: ToolExecutor | None = None)` 提供 `async prepare(conversation_id: str, message: str) -> PreparedToolChat`、`stream(prepared: PreparedToolChat) -> AsyncIterator[StreamEvent]`、`release(prepared: PreparedToolChat) -> None`。受控 `ToolModel` 实现 bind_tools、ainvoke、astream 并记录调用；测试中注入受控执行器，仓储与事件采集将完成顺序记录到 trace。

- [ ] **写失败测试：** `test_one_call_reinjects_matching_tool_and_streams`：

```python
assert model.selection_requests == 1
assert executor.calls == 1
assert model.final_stream_requests == 1
assert final_input[-1].tool_call_id == selected.tool_calls[0]['id']
assert events[-1].event == 'done'
assert trace.index('commit_final') < trace.index('done')
```

  `test_no_tool_still_uses_final_stream` 断言 executor.calls 为 0、final_stream_requests 为 1；`test_multiple_calls_execute_nothing` 断言 executor.calls 为 0、末帧 error。补无效/未知名称、长 id、invalid_tool_calls、选择被截断、最终再次申请、空回复、缺 stop、预算超限和数据库提交失败测试，均不得保存成功最终回答。
- [ ] **确认红灯：** `uv run pytest tests/test_tool_chat_service.py tests/test_tool_llm_payload.py -q`，预期新服务缺失而失败。
- [ ] **实现流程：** prepare 获取锁、读历史、存 user 得到 message.id；失败释放锁。stream 发 selecting，bind_tools 一次（tool_choice=auto、parallel_tool_calls=False），检查申请数量/结构；无申请只接受 stop，有申请只接受 tool_calls/stop，调用 id 非空且最长 64。合法单次申请落 assistant 行，执行并落 tool 行，发 tool_running/tool_completed。最终使用未绑定工具的原模型 astream，发 answering/delta，预算重新核对。参数错误可作为合法调用的错误结果回灌；畸形或多个申请直接 error，不选其中一个。完成校验通过后 await 保存最终回答，再 done。
- [ ] **验证：** 上述测试使用受控模型/数据库替身；HTTP mock 检查第一次请求包含五个工具，第二次无 tools 且申请/结果匹配，原模型工厂仍 max_retries=0、Chat Completions。预期全部通过，不发送真实请求。
- [ ] **Prompt/数据样例验证：** 此部分按用户要求用标注评估替代 TDD。客服 Prompt 依据结果作答并标明 mock，禁止伪造政策/执行退款。JSONL 固定八类：物流、订单、商品、退货 FAQ 命中、邮费 FAQ 预期未命中、人工工单、普通问候无工具、缺订单号先澄清无工具；标注预期工具/关键参数/命中状态。先校验样例结构和受控回灌回答，真实模型质量留任务 7。
- [ ] **评审/留痕/提交：** `feat: add single-call tool chat orchestration`；此时旧入口未切换，现有服务仍可运行。

### Task 5: 会话 API 与 SSE 生命周期接入

**Files:** 创建 `app/api/conversations.py`、`app/schemas/conversation.py`、`tests/test_conversation_api.py`；修改 `app/main.py`、`app/api/chat.py`、`app/api/streaming.py`、`app/schemas/chat.py`；适配 `tests/fakes.py`、`tests/test_schemas.py`、`tests/test_chat_api.py`、`tests/test_stream_lifecycle.py`、`tests/test_network_stream.py`、`tests/test_upstream_completion.py`、`tests/test_extract_api.py`、`tests/test_eval_http.py`。

**Interfaces:** `create_app(settings: Settings | None = None, *, model=None, database: Database | None = None, repository: ConversationRepository | None = None) -> FastAPI`；注入资源由调用者管理，应用自建资源在 lifespan 关闭。`POST /api/conversations` 请求 user_id 1..64 字符，响应 conversation_id 字符串；`POST /api/chat` 请求 conversation_id/message。ManagedChatResponse 消费任务 4 服务，只有 done/error 终止。

- [ ] **写失败测试：** `test_status_frames_do_not_end_chat` 断言 `assert names == ['status', 'status', 'status', 'status', 'delta', 'done']`，done 的 `assert data['conversation_id'] == '9007199254740993'`。`test_invalid_identity_before_model` 参数化 UUID、数字 JSON、布尔、`'0'`、`'01'`、`'18446744073709551616'`：`assert response.status_code == 422`、`assert model.requests == 0`。不存在会话 404，已结束/同会话并发 409。
  生命周期测试覆盖 ASGI 2.3/2.4：状态帧后断开释放锁、取消不重试；提交异常只有 error、没有 done；done 发送失败时完整回答已提交且不回滚；迭代器与资源关闭一次。提取接口仍返回既有结构。
- [ ] **确认红灯：** `uv run pytest tests/test_conversation_api.py tests/test_chat_api.py tests/test_stream_lifecycle.py -q`，预期因旧身份/终止/提交契约而失败。
- [ ] **实现入口：** await prepare 后返回 SSE；绑定会话/领域异常到明确 HTTP 错误，不泄露配置。删除响应层旧同步 commit 调用，提交归服务负责；保留既有取消/迭代器关闭保护，status 非终止，编码数据允许工具状态字段。factory 支持模型和仓储测试注入，不要求单元测试连接真实 MySQL；health 不探测模型/数据库，extract 不改变。
- [ ] **验证：** 运行上述目标测试及 `uv run pytest -q`，预期离线全通过。旧测试按照新契约改写而保留原验证意图，不能整批删除流式异常测试；旧 UUID 与“发 done 再内存 commit”的断言明确替换。
- [ ] **评审/留痕/提交：** `feat: integrate persistent tool chat with FastAPI SSE`。

### Task 6: Vibe Coding 改造聊天页

**Files:** 修改 `app/static/index.html`、`app/static/chat.js`、`app/static/chat.css`；不增加前端框架。

**Interfaces:** 消费任务 5 的会话创建、conversation_id 和 status/delta/done/error；tool_running/tool_completed 含 tool_name、tool_call_id、status。

- [ ] **直接实现页面：** 首次发送前创建 demo-user 会话，保留服务返回的字符串身份；新对话清空身份，禁止重复发送。气泡内分开工具徽章容器与回答文本容器，delta 不覆盖徽章；状态更新徽章但不显示模型推理。所有用户/结果文本用 textContent，保留停止、错误恢复、多轮与自动滚动。
- [ ] **浏览器验证：** 在独立测试端口用真实 ASGI 和受控 ToolModel 演示物流徽章/逐字流式、FAQ 命中/邮费未命中、多轮及新会话；检查执行中停止、错误后重发、文本含 HTML 时按字面显示、默认窗口及窄屏。不改变现有端口服务。真实上游浏览器验收在任务 7。
- [ ] **即时留痕/提交：** 按用户例外不做 brainstorm/TDD/code review，记录观察与返工，`feat: show tool traces in customer chat bubbles`。

### Task 7: 实测评估、回归与交付

**Files:** 创建 `evals/evaluate_tools.py`、`tests/test_tool_evaluation.py`、`docs/validation/tool-calling-results.md`；修改 `evals/smoke.py`、`tests/test_smoke.py`、`README.md`，逐阶段追加 `dev-notes/ch02.md`。

**Interfaces:** `ToolEvaluationReport(attempted: int, not_attempted: int, cases: list[dict])`；`async evaluate_tools(client: httpx.AsyncClient, base_url: str, cases: Sequence[dict], *, repository: ConversationRepository) -> ToolEvaluationReport`；`python -m evals.evaluate_tools --base-url http://127.0.0.1:8000 --cases evals/tool_cases.jsonl --output .cache/tool-evaluation.json`。评估通过应用 API 而非绕过工具链；本地 CLI 从当前配置建立只读审计仓储，每个新会话结束后读取消息流水，确认实际参数、ToolMessage 的 found/matches 和工单号，不添加调试接口。报告记录预期/实际工具、参数、命中、最终回答与 SSE 完成状态，不输出凭据；保留需要人工判断的回答质量。更新原 smoke 先创建会话再两轮聊天和一次提取；分别记录 HTTP 请求与模型请求，聊天总期限 150 秒、提取保留 75 秒，不新增客户端自动重试。

- [ ] **评估代码 TDD：** `test_compatibility_failure_stops_remaining_cases` 断言 `assert report.attempted == 1`、`assert report.not_attempted == 7`；`test_expected_faq_miss_is_success` 断言 `assert case['passed'] is True`；`test_incomplete_stream_is_not_pass` 断言 `assert case['passed'] is False`。另覆盖坏 JSON、错身份、多个工具、乱码、error 与正常 done 的识别。先运行 `uv run pytest tests/test_tool_evaluation.py tests/test_smoke.py -q` 确认红灯，再实现并跑绿灯。
- [ ] **最终离线/MySQL 验证：** `uv run pytest -q`、`uv run pytest tests/integration --run-mysql -q`。仅重启独立 mysql-test 服务及新应用实例，确认数据库历史仍接续、工单事实保留；不触及其他数据库/旧服务。记录命令、版本、通过数量与未执行部分。
- [ ] **真实上游能力闸门：** 启动本步 MySQL/后端，沿用当前 glm-5.3-flash 与标准端点，先跑一个物流样例。模型/协议/预算不兼容时停止后续真实请求、保存脱敏证据并询问用户，不自动换模型。通过后跑八类样例；Prompt/种子作为数据评估，不伪称单元测试，改动后做一次完整复验，记录实际请求而不是理论数量。
- [ ] **真实浏览器/curl 验收：** 用户三个原问题逐一演示；再验人工工单、重启接续和第一步 extract。回答需与实际工具结果一致，邮费漏召回作为预期结果写入报告；没有完成的人工项写待验收，不能虚构通过。
- [ ] **交付文档：** README 使用“第二步”，给出 Docker 初始化/既有卷维护、启动、创建会话、curl -N 聊天、提取及评估命令，解释 mock、单 worker、最终提交边界及 FAQ 漏召回；SQL 原生执行证据与真实模型结果进入验证报告。
- [ ] **评审/留痕/提交：** 评估代码任务评审后执行整个后端分支评审，页面按用户例外排除该代码评审。解决有效意见后重新运行对应检查，记录 review/finish，`test: validate tool calling and document delivery`。全部证据通过再使用 finishing-a-development-branch 让用户选择集成；不擅自推送或重写历史。

## 计划自审

- 规格覆盖：四表/Docker/种子在任务 1；持久化与预算在 2；五工具及错误重试在 3；单轮/Prompt 在 4；现有聊天/SSE/提取回归在 5；工具徽章在 6；三个验收及交付在 7。
- 接口一致：prepare 为异步；模型 stream 与 SSE 事件统一；message.id 进入 ToolContext/工单摘要；身份全程字符串；回灌与数据库 tool_call_id 匹配。
- 五项 Review Focus 均有归属和断言；不依赖 Python/JavaScript 数字隐式转换，不以重复 tool_call_id 当跨轮次幂等键。
- 后端代码 TDD、Prompt/数据样例评估、页面 Vibe Coding 三项均按用户要求区分；选择 Subagent-Driven 保留，不再次询问执行方式。
- 原建表文件不修改；不把 ORM 映射测试当实际 SQL 执行，不把模型替身通过当真实上游验收。
- 自审发现并修正：工单摘要加入已存在的 user 消息主键，修复跨轮 tool_call_id 复用；最终数据库提交放在服务中，避免旧同步响应提交契约冲突；工具调用 id 明确由 LangChain 注入，重试复制输入；验收通过 API 运行再读取数据库流水核对真实参数和命中。

状态：用户已回复“确认啊，赶紧开始实现”，计划审阅通过；进入 Subagent-Driven 实施阶段。
