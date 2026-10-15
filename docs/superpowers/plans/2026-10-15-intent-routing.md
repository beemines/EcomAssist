# 正式意图分流与退款售后流程 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 让客服正确理解本会话中的指代和业务切换，对具体退款/售后先取得订单和政策，再允许用户自主提交待审核退款申请。

**Architecture:** 沿用外层 LangGraph Workflow 和内部 Agent 子图，入口增加合并理解及八类意图分类，退款/售后增加订单优先子流程。订单选择通过原生 interrupt/Command 在 SQLite 上暂停恢复，MySQL 只在用户提交时保存待审核退款申请；检索复用 Milvus/BGE，逐查询召回后统一去重重排。

**Tech Stack:** 现有 Python 3.11–3.13、FastAPI 0.142.2、SQLAlchemy 2.0.54、Pydantic 2.13.5、MySQL、Milvus、LangChain Core 1.6.6/OpenAI 1.6.7、LangGraph 1.2.15、langgraph-checkpoint-sqlite 3.1.2、原生 HTML/CSS/JavaScript。

**Spec:** [2026-10-15-intent-routing-design.md](../specs/2026-10-15-intent-routing-design.md)。用户在书面设计提交 `d414dd9` 后回复“继续”，又在计划提交 `73a948e` 后回复“开始实现”，现已批准实施。沿用此前已选择的 Subagent-Driven 执行方式，前端按用户指定的 Vibe Coding 例外处理。

## Global Constraints

- 新工作在计划获批后经 using-git-worktrees 检查并创建/复用隔离工作树；建议 `.worktrees/intent-routing`、`feat/intent-routing`。当前 8002 保留，新服务在 8003、单 worker 验收；不复用正在运行服务的 SQLite 文件。
- 不新增基础设施或依赖，不更新 pyproject/uv.lock 中的锁定版本。默认沿用 `glm-5.3-flash`、原上游及 online low，不自动换模型或启用大小模型升级链。
- 理解 JSON 只有 `query`；意图 JSON 恰为 `intent/confidence`；扩写 JSON 只有 `queries`。八类为物流、订单、商品咨询、退款退货、售后、投诉、闲聊、其他；初始 confidence 阈值 0.70。
- 明确整句社交规则快路整轮零模型调用；其余先理解再分类。纯政策 FAQ 直接一次检索，不选单、不扩写；具体退款/售后先订单、后 2～3 路查询、后政策、后闸、后 Agent。
- Milvus 每查询 dense Top-50 + BM25 Top-50，用原生 hybrid_search RRF；跨查询 RRF 常数 60，chunk_id 去重并取最多 50 候选，bge-reranker-v2-m3 仅重排一次到 Top-10。过滤每路生效，知识只留一份。
- 保留真实重排分门槛、内容充分性自评、引用编号/原文、低置信度池。任何最终 delta 前过闸；缺订单/未知意图/依赖故障不能冒充知识不足。
- 官方 AsyncSqliteSaver、原 astream/custom+updates/SSE；不迁移 stream_events v3，不回退内存，不从历史 checkpoint 分叉执行。恢复不重复 SQL 用户消息、理解、分类或重置已消费预算。
- 演示订单固定业务时间 `2026-10-15`，卡片/工具/判断/表单一致，明确 mock；不猜订单或未知商品条件，不把维修自动改为退货，不把演示身份校验描述成生产鉴权。
- 退款原因仅表单必选，六类固定枚举；仅用户提交写 MySQL“待审核”，不实际退款、不改订单或人工状态、不自动建工单、不承诺到账时间。
- 最终回答 512；理解/分类/扩写/Agent 控制 JSON 2048；单次模型 60 秒、零模型重试，活动聊天累计 240 秒、FAQ 段 90 秒、最多四次逻辑工具调用。强制查单与聚合检索各计一次。
- 32000 账本包含分类/理解/扩写及 Agent，充分性等检索内部调用另记 usage/期限；不宣称全链路严格费用上限。暂停保留已消费活动时间与计数，人等待另计。
- UTF-8，新增/修改函数有中文用途说明；每个阶段/任务完成即时追记 `dev-notes/ch06.md` 的用户原话、产出、纠偏、返工。提交标题不加 ch 前缀，只提交本任务文件。
- Context7 本章月度额度耗尽，用户已允许官方文档替代；动具体 API 前核对锁定版本/官方接口并记来源。已查且无变动的接口复用记录，不反复请求已耗尽服务。
- 后端 RED→GREEN，Prompt/数据以标注样例验证替代纯 Prompt TDD；前端不套 brainstorm/TDD/code review，但需真实浏览器点击验收。不开 300 题评估，不把未执行样例计为通过。

## Review Focus

1. 同历史出现两单、否定及新订单切换时，不能把上轮订单或诉求带到本轮——Task 2/5 的实体来源和切换用例。
2. 页面刷新、重复点卡片、暂停后新消息及恢复断连时，不能重复跑原问题或留下永久忙碌锁——Task 4/6 的真 SQLite 与 SSE 故障用例。
3. SQL 答复已写而根检查点未完成、或部分 delta 后失败时，不能发退款 offer 或伪造完成——Task 5/6 的完成边界故障注入。
4. 跨会话同订单申请、客户端改金额/状态/原因、写成功丢响应时，必须保留服务器金额和至多一条待审核记录——Task 7 的 MySQL 并发与幂等用例。
5. 某路检索超时、取消被包装、旧评估路径和未知商品条件，不能被吞成合法扩写/充分证据或让所有退款都拒答——Task 3/5/9 的真实分母及条件判断用例。

---

## 文件分工、依赖与执行准备

| 文件/目录 | 职责与任务 |
| --- | --- |
| `app/orders/{types,demo}.py`、`app/orders/demo_orders.json` | 稳定演示订单与身份范围，Task 1 |
| `app/workflow/{understanding,entities}.py`、现有 intent/prompts | 合并理解、可信实体、严格分类，Task 2 |
| `app/workflow/expansion.py`、`app/retrieval/multi.py` | 扩写协议及多路合并，Task 3 |
| 现有 workflow/state/runtime、`app/workflow/selection.py` | 状态版本、暂停节点、活动预算，Task 4 |
| `app/workflow/after_sales.py`、现有 graph/nodes/agent | 订单优先节点及结构化退款判断，Task 5 |
| `app/workflow/order_actions.py`、`app/schemas/order_actions.py`、`app/api/order_actions.py` | 待选读取、恢复及 SSE，Task 6 |
| `app/refunds/{types,migration,repository,service,cli}.py`、`sql/ch06-ddl.sql`、`app/api/refunds.py` | 退款申请契约、表、事务、提交入口，Task 7 |
| 现有 static/index.html/chat.js/chat.css | 订单卡片、主题退款表单、独立结果气泡，Task 8 |
| `evals/intent_routing_cases.jsonl`、`evals/evaluate_intent_routing.py` | 新口径标注集与有界测量，Task 2 建集、Task 9 执行 |
| `scripts/verify-intent-routing-browser.cjs`、`docs/validation/2026-10-15-intent-routing-acceptance.md` | 浏览器证据与最终验收，Task 8/9 |

Task 1/2 完成后做 Task 3；Task 4→5→6 接通图；Task 7 依赖 Task 5 的完成 offer 和 Task 6 的动作边界；Task 8 依赖公开契约；Task 9 整体验收。接口依赖密集，实施按顺序推进，不并行修改共享图或服务文件。

执行阶段先读取 using-git-worktrees：检查附加工作树与 Git 状态，独立工作树从含本计划的 master 提交建立，`.env` 仅本机复用且不显示凭据。新检查点路径使用新工作树 `runtime/workflow/checkpoints.sqlite`，不拷贝 8002 的活跃 SQLite。执行 `uv sync --locked` 后一次基线 `uv run --locked pytest -q`，失败先归因，不修改与本章无关的工作。

以下命令除特别说明外在新工作树根目录用 PowerShell 执行，先设 `$env:PYTHONUTF8='1'`。仓库没有 Makefile，演示使用实际存在的 uv/CLI 入口。每个任务提交前 `git diff --cached --check`，每次仅 stage 对应文件及本阶段开发记录。

### Task 1: 稳定、同身份的订单列表与原查询工具

**Files:** Create `app/orders/__init__.py`、`types.py`、`demo.py`、`demo_orders.json`；Modify `app/repositories/conversations.py`、`app/tools/business.py`、`app/tools/registry.py`；Test `tests/test_demo_orders.py`、`tests/test_business_tools.py`。

**Interfaces:**

- `OrderSnapshot` 为 Pydantic BaseModel（strict/frozen、extra=forbid），字段 user_id/order_id/product_id/product_name/model/category/status、整数 amount_cents、currency='CNY'、signed_at:date|None、as_of:date（固定 2026-10-15）、mock=true、fixture_version。JSON 数据用 model_validate_json 读取，工具/State/HTTP 快照用 model_dump(mode='json') 转成可序列化值；`to_card()` 只返回前端展示字段，不暴露 user_id。
- `OrderProvider` 协议：`async list_orders(*, user_id:str)->list[OrderSnapshot]`；`async get_order(*, user_id:str, order_id:str)->OrderSnapshot|None`。`DemoOrderProvider` 从 JSON 读固定数据，无网络。
- `ConversationRepository.get_user_id(conversation_id:str)->str`：从 SQL 会话取身份，不消费浏览器传入的 user_id。
- `build_registry(faq,tickets,context,*,order_provider:OrderProvider|None=None,owner_resolver:Callable[[str],Awaitable[str]]|None=None)` 保留原位置参数。新增依赖成对提供时，对原 query_order/query_logistics 名称创建作用域闭包；未提供时保留旧教学/测试接口。

- [ ] **Step 1 — RED 测试：** `test_list_and_query_return_same_snapshot` 连查两次对象与金额/签收一致；`test_unknown_order_is_not_random_success` 为 not_found；`test_other_owner_order_not_visible` 列表/查询均不可取；`test_order_tool_uses_sql_owner_not_model_arg` 拒绝模型提供 owner。默认 demo-user 的 1001 为 MH-LP200、签收两天；1002 超七天但未超保修；1003 未发货；1004 退货例外商品，均明确 mock。

```python
assert first.model_dump() == second.model_dump()
assert first.as_of.isoformat() == '2026-10-15' and first.mock is True
assert await provider.get_order(user_id='other-owner', order_id='1001') is None
assert set(registry['query_order'].args_schema.model_fields) == {'order_id'}
```

- [ ] **Step 2 — 验证失败：** `uv run --locked pytest tests/test_demo_orders.py -q`，预期提供器未实现或随机数据一致性断言失败，不访问真实模型。
- [ ] **Step 3 — 实现：** 按上述签名建立固定事实；未知演示身份返回空候选。查单和物流闭包共享订单身份，物流使用稳定 mock 跟踪数据；测试另注入私有用户订单，不为任意输入订单号编造结果。订单读取不写 tickets/refund_requests。
- [ ] **Step 4 — GREEN：** `uv run --locked pytest tests/test_demo_orders.py tests/test_business_tools.py tests/test_tool_executor.py -q`；所有指定断言通过，原五工具名称/Schema 仍可绑定。
- [ ] **Step 5 — 留痕提交：** `feat: share stable scoped demo order facts`，记录模型工具仍为原名称、实际数据是演示。

### Task 2: 合并理解、八类意图与固定标注样例

**Files:** Create `app/workflow/understanding.py`、`entities.py`、`evals/intent_routing_cases.jsonl`；Modify `app/workflow/intent.py`、`prompts.py`、`nodes.py`、`graph.py`；Test `tests/test_query_understanding.py`、`tests/test_intent_contract.py`、`tests/test_workflow_routes.py`、`tests/workflow_fakes.py`。

**Interfaces:**

- `QueryUnderstanding(model,*,input_budget:int,timeout_seconds:float)`；`async resolve(raw_question:str,history:list[BaseMessage])->Resolution`，内部 Resolution 含 query/changed；模型 Schema 仅 query，1～512 字符；usage 采用原账本四项字段。
- `trusted_order_ids(history:list[BaseMessage])->set[str]`、`validate_resolved_entities(raw_question:str,resolved_question:str,history:list[BaseMessage])->None`；只从本会话已完成工具配对及用户明确订单表达取订单锚点，拒绝模型新造实体。
- `IntentResult(raw_intent:Intent,intent:Intent,confidence:float)`；`IntentClassifier.classify(question:str)->IntentResult`，模型恰为 intent/confidence；`route_intent` 增加 other 固定出口。节点改为消费 typed result，不能把 dataclass 当旧字符串。
- 新数据集恰 48 轮：24 单轮 + 6 组四轮；字段 id/dialogue_id/turn/query/expected_query/expected_intent/expect_order_picker/expect_expansion/critical/split，必要时另给 history_fixture（固定可信工具事实，不包含期望改写或标签）。四组四轮为 acceptance，余 32 轮 development；运行时不将期望标签发给模型。

- [ ] **Step 1 — 先建标注样例：** 从设计边界写 48 轮及人工可审的期望，完整问句逐字保留；补“前轮两单→它”、否定“不要退款，我要查物流”、1001→1002 切换、纯退货政策、维修、明确投诉和其他。标记可消解及完整透传样例，确保各指标有固定分母。这一步是 Prompt/数据样例验证，不写镜像 Prompt 的单测。
- [ ] **Step 2 — RED 契约测试：** `test_intent_exact_fields_and_finite_confidence` 拒绝额外键、字符串/布尔 confidence、NaN、截断；0.69→有效其他、0.70→原标签，保留 raw_intent。`test_resolution_cannot_invent_order` 拒绝来源外订单；`test_social_fullmatch_skips_both_models` 为零调用；问候加业务不得快路。

```python
assert low.intent == '其他' and low.raw_intent == '退款退货' and low.confidence == 0.69
assert boundary.intent == '退款退货' and boundary.confidence == 0.70
assert social_model_calls == 0
assert len(cases) == 48 and sum(c['split'] == 'acceptance' for c in cases) == 16
```

- [ ] **Step 3 — 验证失败：** `uv run --locked pytest tests/test_query_understanding.py tests/test_intent_contract.py -q`，预期旧协议缺 confidence 或新理解组件缺失失败。
- [ ] **Step 4 — 实现：** 两个独立 JSON 调用分别做理解、分类；Prompt 按选择题/JSON/few-shot/其他四件套。沿现有 include_raw 校验和结束状态检查，不把错误降级为其他。加入固定 other_response；仅接新分类消费及出口，完整理解节点与售后图在 Task 5 接入。
- [ ] **Step 5 — GREEN 与样例核对：** `uv run --locked pytest tests/test_query_understanding.py tests/test_intent_contract.py tests/test_workflow_routes.py -q`；受控输出只证明协议，48 轮 JSONL 的数量/组序/标签/分割核验通过，真实模型准确率留 Task 9。
- [ ] **Step 6 — 留痕提交：** `feat: define contextual query and intent contracts`；说明旧第五步金标及报告口径是历史材料，不静默把其“通用退货政策=退款退货”改成当前通过证据。

### Task 3: 严格扩写与有界多查询召回

**Files:** Create `app/workflow/expansion.py`、`app/retrieval/multi.py`；Modify `app/retrieval/service.py`、`app/workflow/prompts.py`；Test `tests/test_query_expansion.py`、`tests/test_multi_query_retrieval.py`、`tests/test_retrieval_service.py`。

**Interfaces:**

- `QueryExpander(model,*,input_budget:int,timeout_seconds:float)`；`async expand(question:str,order:OrderSnapshot)->tuple[str,...]`，原始 JSON 恰为 queries；首条等于规范问题，总数 2～3，每条不空且 ≤512 字符，空白去重后仍满足数量；usage 与理解器同口径。
- `RetrievalService.recall_candidates(query:str,*,category:str|None=None)->list[VectorHit]`：单查询 hybrid 前 50，不调用旧 planner/重排。
- `RetrievalService.finalize_candidates(*,question:str,plan:QueryPlan,candidates:list[VectorHit],category:str|None,strategy:str)->RetrievalBundle`：提取原权威回填/重排尾段，原 retrieve 仍按既有四策略调用它，保留返回契约。
- `WorkflowRetrieval(payload:dict,audit:dict)`；`WorkflowRetriever(retriever:RetrievalService)` 的 `async retrieve(*,question:str,queries:tuple[str,...],category:str|None)->WorkflowRetrieval`。一条显式 QueryPlan(expansions=[])；多条独立召回后第二层 RRF；payload 仍用 faq_payload，额外 provenance/counts 只放 audit，不突破证据 Schema。

- [ ] **Step 1 — 扩写样例核对：** 退款/维修各给明确检索角度；既有“商品完好未知”不得扩成“商品完好”，未提质量原因不得写成已确认质量故障。纯 FAQ 不调用本扩写器。
- [ ] **Step 2 — RED 测试：** `test_rrf_union_deduplicates_before_single_rerank`：三次 index hybrid、一次 reranker、最多 50 候选/10 证据；每路重复 ID 仅贡献一次，融合相同分按 ID 稳定。`test_filter_and_authority_apply_to_each_query` 严格同品类；`test_one_failing_lane_fails_request` 不返回残缺成功；`test_wrapped_cancellation_never_becomes_partial_success` 注入取消和超时包装链，必须传播取消/超时且 reranker 零调用；`test_expansion_wrong_schema_not_degraded` 不回退旧协议；`test_plain_faq_never_calls_planner` 规划器调用零次。

```python
assert index.call_count == 3 and reranker.call_count == 1 and planner.call_count == 0
assert result.payload['retrieval']['candidate_count'] <= 50
assert len(result.payload['matches']) <= 10
assert len({m['id'] for m in result.payload['matches']}) == len(result.payload['matches'])
```

- [ ] **Step 3 — 验证失败：** `uv run --locked pytest tests/test_query_expansion.py tests/test_multi_query_retrieval.py -q`，预期多查询入口缺失/旧实现只做一次召回失败。
- [ ] **Step 4 — 实现：** 每条 embedding+Milvus 原生 hybrid，跨路得分为各路唯一名次的 `sum(1/(60+rank))`，截断后权威回填再统一重排；保留 provenance。顺序最多三路，由调用节点一个 90 秒 FAQ 段统一包裹，取消/超时传播；不新增集合或重建知识。
- [ ] **Step 5 — GREEN：** `uv run --locked pytest tests/test_query_expansion.py tests/test_multi_query_retrieval.py tests/test_retrieval_service.py tests/test_retrieval_metrics.py -q`；原 dense/bm25/hybrid/hybrid_rerank 和旧解析降级专项不变。
- [ ] **Step 6 — 留痕提交：** `feat: merge bounded multi-query hybrid candidates`，记录算法/过滤/一次重排证据及无入库改动。

### Task 4: 新状态、纯暂停节点与恢复预算

**Files:** Create `app/workflow/selection.py`；Modify `app/workflow/state.py`、`runtime.py`；Test `tests/test_order_selection_state.py`、`tests/test_workflow_persistence.py`、`tests/test_workflow_state.py`。

**Interfaces:**

- 扩展 WorkflowState：state_version=2、raw_intent/confidence、order_selection/order_snapshot、retrieval_queries、refund_decision/decision_reason/refund_offer、stage_usage、active_elapsed_seconds、supersedes_turn_id；turn_status 新增 awaiting_order/superseded。新轮全部派生字段重置，恢复保留。
- OrderSelection 为 TypedDict 纯数据：selection_id（UUID）、turn_id（原 user_message_id）、cards（服务器快照）、selected_order_id 或空；checkpoint_id 来自实际暂停根快照，在公开响应时补，避免在 State 里预造尚不存在的 ID。
- `prepare_order_selection(state,runtime)->dict` 准备持久化候选并设 awaiting_order；`await_order_selection(state,runtime)->dict` 只调用 interrupt 并校验返回 order_id，恢复后返回选中值及 running，无外部副作用。`remaining_active_seconds(state,*,limit:float=240)->float` 只处理已存活动耗时，不序列化 monotonic 时间戳。
- Runtime 末尾追加 order_provider/workflow_retriever/understanding/expander 等可选依赖，生产在 Task 6 明确注入；旧测试依赖形状保持。Session/模型/lease/当前 deadline 不入检查点。

- [ ] **Step 1 — RED 测试：** `test_sqlite_pause_close_reopen_resume_same_turn` 用临时真文件小图，先暂停再关连接/重开/Command 恢复；order_id 保持、模型调用零次。`test_fresh_turn_clears_selection_and_refund_offer` 不继承旧权限；`test_resume_retains_usage_and_active_time` 已消耗 30 秒则仅余 210 秒，人等待不计；`test_v1_completed_snapshot_is_readable_without_refund_permission`。

```python
assert paused.values['turn_status'] == 'awaiting_order' and paused.next
assert restored.values['order_selection']['selected_order_id'] == '1001'
assert remaining_active_seconds(saved_state) == 210
assert fresh['order_selection'] is None and fresh['refund_offer'] is None
```

- [ ] **Step 2 — 验证失败：** `uv run --locked pytest tests/test_order_selection_state.py -q`，预期旧状态不支持 awaiting_order 或新节点不存在失败。
- [ ] **Step 3 — 实现：** 准备节点把固定候选先落 State，中断节点不写用户消息、不查单、不调模型、不包宽泛 except。原生恢复只提供当前 thread_id 和 resume 值；原完成检查点可只读，未带合法选择身份的旧 pending 不可续办。
- [ ] **Step 4 — GREEN：** `uv run --locked pytest tests/test_order_selection_state.py tests/test_workflow_persistence.py tests/test_workflow_state.py -q`；真实 SQLite 重开恢复、未完成历史忽略及原工单快照测试均通过。
- [ ] **Step 5 — 留痕提交：** `feat: persist resumable order selection state`，保留本机接口签名/SQLite 版本与实际暂停证据。

### Task 5: 接通理解与订单优先子流程、条件判断

**Files:** Create `app/workflow/after_sales.py`；Modify `app/workflow/nodes.py`、`graph.py`、`agent.py`、`prompts.py`、`logging.py`、`app/core/sufficiency.py`、`app/core/prompts.py`；Test `tests/test_after_sales_workflow.py`、`tests/test_refund_decision.py`、`tests/test_workflow_gate.py`、`tests/test_workflow_agent_limits.py`。

**Interfaces:**

- 节点签名沿 `async node(state:WorkflowState,runtime:Runtime[WorkflowRuntime])->dict`。新节点 resolve_order/prepare_order_selection/await_order_selection/load_order/expand_queries/retrieve_policies；knowledge 仍为 retrieve_knowledge/confidence_gate；after_sales 是退款退货和售后的固定出口。
- `resolve_order_anchor(raw_question:str,resolved_question:str,history:list[BaseMessage])->str|None`：只消费 Task 2 可追溯实体，多个/歧义返回空；只对明确单号自动查，不自动取列表唯一项。
- `SufficiencyService.check(raw_question,evidence,*,order_context:dict|None=None)->QualityDecision`，可选参数保持旧调用。结构输出仍原协议；只增加可信订单上下文及政策是否足够做条件判断的说明。
- `AfterSalesControl`：reply_mode、suggested_actions、refund_decision（eligible/needs_review/ineligible/not_applicable）、decision_reason（1～256 非空）；普通 Agent 仍用旧 AgentControl。`make_refund_offer(state)->dict|None` 仅在有效退款意图、闸通过、answer 与 eligible/needs_review 时生成不可变许可。

- [ ] **Step 1 — RED 路由测试：** `test_faq_no_order_no_expansion`、`test_refund_loads_order_before_expand_and_policy`、`test_missing_order_interrupts_before_agent`、`test_repair_is_not_refund`。日志轨迹精确断言查单→扩写→政策→闸→Agent；FAQ 无订单/扩写，缺单暂停不调用后续节点。
- [ ] **Step 2 — RED 判断/证据测试：** 未知二次销售条件但有足够政策可返回 needs_review 和条件答复；超七天不一律否认质量保修。证据弱 Agent 调用零次、入池原话保持；依赖异常不入池。已取的订单/政策是真实本轮配对，引用只映射当前实际证据；维修+退款许可、clarification+许可等矛盾控制输出报错。

```python
assert trace.index('load_order') < trace.index('expand_queries') < trace.index('retrieve_policies')
assert trace.index('confidence_gate') < trace.index('agent')
assert weak_evidence_agent_calls == 0
assert conditional_state['refund_decision'] == 'needs_review'
assert repair_state['refund_offer'] is None
```

- [ ] **Step 3 — 验证失败：** `uv run --locked pytest tests/test_after_sales_workflow.py tests/test_refund_decision.py -q`，预期旧退款路径不查单/售后不检索失败。
- [ ] **Step 4 — 实现：** 图固定分支，理解节点消费完成 SQL 历史；查单与聚合 FAQ 使用服务器身份，日志 origin=workflow，logical calls 各加一。注入预加载事实给 Agent，强制子流程不重复开放同次 query_faq；仍允许有界读取其他必要业务信息。扩写使用订单事实，充分性判断针对规范问题+可信订单，最终 Prompt 不追问退款原因。
- [ ] **Step 5 — 预算/完成处理：** 理解、分类、扩写加入现有 UsageLedger；每阶段预留后续额度，保留充分性单列 usage。已有四工具上限含两次强制调用。log_response 在 SQL 最终答案保存后写 State 的不可变 offer；只生成许可数据，不调用退款仓储，公开发事件由 Task 6 根检查点确认。
- [ ] **Step 6 — GREEN：** `uv run --locked pytest tests/test_after_sales_workflow.py tests/test_refund_decision.py tests/test_workflow_routes.py tests/test_workflow_gate.py tests/test_workflow_agent.py tests/test_workflow_agent_limits.py -q`，关键新旧路径均通过。
- [ ] **Step 7 — 留痕提交：** `feat: route after-sales through orders and policy evidence`，说明退款判断只决定申请入口，未执行退款或提交。

### Task 6: 同轮恢复 HTTP、SSE 暂停终态与运行接线

**Files:** Create `app/workflow/order_actions.py`、`app/schemas/order_actions.py`、`app/api/order_actions.py`；Modify `app/workflow/service.py`、`app/api/streaming.py`、`app/api/chat_actions.py`、`app/main.py`；Test `tests/test_order_actions.py`、`tests/test_order_resume_lifecycle.py`、`tests/test_workflow_lifecycle.py`、`tests/test_workflow_api.py`。

**Interfaces:**

- `OrderSelectionRequest` 严格四字段 turn_id/selection_id/checkpoint_id/order_id；SQL 身份为规范十进制字符串，selection/checkpoint 为规范 UUID。不接受 owner/amount/category 替换值。
- `WorkflowChatService.prepare_resume(conversation_id:str,payload:OrderSelectionRequest)->PreparedWorkflowChat`，复用 stream/release；prepared 显式区分初始字典输入与 Command 输入，runtime 从服务器重建且沿用原用户消息。
- `OrderActionService.pending(conversation_id:str)->dict` 返回 `{pending:null}` 或选择快照；`async select(conversation_id,payload)->PreparedWorkflowChat` 调用服务预检。GET pending-order、POST actions/select-order 路径按 spec，select 返回 ManagedChatResponse。
- 新事件 order_selection/paused/refund_offer 按 spec；ManagedChatResponse 终止事件增加 paused，不能发送空 done。重复完成选单仅重放已保存事件，不启动图。

- [ ] **Step 1 — RED 生命周期测试：** `test_resume_does_not_append_user_or_reclassify`：同 user_message_id、理解/分类各一次；`test_paused_sse_closes_and_releases_lock`：paused 后 HTTP 结束、final_message_id 缺席；刷新 pending 与暂停快照一致；`test_new_message_supersedes_old_card`：旧卡 409、新轮普通字典从 START，历史完成工单许可仍可用。
- [ ] **Step 2 — RED 故障测试：** 重复并发点击只执行一次，另一请求 409；已完成同选择请求可重放，不同选择拒绝。跨会话/旧 root/伪候选拒绝；SQL 最终写入后 saver 失败时 done/refund_offer 都缺席；部分 delta 断连清理锁，恢复失败不制造完成状态；累计活动时限不清零。

```python
assert paused_events[-1].event == 'paused'
assert sum(row.role == 'user' for row in stored_rows) == 1
assert understanding.calls == 1 and classifier.calls == 1
assert stale_response.status_code == 409
assert not {'done', 'refund_offer'} & {event.event for event in failed_checkpoint_events}
```

- [ ] **Step 3 — 验证失败：** `uv run --locked pytest tests/test_order_actions.py tests/test_order_resume_lifecycle.py -q`，预期旧服务把 snapshot.next 判失败或入口不存在失败。
- [ ] **Step 4 — 实现：** 加锁后核验最新根中断及 SQL 原轮身份，恢复只用 thread_id，不以客户端旧 checkpoint 分叉。普通新消息记录 supersedes 并用输入字典开始；恢复不 append_message。暂停后保持可序列化状态并释放资源，活动段用剩余额度重建 deadline；正常完成仍先确认 SQL+根 completed，再发 actions/refund_offer/done。
- [ ] **Step 5 — 接线与边界：** main 注入同一 OrderProvider、WorkflowRetriever 与 SQL owner resolver；模型预算 wrapper 复用原 create_model。写接口复用同源 JSON guard，但 ActionRoute 错误处理只包 HTTP 预检，不能在流开始后吞 SSE 错误；GET 待选不误走要求 JSON body 的写 guard。扩充安全错误白名单，不回传异常正文。
- [ ] **Step 6 — GREEN：** `uv run --locked pytest tests/test_order_actions.py tests/test_order_resume_lifecycle.py tests/test_workflow_lifecycle.py tests/test_workflow_api.py tests/test_chat_actions.py -q`；真文件暂停重启、现有取消/锁和历史工单场景通过。
- [ ] **Step 7 — 留痕提交：** `feat: resume selected orders within the original chat turn`，记录普通消息/恢复/暂停/完成四种边界实际验证结果。

### Task 7: MySQL 待审核退款申请与显式提交

**Files:** Create `app/refunds/__init__.py`、`types.py`、`migration.py`、`repository.py`、`service.py`、`cli.py`、`sql/ch06-ddl.sql`、`app/api/refunds.py`；Modify `app/db/models.py`、`app/main.py`、`app/api/chat_actions.py`；Test `tests/test_refund_contracts.py`、`tests/test_refund_actions.py`、`tests/integration/test_refund_migration.py`、`tests/integration/test_refund_requests.py`。

**Interfaces:**

- `RefundReason` 为 Literal 六值 unwanted/quality/not_as_described/wrong_or_missing/damaged/other，标签按 spec；`RefundActionRequest` 四字段 assistant_message_id/checkpoint_id/offer_id/reason，严格禁止额外金额、状态或订单字段。
- `RefundDraft` 仅服务器构造：完整消息定位、offer_id、owner/order、amount_cents/currency、order/policy/decision 快照。`RefundRepository.create_pending(draft:RefundDraft,reason:RefundReason)->RefundReceipt`；receipt 含 request_no/status='待审核'/order_id/amount_cents/currency。
- `RefundActionService.submit(conversation_id:str,payload:RefundActionRequest)->RefundReceipt` 读取原不可变根 completed 快照、SQL 答复归属及合法 offer，再调用仓储。入口为 POST actions/refund，不放入 Agent 工具表。
- `async migrate_refunds(database:Database)->None`、`async verify_refunds(database:Database)->None`；`python -m app.refunds.cli init|verify`，默认从现有配置读取目标；仅显式 init 建表，在线启动只 verify。
- DDL/model 按 spec 全字段：BIGINT 消息外键、唯一 request_no/offer_id/pending_key、用户/订单/状态索引、六值 reason、待审核 status、整数分、JSON 快照、服务端 created_at；utf8mb4。pending_key=SHA256(规范 UTF-8 JSON 数组 `[user_id,order_id]`)，本章不释放。

- [ ] **Step 1 — RED 契约/权限测试：** 只接受四字段；缺/非法原因、额外金额/状态、跨会话 root、子图 checkpoint、未完成/clarification/维修/无 offer 一律拒绝且仓储零调用。合法申请金额与证据完全来自服务器，表单 reason 与模型决定分开。
- [ ] **Step 2 — RED 集成测试：** 真 MySQL 中相同 offer+原因重试同单号；改原因 409；同用户同订单不同会话并发仅一条 pending；不同用户同数字订单号互不冲突。模拟 commit 后丢响应重试同单；非 1062 故障不冒充成功。SQL tickets/订单/会话人工状态均未改变。

```python
assert first.request_no == retried.request_no and first.status == '待审核'
assert first.amount_cents == server_order.amount_cents and first.currency == 'CNY'
assert await count_pending(user_id='demo-user', order_id='1001') == 1
assert changed_reason.status_code == 409 and forged_amount.status_code == 422
```

- [ ] **Step 3 — 验证失败：** `uv run --locked pytest tests/test_refund_contracts.py tests/test_refund_actions.py -q`；`uv run --locked pytest tests/integration/test_refund_migration.py tests/integration/test_refund_requests.py --run-mysql -q`。后者只用现有 3308 独立测试 fixture；未启动服务应明确失败，不使用应用库代跑。
- [ ] **Step 4 — 实现 DDL/仓储：** 新表迁移仅缺表时创建，已存在核验结构，漂移拒绝；不改历史 schema/ch04 DDL。事务内锁当前 Conversation、核对 user/assistant 消息与 owner，查旧记录再插；唯一 pending_key 最终兜底跨会话竞争，1062 退出失败事务后新 Session 重读并区分同源幂等与异源冲突，不覆盖原内容。不同会话重复 offer 的返回值不得泄漏不属于调用者的申请信息。
- [ ] **Step 5 — 实现服务/API与启动核验：** 先以会话锁核对不可变完成许可，服务器构造 draft；不执行支付。完成后写安全审计，只在提交成功后返回待审核。main lifespan 复用真实 DB 只 verify，不自动 DDL；纯仓储注入测试不凭空连接数据库。
- [ ] **Step 6 — GREEN：** 重跑上列四文件，以及 `uv run --locked pytest tests/test_chat_actions.py tests/test_ticket_form.py -q`；真集成测试缺失时不得宣称退款持久化已验收。测试只清理本次自有行或随机专用库，保留其他资料。
- [ ] **Step 7 — 留痕提交：** `feat: persist user-submitted refund requests for review`，记录真实 MySQL 约束/冲突验证、无真实资金动作。

### Task 8: 聊天订单卡片与主题退款表单（Vibe Coding）

**Files:** Modify `app/static/index.html`、`chat.js`、`chat.css`；Create `scripts/verify-intent-routing-browser.cjs`；Update `docs/validation/2026-10-15-intent-routing-acceptance.md`。

**Interfaces:** 只消费 Task 6 的三种新 SSE 事件/待选读取与 Task 7 提交契约。旧 actions 仍只有 handoff/create_ticket，既有按钮和满意度/引用不改协议。

- [ ] **Step 1 — 直接实现卡片：** paused 结束本轮加载态，在聊天流显示订单摘要与可选按钮；点击 POST select-order 并复用流解析，锁定同组卡片。刷新调用 pending-order 恢复，用户新消息后旧卡失效；不将选择伪装成新的用户问句。
- [ ] **Step 2 — 直接实现表单：** 完成 offer 才显示退款入口；浅绿圆角主题弹窗，订单/金额只读，六类原因初始空白必选。取消不发请求；提交中防重；成功另起申请号/待审核气泡，失败保留原因。键盘焦点、Esc 取消和窄屏可用，不使用原生 confirm/prompt。
- [ ] **Step 3 — 浏览器验收脚本：** 复用现有 Chromium 定位/运行时探测经验，不安装新组件。受控模式从本机分段 SSE 夹具覆盖 paused/刷新/409/恢复/表单取消/成功，保存截图、请求次数和结果；真实模式连接 8003，不拦截后端事实或伪造 SQL 成功。脚本新入口 `node scripts/verify-intent-routing-browser.cjs --url http://127.0.0.1:8003/ --mode controlled|live`。
- [ ] **Step 4 — 直接浏览器检查：** 受控模式验证卡片和表单；确认取消退款零 POST、提交只有一个 POST、通知独立气泡、人工/工单原有交互不回退。turn/message ID 以字符串传递，夹具覆盖大于 JavaScript 安全整数范围的身份。无前端 TDD/代码评审波次；问题根据截图和点击结果直接修，真实落库验证见 Task 9。
- [ ] **Step 5 — 留痕提交：** `feat: add themed order selection and refund forms`，记录用户效果要求与实际截图，不把受控 UI 通过写成真实业务通过。

### Task 9: 有界模型验证、真实浏览器与交付

**Files:** Create `evals/evaluate_intent_routing.py`、`tests/test_intent_routing_evaluation.py`、`docs/validation/2026-10-15-intent-routing-acceptance.md`；Modify `README.md`、`dev-notes/ch06.md`；补充 Task 8 脚本的真实模式断言。仅必要时修复前面任务文件并保留失败记录。

**Interfaces:**

- `python -m evals.evaluate_intent_routing --mode understanding|chat --split acceptance|development --output <path>`：默认仅生成 not_executed 报告、零上游调用；understanding 加 `--live` 才调用模型。acceptance 固定 16 轮，development 32 轮；定点复验 `--case-id <id>` 只执行选中题及已有有效历史，不自动重跑前序收费调用。不接收无限 repeats 参数。
- understanding 逐轮调用真实理解/分类，历史仅由原问题、已观察输出及必要 history_fixture 事实构造，不能把 expected_query/intent 放入 Prompt；前轮失败则后轮 blocked，不用金标修复继续。chat 的 `--live --evidence <browser-results.json>` 只核验真实浏览器证据及关联 SQL/根状态，不再次发送整套聊天造成重复收费或申请；缺证据不得计为通过。两种模式的模型分数与全链路完成率分别报告。
- 报告包含样例/Prompt 哈希、模型名、实际/估算 usage、真实分母、逐轮 raw/resolved/intent/confidence/路由、错误/超时/截断/未执行，不存密钥。某步失败导致后续上下文无效则标 blocked/not_executed，不用金标替模型补上下文继续计成功。

- [ ] **Step 1 — RED 报告测试：** `test_default_evaluation_makes_zero_calls`、`test_protocol_error_stops_paid_continuation`、`test_bad_turn_not_removed_from_denominator`、`test_previous_turn_failure_does_not_inject_gold_history`，以及完整透传/实体保持/歧义零猜单指标；旧第五步结果仅历史对照，不当当前新协议通过证据。

```python
assert dry_report['counts']['total'] == 16 and dry_report['counts']['passed'] == 0
assert dry_report['model_calls'] == 0 and dry_report['counts']['not_executed'] == 16
assert failed_report['counts']['total'] == 16
assert dependent_turn['status'] == 'blocked' and dependent_turn['model_calls'] == 0
```

- [ ] **Step 2 — GREEN 离线：** `uv run --locked pytest tests/test_intent_routing_evaluation.py -q`，再运行完整 `uv run --locked pytest -q`；真实存储专项 `uv run --locked pytest tests/integration/test_refund_migration.py tests/integration/test_refund_requests.py tests/integration/test_workflow_actions.py --run-mysql -q`。仅当新代码引入 Milvus API 用法变化或未解候选问题时补对应独立集合测试，不重复全量 RAG。
- [ ] **Step 3 — 启动隔离服务：** 明确当前配置指向的数据库后显式 `uv run --locked python -m app.refunds.cli init`、`uv run --locked python -m app.refunds.cli verify`；再 `uv run --locked uvicorn app.main:create_app --factory --host 127.0.0.1 --port 8003 --workers 1`。后台启动遵守 Windows 隐藏窗口，保存 stderr 日志；不停止 8002，不变更其检查点。
- [ ] **Step 4 — 第一批真实模型：** `uv run --locked python -m evals.evaluate_intent_routing --mode understanding --split acceptance --live --output .cache/intent-routing/acceptance-live.json`。只跑固定 16 轮一次，错误/截断停止依赖链，保留所有分母；不得自动加预算、重试、换模型或扩成别的数据集。用报告确认协议/边界后才跑 development 32 轮；失败仅定点复验，不整批反复跑到通过。
- [ ] **Step 5 — 真实浏览器：** 优先 Computer Use；不可用时沿用获准的真实 Chromium 替代。执行 Task 8 live 模式，固定八组场景按 spec：政策无选单；物流→退款→物流；缺单点选续办；暂停刷新/重启/新消息失效；表单取消/提交；重复与跨会话申请；维修；投诉/问候/其他。先读取已有待审状态，已有申请则验证幂等/409及记录数不增，不删除业务行制造“新建成功”；首次新建与重复路径分别计。查询实际 MySQL 确认新增只来自明确提交，记录号、快照、未改其他状态；保存截图/日志，当前轮失败即暂停后续依赖动作。
- [ ] **Step 6 — 检查目标：** 48 轮意图 ≥46 正确、完整透传全部保持、明确可消解 ≥95%、歧义零猜单、关键路由全正确；JSON 可解析率与全链路完成率独立统计。未跑完或未达标如实列出，不从离线 fake 推断真实通过；如需改固定模型/技术方案，按用户要求先讨论。
- [ ] **Step 7 — 后端整分支审查与必要修复：** 按选定执行技能进行全分支接口/行为审查，重点看五项 Review Focus、旧完成工单、SQLite 与 MySQL 非原子边界及输入来源；前端保持用户例外，只依据浏览器验收。不将已验证任务无理由重做；修复后仅重跑受影响测试，最终代码变更后再做一次必要完整验证并分别记录结果。
- [ ] **Step 8 — 留痕与交付提交：** 更新 README 的 8003 地址、真实启动/迁移/演示命令、模型验证范围及已知边界；验收报告列具体命令/结果，不预填通过数量。每次任务与 review 结论已即时记录，最后只追加 finish。提交 `docs: record intent routing acceptance and demo commands`。
- [ ] **Step 9 — 完成分支：** 使用 verification-before-completion 和 finishing-a-development-branch，依据本章最终用户整合选择处理，不在当前计划阶段合并/推送。保留仍供用户查看的服务及必要运行资料；功能交付必须附测试结果、演示命令、标注报告与 `dev-notes/ch06.md`。

## 官方接口与执行前查证清单

设计已查证 LangGraph interrupt/Command、持久化、LangChain JSON/原始输出和 SQLAlchemy asyncio。计划补查 [FastAPI StreamingResponse](https://fastapi.tiangolo.com/advanced/custom-response/#streamingresponse)、[Pydantic strict mode](https://docs.pydantic.dev/latest/concepts/strict_mode/)、[SQLAlchemy 唯一约束](https://docs.sqlalchemy.org/en/20/core/constraints.html#unique-constraint)。官方 LangGraph reference 的一次 aget_state 深链读取失败，执行时以已可用的[持久化文档](https://docs.langchain.com/oss/python/langgraph/persistence)、项目现有调用及锁定安装包签名核对，不当作接口缺失或换框架依据。

Task 4/6 先核对本机 `interrupt/Command/CompiledStateGraph.astream/aget_state` 和官方 SQLite 生命周期；Task 3 复用现有 HybridMilvusIndex.recall，不引入新 Milvus API；Task 7 核对 AsyncSession.begin/唯一键失败后回滚重读；Task 6 核对 ManagedChatResponse 中 pause 终止和预检错误不会在 response.start 之后重新写 HTTP 状态。所有来源、锁定版本与实际签名追加到开发记录。

## 计划自审与实施交接

覆盖关系：设计 1～3→Task 1/2；4→Task 3/5；5～6→Task 4/6；7→Task 5/7；8→Task 8；9→Task 4/5/6；10→Task 2/9；11→各 API 任务前置查证。九项任务均有明确输入/输出和可验证结果；Review Focus 五项分别落到命名测试或真实存储/浏览器验收。

自审修正：恢复输入与普通新轮输入分开，GET 待选不误复用写入 guard；新扩写不塞进旧 QueryPlan.expansions 的 64 字符契约；额外检索审计不突破原 evidence payload；退款唯一键处理跨会话竞争；暂停 checkpoint_id 从真实快照取得；预加载工具占用原工具上限；真实模型分批与未执行分母明确。无待定接口或实现占位。

计划批准后按保留的 Subagent-Driven 方式逐任务实施，前端 Vibe Coding 例外。书面计划尚未批准前，只提交本计划和阶段记录，不编写产品代码、安装依赖、执行迁移或调用真实模型。
