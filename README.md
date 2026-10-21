# 电商智能客服

第九步本地可观测性与数据飞轮：本地Langfuse、正式证据置信度、三路问题池、人工审核补库、意图成本与评估趋势已实现并实际运行。[原始提示词与DDL](docs/prompts/step-09-observability-flywheel.md)、[本地演示命令](docs/ch09-local-demo.md)、[PyCharm逐步验收](docs/ch09-pycharm-acceptance.md)、[手动验收](docs/ch09-manual-acceptance.md)及[真实结果与限制](docs/superpowers/reports/2026-10-20-reference-acceptance.md)分别保留需求与事实。客服8006、待审`/review`、观测`/observability`、Langfuse3000，页面沿用聊天界面的浅灰绿与墨绿风格。原两轮20题有9/8个阶段错误，后续一轮完整20题错误0、Faithfulness0.875；配置和有效分母分别展示，不当作两轮同配置质量全绿。留出集误放4、误拒9等质量项继续记录。

第八步工具系统与MCP：两个独立业务Server、动态工具注册、统一执行审计和工单确认流已实现。入口见[演示命令](docs/tool-system-demo.md)、[PyCharm验收](docs/ch08-pycharm-acceptance.md)、[手动验收](docs/ch08-manual-acceptance.md)及[第八步原始提示词与DDL](docs/prompts/step-08-pluggable-tools.md)。测试与真实验收的版本、失败和范围分别保留在[开发记录](dev-notes/ch08.md)及报告中。

第七章分层上下文的离线21轮回放、预算profile、8004进程守卫和共享物理HTTP限额见[可复现验收说明](docs/context-management-demo.md)。离线回放与受控浏览器已验证；3307迁移、真实应用启动及真实长对话验收留待Task11，不把离线结果当作模型质量结论。

300 题四策略已完成全部 1200 条尝试：1188 条成功、12 条失败，0 未执行。原 158 题保持，剩余 142 题以 8 题并发补跑约 11 分 22 秒。公平共同题集上，混合加重排的检索排名和答案要点覆盖最高。见[实际结果分析](docs/validation/merchant-rag-comparison-analysis.md)、[完整合并报告](docs/validation/merchant-rag-comparison.md)与[独立验收](docs/validation/merchant-rag-completion-proof.json)。错误及两次运行的真实来源均保留。

基于 Python、FastAPI、LangChain、SQLAlchemy、MySQL 和 Milvus 的电商客服项目。开发按步骤推进：第一步跑通流式多轮对话与售后字段提取；第二步接入单轮 Function Calling 和持久化；第三步建立可恢复的知识库；第四步加入混合检索、重排、质量控制与评估。

每轮一次工具选择、最多一个逻辑工具、一次最终流式回答，不运行 Agent Loop。订单、商品、物流工具使用随机模拟数据；人工工单真实写库。`query_faq` 保留原入参出参契约，内部使用 BGE-M3 Dense 与 Milvus 原生中文 BM25 各召回 Top-50，通过 RRF 融合，再由 `BAAI/bge-reranker-v2-m3` 重排为 Top-10。正文从 MySQL 已完成向量化的知识行读取。

第四步新增来源引用、知识充分性自评、证据不足拒答与低置信度池、四策略评估和忠实度个案台账。页面支持点击 `[n]` 查看本轮原文和章节路径，完成回复后选择一次 👍/👎 并锁定；反馈当前只存页面状态。原售后信息提取接口保留。具体运行结果及错误分母见[校准](docs/validation/hybrid-retrieval-calibration.md)、[四策略对比](docs/validation/hybrid-retrieval-comparison.md)和[页面验证](docs/validation/hybrid-ui.md)，不以单元测试代替真实模型质量。

## 目录

| 路径 | 内容 |
| --- | --- |
| `app/api`、`app/core` | HTTP/SSE 接口、对话、Prompt、上下文预算与生成质量 |
| `app/retrieval` | 查询理解、Dense/BM25/RRF、重排与检索服务 |
| `app/knowledge` | Markdown 切分、历史 QA 抽取、双写与恢复任务 |
| `app/db`、`app/repositories`、`app/quality` | SQLAlchemy 映射、短事务仓储、质量迁移与台账 |
| `app/tools` | 五个 LangChain 业务工具与执行基础设施 |
| `app/static` | 聊天气泡、流式显示、引用来源与一次性反馈 |
| `sql`、`knowledge-docs` | 用户原始 DDL、种子及合成知识文档 |
| `evals`、`tests` | 标注评估集、真实评估 CLI 与回归测试 |
| `prompt.md`、`dev-notes`、`docs` | 每步提示词/插件、阶段记录、设计/计划/源码解析/验证 |

## 安装与数据库

使用 Python 3.11–3.13；本轮运行环境为 Python 3.13.5。以下命令在当前项目 checkout 根目录执行，Windows 终端可设置 PYTHONUTF8=1 / PYTHONIOENCODING=utf-8 使中文控制台输出也使用 UTF-8：

```powershell
$env:UV_CACHE_DIR = '.cache/uv'
uv sync --locked
if (-not (Test-Path -LiteralPath '.env')) { Copy-Item .env.example .env }
docker compose -p ecs-tool-calling --profile test up -d --wait --wait-timeout 120
docker compose -f compose.milvus.yaml -p ecs-knowledge up -d
```

在本地 `.env` 填写 `LLM_API_KEY`、`SILICONFLOW_API_KEY`、`MYSQL_PASSWORD` 和 `MYSQL_ROOT_PASSWORD`，不要提交密钥。当前模型为 `glm-5.3-flash`，标准 Chat Completions 上游为 `https://open.bigmodel.cn/api/paas/v4/`。应用默认数据库是 `127.0.0.1:3307/customer_service`，隔离测试库是 `127.0.0.1:3308/customer_service_test`。

首次空 MySQL 卷执行 `sql/schema.sql` 和 `sql/seed.sql`，创建 FAQ/会话/消息/工单四表。已有卷不会重跑初始化；知识两表和质量两表通过显式迁移执行，应用启动只核验，不执行 ORM 建表。迁移遇到现有结构不符会失败，不自动改列或删表。保留已有数据卷，不使用 `down -v`。

```powershell
uv run --locked python -m app.knowledge.cli migrate
uv run --locked python -m app.quality.cli migrate
uv run --locked python -m app.knowledge.cli init-vectors
```

当前 Compose 为 Milvus 3.0.2；中文分词使用内置 `chinese` analyzer，`text` 字段挂 BM25 函数。用户已批准开启该版本 TEXT 所需的 StorageV3（`config/milvus-user.yaml`）；已有数据迁移需核对版本支持，不把关闭开关当作数据格式回滚。

## 建库、切换与恢复

2026-10-12 在线聊天已发布八份商家演示资料（与 300 题评估共用的冻结语料）：[资料目录](evals/datasets/merchant-rag-300/corpus)。本机使用 `knowledge_merchant_live`，只索引这份资料的 50 块；MySQL 保留旧 84 块和全部会话。旧 XM 型号、普通配送 8 元等规则不再参与该集合的回答。发布范围、物理主键和保留数据校验见[发布记录](docs/validation/online-merchant-publication.json)。

本机 `.env` 的 `RERANK_MIN_SCORE=0.3218679428100586` 来自这份语料的八道独立检索校准题，见[原始分数与选择过程](docs/validation/online-merchant-calibration.json)。该值只是当前演示语料的校准结果，不代表业务置信度概率；改写和生成另由聊天验收检查。`ONLINE_REASONING_EFFORT=low` 显式传给在线 GLM，保持回答 512、改写/自评 2048 和零重试；不填写则保持上游默认行为，评估专用参数仍独立。

首次部署到**空知识表**时，可在 `.env` 设置独立 `MILVUS_COLLECTION=knowledge_merchant_live`，导入同一份资料，再运行下方既有双写/核验命令：

```powershell
$types = @{ 'after-sales-manual'='manual'; 'product-faq'='faq'; 'product-specs'='manual'; 'returns-policy'='policy'; 'membership-benefits'='policy'; 'integral-rules'='policy'; 'invoice-policy'='policy'; 'cat-bed-care'='manual' }
foreach ($name in $types.Keys) {
  uv run --locked python -m app.knowledge.cli import-document --path "evals/datasets/merchant-rag-300/corpus/$name.md" --type $types[$name]
}
uv run --locked python -m app.knowledge.cli vectorize-pending --batch-size 20
uv run --locked python -m app.knowledge.cli rebuild-hybrid --batch-size 20
uv run --locked python -m app.knowledge.cli verify-hybrid --batch-size 20
```

已有混合资料的数据库不能直接全库重建到这份集合，否则会重新混入旧规则。本机发布按 50 个已登记主键独立核验；全库 `verify-hybrid` 预期集合等于所有 done 主键，不能拿它核验这种资料子集。导入 CLI 不去重，请勿重复导入已经存在的资料。

以下旧演示建库命令用于复现第三步/早期第四步，使用另一集合和隔离数据库：

新集合默认名为 `knowledge_hybrid`，旧 Dense 集合不原地改 schema。已有 MySQL `done` 原文可重建新集合并核验；新文档先落 `pending`，向量 ACK 和读回核对后才回填为 `done`。

```powershell
uv run --locked python -m app.knowledge.cli import-document --path knowledge-docs/demo-policy.md --type policy
uv run --locked python -m app.knowledge.cli import-document --path knowledge-docs/demo-faq.md --type faq
uv run --locked python -m app.knowledge.cli import-document --path knowledge-docs/demo-manual.md --type manual
uv run --locked python -m app.knowledge.cli import-document --path knowledge-docs/retrieval-models.md --type faq
uv run --locked python -m app.knowledge.cli vectorize-pending --batch-size 20
uv run --locked python -m app.knowledge.cli rebuild-hybrid --batch-size 20
uv run --locked python -m app.knowledge.cli verify-hybrid --batch-size 20
```

重复导入会新增知识行，不等于文档去重；中断恢复只重跑 `vectorize-pending`。Milvus 主键来自 MySQL，同一主键 upsert 可重放；重建已完成行不会把 MySQL 状态退回 pending。向量化文本只含 category/questions/answer，章节路径、内容类型、关键条款、前后指针保存在 MySQL，不进入向量。双写恢复的历史实证见[第三步记录](docs/validation/ch03-results.md)。

历史知识挖掘按北京时间半开区间读取已结束会话，分批抽 QA、暂存、整体精确去重，再补向量：

```powershell
uv run --locked python -m app.knowledge.cli mine-conversations --start 2026-10-06T00:00:00 --end 2026-10-07T00:00:00 --batch-size 20
uv run --locked python -m app.knowledge.cli deduplicate-staging
uv run --locked python -m app.knowledge.cli vectorize-pending
uv run --locked python -m app.knowledge.cli run-daily
```

`run-daily` 处理北京时间前一天，并沿用同一 MySQL 任务锁；取消释放连接，不暗中重复调用。`scripts/run-knowledge-daily.ps1` 可交给宿主调度器，本轮未注册定时任务，也未读取生产历史。

## 校准与四策略评估

评估集为 30 题、五类桶，每类都有 easy/medium/hard，另有不重叠的 8 道校准题。默认 `--database test` 固定 3308，用自有合成知识行和 UUID 集合，结束清理这些临时资源并保留忠实度台账。真实评估会调用配置的收费模型；报告逐项保留错误、未执行和每个指标的有效分母。

```powershell
uv run --locked python -m evals.evaluate_retrieval --mode calibrate --output .cache/calibration-new.json
# 查看校准报告，仅将有效的 calibration.threshold 写入本地 .env 的 RERANK_MIN_SCORE。
# 不借用单元测试中的示例阈值；更换模型、知识集或重排配置后需要重新校准。
uv run --locked python -m evals.evaluate_retrieval --mode compare --output .cache/comparison-new.json
```

报告路径必须是新路径，CLI 拒绝覆盖历史。默认测试库校准的阈值只代表本轮合成语料；正式知识库请在相同数据分布上校准，可显式使用 `--database configured` 读取当前配置库与集合。只有 `hybrid_rerank` 使用校准后的重排门槛，三条基线仅做内容自评，报告明确披露这一差异；不能把全部生成变化归因于排序。COSINE/BM25/RRF 分数不当作概率比较。本次八题样本内校准F1=1仍出现口语“邮费是多少”的误拒答（正确证据.701876低于门槛.820160），见页面报告；不能把该门槛推广为已验证的业务置信度。

Faithfulness 裁判逐条核对断言与实际证据全集。非法/截断裁判输出记错误，不伪造编造结论；无断言拒答记 n/a，不记完美分。同题再次编造更新证据快照并累加次数；已处置题复发回到未解决，保留既往处置时间。

```powershell
uv run --locked python -m app.quality.cli cases --status 未解决
# 下列题号只是操作示例，先从 cases 输出选择实际存在的题号。
uv run --locked python -m app.quality.cli resolve --eval-id TA01 --status 已解决 --resolution '已补充知识并重跑该题验证'
```

## 启动、页面与 SSE

配置库已有八张表、混合集合已建并核验、`RERANK_MIN_SCORE` 是有效有限数后启动。缺门槛/集合/正确质量表时启动失败，不填假门槛绕过。

```powershell
uv run --locked uvicorn app.main:create_app --factory --host 127.0.0.1 --port 8000 --workers 1
```

默认 Workflow 在启动控制台（stderr）输出单行 JSON 审计：`workflow_node` 包含检索、置信度闸理由、路由与工具顺序；`workflow_lifecycle` 包含本轮唯一终态与已观察计数；`workflow_ticket` 关联确认工单的原用户和回复身份。只输出受控身份、枚举和计数，工具调用 ID 记摘要，不记录问题、证据、参数、控制 JSON 或异常正文；重复创建应用不会叠加处理器，无需额外日志服务。

浏览器打开 <http://127.0.0.1:8000/>。Enter 发送，Shift+Enter 换行，可停止生成。页面先创建会话后连续多轮聊天；新对话创建独立会话，暂不加载已有记录。保持单 worker，因为会话占用锁在单进程内；消息保存在 MySQL，可跨服务重启读取。

SSE 的 `status` 包含工具与 `checking` 阶段，知识回答在第一段 `delta` 前发送 `citations`；`done` 带真实字符串 `conversation_id` 和 `message_id`，必须在最终消息提交后才发送。来源编号限定本轮，跨轮 `[1]` 不混用；所有 ID 使用十进制字符串以保留超大整数。网络增量不保证一个增量恰好一个 tokenizer token。

证据按完整知识块裁剪，历史按完整轮次裁剪；最佳证据放首尾。自评 useful=false 的合法判定返回固定拒答，并与问题池同事务提交。认证、超时、结构化非法、预算或生成校验错误不冒充拒答入池。失败/取消的流水保留审计但不回放成完整历史；取消或错误回复不出现反馈按钮。

## curl 演示

PowerShell 用 UTF-8 无 BOM 文件传 JSON，避免转义损坏。当前商家演示资料中，“给大猫用的那款猫砂盆能装多少砂”对应 MH-LP200 的 12L；普通地区 80 元商品配送费为 10 元，满 99 元包邮；库外问题可问宠物美容服务价格。资料只用于项目演示。

```powershell
$utf8 = [System.Text.UTF8Encoding]::new($false)
New-Item -ItemType Directory -Force .cache | Out-Null
[System.IO.File]::WriteAllText((Join-Path (Get-Location) '.cache/create.json'), '{"user_id":"demo-user"}', $utf8)
$created = curl.exe --max-time 75 -sS -H 'Content-Type: application/json' --data-binary '@.cache/create.json' http://127.0.0.1:8000/api/conversations | ConvertFrom-Json
$conversationId = $created.conversation_id
foreach ($question in @('给大猫用的那款猫砂盆能装多少砂', '普通地区买80元商品，邮费多少？', '你们提供宠物洗澡美容服务吗，具体价格是多少？')) {
  $payload = @{conversation_id=$conversationId; message=$question} | ConvertTo-Json -Compress
  [System.IO.File]::WriteAllText((Join-Path (Get-Location) '.cache/chat.json'), $payload, $utf8)
  curl.exe -N --max-time 260 -H 'Content-Type: application/json' --data-binary '@.cache/chat.json' http://127.0.0.1:8000/api/chat
}
# 分类过滤由可信请求字段提供，不让模型生成过滤表达式。
$payload = @{conversation_id=$conversationId; message='MH-W40水箱多大？'; category='商品规格手册'} | ConvertTo-Json -Compress
[System.IO.File]::WriteAllText((Join-Path (Get-Location) '.cache/filtered.json'), $payload, $utf8)
curl.exe -N --max-time 260 -H 'Content-Type: application/json' --data-binary '@.cache/filtered.json' http://127.0.0.1:8000/api/chat
```

## 预算与边界

| 配置 | 默认值 | 用途 |
| --- | --- | --- |
| `MAX_OUTPUT_TOKENS` | 512 | 最终聊天回答及原售后抽取 |
| `QUERY_MAX_OUTPUT_TOKENS` | 2048 | 仅改写结构化输出 |
| `SUFFICIENCY_MAX_OUTPUT_TOKENS` | 2048 | 仅知识充分性结构化输出 |
| `QUERY_TIMEOUT_SECONDS` | 60 | 用户批准的改写期限 |
| `SUFFICIENCY_TIMEOUT_SECONDS` | 20 | 自评期限 |
| `FAQ_TIMEOUT_SECONDS` | 90 | 整条知识工具链期限 |
| `CHAT_TIMEOUT_SECONDS` | 240 | 每轮绝对期限 |
| `EMBEDDING_TIMEOUT_SECONDS` / `MILVUS_TIMEOUT_SECONDS` / `RERANK_TIMEOUT_SECONDS` | 20 / 5 / 20 | 组件期限，仍受外层约束 |
| `TOOL_INPUT_TOKEN_BUDGET` | 8000 | 完整 Prompt、历史、工具与证据估算预算 |
| `FAITH_JUDGE_INPUT_TOKEN_BUDGET` / `FAITH_JUDGE_MAX_OUTPUT_TOKENS` | 16000 / 2048 | 独立忠实度裁判 |
| `QA_MAX_OUTPUT_TOKENS` | 2048 | 离线历史 QA 抽取 |
| `RERANK_MIN_SCORE` | 必须校准 | 线上重排低分门槛 |

模型及 FAQ 不额外重试，取消传播至底层。其他业务工具沿用原有限重试。用户批准保留 PyMilvus 3.0.2 内部不可公开关闭的一次 schema 缓存刷新重试；写入沿用同一主键，所有逻辑调用受外层期限限制。修改 `.env` 后重启进程。

## 冻结 300 题评估工作台

当前交付：合法固定pilot `aecdf615794d4ccdad984c9caeda979f` 通过后启动的全量 `2486afc8e62e4550bdfec6d676a27d84` 已中断，原报告保留。用户要求最快完成后，新run `7adfc4c7dc3a4750885c23c94f3be671` 只补142个未结束题组，568条全部尝试、562完成/6错误、清理成功；保留原158题后，300题1200条中1188完成/12错误。两次按整题四路合并，配置指纹`46d11df…`逐值相同，实际操作并发2→8另记；未改模型/预算/期限/retry/Prompt/冻结数据，也未重试原6条明确错误。共同四路完整题289，其中可答230、库外59；完整结论与真实分母见[结果分析](docs/validation/merchant-rag-comparison-analysis.md)、[合并报告](docs/validation/merchant-rag-comparison.md)及[当前交付](docs/validation/rag-evaluation-delivery.md)。原中断run的历史清理失败仍明示。

前一透明观测阶段：用户“继续”获root执行前放行后，原参数透明观測pilot `7d421bf017ff4c02afec385178848fde` 从真实8002页面只启动一次，40尝试/32完成/8改写错误（B3/B54各一次共享结构失败影响四路），清理成功。HTTP200/stop仍因根list/answer包裹对象被生产严格QueryPlan拒绝；无参数或源码变更，191d53…配置保持。该轮actual matching_pilot=false、full未运行、收费停止。详见[该轮原报告](docs/validation/merchant-rag-observed-pilot.json)、[安全观测](docs/validation/merchant-rag-observed-rewrite-evidence.md)、[精确分母分析](docs/validation/merchant-rag-observed-analysis.md)与[资源归因](docs/validation/merchant-rag-observed-resource-proof.json)。

此前阶段：N1/N2已在源码 `42bd812` 的唯一额外定点复核通过。原固定pilot `52678f9492114f1789466442e575c168` 的9/40和前一low pilot `201215b02b874feea7e866db10ee23db` 的39/40、全部错误及原时钟完整保留。评估专用low源码 `cfc65fd` 已独立复核；原两条真实单调用探针均合法，依赖按明确授权恢复。用户另行批准C5/dense单次诊断及条件继续：诊断仅answer1、stop/引用合法且清理成功；随后真实8002页面仅启动一次新固定pilot `b1af9aadc0094141aa5df5ae0ec91bd1`，40尝试/32完成/8改写错误（B54/E19各一次共享失败影响四路）、清理成功。实际matching_pilot=false，full仍未运行。Task10未完成，详见[交付状态](docs/validation/rag-evaluation-delivery.md)、[新实际报告](docs/validation/merchant-rag-c5-followup-pilot.json)、[精确分析](docs/validation/merchant-rag-c5-followup-analysis.md)及[单次诊断](docs/validation/merchant-rag-c5-diagnostic.md)；未调参、重标或通过重复试跑洗分。

工作台入口为 `/rag-eval`，聊天入口为 `/`。默认 `RAG_EVALUATION_ENABLED=false`，页面可读取资料、历史与合法已提交报告；启动和取消需要显式启用，旧 pre-audit v2 下载已由 N2 最小兼容修复恢复。新评估固定使用 `merchant-rag-300-v1`：五桶各 60 题、八篇 50 块、固定 pilot 10 题 / 40 条策略记录；全部40条合法完成、当前 audit-v1/source-map 与冻结资料及配置匹配、清理成功后才能运行 full 300 题 / 1200 条。线上原有 `calibrated_score` 门槛保持，新评估采用共同内容充分性门槛 `content_ablation`。

在当前 checkout 根目录启动新服务，端口须与来源白名单一致。已有服务无需停止；以下以独立端口 8002 为例，仍沿用本地 `.env` 的模型、密钥、预算和线上校准值：

```powershell
$env:PYTHONUTF8 = '1'
$env:PYTHONIOENCODING = 'utf-8'
$env:RAG_EVALUATION_ENABLED = 'false'
$env:RAG_EVALUATION_ALLOWED_ORIGINS = '["http://127.0.0.1:8002","http://localhost:8002"]'
uv run --locked uvicorn app.main:create_app --factory --host 127.0.0.1 --port 8002 --workers 1
```

上例为只读配置参考，本次文档阶段没有启动服务。只有控制端明确放行收费门禁后，才将 `RAG_EVALUATION_ENABLED` 设为 `true` 并重启自有服务。服务必须只有一个 worker；CLI 和 HTTP 共用 OS 文件锁，同一时刻只有一个运行，取消与清理结束前不会放行下一轮。重启会保留中断记录，不自动续跑收费请求。

```powershell
uv run --locked python -m evals.rag_workbench validate --dataset merchant-rag-300-v1
uv run --locked python -m evals.rag_workbench show --run-id '<已有实际32位run_id>'
```

下列收费运行命令仅供门禁放行后的复现。原任务要求先从真实页面启动 pilot 一次，核对合法输出与清理，服务端允许后再由同页启动 full 一次；页面与 CLI 不能重复或同时启动同批。

```powershell
uv run --locked python -m evals.rag_workbench run --dataset merchant-rag-300-v1 --scope pilot
uv run --locked python -m evals.rag_workbench run --dataset merchant-rag-300-v1 --scope full
```

API 基址 `/api/rag-evaluations` 提供 `GET /datasets`、`POST /runs`、`GET /runs`、`GET /runs/{run_id}`、`GET /runs/{run_id}/cases`、`GET /runs/{run_id}/cases/{eval_id}/{strategy}`、`POST /runs/{run_id}/cancel`、`GET /runs/{run_id}/export?format=json|markdown`。启动 JSON 仅接受 `dataset_id` 和 `scope`，取消发送 `{}`；不开放模型、预算、数据库或输出路径修改。新旧报告按各自指标口径展示，`vector` 对应内部 `dense`。

新运行的本地文件位于 `runtime/rag-evaluation/{run_id}/`，该目录已忽略，原始裁判与归属快照不提交。单份不可变 `source-map.json` 保留完整50块来源和本轮主键，逐题 `audit` 保留稳定组、答案要点及实际候选/最终排序 score/kind；不同分数种类不可直接比较。公共 `report.json` / `report.md` 经白名单投影并一致发布后才可下载，缺少历史捕获的数据保持 null/N/A。旧原始报告已原字节移到 `evals/legacy/rag-evaluation-history.json`，静态URL不再公开原始字段，安全历史API仍提供原指标。

材料与标注说明见[材料审计](docs/validation/rag-evaluation-materials-audit.md)，受控UI边界见[页面验证](docs/validation/rag-evaluation-ui.md)。初次实际失败pilot的[公开JSON](docs/validation/merchant-rag-pilot.json)与[Markdown](docs/validation/merchant-rag-pilot.md)保留所有阶段、指纹、计数、指标分母/排除原因与审计来源；该轮共同合法题仅D1/D3，不足以比较可答生成。Ruling25补跑及[终态比较](docs/validation/merchant-rag-comparison.md)已交付，真实失败保留，不用受控夹具替代模型质量。

这版材料参考同一金标题库构造，只能支持项目内受控比较。候选 Top-50 等于全部 50 块，候选覆盖饱和不能证明泛化；实际比较还需看首命中、Top-5/10 完整组、Prompt 覆盖、回答要点与忠实度，并列出各指标有效分母、错误与四路共同有效子集。部分失败如实保留，不通过重复全量收费洗分。

## Workflow 与 Agent 演示

正式 `/api/chat` 使用固定 Workflow 分流与有界 Agent 子图。知识问题先强制检索和检查置信度；订单、物流和售后交给 Agent；明确问候、感谢和告别使用零模型固定回复。投诉提供独立的转人工、建工单按钮，只有明确确认建工单才写库。

裸循环教学演示默认不调用模型：

```powershell
uv run --locked python -m app.agent.cli demo
```

示例会依次执行 `query_order`、`query_logistics` 并回灌工具结果。这些业务查询返回带 `mock` 标记的演示数据；FAQ 读取真实知识库，工单写入 MySQL。裸循环供走读，正式 HTTP 使用 LangGraph。

已配置 merchant 集合和原校准值后，以单实例、单 worker 启动：

```powershell
uv run --locked uvicorn app.main:create_app --factory --host 127.0.0.1 --port 8002 --workers 1
```

实际聊天地址为 [http://127.0.0.1:8002/](http://127.0.0.1:8002/)。MySQL 保存会话、消息、知识原文、质量记录和工单；官方 `AsyncSqliteSaver` 在 `runtime/workflow/checkpoints.sqlite` 保存 Workflow 根状态与旧操作快照。该目录已忽略且不由静态服务公开。同一 SQLite 重启后新消息从 START 开始，旧完成回复的按钮仍按原 checkpoint 校验。会话锁属于进程，因此保持单 worker。

报告工具默认不收费，所有未执行题保留分母：

```powershell
uv run --locked python -m evals.evaluate_workflow --mode intent --output .cache/workflow-intent-not-executed.json
uv run --locked python -m evals.evaluate_workflow --mode chat --output .cache/workflow-chat-not-executed.json
```

真实验收命令须在获授权的有界验收中运行：

```powershell
uv run --locked python -m evals.evaluate_workflow --mode intent --live --output .cache/workflow-intent-live.json
node scripts/verify-workflow-browser.cjs --url http://127.0.0.1:8002/ --mode live
# 用上一步实际run目录中的results.json，读取已有SSE/SQL/SQLite证据，不重复调用聊天模型。
uv run --locked python -m evals.evaluate_workflow --mode chat --live --evidence .cache/workflow-browser/live/<实际run-id>/results.json --output .cache/workflow-chat-live.json
```

修复后可用 `--cases logistics,two-step,usage-help` 仅执行白名单中的固定场景；未选项仍记未执行，投诉附加按钮场景只随 complaint/default 执行。非法、空或重复名称在浏览器启动前拒绝。

固定意图集为21题加3题边界，每题单次；浏览器固定场景每轮上限240秒，相同链路首次失败停止后续收费。32000账本统计意图与 Agent 决策/最终调用；检索改写和充分性沿用各自预算、期限并单独说明。错误、超时、截断、资料不足拒答及未执行分别统计，实际证据和完成范围见[本次验收](docs/validation/2026-10-13-workflow-agent-acceptance.md)。

固定功能场景已按各次实际证据覆盖，来源与原失败详见验收记录。当前状态以本页“第五步最终验证”和验收文档末尾为准；历史1782/118及窄修复72项结果不替代最终提交验证。两步功能正常但严格主意图订单/物流差异仍保留。

## 回归与开发记录

```powershell
uv run --locked pytest -q
uv run --locked pytest -q --run-mysql --run-milvus -o faulthandler_timeout=30
git diff --check
```

2026-10-10，生产修复提交 `77d7d02ef1fb500e3ae00f069c368fd204135b3a` 的默认完整回归 **1386 passed、116 skipped（250.03秒）**；最后显式 MySQL/Milvus完整回归 **1502 passed、0 failed、0 skipped（388.30秒）**。显式首轮的四个子进程fixture接线失败已保留，最小fixture修正后才得到该绿色结果。原I1–I4与随后N1/N2均已关闭；`42bd812` 最终七文件定向回归 **242 passed、1 skipped（229.84秒）**，唯一额外定点复核规格/质量PASS，无新问题。上述均为已读取的原始证据，本次真实阶段没有重复套件。

2026-10-11，评估专用low配置 `cfc65fd` 的已保存工程证据为确认RED **17 failed、8 passed（16.49秒）**，GREEN **25 passed（24.08秒）**，最终受影响套件 **262 passed、7 skipped（170.03秒）**，最终默认完整套件 **1438 passed、116 skipped（260.94秒）**。规格PASS、质量Approved，无Critical/Important；真实调用阶段读取已有日志，未重复套件。专用设置 `RAG_EVALUATION_REASONING_EFFORT=low` 只传给评估拥有的模型，在线实例保持原参数；新字段参与配置指纹，旧pilot不能授权新配置full。

此前 Task10 工程提交 `ab25215` 的 **1358 passed、116 skipped / 显式1474 passed** 及累计期限诊断仍为历史证据。受控测试与真实服务检索均不等于真实模型质量。

此前混合检索阶段显式回归 **1205 passed**、默认 **1096 passed、109 skipped** 为历史记录。此前实际云端比较为 **101/120 项完成、19 项错误**，口语邮费问题仍有误拒答，详见[历史本轮结果](docs/validation/hybrid-retrieval-results.md)及[审查记录](docs/validation/hybrid-retrieval-review.md)，不替代新300题结果。

默认回归跳过真实 MySQL/Milvus 集成；显式启用但服务未就绪会失败。受控模型与确定性向量测试证明协议/事务/错误边界，不证明上游事实质量。第四步过程记录在 [dev-notes/ch04.md](dev-notes/ch04.md)；历史文件名保留原提示词约定，README 和提交不使用章名标记开发阶段。

本轮开发使用 `feat/hybrid-retrieval`，真实验收使用自有测试资源；主库建库、业务数据校准、主 checkout 部署和调度器注册不由测试脚本自动执行。旧[第二步验证](docs/validation/tool-calling-results.md)与[第三步验证](docs/validation/ch03-results.md)保留，不能用旧数字代替当前结果。

### 第五步最终验证（2026-10-14）

产品代码 `919662e` 已完成整分支审查及四项修复复审。相关166项通过；完整回归1843通过/118跳过，唯一受控浏览器启动路径错误补配置后单项复验通过；真实隔离MySQL/SQLite10项通过。原始失败及分开计数见[最终验收](docs/validation/2026-10-13-workflow-agent-acceptance.md)。最终8002真实浏览器问候通过、零模型调用，默认控制台可见节点与唯一终态日志。两步功能已通过但严格主意图订单/物流差异保留，未重跑300题。

本机执行受控浏览器回归时，除Node依赖外需指向已经安装的Chromium：

```powershell
$env:WORKFLOW_BROWSER_CONTRACT = '1'
$env:WORKFLOW_CHROMIUM_PATH = 'C:/Users/beemines/AppData/Local/ms-playwright/chromium-1234/chrome-win64/chrome.exe'
```

当前演示为 http://127.0.0.1:8002/?ui=20261014-dialog2 ，运行工作树和检查点继续保留，避免影响已打开的验收页面。
### 人工与工单交互调整

转人工使用浅绿圆角主题确认弹窗，确认后以独立服务通知及客服小猫新气泡显示。工单由用户在空白弹窗中选择类别、填写问题描述，再明确提交；不再自动从原投诉推断。取消不写库、两个按钮相互独立，成功后另起气泡显示单号。接口增加必填`ticket_type`、`description`，保留原两个回复定位字段及幂等校验。聊天HTML禁止持久缓存，CSS/JS使用版本地址，避免旧页面继续执行原生黑色确认框。最新专项、完整回归及计时测试复验结果详见[验收记录](docs/validation/2026-10-13-workflow-agent-acceptance.md)。

第五步的完整原始需求、后续确认及页面纠偏见[第五步提示词](docs/prompts/step-05-workflow-agent.md)，根目录[prompt.md](prompt.md)提供各步入口；开发过程记录在[dev-notes/ch05.md](dev-notes/ch05.md)。

第五步已按用户要求合并到`master`并推送`origin/master`。主分支冒烟2项通过；完整回归与计时测试修正专项分别保留，详见验收记录末尾。演示所用独立工作树继续保留运行资源。

## 意图理解、选单与退款申请演示（2026-10-15）

本次功能演示地址为 [http://127.0.0.1:8003/](http://127.0.0.1:8003/)，单 worker，检查点独立于仍保留的8002。八意图先理解再分类；整句固定社交零模型，纯政策FAQ不选单、不扩写；具体退货/维修先确认演示订单再检索政策。订单业务时间固定2026-10-15且标注mock。退款表单只有明确提交才保存“待审核”申请，不执行支付、不修改订单或人工状态。维修不转为退款。

先核对当前 `.env` 的数据库目标（不打印密码），再显式准备申请表；启动过程只校验，不自动迁移：

```powershell
uv run --locked python -c "from app.config import load_settings; s=load_settings(); print(s.mysql_host,s.mysql_port,s.mysql_database,s.mysql_user)"
uv run --locked python -m app.refunds.cli init
uv run --locked python -m app.refunds.cli verify
$env:WORKFLOW_CHECKPOINT_PATH = 'runtime/workflow/intent-routing-8003.sqlite'
uv run --locked uvicorn app.main:create_app --factory --host 127.0.0.1 --port 8003 --workers 1
```

订单卡片只在服务正式暂停后可点选，刷新会重新核验当前待选状态；新消息使旧卡失效。退款入口来自原始完成根的服务许可，表单六类原因必选、金额只读。取消/Esc不提交，成功另起服务通知气泡。相同申请重试幂等，不同会话针对已有同单待审申请返回409；不删除已有申请来制造新建成功。演示身份校验不等于生产鉴权。

评估缺省全部未执行且零上游调用；真实执行必须遵守已批准的固定范围和gate，不循环整批刷分：

```powershell
uv run --locked python -m evals.evaluate_intent_routing --mode understanding --split acceptance --output .cache/intent-routing/new-dry.json
# 经授权：acceptance固定16轮一次；协议/边界gate确认后development固定32轮一次。
uv run --locked python -m evals.evaluate_intent_routing --mode understanding --split acceptance --live --output .cache/intent-routing/new-acceptance.json
# 仅定点修复；--previous可重复传入已有有效观测报告，不重新调用前序。
uv run --locked python -m evals.evaluate_intent_routing --mode understanding --split acceptance --live --case-id dialogue-1-4 --previous .cache/intent-routing/acceptance-live.json --output .cache/intent-routing/new-point.json
# 真实浏览器固定八组；重启脚本只能操作自己启动的8003，不能停止8002。
node scripts/verify-intent-routing-browser.cjs --url http://127.0.0.1:8003/ --mode live --restart-script scripts/start-intent-routing-demo.ps1
# 导入浏览器已有SQL/SQLite证据；本命令不发送聊天、不重复申请。
uv run --locked python -m evals.evaluate_intent_routing --mode chat --split acceptance --live --evidence .cache/intent-routing-browser/live/<实际run-id>/results.json --output .cache/intent-routing/new-chat-evidence.json
```

报告拒绝覆盖已有输出，保留所有失败、Prompt/样例哈希、原输出、真实分母及实际/估算usage。失败依赖轮blocked，不用金标补上下文；跨Prompt修复带历史来源，不能混算为独立单Prompt48题通过。默认测试和受控浏览器不证明真实模型质量。当前已执行范围、真实失败及SQL/根状态证据见[本次验收记录](docs/validation/2026-10-15-intent-routing-acceptance.md)，开发记录见[dev-notes/ch06.md](dev-notes/ch06.md)。

本机锁定依赖已安装时，Windows受限环境实际验证等价使用 `.venv/Scripts/python.exe -m ...`，设置 `PYTHONUTF8=1`、`PYTHONPATH` 为本工作树完整路径；没有同步或更改依赖。真实存储专项为 `pytest tests/integration/test_refund_migration.py tests/integration/test_refund_requests.py tests/integration/test_workflow_actions.py --run-mysql -q`，只操作3308随机自有库，不清理应用业务行。


历史真实验收曾发现物流澄清最终流在校验前展示未验证历史事实；该Agent阻断项已在最终后端修复中关闭，后续唯一物流末轮定点通过。当前仍保留维修政策低于原校准门槛的答复缺口；不能把定点修复混算为独立48题或八组全通过。原始失败、真实SQL申请与最终审查/回归边界均在上述验收记录中。

最终审查修复后的8003辅助启动命令（PowerShell 7）：`pwsh -NoProfile -File scripts/start-intent-routing-demo.ps1`。辅助脚本先拒绝预占且没有匹配owner JSON的服务，核验工作树、解释器、启动父链及PID创建身份后才认领或停止；旧的仅PID文件不能授权自动重启，8002保持不动。澄清文字现在先验证再发送，完整物流/订单请求必须取得本轮对应读取；失败调用也记录实测或标明估算的用量。最终验收增量见上述验收文档，原失败记录保留。

后端修复版本e329dd0的验证：默认测试2149通过/143跳过；相关真实MySQL27通过。唯一复用cid58的物流末轮已通过，合并历史浏览器证据7/8，维修仍因原校准知识闸拒答而未完成，详见验收记录；这些结果不代表重新执行的独立8组或48题全通过。

后续I4评分器离线收口采用request-semantics-v3-whole-query：只对六条固定消解题完整匹配已明确支持的主语、动作和请求语法，未知措辞保守失败，不作为通用自然语言语义判官。七份原报告追加离线重算，原48仍43通过/3失败/2阻塞；原报告不覆盖、无新增模型或浏览器调用。新源码冻结后唯一默认全量2214通过/143跳过，详见验收记录；旧2149结果单独保留。

2026-10-16用户原句“我的订单1001到哪了”两次暴露首个Agent决策协议错误。增量bbedb0e把已有必需当前读取约束前置到原生tool_choice；相关352项回归通过，限定审查PASS。随后通过Computer Use在同一会话64实际提交原句一次，调用query_logistics1001并返回已签收与模拟说明，SQL269–272及原始完成根核对通过。该增量没有重跑完整套件，2214/143仍是此前版本结果；维修及48题质量缺口不变。辅助启动使用上述已验证PowerShell7命令，旧Windows PowerShell对这些UTF-8脚本有解析兼容问题。

2026-10-16后续用户再次报告“还是不行”：会话64的user280/283在query_logistics成功后第二Agent决策失败。精确工具后状态的单次旧协议诊断复现stop/0tools/82字符非JSON（1469实际tokens），说明bbedb0e只处理了首次读取，不能代表整个控制协议已恢复。当前修正把普通/售后内部响应控制纳入原生Function Calling，非首次必读阶段required单选，业务工具与控制严格分离；旧客户端只兼容合法JSON，非JSON继续拒绝。修后离线验证进行中，真实浏览器与限定复审待完成；原48、7/8、维修缺口及旧2214/352结果均保留，详见验收末尾。

本次离线最终结果：冻结后唯一完整默认套件2266通过/143跳过、377.34秒、exit0；242个源码/测试文件哈希一致。相关专项的旧提示词断言已只做测试修正，最后受影响文件13通过。内部原生控制修正尚待控制器独立审查和真实浏览器验证，不改写此前失败或质量缺口。

随后限定审查通过，但真实首条仍失败：同一会话64/user286的query_logistics成功后未获得合法结束控制，后两条已停止。实际供应商智谱官方仅支持tool_choice=auto；此前required/named前提不成立。现按官方JSON模式修正离线实现，不改模型或重试。一次精确输入诊断被自动审批在启动前拒绝，已请求具体发送授权；尚无本次修正的线上通过结论。失败截图、SQL286–288和未完成根均保留，退款1、工单10不变。

本次定点复验已完成：08f0889使用智谱官方auto+json_object，每个决策仍可继续读工具或严格结束控制，最终流保持正文。相关394项通过（36.57秒）、增量独立审查PASS；用户批准后的一次诊断与三条真实页面问句均通过，SQL289–300与各轮done精确检查点核对一致，8003 PID62496。物流由既有Workflow当前读取保护执行；不能据此宣称Agent自主调用或整章全部验收完成。前端修正Workflow物流误标“知识检索”，node --check及后两条真实页面确认。原失败不删除，模型/预算/零重试不变，未提交退款或工单。用户已持续授权少量页面GLM测试，上百次大批量调用另行确认；详见[验收记录](docs/validation/2026-10-15-intent-routing-acceptance.md)。

2026-10-16连续追问定点修复：当前84b3626在8003通过真实四轮“查1001物流→这个能退吗→那大概什么时候到→slkfnsiogn”，SQL364–379与精确完成根核对PASS。补齐已绑定订单的政策评分输入（含仅订单号的等价表达）、理解阶段旧FAQ挤掉订单历史、模拟说明遗漏和OTHER明确澄清；页面安全呈现加粗。退款needs_review，来源119原文、空白原因表单打开取消通过，未提交业务申请。相关129/218/107项分别通过，不相加当全量；原48题、7/8及维修缺口不变。失败358的问题池id13保留。少量页面GLM与既有BGE完整链路测试已持续授权，上百次评估另行确认。命令及失败/最终证据见[本轮验收](docs/validation/2026-10-15-intent-routing-acceptance.md)，过程见[第六步记录](dev-notes/ch06.md)。

第八步可插拔工具：见[手动验收步骤](docs/ch08-manual-acceptance.md)、[演示命令](docs/tool-system-demo.md)、[最新复验报告](docs/superpowers/reports/2026-10-19-pluggable-tools-reacceptance.md)和[开发过程](dev-notes/ch08.md)。2026-10-19截图主流程及两个组合失败原句已真实复验；8005客服、8101物流、8102售后分别运行，原8004保持。
