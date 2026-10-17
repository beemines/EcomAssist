# Authorized summary prompt clarification — source-ready, live acceptance pending

Source commit: `0a502c073027cbc78aa65ea61acb505b8f47337f` (base `ba7db6906116e73feec9d0b649b92f05d4f0397b`). This report is a documentation-only follow-up. Candidate `SUMMARY_SYSTEM` SHA256: `5d826ba18a7a3c43de1214dc7131081a9bd0b8ac458a2a447202909f0dae5d27`.

Human answer: “允许最小修复和有界复验（推荐）”. The approved question restricted this extra wave to the summary producer prompt and bounded rechecks within the original demo allowance; no model/window/threshold/guard changes, full-batch rerun, or clean-new-source21 claim. The controller assigned implementation/offline annotation here and retained the single scoped review and all real validation. No prior plan or task sequence was rebuilt.

## Exact source change and guard correspondence

Only `SUMMARY_SYSTEM` in `app/context/prompts.py` changed:

- Every successfully paired tool result, explicitly including FAQ, must be historical, with “当时” even when the summary only records the consultation topic or that FAQ was answered. This matches the existing `facts` → `当时|曾|历史` requirement in `validate_summary`; the unchanged guard already correctly rejected FAQ-only negatives.
- Retained amounts preserve source value/unit, explicitly `59900分`, without conversion to `599元`. Actual order evidence has `amount_cents: 59900`, `currency: CNY`. Conversion introduced the unsupported numeric token `599` and the existing trusted-source token guard correctly rejected it.
- Retained time expressions preserve source separators/wording, explicitly `9:00 至 22:00`, without joining to `9:00-22:00`. Actual FAQ answer says `人工客服服务时间为每日 9:00 至 22:00`; joining introduced unsupported token `00-22` under the unchanged token guard.

Examples are expressly conditional on a source fact, so the prompt does not request inventing example facts. The prior sole-content JSON, factual short summary/200-character maximum, trusted entity sources, FAQ/citation restraint, mock simulation, canonical order-switch/ambiguity, negation and action-stage rules remain intact. No validator, schema, manager, history/layers, budgets, capacities, retry behavior, model API, imports, or dependencies changed. No old segment was recompressed and no history was deleted.

## Actual negatives and human annotations

Ignored artifact: `runtime/context-evidence/summary-prompt-fix-20261018/annotated-cases.json`.

Ignored executable: `.cache/summary-prompt-fix-check.py`; output `.cache/summary-prompt-fix-annotations.txt`.

Inspected actual requests/responses: 27 from `runtime/context-evidence/ch07-demo-21-20261017/original-attempt-1/`; 61,73,85,90,96,98,103,105,110,111,117,118 from its `resumed-turns-7-21/` directory. Both `summary-failure-analysis.json` and `resumed-turns-7-21/final-failure-analysis.json` were inspected, along with the current producer and unchanged summarizer guard.

All **13 actual negative bodies remain rejected**, with their original recorded guard error. All **13 human-authored canonical references pass** the unchanged guard. These references minimally correct the observed historical label/amount/time formatting. They are annotations, **not candidate model output**, and guard acceptance does not prove semantic faithfulness or general model reliability. Earlier negation/actions/ambiguity behavior is covered by the existing tests rather than mirrored prompt-wording assertions.

The artifact retains each complete actual negative raw body, IDs/ranges, original request/response pointers and file SHA256, original `source_sha256` and `snapshot_id` labels, independently computed raw-source-body SHA256, repository row hash, source order/time evidence and required entities. Repository row hashes independently match the original snapshot IDs for all 13. Prior analysis `source_sha256` is preserved verbatim without assuming its serialization basis.

## Three exact sources for controller-owned real contrasts

The acceptance owner selected these distinct immutable source batches. Use each exact saved request's original human/source body with the candidate summary system. This implementer made no candidate model calls and no contrast DB append.

| Index | Actual request pointer under original-attempt-1 | Range | Observed mismatch | Candidate estimated input |
| --- | --- | --- | --- | ---: |
| 27 | `summary-request-27.json` (response same prefix `summary-response-27.json`) | 504–523 | `599元` conversion | 6913 |
| 61 | `resumed-turns-7-21/summary-request-61.json` (response `summary-response-61.json`) | 524–539 | Missing historical marker in FAQ-only output | 7054 |
| 118 | `resumed-turns-7-21/summary-request-118.json` (response `summary-response-118.json`) | 548–579 | Missing historical marker, converted amount, joined time range | 12097 |

Index61 is the actual failed 524–539 batch, not the accepted summary2 batch 524–547.

Preserved original evidence identities:

- 27 source_sha256 `39e48eaf6975686150044b150caea6bbe2436d704ba486705b738e72164e9ee4`; snapshot_id `44a6e080dc47f6d006c6e14eeb6c42ceb87ce3329bbf959b248cb48cb6154885`.
- 61 source_sha256 `30289af7f5050f1c6251725595b9834331426d35922357cfedf2f6c2e46d20ae`; snapshot_id `0f108bc00cde952a8ded3d275525ff3c4180bc02e12a485df9b9d632a928a970`.
- 118 source_sha256 `8be63d20b7fbf58d12d69309341130cf3a7cb5fe205a6ba755176e60cefb9dd9`; snapshot_id `3bb8a408eeea920d043d053b921b8b5489059deb430cfe08c41f27520d45f24d`.

The complete request/response file hashes and all additional samples are in the ignored artifact; no original evidence was rewritten.

## Fresh offline verification

PowerShell `login=false`, worktree cwd, `PYTHONUTF8=1`, `PYTHONUNBUFFERED=1`, `PYTHONPATH` equal to this worktree; Python used the existing narrow `require_escalated` venv-launcher workaround. No dependency installation or environment-secret dump.

1. `.venv/Scripts/python.exe .cache/summary-prompt-fix-check.py`: final **exit0**. 13 negative rejections/13 annotated reference acceptances, actual factory budget recomputation, identical candidate system prefix across all saved batches, strict two-message system/human composition, and each batch admitted with unchanged output512+safety540 inside demo18000. Final successful output `.cache/summary-prompt-fix-annotations.txt`.
2. `.venv/Scripts/python.exe -m pytest tests/test_context_summarizer.py tests/test_context_prefix.py tests/test_context_budget.py tests/test_context_lifecycle.py tests/test_context_long_conversation.py tests/test_context_manager.py -q`: **exit0, 192 passed in 31.61s**. Log `.cache/summary-prompt-fix-focused.txt`. Covers validation/protocol/negation/action/ambiguity, stable workflow prefixes, actual budget rules, lifecycle/manager recovery and both existing full offline21 trajectories. No added prompt-wording tests and no whole-suite rerun.
3. `git diff --check`: exit0 before source commit. Source diff inspected: only the single summary-system producer clarification; explicit ignored-path checks confirmed annotation/runtime evidence and scratch script remain ignored.

Rework retained transparently: one initial combined patch failed atomic context verification, then was reapplied accurately. The first two annotation launches each exited1 at the first sample because they wrongly assumed that the prior analysis `source_sha256` represented (first) repository row serialization and (second) the raw human/source body. Corrected the annotation bookkeeping to preserve that prior label separately, compute both hashes explicitly, and verify the repository hash against the existing snapshot ID. These were harness assumptions, not source/validator failures. Failed stdout remains in the tool record; the final success log replaces the scratch command's earlier output file. No old evidence was altered to make assertions pass.

## Fresh capacities and prefix cost

Factory computation uses `profile_budget` with offline `profile_settings` and actual production registry construction, not a copied constant.

| Profile | Window | H | Layer1 | Layer2 | Summary allowance | Safety | Derived turn limit |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| default | 128000 | 59880 | 41916 | 17964 | 2000 | 3840 | 1135879 |
| demo | 18000 | 2691 | 1883 | 808 | 563 | 540 | 174823 |

Main workflow decision fixed prefix remains F2890. Summary system estimated payload increased **830→1024 (+194)**; each saved source's full estimated summary input increased by194. Largest examined input is12097; with output512+safety540 the total13149 fits18000. This is an input-window check on these actual samples, not a proof that arbitrary future batches fit. Summary generation's own unchanged preflight remains authoritative. Main workflow H and turn limits are unchanged because this summary-system text is not part of `workflow_budget`'s main phase inventory; no capacity was adjusted to compensate.

## Acceptance status and hold

Source-ready only. Default fixed21 plus separate postrestart1002 continuation passed on producta82; the previous full2720/184 was also a82. This prompt candidate has only the fresh scoped offline results above.

Original demo conv70 remains **20 completed, original question21 HTTP422 before model invocation**: S547/L579, compact548–583 history2744 exceeds H2691. Original first20 rows remain intact; faileduser584 exists in SQL while the last completed checkpoint isuser580. That expected failed-root inequality is not evidence of raw deletion. No original21-passed or clean-new-version21 claim is made.

This implementer made **zero real API/browser/application-DB/restart calls**, no business submission, and touched neither existing8004 nor8002/8003. Physical demo ledger remains118GLM/16embedding/16rerank against immutable150/50/25, leaving32/34/9. All real calls remain **HOLD** for the controller/acceptance owner: at most the selected three saved-source contrasts, recovery and original final-question recheck, plus one conditional restart continuation within that same remaining allowance. No full21 rerun, new capacity, new guards, extra implementer agent/reviewer, merge or push. The controller owns the one scoped review and the real-call release; source readiness does not resolve the still-incomplete real acceptance.
