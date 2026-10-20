# 第九步参考标准修正 · 实际验收报告

日期：2026-10-20。分支feat/observability-flywheel；工作目录D:/shixi/ecommerce-customer-service/.worktrees/observability-flywheel。按18张标准图实施Task11–17；[首次报告](2026-10-19-observability-flywheel-acceptance.md)保留原事实，[逐项差距](../../ch09-reference-gap-analysis.md)更新为本轮状态。

## 当前结论

页面、追踪、数据飞轮闭环及后端审查修复已完成本轮验证；**不能宣布全部质量验收通过**。新配置只有一轮完整无阶段错误的20题，未有第二轮同配置完整结果；校准200题留出仍有4条误放。用户明确保留原额度，未批准两轮300题或扩额；到278/280 GLM后停止付费调用。

最终完整离线回归：**3264通过、257跳过，634.73秒（退出码0）**。完整日志runtime/ch09-evidence/reference-final6.log；跳过项没有计为通过。真实本地MySQL3308/Milvus/Langfuse关键集成：**133通过，174.13秒**。后端审查修复目标集94通过153.59秒；MCP端口/审查/启动守卫集27通过20.49秒。JS语法检查和Git whitespace检查通过。

## 页面演示入口

| 页面 | 地址 |
| --- | --- |
| 客服 | http://127.0.0.1:8006/ |
| 飞轮待审 | http://127.0.0.1:8006/review |
| 成本/评估/校准 | http://127.0.0.1:8006/observability |
| 本地Langfuse | http://127.0.0.1:3000/ |

旧/review-queue保留。当前8006受管普通模式PID63436，v3规则在用；自有验收任务journal已关闭，旧8004/8005、MCP8101/8102及其归属保留。没有通过切普通模式继续付费验收。

## 真实飞轮前后对照

使用专门模拟问题“验收用的CH09-A21猫窝磁吸配件要隔多久保养一次？”。

1. 会话94得到资料不足兜底及转人工，原轮有实际召回但与问题不匹配。pool23入口retrieval_low_conf，snapshot_status=captured。
2. 对这条回答点👎，pool24入口user_feedback，准确回捞相同用户/助手轮，召回快照与23完全相同。两入口均归并review3；同一逻辑用户轮次计出现1次，详情保留两条原话。
3. 审核页已预填AI草稿。人工修改成明确标注的模拟知识：“每14天用干布清理一次，不可水洗，仅用于验收”。确认通过后knowledge136，vectorize_status=done，publication=ready。未就绪时页面只显示等待。
4. 新会话95重问，正确回答14天/干布/不可水洗，带[1]，并声明这属于模拟知识、不适用于真实商品。
5. 原模拟优惠券review2驳回后，会话96再次问同义问题，pool25归并2，次数1→2，状态仍驳回，没有新增知识。
6. 会话97发送已授权模拟闲聊，正常回答，补充第二类真实意图成本。

本轮新增客服94–97、问题池23/24/25，知识136。原会话87–92及self_check入口证据保留。实际客服未提交工单、退款或真实商品承诺；历史客户池没有批量外发。

运行证据：runtime/ch09-evidence/reference-live-proof.json、reference-live-summary.json、reference-final-verification.json。截图：reference-live-before.png、reference-live-after-final.png、reference-two-sources.png、reference-publication-ready.png、reference-rejected-count.png。

## 完整trace与成本

会话95 trace：[打开根问答与节点树](http://127.0.0.1:3000/project/ch09-local-project/traces/d6205e14debb348066ed3be91d3d7353)。根Input为原问题，Output为上述实际答案；intent:商品咨询标签、会话95、耗时14.83秒；展开可看指代、分类、检索、置信度、Agent及各generation的prompt/用量/耗时/成本。截图reference-trace-root.png、reference-trace-generation.png。

统计只计generation，归属最终意图，排除fixture；旧未标记来源可另选“全部”查看。新标记客服4请求、11调用、**17687实际Token**，未知usage0：

| 意图 | 请求/模型调用 | 实际Token | 单均 | 占比 | 标准刊例CNY估算 | Langfuse USD |
| --- | --- | --- | --- | --- | --- | --- |
| 商品咨询 | 3/9 | 15112 | 5037.33 | 85.44% | 0.0126656 | 0.001895845630 |
| 闲聊 | 1/2 | 2575 | 2575 | 14.56% | 0.0021200 | 0.000317331412 |

总刊例人民币0.0147856元，美元读值0.002213177042。两币种不相加，均非账户账单；价格/汇率版本bigmodel-standard-2026-10-20-ecb-2026-10-19，官方与锁定源码核对见research记录。usage不完整时已知总量保留，单均和完整占比返回N/A。后台飞轮、评估、诊断另外分列。最终截图reference-cost-final.png。

## 评估真实范围

| 轮次 | UUID | 配置 | 完成/错误 | Faithfulness有效分母 |
| --- | --- | --- | --- | --- |
| 原轮1 | 1dca3ee1-5a49-4c60-a82c-7454d49b4be3 | 5f6f500a… | 11/9 | 1.0 / 7 |
| 原轮2 | 3ecfae0f-2897-434f-8ec9-b37df20fc3e4 | 同上 | 12/8 | 1.0 / 8 |
| 修正轮 | fa5625c9-c358-452b-b1b9-434088537b77 | 572498a0… | 20/0 | 0.875 / 18 |

原13条裁判length/空结果与4条answer错误未删除。评估原来没有继承online_reasoning_effort，模型默认max；现在评估显式配置优先，否则继承线上low并进入指纹，保持原模型、各阶段输出预算和0模型重试。E46先做一次原失败裁判定点复验，正常stop、477输出Token；随后完成修正20题。

修正轮：70次GLM、23次嵌入、20次重排，97948实际Token，cleanup.ok=true、已落eval_runs。Recall@5=1.0、Recall@10=1.0、MRR@10=1.0（有效16）；答案要点覆盖0.875（有效16）；Faithfulness0.875（有效18，零claim排除2）；库外拒答1.0（有效4）；可答误拒0.0625（1/16）。

新旧配置/有效分母不同，页面分别画图并警示，没有合并成“质量稳定1.0”。当前只完成一轮修正后完整20，不伪造第二轮。原始逐题报告runtime/eval-pipeline/<UUID>/report.json，页面“查看”链接可读，截图reference-eval-final.png。

## 四信号校准与版本

权重0.5Top1/0.2有效证据数/0.2Top1–Top2分差/0.1条款命中，校准先最小化误放，再降低误拒。只使用原始真实检索采集，按内容hash还原原文；本轮重算外部调用0。

- 校准100：证据充分79、不足21；通过76/79=96.2%，误放0、误拒3。
- 留出200：证据充分159、不足41；通过150/159=94.34%，误放4/41=9.76%，误拒9。留出标签未参与选参。
- 阈值0.2798557313785（页面0.280），当前v3版本fd576454bb9d62b6…；明确型号/带单位数量须有对应。分组互斥、划分hash、冻结数据集/原始规则/原校准样本hash均受检。
- 原v1和本次v2保留。v3修正中英文数量单位及精确数值归一，原v2语义仍可复现。20题付费轮使用v2；对已存20份prompt-citation做v3离线锚点回放，决策20/20相同。它不重问模型、不产生新的评估轮次，也不能替代下一轮真实验收。

路径：runtime/ch09-evidence/reference-calibration/{rule,report}.json、reference-calibration-v2/、reference-final-verification.json。截图reference-calibration-final.png、reference-calibration-scan-final.png。

## 审查、费用与剩余项

[独立后端审查及四项修复](2026-10-20-reference-backend-review.md)。没有待修Critical/Important；原审查不为作者之后的修复背书，修复由RED→GREEN与最终完整回归验证。前端按用户Vibe例外。

累计固定账本：GLM278/280、嵌入383/450、重排367/450（失败计数，重启不清零）。本轮增量88/27/23。没有提高上限、运行收费定时或两轮300题。

剩余质量项：第二轮同新配置完整20、留出4误放与9误拒、Faithfulness0.875，以及原延期Minor F08草稿偶发含忽略注入999的解释性文字（仍需人工核准，未自动发布）。完整质量验收仍受这些事实限制。

[PyCharm步骤](../../ch09-pycharm-acceptance.md) · [逐页验收](../../ch09-manual-acceptance.md) · [功能命令](../../ch09-local-demo.md) · [过程记录](../../../dev-notes/ch09.md)

## 20题质量差错定位（只读诊断）

逐题保存reference-quality-findings.json，没有修改分数或重跑模型：

- A23遗漏一个适用条件（港澳台海外无自营配送），要点覆盖不全。
- C19在已有运输破损流程证据时拒答，缺少48小时/证据材料及补发退款要点，属于误拒。
- C17的转人工承诺被裁判按FAQ无证据判unsupported；D15符合应拒标签，但“现有资料不足”的拒答话术仍被裁判判unsupported。这两项包含产品通用能力或元话术的裁判口径问题，需要人工复核，不能仅据自动分数认定真实业务幻觉。

本轮保持Ch04原指标/裁判合同和原始分数，不为得到1.0而删claim、改标签或改分母。后续复验需要明确新的调用预算及样例范围。

## 最新页面风格调整

用户进一步明确参考图仅供借鉴，页面保持聊天界面的风格。待审与观测两页已统一为浅灰绿、墨绿、圆角和细边框，移除奶油橙色及方格纸；功能、真实数据和上面的质量限制保持不变。本次只读浏览器检查覆盖1265px桌面和468px窄屏待审列表、筛选、原话证据、状态弹窗、成本卡片与表格、评估和阈值曲线；468px页面宽度与视口相等，无整页横向溢出。未发起模型请求或审核写入。

新版证据位于runtime/ch09-evidence/chat-style-{review,review-narrow,dialog,evidence,observability,trends,trend-charts,calibration,calibration-scan}.png。静态JS语法检查和git diff --check通过；本次纯样式调整未重复运行完整后端测试，原完整测试证据仍对应上面的功能实现。
