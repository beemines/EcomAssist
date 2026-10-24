# 第十步 · PyCharm操作与人工抽审

当前实现工作树：`D:/shixi/ecommerce-customer-service/.worktrees/topic-classifier`。
业务解释器：该目录下`.venv/Scripts/python.exe`（Python3.13.5）。
独立训练解释器：该目录下`ml/topic_classifier/.venv/Scripts/python.exe`（Python3.12.13）。
证据、权重和共享预算：`D:/shixi/ecommerce-customer-service/.cache/ch10-evidence`。

## 2026-10-24：按参考流程进入统一验收页

页面沿用聊天界面的浅绿风格，参考图用于组织验收内容。本次只补展示，没有重训、重新标注或改变模型阈值。

1. 打开[后台首页](http://127.0.0.1:8007/admin)，点“进入分类器验收”；也可以[直接进入](http://127.0.0.1:8007/topics/acceptance)。
2. 先看“总览”的九项证据卡。**证据齐备不等于质量通过**；分组已知问题、AI代审来源和整体低分单独标明。上方统计读取当前数据库，报告标明自己的证据时间与模型版本。
3. 点“数据产物”，依次看29/20种子来源、2369冻结原句、1887/295/187分区、143增强、2030实际训练输入、7个epoch的验证曲线与最佳epoch5，以及模型包的大小和hash。权重390.2MiB来自本地真实文件，不是参考图数值。本项目为Transformers CPU8103，没有ONNX产物。
4. 点“评测详情”，默认看全部187条银标。右上“查看范围”可以切到67条有效AI代审测试或34条选定错例，P/R/F1、support与17张混淆矩阵一同切换，分母不混用。向下看在用逐类阈值，以及“买大了想退”的17类真实HTTP概率。
5. 点“错例复核”，看FP多标/FN漏标分布。点“打开34条错例代审结果”可逐项核对原预标、固定模型预测和代审理由；102条已完成的代审不必重新提交，也不冒称独立人工gold。
6. 点顶部“主题分布”，看已命中5/17类，点击类目读脱敏原话；可筛选入池来源。分类输入仍是脱敏原话，标准化FAQ在卡片的“查看归并缺口”中查看；这次改版没有换模型输入。
7. 总览的“打开实时health”会打开8103本地模型状态；“刷新只读状态”只读取当前主题统计，不发起推理、训练或收费调用。页面上的模型报告是带时间的快照，当前模型不同或统计不可用时会明确提示。

本页不包含训练语料或客户原话下载。数据产物的“下载汇总JSON”只下载汇总与产物元数据。完整补齐范围与保留差异见[参考验收对照](superpowers/reports/2026-10-24-ch10-reference-acceptance.md)。

## 当前可验收状态（2026-10-23）

第5次真实HFL全参训练、CPU旁路服务和20条问题池归类已完成。**整体质量尚不足，当前用于功能演示。** 没有第6次训练、合并或推送。

用户本轮明确说“你全部确认就行了”，因此68条测试和34条错例由Codex逐条代审，来源标为“用户授权的AI代审，非人工”，不是用户人审gold。训练用64条实际人工回执仍原样保留，不用重做。

| 范围 | 数量 | Macro-F1 | Micro-F1 | 完全匹配 |
| --- | --- | --- | --- | --- |
| 完整独立合成银标 | 187 | 0.7672 | 0.7606 | 69/187 |
| AI代审测试（排除1条歧义题） | 67 | 0.7451 | 0.7426 | 28/67 |
| 主动筛选的额外错例，不能代表总体 | 34 | 0.5463 | 0.6429 | 5/34 |

8条固定诊断全过，真实HTTP服务中“买大了想退”返回“退换货、尺码”，“不退货,只问尺码”只返回“尺码”。这些诊断不是整体质量分数。完整17类P/R/F1及2×2矩阵、102条代审决定和理由见[只读报告](D:/shixi/ecommerce-customer-service/.cache/ch10-evidence/coverage-v5/reports/ai-review-report.html)。独立标准库整数计数核对结果在同目录ai-independent-audit.json；原silver/预测/阈值hash无变，修订不回流本轮训练。

最终审查还发现本轮训练/验证有1对积分短句近重复，历史验证不能称完全独立。原样保留数据、权重、阈值和分数，追加限制；不会移动题目或自动第6次训练。四项后端修复及裁定见[审查处置](superpowers/reports/2026-10-23-ch10-backend-review.md)。

- [主题分布](http://127.0.0.1:8007/topics)：当前实际问题池29条，20条有效分类、9条未有效分类；问题池来源真实性未核实，不能称29名真实客户。
- [68条测试代审结果](http://127.0.0.1:8010/topics/test-review)：57保留、10改标、1排除。无需再提交。
- [34条错例代审结果](http://127.0.0.1:8010/topics/error-review)：24保留、10改标、0排除。无需再提交。
- [64条训练人工审核](http://127.0.0.1:8010/topics/pilot-review)：真实人工回执0fdf4212…594969，不变。

在主题页点左侧“退换货”等类目看原话；选择“用户反馈没解决”后点“查询”，显示3条池流水、1条有效分类。全部来源SQL与API逐项一致：退换货5、商品信息5、优惠活动2、保修维修1、其他7，其余12类0。默认页长20；实际API用每页2条验证“其他”7条的4页不重复、不漏项。多标签按每个命中分别计数，比例可能超过100%。

最新累计上限600次、10元；已用572次，保守占用2.911919元，包含1条历史未知预留。数据已齐，不消耗剩余28次。实际训练1887原句+143原增强=2030，验证295，独立测试187；训练7轮早停，按验证选epoch5。模型版本`ef4652e363bbb8fabcdf4d5d8a4f4ab946bd0f760c1f160934afceda998e9d29`。原107项历史证据保留。

## PyCharm：只重启现成服务，不再训练或生成数据

当前8007、8010、8103均由本章受管进程运行，可直接访问。需要自行管理时先核对并停止本章对应进程，避免端口冲突；不要直接结束全部Python进程。以下配置的工作目录统一为本文件开头的第十步worktree。

1. 在“运行 → 编辑配置 → + → Python”添加配置，使用“模块名称”，不要把模块路径填进“脚本路径”。
2. **主题模型8103**：解释器选独立训练环境；模块`ml.topic_classifier.cli`；参数如下。此命令只加载已有模型，不训练、不下载、不访问数据库或教师。

```text
serve --bundle D:/shixi/ecommerce-customer-service/.cache/ch10-evidence/coverage-v5/model --host 127.0.0.1 --port 8103
```

3. **本章应用8007**：解释器选业务环境；模块`uvicorn`；参数如下。

```text
app.topics.demo:create_app --factory --host 127.0.0.1 --port 8007
```

环境变量（不填API Key）统一添加：

```text
CH10_ENV_FILE=D:/shixi/ecommerce-customer-service/.env
CH10_TOPIC_PROFILE=D:/shixi/ecommerce-customer-service/.cache/ch10-evidence/coverage-v5/topic-profile.json
CH10_REVIEW_ROOT=D:/shixi/ecommerce-customer-service/.cache/ch10-evidence/coverage-v5
PYTHONUTF8=1
PYTHONIOENCODING=utf-8
```

4. **审核结果8010**：业务解释器；模块`uvicorn`；参数`app.topics.demo:create_review_app --factory --host 127.0.0.1 --port 8010`；同上环境变量。该入口不连接业务库、没有收费后台。
5. 先启动8103，再启动8007；8010只用于查看审核结果。8007演示不恢复历史飞轮、摘要或收费评估，也不启动分类watch，聊天主链路不调用主题分类器。第九步完整后台仍在8006。
6. 点击本章服务的PyCharm红色停止按钮即可停止自己启动的进程；不要停8006或其他章节服务。

在PyCharm终端复验已冻结的20条（以下全部本地，重放不会再新增分类）：

```powershell
$AppPy = '.venv/Scripts/python.exe'
$MlPy = 'ml/topic_classifier/.venv/Scripts/python.exe'
$Evidence = 'D:/shixi/ecommerce-customer-service/.cache/ch10-evidence/coverage-v5'
$env:CH10_ENV_FILE = 'D:/shixi/ecommerce-customer-service/.env'
$env:PYTHONUTF8 = '1'
& $AppPy -m app.topics.cli verify --database configured
& $AppPy -m app.topics.cli run-once --database configured --profile "$Evidence/topic-profile.json" --preview-file "$Evidence/real-batch-preview.json"
# 上一条是dry-run；确认20条既定范围后，以下重放应written=[]、skipped=20
& $AppPy -m app.topics.cli run-once --database configured --profile "$Evidence/topic-profile.json" --preview-file "$Evidence/real-batch-preview.json" --execute
```

3307表结构已实际迁移并verify，不需要重建；禁止为演示删表、清池或重分类旧结果。实际幂等重放前后，原池完整hash、15条工单、58条工具审计及预算文件hash均不变。需要新批次时另行明确范围；本次不自动扩到其余9条。

## 以下为历史过程记录（不代表当前运行状态）
## 第4次训练与人审记录（已完成、未发布）

2026-10-23记录：基线、第二轮、一次本地采样对照及否定语义修复，共4次真实GPU全参训练均已完成。本轮187条新合成独立测试Macro-F1=0.9787、Micro-F1=0.9794、完全匹配177/187，CPU重加载最大差0；但“买大了想退”仍漏尺码，否定句仍误报退换货，固定8条诊断只过5条，保持未发布。8103和真实批量入库尚未验收，不用规则或调测试阈值冒充修好，原各轮数据/权重/报告均保留。

该轮结束时累计500/500次、保守预算占用约2.775101元，含1条历史未知预留；当时在请求上限停止。该轮64条训练对照人审、冻结、一次重训和独立测试均已完成。最新追加授权见本文开头，不修改这段历史计数。

[8009的64条新训练对照](http://127.0.0.1:8009/topics/pilot-review)已全部确认原标签，修改0、排除0，回执`022b4583…6626a67`已核实；本页保留供查看，不用重做。数据冻结后为训练原句1823条、原增强143条、验证263条、新独立测试187条，旧已暴露测试不混入本次独立测试。

本轮[68条测试题](http://127.0.0.1:8009/topics/test-review)和[4条额外错例](http://127.0.0.1:8009/topics/error-review)也已实际提交：全部接受原标签，改标0、排除0，不用再做。人工gold的Macro-F1=0.9636、Micro-F1=0.9641、全标签正确62/68；额外4条是主动筛出的错例，0/4不能代表整体准确率。完整人工报告在`D:/shixi/ecommerce-customer-service/.cache/ch10-evidence/negation-v4/reports/human-metrics.html`，原silver/预测/阈值均保留，未回流训练或重调阈值。

只读复盘发现关键组合训练/验证覆盖缺口及过宽的验收家族隔离，详见`docs/superpowers/specs/2026-10-23-topic-classifier-data-design-review.md`。据此形成并获批本文开头的新修复范围；该轮模型继续保持未发布。

## 第二轮人审已完成（2026-10-23）

已验证实际网页回执：测试68条和额外错例8条均接受原预标，修改0条、排除0条。这里“通过”指认可标准标签，不代表模型回答正确。

| 报告范围 | 数量 | Macro-F1 | Micro-F1 | 全部标签完全正确 |
| --- | --- | --- | --- | --- |
| 人工确认的测试子集 | 68 | 0.9675 | 0.9746 | 63/68（92.65%） |
| 原完整合成silver留出集 | 186 | 0.9706 | 0.9711 | 173/186（93.01%） |

额外8条由错误筛选而来，不能用它的分数代表总体；你确认了这8条的原标准标签，8条模型预测仍未完全正确。所有测试题均为合成句，不能把人审子集说成真实客户数据测试。每类人审正例只有3至8条，注意小样本限制。

可直接打开本机的[第二轮人工指标与错例报告](D:/shixi/ecommerce-customer-service/.cache/ch10-evidence/remediation-v2/reports/human-metrics.html)，含17类指标、混淆矩阵、13条已确认错误及验收结论。机器证据分别为`reports/gold.json`、`error.json`、`human-complete.json`；原`silver.json`中的pending属于当时冻结状态，以追加的human-complete为人审完成依据，不覆盖历史文件。

独立验收句“买大了想退”仍只输出“退换货”，缺“尺码”，所以模型仍未发布，不能启动正式8103或将它写入真实分类表。本次finalize只追加报告，未改数据、模型、阈值或首轮记录。逐项从实际人审标签和冻结预测重新计算，核对了17类矩阵、Macro/Micro-F1、完全匹配、Hamming loss与空预测率。

已记录的覆盖诊断：1902条训练样本只有154条4–16字短句；199条验证只有5条短句；11条尺码+退换货训练组合均带“码”字。这说明现有验证和训练对隐含短语组合的覆盖有限，并非已经证明下一轮重训会解决。两份复核结果不回流本轮训练或重调阈值。

## 已批准的一次本地采样对照

用户已明确批准“批准一次本地对照，额度不变”。仅改变现有训练数据的抽样：每epoch仍1902次，其中571次来自原154条短句、1331次来自原1748条长句，短句比例约30%。不会新造语料或改标签；全参底座、固定seed、最多8轮、验证选模和验证阈值流程保持原样。各轮索引hash在训练前冻结，默认train命令仍用原策略，只有显式`--short-sampling-control`开启这次对照。

本地输出独立保存于`D:/shixi/ecommerce-customer-service/.cache/ch10-evidence/sampling-control-v3`；`scope.json`绑定批准范围、抽样序列和49项旧文件SHA，`training/sampling.json`记录定额。此次完整ML回归61项通过；实际GPU全参8轮完成（440.797秒），原验证选出epoch8、Macro-F1@0.5=0.9939148。

实际CPU诊断8条通过7条：“买大了想退”输出退换货+尺码（尺码概率0.655），买小/太大想换的组合也通过；“不退货,只问尺码”仍多报退换货（概率0.820）。因此继续保持未发布。

| 已暴露回归范围 | 第二轮候选 Macro-F1 | 本地对照 Macro-F1 | 本地对照全部标签完全正确 |
| --- | --- | --- | --- |
| 原186条合成题 | 0.9706 | 0.9722 | 173/186（与原候选相同） |
| 原68条人审子集 | 0.9675 | 0.9675 | 63/68（与原候选相同） |

看[本地采样对照报告](D:/shixi/ecommerce-customer-service/.cache/ch10-evidence/sampling-control-v3/reports/comparison.html)，完整17类矩阵在同目录comparison.json。回归只有5条预测变化：2条完全修复、2条新变错、1条仍错但少一个误报，详见regression-delta.json。例如原来正确的“密码怎么改,积分在哪看”现在漏账号，“到货就裂了,运费还得我担?”现在漏质量问题；不能只凭必测句改善就说整体问题已修好。

这些只是已暴露回归，不能宣称新独立测试；诊断句成功也不会直接发布或写真实分类表。独立重算17类矩阵/总体指标通过，49项旧文件SHA全部未变。仍累计442/450次、最多10元，本地训练不调用付费API。此批准范围的一次训练已结束，不自动开第四次训练或修改前两轮输出。

### 下一轮修复范围（2026-10-23已批准）

用户明确回复“批准该范围，累计500次仍最多10元”。已追加500审批文件，原SQL和300/400/450审批SHA不变，当前仍442次/保守占用2.622487元；尚未新付费或重训。以下是本轮绑定的范围。

本地对照验证了提高短句采样可以改善关键组合，但现有验证集短句仅5条、缺少短否定场景，继续只看高验证分数不足以决定发布。建议在现有数据/训练流程内做一次有界修复：

- 新造约64组训练对照：肯定/否定、多个同时诉求、取消一个诉求后保留另一个；覆盖不同主题，不把已暴露的8条诊断句或语义近似家族放进训练。先在网页人工核对这64条，不能默认相信教师。
- 原199验证保留，补约64组独立短句验证；原训练和143增强仍保留。新版本单独冻结并核验分组、标签覆盖和比例，不改旧文件。另建约187组真正新留出，各类至少10正/负例组，旧208/186题都只作回归。
- 只向原智谱标准API发送本章新合成短句与17类术语表，生成与预标分别计账；不发新增客户原话、历史会话或检索快照。预计约40次物理请求，含无效项余量建议累计上限450→500，金额仍严格不超过10元、旧442次/未知预留保留。没有这项新授权就不执行收费调用。
- 仅再训练一次，HFL全参、30%短句采样、固定seed和最多8轮不变；按补充后的验证选模及阈值，不用新测试挑模型。新版留出仍需68条网页人审和至多34条额外错例；这不是要求重做已完成的76条。
- 必测及否定/近邻诊断实际通过、独立留出和人审完成后，才继续CPU导出、8103与3307旁路验收。不保证一次补数就能解决，不自动追加第五次训练、提高费用或换技术栈。

此范围现已批准，先准备64条训练对照交给用户实际人审；在这份真实人审回执之前不开始重训。旧76条复核不重做。

## 当前第二轮复核入口

- [第二轮8条错例](http://127.0.0.1:8008/topics/error-review)
- [第二轮68条测试复核](http://127.0.0.1:8008/topics/test-review)

两页已完成提交，保留供查看，不必重复复核。以下是原操作说明：正确点“通过”，有错点“修改标签”，不采用点“排除”。页面底部填一次昵称、勾选已逐条核对声明，再点“确认提交并保存”，两页分别提交。边界不清的题可以排除并填原因，不用强行同意教师预标。结果只追加人工报告，不回流本轮训练或重调阈值。

第二轮证据在`D:/shixi/ecommerce-customer-service/.cache/ch10-evidence/remediation-v2`，其中`reports/metrics.html`是17类F1和矩阵，`reports/implicit-size-diagnosis.json`是固定模型对照，不是训练语料。旧8007入口和首轮报告不覆盖。

8008是专用审核服务，不加载模型/Key、不连数据库、不提供聊天。若需在PyCharm重启，先确认8008已停止；选择业务解释器和本工作树，模块名称`uvicorn`，参数：

```text
app.topics.demo:create_review_app --factory --host 127.0.0.1 --port 8008
```

环境变量只需`CH10_REVIEW_ROOT=D:/shixi/ecommerce-customer-service/.cache/ch10-evidence/remediation-v2`、`PYTHONUTF8=1`、`PYTHONIOENCODING=utf-8`。当前服务已启动，不要再起第二份。

## 首轮复核入口与原操作记录（保留）

1. 打开[测试集人工复核](http://127.0.0.1:8007/topics/test-review)，这是新的68条，不是已经提交过的首批训练抽审。
2. 看每句的“预标标签”；正确点“通过”，有错点“修改标签”勾选全部正确标签，不采用点“排除”。旁边“固定模型预测”供对照，不能把模型输出当作标准答案。
3. 到页面底部填一次昵称，勾选逐条核对声明，再点“确认提交并保存”。如果已经逐条看过且剩余都对，可先点“已核对的其余样本通过”，再提交。
4. 同样完成[6条额外错例复核](http://127.0.0.1:8007/topics/error-review)。这6条与上述68条不重复；68条中也可能有预测错误。
5. 两页显示提交成功后告诉助手。结果只保存本机，不能自动改模型、阈值或训练集。助手据实际回执生成gold与错例报告，不能代替人审。

首次真实报告在`D:/shixi/ecommerce-customer-service/.cache/ch10-evidence/reports/metrics.html`，含17类F1和混淆矩阵；`silver.json`明确全测试来自合成题，gold未提交前保持pending。`probe.json`保留漏标签失败，`cpu-roundtrip.json`记录导出前后一致。不要删除或覆盖这轮文件。

后端已经实现如下本地命令，只有完成对应门槛才执行：

```powershell
# 两包真实人审提交后：只追加独立人工报告，候选失败时不会生成可发布模型
& $MlPy -m ml.topic_classifier.cli finalize --reports "$Evidence/reports" --bundle "$Evidence/model" --review-root "$Evidence"
# 只有模型通过CPU/probe且具备完整人审发布清单后才能启动；当前候选会被拒载
& $MlPy -m ml.topic_classifier.cli serve --bundle "$Evidence/model" --host 127.0.0.1 --port 8103
```

上述变量的逐行定义见下文“先看预算和快照”。当前不要重跑expand/augment/train；首次产物已冻结，修复提案另行审批并使用新版本目录。下文保留首次实施操作以便追溯，旧的“尚未训练”描述属于当时基线。

## 模型发布通过之后的旁路命令（当前先不执行）

在PyCharm里新建本地`$Evidence/topic-profile.json`，只放下面三项；路径改成最终实际发布目录，不放Key。此文件不提交Git：

```json
{
  "service_url": "http://127.0.0.1:8103",
  "manifest_path": "D:/shixi/ecommerce-customer-service/.cache/ch10-evidence/model/manifest.json",
  "runtime_root": "D:/shixi/ecommerce-customer-service/.cache/ch10-evidence/runtime"
}
```

先确认8103实际服务health返回正确模型版本，再依次执行。下面是已实现的接口，当前候选失败时会拒绝；不表示已完成真实入库验收。

```powershell
$Profile = "$Evidence/topic-profile.json"
# 第一次只预览建表；确认目标是本项目3307业务库再执行新增表及四列，不改原问题池
& $AppPy -m app.topics.cli migrate --database configured
& $AppPy -m app.topics.cli migrate --database configured --execute
& $AppPy -m app.topics.cli verify --database configured
# 冻结最多100条的ID/高水位/脱敏文本/原文hash/模型版本，供执行前复核
& $AppPy -m app.topics.cli preview --database configured --profile $Profile --from-id 1 --limit 100 --output "$Evidence/batch-preview.json"
# 无execute只检查范围；加execute才调用本机分类器并写topic_classifications
& $AppPy -m app.topics.cli run-once --database configured --profile $Profile --preview-file "$Evidence/batch-preview.json"
& $AppPy -m app.topics.cli run-once --database configured --profile $Profile --preview-file "$Evidence/batch-preview.json" --execute
```

同一preview重放不会重复插行；原话hash、模型版本或数据库身份变化会拒绝。未过阈值、不合法和长句保留明确失败回执，不塞进“其他”。只有已发布模型会成为主题页当前统计版本。

需要长期攒够20条才起批时，下面命令默认仍是dry-run；明确加`--execute`才常驻，Ctrl+C结束。每批最多100条，连续3个故障回合持久暂停；业务低置信度不按网络故障自动重试。

```powershell
& $AppPy -m app.topics.cli watch --database configured --profile $Profile --from-id 1 --limit 100
# 确认范围后才执行：在上一行末尾加 --execute
# 对已核对的失败范围显式解除暂停，不扩大范围、不重新归类已有旧模型结果
& $AppPy -m app.topics.cli retry --database configured --profile $Profile --preview-file "$Evidence/batch-preview.json" --execute
# 需要更新旧版本结果时，另建有明确范围的preview，再显式执行reclassify
& $AppPy -m app.topics.cli preview --database configured --profile $Profile --from-id 1 --to-id 31 --limit 100 --reclassify --output "$Evidence/reclassify-preview.json"
& $AppPy -m app.topics.cli reclassify --database configured --profile $Profile --preview-file "$Evidence/reclassify-preview.json" --execute
```

8007加载最终统计版本时，在原PyCharm演示运行配置环境变量增加`CH10_TOPIC_PROFILE=D:/shixi/ecommerce-customer-service/.cache/ch10-evidence/topic-profile.json`，仅重启本章8007。打开[主题分布](http://127.0.0.1:8007/topics)，点击类目看分页原话，已有归并缺口可跳转审核页。页面GET不会启动分类、训练或教师调用。

## 在PyCharm打开正确工作树

1. 菜单“文件 → 打开”，选择上述`topic-classifier`目录。不要在旧第八/九步工作树运行本章命令。
2. “设置 → 项目 → Python解释器 → 添加现有解释器”，先选择业务`.venv/Scripts/python.exe`。
3. “运行 → 编辑配置 → + → Python”，选择“模块名称”，工作目录填工作树完整路径。普通数据命令模块是`app.topics.data_cli`。
4. 环境变量添加`CH10_ENV_FILE=D:/shixi/ecommerce-customer-service/.env`、`PYTHONUTF8=1`、`PYTHONIOENCODING=utf-8`。只填环境文件路径；不要把Key复制进文档、聊天或截图。
5. 本章训练命令使用第二个解释器；不要往业务解释器装Torch。已有8006第九步服务保持原样。

## 先看预算和快照

PyCharm底部“终端”选PowerShell，逐行执行：

```powershell
Set-Location 'D:/shixi/ecommerce-customer-service/.worktrees/topic-classifier'
$AppPy = '.venv/Scripts/python.exe'
$MlPy = 'ml/topic_classifier/.venv/Scripts/python.exe'
$Evidence = 'D:/shixi/ecommerce-customer-service/.cache/ch10-evidence'
$env:CH10_ENV_FILE = 'D:/shixi/ecommerce-customer-service/.env'
$env:PYTHONUTF8 = '1'
$env:PYTHONIOENCODING = 'utf-8'
& $AppPy -m app.topics.data_cli budget-status
```

共享账本已初始化，勿再运行`budget-init --execute`，没有重置命令。`used_micro / 1000000`是保守预算占用，含未知请求预留，不等同于供应商实际扣费。金额硬上限10元；物理次数由300次经两次明确批准增至400、450次，均为同一累计账本。原审批与记录全部保留，重启不清零。

首次扩量与增强已完成，无需再次执行；累计392/400次，保守占用约2.507389元。只读查看可在项目工作目录运行（免费，不调用模型）：

```powershell
& .venv/Scripts/python.exe -m app.topics.data_cli budget-status
& .venv/Scripts/python.exe -m app.topics.data_cli corpus-status --corpus D:/shixi/ecommerce-customer-service/.cache/ch10-evidence/corpus
```

`$Evidence/pool/preview.json`和`snapshot.json`已保存29行有界只读快照，高水位31，原文去重21问。所有来源真实性均未核实；本地原话文件含隐私，不能提交Git。快照不会修改问题池，也不会自动发送模型。

## 首次小批抽审包的历史操作（已完成，不重跑）

先免费预览：

```powershell
& $AppPy -m app.topics.data_cli pilot --snapshot "$Evidence/pool/snapshot.json" --output "$Evidence/pilot"
```

执行版本增加`--execute`，会使用10元共享账本并向标准智谱API发送经过本地复查的单句与术语表，也会生成合成题；不发送会话历史、检索快照和数据库凭据。用户现已明确允许本批最多20条去重脱敏单句发送到`https://open.bigmodel.cn/api/paas/v4/chat/completions`，使用`glm-5.3-flash`；该授权不代替后续人工抽审。

```powershell
& $AppPy -m app.topics.data_cli pilot --snapshot "$Evidence/pool/snapshot.json" --output "$Evidence/pilot" --execute
```

每个收费阶段会先留下检查点。已完成阶段重跑会复用；未完成、失败或范围变更会拒绝自动重复调用。不要删除journal或预算文件来“重新开始”。报错时先看安全错误代码和`budget-status`。

结构失败的响应会保存在本地私有`pilot/diagnostics/`，便于修复后离线重验，不提交Git。需要重新请求时，仅可在查明原因后显式指定`--retry-failed-stage`和`--retry-reason`恢复一个同范围failed阶段，原失败回执另行留存；in_flight不能用此方式重发。此选项不用于连续盲试，也不重置预算。

## 在页面里点选审批（推荐）

当前包已实际生成：68条、17类齐、32条多诉求；20条池句来源真实性未核实、48条合成。包hash为`6cb5bbbdaa3944feba577efd47e9a1e0b43d8b96f82dc80d2eda337d334b4225`，尚未人工审阅通过。文件在`D:/shixi/ecommerce-customer-service/.cache/ch10-evidence/pilot/`：

- [本机审核页](http://127.0.0.1:8007/topics/pilot-review)：直接点选并保存。无需逐条发聊天消息，也无需手填JSONL或时间。
- `pilot/review.html`：可离线点选、导出JSONL的备用页；文件页不能直接写回本机。建议从页内链接进入上面的本机审核页再操作。
- `pilot/decisions.jsonl`：初始68条仍未决定；只有你完成审核并提交，页面才会写入决定、署名和实际时间。
- `pilot/coverage.json`：实际是否达到68条、17类覆盖和至少17条多诉求。未满足就保留缺项，不能口头当通过。
- `pilot/pack.json`与`journal/`：冻结机器材料。不要改id、pack_hash、问题原句或机器材料。

操作顺序：

1. 启动本章8007演示（本文末尾有PyCharm运行配置），打开上述本机审核页。
2. 从第1条往下看，核对“问题”和“预标标签”。标签正确可点“通过”；需要调整点“修改标签”，勾选最终全部标签后点“保存标签”；不采用的点“排除”。误操作可点“撤回”。
3. 为减少点击，正确样本可以先不逐条点通过：看完全部68条，勾“我已逐条核对全部样本，认可以上审核结果”，再点“已核对的其余样本通过”。先前修正/排除的项不会被覆盖。未看的不能算通过。
4. 底部“审核署名”只填一次昵称，点“确认提交并保存”。页面显示“审核已保存”及保留/排除数，才表示落盘成功。
5. 结果自动保存为`pilot/decisions.jsonl`和`pilot/review-receipt.json`；刷新会显示同一回执。按钮不会调用模型或开始训练。浏览器草稿只保存在当前浏览器及同一地址中，换浏览器或从文件页切到HTTP页不会自动迁移。

不需要逐条发sample_id。提交后只需告诉助手“审核已提交”，助手读取真实回执继续；仅说“继续”不代替审核。若保存失败，可点“导出备份”，保留下载文件，不要删除原包或预算账本。

标签只能取17类权威表的名称；“其他”不能与其他标签同时出现。不要替模型猜没有说出的诉求。例如“XL还有货吗”只问库存，“不要退，只想修”只标保修维修。“买大了想退”是保留的验收probe及其近重复，不进入训练集。

### 手动导入备用方式

只有使用离线导出时才需要本段。导出的`decisions-reviewed.jsonl`已经包含署名和时间，无需再手填；把下方`--decisions`参数指向实际下载文件即可。人工手改JSONL时字段含义：

| 字段 | 怎么填 |
| --- | --- |
| decision | 标签正确填`"accept"`；需改标签填`"correct"`；不应使用填`"exclude"` |
| final_labels | 接受时保留现有数组；修正时写最终全部标签；排除时写`[]` |
| reviewer | 填你自己的审核署名，不能空着 |
| reviewed_at | 填带时区的时间，如`"2026-10-21T20:00:00+08:00"`，应使用实际审核时间 |
| notes | 纠偏、疑难或排除原因；无则保留空字符串 |

导入前先仅验证：

```powershell
& $AppPy -m app.topics.data_cli review-import --pack "$Evidence/pilot/pack.json" --decisions "$Evidence/pilot/decisions.jsonl" --output "$Evidence/pilot/review-receipt.json"
```

没有报错且接受/排除数量正确，再增加`--execute`保存回执。已在网页提交的不用再导入。缺样本、重复ID、空审核人、默认同意、错hash和无时区时间都会拒绝。导入不调用收费模型。

也可在聊天明确回复“我已逐条审阅这个包，全部通过”，或按sample_id列出修正/排除项，由助手据你的实际决定填写回执。仅说“继续”不算人工抽审。扩量训练仍等待这份真实回执；后端旁路开发可以继续。

## 当前可复验的本地基线

模型底座与一次完整GPU优化器探测已完成，结果在`$Evidence/doctor.json`；探测权重已丢弃，训练将重新加载底座。

```powershell
& $AppPy -m pytest tests/test_topic_contracts.py tests/test_topic_cleaning.py tests/test_topic_budget.py tests/test_topic_teacher.py tests/test_topic_review_receipts.py -q --basetemp='.cache/ch10-tests/manual'
& $MlPy -m pytest ml/topic_classifier/tests/test_doctor.py -q --basetemp='.cache/ch10-tests/manual-ml'
```

这些命令不产生收费请求。训练、评测、serve、业务库实际迁移、批量归类与主题页的操作将在实际实现和验证后补入，不把尚未实现的命令写成可用验收流程。

## 已实现的表结构预检（不执行迁移）

以下命令只读，当前3307尚无topic_classifications表，输出stage=missing、preview=true、applied_count=0：

```powershell
& $AppPy -m app.topics.cli migrate --database configured
```

原DDL在`sql/ch10-ddl.sql`，四个nullable追溯字段在`sql/ch10-runtime.sql`；3308自有fixture已验证迁移、默认RESTRICT外键、question_id唯一性、旧行四列NULL及ORM往返。暂不对3307执行迁移或真实批量归类；原问题池保持原样。

## 当前可打开的主题页（模型尚未训练）

本章演示已启动：[主题分布](http://127.0.0.1:8007/topics)。当前显示实际问题池29条；选择“用户反馈没解决”后点“查询”，显示3条。当前有效分类和待复核显示“—”，原因是实际模型尚未训练/配置，不能把它们当作0条。17个主题暂时不可点；实际训练、服务、批次完成后才能验收非空分布和分页。

PyCharm重新启动本章页面：工作目录选择第十步worktree，解释器选择业务`.venv/Scripts/python.exe`，运行配置“模块名称”填`uvicorn`，参数填：

```text
app.topics.demo:create_app --factory --host 127.0.0.1 --port 8007
```

环境变量填`CH10_ENV_FILE=D:/shixi/ecommerce-customer-service/.env`、`PYTHONUTF8=1`、`PYTHONIOENCODING=utf-8`。启动前确认8007没有其他进程；当前演示仍在运行时，不要再启动第二份。`CH10_TOPIC_PROFILE`在实际模型包就绪后再填三字段JSON路径，不放API Key，不用空壳manifest伪装模型。

这个入口不恢复飞轮消费、摘要历史或收费评估，不启动分类Worker；审核页只读，完整第九步审核与评估仍在原[8006后台](http://127.0.0.1:8006/review)。主题页刷新仅发送GET。点击已有归并缺口链接可到`/review?review_id=...`查看，未归并的原话不造链接。
