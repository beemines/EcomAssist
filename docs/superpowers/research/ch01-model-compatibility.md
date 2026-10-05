# Ch01 模型兼容性调研

日期：2026-10-05。仅查公开文档，未读取凭据、未发送模型请求、未安装依赖。本报告不是上游实测结果。

## Context7 查询过程与覆盖限制

使用官方 `https://mcp.context7.com/mcp` 的 `tools/list`，随后 `resolve-library-id` → `query-docs`。

- DeepSeek：`/websites/api-docs_deepseek`。
- Ollama：`/llmstxt/ollama_llms-full_txt`。
- LangChain：`/websites/reference_langchain`。
- 智谱：`/websites/bigmodel_cn_cn_guide`。

Context7 确认了主要兼容地址、流式、JSON 模式、ChatOpenAI 路由和 stream_usage 参数。其智谱摘录主要仍为 GLM-5.2，未确认用户指定的最新模型；ChatOpenAI 输出参数改写检索混入其他集成的 max_tokens 文档。对这些缺口已补查官方当前 `.md` 文档和官方源码，不把搜索未命中当成模型不存在。

## 首个真实验收上游：GLM

用户原话是 `glm5.3-flash`。官方 [模型页](https://docs.bigmodel.cn/cn/guide/models/vlm/glm-5.3-flash) 给出的 Model Code 是 `glm-5.3-flash`（另有不同模型 `glm-5.3-flashx`）。控制器已向用户说明官方拼写，后续配置采用该 ID；不再要求重新选择，也不静默换模型。

- 标准服务 `base_url=https://open.bigmodel.cn/api/paas/v4/`；调用 `chat/completions`。[官方 OpenAI SDK 迁移说明](https://docs.bigmodel.cn/cn/guide/develop/openai/introduction) 明列 `glm-5.3-flash` 示例。
- [Coding Plan FAQ](https://docs.bigmodel.cn/cn/coding-plan/faq) 给出套餐端点 `https://open.bigmodel.cn/api/coding/paas/v4/`，且明确套餐只用于指定工具与产品环境；自建应用、网站、机器人、SaaS 的 API 集成应使用标准 API。本项目客服后端应配置标准端点。
- 模型支持流式；`thinking.type` 仅支持 `enabled`，不能关闭思考。不要为实现纯聊天擅自切模型；SSE 仍仅转发可展示回答，不公开推理。
- [官方对话补全 API](https://docs.bigmodel.cn/api-reference/%E6%A8%A1%E5%9E%8B-api/%E5%AF%B9%E8%AF%9D%E8%A1%A5%E5%85%A8) 为 GLM-5.3-Flash 系列列出 `max_tokens`、128K 最大输出，建议至少 1024（建议不是强制）。设计默认 512 不应被实现静默放大；思考模型可能耗尽小预算，必须真实验证最终回答和提取是否截断。
- 模型页称支持结构化输出；[结构化指南](https://docs.bigmodel.cn/cn/guide/capabilities/struct-output) 指定 `response_format={"type":"json_object"}`，并要求 Prompt 描述字段。总 API 的 `response_format` 又写“仅文本模型支持”，而 Flash 是原生多模态。这一文档不一致需要真实 `json_mode` 请求验证，不能提前声称原生 JSON 模式已验收。

## 其他上游配置边界

| 上游 | base_url | 流式/JSON | 输出上限字段 |
| --- | --- | --- | --- |
| DeepSeek | `https://api.deepseek.com` | `stream=true`；`response_format={"type":"json_object"}` | `max_tokens`；官方明确不是 `max_completion_tokens` |
| 本地 Ollama | `http://localhost:11434/v1/` | 官方列流式、JSON mode、`response_format` | 官方支持字段列 `max_tokens`；未据此确认 `max_completion_tokens` |
| Claude 官方兼容层 | `https://api.anthropic.com/v1/` | `stream` 支持；`response_format` 忽略 | `max_tokens` 和 `max_completion_tokens` 都支持 |

DeepSeek JSON 模式 Prompt 要包含 JSON 要求，输出可能为空，预算不足可能截断：[JSON 指南](https://api-docs.deepseek.com/guides/json_mode)、[API](https://api-docs.deepseek.com/api/create-chat-completion)、[明确字段兼容说明](https://api-docs.deepseek.com/quick_start/agent_integrations/oh_my_pi)。选择无需 `/v1` 的已核对地址即可，不依赖不同集成的路径建议。

Ollama 本地 `api_key="ollama"` 是 SDK 必需但服务忽略的占位值；云端 `https://ollama.com/v1` 需要真实云端 API key，两者不要混同。[兼容说明](https://docs.ollama.com/api/openai-compatibility)。本章示例仍以本地实例为准。

Claude JSON 依赖 Prompt 遵循与应用 Pydantic 验证；不自动换原生 Messages、工具调用或其他协议。[官方兼容说明](https://platform.claude.com/docs/en/cli-sdks-libraries/libraries/openai-sdk)。

## 同一 ChatOpenAI 工厂的保守配置

- 显式 `use_responses_api=False`，因为模型名可能触发 Responses 路由，独立于 base_url。
- 显式 `stream_usage=False`，避免要求通用兼容端点必须支持 usage chunk。缺 usage 不等于 token 使用为零。
- 配置有限 timeout；初始推荐 `max_retries=0`，让应用清楚处理上游失败，避免重试导致 SSE 行为含糊。具体秒数与是否容许连接建立前重试是应用决策，不是文档保证。
- 提取显式 `with_structured_output(ExtractionSchema, method="json_mode")`；Prompt 描述三字段、枚举和 null，Pydantic 负责字段校验。JSON mode 不等于原生 schema 强制。不要传 `strict=True`，也不依赖随版本变化的默认 method。

依据：[ChatOpenAI 参考](https://reference.langchain.com/python/langchain-openai/chat_models/base/ChatOpenAI)、[stream_usage](https://reference.langchain.com/python/langchain-openai/chat_models/base/BaseChatOpenAI/stream_usage)、[with_structured_output](https://reference.langchain.com/python/langchain-openai/chat_models/base/ChatOpenAI/with_structured_output)。

## 输出上限必须验证最终 HTTP JSON

官方参考所指 [ChatOpenAI 源码快照](https://github.com/langchain-ai/langchain/blob/026c3da2b615abe52f8446e37de460b844d07a43/libs/partners/openai/langchain_openai/chat_models/base.py) 中 `_default_params` 与 `_get_request_payload` 都把顶层 `max_tokens` 改为 `max_completion_tokens`。因此构造器 `max_tokens=512` 不足以保证 DeepSeek/Ollama/GLM 正确收到 `max_tokens`。`disabled_params` 不是通用的最终请求重写机制。

建议使用公开的 `extra_body` 路径：不要设置 ChatOpenAI 顶层 `max_tokens`/`max_completion_tokens`，由 `.env` 明确选择 `LLM_TOKEN_LIMIT_FIELD=max_tokens|max_completion_tokens`，构造 `extra_body={所选字段: MAX_OUTPUT_TOKENS}`。ChatOpenAI 只改写顶层参数；[OpenAI SDK 官方源码](https://github.com/openai/openai-python/blob/main/src/openai/_base_client.py) 将 `extra_body` 放入 `extra_json` 并在创建 HTTP 请求时合并到 JSON 顶层。因此该路径可保留所选字段，不需要私有方法覆写、代理或换协议。这是依据公开接口和源码的推论，尚未对项目锁定版本实际执行。

实现后必须用模拟 HTTP transport 捕获完整最终 JSON：选择 max_tokens 时存在正数 max_tokens 且无 max_completion_tokens；反向选择亦然；同时断言 `chat/completions` 路径、流式参数和提取 `response_format`。不要只断言工厂对象属性，不能静默丢弃上限。官方允许的参数与某一模型/账号实际可用能力仍需真实验收。

若 JSON mode 被上游拒绝，按 spec 报错并记录能力限制，不自动换协议、调用工具、换模型或删除格式参数。Claude 官方忽略 response_format 的已知行为仍按 Prompt 与应用校验验收。
