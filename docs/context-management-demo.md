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
| default | 128000 | 59880 | 41916 | 17964 | 6000 | 2000 | 3840 | 1135124 |
| demo | 18000 | 2770 | 1939 | 831 | 2250 | 563 | 540 | 175174 |

决策阶段固定前缀 F=2811。128000是应用声明窗口，尚非验证过的供应商窗口；估算器版本 `cjk-ascii-protocol-v1`，没有真实usage校准。累计额度是容量上限，不是实际消耗或HTTP次数。

Profiles显式设置窗口/最终输出/用户上限/两种工具步数别名/工具结果/Top-K/40轮目标。default最终输出512；demo最终输出2000、工具步数3、Top-K5。两种别名始终一致；验收profile显式选择派生累计额度，忽略旧 `.env` 的32000费用项。普通 `load_settings()` 仍尊重旧显式费用配置。不会修改 `.env`。

默认21轮不出现 `context_downgrade`、`summary_trigger`、`summary_done`；demo出现全部三类。所有调用日志含真实注入的消息和预算，每轮都有history_ctx，SQL原文与检查点一致。摘要响应在最终流已被Event挂起时才释放，验证后台摘要能独立提交。H1/H2是软线：若达到H1后总历史仍超H，可继续按完整最旧轮降级，直到硬H满足；若合法压缩仍不够，明确失败，不删用户原话。

**摘要长度风险保留：** 50字目标的受控摘要允许实体较多时自然超过目标，末轮能看到最早段；200字受控变体使最早段在G预算中被省略，末轮只澄清订单号。测试明确要求此时不能恢复1001。旧段不回炉、没有最早话题固定保留；真实摘要质量和真实21轮仍待Task11，不能将离线名义成功当作真实验收。

## Task11 待执行：真实数据库与应用

以下命令已提供接口/离线守卫验证，**尚未在3307应用库或健康真实应用执行**。Task11按授权完成前置原有DDL、迁移、核验与上线；不把待执行命令写作通过。

```powershell
.venv/Scripts/python.exe -m app.context.cli migrate
.venv/Scripts/python.exe -m app.context.cli verify
pwsh -NoProfile -File scripts/start-context-demo.ps1 -Profile demo
```

`migrate`是显式DDL（已有知识、质量、退款及基础表DDL必须先具备）；`verify`及在线启动只读核验，不创建/修改应用SQL结构。启动器只处理本checkout的8004，检查保存的创建时间、完整命令行/工作区、解释器、启动祖先和监听PID；PID文件本身不能授权停止，未知监听直接拒绝。8002/8003不变。启动隐藏窗口，default/demo分别写 `runtime/workflow/context-{profile}-8004.sqlite`。

真实调用必须先用整组运行标识和限额启动，再用完全一致的参数验证；下例是**待Task11批准的真实21轮调用**：

```powershell
pwsh -NoProfile -File scripts/start-context-demo.ps1 -Profile demo -RunId ch07-demo-001 -MaxGlmCalls 150 -MaxEmbeddingCalls 50 -MaxRerankCalls 25
node scripts/verify-context-browser.cjs --live --profile demo --run-id ch07-demo-001 --max-glm-calls 150 --max-embedding-calls 50 --max-rerank-calls 25 --output runtime/context-evidence/ch07-demo-001
.venv/Scripts/python.exe scripts/context-storage-evidence.py --profile demo --conversation-id ID --output runtime/context-evidence/ch07-demo-001/storage.json
```

浏览器默认受控模式；live只访问固定8004，先GET health核对profile/run/三项限额才创建会话。自动轨迹不提交业务动作。服务器创建的GLM同步/异步、背景摘要、BGE嵌入和重排在物理HTTP派发前预占同一run账本；超限直接拒绝，失败请求也占次数，重启同一run不可重置或变更限额。账本独立为 `runtime/context-evidence/call-ledger.sqlite`。验收期间禁用独立评估任务；外部注入客户端由创建者负责。普通运行不注入cap。

取证脚本只SELECT SQL原文/锚点/段落，并以SQLite `mode=ro`、`query_only`读取现有根。缺失根返回unknown，不创建数据库、不捏造原轮元数据。可用 `--checkpoint PATH` 指定已存在的检查点；输出会话原文应留在忽略目录。真实SQL取证命令仍待Task11；已有离线检查证实原始SQLite字节读取前后不变。

`runtime/context-evidence/` 保存预算、replay、app.log、截图及账本，已忽略。回放结果同时列出实际摘要源范围、遗漏段、原始SQL投影和检查点路径；不要提交这些内容或把真实凭据写入报告。
