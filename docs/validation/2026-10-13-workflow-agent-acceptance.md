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
