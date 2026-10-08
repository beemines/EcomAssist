# Chapter 3 code review record

Current status: the three initial Important findings below were fixed in 86df0d1 and independently re-reviewed as ADDRESSED, with no new or residual findings. Final current-code tests passed 729/729 with MySQL/Milvus explicitly enabled. The initial review is retained verbatim below, followed by the scoped fix-wave verdict. Integration is pending the user's choice.

# Final whole-branch review — 6907da9..e9eb358

Base: `6907da9ba3db196ad3615033b6ee3ba101c90da7`
Head: `e9eb358333687cc5650a68e0605641911791cb45`
Verdict: **With fixes — three Important findings; no Critical or Minor findings.**

## Scope and evidence

Read the final brief, approved design, implementation plan, recovery ledger, and supplied 501,306-byte / 8,310-line review package in bounded sequential passes. Reviewed all 78 changed files, including the complete lockfile diff, development notes, validation narrative, actual safe JSON artifacts, and tests. Two output cutoffs were recovered only for their named README/config/extraction and deployment-note content. No second Git diff, history crawl, changed-source-file reread, private history, `.env`, credential read, suite rerun, cloud request, deployment, or integration was performed. The controller's uncommitted note-only entry is outside this reviewed HEAD.

Followed the requesting-code-review `code-reviewer.md` criteria. The prior clean task reviews are useful context, not proof of whole-branch correctness. The two focused probes below execute current code against synthetic in-memory boundaries only. Dotenv and bytecode generation were disabled. The first sandboxed Python invocation could not resolve the uv interpreter location and was stopped; the approved read-only invocation succeeded. That launcher restriction is not a product defect. No outside-diff product source was inspected; no code/index/HEAD was modified. This requested scratch report is the only file written.

## Strengths

- The MySQL authority boundary is clear: import/promotion commits pending rows atomically; embeddings and Milvus I/O happen outside the write transaction; acknowledged IDs are verified before `mark_done`; retrieval projects only MySQL done text in vector-hit order. No LIKE fallback, rewrite, hybrid search, reranking, or arbitrary threshold was introduced.
- The explicit Milvus schema, fixed model, SDK pin, index/metric/consistency checks, positive INT64 limits, returned vector order/dimensions/finite values, and upsert acknowledgement validation form a coherent adapter boundary. The real SDK protobuf return-container case has a regression, rather than relying solely on a hand-written mock response.
- Cancellation and ownership received meaningful coverage: the named lock uses a dedicated connection, invalidates uncertain acquisitions/releases, and shields release against repeated cancellation. App/CLI exit stacks unwind independently owned resources after initialization or close failures and leave injected resources caller-owned.
- Migration maps the supplied SQL closely, checks existing structure instead of silently repairing it, and retains original-table regression assertions. Document insertion and neighbor linking share a transaction; malformed FAQ groups and oversize MySQL fields fail before insertion.
- The live retrieval artifact contains actual queries, IDs, MySQL bodies, persisted tool arguments, and the full original-question answer. I independently compared the answer with the included demo policy/FAQ: 8 yuan, the 99-yuan paid-goods threshold, scope/exclusions, and synthetic-data disclaimer agree. The report honestly records domain retrieval 5/5 and overall labels 5/6, with the unrelated-query miss still false.
- The recovery artifact distinguishes the failed launcher attempt from successful owned-PID interruptions, records before/after pending/done states, acknowledgement IDs, body hashes, and unique vector counts for both boundaries. The final harness code preserves primary failures while attempting independent cleanup. These are materially stronger acceptance checks than simply raising an exception inside a worker.
- Online model/provider/output budget remain unchanged; the dedicated offline QA budget follows the controller's explicit ruling. Documentation differentiates controlled tests, live provider samples, buffered ASGI SSE evidence, and deployment/scheduler work that has not occurred.

## Issues

### Critical (Must Fix)

None found.

### Important (Should Fix)

1. **R1 / P2 — Existing multi-question chunks do not participate in deduplication per question.**

   - Location: `app/knowledge/mining.py:14` (with `app/repositories/knowledge.py:98-100`).
   - `qa_pairs()` returns the full `questions` cell, and the `seen` comprehension normalizes that entire multiline value into a single string. The Markdown importer intentionally stores multiple supplied questions separated by newlines. Consequently an extracted QA matching either individual question and the identical answer is not recognized as already present.
   - Focused current-code probe: existing `questions='邮费是多少？\n快递费用怎么收？'`, `answer='标准配送8元。'`; staged question `'快递费用怎么收？'` with the same answer. Actual promotion call was `kept_ids=[7], discarded_ids=[]`, result `{'kept': 1, 'discarded': 0}`. Required result is discard. The existing real/global dedup tests seed only one-question cells, so they miss the importer→mining boundary.
   - Impact: a supported document format produces duplicate knowledge and vectors when historical QA is mined, contrary to design §4: existing knowledge's individual `questions` variants must all participate. Duplicates also consume the fixed Top3 result slots.
   - Smallest fix: expand existing `questions.splitlines()` into separate nonblank `(question, answer)` comparison pairs before NFKC/whitespace normalization; do not rewrite stored text. Add a focused regression using a multi-question existing chunk, including normalized punctuation/whitespace, and retain the different-answer case. No schema or semantic matching change is needed.

2. **R2 / P2 — The extraction prompt authorizes semantic merging before the required exact-dedup stage.**

   - Location: `app/core/prompts.py:69` (`'同义重复可合并；不同答案保留各自来源，不自行裁决。'`); related acceptance gap in `evals/evaluate_qa.py:23-35` and `evals/qa_extraction_cases.jsonl:2`.
   - The approved design and final brief explicitly preserve different real question phrasings and limit deduplication to normalized identical question/answer pairs. The production prompt instead tells the model that synonymous duplicates may be merged. If a batch contains “邮费是多少？” and “快递费用怎么收？” with the same answer, following that instruction can discard one real phrasing before staging; the later exact deduplicator cannot recover it.
   - This is a direct instruction/requirement conflict, not a claim that a particular live sample failed. The current duplicate annotation contains two identical questions only, and its scorer intentionally allows paraphrases, so the recorded 8/8 does not validate preservation of distinct real questions.
   - Impact: extracted knowledge/provenance depends on the model's semantic consolidation despite the explicitly chosen exact-only rule, losing distinct source questions and undermining the advertised boundary.
   - Smallest fix: remove permission to merge synonyms and explicitly retain each distinct source question with its source answer; only privacy removal necessary for a general QA should alter source wording. Leave normalized exact decisions to the existing global stage. Add a labeled two-paraphrase/same-answer case that requires both real question variants (and source membership), plus a focused controlled regression. Because this changes an extraction prompt, perform the appropriately scoped real labeled validation and record it separately from the existing 8/8 evidence; do not silently relabel that evidence as proving the new behavior.

3. **R3 / P2 — A failed mining batch cannot be identified from the delivered job output.**

   - Location: `app/knowledge/mining.py:37-40`; `app/knowledge/cli.py:96-99`; scheduled invocation at `scripts/run-knowledge-daily.ps1:11`.
   - The stable `batch_no` is computed but neither logged nor attached to a safe error. Extraction failures happen before `stage()`, leaving no staging row for that batch. The CLI strips the exception to its type and prints only the full window. No batch/conversation/message boundary is retained, and the scheduled launcher supplies no log destination.
   - Focused current-code CLI probe: synthetic conversation ID 4321 / last message 9876 with `InputTooLong`. Exit was correctly 1, but the entire output was the Beijing window plus `Knowledge job failed (InputTooLong); check configuration and input`. Neither its batch hash nor its source boundary appeared.
   - Impact: when one conversation is oversized or one model batch is invalid, the remaining window stops, as designed, but the maintainer cannot locate the failing batch from the daily-job evidence. Blindly rerunning the whole window repeats cloud work and still cannot isolate a persistent input failure. Design §4 explicitly requires recording the failed batch and supporting manual replay.
   - Smallest fix: emit safe batch context before extraction or wrap the failure with structured, sanitized `batch_no`, window, and conversation/message IDs (never message bodies or provider exception text). Ensure the daily launcher retains this output in a known log file or document an equivalent actual capture path. Add a focused failure-output test asserting identity is present and synthetic secret/body text remains absent. Keep the existing fail-fast/nonzero behavior and schema.

### Minor (Nice to Have)

None. No findings are parked or silently deferred.

## Recommendations and verification assessment

Address the three findings in the single controller-owned fix wave, with narrow regressions at the relevant boundaries. R1 can be proved entirely offline plus the existing real repository integration if repository behavior is altered; R2 requires a focused prompt/data acceptance update; R3 requires a synthetic failure through the actual CLI/launcher path. Do not introduce new tables, semantic deduplication, a scheduler framework, or broader retries.

The package records 652 offline passes / 62 gated skips, all 62 explicitly enabled service tests passing, and 29 focused tests after the final cleanup fix. I reviewed the code/tests and artifacts but did not rerun those suites; the controller's final comprehensive run remains required after the fix wave. The QA live artifact retains counts and pass decisions rather than raw extracted QAs, so it supports the recorded labeled scorer result, not an independent verbatim audit of all eight model responses. The full online shipping answer *is* retained and was independently checked above.

## Declined to judge

Every behavior considered and intentionally left outside this verdict is listed here for controller adjudication:

- **Domain-irrelevant Top3 recall and a universal rejection threshold:** explicitly observed and accepted chapter boundary; no fabricated empty result or threshold fix is requested.
- **Semantic duplicate elimination and automatic resolution of conflicting answers:** explicitly excluded; retaining paraphrases/conflicts is required, and R2 addresses the contradictory prompt rather than requesting semantic merging.
- **Whole-document reimport/version replacement and edits to already-done chunks:** explicitly excluded; per-chunk vector primary-key replay is the supported guarantee.
- **Byte-for-byte equality with a separate original user DDL attachment/private prompt:** the supplied DDL, ORM, migration, and tests were compared, but independent original-source bytes are not in the permitted package; the recorded source hash is not substituted for unseen original bytes. No private prompt/history was read.
- **A formal MySQL↔Milvus model-version migration or two independently configured databases sharing the fixed production collection:** fixed model/collection and one local deployment are the accepted architecture; no migration/multi-tenant mechanism is promised.
- **Historical mixed database timezones and DST migrations:** documented limitation; current fixed UTC storage and Beijing window conversion are covered by explicit integration evidence.
- **Deterministic generative output on repeated extraction windows:** the selected contract has normalized exact comparison and same-batch/source/question/answer staging checks, not a persisted completed-batch manifest or a promise of deterministic LLM phrasing. R1/R2 still require correctness within that exact-only boundary.
- **Full Markdown/CommonMark support beyond the named ATX/fence/paragraph/sentence/table/Q&A conventions:** the chapter deliberately uses a bounded standard-library chunker; no renderer or general parser is promised. The named conventions and failure paths were reviewed.
- **Repeated lifespan entry on the same already-shut-down FastAPI object:** production uses one lifespan per app process; reentrant test-host lifecycle behavior is not a stated delivery requirement. The intended one-lifespan ownership/error paths were reviewed.
- **Provider quality for arbitrary private conversations or all possible prompt injections/PII:** eight synthetic labels are evidence only for their samples, not a universal guarantee; no private history/cloud repetition was authorized for review. This does not excuse the concrete prompt conflict in R2.
- **Browser rendering, actual network frame timing, and complete chapter-2 tool/handoff model quality:** UI is unchanged; this chapter's live ASGI transport is expressly buffered, and prior chapter-2 failures remain disclosed rather than asserted fixed.
- **Production main-checkout build, real customer-history mining, host task registration, and deployment security beyond the local loopback setup:** not performed or authorized in this review; the README explicitly gates them on deployment. Logging for the delivered scheduler path is still in scope as R3.
- **Remote artifact reproducibility on every OS/Python platform, package supply-chain audit, and registry metadata revalidation:** the pinned lockfile diff and reported local 3.0.2 runtime evidence were reviewed; no fresh installs or internet/package downloads were warranted by a concrete defect.
- **Physical Milvus version/tombstone compaction after upsert:** live checks correctly assert unique currently queryable primary keys and preserved MySQL text; underlying storage compaction is not this chapter's recovery guarantee.
- **Credential rotation and proof of eradication from prior private tool output:** the incident is transparently documented, but rotation is user/provider work; no secrets were read or replayed and no credential-eradication claim is made here.
- **Re-executing actual provider/kill acceptance or the final whole suite at this review seat:** explicitly assigned to existing evidence and the controller's post-review verification; the two new in-memory probes alone were run.

## Assessment

**Ready to merge? With fixes.**

The dense retrieval/state-recovery architecture and actual shipping/restart evidence are sound for the approved chapter scope. Resolve the multi-question dedup omission, contradictory semantic-merging instruction, and missing failed-batch traceability, then complete scoped rereview and the controller's final verification before integration.

---

# Final scoped fix-wave re-review — e9eb358..86df0d1

The initial three findings above were fixed in 86df0d1. The independent scoped review below confirms their resolution; comprehensive current-tree tests are recorded separately in ch03-results.md.
- **R1 — Existing multi-question chunks participate in deduplication per question — ADDRESSED.** `app/knowledge/mining.py:15` expands each existing `questions.splitlines()` value, skips blank variants, and pairs each variant with the existing answer before the unchanged NFKC/whitespace normalization. The seen set still includes the answer, so a different-answer conflict remains eligible for promotion. `tests/test_knowledge_mining.py:96` covers two stored variants, blank lines, fullwidth punctuation/space and answer whitespace, and asserts two discards plus one retained conflict. No repository/schema/stored-text changes appear in this fix package.
- **R2 — Extraction preserves distinct actual source questions and paired sources instead of merging synonyms — ADDRESSED.** `app/core/prompts.py:69` now explicitly preserves each different real question with its paired assistant answer/source, prohibits synonym merging, retains source wording except necessary privacy removal, and leaves normalized exact duplicates to the later stage. `evals/qa_extraction_cases.jsonl:9` appends the two-source/same-answer label; the original eight lines are unchanged in the package. `evals/evaluate_qa.py:31` gates this explicit label on normalized original-question equality and an extracted QA with the expected paired source, alongside the existing answer-term and no-extra-unique-QA checks. `tests/test_qa_evaluation.py:16` rejects missing, keyword-preserving rewritten, invalid-source, swapped-source and wrong-answer outputs; `tests/test_qa_evaluation.py:27` accepts normalization and preserves all original labels. `docs/validation/ch03-qa-live-final9.json:3` records a separate single current-prompt live run: 9/9, attempted 9/not attempted 0, two QAs for the new label, glm-5.3-flash/2048, exit 0, no errors, UTC 2026-10-07T15:32:13.6780720Z–15:32:57.8228298Z. This verdict accepts the tested strict scorer conclusions and counts; actual literal outputs were not retained and were not manually audited. The withdrawn late capture requirement is not reopened.
- **R3 — Failed mining batches are identifiable in safe CLI output retained by the daily launcher — ADDRESSED.** `app/knowledge/mining.py:48` validates numeric conversation/last-message IDs before constructing the unchanged window/source batch hash; `app/knowledge/mining.py:58` wraps extraction/staging failures using only that hash, window, validated IDs and exception type. `app/knowledge/cli.py:94` prints the known safe error and returns 1 while retaining the generic sanitized path for arbitrary exceptions. `tests/test_knowledge_cli.py:34` exercises actual CLI → mining → QAExtractor for both oversized-input and provider failures, asserts the independent literal hash/window/source and safe type, and excludes private body/provider operands. `scripts/run-knowledge-daily.ps1:18` merges actual stdout/stderr through Tee-Object into the documented ignored `.cache/knowledge-daily.log`; `scripts/run-knowledge-daily.ps1:20` captures native exit status and `scripts/run-knowledge-daily.ps1:29` returns it. `tests/test_knowledge_cli.py:159` executes the actual launcher with only uv shadowed by a native synthetic child, verifies both streams in the actual log and retains exit 23. The reported context identifies the paginated mining batch, not an unclaimed individual inner model sub-batch.

## New breakage in the fix diff

- **None.** The narrow mining, safe-error/CLI, prompt, scorer and PowerShell changes introduce no new Critical/Important/Minor defect found in the supplied fix diff. Cancellation remains outside the new `except Exception` wrapper; ordinary failure remains fail-fast/nonzero. The exact-label scorer addition is optional and does not relax old labels. Documentation distinguishes prior eight-label evidence, current nine-label evidence and its literal-output limit.

## Out-of-scope observations

- **None.** Untouched whole-branch observations and previously accepted boundaries were not reopened.

## Checks and evidence assessment

- **Checked:** `final-review.md`, `final-fix-brief.md`, `final-fix-report.md`, and the supplied 53,566-byte `review-e9eb358..86df0d1.diff` for fix base `e9eb358333687cc5650a68e0605641911791cb45` → HEAD `86df0d1435a6f9d1ecd9e770b5538ae21c3b78c0`. The initial batched tool display truncated report/diff output; only the missing report and named diff portions were recovered. No Git diff/history rederivation or source-file crawl occurred.
- **Checked reported coverage against code/tests:** complete focused RED was 7 failed/20 passed, specifically covering R1, rewritten/wrong/swapped-source scorer behavior, oversized/provider CLI identity and absent launcher log; first GREEN was 43 passed; fresh final scoped current-code GREEN was 43 passed/7.45s/exit 0. The report names the four covering files and commands. The affected actual MySQL mining/global-normalization/conflict/window-replay regression records 1 passed/1.27s. These outputs are reported execution evidence, not reviewer reruns.
- **Checked retained acceptance evidence:** the diff adds controlled9 and actual current9 artifacts separately, preserves the eight existing case lines, and does not modify the old live-eight artifact. Current live9 records all nine attempted cases, all verdicts true, expected excluded-class zero counts, duplicate/conflict/new-label counts of 2, current model/budget/timing/exit and no errors. The report explicitly records no pooled retries or reconstructed literal outputs.
- **Checks run by this reviewer:** read-only inspection only. No test suite, cloud call, actual service rerun, extra probe, private-history/secret/.env read, scheduler/main-history job, source/index/HEAD edit, deployment or integration. No specific unresolved code doubt required a new probe. This requested scratch report is the only write.

## Verdict

- **Fix round: All findings addressed, no new Critical/Important breakage.** R1, R2 and R3 are closed for this scoped fix-wave re-review. Controller-owned residual adjudication, fresh final all-flag verification and finish/integration remain outstanding; this review does not claim those steps occurred.
