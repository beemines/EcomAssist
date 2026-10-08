# 第一步

## 使用插件

- Superpowers
- Context7

## 后端提示词

```markdown
我要用 Superpowers 模式做一个电商智能客服系统,第一步先跑通纯对话。

## 功能需求
1. 对话接口:支持多轮对话,SSE 流式输出、逐 token 推送
2. Prompt 管理:用 PromptTemplate 模板化,System Prompt 写清客服角色设定和行为约束
3. 结构化输出小功能:把用户的售后描述提取成订单号、诉求类型、期望方案这样的固定字段,用 with_structured_output 实现
4. 多轮上下文先做最简版:历史消息裁剪加 token 预算控制

## 技术栈
- Python + FastAPI + LangChain
- 模型接入直连上游,应用侧统一说 OpenAI 协议,地址、模型名、密钥全在 .env,GPT、Claude、DeepSeek、Ollama 都能换着接

## 本章不做
- 工具调用、Agent 循环,先跑通纯对话

## 验收标准
1. curl 调对话接口能看到流式回复
2. 连续问两轮,第二轮能接住第一轮的上下文
3. 发一段售后描述,能拿到结构化 JSON

## 工作要求
1. 全程走 Superpowers 流程,技能自动触发;产出不是可单测代码的任务(纯 Prompt、数据类),把 TDD 那步换成拿标注样例或评估集跑一遍验证,其余步骤照走;聊天页面是例外,用 Vibe Coding 方式直接做,我描述效果你改,不套 brainstorm、TDD、code review 那套流程
2. 过程留痕:在仓库 dev-notes/ch01.md 里追记开发过程,每完成一个阶段(brainstorm 定稿、计划评审通过、每个任务完成、code review 结论、finish)就补一段,记四样:我这一步发的关键原话、你的关键产出(spec / plan 路径、评审结论)、我拒绝或纠偏了什么、翻车与返工;不许收尾时一次性补记
3. 涉及具体库、框架、API 的用法(FastAPI、SQLAlchemy、LangChain、LangGraph、Milvus、Langfuse 这些),一律先用 Context7 MCP 查最新官方文档和接口定义再动手,别凭记忆写,版本对不上的 API 是返工重灾区
4. 上面点名的技术选型是定死的,实现中发现矛盾或走不通,停下来问我,不要自行换方案
5. 完结交付:功能演示命令、测试结果、dev-notes 路径
```

## 聊天页面提示词

```text
聊天页面:一个客服对话 Web 界面,消息气泡排布,对接 SSE 接口把回复逐字渲染出来,能连续多轮聊
浏览器打开聊天页,发一个问题能看到回复逐字蹦出来,接着追问一句上下文也接得住
```

# 第二步

## 使用插件

- Superpowers
- Context7

## 开发提示词

```markdown
我要用 Superpowers 模式给现有的客服系统装上查数据的能力,用 Function Calling 让模型自己决定调什么工具——工具链要长在客服聊天本身,用户在聊天页问一句就能触发。

## 功能需求
1. 项目基建搭正式:FastAPI 加 SQLAlchemy 的分层骨架;Docker 起 MySQL;建四张表灌测试数据——faq(问题、答案、分类)、conversations(会话壳:用户、处理状态、创建时间)、messages(消息流水:会话 id、role 取 user/assistant/tool、内容、工具调用申请与 tool_call_id、创建时间)、tickets(工单号主键、关联会话、问题描述、工单类型、处理状态、创建时间)
2. 用 LangChain 的 @tool 装饰器定义五个业务工具:
   - query_order 查订单、query_product 查商品、query_logistics 查物流:这三个真实场景该调公司电商系统和物流系统的 API,演示起见在工具内部随机生成数据返回,不接真实接口、不建表
   - query_faq 查常见问题:用 SQL LIKE 关键词查 faq 表
   - create_ticket 创建人工工单:写入 tickets 表
3. 工具基础设施:注册管理、参数 Schema 校验、执行错误处理、超时重试,工具结果回灌给模型组织回答
4. 工具链接进现有客服聊天入口:那个 SSE 流式聊天页,用户问一句后端就走「模型定工具 → 执行 → 回灌收敛」;最终回答仍逐 token 流式吐出,工具执行那一段先推个状态帧;聊天记录(含工具调用与结果)落 conversations/messages 表;聊天页在气泡里显示这轮调了哪个工具(工具轨迹小徽章)
5. 只做单轮调用:模型调一次工具就收敛

## 技术栈
- FastAPI + SQLAlchemy + MySQL(Docker 起)
- LangChain @tool 装饰器

## 本章不做
- 多轮自动循环的 Agent Loop
- 向量检索、RAG

## 验收标准
1. 浏览器打开聊天页,问「订单 1001 的物流到哪了」,能看到模型选中工具(气泡带工具徽章)并按返回结果作答
2. 问「退货政策是什么」,query_faq 查得到并作答
3. 换个说法问「邮费是多少」,确认关键词查表查不出来——这个漏召回是预期结果,记下来留给下一步升级

## 工作要求
1. 全程走 Superpowers 流程,技能自动触发;产出不是可单测代码的任务(纯 Prompt、数据类),把 TDD 那步换成拿标注样例或评估集跑一遍验证,其余步骤照走;聊天页改造是例外,用 Vibe Coding 方式直接做,我描述效果你改,不套 brainstorm、TDD、code review 那套流程
2. 过程留痕:在仓库 dev-notes/ch02.md 里追记开发过程,每完成一个阶段…(不变)
3. Context7 查最新库/API 文档再动手…(不变)
4. 技术选型定死,走不通停下问我…(不变)
5. 完结交付:功能演示命令、测试结果、dev-notes 路径
```

## 建表 SQL

```sql
-- =============================================================
-- ch02 · Function Calling 工具链 · 建表 DDL
-- 本章新建:faq / conversations / messages / tickets 四张表
-- 商品、订单、物流走工具内 mock,不建表
-- 全库统一 ENGINE=InnoDB、CHARSET=utf8mb4
-- 建表顺序:先 conversations,再依赖它的 messages / tickets
-- =============================================================

-- 会话壳:一通对话的统一身份,messages / tickets 都引用它
CREATE TABLE conversations (
  id          BIGINT UNSIGNED NOT NULL AUTO_INCREMENT COMMENT '会话主键',
  user_id     VARCHAR(64)     NOT NULL                COMMENT '用户标识',
  status      ENUM('进行中','已转人工','已结束') NOT NULL DEFAULT '进行中' COMMENT '处理状态',
  created_at  DATETIME        NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '开启时间',
  updated_at  DATETIME        NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
  PRIMARY KEY (id),
  KEY idx_user_id (user_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='客服会话';

-- 消息流水:一通会话底下挂 N 条,role 对齐 Chat Completions 协议
CREATE TABLE messages (
  id              BIGINT UNSIGNED NOT NULL AUTO_INCREMENT COMMENT '消息主键',
  conversation_id BIGINT UNSIGNED NOT NULL                COMMENT '所属会话',
  role            ENUM('user','assistant','tool') NOT NULL COMMENT '角色:用户/助手/工具结果',
  content         TEXT            NULL                     COMMENT '消息正文,assistant 纯工具调用时可为空',
  tool_calls      JSON            NULL                     COMMENT 'assistant 消息带的工具调用申请单',
  tool_call_id    VARCHAR(64)     NULL                     COMMENT 'tool 消息对应的申请单 id,回灌时对号入座',
  created_at      DATETIME        NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '产生时间',
  PRIMARY KEY (id),
  KEY idx_conversation_id (conversation_id),
  CONSTRAINT fk_messages_conversation FOREIGN KEY (conversation_id) REFERENCES conversations (id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='会话消息流水';

-- FAQ 问答对:query_faq 的数据源;ch03 起检索改走向量库,这张表退居原始录入
CREATE TABLE faq (
  id          BIGINT UNSIGNED NOT NULL AUTO_INCREMENT COMMENT 'FAQ 主键',
  question    VARCHAR(512)    NOT NULL                COMMENT '问题',
  answer      TEXT            NOT NULL                COMMENT '答案',
  category    VARCHAR(64)     NOT NULL                COMMENT '分类',
  created_at  DATETIME        NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  updated_at  DATETIME        NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
  PRIMARY KEY (id),
  KEY idx_category (category)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='常见问答';

-- 人工工单:create_ticket 落地,工单号当业务主键
CREATE TABLE tickets (
  ticket_no       VARCHAR(32)     NOT NULL                COMMENT '工单号,如 T20260701008',
  conversation_id BIGINT UNSIGNED NOT NULL                COMMENT '关联会话,可倒查当时聊了什么',
  description     TEXT            NOT NULL                COMMENT '问题描述',
  ticket_type     ENUM('售后','投诉','咨询') NOT NULL     COMMENT '工单类型',
  status          ENUM('待处理','已处理') NOT NULL DEFAULT '待处理' COMMENT '处理状态',
  created_at      DATETIME        NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  PRIMARY KEY (ticket_no),
  KEY idx_conversation_id (conversation_id),
  CONSTRAINT fk_tickets_conversation FOREIGN KEY (conversation_id) REFERENCES conversations (id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='人工工单';
```
