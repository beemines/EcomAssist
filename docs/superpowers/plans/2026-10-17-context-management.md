# Chapter 7 Context Management Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 在同一会话内保留完整原文，通过三层模型视图、异步分段摘要和窗口预算支持长对话，并提供可切换、可继续的多会话聊天页。

**Architecture:** MySQL保存原始消息、两个分层锚点和只追加的摘要段，LangGraph的add_messages/checkpoint保存完整历史。统一ContextSnapshot负责模型视图；lifespan拥有有界摘要任务，后台提交不改活跃图。只读会话接口从原轮完成根恢复引用，前端复用现有主题与安全渲染。

**Tech Stack:** Python、FastAPI 0.142.2、SQLAlchemy 2.0.54/MySQL、LangGraph 1.2.15、langchain-core 1.6.6/trim_messages、langgraph-checkpoint-sqlite 3.1.2、现有GLM/BGE/Milvus、原生HTML/CSS/JavaScript。

**Spec:** `docs/superpowers/specs/2026-10-17-context-management-design.md`，用户2026-10-17已批准；基线`87d50359ec8f89deaea3fc48e47d560c6b3be22f`。

## Global Constraints

- 状态：用户于2026-10-17批准本计划，按Subagent-Driven方式开始实现。工作区固定`.worktrees/context-management`、分支`feat/context-management`，保留8002/8003。
- 原文完整持久化：保留SQL工具申请/结果，State.messages使用add_messages，普通节点只吐增量；不把裁剪列表写回checkpoint。
- `id <= S`已摘要；`S < id <= L`层2；`id > L`层1。S/L分别是summary_upto_msg_id/layer1_from_msg_id，均为完整轮次最终消息的排他上界，单调前进。
- 层2客服正文前80个Unicode字符；小工具结果不超过160字符可原样；大结果一行标识但保留配对、实体和mock。层1原文不改。
- 历史H按实际扣项倒推，H1=floor(H×0.70)，H2=H-H1；默认六配置128000/2000/4/1200/10/40分别对应窗口、用户上限、工具步数、结果上限、Top-K、目标轮数。最终回答默认512。
- 演示显式配置`MODEL_CONTEXT_WINDOW=18000 MAX_OUTPUT_TOKENS=2000 MAX_USER_INPUT_TOKENS=2000 MAX_AGENT_STEPS=3 TOOL_RESULT_MAX_TOKENS=1200 RERANK_TOP_K=5`；不凑5650/3954/1695。
- E=min(6000,ceil(W/8))、G=min(2000,ceil(W/32))、M=max(256,ceil(W×0.03))。128000是应用声明预算，不称已验证供应商窗口；模型和技术栈不换。
- 后台每会话1任务、全应用2个摘要调用并发、等待最多8会话；摘要输出预留512、沿用LLM_TIMEOUT_SECONDS、零模型自动重试；关闭宽限5秒。
- 摘要目标50–200中文字符，只压新批原文；旧段不回炉。SQL段只追加，失败不推进S，当前轮快照冻结；不做跨会话/语义检索历史/用户画像。
- system和tools同阶段跨轮固定；摘要＋证据放当前用户之后的同一user侧附件。动态控制附件单独计V；不假定缓存必命中。
- `log/app.log`原样记录实际上下文；history_ctx每轮都有，固定回复标sent=false；既有元数据审计白名单不放宽。
- Context7当前不可调用，按用户许可先查官方文档及锁定源码再用具体API，来源追加references文件；技术走不通先问，不换选型。
- 每任务完成、评审和finish立刻追记`dev-notes/ch07.md`四项；不预写“通过”。产品代码TDD，纯prompt/数据以标注样例验证替代TDD。
- 少量真实GLM/BGE页面调用已有持续授权；下文两组大批次不在本次计划审批中自动取得调用授权。无工单/退款业务提交，无合并/远程推送。

## Review Focus

1. 旧根缺较早SQL消息或取消轮次留下孤立工具：恢复后原文不乱序、不重复、不把未完成操作说成成功（任务4）。
2. 摘要正在生成时新轮推进L或服务重启：当前轮不阻塞，提交不跨会话、不覆盖新S，也不重复压旧段（任务5/6）。
3. 用户粘贴长中文、巨大工具结果或保留旧32000费用配置：在实际调用前明确预算原因，不能截半个JSON或悄悄删用户原话（任务1/3/7）。
4. 老回复与新回复都有[1]、原根缺失或BIGINT超过JS安全范围：回载用原轮来源，缺源不伪造，ID始终字符串（任务8/9）。
5. 切换会话时旧GET/SSE迟到、侧栏500或用户打开了业务表单：不得串会话、自动提交或使聊天输入不可用（任务9）。

---

## 文件与接口约定

现有入口是`app/main.py:create_app`、前端`app/static/{index.html,chat.css,chat.js}`；仓库无Makefile，不编造`make dev`。新增文件在各任务列出，不做无关目录重构。

内部SQL主键可用int；HTTP、LangGraph消息ID及locator使用str。`app/context/types.py`统一定义以下不可变数据载体，后续任务不得各造同义字段：

- `PhaseOverheads(name, system, tools, output_tokens, attachment_tokens, tool_peak_tokens, uses_evidence)`；`ContextBudget(window, phases, desired, history, layer1, layer2, evidence, summary, safety, estimator_version)`。phases为按阶段名索引的扣项字典，键固定为F/U/E/G/V/O/M/P/A，值为int，供日志及断言直接核对。
- `ContextAnchors(summary_upto: int|None, layer1_from: int|None)`；`SummarySegment(seq, from_msg_id, upto_msg_id, content, created_at)`；`SummaryBatch(conversation_id, expected_summary_upto, expected_seq, from_msg_id, upto_msg_id, source_rows, source_hash)`。
- `FrozenMessage(id, role, content, tool_calls_json, tool_call_id)`：ID为str，JSON为不可变序列化文本，content允许SQL工具申请的NULL；转换LangChain时沿用现有records规则。
- `LayerPlan(anchors, layer1, layer2, raw_layer2_rows, layer1_tokens, layer2_tokens, downgrade_ranges)`；`ContextSnapshot(snapshot_id, conversation_id, user_message_id, anchors, summaries, omitted_summary_seqs, layer1, layer2, budget)`；`ModelContextPacket(messages, tools, estimated_tokens, output_tokens, prefix_hash, snapshot_id)`。消息/段集合用tuple，出站时生成防御性副本。

## 执行前基线（计划获批后执行）

- [x] 确认`git status --short --branch`只有预期文档提交；读取原spec、API记录和各任务现有源码。本章产品基线结果另外记入dev-notes，不能用设计检查代替。
- [x] 在该worktree使用`uv sync --frozen --offline`准备锁定依赖（从本机既有缓存安装77包）；未复制含密钥的环境内容到报告。PowerShell设`$env:PYTHONUTF8='1'`，以下命令均在该worktree执行。
- [x] 运行`.venv/Scripts/python.exe -m pytest -q`记录基线实际数量。MySQL集成测试用现有3308随机自有库夹具，显式`--run-mysql`；不清空3307应用库。基线失败须先分清既有失败和环境缺失，不写“基线通过”。

各任务的代码块是必须落实的核心测试断言；其中变量由该Task的测试布置，不代表仓库已有这些fixture或这些测试已经运行。

## Task 1: 统一token估算、窗口预算和配置自检

**Files:** Create `app/context/{__init__,types,tokens,budget}.py`, `tests/test_context_budget.py`, `tests/fixtures/context/steady_turns.json`; Modify `app/config.py`, `.env.example`, `app/agent/controls.py`。

**Interfaces:** `estimate_payload(messages: Sequence[BaseMessage], tools: Sequence[dict]=()) -> int`；`derive_budget(settings: Settings, phases: Sequence[PhaseOverheads], *, steady_turn_tokens: int, minimum_turn_tokens: int) -> ContextBudget`；`derive_turn_token_limit(budget: ContextBudget, *, call_limits: Mapping[str,int]) -> int`。类型定义按上表，复杂载体可随所属任务补全，但字段不改名。

```python
assert budget.history == min(budget.desired, min(p['A'] for p in budget.phases.values()))
assert budget.layer1 == budget.history * 70 // 100
assert budget.layer1 + budget.layer2 == budget.history
```

- [x] **Red**：写`test_same_counter_covers_cjk_json_schema_and_call_ids`、`test_budget_formula_has_no_unaccounted_attachment`、`test_alias_conflict_and_explicit_total_limit`、`test_no_full_turn_fails_without_paid_startup`。断言`A=W-F-U-E-G-V-O-M-P`、`H=min(D,min(A))`、`H1=floor(.7H)`、`H1+H2=H`；工具schema/JSON/关联ID都会增加输入估算；MAX_AGENT_STEPS=3与显式旧4冲突；显式32000保留。
- [x] **确认失败**：运行`.venv/Scripts/python.exe -m pytest tests/test_context_budget.py -q`，因新增模块/计算缺失失败，不接受凭据或数据库连接失败冒充Red。
- [x] **实现**：类型及六项配置、输入数值严格校验（排除bool/非有限值/非法Top-K，步数仍≤4）、中文与ASCII/协议分项计数、F/U/E/G/V/O/M/P/D计算和启动最低业务轮次校验。稳态夹具包含真实形状的单工具订单、物流、Top-10 FAQ及短回答，T取这些完整轮次的最大估算值、启动最小轮次取最小值，不使用问候或填充文本。估算器参数单独版本化，初始依据及不确定性写入夹具说明；任务7完成实际序列化接线后用实测usage校准，任务11复核，不按目标滑窗倒推系数。旧工具预算仅从Workflow调用链退出，不改离线评估阈值；累计额度缺省可推导，显式值仍生效。
- [x] **Green**：同一命令通过，再运行`tests/test_config.py tests/test_agent_controls.py tests/test_db_config.py`；已有成本账本实测值不被新估算覆盖，派生上限不当作已花费用。
- [x] **提交**：追记本任务四项和真实Red/Green结果；`git add`仅本任务文件及ch07记录，`git commit -m "feat: derive workflow context budgets from model window"`。

## Task 2: 用户DDL、边界仓储和追加式摘要事务

**Files:** Create `sql/ch07.sql`, `sql/ch07-layers.sql`, `app/context/{migration,cli}.py`, `app/repositories/context.py`, `tests/test_context_migration_cli.py`, `tests/integration/test_context_{migration,repository}.py`; Modify `app/db/models.py`, `app/context/types.py`。

**Interfaces:** `verify_context(database: Database) -> None`、`migrate_context(database: Database) -> None`均async；`ContextRepository(database)`提供async `load(conversation_id: str) -> tuple[ContextAnchors,tuple[SummarySegment,...]]`、`advance_layer1(conversation_id: str, *, expected: ContextAnchors, upto_msg_id: int) -> bool`、`load_batch(conversation_id: str, *, target_upto: int) -> SummaryBatch|None`、`append_segment(batch: SummaryBatch, content: str, *, summary_budget: int) -> SummarySegment|None`。CLI：`python -m app.context.cli migrate|verify`，verify永不DDL。

```python
assert sum(result is not None for result in concurrent_appends) == 1
assert original_message_bytes_before == original_message_bytes_after
assert anchors.summary_upto == segments[-1].upto_msg_id
```

- [x] **Red**：用`migration_database`建原conversations/messages及一条原文，测试新列/完整段表与用户DDL相同、重复迁移不动原文、部分DDL已成功可继续、结构漂移拒绝；测试S/L不能越过当前用户、落在tool中间、回退或跨会话；并发append同一batch仅一段提交。
- [x] **确认失败**：运行`.venv/Scripts/python.exe -m pytest tests/test_context_migration_cli.py tests/integration/test_context_migration.py tests/integration/test_context_repository.py --run-mysql -q`；先确认3308自有测试库就绪，不能对3307执行这些迁移测试。
- [x] **实现**：原样两步DDL与ORM映射；information_schema核对列、类型、索引、字符集/中文注释。MySQL DDL会隐式提交，迁移按已存在结构逐项检查后继续，不能假定整次ALTER可回滚。仓储用每调用独立session/短事务、conversation行锁及expected S/seq核验；模型调用不在事务内。追加段＋S＋投影一次提交，NULL边界规范化、全局ID间隙和唯一键冲突有明确结果。
- [x] **Green**：重跑上述命令；断言原消息哈希一致、旧段内容/时间不变、失败事务无S推进。CLI错误不打印数据库URL或密码。
- [x] **提交**：记四项，`git commit -m "feat: persist layered context anchors and append-only summaries"`。

## Task 3: 完整轮次降级、冻结快照与模型包

**Files:** Create `app/context/{layers,view}.py`, `tests/test_context_{layers,view}.py`; Modify `app/context/types.py`, `app/core/tool_history.py`（只提取可复用校验，不改早期模式裁剪语义）。

**Interfaces:** `plan_layers(rows: Sequence[MessageRecord], anchors: ContextAnchors, budget: ContextBudget, *, current_user_id: int) -> LayerPlan`；`build_snapshot(plan: LayerPlan, segments: Sequence[SummarySegment], *, conversation_id: str, user_message_id: str, budget: ContextBudget) -> ContextSnapshot`；`compose_call(snapshot: ContextSnapshot, *, system: SystemMessage, current: HumanMessage, attachment: dict, pending: Sequence[BaseMessage], tools: Sequence[dict], output_tokens: int) -> ModelContextPacket`。

```python
assert tuple(m.content for m in snapshot.layer1) == expected_original_contents
assert shortened_assistant.content == original_assistant.content[:80] + '后文已截短'
assert snapshot_before_background_commit == snapshot_after_background_commit
```

- [x] **Red**：测试`test_layer1_is_exact_and_layer2_user_is_exact`（客服80字符、大结果一行、小结果160字符界限）、`test_trim_aligns_to_complete_tool_turns`、`test_summary_race_cannot_change_snapshot`、`test_oversize_backlog_errors_without_dropping_user`。断言最近原文/role/参数/结果/ID完全相同，预算恰好等于阈值不降级；一轮多工具与失败残留不拼接成新成功轮次。
- [x] **确认失败**：运行`.venv/Scripts/python.exe -m pytest tests/test_context_layers.py tests/test_context_view.py -q`。
- [x] **实现**：以`trim_messages`选择候选后对齐完整轮次，推进L只降最旧完整轮；用户正文不动，层2工具仍成对。摘要按完整段时间顺序选择，超过G只选最新完整段并记录遗漏。compose固定system→层2→层1→当前user→一个摘要/证据/控制user附件→当前原生工具对；附件非system，不把当前用户复制两遍。校验最终输入＋输出＋M≤W、H硬上限和防御性副本；超大必需输入给容量错误，不删除原话、不等待摘要。
- [x] **Green**：重跑新测试及`tests/test_tool_history.py tests/test_memory.py tests/test_multi_tool_history.py`，证明纯聊天既有完整轮次保护仍在。
- [x] **提交**：记四项，`git commit -m "feat: build immutable three-layer model context views"`。

## Task 4: add_messages增量和旧根完整原文恢复

**Files:** Create `app/workflow/history.py`, `tests/test_context_state_history.py`; Modify `app/workflow/{state,service,nodes,agent}.py`, `tests/{workflow_fakes,test_workflow_state,test_workflow_persistence,test_multi_tool_history}.py`。

**Interfaces:** `prepare_history_update(previous: Mapping, rows: Sequence[MessageRecord], *, current_user_id: int) -> tuple[list[BaseMessage]|Overwrite,bool]`（bool标记bootstrap）；`new_turn_state`保留原公开参数，补`context_version`和可序列化上下文快照字段；Agent子图适配出口`agent_delta(before_ids: frozenset[str], result: Mapping) -> dict`只返新增消息。普通路径从实际SQL新增行同步，不复用原匿名模型ID。

```python
assert [m.id for m in latest.values['messages']] == [str(r.id) for r in sql_rows]
assert len({m.id for m in latest.values['messages']}) == len(sql_rows)
assert original_completed_root == reread_original_root
```

- [ ] **Red**：真实SQLite开关两次，测试两轮历史累积、新消息仅出现一次、父子图无重复、SQL ID排序；模拟旧根缺较早消息、旧根无context_version、取消后新轮和pending选单恢复。断言历史根字节不变、state_version仍2、语义裁剪不减少messages。
- [ ] **确认失败**：运行`.venv/Scripts/python.exe -m pytest tests/test_context_state_history.py tests/test_workflow_state.py tests/test_workflow_persistence.py -q`。
- [ ] **实现**：messages挂官方add_messages，各工具/最终节点先保存SQL再给返回消息设置SQL ID，只返回delta；子图出入口显式处理父图再次合并。只有旧根规范化允许Overwrite完整SQL原文；没有原文可恢复就报错。保持未完成流水可审计、模型投影只回放合法完整轮次；同步调整现有`agent._parts`等读者，不能在任务7接线前把完整审计流水直接送入旧完整轮次校验。旧测试中重复使用相同最终ID的替身改为递增真实形状，不能仅删除“历史不重复”的断言。
- [ ] **Green**：上述测试及`tests/test_after_sales_workflow.py tests/test_workflow_routes.py tests/test_workflow_api.py tests/test_refund_actions.py tests/test_chat_actions.py`通过；原locator完成根仍能核验，暂停恢复不新建重复用户轮次。
- [ ] **提交**：记四项，`git commit -m "refactor: preserve complete workflow history with message deltas"`。

## Task 5: 标注摘要样例、严格生成器和有界后台管理器

**Files:** Create `app/context/{prompts,summarizer,manager}.py`, `tests/fixtures/context/summary_cases.json`, `tests/test_context_{summarizer,manager}.py`; Modify `app/context/types.py`, `docs/superpowers/references/2026-10-17-context-management-apis.md`。

**Interfaces:** `validate_summary(content: str, batch: SummaryBatch) -> str`；`SummaryGenerator(model, settings).summarize(batch: SummaryBatch) -> str` async，恰有`content`字段JSON、正常stop、无tool；`SummaryManager(repository: ContextRepository, generator: SummaryGenerator, *, budget_provider: Callable[[],ContextBudget])`提供同步非等待 `notify(conversation_id: str, *, layer2_tokens: int, budget: ContextBudget) -> bool`、async `startup() -> None`、`aclose() -> None`。startup用budget_provider重算当前部署预算，触发函数自身不调用LLM或等待队列。

```python
assert reply_done.is_set() and not summary_released.is_set()
assert max_active_calls == 2 and max_waiting_conversations <= 8
assert anchors_after_failed_summary == anchors_before_failed_summary
```

- [ ] **Prompt验证先行**：写12个带原文、必须保留事实/禁止事实的样例：单订单、明确换单、多订单歧义、型号、手机号、否定、包裹未找到、mock历史状态、故障尚未解决、表单打开/取消、已申请但未退款、纯寒暄。摘要目标50–80字、上限200，不复述通用FAQ条款；旧段不作为生成原料。先离线标注与审阅，真实prompt检查计入任务11少量调用额度。
- [ ] **Red并确认**：协议代码及调度测试`test_invalid_json_entities_or_length_does_not_advance`、`test_event_blocked_summary_does_not_block_caller`、`test_two_running_eight_waiting_one_per_conversation`、`test_boundary_conflict_and_restart`；运行`.venv/Scripts/python.exe -m pytest tests/test_context_summarizer.py tests/test_context_manager.py -q`确认预期失败。
- [ ] **实现**：严格JSON/结束状态和实体来源校验，不把词法检查称为全面忠实度证明。按完整轮次切原始批次，追加到冻结目标L；纯寒暄允许空content覆盖行。每任务独立session，锁只在commit期间；失败不推进、无自动模型重试；触发/开始/完成/跳过/失败都有范围与耗时。启动只恢复L>S的降级会话；5秒关闭宽限后取消并等待清理。
- [ ] **Green**：重跑测试；用asyncio.Event确定摘要未释放前普通业务回复已完成，不靠sleep碰运气；交叉会话任务结束乱序也不串段。12个样例的离线校验报告区分协议通过、标注事实检查及尚未真实生成。
- [ ] **提交**：记四项，`git commit -m "feat: add bounded asynchronous append-only conversation summaries"`。

## Task 6: 共用历史视图、来源校验、生命周期和上下文日志

**Files:** Create `app/context/{service,logging}.py`, `tests/test_context_{workflow,lifecycle,logging}.py`; Modify `app/workflow/{runtime,service,nodes,understanding,intent,entities,prompts}.py`, `app/main.py`, `.gitignore`, `tests/workflow_fakes.py`。

**Interfaces:** `ContextCoordinator(repository: ContextRepository, manager: SummaryManager, settings)`提供async `prepare(conversation_id: str, user_message_id: str, rows: Sequence[MessageRecord], budget: ContextBudget) -> ContextSnapshot`、同步 `on_completed(snapshot: ContextSnapshot) -> None`。`ContextLogger(path: Path)`提供`history(snapshot, *, consumer: str, packet: ModelContextPacket|None, sent: bool)`、`model(packet, *, conversation_id: str, user_message_id: str, phase: str, call_index: int)`、`event(name: str, fields: Mapping)`和`close()`。理解/分类接收同一snapshot，不能自行再按8000裁一次。

```python
assert understanding_snapshot_id == intent_snapshot_id
assert any(row['event'] == 'history_ctx' and row['sent'] is False for row in social_logs)
assert 'Authorization' not in log_text and runtime_api_key not in log_text
```

- [ ] **Red**：测试固定闲聊sent=false仍有history_ctx、理解和分类实际读同一层、后台提交不改变当前快照、摘要实体只能按实际注入段追溯且不能从助手正文造订单。测试新手机号/否定/多个订单和“最开始”与最近订单不同；测试暂停后部署换小窗口时恢复调用会重新核验预算，装不下则明确配置冲突而非超窗发出；logger实际正文含完整摘要/工具JSON且无运行时Authorization；关闭顺序先结束聊天/摘要再关客户端/SQL。
- [ ] **确认失败**：运行`.venv/Scripts/python.exe -m pytest tests/test_context_workflow.py tests/test_context_lifecycle.py tests/test_context_logging.py -q`。
- [ ] **实现**：prepare取得本会话快照并按expected边界推进L；State携带可序列化版本，运行期客户端只在Runtime。替换理解器旧过滤投影、分类器仅当前字符串入口；当前诉求优先、summary只定位身份，业务结果必须本轮重读。理解query长度与20k SQL文本/输出预算联合检查，不能截到旧512；路由检索自身512上限仍返回明确输入限制。专用UTF-8 log/app.log逐JSON行，不放宽workflow.audit白名单；每次真实调用前记实际payload，失败/取消不丢已发记录。lifespan注册摘要管理器、verify_context只读核验；注入替身资源仍由调用方拥有，测试不偷连真实库。
- [ ] **Green**：新测试及`tests/test_workflow_lifecycle.py tests/test_workflow_audit.py tests/test_intent_contract.py tests/test_online_chat_reliability.py`；确认闭包与单次Runtime不共享可变快照，任务结束/cancel只有一次成本结算。
- [ ] **提交**：记四项，`git commit -m "feat: share layered history and log actual model contexts"`。

## Task 7: Agent稳定前缀、真实证据包和全链路预算接线

**Files:** Create `app/workflow/controls.py`, `tests/test_context_{agent,prefix,evidence}.py`, `tests/fixtures/context/token-calibration.json`; Modify `app/workflow/{agent,after_sales,prompts,nodes,service,expansion}.py`, `app/core/{evidence,sufficiency}.py`, `app/retrieval/{service,multi,query}.py`, `app/agent/controls.py`, `app/main.py`, `tests/test_agent_native_control.py`, `tests/test_agent_final_boundary.py`。

**Interfaces:** `UnifiedAgentControl(reply_mode, suggested_actions, refund_decision: Literal['eligible','needs_review','ineligible','not_applicable']|None, decision_reason: str|None)`；`parse_control(reply: AIMessage, *, route: str, intent: str) -> UnifiedAgentControl`；`stable_read_schema(registry: Mapping[str,BaseTool]) -> list[dict]`；`prepare_workflow_evidence(payloads: Sequence[dict], *, top_k: int, token_budget: int) -> WorkflowEvidence`。在core/evidence.py定义`WorkflowEvidence(payload, citations: tuple[Citation,...], best_score, strategy, tool_receipts)`，不借用旧EvidencePacket.messages占位；模型消息只由任务3的compose_call产生。`RetrievalService.retrieve/finalize_candidates`新增可选`top_k: int=10`，WorkflowRetriever透传线上Top-K，离线默认不变。

```python
assert ordinary_decision_packet.prefix_hash == after_sales_decision_packet.prefix_hash
assert len(demo_evidence.citations) <= 5
assert actual_http_body['messages'] == logged_model_context['messages']
```

- [ ] **Red**：跨普通/知识/售后轮断言同阶段prefix hash与tools字节一致、没有动态system、普通控制后两字段必须null、售后四字段语义仍严格；模拟越权FAQ/写工具在执行前拒绝。证据Top-5/Top-10、整块预算/首尾引用、实际选入集合过闸；捕获出站请求体与model_ctx相等。巨量工具返回、输入/输出/峰值/累计额度分别有明确终态，不能length JSON当成功。
- [ ] **确认失败**：运行`.venv/Scripts/python.exe -m pytest tests/test_context_agent.py tests/test_context_prefix.py tests/test_context_evidence.py -q`。
- [ ] **实现**：把现有AgentControl/AfterSalesControl解析统一到独立controls模块，动态意图/回复模式/售后理由进用户附件。固定四个读取schema和内部控制schema，服务端保留执行权限；最终阶段不绑工具。从ContextBudget取窗口、MAX_AGENT_STEPS、配置最终输出，不再硬编码512或8000；累计预算独立。FAQ正文只在附件，当前原生回执仍配对，业务结果完整类型副本保留关键字段。top_k只限制线上最终证据，不改Milvus dense/BM25各50或重排模型，不重校准既有得分阈值。
- [ ] **Green**：新测试及`tests/test_workflow_agent.py tests/test_workflow_agent_limits.py tests/test_workflow_agent_quality.py tests/test_agent_native_current_read.py tests/test_agent_native_control.py tests/test_agent_final_boundary.py tests/test_workflow_gate.py tests/test_refund_decision.py tests/test_refund_policy_scoring.py`；对原政策、两步订单物流、退款需审核、库外拒答各做离线完整图复验。
- [ ] **首轮校准**：在默认窗口完成最多3轮真实链路冒烟并将实际序列化包与可取得的非流式prompt_tokens配对，保存校准样本/系数/误差，重跑预算与视图测试再交给任务10。计入任务11统一的小额总上限，不为校准修改stream_usage或发明缺失usage；没有usage的调用标未知，不能填0。
- [ ] **提交**：记四项，`git commit -m "feat: apply stable agent prefixes and bounded context packets"`。

## Task 8: 只读会话分页、原文和原轮引用恢复

**Files:** Create `app/context/history_reader.py`, `tests/test_context_conversation_api.py`, `tests/integration/test_context_conversation_reads.py`; Modify `app/repositories/conversations.py`, `app/schemas/conversation.py`, `app/api/conversations.py`, `app/workflow/persistence.py`, `app/main.py`。

**Interfaces:** async `ConversationRepository.list_for_user(user_id: str, *, before_id: str|None, limit: int) -> ConversationPage`、`read_page(conversation_id: str, *, user_id: str, after_id: str|None, upto_id: str|None, limit: int) -> MessagePage`；schema定义两Page：`items/next_before_id`及`messages/upto_id/next_after_id/turn_metadata`。async `HistoryReader(checkpointer, repository).decorate(page: MessagePage) -> MessagePage`按final_message_id关联原完成根。

```python
assert old_metadata['citations'][0]['chunk_id'] != new_metadata['citations'][0]['chunk_id']
assert response.json()['messages'][0]['id'] == '9007199254740993'
assert model_calls_after_get == model_calls_before_get
```

- [ ] **Red**：测试默认50/200、所有页完整、首次冻结upto_id、新消息到来不重复不丢、BIGINT字符串、首问取第一条、summary完成不把旧会话排第一、别的user_id为404。旧/新答复均引用[1]但chunk不同；旧根缺失不重新检索、不捏造引用或动作；GET不产生模型/任务/业务写入。
- [ ] **确认失败**：运行`.venv/Scripts/python.exe -m pytest tests/test_context_conversation_api.py tests/integration/test_context_conversation_reads.py --run-mysql -q`。
- [ ] **实现**：两条GET的当前身份服务端限定demo-user；完整原始role/content/工具字段返回，原SQL NULL不伪造文本；可带created_at。HistoryReader一次构建原轮根映射，核验conversation、completed终态、final_message_id及SQL正文，不使用必须“最新用户轮次”的写动作校验来误拒旧历史。恢复locator只供后续已有业务接口再核验，不在GET执行。
- [ ] **Green**：上述测试及`tests/test_conversation_api.py tests/test_chat_actions.py tests/test_refund_actions.py`；对查询执行计数作断言，避免N条消息反复全扫描checkpoint。
- [ ] **提交**：记四项，`git commit -m "feat: expose owned conversation history with original citations"`。

## Task 9: 主题内多会话侧栏和原文回载

**Files:** Create `app/static/conversations.js`, `scripts/verify-context-browser.cjs`; Modify `app/static/{index.html,chat.css,chat.js}`。

**Interfaces:** `ConversationSidebar({onSelect, onNew, getBusy}).refresh()/setActive(id)/setBusy(bool)`；聊天页提供async `switchConversation(id)`、`hydrateConversation(pageSet)`、`createConversation()`，复用`addMessage/renderAnswer/acceptCitations/acceptStatus`安全渲染。conversations.js在chat.js之前defer加载，UI类不复制SSE解析器。

```javascript
assert.equal(await page.locator('#source-answer').innerText(), originalChunkText);
assert.equal(fixture.refundSubmissions, 0);
assert.equal(fixture.ticketSubmissions, 0);
```

- [ ] **Red（浏览器交互）**：先扩展独立临时端口fixture server，断言侧栏完整翻页、两个[1]各开原chunk、大ID无精度损失、切换旧GET迟到不会覆盖新选择、列表500仍可输入发送、流式期间不能切换。无需为CSS写镜像单测；用真实Chromium跑新场景确认现状失败。
- [ ] **实现**：复用现有颜色、圆角、对话滚动区，桌面侧栏新在前/首问预览/已摘要标记，手机收起可打开。全部原文页加载成功才切换；失败保留当前会话，列表失败静默。切换前关闭未提交表单、不提交业务，旧abort/代号结果不能覆盖新会话。新对话立即POST新身份，旧会话保留；刷新回载原文、pending选择器/原退款入口按既有GET恢复。转人工仍另起通知和小猫气泡，满意度只前端；不用confirm/alert黑框或innerHTML渲染历史。
- [ ] **Green**：`node --check app/static/conversations.js`、`node --check app/static/chat.js`、`node scripts/verify-context-browser.cjs`及既有`node scripts/verify-intent-routing-browser.cjs`；测试受控服务GET/POST按method区分，新增GET不能被旧“所有/api/conversations都返回创建回执”的替身误处理。
- [ ] **记录截图与提交**：保存桌面/窄屏、旧引用、切回继续聊截图及机器结果，明确是受控浏览器还是实际应用证据；记四项，`git commit -m "feat: add themed conversation sidebar and history hydration"`。

## Task 10: 固定21轮轨迹、离线级联和可复现演示工具

**Files:** Create `tests/fixtures/context/long_conversation.json`, `tests/test_context_long_conversation.py`, `scripts/{start-context-demo,context-process-ownership}.ps1`, `scripts/context-storage-evidence.py`, `app/context/acceptance.py`, `tests/test_context_call_cap.py`, `docs/context-management-demo.md`; Modify `app/context/cli.py`, `scripts/verify-context-browser.cjs`, `app/main.py`, `README.md`及现有GLM/BGE客户端的可选注入接线。

**Interfaces:** CLI新增`budget --profile default|demo`和`replay --profile default|demo --output PATH`（完全离线）；PowerShell `start-context-demo.ps1 -Profile default|demo`只拥有8004，分别使用`runtime/workflow/context-{profile}-8004.sqlite`；证据脚本 `--conversation-id ID --output PATH`只读当前SQL/checkpoint。`AcceptanceCallCap(run_id, limits: Mapping[str,int], ledger_path: Path).reserve(provider: Literal['glm','embedding','rerank']) -> None`在真实HTTP派发前原子计数，超额拒绝（async hook中不得调用模型），失败请求也占次数；仅验收启动显式注入，普通运行关闭。启动器可另收`-RunId/-MaxGlmCalls/-MaxEmbeddingCalls/-MaxRerankCalls`，必须整组出现。浏览器脚本默认受控；真实示例为`node scripts/verify-context-browser.cjs --live --profile demo --run-id ch07-demo-001 --max-glm-calls 150 --max-embedding-calls 50 --max-rerank-calls 25 --output runtime/context-evidence/ch07-demo-001`，运行前校验与服务端run及限额完全一致。

```python
assert not {'context downgrade', 'summary trigger', 'summary done'} & set(default_events)
assert {'context downgrade', 'summary trigger', 'summary done'} <= set(demo_events)
assert real_http_dispatches == accepted_reservations  # 不计前端轮数冒充上游次数
```

- [ ] **先标注数据**：冻结下列21轮原话及预期意图/实体/动作/摘要事实，保存哈希。第1/4/10/16/21轮走业务；第21轮允许“订单”或“物流”这两种合理分类，但必须恢复1001及原诉求，其余业务轮分别按物流/订单/物流/订单标注。其余轮为完整通用知识问题，不选单、不扩写。末轮必须区分最初1001与最近1002，并保留“没找到包裹、未申请退款”；不在中间反复提示1001。

```text
01 订单1001的物流到哪了？我还没找到包裹，先帮我查物流，不申请退款。
02 退换货政策是怎样的？
03 运费怎么算？
04 订单1002现在是什么状态？
05 电子商品的保修期多长？
06 MH-LP200可以装多少猫砂？
07 发票如何开具？
08 现货商品多久发货？
09 会员运费权益有哪些？
10 订单1002的物流到哪了？
11 价格保护怎么申请？
12 可以用信用卡付款吗，支持线下转账吗？
13 积分按什么规则累计？
14 MH-W40的水箱有多大？
15 人工客服的服务时间是什么？
16 订单1002的商品名称和订单状态是什么？
17 换货的期限和流程是什么？
18 无理由退货的退回运费由谁承担？
19 金卡会员有哪些专属售后权益？
20 申请发票需要准备什么信息？
21 最开始那个订单后来怎么说？我当时的诉求是什么？
```

- [ ] **Red并确认**：运行`.venv/Scripts/python.exe -m pytest tests/test_context_long_conversation.py tests/test_context_call_cap.py -q`，用真正图/SQLite、内存SQL边界替身、受控外部模型和固定真实形状工具结果，断言默认21轮不降级不摘要、演示真实计费触发级联，最初订单进摘要后才能继续理解；不能预置摘要/手改边界。回复被Event挂起摘要也能完成，所有上下文均有日志且在预算内，SQL/checkpoint原文一致。HTTP限额测试模拟聊天与两个摘要并发抢最后额度，只有一个出站；重启读取既有run账本、不清零掩盖次数。
- [ ] **实现与Green**：完成离线replay/budget、只读证据、验收专属HTTP请求计数hook及启动器；重跑测试和两profile replay，输出实际H/H1/H2和所有扣项。所有真实GLM/BGE客户端包括后台摘要共享同一run上限，不能只数前端POST；注入客户端的资源所有权仍由创建者负责。启动器复用上一章进程身份核验方式，必须检查PID创建时间、命令行/工作区和监听所有权；已有未知8004直接拒绝，不停8002/8003，Start-Process用WindowStyle Hidden。Profile显式解决旧steps别名和累计费用配置冲突，不修改用户.env、不暗增限制。
- [ ] **文档和自检**：文档给出`.venv/Scripts/python.exe -m app.context.cli migrate`、`verify`、`budget --profile demo`、`replay --profile demo --output runtime/context-evidence/offline-demo.json`、`pwsh -NoProfile -File scripts/start-context-demo.ps1 -Profile demo`；标明migrate显式DDL、在线启动只读核验，原有DDL前置。进程脚本测试不允许以PID文件单独授权停止。所有命令必须实际验证，不把这里的预期当成运行成绩。
- [ ] **提交**：记四项，`git commit -m "test: add reproducible layered-context acceptance profiles"`。

## Task 11: 校准、真实页面验收、评审与交付

**Files:** Create `docs/superpowers/reports/2026-10-17-context-management-acceptance.md`; Modify only discovered feature files/tests plus`tests/fixtures/context/token-calibration.json`、`docs/context-management-demo.md`、references和`dev-notes/ch07.md`。运行日志/截图/SQL证据放`runtime/context-evidence/<run-id>/`或`.cache/context-management/`，不进Git。

```python
assert default_completed_turns >= 21 and demo_completed_turns >= 21
assert recalled_order_id == '1001' and latest_other_order_id == '1002'
assert original_order_summary_seq in final_injected_summary_seqs
```

- [ ] **离线门槛**：运行`.venv/Scripts/python.exe -m pytest -q`、本章3308集成测试（`tests/integration/test_context_migration.py tests/integration/test_context_repository.py tests/integration/test_context_conversation_reads.py --run-mysql`）和两套受控浏览器脚本。记录总数、skip与环境限制，不能把单个子集累加成全量通过；无新改动/失败不反复扩大回归。
- [ ] **少量真实页面、prompt与校准复核**：用8004、真实当前GLM/BGE、现有知识库做政策、订单物流、选单暂停/取消、OTHER/闲聊、回载引用等固定冒烟；不提交工单/退款。本章小额阶段（含任务7）合计最多6个付费聊天轮次、60次GLM、12次嵌入、6次重排，后台summary也计GLM；任务5的12个标注prompt样例各真实生成一次，全部计入60次GLM总额，不能用假模型结果代替效果验证。沿用任务7计数器并复核provider prompt_tokens误差，未知usage不填0；如需改参数，版本化并重跑受影响离线两profile/预算测试，后续完整批次固定同版本。
- [ ] **完整批次的调用边界**：准备好代码、离线报告及预计调用账本后，核对当前持续授权；两组21轮预计合计约200–280次GLM，另有BGE调用，已超过“不是上百次大量调用”的边界。须把具体轨迹、每组估算和硬上限交用户批准再启动完整批次。计划预留每组最多150次GLM（含摘要）、50次嵌入、25次重排；达到上限立即终止并留失败结果，不重试整组、不扩大上限。若未取得该批授权，标注真实长会话验收待运行，不称本章全部验收完成。
- [ ] **真实验收与证据**：获该批授权后，先默认21轮、再演示21轮。每轮核对done、模型调用/用量、实际包与日志；默认S/L/段数不变，演示出现downgrade→trigger→done且原订单确实被摘要覆盖并注入。末轮恢复1001与诉求且本轮重新查业务。核对所有原文哈希、原根/引用、后台未阻塞事件时间；重启自己拥有的8004后，浏览器切回两旧会话继续聊、点原引用，桌面和窄屏截图。失败保留原批次报告；定点修复报告单例与整批是否已复验，不覆盖负例。
- [ ] **整分支评审**：按已选Subagent-Driven逐任务做规格/代码评审，最终对整分支做一次新评审，重点看Review Focus五项和原文/动作兼容。修复实际问题后跑相应验证；本任务不另造“手动清数据使断言通过”。评审结论、剩余风险、验证版本和实际调用数立刻追记ch07。
- [ ] **finish**：用verification-before-completion核对演示命令/报告/源码差异，提交`test: verify ch07 context management acceptance`，再按finishing-a-development-branch交付本地分支；本章没有合并/推送授权，不能借用第五步授权推送第七步。

## 计划自审与交接

覆盖映射：spec 1–3→任务1/2；spec 4→任务4；spec 5→任务3；spec 6→任务6/7；spec 7→任务1/7/10/11；spec 8→任务5/6；spec 9→任务5/6；spec 10→任务6/7；spec 11→任务8/9；spec 12→任务10/11。Review Focus逐项已落入上述Red断言。这里是计划覆盖结论，不是实现/测试通过结论。

计划自审检查接口/字段跨任务一致、无占位步骤、实测与预期分开、DDL隐式提交、默认与演示同轨迹、原轮引用及授权边界。执行时每个Task完成其验证/评审后才勾选并记四项；未经用户审阅本计划不进入实现。沿用此前用户选定的Subagent-Driven方式，不在本次计划编写阶段派发实现或评审子代理。
