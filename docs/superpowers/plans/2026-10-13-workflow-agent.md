# Workflow 与主力 Agent Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 将现有客服聊天接入确定性 Workflow 和多步 Agent，保留检索质量守卫、SQLite 持久化以及独立的人工/工单操作。

**Architecture:** 外层 StateGraph 固定七类意图到四条路径，知识类先检索过闸，主力 Agent 是循环子图。MySQL 保存业务和可回放消息，AsyncSqliteSaver 保存图状态及完成回复的操作快照；只有最终正文流向用户。先交付无 LangGraph 的裸循环，再以相同控制组件构造正式子图。

**Tech Stack:** Python 3.11–3.13、FastAPI 0.142.2、SQLAlchemy 2.0.54、现有 MySQL/Milvus/BGE、LangChain Core 1.6.6、LangGraph、官方 SQLite checkpointer、原生 HTML/CSS/JavaScript。

**Spec:** [已批准设计](../specs/2026-10-13-workflow-agent-design.md)，用户于 2026-10-13 批准。计划状态：已完成自审，等待用户审阅；执行方式沿用已明确选择的 Subagent-Driven，不重新询问。

## Global Constraints

- 新工作树 .worktrees/workflow-agent，分支 feat/workflow-agent；提交标题不使用 ch 前缀。工作树在计划获批后的执行阶段创建，不在本计划阶段安装依赖。
- 官方 AsyncSqliteSaver，默认 runtime/workflow/checkpoints.sqlite；整个 runtime/workflow/ 忽略，检查点不进 static 或 Git。单实例、单 Uvicorn worker 验收。
- 七意图固定为物流、订单、商品咨询、退款退货、售后、投诉、闲聊；明确问候/感谢/告别全轮零模型调用，其他输入使用模型 JSON 分类。resolve_reference 原样透传。
- 知识类强制检索和置信度闸必须先于 Agent/最终 delta；业务不预检索；投诉不进 Agent、不自动动作；最终引用继续可定位原文。
- 工具每个申请消息最多一个，parallel_tool_calls=False；最多4次逻辑调用、5次决策、1次最终生成。ToolExecutor 已有重试至多1次，query_faq 90秒/0重试。
- 输入预算沿用8000，Agent累计32000，控制/意图JSON上限2048，最终回答512；整轮240秒、原GLM/端点/零模型重试不变。保留原线上重排门槛与 query/self-check 预算。
- Agent 不暴露 create_ticket；按钮明确确认才执行原工具。转人工是纯前端模拟，创建工单不再自动改变会话为已转人工。旧按钮依赖旧完成快照，可跨后续轮次使用。
- 所有新增/修改函数有中文说明，UTF-8；每阶段/任务完成即时追记 dev-notes/ch05.md 的原话、产出、纠偏、返工。
- 每个涉及具体库/API的任务在动代码前查询Context7，记录库ID、版本、接口和来源；Task3核对LangGraph/SQLite，Task6补FastAPI lifespan/ASGI/DI，Task7补SQLAlchemy事务和LangChain隐藏调用ID。已查的接口不无故重复查询；官方文档例外仅沿用先前允许的故障回退。
- 后端任务执行 RED → GREEN；纯Prompt/标注用样例验证，页面做真实浏览器交互验收。本计划不启动300题RAG评估，不读出/提交真实.env。
- 依赖候选锁定 langgraph==1.2.15、langgraph-checkpoint-sqlite==3.1.2。PyPI只读元数据确认二者共同要求 langgraph-checkpoint>=4.3.0,<5；LangGraph要求langchain-core>=1.4.7,<2。实际解析必须保持现有直依赖版本，若冲突停下说明，不擅自升级模型栈。[LangGraph发布](https://pypi.org/project/langgraph/1.2.15/)、[SQLite发布](https://pypi.org/project/langgraph-checkpoint-sqlite/3.1.2/)。

## Review Focus

1. “你好，订单1001到哪了”不能误命中问候直出；没有型号的使用求助不能当库外拒答——Task4/5固定回归。
2. 第一轮有知识/动作，下一轮没有时不能继承旧证据、旧按钮许可或token计数——Task3/6检查每轮初始化。
3. SQL已提交而SQLite失败，或浏览器收到部分delta后断开：不得发done、误显示可点击动作或留下会话锁——Task6故障注入。
4. 旧回复按钮在新消息后点击、重复POST、伪造跨会话checkpoint：只允许原完成回复的操作且至多一张工单——Task7/8。
5. 第二次工具调用、非法参数、重复参数和缺usage会触发旧单次协议或预算漏洞——Task1/2/5，保留工具错误关联与有界停止。

---

## 文件与接口分工

app/agent/controls.py、bare.py、cli.py 是无 LangGraph 的循环控制与教学演示；app/workflow/state.py、runtime.py、persistence.py 定义图状态、运行依赖和存储；intent.py、nodes.py、graph.py 定义外层路径；agent.py 定义循环子图；service.py、actions.py 分别负责聊天生命周期和已确认操作。

现有 core/tool_history.py/records.py 支持多步回放，core/evidence.py 增加多结果证据装配而不破坏旧入口。api/streaming.py 仅放宽服务类型为协议，api/chat.py/主应用接入新服务。tickets.py 解除转人工耦合；chat.js/chat.css 加多徽章和独立按钮。原 tool_chat.py 及旧评估器不整体重写。

以下命令在计划获批后新工作树根目录执行，PowerShell先设置 `$env:PYTHONUTF8='1'`。`uv run --locked`不隐式更新依赖；Task3首次同步后各任务默认离线pytest，只有Task9明确调用真实模型。没有Makefile，不使用不存在的make dev。

### Task 1: 多步消息回放与预算保持完整轮次

**Files:** Modify app/core/tool_history.py、app/repositories/records.py；Test tests/test_tool_history.py、tests/test_multi_tool_history.py。

**Interfaces:** Consumes现有MessageRecord/record_from_message/message_from_record。Produces原签名不变的completed_turns(rows)->list[list[BaseMessage]]、build_tool_messages(...,current_tool_messages=...)->list[BaseMessage]，支持N组严格顺序申请/结果。

- [ ] **Step1: 写失败测试**，使用现有selected_call和ToolMessage创建两步/四步轮次；断言以下接口，而非只检查数量：

```python
assert [m.type for m in completed_turns(rows)[0]] == ['human','ai','tool','ai','tool','ai']
assert [m.tool_call_id for m in result if isinstance(m, ToolMessage)] == ['call_1','call_2']
assert completed_turns(rows_with_wrong_second_id) == []
assert completed_turns(rows_with_duplicate_call_id) == []
assert completed_turns(rows_without_final_answer) == []
assert all(m.content != 'old turn' for m in budgeted)  # 只整轮删历史
```

- [ ] **Step2: RED** `uv run --locked pytest tests/test_multi_tool_history.py -q`，预期原实现无法回放两步轮次，出现断言失败。
- [ ] **Step3: 最小实现** `_validate_turn`允许 user +(申请/结果)*N +最终AI，pending允许缺最后AI；全轮调用ID唯一，每个结果匹配紧邻申请。completed_turns去掉三条截断；非法组停到下一user。保留旧两条/四条兼容，records仅改“每个申请消息”的说明，不允许一个AI并发多工具。
- [ ] **Step4: GREEN** `uv run --locked pytest tests/test_multi_tool_history.py tests/test_tool_history.py tests/test_budget.py tests/test_evidence.py -q`，零失败；覆盖非法JSON/不支持角色、当前必需数据超预算和旧单工具路径。
- [ ] **Step5: 提交与留痕** 只stage本任务文件与dev-notes/ch05.md，`git diff --cached --check`后commit `feat: replay complete multi-tool conversations`。

### Task 2: 裸 Agent 循环、共享停止控制与演示

**Files:** Create app/agent/__init__.py、controls.py、bare.py、cli.py；Create tests/workflow_fakes.py、tests/test_bare_agent.py、tests/test_agent_controls.py；Modify app/config.py、.env.example。

**Interfaces:** ConsumesToolCall/ToolOutcome/ToolExecutor/BaseTool和Task1完整消息预算。Produces：

- `AgentLimits(max_tool_calls:int=4, total_token_budget:int=32000, max_decisions:int=5, final_output_tokens:int=512)`；`UsageLedger`含actual/estimated开销和剩余预算。
- `parse_tool_selection(reply:AIMessage, registry:Mapping[str,BaseTool])->ToolCall|None`：合法结束、真实raw镜像、ID/名称/对象参数校验；完整参数Schema由执行器校验并返回错误结果。
- `reserve_call(messages, tool_schema, ledger, *, output_limit:int, final_reserve:int)->None`拒绝超预算；`record_usage(reply,ledger, *, estimated_input:int, output_limit:int)->None`检查非负usage，无合法usage时保守估算；重复签名按工具名+排序紧凑JSON参数计算。
- `async run_bare_agent(model, registry, executor, messages:list[BaseMessage], *, limits:AgentLimits)->BareAgentResult`，结果含answer、工具轨迹、usage和stop_reason。
- `ScriptedWorkflowModel`受控替身：独立记录intent、decisions、streams和bind参数；支持给定AI响应队列、final_chunks、阻塞/异常，并保留旧模型替身不改其生产含义。

- [ ] **Step1: 写失败测试** test_bare_two_calls_then_answer、test_repeat_call_never_executes_twice、test_four_call_limit、test_missing_usage_is_estimated、test_reserves_final_budget、test_invalid_args_returns_matched_tool_message，关键断言：

```python
assert result.calls == ['query_order','query_logistics']
assert len(model.tool_inputs[-1]) >= 5
assert result.answer == '受控物流答案'
assert result.stop_reason == 'repeat_call' and executor.calls == 1
assert executor.calls == 4 and result.stop_reason == 'step_limit'
assert ledger.source == 'estimated' and ledger.spent > 0
assert 'langgraph' not in imported_by_bare  # 只检查裸模块的导入依赖
```

- [ ] **Step2: RED** `uv run --locked pytest tests/test_bare_agent.py tests/test_agent_controls.py -q`，预期缺循环/控制实现失败，不依赖真实网络。
- [ ] **Step3: 实现循环与配置** while循环调模型，有申请就执行并加完整配对，无申请就返回文本；复用执行器、步骤/重复/预算控制。新增AGENT_MAX_TOOL_CALLS=4、AGENT_TOTAL_TOKEN_BUDGET=32000、AGENT_DECISION_MAX_OUTPUT_TOKENS=2048、INTENT_MAX_OUTPUT_TOKENS=2048，拒绝bool/非有限/非正配置，工具上限不得配置超过4；不改既有MAX_OUTPUT_TOKENS。
- [ ] **Step4: 实现CLI** `python -m app.agent.cli demo`默认受控query_order→query_logistics，无模型请求。`demo --live --question '...'`才使用既有GLM与原查询工具；不开放create_ticket、不创建假用户/工单，真实演示只需无数据库依赖的三个查询工具。
- [ ] **Step5: GREEN** `uv run --locked pytest tests/test_bare_agent.py tests/test_agent_controls.py tests/test_config.py tests/test_tool_executor.py -q`及`uv run --locked python -m app.agent.cli demo`；输出两步轨迹和受控最终答案，停止测试零额外执行。
- [ ] **Step6: 留痕提交** `feat: demonstrate a bounded bare agent loop`，记录裸循环产出、RED/GREEN和未调用真实模型。

### Task 3: State、运行依赖与真实 SQLite 检查点

**Files:** Create app/workflow/__init__.py、state.py、runtime.py、persistence.py；Modify pyproject.toml、uv.lock、.gitignore、.env.example、app/config.py；Create tests/test_workflow_persistence.py、tests/test_workflow_state.py。

**Interfaces:**

- WorkflowState为TypedDict，字段固定为conversation_id、user_message_id、raw_question、resolved_question、category、intent、route、messages、evidence_payload、citations、quality、tool_trace、suggested_actions、decision_count、tool_call_count、usage、reply_mode、final_answer、final_message_id、turn_status。消息列表顺序更新，不使用累加reducer。
- `new_turn_state(*, conversation_id:str, user_message_id:int, raw_question:str, category:str|None, messages:list[BaseMessage])->WorkflowState`，每轮清空证据、质量、建议、计数、结果；字符串SQL消息ID稳定。
- WorkflowRuntime为运行期dataclass，含model/decision_model/intent_model、repository、faq_repository、sufficiency、quality_repository、registry、executor、settings、deadline、upstream；连接/Session/lease不放State。
- `@asynccontextmanager async open_checkpointer(path:Path)->AsyncIterator[AsyncSqliteSaver]`；`checkpoint_config(conversation_id:str, *, checkpoint_id:str|None=None)->RunnableConfig`只派生可信thread_id/root namespace；`checkpoint_path(settings:Settings, project_root:Path)->Path`不随cwd漂移。

- [ ] **Step1: 写失败测试** test_sqlite_reopen_recovers_state、test_old_snapshot_survives_new_turn、test_state_reset_does_not_keep_evidence_or_actions、test_invalid_path_fails_without_memory_fallback，关键断言：

```python
assert restored.values['final_message_id'] == '104'
assert old.values['suggested_actions'] == ['handoff','create_ticket']
assert fresh['evidence_payload'] == {} and fresh['suggested_actions'] == []
assert fresh['tool_call_count'] == 0 and fresh['final_message_id'] is None
assert 'model' not in saved.values and 'deadline' not in saved.values
```

- [ ] **Step2: 查询/锁定依赖** 在安装前用Context7查所选版本的StateGraph、Runtime context、custom流、durability和AsyncSqliteSaver；核对官方源码。加两个精确版本，`uv lock`检查diff无旧直依赖升级，`uv sync --locked`。若冲突说明具体约束，不换后端/框架。
- [ ] **Step3: RED** `uv run --locked pytest tests/test_workflow_persistence.py tests/test_workflow_state.py -q`，预期应用状态/生命周期接口未实现失败；不能只用InMemorySaver证明持久化。
- [ ] **Step4: 最小实现** 默认WORKFLOW_CHECKPOINT_PATH=runtime/workflow/checkpoints.sqlite；父目录创建、全运行目录忽略；官方异步context manager管理连接。测试编译只有保存状态的小图，以durability=sync执行，关连接重新打开同文件读旧checkpoint_id。无写权限/损坏明确失败，不自动回退内存。
- [ ] **Step5: GREEN** 上述两个测试和`uv run --locked pytest tests/test_config.py -q`；`uv tree`确认版本、`git check-ignore runtime/workflow/checkpoints.sqlite`命中，关连接后无挂起任务。
- [ ] **Step6: 留痕提交** `feat: persist workflow state with async sqlite checkpoints`，记录实际锁版本和最小异步兼容验证，不宣称在线服务已接入。

### Task 4: 外层分流、强制 RAG 和置信度闸

**Files:** Create app/workflow/intent.py、nodes.py、graph.py、prompts.py；Create evals/workflow_intent_cases.jsonl、tests/test_workflow_routes.py、tests/test_workflow_gate.py；Modify app/core/evidence.py、tests/workflow_fakes.py。

**Interfaces:** ConsumesTask3状态/运行依赖、现有FAQRepository.retrieve、SufficiencyService、QualityRepository。Produces `IntentClassifier(model, *, input_budget:int, timeout_seconds:float)`、`async classify(raw_question:str)->Intent`；`social_fast_path(raw_question:str)->bool`；`route_intent(intent:Intent)->Literal['knowledge','business','complaint','social']`；`build_workflow_graph(agent_graph:CompiledStateGraph, *, checkpointer:BaseCheckpointSaver)->CompiledStateGraph`。

节点签名为`async node(state:WorkflowState, runtime:Runtime[WorkflowRuntime])->dict`；节点名严格沿spec。graph在此任务可用受控空Agent子图验证外层，下一任务替换为真实Agent子图。

证据扩展签名`build_agent_evidence(*,system:SystemMessage, turns, current:HumanMessage, current_tool_messages:list[BaseMessage], payloads:list[dict], budget:int)->EvidencePacket`；复用既有完整块/编号/首尾排布逻辑，保留build_evidence旧签名及测试。当前工具结果与证据内容均计费；SQL审计原结果不因展示编号而改写。

- [ ] **Step1: 写失败测试** test_all_seven_routes、test_greeting_with_order_is_not_social、test_weak_knowledge_never_enters_agent、test_business_empty_evidence_bypasses_gate、test_complaint_has_two_options_no_tools、test_new_turn_drops_previous_evidence；断言：

```python
assert [route_intent(x) for x in ['商品咨询','退款退货','物流','订单','售后','投诉','闲聊']] == ['knowledge','knowledge','business','business','business','complaint','social']
assert social_fast_path('你好') and not social_fast_path('你好，订单1001到哪了')
assert trace == ['resolve_reference','classify_intent','retrieve_knowledge','confidence_gate','knowledge_fallback','log_response']
assert agent_calls == 0 and refusal_source == 'retrieval_low_conf'
assert retrieval_calls == gate_calls == 0 and agent_calls == 1  # 业务路径
assert actions == ['handoff','create_ticket'] and ticket_writes == 0
```

- [ ] **Step2: RED** `uv run --locked pytest tests/test_workflow_routes.py tests/test_workflow_gate.py -q`，节点与路由尚未存在。
- [ ] **Step3: 实现分类与固定节点** 透传原话；整句闲聊regex使用spec固定话术。模型JSON严格枚举/extra forbid/raw stop，无非法降级；分类及检索以当前raw_question/category为可信源。投诉固定安抚；常规路径统一到log_response，真正提交逻辑通过Runtime仓储执行。
- [ ] **Step4: 实现强制检索/闸/证据** Workflow生成query_faq申请配对并标origin=workflow；空/低分提前兜底，达标才内容自评，业务路径不执行两节点。故障保留error而非写拒答池。证据去重依据chunk_id，合并后按同一重排分排序取至多10块再按预算整块选择；编号是最终Prompt集合，业务混合工具结果必须同样保留。
- [ ] **Step5: Prompt样例验证** 21题七类各3，另加带问候业务、投诉优先、缺型号使用求助；包含期望intent/route与“应追问”标记。先离线校验ID和分桶，不用字符串关键字直接冒充模型分类质量。
- [ ] **Step6: GREEN** `uv run --locked pytest tests/test_workflow_routes.py tests/test_workflow_gate.py tests/test_evidence.py tests/test_answer_citations.py -q`；强制检索先于delta/Agent的顺序断言通过。
- [ ] **Step7: 留痕提交** `feat: route customer requests through guarded workflow`，记录分类Prompt样例和路由/闸结果。

### Task 5: 主力 Agent 循环子图与流式收敛

**Files:** Create app/workflow/agent.py；Modify app/workflow/prompts.py、runtime.py、app/core/answer_validation.py；Create tests/test_workflow_agent.py、tests/test_workflow_agent_limits.py、tests/test_workflow_agent_quality.py。

**Interfaces:** ConsumesTask2控制器/Task3 State和Runtime/Task4证据。Produces`build_agent_graph()->CompiledStateGraph`，子图compile(checkpointer=None)使用父图每次调用持久化；llm_call/tool_node/finalize_answer使用Task4节点签名。

AgentControl严格Schema：reply_mode=answer|clarification，suggested_actions为handoff/create_ticket去重列表、长度最多2、extra forbid。parse控制JSON沿现有validate_structured_output/raw结束验证，不接受工具调用和控制正文混杂。决策由2048模型输出，最终由原512模型astream。

- [ ] **Step1: 写失败测试** test_agent_two_sequential_tools、test_final_stream_hides_control_json、test_usage_help_asks_for_product、test_ticket_never_in_bound_tools、test_business_faq_checks_new_evidence、test_knowledge_does_not_query_faq_twice；断言：

```python
assert trace_names == ['query_order','query_logistics']
assert state['tool_call_count'] == 2 and model.stream_calls == 1
assert 'create_ticket' not in bound_names
assert all('reply_mode' not in e.data.get('delta','') for e in events)
assert state['reply_mode'] == 'clarification' and low_confidence_writes == 0
assert '商品' in final and '型号' in final
assert quality_checked_before_first_delta and all_citations_belong_to_current_turn
```

- [ ] **Step2: RED** `uv run --locked pytest tests/test_workflow_agent.py tests/test_workflow_agent_limits.py tests/test_workflow_agent_quality.py -q`，预期缺Agent图/收敛实现。
- [ ] **Step3: 实现决策/执行条件边** 真实绑定现有读工具，依intent排除create_ticket和已预检索的query_faq；调用和结果逐个SQL保存，推custom status。query_faq入参归一沿现有trusted question防幻造，追加证据必须过闸。错误结果匹配调用并计数；查询服务外部故障保持服务error。
- [ ] **Step4: 实现终止与收敛** 4/5/1上限、recursion_limit=32、重复签名、完整输入预留最终预算、usage估算；决策不泄露正文。限额用固定未完成提示+handoff建议，不做虚假成功。缺参问句无知识事实；知识final必须有效引用，业务结果保留mock含义。final流复用text_delta/结束/引用守卫并随取消关闭。现有非事实句式守卫只补充产品求助的明确追问和纯应答开头，使“可以的，你买的是什么商品或型号？具体在哪一步不会操作？”合法；不把任意含问号的句子判为追问，不扩大旧SufficiencyService的空证据放行规则。
- [ ] **Step5: 追加限制失败测试** 参数错误回灌后能修正但总调用不超4；负usage回退估算；无finish/length/异常不commit；第二轮只带完整历史，无旧质量绕过；步数停止保留完整配对。追问后附“可以退货”“已发货”“三天到账”均被非事实守卫拒绝，不能借clarification绕过证据。`uv run --locked pytest tests/test_workflow_agent.py tests/test_workflow_agent_limits.py tests/test_workflow_agent_quality.py tests/test_bare_agent.py tests/test_tool_executor.py tests/test_answer_citations.py tests/test_online_chat_reliability.py -q`全部通过。
- [ ] **Step6: 留痕提交** `feat: orchestrate the main agent as a bounded react subgraph`，分别记录简单/复杂/缺参/限制路径的调用次数。

### Task 6: 聊天入口、终态提交与检查点生命周期

**Files:** Create app/workflow/service.py、logging.py；Modify app/main.py、app/api/chat.py、app/api/streaming.py、tests/fakes.py；Create tests/test_workflow_api.py、tests/test_workflow_lifecycle.py；Modify tests/test_chat_api.py中仅用于旧传输契约的client装配。

**Interfaces:** `PreparedWorkflowChat`含conversation_id/user_message_id/lease、state、runtime、deadline；`WorkflowChatService(model, repository, registry_factory, locks, settings, *, graph, checkpointer, faq_repository, sufficiency_service, quality_repository, executor=None)`提供`async prepare(conversation_id:str,message:str,*,category:str|None=None)->PreparedWorkflowChat`、`stream(prepared)->AsyncIterator[StreamEvent]`、`release(prepared)->None`，以同一协议兼容ManagedChatResponse。registry_factory沿旧接口消费ToolContext、返回dict[str,BaseTool]，runtime和budgeted模型由服务按本轮组装。

新增SSE载荷固定为`actions: {"assistant_message_id":"104","checkpoint_id":"<官方检查点UUID>","options":[{"action":"handoff","label":"转人工"},{"action":"create_ticket","label":"建工单"}]}`。选项可为空/一个/两个但不得重复；label由服务固定映射，不能来自模型任意文本。无建议不发送actions，旧done仍为`{"conversation_id":"1","message_id":"104"}`。

status.phase保持selecting/checking/answering/tool_running/tool_completed白名单，阶段内多次工具状态有独立ID；origin是可选固定workflow|agent附加字段，未经识别的phase不可直接转发。citations每轮只在第一delta前发一次，最多10条；内部阶段和LLM控制过程仅写节点日志。

create_app新增显式可注入chat_service/checkpointer，默认生产路径在lifespan中用Task3创建SQLite并装配Workflow。测试注入依赖由测试自己关闭；旧ToolChatService传输测试显式注入旧服务，不允许依据模型替身能力在产品代码偷偷回退。新增默认应用测试必须证明默认选择Workflow。

- [ ] **Step1: 写失败测试** test_default_app_uses_workflow、test_social_zero_model_calls、test_sql_commit_then_checkpoint_then_done、test_sql_success_checkpoint_failure_no_done、test_disconnect_releases_every_resource、test_restart_new_input_never_resumes_failed_tools；断言：

```python
assert model.all_requests == 0 and frames[-1][0] == 'done'  # 你好
assert trace.index('commit_final') < trace.index('checkpoint_complete') < trace.index('done')
assert 'done' not in names and 'actions' not in names and names[-1] == 'error'
assert saved_final_count == 1 and no_new_tool_executions_after_restart
assert locks.acquire('1') is not None  # 测试随后release
assert final_snapshot.next == () and final_snapshot.values['turn_status'] == 'completed'
```

- [ ] **Step2: RED** `uv run --locked pytest tests/test_workflow_api.py tests/test_workflow_lifecycle.py -q`，当前默认单次聊天服务不满足路由/检查点要求。
- [ ] **Step3: 实现prepare/stream** 预检预算/会话锁在启动SSE前；读取SQL完整轮次，检测旧检查点但新问题显式新输入从START跑。图custom只转发status/citations/delta，不自动转发messages。正常图结束后aget_state检查本轮ID/status/空next，获得checkpoint_id，再产生actions、done。done仍是原conversation_id/message_id两个键。
- [ ] **Step4: 接入lifespan与日志** 资源在AsyncExitStack按逆序退出；运行流有Task管理，shutdown有界取消后关闭SQLite；Runtime deadline全轮同一monotonic期限。无恢复收费调用、无跨请求共享可变证据。finally在ASGI2.3/2.4、发送失败、慢关闭均释放lease，5秒shield清理沿原响应层。
- [ ] **Step5: GREEN与旧边界回归** `uv run --locked pytest tests/test_workflow_api.py tests/test_workflow_lifecycle.py tests/test_chat_api.py tests/test_stream_lifecycle.py tests/test_hybrid_lifecycle.py tests/test_network_stream.py -q`。迁移旧HTTP装配只保留传输测试的原断言；新默认应用覆盖路由真实行为，不能删失败测试以回避行为变化。
- [ ] **Step6: 留痕提交** `feat: serve checkpointed workflows through the chat stream`，记录SQL/SQLite非原子故障、断开和重启的实测，不声称收到delta就是完成。

### Task 7: 已确认工单入口、可信旧快照和动作解耦

**Files:** Create app/workflow/actions.py、app/api/chat_actions.py、app/schemas/chat_actions.py；Modify app/repositories/tickets.py、app/main.py；Create tests/test_chat_actions.py、tests/integration/test_workflow_actions.py；Modify tests/integration/test_business_repositories.py中旧自动转人工断言。

**Interfaces:** `TicketActionRequest(assistant_message_id:str,checkpoint_id:str)`严格forbid额外字段/BIGINT字符串/有界checkpoint_id；`TicketActionService(graph,repository,registry_factory,executor,locks)`的`async create_ticket(conversation_id:str,payload:TicketActionRequest)->dict`返回ticket_no/status。POST路径按spec，不允许客户端传question/description/type/user_message_id或tool_name。

- [ ] **Step1: 写失败测试** test_suggestion_creates_nothing、test_old_completed_offer_after_new_message、test_cross_conversation_checkpoint_denied、test_duplicate_confirmation_returns_one_ticket、test_ticket_does_not_transfer_conversation、test_extra_or_bad_origin_writes_nothing；断言：

```python
assert tickets_before == tickets_after_suggestion
assert response1['ticket_no'] == response2['ticket_no'] and ticket_count == 1
assert conversation_status == '进行中'
assert forbidden.status_code in (403,404,409,422) and writes == 0
assert call.name == 'create_ticket' and call.id == f'ui_ticket:{assistant_message_id}'
assert call.args == {'description': trusted_description, 'ticket_type': '投诉'}
```

- [ ] **Step2: RED** `uv run --locked pytest tests/test_chat_actions.py -q`；独立MySQL测试在Task9前启动3308固定测试库后运行，原仓储会错误转人工。
- [ ] **Step3: 实现校验/调用** 按thread_id/root namespace+请求checkpoint_id只读aget_state，要求completed/next空/final_message_id匹配且suggested_actions允许；SQL核对user/assistant属于当前会话。原话从可信快照/SQL校验后取描述，超长截2000且含截取标记。intent投诉→投诉，退款退货/售后→售后，其余→咨询；稳定ui_ticket:replyID调用现有工具和执行器。
- [ ] **Step4: 实现写接口边界** JSON并验证Origin等于请求可信的本机Host/scheme或配置白名单，拒绝外部/null来源；无Origin的本机CLI仅允许明确loopback Host。沿现有错误白名单，不泄露异常。会话lease阻止同时写消息/工单，重复请求在完成后仍返回同编号；已结束会话不新建工单但可读幂等结果。
- [ ] **Step5: 解除工单转人工耦合并验证** 删除自动status赋值及对应旧说明；不改编号哈希/短事务/并发唯一性。`uv run --locked pytest tests/test_chat_actions.py tests/test_business_tools.py tests/test_tool_executor.py -q`；`uv run --locked pytest tests/integration/test_business_repositories.py tests/integration/test_workflow_actions.py --run-mysql -q`一张工单且会话未转人工。
- [ ] **Step6: 留痕提交** `feat: create tickets only from confirmed reply actions`，记录旧快照、重试幂等和转人工零后端调用。

### Task 8: 多工具徽章、独立按钮与现有引用/反馈兼容

**Files:** Modify app/static/chat.js、chat.css、index.html；Create scripts/verify-workflow-browser.cjs；Create docs/validation/workflow-browser-checklist.md。

**Interfaces:** 消费status中的tool_call_id/tool_name/status，actions中的assistant_message_id/checkpoint_id/options；只允许handoff/create_ticket。每条助手回复有独立Map工具徽章和动作状态，不用当前会话全局ID覆盖旧按钮；done后才激活动作。

- [ ] **Step1: 建立浏览器验收脚本** 用真实Chromium页面、受控SSE/写接口记录覆盖下面交互，先对现有页面运行以看到缺按钮/第二徽章失败；不把JS静态字符串匹配当页面验收。脚本支持`--url`和`--mode controlled|live`，controlled只拦截明确聊天/工单接口，live不拦截真实模型/工具。
- [ ] **Step2: 实现多徽章与actions解析** 按call_id维护多个标识，停止/断开时将未完成徽章标为结果未确认；origin=workflow显示检索而不是伪称Agent选择。严校actions身份、选项、重复帧和顺序；保存建议但done之前不显示可点击按钮。
- [ ] **Step3: 实现两独立确认交互** 手工确认可用浏览器原生confirm。handoff确认只在页面插入两句指定文案且锁自己的按钮，零fetch；ticket确认才POST固定同源接口，成功显示编号锁自己的按钮，失败允许重试。取消确认不锁定、不写数据；两个都不点继续正常聊天。文案与模型数据用textContent，不执行HTML。
- [ ] **Step4: 浏览器验收** 两步查询有两个徽章；投诉初始零POST；取消/确认人工零工单请求、两句文案准确；确认工单一次POST、不展示已转人工；旧回复新消息后仍可点击；失败能重试；error/断开无按钮；引用原文弹窗和👍/👎一次锁定仍可用。窄屏不挤出输入框，键盘焦点可用。
- [ ] **Step5: 执行命令并留证** `node scripts/verify-workflow-browser.cjs --url http://127.0.0.1:8002/ --mode controlled`，脚本输出各场景pass/fail，截图存在.cache/workflow-browser/；实际浏览器路径来自当前机器探测，不把机器绝对路径写成唯一代码常量。Task9另跑live。
- [ ] **Step6: 留痕提交** `feat: show independent support actions and multi-step tool traces`。本次用户没有给第五步前端免TDD/免审查例外，但行为是低成本原生页面改造：受控浏览器失败/通过作为交互验证，不写逐行镜像单测。

### Task 9: 有界真实验收、全分支检查和交付

**Files:** Create evals/evaluate_workflow.py、tests/test_workflow_evaluation.py、docs/validation/2026-10-13-workflow-agent-acceptance.md；Modify README.md、dev-notes/ch05.md；完善scripts/verify-workflow-browser.cjs的live证据导出。

**Interfaces:** `python -m evals.evaluate_workflow --mode intent|chat --output <path>`，intent使用Task4固定标注集逐题单次，无重试；chat固定spec场景，记录原问题/实际intent/node/tool调用/合法结束/用量/引用/工单增量/错误，并与真SQL自有ID对照。报告不给模型金标作生成上下文。

- [ ] **Step1: 离线报告契约验证** 确认错误/截断/超时和知识拒答分别统计，标题声明真实或受控模式，覆盖21题+边界分类样例；测试`tests/test_workflow_evaluation.py`断言调用数、未执行、误分类和错误不会被写成通过，默认不调用模型。
- [ ] **Step2: 最终离线/集成检查** `uv run --locked pytest -q`完成一次必要完整回归；再运行Task7真实MySQL专项和实际SQLite重启测试，保留skip原因及计数。若新修改影响边界再补对应专项，不重复已通过大规模评估。`git diff --check`；逐个新增/修改函数检查中文说明及UTF-8。
- [ ] **Step3: 启动隔离验收实例** 已有8001先保持；新工作树复制本机已授权忽略.env、不输出密钥，确认真实merchant集合/原校准值不变，检查8002空闲后以隐藏进程启动：`uv run --locked uvicorn app.main:create_app --factory --host 127.0.0.1 --port 8002 --workers 1`。PID和日志放忽略缓存；不会停止不属于本次启动的进程。
- [ ] **Step4: 真实模型/浏览器固定验收** intent标注逐题各一次；`node scripts/verify-workflow-browser.cjs --url http://127.0.0.1:8002/ --mode live`执行spec政策/物流/复杂两步/投诉/零模型闲聊/使用求助/MH-LP200/库外样例和按钮组合。每轮限制240秒，首次失败停止受影响验收并定位，不以换模型/加预算/重复全量试跑蒙混通过。
- [ ] **Step5: 重启与持久性验收** 关闭仅自有8002进程，等待资源释放，重开同SQLite；同会话继续发送，SQL无重复旧turn，读取旧操作checkpoint并可确认工单。可保留自有验收业务记录以便用户复查，不删除整个表或知识集合。
- [ ] **Step6: 分支审查与收尾** 用requesting-code-review做整分支review，涉及bug按systematic-debugging定位，修复后相关回归；该阶段的修复范围与审查波次按实际技能执行，不预先承诺无限重跑。记录真实命令、通过/失败/skip、两步工具SQL和节点证据、SQLite重开与截图路径，不用旧1531通过数字冒充本次结果。
- [ ] **Step7: 提交交付** README加裸循环demo、单worker启动、实际前端地址及SQLite/MySQL职责。开发记录立即补验收/审查/finish。相关验证通过后提交 `docs: document workflow agent validation and usage`，按finishing-a-development-branch及本会话实际授权处理合并/推送；任何未完成验收明确列出，不能宣称第五步已完成。

## 自审与执行交接

覆盖映射：spec1/2→全局约束和Task1/6；spec3→Task2；spec4/5→Task4；spec6→Task2/5；spec7→Task3/6/7；spec8→Task1/6；spec9→Task7/8；spec10/11→Task3/9。Review Focus五条均有对应失败测试和验收。

签名核对：父图使用build_workflow_graph(build_agent_graph(),checkpointer=...)；Runtime与State字段统一；HTTP只依prepare/stream/release，操作接口只读历史完成快照；done字段不扩展。旧接口仅显式DI保留测试，不作为默认生产路径降级。

任务大小核对：依赖安装包含在SQLite可持久化交付任务；多步历史、裸循环、存储、固定分流、Agent、入口生命周期、工单授权、浏览器页面分别可独立验证和审查。没有悬空函数/待定技术项/通用“处理边界”占位。测试示例是需实现的断言约束，不把本文当作已经运行过的测试报告。

计划审阅获批后，用using-git-worktrees在已获授权的隔离方式创建工作树，再按用户已选Subagent-Driven逐任务执行；当前工作区只保存设计/计划/记录，产品开发尚未开始。
