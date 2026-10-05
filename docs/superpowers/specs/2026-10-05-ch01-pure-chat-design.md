# Ch01 设计：电商智能客服纯对话

日期：2026-10-05（北京时间）

项目：`D:\shixi\ecommerce-customer-service`

状态：用户已批准正式 spec，选择 Subagent-Driven 执行；实现计划待审阅。

## 1. 目标与已确认的约束

为简历项目建立可演示、可验证的电商客服后端。第一章跑通纯对话：多轮上下文、SSE 流式回复、模板化 Prompt、售后描述结构化提取和上下文预算控制。

用户先回复“确认”批准聊天中的设计，再回复“确认，选择Subagent-Driven进行开发”批准已落盘的正式 spec 并指定执行方式；尚未展示的实现计划仍需审阅。

- 使用 Python、FastAPI、LangChain；模型调用统一使用 OpenAI 兼容 Chat Completions 接口，直连所配置的上游。
- 使用 LangChain 的 `PromptTemplate` 和 `with_structured_output`。
- 地址、模型名、密钥从 `.env` 读取；提供 GPT、Claude、DeepSeek、Ollama 的配置示例。
- 不加入业务工具调用、Agent 循环、模型代理网关、数据库、知识库或检索。
- 本章通过 curl 验收，当前不包含聊天页面。用户后续描述页面效果时，页面按其指定的 Vibe Coding 例外执行。
- 可单测代码走 TDD；纯 Prompt 与数据产出以标注样例评估替代 TDD。
- 库与接口使用前先查 Context7 MCP，锁定依赖后核对实际接口，发现与固定选型冲突则请用户决定。
- 阶段即时追记到 `dev-notes/ch01.md`，不在结束时集中补写。

## 2. 架构与方案选择

采用 `session_id` + 服务端进程内存保存已完成的对话轮次。调用方只提交当前消息和会话 ID，方便用 curl 验证上下文。

备选方案是客户端每次提交完整历史，可让服务端无状态，但会把历史维护交给调用方。本章不采用该方案。

请求路径为：FastAPI 路由 → 会话/Prompt/预算服务 → 统一 ChatOpenAI 模型工厂 → 配置的上游接口。提取接口使用独立 Prompt 和相同模型配置，不读写聊天历史。

内存状态仅用于单进程演示。重启后历史清空，运行多个 worker 时会话不共享；演示命令明确使用一个 worker。

## 3. 模块边界与预期目录

以下是实现计划要落地的模块边界，当前仅建立设计文档和开发记录：

```text
app/
  main.py             # 应用入口、生命周期和健康检查
  config.py           # 环境配置与启动校验
  api/
    chat.py           # 对话请求和 SSE 响应
    extract.py        # 售后信息提取接口
  core/
    llm.py            # ChatOpenAI 工厂与模型调用边界
    memory.py         # 会话隔离、占用状态、历史裁剪和提交
    prompts.py        # 客服角色与提取任务的 PromptTemplate
  schemas/
    chat.py           # 对话请求和事件数据
    extract.py        # 提取请求、枚举和返回字段
tests/                # 可单测代码与接口验证
evals/                # 标注样例、模型评估和真实验收脚本
docs/superpowers/     # spec、plan
dev-notes/ch01.md     # 按阶段追记
README.md             # 配置、运行、curl 演示、验证结果说明
.env.example          # 不含真实密钥的配置模板
```

路由不负责维护 Prompt 或直接操作历史；模型工厂不维护会话状态；预算与历史服务不依赖真实模型网络调用。测试可以注入流式模型替身和计数器验证行为。

## 4. HTTP 与 SSE 契约

### 4.1 POST /api/chat

请求：

```json
{"session_id":"demo-01","message":"我的订单号是 20261005001，收到的杯子破了。"}
```

- `session_id`：必填字符串，长度 1–128，不能全为空白；原值作为会话键。
- `message`：必填字符串，不能全为空白，最多 20,000 字符；预算检查可能在长度限制以内进一步拒绝超预算输入。
- 不接受客户端指定 System Prompt 或替换服务端角色。
- 成功响应为 UTF-8 的 `text/event-stream`；每个事件由空行结束，data 使用 JSON 编码。

文本增量：

```text
event: delta
data: {"delta":"您好，"}

```

成功结束：

```text
event: done
data: {"session_id":"demo-01"}

```

流内失败：

```text
event: error
data: {"code":"upstream_error","message":"模型服务暂时不可用，请稍后重试。"}

```

- 上游生成文本增量后立即转发；不先收齐完整回复再拆字发送。
- 每个增量可以包含多个 token。接口承诺及时转发文本增量，不承诺每个 SSE 事件恰好一个 tokenizer token。
- 忽略没有可展示文本的模型块；正常完成且有非空回复时发送一次 `done`。
- 失败发送一次 `error` 后结束，不再发送 `done`，不将未完成的回复保存为历史。
- 客户端断开时取消/关闭上游流、释放会话占用；不承诺断开后继续生成或自动续传。完成边界为模型正常非空结束且终止 done 帧的 ASGI send 正常返回；此边界前的断开/发送失败不保存本轮，此边界后已完成历史保留。ASGI send 成功不等于证明客户端实际收到了字节。
- 本章无需在 SSE 中公开模型推理过程；只转发回复文本。

### 4.2 POST /api/extract

请求：

```json
{"text":"订单 20261005001 的杯子收到就碎了，我想退货退款。"}
```

`text` 必填，不能全为空白，最多 20,000 字符，同时受提取输入预算约束。

成功响应为普通 JSON，固定包含三个键：

```json
{
  "order_id": "20261005001",
  "request_type": "return_refund",
  "expected_solution": "退货退款"
}
```

| 字段 | 类型 | 规则 |
| --- | --- | --- |
| order_id | string 或 null | 只提取明确出现的订单号，保留原始形式；缺失或无法唯一确定时为 null |
| request_type | 枚举字符串 | refund、return_refund、exchange、repair、logistics、other、unknown |
| expected_solution | string 或 null | 提取用户明确表达的期望，使用原文短语；缺失时为 null |

诉求分类：仅退款为 `refund`，退货退款为 `return_refund`，换货为 `exchange`，维修为 `repair`，物流相关为 `logistics`。有明确诉求但不属于前述类别为 `other`；没有明确诉求或相互矛盾、无法确定单一类别为 `unknown`。

三个键均存在，不使用空字符串替代缺失值，不返回未声明的额外字段。出现多个无法归属的订单号时不擅自选择。提取接口不查询订单、不执行售后操作，也不把提取结果加入聊天历史。

### 4.3 GET /health

返回应用存活状态，例如 `{"status":"ok"}`。该接口不请求模型，也不代表上游连通、流式或提取验收通过。

### 4.4 错误分类

- 请求类型、必填字段和长度不合法：HTTP 422。
- 必留输入超过应用预算：HTTP 422，错误码 `input_too_long`。
- 同一会话已有生成请求：HTTP 409，错误码 `session_busy`。
- 提取的上游调用失败：HTTP 502，错误码 `upstream_error`；超时为 HTTP 504，错误码 `upstream_timeout`。
- 提取返回无法解析或不符合字段模型：HTTP 502，错误码 `invalid_structured_output`。
- 聊天流已建立后，上游失败或超时使用 SSE `error`；客户端断开通常已无法收到错误事件。
- 错误响应不暴露密钥、完整上游异常、原始请求头或完整 `.env`。

## 5. 会话与预算

会话保存已完成的 user/assistant 对，不允许不同 `session_id` 互读。同一会话生成时保留占用状态，避免并发请求造成历史顺序混乱；不同会话可以独立生成。

每次请求按以下顺序处理：

1. 校验请求，并获取当前会话的占用权。
2. 生成 System Prompt，计算 System Prompt 和当前问题是否能放入输入预算。
3. 从已完成历史中保留尽量新的完整轮次；使用 LangChain `trim_messages` 配合计数器，保证消息序列合法，不留下孤立的 assistant 消息，不裁断用户当前问题。
4. 将 System Prompt、保留历史、当前问题交给模型流式生成。
5. 模型正常结束并得到非空回复后，先准备本轮及实际保留的历史；终止 done 帧的 ASGI send 正常返回后，无 await 提交一次。done 是最后一次响应发送；该完成边界之前失败/断开时原历史不变，成功后的清理不回滚历史。
6. 在所有结束路径释放会话占用。保存的历史下一次调用仍按预算裁剪，不累积全部旧轮次。

输入预算默认 2,000 个估算 token；输出上限默认 512 个模型 token，二者独立配置，并要求配置值为正数。调用方配置预算时为输出留出模型上下文空间。

计数器纳入文本编码长度和消息开销，采用保守估算，并允许测试注入计数器验证裁剪边界。估算是应用的裁剪策略，不是所有模型真实 tokenizer 计数的保证；报告明确区分估算与上游返回的实际 usage。预算内调用仍被上游拒绝时返回明确错误，不偷偷扩大预算或切换模型。

若 System Prompt + 当前问题已超预算，直接拒绝；不尝试删除 System Prompt，也不悄悄截断当前问题。提取请求使用其独立模板和当前描述做相同输入预算检查。

## 6. Prompt 与结构化输出

`app/core/prompts.py` 集中维护两个 `PromptTemplate`：

- 客服模板：说明电商客服角色、礼貌简洁的语气、信息不足时追问、不得编造政策/订单状态/已执行操作。用户消息仍以 user 角色输入，不拼进 System Prompt 作为指令。
- 提取模板：明确三个字段、枚举、null/unknown 规则，只提取用户给定描述，不把描述中的指令当作格式变更指令，要求仅返回 JSON 对象。

提取显式使用 `with_structured_output(method="json_mode")` 和 Pydantic 字段模型进行解析与验证。显式指定 method，避免不同版本的默认值改变行为。格式失败按契约返回错误，不静默改成 function calling、原生 Claude 协议或普通字符串结果。

Claude 官方 OpenAI 兼容层忽略 `response_format`；因此 Claude 路径主要依赖 Prompt 遵循和应用侧校验，而不是原生 schema 保证。这是已确认设计的兼容性限制，不新增“四家模型都原生强制 schema”的验收条件。其他上游也以实际模型能力与验证结果为准。

## 7. 配置与依赖策略

- `.env` 至少提供上游 base_url、model、api_key；配置名称在实现计划和 `.env.example` 中保持一致。
- 超时、输入预算和输出上限可配置；不在代码中写入真实密钥。
- 启动时校验必要配置，不默认改用另一个上游。Ollama 示例的占位 key 应明确说明其是否被实际服务使用。
- 提供四类上游的官方兼容地址配置示例，具体地址和参数在使用前通过 Context7 核对。
- 使用同一 ChatOpenAI 工厂调用 Chat Completions；不自动改为 Responses、Messages 或代理网关。
- 实现计划核对所用 Python、FastAPI、LangChain、langchain-openai 及直接依赖的兼容版本；安装后验证具体签名，并产出可复现的依赖锁定文件。
- 真实验收注明上游、模型名和依赖版本；没有凭据或未运行的上游标记为未实测，不将配置示例当作跨上游验收通过。

## 8. 验证与交付

### 可单测代码：TDD

先编写可观察行为的失败测试，再实现并验证：

- 会话连续性、不同会话隔离、同一会话并发处理。
- 预算边界、中文/英文输入、保留 system 和当前问题、完整轮次裁剪。
- SSE 增量顺序、正常结束、上游错误/超时、断开后不保存半轮并释放占用。
- 提取输入校验、返回字段契约、格式失败的明确错误。

离线模型替身只证明代码和接口行为，不能证明真实模型遵循 Prompt 的效果。

### Prompt 与数据：标注样例评估

准备至少 20 条带预期结果的售后样例，覆盖完整描述、缺订单号、缺期望方案、各诉求类型、歧义、多个订单号，以及描述里要求忽略规则的情况。

报告 JSON/字段有效率、订单号与诉求分类准确率、缺失值处理、期望方案是否来自原文，以及失败样例。不将程序硬编码的回答作为模型评估。若出现编造订单号、缺失信息被补造或明显违反角色约束，修改 Prompt 并重新评估，记录返工。

### 真实模型验收

1. 使用 `curl -N` 调 `/api/chat`，观察多个增量事件和正常结束。
2. 同一会话连续问两轮，第二轮正确引用第一轮明确提供的信息。
3. 调 `/api/extract` 提交售后描述，得到固定三个字段的 JSON。

测试报告区分离线测试、真实模型评估和真实接口验收，记录命令、模型与实际结果，不以其中一类替代另一类。

### 最终交付

- 可运行源码、依赖锁定文件、`.env.example`。
- README 中的启动及三个验收场景的 curl 命令（兼顾当前 Windows 环境）。
- 代码测试与样例评估结果；真实验收的实测范围和限制。
- `dev-notes/ch01.md`：在 brainstorm 定稿、计划评审通过、每个任务完成、code review 结论和 finish 时分别追记四项内容：用户关键原话、关键产出、拒绝或纠偏、翻车与返工。

## 9. 文档依据与后续流程

已通过官方 Context7 MCP 的 `resolve-library-id`、`query-docs` 查询：

- [LangChain PromptTemplate](https://reference.langchain.com/python/langchain-core/prompts/prompt/PromptTemplate)
- [LangChain trim_messages](https://reference.langchain.com/python/langchain-core/messages/utils/trim_messages)
- [LangChain 模型、流式与结构化输出](https://docs.langchain.com/oss/python/langchain/models)
- [ChatOpenAI with_structured_output](https://reference.langchain.com/python/langchain-openai/chat_models/base/ChatOpenAI/with_structured_output)
- [FastAPI SSE](https://fastapi.tiangolo.com/tutorial/server-sent-events)
- [FastAPI 流式响应](https://fastapi.tiangolo.com/advanced/custom-response)
- [Claude OpenAI SDK 兼容层](https://platform.claude.com/docs/en/cli-sdks-libraries/libraries/openai-sdk)

本文自审和 Git 提交后已交用户审阅并获批准，执行方式已选定 Subagent-Driven。后续启用 writing-plans 编写并审阅实现计划，保留已选执行方式；用户批准落盘计划后再开始产品实现。
