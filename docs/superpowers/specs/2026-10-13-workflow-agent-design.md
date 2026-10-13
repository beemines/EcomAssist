# 第五步设计：确定性 Workflow 与主力 Agent

日期：2026-10-13。状态：设计稿已完成自审，等待用户审阅；尚未编写实施计划或修改产品代码。

## 1. 目标、已确认选择和范围

把现有 SSE 客服从“一次工具调用后回答”升级为外层确定性 Workflow、内层可循环 Agent。知识问题必须先检索并过置信度闸，业务问题由 Agent 自选查询工具；投诉和闲聊有明确的固定路径。用户要能看懂裸 Agent 循环，再看到同样的逻辑如何放进 LangGraph。

用户已确认：

- 明确问候、感谢、告别先由规则识别，整轮零模型调用；其余问题由简单 Prompt 分类。
- 外层 Workflow 固定分流，主力 Agent 是内部循环子图；同时改造多步历史回放和多工具徽章。
- 最新截图指令“用这个”选择 AsyncSqliteSaver，覆盖此前“检查点必须也存 MySQL”的偏好。检查点保存到独立 SQLite 文件；现有 MySQL 继续保存业务表。
- Context7 暂不可用时允许查官方文档。该服务现已恢复，已补查 LangGraph、检查点和 LangChain 工具接口。

固定技术为 FastAPI、SQLAlchemy、Docker MySQL、现有 Milvus/BGE 检索器、LangChain 工具、LangGraph、原生 HTML/CSS/JavaScript。沿用现有 GLM 模型、上游地址、零模型重试和最终回答 512 token 上限。新增 LangGraph 和官方 SQLite 检查点依赖，具体兼容版本在实施计划中核对并锁定。

本次 SQLite 和现有会话锁按本地单实例、单 worker 验收。架构分层和控制流按用户目标改造，但不把 SQLite 方案宣称为已经通过多实例生产负载验收。官方 AsyncSqliteSaver 文档也明确其写入性能边界。

本步不升级正式意图识别、指代消解、上下文管理，不接 MCP、真人客服系统或飞轮入库；不改四策略评估算法，不重新跑 300 题付费评估。新增的建工单入口复用现有工具，不新增业务工具。

分支采用 feat/workflow-agent，提交标题不使用 ch 前缀；dev-notes/ch05.md 按本次用户明确要求保留。每个新增或修改函数保留中文用途说明，文件采用 UTF-8。

## 2. 现有实现的必要改动

基线为 master 的 198138c：

- ToolChatService 限制每轮一次工具调用，必须由 Workflow 服务接替在线聊天入口。
- tool_history 只接受两条普通消息或四条单工具消息，需要接受多组顺序工具申请和结果。
- records 的“一个申请消息只能有一次调用”仍可保留，但错误说明改为每个申请消息而非整轮。
- 前端只有一个工具徽章，需要按 tool_call_id 保存多个徽章并接受回答前的连续执行状态。
- TicketRepository.create 目前同时修改会话为“已转人工”，必须解除耦合。
- 现有证据编号、首尾排布、引用校验、低置信度池、SSE 断开清理、会话锁和完整回复落库继续复用。

旧 ToolChatService 的直接单元测试与评估器仍可保留，正式 /api/chat 使用新服务；不另建第二套检索引擎或工单实现。

## 3. 裸 Agent 与 LangGraph 的关系

先实现独立教学模块和命令行入口，不依赖 LangGraph：

1. 组装 System Prompt、问题和已完成历史，绑定现有查询工具。
2. 调 LLM；有工具调用则严格校验名称、参数和调用编号。
3. 执行工具，加入对应的 AIMessage 和 ToolMessage，再调 LLM。
4. 没有工具调用则返回最终回答；达到步数、重复调用或预算限制则停止。

该模块保留在仓库供走读，默认用可重复的受控模型演示两步调用，显式选项才调用真实上游。只复用业务工具与执行器，不把教学模块接入在线 HTTP 服务。

随后用 LangGraph 的条件边表达同一循环。工具校验、计费、停止规则提取为可复用组件，教学示例和正式子图不能各自定义一套冲突规则。正式服务为满足流式回答和独立操作建议，区分内部决策和最后的文本生成。

## 4. 外层 Workflow 和固定分流

节点链为 START → resolve_reference → classify_intent → route_intent，之后按下表分流，全部正常路径汇入 log_response → END。

| 意图 | 路径 | 约束 |
| --- | --- | --- |
| 商品咨询 | retrieve_knowledge → confidence_gate → agent 或 knowledge_fallback | 先检索、闸后才能回答 |
| 退款退货 | retrieve_knowledge → confidence_gate → agent 或 knowledge_fallback | 政策证据通过后，Agent 可继续查订单 |
| 物流 | agent | 不预检索、不走知识闸 |
| 订单 | agent | 同上 |
| 售后 | agent | 缺商品、型号或故障描述时追问 |
| 投诉 | complaint_response | 不调用 Agent、不自动执行任何操作 |
| 闲聊 | social_response | 固定话术；规则命中的明确闲聊整轮零模型调用 |

resolve_reference 原样透传，State 同时保存 raw_question 和 resolved_question。此处不承诺“继续”“那个”等指代已经解决。

明确闲聊规则只匹配整个问题，不能因“你好，订单 1001 到哪了”含问候就提前返回。其余输入由简单意图 Prompt 输出严格 JSON：{"intent":"七类之一"}，拒绝未知值、额外字段、工具调用、截断和非正常结束。非法输出与上游超时是服务错误，不冒充闲聊或知识拒答。

分类边界写入 Prompt 和标注样例：政策、规格属于商品咨询或退款退货；已购商品不会使用、设备故障属于售后；明确表达投诉诉求归投诉；没有订单号的订单查询仍走业务路径，由 Agent 追问。分类暂不细分多意图，但带明确投诉诉求优先归投诉。

闲聊固定返回“您好，我是 MewHelp 智能客服，可以帮您查询订单、物流以及商品和售后问题。”投诉固定安抚，并建议“转人工”和“建工单”两个选项，不写工单、不改变会话状态。

## 5. 强制检索与置信度闸

retrieve_knowledge 直接调用现有 FAQRepository/retrieval service，传可信的当前问题和已校验 category，不让模型决定是否检索。沿用 hybrid_rerank、现有问题理解、Milvus RRF、bge-reranker-v2-m3、Top-10、整块证据预算和首尾排布。

这次检索属于 Workflow 行为。消息审计可采用服务器生成的 query_faq 申请/结果配对，但必须在节点日志标明 origin=workflow，不能宣称这次工具是 Agent 自己选择的。申请编号由服务器生成，入参契约不变。

confidence_gate 在任何最终回答 delta 前执行：

- 没有证据或真实重排分低于当前已校准门槛，直接 knowledge_fallback，不调用主力 Agent。
- 分数达标后复用第四步内容充分性自评；useful=false 同样不进入 Agent。
- 固定兜底明确资料不足，复用 QualityRepository 将用户原话、会话、来源和理由落入低置信度池。
- 数据库、嵌入、向量库或模型调用故障走 error，不记成“知识不足”。

保留现有线上门槛和自评预算，不拿 BM25/RRF 分数冒充重排分，也不套评估消融模式来绕过线上闸。业务数据类不存在预检索证据，不能因为 evidence 为空就被闸拒答。

知识类进入 Agent 后已有本轮证据，查询工具列表不重复开放 query_faq；可继续查订单等业务信息。业务类可使用原 query_faq 工具处理进一步需要知识的子问题；该工具结果通过同一证据检查后才允许生成知识事实。新的合法证据统一编号、去重，引用以最终实际装入 Prompt 的证据为准。

## 6. 主力 Agent 子图、追问和停止条件

子图为 llm_call → should_continue → tool_node → llm_call；不再调用工具时进入 finalize_answer，随后返回父图。

每次只允许一个逻辑工具调用，bind_tools 明确关闭 parallel_tool_calls。物流、订单、商品、FAQ 都复用现有 @tool 和 ToolExecutor。create_ticket 不放进模型可执行的工具列表；它只在用户明确确认的按钮接口中执行。

llm_call 的工具选择不向前端输出正文。有工具调用时，保存真实申请和结果、推送 status；无工具调用时以严格 JSON 给出 reply_mode（answer 或 clarification）和 suggested_actions（handoff、create_ticket 的去重子集）。这段控制输出不作为用户答案或思维链展示，也不写成可见助手消息。

finalize_answer 关闭工具，按控制结果生成普通文本并逐 token 推送。知识答案必须基于通过闸的当前证据并引用；业务答案基于工具返回值，不承诺模拟数据是商家真实业务。clarification 只能请求缺失信息，不补造订单号、型号或政策，也不因缺商品型号而把问题写入低置信度知识池。

停止与预算默认值：

- 每轮最多执行 4 次逻辑工具调用；工具自身已有的有界重试仍属于同一次调用。
- 同名工具加规范化参数重复出现时停止，不重复执行；无效参数和执行错误作为对应 ToolMessage 回灌，也计入逻辑调用次数。
- 最多 5 次决策调用和 1 次最终生成；图另有有限 recursion_limit 作为防线。
- 每次输入沿用 TOOL_INPUT_TOKEN_BUDGET（默认 8000）；决策 JSON 和意图 JSON 的输出上限默认 2048，最终可见回答沿用 512。
- Agent 累计输入与输出预算默认 32000，真实 usage 优先；缺 usage 时采用现有保守估算并标注 estimated。每次调用前计入完整消息和工具 Schema，并预留最终回答所需预算，不把这个数字宣称为精确费用上限。
- 整轮沿用 CHAT_TIMEOUT_SECONDS（默认 240），每次上游和工具还受剩余期限约束；重启后不沿用旧 monotonic 时间值。

达到步数、重复调用或预算门槛时退出循环，返回明确的未完成提示和可选人工入口，不编造“查询成功”。上游非法结束、超时、取消属于 error；这些错误不通过 done 宣称成功完成。

有信息缺口就追问。例如“新买的商品不太会用，能帮我看看吗？”必须询问商品/型号以及卡在哪一步；不能继续显示知识不足的固定拒答。用户下一轮补充具体设备后，现有完整历史能让 Agent 接着处理；正式指代消解仍在下一步。

## 7. State、检查点与 MySQL 的职责

WorkflowState 保存可序列化字段：会话和原用户消息 ID、原话/透传问题、category、intent、route、messages、证据、质量决定、工具轨迹、建议操作、调用计数、用量、final_answer、final_message_id 和本轮状态。运行期模型客户端、Session、连接池、执行器、锁、上游流和密钥只放 Runtime/服务依赖，不进入检查点。

本图顺序执行，messages 使用显式整列表更新，避免历史重新装载后被 reducer 重复累加。数据库消息赋稳定 ID；内部控制 JSON 不混进用户消息历史。每个新问题重新置空上一轮证据、动作、终态和计数。

应用 lifespan 通过 async with AsyncSqliteSaver.from_conn_string(...) 持有连接，父图 compile 时传 checkpointer。子图采用每次调用作用域并继承父图检查点，不自己创建另一套持久化。只使用异步接口；按锁定版本核对 durability="sync"，完成节点状态保存后才确认整轮完成。

默认文件为 runtime/workflow/checkpoints.sqlite，由明确配置控制；父目录可创建，文件、WAL 和 SHM 都在 Git 忽略的同一运行目录，不放 static，不提交到远程。路径以项目目录为基准，不随终端 cwd 漂移；应用退出先结束受控运行再关闭 SQLite。

checkpointer thread_id 由已验证的 MySQL conversation_id 派生，不接受浏览器任意另传线程。MySQL 仍是聊天消息、工单和低置信度记录的权威源；SQLite 保存图状态、节点进度和该轮的操作建议快照。

重启后的继续聊天从 MySQL 已完成轮次与检查点恢复身份和状态。不自动重放失败或未完成节点，不调用 ainvoke(None) 恢复收费模型或工具执行。发现 interrupted 状态时记入日志，新问题从 START 开始；上一轮孤立申请/结果不作为完整历史回放。

MySQL 和 SQLite 不是跨库原子事务。log_response 用短 MySQL 事务提交最终答复并返回 ID；图结束后服务确认对应的完成检查点，再发送 actions/done。若 MySQL 已提交而检查点保存失败，发 error、不发 done；重启后以已完成 SQL 消息为准恢复，不重复执行旧轮。断开前已经送出的文本不代表后台整轮已完成。

## 8. 多步消息回放和日志

完整轮次支持 user → (assistant 工具申请 → tool 结果)重复 N 次 → assistant 最终文本。每个申请严格匹配对应 tool_call_id，按 SQL 主键顺序回放；缺结果、重复编号、错序或半轮不进入历史。

继续按整轮淘汰最旧历史，当前问题、全部本轮申请/结果和必要证据不能单独裁成孤立消息。必需部分超预算则明确失败或受控停止，不通过只删工具结果来凑预算。

结构化节点日志保存 turn/user_message_id、节点名、intent、route、通过/拒绝理由代码、调用编号和名称、耗时、用量、终态。必须能证明政策走到 retrieve_knowledge、业务绕过 gate、复杂问题的工具先后关系。默认不记录完整原话、证据全文、模型内部控制正文、密钥或思维链。

所有正常路径经过 log_response。异常、取消、断开在外围 finally 记录终态，关闭上游流并释放会话 lease；不要求错误时继续跑生成节点或保存半个助手回答。

## 9. SSE 和独立操作按钮

保留 status、citations、delta、done、error，新增 actions。只将明确的节点事件转换成 SSE；不直接把 LangGraph 所有 messages 事件转发，否则意图和内部决策也可能流向用户。

多个 status 按 tool_call_id 显示多个徽章，执行状态只出现在最终正文之前。citations 在第一段最终正文前发布，编号映射保持第四步交互。actions 只在回复已验证、MySQL 已提交、完成检查点已确认后发送，紧接 done；error 和 done 都是终态，之后无新事件。

actions 数据包含当前 final_message_id、完成快照的 checkpoint_id，以及 handoff/create_ticket 选项与展示说明。无建议时不出现按钮。前端不得执行模型给出的 URL、脚本或任意工具名，只渲染两个固定白名单选项。

转人工：点按钮经确认后，前端展示“已转接人工客服”和“您好，我是客服小猫，请问有什么可以帮您的”。该按钮不发建工单 HTTP 请求、不写 tickets、不自动改 MySQL 会话状态。按钮独立锁定，页面仍可继续发送消息。

建工单：点击后先显示独立确认，再 POST /api/conversations/{conversation_id}/actions/ticket，JSON 只含 assistant_message_id 和 checkpoint_id。服务按当前会话读取指定完成检查点，验证快照确有 create_ticket 选项、答复及原用户消息均属于本会话，不能信任浏览器提供描述或工单类型。

描述由原问题的前 2000 字生成，过长时明确标注截取；类型由快照 intent 映射为投诉/售后/咨询。调用稳定编号由 assistant_message_id 派生，因此重复点击、响应丢失后重试均复用同一张工单。接口调用现有 create_ticket @tool 和 ToolExecutor；工单仓储仅创建工单，不同步转人工。

成功返回 ticket_no/status，前端显示“工单已创建”和编号，只锁定建工单按钮。失败显示可重试错误，不误报已完成。旧回复的按钮在新消息后仍能使用，其权限来自旧的完成快照，而非当前轮全局变量。

按钮操作在结构化日志里记录原问题和答复 ID、确认动作、工单编号及结果；不插入孤立 ToolMessage 污染聊天回放。两个按钮都不点击则零动作；仅点其中一个也不连带执行另一个。

新增写接口采用 JSON 和现有同源来源校验模式，拒绝异常 Origin；不存在/不匹配快照、未完成回复或未提供选项均拒绝且不写工单。完整公网账户鉴权不在当前本机开发验收范围内。

## 10. 验收与验证范围

后端先 TDD，Prompt/分类用标注样例验证，页面用真实浏览器验收。一次真实验收失败只定位受影响链路，不以整套 300 题重跑代替排查。

| 场景 | 期望行为和证据 |
| --- | --- |
| 退货政策是什么 | 日志含强制检索和置信度闸；有依据时回答并可点引用 |
| 订单 1001 的物流到哪了 | 直接 Agent，自选 query_logistics，回灌后流式回答 |
| 先查订单 1001 的状态，再按订单查物流 | 两次独立决策、query_order → query_logistics，两个徽章和两组 SQL 申请/结果 |
| 我要投诉 | 固定安抚、两个独立按钮；出现按钮时 tickets 不增加 |
| 只点转人工 | 两句模拟效果；tickets 不增加，建工单按钮仍独立可用 |
| 只点建工单并确认 | 写一张 tickets；重复请求只返同编号；不出现已转人工 |
| 投诉后不点按钮，继续问物流 | 原按钮不自动执行，继续正常业务路径 |
| 你好 / 谢谢 / 再见 | 固定话术，模型调用总数为零 |
| 新买的商品不太会用，能帮我看看吗 | 追问商品/型号和使用问题，不返回知识不足兜底 |
| MH-LP200 能装多少猫砂 | 当前真实知识库回答 12L，引用定位商品规格原文 |
| 库外知识问题 | 闸前拒答、不进 Agent；原话进入低置信度池 |
| 原会话完成后重启，再发消息 | SQLite 状态可读；会话继续，SQL 历史不重复，旧操作快照仍可校验 |

离线专项测试覆盖七类固定路由、问候包含业务内容不误判、弱证据不调用 Agent、业务空证据不被拒答、多步协议、缺参追问、重复调用和步数/预算停止、非法 JSON/finish_reason、跨会话快照拒绝、工单幂等、两个动作互不影响、SQLite 重开文件、MySQL/检查点失败和 SSE 断开清理。

真实分类样例至少覆盖七类各三题，记录实际标签、误分和非法输出；不为追求通过率更换模型或静默扩大预算。真实聊天验收使用当前 merchant 知识集合，数据库验证只检查本轮自有会话、消息和工单，不删除其他数据。

完成后交付裸循环演示命令、应用启动命令、聊天页实际地址、真实浏览器截图/结果、相关测试结果和 dev-notes/ch05.md。提交/合并/推送按照会话授权和实际完成状态处理，设计阶段不声称功能已完成。

## 11. API 查证与设计自审

已通过 Context7 MCP 查询 LangGraph StateGraph、条件边、子图检查点继承、流事件，以及 LangChain bind_tools/AIMessage/结构化输出。部分生成示例的 await/async with 用法不准确，已以官方源码核对，不能直接复制示例。

官方依据：

- [AsyncSqliteSaver 源码和生命周期](https://github.com/langchain-ai/langgraph/blob/main/libs/checkpoint-sqlite/langgraph/checkpoint/sqlite/aio.py)
- [LangGraph 持久化](https://docs.langchain.com/oss/python/langgraph/persistence)
- [LangGraph 流式输出](https://docs.langchain.com/oss/python/langgraph/streaming)
- [Workflow 与 Agent](https://docs.langchain.com/oss/python/langgraph/workflows-agents)
- [检查点后端选择](https://docs.langchain.com/oss/python/langgraph/checkpointers)

依赖锁定后还需按实际版本查询具体 API 和做最小离线兼容测试，尤其是 aget_state 的 checkpoint_id、子图作用域、Runtime context、durability 和 custom 流，避免把最新文档签名套到不匹配版本。

设计自审：七类意图全部有固定出口；知识闸在正文流之前；业务无预检索；明确闲聊零模型调用；创建工单从 Agent 工具列表移除且与转人工解除耦合；SQLite 与 MySQL 的非原子边界、重启行为和资源责任明确；多步历史、徽章、引用和终态协议一起改造；没有待定技术项或预算占位。

本文是待用户审阅的设计，后续实施计划必须单独形成和审阅，不把此前方向确认当作尚未存在的计划已获批准。
