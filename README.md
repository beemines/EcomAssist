# 电商智能客服

第三章在 MySQL 持久会话与单轮工具调用上加入 Dense 知识库，沿用 FastAPI、LangChain 和 OpenAI 兼容 Chat Completions。每条用户消息一次工具选择、最多一个逻辑工具、一次最终流式回答，没有 Agent Loop。订单、商品和物流返回随机模拟数据；FAQ 使用云端 BGE-M3 与本机 Milvus 检索、MySQL 读取权威正文；人工工单真实写库并将会话转人工。原售后信息提取接口继续保留。

本章实际域内召回5/5、原问法应用SSE及持久回答、两个自建进程中断恢复已验证；域外误召回观察仍失败。当前 Prompt 实际九类评估9/9；最终总回归显式启用 MySQL/Milvus，729 passed、0 failed、0 skipped。六项任务审查及整分支修复复核通过。详见[第三章验证记录](docs/validation/ch03-results.md)、[代码审查](docs/validation/ch03-code-review.md)与[开发记录](dev-notes/ch03.md)；合并/推送待用户选择，主库建库和宿主定时任务尚未部署。第二章的历史工具验收及未完成项保留在[旧验证记录](docs/validation/tool-calling-results.md)，不能由本章单个邮费回答推断旧八类均已通过。原始业务建表为[sql/schema.sql](sql/schema.sql)，新增两表为用户原样[sql/ch03-ddl.sql](sql/ch03-ddl.sql)。

## 安装、数据库与启动

在项目根目录使用 Python 3.11–3.13；本次验证 Python 3.13.5、uv 0.11.7。

```powershell
$env:UV_CACHE_DIR = '.cache/uv'
uv sync --locked
if (-not (Test-Path -LiteralPath '.env')) { Copy-Item .env.example .env }
```

在 `.env` 填写 `LLM_API_KEY`、`SILICONFLOW_API_KEY`、`MYSQL_PASSWORD` 和 `MYSQL_ROOT_PASSWORD`。沿用 `glm-5.3-flash` 和标准端点 `https://open.bigmodel.cn/api/paas/v4/`。应用默认连接 `127.0.0.1:3307/customer_service`；独立测试库固定为 `127.0.0.1:3308/customer_service_test`。下面启动命令适用于已合并部署的 checkout；正式数据导入见第三章建库说明。

```powershell
docker compose -p ecs-tool-calling --profile test up -d --wait --wait-timeout 120
docker compose -p ecs-tool-calling --profile test ps
docker compose -f compose.milvus.yaml -p ecs-knowledge up -d
uv run --locked python -m app.knowledge.cli migrate
uv run --locked python -m app.knowledge.cli init-vectors
uv run --locked uvicorn app.main:create_app --factory --host 127.0.0.1 --port 8000 --workers 1
```

首次空卷启动由官方入口原样执行挂载的 `sql/schema.sql`，再执行 `sql/seed.sql`。客户端明确使用 utf8mb4；原业务四表为 faq/conversations/messages/tickets，本章 migrate 额外执行 knowledge_chunks/qa_extraction_staging 两表DDL。旧faq表保留但在线语义检索使用新知识表。种子使用 seed-user，包含完整对话、人工售后工单、退货与运费 FAQ；不占用浏览器 demo-user 的会话。种子采用存在性检查，不清空数据。

既有卷再次 up 不重跑初始化 SQL。维护时保留 `ecs-tool-calling_mysql-data-initialized` 与 `ecs-tool-calling_mysql-test-data-initialized` 卷。可只重启独立测试库：

```powershell
docker compose -p ecs-tool-calling --profile test restart mysql-test
docker compose -p ecs-tool-calling --profile test ps
```

应用不执行 ORM 建表、create_all/drop_all。初始化 SQL 或数据库密码改动不会自动修改已有卷内数据库，需按实际库状态明确维护，不能用删除卷代替迁移。

保持单 worker：历史保存在 MySQL，可跨应用重启读取；同会话占用锁仍在单进程内。模型生成和 SSE 等待期间不持有事务。`GET /health` 的 `{"status":"ok"}` 仅表示服务存活。

## 页面与 API

打开 <http://127.0.0.1:8000/>。页面先 POST `/api/conversations`，获得数据库分配的正整数十进制字符串 ID，再以 `conversation_id` 连续聊天；徽章显示工具阶段。Enter 发送，Shift + Enter 换行，生成中可停止；失败/取消提示本轮未完整完成。新对话创建独立会话，页面不加载已有数据库记录。

ID 全程保持字符串，包括 JavaScript 安全整数范围以外的值。拒绝 UUID、数字 JSON、布尔、浮点、空串、前导零及超出 unsigned BIGINT 的值。消息最多 20000 字符。同会话并发返回 409 session_busy，不存在返回 404，已结束返回 409；已转人工的会话仍可聊天。

SSE status 的 phase 为 selecting/tool_running/tool_completed/answering，工具阶段含名称及调用 ID；delta 为回复增量。成功最后恰好一个 done，携带同一字符串 conversation_id；失败为 error 后关闭。网络块不等同于 tokenizer token。

最终回复必须非空、流正常结束、明确 finish_reason=stop，并在数据库提交成功后才发送 done。截断、错误、取消、不完整轮次保留审计流水，但不回放给下一轮模型。提交后发送失败时数据库可能已有完整回答，不能据此证明客户端收到 done。

## curl 演示

PowerShell 使用 UTF-8 无 BOM 文件避免引号损坏。先创建会话，再发三个原问题；聊天最长等待 150 秒，提取 75 秒。下面是演示命令，不是当前真实验收已通过的声明。

```powershell
$utf8 = [System.Text.UTF8Encoding]::new($false)
New-Item -ItemType Directory -Force .cache | Out-Null
[System.IO.File]::WriteAllText((Join-Path (Get-Location) '.cache/create.json'), '{"user_id":"demo-user"}', $utf8)
$created = curl.exe --max-time 75 -sS -H 'Content-Type: application/json' --data-binary '@.cache/create.json' http://127.0.0.1:8000/api/conversations | ConvertFrom-Json
$conversationId = $created.conversation_id
$questions = @('订单 1001 的物流到哪了', '退货政策是什么', '邮费是多少')
foreach ($question in $questions) {
  $payload = @{conversation_id=$conversationId; message=$question} | ConvertTo-Json -Compress
  [System.IO.File]::WriteAllText((Join-Path (Get-Location) '.cache/chat.json'), $payload, $utf8)
  curl.exe -N --max-time 150 -H 'Content-Type: application/json' --data-binary '@.cache/chat.json' http://127.0.0.1:8000/api/chat
}
$ticket = @{conversation_id=$conversationId; message='请转人工处理我的问题'} | ConvertTo-Json -Compress
[System.IO.File]::WriteAllText((Join-Path (Get-Location) '.cache/ticket.json'), $ticket, $utf8)
curl.exe -N --max-time 150 -H 'Content-Type: application/json' --data-binary '@.cache/ticket.json' http://127.0.0.1:8000/api/chat
[System.IO.File]::WriteAllText((Join-Path (Get-Location) '.cache/extract.json'), '{"text":"订单 20261005001 的杯子收到就碎了，我想退货退款。"}', $utf8)
curl.exe --max-time 75 -H 'Content-Type: application/json' --data-binary '@.cache/extract.json' http://127.0.0.1:8000/api/extract
```

提取预期为 `{"order_id":"20261005001","request_type":"return_refund","expected_solution":"退货退款"}`。保留 conversationId 后可在应用重启后用同一 ID 追问前轮内容。

FAQ 参数仍必须是当前问题的连续原文片段（1–128 字符）。该原文直接交给云端 BGE-M3，Milvus Dense 检索最多三条，随后仅从 MySQL 的 done 行取权威正文；不做查询改写、LIKE 回退、混合检索或重排。导入并向量化演示文档后，“邮费是多少”应命中标准配送费用，不需要换成“运费”。无相似度阈值的 Top3 会返回域外不相关知识，found=true 只表示有已完成的检索结果；不能据此证明问题属于知识范围。订单/商品/物流是模拟演示，不能声称真实订单状态或已执行退款。工单编号由会话、当前 user 消息主键和调用 ID 的 SHA256 生成，同次重试复用，不同用户消息独立编号。

## 配置和预算

| 配置 | 当前/默认值 | 用途 |
| --- | --- | --- |
| LLM_MODEL | glm-5.3-flash | 既定上游模型 |
| LLM_BASE_URL | GLM 标准端点 | Chat Completions |
| LLM_TOKEN_LIMIT_FIELD | max_tokens | 既有输出字段 |
| MAX_OUTPUT_TOKENS | 512 | 既有输出上限 |
| LLM_TIMEOUT_SECONDS | 60 | 单次上游请求期限 |
| TOOL_INPUT_TOKEN_BUDGET | 8000 | 聊天 system/历史/工具定义/申请/结果的估算预算 |
| INPUT_TOKEN_BUDGET | 2000 | 原售后提取估算预算 |
| TOOL_TIMEOUT_SECONDS | 5 | 单次工具执行期限 |
| TOOL_MAX_RETRIES | 1 | 仅超时/暂时连接错误允许一次工具重试 |
| SILICONFLOW_API_KEY | 后端密钥 | 云端 BGE-M3 embeddings |
| EMBEDDING_MODEL | BAAI/bge-m3 | 1024 维 Dense 向量 |
| EMBEDDING_TIMEOUT_SECONDS | 20 | 单次嵌入请求期限；在线仍受工具总期限约束 |
| MILVUS_URI | http://127.0.0.1:19530 | 本机 Milvus |
| MILVUS_TIMEOUT_SECONDS | 5 | Milvus 请求期限 |
| QA_MAX_OUTPUT_TOKENS | 2048 | 仅离线历史 QA 抽取，在线聊天/售后仍为 512 |

保留完整历史轮次和当前工具申请/结果组合。必需输入超预算返回 422 input_too_long；取消后不重试。模型 SDK 和评估 HTTP 客户端均无自动重试。密钥只在后端读取，不发送给浏览器或写入报告；改 .env 后重启服务。

## 评估与回归

先以当前配置执行一个物流能力闸门。兼容、认证、预算或协议失败时停止所有后续真实请求，保存脱敏证据并确认下一步，不自动改模型、协议或参数。八条 [样例](evals/tool_cases.jsonl) 属于 Prompt/数据评估；模型替身测试不能代表真实上游质量。

```powershell
uv run --locked python -m evals.evaluate_tools --base-url http://127.0.0.1:8000 --cases evals/tool_cases.jsonl --output .cache/tool-evaluation.json
uv run --locked python -m evals.smoke --base-url http://127.0.0.1:8000 --output .cache/tool-smoke.json --configured-upstream https://open.bigmodel.cn/api/paas/v4/ --configured-model glm-5.3-flash
```

评估通过应用 API 创建新会话、聊天，再从当前配置建立只读审计仓储读取流水，核对实际工具、参数、FAQ found/matches、稳定工单号及已提交回答。剩余未尝试样例明确标记 not_attempted。工具/参数差异可继续采样，流/接口失败停止剩余调用。完整正常流及审计匹配才能结构通过；answer_contains 只产生 answer_phrase_match 观察，回答质量始终 human_answer_review=pending，同义措辞不会直接判为工具失败。

smoke 正常有创建会话、两轮聊天、一次精确提取，共 4 次应用 HTTP；聊天 deadline150秒、提取75秒，失败后停止。正常聊天通常每轮一次选择、一次最终模型请求，提取一次；不能将理论次数冒充实测。普通 API 客户端无法观察后端上游调用，model_request_count 为 null；真实验收以原请求的脱敏上游观察记录计数，见验证记录。身份参数只声明公开配置，不能证明提供方身份。

```powershell
$env:UV_CACHE_DIR = '.cache/uv'
uv run --locked pytest -q
uv run --locked pytest tests/integration --run-mysql --run-milvus -q
git diff --check
```

未传 --run-mysql / --run-milvus 跳过对应集成；显式请求但服务未就绪会失败。离线测试使用受控模型、仓储、HTTP 分片，不调用真实上游。真实回答质量、实际检索和恢复证据见 [第三章验证记录](docs/validation/ch03-results.md)，不能由离线通过推断。

## 第三章建库与每日任务

以下正式建库命令需要在本章合并、部署到主 checkout 后运行。此次实测仅使用 `127.0.0.1:3308/customer_service_test` 的自建行和 `knowledge_test_<UUID>` 集合，结束即清理；未填充主库或正式 `knowledge` 集合，未部署主 checkout，未读取生产个人历史，未注册宿主机定时任务。原卷、四张业务表和原 UI 保留。

保留已初始化的 `ecs-tool-calling` 项目及其卷，额外迁移用户原样两表 DDL；迁移发现已有表结构不符即失败，不改列或删表。Milvus 使用独立 `ecs-knowledge` 项目及卷；不要执行 `down -v`。

```powershell
$projectRoot = 'D:\shixi\ecommerce-customer-service'
$env:UV_CACHE_DIR = 'D:\shixi\ecommerce-customer-service\.cache\uv'
docker compose -p ecs-tool-calling --profile test up -d
docker compose -f compose.milvus.yaml -p ecs-knowledge up -d
uv --directory $projectRoot run --locked python -m app.knowledge.cli migrate
uv --directory $projectRoot run --locked python -m app.knowledge.cli init-vectors
uv --directory $projectRoot run --locked python -m app.knowledge.cli import-document --path knowledge-docs/demo-policy.md --type policy
uv --directory $projectRoot run --locked python -m app.knowledge.cli import-document --path knowledge-docs/demo-faq.md --type faq
uv --directory $projectRoot run --locked python -m app.knowledge.cli import-document --path knowledge-docs/demo-manual.md --type manual
uv --directory $projectRoot run --locked python -m app.knowledge.cli vectorize-pending --batch-size 20
uv --directory $projectRoot run --locked uvicorn app.main:create_app --factory --host 127.0.0.1 --port 8000 --workers 1
```

先在 `.env` 配置已有 MySQL 凭据、LLM 凭据及 `SILICONFLOW_API_KEY`，不要提交密钥。`init-vectors` 校验 INT64 id、1024 维、auto_id=False、Strong、FLAT/COSINE；不匹配即拒绝。导入会新增 pending 行，重复 import 不等于文档去重；续跑应只执行 vectorize-pending。MySQL id 为 Milvus 主键，同一行 upsert 可重放；中断后的 pending 在再次启动命令时补齐，不宣称服务启动会自动调度补齐。向量文本固定只含 category/questions/answer，其余章节、指针及关键条款元数据保存在 MySQL。

部署后历史处理命令如下；时间为北京时间半开区间，只采集已结束会话，按 id 分页，每批最多 20 条。全局精确去重规范化 NFKC 与空白，保留同问题不同答案；它不能去掉所有语义近似问题。暂存推广事务完成后再补向量。脚本内容是部署说明；运行这些历史命令会调用真实模型并处理配置库的数据，应由维护者选择已授权的时间窗口。

```powershell
uv --directory $projectRoot run --locked python -m app.knowledge.cli mine-conversations --start 2026-10-06T00:00:00 --end 2026-10-07T00:00:00 --batch-size 20
uv --directory $projectRoot run --locked python -m app.knowledge.cli deduplicate-staging
uv --directory $projectRoot run --locked python -m app.knowledge.cli vectorize-pending
uv --directory $projectRoot run --locked python -m app.knowledge.cli run-daily
```

run-daily 处理北京时间前一天，持同一 MySQL GET_LOCK 完成挖掘→暂存去重→pending 向量化；已有任务占锁时退出失败，取消/释放失败作废锁连接。已验证当前 MySQL SYSTEM/UTC 时钟转换；历史混合时区与 DST 迁移需另行核对。

仅在主 checkout 合并部署且宿主机时区为 `China Standard Time` 后，维护者可注册每日 02:00 的外部计划。`scripts/run-knowledge-daily.ps1` 固定主 checkout 路径，将实际 stdout/stderr 追加至已忽略的 `D:\shixi\ecommerce-customer-service\.cache\knowledge-daily.log`，同时保留控制台输出和 uv 退出码；本次没有执行注册命令，也没有常驻调度器。

挖掘失败时日志包含失败类型、batch_no、北京时间半开窗口及 conversation/message ID，不含消息正文或提供方错误详情。维护者可用这些 ID 定位源会话、检查超长输入或来源问题后，再使用上方 `mine-conversations --start ... --end ...` 手动重放该窗口；不会自动纠错或重试。日志在 Windows PowerShell 5.1 使用 UTF-16LE，pwsh 使用 UTF-8，维护者按本地保留要求清理 `.cache` 中的旧日志。

```powershell
schtasks /Create /TN "ECS Knowledge Daily" /SC DAILY /ST 02:00 /TR 'powershell.exe -NoProfile -ExecutionPolicy Bypass -File "D:\shixi\ecommerce-customer-service\scripts\run-knowledge-daily.ps1"' /F
```

原问法聊天沿用上面的 curl 演示：创建独立会话后发送 `邮费是多少`。演示政策明确为合成教学数据：大陆普通配送区域的普通小件配送 8 元，单笔商品实付满 99 元包邮；港澳台、偏远地区和大件另确认，不能推广到真实商家。

在尚未部署的 worktree 可独立复现本次验收。先明确向测试库执行相同迁移（临时设置 MYSQL_PORT=3308、MYSQL_DATABASE=customer_service_test 后 migrate，完成后恢复原环境值）；不要从初始化卷假定新 DDL 已执行。两个 harness 固定测试库、使用自建行与 UUID 集合、真实云端模型，结束清理自有资源。离线测试和普通 Milvus 集成的确定性替身向量不能证明云端语义质量。

```powershell
$worktreeRoot = 'D:\shixi\ecommerce-customer-service\.worktrees\ch03-dense-knowledge'
uv --directory $worktreeRoot run --locked python -m evals.evaluate_knowledge --output .cache/knowledge-live.json
uv --directory $worktreeRoot run --locked python -m evals.knowledge_recovery --output .cache/knowledge-recovery.json
uv --directory $worktreeRoot run --locked python -m evals.evaluate_qa --controlled --output .cache/qa-controlled.json
# 当前九类包括两种同答案真实问法，均须保留原问题及配对来源。
# 旧 prompt 的 8/8 原证据保存在 docs/validation/ch03-qa-live.json，当前九类另存。
uv --directory $worktreeRoot run --locked python -m evals.evaluate_qa --output .cache/qa-live.json
```

knowledge 评估先验证实际 1024 维/集合 schema，再导入三份合成文档及 scoped pending 向量化；六条标注分别记录预期章节、实际主键/工具结果及耗时。域外观测标注 required=false，误召回仍保留 passed=false，退出码只代表五条必需域内及应用结构验收；事实质量必须另读原回答核对。实际应用使用 lifespan 和缓冲 HTTPX ASGITransport 验证 SSE 事件及持久消息，因此不声称网络逐帧延时/真实浏览器验收。恢复 harness 真正创建并终止它的 worker OS 进程，两个边界均记录匹配 PID、pending/done、唯一向量数及正文哈希。
