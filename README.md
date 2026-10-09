# 电商智能客服

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

浏览器打开 <http://127.0.0.1:8000/>。Enter 发送，Shift+Enter 换行，可停止生成。页面先创建会话后连续多轮聊天；新对话创建独立会话，暂不加载已有记录。保持单 worker，因为会话占用锁在单进程内；消息保存在 MySQL，可跨服务重启读取。

SSE 的 `status` 包含工具与 `checking` 阶段，知识回答在第一段 `delta` 前发送 `citations`；`done` 带真实字符串 `conversation_id` 和 `message_id`，必须在最终消息提交后才发送。来源编号限定本轮，跨轮 `[1]` 不混用；所有 ID 使用十进制字符串以保留超大整数。网络增量不保证一个增量恰好一个 tokenizer token。

证据按完整知识块裁剪，历史按完整轮次裁剪；最佳证据放首尾。自评 useful=false 的合法判定返回固定拒答，并与问题池同事务提交。认证、超时、结构化非法、预算或生成校验错误不冒充拒答入池。失败/取消的流水保留审计但不回放成完整历史；取消或错误回复不出现反馈按钮。

## curl 演示

PowerShell 用 UTF-8 无 BOM 文件传 JSON，避免转义损坏。库外问题可以使用“XM-Z99支持卫星通信吗？”；型号知识为合成测试参数，不能作为真实商品规格。

```powershell
$utf8 = [System.Text.UTF8Encoding]::new($false)
New-Item -ItemType Directory -Force .cache | Out-Null
[System.IO.File]::WriteAllText((Join-Path (Get-Location) '.cache/create.json'), '{"user_id":"demo-user"}', $utf8)
$created = curl.exe --max-time 75 -sS -H 'Content-Type: application/json' --data-binary '@.cache/create.json' http://127.0.0.1:8000/api/conversations | ConvertFrom-Json
$conversationId = $created.conversation_id
foreach ($question in @('邮费是多少', 'XM-A17参数是什么？', 'XM-Z99支持卫星通信吗？')) {
  $payload = @{conversation_id=$conversationId; message=$question} | ConvertTo-Json -Compress
  [System.IO.File]::WriteAllText((Join-Path (Get-Location) '.cache/chat.json'), $payload, $utf8)
  curl.exe -N --max-time 260 -H 'Content-Type: application/json' --data-binary '@.cache/chat.json' http://127.0.0.1:8000/api/chat
}
# 分类过滤由可信请求字段提供，不让模型生成过滤表达式。
$payload = @{conversation_id=$conversationId; message='普通小件配送费用是多少？'; category='合成型号与条件知识'} | ConvertTo-Json -Compress
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

## 回归与开发记录

```powershell
uv run --locked pytest -q
uv run --locked pytest -q --run-mysql --run-milvus -o faulthandler_timeout=30
git diff --check
```

当前代码显式启用 MySQL/Milvus 完整回归 **1205 passed、0 failed、0 skipped**；默认配置回归 **1096 passed、109 skipped**。最终后端修复均已通过定向复核。实际云端比较为 **101/120 项完成、19 项错误**，口语邮费问题仍有误拒答，详见[本轮结果](docs/validation/hybrid-retrieval-results.md)及[审查记录](docs/validation/hybrid-retrieval-review.md)。

默认回归跳过真实 MySQL/Milvus 集成；显式启用但服务未就绪会失败。受控模型与确定性向量测试证明协议/事务/错误边界，不证明上游事实质量。第四步过程记录在 [dev-notes/ch04.md](dev-notes/ch04.md)；历史文件名保留原提示词约定，README 和提交不使用章名标记开发阶段。

本轮开发使用 `feat/hybrid-retrieval`，真实验收使用自有测试资源；主库建库、业务数据校准、主 checkout 部署和调度器注册不由测试脚本自动执行。旧[第二步验证](docs/validation/tool-calling-results.md)与[第三步验证](docs/validation/ch03-results.md)保留，不能用旧数字代替当前结果。
