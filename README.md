# 第一章：纯聊天与售后提取

Python + FastAPI + LangChain 的单进程后端。聊天通过 SSE 返回文本增量，提取通过 OpenAI 兼容 Chat Completions 的 JSON 模式返回三个字段。当前没有聊天页面、数据库、检索、业务工具或 Agent 循环。

当前交付状态：**OFFLINE_READY / REAL_ACCEPTANCE_PENDING**。密钥尚待用户填写，真实 GLM JSON 兼容性、聊天角色表现与标注准确率尚未实测。离线测试通过不表示整章真实验收通过，详见 [验收记录](docs/validation/ch01-results.md)。

## 安装与启动

在本项目根目录使用 Python 3.11–3.13（开发验证使用 Python 3.13.5、uv 0.11.7）：

```powershell
$env:UV_CACHE_DIR = '.cache/uv'
uv sync --locked
Copy-Item .env.example .env
```

在本项目 `.env` 中填写 `LLM_API_KEY`。首个真实验收模型为 `glm-5.3-flash`，标准端点为 `https://open.bigmodel.cn/api/paas/v4/`，不是 Coding 端点；然后启动：

```powershell
uv run --locked uvicorn app.main:create_app --factory --host 127.0.0.1 --port 8000
```

保持一个 worker：会话历史及占用锁在进程内，重启丢失，多 worker 无法保证同会话连续性。`GET /health` 返回 `{"status":"ok"}` 仅证明应用存活，不调用模型，也不证明模型连通或 JSON 模式兼容。

## 配置与边界

| 配置 | 默认/示例 | 用途 |
| --- | --- | --- |
| `LLM_BASE_URL` | GLM 标准端点 | 直接连接 OpenAI 兼容上游 |
| `LLM_MODEL` | `glm-5.3-flash` | 上游实际可用模型 ID |
| `LLM_API_KEY` | 用户填写 | 不得提交或写入验收报告 |
| `LLM_TOKEN_LIMIT_FIELD` | `max_tokens` | 可设 `max_completion_tokens` |
| `INPUT_TOKEN_BUDGET` | `2000` | 输入估算 token 预算，并非模型 tokenizer 精确计数 |
| `MAX_OUTPUT_TOKENS` | `512` | 独立的模型输出上限 |
| `LLM_TIMEOUT_SECONDS` | `60.0` | 上游请求超时 |

所有预算和超时须为正值。保留完整 user/assistant 轮次；system 和当前输入不裁断，必留输入超预算返回 422 `input_too_long`。已知截断、断开、失败及空回答不提交半轮历史；同会话同时请求返回 409 `session_busy`。应用不查询订单或执行退款，只给建议，不公开推理内容。GLM 的 JSON 模式与 512 上限是否足够等待实测；文档存在 `response_format` 差异，不能静默改变格式、模型或默认预算。

`.env.example` 包含 GPT、Claude、DeepSeek、Ollama 的端点示例。调用统一使用 OpenAI 兼容 Chat Completions、LangChain `PromptTemplate` 及 `with_structured_output(method="json_mode")`。Claude 官方兼容层忽略 `response_format`，JSON 依赖提示与应用校验，能力不等同原生 JSON 模式；切换端点不保证提取成功。配置声明也不是上游自行返回的身份证明。

## Windows curl 验收

在另一个 PowerShell 终端进入本项目根目录。用 UTF-8 无 BOM 文件传送 JSON，避免 shell 内引号损坏：

```powershell
$utf8 = [System.Text.UTF8Encoding]::new($false)
$session = 'manual-' + [guid]::NewGuid().ToString('N')
$first = @{session_id=$session; message='我的订单号是 20261005001，杯子收到就碎了，请给我售后建议。'} | ConvertTo-Json -Compress
[System.IO.File]::WriteAllText((Join-Path (Get-Location) 'chat-first.json'), $first, $utf8)
curl.exe -N --max-time 75 -H "Content-Type: application/json" --data-binary "@chat-first.json" http://127.0.0.1:8000/api/chat

$second = @{session_id=$session; message='我刚才提供的订单号是什么？请复述并说明下一步。'} | ConvertTo-Json -Compress
[System.IO.File]::WriteAllText((Join-Path (Get-Location) 'chat-second.json'), $second, $utf8)
curl.exe -N --max-time 75 -H "Content-Type: application/json" --data-binary "@chat-second.json" http://127.0.0.1:8000/api/chat

$extract = @{text='订单 20261005001 的杯子收到就碎了，我想退货退款。'} | ConvertTo-Json -Compress
[System.IO.File]::WriteAllText((Join-Path (Get-Location) 'extract.json'), $extract, $utf8)
curl.exe --max-time 75 -H "Content-Type: application/json" --data-binary "@extract.json" http://127.0.0.1:8000/api/extract
```

未填写有效配置时，以上真实输出待验收。成功流须有多个 `event: delta` / `data: {"delta":"..."}`，最后恰好一次 `event: done` / `data: {"session_id":"..."}`。失败为 `event: error` 后关闭；不能把一个网络块当作一个 tokenizer token。第二轮应复述第一轮订单。提取预期精确为：

```json
{"order_id":"20261005001","request_type":"return_refund","expected_solution":"退货退款"}
```

一般 Unix shell 的等价示例（两轮使用同一个新 session ID）：

```sh
session="manual-$(date +%s)-$$"
curl -N --max-time 75 -H 'Content-Type: application/json' --data-binary "{\"session_id\":\"$session\",\"message\":\"我的订单号是 20261005001，杯子收到就碎了，请给我售后建议。\"}" http://127.0.0.1:8000/api/chat
curl -N --max-time 75 -H 'Content-Type: application/json' --data-binary "{\"session_id\":\"$session\",\"message\":\"我刚才提供的订单号是什么？请复述并说明下一步。\"}" http://127.0.0.1:8000/api/chat
curl --max-time 75 -H 'Content-Type: application/json' --data-binary '{"text":"订单 20261005001 的杯子收到就碎了，我想退货退款。"}' http://127.0.0.1:8000/api/extract
```

## 标注评测与 smoke

待密钥填写并启动应用后执行，脚本调用本地应用接口，不直连模型。20 条数据的**第一条本身**检查 JSON 兼容性，结果计入该轮，不增加重复探测。客户端每个请求有 75 秒墙钟 deadline；应用和脚本均无自动模型重试。使用独立报告名保留每轮失败：

```powershell
uv run --locked python -m evals.evaluate --base-url http://127.0.0.1:8000 --cases evals/ch01_cases.jsonl --output docs/validation/round-1-evaluation.json --configured-upstream https://open.bigmodel.cn/api/paas/v4/ --configured-model glm-5.3-flash
```

先检查退出码、`first_case_json_compatible` 和 `records[0]`。首条 HTTP、JSON/schema 或传输失败会停止后续评估请求：只尝试 1 次，剩余样例保留原文和 gold，以 `error_code: "not_attempted"`、null 状态/响应明确记录，仍计入全部样例分母。`request_count` / `attempted_count` 表示实际请求尝试数，`not_attempted_count` 表示未尝试数；首条有效 JSON 的标签差异不会触发此门槛，仍继续 Prompt 效果评测。首条兼容检查失败时先诊断，不运行下面的 smoke。不能仅由安全的 `upstream_error` 推断上游拒绝 `response_format`，需确认实证。固定技术选型不兼容时请用户决定，不能自动换协议或模型。有任意失败/未尝试/标签不一致返回退出码 1，这用于提醒检查，不代表新增一个准确率验收阈值。

```powershell
uv run --locked python -m evals.smoke --base-url http://127.0.0.1:8000 --output docs/validation/round-1-smoke.json --configured-upstream https://open.bigmodel.cn/api/paas/v4/ --configured-model glm-5.3-flash
```

smoke 共三次请求：同一新会话的两轮聊天、一次精确提取。每轮至少两个非空增量、最后一次 done、无 error；第二轮包含前轮订单号。报告保存增量、首增量耗时、终止事件和提取结果。`human_role_review` 始终是 `pending`，须人工检查客服角色、政策/订单状态/已执行操作是否编造。报告中的上游/模型只来自显式 CLI 配置声明，缺省为 unknown，包含本地库版本，不存密钥、不自动读取 `.env`，不宣称提供方身份已验证。`--base-url` 是运行中的应用地址，不能传模型端点；身份参数只填公开端点和模型名。

首条兼容检查成功时，默认完整一轮为 **20 次提取 + 3 次 smoke = 23 次上游调用**；首条失败时只尝试 1 次评估请求，剩余 19 条未尝试，先诊断且不运行 smoke。请求尝试次数不证明上游实际收到多少次，HTTP/传输失败应按报告记录实际证据。上面的三个手动 curl 会另增加 3 次，勿计入自动轮次。真实失败或角色违规时先诊断，必要时改 Prompt 并定向复测失败样例，再完整评估+smoke（首条成功时再 23 次），记录返工和实际次数；完整复测仍失败则报告问题，不无限重试。512 截断时记录实证并请用户决定 `.env` 输出预算。

指标分母始终包含失败：三字段准确率分别计数；有效率要求 HTTP 200、无错误、完整三键 schema；missing 指标以 gold 的订单 null、方案 null、类型 unknown 的**字段位置**计数；source 指标以样例计数，要求有效输出和所有非 null 订单/方案为原文片段。分母为零时率为 null，无自行设定的准确率阈值。

## 离线验证

```powershell
$env:UV_CACHE_DIR = '.cache/uv'
uv run --locked pytest -q
git diff --check
```

测试使用模型替身和可控 HTTP/分片流，不读取真实 `.env` 或请求真实上游。网络替身验证脚本能识别异常，不证明真实模型质量。真实验收仍待用户填写凭据后运行并人工复核。
