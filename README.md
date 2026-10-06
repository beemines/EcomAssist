# 电商智能客服

第二步加入 MySQL 持久会话与单轮工具调用，沿用 FastAPI、LangChain 和 OpenAI 兼容 Chat Completions。每条用户消息一次工具选择、最多一个逻辑工具、一次最终流式回答，没有 Agent Loop。订单、商品和物流返回随机模拟数据；FAQ 读取 MySQL 问题列；人工工单真实写库并将会话转人工。原售后信息提取接口继续保留。

离线测试、真实 MySQL 集成和保留数据的重启检查已通过。真实物流闸门通过，八类评估在人工工单项发生错误后停止，剩余真实验收待完成，见 [验证记录](docs/validation/tool-calling-results.md)。开发过程见 [dev-notes/ch02.md](dev-notes/ch02.md)，原始建表文件为 [sql/schema.sql](sql/schema.sql)。

## 安装、数据库与启动

在项目根目录使用 Python 3.11–3.13；本次验证 Python 3.13.5、uv 0.11.7。

```powershell
$env:UV_CACHE_DIR = '.cache/uv'
uv sync --locked
if (-not (Test-Path -LiteralPath '.env')) { Copy-Item .env.example .env }
```

在 `.env` 填写 `LLM_API_KEY`、`MYSQL_PASSWORD` 和 `MYSQL_ROOT_PASSWORD`。沿用 `glm-5.3-flash` 和标准端点 `https://open.bigmodel.cn/api/paas/v4/`。应用默认连接 `127.0.0.1:3307/customer_service`；独立测试库固定为 `127.0.0.1:3308/customer_service_test`。

```powershell
docker compose -p ecs-tool-calling --profile test up -d --wait --wait-timeout 120
docker compose -p ecs-tool-calling --profile test ps
uv run --locked uvicorn app.main:create_app --factory --host 127.0.0.1 --port 8000 --workers 1
```

首次空卷启动由官方入口原样执行挂载的 `sql/schema.sql`，再执行 `sql/seed.sql`。客户端明确使用 utf8mb4；仅有 faq/conversations/messages/tickets 四表。种子使用 seed-user，包含完整对话、人工售后工单、退货与运费 FAQ；不占用浏览器 demo-user 的会话。种子采用存在性检查，不清空数据。

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

FAQ 关键词必须是当前问题的连续原文片段，只查问题列，最多三条，不扩展同义词。“邮费是多少”查不到是预期结果；不能换成“运费”掩盖漏召回。订单/商品/物流是模拟演示，不能声称真实订单状态或已执行退款。工单编号由会话、当前 user 消息主键和调用 ID 的 SHA256 生成，同次重试复用，不同用户消息独立编号。

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
uv run --locked pytest tests/integration --run-mysql -q
git diff --check
```

未传 --run-mysql 跳过独立集成；显式请求但测试库未就绪会失败。离线测试使用受控模型、仓储、HTTP 分片，不调用真实上游。真实浏览器/curl、客服回答质量、真实工单和提取能力须按验证记录核对，不能由离线通过推断。
