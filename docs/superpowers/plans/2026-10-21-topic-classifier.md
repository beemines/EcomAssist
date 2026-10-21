# Chapter 10 Multilabel Topic Classifier Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 用指定RoBERTa全参训练可追溯的17类多标签模型，旁路批量归类问题池并显示主题分布。

**Architecture:** 业务环境负责脱敏、受预算控制的教师调用、MySQL批处理和统计；独立Python3.12环境负责分层数据、训练、评测和CPU推理HTTP服务。两侧共享轻量术语/数据契约，训练和推理库不进入业务主环境，实时对话不调用分类器。

**Tech Stack:** HFL chinese-roberta-wwm-ext；torch2.14.1+cu130、transformers5.20.2、accelerate1.15.0、numpy2.5.4、scikit-learn1.9.1、iterative-stratification0.1.9、safetensors0.8.0；现有FastAPI0.142.2、Pydantic2.13.5、HTTPX0.28.1、SQLAlchemy2.0.54、MySQL。

**Spec:** [2026-10-21-topic-classifier-design.md](../specs/2026-10-21-topic-classifier-design.md)，用户已批准首版`bb89ce0`。用户已批准本计划`ce10a63`，选择Native顺序执行及第十步隔离工作树；实际进度追记于dev-notes/ch10.md。

## Global Constraints

- 固定使用哈工大讯飞 `hfl/chinese-roberta-wwm-ext` 全参数微调，不使用LoRA/QLoRA，不做embedding或意图模型微调。
- 权威顺序：退换货、物流、尺码、发票、质量问题、运费、优惠活动、价保、支付、订单修改、库存补货、商品信息、保修维修、账号、会员积分、评价、其他；其他与前16类互斥，模型低把握独立为needs_review。
- 目标是清洗去重后约2040个原始问题组（增强前）；至少25%多标签，每类至少100个正例组；train/validation/test目标80/10/10，偏差最多3个百分点，验证/测试各类正反例均至少10。
- 先68条小批人工抽审再扩量；测试冻结后另抽68条人审、最多34条错例复核。小批同义家族只进训练；测试不调参、不删失败样本。
- 造数、预标注及其修复/重试累计最多人民币10元，账本独立于第九步，重启不清零；最多300次物理尝试，连续3次失败暂停。
- 教师glm-5.3-flash、reasoning_effort=low、输出8192、每批最多16；不改现有线上模型/预算，不运行第九步收费评估。
- 训练最大128 token、micro-batch4、累积4、FP16/检查点、AdamW 2e-5、weight decay0.01、warmup10%、最多8 epoch、早停patience2/改善0.001；只验证选epoch/阈值。
- Worker每60秒检查、起批20、最大64；本章实际验收冻结最多100条现有池记录，不造业务池数据。主聊天路径不注册此工具、不触发此worker、不写topic_classifications。
- 原DDL保留，独立补充model_version/taxonomy_version/input_hash/batch_id四列；唯一question_id及原FK删除语义保持。
- 产品依赖、权重、GPU训练、付费调用和数据库迁移须在本计划批准并选择执行方式后开始。按用户例外：数据/Prompt/训练用标注和评估验证；前端Vibe，不套前端TDD或code review。
- API实现前先读本章research记录和对应锁定源码；未覆盖的具体接口先查官方文档/锁定源码再编码，记录来源，沿用本章已批准的Context7替代方式。
- 每项任务验证后立即追记dev-notes/ch10.md并提交。后端Native推荐，最终独立整分支审查；不把本计划自检称独立审查。

## Review Focus

1. 含姓名/运单/详细地址的原句，以及带“验收”字样的正常问题：保护身份而保留尺寸/金额/否定，真实性不靠关键词猜；Task2测试。
2. 两个进程同时预留、发出后进程崩溃、结构错误但已计费：费用不能丢或重复释放，预算按物理尝试；Task3测试。
3. 同义题跨来源、pilot固定训练、金标事后修订：不能跨集合泄漏或用测试修订重调阈值；Task5/7验证。
4. 包文件损坏、空预测、NaN概率及过长多诉求：拒绝无效结果而保留待复核，不输出其他假成功；Task8测试。
5. 推理中原话被编辑、锁丢失、切换模型及提交后崩溃：不覆盖错误问题、不重复落表，页面不把旧结果混入当前统计；Task9/10测试。

## 文件边界与运行约定

| 文件组 | 职责 |
| --- | --- |
| config/topic-taxonomy.json；app/topics/taxonomy.py、types.py | 唯一17类权威表与两环境共享的轻量契约 |
| app/topics/cleaning.py、snapshot.py、reviews.py | 脱敏快照和人审回执，保持来源 |
| app/topics/budget.py、teacher.py、prompts.py、data_cli.py | 持久费用许可、教师预标与造数编排 |
| ml/topic_classifier/pyproject.toml、uv.lock、doctor.py、data.py、train.py、evaluation.py、artifacts.py、service.py、cli.py | 独立依赖及科学计算/服务，模块从仓库根运行 |
| app/topics/profile.py、migration.py、repository.py、batch.py、receipts.py、statistics.py、cli.py | 轻量业务旁路与只读统计；不引入torch |
| app/api/topics.py；app/main.py；app/topics/demo.py | 后台路由、可选依赖注入、独立演示配置 |
| app/static/topics.html/js/css；现有review-queue.html导航 | 沿用聊天风格的页面；Vibe例外 |
| sql/ch10-ddl.sql、sql/ch10-runtime.sql；app/db/models.py | 原DDL及四列补充迁移、ORM映射 |
| docs/ch10-pycharm-acceptance.md；docs/superpowers/reports/2026-10-21-ch10-delivery.md | 实际命令、人工步骤和有证据的交付范围 |

全部命令从执行时选定的仓库工作树根目录运行。`$Repo`表示该实际工作树；`$AppPy`为该树业务虚拟环境或已核对的主仓库业务解释器；`$MlPy`为`$Repo/ml/topic_classifier/.venv/Scripts/python.exe`。不要用裸python猜环境。

业务data_cli、topics.cli和demo均读取显式`CH10_ENV_FILE`路径并调用既有`load_settings(env_file=...)`，不要求把主仓库.env复制到工作树；`CH10_TOPIC_PROFILE`指本章本地profile JSON，CLI也允许显式--profile覆盖非秘密配置。两项环境变量只由本章入口读取，不往旧Settings的dotenv添加未知键，不输出文件内凭据。

本章固定共享运行目录建议`D:/shixi/ecommerce-customer-service/.cache/ch10-evidence`（既有.cache忽略规则已覆盖），跨工作树只使用这里同一本`budget.sqlite3`；目录含账本/人审/权重，不得作为普通临时缓存清理。`$Evidence`指这个绝对路径。数据不写进Git或static目录。实现创建目录与初始化预算时记录授权身份ch10-topic-20261021，不提供reset命令。

### Task 1: 术语契约与真实模型运行基线

**Files:** 创建config/topic-taxonomy.json；app/topics/{__init__,taxonomy,types}.py；ml/topic_classifier/{__init__,pyproject.toml,uv.lock,doctor.py}；tests/test_topic_contracts.py；ml/topic_classifier/tests/test_doctor.py。

**Interfaces:** `load_taxonomy(path: Path) -> Taxonomy`，含ordered_names/version/digest；types.py定义`LabelledSample(id,text,labels,origin,group_id,source_question_ids,pilot)`、`Prediction(id,labels,probabilities,status,model_version,taxonomy_version)`、`ModelIdentity(model_version,taxonomy_version,taxonomy_hash,cleaning_version,max_tokens)`，ID均为字符串，probabilities为17个有限0..1值。`doctor(base_dir: Path, *, probe: bool) -> dict`。

Consumes：已批准spec及官方固定源码；Produces：后续任务共用的上述类型、术语加载器和实际可运行的ML解释器。

- [ ] 写契约失败用例test_taxonomy_order_and_reject_unknown：17类顺序等于设计原表，未知/重复标签、布尔概率、其他与业务类并存拒绝；运行`& $AppPy -m pytest tests/test_topic_contracts.py -q`确认RED。
- [ ] 实现轻量术语与类型，不在app/topics/__init__.py导入模型/数据库。对标注样例断言“买大了想退”的多热向量第0和2位为1，其余0；这是标签契约，不是效果成绩。运行同命令确认GREEN。
- [ ] 创建独立非安装式工具项目，Python==3.12.13、表头精确依赖；torch仅来自官方cu130显式源，其他依赖PyPI，FastAPI/Pydantic/HTTPX/Uvicorn沿用主项目版本；dev依赖pytest。执行`uv lock --project ml/topic_classifier --python 3.12.13`再`uv sync --project ml/topic_classifier --locked --group dev`；记录完整lock hash，不安装vision/audio/all extras。解析冲突停止，不静默改固定技术。
- [ ] 先核对锁定huggingface-hub下载API，再下载HFL revision `5c58d0b8ec1d9014354d691c538661bf00bfdb44`的必要PyTorch/tokenizer文件；记录SHA/字节数。doctor验证CUDA可用、全参可训练、多标签float/BCE、128长度，按正式优化器做一个小批前后向及optimizer step以分配真实Adam状态，记录峰值显存；probe权重不作为训练起点或导出物。命令`& $MlPy -m ml.topic_classifier.doctor --base-dir "$Evidence/base" --probe`；预期全参参与、loss有限、实际GPU/版本与峰值有记录。OOM按设计减micro-batch维持有效16，最终失败则暂停。
- [ ] `& $MlPy -m pytest ml/topic_classifier/tests/test_doctor.py -q`验证配置及安全加载错误；追记实际安装/下载/探测结果与翻车，提交`feat(ch10): establish topic model contracts and runtime`。不声明完成训练。

### Task 2: 脱敏及有限问题池快照

**Files:** 创建app/topics/{cleaning,snapshot,data_cli}.py；tests/test_topic_cleaning.py；tests/integration/test_topic_snapshot.py。

**Interfaces:** `clean_question(raw: str, *, sample_id: str) -> CleanQuestion(sample_id,text,input_hash,edits,quarantine_reasons)`；`async preview_pool(database: Database, *, from_id: int, to_id: int | None, limit: int) -> SnapshotPreview`；`async export_pool(database: Database, preview: SnapshotPreview, output: Path) -> PoolSnapshot`。Preview含数据库身份/高水位/有界ID/hash，Snapshot含preview及每条的source、origin、CleanQuestion，origin默认unverified。

Consumes：Task1轻量契约与现有Database；Produces：清洗结果和本地冻结快照，供Task4/5使用；snapshot子命令也供最终PyCharm手册使用。

- [ ] 写失败测试：脱敏手机号/地址但保留“XL、39.9元、不要退”；歧义身份隔离；“验收运费怎么算”不自动标真实或删除。测试预览限1..100、范围变化拒绝execute、重复同轮ID仍保留追溯。运行`& $AppPy -m pytest tests/test_topic_cleaning.py -q`确认RED。
- [ ] 实现本地清洗/UTF-8原文hash、preview→execute的同范围校验，使用既有Database短只读会话，不改原表。日志仅安全ID和计数，原始文本只进本地受控快照；输出疑难隐私清单供检查，不自动发给教师。
- [ ] 用署名的合成样例核对清洗前后意思/否定和多诉求，保存清洗审计。运行上述单测GREEN及`& $AppPy -m pytest tests/integration/test_topic_snapshot.py --run-mysql -q`；集成仅3308自有fixture，验证快照不写库。
- [ ] 增加data_cli snapshot子命令：`snapshot --database configured --from-id 1 --limit 100 --preview --output "$Evidence/pool/preview.json"`，随后` snapshot --database configured --preview-file "$Evidence/pool/preview.json" --execute --output "$Evidence/pool/snapshot.json"`形成冻结快照；核对身份/高水位，不输出客户原话到终端/提交，不向外发。来源判断不确定保留unverified，实际客户题为零须如实标记。
- [ ] 追记快照行数、去重、来源核实状态与路径，提交`feat(ch10): snapshot and sanitize flywheel questions`。

### Task 3: 跨进程10元硬预算及教师传输

**Files:** 创建app/topics/{budget,teacher,prompts}.py；扩展data_cli.py的budget-init/budget-status子命令；tests/test_topic_budget.py、tests/test_topic_teacher.py。

**Interfaces:** `BudgetLedger(path: Path, approval_id: str)`；`reserve(stage: str, payload_hash: str) -> Reservation`、`settle(attempt_id: str, usage: Usage) -> None`、`mark_unknown(attempt_id: str, reason: str) -> None`、`summary() -> BudgetSummary`。teacher.py定义`GenerationPlan(count,scenario_labels,taxonomy_hash)`、`GeneratedQuestion(id,text,family_id,requested_labels)`、`Prelabel(id,cleaned_text,labels,notes)`；`TeacherClient.generate(plan: GenerationPlan) -> tuple[GeneratedQuestion,...]`、`label(samples: Sequence[CleanQuestion]) -> tuple[Prelabel,...]`、`augment(samples: Sequence[LabelledSample]) -> tuple[LabelledSample,...]`均异步，共用Ledger。Usage含prompt/completion/total及可核对的思考计数，Reservation/BudgetSummary的金额为微元整数。

Consumes：Task1术语与Task2 CleanQuestion；Produces：所有收费数据阶段唯一可用的TeacherClient，CLI只接受固定共享账本身份/路径，不能用新工作树参数重新init零账本。

- [ ] 写失败测试test_budget_survives_crash_and_competing_processes：10_000_000微元总额，单次预留ceil(1.2058624元)=1_205_863微元；双进程第9个全额未知请求不获许可；重开账本金额相同；重复结算不释放两次；损坏/丢失/错误授权身份拒绝。运行`& $AppPy -m pytest tests/test_topic_budget.py tests/test_topic_teacher.py -q`确认RED。
- [ ] 用sqlite3事务实现单一本地账本和整数金额；先落许可后HTTP。未知usage保留预留；完整有效usage按未缓存刊例结算，明确思考已包括或额外计入，不能漏/重复解释为实账。记录prompt/请求hash，不存Key。init是单独显式一次性命令，所有正常阶段只open-existing。
- [ ] 实现受控HTTPX教师传输，固定标准端点/模型、thinking enabled/low、8192、无工具、最大16、序列化请求正文最多64KiB、总时限120秒、禁止跳转及隐式重试。只暂时故障最多再发1次并重新预留，连续3败/300次/额度任一触发即暂停；JSON截断/多余ID/未知标签隔离但仍结算费用。
- [ ] 用MockTransport验证每个物理请求先有许可；JSON错误且usage有效也收费；timeout保留许可；429余额不足不重试；非JSON/缺usage不退款；响应命令不被执行。运行同命令GREEN，不把传输假响应当标注效果。
- [ ] 用已批准10元授权初始化共享账本但先不调用教师，记录路径和身份、金额精度、故障用例，提交`feat(ch10): bound teacher calls with durable budget`。

### Task 4: 68条小批预标与人工抽审交接

**Files:** 创建app/topics/reviews.py；扩展app/topics/data_cli.py；tests/test_topic_review_receipts.py；tests/fixtures/topics/annotation_cases.json；docs/ch10-pycharm-acceptance.md初版。

**Interfaces:** `async build_pilot(snapshot: PoolSnapshot, teacher: TeacherClient, *, count: int=68) -> ReviewPack`；`apply_review(pack: ReviewPack, decisions: Sequence[ReviewDecision]) -> ReviewReceipt`。ReviewDecision含sample_id、accept/correct/exclude、明确最终labels、reviewer、时间；Receipt绑定样本/prompt/taxonomy hash。data_cli提供pilot/review-import/budget-status，均preview默认，收费动作要--execute。

Consumes：Task2 PoolSnapshot、Task3 TeacherClient；Produces：标注规则定稿、小批回执及训练专用pilot家族清单；apply_review在reviews.py，build_pilot在data_cli.py。

- [ ] 为审核回执代码写RED：缺样本/重复ID/空reviewer/默认同意/错hash不得成为审核通过；只允许人的明确决策。运行`& $AppPy -m pytest tests/test_topic_review_receipts.py -q`，随后实现并GREEN。
- [ ] Prompt按设计写入prompts.py，从术语表生成边界；原句中的命令只作数据，造数与预标分开调用、标签语义保持、生成样本不伪装真实。以人工可读标注样例验证提示词，不用预先固定标签响应冒充LLM结果。
- [ ] 命令`& $AppPy -m app.topics.data_cli pilot --snapshot "$Evidence/pool/snapshot.json" --output "$Evidence/pilot" --execute`产生68条覆盖包：JSONL数据、只读HTML、待填决策JSONL和费用摘要。全部使用同一账本，隐私疑难行未放行不外发；达不到覆盖时显示实际缺项。
- [ ] 向用户给出PyCharm打开文件、逐项填写标签/排除、回传/导入的具体操作；等待实际抽审。不能把未回复当同意；可以继续Task8–10的契约/后端工作，最终真实模型验证仍须等后续训练。
- [ ] 收到决策后运行review-import核对hash，记录修订和人审身份；不全通过则按实际返工，费用不重置。追记并提交`feat(ch10): add auditable pilot annotation workflow`，没有回执时任务维持待人审。

### Task 5: 扩量、分组分层及仅训练增强

**Files:** 扩展app/topics/data_cli.py；创建ml/topic_classifier/data.py、cli.py、ml/topic_classifier/tests/test_data.py；tests/fixtures/topics/split_cases.json；冻结清单仅本地存放。

**Interfaces:** `async expand_corpus(snapshot: PoolSnapshot, review: ReviewReceipt, teacher: TeacherClient, *, target_groups: int=2040) -> Path`；`build_splits(samples: Sequence[LabelledSample], tokenizer, *, seed: int=20261021) -> SplitManifest`；`validate_augmentation(parent: LabelledSample, child: LabelledSample) -> None`。SplitManifest含三份ID/group/hash、来源/每类计数、pilot集合、长度隔离与probe清单。

Consumes：Task4真实人审回执、Task1本地tokenizer；Produces：冻结数据清单和训练增强；expand_corpus由业务环境data_cli运行，分层/长度审计由ML环境data.py运行。

- [ ] 对分组/划分程序写失败样例：同轮/跨来源同义家族不跨集，pilot固定训练，重复文本标签冲突隔离，比例差>3个百分点或逐类正反例<10失败。运行`& $MlPy -m pytest ml/topic_classifier/tests/test_data.py -q`确认RED。
- [ ] 实现按group聚合的多标签迭代分层：固定pilot训练后，剩余目标数按80/10/10扣除已占份额，固定seed一次划分，不扫seed挑测试成绩。用不截断tokenizer检查128上限；真实组>=5时验证/测试各至少1。实现增强父子核对和跨集去重后GREEN。
- [ ] 人审通过后执行`data_cli expand --pilot-receipt "$Evidence/pilot/review-receipt.json" --snapshot "$Evidence/pool/snapshot.json" --output "$Evidence/corpus" --execute`，达到约2040组/25%多标签/各类100正例或先遇预算暂停；gen和label独立、所有调用结算。失败和隔离单独保留，不能靠重复句凑数。
- [ ] 用ML环境运行`-m ml.topic_classifier.cli split --corpus "$Evidence/corpus" --output "$Evidence/dataset"`保存冻结清单；随后data_cli仅对manifest中的约25%训练组增强，最多一条/原句，保护数值/否定，验证测试不增强。再次检查无跨集家族、来源统计和实际比例，写data-audit.json。
- [ ] 不满足预检则停在数据阶段报告缺口；满足则冻结manifest和训练/验证/测试hash及预算累计。追记并提交`feat(ch10): freeze grouped multilabel dataset`；不提交真实语料或声称已达F1。

### Task 6: 实际全参训练与最佳checkpoint

**Files:** 创建ml/topic_classifier/train.py、tests/test_training_contract.py；扩展ml/topic_classifier/cli.py。

**Interfaces:** `train(dataset: Path, base_dir: Path, output: Path, *, seed: int=20261021) -> TrainingReceipt(best_checkpoint,history_path,dataset_hash,config_hash)`；`training_arguments(output: Path, micro_batch: int) -> TrainingArguments`。

Consumes：Task5 SplitManifest及Task1原始底座；Produces：TrainingReceipt和最佳checkpoint，未读取测试真值。

- [ ] 用标注样例核验float多热标签/BCE、所有编码器与头requires_grad、训练与验证ID无交集，监控训练文件访问证明不打开测试真值；tiny随机模型只用于损失/配置连通验证，明确不当作预训练训练成绩。命令`& $MlPy -m pytest ml/topic_classifier/tests/test_training_contract.py -q`。
- [ ] 依据已核对v5.20.2使用eval_strategy/save_strategy=epoch、processing_class、warmup_steps=0.1、optim=adamw_torch；按Global Constraints配置训练、早停和最多2个checkpoint，report_to=none，dataloader_num_workers=0。Windows模块有main保护；训练不读取测试标签文件。
- [ ] `& $MlPy -m ml.topic_classifier.cli train --dataset "$Evidence/dataset" --base-dir "$Evidence/base" --output "$Evidence/training"`，从原始底座重新加载而不是probe变更权重。按设计资源预检的micro-batch/累积运行，记录GPU峰值、完整epoch曲线、停止原因；恢复仅限同一数据/配置hash。
- [ ] 验证最佳epoch由验证macro-F1@0.5确定、较早平分胜出，编码器权重hash确实改变，训练history完整且total=trainable。不伪造loss下降；异常记录未完成，不用CPU随机权重或冻结底座替代。
- [ ] 追记实际耗时、环境、最佳轮次和资源/返工；提交`feat(ch10): train full parameter multilabel model`。训练失败与人工等待均不得勾选为完成。

### Task 7: 验证定阈值、留出报告及不可变模型包

**Files:** 创建ml/topic_classifier/{evaluation,artifacts}.py、tests/test_evaluation.py、tests/test_artifacts.py；扩展cli.py；创建app/topics/manifest.py供轻量校验。

**Interfaces:** `select_thresholds(logits, y_true, *, split: str) -> ThresholdSet`只接受validation；`evaluate_multilabel(y_true, predictions, *, taxonomy: Taxonomy) -> EvaluationReport`；`export_bundle(training: TrainingReceipt, thresholds: ThresholdSet, reports: Path, output: Path) -> ModelIdentity`；`verify_manifest(path: Path) -> ModelIdentity`。核心hash不包括反向引用模型版本的报告。

Consumes：Task6 TrainingReceipt、Task5冻结验证/测试清单、Task4同格式的人审回执；Produces：冻结ThresholdSet、完整评测、可由Task8加载的`$Evidence/model`。verify_manifest位于轻量app/topics/manifest.py，训练端同样调用它，避免两份身份算法。

- [ ] 用已标注矩阵计算样例核验指标：三个样本前两列真值[[1,1],[1,0],[0,1]]，预测[[1,0],[0,1],[0,1]]；第0类矩阵[[1,0],[1,1]]，第1类[[0,1],[1,1]]，其余15类仍有显式零支持。不排除空预测。运行`& $MlPy -m pytest ml/topic_classifier/tests/test_evaluation.py ml/topic_classifier/tests/test_artifacts.py -q`。
- [ ] 实现验证0.10..0.90步长0.05阈值选择、平分规则及支持不足回落；训练选epoch时仍用0.5。实现17张2×2矩阵、precision/recall/F1/support、macro/micro/完全匹配/Hamming/needs_review；zero_division=0并单列未定义分母原因，macro明确是固定17类口径，JSON不含NaN，HTML无外部脚本或原始隐私。
- [ ] 先只读验证集定阈值并冻结，再运行`& $MlPy -m ml.topic_classifier.cli evaluate --dataset "$Evidence/dataset" --training "$Evidence/training" --output "$Evidence/reports"`，保存每题预测，完整silver与真实/合成来源分开报告；不删除难题、错误或空预测。
- [ ] 冻结后按固定seed抽68条测试人审包并交用户；按实际回执产生gold报告，未人审保持pending。另交最多34条FP/FN错例包。修订只产生新报告，不能回调select_thresholds或改训练数据后继续宣称原留出成绩。
- [ ] 从最佳权重导出safetensors/tokenizer/阈值/清洗解码/核心manifest及外层证据清单，CPU float32重加载同一实际样例logits以atol=1e-5、rtol=1e-4核对。核对无hash循环及文件损坏拒载；独立probe必须实际返回“买大了想退”恰好两个标签，否则候选未通过。追记并提交`feat(ch10): evaluate and export versioned topic model`。

### Task 8: 独立CPU推理HTTP服务

**Files:** 创建ml/topic_classifier/service.py、tests/test_service.py；扩展cli.py；创建app/topics/client.py、tests/test_topic_client.py。

**Interfaces:** `load_predictor(bundle: Path) -> Predictor`，`Predictor.predict(items: Sequence[ClassifyItem]) -> Sequence[Prediction]`；`create_app(bundle: Path, *, predictor=None) -> FastAPI`；`TopicClient.health() -> ModelIdentity`、`TopicClient.classify(items: Sequence[ClassifyItem], expected: ModelIdentity, *, request_id: str) -> Sequence[Prediction]`异步。ClassifyItem只有id/text，extra forbidden，批1..64、文1..512；请求含request_id/items，响应回传同一request_id，类型定义放共享types.py。

Consumes：Task7 verify_manifest/ThresholdSet及Task1轻量Prediction；Produces：同一契约的真实HTTP服务和业务客户端；root环境不导入Predictor实现。

- [ ] 写RED覆盖未知/损坏包、taxonomy不匹配、重复ID、空文本、65条、NaN/inf/布尔概率、超过128 token不截断、其他冲突、17类均未达阈值needs_review。运行`& $MlPy -m pytest ml/topic_classifier/tests/test_service.py -q`及`& $AppPy -m pytest tests/test_topic_client.py -q`。
- [ ] FastAPI lifespan只加载一次模型，CPU eval/inference模式；默认127.0.0.1:8103，并发1/有限等待队列，503 busy。只暴露health/classify；不连MySQL、不调用教师、不下载模型。纯契约测试可注入fixture，报告不得用它替代真实模型。
- [ ] 实现轻量HTTP客户端及外层60秒总时限、回环地址/无跳转/版本与完整ID集合核对；逐项invalid/needs_review不改成成功。任何序号错配或概率非法拒收整批，不按错误顺序关联原话。
- [ ] 运行上述测试GREEN。命令`& $MlPy -m ml.topic_classifier.cli serve --bundle "$Evidence/model" --host 127.0.0.1 --port 8103`后，用实际导出包验health、单/多诉求、长句拒绝，记录CPU批量延时和资源；不发聊天请求或写业务表。
- [ ] 追记实际服务验证与端口归属，提交`feat(ch10): serve isolated topic predictions`。

### Task 9: 严格迁移与幂等批量Worker

**Files:** 创建sql/ch10-ddl.sql、sql/ch10-runtime.sql；app/topics/{profile,migration,repository,receipts,batch,cli}.py；修改app/db/models.py；tests/test_topic_batch.py、tests/test_topic_migration.py；tests/integration/test_topic_storage.py。

**Interfaces:** `load_profile(path: Path) -> TopicProfile`固定service_url、活动manifest、共享回执路径；`async migrate_topics(database, *, preview: bool) -> MigrationReceipt`；`TopicRepository.preview_pending(from_id,to_id,limit,identity) -> BatchPreview`；`TopicRepository.commit_predictions(preview,predictions,lease) -> BatchReceipt`；`BatchRunner.run_once(preview, *, reclassify: bool=False) -> BatchReceipt`；`async BatchRunner.watch(*, stop: Event) -> None`。方法均async，除profile/回执读写。

Consumes：Task8 TopicClient及Task7 ModelIdentity；Produces：实际topic_classifications行、幂等批次和本地回执。TopicProfile字段固定为service_url、manifest_path、runtime_root；预算路径仍固定共享，不由普通profile覆盖。配置JSON不含Key，活动manifest缺失时批处理拒绝、统计显示未配置模型。

- [ ] 写RED覆盖原表/补充表结构、原FK默认RESTRICT、拒绝冲突DDL、四列NULL旧行、唯一question_id；批次提交后重放不增行、源hash改变不写、锁丢失不提交、响应版本变更拒收。运行`& $AppPy -m pytest tests/test_topic_batch.py tests/test_topic_migration.py -q`。
- [ ] 复制设计附录原DDL，不改变字段；独立补充四列及model_version索引，基于既有DDL契约/ProcessingLease方式实现精确预检、短事务、同一物理锁连接。输入hash取数据库原文UTF-8；推理只传脱敏文本。本地receipts.sqlite3维护失败项及批次；每回合至多1次即时网络重试，连续3个失败回合暂停，回合退避60/120秒、上限240秒，需显式retry。旧结果只经范围明确reclassify更新。
- [ ] 在3308自有fixture测试迁移、插入/重放、部分成功后进程退出、另进程接管、输入编辑与旧模型隔离，不能给3307塞测试行。运行`& $AppPy -m pytest tests/integration/test_topic_storage.py --run-mysql -q`及离线测试GREEN。
- [ ] CLI提供migrate/verify/preview/run-once/watch/retry/reclassify；默认dry-run，写操作需--execute，database只能显式test/configured。先对3307结构preview后执行批准的新增表及四列，verify成功才使用；不能自动修复未知表或清理原池。
- [ ] 实际范围preview冻结最多100条、高水位及model_version，run-once通过实际服务落表；再对同一范围重放验证无重复，watch达到20才起批。记录SQL计数、实际/演示来源、失败回执和0个教师调用。追记并提交`feat(ch10): classify flywheel questions in bounded batches`。

### Task 10: 主题统计API、后台页面与演示入口

**Files:** 创建app/topics/{statistics,demo}.py、app/api/topics.py；修改app/main.py可选注入及页面路由；创建app/static/topics.{html,js,css}，修改review-queue.html导航及review-queue.js按review_id定位的可选入口；tests/test_topic_statistics.py、tests/test_topic_api.py；tests/integration/test_topic_distribution.py。

**Interfaces:** `TopicStatisticsService(repository, profile, receipts)`；异步`summary(filters: TopicFilters) -> TopicSummary`和`questions(label: str, filters: TopicFilters, offset: int=0,limit: int=20) -> TopicQuestionPage`。API GET /api/topics/summary、/api/topics/questions，GET /topics页面；main.create_app增加可选topic_profile/topic_service，默认关闭，并增加可信启动参数background_tasks_enabled=True（旧入口默认行为保持）。demo.create_app读取显式profile、传False，复用既有业务资源所有权，不启动分类worker。

Consumes：Task9 Repository/Profile/回执；Produces：当前版本只读统计与页面。TopicFilters含source（原表三种入池来源或空）、since/until（按既有created_at时间口径转换的半开范围）；TopicQuestionPage含total/items，items为question_id/脱敏问题/labels/source/classified_at/model_version/matched_review_id。页长默认20、最大100，负offset拒绝。

- [ ] 仅为后端写RED：一个问题两标签各计1、当前有效分母为1、缺类仍0；旧/NULL版本与input_hash失效不计入当前；无manifest可打开页面但显示未配置，回执不可用待复核显示unknown；非法label、偏移、跨来源日期过滤、DB失败不能装0。另加test_topic_demo_does_not_recover_paid_jobs，断言新demo不恢复三类收费后台、旧factory默认仍遵循原启动规则。运行`& $AppPy -m pytest tests/test_topic_statistics.py tests/test_topic_api.py -q`。
- [ ] 实现只读统计、脱敏分页、既有guard_read限制及可选DI生命周期，SQL有界；相同question_id不重复累计，计数口径按设计。3308验证统计和实际JSON标签一致；GREEN命令再加`& $AppPy -m pytest tests/integration/test_topic_distribution.py --run-mysql -q`。
- [ ] 前端Vibe直接做：浅色绿色圆角，17类条形图/版本/分类覆盖，点击类目看脱敏问题，已有matched_review_id时可点到/review?review_id=对应字符串ID；未归并不造链接。明确多标签比例可超100%、来源是原话流水数、旧结果和待复核状态。用户描述效果就调整，不执行前端TDD或code review。
- [ ] 演示factory使用独立checkpoint `runtime/workflow/ch10-checkpoints.sqlite`，background_tasks_enabled=False跳过flywheel消费者/发布worker、摘要恢复及评估Manager恢复，eval_schedule_enabled/eval_pipeline_enabled/rag_evaluation_enabled亦为False；保留只读审核所需Repository，不自动处理旧任务。沿用已核对检索配置，不拍脑袋设阈值。缺必要配置明确报错；不改8006环境/账本。命令`& $AppPy -m uvicorn app.topics.demo:create_app --factory --host 127.0.0.1 --port 8007`。页面刷新只读，观察网络确认没有教师/分类POST。
- [ ] 浏览器验证/topics分布、筛选、分页、空态/故障、宽屏和窄屏；页面与Task9 SQL统计一致，现有review/observability入口可达并明确展示本演示禁用的后台任务，完整第九步服务仍在原8006；聊天图不产生分类调用。记录视觉与后端结果后提交`feat(ch10): expose topic distribution in flywheel admin`。

### Task 11: 整分支审查、回归及PyCharm交付

**Files:** 完成docs/ch10-pycharm-acceptance.md；创建docs/superpowers/reports/2026-10-21-ch10-delivery.md；更新README.md与dev-notes/ch10.md；修复审查指出的实际后端文件/测试。

**Interfaces:** 只消费前述已实现命令/类型/产物，不再新增模型或业务流程。整分支审查范围为后端/数据工具/训练代码，前端按用户例外只做效果验证。

Consumes：Task1–10实际产物和未达成清单；Produces：可独立复现的PyCharm手册、审查结论及事实交付报告。

- [ ] Native被选择时用requesting-code-review技能安排一位新的整分支后端审查者；提交spec/plan、基线和最终diff、真实数据/训练证据、未完人审项。审查重点依Review Focus，不能只读测试通过就盖章；按receiving-code-review核对意见并修复/验证。
- [ ] 按实际改动先定点复验，再各运行一次`& $AppPy -m pytest tests -q`和`& $MlPy -m pytest ml/topic_classifier/tests -q`；相关3308集成`& $AppPy -m pytest tests/integration/test_topic_storage.py tests/integration/test_topic_distribution.py --run-mysql -q`。这些测试不触发任何收费模型；失败、跳过和未启动资源分别记录，不重复全量跑刷结果。
- [ ] 验收报告交付：完整留出逐类F1/17张2×2矩阵，gold/真实/合成分母与限制，实际多标签probe、全参证据、真实池SQL与主题页截图、幂等/输入改变/超时、实际预算及未知预留。人审未完成、真实来源不足或模型关键probe失败就保留未达成项，不能以代码测试补齐。
- [ ] 手册给出PyCharm两解释器和每个Run Configuration（工作目录、模块、参数、环境文件）；按preview→人审→扩量→训练→评测→serve→migrate/verify→run-once/watch→浏览8007/topics逐步写，附停机方法和哪些操作耗10元账本、哪些仅本地计算。实际端口/模型路径替换所有示意，密码不写入文档。
- [ ] 每阶段已追记后再补finish总结，运行git diff --check和产物/链接/秘密检查，使用verification-before-completion与finishing-a-development-branch技能交付并由用户选择集成；本次计划批准不预先授权第十步合并推送。

## 计划自检与执行选择

覆盖映射：设计§1–3→Task1；§4.1→Task2；§6→Task3；§4.3→Task4/7；§4.2/5→Task5；§7→Task6；§8→Task7；§9→Task7/8；§10→Task9；§11→Task10；§12–14→Task11及逐任务记录。Review Focus五项分别落在Task2/3/5/7/8/9/10的明确用例。

依赖路径1→2→3→4（人审）→5→6→7（人审）→8真实包验收→9真实批次→10页面→11交付。人审等待时可实现8–10中只依赖共享契约的代码与fixture测试，但没有真实包/真实SQL前不能宣称对应验收完成。预算/数据不足停止依赖步骤，继续不受影响的代码工作并交代缺口。

推荐Native本会话顺序实现、单独第十步隔离worktree：接口/数据/模型版本依赖紧密，顺序实现便于保持一致且少付重复上下文成本；最后统一新审查者核对后端。另一选择是逐任务Subagent-driven，实现和评审各用独立上下文，审查更早但上下文成本更高。用户需审阅计划并选择后，才开始任务。
