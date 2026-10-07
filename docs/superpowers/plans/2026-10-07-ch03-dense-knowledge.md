# 客服 Dense 知识库 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 用云端 BGE-M3 与本机 Milvus 替换 query_faq 的关键词查表，完成 Markdown/对话建库及中断后的 pending 补齐。

**Architecture:** 当前 FastAPI 应用保留单轮工具流程，MySQL 管理正文和双写状态；Milvus 存显式 chunk 主键及 Dense 向量。离线入口运行切分、抽取、整体精确去重和向量化，外部调度执行每日任务。

**Tech Stack:** 保留 Python 3.11–3.13、现有 FastAPI/LangChain/SQLAlchemy/httpx；新增 PyMilvus 3.0.2、Docker Milvus Standalone 3.0.2；MySQL 8.4；硅基流动 BAAI/bge-m3。

**Spec:** [已批准设计](../specs/2026-10-07-ch03-dense-knowledge-design.md)。用户回复“确认”批准设计；本计划已自查，待用户审阅后执行。执行方式沿用前章已选择的 Subagent-Driven，每次只实现一项，前一项审核后再推进。

## Global Constraints

- `sql/ch03-ddl.sql` 原样保存并执行用户两表 DDL，不新增字段、不删除已有卷、不使用 create_all/drop_all。
- 生产集合 `knowledge`：显式 INT64 `id`、1024 维 `embedding`、auto_id=False、COSINE、FLAT、Strong；MySQL ID 必须在 `1..9223372036854775807`。
- 只有 category/questions/answer 进入固定向量文本；其余元数据仍保存到 MySQL。
- 只做 Dense，K 默认及上限均为 3，不增加关键词、混合、重排、查询改写或未经验证的阈值。
- `query_faq(keyword)` 保留 1–128 字符、原文片段校验及 found/matches/id/question/answer/category 契约。
- 正文切分目标 1200 字符、句子重叠目标 120 字符；整句/表格行不截断；每个表格块复制表头。
- 默认每批最多 20 个已结束会话，时间窗口为北京时间的半开区间，按 id 分页；暂存后全局精确问答去重。
- 每个实施任务先 Context7 核对所用 API 与版本，再 TDD；纯 Prompt/数据用标注评估。每项完成后及时记录 ch03.md、验证并提交。
- `.env` 不提交；不输出 Key/完整个人对话。已有 prompt.md 改动保留。产品 UI 不变。

## Review Focus

1. 深层标题/超长句/表格转义竖线，不能造成 MySQL 长度截断或丢行：任务 1/2 验证明确失败和内容覆盖。
2. SDK 回包乱序、缺项、非有限浮点及 UNSIGNED ID 溢出，不能标记 done：任务 3 验证。
3. Milvus 有结果但 MySQL pending/缺行，不能返回错误正文或退回 LIKE：任务 4 验证。
4. 命名锁占用、取消或释放失败，不能把仍持锁的连接放回池：任务 1/5 验证释放或作废连接。
5. 对话重复批次、无 QA、答案冲突、模拟工具结果，不能伪造知识或重复推广：任务 5 标注评估和事务回归。

## 共享文件与接口

`app/knowledge/types.py` 用 dataclass 定义 Draft/Record/Hit/QA，不引入新数据建模框架：
- `ChunkDraft`：category/questions/answer、section_path/content_type/is_key_clause。
- `ChunkRecord`：上述字段加 id/prev_chunk_id/next_chunk_id/vector_id/vectorize_status。
- `VectorHit(id: int, score: float)`；`ExtractedQA(source_ref: str, question: str, answer: str)`；`StagedQA` 在 QA 字段上加 id/batch_no/status。
- `ConversationTranscript(id: int, last_message_id: int, messages: list[MessageRecord])`，MessageRecord 复用现有 app.repositories.records。
- `embedding_text(chunk: ChunkDraft | ChunkRecord) -> str`，固定 `category: ...\nquestions: ...\nanswer: ...`。

仅这两个 I/O 边界使用 Protocol，便于离线替身：`Embedder.embed(texts: list[str]) -> list[list[float]]` 与 `VectorIndex.upsert(rows: list[tuple[int, list[float]]]) -> list[int] / search(vector: list[float], limit: int=3) -> list[VectorHit]`，全部异步；自有客户端提供 `aclose()`。

### Task 1: 权威 DDL、事务仓储与单实例锁

**Files:** 创建 sql/ch03-ddl.sql、app/knowledge/__init__.py、app/knowledge/types.py、app/knowledge/locking.py、app/repositories/knowledge.py、app/knowledge/migration.py；修改 app/db/models.py、compose.yaml、tests/conftest.py、tests/test_db_mapping.py、tests/integration/test_mysql_schema.py；创建 tests/test_knowledge_mapping.py、tests/test_knowledge_validation.py、tests/integration/test_knowledge_repository.py、tests/integration/test_knowledge_migration.py。

**Interfaces:** `KnowledgeRepository(database)` 提供异步 `add_chunks(drafts: list[ChunkDraft], link_neighbors: bool=False) -> list[int]`、`pending(limit: int=20) -> list[ChunkRecord]`、`mark_done(ids: list[int]) -> None`、`get_done(ids: list[int]) -> list[ChunkRecord]`、`stage(batch_no: str, items: list[ExtractedQA]) -> None`、`extracted() -> list[StagedQA]`、`qa_pairs() -> list[tuple[str,str]]`、`promote(kept_ids: list[int], discarded_ids: list[int]) -> list[int]`。`job_lock(database)` 为异步上下文管理器；`migrate(database) -> None` 执行与检查 DDL。

- [ ] 写红测试：映射与原 DDL 对齐；事务结束后 pending 可读；链接双向正确；mark_done 回填相同 ID；promote 与状态同事务；验证 category 255、section_path 512 字符及 TEXT 65535 UTF-8 字节上限，超限失败而非截断。
- [ ] 添加真实数据库断言（fixture 只拥有自己的行）：
  ```python
  ids = await repo.add_chunks([draft_a, draft_b], link_neighbors=True)
  rows = await repo.pending()
  rows_by_id = {r.id: r for r in rows}
  assert rows_by_id[ids[0]].next_chunk_id == ids[1]
  assert rows_by_id[ids[1]].prev_chunk_id == ids[0]
  await repo.mark_done(ids)
  assert [r.vector_id for r in await repo.get_done(ids)] == list(map(str, ids))
  ```
- [ ] 先运行新增单元测试，确认因缺失实现失败；真实仓储红测试先明确 fixture 的 schema 前置，不能把连接错误算红测试。
- [ ] 实现最小映射/仓储/迁移：原 SQL 客户端语义，表已存在必须比对；所有数据库工作短事务。迁移先检查目标数据库和新表状态，部分存在拒绝，不用 IF NOT EXISTS 吞错。
- [ ] 原四表测试保留字段与约束验证，只将表集合扩大到六表；新增用例独立核查两个新表，不能删除原有约束断言。
- [ ] 锁使用独占连接 `GET_LOCK(name,0)`；name 为 `ch03:` 加数据库名 SHA256 前 48 位，成功值必须为 1。finally 同一连接 RELEASE_LOCK；失败作废连接，不能仅 close 回池。两个连接互斥及异常释放都做真实测试。
- [ ] 更新 Compose 新卷初始化 SQL 挂载顺序；运行 `uv run --locked pytest tests/test_knowledge_mapping.py tests/test_knowledge_validation.py -q`，迁移独立测试库后运行新增 MySQL 测试 `--run-mysql`；记录日志和证据，审核后提交本任务文件。

### Task 2: Markdown 切分与 pending 文档导入

**Files:** 创建 app/knowledge/chunking.py、app/knowledge/ingestion.py、app/knowledge/cli.py、knowledge-docs/demo-policy.md、knowledge-docs/demo-faq.md、knowledge-docs/demo-manual.md、tests/test_knowledge_chunking.py、tests/test_knowledge_ingestion.py。

**Interfaces:** `chunk_markdown(text: str, *, document_name: str, content_type: str, target_chars: int=1200, overlap_chars: int=120) -> list[ChunkDraft]`；`import_document(path: Path, content_type: str, repository: KnowledgeRepository) -> list[int]`。CLI 初始提供 `migrate` 和 `import-document --path PATH --type policy|faq|manual`，文档导入只提交 pending；后续任务提供向量化命令。

- [ ] 写红测试：ATX 路径、围栏中井号、无标题、Q/A 多问法、章节标记、中文和英文句子闭合引号、价格小数点不切开、整句超目标长、只有空正文、大表格表头复制/转义竖线与代码内竖线、跨文档指针隔离。例如：
  ```python
  chunks = chunk_markdown('# 售后\n## 退货\n七天内可申请。', document_name='政策', content_type='policy')
  assert (chunks[0].category, chunks[0].questions, chunks[0].answer) == ('售后', '退货', '七天内可申请。')
  assert chunks[0].section_path == '售后/退货'
  assert chunks[0].content_type == 'policy'
  ```
- [ ] 运行 `uv run --locked pytest tests/test_knowledge_chunking.py tests/test_knowledge_ingestion.py -q`，确认缺失模块/算法导致失败。
- [ ] 实现标题栈→段落→整句递归拆分；重叠只取末尾完整句子；表格按完整行切分并重复表头。切分器仅标准库，不套额外 LLM 或文档服务。
- [ ] 实现 import_document：先读/校验整份文档，再以 Task 1 单事务插入，失败回滚；CLI 用 argparse，资源在 finally 释放、失败非零退出。多个命令共用 job_lock。
- [ ] 标注明确的合成演示运费：标准配送 8 元、满 99 元包邮，仅限样例写明范围；正文内容覆盖、重叠和每行出现次数按固定样例验证，不冒称真实商家政策。
- [ ] 运行单元测试及 MySQL 指针/回滚集成；记录并审核、提交。

### Task 3: 云端嵌入、Milvus 与可恢复向量化

**Files:** 创建 app/knowledge/embeddings.py、app/knowledge/vectors.py、app/knowledge/vectorization.py、compose.milvus.yaml、tests/ch03_fakes.py、tests/test_knowledge_embeddings.py、tests/test_knowledge_vectors.py、tests/test_knowledge_vectorization.py、tests/integration/test_knowledge_milvus.py；修改 pyproject.toml、uv.lock、app/config.py、.env.example、app/knowledge/cli.py、tests/conftest.py。

**Interfaces:** `SiliconFlowEmbedder(settings, *, http_client=None)` 实现 Embedder；`MilvusIndex(uri: str, *, collection: str='knowledge', client=None)` 实现 VectorIndex，另有 `ensure_collection() -> None`；`PendingVectorizer(repository, embedder, index).run(batch_size: int=20) -> int` 返回本次转 done 数量。测试替身 `MemoryVectorIndex` 必须按主键覆盖并能检查 upsert 次数与唯一 id；`RecordingEmbedder` 记录收到的文本。

- [ ] Context7 核对 httpx 0.28.1、硅基流动批量 embeddings 与 PyMilvus 3.0.2；安装后对实际 SDK 方法签名、返回结构和 lazy connection 检查。先锁依赖、更新 uv.lock，再运行测试，不能照搬 master 文档。固定版本不能安装/运行时停下询问。
- [ ] 写红测试：只向量化三字段；HTTP 回包 index 乱序可正确还原；重复/缺失 index、数量错误、维度错误、bool/NaN/Inf 拒绝；SDK 返回主键不匹配和 ID 溢出不调用 mark_done。
  ```python
  assert embedding_text(draft) == 'category: 运费\nquestions: 配送费用\nanswer: 标准配送8元。'
  assert await worker.run() == 1
  assert memory_index.ids == {chunk_id}
  assert (await repo.get_done([chunk_id]))[0].vector_id == str(chunk_id)
  ```
- [ ] 运行三个新单元文件确认红；实现直接 POST 云端 API、严格验证向量，不增加模型 SDK/网关或无限重试。新增 SecretStr 配置字段接纳 SILICONFLOW_API_KEY；旧无向量能力的测试设置允许 None，实际调用时明确失败，不把缺 Key 解释成无命中。
- [ ] 新增 MILVUS_URI 默认 http://127.0.0.1:19530；EMBEDDING_TIMEOUT_SECONDS 默认 20、MILVUS_TIMEOUT_SECONDS 默认 5；EMBEDDING_MODEL 只允许 BAAI/bge-m3。客户端异步 I/O，aclose 只关闭自有实例；在线工具原总期限仍由 ToolExecutor 控制。
- [ ] 向量集合校验显式 schema/index/metric/dimension；已存在不匹配拒绝。worker 读 pending→embed→upsert→验证 ids→短事务回填；任何错误/取消不会后续标记成功。增加 CLI `init-vectors`、`vectorize-pending --batch-size 20`。
- [ ] Compose 使用官方 3.0.2 Standalone 配置和独立卷，Milvus 仅绑定本机；etcd/对象存储不另行公开端口，保留原 MySQL 服务。`docker compose -p ecs-knowledge -f compose.milvus.yaml up -d --wait --wait-timeout 180` 后先核查版本/就绪。
- [ ] 模拟 MySQL pending 后失败及 Milvus 成功但 mark_done 失败，重跑断言唯一 id、done 数量正确；实际 SDK 集成通过 `--run-milvus` 显式开启，只创建/清理 knowledge_test_*。记录、审核后提交。

### Task 4: 在线 query_faq 语义检索与应用生命周期

**Files:** 修改 app/repositories/faq.py、app/tools/business.py、app/main.py、tests/integration/test_business_repositories.py、tests/fakes.py 及依赖 FAQ 的测试入口；创建 tests/test_semantic_faq.py、tests/test_knowledge_lifecycle.py；保留 tests/test_business_tools.py 的原文校验/输出契约回归。

**Interfaces:** `FAQRepository(database, embedder: Embedder, index: VectorIndex)`，`search(keyword: str, limit: int=3) -> list[dict]` 签名保留；`create_app` 增加可选 `faq_repository` 注入，避免离线测试建立真实云端/向量连接。

- [ ] 写红测试：向量命中 ID 顺序与 SQL 结果不同仍保持相似度顺序；pending/缺行过滤，最多三条；不改 query 原文；失败为工具错误；没有向量调用时不能返回旧 LIKE 命中。
  ```python
  result = await faq.search('邮费是多少', limit=10)
  assert [row['id'] for row in result] == [shipping_id, returns_id]
  assert set(result[0]) == {'id', 'question', 'answer', 'category'}
  assert recording_embedder.texts == ['邮费是多少']
  ```
- [ ] 运行 `uv run --locked pytest tests/test_semantic_faq.py tests/test_knowledge_lifecycle.py -q` 确认红；实现 embed 原文→Dense Top-3→get_done→按 hit 顺序投影旧字段，不增加其他回退分支。
- [ ] 更新工具说明为语义检索，保留 FAQArgs 字段和连续原文校验；应用工厂创建/拥有客户端并在 lifespan 释放。注入 FAQ 时不创建向量客户端；初始化异常也释放已经创建的自有资源。
- [ ] 按新行为替换旧“真实 LIKE/邮费必无命中”的集成用例，保留 MySQL 原文与事务验证；无关工单测试改注入 FAQStub。新测试不能请求真实提供方，不以跳过旧失败作为通过。
- [ ] 针对外层取消/工具超时验证没有后续检索或模型重试；测试原配置及未知字段约束。运行全套离线测试和相关真实 MySQL/Milvus 检索集成，记录审核后提交。

### Task 5: 对话挖 QA、暂存推广与外部定时入口

**Files:** 创建 app/knowledge/extraction.py、app/knowledge/history.py、app/knowledge/mining.py、tests/test_knowledge_extraction.py、tests/test_knowledge_mining.py、tests/test_knowledge_cli.py、evals/qa_extraction_cases.jsonl、evals/evaluate_qa.py、scripts/run-knowledge-daily.ps1；修改 app/core/prompts.py、app/knowledge/cli.py；MySQL 集成补到 tests/integration/test_knowledge_repository.py。

**Interfaces:** `KnowledgeHistory(database).completed(start: datetime, end: datetime, after_id: int=0, limit: int=20) -> list[ConversationTranscript]` 按 conversation.updated_at 的半开窗口及 id 分页；`QAExtractor(model, input_budget: int).extract(conversations: list[ConversationTranscript]) -> list[ExtractedQA]`；`normalize_qa(question: str, answer: str) -> tuple[str,str]`；`ConversationMiningJob(history, repository, extractor).run(start: datetime, end: datetime, batch_size: int=20) -> dict[str,int]` 返回 conversations/staged/kept/discarded 统计。

- [ ] 先查 Context7 确认锁定 LangChain 的 with_structured_output/json_mode/include_raw 及 Pydantic 原始 JSON 校验。复用现有 ChatOpenAI 构建和现有提取服务的完整输出检查；新 schema 包含 source_ref/question/answer，source_ref 必须属于输入批次，不能由模型伪造来源。
- [ ] 写红测试：时间窗口/排序/批次与消息预算；单会话超预算失败不截断；无 QA 返回空列表；同批重复、跨批规范化重复和已入库重复丢弃，答案冲突保留；promotion 失败 staging 不转 kept；重复窗口不产生重复知识。
  ```python
  assert normalize_qa('　邮费多少？\n', '标准配送  8元。') == ('邮费多少?', '标准配送 8元。')
  assert counts['kept'] == 1
  assert counts['discarded'] == 1
  assert await rerun_same_window() == 0  # 返回新增知识数量的测试辅助函数
  ```
- [ ] 明确测试辅助函数在本任务测试中包裹 job.run 并返回 kept，不新增产品接口。运行新增提取/挖掘/CLI 测试，确认红。
- [ ] 实现由稳定时间窗口/会话 id/末条消息 id 派生 SHA256 batch_no，分批抽取后 stage；已有同 batch/source/question/answer 不重复暂存。整体 normalize_qa 后将 promotion 与状态转换置于 Task 1 事务，kept 不再次推广。
- [ ] 所有命令使用 job_lock；完整 daily 只持一个锁，内部步骤不再次 GET_LOCK。取消及释放失败作废锁连接；模型/HTTP/SDK 资源释放复用生命周期管理。CLI 增加 `mine-conversations --start ISO --end ISO --batch-size 20`、`deduplicate-staging`、`run-daily`（北京时间前一日）、`vectorize-pending`。
- [ ] Prompt/标注样例覆盖 8 类：通用问法、重复 QA、答案冲突、无客服答案、个案标识、虚构退款承诺、mock 工具数据、提示注入；运行受控结构校验，再用真实 LLM 跑标注评估。误抽取返工 Prompt，不加自动纠错链。
- [ ] PowerShell 启动脚本固定项目绝对路径与 uv 工作目录、返回原退出码；提供 Windows 任务计划程序每日 02:00 执行的注册命令，重复运行失败非零退出。评估报告明确哪些实际运行、哪些未尝试。验证记录、审核后提交。

### Task 6: 真实召回、中断恢复、审查与交付

**Files:** 创建 evals/knowledge_cases.jsonl、evals/evaluate_knowledge.py、evals/knowledge_recovery.py、tests/test_knowledge_evaluation.py、docs/validation/ch03-results.md；修改 README.md、evals/tool_cases.jsonl（邮费预期改为向量命中）、docs/superpowers/plans/2026-10-07-ch03-dense-knowledge.md、dev-notes/ch03.md。

**Interfaces:** 评估通过 Task 4 FAQ 和已有应用创建会话/SSE、审计持久消息；恢复 harness 使用实际 MySQL/Milvus 与独立测试行/集合，不向产品加入故障 API。JSON 报告字段包含 attempted/not_attempted、expected/actual hit ids、tool result、final_answer、latency、answer_review 和恢复前后状态/唯一主键计数。

- [ ] 标注检索样例至少 6 条：邮费是多少、快递费用怎么收、发货运费标准、退货运费谁付、售后申请及域外问题；明确预期章节。先写报告统计/失败停机红测试，再实现评估，不能把替身质量当真实质量。
- [ ] 先验证模型实际返回 1024 维和集合 schema，再导入 demo 文档并执行 pending 向量化；确保原问法语义检索命中运费知识且未改写查询。
- [ ] 实际应用端创建独立演示会话，发送“邮费是多少”，审计实际 query_faq、原文参数、正确知识、正常 SSE done 与持久回答；回答需包含 8 元/满99包邮及适用范围，人工检查事实而非仅关键词匹配。超时/配置问题如实失败，不随意换模型。
- [ ] 恢复 harness 启动自己创建的子进程：一次在提交 pending 后、一次在真实 upsert 返回但 mark_done 前，包装 I/O 客户端写检查点并阻塞；父进程只终止它拥有的 PID，然后启动正常 worker 重跑。断言所有预期 done、唯一向量 id 无重复、正文未丢；记录重启检查，不能用抛异常替代真实进程中断。
- [ ] 执行 `uv run --locked pytest -q`、`uv run --locked pytest tests/integration --run-mysql --run-milvus -q`、真实标注提取及在线评估、`git diff --check`。显式要求的集成环境不就绪应失败，普通 gating skips 单列说明，不冒称全部运行。
- [ ] 使用 requesting-code-review 完成整分支独立审查；按 receiving-code-review 核实建议，修复后重跑受影响验证。及时记录每条结论与返工。
- [ ] README 给出保留既有 MySQL 项目的迁移、Milvus 启动、import-document→vectorize-pending、mine-conversations、run-daily、每日定时部署和原问法聊天命令。记录完整测试结果与未解决限制。
- [ ] 使用 verification-before-completion 和 finishing-a-development-branch；只有要求的真实验收及审查通过才报告完成。此次只授权功能开发，Git 合并/推送方式按本章 finish 决策，前章发布授权不自动扩展；保留 prompt.md 的原有改动。

## 计划自查

- Spec 覆盖：两表/指针/权威原文→1；文档结构/重叠/表格→2；云端/集合/主键双写恢复→3；旧工具契约→4；历史抽取/暂存/整体去重/外部定时→5；真实问法、中断及交付→6。
- Review Focus 的五类输入全部有归属测试。命名锁归属 1，命令复用归属 5；没有跨任务重复持锁。
- Task 1 定义共享类型和所有仓储接口，后续任务只消费这些名称；所有替身/辅助函数在所属任务中创建，不依赖未定义的产品方法。
- 保留 TDD 红→绿→记录/审核/提交；Prompt/数据走标注评估例外。没有 TODO/TBD 或以“适当测试”代替命令。
- 此为实施要求，尚未安装产品依赖、执行测试或完成产品功能；用户计划审阅与执行确认仍待完成。
