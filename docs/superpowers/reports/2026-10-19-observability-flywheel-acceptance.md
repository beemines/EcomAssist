# 第九步实际验收报告

> 本文保留首次验收原始事实。按18张标准图修正后的最新结果见[参考标准实际报告](2026-10-20-reference-acceptance.md)，包含新增完整20题及仍未达成的质量项。

2026-10-20新增验收基线：用户提供18张标准流程与页面截图后，完成[参考页面差距对照](../../ch09-reference-gap-analysis.md)。**按新增标准当前尚未完整通过**；下文保留原本地运行事实，未覆盖项与质量失败以后续对照表逐项复验。

验收日期：2026-10-20。工作区：`D:/shixi/ecommerce-customer-service/.worktrees/observability-flywheel`，分支 `feat/observability-flywheel`。采用已批准的 Native 顺序实施；一次独立后端整分支审查，前端按用户要求采用 Vibe Coding。设计、计划和本报告的“完成”只覆盖本章本地部署范围。

## 使用入口

- [PowerShell启动与命令](../../ch09-local-demo.md)
- [PyCharm逐步运行与验收](../../ch09-pycharm-acceptance.md)
- [页面手动验收步骤](../../ch09-manual-acceptance.md)
- [开发过程](../../../dev-notes/ch09.md)
- [独立后端审查与一轮修复](2026-10-20-observability-flywheel-review.md)
- [全部执行裁决与finish验证](2026-10-20-observability-flywheel-execution.md)
- 客服 `http://127.0.0.1:8006/`；审核与统计 `http://127.0.0.1:8006/review-queue`；本地Langfuse `http://127.0.0.1:3000/`。

本章文件在独立worktree里，主目录master尚未合并。用户本次批准的是实施和隔离工作区，没有授权第九步合并或推送。`.env`、本地管理员密码与SDK密钥均未提交。

## 自动测试及结构

后端最终完整回归：**3215通过、255跳过，457.77秒（交付前再次完整运行）**。真实本地MySQL3308、Milvus、本地Langfuse及旧质量/上下文/工具审计/工单确认关键集成：**136通过，89.04秒**。跳过项不当作通过，真实集成另行显式启用。

三个审查Important均先观察失败后修复：API人工重试唤醒暂停消费者而不重置次数；真实向量化Jobs失锁后不能提交权威done；审核表单显式选择分类并保证同分类检索能找到新知识。审查0 Critical、3 Important、0 Minor；一轮修复后没有未解决Critical/Important，没有第二次派审。后续Prompt实测发现的草稿Minor另列下文，不能混成审查“全部无问题”。

业务3307和测试3308增量迁移已应用并只读核验，先保存原表结构。3308缺失的旧退款/审计前置表按原迁移补齐，没有清表或重建旧会话。用户原DDL保存在 `sql/ch09-ddl.sql`；运行时必要字段和严格检查属于另一个增量，迁移冲突会停止。旧八题门槛相关合同和原质量回归保留在自动测试；本批未额外付费重跑那八题，不以其替代本次300题校准。

## 真实置信度校准

冻结数据集 `merchant-rag-300-v1`，同一冻结语料、实际BGE嵌入/重排。确定性分组分层切分：100题校准、200题留出；关联回归题随父组，不跨集合。留出标签未用于拟合或回调阈值。

| 拒答为正类 | 拒答F1 | 误放 | 误拒 | 样本数 |
| --- | ---: | ---: | ---: | ---: |
| 旧Top1闸门·校准 | 0.7500 | 0 | 14 | 100 |
| 新多信号闸门·校准 | 0.9767 | 0 | 1 | 100 |
| 旧Top1闸门·留出 | 0.7647 | 2 | 22 | 200 |
| 新多信号闸门·留出 | 0.9091 | 6 | 1 | 200 |

新规则减少误拒但增加误放，不能宣称所有维度优于旧规则。特征保留Top1、有效证据数和Top1/Top2分差；此次校准权重为 **1/3/0**，分差没有获得权重。置信度是校准判别分，**不是概率**。阈值0.80303030303，严格大于才放行；固定TopK10和证据预算6000。规则版本 `19757a9d2bfb0afa35bb564b9229c6be7e44f4e6ac764465b34d321fe8b2fe0b`。

实际产物：`runtime/ch09-evidence/calibration/{manifest,split,rule,report}.json` 与 `samples.jsonl`。临时SQL行、Milvus集合均按归属清理，`cleanup.ok=true`。首笔嵌入ConnectError发生时0题成功，原失败产物另存 `calibration-attempt1-connect-error`；一次有界模拟文字诊断成功后，仅重新起一次300题采集，没有重跑已成功题目或清零计数。不能确定首笔网络异常根因，没有将其归咎额度或算力。

校准共305次嵌入（首笔失败1、诊断1、语料批次3、问题300）和300次重排；GLM为0。

## Prompt标注评估

固定12组，各一次标准化和一次查重，**24次GLM，7970实际tokens，零SDK重试**。12组均返回严格可解析结构，查重12/12符合固定标签。语义逐项核对型号、否定、适用条件、多诉求及草稿事实边界，严格内容 **11/12**。

- F02使用“拆下来清洗”而非“拆洗”，语义保留A1并正确拒绝与A2归并；原字面检查false保留。
- **延期Minor：F08草稿复述了“忽略999指令”的元说明**。标准问题删除注入，实际只归并到本批候选18，未执行999；没有越权归并或自动发布。草稿仍需人工核准，但内容干净程度未全过，不能称12/12内容全绿。未改固定标签或静默扩展24调用批次。

原始输出、各字面检查和后续人工语义说明分开保存：`runtime/ch09-evidence/prompt-evaluation/report.json`。

## 页面真实飞轮闭环

全部为本批新建模拟会话87～92，不读取旧会话正文外发，不执行工单或退款写入。

| 检查 | 真实证据 |
| --- | --- |
| 缺失政策→可信兜底 | 会话87问星舟CH09体验服务押金/归还期限，retrieval_low_conf入池17 |
| 👎回捞原轮证据 | 同轮反馈18，和17均保存当时Top10正文/得分；不是当前轮或后续新知识 |
| 同轮幂等/跨入口计数 | 17/18属于同一assistant846，只计一次；两次重放反馈都返回18、created=false |
| 同义缺口归并 | 会话88同义问入池19，仍归到review1，两个逻辑轮累计2次 |
| 人工审核/索引就绪 | review1填“验收模拟政策”分类及明确模拟答案，knowledge135一次发布ready，MySQL vectorize_status=done |
| 新会话重新检索 | 会话89实际答出押金199元、领取后7天内归还，trace中可见新片段135；未用上个会话记忆 |
| 生成自评入口 | 会话92问CH09专用50元券，相关运费片段不包含领券规则；self_check入池22→review2待审 |
| 旧物流MCP主链路 | 会话90订单1001，query_logistics审计source=mcp:logistics、success、retry0，无工单退款 |
| 闲聊与意图成本 | 会话91正常结束并记录最终闲聊意图 |

三路入口均有实际落池和原轮证据。review2留作明确模拟政策缺口示例，未自动通过。不同型号/否定/条件的查重边界由固定Prompt标注和后台回归覆盖；没有为页面再发无限量变体。

SQL、审计和归属证据：`runtime/ch09-evidence/actual-page-storage.json`、`actual-feedback-replay.json`、`acceptance-owned-jobs.json`。本次人工核准的135明确标记“仅用于第九步验收，不适用于真实订单”。

## Langfuse与Token对账

本地v4.63.0 + Python SDK5.0.2。已在界面展开真实树，查看意图generation的prompt、输出、token和耗时；检索、精排、统一工具执行、Agent最终回答等span和父子关系均从本地API回读存档。正式图构造处统一挂回调，没有每轮重复挂载。

- [缺失政策拒答trace·会话87](http://127.0.0.1:3000/project/ch09-local-project/traces/6d8121b4fe575acc376d573bfc4e34b6)
- [补库后回答trace·会话89](http://127.0.0.1:3000/project/ch09-local-project/traces/0b8f192c3a9a6390bffcc5f4fbcde3f1)
- [物流MCP trace·会话90](http://127.0.0.1:3000/project/ch09-local-project/traces/dcde1d3ea7b44a87d730df94b0060460)
- [闲聊trace·会话91](http://127.0.0.1:3000/project/ch09-local-project/traces/890fc3fb0097470c9d5d65e3321615e0)
- [生成自评不足trace·会话92](http://127.0.0.1:3000/project/ch09-local-project/traces/ea46caba993be9f7209d3625d416f381)

仅汇总本批六个chat根执行，按generation ID去重，不加父span合计，不混后台和评估。分类前的指代/分类模型消耗归入最终意图。

| 最终意图 | 请求数 | 模型调用 | 实际tokens | 缺usage |
| --- | ---: | ---: | ---: | ---: |
| 商品咨询 | 4 | 12 | 18583 | 0 |
| 物流 | 1 | 5 | 7152 | 0 |
| 闲聊 | 1 | 2 | 2575 | 0 |

合计28310实际tokens，19次模型调用。后台标准化/发布/评估按purpose单列。无可信价格定义，货币费用显示N/A；Langfuse的no cost不当成实际0元。模型返回total可能含未分拆的内部token，不自行强行改成input+output。页面按本机日期分钟选择，避免同日离线集成trace污染本批实际统计；后台缓存60秒。

详见 `runtime/ch09-evidence/actual-chat-traces.json` 和 `actual-proof-summary.json`。截图：`actual-langfuse-prompt-tree.png`、`actual-review-ready.png`、`actual-flywheel-answer.png`、`actual-mcp-logistics.png`、`actual-intent-usage.png`。

## 两轮真实评估与实际调用量

运行使用同一smoke_20、同一rule、同一冻结配置，正式评估API启动两个UUID，未复用旧报告填第二轮。全量300题及收费定时均未执行。

| 真实轮次 | 第1轮 | 第2轮 |
| --- | --- | --- |
| run_key | `1dca3ee1-5a49-4c60-a82c-7454d49b4be3` | `3ecfae0f-2897-434f-8ec9-b37df20fc3e4` |
| 状态 | completed_with_errors | completed_with_errors |
| 尝试/成功/错误 | 20 / 11 / 9 | 20 / 12 / 8 |
| Recall@10 | 1.0，n=16 | 1.0，n=16 |
| MRR@10 | 1.0，n=16 | 1.0，n=16 |
| Faithfulness | 1.0，n=7 | 1.0，n=8 |
| 生成/裁判失败 | 1 / 8 | 3 / 5 |
| GLM物理调用 | 71 | 70 |
| 嵌入/重排 | 23 / 20 | 23 / 20 |
| 实际/估算tokens | 107283 / 39339 | 108094 / 25294 |
| 自有资源清理 | ok=true | ok=true |

两轮配置指纹相同：`5f6f500a7b151ada48a3492b4a7b1c88227d9d970a25121da30496091dd3a4b4`。检索分母16排除4道预期拒答；Faithfulness分别再排除生成/裁判错误与4个无事实断言的拒答样本。有效子集均1.0，**不代表20/20生成成功，也不代表300题满分**；17个生成/裁判错误完整保留。两轮趋势页截图为 `runtime/ch09-evidence/actual-two-eval-results.png`。

各轮原始报告/逐题judge快照/独立资源归属和清理结果保存在 `runtime/eval-pipeline/<run_key>/`，对应 `eval_runs` 每UUID恰有一行。排除项会显示到趋势页，不能把Faithfulness的有效分母当作全部20题。第一轮部分裁判返回finish_reason=length、原文为空，固定2048输出预算未改动；未补括号或伪造判定，也没有静默重跑失败题。

本批唯一账本 `ch09-local-20261019` 最终实际累计 **GLM190/280、嵌入356/450、重排344/450**，失败也计数，零SDK自动重试。GLM分解：Prompt24、两轮评估141、页面19、后台标准化/查重6；页面和后台合计25，低于本阶段80。嵌入305校准+46评估+5页面/发布；重排300校准+40评估+4页面。账本 `runtime/ch09-evidence/call-ledger.sqlite` 保留，未清零或换run_id。

## 最终运行状态与磁盘

- 本轮池17/18/19/22均matched；审核1/知识135已ready；审核2仅待审、不自动发布；两轮评估终态且cleanup=true。归属清单closed=true，未遗留未完成测试任务交给无上限服务继续外发，不需要取消或清理他人任务。
- 8006已通过严格PID/创建时间/命令/工作区守卫切回**普通模式**，PID54956；`/health`实际返回`{"status":"ok"}`，不带acceptance额度。新工厂仍关闭收费定时和旧摘要启动回扫；正常新聊天按业务配置调用模型。8004/8005和既有MCP8101/8102未停止或接管。
- 本地Langfuse六容器保留，8007离线预览已停止，随机测试schema已按journal清理；正式知识135和真实trace保留供复核。
- Docker总量观测：镜像由3.649GB到9.158GB，卷由1.513GB到1.919GB；本次期间逻辑增量约**5.9GB**（镜像5.509GB、卷0.406GB）。含同机校准/评估活动，不能严格全归因Langfuse，也不是Windows VHDX文件缩减量；这是本机实际观测，未预分配100GB。

## 验收结论与限制

六项功能流程均有实际证据：本地trace、缺失问题/原轮证据入待审、人工补库后新会话答对、👎后端幂等、三种意图Token汇总、两轮实际评估趋势。自动测试与本地集成通过。**模型质量存在明确边界**：留出误放6/200、Prompt草稿Minor一项、两轮17个生成/裁判错误，不能称质量全绿或保证任意输入不失败。

未执行：两轮全量300题生成、收费定时、真实订单系统、真实工单退款写入、公网多人后台。分支和worktree保留，合并/推送等待用户另行指示。
