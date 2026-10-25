# Authorized summary prompt clarification — bounded summary pass, end-to-end acceptance unmet

**Historical summary-stage snapshot, 2026-10-18:** R1 source `0221b71c8fec3302a0eed0414776159c8d284471`, tested at clean HEAD `1916cbb4775515162582a260115e9a9b3d8977c5`. Three exact-source contrasts passed and normal startup recovery committed seq3. The original final question correctly resolved1001, but classification returned其他/confidence0.6 and no current business read occurred. The conditional restart/1002 continuation was not executed. All real calls are stopped; Task11/end-to-end acceptance remains unmet. Final demo125/16/16, remaining25/34/9 within unchanged150/50/25. The same scoped reviewer closed evidence-only: bounded actual SUMMARY gate PASS; startup PASS; E2E FAIL. Earlier source-ready/HOLD/counter paragraphs below are historical snapshots, not the current status.

Later classification/understanding repairs and qualified final delivery are recorded in [final actual evidence](2026-10-18-final-intent-recall.md). The125-call/E2E-failed status above belongs to the summary stage; latest demo149/16/16 includes successful current1001 reading and restart continuation, while explicit no-refund restatement remains NOT MET.

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

## Documentation placement correction

The implementer mistakenly force-added the temporary ignored SDD report path in commit `868cf8188d5a272de3874645bc179b1092b1107c`. The controller intended that location to remain ignored scratch. This docs-only correction preserves the report under `docs/superpowers/reports/2026-10-18-summary-prompt-fix.md` and removes the temporary path from Git tracking with `git rm --cached`, keeping its ignored physical copy for existing review references. Source commit `0a502c073027cbc78aa65ea61acb505b8f47337f` is unchanged. No source edits, tests, API calls, application access, or restarts were performed for this correction.

## R1 — final candidate under the same authorization

R1 base HEAD `62868c23b6fdefadac118c487dda02da633a5da4`; this appended section is committed with the R1 source. Candidate prompt SHA256: `58dd217fec066d1328851591690354425c66dcdf9461bbf2543de695e782ca64`. This is the one final candidate allowed within the existing minimal-prompt authorization. It does not authorize a third candidate if real validation fails again.

### Prior candidate's actual failure and cost

The acceptance owner ran only real contrast27, original range504–523, on candidate62868c2/prompt5d826ba1. It preserved historical/simulation labels and59900分 but omitted required model `MH-LP200`; unchanged `validate_summary` rejected it with `Summary omitted a source entity; use smaller complete batches.` StrictSTOP followed immediately. Contrast61/118, recovery, page recheck and restart did not run. Actual evidence is `runtime/context-evidence/ch07-demo-21-20261017/extra-minimum-validation/source-contrasts/result.json` plus `physical-packets.jsonl` (request/response index1, session `2026-10-18T00:10:51.152153+08:00`). Its `nonstream-replies.jsonl` exists but is empty; the actual response is retained in the physical capture and result wire, whose body equality is verified by the ignored annotation script.

This cost1GLM/0embedding/0rerank: demo totals **119/16/16**, same hard150/50/25, remaining **31/34/9**. The old actual failure and its cost remain evidence, not a successful candidate result or reset ledger. Prior sections'118/16/16 describe the earlier stage only; this R1 section is the current handoff state.

### Minimal clarification and actual annotations

The only R1 production edit is one added `SUMMARY_SYSTEM` sentence: treat trusted orders, product_id/model, phone numbers and user-source identifiers as the mandatory `required_entities` completeness checklist; check each item before output and preserve every exact order/model, without replacing it by a product name or shortening the model for brevity. This makes the existing source-entity obligation explicit. `required_entities` and `validate_summary` remain unchanged; no validator/schema, source provenance, batch split, model, window, budget, threshold, config or manager edit. Earlier canonical history/mock, raw amount/time, action/negation/ambiguity rules remain intact.

Ignored R1 artifact: `runtime/context-evidence/summary-prompt-fix-20261018/annotated-cases-r1.json`; script `.cache/summary-prompt-fix-r1-check.py`; log `.cache/summary-prompt-fix-r1-annotations.txt`. The previous `annotated-cases.json` remains unmodified and its hash is recorded in R1. R1 keeps the first13 actual negatives and adds the14th **actual prior-candidate model output**, with physical/result file hashes, original source hash, candidate identity/session/index and exact raw response. The sole missing entity is independently confirmed asMH-LP200. Its clearly marked **human-authored reference** restores that model to the order1001 clause and passes the unchanged guard. All14 actual negatives remain rejected and all14 human references pass; no R1 real model output is fabricated or implied.

### Fresh R1 checks and capacities

- `.venv/Scripts/python.exe .cache/summary-prompt-fix-r1-check.py`: **exit0**. Revalidates all14 actual negatives/references, physical/result actual body equality, original source identities, exact missing entity and pure actual factory budgets; previous annotation file is preserved. No API or app-DB call.
- `.venv/Scripts/python.exe -m pytest tests/test_context_summarizer.py tests/test_context_prefix.py tests/test_context_budget.py tests/test_context_lifecycle.py tests/test_context_long_conversation.py tests/test_context_manager.py -q`: **exit0, 192 passed in34.74s**, `.cache/summary-prompt-fix-r1-focused.txt`. Same existing summary/protocol/entity/negation/action/ambiguity, prefix/budget, lifecycle/manager and both offline21 trajectory coverage; no new wording-mirroring test or full-suite rerun.
- Both commands use PowerShell loginfalse, PYTHONUTF8/PYTHONUNBUFFERED1 and worktree PYTHONPATH, with the existing narrow elevated venv-launcher workaround. No dependency install. Scoped source diff contains only the one sentence; `git diff --check` is checked before commit.

Fresh actual factory H is stilldefault59880/demo2691; layer1 41916/1883, layer2 17964/808; main decision prefixF2890 and derived turn caps1135879/174823 remain unchanged. R1 summary system estimate is **1163**, versus prior candidate1024 (**+139**) and original830 (**+333**). The selected27/61/118 candidate inputs are **7052/7193/12236**; the largest plus unchanged output512+safety540 is13288, within demo18000. No capacity was adjusted. The unchanged summary preflight remains authoritative for other batches.

### Handoff limits

R1 is source-ready/offline-verified only; original demo final-question acceptance remains incomplete. This implementer made zero real calls, browser/application-DB access or restarts and spawned no agents. Controller owns the one scoped R1 rereview and release of at most three revised saved-source contrasts27/61/118 within the original remaining cap, preserving the prior candidate failure. Another real failure closes the run honestly as unmet; no third candidate or full21 rerun. Recovery/page/conditional restart remain controller-owned and subject to the same cap and stop conditions.

The acceptance owner has a separate dirty edit in `docs/superpowers/reports/2026-10-17-context-management-acceptance.md`; R1 leaves it untouched and unstaged. Only the summary prompt, append-only dev-notes and this public report are included in the R1 commit. The temporary SDD report remains an ignored physical copy, not a tracked deliverable.


## Final actual bounded evidence and same-review closure

R1 prompt SHA remains `58dd217fec066d1328851591690354425c66dcdf9461bbf2543de695e782ca64`. No product changes followed the R1 scoped source approval. Actual source contrasts used immutable failed requests27[504–523],61[524–539],118[548–579], once each, through the original demo cap and HTTP capture hooks. All3 passed the unchanged guard; no contrast appended a database segment or recompressed saved segments. Prior v3 contrast27's missingMH-LP200 failure remains unchanged, along with its1GLM charge.

The three R1 contrasts added3GLM:119→122. Exact-owned Hidden8004 restart then used the normal SummaryManager startup scan, without directnotify/anchor edits, to commit seq3 covering548–579, adding1GLM:122→123. Original seq1/2 and all raw rows, including faileduser584, remained unchanged. The new segment retained1002/MH-WD100, historical/simulation labels and59900分. This proves this bounded recovery, not arbitrary future summary fidelity or a fresh21-run.

One approved original-question page in the same conversation70 then added2GLM:123→125. Actual understanding returned `{"query":"最开始那个订单1001（智能猫砂盆Max，MH-LP200）后来物流怎么说？我当时的诉求是什么？"}`. Actual classification returned `{"intent":"其他","confidence":0.6}`. HTTP200/done produced the fixed clarification and **no current query_order/query_logistics call**. Actualhistory_ctx and wire contained originalseq1; snapshot selected1/2/3 with no omissions; S=L579 and SQL/checkpoint equality were restored. Originaluser584 and original attempt files were preserved. Thus reference recovery and summary consumption passed, but the required current1001read and original-request answer did not. The semantic gate failed and all further calls stopped; no classifier fix, third candidate, capacity increase, extraquestion, conditionalrestart/continuation or new21batch.

Evidence under `runtime/context-evidence/ch07-demo-21-20261017/extra-minimum-validation-v4/`: `source-contrasts/result.json`, `startup-recovery/manifest.json`, `original-final/result.json`, `original-final/targeted-inspection.json`, original wire responses, SQL and screenshots. Source/version/hashes/session/offsets and increments versus cumulative totals are separate. R1 cost6GLM; including v3 cost1, the human-approved extra scope used7 of its original32GLM available. Final demo125/16/16 leaves25/34/9; all runs total297/36/36 (small46/2/2, default126/18/18). Every failed/background request counted; SDK retries0, distinct normal productionnotify jobs counted separately.

The same scoped reviewer inspected the actual evidence without another source scan or test/provider call: bounded actual SUMMARY gate PASS, startup PASS, E2E FAIL. Source approval remains valid, but Task11 and full step acceptance are unfinished. The original demo remains20/21 with its422 preserved; later single-page done does not rewrite that result or imply full21 on R1. The default21+separatecontinuation and2720/184 full belong to producta82; R1 has192 focusedpassed34.74s. Current H59880/2691 and derived fees1135879/174823 remain unchanged. See the [step acceptance record](2026-10-17-context-management-acceptance.md) for all prior failures and parked limitations.
