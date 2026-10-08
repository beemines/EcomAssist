# 第四步混合检索与评估 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 在现有客服聊天中跑通中文 BM25/Dense 混合检索、重排、引用与拒答，并交付有真实数字的四策略评估。

**Architecture:** MySQL 保持知识原文权威源，新 Milvus 集合负责两路召回及 RRF；检索服务负责查询理解与重排，生成前独立组装证据并判断充分性。现有单轮工具聊天负责审计、SSE 和最终提交，评估复用同一检索、证据和回答校验接口。

**Tech Stack:** 现有 Python 3.11–3.13、FastAPI 0.142.2、SQLAlchemy 2.0.54/MySQL、LangChain Core/OpenAI 1.6.x、PyMilvus/Milvus 3.0.2；BGE-M3；Milvus 原生 BM25/chinese analyzer/hybrid_search/RRFRanker；SiliconFlow BAAI/bge-reranker-v2-m3。

**Spec:** [2026-10-08-hybrid-retrieval-design.md](../specs/2026-10-08-hybrid-retrieval-design.md)。用户“是的，继续”批准该书面 Spec。执行方式沿用已选择的 Subagent-Driven；本计划保存后仍需用户审阅，之后开始实现。

## Global Constraints

- 两路各 Top-50，RRFRanker(k=60) 融合 Top-50，bge-reranker-v2-m3 重排 Top-10；不能用客户端 BM25、拼关键词 LIKE 或其他重排模型替换。
- 新集合 knowledge_hybrid：id/embedding/text/category/sparse；embedding=1024、FLAT/COSINE；TEXT/chinese/BM25，SPARSE_INVERTED_INDEX/DAAT_MAXSCORE，k1=1.2、b=0.75，Strong 一致性。
- knowledge_chunks 三栏原文保持一份；旧 done 重建不改状态，切换后 pending 仅在向量写入确认后标 done；保持原任务锁名，避免新旧任务锁相互失效。
- 用户两表 DDL 保存 sql/ch04-ddl.sql，SET NAMES utf8mb4；不改列/ENUM/COMMENT，不新增 useful 列，不用 create_all/drop_all。
- useful=false 才写问题池；外部故障、预算错误和非法自评输出不入池；拒答与问题池同一短事务。
- 同轮最多一个逻辑工具；单轮改写只读本轮原话；keyword 仍是原话连续片段，1–128 字符；category 可选等值过滤，最长 255。
- FAQ 链路 90 秒/0 重试，改写 15 秒、嵌入 20 秒、Milvus 5 秒、重排 20 秒、自评 20 秒、单轮总上限 240 秒；其他工具维持原策略。
- 证据整块裁剪，工具 JSON 满足 20000 字符和 TEXT 65535 UTF-8 字节；稳定引用编号与实际 Prompt 证据全集一致。
- 中文注释、UTF-8；分支 feat/hybrid-retrieval，提交无 ch04 前缀；前端仅 Vibe Coding/浏览器验收，不安排前端 TDD 或代码审查。
- 五桶各 6 题、每桶 easy/medium/hard 各 2；独立校准 8 题；真实 MySQL 测试仅 3308/customer_service_test，Milvus 集合随机唯一命名；真实模型报告与受控报告分开。
- 每任务通过审查后现场追加 dev-notes/ch04.md 四项记录；模型/API 用法先查 Context7；不复制密钥进仓库、日志或子代理提示。

## Review Focus

- 正确数量但错误主键或旧正文的重建：切换检查应失败，不能仅凭 count 放行；Task 3 验证。
- 中文混英文/数字型号及否定条件被改写丢失：检索仍保留原标识，冲突改写回退原话；Task 4 验证。
- 单个长关键条款和 JSON 元数据占满预算：整体舍弃或明确预算错误，不截半句、不把未喂入块当引用；Task 6 验证。
- 自评后取消、最终事务失败或重复上游终止帧：无成功 done，问题池和拒答不得部分提交；Task 7 验证。
- 分块的 [n]、过期编号和超出 JS 安全整数的身份：映射限定本轮、引用安全渲染、ID 始终字符串；Task 7 后端验证，Task 9 浏览器验证。

## 文件职责与执行顺序

1. app/quality/ 保存 DDL 迁移、问题池/编造台账类型、仓储及处置 CLI。
2. app/retrieval/ 保存混合索引类型、Milvus 适配、查询理解、云端重排和检索组合服务。
3. app/knowledge/hybrid_jobs.py 负责 done 重建与 pending 双写；原分块/挖掘模块不重写。
4. app/core/evidence.py、sufficiency.py、answer_validation.py 负责预算/编号、自评与正常回答校验；tool_chat.py 负责运行流程，不塞入索引/评估细节。
5. evals/retrieval_metrics.py、faithfulness.py、evaluate_retrieval.py、retrieval_cases.jsonl、retrieval_calibration.jsonl 负责评估；数据与算法分开。
6. app/static/ 原文件承担引用面板与本地反馈；不新增前端框架或后台满意度 API。

Task 1→2→3→4→5→6→7→8→9→10 顺序执行。每项 backend task 都由新实现代理完成、独立审查通过后再进行下一项；前端任务按例外由当前代理直接迭代。

各任务中的代码块给出测试名称与关键断言；其中场景 fixture 在该任务列出的测试文件中定义，准备条件以对应测试步骤为准，不从未定义的跨任务辅助模块导入。

执行开始时读取 using-git-worktrees、subagent-driven-development、TDD 技能；检查 attached worktrees，使用包含本 Spec/Plan 的当前 master 创建或复用合适隔离工作树。旧三步工作树不得当成最新 master；本地 .env 只复制到被忽略的工作目录。先记录基线，不安装新模型框架或修改 Docker 镜像版本。

## Task 1：原样 DDL、拒答事务与编造台账

**Files:** Create sql/ch04-ddl.sql、app/quality/{__init__,types,migration,repository,cli}.py；Modify app/db/models.py；Test tests/test_quality_mapping.py、tests/integration/test_quality_repository.py、tests/integration/test_quality_migration.py。

**Interfaces:**
- Consumes Database.session()、ConversationRepository、MessageRecord/record_from_message、原 conversations/messages 表。
- Produces FaithCaseInput(eval_id: str, bucket: str, query: str, strategy: str, answer: str, reason: str, citations: list[dict], judge_model: str | None)；QualityRepository(database)。
- Produces async migrate_quality(database: Database) -> None；async QualityRepository.commit_refusal(conversation_id: str, answer: AIMessage, *, raw_question: str, source: Literal['retrieval_low_conf','self_check'], reason: str) -> int。
- Produces async record_fabrication(case: FaithCaseInput) -> None、async resolve_case(eval_id: str, status: Literal['未解决','已解决','无需解决'], resolution: str | None) -> None、async list_cases(status: str | None = None) -> list[dict]。

- [x] **1. 编写 RED 测试。** 原样中文 DDL/ENUM/默认值一致；不存在 useful 列；重复迁移只核验，部分表存在拒绝；拒答两项写入同事务、故障全部回滚；同 eval_id 两次编造只一行/count=2，已处置复发清空说明并保留 resolved_at；并发 upsert 不丢次数，空说明拒绝。
  ```python
  def test_pool_mapping_has_no_useful_column():
      assert 'useful' not in LowConfidenceQuestion.__table__.c
  def test_recurrent_case_reopens_without_losing_resolution_time(recurrent_case):
      row, previous_resolved_at = recurrent_case
      assert row.seen_count == 2 and row.status == '未解决'
      assert row.resolution is None and row.resolved_at == previous_resolved_at
  def test_refusal_transaction_rolls_back_both_writes(failed_refusal):
      assert (failed_refusal.assistant_count, failed_refusal.pool_count) == (0, 0)
  ```
- [x] **2. 运行 RED。** `.venv/Scripts/python.exe -m pytest tests/test_quality_mapping.py tests/integration/test_quality_repository.py tests/integration/test_quality_migration.py --run-mysql -q`；在独立 owned schema 准备原 conversations/messages 前提，失败应来自缺失的新映射/行为，不能来自未启动数据库。
- [x] **3. 实现原 DDL 迁移和仓储接口。** 模型对应原字段及 COMMENT；MySQL dialect insert().on_duplicate_key_update 原子加计数，显式更新 last_seen_at；不用 INSERT RETURNING，flush 得到最终消息 ID。最终拒答事务不自动重试。CLI 支持 migrate、cases、resolve，限制状态/说明并安全打印错误类型。
- [x] **4. 运行 GREEN。** 同一命令全部通过，SQL 结构与用户原文对照通过；检查参数绑定、并发和只清理 owned 数据。
- [x] **5. 审查、留痕、提交。** 审查后提交 `feat: add quality pool and faithfulness case ledger`，追加本任务四项记录。

## Task 2：原生中文 BM25 混合索引

**Files:** Create app/retrieval/{__init__,types,milvus}.py；Test tests/test_hybrid_milvus.py、tests/integration/test_hybrid_milvus.py；Modify app/config.py、.env.example；旧 app/knowledge/vectors.py 保留以支持既有评估。

**Interfaces:**
- Produces IndexedChunk(id: int, embedding: list[float], text: str, category: str)，VectorHit 复用 app.knowledge.types。
- Produces HybridMilvusIndex(uri: str, *, collection: str = 'knowledge_hybrid', client=None, timeout: float = 5)。async ensure_collection() -> None、async upsert(rows: list[IndexedChunk]) -> list[int]、async get_rows(ids: list[int]) -> list[IndexedChunk]、async verify_rows(rows: list[IndexedChunk]) -> None、async all_ids() -> set[int]、async aclose() -> None。
- Produces async recall(vector: list[float] | None, text: str | None, *, strategy: Literal['dense','bm25','hybrid'], category: str | None = None) -> list[VectorHit]，所有候选最多 50。
- Settings 增加 MILVUS_COLLECTION（默认 knowledge_hybrid）；模型和维度固定，不增加替代 BM25 模式。

- [ ] **1. 编写 RED 测试。** 核验五字段、TEXT/chinese/BM25 函数、两索引和 Strong；schema 错误不 drop；两路相同参数化 category 前过滤；重复 id/无效向量/错误确认拒绝；无分类时无筛选表达式；实际 analyzer/型号检索。
  ```python
  def test_hybrid_requests_use_equal_prefilters_and_limits(hybrid_call):
      dense_request, sparse_request, ranker, hybrid_limit = hybrid_call
      assert dense_request.limit == sparse_request.limit == 50
      assert dense_request.expr_params == sparse_request.expr_params == {'category': '耳机'}
      assert ranker.dict() == {'strategy': 'rrf', 'params': {'k': 60}}
      assert hybrid_limit == 50
  def test_real_bm25_model_search_stays_inside_category(filtered_hits, headphone_ids, target_model_id):
      hit_ids = [hit.id for hit in filtered_hits]
      assert target_model_id in hit_ids[:10] and set(hit_ids) <= headphone_ids
  ```
- [ ] **2. 运行 RED。** `.venv/Scripts/python.exe -m pytest tests/test_hybrid_milvus.py -q`；集成测试加 `tests/integration/test_hybrid_milvus.py --run-milvus`，随机集合初始化由 fixture 拥有，缺少新实现或错误过滤应失败。
- [ ] **3. 实现 HybridMilvusIndex。** 用 PyMilvus FunctionType.BM25/AnnSearchRequest/RRFRanker；匹配 Global Constraints。按 PK 写全部字段，读回字段核验；verify_rows 对 Dense float32 比较使用明确容差，text/category 精确一致。外部注入 client 不由适配器关闭。
- [ ] **4. 运行 GREEN。** 受控调用参数测试与真实 Milvus 测试都通过；确认具体型号在过滤范围内命中，而非仅断言 token 非空。
- [ ] **5. 审查、留痕、提交。** `feat: add native Chinese BM25 and RRF retrieval index`。

## Task 3：done 全量重建与 pending 增量恢复

**Files:** Create app/knowledge/hybrid_jobs.py；Modify app/repositories/knowledge.py、app/knowledge/cli.py、scripts/run-knowledge-daily.ps1（仅必要说明/参数）；Test tests/test_hybrid_jobs.py、tests/test_knowledge_cli.py、tests/integration/test_hybrid_recovery.py。

**Interfaces:**
- Consumes IndexedChunk、HybridMilvusIndex、Embedder.embed(texts)、embedding_text、KnowledgeRepository.pending/mark_done、原 job_lock。
- Produces async KnowledgeRepository.done_page(*, after_id: int = 0, limit: int = 20) -> list[ChunkRecord]。
- Produces HybridKnowledgeJobs(repository, embedder, index)；async rebuild_done(batch_size: int = 20) -> dict、async vectorize_pending(batch_size: int = 20) -> int、async verify_done(batch_size: int = 20) -> dict。rebuild_done 调用后逐批读回，最终比较 done 主键全集；verify_done 返回 ready/mysql_count/vector_count/missing_ids/extra_ids/mismatched_ids，ready=false 时 CLI 非零退出。读回 text/category 与 MySQL 精确比较，Dense 验维度及有限值；不为独立核验再重复全量云端嵌入。
- CLI 增加 rebuild-hybrid、verify-hybrid（各 --batch-size，默认 20）；init-vectors/vectorize-pending/run-daily 使用配置的混合集合。旧 Dense helper 不再被新 CLI 误调用。

- [ ] **1. 编写 RED 测试。** done 可被新集合重建且状态不改；pending 不被重建标 done；批次中断后相同主键重跑无重复；虚假 ACK 不标 done；数量相等但错 id、错误 text/category 或额外 id 导致校验失败；每日任务共用原锁。
  ```python
  async def test_rebuild_covers_done_without_promoting_pending(rebuilt_index, mysql_done_ids, pending_row):
      assert mysql_done_ids == await rebuilt_index.all_ids()
      assert pending_row.vectorize_status == 'pending'
  def test_interrupted_rebuild_resumes_with_same_primary_keys(recovered_ids):
      actual, before, missing = recovered_ids
      assert actual == before | missing
  def test_equal_count_with_wrong_text_cannot_pass_cutover(verification):
      assert not verification['ready']
  ```
- [ ] **2. 运行 RED。** `.venv/Scripts/python.exe -m pytest tests/test_hybrid_jobs.py tests/test_knowledge_cli.py -q`；恢复集成单独 `tests/integration/test_hybrid_recovery.py --run-mysql --run-milvus`。
- [ ] **3. 实现分批工作与 CLI。** 外部嵌入/索引调用不持 MySQL 写事务，任务锁覆盖整个命令；text/category 和 Dense 一起 upsert，ACK/读回正确才做下一步；pending 的 mark_done 只发生在当前新集合成功写入后。验证失败退出非零，不自动清旧集合或重置状态。
- [ ] **4. 运行 GREEN。** 假中断和真实 owned 任务中断恢复验证都通过；记录原主键集、新主键集及复跑结果。任务程序进程中断只针对本次创建的进程。
- [ ] **5. 审查、留痕、提交。** `feat: rebuild hybrid knowledge index and resume pending writes`。

## Task 4：单轮查询理解与云端重排适配

**Files:** Create app/retrieval/query.py、rerank.py；Modify app/retrieval/types.py、app/core/prompts.py、app/config.py、.env.example；Test tests/test_query_understanding.py、tests/test_reranker.py；Create evals/query_understanding_cases.jsonl。

**Interfaces:**
- Produces QueryPlan(standard: str, expansions: list[str])（Pydantic 严格对象；standard 最长 512，扩展最多 4 个、每个最长 64）。QueryPlanner(model, input_budget: int, timeout: float = 15)，async plan(raw_question: str) -> QueryPlan。
- Produces RerankHit(index: int, score: float)；SiliconFlowReranker(settings: Settings, *, http_client=None)，async rank(query: str, documents: list[str], *, top_n: int = 10) -> list[RerankHit]、async aclose() -> None。
- Settings 增加 RERANK_MODEL 固定 BAAI/bge-reranker-v2-m3，RERANK_TIMEOUT_SECONDS=20、QUERY_TIMEOUT_SECONDS=15、RERANK_MIN_SCORE 缺省 None 但线上启用需有限数；校准 CLI 可在该值缺失时运行。.env.example 对阈值只写校准说明，不填空字符串或假定固定值。新增数值配置拒绝布尔值，超时必须有限且正。

- [ ] **1. 编写 RED 测试。** 原始 json 截断/解析器修补/多余字段/非 stop 拒绝；明确型号、数值和否定条件不被丢弃，冲突标准问法确定性回退原话；HTTP 请求正确模型、top_n、return_documents=false；重复/out-of-range/布尔索引、NaN 分数拒绝；取消传播、外部 HTTP 客户端归属正确。
  ```python
  def test_conflicting_rewrite_preserves_original_question(conflicting_plan, raw_question):
      assert conflicting_plan.standard == raw_question
      assert len(conflicting_plan.expansions) <= 4
  def test_cloud_rerank_request_uses_fixed_model(request_json):
      assert request_json['model'] == 'BAAI/bge-reranker-v2-m3'
      assert request_json['top_n'] == 10 and request_json['return_documents'] is False
  ```
- [ ] **2. 运行 RED。** `.venv/Scripts/python.exe -m pytest tests/test_query_understanding.py tests/test_reranker.py -q`，由受控模型/HTTP transport 提供原始回包，不连接云端。
- [ ] **3. 实现两个适配器。** QueryPlanner 明确 method=json_mode、include_raw=True；复用原始 JSON 校验思路并要求 finish_reason=stop。Prompt 保留品牌/型号/金额/条件，把扩展限定为检索。Reranker 校验回包并按分数降序、同分服务顺序返回，最多 min(top_n, 输入数)；不靠返回 document 替换权威正文。
- [ ] **4. 运行 GREEN 与 Prompt 样例。** 同命令通过；标注样例至少含中文口语、品牌/连字符型号、数值、否定、多条件各两条，真实 GLM 对提交的合成样例评估，记录失败但不修改标注使其通过。
- [ ] **5. 审查、留痕、提交。** `feat: normalize retrieval queries and add BGE reranking`。

## Task 5：统一检索服务与 FAQ 契约扩展

**Files:** Create app/retrieval/service.py；Modify app/retrieval/types.py、app/repositories/faq.py；Test tests/test_retrieval_service.py、tests/test_semantic_faq.py。

**Interfaces:**
- Produces ScoredChunk(chunk: ChunkRecord, score: float, score_kind: Literal['cosine','bm25','rrf','rerank'])；RetrievalBundle(query: QueryPlan, strategy: str, candidates: list[VectorHit], matches: list[ScoredChunk])。
- Produces RetrievalService(repository: KnowledgeRepository, embedder: Embedder, index: HybridMilvusIndex, planner: QueryPlanner, reranker: SiliconFlowReranker)。async retrieve(raw_question: str, *, category: str | None = None, strategy: Literal['dense','bm25','hybrid','hybrid_rerank'] = 'hybrid_rerank', query_plan: QueryPlan | None = None) -> RetrievalBundle。
- Produces faq_payload(bundle: RetrievalBundle) -> dict，含 found/matches，matches 至多 10，字段 id/question/answer/category/section_path/score/score_kind；retrieval 元数据含策略和计数，不重复存正文。
- FAQRepository 原位置参数保持可用，新增可选 retriever；新增 async retrieve(keyword: str, *, raw_question: str, category: str | None = None) -> dict。旧 search(keyword, limit=3) 用于旧 Dense 评估；新的聊天工具调用 retrieve。

- [ ] **1. 编写 RED 测试。** 四策略按签名选择路径，BM25 不额外请求嵌入，已注入 query_plan 不重复改写；Dense/RRF/重排的分数类型不混用；取权威 done 正文并复核 category；缺失或 pending id 丢弃后不能伪造命中；重排 index 对齐融合候选，JSON payload 不带 Top-50 正文。
  ```python
  def test_rerank_top_ten_keeps_mysql_authoritative_text(retrieved):
      bundle, output, authoritative_mysql_answer = retrieved
      assert len(bundle.matches) <= 10 and bundle.strategy == 'hybrid_rerank'
      assert output['matches'][0]['answer'] == authoritative_mysql_answer
  def test_four_strategies_share_frozen_query_plan(planner_call_count):
      assert planner_call_count == 1
  ```
- [ ] **2. 运行 RED。** `.venv/Scripts/python.exe -m pytest tests/test_retrieval_service.py tests/test_semantic_faq.py -q`。
- [ ] **3. 实现 RetrievalService 与 FAQ adapter。** 标准问法供 Dense，标准问法+扩展+保留原标识供 BM25，重排使用本轮原问题判断相关性；所有候选按主键去重；使用 get_done 读权威数据。category 进入两路索引而不是结果后过滤代替前过滤。
- [ ] **4. 运行 GREEN。** 同命令通过，旧独立 Dense evaluator 仍能用 search；新路径 found=false 仅表示无合法证据，不把连接异常包装成空结果。
- [ ] **5. 审查、留痕、提交。** `feat: integrate hybrid retrieval behind the FAQ contract`。

## Task 6：证据预算、引用编号及充分性自评

**Files:** Create app/core/evidence.py、sufficiency.py、answer_validation.py；Modify app/core/prompts.py、app/config.py、.env.example；Test tests/test_evidence.py、tests/test_sufficiency.py、tests/test_answer_citations.py；Create evals/sufficiency_cases.jsonl。

**Interfaces:**
- Produces Citation(n: int, chunk_id: str, section_path: str | None, question: str, answer: str)；EvidencePacket(payload: dict, citations: list[Citation], messages: list[BaseMessage], best_score: float | None, strategy: str)。
- Produces build_evidence(*, system: SystemMessage, turns: Sequence[Sequence[BaseMessage]], current: HumanMessage, request: AIMessage | None, payload: dict | None, budget: int) -> EvidencePacket，空工具分支也可构造。
- Produces QualityDecision(useful: bool, reason: str, response_kind: Literal['knowledge','social','clarification'], source: Literal['retrieval_low_conf','self_check'] | None)。SufficiencyService(model, *, input_budget: int, timeout: float = 20, minimum_rerank_score: float | None)，async check(raw_question: str, evidence: EvidencePacket) -> QualityDecision。
- Produces validate_answer(answer: str, finish_reasons: set[str], evidence: EvidencePacket, decision: QualityDecision) -> None；固定 REFUSAL_TEXT='目前的知识资料不足以确认这个问题，我无法给出可靠答案。请补充具体商品或适用条件，或联系人工客服确认。'。Settings 增加 SUFFICIENCY_TIMEOUT_SECONDS=20。

- [ ] **1. 编写 RED 测试。** 整块预算、JSON 双限、历史整轮裁剪；所有候选因尺寸不能放入时报预算错误；最强首/次强尾，编号不因排列改变；模型自评 true 不能放行空知识/低重排分；social/clarification 不得代替有业务事实的知识回答；非法原始 JSON/截断/超时不变成 useful=false；引用必须在本轮且知识回答至少一个。
  ```python
  def test_evidence_keeps_best_at_edges_and_citations_exact(packet_view):
      order, citation_ids, actual_prompt_chunk_ids, payload_json = packet_view
      assert order[0].n == 1 and order[-1].n == 2
      assert citation_ids == actual_prompt_chunk_ids
      assert len(payload_json) <= 20000 and len(payload_json.encode('utf-8')) <= 65535
  def test_empty_or_low_score_evidence_cannot_be_self_approved(decision):
      assert (decision.useful, decision.source) == (False, 'retrieval_low_conf')
  ```
- [ ] **2. 运行 RED。** `.venv/Scripts/python.exe -m pytest tests/test_evidence.py tests/test_sufficiency.py tests/test_answer_citations.py tests/test_tool_history.py -q`。
- [ ] **3. 实现三模块。** 编号在预算选择后确定；展示顺序使用两侧交替规则，不改变编号。自评 json_mode/include_raw 严格验证，缺失阈值在 hybrid_rerank 在线准备阶段明确拒绝。单纯 BM25/Dense/RRF 分数不冒充重排置信度；评估基线使用同一内容自评，报告披露 hybrid_rerank 额外低分门槛。Prompt 列明禁止保证到账/配送日期及工单处理承诺，最终不绑定工具。
- [ ] **4. 运行 GREEN 与评估样例。** 同命令通过；充分性标注集含无证据、无关证据、缺关键条件、完整证据、低分强制拒答、社交/澄清和禁止承诺，真实合成样例结果另存；不用单测假分数校准真实阈值。
- [ ] **5. 审查、留痕、提交。** `feat: ground answers with bounded evidence and sufficiency checks`。

## Task 7：聊天工具、SSE、拒答提交与资源生命周期

**Files:** Modify app/tools/{business,types,executor}.py、app/core/tool_chat.py、app/api/chat.py、app/schemas/chat.py、app/main.py、app/repositories/conversations.py、tests/tool_fakes.py；Test tests/test_hybrid_chat.py、test_hybrid_lifecycle.py、test_tool_executor.py、test_schemas.py、test_stream_lifecycle.py、test_tool_chat_service.py。

**Interfaces:**
- ToolContext 增加 category: str | None = None；ChatRequest 同名可选字段；ToolChatService.prepare(conversation_id: str, message: str, *, category: str | None = None) 保留原参数。
- ToolExecutor 增加可选 overrides: Mapping[str, tuple[float, int]] | None，query_faq=(90,0)，默认仍原 timeout/max_retries；FAQ 文档改为混合检索最多 10，模型看不到会话/分类身份参数。Settings 增加 FAQ_TIMEOUT_SECONDS=90、CHAT_TIMEOUT_SECONDS=240。
- ConversationRepository.append_message 仍返回 int；done={conversation_id: str, message_id: str}。create_app 增加可选 sufficiency_service、quality_repository 注入，其他原注入参数保留。
- citations 事件 data={citations: [Citation 的原始字段对象]}；status 增加 checking；tool 结果持久化使用 EvidencePacket.payload，编号映射不能与实际模型输入分叉。

- [ ] **1. 编写 RED 测试。** 一次选择/一个工具/一次自由文本生成；category 校验和可信闭包；先 citations 后 delta，提交后 done；知识不足仅固定拒答+单条池记录；无工具知识问题自评不足同样拒答；FAQ 故障/非法自评/预算错误无池记录；取消传播、240 秒上限、事务失败无 done；invalid [99]/非 stop/再次工具申请不保存完整回答；超大身份字符串不转浮点。
  ```python
  def test_citations_precede_deltas_and_done_follows_commit(completed_stream):
      events, done, persisted_assistant_id = completed_stream
      assert events.index('citations') < events.index('delta') < events.index('done')
      assert done['message_id'] == str(persisted_assistant_id)
  def test_insufficient_answer_is_fixed_and_persisted_once(refusal_result):
      answer, rows = refusal_result
      assert answer == REFUSAL_TEXT and len(rows) == 1
  def test_failed_or_cancelled_turn_has_no_success_or_pool(failed_turn):
      assert not failed_turn.has_done and not failed_turn.has_pool_row
  ```
- [ ] **2. 运行 RED。** `.venv/Scripts/python.exe -m pytest tests/test_hybrid_chat.py tests/test_hybrid_lifecycle.py tests/test_tool_executor.py tests/test_schemas.py tests/test_stream_lifecycle.py tests/test_tool_chat_service.py -q`；故障触发必须可观测，不能只断言内部函数调用次数。
- [ ] **3. 接入主流程与应用工厂。** FAQ 成功后先选证据、自评，再保存对应 tool 结果；工具失败明确走故障路径。拒答流结束后用 QualityRepository 短事务提交，正常回答用既有仓储；都返回可信 message_id。应用 lifespan 管理自建客户端并保持注入对象外部归属，启动核验集合、阈值和必要表结构，不自动建库或执行产品 DDL。
- [ ] **4. 运行 GREEN 与回归。** 同命令及现有 HTTP/历史/取消测试通过；显式退出 lifespan 验证资源关闭顺序和关闭异常，SSE 多字节/终止事件用真实本地网络测试，不以 ASGI 缓冲结果证明逐 token 到达。
- [ ] **5. 审查、留痕、提交。** `feat: stream cited knowledge answers and persist safe refusals`。

## Task 8：标注数据、校准、四策略报告与忠实度台账

**Files:** Create knowledge-docs/retrieval-models.md、evals/retrieval_cases.jsonl、retrieval_calibration.jsonl、retrieval_metrics.py、faithfulness.py、evaluate_retrieval.py；Test tests/test_retrieval_metrics.py、test_retrieval_evaluation.py、test_faithfulness_judge.py；Modify app/config.py、.env.example、app/quality/cli.py（仅必要输出）。

**Interfaces:**
- Consumes Task 5 retrieve(...query_plan=...)、Task 6 build_evidence/SufficiencyService/validate_answer、Task 1 record_fabrication。评估构造匹配的单次 FAQ 申请和 ToolMessage，复用同一 Prompt/预算/真实模型 astream，不另写一套“更容易过”的生成逻辑。
- Produces retrieval_metrics(ranked_ids: list[int], gold_ids: set[int], *, k: int) -> dict（recall/mrr，空 gold 返回 None）；choose_threshold(samples: list[dict]) -> dict（八题标注、拒答 F1、同分较高门槛、混淆矩阵）。
- Produces FaithfulnessJudge(model, input_budget: int)，async judge(question: str, answer: str, citations: list[Citation]) -> dict，含 claims/support/reason/score，非法输出抛安全错误，不生成编造记录。Settings 增加 FAITH_JUDGE_INPUT_TOKEN_BUDGET=16000、FAITH_JUDGE_MAX_OUTPUT_TOKENS=2048；裁判使用同一 LLM_MODEL/上游的独立模型实例，输出上限取该字段，线上回答仍使用既有 MAX_OUTPUT_TOKENS，不修改共享实例预算。
- CLI `python -m evals.evaluate_retrieval --mode calibrate|compare --output PATH`；可选 `--cases PATH`（比较默认 retrieval_cases.jsonl，校准默认 retrieval_calibration.jsonl）、`--database test|configured`（默认 test）。PATH 为 JSON 报告路径，Markdown 写同 stem 的 .md；两模式均保存逐题检查点。

- [ ] **1. 写固定合成数据和金标。** 30 题五桶，每桶难度各两题；8 校准题独立 ID，型号近邻干扰项、双证据多条件、无答案均具备人工可核对事实。gold_chunk_refs 使用冻结原文的 section_path/questions/answer 三元组，映射到当次导入的 owned chunk，避免同一 FAQ 标题下不同问题都误算相关；缺失映射立即失败。同一三元组若对应多个物理块，明确记录全部相关 ID 和重复数，指标仍遵循 Spec 的 chunk ID 定义，不改成另一套分组评分。纯数据/Prompt 用这套标注集验证替代 TDD。
- [ ] **2. 为可单测评分器/运行器写 RED。** 覆盖多相关块、重复 id、未命中/空 gold、Top-50 与 Top-10 区分、阈值同分、四策略冻结输入、错误/未执行计数、裁判原 JSON 非法、拒答无断言 n/a；只有真实有效 unsupported claim 才调用台账。
  ```python
  def test_metrics_distinguish_partial_recall_and_rank():
      assert retrieval_metrics([20, 10], {10, 30}, k=10) == {'recall': 0.5, 'mrr': 0.5}
  def test_no_gold_is_not_a_perfect_retrieval_result():
      assert retrieval_metrics([20], set(), k=10) == {'recall': None, 'mrr': None}
  def test_refusal_without_claims_is_not_perfect_faithfulness(refusal_faithfulness):
      assert refusal_faithfulness['score'] is None
  def test_failed_run_preserves_unattempted_count(partial_report):
      report, completed, remaining = partial_report
      assert (report['attempted'], report['not_attempted']) == (completed, remaining)
  ```
- [ ] **3. 运行 RED。** `.venv/Scripts/python.exe -m pytest tests/test_retrieval_metrics.py tests/test_retrieval_evaluation.py tests/test_faithfulness_judge.py -q`。
- [ ] **4. 实现评估接口。** 默认测试库/UUID 集合及本次拥有记录，比较前冻结语料/查询/阈值/模型/预算；按三元组将金标映射到物理 ID，再调用 retrieval_metrics，同一命中 ID 只计一次。Faithfulness 逐断言判支持，保留完整证据和裁判版本。所有有效编造判定写台账，不能靠可选开关忽略；test 模式 ledger_eval_id='T'+数据集 eval_id，configured 模式使用数据集原 ID，报告同时保存两种 ID。台账在所选数据库长期保留；清理只移除本次临时知识、会话和集合。configured 模式显式读现有知识/写对应台账，不删除既有知识或台账。报告记录 hybrid_rerank 的分数门槛差异，避免将全部生成变化归因为排序。JSON 逐题检查点+Markdown 总体/五桶四行对照；运行失败写缺失项并非零退出，清理错误也算失败。
- [ ] **5. 运行 GREEN，再真实校准/比较。** 先通过受控回归，再对提交的合成语料做真实八题校准，记录建议阈值并填本地 .env；随后跑四策略，逐题保存 ranked IDs/原问/标准问/全部证据/答案/自评/裁判及耗时。真实模型数量与调用失败如实记录，不自动换模型、扩充输出上限或反复重跑全量。受控报告必须标明 controlled。
- [ ] **6. 审查、留痕、提交。** `test: evaluate four retrieval strategies and persist fabrication cases`；真实报告保存在 docs/validation/hybrid-retrieval-{calibration,comparison}.json 与 Markdown 报告，历史报告不覆盖。

## Task 9：引用来源面板与一次性满意度（Vibe Coding）

**Files:** Modify app/static/index.html、chat.js、chat.css；保存浏览器验收结果到 docs/validation/hybrid-ui.md。

**Interfaces:** Consumes citations/checking/delta/done 及 Task 8 校准结果；message_id/conversation_id/chunk_id 均字符串。本任务直接迭代，不派前端 TDD 或代码审查任务。

- [ ] **1. 直接实现交互。** 已知 [n] 变为按钮，跨增量的半个编号先缓存直到完整；打开可关闭/键盘访问的来源面板，使用 textContent 显示章节与原文。新回复拥有自己的映射。
- [ ] **2. 直接实现反馈。** 成功 done 后在左下角显示 👍/👎，第一次选择点亮并显示“已反馈”，随后禁用；只存页面状态，无后端请求。
- [ ] **3. 浏览器验收。** 在3308测试库/owned知识和唯一集合启动专用本地应用，使用已校准阈值；验证后按所有权清理本任务数据，先删除这些会话关联的问题池/消息/工单，再删会话和本任务知识/集合，保留已生成的编造台账。查看真实引用原文；重复编号都定位同块；两轮 [1] 不串源；含 HTML/脚本字面的原文作为文本；分块 [、1、] 能形成按钮；超大 ID 保留；点击反馈一次锁定，网络面板无反馈 POST；取消回复不显示反馈。
- [ ] **4. 留痕、提交。** `feat: add clickable citations and one-time chat feedback`；记录截图/结果与用户纠偏。前端的运行报错按实际行为修复，不补上用户排除的工作流。

## Task 10：整分支核验、真实聊天验收与交付

**Files:** Modify README.md、dev-notes/ch04.md；Create docs/validation/hybrid-retrieval-results.md、hybrid-retrieval-review.md；按必要修复更新实际涉及文件，不重新改整仓注释或上一轮报告。

**Interfaces:** Consumes Task 1–9 的当前代码、真实评估报告及来源/反馈页面；Produces 当前分支审查结论、真实验收结果、演示命令和 finish 过程记录。本任务不新增业务接口。

- [ ] **1. 总体后端审查。** 按 Spec/Plan 对所有 backend/dataset/CLI 做独立整分支审查，关注 Review Focus 五项、台账复发与跨策略更新、最终事务、资源生命周期和 Prompt 注入边界；前端范围按用户例外排除。发现问题交原实现者修复并定向复核，更新过程记录。
- [ ] **2. 当前代码完整核验。** UTF-8/中文函数说明/无意密钥/`git diff --check`；`.venv/Scripts/python.exe -u -m pytest -q --run-mysql --run-milvus -o faulthandler_timeout=30`。测试库及新表前提先显式准备；Windows 回环限制用已确认的沙箱外本地方式，不改业务代码绕过环境。记录通过/失败/跳过实际数，沿用老结果无效。
- [ ] **3. 当前代码真实聊天。** 本轮 owned 合成会话问具体型号、邮费、带品类过滤、多条件和库外问题；检查 SSE 增量、引用一致、拒答及 MySQL 问题池。Task 8 数字与浏览器结果互相独立记录，ASGI 缓冲不能替代浏览器流式演示。
- [ ] **4. 准备交付命令和文档。** 明确 `python -m app.quality.cli migrate`、`python -m app.knowledge.cli rebuild-hybrid/verify-hybrid`、pending、阈值校准、四策略评估、`uvicorn app.main:create_app --factory --workers 1` 及创建会话/curl -N 调用；curl 上限至少 250 秒。引用和反馈在浏览器验收；人工台账 `cases/resolve` 展示必填说明。
- [ ] **5. 记录 finish、提交并整合。** 所需测试和真实验收通过后追加 finish 四项；交付实际报告路径/限制/命令及 dev-notes。按 finishing-a-development-branch 技能和用户已明确的整合指令处理分支；未获得本步整合选择时交付可审查分支，不强推或重写历史。

## 自审与待执行状态

Spec 覆盖：第 3 节→Task 1–3；第 4 节→Task 4–5；第 5 节→Task 6–7；第 6 节→Task 7/9；第 7 节→Task 1/8；第 8 节→所有任务留痕及 Task 10。所有消费的接口在本任务或前置任务定义，没有未指定的实现替换或占位代码。校准/评估先于浏览器任务，避免在无真实阈值时启动线上质量验收。

计划补明比较口径：四策略复用相同内容自评和生成约束，hybrid_rerank 额外使用已校准的重排低分门槛，基线分数不当概率；报告必须披露该检索策略特有门槛，而不是隐瞒为仅排序变化。此项不变更技术选型或自评入池条件。

本轮 Context7 补查记录保存 .cache/context7-plan-*.txt：SQLAlchemy MySQL insert/on_duplicate_key_update 与 INSERT RETURNING 限制、FastAPI lifespan/async testing、LangChain with_structured_output 的 include_raw/json_mode。安装的 ChatOpenAI 1.6.7 默认 method 为 json_schema，与一段文档摘要的默认值描述不同；计划始终明确指定 json_mode，并复核原始 JSON 和 stop 状态。

接口参考：[SQLAlchemy MySQL](https://docs.sqlalchemy.org/en/20/dialects/mysql.html)、[FastAPI 生命周期](https://fastapi.tiangolo.com/advanced/events/)、[FastAPI 异步测试](https://fastapi.tiangolo.com/advanced/async-tests/)、[LangChain 模型](https://github.com/langchain-ai/docs/blob/main/src/oss/langchain/models.mdx)。

当前为书面计划阶段，所有任务未开始；未创建新工作树、未安装依赖、未执行新 DDL 或收费模型请求。用户审阅本计划后按保留的 Subagent-Driven 方法执行。
