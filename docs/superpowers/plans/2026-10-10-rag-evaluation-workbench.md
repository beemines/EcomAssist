# RAG 评估工作台与 300 题 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 在 /rag-eval 上运行、取消和追溯冻结的 300 题四策略比较，分别报告检索与生成效果。

**Architecture:** 复用现有检索、证据组装、生成守卫与 MySQL/Milvus 双写，新建小型评估包负责材料、指标、运行存储及生命周期。CLI 与 FastAPI 使用同一执行器及本地进程锁；临时知识与业务库隔离，报告持久保存。现有前端预览接入任务接口，旧报告保持原指标口径。

**Tech Stack:** 现有锁定版本 Python / FastAPI / SQLAlchemy / MySQL / LangChain / Milvus，BGE-M3、Milvus BM25 chinese analyzer + RRF、bge-reranker-v2-m3；不新增任务队列或依赖。

**Spec:** [书面设计](../specs/2026-10-09-rag-evaluation-workbench-design.md)，用户 2026-10-10 “确认”。本计划已由用户“开始实现”批准；执行方式沿用已选 Subagent-Driven，前端采用 Vibe Coding 例外。

## Global Constraints

- 展示 vector 对应内部 dense；其余 bm25、hybrid、hybrid_rerank。每路候选 50、最终 10，切分 target_chars=1200 / overlap_chars=120；当前八篇实际 50 块，不凑教程数字。
- A_policy、B_model、C_colloquial、E_multi、D_absent 各 60 题，总计 300；原 CSV 不改，修订版、逐题理由、运行 JSONL 分开保存。D_absent 的内部兼容名为 D_unanswerable。
- 正式模式 content_ablation；四路共用内容充分性判断。线上 calibrated_score 默认行为和旧门槛保持，生成不得读取金标。
- 真实上游沿用本地 .env 的 GLM 与既有密钥。最终回答 512，改写/自评各 2048，裁判输入 16000 / 输出 2048 token；改写 60s、自评 20s、FAQ 90s、聊天 240s、裁判沿用现有 60s，模型零重试。
- 生成证据输入沿用 TOOL_INPUT_TOKEN_BUDGET，当前默认 8000；实际配置值全部冻结进报告。嵌入/重排 20s、Milvus 5s 沿用当前配置；不自动加预算或换模型。
- 仅隔离库 127.0.0.1:3308/customer_service_test、新 UUID knowledge_test_ 集合；业务 3307、knowledge_hybrid、旧报告和其他任务资源不改。运行记录 runtime/rag-evaluation 加入忽略。
- 一次最多一个运行，题并发最多 2；CLI 与 HTTP 共用 OS 文件锁；服务只支持一个 Uvicorn worker。取消/异常/重启均留痕，无自动收费续跑。
- 先全量离线审标，再固定 10 题 / 40 条试运行；匹配版本试运行合法并清理成功后才运行 300 题 / 1200 条。错误不填满分；没有新分数前不宣称某策略最好。
- 后端代码 RED/GREEN，资料与 Prompt 用标注样例验证。具体 API 修改前先 Context7 查官方资料并核对安装版本；中文 UTF-8 注释，每个函数至少有有用说明。
- 每任务完成立即补 dev-notes/ch04.md 四项记录；后端经过规格与质量审查再进入下一任务。前端不套 brainstorm/TDD/code review；本次不合并或推送。

## Review Focus

1. AND/OR 组里有多个子块、排名重复 ID：完整替代组合才能满足组，重复不能抬分；任务 1/2 加测试。
2. 同题号换题面、语料或 Prompt 改动：台账键和运行指纹区分，旧试运行不得放行；任务 1/7 加测试。
3. Windows 中断发生在 flush/manifest/commit 之间：不提交未记录归属的数据，只回收有证明资源；任务 4/5 加进程与事务测试。
4. 重复取消、上游吞取消、流截断、清理失败：保留真实错误，完整终止前不得解锁第二个运行；任务 6/7 加测试。
5. 外站启动、伪造过滤或路径、意外密钥入错误：写入口拒绝、路径封闭、公开 DTO 白名单；任务 4/8 加测试。

---

## 文件与接口地图

所有下列路径相对当前 worktree；除注明外是新增文件，不重构无关系统。

| 文件 | 责任 |
| --- | --- |
| app/rag_evaluation/contracts.py、dataset.py | 不可变材料契约、加载和全批离线校验 |
| evals/datasets/merchant-rag-300/ | original.csv（已原样归档）、reviewed.csv、cases.jsonl、audit.jsonl、regressions.jsonl、manifest.json |
| app/rag_evaluation/metrics.py、report.py | 组指标、有效分母、共同子集、v1 兼容与公共报告 |
| app/rag_evaluation/judgment.py | 严格联合裁判、逐点覆盖和实际证据忠实度 |
| app/rag_evaluation/store.py、locking.py | 原子文件、运行历史、跨进程排他锁 |
| app/rag_evaluation/resources.py | 隔离建库、提交前归属记录、精确清理 |
| app/rag_evaluation/runner.py、manager.py | 四路执行、任务生命周期、试运行门槛 |
| app/api/rag_evaluations.py | 同源工作台 JSON API |
| evals/rag_workbench.py | 新版离线校验/运行命令，复用 manager |
| app/static/rag-evaluation.html/css/js | Vibe Coding 运行与报告页面 |
| tests/test_rag_*.py | 各后端交付单元的边界验证 |
| docs/validation/rag-evaluation-*.md/json | 审标核验、真实结果、验收证据；不覆盖旧报告 |

公共契约用冻结 dataclass、tuple 及 Literal；跨模块不传共享 AsyncSession。下列 JSON 返回约定为 dict[str, object]，具体字段在所属任务定义，不接收任意对象序列化。

- Strategy = Literal["dense","bm25","hybrid","hybrid_rerank"]，Scope = Literal["pilot","full"]。
- CorpusChunk(chunk_key: str, document: str, ordinal: int, draft: ChunkDraft)；chunk_key 为文件名、序号及规范内容 SHA-256 的稳定组合。
- GoldGroup(group_id: str, alternatives: tuple[tuple[str, ...], ...])；内层组合的所有 chunk_key 都需要，外层组合任一满足即可。
- MappedGroup(group_id: str, alternatives: tuple[tuple[int, ...], ...])；只由本轮逻辑块到物理主键映射产生。
- AnswerPoint(point_id: str, text: str, condition: str | None, aliases: tuple[str, ...])。
- EvalCase(eval_id: str, bucket: str, difficulty: str, query: str, category: str | None, should_refuse: bool, groups: tuple[GoldGroup, ...], points: tuple[AnswerPoint, ...], ledger_eval_id: str)。
- FrozenDataset(dataset_id: str, fingerprint: str, corpus_hash: str, cases_hash: str, annotation_hash: str, chunks: tuple[CorpusChunk, ...], cases: tuple[EvalCase, ...], pilot_ids: tuple[str, ...])。
- PointVerdict(point_id: str, covered: bool, reason: str)、ClaimVerdict(claim: str, supported: bool, reason: str)；GenerationJudgment(points: tuple[PointVerdict, ...], claims: tuple[ClaimVerdict, ...], raw_response: str, finish_reason: str, prompt_version: str)。raw_response 仅进本地私有裁判快照，不返回公共 DTO；JudgeError 同样携带有界 raw_response 供失败审计，不携带请求/密钥。
- CaseRecord：由 report.py 校验的 JSON 数据，固定含 eval_id、strategy、status、stage、query、query_plan、mapped_groups、candidate_ids、final_ids、prompt_citations、decision、answer、point_verdicts、claim_verdicts、metrics、error、elapsed_ms、judge_snapshot；未完成阶段为 null，不用 0 冒充。status 为 completed / rewrite_error / retrieval_error / self_check_error / answer_error / judge_error / cancelled / not_attempted；stage 为 rewrite / retrieval / self_check / answer / judgment / complete。judge_snapshot 为本地私有字段，公开保留 Prompt版本与判定，不暴露原始响应。
- RunConfig：由 store.py 校验的 JSON 数据，含 dataset_id、scope、fingerprint、mode=content_ablation、模型名、预算、Prompt 版本和上游地址摘要；不含密钥或连接串。
- RunManifest：含 run_id、config、state、outcome、stage、计划题数/策略数、计数、请求数、ownership、cleanup、时间与公共错误；完整字段在任务 4 冻结。
- CleanupResult(ok: bool, errors: tuple[str, ...], unverified: tuple[str, ...])；归属未知不是清理成功。

## 执行约定

从 worktree 根目录使用现有解释器；下面 $py 仅是命令缩写，不写入应用：

~~~powershell
$py = 'D:/shixi/ecommerce-customer-service/.venv/Scripts/python.exe'
$env:PYTHONUTF8 = '1'
$env:PYTHONIOENCODING = 'utf-8'
~~~

每个后端任务：Context7 查询 → RED → 最小实现 → GREEN → 控制端核验 → 两阶段子代理审查 → 修复复验 → 立即 dev-notes → 显式文件提交。资料审标不得以测试自动通过代替逐题人工核对。任务 9 走用户前端例外。

### Task 1：冻结资料，逐题审标与可验证的金标加载

**Files:** 新增 contracts.py、dataset.py、tests/test_rag_dataset.py、reviewed.csv、cases.jsonl、audit.jsonl、regressions.jsonl、manifest.json；更新材料审计文档。原 original.csv 已保存，本任务只读。

**Interfaces:** load_dataset(dataset_id: str, *, root: Path) -> FrozenDataset；map_groups(case: EvalCase, id_map: Mapping[str, int]) -> tuple[MappedGroup, ...]；ledger_key(eval_id: str, query: str) -> str。未知 ID、坏哈希/类别/金标抛 DatasetError，无网络副作用。

- [ ] 查 Context7 的 CPython CSV/哈希及所用 Pydantic 数据模型 API，核对锁定版本；读取项目现有 chunk_markdown 实现，保存原文及八篇哈希、切分参数、50 个块的稳定标识。
- [ ] 用原 CSV 逐题审阅全部 300 行，audit.jsonl 每题一行含 before/after/reason/source_refs，未改题明确“保持”理由；完成设计 §3 全部纠偏。D3/D30 原问题保存额外可答回归，D 位换真正库外题；60 道 E 均有真实多小节问题。为所有要点绑定可审查来源及条件，不静默猜章节。
- [ ] 先写测试：test_300_unique_cases_and_five_buckets、test_group_alternative_requires_complete_bundle、test_ledger_key_changes_with_query_and_fits_16、test_freeze_rejects_bad_hash_empty_gold_unknown_category_and_missing_reason；分别断言 300、各60、[[a,b],[c]] 的 a 单独不满足、换题键不同且≤16、非法输入在模型零调用时失败。
- [ ] RED：& $py -m pytest tests/test_rag_dataset.py -q，观察尚不存在加载器/校验的失败。
- [ ] 实现上述契约；dataset_id 固定 merchant-rag-300-v1，文件白名单与根目录固定；manifest 冻结文件/原题/审标/切分 SHA-256。稳定标识在入库前校验，E 的独立组不能只是同块重复。
- [ ] GREEN：运行同一测试；对 300 题全部核对来源/作用域，对 8 类纠偏列出前后样例。固定 pilot_ids=A21,A43,B3,B54,C5,C35,D1,D3,E2,E19，恰好每桶两题；分数高低不参与选题。
- [ ] 记录 task/review 四项，提交材料与加载器：feat: freeze audited merchant RAG evaluation dataset。

### Task 2：组指标与报告 v2，保留旧报告

**Files:** 新增 metrics.py、report.py、tests/test_rag_metrics.py；读取旧 evals/retrieval_metrics.py，不改旧指标语义。

**Interfaces:** retrieval_metrics(ranked_ids: Sequence[int], candidate_ids: Sequence[int], prompt_ids: Sequence[int], groups: tuple[MappedGroup, ...]) -> dict[str, float | None]；summarize_records(records: Sequence[dict[str, object]]) -> dict[str, object]；public_report(report: Mapping[str, object]) -> dict[str, object]；adapt_legacy(report: Mapping[str, object]) -> dict[str, object]。GenerationJudgment 契约在 contracts.py 定义，裁判实现见任务 3。

- [ ] 先写 test_duplicate_rank_and_multi_chunk_group_metrics：组为 [[1,2],[3]] + [[4]]，排名 [1,1,4,2] 去重后 [1,4,2]；MRR=1，Recall@5=1，但 Prompt [1,4] 覆盖=.5；候选阶段与最终阶段分别计分。
- [ ] 先写 test_first_hit_not_all_groups 与 test_metric_valid_n_and_common_subset：前十仅第一组时 MRR 非零且全组命中=0；检索已完成、裁判失败仍计检索，生成不计；共同有效子集只包含四路均合法的题号。库外检索和零断言忠实度为 null。
- [ ] 先写 test_v1_missing_metrics_are_na_and_source_unchanged：旧 120/101/19 及已有 summary 保持，新增 Recall@5/要点覆盖不存在，禁止填0。
- [ ] RED：& $py -m pytest tests/test_rag_metrics.py -q。
- [ ] 实现指标：组覆盖按完整替代组合；MRR 命中任一相关块；先逐题再宏平均。summary 含每桶/总体、每指标 valid_n/排除原因、策略完成/错误/未执行、四路共同生成子集及题号；公共 CaseRecord 白名单校验，错误仅 code/type/安全消息。
- [ ] GREEN：同一测试，加已审 E2/E19 证据子集标注样例；确认 v1 源文件字节哈希不变。
- [ ] 阶段记录和两阶段审查后提交：feat: report grouped retrieval and generation metrics。

### Task 3：公平的内容自评与严格联合裁判

**Files:** 修改 app/core/sufficiency.py:SufficiencyService；新增 judgment.py、tests/test_rag_judgment.py；既有 evals/faithfulness.py 保留 v1；补评估 Prompt 版本及标注核验稿。

**Interfaces:** SufficiencyService(..., *, mode: Literal["calibrated_score","content_ablation"]="calibrated_score")，既有 .check 不变；GenerationJudge(model: Any, input_budget: int, timeout: float=60)，async judge(question: str, answer: str, citations: Sequence[Citation], points: tuple[AnswerPoint, ...]) -> GenerationJudgment。

- [ ] 先 Context7 查 LangChain with_structured_output/raw 输出、Pydantic strict 校验和 asyncio timeout 的当前版本接口。
- [ ] RED 测试 test_content_ablation_all_strategies_share_gate：同一低分证据四路执行同样自评，默认线上 hybrid_rerank 仍须校准门槛。test_empty_or_knowledge_question_cannot_bypass_gate：空证据事实问法不能改为 social 绕过。
- [ ] RED 测试 test_judge_rejects_missing_duplicate_point_string_bool_and_nonstop：缺/重复 point_id、"true"、finish_reason=length 全部 judge_error；test_gold_fact_is_not_faithfulness_evidence：只在标准点里出现而证据没有的断言判 unsupported；test_zero_claims_not_perfect_faithfulness。
- [ ] RED：& $py -m pytest tests/test_rag_judgment.py tests/test_sufficiency.py -q；tests/test_sufficiency.py 为已核实存在的现行线上测试。
- [ ] 实现显式 mode；联合 Prompt 分开“覆盖裁判要点”和“唯一支持证据”，完整列 point_id 和全部事实断言，reason 非空，限制输出长度和严格 bool，原始 stop 及结构校验失败直接报错，无修复重试。保存有界原响应/finish/Prompt版本到私有 judge_snapshot，公共裁判理由仍可审查。拒答正例覆盖0、无断言忠实度 N/A。
- [ ] GREEN 同组测试；Prompt 标注集覆盖同义/条件遗漏/部分可答/有依据否定/纯拒答/金标泄漏反例，受控 raw 模型跑验证；此阶段不收费调用。
- [ ] 记录评估专用门槛与线上差异、审查后提交：feat: add common sufficiency mode and joint generation judge。

### Task 4：运行文件存储与跨进程排他锁

**Files:** 新增 store.py、locking.py、tests/test_rag_store.py、tests/test_rag_locking.py；修改 .gitignore。

**Interfaces:** RunStore(root: Path)，async create(config: dict[str, object], case_keys: Sequence[tuple[str, Strategy]]) -> str，async update(run_id: str, patch: Mapping[str, object]) -> None，async put_case(run_id: str, record: Mapping[str, object]) -> None，async get(run_id: str) -> dict[str, object]，async records(run_id: str) -> list[dict[str, object]]，async list_runs(offset: int=0, limit: int=20) -> list[dict[str, object]]；RunLock(root: Path).acquire() -> RunLease，RunLease.close() -> None；忙抛 RunBusy，路径/格式错抛 StoreError。

- [ ] Context7 核对 CPython 原子 replace、msvcrt.locking / fcntl、任务取消语义；所有文件操作限制 root，拒绝外部符号链接落点。
- [ ] 先写 test_atomic_snapshot_failure_preserves_previous、test_case_checkpoint_reconciles_counts_after_restart、test_path_escape_and_unknown_fields_rejected；原子写失败旧 JSON 仍合法，case 写入后计数未更新可从 records 恢复；../、绝对路径、模型请求/密钥字段不能公开。
- [ ] 先写 test_two_processes_cannot_acquire_same_lock_and_death_releases：真实 Windows 子进程占同一规范化根的锁，第二个即刻 RunBusy，前者退出释放；进程内也排他。
- [ ] RED：& $py -m pytest tests/test_rag_store.py tests/test_rag_locking.py -q。
- [ ] 实现 UUID32hex run_id，manifest.json / records/<eval_id>--<strategy>.json / report.json / report.md；各文件同目录临时写后 replace，store 异步锁串行发布，读取一致快照。case 保存逐条原子，不每条重写整份1200题报告；启动恢复以 case 文件修正计数。judge_snapshot 随本地记录保存且目录不静态挂载，GET/export 经公共白名单移除，不提交版本库。
- [ ] manifest 冻结上述契约，版本2；ownership 含测试库身份、UUID集合、owned_ids 与每块内容摘要；请求计数按实际网络调用。锁文件固定 evaluation.lock 的首字节，保留打开句柄直到结束，不按 PID 删除重建锁文件。runtime/rag-evaluation/ 忽略；无凭据自动序列化。
- [ ] GREEN 同组测试；两阶段审查与记录后提交：feat: persist RAG runs and serialize local evaluators。

### Task 5：隔离建库与提交前资源归属

**Files:** 新增 resources.py、tests/test_rag_resources.py；修改 app/repositories/knowledge.py:KnowledgeRepository.add_chunks；复用 app/knowledge/hybrid_jobs.py、app/retrieval/milvus.py 的现有接口。

**Interfaces:** add_chunks(drafts: list[ChunkDraft], link_neighbors: bool=False, *, before_commit: Callable[[list[int]], Awaitable[None]] | None=None) -> list[int]；OwnedResources(settings: Settings, store: RunStore, run_id: str)，async prepare(dataset: FrozenDataset) -> Mapping[str, int]，async cleanup() -> CleanupResult，async recover(manifest: Mapping[str, object]) -> CleanupResult。prepare 成功后暴露 scoped repository/index/embedder/reranker/model/judge_model/planner/quality；其类型沿用现有构造函数，生命周期只属 OwnedResources。

- [ ] Context7 查 SQLAlchemy async flush/begin/rollback、Milvus 集合创建/删除和 native BM25，核对实际版本；核实固定 3308 库已有现行八表，不自动改建业务库。
- [ ] 先写 test_manifest_failure_rolls_back_flushed_rows 与 test_recorded_ids_recover_after_commit_interruption；回调在同一短事务 flush 后 commit 前持久记录，抛错则本批无行。使用故障注入证明各提交窗口，补真实 MySQL 子进程中断验证。
- [ ] 先写 test_cleanup_only_owned_ids_and_exact_collection、test_unverified_ownership_is_not_deleted、test_partial_constructor_failure_closes_owned_clients：保留旁置哨兵行/集合与 faith_cases；未知归属不删；后续客户端构造失败前面的关闭一次。
- [ ] RED：& $py -m pytest tests/test_rag_resources.py -q；真实用例加 --run-mysql --run-milvus。
- [ ] 实现回调默认 None，现有业务调用不变；批次短事务，不跨嵌入 HTTP。记录 UUID集合名先于创建；按白名单块导入 pending、向量化回填 done，完整核对物理/稳定标识及数量后生成 id_map；ScopedRepository 只读 owned_ids。
- [ ] cleanup 每动作最多10秒，集合内部沿用5秒服务期限；删除自有知识和精确集合、关闭各客户端/数据库，汇总所有错误不首错丢其余。未知身份标 unverified，不能只凭前缀或 ID 删除不匹配内容；保留裁判台账及报告中的证据快照。
- [ ] GREEN 单测和真实恢复/哨兵集成；确认业务84块及其他集合无变化，记录后审查提交：feat: own and recover isolated evaluation resources。

### Task 6：共用四策略执行器与准确检查点

**Files:** 新增 runner.py、tests/test_rag_runner.py；复用 app/core/evidence.py、answer_validation.py 和检索服务，不复制流守卫。

**Interfaces:** EvaluationRunner(resources: OwnedResources, store: RunStore, run_id: str, settings: Settings)，async run_cases(dataset: FrozenDataset, id_map: Mapping[str, int], case_ids: Sequence[str], cancel_event: asyncio.Event) -> str；返回 completed / completed_with_errors / cancelled 的评估 outcome，最终生命周期由 manager 决定。

- [ ] Context7 查具体 LangChain ainvoke/astream、httpx event hooks 和取消 API；核对 FinalAnswerStream、ensure_answer_active、close_answer_stream、validate_answer 的现有调用形状。
- [ ] 先写 test_one_query_plan_shared_by_four_strategies_and_no_gold_in_generation、test_shared_rewrite_failure_four_errors_one_request；模型看不到 points/groups，四路复用同一计划；共享失败落四条 rewrite_error，实际请求只增1。
- [ ] 先写 test_shared_rewrite_elapsed_charged_independently、test_truncated_stream_and_swallowed_cancel_do_not_finish、test_cancel_keeps_started_and_unstarted_distinct；每路扣共享改写耗时而不扣别路耗时，stop 缺失拒绝，已开始 cancelled、未开始 not_attempted。
- [ ] RED：& $py -m pytest tests/test_rag_runner.py -q。
- [ ] 实现题并发2、每题四策略有序调用；各阶段写 case 检查点与统计，候选50/最终10/实际 Prompt 证据分开冻结；四路共用 content_ablation 自评。FAQ/聊天各自期限沿用线上守卫，取消重复检查，不将上游吞取消当成功。
- [ ] 使用严格联合裁判及任务2指标；只把有效 unsupported 断言写 faith_cases，键为 ledger_eval_id，保留所有策略证据快照和 judge版本。评估拒答只留报告，不写线上 low_confidence_questions。计数用现有实际 HTTP hook，非法裁判保留 error，不重试。
- [ ] GREEN 同组测试及四路真实 MySQL/Milvus检索的非 LLM 集成；核对型号/跨节候选和清理。审查记录提交：feat: execute fair four-strategy RAG comparisons。

### Task 7：运行管理、取消恢复、版本匹配试运行与 CLI

**Files:** 新增 manager.py、evals/rag_workbench.py、tests/test_rag_manager.py；修改 evals/evaluate_retrieval.py:main 的入口锁，旧算法/格式保持。

**Interfaces:** RunManager(store: RunStore, settings: Settings, dataset_root: Path)，async startup() -> None，async start(dataset_id: str, scope: Scope) -> str，async cancel(run_id: str) -> dict[str, object]，async shutdown() -> None；start 预检抛 DatasetError / PilotRequired / RunBusy，不自动排队。CLI 通过同一个 manager 启动和等待，validate 只调用 dataset loader。

- [ ] 先写 test_single_start_and_cancel_idempotent、test_full_requires_successful_matching_pilot、test_changed_prompt_budget_or_corpus_invalidates_pilot；40条合法且清理成功才放行，低召回不阻断，任何结构错误/配置变更不放行。
- [ ] 先写 test_restart_interrupted_never_resumes_model、test_cleanup_failure_overrides_completed_or_cancelled、test_hung_cancel_does_not_release_lease_early；重启只核验归属并清理，无模型调用；清理坏则 state=failed 且保存原 outcome，运行没真结束不允许第二个任务。
- [ ] RED：& $py -m pytest tests/test_rag_manager.py -q。
- [ ] 实现启动流程：全批离线预检→取得跨进程锁→建立 queued记录→强引用后台任务→preparing/run→cancelling/cleanup→发布终态→释放lease。异常路径也同序；store/锁失效即拒绝收费。
- [ ] 配置指纹包含语料/题库/审标、生成模式、模型、上游地址摘要、全部相关预算/期限与各 Prompt版本。重启遍历非终态，按 manifest 清理后 interrupted 或 failed；unknownownership不删且清理不通过。shutdown 发取消并有界等候清理，保留尚未结束的任务/锁归属，禁止提前伪称释放。
- [ ] 新 CLI 命令：& $py -m evals.rag_workbench validate --dataset merchant-rag-300-v1；run --dataset merchant-rag-300-v1 --scope pilot|full；show --run-id <UUID>。固定 runtime根、不可传任意DB/模型/输出路径。旧 evaluate_retrieval main 也取得相同锁，保留现有参数与报告行为。
- [ ] GREEN 同组、旧 test_retrieval_evaluation.py 和跨 CLI/HTTP 并发冲突测试；记录后两阶段审查提交：feat: manage RAG evaluation lifecycle and pilot gate。

### Task 8：FastAPI 工作台与同源写接口

**Files:** 新增 app/api/rag_evaluations.py、tests/test_rag_api.py；修改 app/config.py:Settings、app/main.py:create_app/lifespan、.env.example。

**Interfaces:** create_router(manager: RunManager, store: RunStore, settings: Settings) -> APIRouter；create_app 增可选 evaluation_manager 注入，现有参数兼容。新增 RAG_EVALUATION_ENABLED 默认 false、RAG_EVALUATION_ALLOWED_ORIGINS 固定本机 http://127.0.0.1:8001 和 http://localhost:8001；启动换端口需显式配置，HTTP 请求不能修改。

- [ ] Context7 查锁定 FastAPI lifespan、Pydantic 请求约束、FileResponse；复用现有 AsyncExitStack 管理 manager，不用请求结束即丢的 BackgroundTasks。
- [ ] 先写 test_readonly_rejects_start、test_start_202_and_busy_409、test_bad_dataset_strategy_filter_and_path_rejected、test_cross_origin_or_nonjson_start_rejected、test_public_error_does_not_expose_secret；用注入 manager 断言错误请求零模型调用。
- [ ] RED：& $py -m pytest tests/test_rag_api.py -q。
- [ ] 实现设计 §6 全部九类路由，包括 /rag-eval；写接口要求 application/json，Origin 与 Host 对应显式 loopback白名单（缺 Origin 仅允许同白名单本机 CLI请求）；未知字段/ID拒绝，GET不触发模型。禁用状态页面仍可读历史。
- [ ] 历史分页 offset≥0、limit1..100；cases 过滤 bucket/strategy/status枚举、query≤512字符；参数化/受控路径，无服务器任意文件下载。export format=json|markdown；旧报告注册 read-only legacy-30-v1，不能 cancel/re-run冒充新语料运行。
- [ ] DTO 使用 report.py白名单，隐藏内部调用栈、连接串、raw模型请求及私密响应；公开答案/证据/判定结果与安全失败信息。manager lifespan关闭与API读取并行测试，不共享数据库session。
- [ ] GREEN 同组及原 app启动/健康/SSE测试；记录后审查提交：feat: expose local RAG evaluation workbench API。

### Task 9：前端 Vibe Coding 接入与浏览器验收

**Files:** 修改 app/static/rag-evaluation.html/css/js、聊天页导航；补 docs/validation/rag-evaluation-ui.md。不写前端 TDD，不安排前端子代理规格/质量审查。

**Interfaces:** 仅调用任务8 API；GET轮询2秒，终态停止；页面卸载清理定时器。vector展示映射dense，五桶展示库外名兼容。旧静态URL保持，新正式URL /rag-eval。

- [ ] 对照用户两个页面截图接入数据集/历史选择、试运行/全量、进度/取消、重跑/导出。运行时按钮锁定；409恢复真实活动run，不能通过重复点击创建任务；全量未放行说明匹配试运行要求。
- [ ] 指标切换支持设计全部指标、有效分母、并列领先策略；不做唯一总体冠军卡。生成共同有效子集另列；旧v1缺指标清楚N/A。
- [ ] 详情显示金标组完整组合、候选/前十/Prompt差别、完整原文快照、逐点覆盖、全部断言及错误。数据一律textContent；分页/筛选不运行模型；关闭弹窗恢复焦点。
- [ ] 浏览器用受控API先验收启动/409/取消清理/失败/历史/导出、多页筛选与详情；确认聊天页引用/纯前端👍👎仍可用，控制台无错误，Node语法检查通过。真实试运行与全量的页面状态留到任务10。
- [ ] 立即留截图和dev-notes四项，提交：feat: run and inspect RAG evaluations in the workbench。

### Task 10：工程回归、真实试运行与完整对比交付

**Files:** 更新 README.md、docs/validation/rag-evaluation-materials-audit.md；新增 merchant-rag-pilot.json/md、merchant-rag-comparison.json/md、rag-evaluation-delivery.md；持续 dev-notes/ch04.md。只导出公共白名单报告，不提交runtime私密文件。

**Interfaces:** 消费 tasks1–9 全部接口；不新增算法、模型或预算。真实运行由 /rag-eval 启动，CLI可复现同批，不能同时开两轮。

- [ ] 离线：dataset validate输出300/各60/50chunks/固定10题/全部映射无错误；审标与Prompt样例核验；运行全套默认测试及显式 --run-mysql --run-milvus，一次当前完整绿色后不无故重复。UTF-8/中文函数说明/私密追踪/JS语法/git diff --check全部核验。
- [ ] 后端整分支独立审查；问题逐项验证、修复、相关RED/GREEN和必要回归，真实收费之前核实门槛/默认线上兼容/归属及取消边界；前端例外不补套代码审查。
- [ ] 页面固定 pilot10/40 运行一次，保存指纹、调用数、合法输出、清理和错误。存在错误则保存报告、全量继续锁定，诊断当前失败，不自动提高预算/换模型；技术矛盾按原要求问用户。
- [ ] 合法匹配试运行后，页面运行 frozen full300/1200一次。保存各阶段真实完成/错误/未执行、分桶/总体/共同子集、台账证据；服务端及浏览器读同一run。若部分失败用 completed_with_errors 如实交付，不反复收费全量洗分。
- [ ] 解释实际各策略差距：先看检索组覆盖与首命中，再看生成点覆盖/忠实度/拒答及有效分母；核对具体型号BM25位置、口语/跨节错误，声明资料参考金标构造的受控比较局限。不得套教程0.90/0.94/100%或推断永远最好。
- [ ] 验收当前 / 聊天、/rag-eval运行/历史/分页/指标/取消/重跑新ID/导出；检查原业务知识与其他测试资源不受影响，截图真实状态；不为了截图再次收费跑full。
- [ ] README 提供PowerShell启动（--workers 1）、只读/显式启用配置、validate/pilot/full/show命令、接口/页面与报告路径。记录fresh测试结果、真实运行数量和未完成限制。
- [ ] 立即记录code review及finish四项、提交交付文件；使用 finishing-a-development-branch 汇报已完成和真实阻塞，按用户下一步决定整合，当前不合并或推送。

## 计划自审与门槛

2026-10-10 由控制端自审（未派子代理替代计划自审）：

- 设计§1/2边界落实全局约束；§3材料由任务1；§4指标/共同生成由2/3/6；§5隔离/存储/生命周期由4/5/7；§6接口/前端由8/9；§7真实验收由10；§8过程与核验贯彻所有任务。
- 五类 Review Focus 各有命名测试和所属任务；跨模块类型、同名接口与实体资源所有者一致，没有匿名“处理边界”或未定义后继接口。
- 本计划不抄写实现函数体；10个交付单元各自可验收，前端采用用户例外。新增路径仅在实现任务时创建。
- 原 CSV 的归档/行数检查不等于300题审标完成；八篇50块是离线材料事实，不等于已建库。既有1205工程测试结果不代替本次新代码测试。
- 用户已批准书面设计并保留 Subagent-Driven；2026-10-10 以“开始实现”批准本计划，进入任务1。批准时新评估后端与收费试运行尚未启动。
