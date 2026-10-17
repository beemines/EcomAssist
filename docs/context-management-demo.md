# 分层上下文演示与实际验收边界

当前本章真实验收未完成。默认配置在产品a82上固定21轮及单独重启续聊通过；demo原批20/21，第21轮容量拒绝。最后摘要提示R1的3个真实来源对照及正常启动恢复通过，但原末句虽被理解为订单1001，分类为“其他”而未重新读业务，条件续聊未执行。全部真实调用已停止，没有新源码完整21轮通过声明。详细负例、版本与账本见[实际验收记录](superpowers/reports/2026-10-17-context-management-acceptance.md)。

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

生产唯一预算工厂输出各阶段F/U/E/G/V/O/M/P/A。最后R1源码 `0221b71c8fec3302a0eed0414776159c8d284471` 的离线实际重算如下：

| Profile | W | H | H1 | H2 | E | G | M | 每轮派生累计额度 |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| default | 128000 | 59880 | 41916 | 17964 | 6000 | 2000 | 3840 | 1135879 |
| demo | 18000 | 2691 | 1883 | 808 | 2250 | 563 | 540 | 174823 |

主决策F2890不变。早期1135519/174463只属于旧理解提示。最后SUMMARY_SYSTEM前缀1163，三个保存来源估算7052/7193/12236，最大加输出512及安全540为13288，适配demo18000；未调窗口、阈值或费用补偿摘要质量。累计额度是应用容量，不是实际费用或HTTP次数。

默认最终输出512；demo最终输出2000、工具步数3、Top-K5；两种工具步数别名一致，40轮目标不变。验收profile显式采用派生累计额度，普通load_settings仍尊重旧显式费用配置；不改.env。128000为应用声明窗口，未验证为供应商实际窗口。cjk-ascii-protocol-v1首三个付费页面取得11组非流usage，估计约实际1.82–2.14倍，参数未调；最终流usage未知，不填0。

## 本地数据库、服务与原始证据

3307/customer_service迁移已在同一DDL连接核对本地容器、hostname/server_uuid、数据库、端口和会话身份后执行migrate/verify。`migrate`是显式DDL，不能对未核实目标盲目重复；`verify`与在线启动只读检查。指定3308集成只使用fixture拥有的随机schema。

8004由 `scripts/start-context-demo.ps1` Hidden启动/重启，停止前复查创建时间、解释器、完整命令/工作区、launch祖先及监听PID；未知占用直接拒绝。8002/8003未操作。default/demo分别保存 `runtime/workflow/context-{profile}-8004.sqlite`。

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
| demo | 125/16/16 | 150/50/25 | 25/34/9 |

合计297/36/36。余额不是继续调用许可。小额8个付费页面加1免费寒暄；12真实摘要首9/12，旧提示三负例定点3/3，非最终全12同版本重测。真实typed O-101理解探针通过，但不代替长会话验收；OTHER原幻想问句分类social的边界仍保留。

默认原会话68第3轮理解器误产工具动作JSON，strict schema拒绝，原2done/3attempted完整保留。a82原句定点通过后另建会话69固定21/21，S/L不变、摘要0，末轮重新读1001物流；105GLM/16嵌入/16重排。封存固定21后exact-owned重启，再一页1002本轮query_order及桌面/390窄屏原引用回载通过，单独计5GLM。运费定点回答使用历史1001金额199元、没有当前订单读取的观察不隐藏。

demo会话70前6轮因helper额外禁止任何summary_failed而暂停；父控查明一次保守词法拒绝已由独立正常notify恢复，允许只续7–21。原批最终20done，第21轮HTTP422：seq3持续拒绝导致S547/L579，完全降级历史2744>H2691；原user584保留、checkpoint停上一完成根。旧18摘要job为16拒绝/2提交，失败来源及body完整保存。

追加SUMMARY_SYSTEM首候选真实来源27漏MH-LP200，+1GLM后立即停止。最后候选R1只明确已有required_entities义务：27/61/118三真实对照3/3，+3GLM且不append旧段；同run正常startup新seq3覆盖548–579，+1GLM，旧seq1/2不变。原末句一次+2GLM：实际seq1/2/3注入、理解query恢复1001/MH-LP200，随后intent其他/confidence0.6，固定澄清且无当前业务读取。原失败user584、旧文件哈希不变，SQL/checkpoint恢复相等，但最终语义门槛仍未通过，条件重启/1002续聊/两屏引用未执行。

最后全量2720 passed/184 skipped属于a82（427.06s）；最终R1仅192项定向passed（34.74s），包含两profile离线21，不重复full。3308指定41及最终受控上下文13/13、意图11/11分别保留。原容量失败、新候选漏型号、最终分类缺口、200字摘要遗漏、有限校准均不以绿测掩盖。另保留全历史O(N)锁内读取minor，以及等待选单旧提示可能残留、启动费用下界漏一个输出预留两项P3；安全上界和runtime guard未放松。当前保留本地分支/scratch，不merge/push，不宣称整章验收完成。
