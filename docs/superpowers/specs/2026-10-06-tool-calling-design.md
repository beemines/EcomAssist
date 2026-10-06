# 第二步设计：数据库持久化与单轮工具调用

日期：2026-10-06（北京时间）。

状态：用户已确认聊天中的设计并提供权威建表 SQL；本正式 spec 供用户审阅，实施计划尚未编写。

## 1. 目标与用户确认

在现有电商客服的聊天入口中加入 Function Calling：用户在聊天页提问，由模型选择业务工具，应用执行并回灌结果，模型再流式组织最终回答。

固定技术栈为 FastAPI、SQLAlchemy、Docker MySQL、LangChain `@tool`，模型继续通过已有的 OpenAI 兼容 Chat Completions 配置直连上游。执行方式沿用已选择的 Subagent-Driven；聊天页面改造按用户指定的 Vibe Coding 例外直接实现和验证。

用户本轮确认：“确认，然后以上是建表语句，到时候执行这段来建表，然后放一个sql文件在代码中进行存放”。

每条用户消息最多执行一个逻辑工具调用；允许该工具内部有限重试，禁止再启动一次模型选工具流程。没有工具申请时直接进入最终回答阶段。不加入 Agent Loop、向量检索、RAG 或订单/商品/物流数据库表。

## 2. 权威 DDL 与 Docker 初始化

用户 SQL 原样保存为 `sql/schema.sql`，它是建表结构的唯一来源。保留四张表、字段、可空约束、长度、中文 ENUM、默认值、索引、外键、InnoDB 和 utf8mb4；不添加消息状态、轮次 id 或工单幂等键列。

| 表 | 身份与主要字段 |
| --- | --- |
| conversations | 自增 BIGINT UNSIGNED 主键；user_id；进行中/已转人工/已结束；创建和更新时间 |
| messages | 自增主键；关联会话；user/assistant/tool；可空 content；JSON tool_calls；tool_call_id；创建时间 |
| faq | 自增主键；question、answer、category；创建和更新时间 |
| tickets | ticket_no 业务主键；关联会话；description；售后/投诉/咨询；待处理/已处理；创建时间 |

采用 MySQL 官方 `8.4` 镜像、具名数据卷和仅绑定本机的 `127.0.0.1:3307:3306`。容器入口的初始化目录挂载 `sql/schema.sql` 为首个建表脚本、独立的 `sql/seed.sql` 为第二个种子脚本；新数据卷首次启动时由 MySQL 原生客户端执行，不由 ORM 重新生成 DDL。

已有数据卷不会重复执行建表或重置数据。提供只读结构检查及单独执行 SQL 的维护说明；建表脚本不含 IF NOT EXISTS，不能把已有表错误忽略为成功，更不能自动 DROP 表或卷。运行前检查目标为本项目的演示数据库。

种子数据覆盖四张表：独立演示用户的会话、完整示例消息轮次及关联工单；FAQ 包含退货政策和以“运费”为关键词的配送费用问题。种子消息与工单符合外键和角色约束。

SQLAlchemy ORM 映射与 DDL 对齐。特别核对 UNSIGNED、自增、中文枚举及 MySQL 的 ON UPDATE 时间戳；ORM 不负责 create_all/drop_all。

## 3. 模块分层与资源生命周期

保留现有应用工厂、提取接口及静态页面，以本次需要的边界组织代码：

```text
sql/schema.sql、sql/seed.sql          # 权威结构与演示数据
compose.yaml                       # MySQL 服务、健康检查及数据卷
app/db/                            # 异步 Engine、Session 工厂和 ORM 映射
app/repositories/                  # 会话/消息、FAQ、工单数据库操作
app/tools/                         # 五个 @tool、注册表、参数与执行策略
app/core/chat.py                    # 单轮工具调用与最终流式回复服务
app/api/                           # 会话创建、聊天、提取和 SSE 编码
app/schemas/                       # 请求、工具参数及结果模型
app/static/                        # 既有聊天页面及工具徽章
```

采用 SQLAlchemy 2.x 的 `create_async_engine`、`async_sessionmaker` 和 aiomysql MySQL 驱动；新增版本在计划/依赖任务中锁定并核对实际接口。一次数据库工作对应一个短 Session/事务；模型请求、工具等待及 SSE 推送期间不持有长事务。应用关闭释放异步 Engine 和自有模型客户端。

本步保持单 worker 与会话占用锁，同会话并发返回 409，进程重启后从 MySQL 恢复完整历史。演示使用 user_id，不添加登录与后台工单管理功能。

## 4. 会话身份与聊天接口

DDL 的数字会话主键取代第一步的客户端 UUID。保留 `/api/chat` 路径，新增 `POST /api/conversations` 创建会话壳，请求 `{"user_id":"demo-user"}`，响应 `{"conversation_id":"1"}`。

`POST /api/chat` 请求改为 `{"conversation_id":"1","message":"订单 1001 的物流到哪了"}`。ID 是正整数的十进制字符串，转换为数据库 BIGINT 后校验；响应使用字符串避免 JavaScript 大整数精度损失。无效参数返回 422，不存在的会话返回 404，已结束的会话返回 409；已转人工的会话允许继续提问。

页面首次发送前创建会话并保留返回的 conversation_id；“开启新对话”清空当前身份，下一次发送再创建会话。修改页面、curl、smoke 和相关测试，明确新请求契约；不增加 UUID 对照表或隐式进程内身份映射。

`/api/extract` 的请求和结构化提取功能保留。`/health` 仍只表示应用存活；数据库就绪和模型能力分别验证。

## 5. 五个工具与执行策略

| 工具 | 参数 | 数据源及约束 |
| --- | --- | --- |
| query_order | order_id | 随机生成订单演示信息，返回用户提供的订单号及 mock 标识，不含物流跟踪接口 |
| query_product | product_id | 随机生成商品演示信息，带 mock 标识 |
| query_logistics | order_id | 随机生成物流进度、运单与预计送达等演示信息，带 mock 标识 |
| query_faq | keyword | 使用绑定参数的 LIKE 查 faq.question，最多返回 3 条；关键词必须来自当前用户问题的连续原文片段，不做同义词扩展 |
| create_ticket | description、ticket_type | 写 tickets 并将所属 conversations.status 设为已转人工；会话身份由应用上下文注入，不由模型指定 |

工具用 LangChain `@tool` 和 Pydantic `args_schema` 定义，限制长度、非空值、枚举及多余参数；注册表只有上述五个名称。不得把模型输出当 Python 代码、SQL 或任意函数名执行。

工具执行超时默认 5 秒；初次执行加最多一次重试。只重试可判定为临时故障的超时/连接问题，不重试未知工具、坏参数或业务未命中。取消客户端请求后不再启动新尝试。工具错误以固定、可读的结果回灌给模型，回答依据错误说明能力边界。

工单使用 `T` 加 conversation_id 与 tool_call_id 的稳定摘要生成不超过 32 字符的编号，同一次执行的重试使用同一编号。已存在编号时核对会话、类型和描述一致再返回；冲突不覆盖。写工单及更新会话状态在同一短事务内完成，无需改用户 DDL。用户重新发消息属于新的请求，不宣称支持跨请求去重。

## 6. 单轮模型调用与 SSE

1. 校验请求和会话、获取占用锁、加载完整历史、保存当前 user 消息；立即开始 SSE 状态提示。
2. 使用绑定五个工具的模型执行一次选择，要求最多一个工具；应用检查 finish_reason、tool_calls/invalid_tool_calls、工具名称、参数和 tool_call_id。
3. 没有申请则进入最终生成；有一个有效申请则保存 assistant 工具申请，推送执行状态，执行工具并保存匹配的 tool 结果。多个申请或畸形申请安全终止，不自行挑选其中一个执行。
4. 收敛阶段调用不绑定工具的模型，将合法申请与对应 ToolMessage 结果一并回灌；最终回答流式产生 delta。意外的再次工具申请视为异常，不执行。
5. 仅在正常 EOF、明确 stop、回复非空且没有截断时持久化最终 assistant 回答，数据库事务成功后发送 done。数据库写入失败返回 error，不能发送成功终止帧。
6. 断开或失败释放迭代器与占用锁；保留已经落地的用户/工具流水和工单事实，不回滚已成功创建的工单。

推荐实现每轮一次选择请求、一次最终流式请求，共最多两次模型请求；没有工具时也由第二次请求生成真实流式回答，不把一次性文本切块冒充上游流式。

SSE 保留 delta/error，done 的身份字段改为 conversation_id；增加非终止的 status 帧：selecting、tool_running、tool_completed、answering。工具相关状态包含 tool_name、tool_call_id 与成功/失败状态，不显示堆栈或配置值。仅 done/error 是终止帧。

聊天 System Prompt 更新为依据工具结果作答，订单/商品/物流结果明确作为模拟数据；FAQ 未命中时说明未查到，不编造退货政策、邮费或已执行操作。仍不执行退款等未注册业务操作，不公开模型推理内容。

## 7. 持久化与预算边界

工具申请按 Chat Completions 的结构保存到 assistant.tool_calls，纯工具申请的 content 可为空；结果以 tool 角色保存并关联 tool_call_id。消息按数据库 id 顺序加载。

不新增轮次/状态列：每个 user 消息开启一轮，随后必须是完整最终 assistant 回答，或 assistant 申请 + 匹配的 tool 结果 + 最终 assistant 回答。遇到新 user 或流水结尾时，不完整上一轮只保留为数据库流水，不用于模型历史。只有经过正常完成校验的回答才写为最终 assistant 行。

上下文按完整轮次裁剪，不能留下孤立 tool 消息；历史中的旧工具只作为背景，不代表本轮已调用。本步新增可配置 `TOOL_INPUT_TOKEN_BUDGET=8000` 供聊天链使用，预算包括 system、工具 Schema、申请、结果和消息；提取保留既有 INPUT_TOKEN_BUDGET=2000，输出上限沿用现有配置。收敛前重新核对预算，必要时只删除较旧的完整历史轮次；必需输入仍超预算则明确失败，不裁断当前申请或结果。

因数据库持久化需要异步事务，本步完成边界为“最终回答验证通过且数据库提交成功，再发送 done”。发送失败时数据库可能已保存完整回答，这不证明远端收到；这是与第一步内存提交边界的明确变更。

## 8. 验证与交付

后端按 TDD 验证：四表映射和 MySQL 真实建表结构、会话创建与重启恢复、完整调用组合裁剪、参数/注册表校验、只允许一次工具、超时与有限重试、工单重试防重复及事务状态、未知工具和坏参数、状态帧不终止、异常/取消/截断、数据库失败时不能 done。固定 MySQL 业务实现不换成其他数据库；单元测试可注入替身，数据库集成测试必须在独立 MySQL 测试库执行。

纯 Prompt 与演示数据使用标注样例验证工具选择和依据结果回答。聊天页面不走 brainstorm/TDD/code review，按用户例外直接改，并用浏览器验证徽章、流式文本、多轮、停止和错误恢复。

人工验收至少包含：

- “订单 1001 的物流到哪了”：模型申请 query_logistics，徽章显示工具，回答与模拟结果一致。
- “退货政策是什么”：query_faq 命中并根据 FAQ 作答。
- “邮费是多少”：query_faq 不命中，不把关键词改成运费，记录预期漏召回。
- 请求人工处理：create_ticket 写入关联会话的工单，会话状态为已转人工；受控重试只保留一张。
- Docker/MySQL、后端重启后，同一 conversation_id 的完整历史仍可接续。

保留第一步提取功能回归，更新演示命令和验收报告。正式验收沿用现有 glm-5.3-flash 标准端点；若 Function Calling、工具选择参数或默认输出预算走不通，记录证据并按用户要求确认，不自动换选型。

每阶段即时追记 `dev-notes/ch02.md` 的四项记录。最终交付启动/建表/种子命令、浏览器和 curl 演示、测试结果、预期漏召回记录及过程记录路径。实现计划与执行尚待本 spec 审阅。

## 9. API 资料与环境证据

Context7 查询、官方来源及本地接口签名核对记录见 [研究记录](../research/2026-10-06-tool-calling-apis.md)。用户 DDL 见 [sql/schema.sql](../../../sql/schema.sql)。

设计阶段 Docker CLI 和 Compose 可用，Docker Desktop Linux Engine 尚未运行；SQL 未执行。当前模型文档索引未找到其具体工具调用条目，需以实现阶段的兼容实测核对；本阶段真实模型请求次数为 0。
