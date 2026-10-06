# 第二步工具调用验证记录

日期：2026-10-06。当前代码验证已完成，真实模型验收尚未全部完成；不能称为八类全通过。

## 环境与实际 SQL

Python 3.13.5、uv 0.11.7；httpx 0.28.1、langchain-openai 1.6.7、langchain-core 1.6.6、openai 2.54.0、FastAPI 0.142.2、SQLAlchemy 2.0.54、aiomysql 0.3.2、uvicorn 0.54.0、pytest 9.1.1。MySQL 为 8.4.11。

使用 Compose 项目 ecs-tool-calling。应用库 127.0.0.1:3307/customer_service，独立测试库 127.0.0.1:3308/customer_service_test，两个容器均 healthy。首次初始化已经由官方入口实际执行原始 schema.sql 与 seed.sql，日志包含两文件路径和初始化完成信息；此证据来自 Task 1 实测，并在本步再次用真实 information_schema 集成测试核对。

四表仅为 conversations/messages/faq/tickets，UNSIGNED 自增主键、两个外键、中文 ENUM、JSON、索引、InnoDB/utf8mb4 与更新时间属性均在实际 MySQL 验证。代表性原生 SHOW CREATE TABLE 结果：

```sql
`status` enum('进行中','已转人工','已结束') NOT NULL DEFAULT '进行中'
`updated_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
`tool_calls` json DEFAULT NULL
CONSTRAINT `fk_messages_conversation` FOREIGN KEY (`conversation_id`) REFERENCES `conversations` (`id`)
`ticket_type` enum('售后','投诉','咨询') NOT NULL
`status` enum('待处理','已处理') NOT NULL DEFAULT '待处理'
CONSTRAINT `fk_tickets_conversation` FOREIGN KEY (`conversation_id`) REFERENCES `conversations` (`id`)
```

本步未再次初始化、清表、删卷、create_all/drop_all；git 对比确认 sql/schema.sql 未修改。保留两个 initialized 卷及之前失败初始化卷。本步只重启 mysql-test，不触及应用 mysql、旧8000或受控页面8002。

## 离线与真实 MySQL

全部 uv 命令设置 UV_CACHE_DIR=.cache/uv。沙箱 uv trampoline 无法 canonicalize，获准使用同一工作区 runtime 提权执行，没有改变依赖或技术栈。

| 命令 | 实际结果 |
| --- | --- |
| uv run pytest tests/test_tool_evaluation.py tests/test_smoke.py -q，最初 RED | 24 failed；缺 evaluator，旧 smoke 使用 session_id 且未创建会话 |
| 同命令，初次 GREEN | 24 passed in 3.63s |
| smoke 失败后停发回归 RED | 10 failed, 5 passed，仍发四次请求而非停在失败处 |
| FAQ 同义措辞回归 RED | 1 failed，正确未命中被固定措辞误判 |
| 以上修正 GREEN | 26 passed in 3.87s |
| 自审：失败最终回答保留工具审计 RED | 1 failed，缺最终 assistant 时 actual_tool 错为 null |
| 最后定向 GREEN | 27 passed in 4.11s |
| 任务7原最终 uv run pytest -q | 424 passed, 16 skipped in 22.61s；跳过项全部为未显式请求的 MySQL 集成 |
| uv run pytest tests/integration --run-mysql -q，首次 | 15 passed, 1 failed，旧种子测试假定 demo-user 无任何会话 |
| 授权修改后单项种子检查 | 1 passed in 0.77s |
| 授权修改后全部集成 | 16 passed in 2.71s |
| mysql-test 重启后全部集成 | 16 passed in 2.09s |
| git diff --check；原始 schema.sql 对比 | exit 0 |

旧种子断言与真实浏览器写入 demo-user 冲突。控制任务授权改为核对 seed-user 身份、固定种子工单号及关联；其余 schema/FAQ/消息断言保留。sql/seed.sql 的写入目标实际仍仅为 seed-user；没有删掉正常用户数据以获得绿灯。

评估还覆盖分片 UTF-8、坏 JSON、错 done 身份、多个工具、error、缺 done、正常 done、参数差异、实际 API 工具链和提交后流水。smoke 正常先创建会话再两轮聊天与一次提取；失败停止后续请求，聊天墙钟期限150秒，提取75秒，无客户端自动重试。评估结构通过与回答质量人工判断分离。

## 真实模型闸门与八类样例

当前配置始终为 glm-5.3-flash、https://open.bigmodel.cn/api/paas/v4/，max_tokens=512、聊天输入估算8000、提取2000、模型超时60秒；没有静默修改模型、端点、参数或 Prompt。独立真实后端运行在127.0.0.1:8001，单 worker，数据库3307。

先通过应用 API 跑一个物流闸门：query_logistics(order_id=A-42)，实际 ToolMessage mock=true，已揽收、MOCK19795904、4天，最终回答准确复述并说明模拟。数据库提交后正常 done。控制任务人工复核通过。

之后执行八类应用 API 评估。原始报告 .cache/task7-evaluation.json 保留不改：attempted=6、not_attempted=2，原自动通过3项。FAQ 两项因固定 answer_contains 措辞不一致判失败，而实际参数、found/matches 和回答事实正确。回归测试后改为结构验收与 answer_phrase_match 观察分开；使用既有流水只读复核，没有再请求模型，结构通过5/6项。

| 样例 | 实际工具/结果 | 状态与人工观察 |
| --- | --- | --- |
| 物流，conv3 | query_logistics(A-42)，模拟运输中，MOCK26163392，1天 | 完整 done；事实符合工具 |
| 订单，conv4 | query_order(A-42)，模拟已完成，20.58元 | 完整 done；事实正确；额外承诺可重新核实真实订单，回答质量需修正/复核 |
| 商品，conv5 | query_product(P-7)，模拟便携水杯，244.21元，库存93 | 完整 done；事实符合工具 |
| 退货 FAQ，conv6 | query_faq(退货)，found=true，2条 matches | 完整 done；根据 FAQ 作答；固定措辞未出现，人工事实复核通过 |
| 邮费 FAQ，conv7 | query_faq(邮费)，found=false，matches=[] | 完整 done；说明无法确定邮费，预期漏召回；人工事实复核通过 |
| 人工工单，conv8 | 选择响应 stop，零 tool_calls；未执行 create_ticket | API status/status/error，upstream_error；无 delta/done；数据库仅 user，未创建工单 |
| 问候 | 未尝试 | not_attempted |
| 缺订单号澄清 | 未尝试 | not_attempted |

人工工单的原始选择请求 HTTP200，finish_reason=stop、tool_calls_count=0；completion_tokens=240（其中 reasoning_tokens=149）、prompt_tokens=698。最终流式请求 HTTP200，但应用随后发 upstream_error。原始 observer 没有记录流末块元数据或安全异常类型，因此不能据此断言截断、超时、认证或具体协议原因。全部真实请求已停止；进一步同配置诊断待用户明确决定。

实际计数来自原始请求 HTTP hooks，而不是根据结构推算：

| 运行 | 应用 API HTTP | 模型请求 | 上游响应 |
| --- | --- | --- | --- |
| 物流闸门 | 2（创建+聊天） | 2（选择+最终流） | 2次200 |
| 八类轮次，实际前6项 | 12（6创建+6聊天） | 12 | 12次200 |
| 当前总计 | 14 | 14 | 14次200 |

SDK max_retries=0，客户端未添加重试。计数与脱敏 status/errorcode/选择 finish_reason 在 .cache/task7-upstream.jsonl。普通 API 评估/ smoke 客户端看不到服务端实际上游调用，所以报告 model_request_count 为 null；本表明确给出原始 observer 实测。配置声明不等同于提供方身份验证。安全记录不包含 key、密码、请求头或原始推理内容。

## 整个后端评审与最终修复

整个后端分支评审发现空白业务参数校验不足和活跃聊天未使用PromptTemplate两项问题，已通过一轮修复及一次范围复审解决，复审Approved。页面按用户Vibe Coding例外排除代码评审。

- 空白 order_id/product_id/keyword/description 在工具执行前返回 invalid_arguments、attempts=0；直接工单仓储在打开Session前拒绝空描述。保留合法原字符串，不裁切FAQ原文。
- TOOL_CHAT_SYSTEM_TEMPLATE 使用 PromptTemplate；实际渲染266字符及UTF-8 SHA256 1c28ea60def4667d18cb78d72bf494146a1996af3b8b8e13f0c51cf848384b8d 与修复前相同，四种参数JSON Schema、提取与既有Prompt保持相同。
- 新回归RED24失败，相关GREEN111 passed；实际工具仓储MySQL12 passed（原10+新增2）。修复后完整离线453 passed、18 MySQL gated skips；Controller在最终版本显式执行全部独立MySQL集成18 passed in2.48s，exit0、无pytest警告。
- 新版8001重新载入修复代码，浏览器页面可打开，GET /health返回ok；仅存活检查，未发送聊天或模型请求，原始模型计数仍14。
- 代码和数据库验证已通过；真实GLM工单错误根因、订单额外真实查询承诺、剩余真实场景仍未验收。不能把这两项代码修复称为未知GLM错误的已证明根因。
## 重启、页面与待验收部分

先以短生命周期只读仓储快照，再 docker compose -p ecs-tool-calling --profile test restart mysql-test，确认 healthy；仅关闭监听8001且命令行精确匹配本步 runtime 的自有进程，再以相同配置重启。随后新连接重新读取：

- 应用库 conv2 的4条流水、1个完整工具轮次及内容 SHA256 完全相同。
- 测试库 conv9007199254741045 的25条流水、6个完整轮次、1张待处理工单、已转人工状态完全相同。
- 快照 .cache/task7-persist-before.json / task7-persist-after.json；after unchanged=true。没有发送重启后的模型追问，这部分仅证明持久数据和完整历史仍可读取。

Task6 受控模型+真实 MySQL 浏览器证明徽章、流式显示、上下文、工单、停止/失败、新会话、窄屏及字面 HTML；它的真实模型请求为0，不能替代本步真实上游浏览器验收。

因工单项失败而停止，三个原问题的真实 curl 演示、另一次真实工单、重启后的真实模型接续、真实 smoke、第一步 extract 回归、问候/缺号样例、真实上游浏览器尚未执行。没有用替身结果补写通过。客服质量人工复核仍有订单真实查询承诺这一问题；没有修改Prompt渲染文案、种子或执行完整真实复验。任务代码评审和整个后端分支修复复审已通过；最终finish/集成仍等待真实验收完成。
