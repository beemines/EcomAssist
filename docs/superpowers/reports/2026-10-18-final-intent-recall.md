# Chapter7 final intent-recall prompt repair

Status: source candidate and human gold prepared; bounded offline checks passed. Real acceptance remains **HOLD**. This continues approved Task11 and does not claim chapter completion.

## Scope and source identity

Worktree: `D:/shixi/ecommerce-customer-service/.worktrees/context-management`, branch `feat/context-management`; base `bed1ca0d9ece2c734646dfeacb172b8d3fd7bf50`. The only production edit is `INTENT_SYSTEM` in `app/workflow/prompts.py`. Candidate prompt SHA256: `64c61897d3aa44e02b11ace5c33a06e15b8e723341fc9853c70074eda345f1bd`; source file SHA256: `4f4bf181317258555937d4feb2a285ffde76ae7eb7c48163ae661b850a5ee86a`.

No model/schema, threshold0.70, retries0, tool permissions, understanding, summary producer, attachment ordering, capacity setting, dependency or API change. No merge or push. The controller's pre-existing authorized dev-notes stage entry is preserved and included with the completed-stage append. This public report is committed; the same report is copied to ignored `.superpowers/sdd/2026-10-17-context-management/final-intent-recall-report.md` for local review references, without force-adding scratch.

## Demonstrated failure and narrow hypothesis

Read all four preserved files under `runtime/context-evidence/ch07-demo-21-20261017/extra-minimum-validation-v4/original-final/`: `targeted-inspection.json`, `physical-packets.jsonl`, `nonstream-replies.jsonl`, `context-events.json`. The exact classification request is physical index3, prior measured source HEAD `1916cbb4775515162582a260115e9a9b3d8977c5`. Its eight wire messages match the saved classification `model_ctx` message-for-message; the pre-edit prompt also equals the captured system exactly. The packet contains the historical native FAQ request/result, its assistant answer, the saved repeated current-user row, the current original question, and the final context_data attachment. No packet repair is made here.

Original: `最开始那个订单后来怎么说？我当时的诉求是什么？`

Attached resolved question: `最开始那个订单1001（智能猫砂盆Max，MH-LP200）后来物流怎么说？我当时的诉求是什么？`

Summary seq1 explicitly identifies the original1001/MH-LP200 logistics request, the user's missing package, and refusal to apply for refund. Seq2 and3 are also present; omitted is empty. The actual model returned `{"intent":"其他","confidence":0.6}` with normal stop and no tool calls. The nonstream capture, physical response and targeted-inspection agree. HTTP200/done ended in the fixed OTHER clarification, with no current1001 business read; semantic_gate is false.

`nodes.classify_intent` correctly forwards the untouched raw question plus the resolved attachment on the shared snapshot. `intent_packet` correctly composes that packet, and `IntentClassifier.classify` correctly retains the raw label and applies the unchanged0.70 threshold. This is a semantic classification failure after successful transport/history/JSON handling, rather than evidence that a summary was missing. The prior prompt limits history to referent identity, says it is not the current request, and frames classification as the current handling action. That combination can leave a mixed business follow-up plus historical-request recall outside its stated business categories even when the business topic is supported. This is a prompt-boundary hypothesis from observed input/output, not access to model reasoning.

## Minimal producer diff

Replace only the initial history-boundary sentence, preserving the existing current-direction/negation clause, and add one sentence:

```diff
-历史与context_data摘要只帮助确认指代对象，不是当前诉求。
+历史与context_data摘要帮助确认本轮指代对象和有据可查的业务主题，不把历史办理动作当成本轮新申请。
+本轮追问已可靠消解的业务主题，并同时回忆当时诉求或处理情况，仍按该业务意图分类；“最开始、后来、当时”等历史限定不单独构成意图，不因附带回忆问句就归其他。
```

Current explicit action and negation still override old history; the existing complaint-priority rule remains. The change does not route on phrases/order IDs, output slots, force confidence, coerce OTHER, or add a second call. Genuine unrecognizable requests still use OTHER. Missing/ambiguous order identity alone is not an unrecognizable business action: an explicit refund request still receives the refund label and later object clarification.

## Six-case human gold, distinct from model outputs

Ignored artifact: `runtime/context-evidence/final-intent-recall-20261018/annotated-cases.json`, SHA256 `9beaacc55545a80b9a79cea59877253f3496c5502b09366df22855d64fbadd69`. Its `saved_negative` preserves the exact old request/response, source HEAD, physical session/index, snapshot ID and source-file hashes. Each case preserves exact raw/resolved input, history, summaries, complete candidate wire messages, expected label/route and annotation rationale. All `actual_candidate_output` fields are null: these are human gold, not candidate outputs.

| Case | Expected intent | Annotation boundary |
| --- | --- | --- |
| original-mixed-logistics-request-recall | 物流 | Original captured packet, only system changed |
| logistics-recall-paraphrase | 物流 | No current order ID; supported earliest-order logistics referent |
| current-refund-overrides-logistics-history | 退款退货 | Explicit new refund direction wins over previous logistics/no-refund |
| current-complaint-priority | 投诉 | Explicit current complaint retains priority |
| ambiguous-object-clear-refund | 退款退货 | Two orders remain ambiguous; later selector clarifies, no guessed identity |
| unintelligible-other | 其他 | No identifiable current business request |

The original case retains its complete exact captured input including its repeated current-user row. Other cases are explicitly human-authored contrasts using saved summaries; the ambiguous-object case supplies two contemporaneous candidate orders and leaves `它能退吗？` unresolved. The classifier still emits exactly intent/confidence, never identity fields. Acceptance owner may run at most6 candidate classification calls, one per case, preserving actual results separately; no additional baseline call is needed because the saved failure is already a real negative.

## Offline evidence and actual factory arithmetic

Commands run from this worktree with PowerShell loginfalse and `PYTHONUTF8=1`, `PYTHONUNBUFFERED=1`, `PYTHONPATH=(Get-Location).Path`:

```text
.venv/Scripts/python.exe .cache/final-intent-recall-check.py
.venv/Scripts/python.exe -m pytest tests/test_intent_contract.py tests/test_intent_routing_evaluation.py tests/test_context_prefix.py tests/test_context_budget.py tests/test_context_understanding_role.py tests/test_context_workflow.py tests/test_context_long_conversation.py -q
```

The ignored annotation/factory script ran before the source edit (exit0, `.cache/final-intent-recall-baseline-annotations.txt`) and after it (exit0, `.cache/final-intent-recall-annotations.txt`). It verifies physical/nonstream/event agreement, exact captured prompt/input, six-case artifact construction and the actual `profile_budget` factory with the production registry. It does not invoke any model, server or application database. No new wording-mirroring unit test was added.

Pytest result: **exit0, 230 passed in20.84s** from the single functioning launcher run (session74038). Output: `.cache/final-intent-recall-focused.txt`. The selected long-conversation tests use temporary offline SQLite resources and controlled provider outputs; they do not access the application database or establish live model quality. No broad full-suite rerun was requested or executed.

Fresh factory details are saved to ignored `runtime/context-evidence/final-intent-recall-20261018/factory-and-prefix.json`, SHA256 `1243ec9ddab156e46e4f91e5954f3257105523ab0c3df97451c636bcad9cc7d6`.

| Factory profile | H | Layer1 | Layer2 | Classification F old→candidate | Derived turn fee old→candidate |
| --- | ---: | ---: | ---: | ---: | ---: |
| default128000 | 59880 | 41916 | 17964 | 1159→1305 | 1135879→1136025 |
| demo18000 | 2691 | 1883 | 808 | 1159→1305 | 174823→174969 |

The same heuristic estimator `cjk-ascii-protocol-v1` charges the added prompt146 units. Classification A becomes114669/default and9406/demo; neither is the binding H limit. Default H remains the fixture desired59880; demo H remains decision A2691 (decision F2890 unchanged). The derived cumulative capacity grows146 because the factory reserves one classification call. No configured capacity was modified to make this fit. The exact saved classification packet estimate3421 becomes3567; with unchanged output2048 and demo safety540 it totals6155, below18000. These are conservative estimator units, not claimed provider-token measurements or actual usage.

## Failed attempts and limits

Initial shell reads loaded a user PowerShell profile with an unrelated unavailable conda hook; subsequent commands use loginfalse. Several exploratory `rg` probes guessed nonexistent factory paths/Windows globs and returned path errors before the actual `app/workflow/context_budget.py` and `app/context/acceptance.py` factories were located. One PowerShell response-shape probe assumed request.body on response rows and emitted null-array indexing errors; corrected inspection used top-level response choices. A process diagnostic could not access CIM resources. None modified source/evidence or invoked a service.

The first sandboxed pytest launcher stalled with an empty output file and no test/assertion output. The owned session62565 was terminated by Ctrl-C and confirmed exit1. This is a launcher failure, not RED/test evidence. Following the controller's explicit direction and the previously used narrow virtualenv-launcher workaround, the exact seven-module command was restarted once with require_escalated; no interpreter replacement, install or expanded suite. It completed exit0 with230 passed in20.84s. There was only one source candidate and no failed assertion or model retry to conceal.

Implementer real API/browser/application-DB/restart/business-submission calls: **zero**. No subagents. Existing services and other worktrees remain untouched. Old original20/21 capacity failure, v3 summary failure and R1 classifier failure remain preserved in their original artifacts. Demo physical ledger remains125GLM/16embedding/16rerank against150/50/25, remaining25/34/9; total prior297/36/36. Balance is not permission for extra calls.

After explicit source/documentation commit: **HOLD** for the controller-owned single scoped independent review and bounded acceptance. Offline checks prove contracts, packet handling and arithmetic; they do not demonstrate that the new prompt fixes live classification or that Chapter7 acceptance has passed. The acceptance owner retains any approved original-history browser/restart continuation, bounded by the same original cap and stop conditions.
