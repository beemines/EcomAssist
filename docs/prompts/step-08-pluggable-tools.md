# 第八步提示词：即插即用工具系统与 MCP

本文归档用户于2026-10-19再次提供的第八步完整提示词与建表DDL，仅整理Markdown排版。原始需求不按实现结果倒改；此前已确认的实施口径与字段对应关系单列在文末。本文是需求归档，不代表每项真实验收均在同一版本重新通过。

## 完整原始提示词

````markdown
我要用 Superpowers 模式把客服系统的工具层从几个写死的内置工具,升级成即插即用的工具系统。

## 功能需求
1. 工具注册中心:不管内置还是 MCP 来的工具,一律带齐工具名、用途描述、JSON Schema 参数定义三样,登记进同一份工具表;内置工具服务启动时登记,MCP 工具连上 Server 动态发现、现问现拿;新工具注册进来就能被主力 Agent 用上,不改核心代码、不重启服务
2. 参数校验:工具执行前统一按 JSON Schema 校验一遍,类型不对、必填缺失、取值越界的拦下;拦下不抛异常了事,把校验错误说明包成一条工具结果回灌给模型,让它追问用户或重新组织调用
3. 权限控制:工具分只读、写两类,写操作由执行引擎把门;本系统的写操作就 create_ticket 一个,规矩是——只有客户明确要求建工单时才发起,真正执行还要等第 7 点的前端确认回来,没确认的调用引擎直接拒绝,不给模型绕过去的机会;外部 MCP 工具的用途声明是对方自己写的、不可信,能不能调(尤其写操作)只认我们这侧的权限规则,不看 Server 声明、不让模型临场判断
4. 执行引擎:所有工具调用走同一处,统一管超时、重试、错误处理、结果格式化;重试只给网络抖动这类暂时性故障,业务空结果不重试,写操作默认不自动重试(超时未必没执行,重复执行比失败更糟);错误按参数不合法、查询落空、真故障三类分诊,坏消息如实回给模型;结果只挑回答用得上的字段、内部枚举码翻成人话、序列化 JSON 中文不转义
5. 审计留痕:建 tool_audit_logs 表,每次工具调用落一条——所属会话、tool_call_id、工具名、来源是内置还是哪个 MCP Server、调用参数、结果摘要、状态(成功/失败/超时/校验拦下/权限拒绝)、错误说明、重试次数、耗时、时间;被权限拒、被校验拦的调用同样要落;审计表不挂外键,写审计失败不许反过来拦工具执行
6. MCP 接入:自建两个业务 MCP Server——物流(查物流轨迹)、售后(查在保、查退货进度),各自独立进程,Server 内部照第二步工具的做法随机生成 mock 数据返回,不接真实系统、不建表;客服系统作为 MCP Client 接入,拿回的工具跟内置清单合成一份,主力 Agent 一视同仁地调;物流查询由物流 MCP Server 接管,第二步内置的 query_logistics 从清单里下线,别留重名工具
7. 建工单确认流(带前端配套):客户明确要求建工单才走这条流,Agent 先核对信息够不够,缺问题描述这类必填项就主动追问用户,不许瞎编;凑齐后发起 create_ticket,执行引擎不直接执行,照第六步订单选择器的做法用 LangGraph interrupt 把工单预览(工单类型、问题描述)推给前端;前端渲染成预览卡片,带「确认提交」「取消」两个按钮:点确认,回传后端 resume 放行,落 tickets 表,回复里把工单号带给用户;点取消,不执行,这次调用按「权限拒绝」落审计;第五步投诉流程里前端按钮建单那条路保持不动,点按钮本身就是用户确认

## 技术栈
- MCP Server:用 MCP 官方 Python SDK 自建,走 Streamable HTTP 传输
- MCP Client:用 LangChain 官方 langchain-mcp-adapters 的 MultiServerMCPClient 多 Server 接入

## 本步骤不做
- Skill 机制(只是生态概念,不落代码)
- 仓储这类更多外部系统不接,两个业务 MCP 足够撑起本步骤

## 验收标准
1. 新写一个简单工具,只做注册动作、不动核心代码,Agent 就能在对话里用上它
2. 两个 MCP Server 单独起进程,问物流轨迹,Agent 都通过 MCP 查到数据并回答
3. 在 MCP Server 侧新加一个工具、只重启该 Server,客服系统这边代码不动、服务不重启,再问对应问题 Agent 就能用上新工具
4. 聊天里明确说「帮我建个工单」但没讲清楚问题,Agent 先追问补齐;然后聊天页出现工单预览卡片,点「确认提交」,tickets 表落一条新工单,回复里带着工单号
5. 同样走到工单预览,这回点「取消」,工单没建,tool_audit_logs 里这条 create_ticket 状态是「权限拒绝」
6. 人为让一个工具超时,能看到重试和错误兜底,tool_audit_logs 里这次调用的重试次数、超时状态、耗时都齐;再人为让一个写操作超时,确认它没被自动重试(审计里重试次数为 0)

## 工作要求
1. 全程走 Superpowers 流程,技能自动触发;产出不是可单测代码的任务(纯 Prompt、数据类),把 TDD 那步换成拿标注样例或评估集跑一遍验证,其余步骤照走;工单预览卡片这类前端部分是例外,用 Vibe Coding 方式直接做,我描述效果你改,不套 brainstorm、TDD、code review 那套流程
2. 过程留痕:在仓库 dev-notes/ch08.md 里追记开发过程,每完成一个阶段(brainstorm 定稿、计划评审通过、每个任务完成、code review 结论、finish)就补一段,记四样:我这一步发的关键原话、你的关键产出(spec / plan 路径、评审结论)、我拒绝或纠偏了什么、翻车与返工;不许收尾时一次性补记
3. 涉及具体库、框架、API 的用法(FastAPI、SQLAlchemy、LangChain、LangGraph、Milvus、Langfuse 这些),一律先用 Context7 MCP 查最新官方文档和接口定义再动手,别凭记忆写,版本对不上的 API 是返工重灾区
4. 上面点名的技术选型是定死的,实现中发现矛盾或走不通,停下来问我,不要自行换方案
5. 完结交付:功能演示命令、测试结果、dev-notes 路径
````

## 用户提供的建表 DDL

以下原样保留为本次提示词附件；不是自动执行的迁移脚本。当前实现的显式迁移文件为[sql/ch08-tool-audit.sql](../../sql/ch08-tool-audit.sql)，字段差异见后文。

```sql
-- =============================================================
-- step08 · 工具系统 · 建表 DDL
-- 本步骤新建:tool_audit_logs(工具调用审计留痕,统一执行引擎每次调用落一条)
-- 不挂外键:审计写入不能被引用约束拦住,conversation_id 只建普通索引
-- 全库统一 ENGINE=InnoDB、CHARSET=utf8mb4
-- =============================================================

-- 确保中文 ENUM 定义值/DEFAULT/COMMENT 按 utf8mb4 解析
-- (否则 latin1 默认的 mysql client 会把中文 double-encode,ENUM 值存成乱码)
SET NAMES utf8mb4;

-- 工具调用审计:内置和 MCP 工具都记,被权限拒、被校验拦的调用同样落一条
CREATE TABLE tool_audit_logs (
  id              BIGINT UNSIGNED NOT NULL AUTO_INCREMENT COMMENT '审计主键',
  conversation_id BIGINT UNSIGNED NULL                    COMMENT '所属会话,无会话上下文的调用为 NULL',
  tool_call_id    VARCHAR(64)     NULL                    COMMENT '模型申请单 id,可对回 messages 流水',
  tool_name       VARCHAR(128)    NOT NULL                COMMENT '工具名',
  tool_source     ENUM('builtin','mcp') NOT NULL          COMMENT '工具来源:内置 / MCP 接入',
  mcp_server      VARCHAR(64)     NULL                    COMMENT '来源 MCP Server 名,内置工具为 NULL',
  arguments       JSON            NULL                    COMMENT '调用参数',
  result_summary  TEXT            NULL                    COMMENT '返回结果,过长截断存摘要',
  status          ENUM('成功','失败','超时','校验拦下','权限拒绝') NOT NULL COMMENT '本次调用结局',
  error_message   VARCHAR(512)    NULL                    COMMENT '失败 / 拦下时的原因说明',
  retry_count     TINYINT UNSIGNED NOT NULL DEFAULT 0     COMMENT '实际重试次数,写操作默认不重试恒为 0',
  duration_ms     INT UNSIGNED    NULL                    COMMENT '耗时毫秒',
  created_at      DATETIME        NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '调用时间',
  PRIMARY KEY (id),
  KEY idx_conversation_id (conversation_id),
  KEY idx_tool_name (tool_name),
  KEY idx_status (status)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='工具调用审计留痕';
```

## 此前已确认的实施口径

- 当前会话没有可调用的Context7 MCP；用户已明确允许本步骤使用官方文档和锁定版本源码核对，技术栈保持不变。
- 用户选择锁定`mcp==1.30.0`与`langchain-mcp-adapters==0.3.2`，避免官方SDK主版本与适配器约束冲突。
- 用户选择本地逐工具授权、策略热加载。新工具被发现后，还需在本地策略登记来源、名称与读写规则；不采信外部Server自报权限，不需要更改Agent核心或重启客服。
- 用户批准[正式设计](../superpowers/specs/2026-10-18-pluggable-tools-design.md)及[实施计划](../superpowers/plans/2026-10-18-pluggable-tools.md)，选择Native本会话顺序实现；前端保留Vibe Coding例外。
- 过程、失败与分批验证边界保留在[dev-notes/ch08.md](../../dev-notes/ch08.md)，不以需求归档代替真实验收结果。

## 本次原始 DDL 与已批准实现的差异

已批准设计的第7节及现有迁移采用以下存储契约，本次归档不执行重建或改名：

| 本次原始DDL | 已有实现 |
| --- | --- |
| `tool_source`和`mcp_server`两列 | `source`一列，值为`builtin`、`mcp:logistics`、`mcp:aftersales`等 |
| 中文`status`枚举 | `success`、`failed`、`timeout`、`validation_blocked`、`permission_denied`，分别对应成功、失败、超时、校验拦下、权限拒绝 |
| `duration_ms` | `elapsed_ms`，同样记录总耗时毫秒 |
| 可空`tool_call_id`、参数、结果和耗时 | 当前实现非空；`conversation_id`仍可空，另有`error_code`细分原因 |
| `tool_name VARCHAR(128)`、`retry_count TINYINT`、`duration_ms INT` | 当前分别为`VARCHAR(64)`、`INT UNSIGNED`、`BIGINT UNSIGNED` |
| 会话、工具名、状态普通索引 | 当前为会话/时间复合索引与tool_call_id普通索引；同样无外键 |

若后续要求数据库物理结构逐列采用本次DDL，应另做有数据兼容的迁移，不能在已存在的`tool_audit_logs`上再次直接执行上述CREATE TABLE。
