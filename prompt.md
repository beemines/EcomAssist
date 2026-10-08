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

# 第三步

## 使用插件

- Superpowers
- Context7

## 开发提示词

```markdown
我要用 Superpowers 模式给客服系统建知识库,把 query_faq 的内部实现从关键词查表升级成向量语义检索,工具的入参出参契约保持不变。

## 功能需求
1. 离线建库·文档处理:知识文档(退货政策、商品 FAQ、售后手册这类 Markdown)按标题层级做结构感知切分;超长内容递归切;块间加重叠且裁到最近句号,不留半截话;大表格按行切时每块都复制表头
2. 离线建库·对话挖知识:做一条从历史客服对话挖知识的定时任务,分批喂给 LLM 抽取问答对,先进暂存表、再整体去重入库
3. 落库结构:每条知识带 category、questions、answer 三个字段,拼成一段文本做向量化;商品 FAQ 和挖出来的问答对,questions 填真实问法;政策手册这类没有天然问题的,questions 填所在章节标题、category 填上级标题路径;另带章节路径、内容类型、是否关键条款、前后块指针四类元数据,只存不进向量
4. 双写落库:MySQL 建 knowledge_chunks 表当原文权威源、Milvus 建 knowledge 集合;先写 MySQL 记「待向量化」,再写 Milvus 拿 vector_id 回填、状态转「已向量化」;按主键幂等,挂了能重跑
5. 在线检索:问题向量化后到 Milvus 按相似度取 Top-K,替换掉 query_faq 的关键词查表实现

## 技术栈
- 嵌入模型 BGE-M3
- 向量库 Milvus,MySQL 当原文权威源

## 本章不做
- 关键词召回、混合检索、重排,本章只跑 dense 向量单路

## 验收标准
1. 「邮费是多少」这类换说法的问题,现在能召回运费说明并答对
2. 故意中断建库任务再重跑,漏向量化的块能被捡起补齐

## 工作要求
1. 全程走 Superpowers 流程,技能自动触发;产出不是可单测代码的任务(纯 Prompt、数据类),把 TDD 那步换成拿标注样例或评估集跑一遍验证,其余步骤照走
2. 过程留痕:在仓库 dev-notes/ch03.md 里追记开发过程,每完成一个阶段(brainstorm 定稿、计划评审通过、每个任务完成、code review 结论、finish)就补一段,记四样:我这一步发的关键原话、你的关键产出(spec / plan 路径、评审结论)、我拒绝或纠偏了什么、翻车与返工;不许收尾时一次性补记
3. 涉及具体库、框架、API 的用法(FastAPI、SQLAlchemy、LangChain、LangGraph、Milvus、Langfuse 这些),一律先用 Context7 MCP 查最新官方文档和接口定义再动手,别凭记忆写,版本对不上的 API 是返工重灾区
4. 上面点名的技术选型是定死的,实现中发现矛盾或走不通,停下来问我,不要自行换方案
5. 完结交付:功能演示命令、测试结果、dev-notes 路径
```

## 建表 SQL

```sql
-- =============================================================
-- ch03 · RAG 基础 · 建表 DDL
-- 本章新建:knowledge_chunks(知识库原文权威源)
-- 向量落 Milvus 集合 knowledge(非 MySQL,DDL 不含);MySQL 存原文 + 双写状态
-- category + questions + answer 三格拼成向量化文本;其余字段是元数据,只存不进向量
-- =============================================================

-- 确保中文 COMMENT 按 utf8mb4 解析(latin1 默认的 mysql client 会把中文 double-encode)
SET NAMES utf8mb4;

CREATE TABLE knowledge_chunks (
  id               BIGINT UNSIGNED NOT NULL AUTO_INCREMENT COMMENT 'chunk 主键,与 Milvus 集合主键对齐',
  category         VARCHAR(255)    NOT NULL                COMMENT '分类 / 上级标题路径,进向量化文本',
  questions        TEXT            NOT NULL                COMMENT '问法或本节标题,多个问法换行分隔,进向量化文本',
  answer           TEXT            NOT NULL                COMMENT '正文答案,进向量化文本',
  section_path     VARCHAR(512)    NULL                    COMMENT '章节路径,元数据,溯源用,不进向量',
  content_type     VARCHAR(32)     NULL                    COMMENT '内容类型:faq / policy / manual 等,元数据',
  is_key_clause    TINYINT(1)      NOT NULL DEFAULT 0      COMMENT '是否关键条款,0 否 1 是,元数据',
  prev_chunk_id    BIGINT UNSIGNED NULL                    COMMENT '前一块指针,元数据',
  next_chunk_id    BIGINT UNSIGNED NULL                    COMMENT '后一块指针,元数据',
  vector_id        VARCHAR(64)     NULL                    COMMENT 'Milvus 集合 knowledge 里的主键,写入后回填',
  vectorize_status ENUM('pending','done') NOT NULL DEFAULT 'pending' COMMENT '待向量化 / 已向量化,双写幂等靠它',
  created_at       DATETIME        NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  updated_at       DATETIME        NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
  PRIMARY KEY (id),
  KEY idx_category (category),
  KEY idx_vectorize_status (vectorize_status),
  CONSTRAINT fk_chunks_prev FOREIGN KEY (prev_chunk_id) REFERENCES knowledge_chunks (id) ON DELETE SET NULL,
  CONSTRAINT fk_chunks_next FOREIGN KEY (next_chunk_id) REFERENCES knowledge_chunks (id) ON DELETE SET NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='知识库 chunk 原文权威源';

CREATE TABLE qa_extraction_staging (
  id               BIGINT UNSIGNED NOT NULL AUTO_INCREMENT COMMENT '暂存行主键',
  batch_no         VARCHAR(64)     NOT NULL                COMMENT '抽取批次号,一批几十个会话跑一次,分批防串味、按批追溯',
  source_ref       VARCHAR(255)    NULL                    COMMENT '来源会话 / 导出文件标识,溯源用,不入最终知识库',
  question         TEXT            NOT NULL                COMMENT 'LLM 从会话抽出的用户问法',
  answer           TEXT            NOT NULL                COMMENT 'LLM 从会话抽出的客服答案',
  status           ENUM('extracted','kept','discarded') NOT NULL DEFAULT 'extracted' COMMENT '已抽出待去重 / 去重保留 / 去重丢弃',
  created_at       DATETIME        NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '抽取写入时间',
  PRIMARY KEY (id),
  KEY idx_batch_no (batch_no),
  KEY idx_status (status)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='历史对话抽 QA 的离线中转暂存表:分批抽取、整体去重,保留项入 knowledge_chunks,建库完成可清空';
```

## 第四步：混合检索、重排与评估

使用插件：Superpowers、Context7。

```Markdown
我要用 Superpowers 模式把客服系统的检索质量做上一个台阶:混合检索加重排,再配一套评估体系。

## 功能需求
1. 混合检索:关键词召回这条路也落在 Milvus 上,用它 2.5 版起原生的 BM25 全文检索,text 字段挂 BM25 函数,中文分词用内置 chinese analyzer;检索时 dense 向量和 BM25 各召回 Top-50,用 hybrid_search 配 RRF 融合
2. 重排:用 bge-reranker-v2-m3 精排出 Top-10;组装进 prompt 时把最相关的放首尾,别按分数顺序堆中间
3. 元数据过滤:支持按品类这类字段先过滤再检索
4. Query 理解:口语模糊问法改写归一成标准问法;同义词扩展只在检索侧做,不在入库侧拆存多份
5. 生成质量控制:
   - 回答带引用编号,编号能映射回来源 chunk 的章节路径、跳回原文
   - 检索不到或证据置信度低就显式拒答,不硬编答案
   - 生成阶段让模型自评召回的知识够不够答这个问题,不够则拒答,并把问题落进低置信度问题池(建 low_confidence_questions 表:原话、来源会话、入池入口、判不能的原因、时间)
   - System Prompt 列明禁止承诺的负面知识,比如不承诺到账时间
6. 评估体系:造一份带难度梯度、标注 ground-truth 的评估集;检索段评 Recall@K、MRR,生成段评 Faithfulness;跑纯向量、纯 BM25、混合、混合加 Rerank 四种策略的对比,按 query 类型分桶出报告
7. 前端配套:在现有聊天页上把回答里的引用编号做成可点的,点开能看到来源 chunk 的原文和章节路径;再给每段回答的左下角挂一组满意度反馈(👍/👎),用户点一下就点亮所选、显示「已反馈」并一次性锁定——这条信号先做纯前端采集,为后面的数据飞轮留个入口

## 技术栈
- Milvus 原生 BM25 + hybrid_search RRF 融合
- 重排模型 bge-reranker-v2-m3

## 本章不做
- 指代消解、多轮改写

## 验收标准
1. 四策略对比报告能跑出数字
2. 问带具体型号的问题,BM25 那路能命中
3. 答案引用编号能定位回原文,聊天页上点引用能看到来源原文
4. 问知识库没有的内容,得到明确拒答,且问题进了低置信度池

## 工作要求
1. 全程走 Superpowers 流程,技能自动触发;产出不是可单测代码的任务(纯 Prompt、数据类),把 TDD 那步换成拿标注样例或评估集跑一遍验证,其余步骤照走;前端部分是例外,用 Vibe Coding 方式直接做,我描述效果你改,不套 brainstorm、TDD、code review 那套流程
2. 过程留痕:在仓库 dev-notes/ch04.md 里追记开发过程,每完成一个阶段(brainstorm 定稿、计划评审通过、每个任务完成、code review 结论、finish)就补一段,记四样:我这一步发的关键原话、你的关键产出(spec / plan 路径、评审结论)、我拒绝或纠偏了什么、翻车与返工;不许收尾时一次性补记
3. 涉及具体库、框架、API 的用法(FastAPI、SQLAlchemy、LangChain、LangGraph、Milvus、Langfuse 这些),一律先用 Context7 MCP 查最新官方文档和接口定义再动手,别凭记忆写,版本对不上的 API 是返工重灾区
4. 上面点名的技术选型是定死的,实现中发现矛盾或走不通,停下来问我,不要自行换方案
5. 完结交付:功能演示命令、测试结果、dev-notes 路径
```

```SQL
-- =============================================================
-- ch04 · RAG 进阶 · 建表 DDL
-- 本章新建:low_confidence_questions(低置信度问题池)、faith_cases(编造个案台账)
-- 生成阶段模型自评知识不够答就拒答,把原话落进这张池子,是 ch09 数据飞轮的入口
-- 本章只靠 useful 自评判入池(useful=false 才入,不单独存该字段);ch09 会给这张表 ALTER 加归并字段
-- =============================================================

-- 确保中文 ENUM 定义值/DEFAULT/COMMENT 按 utf8mb4 解析
-- (否则 latin1 默认的 mysql client 会把中文 double-encode,ENUM 值存成乱码)
SET NAMES utf8mb4;

CREATE TABLE low_confidence_questions (
  id              BIGINT UNSIGNED NOT NULL AUTO_INCREMENT COMMENT '主键',
  conversation_id BIGINT UNSIGNED NULL                    COMMENT '来源会话',
  raw_question    TEXT            NOT NULL                COMMENT '用户原话,带情绪口语',
  source          ENUM('retrieval_low_conf','self_check','user_feedback') NOT NULL COMMENT '入池入口:检索证据低 / 生成自评不足 / 用户反馈未解决',
  reason          TEXT            NULL                    COMMENT '判不能的原因,留作复盘',
  created_at      DATETIME        NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '入池时间',
  PRIMARY KEY (id),
  KEY idx_source (source),
  KEY idx_created_at (created_at),
  CONSTRAINT fk_lcq_conversation FOREIGN KEY (conversation_id) REFERENCES conversations (id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='低置信度问题池';

-- ch04 编造个案台账:忠实度裁判判出的每条编造,不只留在这一轮的报告里,进表长期管理。
--
-- 为什么要一张表:报告是产物,重跑一次就被覆盖,上一轮判出的个案连带它的处置状态一起没了。
-- 而这些个案的价值恰恰在跨轮追溯——同一道题反复被判编造,说明库里那一格一直没补对。
--
-- 一题一行(uk_eval_id):同一道题再次被判编造不新增行,只把答案/理由/角标快照更新成最近一次、
-- seen_count 加一。已经标「已解决」的题又被判出来,状态自动退回「未解决」——那是复发,
-- 不是新问题,得让它重新出现在待处理列表里。
--
-- citations 存的是这一轮喂给模型的 Top-K 证据**全集**(答案里的角标 [n] 就是这份列表的序号)。
-- 裁判说「证据里没有」,追溯时必须能当场看到当时喂进去的到底是什么,不能只留一句结论;
-- 而且要看得出「手里有哪几条、实际只引了哪几条」——没被引用的那些同样是判断依据。
CREATE TABLE faith_cases (
  id            BIGINT UNSIGNED NOT NULL AUTO_INCREMENT COMMENT '主键',
  eval_id       VARCHAR(16)     NOT NULL                COMMENT '评估集题号,如 A43;一题一行',
  bucket        VARCHAR(24)     NOT NULL                COMMENT '题目所属桶:A_policy / B_model / C_colloquial / E_multi',
  query         VARCHAR(512)    NOT NULL                COMMENT '用户问题原文',
  strategy      VARCHAR(24)     NOT NULL DEFAULT 'hybrid_rerank' COMMENT '产出这条答案的检索策略',
  answer        TEXT            NOT NULL                COMMENT '被判编造的那版生成答案原文',
  reason        TEXT            NOT NULL                COMMENT '裁判给的理由:编在哪一句',
  citations     JSON            NULL                    COMMENT '这一轮喂给模型的 Top-K 证据全集快照:[{n,chunk_id,section_path,question,answer}];答案里的角标 [n] 就是这份列表的序号,答案通常只引用其中两三条;老数据没记为 NULL',
  judge_model   VARCHAR(64)     NULL                    COMMENT '判这条的裁判模型',
  status        ENUM('未解决','已解决','无需解决') NOT NULL DEFAULT '未解决' COMMENT '处置状态,人工点按钮改',
  seen_count    INT UNSIGNED    NOT NULL DEFAULT 1      COMMENT '被判编造的累计次数(跨轮)',
  first_seen_at DATETIME        NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '第一次被判编造的时间',
  last_seen_at  DATETIME        NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '最近一次被判编造的时间',
  resolution    VARCHAR(300)    NULL                    COMMENT '处置说明:标已解决要写清怎么解决的,标无需解决要写清为什么不用改;退回未解决时清空。空着的处置在台账上等于没有交代',
  resolved_at   DATETIME        NULL                    COMMENT '最近一次被标为已解决/无需解决的时间;复发后仍保留,用来标「复发」',
  PRIMARY KEY (id),
  UNIQUE KEY uk_eval_id (eval_id),
  KEY idx_status (status),
  KEY idx_last_seen_at (last_seen_at)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='ch04 忠实度编造个案台账';
```
