# Workflow Agent 有界验收（2026-10-13）

当前代码分支为 `feat/workflow-agent`，基线 `83ea49620bb710e559947475229b7b5910ea1b21`。**第五步尚未完成：2026-10-14复验中知识/12L来源/库外拒答已通过；物流决策错误选择澄清模式导致最终校验失败，两步和使用求助停止。**该轮HEAD为`316d0cc`，完整离线1782通过/118跳过；后续模式修复不能冒用这次旧HEAD结果。原分类、独立按钮和重启证据继续保留，下面分轮列事实。

## 初轮验证（原始事实保留）

| 类型 | 本次结果 | 命令 / 原始证据 |
| --- | --- | --- |
| 报告契约 RED | 6 failed；缺少验收模块断言 | `pytest tests/test_workflow_evaluation.py -q`；`.cache/task-9-red.txt` |
| 报告契约 GREEN | 6 passed，4.39秒 | 同上；`.cache/task-9-green.txt` |
| 场景语义 RED/GREEN | 5 failed /6 passed →11 passed，4.29秒 | `.cache/task-9-semantic-red.txt`、`task-9-semantic-green.txt` |
| 失败子图账本 RED/GREEN | 1 failed /11 passed →12 passed，4.75秒 | `.cache/task-9-ledger-red.txt`、`task-9-ledger-green.txt`；只补对应报告回归 |
| 完整离线 | 1748 passed、118 skipped，319.70秒 | `uv run --locked pytest -q`；`.cache/task-9-full-offline.txt` |
| 真实独立MySQL3308与SQLite重开 | 10 passed，7.32秒，无skip | `pytest tests/integration/test_workflow_actions.py tests/test_workflow_persistence.py -q --run-mysql -rs`；`.cache/task-9-mysql-sqlite.txt` |
| 受控真实Chromium | 25/25 PASS | `node scripts/verify-workflow-browser.cjs --url http://127.0.0.1:8002/ --mode controlled`；`.cache/task-9-browser-controlled.txt` |
| 真实意图分类 | 24/24正确，21调用；3题社交零调用；0错误/超时/截断/未执行 | `python -m evals.evaluate_workflow --mode intent --live --output .cache/task-9-live-intent.json`；同名txt |

完整离线的118项跳过真实MySQL/Milvus集成，显式专项验证只运行本次两项工单与8项官方SQLite持久性测试。其他真实集成不由这10项结果宣称通过。裸循环默认演示实际执行订单→物流，`stop_reason=completed`，输出用量10202来自估算，未调用真实模型。

## 真实环境与边界

使用主checkout已授权的当前merchant忽略`.env`原字节复制到工作树，两份SHA256相等。没有字面名为merchant.env的文件；依据当前主checkout部署配置和2026-10-12交付记录确认来源。公开配置为 `knowledge_merchant_live`、门槛 `0.3218679428100586`、`glm-5.3-flash`、online low、最终512、控制/意图2048、输入8000、Agent累计32000、整轮240秒、FAQ90秒零重试；检索改写/充分性原独立上限与期限保持。密钥不记录、不提交。真实意图命令有一次LangChain检测到系统代理的custom HTTP transport警告，原文保存在txt；未据此换设置、模型或重试。

隐藏隔离实例：`uv run --locked uvicorn app.main:create_app --factory --host 127.0.0.1 --port 8002 --workers 1`。初始uv启动PID56500，Uvicorn PID93344，health为ok；netstat显示8001原PID58816保持。日志在`.cache/task-9-server.stdout.log`、`task-9-server.stderr.log`；只允许关闭本次证明归属的8002进程。

32000账本范围仅含记录的意图+Agent决策/最终；query改写与充分性仍受各自原预算和共同期限约束，未算入该账本。未启动300题RAG，不改变模型/端点/校准值，不自动重试或重复完整真实试跑。

## 真实浏览器、SQL与重启

真实Chromium唯一固定试跑：`node scripts/verify-workflow-browser.cjs --url http://127.0.0.1:8002/ --mode live`，Playwright **1.59.1**，Chromium1234（受控此前文档1.62.1为旧环境描述，本次以实际加载输出为准）。run-id `3cccc1a8-be81-486e-9f8d-1fc588a9dec8`，原SSE、页面请求、按钮前后SQL及截图保存在`.cache/workflow-browser/live/<run-id>/`。脚本未拦截任何live请求。

| 固定场景 | 自有会话 | 结果 / 实际证据 |
| --- | --- | --- |
| 退货政策 | 25 | ERROR，强制FAQ完整SQL配对；公开running→completed含success→checking，无delta/done/actions。SQLite根已通过confidence_gate，quality.useful=true；子图首次llm_call记录invalid_structured_output，未到finalize_answer。 |
| 订单1001物流 | 26 | ERROR，Agent首次决策选query_logistics并实际成功，SQL一组申请/结果；子图下一llm_call记录invalid_structured_output，decision_count=1，未进入最终生成。 |
| 两步订单→物流 | — | NOT_EXECUTED，首次业务失败停止；不能宣称有两步真实SQL证据。 |
| 投诉 | 27 | PASS，按钮出现时SQL零工单；取消两个确认零新增HTTP；转人工确认零新增HTTP且两句固定文案；随后明确工单确认一POST，SQL一单、原投诉描述，状态仍进行中。 |
| 你好 | 28 | PASS，固定话术，无工具，实际根用量四项全零。 |
| 缺型号使用求助 | — | NOT_EXECUTED，业务链路已停止。 |
| MH-LP200 | — | NOT_EXECUTED，知识链路已停止；未验证12L/真实引用。 |
| 库外知识 | — | NOT_EXECUTED，知识链路已停止；不能计为知识拒答。 |

固定8场景：**4尝试、2通过、2错误、4未执行、0拒答/超时/截断**。补充只建工单会话29、未确认重启offer会话30均PASS，因此浏览器总10场景为**4PASS、2FAIL、4NOT_EXECUTED**。会话29只确认工单后仅该按钮锁定，未出现人工转接文案；会话30重启前未点击确认，SQL零工单。没有以受控25项通过或24题分类通过填补真实聊天未执行项。

只读复核命令：`python -m evals.evaluate_workflow --mode chat --live --evidence .cache/workflow-browser/live/3cccc1a8-be81-486e-9f8d-1fc588a9dec8/results.json --output .cache/task-9-live-chat.json`。它读取既有SSE、真实SQL与官方根/子图SQLite，未再次请求聊天模型。主8场景已持久化账本合计4次，其中物流子图包含分类+一次成功工具决策的2次；失败调用本身用量未保存，**4不能当全部收费调用数**。query改写/充分性调用也不在该账本。失败阶段通过`.cache/task-9-first-failure-checkpoints.json`定位；原始无效模型JSON、字段、finish_reason未保留，故不能猜测确切上游内容或宣称已修复。最小后续建议是经控制器许可定点记录Agent控制响应以诊断，未在本次增加收费探针、重试、换模型或放宽Schema。

截图已人工读取：`policy.png`显示知识检索成功徽章和明确结构错误、无动作；`complaint.png`显示两个独立完成结果；`complaint-ticket-only.png`显示人工按钮仍可用、仅真实工单编号完成。布局完整，输入框可见，错误未变成普通回复。

同SQLite重启：核对初始自有控制台PIDs56500/34228/96976/93344与信号工具110208后只发送Ctrl+C，日志完整记录Shutting down / Application shutdown complete / Finished server；8002释放后再启动隐藏uv PID87144，Uvicorn PID61352。8001 PID58816一直保持。当前8002为这次重开的自有实例，入口仍为`http://127.0.0.1:8002/`。

会话30重启后通过真实HTTP发送“谢谢”，**模型调用0**，原两条消息主键/内容保持，SQL只增加一对用户/最终助手，2→4，无旧turn重复。旧根checkpoint `1f1c70cc-242a-60cc-8004-0c7cf5f15b90`仍可读并校验原操作；原message身份的工单确认两次返回同一 `T43c1497dbbf6b6c71a3b5fc4a884db4`，SQL仅一单，描述为原投诉、会话状态进行中。`.cache/task-9-restart-proof.json`保存前后全部自有SQL、原SSE、两次请求结果和新旧checkpoint；`.cache/task-9-stop-owned.txt`、server/restart日志保存归属与关闭证据。本项证明同会话HTTP接续与后端旧按钮授权，前端尚无加载旧历史能力，未声称重开页面恢复原UI按钮。

## 审查与收尾

实现者按implementer-prompt自审，不派评审子代理。整个分支的独立审查、最终集成/推送由控制器负责；本报告不将尚未执行的审查或合并写为完成。

交付保留本次会话25–30、三张明确确认的自有工单与SQLite快照，供复查；没有清整个业务表、知识集合或其他会话。工具/文档可以审查，真实Agent控制协议故障仍阻塞完整第五步验收。

## 2026-10-14：审查修复后的固定复验

Task5决策/最终Prompt隔离、Task9 SQL配对与引用选择均通过scoped审查后，在`316d0cc`执行一次固定复验。用户通过`call_ec17b619fb6146cca74f82144b55b462`明确允许同一.env GLM的固定场景及修复后定点复验，发送测试问句/FAQ/模拟结果，保持每轮240秒、原预算、零重试、不跑300题。先前自动审批拒绝发生在启动前0调用；新明确许可后原命令获准，没有绕过拒绝。

仅自有8002旧控制台87144/99844/45716/61352及停止工具96416核对后Ctrl+C，日志正常关闭；同.env SHA256、同SQLite隐藏重开，uv78840/Uvicorn99840、healthok。8001原PID58816未动。当前8002仍为这次自有实例，后续模式修复需要再次仅重启它。

完整离线一次：`uv run --locked pytest -q`，显式`WORKFLOW_BROWSER_CONTRACT=1`包含真实受控后置容量引用点击，**1782 passed、118 skipped、370.44秒、exit0**。完整输出已读，`.cache/task-9-final-full-offline.txt`无失败；118skip保持未启用真实MySQL/Milvus等资源集成原因。真实3308/SQLite的10项专项沿前次已通过证据，不重复运行。此完整套件属于本轮HEAD，模式再次修复后须另列相应覆盖。

唯一真实固定脚本run `a08d00ad-3bd5-4d98-9bf1-dc5b00af375b`，原命令`node scripts/verify-workflow-browser.cjs --url http://127.0.0.1:8002/ --mode live`；浏览器汇总**7PASS、1FAIL、2NOT_EXECUTED，exit1**。经过加强后的只读SQL/官方SQLite导出，主8场景为**6尝试、4通过、1预期知识拒答、1错误、2未执行**；拒答不混为模型错误或一般回答通过。

| 场景 / 自有会话 | 本轮实际结果 |
| --- | --- |
| 政策 /31 | PASS；SQL136用户→137 FAQ申请→138结果→139最终，逻辑工具1、决策1、已记录模型3次。成功经过检索/闸/Agent/最终提交；实际点击来源[4]为签收7天退货原文。 |
| 物流 /32 | ERROR；SQL140用户→141 query_logistics申请→142结果，工具成功但无最终助手SQL、无done/actions。最终正文明确模拟并给已揽收/MOCK11540677/2天，随后invalid_answer。 |
| 两步 | NOT_EXECUTED；首个业务失败后停止，未声称两组真实SQL已经通过。 |
| 投诉 /33 | PASS；SQL143/144，建议出现前零工单，独立确认后仅Tcc00f0083a27753f5641f86ec104a8b、会话进行中。 |
| 闲聊 /34 | PASS；SQL145/146，零工具、用量四项全0。 |
| 使用求助 | NOT_EXECUTED；业务链路停止，待定点验收。 |
| MH-LP200 /35 | PASS；SQL147→148FAQ→149结果→150最终；回答12L，实际打开[1]商品规格原文明确型号MH-LP200、猫砂容量12L。引用匹配真实SQL/最终引用，无首条假设放宽。 |
| 库外 /36 | EXPECTED REFUSAL；SQL151→152FAQ→153结果→154固定拒答；不进Agent，低置信池id7保存完整原话，source=retrieval_low_conf。 |

补充只建工单/37 PASS，仅明确确认后单号T485d8193eab72a4b17725af5fe237f9、无转人工文字；未确认旧offer/38 PASS、SQL零工单。原会话30同SQLite重启、谢谢零模型、旧checkpoint工单幂等的证明继续复用，因为Prompt/验收器修复没有改持久化或动作授权。保留所有原始25–30及新31–38数据，不删整表/集合。

物流根因仅做本地无收费重建：子图`agent:a579e0df-1ac6-6719-b630-bf000b085320`最新状态`decision_count=2`、`reply_mode=clarification`、`quality={}`、`selected=None`；根状态尚未接收子图结果，reply_mode为null。严格AgentControl要求reply_mode且无默认值，llm_call直接写模型解析值，因此是本次模型错误选择澄清，不是适配器默认。最终packet带“回复模式：clarification”；finalize据此构造clarification质量决策，实际包含物流事实的delta触发非事实守卫。用真实delta、相同packet及`{'stop'}`离线重放，复现完全相同`invalid_answer / 社交或澄清回复包含未验证内容`。`.cache/task-9-final-logistics-local-diagnosis.json`保存packet/子图/原delta；无新模型调用。

主8场景已持久化账本11次，物流最终失败调用自身用量未持久化、usage_complete=false，**11不是全供应商收费次数**。32000仍只含已记录意图+Agent决策/最终；委托query改写/充分性按原独立cap/deadline运行，排除在该账本外。没有重复24题分类、完整试跑或增加诊断；错误后只继续独立知识/投诉/社交路径。下一步由原Task5修复模式指令并审查，随后只定点物流/两步/使用求助，不重跑已通过项。

原始与本轮JSON/SSE/SQL/截图各自保持：`.cache/workflow-browser/live/<各run-id>/`；本轮导出`.cache/task-9-final-live-chat.json`、`.cache/task-9-final-live-chat.txt`。已人工查看MH-LP200、库外、物流截图：12L与引用可见，预期拒答显示转人工入口；物流错误有红色说明、无反馈/动作，未误写普通成功。

## 2026-10-14：模式修复后的三项定点续验

生产模式修复5f98563通过审查后，选择器600ccc7785c3ed8345cc7d2402696ba4175eb6ed只增加固定主场景 --cases，原默认与语义/来源/SQL门槛不变。聚焦TDD 5失败→41通过，等号误用前置拒绝另5通过；未重复full、25项受控全批或意图24题。

旧8002链78840→35900→38816→99840及停止工具110612核对后优雅关闭，shutdown complete后才隐藏重开同.env/SQLite。当前uv17620/Uvicorn7308、healthok；8001仍58816。日志/归属在`.cache/task-9-targeted-stop-owned.txt`、`task-9-targeted-server.*`。

直接人类许可call_ec17b619fb6146cca74f82144b55b462覆盖固定场景及修复后定点续验；引用其原话后执行一次 `D:/vue/node.exe scripts/verify-workflow-browser.cjs --url http://127.0.0.1:8002/ --mode live --cases logistics,two-step,usage-help`，run `1e35ffad-79e3-4c75-bfb1-98f5be22c0d9`。原模型/预算/240秒/零重试保持，未选政策、投诉、社交、MH、库外及两个附加项均NOT_EXECUTED；使用求助因两步首次业务失败停止，未调用。

- 物流39：PASS。SQL159用户→160 query_logistics申请→161同ID成功结果→162最终，reply_mode=answer、决策2、工具1，严格SQL配对无误，正常done。已持久化4次/2320用量，usage_complete=true。
- 两步40：ERROR。SQL163用户→164/165 query_order→166/167 query_logistics，两组同ID工具配对按顺序成功，页面有两个成功徽章；最终正文却给订单金额及物流结果加[1]/[2]，SSE citations=[]，触发invalid_answer_citations，无最终SQL、无done/actions。已持久化4次/2949用量，失败最终调用用量未入账、usage_complete=false。

浏览器**1PASS/1FAIL/8NOT_EXECUTED，exit1**；严格只读导入主8分母**2尝试/1通过/1错误/6未执行，exit1**。导入命令 `python -m evals.evaluate_workflow --mode chat --live --evidence .cache/workflow-browser/live/1e35ffad-79e3-4c75-bfb1-98f5be22c0d9/results.json --output .cache/task-9-targeted-live-chat.json`。只读取既有SSE/MySQL/官方SQLite，零新增模型请求。8次账本不是全部收费数；32000范围仍限已记录intent+Agent，委托query/充分性不混入。

本地零模型重建`.cache/task-9-targeted-two-step-local-diagnosis.json`证明子图reply_mode=answer、packet.citations=[]，同一正文/packet由validate_business_answer精确复现invalid_answer_citations。原packet完整保留，未采集推理；最初诊断提前break出现生成器清理告警，改为连接内消费完有限快照后重放，最后输出无告警。实际截图two-step.png已人工查看：两工具成功、伪引用与红色错误同时可见，不当成功答复。

先前a08d00ad的政策/MH/拒答/独立按钮/社交、会话30重启幂等证据继续按原run复用，没有复制到本次结果。本轮仍未完成全部验收，控制器负责下一轮业务结果与FAQ引用指令修复及审查；本轮不再live/full、不放松guard、不删除未知引用、不调整模型或预算。

## 2026-10-14：引用指令修复后的剩余两项复验

`26d3758af0a39fbb481064e6d8888939d01677f9`引用契约修复经独立审查放行后，只优雅关闭自有链17620→98900→13236→7308（控制台另含停止工具44396），同.env SHA/同SQLite隐藏重开uv32524/Uvicorn98024、healthok；8001 PID58816保持。缓存`.cache/task-9-last-stop-owned.txt`、`task-9-last-server.*`保存归属/关闭/启动证据。

按原人类明确授权call_ec17b619fb6146cca74f82144b55b462，仅执行一次 `D:/vue/node.exe scripts/verify-workflow-browser.cjs --url http://127.0.0.1:8002/ --mode live --cases two-step,usage-help`。run `5c7dd489-8c35-482e-bb6e-12abf16a1db8`：两步会话41仅发selecting后返回upstream_error“模型返回了无效工具申请或未正常结束。”，没有工具或最终答复；使用求助依同链路首次失败规则未执行。其余已通过场景不重复。本轮浏览器**0PASS/1FAIL/9NOT_EXECUTED，exit1**。

严格只读导入主8项为**1尝试/0通过/1错误/7未执行，exit1**，SQL仅用户168；根与子检查点pending __error__，子图决策0/工具0，已记录分类1call/385actual、usage_complete=false。失败Agent调用用量未持久化，1不是全部收费次数。导入命令 `python -m evals.evaluate_workflow --mode chat --live --evidence .cache/workflow-browser/live/5c7dd489-8c35-482e-bb6e-12abf16a1db8/results.json --output .cache/task-9-last-live-chat.json`，读取已有证据、零新增模型调用。

源码确认该错误由parse_tool_selection协议校验发出，可对应结束标记、工具数量、非法申请或raw镜像等多个条件。失败原始AIMessage未落检查点，现有证据无法区分具体字段；本轮未进行收费诊断或重试，也不能声称刚修复的最终引用已通过，因为失败尚未到最终阶段。原物流39及更早政策/MH/库外拒答/按钮/社交和重启幂等证据按各自run保留，不复制到本轮。整体验收仍未完成，后续处理由控制器决定，本轮无产品修改、full或额外调用。

## 2026-10-14：安全诊断版本的两项定点结果

BASE `ac2cb81841d2a9b316745e830dc89cfc9ccb52ac` 的无内容协议诊断经独立审查放行后，仅重启自有8002链32524→29900→83920→98024；控制台全集加自身59732核对后优雅关闭，.env SHA一致、同SQLite隐藏重开uv34776/Uvicorn106652、healthok。8001 PID58816保持，证据`.cache/task-9-diag-stop-owned.txt`与`task-9-diag-server.*`。

依原人类固定场景/修复后定点授权，仅一次 `D:/vue/node.exe scripts/verify-workflow-browser.cjs --url http://127.0.0.1:8002/ --mode live --cases two-step,usage-help`，run `e867aeab-22c7-49fb-acec-b0dfe3c8f14a`；浏览器**1PASS/1FAIL/8NOT_EXECUTED，exit1**。其他已通过场景未执行，原协议错误本轮未复现，日志没有agent_tool_protocol_failure；不能因此宣称外部协议异常已根治。

- 两步42功能PASS：SQL169用户→170/171 query_order（call_-7181255034821147660）→172/173 query_logistics（call_-7181205728596582884）→174最终；两工具成功徽章、实际正常done、reply_mode=answer、决策3/工具2，正文保留模拟说明且无虚假[1]/[2]，本地直接调用严格sql_turn_errors返回[]。但实际分类“订单”，金标“物流”，报告如实保留misclassified，未改金标或放宽评估。已记录5calls/3459actual，usage_complete=true，零低置信记录。
- 使用求助43 ERROR：意图售后，零工具/零低置信记录；正文“可以的，您买的是什么商品或型号？具体在哪一步不会操作呢？”随后invalid_answer“社交或澄清回复包含未验证内容”。SQL仅user175，无final/done/actions。已记录2calls/1154actual，失败final用量不完整。既有非事实句式以fullmatch识别“具体在哪一步不会操作”，未允许句尾“呢”；本地同一句校验False，仅本地移除“呢”后True，见`.cache/task-9-diag-local-validation.json`。未改生产句式、原文或原报告。

严格只读导入命令 `python -m evals.evaluate_workflow --mode chat --live --evidence .cache/workflow-browser/live/e867aeab-22c7-49fb-acec-b0dfe3c8f14a/results.json --output .cache/task-9-diag-live-chat.json`，主8分母**2尝试/0通过/1误分类/1错误/6未执行，exit1**。持久化账本7次不是全部收费次数；32000范围/委托query与充分性排除规则不变。两个截图已人工查看：两步成功与正常反馈、help正确追问及红色错误。旧各run与当前结果严格分开保存，未重复已通过场景、未自动重试/full/付费诊断。使用求助仍待控制器处理句式边界，两步分类差异单独保留，不能称全验收通过。

## 2026-10-14：使用求助完成与跨批次功能证据汇总

句式小修`c10c9e8235a74c1e94987a4d5f197e0a28b10a4c`经scoped审查无新增问题后，只核对并优雅关闭旧自有链34776→85000→103764→106652（控制台加停止工具91088），同.env SHA/同SQLite隐藏重开uv64976/Uvicorn97940；healthok，8001仍58816。缓存`.cache/task-9-help-stop-owned.txt`、`task-9-help-server.*`。原240秒、零重试、模型预算/merchant集合/阈值保持，直接人类call_ec17b619fb6146cca74f82144b55b462许可原话随命令申请提交。

唯一真实命令 `D:/vue/node.exe scripts/verify-workflow-browser.cjs --url http://127.0.0.1:8002/ --mode live --cases usage-help`，run `b1662cd0-1cc8-4c00-897f-82392feaeb0e`，浏览器**1PASS/0FAIL/9NOT_EXECUTED，exit0**。会话44：SQL176用户→177最终，实际意图售后、reply_mode=clarification、决策1/工具0、无低置信记录，原文“可以的，你买的是什么商品或型号？具体在哪一步不会操作？”，正常done。实际截图已查看，型号/步骤追问与正常反馈可见，无错误。该次生成未带“呢”，窄修复的精确带呢覆盖由离线真实原文回灌测试证明，不混作本次实际生成。

严格只读导入 `python -m evals.evaluate_workflow --mode chat --live --evidence .cache/workflow-browser/live/b1662cd0-1cc8-4c00-897f-82392feaeb0e/results.json --output .cache/task-9-help-live-chat.json` →**主8分母1尝试/1通过/7未执行，其余0，exit0**；sql_pairing_errors=[]，3calls/1495actual、usage_complete=true。输入/决策/最终保留原预算，32000仅计已记录intent+Agent；委托query/充分性排除规则不变。未重复其他场景或完整套件。

| 固定功能证据 | 实际来源 | 核对结论 |
| --- | --- | --- |
| 政策、投诉、闲聊、MH-LP200 | a08d00ad，31/33/34/35 | 政策实际引用、投诉明确确认工单、闲聊零模型、MH-LP200实际引用12L通过。 |
| 库外问题 | a08d00ad，36 | 资料不足为预期拒答，不计一般回答通过；保留低置信记录。 |
| 物流 | 1e35ffad，39 | 一组成功工具SQL、answer模式、正常最终与done通过。 |
| 两步订单→物流 | e867aeab，42 | 两组顺序SQL、两成功徽章、合法最终/无伪引用正常完成；严格报告依旧misclassified（actual订单/expected物流）。 |
| 使用求助 | b1662cd0，44 | 追问型号/步骤、零工具/零低置信、clarification与正常done通过。 |
| 独立按钮及重启幂等 | a08d00ad，33/37/38；原会话30重启proof | 两按钮互不依赖、仅明确确认写工单；同SQLite接续不重复旧turn，旧checkpoint重复确认仍同一工单。 |

本表是跨run功能证据索引，不是一次新“8/8”报告，未把旧成功复制进help-only JSON；原strict分类金标/误分类计数不变。按控制器Ruling，两步订单/物流共用业务出口，组合优先级留后续正式意图阶段定义。旧3cccc1a8、a08d00ad、1e35ffad、5c7dd489、e867aeab全部失败/未执行与用量不完整记录保留，原工具协议异常未在后次复现并不等于根治。完整功能路径证据已齐，最终整分支独立审查、其发现处理及当前HEAD完整回归仍由控制器执行；不以316d0cc的1782/118替代未来HEAD结果。

## 2026-10-14：最终审查与收尾验证

最终产品代码为 `919662ec026b561bdb1b6b0cfb75f6348fbd3625`。整分支审查发现的四项问题已在一次修复波次完成，并经独立定向复审全部确认：知识路径合法追问使用澄清校验；默认控制台可见的安全节点/终态/工单审计；生产图同步写检查点；裸循环演示直接回答上限512。相关9文件166项通过。日志只配置应用自建处理器，首次105通过/60失败的捕获器接线错误及修正证据均保留。

最终完整命令 `uv run --locked pytest -q`（启用 `WORKFLOW_BROWSER_CONTRACT=1`）实际为 **1843 passed、118 skipped、1 failed，397.71秒**；唯一失败发生在受控浏览器启动前，当前Playwright默认寻找未安装的chromium-1217。控制器补上既有安装路径 `WORKFLOW_CHROMIUM_PATH=C:/Users/beemines/AppData/Local/ms-playwright/chromium-1234/chrome-win64/chrome.exe`，原代码不变，仅复验同一用例，**1 passed、4.33秒**。这是完整运行加单项环境修复复验，不能表述为一次全绿完整运行；原输出 `.cache/workflow-final-full.txt` 与复验 `.cache/workflow-final-browser-path-recheck.txt` 分别保留。默认跳过的资源集成不计通过。

最终本机隔离MySQL/SQLite专项：`uv run --locked pytest -q --run-mysql tests/integration/test_workflow_actions.py tests/test_workflow_persistence.py`，**10 passed、5.46秒**。控制器首次误写SQLite测试路径导致0项收集，修正后才执行该专项。最终 `git diff --check`（全分支范围）通过。未追加真实模型调用、重试或300题评估。

同.env与同官方SQLite重启最终8002：uv99376/Uvicorn45360，原8001 PID58816保持。唯一零模型问候浏览器冒烟run `f4842306-4a72-42ba-b678-c60dd18e131a` 通过；会话45的SQL178用户→179最终、checkpoint与done一致，用量四项均0。实际控制台有4个workflow_node、checkpoint_complete和恰好一次terminal success，证明默认启动可见日志；截图已检查。证据 `.cache/workflow-final-runtime-proof.json`、`workflow-final-runtime.stderr.log` 与相应browser/chat文件。

固定功能证据按前表各run来源保留，不合成为新8/8。两步查询功能正常，但严格主意图标注仍保留actual订单/expected物流的差异；正式组合意图与指代消解留后续。历史供应商协议异常的精确原因未有原始内容证据，后续成功不代表永久消除。32000账本仍限已记录intent+Agent，检索改写/充分性及未保存失败调用不混作全供应商成本。

本轮实现与必要验证完成，代码已提交在 `feat/workflow-agent`，主分支与远程尚未改动。当前演示入口为 http://127.0.0.1:8002/ 。启动与裸循环命令见README。技术裁决及判断错误时的成本见[裁决记录](workflow-agent-decisions.md)；开发过程见 `dev-notes/ch05.md`。集成方式交由用户选择，保留工作树、运行检查点和本地验收证据。
## 2026-10-14：验收调整——独立人工消息与手填工单

根据用户后续要求，点击转人工直接在消息列表新增“已接入人工客服”服务通知，再新增“客服小猫 · 人工客服”的独立问候气泡，不再向原答复内部追加，也不再使用浏览器原生确认框。转人工仍是纯前端模拟、零HTTP；按钮与工单保持独立。

建工单打开空白原生dialog表单，用户选择售后/投诉/咨询并填写1至2000字非空描述。取消、Escape和未填校验均不写库；提交期间禁用重复提交，失败保留内容可重试，成功在新的服务通知气泡显示单号。接口现要求`assistant_message_id`、`checkpoint_id`、`ticket_type`、`description`四字段；旧两字段客户端需刷新后使用。原完成快照/SQL归属、同源、会话锁、原工具与稳定幂等身份均保留；更改表单重提同一回复返回409，不覆盖已有工单。

产品提交`03360024344fca7609cccddea98f414ef4e8f925`：后端RED3失败/7通过，相关54项GREEN（含真实隔离MySQL）；后端独立审查PASS/APPROVE。真实Chromium受控26/26通过，桌面及390px表单截图已检查。完整离线回归1854通过/119跳过，350.78秒、exit0；显式Chromium1234路径已配置。各阶段原日志分别保留在`.cache/ticket-form-*.txt`、`.cache/ticket-actions-*.txt`。

实际8002固定投诉及两个附加场景只运行一次，run`4924df9d-0455-40d0-9046-bc5ab00fc786`，3PASS/0FAIL/7未执行、exit0；并非新的10/10全量验收。自有会话48手填咨询工单、会话49只建工单、会话50取消不建单均通过。SQL逐字段与实际表单POST一致，会话仍进行中；消息截图显示原答复与接入通知、人工问候、工单结果为独立消息。原模型/预算/240秒/零重试不变，无其他收费场景或300题。

当前8002：uv93108/Uvicorn37408，同.env SHA及SQLite，原8001保留。需先关闭旧确认框，再Ctrl+F5刷新 http://127.0.0.1:8002/ ，才能加载新脚本及手填接口。真实证据与截图位于`.cache/workflow-browser/live/4924df9d-0455-40d0-9046-bc5ab00fc786/`；界面表单截图位于`.cache/workflow-browser/controlled/ticket-form-desktop.png`与`ticket-form-mobile.png`。

## 2026-10-14：投诉原句及运行入口定点复验

用户截图中的两条拒答保存于会话52，使用旧版固定拒答文本，未出现在当前8002 Workflow日志。实际浏览器同时开着旧8001与新8002；旧页脚与截图一致，新8002提供手填工单四字段接口。失败请求的网络记录不在手中，无法仅凭截图认定其确切端口。

Computer Use在8002发送“我要投诉”和“你们太差了，我要投诉”，会话53的两轮均经过投诉节点，正确返回安抚话术和两个独立按钮。点击阶段CDP超时后，按既有授权使用真实Chromium在同8002追加一条投诉定点复验：固定投诉回复、人工零HTTP及两条独立消息、原回复正文保持、工单空白表单、取消零写入，全部通过。实际SSE、请求清单与截图位于`.cache/complaint-entry-validation/`，脚本`.cache/verify-complaint-entry.cjs`；没有路由替身、模型配置变化、自动重试或全量评估。本轮没有产品代码修改，不将定点通过表述为重新执行完整回归。

## 2026-10-14：主题弹窗与用户当前标签升级验收

用户后续截图明确显示8002仍用旧脚本。Computer Use在其当前标签3读得两个新dialog节点均不存在、脚本地址无版本号，不能用另一个标签的通过结果替代实际用户页面。新增同主题人工确认dialog，确认后才新增接入通知和独立客服问候，取消/关闭/Escape不动作；手填工单仍独立。HTML设置no-store，CSS/JS地址增加`v=20261014-dialog2`。新入口为`http://127.0.0.1:8002/?ui=20261014-dialog2`。

HTTP缓存专项先RED1失败、随后相关后端首轮65项通过（20.22秒）；自审恢复原默认服务测试的检查点断言位置后同组最终65项通过（27.59秒）。真实Chromium受控28/28通过，人工确认桌面和390px两张截图已检查：`.cache/workflow-browser/controlled/handoff-dialog-{desktop,mobile}.png`。JS语法与git diff --check通过。没有再次跑完整回归或300题，模型/预算/零重试均不改。

自有8002隐藏窗口重启为uv74572/Uvicorn11740，同.env/SQLite，8001保持原进程。实际HTTP返回no-store与版本资源。Computer Use在用户同一标签导航新地址并核对两个dialog节点出现后，只发送一次真实投诉原句，会话56、SQL214→215；主题弹窗取消后无新增接入、再次确认后出现两个独立消息、工单类别和描述初始均为空、最后取消未写工单。当前用户标签已完成真实升级，无需用独立测试窗口替代交付。
