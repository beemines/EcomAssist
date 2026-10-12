# Final working-tree review — online chat acceptance

Base: `273233b36498103b82b57ec9c270a89ce6633be4`. Reviewed the supplied final working diff, current implementation, new regression tests, acceptance plan and ledger, publication/calibration artifacts, browser reports and their operational scripts. This is a review of uncommitted work; no commit, browser run, model request, or test-suite rerun was performed by this reviewer.

## Findings

- Critical: none found.
- Important: none found.
- Minor: none found requiring a code change or deferral.

## Review conclusions

- `app/config.py:27` and `app/main.py:97`: online low reasoning effort is optional and limited to `low`; absence preserves the original factory call. Explicit online configuration stays separate from the evaluation setting. The actual SDK transport regression checks omission/presence, the three output budgets, timeout and zero retry behavior.
- `app/retrieval/service.py:35`: raw-query fallback requires `invalid_structured_output` and an allowlisted parser-only exception chain. Authentication, storage, input limits, arbitrary failures and timeouts cannot enter fallback. `QueryPlanner` and strict JSON validation are unchanged. The complete original query feeds retrieval after fallback, retaining model identifiers, amounts and negative conditions.
- `app/retrieval/service.py:48`: deadline-owned cancellation is distinguished from caller cancellation; the previously reported timer classification issue is corrected in the inspected code, with an actual `QueryPlanner` timeout regression. The post-planner checks also stop late results and swallowed caller cancellation before retrieval dependencies execute.
- `app/core/tool_chat.py:133`: FAQ normalization is applied only after valid strict FAQ schema validation, copies the model message, replaces only a non-original keyword with an actual original fragment, and updates both message representations before persistence. The actual tool closure retains the entire original question and category. Invalid schema and direct tool/repository guards remain intact. New tests exercise real chat orchestration/executor/repository boundaries, audit consistency, dependency failure and cancellation.
- `app/tools/executor.py`: added error codes use fixed safe messages and logs omit exception bodies and tracebacks. Existing failure/cancellation handling remains in place.
- `.cache/publish-online-merchant.py`: publication reuses existing locked storage and vector write/readback operations, rejects partial/ambiguous reuse and unexpected collection IDs, verifies exact 50 IDs plus text/category/done status, and checks retained old records. The committed publication artifact records 50 merchant chunks and 84 preserved prior chunks. Calibration explicitly covers eight independent retrieval-only cases and makes no population or generation quality claim. README correctly warns against applying full-database rebuild/verification to the mixed database's subset collection.
- Browser evidence contains five completed real chat cases with factual answers or explicit refusal, SSE completion, source dialogs and feedback locking. Feedback is intentionally browser-local in the existing product, which the harness verifies. The independent RAG page report passes with real GET responses and 20 chart bars; no fresh evaluation is run.

## Integration gate

Code review is clear for integration once the controller finishes its already-running full suite. Follow-up inspection confirms `docs/validation/online-chat-acceptance.json` now reports passed with the independent RAG-page success joined; the original wait failure is retained separately. `docs/validation/online-chat-storage-proof.json` reports passed for all five rounds, final committed answers and tool identities, the refusal pool, exact online 50-chunk data, and the unchanged retained 84-row hash. The scoped Task 1 rereview also marks all three prior findings addressed. The latest suite log is at 69% without a final result. Do not commit or push until the suite completes successfully; this remaining gate is already in progress and is not a new implementation defect.

Verification performed by reviewer: source/artifact inspection and `git diff --check` (no whitespace errors printed; only existing LF/CRLF notices). No additional tests were necessary to establish a concrete new finding.

Controller final verification: full suite completed with exit 0, 1531 passed, 116 skipped. Integration gate above is now satisfied. All five browser cases, independent RAG page, and storage proof are passed.
