# 第七步提示词：会话上下文管理

本文归档用户提供的第七步完整提示词和两段建表 DDL，仅整理 Markdown 排版。原始要求不按实现结果倒改；后续明确确认的调整单独列在文末。本文是需求归档，不代表全部真实验收已通过。

## 完整原始提示词

````markdown
我要用 Superpowers 模式让客服在一通会话里记得住前面聊过什么，把第一版的简单裁剪升级成正经的上下文管理。只管当前会话，不跨会话、不存用户画像。

## 功能需求

1. 三层结构：按离当前这一轮的远近把历史切成三段。最近的留原文，一个字都不压；中间一层按规则截短，用户原话不动、客服答复只留开头几十个字、大块工具结果换成一行标识；最远的异步压成一段段梗概。两个锚点划边界，summary_upto_msg_id 标出摘要覆盖到哪条，layer1_from_msg_id 标出层 1 从哪条起，降级只挪这两个 id、不搬数据。梗概单开一张会话摘要表，不塞进逐条消息里。
2. 摘要走后台异步：中间那层攒到超预算就在后台起一次摘要任务，把这一批压成新的一段追加进摘要表，边界追到层 1 起点，全程不阻塞用户当前这轮回复。梗概一段段攒、压完不回头重写，旧梗概只作背景给模型看、不参与合并，免得同一个事实被反复有损压缩。触发看用量不数条数，工具结果压根不落消息表，数条数看不见它涨。摘要提示词只提炼事实与诉求（问过哪款商品、报过的订单号手机号、明确诉求、还没解决的问题），对话里没出现的内容一个字不许编，寒暄闲聊不留，长度控制在几十到一两百字。
3. 调模型的上下文按固定顺序拼装：system 人设、红线和工具定义打头，这一段每轮都一样；接中间那层截短过的对话，再接最近几轮原文，然后是用户当前这句话；早期梗概和检索证据合成一条挂在用户这句之后。梗概不许单独占一条 system，上游模板会把所有 system 上提合并渲染，工具定义被挤到可变内容之后，前缀缓存整段作废。
4. token 预算从模型窗口倒推，不写死成常量：扣掉系统提示、检索证据、注入梗概、输出预留和安全余量这些固定开销，再扣掉当前这一轮 ReAct 的瞬时峰值，剩下的才归历史；历史预算取「想留住的轮数 × 每轮稳态占用」和「窗口实际匀得出来的」两个数里小的那个，层 1 拿七成、层 2 拿三成。启动时自检一遍，连一轮都装不下就报警。中文按字数折 token 的口径要和预算一起校准，只改一个净效果是反的。
5. 对话历史落在 conversations 和 messages 两张表里，会话上下文随 LangGraph 的 State 一路贯穿：State 的 messages 字段挂 add_messages reducer，各节点只管吐新消息、框架自动按顺序并入；State 里的完整历史靠 checkpoint 落盘留着，调模型前另外整理一份裁过、带摘要的精简版递进去，完整历史和精简版各走各的、互不影响。
6. 上下文可观测：每轮调模型前，把实际发出的上下文原样打进 log/app.log——主力 Agent 打 model_ctx（摘要全文 + 滑窗逐条消息 + 窗口条数 + tokens 估算），指代消解/意图识别共用的历史打 history_ctx（摘要行 + 滑窗，每轮必打，不进 Agent 的闲聊兜底轮也看得到）；后台摘要任务的触发/开始/完成/跳过/失败全留痕，带覆盖边界和耗时。
7. 前端多会话页面：聊天页加会话侧栏，列出该用户全部会话（新在前、首问预览、已摘要标记），点击切换并回载历史原文继续聊；「新对话」只是开新会话，旧会话仍在侧栏可切回；后端配两个只读接口（GET /api/conversations、GET /api/conversations/{id}/messages），侧栏加载失败静默降级不影响聊天。

## 技术栈

- LangGraph State（add_messages reducer + checkpoint）+ LangChain trim_messages + MySQL（conversations / messages 表）

## 本步骤不做

- 语义检索捞历史、主题重要度留关键事实这两层不实现（理论篇讲的三种选法里，本课量级滑窗打底加摘要够用，另外两层按需再上）
- 跨会话长期记忆、用户画像

## 验收标准

1. 连续聊二十轮以上，token 不爆、系统不崩。
2. 按演示配置再聊一遍（光调窗口不够，固定开销和单轮峰值是按默认的 X、Y、步数算的，滑窗会归零并报「上下文预算不足」）：MODEL_CONTEXT_WINDOW=18000 MAX_OUTPUT_TOKENS=2000 MAX_USER_INPUT_TOKENS=2000 MAX_AGENT_STEPS=3 TOOL_RESULT_MAX_TOKENS=1200 RERANK_TOP_K=5。这组算出来滑窗 5650、层 1 预算 3954、层 2 预算 1695。日志里能看到完整级联：层 1 超预算就降级一批（层1 降级 X→Y），层 2 攒到超预算才起摘要（summary trigger 层2 约 N token > 预算 M），压完落成新的一段（summary done 第N段）；这时再问「最开始那个订单后来怎么说」，要能靠梗概里存下的订单号和诉求答对。
3. 默认窗口下聊二十轮，不该触发任何降级和摘要。装得下就不压，压缩是成本不是美德，这一条也要验。
4. 日志里能看到早期轮次被后台摘要任务压缩的痕迹，且摘要生成没有阻塞该轮用户回复；grep model_ctx / history_ctx 能直接看到每轮发给模型的摘要和滑窗内容。
5. 前端侧栏能开多个会话对照、切回旧会话时历史完整回载、能接着聊。

## 工作要求

1. 全程走 Superpowers 流程，技能自动触发；产出不是可单测代码的任务（纯 Prompt、数据类），把 TDD 那步换成拿标注样例或评估集跑一遍验证，其余步骤照走。
2. 过程留痕：在仓库 dev-notes/ch07.md 里追记开发过程，每完成一个阶段（brainstorm 定稿、计划评审通过、每个任务完成、code review 结论、finish）就补一段，记四样：我这一步发的关键原话、你的关键产出（spec / plan 路径、评审结论）、我拒绝或纠偏了什么、翻车与返工；不许收尾时一次性补记。
3. 涉及具体库、框架、API 的用法（FastAPI、SQLAlchemy、LangChain、LangGraph、Milvus、Langfuse 这些），一律先用 Context7 MCP 查最新官方文档和接口定义再动手，别凭记忆写，版本对不上的 API 是返工重灾区。
4. 上面点名的技术选型是定死的，实现中发现矛盾或走不通，停下来问我，不要自行换方案。
5. 完结交付：功能演示命令、测试结果、dev-notes 路径。

## 建表 DDL（两步均需 apply）

```sql
-- =============================================================
-- step07 · 会话上下文管理 · 建表 DDL(第一步,共两步)
-- 这一步给 step02 的 conversations 表加两列:一段投影用的摘要,和摘要覆盖到哪条的锚点。
-- 分层要用的另一个锚点和分段摘要表在 ch07-layers.sql,两个文件都要 apply。
-- =============================================================

-- 确保中文 COMMENT 按 utf8mb4 解析(latin1 默认的 mysql client 会把中文 double-encode)
SET NAMES utf8mb4;

ALTER TABLE conversations
  ADD COLUMN summary             TEXT            NULL COMMENT '最近几段梗概拼成的投影,拼装时跟证据一起挂在用户那句之后' AFTER status,
  ADD COLUMN summary_upto_msg_id BIGINT UNSIGNED NULL COMMENT '摘要已覆盖到哪条消息,滑窗从其后接原文' AFTER summary;


-- =============================================================
-- step07 · 分层上下文 · 建表 DDL
-- 两件事:conversations 加一列记层 1 起点;新建一张分段摘要表。
--
-- 层的边界靠消息 id 表达,不搬数据:
--   id ≤ summary_upto_msg_id          已进摘要
--   summary_upto < id ≤ layer1_from   层 2,渲染成半压形态
--   id > layer1_from                  层 1,原样
--
-- 摘要一段一行、只追加:压完的段落不再回炉重压,一个事实只经历一次有损压缩。
-- 反过来滚动重写的话,第五版摘要就是最早那批内容被压了五次的结果,
-- 订单号哪一次被判成不重要给丢了,事后谁也查不出来。
-- =============================================================

SET NAMES utf8mb4;

ALTER TABLE conversations
  ADD COLUMN layer1_from_msg_id BIGINT UNSIGNED NULL
    COMMENT '层1(原文)起点;此 id 之后原样,之前渲染成半压形态'
    AFTER summary_upto_msg_id;

CREATE TABLE IF NOT EXISTS conversation_summaries (
  id              BIGINT UNSIGNED NOT NULL AUTO_INCREMENT,
  conversation_id BIGINT UNSIGNED NOT NULL,
  seq             INT             NOT NULL COMMENT '第几段,从 1 开始',
  from_msg_id     BIGINT UNSIGNED NOT NULL COMMENT '这段覆盖的消息区间,闭区间',
  upto_msg_id     BIGINT UNSIGNED NOT NULL,
  content         TEXT            NOT NULL,
  created_at      DATETIME        NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (id),
  UNIQUE KEY uk_conv_seq (conversation_id, seq),
  KEY idx_conv_upto (conversation_id, upto_msg_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='分段摘要,一段一行只追加';
```
````

## 后续明确确认的方案

1. 工具流水：用户选择「保留现有 SQL 工具流水，只调整传给模型的三层视图」。因此实现保留原有工具请求/结果持久化；上述“工具结果不落消息表”保留为原始要求，不冒充最终存储口径。
2. 文档核对：本步骤无可调用的 Context7 接口时，用户允许使用各项目官方文档和仓库锁定版本源码核对，不改变技术栈。
3. 预算：用户允许按本仓库实际开销推导，并在日志列清计算过程；原始提示词中的 5650 / 3954 / 1695 是原给定演示数值，不要求通过写死预算复现。
4. 架构：用户批准原文完整持久化、统一三层模型视图、lifespan 托管追加式后台摘要、实际开销预算、完整上下文日志和多会话侧栏，并分别批准正式设计和十一项实施计划，沿用 Subagent-Driven 实现。
5. 参考订单：用户确认补入演示订单 2002，商品自动饮水机、待付款、1557 元，并验证用户称“恒温猫窝”时指出商品不一致。
6. 真实验收：小额页面完整链路测试获持续授权；两组长验收和额外非页面诊断分别单独授权。失败、跳过和不同版本的结果分别保留，合并不代表补齐缺失的真实验收。

## 本轮归档与集成指令

> 合并提交推送到远程……然后把这些记录成第七步的提示词md

## 关联材料

- [设计文档](../superpowers/specs/2026-10-17-context-management-design.md)
- [实施计划](../superpowers/plans/2026-10-17-context-management.md)
- [API 与版本核对](../superpowers/references/2026-10-17-context-management-apis.md)
- [原始长验收记录](../superpowers/reports/2026-10-17-context-management-acceptance.md)
- [后续稳定性修复与验证限制](../superpowers/reports/2026-10-18-model-recovery.md)
- [演示命令](../context-management-demo.md)
- [开发过程记录](../../dev-notes/ch07.md)
- [第一步 DDL](../../sql/ch07.sql)
- [第二步 DDL](../../sql/ch07-layers.sql)
