# 第九步提示词：可观测性与数据飞轮

本文归档用户于2026-10-21再次提供的第九步完整提示词与建表DDL，仅整理Markdown排版。原始需求不按实现结果倒改；已批准的实施调整、实际验证范围和质量限制单列在文末。

## 完整原始提示词

````markdown
我要用 Superpowers 模式给客服系统装上眼睛,再把答不上的问题变成改进燃料。

## 功能需求
1. 接 Langfuse:设环境变量、在 LangGraph 编译时挂一次回调;每条请求的完整 trace 树(每个节点的 prompt、工具调用、检索结果、token 消耗和耗时)都能在界面上铺开看
2. Cost Control:把意图识别结果打进 trace 元数据,按意图维度统计 token 花销,知道钱花在哪类问题上
3. 数据飞轮闭环,三个入口都把问题送进 ch04 建的 low_confidence_questions 问题池,各自标好入池入口;落池时把当轮的召回片段快照(Top 几条的原文和得分)一并存下,问题池新加一列,给人工审核当依据;👎 这种事后落池的,从该会话当轮的检索结果里尽力回捞,那一轮真没走检索(闲聊、业务数据类)才空着:
   - 检索证据置信度低:把 ch05 那道最简版置信度闸升级成正式的置信度检查,拿检索和精排结果算 evidence_confidence(精排 Top1 的相关性分、有效证据数量、Top1 和 Top2 的分差这些信号),阈值拿 ch04 评估集校准、不拍脑袋定;闸的位置不动,仍卡在知识类检索之后、进 Agent 之前,拦下就回兜底话术并落池
   - 生成阶段模型自评知识不够答:ch04 已经在落池,确认接进飞轮即可
   - 用户反馈没解决:ch04 聊天页那组满意度反馈目前是纯前端采集,本步骤把 👎 接到后端,用户点了就把该轮的用户问题落池
4. 飞轮流水线:
   - 问题标准化:口语原话改写成标准 FAQ 式问题,配一条示例答案备查
   - 查重:让模型判断和待审队列里已有问题是不是同一个意思,是就合并、累加出现次数
   - 入待审队列(建 review_queue 表:标准化问题、示例答案、出现次数、审核状态、核准答案;一行一个去重缺口,查重命中就累加出现次数、不新建行,归并落点记回 low_confidence_questions 新加的 matched_review_id 列),人工在后台审核,通过的走 ch03 落库流程写入知识库
5. 自动化评估流水线:复用 ch04 那份评估集和指标(检索段 Recall@K、MRR,生成段 Faithfulness)定期跑,每轮分数落 eval_runs 表(建表:触发方式、评估集条数、各指标分数 JSON、时间;一行一轮),按时间连成趋势,哪个指标在下滑要能一眼看出来
6. 前端配套:待审队列做成一个简单的后台管理页,列出标准化问题、出现次数、示例答案,能点通过或驳回,通过的写入知识库;每行能点开详情,看到归并进来的用户原话和当时的召回片段,审核人对着片段判断知识库是真缺这块、还是有但没检到

## 技术栈
- Langfuse:开源、自部署,链路数据不出自家服务器

## 本步骤不做
- 低置信度问题按主题归类的微调分类器(下一步的事)

## 验收标准
1. Langfuse 里能点开任意一条请求,看到完整链路
2. 问一个知识库没有的问题,拿到兜底话术,且该问题出现在待审队列里;在审核页点开这条,能看到用户原话和当时的召回片段
3. 在后台审核页点通过后,同一个问题再问就能答对——飞轮转完一整圈
4. 在聊天页对一条回答点 👎,这条用户问题落进问题池,标准化查重后出现在待审队列里
5. 能拿出按意图汇总的 token 花销统计,哪类意图最烧钱看得出来
6. 评估流水线至少跑两轮,能看到指标趋势对比

## 工作要求
1. 全程走 Superpowers 流程,技能自动触发;产出不是可单测代码的任务(纯 Prompt、数据类),把 TDD 那步换成拿标注样例或评估集跑一遍验证,其余步骤照走;前端部分是例外,用 Vibe Coding 方式直接做,我描述效果你改,不套 brainstorm、TDD、code review 那套流程
2. 过程留痕:在仓库 dev-notes/ch09.md 里追记开发过程,每完成一个阶段(brainstorm 定稿、计划评审通过、每个任务完成、code review 结论、finish)就补一段,记四样:我这一步发的关键原话、你的关键产出(spec / plan 路径、评审结论)、我拒绝或纠偏了什么、翻车与返工;不许收尾时一次性补记
3. 涉及具体库、框架、API 的用法(FastAPI、SQLAlchemy、LangChain、LangGraph、Milvus、Langfuse 这些),一律先用 Context7 MCP 查最新官方文档和接口定义再动手,别凭记忆写,版本对不上的 API 是返工重灾区
4. 上面点名的技术选型是定死的,实现中发现矛盾或走不通,停下来问我,不要自行换方案
5. 完结交付:功能演示命令、测试结果、dev-notes 路径

-- =============================================================
-- step09 · 可观测性与数据飞轮 · 建表 DDL
-- 本步骤新建:review_queue(待审队列,标准化去重后的知识缺口)
--          eval_runs(自动化评估流水线每轮结果,连起来看趋势)
-- 并给 step04 的 low_confidence_questions 加两列:
--   matched_review_id 记这条原话查重后归并到哪个缺口
--   retrieved_chunks  存落池时的召回片段快照,审核页给人看
-- 建表顺序:先 CREATE review_queue,再 ALTER low_confidence_questions 加外键指向它
-- =============================================================

-- 确保中文 ENUM 定义值/DEFAULT/COMMENT 按 utf8mb4 解析
-- (否则 latin1 默认的 mysql client 会把中文 double-encode,ENUM 值存成乱码)
SET NAMES utf8mb4;

-- 待审队列:一行 = 一个去重后的知识缺口;查重命中就累加 occurrence_count,不新建行
CREATE TABLE review_queue (
  id                  BIGINT UNSIGNED NOT NULL AUTO_INCREMENT COMMENT '缺口主键,也是查重命中要返回的 matched_question_id',
  normalized_question VARCHAR(512)    NOT NULL                COMMENT '标准化后的 FAQ 式问题',
  ai_suggested_answer TEXT            NULL                    COMMENT '模型生成的示例答案,备查',
  occurrence_count    INT UNSIGNED    NOT NULL DEFAULT 1      COMMENT '出现次数,查重命中累加,越高越该优先补',
  review_status       ENUM('待审','通过','驳回') NOT NULL DEFAULT '待审' COMMENT '人工审核状态',
  approved_answer     TEXT            NULL                    COMMENT '审核通过时补的核准答案,走 ch03 落库流程写回知识库',
  created_at          DATETIME        NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '首次入队时间',
  updated_at          DATETIME        NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
  PRIMARY KEY (id),
  KEY idx_review_status (review_status)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='飞轮待审队列';

-- 评估轮次:一行 = 评估流水线跑完的一轮,各指标分数收进 metrics JSON,按时间连起来就是趋势线
CREATE TABLE eval_runs (
  id           BIGINT UNSIGNED NOT NULL AUTO_INCREMENT COMMENT '评估轮次主键',
  triggered_by ENUM('定时','手动') NOT NULL DEFAULT '定时' COMMENT '这轮怎么起的:定时任务,或某次改动后手动跑',
  dataset_size INT UNSIGNED    NOT NULL                COMMENT '这轮跑的评估集条数',
  metrics      JSON            NOT NULL                COMMENT '各指标分数,如 {"recall_at_k":0.82,"mrr":0.71,"faithfulness":0.90}',
  created_at   DATETIME        NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '跑完落表时间',
  PRIMARY KEY (id),
  KEY idx_created_at (created_at)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='自动化评估流水线轮次结果';

-- 原话流水记归并落点:标准化查重后指向 review_queue 里的缺口行,NULL 表示尚未处理
-- 再存一份落池当时的召回片段快照(Top 几条的原文和得分),没走检索的入口为 NULL
ALTER TABLE low_confidence_questions
  ADD COLUMN retrieved_chunks  JSON            NULL COMMENT '落池时的召回片段快照:Top 几条的原文与得分,审核页展示用;没走检索为 NULL' AFTER reason,
  ADD COLUMN matched_review_id BIGINT UNSIGNED NULL COMMENT '查重后归并到的缺口,指向 review_queue.id' AFTER retrieved_chunks,
  ADD KEY idx_matched_review_id (matched_review_id),
  ADD CONSTRAINT fk_lcq_review FOREIGN KEY (matched_review_id) REFERENCES review_queue (id) ON DELETE SET NULL;
````

## 已批准的实施口径与实际范围

- Langfuse按用户选择在本机独立Compose部署，账号预置组织EcomAssist Local和项目EcomAssist step09；链路写往本地3000端口。
- Context7当时没有可调用工具，用户明确批准本步骤使用官方文档与锁定源码核对；技术选型不替换。来源记录见[接口核对](../superpowers/research/2026-10-19-observability-flywheel-apis.md)。
- 用户批准[正式设计](../superpowers/specs/2026-10-19-observability-flywheel-design.md)及[实施计划](../superpowers/plans/2026-10-19-observability-flywheel.md)，Native顺序实施，前端按Vibe例外；最新视觉要求沿用聊天页浅灰绿、墨绿与圆角，参考图只借鉴功能和信息组织。
- 评估范围保留两轮各20题的原额度，未批准两轮300题或收费定时。原两轮有9/8个阶段错误，之后新增一轮完整20题；新旧配置分别保留，不能当成两轮同配置无错误的质量通过。剩余质量项见[实际报告](../superpowers/reports/2026-10-20-reference-acceptance.md)。
- 原始DDL保留为[sql/ch09-ddl.sql](../../sql/ch09-ddl.sql)，并有设计中列明的运行字段扩展；不把扩展字段反写成用户原始需求。
- 本次2026-10-21用户明确要求“写进md，并且把第九步合并提交推送”，取代此前仅保留隔离分支的集成安排。合并前检查及最终交付状态继续追记[dev-notes/ch09.md](../../dev-notes/ch09.md)。

## 运行和验收入口

[功能演示命令](../ch09-local-demo.md) · [PyCharm步骤](../ch09-pycharm-acceptance.md) · [逐页手动验收](../ch09-manual-acceptance.md) · [独立后端审查](../superpowers/reports/2026-10-20-reference-backend-review.md)
