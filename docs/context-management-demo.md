# 分层上下文演示与实际验收边界

2026-10-18最新稳定性续修：每轮共享一次受预算约束的模型恢复；截图原句真实遇到非法控制后恢复完成，运费FAQ切换通过。摘要模型输入已限制为本批用户和可信工具事实。最终冻结源码2825通过/184跳过（405.56s）；额外非页面摘要探针长度失败及参数遗漏单列，不当成功，也未重跑最终同版本两组21轮。普通无cap的8004已加载最终代码。见[本轮验收与限制](superpowers/reports/2026-10-18-model-recovery.md)。以下保留各旧版本当时的记录。

2026-10-18参考效果增补：用户已批准新增模拟订单2002（自动饮水机、待付款、1557元），原1001～1004不变。最终冻结源码全量2768通过/184跳过（402.56s）；商品冲突和联系方式续聊原句R1均通过，自然seq1保存2002/两商品/139****9000。最终复合回忆两次分别分类协议失败、Agent调用60秒超时，尚未通过，不能宣称第七步完整真实验收通过。当前普通无cap服务已恢复。具体版本、实际页面、预算与调用记录以[参考效果报告](superpowers/reports/2026-10-18-reference-effect-alignment.md)为准；旧2002不存在/旧21轮结果保留历史语境。


2026-10-18 交互服务恢复：8004 已由控制器切换为普通 `demo` 模式，当前 `/health` 不带 `acceptance` 配置，可直接继续聊天。此前误留的验收服务已到150/150，导致运费问题在分类前被本地上限拦截；原验收账本保留。切换后已在同一浏览器、同一会话用原句“你们运费怎么算，满多少包邮”完成一次真实验证，回答满99元包邮、不满99元10元运费及偏远地区例外，并显示引用。证据：`runtime/context-evidence/interactive-recovery-20261018/`。下文149/150及“余1次”均为上一次验收收口时的历史记录，不是当前交互服务限制。

**早期R3交付记录：功能实现、历史回忆与本轮业务读取、重启续聊及两屏引用回载已验证；该版本严格“不申请退款”明确复述项 NOT MET。** 以下为当时真实测试停止时的记录。最终产品源码 `9303848288d0dd0c1d785b23f9cd363f67830574`；保留原demo固定批20/21失败与后续各次定点结果，不宣称全绿或最终同版本重新跑完21轮。原失败没有被覆盖，分支/worktree/scratch保留，不merge/push。 当前证据矩阵见[实际验收记录](superpowers/reports/2026-10-17-context-management-acceptance.md)。

## 离线复现

离线回放使用生产FastAPI/SSE、父子图、ContextCoordinator、SummaryManager、SummaryGenerator、实际计费工厂、SQLAlchemy仓储和磁盘SQLite saver；仅外部模型/检索受控，会话原文存临时内存SQL。没有手工设置S/L、预置摘要、固定最早话题或重压旧段。此结果证明管线/容量，不证明真实模型语义质量。

固定轨迹为 `tests/fixtures/context/long_conversation.json`；以21句原话LF连接、不带末尾换行核对其SHA。第1/4/10/16/21轮为业务，其余为知识问题。离线末轮只有实际注入视图包含1001及原否定时才恢复，否则安全澄清。200字受控摘要省略最早段的负例保留，不能隐藏成名义成功。

在本checkout根目录、现有依赖下，设置 `PYTHONUTF8=1`、`PYTHONUNBUFFERED=1`、`PYTHONPATH`为本checkout后运行：

```powershell
.venv/Scripts/python.exe -m app.context.cli budget --profile default
.venv/Scripts/python.exe -m app.context.cli budget --profile demo
.venv/Scripts/python.exe -m app.context.cli replay --profile default --output runtime/context-evidence/offline-default.json
.venv/Scripts/python.exe -m app.context.cli replay --profile demo --output runtime/context-evidence/offline-demo.json
D:/vue/node.exe scripts/verify-context-browser.cjs --profile demo --output runtime/context-evidence/controlled-context
D:/vue/node.exe scripts/test-context-browser-options.cjs
```

使用新的输出路径保留已有原始结果。浏览器默认受控模式，不访问真实模型/应用数据库；上述不是继续付费验收的授权。

## 当前预算

生产唯一预算工厂输出各阶段F/U/E/G/V/O/M/P/A。最终R3源码 `9303848288d0dd0c1d785b23f9cd363f67830574` 的离线实际重算如下：

| Profile | W | H | H1 | H2 | E | G | M | 每轮派生累计额度 |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| default | 128000 | 59880 | 41916 | 17964 | 6000 | 2000 | 3840 | 1136727 |
| demo | 18000 | 2691 | 1883 | 808 | 2250 | 563 | 540 | 175671 |

主决策F2890、分类F1305，最终理解F3005。1135879/174823是较早摘要R1阶段值。早期1135519/174463只属于旧理解提示。最后SUMMARY_SYSTEM前缀1163，三个保存来源估算7052/7193/12236，最大加输出512及安全540为13288，适配demo18000；未调窗口、阈值或费用补偿摘要质量。累计额度是应用容量，不是实际费用或HTTP次数。

默认最终输出512；demo最终输出2000、工具步数3、Top-K5；两种工具步数别名一致，40轮目标不变。验收profile显式采用派生累计额度，普通load_settings仍尊重旧显式费用配置；不改.env。128000为应用声明窗口，未验证为供应商实际窗口。cjk-ascii-protocol-v1首三个付费页面取得11组非流usage，估计约实际1.82–2.14倍，参数未调；最终流usage未知，不填0。

## 本地数据库、服务与原始证据

3307/customer_service迁移已在同一DDL连接核对本地容器、hostname/server_uuid、数据库、端口和会话身份后执行migrate/verify。`migrate`是显式DDL，不能对未核实目标盲目重复；`verify`与在线启动只读检查。指定3308集成只使用fixture拥有的随机schema。

8004由 `scripts/start-context-demo.ps1` Hidden启动/重启，停止前复查创建时间、解释器、完整命令/工作区、launch祖先及监听PID；未知占用直接拒绝。8002/8003未操作。default/demo分别保存 `runtime/workflow/context-{profile}-8004.sqlite`。

用户手动交互演示：在本worktree根目录运行下列命令，然后访问 `http://127.0.0.1:8004`；切换默认配置时将 `demo` 改为 `default`。

```powershell
pwsh -NoProfile -File scripts/start-context-demo.ps1 -Profile demo
```

旧demo长批账本在该阶段余1次GLM；这不限制普通交互服务。上面普通演示命令不带验收RunId/caps，当前用户入口必须保持普通服务。原有界批次只供记录，不应作为日常启动命令。
此前获批实际启动使用如下完整有界参数；当前调用已停止，下面仅是已用入口的记录，不授权重跑：

```powershell
pwsh -NoProfile -File scripts/start-context-demo.ps1 -Profile default -RunId ch07-default-21-20261017 -MaxGlmCalls 150 -MaxEmbeddingCalls 50 -MaxRerankCalls 25
pwsh -NoProfile -File scripts/start-context-demo.ps1 -Profile demo -RunId ch07-demo-21-20261017 -MaxGlmCalls 150 -MaxEmbeddingCalls 50 -MaxRerankCalls 25
.venv/Scripts/python.exe scripts/context-storage-evidence.py --profile demo --conversation-id 70 --output runtime/context-evidence/NEW-readonly-storage.json
```

live浏览器先核对固定8004的profile/run/三项上限；原21入口会创建新会话并跑完整fixture，不能用于有限定点复验。有限复验使用独立ignored helper并以唯一输出/源码SHA锁定范围。服务的同步/异步GLM、后台摘要、BGE嵌入/重排在物理HTTP派发前共享持久cap，失败也计数；同run重启不能重置或改上限。SDK自动重试0，但生产正常notify可启动不同后台job，所有此类调用计费。

只读取证脚本仅SELECT SQL及现有SQLite mode=ro/query_only，不迁移、不创建根。SQL/API保留完整原始工具流水，页面展示用户/最终答复与原轮工具徽章，不能将raw工具JSON渲染为聊天答复。缺失原根时不捏造来源或动作。真实内容/日志/截图/SQL、运行账本与helper均留忽略目录，不进Git。

## 最终实际范围

| run | 已用 GLM/嵌入/重排 | 硬上限 | 当前余额 |
| --- | --- | --- | --- |
| small | 46/2/2 | 60/12/6 | 14/10/4 |
| default | 126/18/18 | 150/50/25 | 24/32/7 |
| demo | 149/16/16 | 150/50/25 | 1/34/9 |

合计321/36/36。余额不是继续调用许可。小额8个付费页面加1免费寒暄；12真实摘要首9/12，旧提示三负例定点3/3，非最终全12同版本重测。真实typed O-101理解探针通过，但不代替长会话验收；OTHER原幻想问句分类social的边界仍保留。

默认原会话68第3轮理解器误产工具动作JSON，strict schema拒绝，原2done/3attempted完整保留。a82原句定点通过后另建会话69固定21/21，S/L不变、摘要0，末轮重新读1001物流；105GLM/16嵌入/16重排。封存固定21后exact-owned重启，再一页1002本轮query_order及桌面/390窄屏原引用回载通过，单独计5GLM。运费定点回答使用历史1001金额199元、没有当前订单读取的观察不隐藏。

demo会话70前6轮因helper额外禁止任何summary_failed而暂停；父控查明一次保守词法拒绝已由独立正常notify恢复，允许只续7–21。原批最终20done，第21轮HTTP422：seq3持续拒绝导致S547/L579，完全降级历史2744>H2691；原user584保留、checkpoint停上一完成根。旧18摘要job为16拒绝/2提交，失败来源及body完整保存。

追加摘要阶段首候选漏MH-LP200失败保留；摘要R1三真实来源3/3和正常startup恢复通过，但末句分类其他0.6失败。后续分类Prompt首例其他0.95仍失败；恢复生产resolved→classification入口后六分类6/6通过，原页面理解未消解而最终invalid_answer。R2理解两例strict/身份失败分别保留。完整历史见[最终修复报告](superpowers/reports/2026-10-18-final-intent-recall.md)。

最终R3缺首段standalone一次通过，正例gold未调用。conv70原末句作为独立真实页面：实际补1001物流及两问，seq1被真实消费，当前query_logistics1001，回顾未找到包裹/核实去向/未解决；最终未明确复述“不申请退款”，原strict FAIL未改。父控与同reviewer据真实证据用单独裁决放行原定最后续聊：同run exact-owned重启后一次1002当前query_logistics，桌面/390窄屏原引用、侧栏和历史回载均通过。原21批与这些定点不拼成最终源码clean21。

最后全量2725 passed/184 skipped属于55b28c（417.96s）；最终R3仅215项相关覆盖passed（14.49s，含两profile离线21），纯Prompt未重复full。3308指定41、受控上下文13/13和意图11/11按各自版本保留。当前费用1136727/175671，所有真实测试停止，余额不是追加验收许可。原容量失败、摘要漏实体、分类/理解失败、R2遗漏首段被guard拒绝及有限token校准均保留。历史O(N)锁内读取minor、回载等待选单旧提示、启动费用下界漏一个输出预留两项P3未改；安全上界/runtime guard有效。功能实现交付，严格复述项仍NOT MET；保留本地分支/scratch，不merge/push，不宣称全绿。
