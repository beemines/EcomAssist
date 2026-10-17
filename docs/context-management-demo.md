# 分层上下文可复现验收

本页的离线回放使用生产 FastAPI/SSE、父子图、ContextCoordinator、SummaryManager、SummaryGenerator、实际计费工厂、SQLAlchemy 仓储和磁盘 SQLite saver。仅外部模型与知识检索返回受控结果；会话原文存临时内存 SQL。没有手工设置 S/L、预置摘要、固定最早话题或把旧段重新压缩。此结果证明管线与容量，不证明真实模型的语义质量。

固定标注轨迹在 `tests/fixtures/context/long_conversation.json`，SHA256 对21句原话以LF连接（不带结尾换行）；回放和浏览器都先核验哈希。第1/4/10/16/21轮走业务，其余是完整通用知识问题；末轮受控模型必须从实际注入的原文或摘要读到1001、没找到包裹、未申请退款，才可恢复该订单。每次回放创建独立检查点，不复用旧锚点。

## 已执行的离线命令

从本 checkout 根目录执行，现有依赖即可，无需安装。Windows终端设置 `PYTHONUTF8=1`、`PYTHONUNBUFFERED=1` 和指向本checkout的 `PYTHONPATH`。

```powershell
.venv/Scripts/python.exe -m app.context.cli budget --profile default
.venv/Scripts/python.exe -m app.context.cli budget --profile demo
.venv/Scripts/python.exe -m app.context.cli replay --profile default --output runtime/context-evidence/offline-default.json
.venv/Scripts/python.exe -m app.context.cli replay --profile demo --output runtime/context-evidence/offline-demo.json
node scripts/verify-context-browser.cjs --profile demo --output runtime/context-evidence/controlled-task10
node scripts/test-context-browser-options.cjs
```

`budget` 输出每个阶段 F/U/E/G/V/O/M/P/A 全部扣项；调用 `app/workflow/context_budget.py` 唯一工厂。当前离线实测：

| Profile | W | H | H1 | H2 | E | G | M | 每轮派生累计额度 |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| default | 128000 | 59880 | 41916 | 17964 | 6000 | 2000 | 3840 | 1135519 |
| demo | 18000 | 2691 | 1883 | 808 | 2250 | 563 | 540 | 174463 |

决策阶段固定前缀 F=2890。Task11在真实物流负例后仅补“decision_reason不是通用推理理由”的提示，F从2811增加79，表中预算由同一生产工厂重新派生，没有改窗口/阈值。128000是应用声明窗口，尚非验证过的供应商窗口；估算器 `cjk-ascii-protocol-v1` 已有前三付费轮11个非流真实usage配对，估计约为实际1.82–2.14倍，参数保持不变，不能视为通用tokenizer已校准。最终流usage未知，未填0。累计额度是容量上限，不是实际消耗或HTTP次数。

Profiles显式设置窗口/最终输出/用户上限/两种工具步数别名/工具结果/Top-K/40轮目标。default最终输出512；demo最终输出2000、工具步数3、Top-K5。两种别名始终一致；验收profile显式选择派生累计额度，忽略旧 `.env` 的32000费用项。普通 `load_settings()` 仍尊重旧显式费用配置。不会修改 `.env`。

默认21轮不出现 `context_downgrade`、`summary_trigger`、`summary_done`；demo出现全部三类。所有调用日志含真实注入的消息和预算，每轮都有history_ctx，SQL原文与检查点一致。摘要响应在最终流已被Event挂起时才释放，验证后台摘要能独立提交。H1/H2是软线：若达到H1后总历史仍超H，可继续按完整最旧轮降级，直到硬H满足；若合法压缩仍不够，明确失败，不删用户原话。

**摘要长度风险保留：** 50字目标的受控摘要允许实体较多时自然超过目标，末轮能看到最早段；200字受控变体使最早段在G预算中被省略，末轮只澄清订单号。测试明确要求此时不能恢复1001。旧段不回炉、没有最早话题固定保留；真实摘要质量和真实21轮仍待Task11，不能将离线名义成功当作真实验收。

## Task11 已执行的小额真实验证与有条件批准长批次

Task11已确认配置仅指向loopback3307/customer_service，并在每次迁移/核验实际连接上对照本地容器hostname/server_uuid/端口和SQL会话，执行现有migrate_context与verify_context；证据在 `runtime/context-evidence/task11-migration.json`。隐藏demo8004已健康启动并重启，原8002/8003不变。以下是复现入口；首次DDL只对已核实的目标执行。

```powershell
.venv/Scripts/python.exe -m app.context.cli migrate
.venv/Scripts/python.exe -m app.context.cli verify
pwsh -NoProfile -File scripts/start-context-demo.ps1 -Profile demo
```

`migrate`是显式DDL（已有知识、质量、退款及基础表DDL必须先具备）；`verify`及在线启动只读核验，不创建/修改应用SQL结构。启动器只处理本checkout的8004，检查保存的创建时间、完整命令行/工作区、解释器、启动祖先和监听PID；PID文件本身不能授权停止，未知监听直接拒绝。8002/8003不变。启动隐藏窗口，default/demo分别写 `runtime/workflow/context-{profile}-8004.sqlite`。

真实调用必须先用整组运行标识和限额启动，再用完全一致的参数验证；下例是**有条件批准、须最终full通过后执行的真实21轮调用**：

```powershell
pwsh -NoProfile -File scripts/start-context-demo.ps1 -Profile demo -RunId ch07-demo-001 -MaxGlmCalls 150 -MaxEmbeddingCalls 50 -MaxRerankCalls 25
node scripts/verify-context-browser.cjs --live --profile demo --run-id ch07-demo-001 --max-glm-calls 150 --max-embedding-calls 50 --max-rerank-calls 25 --output runtime/context-evidence/ch07-demo-001
.venv/Scripts/python.exe scripts/context-storage-evidence.py --profile demo --conversation-id ID --output runtime/context-evidence/ch07-demo-001/storage.json
```

浏览器默认受控模式；live只访问固定8004，先GET health核对profile/run/三项限额才创建会话。自动轨迹不提交业务动作。服务器创建的GLM同步/异步、背景摘要、BGE嵌入和重排在物理HTTP派发前预占同一run账本；超限直接拒绝，失败请求也占次数，重启同一run不可重置或变更限额。账本独立为 `runtime/context-evidence/call-ledger.sqlite`。验收期间禁用独立评估任务；外部注入客户端由创建者负责。普通运行不注入cap。

取证脚本只SELECT SQL原文/锚点/段落，并以SQLite `mode=ro`、`query_only`读取现有根。缺失根返回unknown，不创建数据库、不捏造原轮元数据。可用 `--checkpoint PATH` 指定已存在的检查点；输出会话原文应留在忽略目录。Task11小额真实SQL取证已执行；已有离线检查证实原始SQLite字节读取前后不变。

`runtime/context-evidence/` 保存预算、replay、app.log、截图及账本，已忽略。回放结果同时列出实际摘要源范围、遗漏段、原始SQL投影和检查点路径；不要提交这些内容或把真实凭据写入报告。

小额run `ch07-small-20261017` 的限额固定60GLM/12嵌入/6重排，失败及摘要均计数。原六页结束后人类明确批准追加两页，同run最终46/2/2，八个付费页面轮与一个免费寒暄。政策问答、1002本轮物流读取、选单暂停/刷新恢复/寒暄取消、原会话引用回载有实际证据。1001完整句两次control_schema失败，第一次正文未捕获，第二次捕获非空decision_reason；只改提示强调售后专属字段后，获批原句与政策两页均done且字段均null。OTHER预期的幻想问句实际闲聊，有语义依据但未充分证明OTHER路径。历史原工具JSON渲染缺陷已按设计改为仅用户/最终答复气泡及原轮工具徽章，API原工具原文保留；真实桌面及稳定窄屏回载验证无JSON正文。

12个真实标注摘要首版9/12被validator接受；三项近义状态表达被拒。仅补规范表达提示后，这三项各一次复验3/3，未重跑全12套，两个版本分开保留。真实O-101摘要经来源范围提取并被真实理解调用恢复，不能代替真实21轮的1001保留验收。小额SQL取证会话65/66/67原文与检查点相等，S/L均未前进，没有真实长会话级联证据。

新提示后的离线CLI两profile各21轮，default105/demo110模型包，原文与检查点相等；demo末轮注入最早订单摘要。200字摘要遗漏负例仍要求安全澄清。真实两组21轮预计每组100–140次GLM（包含后台摘要），申请的硬上限各150GLM/50嵌入/25重排；人类已明确有条件批准，修后两页已通过，最终full全绿才启动；达到上限或任一轮失败立即终止并保留原批次。完整状态见 `docs/superpowers/reports/2026-10-17-context-management-acceptance.md`。


Task11最终源码full为2699 passed/184 skipped（551.94s）；修后两页通过后已执行获批默认真实批，但第3句“运费怎么算？”的理解输出误成工具动作JSON，严格query schema拒绝，2/21 done后即停，run累计11GLM/1嵌入/1重排。没有重试或改schema；demo尚未启动。原始失败与SQL/hash/usage证据见详细验收报告。父控正合并最终整分支发现，后续真实调用须等明确整合修复/复验范围；原run不重置。
