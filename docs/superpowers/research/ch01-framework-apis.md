# Ch01 框架接口研究

核对时间：2026-10-05。只查文档与公开源码、PyPI 元数据；未安装依赖、未执行产品代码。Context7 MCP 先于接口与包版本核对，调用了 `tools/list`、`resolve-library-id`、`query-docs`。查询使用官方 MCP `https://mcp.context7.com/mcp`；按 SSE `data:` 返回取得资料。

## 1. Context7 查询来源

- Pydantic Settings：`/pydantic/pydantic-settings`，dotenv、alias、extra 行为。
- Pydantic：resolve Pydantic Settings 结果中同时返回 `/pydantic/pydantic`；查询 SecretStr、required nullable、extra。
- FastAPI：`/websites/fastapi_tiangolo`，原生 SSE 与 request scope yield 依赖。
- LangChain：`/websites/reference_langchain`，`trim_messages` 签名与边界。

## 2. 配置和数据模型

导入 `BaseSettings, SettingsConfigDict` 来自 `pydantic_settings`；`Field, SecretStr, field_validator, ConfigDict` 来自 `pydantic`。

- `SettingsConfigDict(env_file='.env', env_file_encoding='utf-8', extra='forbid')` 会读取相对**进程 cwd** 的文件；不会自动向上搜索父目录。可给绝对路径，或测试构造时传 `_env_file=临时文件路径`；`_env_file=None` 禁用 dotenv。
- `Field(validation_alias='LLM_API_KEY')` 指定输入/env 名；validation_alias 不改变序列化字段名。设置了 alias 的字段不再加 `env_prefix`，避免二者叠加误判。
- 默认优先级：初始化实参 > 进程环境 > dotenv > secrets > 默认值。测试不能受开发者真实环境污染：删除相关 env，并使用临时文件。
- Settings 的 extra 默认 forbid，dotenv 未声明键会触发 ValidationError；系统环境中的其他变量不因此全部成为 extras。专属项目 `.env` 可以显式 forbid，若故意共用大型 `.env` 则需明确 ignore 的理由。
- `SecretStr` 只隐藏 repr/常规序列化，**不自动拒绝空白**。`Field(min_length=1)` 可拒绝空串，空格还需 `@field_validator('api_key')` 的 after validator 对 `value.get_secret_value().strip()` 做非空检查，返回原 SecretStr。不要为了检测空白改写有效密钥。异常不得带真实密钥；Pydantic 验证错误的 input 可能仍包含原值，启动错误需要安全化或使用 `hide_input_in_errors=True` 并避免输出 `.errors()` 原始对象。
- 普通请求/提取 schema 用 `model_config = ConfigDict(extra='forbid')`，否则 BaseModel 默认忽略额外字段。
- `order_id: str | None` 和 `expected_solution: str | None` **不赋默认值**：键必填但允许 null。写成 `= None` 会允许缺键，不符合固定三键契约。
- 对 string/null 字段还需拒绝空串/纯空白（允许 null）；枚举字段本身 required。`Field(min_length=1)` 不等价于非空白检查。

官方依据：[Settings](https://docs.pydantic.dev/latest/concepts/pydantic_settings/)、[required nullable](https://docs.pydantic.dev/latest/migration/#required-optional-and-nullable-fields)、[SecretStr](https://docs.pydantic.dev/latest/api/types/#pydantic.types.SecretStr)、[ConfigDict](https://docs.pydantic.dev/latest/api/config/)。

## 3. SSE 的两个合法构造路径

原生 SSE 于 **FastAPI 0.135.0** 加入。`from fastapi.sse import EventSourceResponse, ServerSentEvent`；`ServerSentEvent(data={'delta': text}, event='delta')` 自动编码 JSON。其他字段：`raw_data=None, id=None, retry=None, comment=None`，data/raw_data 互斥。

继承来的构造器：

```text
EventSourceResponse(content, status_code=200, headers=None, media_type=None, background=None)
StreamingResponse(content, status_code=200, headers=None, media_type=None, background=None)
```

**构造器签名相同不代表任意生成器内容均可直接传入。** `EventSourceResponse` 本身只是 `StreamingResponse` 子类和路由标记。`ServerSentEvent` 的编码发生在 FastAPI **async generator 路由**的 routing 层；普通 `async def` 路由直接 `return EventSourceResponse(生成 ServerSentEvent 对象的生成器)` 不会经过该编码逻辑。

合法选择 A：`@router.post(..., response_class=EventSourceResponse)` 的路由自身 `yield ServerSentEvent(...)`。前置 session_busy / input_too_long 不能放在首次 yield 前的生成器执行体里并期待普通 HTTP 错误——生成器体开始时响应可能已开始。用路由依赖完成占用与预算校验，再进入生成器；request scope 的 yield dependency 管理资源。原生路径自动 no-cache、X-Accel-Buffering: no，并在空闲 15 秒发 ping 注释。

合法选择 B：普通 async 路由先完成占用/预算校验，再 `return StreamingResponse(生成已经编码的 SSE bytes 的生成器, media_type='text/event-stream', headers=...)`。帧应 `event: delta\ndata: JSON\n\n`，JSON 编码保护文本中的换行；设置 no-cache、X-Accel-Buffering: no。无需额外 sse-starlette 包；默认没有原生 ping，当前短对话无需自制心跳机制。

新建项目可以选择 A 或 B；本研究未替用户改变选型。B 的 preflight 边界更容易写清楚。若锁 FastAPI <0.135，原生 A 不存在，B 仍成立。

### 断开与资源释放

Starlette 1.7.0 的 `StreamingResponse`：ASGI spec <2.4 时并行监听 `http.disconnect`，取消流任务；>=2.4 时依赖 send 的 OSError，转换 ClientDisconnect。客户端在上游阻塞时关闭连接，>=2.4 分支不一定立刻观察到断开，不能承诺所有 server/ASGI 版本均同样及时。当前计划必须用选定 Uvicorn 版本实测该路径。

- 生成器 `finally` 显式关闭上游迭代器，退出资源 context，释放占用；不可捕获取消后继续生成或发 done。
- 仅有生成器 finally 也不要视为 send 失败时确定会被即时调用：异常可能发生在生成器暂停 yield 时。推荐让 request scope 依赖/响应生命周期拥有资源，保证响应异常后的清理；`Depends(dependency, scope='request')`（yield 的默认 scope）退出在响应后，`scope='function'` 会过早释放。
- 需要 await 的 cleanup 在 AnyIO cancel scope 内可被再次取消，应用设计需保证其有限时间完成，必要时在 bounded/shielded cleanup 内关闭；释放内存占用应放在无 await 的 finally 中，防止关闭异常遮住释放。
- 原生 FastAPI SSE 当前 routing 在 request-scoped AsyncExitStack 中创建 producer task group，退出时取消 producer；应用仍应显式关闭自己的上游迭代器。
- 取消通常没有可发送 error 的客户端；失败不得提交半轮。对等待下一块时取消、首块之前取消、send 失败、主动关闭生成器等路径都要测试。

官方依据：[SSE](https://fastapi.tiangolo.com/tutorial/server-sent-events/)、[SSE reference](https://fastapi.tiangolo.com/reference/sse/)、[yield dependencies](https://fastapi.tiangolo.com/advanced/advanced-dependencies/)、[FastAPI 0.142.2 sse.py](https://github.com/fastapi/fastapi/blob/0.142.2/fastapi/sse.py)、[routing.py](https://github.com/fastapi/fastapi/blob/0.142.2/fastapi/routing.py)、[Starlette 1.7.0 response](https://github.com/encode/starlette/blob/1.7.0/starlette/responses.py)。

### 测试层级

HTTPX 0.28.1 `ASGITransport` 等待 app 完成后拼接所有 `body_parts` 返回（`ASGIResponseStream.__aiter__` 只 yield join）；即使客户端使用 `.stream()` 也不能证明应用增量及时到达或模拟真实中途断开。

- ASGITransport：422/409/502 JSON 和最终 SSE 帧内容/顺序。
- 直接流服务生成器：用 Event 门控替身，收到第一增量时下一增量仍未被允许；取消/关闭时检查 iterator closed、历史不变、session unlocked。
- 可控 ASGI receive/send harness：发送一次 `http.request` 后，在首 delta 出现时发送 `http.disconnect`；send 故障另测 >=2.4 分支。receive 的其他请求不能竞争消费同一消息流。
- 本地真实 Uvicorn + HTTP 客户端/curl：在最终块未生成时看到首 delta，客户端关闭后上游替身停止且会话可复用；这才验证实际网络栈。不用真实上游密钥做离线行为测试。

依据：[HTTPX ASGITransport 0.28.1](https://github.com/encode/httpx/blob/0.28.1/httpx/_transports/asgi.py)。

## 4. trim_messages 与完整轮次

`from langchain_core.messages.utils import trim_messages`。

```text
trim_messages(messages, *, max_tokens: int, token_counter,
              strategy='last', allow_partial=False,
              end_on=None, start_on=None, include_system=False,
              text_splitter=None) -> list[BaseMessage]
```

`token_counter` 可为 `Callable[[list[BaseMessage]], int]`、单消息 callable、模型或 approximate。项目使用**显式注解 list[BaseMessage] 参数的自定义 callable**，防止库按单消息计数器猜测；计算文本 UTF-8 长度与每消息固定开销，采用可加、非负计数以让边界可测。

对已保证仅 `[HumanMessage, AIMessage]` 成对的历史，可以在 `[SystemMessage, *完整历史, 当前 HumanMessage]` 上调用：`strategy='last', include_system=True, start_on='human', end_on='human', allow_partial=False`。

- 先验证 system + current 在预算内；current 是最后一个 human；`end_on='human'` 在 last 策略下先丢最后 human 后的消息，当前输入没有后续消息，故不会掉历史 assistant。
- last 截出的 suffix 若从旧 assistant 开始，start_on human 会删孤立 assistant，剩下从 human 到 current 的序列；纯交替输入下历史部分仍成对。
- `allow_partial=False` **只禁止裁消息内部**，本身不保证轮次完整；成对前置不变量、start_on 和断言仍必要。
- 结果检查 system 保留、current 原内容保留、历史角色严格 human/ai 交替且为完整 pair、计数 <=预算。当前问题不截断；必留项放不下时拒绝。
- 若改为只 trim 历史并预留 system/current，历史应 `start_on='human', end_on='ai'`；这种方法要求计数的固定整体开销只算一次，避免重复扣预算。推荐 whole-list 方案少一个算术边界。

边界测试：仅必留项正好预算；小 1 被拒；最后单独 assistant 放得下但其 human 放不下时整对淘汰；最后一对超预算只留当前；中文/英文/空历史；失败后原历史不因请求侧裁剪被修改。

依据：[trim_messages](https://reference.langchain.com/python/langchain-core/messages/utils/trim_messages)。

## 5. 版本元数据及候选范围

Context7 查询后从各 `https://pypi.org/pypi/{package}/json` 读取版本、requires_python、requires_dist。以下是查询时最新稳定发行，**不是已安装或已通过运行验证的锁**。

| 包 | 最新稳定版本 | 关键约束 |
|---|---|---|
| fastapi | 0.142.2 | Python >=3.10；starlette >=0.46.0；pydantic >=2.9.0 |
| starlette | 1.7.0 | Python >=3.10；anyio >=4,<5 |
| pydantic | 2.13.5 | Python >=3.9；pydantic-core ==2.46.5 |
| pydantic-settings | 2.15.0 | Python >=3.10；pydantic >=2.7；python-dotenv >=0.21 |
| langchain | 1.4.3 | Python >=3.10,<4；core >=1.6.3,<2；pydantic >=2.7.4,<3；langgraph >=1.2.11,<1.3 |
| langchain-core | 1.6.6 | Python >=3.10,<4；pydantic >=2.7.4,<3 |
| langchain-openai | 1.6.7 | Python >=3.10,<4；core >=1.6.6,<2；openai >=2.45,<4 |
| openai | 3.24.0 | Python >=3.10；pydantic <3；anyio >=4.10,<5；httpx2 >=2.12,<3 |
| uvicorn | 0.54.0 | Python >=3.10 |
| httpx | 0.28.1 | Python >=3.8 |
| pytest | 9.1.1 | Python >=3.10 |
| pytest-asyncio | 1.4.0 | Python >=3.10；pytest >=8.4,<10 |

元数据交集可用 Python >=3.10,<4；控制器实际检测到已有 Python 3.13.5（E:\miniconda3\python.exe），计划明确使用它，取代调研初期的 3.11/3.12 建议；二进制 wheel 可用性需实际解析。框架最小 API floor 是 FastAPI >=0.135（原生 SSE）/Pydantic v2，当前候选版本整体元数据没有上述直接依赖冲突；安装阶段应选一个确切组合并锁全部传递依赖，而非把“最新列表”当成已验证结果。

需要特别确认 OpenAI 3.x 的 httpx2 与 LangChain HTTP client 集成；latest 的 requires_dist 允许 3.x，但实际 Client 签名/运行行为仍需锁后检查。可以在查相应版本官方 API 后选择仍稳定的 OpenAI 2.x 组合，不能只凭记忆指定下界。项目只用 PromptTemplate/messages/trim_messages/ChatOpenAI 时直接依赖 `langchain-core` + `langchain-openai` 就属于 LangChain 技术栈；若用户的“LangChain”要求安装 umbrella 包则保留 `langchain`。umbrella 的 langgraph 传递安装不等于产品使用 Agent。

此文件为实现计划依据；尚无产品实现、依赖安装、真实模型或网络增量测试结论。

## 6. 执行前补充 Context7 查询

控制器于用户批准计划后、相应任务实现前实际查询官方 MCP：

- Task 1：`/pydantic/pydantic-settings` 和 `/pydantic/pydantic`，再次核对源优先级、validation_alias、dotenv extra、必填 nullable 与 extra forbid；版本相关行为仍用安装后的测试核验。
- Task 2：`/websites/reference_langchain`，确认 trim_messages 的完整签名和 role 边界；allow_partial=False 不能单独保证成对历史。
- Task 3：同一官方参考库，核对 PromptTemplate.from_template/format、ChatOpenAI 公开参数与 with_structured_output(method='json_mode', include_raw=True)。返回内容混有旧默认值，因此不依赖默认 method，按锁定版本实际签名和 wire 测试验证。
- Task 4：`/websites/fastapi_tiangolo`，核对返回编码 bytes 的 StreamingResponse 路径；另 resolve AnyIO 得到 `/agronholm/anyio`，再 query-docs 核对 create_task_group、cancel_scope.cancel、get_cancelled_exc_class、CancelScope(shield=True)。取消捕获后须重抛，异步清理需 shield 并设有限超时。
- HTTPX：resolve 得到 `/encode/httpx`，query-docs 确认 AsyncClient.stream、aiter_lines/aiter_bytes/aclose、MockTransport 和 ASGITransport 的公开用法。Context7 索引标注版本 0.27.2，当前锁为 0.28.1；不足部分对照锁定安装的公开接口及官方版本源码，不将旧索引当成当前运行保证。

原始 MCP 返回保存在本计划 SDD 临时工作区对应 context7-*.md；核心依据记录于本文，临时区清理不删除研究结论。

官方来源：[AnyIO cancellation](https://anyio.readthedocs.io/en/stable/cancellation.html)、[HTTPX async](https://www.python-httpx.org/async/)、[HTTPX transports](https://www.python-httpx.org/advanced/transports/)。本补充只报告文档核对，不代替真实运行和模型验收。
