# Chapter7 final intent-recall prompt repair

Current status (Task11 R2): R1 classification passed6/6 actual gold calls, while the original-history page failed after understanding copied an unresolved positional referent. R2 is a minimal understanding-prompt clarification, offline-verified215 checks, **HOLD** for one scoped review and bounded real acceptance. Earlier sections preserve the prior candidates' history; R2 below is the current handoff. This does not claim chapter completion.

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

## R1 — restore understanding-to-classification input sequencing

R1 base: `ccf32fc1c08d2f1a8bacf50e358f17a6783a315d`. This is a concrete integration repair, not another prompt candidate. `INTENT_SYSTEM` remains exactly the ccf32fc version: prompt SHA256 `64c61897d3aa44e02b11ace5c33a06e15b8e723341fc9853c70074eda345f1bd`, prompt source file SHA256 `4f4bf181317258555937d4feb2a285ffde76ae7eb7c48163ae661b850a5ee86a`.

### Actual first-candidate failure and observed input regression

The acceptance owner called only the first gold case onccf32fc. Saved evidence: `runtime/context-evidence/ch07-demo-21-20261017/final-intent-recall-v1/classifier-cases/{result.json,physical-packets.jsonl,nonstream-replies.jsonl}`. Result SHA256: `8b2d8bbde3abdc5d8124ae367e42d38b724ec6af03f3121015ff6e5e734f24a5`. It returned strict valid normal-stop JSON with effective/raw intent其他 and confidence0.95, so the first-case gate failed and the remaining five cases/browser steps were not called. This consumed1GLM: demo125→126, embedding/rerank16/16 unchanged. The earlier prompt hypothesis was insufficient; offline contract checks had not established model semantics.

Read-only comparison with `git show 87d5035:app/workflow/nodes.py` confirms Chapter6 passed `state['resolved_question']` directly to `classifier.classify`. Chapter7's snapshot branch passed raw to the service and `intent_packet` placed raw in the current user message, with the normalized question only inside the final attachment. The raw service argument is still needed for its social fast path; the actual model projection had lost the direct resolved current input. This observable sequencing regression and the new serialized-payload RED motivate R1. They do not expose why the provider chose OTHER internally or establish that R1 must pass live.

### One-line production change and explicit design amendment

```diff
 def intent_packet(raw_question, snapshot, *, resolved_question=None, output_tokens=2048):
     return compose_call(snapshot, system=SystemMessage(INTENT_SYSTEM),
-        current=HumanMessage(raw_question, id=snapshot.user_message_id),
+        current=HumanMessage(resolved_question or raw_question, id=snapshot.user_message_id),
         attachment={'resolved_question': resolved_question or raw_question}, pending=(), tools=(),
         output_tokens=output_tokens)
```

Candidate `app/workflow/intent.py` SHA256: `d11aeb445dd85eb659231a1d55b8b554d839e2d391a85f87160d5364b6f416ba`. Both node preview and actual classifier use this same packet builder. The node and service retain the raw argument for social/audit handling; only the current message content presented to the classification model changes. The same SQL user ID, all frozen history, existing resolved attachment and schema remain. No additional raw message, system, call, threshold change, forced route/confidence, cap/step/model change or understanding rewrite. Previously captured historical raw rows are preserved. Upstream understanding remains authoritative and must retain current negation/direction; ambiguity stays unresolved rather than becoming an invented order.

Design§6 now explicitly amends the earlier raw-current choice: understanding consumes raw; classification consumes resolved with raw fallback and the same user-message identity; stored State/SQL/checkpoint originals remain raw. This records the decision change rather than pretending the earlier specification had always required the new projection.

### Meaningful TDD and bounded GREEN

New committed module: `tests/test_context_intent_resolved.py`. It exercises the actual node, actual budget reservations, actual classifier/strict JSON and actual SDK serialization, replacing only external HTTP with `httpx.MockTransport`. The model-stage wrapper records preview and delegates to the real stage. The independently specified normalized current text makes a raw-current regression fail. Assertions cover current SQL ID, full historical native tool pair, exact attachment, preview/send equality, no new raw duplicate, unchanged original State and serialized snapshot, explicit current negation, ambiguous-object passthrough, absent-resolved fallback, and the raw social zero-call fast path. Controlled intent replies prove plumbing, not model quality.

Before editing production source:

```text
.venv/Scripts/python.exe -m pytest tests/test_context_intent_resolved.py -q
```

**RED: exit1, 2 failed / 3 passed in5.68s**, `.cache/final-intent-recall-r1-red.txt`. Both failures are the expected actual wire `messages[-2].content` mismatch (raw instead of resolved), not import/setup/launcher failures. Ambiguous raw==resolved, fallback and raw social controls passed. The SDK emitted a captured local sync-transport/proxy configuration warning on the failing test; HTTP used the explicit asynchronous MockTransport, with no real network.

After the one-line production edit, one functioning bounded run:

```text
.venv/Scripts/python.exe -m pytest tests/test_intent_contract.py tests/test_intent_routing_evaluation.py tests/test_context_prefix.py tests/test_context_budget.py tests/test_context_understanding_role.py tests/test_context_workflow.py tests/test_context_long_conversation.py tests/test_context_intent_resolved.py -q
```

**GREEN: exit0, 235 passed in14.12s**, `.cache/final-intent-recall-r1-focused.txt`, session13640. Both RED and GREEN used the existing narrow require_escalated virtualenv-launcher workaround from the first attempt, PowerShell loginfalse and the same UTF8/unbuffered/worktree-PYTHONPATH environment as above. No sandbox stall, second GREEN, full-suite rerun or new wording-mirroring test. The existing long-conversation module uses controlled providers and temporary SQLite, not the application database. `git diff --check` is clean aside from Git's existing line-ending notices.

### Separate R1 gold and unchanged actual factories

New ignored gold: `runtime/context-evidence/final-intent-recall-20261018/annotated-cases-r1.json`, SHA256 `94766daa298960bb5f545c07a22ca04b224f09faff798f923b50236eede5a960`. The original `annotated-cases.json` remains byte-for-byte SHA9beaacc55545a80b9a79cea59877253f3496c5502b09366df22855d64fbadd69; the old actual failure result and saved storage snapshot are also hash-checked unchanged. No old negative or gold is overwritten.

The ignored `.cache/final-intent-recall-r1-check.py` ran once, **exit0**, log `.cache/final-intent-recall-r1-annotations.txt`. It restores the original saved checkpoint snapshot against the actual demo factory and constructs every candidate through production `intent_packet`, then the pinned SDK serialization. Human contrasts get honestly rebuilt snapshots from their recorded histories and the same saved summary segments. Every case includes `serialized_snapshot`, `raw_question`, `resolved_question`, exact `candidate_messages`, stable current ID585, prefix/snapshot identity, estimated input, and explicit `input_difference_from_v1_gold`; expected intent/route/identity labels are unchanged and all R1 `actual_candidate_output` values remain null. The prior candidate's real failure is stored separately.

Original case: exactly eight messages, only current index6 changes raw→the saved resolved1001/MH-LP200 logistics question. The paraphrase changes only current index5. Other four packets are byte-equivalent as message objects to v1 because their raw/resolved are equal, including the ambiguous refund case. System, history and attachment equality are asserted in every case; no new raw duplicate is introduced and no historical raw row is deleted. This directly supports acceptance via the real `IntentClassifier.classify(raw, snapshot, resolved_question=...)` seam instead of a build_messages fixture adapter.

New ignored factory artifact: `runtime/context-evidence/final-intent-recall-20261018/factory-and-prefix-r1.json`, SHA256 `c66ef842ccda152878abedb7d27774cfd8320a6f6b09f4f460cc47b65b71542f`. Actual default/demo factory structures equal the prior ccf artifact: H59880/2691, layer1 41916/1883, layer2 17964/808, classification F1305, derived cumulative fees1136025/174969. The normalized current makes the exact original input estimate3567→3587 (+20); adding unchanged output2048 and demo safety540 gives6175<18000. Fixed prefix and capacities are unchanged; the dynamic projection increase is counted by the actual packet estimator, without changing capacity to fit.

### R1 boundaries and handoff

No failed implementation or annotation attempts in R1. An initial evidence read omitted the enclosing `ch07-demo-21-20261017` directory and returned a missing-path error; `rg --files --no-ignore` located the actual result before analysis. A read-only filename/glob probe also hit missing paths; subsequent reads used exact files. Neither was a test failure or external action. The meaningful2-test RED, earlier launcher issue, first-candidate actual OTHER0.95, original20/21 capacity failure, v3 summary failure and prior summary-R1 classifier OTHER0.6 all remain disclosed separately.

R1 implementer real API/browser/application-DB/restart/business-submission calls: **zero**; no agents. Current physical demo allowance is126GLM/16embedding/16rerank, hard150/50/25, remaining24/34/9, prior total298/36/36. The controller's preceding dev-notes entry describing the actual first-candidate failure is preserved with the completed R1 four-field entry. Only explicit code/test/design/report/dev-notes files are committed; ignored gold, scripts, logs and same-stem scratch report are not force-added. No merge/push. **HOLD** for one scoped R1 review and the acceptance owner's bounded actual checks; no chapter-completion claim.

## R2 — distinguish grammatical completeness from resolved order identity

R2 base/source freeze: `55b28c100e3772e26ecb9cd173a132bcc913fb8c`. This continues the same Task11. Only two existing `UNDERSTANDING_SYSTEM` lines change in `app/workflow/prompts.py`; no classifier rework, deterministic rewrite, order pinning, source side channel or new API. Candidate understanding-prompt SHA256: `9b2be584b35eb05efe79aa27fb201279d3c2b46bee06b381d3f70aacde7bc80c`; prompt source-file SHA256: `3a3863f0ff55ec99d24ff44baf66a90c5f377930b6fb05c8092d6ba1f76abfd7`. `INTENT_SYSTEM` SHA remains64c61897d3aa44e02b11ace5c33a06e15b8e723341fc9853c70074eda345f1bd, and the R1 normalized-current packet fix remains unchanged.

### R1 actual classification success, then a separate page failure

Read actual `runtime/context-evidence/ch07-demo-21-20261017/final-intent-recall-r1/classifier-cases/result.json`: all6 cases passed on frozen55b28c, each once through `IntentClassifier.classify(raw, snapshot, resolved_question=...)`. This cost6GLM, demo126→132, embedding/rerank16/16. The original and logistics paraphrase returned物流0.94/0.96; explicit refund and complaint returned their requested intents0.97/0.97; ambiguous refund stayed退款退货0.9 and unintelligible input stayed其他0.95. This gate is separate from E2E acceptance.

Read all saved `final-intent-recall-r1/original-final/{targeted-inspection.json,result.json,physical-packets.jsonl,nonstream-replies.jsonl,context-events.json}`. User587 asked the exact original question `最开始那个订单后来怎么说？我当时的诉求是什么？`. Actual understanding physical index1 returned that raw question unchanged, with strict valid query JSON/normal stop, despite selected seq1/2/3 and omitted[]. Classification consumed that actual result, correctly preserving the R1 integration contract, and returned物流0.85. The decision selected clarification; there was no current business tool call; the final page emitted `invalid_answer` and did not complete. Four physical GLM requests cost132→136. The rejected final stream text was **not captured**; no exact wording or precise content violation is inferred from the final error. No conditional continuation/restart followed.

The actual ten-message understanding request equals the saved `model_ctx` message-for-message. Its seq1 establishes conversation order: user first queried1001/MH-LP200 logistics and declined refund, then queried1002. Although1002's delivery date is earlier, delivery chronology does not define the first-mentioned order. `QueryUnderstanding.resolve` validates the raw provider query and applies only the narrow dropped-greeting restoration; it does not coerce this output back to raw. Entity validation accepts an unchanged unresolved question, so structural/provenance guards alone cannot demonstrate successful semantic resolution.

### Minimal priority clarification and testable hypothesis

The previous instruction “already complete and explicit questions must be copied” can conflict with the earliest-referent rule if grammatical completeness is treated as explicit identity. That is an observable prompt-priority hypothesis, not a statement of model-internal cause. R2 changes the earlier copying definition itself, then tightens the existing chronology paragraph rather than appending redundant end-of-prompt examples:

- Copying requires explicit object identity, not grammar alone. Positional references such as “最开始那个订单/最早那单” first require source-supported unique resolution.
- For “the first order discussed”, use this conversation's mention/query sequence, never delivery dates, numeric order IDs or recency. An explicitly ordered first segment may resolve the earlier order; an unordered multi-order list may not.
- Fill only the referent and supported business topic, retaining every requested question without answering history or inventing a handling action. Explicit current order, direction and negation remain authoritative under the unchanged existing rules.
- A first visible summary seq greater than1 does not establish the conversation's beginning. Missing beginning or unclear chronology preserves ambiguity and must not select a later/recent order.

No application-specific1001 rule or new example was added. The original strict query-only JSON,20000-character/output-budget bound, history/tool-role boundaries, provenance checks, negative/repair/refund distinctions, summary content, SQL originals, checkpoint/history storage, attachment shape, model, retries0, classifier threshold0.70 and capacity rules remain unchanged. The next two actual calls can falsify this hypothesis by checking resolution with intact source and ambiguity without the first segment.

### Two separate human annotations through the production packet/provenance contract

Ignored new artifact: `runtime/context-evidence/final-understanding-recall-20261018/annotated-cases-r2.json`, SHA256 `04c7b40d5c64ba127ab8bd7f4b7be554b1328ca26fb10aa285e39bb8d41564bf`. Old classifier golds and actual outputs remain unchanged. The artifact records source-file hashes, exact saved negative/request/session, restorable `serialized_snapshot`, complete `snapshot_provenance` values (`from_msg_id/summary_seq/order_ids/texts`), exact candidate SDK wire messages, input differences and separately labelled human expectations/reference queries. Both candidate output fields are **null** until the acceptance owner saves actual outputs separately; references and evaluation labels are never put into the request.

1. `actual-587-earliest-order-supported`: actual saved snapshot/restored source rows, same selected seq1/2/3,22 production provenance entries, same current user ID587 and complete history. Its ten-message candidate differs from the actual request only at system index0. Human reference: `最开始那个订单1001（智能猫砂盆Max，MH-LP200）后来物流怎么说？我当时的诉求是什么？`. The local acceptance criteria require supported1001/logistics and both questions without a historical answer or invented handling action; equivalent faithful wording need not match that reference byte-for-byte.
2. `human-contrast-first-summary-omitted`: an explicitly artificial omission contrast, not an actual saved request. It removes only seq1, marks the restorable snapshot's omitted metadata[1], uses17 rebuilt production provenance entries, and gives the snapshot the labelled identity `human-r2-first-summary-omitted`. History, current question and remaining segments are unchanged. Candidate differences are system index0 and final attachment index9. The actual wire has only the existing `kind/summaries/data` fields, `data={}`, and visible seq2/3; it does **not** add an omitted list, a hint field or an expected answer. The model must preserve ambiguity from incomplete visible source chronology. The human reference is the unchanged raw question;1001 or1002 may not be invented as the earliest order.

The ignored script `.cache/final-understanding-recall-r2-check.py` calls actual `understanding_packet`, restores the saved snapshot and uses production `snapshot_provenance` against saved `MessageRecord` rows, without an application database. It verifies exact wire/event/nonstream agreement, human references passing the unchanged entity guard, and both1001/1002 guesses being rejected for the omitted-source contrast. It hash-checks the old golds, actual outputs and storage source unchanged. It ran once: **exit0**, `.cache/final-understanding-recall-r2-annotations.txt`. These are annotated contract checks, not generated candidate outputs or a model-quality pass.

### Fresh narrow coverage and source-bound prior full run

From this worktree, PowerShell loginfalse with UTF8/unbuffered/worktree-PYTHONPATH and the established narrow elevated virtualenv launcher from the first attempt:

```text
.venv/Scripts/python.exe .cache/final-understanding-recall-r2-check.py
.venv/Scripts/python.exe -m pytest tests/test_query_understanding.py tests/test_understanding_input_projection.py tests/test_context_understanding_role.py tests/test_context_prefix.py tests/test_context_budget.py tests/test_context_workflow.py tests/test_context_long_conversation.py -q
```

Focused command: **exit0, 215 passed in15.39s**, `.cache/final-understanding-recall-r2-focused.txt`, session19975. It ran once, with no new wording assertions or tests for this pure prompt revision. Controlled providers and temporary offline SQLite in existing tests are distinct from actual provider/application-DB calls.

Separately, the controller already completed the one final full `.venv/Scripts/python.exe -m pytest -q` on **frozen55b28c**, source unchanged during that run: **exit0, 2725 passed / 184 skipped in417.96s**, `.cache/ch07-final-full-20261018.txt`. Its output tail was read. That full result belongs to55b28c, not the later R2 prompt. R2 did not repeat the full suite.

### Actual factory arithmetic and remaining boundary

Fresh ignored `runtime/context-evidence/final-understanding-recall-20261018/factory-and-prefix-r2.json`, SHA256 `4e5e7ef24ab415872b9281f4ab94e30ed6c33deb98f6967ed13b43f4d86403c9`, contains both actual production-registry factories and the prior R1 comparison. Understanding F2303→2597 (+294 estimator units); default/demo H stay59880/2691, layer1 stay41916/1883 and layer2 stay17964/808. Derived cumulative fee caps1136025→1136319/default and174969→175263/demo reflect the changed one-call understanding prefix. No capacity setting was raised to fit.

The exact original understanding packet input estimate4634→4928, with unchanged output2048 and demo safety540 totals7516<18000. The omitted contrast input is4738. These use the unchanged heuristic `cjk-ascii-protocol-v1`, not claimed provider tokenizer measurements. Prefix cost, dynamic input and derived fee are kept distinct from actual usage and physical call allowance.

R2 has no failed implementation/annotation/test attempts, launcher stall, real provider retry or approval rejection to hide. All original20/21, v3, prior classifier failures and the R1 page failure remain preserved. Implementer API/browser/application-DB/restart/business-submission calls: **zero**, no agents. Demo remains136/16/16 against150/50/25, remaining14/34/9; aggregate prior308/36/36. After explicit source/report/dev-notes commit: **HOLD** for one scoped R2 review, then only the acceptance owner's already bounded two understanding calls, original page and conditional restart continuation within the same remaining14. No new broad batch, merge/push or chapter-completion claim.
