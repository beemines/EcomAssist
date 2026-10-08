# 第二步源码解析：Function Calling 工具链

第一步的客服能聊天，却不能把一句“查一下物流”变成一次有结果可查的业务操作。第二步把工具链接进原来的聊天入口：模型先决定要不要调用工具，应用校验并执行，把结果回灌给模型，再流式返回回答。会话、工具申请、工具结果和最终回复都落进 MySQL，浏览器里也能看到这轮到底调了什么。

本文按 `feat/tool-calling` 的末版 `a564675f9fecb58e57828f002621c1506a35ca85` 走读，代码片段与下表行数都来自 `git show feat/tool-calling:<路径>`，空行和注释计入规模。当前 `master` 已有第三步，尤其 `FAQRepository.search` 已换成语义检索；这里讲的是第二步的问题列 SQL LIKE，不把后来的向量库算进来。

## 模块概览

| 文件 | 规模 | 职责 |
| --- | --- | --- |
| `compose.yaml` | 53 行 | MySQL 应用库、独立测试库、卷与初始化挂载 |
| `sql/mysql-entrypoint.sh` | 7 行 | 复制字符集配置并交回官方入口 |
| `sql/mysql.cnf` | 7 行 | 初始化客户端与服务端使用 utf8mb4 |
| `sql/schema.sql` | 57 行 | 原始四表 DDL、枚举、JSON 与外键 |
| `sql/seed.sql` | 28 行 | 可重复执行的演示数据 |
| `app/main.py` | 89 行 | 装配模型、数据库、仓储与聊天服务 |
| `app/config.py` | 69 行 | 模型、MySQL、工具预算与重试配置 |
| `app/db/models.py` | 58 行 | 映射四表，不代替原始 DDL 建表 |
| `app/db/session.py` | 16 行 | 异步连接池与独立 Session |
| `app/repositories/conversations.py` | 69 行 | 会话创建、消息追加与流水读取 |
| `app/repositories/records.py` | 86 行 | 数据库记录与 LangChain 消息互转 |
| `app/repositories/faq.py` | 20 行 | 第二步的字面 LIKE 检索 |
| `app/repositories/tickets.py` | 61 行 | 工单编号、重试复用与原子转人工 |
| `app/tools/schemas.py` | 34 行 | 四种参数模型与隐藏调用 id |
| `app/tools/types.py` | 23 行 | 请求上下文、工具申请与执行结果 |
| `app/tools/business.py` | 45 行 | 三个 mock 查询、FAQ 与人工工单 |
| `app/tools/registry.py` | 11 行 | 五工具名称到对象的注册表 |
| `app/tools/executor.py` | 105 行 | 校验、超时、有限重试与安全错误 |
| `app/core/tool_chat.py` | 174 行 | 一次选择、执行、回灌与最终流 |
| `app/core/tool_history.py` | 102 行 | 完整轮次识别与预算裁剪 |
| `app/core/conversation_locks.py` | 29 行 | 单 worker 会话占用与幂等释放 |
| `app/core/prompts.py` | 59 行 | 客服、提取及工具聊天模板 |
| `app/api/conversations.py` | 18 行 | 创建数字会话身份 |
| `app/api/chat.py` | 20 行 | 在原聊天入口接入工具服务 |
| `app/api/streaming.py` | 74 行 | SSE 编码、终止与断连清理 |
| `app/schemas/conversation.py` | 26 行 | 会话请求与字符串身份响应 |
| `app/schemas/chat.py` | 27 行 | 聊天身份与正文校验 |
| `app/static/chat.js` | 352 行 | 创建会话、解析 SSE 与工具徽章 |

## 先把四张表按原样落地

### mysql-entrypoint.sh：把编码配置交给官方入口

`compose.yaml`、`sql/mysql-entrypoint.sh`、`sql/mysql.cnf`

```yaml
      - ./sql/mysql.cnf:/config/mysql.cnf:ro
      - ./sql/mysql-entrypoint.sh:/config/mysql-entrypoint.sh:ro
      - ./sql/schema.sql:/docker-entrypoint-initdb.d/01-schema.sql:ro
      - ./sql/seed.sql:/docker-entrypoint-initdb.d/02-seed.sql:ro
```

编号决定先建表再灌种子。这里利用 MySQL 官方入口初始化空数据目录，已有卷再次启动不会重跑这两份 SQL。应用库映射到本机 3307，`test` profile 下的独立库映射到 3308，各自有卷，不靠在应用库里清表来验证。

```sh
# Windows 绑定挂载呈现为全员可写，MySQL 会忽略它；复制到容器后收紧权限。
cp /config/mysql.cnf /etc/mysql/conf.d/charset.cnf
chmod 0644 /etc/mysql/conf.d/charset.cnf
exec /usr/local/bin/docker-entrypoint.sh "$@"
```

这四行来自一次真实初始化失败。镜像客户端的自动编码把中文 ENUM 解码错，种子写不进去；补了 utf8mb4 配置，又遇到 Windows 挂载文件呈现为全员可写，被 MySQL 忽略。包装入口先复制、收紧权限，再用 `exec` 进入官方入口。配置同时指定 `[client]` 的 `default-character-set=utf8mb4` 和服务端字符集，不能只管服务端。脚本另以 LF 固定换行，失败初始化卷当时保留，没有改写用户 DDL 来绕过问题。

### Message：工具申请和结果各占一行

`sql/schema.sql`、`app/db/models.py`、`sql/seed.sql`

```sql
  role            ENUM('user','assistant','tool') NOT NULL COMMENT '角色:用户/助手/工具结果',
  content         TEXT            NULL                     COMMENT '消息正文,assistant 纯工具调用时可为空',
  tool_calls      JSON            NULL                     COMMENT 'assistant 消息带的工具调用申请单',
  tool_call_id    VARCHAR(64)     NULL                     COMMENT 'tool 消息对应的申请单 id,回灌时对号入座',
```

`conversations` 是会话壳，`messages` 是流水，`faq` 存问答，`tickets` 存人工工单；消息和工单都以外键关联会话。订单、商品、物流没有表，它们在工具里模拟。工具申请属于 assistant，申请单放 JSON；执行结果属于 tool，用 `tool_call_id` 对回申请。纯工具申请可以没有正文，这就是 `content` 允许 NULL 的原因。

ORM 的 `JSON(none_as_null=True)` 让没有工具申请的行落 SQL NULL，而不是 JSON 的 `null`。两者对数据库判断不是一回事，这里曾补过回归再修正。`Base` 明确只映射已有表，建表仍执行原始 SQL，不让 `create_all` 另造一份近似结构。

`seed.sql` 在事务里用 `WHERE NOT EXISTS` 插入会话、消息、固定工单和两条 FAQ，重复执行不重复插入。`seed-user` 与浏览器的 `demo-user` 分开：验收库已有正常浏览器会话，旧断言要求没有任何 demo-user，会错把真实写入当故障。返工改成核对种子身份与关联，没有清库求绿灯。种子可重复执行不意味着会话创建接口幂等；调用创建接口会得到新的会话。

## 会话身份与短事务

### create_app：在入口把依赖接起来

`app/main.py`

```python
    faq, tickets = FAQRepository(database), TicketRepository(database)
    app.state.chat_service = ToolChatService(model, repository,
        lambda context: build_registry(faq, tickets, context), ConversationLocks(), settings)
```

模型、会话仓储、注册表工厂、会话锁和设置都从这里交给服务。FAQ 和工单共享连接池，各次操作自己取 Session。默认入口创建并拥有模型和数据库，lifespan 负责关闭；显式注入的资源由调用方管理。只注入无数据库的离线仓储时使用安全不可用对象，误调数据库工具会失败，不会凭空造一份 FAQ 或工单结果。

### _conversation_id 与 Database.session

`app/repositories/conversations.py`、`app/db/session.py`

```python
def _conversation_id(value: str) -> int:
    if not isinstance(value, str) or not re.fullmatch(r"[1-9][0-9]{0,19}", value) or int(value) > 18446744073709551615:
        raise ServiceError("invalid_conversation_id", "Conversation id must be a positive decimal string.", 422)
    return int(value)
```

第一步的内存会话身份在这里对齐数据库的 BIGINT UNSIGNED。HTTP 上始终传规范十进制字符串，不能有前导零，也不能超过无符号 64 位范围；进仓储时才转 Python 整数。这样大于 JavaScript 安全整数的真实主键到浏览器也不会丢精度。请求 Schema 还以 `strict=True` 拒绝数字被偷偷转成字符串，正文和 user_id 拒绝纯空白。

连接池属于 `Database`，Session 每次新取。仓储用 `async with session, session.begin()` 做短事务，创建时 `flush` 拿自增 id，退出事务后才返回字符串。不会拿着一个数据库事务等模型输出几十秒。`app/config.py` 用 `URL.create` 组装连接地址，避免凭据里的特殊字符被当成 URL 分隔符；本文不展开本地配置值。

### record_from_message 与 append_message

`app/repositories/records.py`、`app/repositories/conversations.py`

```python
        serialized = [{"id": call.get("id"), "type": "function", "function": {
            "name": call.get("name"),
            "arguments": json.dumps(call.get("args"), ensure_ascii=False, separators=(",", ":"), allow_nan=False),
        }}]
        decode_tool_calls(serialized)
        return MessageRecord(identifier, "assistant", content or None, serialized, None)
```

LangChain 的申请用 `name/args/id`，持久化换成 Chat Completions 的 `function.name/function.arguments`，其中 arguments 是 JSON 字符串。回放再由 `decode_tool_calls` 换回来。转换器拒绝多个申请、非对象参数、NaN 等非有限 JSON 和过长文本，保存与回放共用规则，避免一边能写、一边读不回来。

```python
            if row.role == "tool":
                previous = (await session.scalars(select(Message).where(Message.conversation_id == identifier).order_by(Message.id.desc()).limit(1))).first()
                if previous is None or previous.role != "assistant" or previous.tool_calls is None:
                    raise ValueError("Tool result has no pending request.")
                calls = decode_tool_calls(previous.tool_calls)
                if row.tool_call_id != calls[0]["id"]:
                    raise ValueError("Tool result does not match the pending request.")
```

工具结果不是随便追加：上一行必须是待处理申请，结果 id 必须匹配。消息按真实主键排序，追加返回真实消息 id，后面工单就用它区分不同用户轮次。`已结束` 会话不能继续写，`已转人工` 仍允许续聊；读取历史则也允许已结束会话。

### acquire 与 Lease.release

`app/core/conversation_locks.py`

```python
    def acquire(self, conversation_id: str) -> Lease:
        if conversation_id in self._occupied:
            raise SessionBusy()
        lease = Lease(conversation_id, self)
        self._occupied[conversation_id] = lease._identity
        return lease
```

这是单 worker、单事件循环内的同步占用检查，没有 await 竞争窗口。第二个同会话请求直接拒绝，不排队等前一轮。它依赖进程内字典，多 worker 各有一份，不能当成跨进程会话锁。

`Lease.release` 比较占用对象与自身 `_identity`，所以重复释放旧 lease 不会删掉后来请求的新占用。这里的幂等是释放幂等；完整聊天串行化仍要遵守单 worker 部署边界。

## 五个工具怎样交给模型

### ToolArgs 与 build_registry

`app/tools/schemas.py`、`app/tools/registry.py`

```python
class ToolArgs(BaseModel):
    model_config = ConfigDict(extra="forbid", strict=True)

    @field_validator("order_id", "product_id", "keyword", "description", check_fields=False)
    @classmethod
    def require_nonblank_business_text(cls, value: str) -> str:
        # 仅拒绝全空白；合法参数保留原文，避免改变标识符或 FAQ 连续片段。
        if not value.strip():
            raise ValueError("Business text must not be blank.")
        return value
```

五个工具只需要四种参数模型：订单和物流共享 `OrderArgs`，商品用 `ProductArgs`，FAQ 用 `FAQArgs`，工单用 `TicketArgs`。长度与类型有界，工单类型只有售后、投诉、咨询。纯空白校验是整分支评审后的修复：`min_length=1` 挡不住几个空格。校验只拒绝全空白，合法值保留原文，不能顺手 strip 改掉订单标识或 FAQ 的连续片段。

`build_registry` 把三个查询与两个上下文工具拼起来，返回 `{tool.name: tool for tool in tools}`，让模型可见定义和执行对象出自同一批。`@tool` 的说明、参数 Schema 交给模型，名字是执行查找入口。`ToolContext` 留在应用里，带会话 id、已保存的 user 消息 id 和当前原问题，不让模型自行指定身份。

### query_order、query_product、query_logistics

`app/tools/business.py`

```python
@tool(args_schema=OrderArgs)
async def query_order(order_id: str) -> dict:
    """查询订单演示信息；结果是随机模拟数据。"""
    return {"order_id": order_id, "mock": True, "status": random.choice(["待付款", "待发货", "已完成"]), "amount": random.randint(1000, 50000) / 100}
```

这不是去订单库查一行，而是带回用户给的号，再随机生成状态和金额。商品随机生成名称、价格和库存，物流随机生成运输状态、MOCK 运单号及预计天数；三者都返回 `mock=true`。同一个号重复问，数值可能不同，所以“工具真的执行了”不能被解释为“真实订单查到了”。

### query_faq 与 FAQRepository.search

`app/tools/business.py`、`app/repositories/faq.py`

```python
    @tool(args_schema=FAQArgs)
    async def query_faq(keyword: str) -> dict:
        """按当前问题原文关键词查询 FAQ，最多三条；无命中时不扩展同义词。"""
        if keyword not in context.user_question:
            return {"error": {"code": "invalid_keyword", "message": "关键词必须是当前用户问题中的连续原文片段。"}}
        matches = await faq.search(keyword, limit=3)
        return {"found": bool(matches), "matches": matches}
```

关键词必须来自当前问题的一段连续原文。“邮费是多少”不能被模型擅自改成“运费”再查，否则原本要暴露的漏召回被模型改写掩盖了。参数模型的 description 先告诉模型这个约束，闭包再检查一次；`found=false` 是正常空结果，错误对象才表示工具失败。

```python
        async with self.database.session() as session, session.begin():
            rows = (await session.scalars(select(FAQ).where(FAQ.question.contains(keyword, autoescape=True)).order_by(FAQ.id).limit(min(limit, 3)))).all()
            return [{"id": row.id, "question": row.question, "answer": row.answer, "category": row.category} for row in rows]
```

第二步的 `contains` 落成 LIKE，只搜 question，不搜 answer，也不扩展同义词。`autoescape=True` 把百分号、下划线按字面字符处理，不能拿它们扩大匹配范围。结果按 id 排序，最多三条，没有语义分数。

种子问题是“如何申请退货？”和“退货运费由谁承担？”。真实验收中 `query_faq(退货)` 得到两条，`query_faq(邮费)` 得到 `found=false, matches=[]`，这个漏召回是预期边界。两项最初因回答没出现固定短语被机械判失败，后来把结构事实和措辞观察拆开，人工复核事实正确。当前 master 的同名仓储已改为嵌入查询、向量召回、回读知识原文，那是第三步的变化，不是这里的 LIKE 有了同义词能力。

### create_ticket：身份由应用注入

`app/tools/schemas.py`、`app/tools/business.py`、`app/repositories/tickets.py`

工单 Schema 的 `tool_call_id: Annotated[str, InjectedToolCallId]` 由 LangChain 注入，不交给模型填写。会话与 user 消息身份从每请求独立闭包拿，调用 id 从工具申请拿，模型只填描述和类型。

```python
        ticket_no = "T" + sha256(f"{conversation_id}:{user_message_id}:{tool_call_id}".encode()).hexdigest()[:31]
```

这三个身份合成稳定业务主键。同一次执行超时后重试仍是同一个号，即使第一次已提交也能回读；用户重发一句会保存新的 user 消息，哪怕调用 id 相同也会得到另一张工单。这是同次调用重试的幂等，不是跨请求按描述去重。已有工单还要比较会话、描述和类型，不一致报冲突，不能覆盖旧内容。

```python
                session.add(ticket)
                conversation.status = "已转人工"
                await session.flush()
                # MySQL 不支持 INSERT RETURNING，显式加载服务端默认状态。
                await session.refresh(ticket, attribute_names=["status"])
                result = _result(ticket, identifier, description, ticket_type)
```

仓储先锁会话行、核对 user 消息确属当前会话，再查稳定编号。新建工单与会话转人工同一事务提交，半成功不会留下来。`refresh` 来自一次 MissingGreenlet：MySQL 没有 INSERT RETURNING，flush 后直接取服务端默认 status 会触发隐式异步加载，改成显式加载。完整性异常只在 MySQL 1062 重复键时开新 Session 回读，其他约束错误继续抛出。工单状态是“待处理”，不是退款已执行。

## 参数校验、超时与有限重试

### ToolExecutor.execute：先验证再尝试

`app/tools/executor.py`

```python
            schema = tool.get_input_schema()
            hidden = {name for name, field in schema.model_fields.items() if any(marker is InjectedToolCallId or isinstance(marker, InjectedToolCallId) for marker in field.metadata)}
            if hidden.intersection(call.args):
                return _error("invalid_arguments", 0)
            # 全参数模型保留 strict/forbid；LangChain 的模型可见子模型不保留所有配置。
            schema.model_validate({**call.args, **dict.fromkeys(hidden, call.id)})
```

未知工具和坏申请直接返回零次尝试。隐藏字段如果出现在模型参数里也拒绝，再把真实 call.id 补进去验证完整参数模型。这一步没有只信模型可见子模型，因为它不能完整保留 strict/forbid 配置。空白参数在这里就结束，不会把数据库连接打开后再碰运气。

```python
                # LangChain 注入会修改字典，因此每次执行都深拷贝原始参数。
                full_call = {"type": "tool_call", "name": call.name, "args": deepcopy(call.args), "id": call.id}
                async with asyncio.timeout(self.timeout_seconds):
                    result = await tool.ainvoke(full_call)
```

每次尝试深拷贝参数，防止第一次注入修改原字典，第二次误以为模型填写了隐藏字段。默认单次工具超时五秒、最多一次重试，也就是最多两次实际尝试；重试仍属于同一个逻辑工具调用，不会重新让模型选择。返回值必须是带 JSON 对象正文的 ToolMessage，再归一成 `ToolOutcome(content, status, attempts)`；安全错误信息不会把底层异常和连接细节送给用户。

只有超时和临时失联能重试；数据库连接错误识别失效连接及限定 MySQL 错误码，不把 SQL 错误、参数错误或业务冲突也算成暂时故障。次数到上限就回灌错误结果，让最终回答明确说明失败。工具返回后及异常归一前还检查 `task.cancelling()`：首轮评审复现过下层把最后一次取消转成超时或正常返回，外层会误重试、甚至报成功；修复后 pending cancellation 直接传播。用户停止与工具自身超时不是一个事件，取消不能变成重试理由。

## 模型只选择一次，执行后回灌收敛

### prepare 与 build_tool_chat_system_prompt

`app/core/tool_chat.py`、`app/core/prompts.py`

```python
            preview = _schema(self.registry_factory(ToolContext(conversation_id, 0, message)))
            messages = build_tool_messages(system, turns, current, self.settings.tool_input_token_budget, tool_schema=preview)
            user_message_id = await self.repository.append_message(conversation_id, current)
            registry = self.registry_factory(ToolContext(conversation_id, user_message_id, message))
            if _schema(registry) != preview:
                raise ServiceError("tool_schema_changed", "工具定义发生变化，请稍后重试。", 500)
```

先占用会话、确认可续聊、读取完整历史，再拿消息 id=0 的注册表只预览 Schema，不执行工具。必需输入能放进预算才保存 user，拿真实主键重建注册表。这样不必为预算检查新增表列，也避免把已知超限消息先写入 TEXT。预览和执行 Schema 必须一致；当前五工具不随 id 变，未来若动态改变会安全拒绝，此时可能已留 user 审计行。

工具聊天模板要求每条消息最多一个工具、问候无需工具、缺订单号先澄清、mock 明确标注模拟、失败不伪造政策，创建工单只能说转人工待处理。活跃 builder 最初直接返回静态文本，评审指出绕过了模板管理要求，末版改回 `PromptTemplate.format()`，渲染文案未变。模板约束不能代替回答质量验收：真实订单样例准确复述了模拟数值，却额外承诺可重新核实真实订单，记录仍把这项质量问题保留待复核。

### stream 与 _validate_selection：一次申请的硬边界

`app/core/tool_chat.py`

```python
            bound = self.model.bind_tools(list(prepared.registry.values()), tool_choice="auto", parallel_tool_calls=False)
            selected = await bound.ainvoke(prepared.messages)
            call = self._validate_selection(selected, prepared.registry)
```

选择阶段不是向浏览器输出正文，只拿模型的工具决定。`auto` 允许不调工具，禁并行只是请求约束，服务仍检查实际返回：必须是可解析 AIMessage，至多一个申请，原始 tool_calls 和解析后数量一致，结束原因也正常。没申请只接受 stop；有申请接受 tool_calls 或 stop，再核对名字、id、参数和可持久化 JSON。没有工具时跳过执行，仍另发最终流，不把选择文本直接当成完成回复。

```python
                result = ToolMessage(json.dumps(outcome.content, ensure_ascii=False, separators=(",", ":"), allow_nan=False),
                                     tool_call_id=call.id, name=call.name, status=outcome.status)
                await self.repository.append_message(prepared.conversation_id, result)
                yield StreamEvent("status", {"phase": "tool_completed", **identity, "status": outcome.status})
                pending = [selected, result]
```

申请先保存，执行前再检查参数预算，随后执行并保存匹配结果。这个预算复查也是返工：初版申请参数已超限仍会执行工具，后来补到副作用之前。结果成功或失败都带同一个调用 id 回灌；`tool_completed` 表示执行阶段结束，status 才区分 success/error，不能从事件名推断业务成功。

```python
            prepared.messages = build_tool_messages(SystemMessage(build_tool_chat_system_prompt()), prepared.turns,
                prepared.current, self.settings.tool_input_token_budget, tool_schema=[], current_tool_messages=pending)
            yield StreamEvent("status", {"phase": "answering"})
            parts: list[str] = []
            size = 0
            reasons: set[str] = set()
            prepared.upstream = self.model.astream(prepared.messages)
```

最后调用的是原模型，没有 bind_tools，Schema 为空，申请和结果作为一个组合重新核对预算。最终流里一旦再出现工具申请就报协议错误，不能开始下一轮执行。这里没有 Agent Loop，正常路径是一次选择、零或一次逻辑工具调用、一次最终回答；工具内部最多一次重试不改变这个形状。模型客户端本身关闭 SDK 自动重试，也没有失败后静默换模型的分支。

## 历史按完整轮次回放与裁剪

### completed_turns：保留流水，不回放半轮

`app/core/tool_history.py`

```python
            if isinstance(message, AIMessage) and not message.tool_calls:
                _validate_turn(group)
                turns.append(group)
                group = None
```

读取按消息主键排序，每个 user 开一个新组。普通轮次是 user、最终 assistant 两条；工具轮次是 user、assistant 申请、匹配 tool 结果、最终 assistant 四条。直到最终无工具 assistant 到来才验证并收进历史，畸形组等下一条 user 重开。中断留下的申请、结果照样在数据库供审计，但不冒充成功上下文；完整轮次之后的孤立结果也忽略。

### build_tool_messages：只丢最旧完整轮次

`app/core/tool_history.py`

```python
    schema_size = _serialized_size(tool_schema)
    required = estimate_tokens([system]) + _message_size([current, *pending]) + schema_size
    if required > budget:
        raise InputTooLong()
    kept = list(turns)
    costs = [_message_size(turn) for turn in kept]
    total = required + sum(costs)
    dropped = 0
    while total > budget and dropped < len(kept):
        total -= costs[dropped]
        dropped += 1
    return [system, *(message for turn in kept[dropped:] for message in turn), current, *pending]
```

System、当前 user、当前申请与结果是必需输入，超预算直接拒绝，不能裁掉半张申请单或截短工具事实。历史才可删，而且从最旧完整轮次开始整组删。选择前、执行前、回灌后各核一次；工具结果变大，也可能使最终阶段拒绝，此时已完成工具审计仍保留。

预算默认独立设为 8000，不能照搬第一步纯文本的 2000。计数沿用文本估算，再加 Schema、申请 JSON 和调用 id 的 UTF-8 序列化字节，是保守估算，不是提供方精确 tokenizer。初期测试用的 2500 连五工具必需定义都装不下，后来对齐本步预算，同时保留整轮裁剪断言。

## API 与 SSE：提交以后才能说完成

### chat 与 encode_sse

`app/api/chat.py`、`app/api/streaming.py`

创建走 `/api/conversations`，聊天仍是 `/api/chat`。prepare 在发 SSE 头之前完成，因此无效身份、不存在、已结束、占用、初始预算不足能以明确 HTTP 错误返回。开始流之后的模型或保存失败改成 error 帧，不再假装能把已发送的 HTTP 200 改成 502。

```python
def encode_sse(event: StreamEvent) -> bytes:
    payload = json.dumps(event.data, ensure_ascii=False, separators=(",", ":"))
    return f"event: {event.event}\ndata: {payload}\n\n".encode("utf-8")
```

状态阶段为 selecting、tool_running、tool_completed、answering，正文片段是 delta。响应层只把 done/error 当终止事件，status 后仍保持连接；否则第一个“正在选择”就会让流提前断掉。

### stream：最终助手提交先于 done

`app/core/tool_chat.py`

```python
            answer = "".join(parts)
            if reasons != {"stop"} or not answer.strip():
                raise _protocol_error("模型回复未正常完成，请稍后重试。")
            # 下层吞掉取消时仍不得把断开的流程提交为成功回答。
            task = asyncio.current_task()
            if task is not None and task.cancelling():
                raise asyncio.CancelledError()
            await self.repository.append_message(prepared.conversation_id, AIMessage(answer))
            yield StreamEvent("done", {"conversation_id": prepared.conversation_id})
```

片段到 EOF 后，结束原因必须恰好为 stop，正文非空，长度也不能超过可保存上限。再确认未被取消，仓储提交最终 assistant，最后才发 done。用户看见几个字不等于完成；保存失败只有 error。反过来，done 发送失败不会回滚已经提交的回答，数据库完成边界在发送之前。

真实 GLM 人工工单样例就停在这个边界之外：选择请求 HTTP 200、stop、零工具申请，未执行 `create_ticket`；最终流请求也是 HTTP 200，但应用只发状态和 upstream_error，没有 delta/done，数据库只留 user。验收观察器没记录流末块元数据和安全异常类型，现有证据不能确定是截断、超时、认证还是具体协议原因。代码检查、受控模型页面与真实 MySQL 验证通过，都不能把这个未知错误或未尝试的真实场景补成通过。

### ManagedChatResponse.__call__：断连时释放所有权

`app/api/streaming.py`、`app/core/tool_chat.py`

```python
            upstream, prepared.upstream = prepared.upstream, None
            close = getattr(upstream, "aclose", None)
            if close is not None:
                with anyio.move_on_after(5, shield=True):
                    try:
                        await close()
                    except Exception:
                        pass
```

服务先清空上游所有权，再以有界 shield 关闭，响应 finally 关闭事件生成器并释放 lease。返工前服务和响应会重复 aclose，上游关闭计数为二，取消也可能打断清理；末版各管自己持有的对象，关闭最多等五秒。ASGI 2.4 以上另监听断连，旧分支交给 Starlette，避免两个读取者竞争 receive。停止时取消传播到工具，最终 assistant 不按成功保存，已有审计流水仍在。

## 浏览器怎样显示这条工具链

### readReply 与 addMessage

`app/static/chat.js`

首轮先创建会话，后面发送 `{conversation_id, message}`。BigInt 只用于上限校验，保存和请求仍用字符串。新会话把页面身份置空，下次重新创建；浏览器内存不再承担后端历史，模型历史由数据库回放。

```javascript
  const answer = document.createElement("div");
  answer.className = "answer-text";
  answer.textContent = text;
  bubble.append(tools, answer);
```

徽章容器 tools 与正文 answer 是气泡里的两个子节点。流式更新只改 answer.textContent，徽章不会被整块覆盖，模型返回的 HTML 也按字面显示。片段用流式 TextDecoder 保留拆在网络包之间的 UTF-8，逐字队列用 `Array.from` 按 Unicode 码点拆，不把中文或代理对字符拆坏。

### acceptStatus 与 acceptFrame

`app/static/chat.js`

```javascript
  if (state.toolCallId !== payload.tool_call_id || state.toolName !== payload.tool_name) {
    throw new Error("这轮收到多个工具调用，请重新尝试。");
  }
  const status = phase === "tool_running" ? "running" : payload.status;
  const suffix = status === "running" ? "执行中" : status === "success" ? "已完成" : "未完成";
  state.toolBadge.dataset.status = status;
  state.toolBadge.textContent = toolLabels[payload.tool_name] + " · " + suffix;
```

工具名先在固定标签表内校验，调用 id 非空且有长度上限，同一轮只能更新同一个徽章。工具运行显示“执行中”，执行结果再变“已完成”或“未完成”；正文尚未结束时工具可以已经完成，两种状态分开。末版按用户要求去掉徽章的“演示”字样，所以看到“查询物流 · 已完成”并不改变后端 `mock=true`，回答仍须注明模拟。

done 还要核对当前会话身份，error 则保留安全提示。网络 EOF 没有终止帧会显示未完整结束，收到终止以后还有事件也拒绝，不能把连接断掉当成功。`stopReply` 在 done 前 abort 请求，done 后只显示完已收文字；未完成的运行徽章改为“结果未确认”。页面验收曾用受控模型与真实测试库验证这些状态，真实上游浏览器验收仍另有待完成部分，不能混在一起算。

## 小结

第二步把聊天中的一句问题走成了一条可审计的单次工具链：字符串会话身份进仓储，模型选择一个工具，应用验证参数并有限重试，申请和结果按调用 id 保存、回灌，未绑定工具的模型生成最终回答，提交成功以后才向浏览器发 done。短事务、完整轮次回放、取消传播和单 worker 占用共同守住这条链路的边界；它没有 Agent Loop，也没有真实订单系统。

FAQ 目前只能认出问题列里相同的一段字。“退货”能查到，“邮费”换个说法就漏掉，这个短板已经被真实结果量出来。下一步要提升的是 FAQ 的语义召回，同时保留这里的工具入口、持久流水和最终提交边界；真实 GLM 工单失败的未定原因仍是单独的验收问题，不能让后续检索升级替它作结论。
