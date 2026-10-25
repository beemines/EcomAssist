# 第十步原始提示词：多标签主题分类器

用户首次提供于2026-10-21，并于2026-10-24再次提供同一提示词，要求归档并合并、提交、推送第十步。下方逐项保留原始功能、技术栈、验收标准、工作要求及DDL，不把后续实现补充字段改写进原需求。

后续批准、纠偏与开发过程见[第十步记录](../../dev-notes/ch10.md)；实现事实与质量限制见[交付报告](../superpowers/reports/2026-10-21-ch10-delivery.md)，合并与推送事实另见[本次集成记录](../superpowers/reports/2026-10-24-ch10-integration.md)。提示词是需求存档，不单独构成验收完成证明。

```markdown
我要用 Superpowers 模式给客服系统训练一个自己的模型:微调一个多标签主题分类器,把飞轮攒下的低置信度问题按主题批量归类,好决定先补哪块知识。

## 功能需求
1. 数据处理四步,语料从飞轮低置信度问题池捞真实问题,池里量不够就让大模型照术语表造一批模拟问题补足:
   - 清洗:脱敏、修错别字和格式
   - 归并术语表:全系统统一一份 17 类的权威类目表,退换货、物流、尺码、发票四大类领头,每类配一句边界说明,近邻类目靠边界说明划开。17 类为:退换货、物流、尺码、发票、质量问题、运费、优惠活动、价保、支付、订单修改、库存补货、商品信息、保修维修、账号、会员积分、评价、其他。近邻边界:修归保修维修、退归退换货;运费管钱、物流管货;价保是补差价、优惠活动是券和满减
   - 分层抽样:按 80/10/10 划训练、验证、测试集,各类别按比例进三份
   - 数据增强:同义词替换、句式微调,只扩训练集
2. 标注:多标签,一句话字面提到几个诉求就打几个标签,一个不多一个不少;标签获取走大模型照术语表预标、人工抽审这条折中路线
3. 训练:RoBERTa-wwm-ext 全参微调,不用 LoRA;训练中用验证集盯分数,配正则化和早停防过拟合
4. 评测:留出测试集上按类目算精确率、召回率、F1,配每类目混淆矩阵;自动指标之外,再人工抽判错样本复核
5. 部署:导出成推理服务,挂在旁路按批量跑——低置信度问题攒够一批归一次类,结果写进 topic_classifications 表(关联问题、多标签 labels、归类时间)喂给飞轮后台看各主题分布;实时对话主链路不调它
6. 前端配套:在飞轮后台加一个主题分布页,各类目问题量做成简单图表,哪类堆得多一眼能看出来

## 技术栈
- 哈工大讯飞 RoBERTa-wwm-ext,全参微调
- 推理服务化(如 ONNX / transformers 服务)

## 本步骤不做
- LoRA / QLoRA(那是大模型才用的手段)
- embedding 微调、意图识别微调

## 验收标准
1. 测试集各类目 F1 和混淆矩阵报告能跑出来
2. 拿一批攒下的真实问题跑归类,后台主题分布页能看到各类目统计
3. 「买大了想退」这类多诉求句子,能同时命中多个类目

## 工作要求
1. 全程走 Superpowers 流程,技能自动触发;产出不是可单测代码的任务(纯 Prompt、数据类、训练类),把 TDD 那步换成拿标注样例或评估集跑一遍验证,其余步骤照走;前端部分是例外,用 Vibe Coding 方式直接做,我描述效果你改,不套 brainstorm、TDD、code review 那套流程
2. 过程留痕:在仓库 dev-notes/ch10.md 里追记开发过程,每完成一个阶段(brainstorm 定稿、计划评审通过、每个任务完成、code review 结论、finish)就补一段,记四样:我这一步发的关键原话、你的关键产出(spec / plan 路径、评审结论)、我拒绝或纠偏了什么、翻车与返工;不许收尾时一次性补记
3. 涉及具体库、框架、API 的用法(FastAPI、SQLAlchemy、LangChain、LangGraph、Milvus、Langfuse 这些),一律先用 Context7 MCP 查最新官方文档和接口定义再动手,别凭记忆写,版本对不上的 API 是返工重灾区
4. 上面点名的技术选型是定死的,实现中发现矛盾或走不通,停下来问我,不要自行换方案
5. 完结交付:功能演示命令、测试结果、dev-notes 路径-- =============================================================
-- step10 · 模型微调 · 建表 DDL
-- 本步骤新建:topic_classifications(微调分类器旁路批量归类结果)
-- 低置信度问题攒够一批,分类器归一次类,结果落这张表喂给飞轮后台看主题分布
-- 实时对话主链路不写这张表
-- =============================================================

-- 确保中文 COMMENT 按 utf8mb4 解析(latin1 默认的 mysql client 会把中文 double-encode)
SET NAMES utf8mb4;

CREATE TABLE topic_classifications (
  id            BIGINT UNSIGNED NOT NULL AUTO_INCREMENT COMMENT '主键',
  question_id   BIGINT UNSIGNED NOT NULL                COMMENT '归类的问题,指向 low_confidence_questions.id',
  labels        JSON            NOT NULL                COMMENT '多标签,17 类权威类目里命中的若干个',
  classified_at DATETIME        NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '归类时间',
  PRIMARY KEY (id),
  UNIQUE KEY uk_question_id (question_id),
  CONSTRAINT fk_topic_question FOREIGN KEY (question_id) REFERENCES low_confidence_questions (id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='主题分类结果';
```
