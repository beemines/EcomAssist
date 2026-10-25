# step07 · 官方接口核对记录

日期：2026-10-17。用户已批准本步骤以官方文档和锁定版本源码替代当前不可调用的Context7。以下是设计期核对，未修改产品实现，也不是测试报告。

## LangGraph：消息增量与持久化

- [add_messages 官方定义](https://reference.langchain.com/python/langgraph/graph/message/add_messages)：接收left/right，按消息ID合并，新ID追加、相同ID更新。引用的在线版本1.2.15与项目锁定版本相同。
- 本地`.venv/Lib/site-packages/langgraph/graph/message.py:64`签名：`add_messages(left: Messages, right: Messages, *, format: Literal["langchain-openai"] | None = None) -> Messages`。
- [Graph API 消息State](https://docs.langchain.com/oss/python/langgraph/graph-api)：State字段通过reducer处理节点增量。原始历史必须保留稳定SQL消息ID，不能把裁剪视图写回messages，也不能在每个节点重复回传全量历史。
- [Persistence](https://docs.langchain.com/oss/python/langgraph/persistence)：继续沿用thread/checkpointer，不新增跨会话记忆。现有SQLite saver锁定3.1.2，安装源码`aget_tuple(config)`、`aput(config, checkpoint, metadata, new_versions)`、`aput_writes(config, writes, task_id, task_path="")`与当前项目接线核对；后台摘要不并发篡改活跃图消息。
- [官方 Overwrite 用法](https://docs.langchain.com/oss/python/langgraph/use-graph-api#bypass-reducers-with-overwrite)：可绕过 reducer 直接设置完整值；同一 super-step 只允许一个覆盖写者。安装版本1.2.15的`langgraph/types.py:1050`含`Overwrite(value: Any)`。仅为旧checkpoint缺失较早SQL消息时建立完整、按SQL ID排序的初始化快照使用，不用于层级压缩或常规节点。单独的reference页抓取因content-type失败，实际依据为上述官方Graph API页及安装源码，未把失败页当作成功读取。

## LangChain：trim_messages

- [官方接口](https://reference.langchain.com/python/langchain-core/messages/utils/trim_messages)：支持自定义token_counter、strategy、allow_partial、start_on/end_on、include_system。在线页标v1.6.2，项目langchain-core锁定1.6.6，不能只按网页版本猜测。
- 本地`.venv/Lib/site-packages/langchain_core/messages/utils.py:1146`实参包括`messages, *, max_tokens, token_counter, strategy="last", allow_partial=False, end_on=None, start_on=None, include_system=False, text_splitter=None`。
- 拟在独立模型视图使用自定义校准计数器，并校验完整轮次/工具配对；最近层不允许截半条。trim_messages不用于删除checkpoint或SQL中的原始历史。

## SQLAlchemy：并发异步事务

- [AsyncSession 并发任务约束](https://docs.sqlalchemy.org/en/20/orm/extensions/asyncio.html#using-asyncsession-with-concurrent-tasks)：每个并发任务独立Session。项目锁定2.0.54；计划阶段重查官方2.0页已标2.0.55，实际用法仍核对本地2.0.54，不跟随网站版本自动升级。
- 摘要生成不持有聊天事务或数据库行锁；保存分段与推进覆盖边界放在独立短事务，并核对生成时的边界快照。具体锁/CAS接口在确定实施方案后继续核对，不把此处概述当成已写代码。
- 已补查[SQLAlchemy官方DML说明](https://docs.sqlalchemy.org/en/20/core/dml.html)，用于短事务内更新边界；实施具体`select(...).with_for_update()`及条件更新前仍须按实际使用的方法核对锁定版本签名。

## 计划阶段补充核对

- [FOR UPDATE官方接口](https://docs.sqlalchemy.org/en/20/core/selectable.html#sqlalchemy.sql.expression.Select.with_for_update)：当前网页为2.0.55；本地2.0.54的`sql/selectable.py:4009`签名为`with_for_update(self, *, nowait=False, read=False, of=None, skip_locked=False, key_share=False)`。计划只用无参数行锁，不把其他数据库的NOWAIT行为套到MySQL。
- [MySQL8.4隐式提交](https://dev.mysql.com/doc/refman/8.4/en/implicit-commit.html)：项目compose同为mysql:8.4；ALTER TABLE等DDL会隐式提交，迁移必须识别部分完成状态，不宣称包在SQLAlchemy事务里就能整体回滚。
- [CompiledStateGraph官方成员列表](https://reference.langchain.com/python/langgraph/graph/state/CompiledStateGraph)确认历史读取继承`aget_state_history`；锁定1.2.15的`pregel/main.py:1554`为`aget_state_history(config, *, filter=None, before=None, limit=None) -> AsyncIterator[StateSnapshot]`，SQLite saver3.1.2的`aio.py:448`为`alist(config, *, filter=None, before=None, limit=None) -> AsyncIterator[CheckpointTuple]`。GET历史装饰器使用真实方法，不能编造`alist_state_history`。旧graphs/锚点地址及单方法页抓取失败已区分，不能把这些失败页计为签名核对成功。
- 本次工具元数据重新检查仍无Context7，继续使用本步骤已批准的官方资料＋锁定源码方式。真实费用HTTP钩子的用法在任务10实现前另核对HTTPX0.28.1官方事件钩子和安装签名。

## 任务1实施前：Pydantic显式配置与别名

- [BaseModel官方属性](https://pydantic.dev/docs/validation/latest/api/pydantic/base_model/)及[Settings环境变量命名](https://pydantic.dev/docs/validation/latest/concepts/pydantic_settings/)已先读取；旧docs.pydantic.dev地址重定向到该官方站点，不以站点latest标签替代本地版本核对。
- 本地pydantic2.13.5的`main.py:307`：`model_fields_set(self) -> set[str]`返回显式赋值字段（非默认填充）；pydantic-settings2.15.0的`main.py:132/193`确认现有BaseSettings构造入口。新旧工具步数别名以及“缺省推导/显式费用上限”需要区别默认值与显式环境值，不能仅比较是否等于旧默认数值。具体新增validator仍需实现者按实际使用接口核对，不借此改动未接线的旧消费者。

## FastAPI：后台任务生命周期

- [lifespan 官方说明](https://fastapi.tiangolo.com/advanced/events/)：应用启动/关闭资源在同一生命周期内管理，项目已有该接线。拟用它拥有后台摘要任务及关闭清理，避免请求取消或应用退出留下无主任务。
- [BackgroundTasks](https://fastapi.tiangolo.com/tutorial/background-tasks/)在响应返回后运行。对于需要显式追踪并发、关闭和重启的摘要任务，设计优先采用应用拥有的异步管理器；不引入Celery、Redis或其他新组件。

## 当前模型窗口

官方智谱域名下精确搜索`GLM-5.3-Flash`未得到可用窗口规格。这不证明该模型不支持现有调用，也不作为更换模型的理由。窗口必须由部署配置明确给出，不能在设计文档中虚构已验证的供应商上限。既有密钥与模型保持，任何窗口默认值须在设计阶段交代依据。

## 任务2实施：独立Session、唯一键冲突与MySQL默认值

- 实施前重读[SQLAlchemy异步并发约束](https://docs.sqlalchemy.org/en/20/orm/extensions/asyncio.html#using-asyncsession-with-concurrent-tasks)、[IntegrityError与原始DBAPI异常](https://docs.sqlalchemy.org/en/20/core/exceptions.html#sqlalchemy.exc.IntegrityError)和[MySQL8.4隐式提交](https://dev.mysql.com/doc/refman/8.4/en/implicit-commit.html)。网页SQLAlchemy为2.0.55，实际使用锁定2.0.54，不升级依赖。
- 锁定源码`sqlalchemy/sql/selectable.py:4009`再次确认无参`with_for_update()`；`ext/asyncio/session.py:779/940`确认`await flush()`与`async with session.begin()`；`exc.py:550`附近确认DBAPI异常保存在`orig`；PyMySQL1.2.3的`constants/ER.py:64`定义`DUP_ENTRY=1062`。只在上下文退出、事务回滚后把1062转成None竞争结果，其他完整性错误继续抛出。
- MySQL服务器生成的`created_at`在flush后可能仍未加载，不能同步属性访问触发异步惰性IO。真实3308测试复现MissingGreenlet后，改用已有显式异步SELECT读取整段集合，再构造不可变返回值；不依赖MySQL未提供的INSERT RETURNING，也不加入新Session共享。
- MySQL把ORM编译的INTEGER规范为INT；锁定`dialects/mysql/base.py:2470`确认INTEGER编译规则。用户SQL中seq仍原样INT、有符号，映射只做该同义类型比较，不能误改成INT UNSIGNED。
- 两个用户DDL原文由控制者补入本计划scratch/task-2-user-ddl.md，实施文件`sql/ch07.sql`与`sql/ch07-layers.sql`保留其完整字段、中文注释、SET NAMES、索引、顺序及无FK设计。迁移契约从这些SQL读取，先核验全部已有结构再执行缺失项；不宣称事务能回滚已提交DDL。

## 任务3实施：完整轮次候选和出站防御性副本

- 实施前重新读取[LangChain官方短期记忆说明](https://docs.langchain.com/oss/python/langchain/short-term-memory#trim-messages)，并核对锁定langchain-core1.6.6的`messages/utils.py:1146`完整签名。使用`trim_messages(messages, max_tokens=..., token_counter=estimate_payload, strategy='last', allow_partial=False, start_on='human')`，随后按共享完整轮次扫描器对齐SQL边界；候选不替换持久化历史，也不承担工具配对正确性的证明。
- 单独`trim_messages`参考页本次抓取返回不支持的text/markdown类型，未当作成功重读；官方短期记忆页及锁定源码均读取成功，已有设计期参考记录仍保留。
- 读取官方[message_to_dict](https://reference.langchain.com/python/langchain-core/messages/base/message_to_dict)及[messages模块](https://reference.langchain.com/python/langchain-core/messages)，核对锁定1.6.6的`messages/base.py`和`messages/utils.py`：`message_to_dict(message: BaseMessage) -> dict[str, Any]`生成type/data字典，`messages_from_dict(messages: Sequence[dict[str, Any]]) -> list[BaseMessage]`重建消息。模型包内部持有JSON文本，取messages/tools时生成新副本，避免后台或调用方修改嵌套工具参数。
- 冻结预算的phases含MappingProxyType，JSON边界沿用统一估算器的普通JSON副本转换，不调用`asdict(ContextBudget)`或对该代理deepcopy。摘要G计实际注入段的seq、字符串来源ID、正文及消息包装；最终整包另计同一user附件的其他字段、审计JSON、当前工具申请/结果和工具schema。

## 任务4实施：完整State、SQL增量与旧根恢复

- 实施前读取[官方Graph API](https://docs.langchain.com/oss/python/langgraph/graph-api)的消息reducer和Overwrite章节、[子图调用转换](https://docs.langchain.com/oss/python/langgraph/use-subgraphs)及[持久化](https://docs.langchain.com/oss/python/langgraph/persistence)。单独Overwrite和AsyncSqliteSaver reference链接本次抓取失败，未把失败页面作为成功读取；实现同时核对以下锁定源码。
- 实际安装版本为LangGraph **1.2.15**、langgraph-checkpoint **4.3.0**、langgraph-checkpoint-sqlite **3.1.2**。1.2.15是图包版本，不是SQLite saver包版本。`graph/message.py:64`的`add_messages(left, right, *, format=None)`按ID合并，已有ID替换、缺ID会生成ID；业务消息必须先取得SQL ID，避免匿名模型ID混入持久化。
- `types.py:1050`的`Overwrite(value: Any)`由`channels/binop.py`识别并绕过reducer，同一super-step不能多个Overwrite。仅完整SQL首次引入/旧根规范化使用，正常节点与语义裁剪均不发Overwrite，不直接修改已有completed根。
- 子图适配核对`pregel/main.py`实际`ainvoke(input, config=None, *, context=None, stream_mode='values', ..., durability=None)`；显式传入父节点RunnableConfig与runtime.context，保留callbacks、namespace和stream上下文。其默认durability从config的CONFIG_KEY_DURABILITY继承；父服务仍使用sync。真实父子图custom/updates回归确认父agent只发新增SQL消息，子图工具增量和正文仍可见。
- sqlite/aio.py:324/367/524核对官方表、aget_tuple和aput：checkpoint以thread_id/namespace/checkpoint_id定位，序列化值写入checkpoint BLOB；新轮沿当前thread产生新ID，不调用update_state改旧根。真实pytest tmp SQLite关闭重开两次、旧root checkpoint/metadata字节相等、原locator历史模式验证共同覆盖该约束。

## 任务5实施：严格摘要、原文窗口与有界后台任务

- 使用[Python 3.13 asyncio任务文档](https://docs.python.org/3.13/library/asyncio-task.html#asyncio.wait)核对：`wait(tasks, timeout=5)`返回done/pending，超时不自动取消；管理器随后逐个cancel并gather等待清理。任务保存强引用；CancelledError清理后重新抛出。查询的是3.13兼容接口，不使用新版3.15新增API。
- [官方ChatOpenAI集成文档](https://docs.langchain.com/oss/python/integrations/chat/openai)用于核对现有客户端与结构化输出能力；具体json_mode以锁定langchain-openai 1.6.7的`chat_models/base.py:2804`为准，其绑定`response_format={"type":"json_object"}`。本任务直接取得原始AIMessage，在本地拒绝重复键、非唯一content字段、非字符串、非stop、工具调用、refusal与超长输出，不使用宽松Markdown JSON解析。
- 锁定源码`base.py:1470`将`max_retries`传入实际SDK客户端，`base.py:2018`合并绑定参数并构造Chat Completions消息。沿用`create_model`的零重试；SummaryGenerator拒绝重试配置非零的ChatOpenAI/根异步客户端。`model_with_output_budget`只复制配置、共享资源所有权，摘要覆盖输出预留为512，支持两个已存在的token-limit字段。离线httpx MockTransport捕获真实请求，500只请求一次；没有请求真实GLM。
- `summary_messages(batch)`只序列化冻结SQL原文行与字符串范围ID，完整system/user及JSON包装按同一`estimate_payload`计数，另加512与部署安全余量。管理器按共享`completed_boundaries`选连续完整轮次，不把旧摘要或层2截断文本喂给生成器；过多实体用完整轮次拆批。单轮不能容纳就失败，不靠缩短原话通过预算。
- 最小新增`ContextRepository.list_downgraded(*, after_id=0, limit=100)`经控制者批准；只筛L非NULL且L>coalesce(S,0)，会话ID升序keyset分页，页大小限制1..100。临时SQLite实测NULL S、已覆盖/未降级排除、跨页顺序；没有改既有append/CAS锁区或应用数据库。
- `SummaryManager(repository, generator, *, budget_provider, event_logger=None)`保留指定位置参数。event_logger同步接收`(event_name, fields)`，可接Task6/10的ContextLogger.event；字段只有任务/会话ID、段号、SQL范围、S/目标L、阈值/用量、时间/耗时、运行/等待数及固定原因码，不含客户端、密钥或异常正文。notify同步仅登记/入队；`summary_notify`范围未知。首个短SQL读取冻结L后才发带真实范围的`summary_trigger`；每子段start/done带真实段范围。队列中的后续任务仍在自己的首次读取时冻结L。单段失败保留以前已提交段，失败段不推进S，不自动重试。
- `SummaryRequest`是冻结内存记录，不是持久任务表。startup每个候选重取budget_provider当前预算，按真实层2投影重算阈值，按同一2运行/8等待规则调度而不等待上游；关闭丢弃等待项、给运行项5秒，再取消并等清理。仅一个应用所有者创建管理器；Workflow/lifespan接线留Task6。
- 12项人工标注样例见`tests/fixtures/context/summary_cases.json`；离线协议/词法与标注事实断言均通过，反例均拒绝。它们不是模型生成质量报告，真实prompt检查留Task11。词法实体/否定/动作守卫只覆盖已知形式，不能证明任意自然语言的完整忠实度。

## Task6：实际消息日志和暂停快照

- 核对锁定`langchain_openai/chat_models/base.py:_convert_message_to_dict`及实际Chat Completions出站调用点。专用日志复用这个序列化器，包含原生tool_calls参数字符串、空申请content=null及tool_call_id；不序列化模型/SDK/请求头。MockTransport捕获真实请求，逐字段对比日志messages与HTTP messages，失败仍仅一次请求，不访问上游。
- 核对锁定`langgraph/types.py:Command`的`update`与`resume`及`pregel/main.py:_aprepare_state_snapshot`。恢复以Command更新纯JSON上下文诊断，无messages更新，也不调用update_state。官方读取会把NULL_TASK_ID pending writes叠到旧暂停根的展示状态（显式checkpoint_id也如此）；原SQLite checkpoint/metadata blob及其raw messages不变，不能把展示投影视作原根字节被改写。实际SQLite关闭/重开覆盖这一区别。
- `ContextCoordinator.prepare`只做边界CAS和不可变视图构造；摘要notify保持同步且不等待生成。已有L>S积压导致当前H容量失败时仍通知管理器，避免每轮失败阻止后续恢复。
- Task6采用显式`context_budget_provider(registry)`；Task7拥有唯一真实阶段工厂、默认激活与Agent/扩写/充分性/query planner调用包及日志。Task6日志阶段为history/understanding/classification/summary；摘要机器事件使用`summary_notify/trigger/start/done/skipped/failed`对应完整snake_case名，层降级为`context_downgrade`，不能用带空格的计划叙述进行字符串验收。
- 理解/分类实际共享冻结段与层，来源校验仅取注入段原SQL范围内的用户表达或成功配对读取，与可见实体取完整token交集。有限身份/位置/手机号反例不是任意自然语言忠实度证明；否定和当前诉求提示仍需Task11真实有限样例验收。

## Task7: stable native schema, nullable required fields and actual boundary capture

- Consulted official [ChatOpenAI integration](https://docs.langchain.com/oss/python/integrations/chat/openai) and [Pydantic fields](https://pydantic.dev/docs/validation/latest/concepts/fields/) before implementing concrete bindings. Locked langchain-openai1.6.7 `chat_models/base.py:480` uses `message.name or message.additional_kwargs.get("name")`; estimator now matches even empty-name cases. `bind_tools` around2540 normalizes dicts with `convert_to_openai_tool`; stable OpenAI tool dictionaries are passed unchanged, `tool_choice=auto`, `parallel_tool_calls=False`, while decision-only JSON response format remains in extra_body.
- Locked pydantic2.13.5 `json_schema.py:field_is_required` derives validation required fields from the absence of a default. Unified nullable fields deliberately have no default; both are required in actual captured native tool schemas. Strict local JSON/native validation retains route semantics.
- Reused locked `_convert_message_to_dict` through ContextLogger at each actual invoke/stream boundary. No guessed node body, HTTP headers or client repr. Offline MockTransport samples compare messages and tools before response, including failed calls; capture compares non-stream input usage only, unknown remains null and calibrated remains false. No stream_usage override or live calibration in Task7.

## Task8: owned history reads and durable original root metadata
- Read official [LangGraph persistence](https://docs.langchain.com/oss/python/langgraph/persistence), [SQLAlchemy SELECT tutorial](https://docs.sqlalchemy.org/en/20/tutorial/data_select.html), [FastAPI Query validation](https://fastapi.tiangolo.com/tutorial/query-params-str-validations/) and [Python3.13 aclosing](https://docs.python.org/3.13/library/contextlib.html#contextlib.aclosing). Context7 remains unavailable; approved fallback used before implementation.
- Pinned source checked: langgraph-checkpoint-sqlite3.1.2 sqlite/aio.py:448 `alist(config, *, filter=None, before=None, limit=None)` yields raw CheckpointTuple values newest-first, namespaces filtered by sqlite/utils.py:search_where. It owns the saver lock and cursors while yielding, so both generator layers use aclosing for exception/cancellation cleanup. Raw channel_values deliberately exclude pending-write projections. Base checkpoint tuple/config/id and empty_checkpoint verified in checkpoint/base/__init__.py. Current parent graph log_response is the sole completed writer and edges directly to END; roots retaining branch:to:* are rejected. Real compiled graph update + pending writes regression checks this invariant without graph execution/model calls.
- SQLAlchemy2.0.54 selectable.py:3742 scalar_subquery and correlate support a single bounded conversation query with first-user-message subquery; no N+1 row reads. Message pages issue owner SELECT, max-ID SELECT, then ascending `limit+1` rows with conversation and frozen bound predicates. No row locks or write transactions needed; final SQL body from the owned page is the source check.
- FastAPI0.142.2 param_functions.py Query supports default/ge/le; GET sizes default50/200 and max200. Pydantic2.13.5 main.py model_copy and existing Field(exclude=True) retain trusted internal conversation identity for HistoryReader while omitting it from HTTP output. No dependency changes.
- Task8 terminal-source follow-up: pinned pregel/_loop.py:1092-1157 applies new input writes to __start__ then persists source=input before START consumes them; prior completed channel values remain at this root. Actual compiled graph interrupted before resolve_reference reproduces that root and wrong locator. Added __start__ absence guard. For Send scheduling, pinned _internal/_constants.py:20 defines TASKS='__pregel_tasks' and pregel/_algo.py:441/964 reads its Topic[Send]; nonempty raw task channel is rejected as nonterminal. No guessed pending-writes keys or private graph execution in GET; the existing branch:to:* guard remains. Regression uses real saver Send serialization and real compiled graph input interrupted before any business/model node.

## Task9: browser navigation and controlled Chromium
- Consulted [MDN AbortController](https://developer.mozilla.org/en-US/docs/Web/API/AbortController), [MDN Using Fetch](https://developer.mozilla.org/en-US/docs/Web/API/Fetch_API/Using_Fetch), [Playwright BrowserContext](https://playwright.dev/docs/api/class-browsercontext) and [Node HTTP server](https://nodejs.org/api/http.html#serverlisten) before concrete implementation. Fetch HTTP failures require response.ok checks; abort cancels request/body reading, while a separate revision guards already-resolved/late work. Full frozen-bound SQL pages are gathered and rendered in a detached fragment before replacing the current conversation.
- Installed bundled Playwright1.62.1 package.json and playwright-core/lib/coreBundle.js were inspected (this runtime bundles the implementation rather than the older lib/client tree). BrowserType.launch at39407 validates options and launches a separate browser; Browser.newContext at52286 creates isolated contexts and initializes storage. Existing project loader's explicit executablePath/cache discovery was reused, with no package installation or persistent profile/session takeover. Each controlled fixture uses server.listen(0, '127.0.0.1'), then closes only its own connections/server; browser close owns its child processes.
- Task8 final wire and current chat.js validators are the application contract: string IDs; frozen upto_id, ascending raw SQL rows, optional per-final-message original citations/actions/refund locator. Restored citations/status/actions pass existing validators; refund GET independently revalidates matching original locator/offer_id, and pending-order GET restores only current pending choices. No restored action invokes a business POST.

### Task10 API sources (2026-10-17)
- https://www.python-httpx.org/advanced/event-hooks/ : request hooks run after preparation and before network dispatch; AsyncClient requires async hooks. Installed .venv/Lib/site-packages/httpx/_client.py lines1691–1694 and976–979 confirm hooks run per redirected physical send too.
- Installed .venv/Lib/site-packages/langchain_openai/chat_models/base.py http_client/http_async_client documentation and constructor: supplying only async does not cover synchronous path; acceptance injects both. Existing create_model max_retries=0 retained; SummaryGenerator uses same bound client.
- https://docs.python.org/3.13/library/sqlite3.html : explicit BEGIN IMMEDIATE and transaction context rollback/commit; closing connection separately because connection context does not close it. Ledger holds only run/provider/limits/counts, not URLs or credentials.
- https://learn.microsoft.com/en-us/powershell/module/microsoft.powershell.management/start-process : Hidden window launch retained. Reused existing exact identity helpers (creation UTC, executable, full app-dir command, bounded launch ancestry) for8004; unknown listeners refused.
- Existing app/workflow/persistence.py and pinned AsyncSqliteSaver source are the checkpoint contracts; evidence reader uses sqlite URI mode=ro + query_only and actual saver deserializer; no setup/migration or root fabrication.
- Task10 installed versions verified without environment dump: Python3.13.5; httpx0.28.1, langchain-openai1.6.7, langgraph1.2.15, langgraph-checkpoint-sqlite3.1.2, SQLAlchemy2.0.54, aiosqlite0.22.1. https://docs.langchain.com/oss/python/langgraph/persistence and installed checkpoint/sqlite/aio.py SELECT/deserialization contract checked; direct read-only evidence intentionally avoids saver.setup. Initial git check-ignore returned no match for runtime/context-evidence JSON/ledger, so only that planned artifact directory was added.

### Task11 actual calibration and scoped migration (2026-10-17)
- Consulted official https://dev.mysql.com/doc/refman/8.4/en/information-functions.html for DATABASE(), CONNECTION_ID(), CURRENT_USER(), VERSION(). The ignored migration driver checked configured loopback3307/customer_service, Docker published mapping and container hostname/server UUID, then queried identity on each exact connection immediately before the existing migrate_context/verify_context operations. No connection URL, credential or process environment was printed.
- Rechecked https://www.python-httpx.org/advanced/event-hooks/ and locked httpx0.28.1 `_client.py`1691–1700: request hooks precede physical dispatch and async response hooks precede body consumption. The ignored annotated-summary capture used request cap first and `await response.aread()` only for these nonstream calls. It recorded only messages/tools/output fields, choices and usage, never headers or URLs. Browser packets use the existing ContextLogger and calibration hooks; an ignored run-scoped local observer subsequently records existing nonstream reply content for diagnosis, without a public API or production audit expansion.
- `absolute_error` now applies abs to the existing signed difference; `relative_error` retains its signed convention. Missing usage remains null. Three paid calibration rounds supplied11 observed nonstream samples; v1 estimator parameters remain conservative and unchanged. This is sampled provider usage, not a validated universal tokenizer or verified128000 provider window.

### Final fix: understanding JSON contract (2026-10-17)
- Controller verified official [structured output guide](https://docs.bigmodel.cn/cn/guide/capabilities/struct-output), [Chat Completions reference](https://docs.bigmodel.cn/api-reference/模型-api/对话补全), and [GLM-5.3-Flash](https://docs.bigmodel.cn/cn/guide/models/vlm/glm-5.3-flash). The documented request uses `response_format: {type: json_object}` and system instructions; the schema example validates client-side. No verified `json_schema`/`strict` or `tool_choice: none` contract was found for this deployment; this does not establish that undocumented capabilities are impossible. No such switch was introduced.
- Installed `langchain-openai 1.6.7`, `chat_models/base.py:2804–2818` inspected: `method='json_mode'` binds `response_format=json_object`, with `PydanticOutputParser` for a Pydantic schema. It does not impose provider-side strict query-schema validation. `include_raw=True` retains original model output for the application validator. The saved actual index11 packet matches this interface exactly: no tools, JSON mode, correct original system SHA256, HTTP200/stop, wrong action-shaped content. Client rejection is correct.
- The narrow candidate changes only UNDERSTANDING_SYSTEM role/protocol guidance. Original native tool pairs and SQL/State history, model/thinking, timeout, zero retries, and client `extra=forbid` validation remain unchanged. The model page lists a 1M window and thinking enabled; neither warrants changing the approved application W128000 or existing thinking configuration.
- Tracked `tests/fixtures/context/understanding_role_regression.json` retains the complete actual negative packet and response with source/hash and annotated multi-turn contrasts. Mock HTTP replay checks SDK transport, source preservation and strict rejection only; it is not evidence that the revised prompt fixes live GLM output. The original ignored run evidence remains untouched and the bounded real recheck belongs to the acceptance owner.
