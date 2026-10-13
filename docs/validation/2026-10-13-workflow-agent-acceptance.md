# Workflow Agent 有界验收（2026-10-13）

当前代码分支为 `feat/workflow-agent`，基线 `83ea49620bb710e559947475229b7b5910ea1b21`。**第五步尚未完成：真实聊天的知识/业务 Agent 控制输出失败，四个后续场景停止；分类、独立按钮和重启验收已通过。**报告区分受控工程验证与真实模型/服务验收，不使用旧1531数字代替本次结果。

## 已完成的当前验证

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
