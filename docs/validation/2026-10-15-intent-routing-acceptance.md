# 意图分流：浏览器验收记录

当前结论（2026-10-16）：实现任务及先前限定复审关闭C1/I1–I5/M2/M3；用户随后在会话64的原句暴露间歇性首个Agent决策协议错误，增量bbedb0e前置原生必需读取约束，相关352项回归及独立限定审查通过。Computer Use在同一会话提交原句一次已通过，SQL269–272与完成根一致，详见文末。完整2214通过/143跳过（394.84秒）属于增量前7398b27版本，不能冒充当前新增量全量结果；相关真实MySQL专项27项的存储代码未再改。原浏览器合并证据仍7/8，维修有效答复缺口未完成。原48题43通过/3失败/2阻塞及所有历史失败均保留，后续定点修复分开记录；不称独立48题或八组全通过，也不作生产就绪承诺。

I4离线收口索引：见本文末“评分器v3整句契约”记录。旧2149/143属于后端提交e329dd0的源码，后续新评分器的冻结全量结果单独记录。

## Task 8：受控 UI 验收（2026-10-15）

用户要求“前端部分用 Vibe Coding”。直接实现后用真实 Chromium 点击与截图检查；本阶段未运行前端 TDD、完整 pytest 或代码评审波次。没有启动真实 8003、调用模型、迁移或写入应用数据库，8002 保持原状。以下全部为受控接口数据的 UI 结果，不能作为真实业务或 SQL 落库通过。

入口：

```powershell
node --check app/static/chat.js
node --check scripts/verify-intent-routing-browser.cjs
node scripts/verify-intent-routing-browser.cjs --url http://127.0.0.1:8003/ --mode controlled
```

受控模式使用自有临时回环端口，`--url` 仅记录目标配置，不启动、改写或拦截该服务。分段 HTTP SSE 经过真实 UTF-8 解码与页面解析。浏览器使用本机既有 Playwright/Chromium，无新组件或依赖。

最终结果：**11/11 PASS，退出码 0**，全部场景 pageerror 为空。完整请求方法/正文/查询字符串和截图在：

`D:/shixi/ecommerce-customer-service/.worktrees/intent-routing/.cache/intent-routing-browser/controlled/96df48d8-3d88-47dc-a120-28acd00432a2/results.json`

| 场景 | 实际断言与请求次数 | 截图文件 |
| --- | --- | --- |
| paused-cards | paused 恢复输入，2 张只读摘要卡，无满意度；HTML 字符按文本显示 | paused-cards.png |
| refresh-pending-and-resume | 刷新 GET pending-order 1 次；双击只发选单 POST 1 次；四字段字符串准确，无新增用户问句 | refresh-pending-and-resume.png |
| selection-409-recovery | 首次 409 保持旧卡锁定；手动 GET 当前待选后继续，累计选单 POST 2 次 | selection-409-recovery.png |
| new-message-invalidates-cards | 新消息禁用旧卡；正文“申请退款”不能触发表单；选单 POST 0 次 | new-message-invalidates-cards.png |
| offer-terminal-and-disconnect | 收到 offer 但尚未 done 时隐藏入口；断连不显示许可 | offer-before-done.png、offer-terminal-and-disconnect.png |
| refund-cancel-escape-keyboard | 空白必选阻止提交、取消与 Esc 均退款 POST 0 次；恢复按钮焦点、焦点保持弹窗内 | refund-cancel-escape-keyboard.png |
| refund-submit-once-receipt | 只读 ¥299.00；双击退款 POST 1 次；只传原定位/offer/原因；原回答不改，独立“服务通知”显示申请号和待审核 | refund-submit-once-receipt.png |
| refund-failure-retains-reason | 首次 503 后原因“运输破损”保留；显式重试成功，累计退款 POST 2 次 | refund-failure-before-retry.png、refund-failure-retains-reason.png |
| refresh-refund-revalidated | sessionStorage 只有会话及两字段定位；刷新 GET refund-offer 使用原 SQL ID/检查点；服务器拒绝则无入口，退款 POST 0 次 | refresh-refund-revalidated.png |
| narrow-refund-dialog | 390×720，浅绿圆角主题，边界无横向溢出、下拉和提交按钮可见 | narrow-refund-dialog.png |
| existing-actions-citation-feedback | 引用原文、反馈锁定正常；人工取消/确认零附加 POST，独立通知/小猫气泡；工单取消 0、双击提交 1 POST | existing-actions-citation-feedback.png |

表内截图均位于上述 JSON 同目录。人工查看了 paused-cards、独立回执、桌面失败表单与窄屏表单；未把仅有断言当作截图视觉检查。

身份夹具刻意使用 `9007199254740993/995/997/999` 等大于 JS 安全整数的规范十进制字符串；请求 JSON 严格保持字符串，金额继续为整数分。

实现：卡片只有完整 paused 后可选择，同组锁定，恢复复用 SSE。退款入口仅来自服务器完成许可；六类原因初始空白必选，金额只读，提交中防重，失败保留原因，按钮标明“提交申请 · 待审核”。刷新不缓存订单/金额/owner/完整政策作为授权依据，不增加通用历史功能。

## 失败与返工

- 首次读取命令触发已知 PowerShell conda profile 警告，随后 `login=false`。一次只读文件探测使用不存在的 contracts/API 文件名，改为实际源码，无业务影响。
- CUA 首选已尝试：IAB 子代理不支持可见页；Chrome 两次因 request-header-policy / Statsig Cloudflare 403 无法创建页。按已授权回退使用既有 Chromium 自动化。
- 沙箱下缓存映射与浏览器启动失败；补齐真实用户缓存探测，`require_escalated` 启动既有 Chromium 成功，未下载浏览器。
- 首个实际浏览器运行仅 2/11 通过：夹具末段 SSE 字节重复导致大多数完成帧解析失败，已修复切片起点；原失败目录 `ef2f646e-5469-4775-98ca-58008c03d97b` 保留。
- 第二次 10/11 通过：未完成场景错误地查询了用户气泡而非助手正文，导致等待超时；修正定位，未以删除断言绕过。目录 `d0ee4c4b-e0ab-4883-8009-4d9aea8c0648` 保留。
- 最终 11/11 通过，同时收紧手动待选 GET 期间的输入锁，避免旧读取与新消息交错。全部运行独立目录，不覆盖失败证据。

## Task 9：真实联调待执行

真实运行入口已实现，**本阶段未执行**：

```powershell
node scripts/verify-intent-routing-browser.cjs --url http://127.0.0.1:8003/ --mode live
# Task 9 需要实际提交时：
node scripts/verify-intent-routing-browser.cjs --url http://127.0.0.1:8003/ --mode live --submit-refund
```

可用 `--message "具体审核用例"` 替换默认退货问句。live 无路由拦截，记录实际 API 响应、截图及请求计数；默认打开后取消，带提交参数才点击提交。结果始终标注 `sql_verified:false`，真实 SQL 需要 Task 9 另取证，不能靠 HTTP 回执推定。

## Task 9：实际有界验证与未闭环项（2026-10-15）

当前状态：**有界验证已完成，仍有阻断性全链路缺口，不能宣称全部验收通过。** 本记录保留Task8受控结果和本次全部真实失败；最终整分支审查及最终产品完整回归由控制器在修复波决定后执行。8002保留；8003为本工作树单worker，专用`runtime/workflow/intent-routing-8003.sqlite`。

### 实际环境、命令与测试边界

非密配置核对：MySQL `127.0.0.1:3307/customer_service`，用户`customer_service`；模型`glm-5.3-flash`、online low不变。显式`.venv/Scripts/python.exe -m app.refunds.cli init`及`verify`均输出`Refund schema ready`，exit0。此前应用refund_requests为0行。后台由`scripts/start-intent-routing-demo.ps1`隐藏启动，日志按启动时间独立保存；实际监听PID写入自有文件，重启不更换SQLite。当前演示[8003](http://127.0.0.1:8003/)；旧8002 PID11740未停止。

本机命令使用锁定且已安装的`.venv/Scripts/python.exe`，等价于计划`uv run --locked python/pytest`；设置`PYTHONUTF8=1`、`PYTHONPATH=D:/shixi/ecommerce-customer-service/.worktrees/intent-routing`。没有安装或更改依赖。pytest实际执行：

| 命令/范围 | 真实结果 | 范围与日志 |
| --- | --- | --- |
| `-m pytest tests/test_intent_routing_evaluation.py -q` 初始RED/GREEN |7 failed→7 passed|task-9-red.log、green-final.log|
| `-m pytest -q` 修前聚合 |2108 passed、142 skipped、537.80秒，exit0|task-9-full.log；收集并执行了初始7项评估测试，不能当后续产品修复最终全量|
| 三项refund/workflow文件`--run-mysql -q` |25 passed、19.89秒|task-9-mysql.log；仅3308随机自有schema|
| 评分器/来源复用/导入逐次RED→GREEN |来源真正RED1 failed/3 passed；导入旗标RED1 failed；后续相关115 passed|初次list参数探测4个API错误另存，不冒充行为RED|
| greeting真实失败与反例 |2 failed/2 passed→相关119 passed、4.67秒|task-9-greeting-{red,green}.log|
| 实际MySQL浮点幂等回归 |2 failed→27 passed、14.02秒|task-9-refund-ulp-{red,green}.log；最终2ULP负例专项2 passed、2.15秒|
| 最终受影响离线8文件 |237 passed、10.60秒|task-9-final-focused.log：evaluator、understanding、intent_contract、refund_actions/contracts、demo/business、workflow_agent|

评分器更正发生在修前聚合运行期间、评估测试已执行之后，已明确向控制器披露；控制器裁定保留该修前聚合，加修后专项，不因评分/Prompt单独重复9分钟全量。后来出现真实产品修复，**最终产品完整回归待审查修复决定后再运行一次**。没有把历史第五步或离线fake当当前协议真实通过；没有运行300题或重复无关Milvus全量。

### 固定48轮与定点修复

新CLI：`python -m evals.evaluate_intent_routing --mode understanding|chat --split acceptance|development --output <新路径>`。缺省零上游调用；真实understanding才加`--live`。现有输出拒绝覆盖；无repeats参数。定点`--case-id`只执行该轮，`--previous`可多次指定已有真实有效观测，记录源Prompt/报告/实现哈希；同模型和样例指纹必须一致，失败或缺失前序blocked，不自动付费回放、不注入expected_query/intent。chat只核验既有浏览器证据，导入时再次读取真实SQL及指定原始完成根。

| 真实执行 | 管线状态 | 意图/协议 | 完整透传 | 可消解 | 关键路由 | 上游调用/实际tokens |
| --- | --- | --- | --- | --- | --- | --- |
| 唯一acceptance16，Prompt v1 |12通过、2失败、2blocked|14/16、14/16|9/12|2/3|12/14|28 /15934|
| 失败1-4、3-2各定点一次，v2 |各1通过/16，15未执行|各1/16|各1/12|未重测其他题|各1/14|4 /2793|
| 此前blocked3-3、3-4依次各定点一次，v2 |各1通过/16，15未执行|各1/16|3-4为1/12|3-3为1/3|各1/14|4 /2879|
| 唯一development32，v2 |31通过、1失败|32/32、32/32|28/29|3/3|18/18|58 /32214|
| single18守卫后定点一次 |1通过/32，31未执行|1/32、1/32|1/29|未重测其他题|1/18|2 /1057|

原始两个固定批次合计仍为**43管线通过/48，3失败、2blocked；意图46/48、关键路由30/32、完整透传37/41、可消解5/6、歧义零猜单1/1、实体保持46/48**。意图数值达到≥46，但完整透传全部保持、可消解≥95%及关键路由全部正确的原始批次目标没有全部达标。五次定点有效管线均通过，不能混合不同Prompt/实现后重称“独立48题全通过”。所有阶段共96次understanding/classification实际上游调用、54877实测tokens、估算0；这不包括浏览器聊天和检索内部费用，不构成全链路严格费用上限。

原acceptance失败分别为完整指令加“的”、短改查指令扩成详情问句。仅一般性澄清Prompt，没有复制失败验收金标作few-shot；修复后只重查两个失败轮及依赖的两个blocked轮，gate验证后才放行32轮。development single18实际模型原输出`{"query":"订单1001到哪了？"}`丢“你好，”；守卫只在后缀逐字相同时恢复原文，实际定点raw仍丢问候、有效resolved恢复完整原句。**这证明工程守卫，不证明原模型已学会完整透传。** 真正指代消解或其他后缀变化不被强制改回原话。

报告路径均在`.cache/intent-routing/`：`acceptance-live.json`、`point-dialogue-*-v2.json`、`development-live-v2.json`、`point-single-18-guard.json`。新报告含样例/Prompt/实现哈希、原模型JSON、finish_reason、resolved/intent/confidence/route、实际/估算usage及全分母。之前报告未补写伪造新版本哈希。

### 真实浏览器八组与SQL

既有真实Chromium151.0.7922.34，无路由拦截、无安装。首选CUA在Task8子代理受限已记录，根控制器本阶段成功打开IAB8003首页且未发聊天；实际固定点击脚本沿用获准Chromium。命令起点：

```powershell
$env:WORKFLOW_CHECKPOINT_PATH='D:/shixi/ecommerce-customer-service/.worktrees/intent-routing/runtime/workflow/intent-routing-8003.sqlite'
node scripts/verify-intent-routing-browser.cjs --url http://127.0.0.1:8003/ --mode live --restart-script scripts/start-intent-routing-demo.ps1
```

首运行`bda983f0-97ff-4102-bd4c-d5ab500560f8`保存前三组后在第4组重启helper发生继承pipe死等；PowerShell已退出、服务健康、没有活动模型轮，只终止自有Node112044。保留partial/interrupted/log。第4组此前pause已产生会话60/user241及2次模型，不能因尚未写入partial记0；恢复用其真实pending，不重复收费原问题。`stdio:ignore`修正helper，日志继续独立文件。

恢复仅`--cases pause-refresh-restart-new-message,refund-form-cancel-submit,duplicate-and-cross-conversation,repair-no-refund,complaint-social-other --resume-evidence <原interrupted-results.json>`，目录`af288aaa-b35a-4d97-bd80-da946b9c728b`：**5/8 PASS，exit1**。最后只对具体失败物流末轮及幂等/跨会话动作各定点一次，复用已观察SQL历史和原offer，不重发前序聊天；目录`92ec17f4-bc0f-469f-897c-ad9d9766db00`：**6/8有效组通过、2项仍未闭环，exit1**，为跨阶段来源合并结果，非独立八组整批通过。

| 固定组 | 实际结果与边界 |
| --- | --- |
| 政策无选单 |通过：knowledge、一次工具检索、无选单/扩写|
| 物流→退款→物流 |失败：前两轮真实完成，退款中间轮低分拒答；原末轮无当前工具直接answer被delta前拒绝；修后仅末轮复核仍失败，见下方阻断项|
| 缺单点选续办 |通过：实际paused、卡片点选，SQL不加新用户消息，understanding调用计数不重置，完成offer|
| 暂停刷新/重启/新消息失效 |通过：会话60真实pause保留跨重启，公开GET恢复；新问候零模型，旧卡锁定/选单409|
| 表单取消/提交 |通过：复用真实59原offer经GET重验；空必选/取消0POST，明确双击提交1POST，实际SQL0→1，独立待审通知|
| 重复与跨会话申请 |首轮同offer错误409；1ULP修复后同原offer200同申请号，改原因409，新会话另一offer409，记录数仍1|
| 维修 |路由/先查单/后政策正确且无退款入口；前置知识闸拒答，未执行Agent。原脚本强求not_applicable是过严断言；实际答复完成率仍gateblocked，不能改称维修知识回答通过|
| 投诉/问候/其他 |通过：complaint/social/other各正确，纯感谢stage_usage为空，无退款入口|

实际申请为`Rcbdae9a1ecfb2d3ee65534c9a0e9f6dc02b2bb2613d614d118e6ae65a15d836d`，会话59/user235/assistant240、原根`1f1c8aae-719b-61f9-800b-22df2f9c9e18`、order1001、19900分/CNY、unwanted、待审核。保留完整订单/政策/决策快照、业务日期与版本。原工单记录及原会话状态未改，没有付款、实际退款、自动工单或删除业务行。

MySQL JSON往返使两个政策建议score各偏1ULP，严格Python字典比较误判同源冲突。修复仅`policy_snapshot.matches[i].score`允许有限double相邻1ULP；所有身份、原因、金额、状态、决策、政策原文/结构及其他数字类型精确，2ULP或改文/金额等均409。没有更新原行或忽略整份policy，原行原分数保留。1001名称按repo及实际KB权威事实纠正为智能猫砂盆Max/fixture v2；id/model/日期/金额不变，原v1根/申请不改。旧原offer在修后公开GET仍合法，实际弹窗截图`old-root-valid-form-after-fix.png`。

证据导入：`python -m evals.evaluate_intent_routing --mode chat --split acceptance --live --evidence <92ec17.../results.json> --output .cache/intent-routing/chat-live-evidence-final.json`。**model_calls=0；full_chain实际8组分母；benchmark_full_chain16题保持未执行。** 每个可计通过组重新读取真实MySQL助手与指定原始durable完成根，不能只信JSON里的sql_verified:true。

### 尚存阻断和维修闸证据

1. **物流最终澄清晚校验泄露：** 原末轮Agent持久子状态为answer、decision_count1、tool_count0，安全守卫在delta前invalid_answer。一般性“本轮读取”Prompt澄清后，唯一末轮定点改为clarification，但模型仍从旧历史输出台灯物流事实，**先发delta后才invalid_answer“社交或澄清回复包含未验证内容”**。没有done/SQL最终助手；原SSE完整保留。该问题需要独立后端审查修复，不能用反复收费Prompt调参或弱化守卫掩盖。当前6/8不能作为可完整交付声明。
2. **售后政策相关但低于原校准门槛：** 订单1002原话与resolved均`订单1002不要退货，只想寄修。`，intent售后/routeafter_sales、tool_count2。实际扩写为原话、`MH-WD100明辉饮水机保修范围与维修适用条件是什么？`、`MH-WD100寄修流程与需提供的故障信息和材料是什么？`。实际Top10含chunk90“售后手册/维修寄修流程”score0.0628956854、chunk124“退货退款政策/质量问题与保修”0.0137902740，确有设备故障/保修/寄修政策；另chunk93申请退款0.0119578969、chunk119无理由范围0.0105613619。最高仍低于原min0.3218679428100586，retrieval_low_conf，充分性/Agent未调用、refund_decision=null、无退款入口。不是先查单/工具排序缺失。修正脚本未来将其标gateblocked；本次原失败原样保留，不重跑付费维修，不降低阈值或虚构事实。完整savedretrieval_audit、查询、匹配全文在`.cache/intent-routing/repair-gate-diagnosis.json`。

中间退款同样实际best0.087793961<0.3218679428；原查询`订单1001的MH-LP200能退货吗`，扩写含旧台灯名，实际chunk109为猫砂盆Max，名称矛盾另已纠正，但没有证据证明名字是低分唯一原因。无300题、无模型/依赖/校准值更换、无新收费循环。此记录供最终审查与用户决定余下修复范围。

失败费用口径另有阻断：上述最后物流user256的终态审计仍为3次调用/3268tokens，但实际还启动并消费了第4个最终模型流。`finalize_answer`在`validate_answer`之后才`record_usage`，晚校验抛错导致该最终流usage未递交。保存的child/terminal记录与SSE只证明缺计路径，不能据此宣称真实全链路费用上限；统一后端修复波需覆盖失败最终流的同步记账。

## 2026-10-16 最终审查修复增量（离线证据）

C1、I1–I5及M2/M3已在统一修复波中处理：澄清先完整验证后公开；Agent两阶段及预算使用规范问题的临时消息；完整物流/订单的唯一可信目标需要当前对应成功读取，合成强制读如实标workflow且保留四工具/五决策预算，真实缺订单仍可澄清；Agent失败/取消尝试进入同步用量快照；固定消解评分增加动作/极性/时间/疑问校验；8003辅助脚本核对精确进程身份与启动来源，拒绝自动认领旧PID文件。详细测试与代码范围见final-fix-report.md。M1无默认未签收运输fixture，明确deferred。

最终修复候选默认全量：**2148 passed、143 skipped、370.87秒**，`.superpowers/sdd/2026-10-15-intent-routing/final-fix-full.log`；真实3308随机自有schema的退款迁移/存储/actions：**27 passed、14.56秒**，`final-fix-mysql.log`。未删除或修改应用已有退款行。收到实际usage的最后一片恰遇期限时，先检查期限会保留估算而未采用收到的actual；额外离线探针已确认此窄记账边界，待控制器裁定，不把全量green覆盖到尚未修改的边界修正。

原七份理解评估观测在最终scorer下追加离线重算：`.cache/intent-routing/offline-semantic-rescore-v2-final.json`，附源文件摘要与scorer实现摘要，**新模型调用0**；实际check和状态没有变化。原48仍43通过/3失败/2阻塞，五个后来定点与原批次分开。评分器曾可把容量请求/无保修结论视为消解通过的反例现在明确失败。

此增量尚不声称新的线上物流通过或整体可交付。原浏览器6/8、两次物流失败、维修政策相关但低于校准闸、原中间退款低分都保留。只允许在控制器批准后复用cid58既有前序，单独执行最后物流点一次；维修不增加付费尝试，质量缺口待明确处置。

### 已确认的最后记账边界修正

收到实际usage片段后先合并账本素材，再检查deadline，过期仍零delta。永久回归先1 failed/17 deselected，修后计费/取消/实际服务审计相关**46 passed/19.50秒**（final-fix-final-accounting-green.log）。控制器明确批准因该新实证缺陷对最终源代码做一次必要全量复跑；2148/143为修正前快照，不冒称最终代码。MySQL27项未重复执行，因为最后变化仅流记账顺序。最终聚合日志为final-fix-final-full.log，实际结果另记。

### 最终源代码与唯一物流定点结果

最终源码聚合 **2149 passed、143 skipped、414.33秒**（6分54秒），`final-fix-final-full.log`，exit0；最终源码manifest在启动新服务后再次核验全部哈希一致。目标MySQL27项仍是相同存储代码验证，没有为最后流顺序修正重复MySQL。

只执行批准的cid58末轮一次：run `85359724-1733-433f-aa07-5ea7e81c8cc3`，使用`--cases logistics-refund-logistics --resume-evidence <92ec17.../results.json>`。请求记录恰为pending-order GET及一条chat POST，原前两轮不重放，没有退款POST。新用户SQL263→模型选择的query_logistics请求264→成功工具结果265→最终助手266；工具结果是订单1001、智能猫砂盆Max、已签收2026-10-13、mock=true、业务日期2026-10-15。SSE中本轮tool_completed success先于任何delta，回答只展示这份当前结果并明确模拟演示，随后done；未再泄露旧台灯信息。截图已目检。

新原始durable completed根为`1f1c8b66-4d7f-67aa-801d-517828cffc3a`，SQL助手与根一致，raw/resolved均`不要退款，我要查订单1001物流。`、intent物流、routebusiness、refund_offer=null、tool_call_count1。此实际点工具来源是**agent**，不是声称触发了工程合成；合成fallback由离线父图回归覆盖并如实标workflow。终态审计**5实际模型调用/6060实际tokens/0估算、2次控制决策/1工具**。源码摘要`66b28b15afa630e5ffa707ca695cb97e3ca57c3a5fd5bdc502d7b53b95d6b756`涵盖本次Agent/nodes修复。

脚本合并来源现在 **7/8 PASS，exit1**；唯一新物流点PASS，退出1是保留的维修失败。不是独立重跑8组；旧六项沿用既有验证来源，原两次物流失败及维修/退款低分原记录不覆盖。baseline/final真实SQL退款仍1行且完整快照相同，工单快照相同；无新申请、删除或状态改写。

旧Task9服务47276在精确CIM创建身份、命令、父进程和日志复验后停止，新helper验证19324→14568、精确工作树/解释器/app-dir及创建时间后保存owner JSON。额外scratch检查最初因CIM微秒与Get-Process100ns（.6262300Z/.6262307Z）精度差异安全拒绝且未停止；修正只用各API实际对应的精确身份，冻结产品helper未修改。8002 PID11740创建时间和命令保持原样。

剩余：维修仍是政策相关但未达到原校准门槛的真实质量缺口，需控制器/用户明确处置；M1继续deferred。未追加维修调用、模型切换或8/48/300批次。整体交付/合并结论留待控制器的一次范围复审及验收处置。

## 2026-10-16：评分器v3整句契约（I4单独离线收口）

最终复审的两条真实反例分别为dialogue-5-2“订单1001无需申请退货。”和dialogue-5-3“后天请查订单1001的配送进度。”：旧v2虽新增负例检查，仍因后缀search与短黑名单而全项通过。因此先前I4完成表述不成立，原v2重算不能独立证明极性/时间保真。本次由控制器明确追加一次有界离线修复，超出原最终波次上限的授权如实记录；没有隐性重跑付费批次。

`request-semantics-v3-whole-query`只对六条固定消解题采用整句fullmatch。订单/型号/产品名来自固定题及可信夹具，主语和请求动作之间没有任意字符占位；有限同义词保留“能不能”“目前”“查询”“保修期”等合法表达。具体退货必须带正确订单，通用保修允许已知型号或唯一来源订单。任意新时间、否定、结论分句或改动作均不能借合法后缀通过，未支持措辞保守失败。这是固定数据集契约，不是通用NLP评判器；不调整标注、Prompt、模型或运行时。

新增65项永久回归：七份报告全部六种实际成功消解输出，加有限合法别名；两条审查反例；无需/无须/不用/不必在前、中、后位置；六题分别新增明天/后天前后缀；伪造事实、请求变结论、动作变更和未知措辞。RED为21failed/44passed/23deselected（3.58秒）；修复后eval+query_understanding+intent_contract专项193passed（5.00秒）。相关日志在`.superpowers/sdd/2026-10-15-intent-routing/final-scorer-closure-{red,focused}.log`。

只读取七份旧观察报告，写入新文件`.cache/intent-routing/offline-semantic-rescore-v3-whole-query.json`，独占创建防覆盖，`new_model_calls=0`；保留每行original_status/original_checks以及原始/重算指标。评分器实现摘要（沿用digest字符串的JSON序列化算法）`667d26613c39df1e530c7fd9907a785166ec8415576d006ef91354a73fd3900d`，源码文件SHA256 `33c255921bbb2a75f9b25b1e6c725d4d45871899a762e8bcb9b076486aeb577e`。七份源文件重算前后字节哈希相同；v2报告未覆盖。

| 原始来源 | v3重算结果 | 检查变化 |
| --- | --- | --- |
| acceptance-live.json | 16总数：12通过、2失败、2阻塞 | 0 |
| development-live-v2.json | 32总数：31通过、1失败 | 0 |
| point-dialogue-1-4-v2.json | 16总数：1通过、15未执行 | 0 |
| point-dialogue-3-2-v2.json | 16总数：1通过、15未执行 | 0 |
| point-dialogue-3-3-v2.json | 16总数：1通过、15未执行 | 0 |
| point-dialogue-3-4-v2.json | 16总数：1通过、15未执行 | 0 |
| point-single-18-guard.json | 32总数：1通过、31未执行 | 0 |

原48仍43通过/3失败/2阻塞，原消解5/6；后续定点分开记录。所有已有有效消解输出在新契约下保留，并不意味着旧48已独立全通过。I4本次只改离线评分，8002/8003服务与PID14568不操作，无SQL写入、MySQL重跑、模型调用或浏览器新执行。维修低分拒答的有效答复缺口与M1默认数据缺少运输中未签收场景仍保留。

新评分器及测试冻结后，仅运行一次当前源码完整默认`python -m pytest -q`：**2214passed / 143skipped / 394.84秒（6分34秒），exit0**，日志`final-scorer-closure-full.log`，冻结清单`final-scorer-closure-frozen.json`两文件hash复验一致。此前2149/143仅对应后端修复e329dd0；本次增加65项评分回归。没有额外MySQL/运行时/付费验证，保留原27项MySQL证据及其来源版本。I4收口等待控制器限定复审，维修缺口不会由离线评分修复自动关闭。

## 2026-10-16：限定复审最终结论与交付边界

I4独立限定复审已完成：六条固定题的整句语义契约**ADDRESSED**，无新增Critical/Important；复审逐项核对七份旧来源及重算行、冻结hash，没有重复运行套件或付费。先前运行时及存储发现C1/I1/I2/I3/I5/M2/M3继续关闭。九项实现任务已完成，代码版本7398b27；本段之后只有交付文档变更。

控制器接受该分支作为可审阅的功能实现，**不把实现结束等同于真实质量全部验收通过**。维修有效答复缺口与原48题未达全目标的记录保留；后续检索质量调优不能在本次收尾中通过降闸或混用定点数据伪装完成。M1运输中未签收状态须在扩大演示订单范围前补齐。当前仅单worker演示身份，不作生产鉴权、支付或生产就绪承诺。

本次只读健康检查8002和8003均HTTP200，原8002 PID11740、新8003 PID14568保持；没有聊天POST、退款/工单新记录或服务重启。现有功能入口为http://127.0.0.1:8003/；从此工作树启动命令为`pwsh -NoProfile -File scripts/start-intent-routing-demo.ps1`（PowerShell7）。完整默认回归与显式MySQL命令见前文；143项默认跳过不等于对应集成全部通过，真实存储证明限定为单列的27项。

全部执行裁决及判断错误时的代价，按账本顺序完整保存在[执行裁决记录](2026-10-16-intent-routing-decisions.md)。开发过程已逐阶段记于[dev-notes/ch06.md](../../dev-notes/ch06.md)。当前feat/intent-routing分支保留；未合并master、未推送远程，等待用户选择整合方式。

## 2026-10-16：user64 原句失败的限定增量（离线已验证，线上待验）

用户“我的订单1001到哪了”在cid64两次invalid_structured_output，原失败仍保留。日志显示理解/分类成功、Agent首决策无工具节点；旧原始响应未留存，不能确定坏载荷形状。同请求的一次诊断实际返回合法query_logistics，仅证明间歇性。现有唯一可信当前读取策略只在合法控制后fallback，首次仍auto，这是本次修复的具体边界缺口。

首次business订单/物流且唯一可信目标、当前读取missing、对应工具确在注册表时，将同一规范工具名传入原生tool_choice；模型仍生成参数，既有执行器/所有权/SQL及四工具五决策、32000/60秒/零重试/2048控制/512最终预算保留。成功或失败读取后、无目标/多目标/明确未选单、knowledge/after_sales/其他意图均auto；合法注入模型控制的原fallback保留。官方bind_tools文档与锁定langchain-openai1.6.7支持exactname，离线真实SDK HTTP边界确认序列化为function/name，无新增依赖。

控制校验失败与工具混正文分别输出固定control_schema/tool_body安全类别，只有可信会话/用户身份、有界计数、白名单finish和账本；没有原响应、字段名/值、问题历史、异常文本或推理内容。仍invalid_structured_output/502、仅尝试计费、无最终SQL、无重试。新增私密标记测试是观测性验证，不能称为原坏响应重现。

有效RED：7failed/8passed/29deselected、7.67秒、exit1（user64-red-valid.log）；首次GREEN44passed、4.99秒；一次相关17文件回归352passed、42.80秒（user64-focused.log，精确文件见.cache/intent-routing/user64-fix-report.md）；清除测试旧死分支后该文件31passed、4.90秒。GREEN及后续回归exit0，git diff --check通过。无真实模型/SQL/服务/浏览器操作，无全量默认重跑；旧2214/143仍是本修复前证据。本增量等待控制器限定审查、拥有权复验重启及一次原句浏览器结果，未宣称线上已恢复。

原48题43通过/3失败/2阻塞、合并来源浏览器7/8、维修有效答复缺口、M1未签收夹具待办全部保留；本修复不改变其分母或结论。未merge/push。

## 2026-10-16：用户会话64原句 Computer Use 定点验收

用户再次报告“这啥情况”，截图中原句“我的订单1001到哪了”连续失败。日志可证明原SQL用户267/268的理解和分类均正确到物流/business，首个Agent决策后、工具执行前发生invalid_structured_output；原始非法回包未留存，不能推断具体错误字段。原始截图保存为.cache/intent-routing/user64-before.png，SQL两个原话仍保留。

仅一次保存输入的同上游决策诊断返回合法query_logistics1001，891实际tokens；因此确认间歇性，不能把该回放称失败重现。根因调查确认：已有“必须取得本轮读取”的约束仅在合法控制解析后兜底，模型请求仍使用auto，使必需读取前存在不必要的原生工具/控制JSON分叉。bbedb0e将唯一可信订单的首个缺失读取指定为原生tool_choice；其他分支保持auto，严格错误、工具执行器、审计和预算不变；新增安全的控制校验/混合正文类别诊断，不输出模型正文或思维链。

有效RED7失败/8通过/29未选；新边界GREEN44通过，最终17文件相关回归352通过/42.80秒，诊断文件最终31通过/4.90秒。独立限定审查spec/quality均PASS，无Critical/Important；原始坏载荷未知和线上验证待办均如实保留在审查报告中，没有伪造具体坏格式。当前增量未重复默认全量、MySQL或评估批次；旧2214/143与27项真实存储证据各保留原版本边界。

所有权校验辅助脚本通过本机PowerShell7重启自有8003到PID125520。首次误用旧Windows PowerShell，UTF-8脚本解析失败，已中止该次执行；之后使用当前PS7成功，不修改运行时脚本来绕过所有权检查。README当前启动命令已修正为pwsh。8002不受重启指令影响。

Computer Use直接控制用户已有IAB tab4：先保存原两条失败截图，再刷新、在同一SQL会话64提交上述原句**一次**。刷新没有重绘旧错误气泡，但保存的SQL身份仍为64，没有假造历史或新建替代会话。页面实际出现“查询物流·已完成”，回复MH-LP200智能猫砂盆Max已签收、2026-10-13，并明确演示/模拟。

实际SQL用户269→原生Agent工具申请270/query_logistics1001→配对成功结果271→最终回答272；saver原始completed根1f1c921c-baff-62d5-800c-62bec6014daa，最终SQL正文与根完全一致，tool_trace来源agent、1次工具、2次决策、5次实际模型调用/3464实测tokens/0估算。未触发新协议失败诊断。修复Agent源码SHA256为3ac127cdd865c124a36c5bde77a5a2b5865a3cbe0f34f1d2192c6fb94030109f，实际复验后核对未变。

只读基线/终态核验：原用户267/268逐字保留；refund_requests1→1、tickets10→10，没有申请提交或状态修改。项目缓存证据：user64-storage-{before,after}.json、user64-verification.json、user64-{before,after}.png、user64-fix-report.md、user64-review.md与对应RED/GREEN日志。根控制器已独立目检修后截图并执行SQL/根配对断言PASS。本次是该用户原句的一次实际通过，不能替代48题、浏览器8组或证明任意模型输出都不会再出错；原维修质量缺口不变。代码已本地提交，未合并/推送。
