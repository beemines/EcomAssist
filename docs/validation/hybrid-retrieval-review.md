# 第四步后端审查记录

任务审查原文按阶段保存。前端按用户明确的 Vibe Coding 例外，没有安排代码审查；其浏览器交互证据另见 hybrid-ui.md。最终整体审查、统一修复与定向复核已完成；完整显式MySQL/Milvus回归1205项通过。云端质量限制保留，尚未合并或推送。


## task-2-review

### Spec Compliance

- ✅ Spec compliant：本任务指定的 9 个产品/测试文件均有对应差异。`app/retrieval/types.py:9` 提供 IndexedChunk 四字段；`app/retrieval/milvus.py:46` 创建并核验五字段、TEXT/chinese/BM25、1024 维 FLAT/COSINE、固定稀疏索引与 Strong；`app/retrieval/milvus.py:123`、`:153`、`:180`、`:193`、`:214`、`:255` 实现全部指定接口，并复用 VectorHit。`app/config.py:31` 与 `.env.example:32` 提供默认 knowledge_hybrid 集合配置。
- ✅ 检索参数符合要求：`app/retrieval/milvus.py:225` 两路共享参数化 category 前过滤；`:228` 每路 Top-50；`:230` RRFRanker(k=60) 融合 Top-50；无分类时省略表达式。`tests/test_hybrid_milvus.py:43` 使用真实 SDK 请求对象检查上述参数。
- ✅ 已批准的 API/config 调整得到实现：`app/retrieval/milvus.py:39` 全部适配器 RPC 传 timeout=None/retry_times=0/retry_on_rate_limit=False；`:17` 外层取消感知期限涵盖初始化；`:59` 创建、索引、加载分别调用。SDK 固有同主键 Schema 刷新例外被明确记录，未宣称严格一次物理写入。`config/milvus-user.yaml:2` 与 `compose.milvus.yaml:73` 启用并只读挂载 StorageV3；category 的 255 字符/1020 字节契约分别在 `app/retrieval/types.py:21` 与 `app/retrieval/milvus.py:54` 实现。
- ✅ 差异中额外的 Spec/Plan 与 dev-notes 修改来自控制端此前的两项调整记录提交，符合已批准的调整范围；本评审未将它们误判为实现代理的额外产品功能。旧 `app/knowledge/vectors.py` 未被修改。
- ⚠️ Cannot verify from diff：实际 standalone 重启、已有集合元数据兼容性以及运行结果属于运行时证据。task-2-report.md 报告 StorageV3 探针成功、专项 72 passed、默认 749 passed/104 skipped，均无 warning；控制端应保留并确认其 `.cache/milvus-{before,after}-storagev3.json` 和既有运行证据。此项不要求重复执行已报告套件，也不将本任务视为后续重排/切换/线上链路已完成。

### Strengths

- `app/retrieval/milvus.py:77`、`:111` 对字段、函数与索引漂移明确拒绝，不破坏同名旧集合；`tests/test_hybrid_milvus.py:436` 枚举实际漂移，`tests/integration/test_hybrid_milvus.py:60` 真实验证旧稠密结构拒绝后仍存在。
- `app/retrieval/milvus.py:123` 同时检查写入计数和主键全集；`:180` 正文/category 精确比较与明确 float32 容差相结合，验证对象对应真实读回行，而非仅检查数量。
- `app/retrieval/milvus.py:193` 显式排序 keyset 分页并拒绝不递增回包；`tests/test_hybrid_milvus.py:205` 的 17,001 主键替身会在缺少排序时暴露漏行。
- `tests/test_hybrid_milvus.py:247` 使用已安装 SDK 的真实重试装饰器；`:259`、`:461`、`:471` 分别覆盖期限取消、初始化不续期与主动取消传播。`tests/integration/test_hybrid_milvus.py:18` 验证真实 analyzer；`:44` 验证四字节分类上限与超过 VARCHAR 容量的 TEXT。
- 聚焦外部检查 1（复用校验器风险）：检查 `app/knowledge/embeddings.py:12`、`app/knowledge/types.py:9`、`:17`、`app/knowledge/vectors.py:14`，确认 1024 维有限向量、正 INT64、category 字符计数和确认主键全集契约，未发现复用引入的正文截断或主键放宽。
- 聚焦外部检查 2（集成测试误清理既有集合风险）：检查 `tests/conftest.py:21`，确认 fixture 创建 UUID 随机名称并在 finally 仅清理该名称。没有运行测试，也没有修改产品、ledger 或 Git 状态。
- 审查范围：指定 BASE..HEAD review package；首次工具展示截断后仅补齐 diff 的缺失显示范围，未另读任何 changed file。

### Issues

#### Critical (Must Fix)

- 无。

#### Important (Should Fix)

- 无。

#### Minor (Nice to Have)

- `tests/integration/test_hybrid_milvus.py:28`：型号检索断言满足 brief 的最低要求，但同类候选只有两个，查询还带有目标正文独有的“降噪”，因此目标出现在 Top-10 不能充分区分“型号具有检索区分度”与“其他词命中”。真实 analyzer 的 XM5 断言已有价值；可另加仅型号查询、更多相近型号干扰文档，并断言目标的相对排名，增强型号处理退化的回归检测。此为覆盖改进，不阻塞当前实现。

### Assessment

**Task quality:** Approved

**Reasoning:** 原生 BM25/RRF、前过滤、写后核验、严格结构验证与取消/零可配置重试实现一致，测试覆盖关键失败边界，并有已报告的真实 Milvus 验收。未发现需要修复后才能信任本任务的缺陷；型号区分测试仍可增强。


## task-3-review

### Spec Compliance

- ✅ Spec compliant. `app/repositories/knowledge.py:65` adds validated, keyword-only done keyset pagination inside a short transaction. `app/knowledge/hybrid_jobs.py:36` rebuilds only done records without marking them; `app/knowledge/hybrid_jobs.py:45` marks pending only after ACK and readback; `app/knowledge/hybrid_jobs.py:55` verifies exact text/category, Dense dimensions/finiteness, and complete missing/extra ID sets without embedding.
- ✅ `app/knowledge/cli.py:39` adds both commands with default batch size 20; `app/knowledge/cli.py:83` routes all vector commands to the configured hybrid collection; `app/knowledge/cli.py:91` independently verifies without constructing an embedder and raises on false readiness. `app/knowledge/cli.py:63` retains one original task lock over the entire command, and `app/knowledge/cli.py:119` maps verification failure to exit 1.
- ✅ All seven planned files have corresponding hunks. `scripts/run-knowledge-daily.ps1:5` adds only cutover guidance and preserves the deployment path. The authorized CLI-only test migration is at `tests/test_knowledge_cli.py:219`; the diff leaves Dense vectorizer unit tests in `tests/test_knowledge_vectorization.py:92` intact.
- ⚠️ The reused integration fixture definitions and full collection/schema/model/global retrieval constraints are outside this task diff. The controller should retain the existing Task 1/2 and fixture safety gates; this review does not re-audit them. The new child explicitly targets 3308/customer_service_test at `tests/integration/test_hybrid_recovery.py:114`.

### Strengths

- `app/knowledge/hybrid_jobs.py:23` shares one write path for rebuild and pending recovery; ACK validation and successful `verify_rows` complete before any MySQL status update. `app/knowledge/hybrid_jobs.py:81` compares actual full ID sets rather than trusting equal counts.
- `app/knowledge/hybrid_jobs.py:62` treats malformed readback as failed verification; `app/knowledge/hybrid_jobs.py:71` explicitly validates Dense shape and finite values. Independent verification uses only stored vectors and authoritative MySQL fields.
- `tests/integration/test_hybrid_recovery.py:136` retains the handle of the newly spawned process and terminates only that handle at line 148. Lines 151–159 verify the partial IDs, original status/vector_id tuples, recovery, and reacquisition of the actual lock.
- `.superpowers/sdd/2026-10-08-hybrid-retrieval/task-3-report.md:2196` contains clean actual focused GREEN output (43 passed); line 2205 contains clean real integration output (3 passed), including original/interrupted/resumed ID sets; line 2216 contains clean final regression output (778 passed, 107 skipped). No tests were redundantly rerun.

### Issues

#### Critical (Must Fix)

- None.

#### Important (Should Fix)

- None.

#### Minor (Nice to Have)

- `tests/integration/test_hybrid_recovery.py:120`, `:140`, `:145`: the child creates the signal file before `write_text` completes, while the parent treats existence as permission to parse JSON. Scheduling between creation and the completed write can yield empty/partial JSON and a flaky integration failure. Publish the completed JSON via a temporary file followed by atomic replacement, or wait for a complete signal payload.

### Assessment

**Task quality:** Approved

**Reasoning:** The product code implements the required state/ID/readback gates with short database transactions and preserves CLI locking and resource cleanup. The sole finding is a minor test synchronization race; reported GREEN runs are clean.

- Review scope: base 9f1b9298c3069871989cfede814c1adeb75915a3 through head 4555219, supplied diff. Its initial tool output was truncated; only the cut-off integration/unit/CLI hunks were recovered from that diff. No Git commands, test reruns, product edits, or dev-notes edits were performed.
- Focused unchanged-code check, adapter-contract risk: `app/retrieval/milvus.py:123`, `:153`, `:180`, `:193`, `app/knowledge/vectors.py:14`, and `app/knowledge/embeddings.py:12` confirm complete ACK validation, Strong readback, successful `verify_rows` returning None, dimension/finite validation, and complete ordered ID enumeration.
- Focused original-lock/cancellation risk: `app/knowledge/locking.py:38` preserves the database-derived ch03 lock name; lines 53–63 preserve cancellation-aware cleanup. The CLI diff omitted the beginning/end of `run`/`main`, so only `app/knowledge/cli.py:58`–73 and `:113`–end were read to verify whole-command lock scope and nonzero exit handling.


## task-4-review

### Spec Compliance

- ❌ Issues found: required colloquial normalization and retrieval-side synonym expansion are reduced to literal-anchor preservation plus a small filler vocabulary (`app/retrieval/query.py:21`, `app/retrieval/query.py:29`, `app/retrieval/query.py:39`; `app/core/prompts.py:87`). The guard also fails to preserve full-width numeric amounts (`app/retrieval/query.py:19`, `app/retrieval/query.py:33`). These conflict with user feature 4 and `docs/superpowers/specs/2026-10-08-hybrid-retrieval-design.md:53`, `docs/superpowers/specs/2026-10-08-hybrid-retrieval-design.md:55`.
- ✅ All nine brief-listed files have corresponding hunks. Strict output contracts, explicit stop-only raw validation, fixed reranker model/request, response validation, stable sorting, bounds, cancellation and ownership match this task (`app/retrieval/types.py:29`, `app/retrieval/query.py:54`, `app/retrieval/query.py:73`, `app/retrieval/rerank.py:35`, `app/retrieval/rerank.py:48`, `app/retrieval/rerank.py:61`).
- ⚠️ Cannot verify from this diff: online threshold enforcement, using expansions only in retrieval, and freezing the same QueryPlan across evaluation strategies belong to subsequent consumers (`app/config.py:37`; design `:53`, `:57`). Controller should check those tasks. Real reranker credentials/network integration was not required or performed.

### Strengths

- Raw protocol coverage drives the actual LangChain parser through HTTP transport rather than asserting only a fake parsed object; repaired/truncated JSON, extra fields, non-stop reasons and parsed/raw disagreement are rejected (`tests/test_query_understanding.py:25`, `:54`, `:108`; `app/retrieval/query.py:67`, `:74`).
- Rerank results are completely validated before slicing, provider documents cannot replace authoritative text, ties retain service order, and caller-owned clients remain open (`app/retrieval/rerank.py:45`, `:48`, `:61`, `:63`; `tests/test_reranker.py:28`, `:46`).
- Reported validation is reproducible and candid: saved logs confirm 63 focused passes and 841 passes/107 skips, with no suite warnings. Live evidence separately records initial 4/10 and revised affected-subset 5/6; it does not claim a final 9/10 run (`.superpowers/sdd/2026-10-08-hybrid-retrieval/task-4-report.md:54`, `:68`, `:82`, `:120`; `.cache/task-4-green.log:2`, `.cache/task-4-live.log:12`, `.cache/task-4-live-rework.log:8`).

### Issues

#### Critical (Must Fix)

- None.

#### Important (Should Fix)

1. `app/retrieval/query.py:21`, `:29`, `:39`, `:43`; `app/core/prompts.py:87`, `:90`: safe colloquial rewrites and genuine Chinese synonyms cannot pass unless they retain the original Chinese content spans literally. A focused no-network probe confirms `物流咋查啊` → `物流如何查询？` falls back to the unnormalized original with no expansions because `咋查` remains part of the anchor. `退款咋办` → `退钱如何办理？` is likewise rejected, although `退货咋办` → `退货如何办理？` with filler-based expansion does pass. The revised live prompt further prefers verbatim originals/empty expansions; all five revised successes use exactly that shape (report `:120`). This is a missing feature, not merely limited ontology coverage: the requested normalization/synonym functionality has no positive semantic example in code or validation. Add a bounded, explicitly safe colloquial/synonym mechanism that preserves protected identities and conditions, keep uncertain/conflicting rewrites fail-closed, and test real positive rewrites/expansions alongside conflicting ones. Re-evaluate the unchanged synthetic labels; preserve the fixed model/cap/deadlines.

2. `app/retrieval/query.py:19`, `:26`, `:33`, `:39`: numeric protection recognizes only ASCII digits and subsequently ignores non-Chinese characters. A focused probe passes raw `满２９９元免运费吗？` and proposed `满１９９元免运费吗？` through `_safe_plan`; the returned standard contains the changed １９９ amount. Full-width digits are ordinary Chinese input, so the promised preservation of numeric amounts is violated and the wrong threshold can enter retrieval. Treat Unicode decimal digits and full-width alphanumerics as protected anchors (or conservatively preserve the original when present), and add controlled regressions for changed full-width amounts/model identifiers.

#### Minor (Nice to Have)

- `app/core/prompts.py:87`; `.superpowers/sdd/2026-10-08-hybrid-retrieval/task-4-report.md:120`: the remaining `conditions-1` length failure with configured 512 tokens is an observed provider limitation, truthfully reported and correctly rejected as invalid structured output (`app/retrieval/query.py:67`, `:74`). It does not justify changing the fixed model/output cap or pretending a fallback succeeded. Retain this limitation in downstream validation/acceptance records; the 5/6 affected subset cannot establish whole-corpus reliability.
- `.superpowers/sdd/2026-10-08-hybrid-retrieval/task-4-report.md:122`; `.cache/task-4-live.log:1`, `.cache/task-4-live-rework.log:1`: live output includes the existing custom-transport/system-proxy advisory. This is validation-output hygiene, not an adapter failure or evidence that completed responses were invalid. Keep it documented and address it only through a supported separately scoped transport decision; controlled suite output is clean.

### Assessment

**Task quality:** Needs fixes.

**Reasoning:** The strict protocol and reranker adapters are well tested, and live evaluation is accurately qualified. The query guard still blocks the requested useful semantic normalization/expansion while allowing a concrete Unicode amount substitution, so safety and feature coverage both need correction.

**Checks and review scope:** Read the supplied diff once, with no changed-file rereads, git rediscovery, broad crawl, subagents, or reported-suite reruns. Focused named checks: feature coverage/protected numeric behavior via one no-network `_safe_plan` probe (re-emitted as ASCII JSON because terminal Unicode was garbled); truthful validation/noise via retained suite/live log tails and synthetic delivered-plan records; governing normalization contract via design lines 49–57. The interpreter emitted `Failed to find real location of E:\miniconda3\python.exe` during the focused probe but returned exit 0 and the expected structured results; this did not occur in the reported suite logs.


## task-4-review-fix-1

- **Safe colloquial normalization and genuine Chinese synonyms** — **ADDRESSED**. `app/retrieval/query.py:21`, `:40`, `:53` now require complete phrase matches with equivalent topic/intent, produce canonical standards, and retain bounded synonyms. Unknown identities, conditions, and conflicting intent fall back verbatim. `app/core/prompts.py:88` explicitly requests positive normalization. Positive, echo-output, and conflict regressions appear at `tests/test_query_understanding.py:53`, `:64`, `:88`. Original ten evaluation cases remain unchanged; the report records four live semantic successes and the protected-amount truncation honestly.

- **Unicode numeric and full-width model protection** — **ADDRESSED**. `app/retrieval/query.py:32` protects Unicode numeric characters and non-CJK letters; `:41` excludes them from semantic normalization, and `:56` preserves the exact original with empty expansions. Regressions at `tests/test_query_understanding.py:76` cover changed full-width amounts, numeric models, letter-only models, and Arabic-Indic amounts.

- **New Breakage in the Fix Diff:** None; no new Critical, Important, or Minor findings.

- **Out-of-Scope Observations:** None.

- **Verification:** Read the supplied fix diff once. Inspected existing log tails: focused tests **77 passed in 4.25s**; default regression **855 passed, 107 skipped in 34.91s**. No tests rerun and no checkout mutations.

- **Fix round:** **All findings addressed, no new Critical/Important breakage.**


## task-5-review

**Spec Compliance: ✅ Compliant.** All five planned files are present. Four strategies, BM25 without embedding, injected-plan reuse, authoritative done/category filtering, integer deduplication, score labels, Top-10 payloads, and backward-compatible FAQ construction/search match the brief (`app/retrieval/service.py:21`, `app/repositories/faq.py:12`, `app/retrieval/types.py:51`).

**Strengths**

- Recall order survives unordered MySQL results; rerank positions map to the filtered authoritative documents (`app/retrieval/service.py:44`).
- Low rerank scores remain available for later rejection and evaluation; external failures propagate directly (`app/retrieval/service.py:54`).
- Payloads expose final evidence and counts without candidate正文 (`app/retrieval/service.py:64`).
- Tests exercise strategy routing, stale/missing rows, large integer IDs, positional alignment, failure propagation, and FAQ compatibility (`tests/test_retrieval_service.py:74`, `tests/test_semantic_faq.py:157`).

**Issues**

- **Critical:** None.
- **Important:** None.
- **Minor:** `tests/test_retrieval_service.py:172` covers invalid strategy/category but omits empty, non-string, and over-512-character raw questions, plus invalid injected plans. Add focused cases confirming rejection before dependencies; production checks already exist (`app/retrieval/service.py:26`).

**Verification limits**

- ⚠️ Reported `42 passed` and `880 passed, 107 skipped` are recorded in the implementer report; execution was not independently repeated. The diff adds 25 parameter-expanded cases, consistent with the focused report.
- ⚠️ Real database behavior and Milvus category prefiltering are outside this diff. Tests verify boundary arguments and authoritative row handling; real integrations remain intentionally skipped.
- Focused outside-diff check: direct rerank indexing could admit invalid or duplicate positions. Existing `SiliconFlowReranker.rank` rejects both and validates finite scores (`app/retrieval/rerank.py:47`).

**Task quality: Approved.** The implementation is compact, preserves existing contracts, and provides meaningful controlled tests. No blocking defect found.


## task-6-review

✅ Spec compliant for Task 6. All ten scoped files are present, and the reviewed implementation matches the requested interfaces, evidence limits, strict self-check behavior, current-round citations, and FAQ/no-tool routing boundary.

### Strengths

- `app/core/evidence.py:35` checks the actual compact JSON against both limits; `:79` selects complete evidence blocks, raises `InputTooLong` when all candidates are unfittable, and delegates history validation and budgeting to `build_tool_messages`. `:44` assigns stable numbers and places the strongest two selected blocks at opposite ends. Tests verify payload/message/citation consistency, complete history trimming, tool-field costs, and unchanged input data (`tests/test_evidence.py:44`, `:72`, `:88`).
- `app/core/sufficiency.py:19` forbids extra fields and coercion; `:73` requires calibrated hybrid-rerank thresholds and authoritative rerank score kinds. Its check requires `stop`, rejects actual self-check tool calls, validates untouched JSON against parsed output, and applies empty/low-score gates only after a valid assessment. Baseline scores remain separate from confidence (`tests/test_sufficiency.py:66`).
- `app/core/answer_validation.py:44` requires exactly `{'stop'}`, the exact fixed refusal for negative decisions, and known current citations for knowledge answers. Nonfactual outputs undergo complete clause checks (`:31`); frozen benign outputs and adjacent factual negatives are covered (`tests/test_answer_citations.py:77`, `:87`, `:103`).
- `app/core/prompts.py:103` uses only the current question and selected evidence for assessment. The final prompt preserves the prohibited commitment rules and requires current evidence references (`:128`).
- Saved evidence confirms **132 focused passes** and **955 passes / 107 skips**, with no warnings in those outputs (`.cache/task6-final-focused.txt:3`, `.cache/task6-final-full-suite.txt:16`). No suites or paid calls were rerun during review.
- Raw saved live records support the separately reported **7 valid / 5 length errors** initial batch and **4 valid / 1 length error** restricted rework batch. The three frozen benign final answers match the regression strings; their local acceptance is not presented as new live generation.

### Issues

- Critical: None found.
- Important: None found.
- Minor: None requiring changes for this task gate.

### Cannot verify / limits

- `app/core/answer_validation.py:44` cannot inspect actual final `AIMessage` tool fields. Trusted-tool routing, global final-tool-call rejection, refusal persistence, and the atomic problem-pool transaction remain Task 7 obligations, as explicitly scoped.
- `app/core/sufficiency.py:75` requires a threshold but does not establish its value. Real independent calibration remains Task 8; the synthetic threshold is explicitly identified as illustrative (`evals/sufficiency_cases.jsonl:5`).
- Citation validation establishes current numbering and format, not sentence-level faithfulness (`app/core/answer_validation.py:52`). The recorded extra “订单详情页提交申请” advice is correctly disclosed; complete semantic grounding is not claimed.
- Current GLM/512 still produced a `length` error for `missing-conditions` in the restricted rework. The implementation preserves that as an error (`app/core/sufficiency.py:90`), and no final twelve-case success rate can be inferred.
- Named outside-diff checks: inspected `app/core/tool_history.py:87` for the reused whole-turn/tool-field budget contract, and `app/core/extraction.py:25` for untouched raw JSON/parsed equality. Both support the new callers. The initial package output was truncated; only its omitted diff range was retrieved. No changed file was separately reread.

**Task quality: Approved.** The implementation maintains the required fail-closed boundaries and has meaningful controlled regression coverage. The disclosed provider limitation and deferred integration/calibration work do not constitute missing Task 6 implementation.


## task-7-review

### Spec Compliance

- ✅ Spec compliant. The absolute deadline spans preparation and streaming (`app/core/tool_chat.py:81,131`); FAQ gets its timeout override and zero retries; category stays in trusted context; FAQ/no-tool branches perform sufficiency checks while business tools retain their existing path (`app/core/tool_chat.py:138,159,179`).
- ✅ The persisted FAQ ToolMessage is the actual budgeted packet message, final generation uses that packet, and citations precede deltas (`app/core/tool_chat.py:168,180,181`). Refusal and normal done events follow persistence and use returned message IDs (`app/core/tool_chat.py:190,228`).
- ✅ Startup rejects missing/nonfinite thresholds, verifies existing Milvus collections without creation, and checks quality tables without migration (`app/main.py:76,94,107`; `app/quality/migration.py:128`).
- ✅ Actual consumers support checking/citations, retain the Top-10 boundary, and compare supplied final message IDs against committed rows (`evals/smoke.py:99,132`; `evals/evaluate_tools.py:53,69`).
- ⚠️ Calibration quality and genuine cloud-model acceptance are subsequent-task requirements. This diff verifies threshold presence and finiteness, not calibration correctness (`app/main.py:76`).

### Strengths

- Evidence selection, serialization, citation numbering and final model input stay consistent; the regression explicitly checks nonsequential display numbering and large integer identities (`tests/test_hybrid_chat.py:59`).
- Invalid assessment, evidence-budget failure and cancellation after refusal output are observable failures with no completed answer or pool entry (`tests/test_hybrid_chat.py:228,246`).
- Resource registration uses reverse-order cleanup, with constructor, readiness, structured-wrapper and close-failure coverage (`app/main.py:80,87,90,93,96`; `tests/test_knowledge_lifecycle.py:114,140`; `tests/test_hybrid_lifecycle.py:83`).
- Real TCP tests prove incremental UTF-8 delivery before model completion and compare done IDs with actual MySQL commits (`tests/test_hybrid_chat.py:263`).
- Supplied logs are readable and clean: 174 passed/2 skipped (`.cache/task7-final-focused.txt:4`), 1010 passed/109 skipped (`.cache/task7-final-full.txt:17`), and 2 real TCP/MySQL tests passed (`.cache/task7-final-tcp.txt:2`). No suite was rerun.

### Issues

#### Critical (Must Fix)

- None.

#### Important (Should Fix)

- None.

#### Minor (Nice to Have)

- `tests/test_hybrid_chat.py:154–156`: The cancellation half reuses `started`, which the preceding timeout run already set. `await started.wait()` therefore returns immediately, and the newly created task is cancelled before `collect` enters the selection call. Because preparation has already acquired a lease, this also bypasses `collect` cleanup. Clear the event before starting the second task, wait for its fresh signal, then assert cancellation leaves no final answer/pool entry and permits reacquiring the conversation lock.

### Assessment

**Task quality:** Approved

**Reasoning:** The implementation satisfies the Task 7 contracts with consistent evidence, atomic refusal persistence, bounded execution and clear ownership. The identified cancellation-test defect is nonblocking; production cancellation handling and other lifecycle regressions remain intact.

- Focused outside-diff checks: atomic-refusal transaction and actual-ID contracts (`app/quality/repository.py:35–42`; `app/repositories/conversations.py:54–71`), terminal/disconnect cleanup (`app/api/streaming.py:40–83`), strict assessment/error handling (`app/core/sufficiency.py:70–105`), and absence of a unified-FAQ dense fallback (`app/repositories/faq.py:21–27`).
- Cutoff-function checks only: executor return/cancellation handling (`app/tools/executor.py:95–118`) and stream iterator cleanup (`app/core/tool_chat.py:240–246`). No checkout mutation, git rerun, test rerun or subagent dispatch.


## task-8-review

### Spec Compliance

- ✅ Task 8 is compliant with the authorized budget and timeout changes. Fixed 30-case/five-bucket data and eight independent calibration cases, physical-ID metrics, four-strategy evaluation, strict judging, mandatory fabrication persistence, checkpoints and cleanup are implemented.
- ⚠️ Historical live results validate runner v1. Current v2 deadline accounting has controlled regression evidence, but no subsequent paid live run; the implementation report discloses this limitation.

### Strengths

- Exact gold triples preserve all physical duplicates and fail on missing mappings; empty gold returns n/a. Independent metric denominators retain usable retrieval measurements when later stages fail — `evals/evaluate_retrieval.py:97,118`, `evals/retrieval_metrics.py:5`.
- Four strategies share one legal rewrite and reuse actual evidence construction, sufficiency checks, streaming generation and answer validation. Unsupported claims must reach the ledger; judge failures cannot become fabrication records — `evals/evaluate_retrieval.py:185`, `evals/faithfulness.py:51`.
- Structured budgets preserve the final model and share its clients without additional ownership. Request-body tests cover both token-limit fields — `app/core/llm.py:10`, `tests/test_structured_budgets.py:14`.
- Initialization failures and owned-resource cleanup receive meaningful coverage, including second-model construction failure and shared HTTP ownership — `evals/evaluate_retrieval.py:340`, `tests/test_retrieval_evaluation.py:238`.
- Read-only artifact recomputation found no discrepancies across all 120 records: retrieval metrics, summary denominators, judge raw JSON/scores, actual Prompt evidence and fabrication triggers agree. The live aggregate is accurately reported as 101 completed, 19 errors and `passed=false` — `docs/validation/hybrid-retrieval-comparison.json:77019`.
- Calibration records support the reported threshold `0.8201608061790466` and TP4/FP0/FN0/TN4. Original failed calibration/comparison histories remain intact — `docs/validation/hybrid-retrieval-calibration.json:3838`.
- Focused outside-diff checks confirmed the online FAQ deadline ends before sufficiency, matching v2’s boundary; unchanged strict parsing and atomic checkpoint helpers support the evaluator. The cut-off application hunk was completed by checking its injected-dependency condition — `app/core/tool_chat.py:149,159`, `app/core/extraction.py:23`, `evals/knowledge_recovery.py:73`, `app/main.py:119`.

### Issues

#### Critical

- None.

#### Important

- None.

#### Minor

- `docs/validation/hybrid-retrieval-comparison.md:7`: The standalone committed summary omits two qualifications already disclosed in the implementation report: its live timings come from v1 and exclude shared rewrite elapsed; Recall measures the frozen canonical gold blocks rather than exhaustive semantic relevance. Add these qualifications to the durable delivery summary, preferably during Task 10. No artifact alteration or paid rerun is needed.

### Assessment

**Task quality: Approved.**

The implementation and recorded metrics are consistent, with appropriate failure handling and resource ownership. Approval covers Task 8’s implementation and truthful evaluation evidence; it does not establish general retrieval quality or live verification of v2 timing.

## 最终整分支审查原文

### Strengths

审查范围：`3ce6de4925b10527496113aa7b35fe83c447b405..68da1f26f33f0b9169da2d305afb91a000ef40ee`。分批检查后端、数据集、CLI、相关测试及交付文档草稿；全程只读，未修改文件、索引或 HEAD，未调用收费服务。

- 拒答助手消息和问题池记录由同一短事务提交，`done` 使用实际消息主键并在提交后发送；外部故障与预算错误不会冒充知识不足。
- 检索坚持 MySQL 权威正文、双路参数化预过滤、稳定主键重建和完整字段核验；同数量但错误内容不能通过切换检查。
- 实际输入证据、持久化 ToolMessage、SSE 引用和编造台账快照保持一致；历史按完整轮次裁剪。
- 台账通过原子 upsert 累加复发次数，并保留处置时间；启动核验与资源所有权边界清晰。
- 文档如实保留实际比较的 101 项完成、19 项错误及邮费问题误拒答，没有把校准样本内 F1=1 或受控测试包装成普遍质量结论。

### Issues

#### Critical — Must Fix

未发现。

#### Important — Should Fix

1. **[P2] 评估最终流的完成条件弱于线上，能够把线上失败结果计为成功**

   文件：[evals/evaluate_retrieval.py:251](D:/shixi/ecommerce-customer-service/.worktrees/hybrid-retrieval/evals/evaluate_retrieval.py:251)，并涉及第 261–272 行。

   评估循环直接累计文本并调用引用校验，缺少线上已有的字符/UTF-8 字节上限、下层吞掉取消后的检查，以及提前失败时显式关闭上游迭代器的处理。工具字段检查也没有完整覆盖线上检查的字段。

   本次无网络受控复现确认：

   - 22,003 字符、66,003 UTF-8 字节的合法引用答案配合支持性裁判：评估四策略全部 `ok`、`passed=True`；同一答案在线上终止为 `upstream_error`。
   - 最终模型吞掉已触发的 0.01 秒总期限取消，随后返回合法 `stop`：评估四策略全部成功；线上终止为 `upstream_timeout`。
   - 最终流返回非法工具申请时，评估四次失败均未调用迭代器 `aclose`；相同线上失败关闭一次。

   这会让评估接受线上不能完成的回答，并在提前退出时延迟释放上游资源。应统一最终流校验边界：长度、所有工具字段、结束状态、取消及有界关闭；在进入裁判/台账/成功状态前完成检查。增加上述受控回归即可，不需重新运行收费比较，也不能改写历史真实报告。

2. **[P2] 检索和评估入口未遵守非空白分类契约**

   文件：[app/retrieval/service.py:30](D:/shixi/ecommerce-customer-service/.worktrees/hybrid-retrieval/app/retrieval/service.py:30)、[app/retrieval/milvus.py:224](D:/shixi/ecommerce-customer-service/.worktrees/hybrid-retrieval/app/retrieval/milvus.py:224)，评估入口另见 [evals/evaluate_retrieval.py:202](D:/shixi/ecommerce-customer-service/.worktrees/hybrid-retrieval/evals/evaluate_retrieval.py:202)。

   `validate_text` 只检查类型和最大长度，接受 `''` 与纯空白字符串；HTTP Schema 则正确拒绝这些值。受控调用确认，两种非法分类均进入了 planner 和 index。

   Spec 要求 CLI/评估采用相同的 1–255 字符、非空白分类契约。当前自定义评估输入可消耗模型请求，并把无效筛选得到的空结果当作证据不足。

   应添加共用的检索分类校验，在服务/索引入口和评估首次模型调用前拒绝非法分类。保留参数绑定，不要通过修改通用数据库文本校验影响其他存储字段。

#### Minor — Nice to Have

1. **[P3] 中断恢复测试的信号文件存在发布竞态**

   文件：[tests/integration/test_hybrid_recovery.py:120](D:/shixi/ecommerce-customer-service/.worktrees/hybrid-retrieval/tests/integration/test_hybrid_recovery.py:120)。

   父进程发现路径存在即读取，子进程此时可能尚未写完 JSON，造成偶发测试失败。先完整写临时文件，再原子替换目标信号文件。

2. **[P3] 取消测试可能没有实际进入第二次模型等待**

   文件：[tests/test_hybrid_chat.py:155](D:/shixi/ecommerce-customer-service/.worktrees/hybrid-retrieval/tests/test_hybrid_chat.py:155)。

   `started` 已在前一次超时场景置位，第二次等待会立即返回，可能在模型开始执行前取消任务。第二次启动前清除事件，等待新的进入信号；补充无最终消息、无问题池记录以及锁可复用断言。

3. **[P3] 已有原话和注入计划早拒保护缺少回归覆盖**

   文件：[tests/test_retrieval_service.py:172](D:/shixi/ecommerce-customer-service/.worktrees/hybrid-retrieval/tests/test_retrieval_service.py:172)。

   当前参数测试只覆盖错误策略和超长分类。补充空白、非字符串、超过 512 字符原话及非法注入计划，断言拒绝发生在模型、嵌入和索引调用之前。这是测试缺口，现有原话保护无需重写。

4. **[P3] 部分新增函数仍缺少用户要求的中文说明**

   文件示例：[app/retrieval/rerank.py:12](D:/shixi/ecommerce-customer-service/.worktrees/hybrid-retrieval/app/retrieval/rerank.py:12)、该文件第 17、63 行，以及 [app/retrieval/types.py:35](D:/shixi/ecommerce-customer-service/.worktrees/hybrid-retrieval/app/retrieval/types.py:35)。

   修正装饰器识别后的审计清单为 **89 处：4 个生产函数、85 个测试函数**。原始 100 处包含 11 个已有有效中文说明的误报。按更新清单人工核对后补充有意义的函数说明；函数前注释或 docstring 均可，避免重复模板文字。

5. **[P3] 独立比较摘要缺少关键解释范围**

   文件：[docs/validation/hybrid-retrieval-comparison.md:7](D:/shixi/ecommerce-customer-service/.worktrees/hybrid-retrieval/docs/validation/hybrid-retrieval-comparison.md:7)。

   新的总结果草稿已解释两项限制，但单独打开比较摘要仍看不到：真实 v1 运行未将共享改写耗时扣入各策略期限；金标为冻结的 canonical 块，并非穷尽所有语义相关块。

   在该摘要加入这两项说明，明确当前 v2 计时修复仅经受控验证。保留原始 JSON 和历史数字。

### Recommendations

将上述两项 Important 与延期 Minor 合入一次修复波，再执行一次限定修复范围的复核。随后完成计划要求的当前代码 MySQL/Milvus 完整回归。

本次 `git diff --check` 通过，所有新增审查探针均为无网络、内存内受控执行且退出码为 0；本审查没有重新运行完整服务测试或收费评估。

### Declined to judge

- 前端 `app/static`、截图和视觉交互实现：用户明确给予 Vibe Coding 审查豁免；本次只审查后端 SSE 契约。
- 重新校准门槛、更换模型、提高预算或重跑真实比较：超出当前授权；已审查实现与现有证据披露，不据此要求新增收费调用。
- 通用业务质量或“所有真实调用通过”：现有 19 项错误与邮费误拒答明确反证，不能由实现审查批准代替质量验收。
- 业务库部署、现有用户服务升级、正式语料校准及调度器注册：属于后续明确部署操作，本次测试资源验证不证明这些动作已经完成。

### Assessment

**Ready to merge? With fixes**

线上拒答、引用和持久化主链路未发现新的阻断问题，但评估完成边界与分类输入契约存在已复现的不一致，需修复后再整合。该结论不表示真实比较全部通过，也不表示当前门槛具有已验证的业务泛化质量。


## 最终唯一修复波报告原文

# 最终统一修复波报告

状态：DONE。基线 `68da1f26f33f0b9169da2d305afb91a000ef40ee`；工作树 `D:/shixi/ecommerce-customer-service/.worktrees/hybrid-retrieval`，分支 `feat/hybrid-retrieval`。本报告对应完整 final-review.md 的 Important 2 + Minor 5，一次统一修复；未派子代理或审查者。

## 修复范围与根因

1. **Important 1：最终流边界一致性。** 评估原来直接拼接文本并仅检查两个工具字段，未执行线上完整流保护。`app/core/answer_validation.py` 新增小型共享 `FinalAnswerStream`，线上和评估共同执行四种工具字段拒绝、累计 20000 字符及 65535 UTF-8 字节上限、唯一合法 stop 集合及非空正文检查。共享 `ensure_answer_active` 检查任务取消状态及绝对期限，既能识别吞掉 CancelledError 的流，也能识别下层 uncancel 或阻塞事件循环后超期返回 stop 的结果。
   - 评估在最终流、拒答分支、裁判返回及成功状态前检查取消/期限，非法最终答案不会进入裁判或台账。
   - 每策略使用基于剩余累计预算的一次绝对 `timeout_at`；保留 v2 唯一共享改写耗时分别扣入四策略 FAQ/chat 的既有会计口径，不让后策略承担前策略耗时。
   - 共享 `close_answer_stream` 在 finally 显式调用上游 aclose，采用线上既有的 5 秒 `move_on_after(..., shield=True)` 清理范围。正常、非法工具、长度、非stop、引用错误、传输失败与取消都覆盖。没有新增重试、后台任务或无界等待。
2. **Important 2：分类入口契约。** `app/retrieval/types.py` 提供检索专用 `validate_category`，接受 None 或 1–255 字符非空白字符串；不转换/裁剪合法分类。服务、索引、索引行和直接聊天准备复用它。compare/calibrate 先预检整批案例；真实 CLI evaluate 在资源和模型构造前也预检，后题非法不会先消耗前题模型请求。通用 `app.knowledge.types.validate_text` 未修改，数据库其他字段的既有契约保持。
3. **Minor 1：信号发布竞态。** 拥有的子进程完整写同目录临时信号，关闭文件后 Path.replace 原子发布；父进程看到目标即能读到完整 JSON。
4. **Minor 2：取消测试。** 第二次启动前 clear 已置位事件，等待模型重新进入后才 cancel；断言没有最终助手消息、没有问题池，随后同一会话 prepare/release 验证锁可复用。
5. **Minor 3：既有早拒缺口。** 补空白/非文本/>512 原话及非 QueryPlan 注入的早拒测试，明确断言 planner/embedder/index/repository/reranker 均无调用；生产已有原话及注入计划保护没有重写。
6. **Minor 4：中文说明。** 按更正清单人工核对并为 89 处给出具体说明（4 production / 85 tests）。11 个已有装饰器中文说明的误报未重复添加。`.cache/final-fix-comment-reconciliation.json` 保留逐项原位置与解释映射；未改忽略的审计 helper。所有新增函数也有中文说明。
7. **Minor 5：独立摘要。** `docs/validation/hybrid-retrieval-comparison.md` 明确真实 v1 未扣共享改写耗时、历史最终流边界较弱、当前 v2 修复仅经受控回归；冻结 canonical 三元组金标并不穷尽所有语义相关块。原始 JSON、历史报告和全部数字未改。

## TDD：生产修改前 RED

默认 Python 均为 `D:/shixi/ecommerce-customer-service/.venv/Scripts/python.exe`；以下命令在上述工作树使用 `-u -m pytest`。运行需要现有 runtime/库/回环能力，按控制端指示使用沙箱外授权运行；不读取或输出凭据。

```powershell
& 'D:/shixi/ecommerce-customer-service/.venv/Scripts/python.exe' -u -m pytest tests/test_retrieval_evaluation.py tests/test_retrieval_service.py tests/test_hybrid_milvus.py -q -k 'category or final_stream_boundary or expired_cumulative or caller_cancellation_swallowed or existing_raw_question or existing_injected_plan'
```

结果（`.cache/final-fix-red.txt`）：`18 failed, 19 passed, 111 deselected in 6.94s`，退出 1。

- chars/bytes 非法最终文本被四策略计为成功：期望 errors=4，实际为 0；裁判/台账得到非法答案。
- early failure 的工具/非stop/引用/传输场景：期望四次显式关闭，实际 `[]`，例如 `assert [] == [True, True, True, True]`。
- 三种超期流（吞 cancel、uncancel、阻塞 loop）：期望 errors=4，实际为 0。
- 调用方取消被下层吞掉后仍有台账写入，违反不得成功/落账的断言。
- 空/空白分类进入服务，`Failed: DID NOT RAISE ValueError`。索引初次探针暴露初始化已被触达，随后将禁止初始化替身改为显式行为失败以定位边界。
- 现有原话/注入计划非法值测试通过，证明本项是覆盖缺口而非要求重写保护。

为避免无限等待的初次取消测试遮蔽 RED 输出，受控模型的取消后续等待改为短有限等待，终止的仅是该次自己启动的 pytest Python 进程；未操作共享服务。以上完整 RED 是修改生产代码前完成的正式证据。

```powershell
& 'D:/shixi/ecommerce-customer-service/.venv/Scripts/python.exe' -u -m pytest tests/test_retrieval_evaluation.py tests/test_hybrid_milvus.py -q -k 'all_case_categories or invalid_category_cannot'
```

结果（`.cache/final-fix-red-preflight.txt`）：`12 failed, 3 passed, 100 deselected in 5.90s`，退出 1。

- compare/calibrate 对五类非法分类均未在整批首次共享改写前拒绝（10 项 `DID NOT RAISE ValueError`）。
- 空/空白索引分类触发 `Failed: invalid category reached index initialization`，明确证明早拒缺失。
- 类型与长度已有索引保护通过；新增共享 guard 只补齐检索契约。

## GREEN 与验证

初次生产修复的覆盖命令：

```powershell
& 'D:/shixi/ecommerce-customer-service/.venv/Scripts/python.exe' -u -m pytest tests/test_retrieval_evaluation.py tests/test_retrieval_service.py tests/test_hybrid_milvus.py tests/test_hybrid_chat.py tests/test_stream_lifecycle.py tests/test_tool_chat_service.py -q
```

`.cache/final-fix-green-initial.txt`：`256 passed, 2 skipped in 31.73s`，退出 0。

扩大后的定向验证（说明补齐、测试可靠性、CLI 和合法边界也包含）：

```powershell
& 'D:/shixi/ecommerce-customer-service/.venv/Scripts/python.exe' -u -m pytest tests/test_retrieval_evaluation.py tests/test_retrieval_service.py tests/test_hybrid_milvus.py tests/test_hybrid_chat.py tests/test_stream_lifecycle.py tests/test_tool_chat_service.py tests/test_hybrid_jobs.py tests/test_query_understanding.py tests/test_reranker.py tests/test_knowledge_cli.py -q
```

第一次扩大运行 `.cache/final-fix-green-focused.txt`：`382 passed, 2 skipped, 3 errors in 40.81s`。根因是新合法长度测试自动生成巨大的 emoji 参数名，Windows 的 `PYTEST_CURRENT_TEST` 环境变量超过 32767 字符，在 setup/teardown 及随后第一服务用例 setup 出错；不是生产测试失败。为两种边界添加短显式 IDs 后重新运行同命令：`.cache/final-fix-green-focused-final.txt`：`384 passed, 2 skipped in 38.10s`，退出 0。

受控新保护覆盖：四种工具字段、字符与独立四字节 UTF-8 上限、非stop/缺stop/非法引用/传输错误、吞取消/uncancel/阻塞loop超期、真实进入最终流后的调用方取消、显式关闭以及关闭永久等待的有界取消。合法 20000 字符及 65535 字节分块答案仍可完成；旧共享改写累计期限测试继续通过。

受影响的真实集成单独验证：

```powershell
& 'D:/shixi/ecommerce-customer-service/.venv/Scripts/python.exe' -u -m pytest tests/integration/test_hybrid_recovery.py -q --run-mysql --run-milvus -o faulthandler_timeout=30
```

`.cache/final-fix-green-recovery.txt`：`3 passed in 12.18s`，退出 0。使用现有 MySQL 3308/customer_service_test、随机唯一 Milvus 集合与本次拥有知识。只有本测试创建的子进程被中断；fixtures按所有权回收，没有共享truncate或业务3307清理。

**默认完整 suite 只运行一次，所有实现修复完成后、提交前：**

```powershell
& 'D:/shixi/ecommerce-customer-service/.venv/Scripts/python.exe' -u -m pytest -q -o faulthandler_timeout=30
```

`.cache/final-fix-default-suite.txt`：`1096 passed, 109 skipped in 45.21s`，退出 0。109 个显式服务/可选集成默认跳过；本结果不代替控制端随后当前提交的完整 `--run-mysql --run-milvus` 运行。

交付审计与空白核验：

```powershell
& 'D:/shixi/ecommerce-customer-service/.venv/Scripts/python.exe' -c "import runpy; runpy.run_path('.cache/audit_delivery.py',run_name='__main__')"
git diff --check
```

审计：`text_files=217; python_functions=1329; utf8_errors=[]; missing_chinese_explanation=[]; secret_locations=[]; tracked_private_files=[]`。`git diff --check` 退出 0；仅 Git 现有 LF/CRLF 提示，没有空白错误。

## Context7 与 API 核对

- `.cache/context7-final-fix-python-resolve.txt`、`context7-final-fix-asyncio.txt`：CPython 官方 asyncio timeout/cancellation/uncancel、async iterator aclose 最终化，正式实现前查询。
- `.cache/context7-final-fix-anyio-resolve.txt`、`context7-final-fix-cleanup.txt`：AnyIO 官方 `move_on_after(..., shield=True)` 有界清理，正式实现前查询。
- `.cache/context7-final-fix-pathlib.txt`：CPython 官方 Path.write_text 关闭文件和 Path.replace/os.replace 原子覆盖。该补查在首次信号修正及真实测试之后完成（此前项目已有相同原子检查点模式）；这是先查 API 时序的遗漏，后续完成官方核对。没有改变已验证实现。
- 本波没有新增 HTTPX 生产调用；rerank 的 HTTPX 用法只补函数说明，所有权未变。

## 修改文件（17个，显式暂存）

- `app/core/answer_validation.py`、`app/core/tool_chat.py`：共享最终流保护/关闭，直接prepare分类保护。
- `app/retrieval/types.py`、`service.py`、`milvus.py`：检索分类 guard；`app/retrieval/rerank.py`：3处中文说明。
- `evals/evaluate_retrieval.py`：整批分类预检、绝对累计期限、最终流/取消保护和资源释放。
- `tests/test_retrieval_evaluation.py`、`tests/test_retrieval_service.py`、`tests/test_hybrid_milvus.py`：受控回归。
- `tests/test_hybrid_chat.py`、`tests/integration/test_hybrid_recovery.py`：取消与原子信号可靠性及说明。
- `tests/test_hybrid_jobs.py`、`tests/test_knowledge_cli.py`、`tests/test_query_understanding.py`、`tests/test_reranker.py`：人工补有意义中文函数说明，不改运行逻辑。
- `docs/validation/hybrid-retrieval-comparison.md`：独立摘要历史与金标口径。

## 自审、边界与待执行

七项逐一与 final-review.md 核对；共享 helper 仅提取线上既有流保护并增加取消/绝对期限检查，不重构其他架构。修改前后当前 API 不新增工具循环；模型、门槛、最终512、query/self2048、query60/self20/FAQ90/chat240、零重试均未变。

root-owned `README.md`、`dev-notes/ch04.md`、`hybrid-retrieval-results.md`、`hybrid-retrieval-review.md` 的已有工作树修改未编辑/暂存/提交；`app/static`、历史JSON与其他历史报告未变。忽略的当前 .env 和资源注入所有权保持，没有收费模型重跑、外部部署或8000/8001/3307操作。

实现无已知剩余技术缺陷；Context7 Path.replace 补查的先后时序遗漏如上披露。当前默认套件通过不代表真实模型业务质量，原 v1 101完成/19错误及邮费误拒答保留。控制端负责后续限定修复复核及当前提交完整显式MySQL/Milvus套件。

提交：`2ac60e51ca44aa784c7085f2a04b45aaa8d434af` — `fix: align evaluation boundaries and complete review corrections`。提交仅包含上列17个显式文件；提交后工作树仅剩控制端原有README/dev-notes/results/review草稿。


## 最终修复波定向复核原文

- **[P2] 评估最终流的完成条件弱于线上，能够把线上失败结果计为成功** — **ADDRESSED**。`app/core/answer_validation.py:32–82` 提供共享取消/绝对期限检查、四类工具字段拒绝、20000 字符及 65535 UTF-8 字节累计限制、唯一 `stop` 与非空正文检查和五秒有界关闭。`app/core/tool_chat.py:197–223` 与 `evals/evaluate_retrieval.py:256–269` 使用同一保护；评估在裁判返回、台账写入前及成功状态前再次检查期限/取消（`evals/evaluate_retrieval.py:274–284`）。`tests/test_retrieval_evaluation.py:350、408、442、489、529` 覆盖非法流、吞取消/uncancel/阻塞事件循环超期、实际进入最终流后的调用方取消、有界关闭及合法长度边界。原复现中的非法答案不能再进入裁判、台账或成功状态。

- **[P2] 检索和评估入口未遵守非空白分类契约** — **ADDRESSED**。`app/retrieval/types.py:12` 的检索专用 `validate_category` 拒绝空字符串、纯空白、非字符串及超过 255 字符值，并保留合法原文及 `None`。服务、索引、索引行和直接聊天准备分别复用该校验（`app/retrieval/service.py:30`、`app/retrieval/milvus.py:224`、`app/retrieval/types.py:31`、`app/core/tool_chat.py:79`）。compare/calibrate 在首次模型调用前预检整批分类；真实 CLI 在配置加载、资源及模型构造前预检（`evals/evaluate_retrieval.py:190、300、362`）。`tests/test_retrieval_evaluation.py:330、475` 验证后题非法也不会消耗前题请求；服务与索引早拒测试位于 `tests/test_retrieval_service.py:181`、`tests/test_hybrid_milvus.py:486`。通用数据库文本校验未修改，过滤仍采用参数绑定。

- **[P3] 中断恢复测试的信号文件存在发布竞态** — **ADDRESSED**。`tests/integration/test_hybrid_recovery.py:129–132` 先完整写入同目录临时文件，再以 `Path.replace` 发布目标信号；父进程不再通过目标存在性读到正在写入的 JSON。已有真实恢复日志 `.cache/final-fix-green-recovery.txt` 显示 **3 passed**，覆盖该拥有子进程的中断恢复场景。

- **[P3] 取消测试可能没有实际进入第二次模型等待** — **ADDRESSED**。`tests/test_hybrid_chat.py:155–159` 在第二次启动前清除旧事件，等待模型重新置位后才取消；`tests/test_hybrid_chat.py:161–165` 断言问题池为空、没有最终助手消息，并重新 prepare/release 同一会话验证锁可复用。第一次超时同样补充了无最终消息断言（第 153 行）。

- **[P3] 已有原话和注入计划早拒保护缺少回归覆盖** — **ADDRESSED**。`tests/test_retrieval_service.py:190` 覆盖空字符串、空白、`None`、数字、布尔值及超过 512 字符原话；第 200 行覆盖非 `QueryPlan` 注入值。两组均明确断言 planner、embedder、index、repository 和 reranker 没有调用。原生产原话及注入计划保护保持原实现。

- **[P3] 部分新增函数仍缺少用户要求的中文说明** — **ADDRESSED**。生产缺口已补齐于 `app/retrieval/rerank.py:12、18、65` 和 `app/retrieval/types.py:46`；修复 diff 为原清单中的测试函数补充了具体中文说明，共享保护及新增回归函数也有说明。只读核对 `.cache/final-fix-comment-reconciliation.json` 得到 **89 项映射**，每项说明均实际存在于对应源文件，无缺失映射。已有 `.cache/delivery-audit.json` 记录 **1329 个 Python 函数、missing_chinese_explanation=[]**；11 项装饰器误报未重复补写。

- **[P3] 独立比较摘要缺少关键解释范围** — **ADDRESSED**。`docs/validation/hybrid-retrieval-comparison.md:10` 明确真实 v1 未扣共享改写耗时、历史最终流保护较弱，以及当前 v2 修复仅经受控回归；第 12 行说明 canonical 三元组金标及重复物理主键映射不穷尽所有语义相关块。diff 仅增加解释段落，保留原始 JSON 和历史数字，包括真实运行 **101 项完成、19 项错误**；没有新增收费比较或修改门槛掩盖误拒答。

### New Breakage in the Fix Diff

- **None**。限定检查本次 17 文件修复 diff，未发现新增 Critical、Important 或 Minor 技术缺陷。共享最终流提取保留线上原有字段、长度、结束和清理边界；新增绝对期限检查没有改变模型、技术栈、输出预算、超时配置或重试设置。

### Out-of-Scope Observations

- **非阻断过程记录**：`.superpowers/sdd/2026-10-08-hybrid-retrieval/final-fix-report.md:96` 如实披露 Path.replace 的 Context7 补查发生在首次信号修正和三项真实恢复测试之后。已读取官方 CPython 来源的本地查询记录，当前实现符合完整写入关闭后再替换的模式；后补核对不能追溯满足“实现前先查”的时序要求。该遗漏已披露，不重新打开本轮技术修复。

### Checks

- **检查**：读取指定 brief、原七项 finding、修复报告和精确 `68da1f26f33f0b9169da2d305afb91a000ef40ee..2ac60e51ca44aa784c7085f2a04b45aaa8d434af` review package；因首次工具输出截断，仅补读遗漏区段，没有重新生成 diff 或运行 git 命令。
- **检查**：核对 Spec/Plan 的分类、共同生成约束、中文说明和用户批准的预算例外；本 diff 保留最终 **512**、改写/自评 **2048**、改写 **60 秒**、自评 **20 秒**、FAQ **90 秒**、单轮 **240 秒**及零新增重试。
- **检查**：已有 RED 日志尾部分别为 **18 failed / 19 passed** 和 **12 failed / 3 passed**；新增失败用例与修复边界对应。
- **检查**：已有 GREEN 日志尾部为初次定向 **256 passed / 2 skipped**、最终定向 **384 passed / 2 skipped**、真实恢复 **3 passed**、默认完整套件 **1096 passed / 109 skipped**。审计记录的 UTF-8、中文说明、密钥位置及私密追踪项均为空。
- **检查**：本复核全程只读，未运行测试、修改工作树/索引/HEAD、派遣子代理或调用云端服务；默认套件日志不代替控制端正在当前提交执行的完整 MySQL/Milvus 验证。前端 Vibe Coding 豁免与控制端拥有的交付草稿保持复核范围之外。

### Verdict

- **Fix round: All findings addressed, no new Critical/Important breakage** — 七项 finding 全部关闭；本结论仅批准该统一修复波，不替代当前提交完整服务验证，也不将历史真实比较或校准样本内结果升级为业务泛化质量证明。


## 同一修复波后续完整服务验证：Schema测试期望修正

控制端在提交 `2ac60e5` 上运行当前代码的显式 MySQL/Milvus 全套回归，真实 RED 日志 `.cache/final-service-suite.txt`：`1 failed, 1204 passed in 119.28s (0:01:59)`。唯一失败 `tests/integration/test_mysql_schema.py::test_mysql_schema_matches_supplied_ddl` 第15行，原精确表集合仍只有旧6表；当前数据库合法新增的 `low_confidence_questions` 和 `faith_cases` 被视为 extra items。未发现其他失败。

本次仅修改 `tests/integration/test_mysql_schema.py`：精确期望集合更新为当前8表，保留等号比较，仍拒绝任何额外或缺失表。全表 InnoDB/utf8mb4 排序规则、字段类型、可空性、中文枚举、时间默认值、外键、索引及种子验证所有原断言不变。文件首行中文说明同步当前表范围。没有生产/API/模型改动，没有删除或修改数据库表，没有以子集校验放宽精确契约。

该完整服务运行已作为本测试修正前的 RED，不重复默认完整套件。修正后 GREEN 命令：

```powershell
& 'D:/shixi/ecommerce-customer-service/.venv/Scripts/python.exe' -u -m pytest tests/integration/test_mysql_schema.py -q --run-mysql
```

当前工作树沙箱外授权运行，`.cache/final-fix-green-mysql-schema.txt`：`2 passed in 0.84s`，退出0。`git diff --check`通过。新用法只有集合字面量，无新增Context7 API。控制端随后重新运行当前提交的完整显式MySQL/Milvus套件，并让同一限定范围审查包含此微小测试hunk；本项仍属于同一次统一修复波验证。

后续测试提交：`c34af70dffe6c50e1ff90b091033630abff6edde` — `test: align database schema expectations with quality tables`；显式仅暂存此一个测试文件，root-owned所有草稿与交付audit未暂存。


## 旧表集合测试修正补充复核原文

- **完整显式服务验收发现的旧 Schema 测试仍只精确期望六表** — **ADDRESSED**。`tests/integration/test_mysql_schema.py:15` 保留集合等号校验，将期望更新为当前八表，仅加入 `low_confidence_questions` 与 `faith_cases`；仍拒绝任何缺表或额外表。两张质量表与 `sql/ch04-ddl.sql:12、37` 一致。第 19 行全表 InnoDB/utf8mb4 校验，以及后续字段类型、可空性、中文枚举、默认时间、外键、索引和种子断言均未修改。第 1 行中文说明准确更新为当前八表范围。

### New Breakage in the Fix Diff

- **None**。精确 `2ac60e51ca44aa784c7085f2a04b45aaa8d434af..c34af70dffe6c50e1ff90b091033630abff6edde` package 仅包含一个测试文件的期望集合及说明修正，没有生产/API/模型变化、数据库操作或子集校验放宽。

### Checks

- **检查**：读取 tiny review package 一次、追加修复报告及相关现有断言；未重复原七项复核。
- **检查**：`.cache/final-service-suite.txt` 尾部确认修正前唯一失败为该六表断言，结果 **1 failed, 1204 passed in 119.28s**。
- **检查**：`.cache/final-fix-green-mysql-schema.txt` 尾部确认同文件真实 MySQL 定向验证 **2 passed in 0.84s**。
- **检查**：全程只读，未运行测试、修改数据库/工作树/索引/HEAD、调用云端服务或派遣子代理；当前提交完整 MySQL/Milvus 套件由控制端执行，其结果不由本补充复核代替。

### Verdict

- **Supplemental fix: All findings addressed, no new Critical/Important breakage** — 此新增验收失败关闭；原七项复核结论保留。


## 控制端完整服务验证与流程决定

当前代码c34af70：完整显式MySQL/Milvus 1205 passed/0 failed/0 skipped，149.10秒、exit0。此前旧六表断言失败记录及单文件严格八表修复已保留；原七项复核及单文件补充复核均无剩余技术问题。服务全套不证明云端生成全通过，历史101完成/19错误及邮费误拒答仍保留。

Ruling: 为满足用户要求的当前完整回归，继续修正服务全套新发现的旧六表断言并对这一小段补充复核，不以最终单波上限保留失败；仍严格断言当前八表且保留引擎/编码核验 — 第四步明确新增两张质量表、测试前提已核实为八表，用户要求完成测试优先 — 若判断错会掩盖结构差异，故不改数据库、不降为子集判断，保留质量DDL专项验证。
