# 第六步执行裁决与代价

按原始计划账本顺序完整导出所有含 Ruling: 的行，共 
40
 项。保留原文、理由及判断错误时的代价；不改写历史失败。

计划：docs/superpowers/plans/2026-10-15-intent-routing.md；代码最终版本7398b27。原始计划账本及审查日志仍保留在本工作树 .superpowers/sdd/2026-10-15-intent-routing/。

## 1

- Ruling: native create_worktree returned “Not a git repository” for the enclosing D:/shixi chat root; target repo manual Git worktree fallback used after verified .worktrees ignored — native tool cannot target this nested repo — cost if wrong: unmanaged but recoverable worktree attachment only.

## 2

- Ruling: Git Bash helper failed NtCreateDirectoryObject 0xC0000022; equivalent PowerShell plan-scoped workspace/brief extraction performed, self-ignore and plan marker verified — preserve required artifact semantics without repeatedly launching denied MSYS — cost if wrong: helper formatting only, checked headings/counts.

## 3

| 2 | exact wire schema vs internal IntentResult, eight routes, 48=24+6x4, 16 holdout | Ruling: strict confidence is mandatory; update necessary existing workflow fakes/contract expectations, never permit old wire JSON as production compatibility — old tests encode replaced contract — cost: local test fixture changes |

## 4

| 8 | UI Vibe exception vs backend review, new events vs unchanged actions | Ruling: browser validation retained, task/front code-review ritual omitted per user's explicit exception — user overrides generic SDD gate — cost: visual and interaction defects caught by browser checks |

## 5

| 9 | fixed batches, default no calls, true denominators, evidence-only chat mode | Ruling: acceptance report created in Task8 is extended in Task9, not overwritten as newly created — same report ownership is sequential — cost if wrong: only document history |

## 6

- Baseline complete: initial full run 1853 passed/120 skipped/1 failed in496.28s. Failure test_default_uvicorn_visible_safe_audit: child script sys.path lacked app root. No code changes. Single rerun with PYTHONPATH=worktree passed1 in12.76s (baseline-audit-recheck.log). Ruling: environment propagation corrected; aggregate baseline green, don't rerun1853 passed cases solely for this environment-only fix — identical root already provided by pytest itself — cost if wrong: next full task suite exposes it.

## 7

- Task1 Ruling: the brief's Test: tests/test_business_tools.py is a test-run/coverage reference, not a mandatory Modify hunk. Scoped registry behavior is exercised in new test_demo_orders.py and existing business-tools suite passed; forcing a redundant edit would violate test hygiene. Accept consolidated placement, no product requirement removed — cost if wrong: reviewer discoverability, covered by report/test paths. Carry this ruling into scoped re-review.

## 8

- Ruling: for Tasks3/5/6: metadata filter remains validated state.category; OrderSnapshot.category informs policy applicability but cannot silently override the request filter and exclude global policy chunks — spec requires per-query consistency, not inferred filter injection — cost if wrong: somewhat broader policy candidates, still ranked/filtered under existing explicit choice. Carry task-5-context.md into integration dispatch.

## 9

- Ruling: Task2: new typed IntentResult requires adapting existing evals/evaluate_workflow.py live boundary if it expects a string; this necessary caller update is in scope despite original file list, but historical gold remains unchanged/labeled — avoid serialization/interface regression without regrading history — cost if wrong: minimal old CLI adapter, covered by existing evaluation tests.

## 10

- Ruling: for Task4/5: concrete state field retrieval_audit preserves spec's candidate provenance; otherwise graph schema drops undeclared output — fulfills approved audit requirement — cost if wrong: extra bounded JSON state only. Carry task-4-context.md.

## 11

- Ruling: for Task4/6: persist server-verified pause_checkpoint_id in selection receipt on resume, not before actual root exists; completed repeated select requests can compare original identities and replay final saved result without historical execution — fulfills spec idempotent replay — cost if wrong: one additional optional UUID state field; covered by native/HTTP tests. Carry task-4-context.md.

## 12

- Ruling: Task4/6: append runtime user_id:str|None=None, injected solely from ConversationRepository.get_user_id for both initial/resume preparation; selection errors if absent — provider requires trusted owner and existing Runtime lacks it — cost if wrong: one optional injection field; no client or generic State identity. Carry task-4/6-context.md.

## 13

- Ruling: Task5: allow minimal shared entities.py connector-tail extraction within order-anchor integration — existing no-guess/multiple-order requirement fails otherwise — cost if wrong: bounded regex parsing behavior; explicit regressions plus prior entity tests retained.

## 14

- Ruling: Task5: update shared route_intent and new chapter6 dataset expected_route metadata to after_sales for退款退货/售后; graph consumes one current map — old helper temporarily retained Task2 routing until integration, leaving it now would give Task9 false routes — cost if wrong: historical benchmark route mismatches, explicitly labeled historical, not regraded. Chapter5 gold/saved reports unchanged; new labels/split/questions untouched.

## 15

- Ruling: Task5 verification: replace helper-dependent compatibility assertion with direct legacy required-positional WorkflowRuntime construction and rerun selection plus affected integration/usage/intent-contract tests; no duplicate full suite for test-only correction — full run already exercised unchanged production code, later Task9 validates whole branch — cost if wrong: unrelated test-side interaction, covered by focused and later full run. Report original failure and corrected focus separately, never claim a nonexistent second full run.

## 16

- Ruling: Task6 active-time persistence: optional Runtime active_started_at and consumed baseline, set at service active preparation; prepare_selection saves baseline+active duration just before pure interrupt, final log may use same helper; no monotonic timestamp in State or aupdate_state on paused root — preserve native interrupt task metadata while excluding human wait — cost if wrong: small timing boundary drift; pause/resume deadline tests must cover. Private Task4 probes without runtime timing retain baseline.

## 17

- Ruling: Task6 durability guard scope: allow small shared raw-root completion helper and necessary existing workflow actions permission check extension — demonstrated pending-write projection must not mint refund/ticket permissions while valid old roots remain valid — cost if wrong: stricter handling of corrupt/incomplete roots; old completed action regression covers compatibility. Task7 must reuse actual immutable raw-root guard.

## 18

- Ruling: Task6 cancellation audit: minimal per-prepared synchronous Runtime audit sink/reference, optional and never checkpointed, receives whitelisted recorded aggregate/stage snapshots before cancellation exits node context; queued events may also arrive but don't double-add — demonstrated consumed paid-stage cost must survive consumer cancellation — cost if wrong: request audit attribution, covered deterministic cancel/normal failure/isolation probes.

## 19

- Ruling: Task6 verification: one necessary additional full default run after this production Runtime/node/service fix and focusedGREEN — actual cancellation gap found after first full, new cross-layer concern justifies final-code suite — cost if wrong: ~8min test time; no further unrelated broad repeats. First2045/120 result retained distinctly, no paid calls.

## 20

- Ruling: Task7 centralize inline six reason labels from workflow/service.py into pure app.refunds.types and reuse public projection — one fixed contract source avoids frontend/API/DB drift — cost if wrong: import-cycle/projection regression, covered startup/offer/API tests; no public envelope change or application migration.

## 21

- Ruling: Task7 small logging.py whitelist addition workflow_refund/submit_refund/request_no is within required safe post-commit audit — unknown values would otherwise be dropped — cost if wrong: audit projection regression, covering logging/action tests; no raw model/credentials logged.

## 22

- Ruling: Task7 add required read-only GET /api/conversations/{id}/refund-offer with strict assistant_message_id/checkpoint_id query and RefundActionService.offer, reuse shared original raw-root/SQL-owner/turn checks and exact public envelope — spec6 requires server revalidation after refresh, existing backend has no such endpoint; frontend cannot infer permission from DOM — cost if wrong: extra narrow read API surface, tested forged/stale/unfinished identities and write-guard separation. No general history or cross-session memory.

## 23

- Ruling: Task7 finish current full frozen, then new GET TDD+focused refund/action/guard+realMySQL regressions; no duplicate default full solely for this bounded read-only integration — affected contracts directly covered, finalTask9 full verifies aggregate before delivery — cost if wrong: untested unrelated router interaction until final full; report pre-GET full and post-GET focus separately, no false final-code full claim.

## 24

- Ruling: Task9 before any paid call, resolution scorer for dialogue-6-2 accepts uniquely sourced expectedmodelMH-WD100 OR antecedentorder1002, preserving action/negation/source and rejecting wrong IDs — annotation expected_query names model for generic warranty and spec rejects exact-string-only grading; requiring order literal would falsely fail correct resolution — cost if wrong: overpermissive metric, bounded source/entity negative regressions and independent final review required. Existing frozen full retains original code/result; final focused evaluator proves bounded repair, no second full solely evaluator-only scorer fix without new concern; production changes still require aggregate verification.

## 25

- Ruling: Task9 narrow understanding Prompt preservation clarification permitted, general rule/development examples preferred, no labels/model/budget/retry change; save original16, pointonly2failed and at most2blockeddependents after valid observed predecessor, never batchrepeat/gold. Gate32onlyafter repairedboundaryvalid, no repeated paidloop onfailure — user approved prompt validation/failed-case checks, spec complete-query preservation — cost if wrong: overfit/mixed-version evidence; retain hashes/denominators and never claim independent single-version16/48 score.

## 26

- Ruling: Task9 evaluator can reuse valid actuallyobserved histories across Promptversions when samplehash+modelmatch, explicit source_prompt_hash/provenance and rejection of failed/blocked/mismatched source, with RED/GREEN coverage — otherwise point recheck is incorrectly blocked solely by changing Prompt, contradicting bounded reuse requirement — cost if wrong: benchmark context contamination; no gold fields allowed and independent review inspects source. No secondfull solely Prompt/evaluatorrepair; finalfocus evaluator/understanding/intent/protocol, previous aggregate remains explicitly oldsnapshot.

## 27

- Ruling: Task9 chatlive fixed8 realbrowsergroups have explicit browser_scenarios/full_chain denominator8 and separate benchmark_full_chain16notexecuted; defaultdrychat remains16notexecuted/0calls — eightgroups don't correspond to16/32benchmarkIDs, invented mapping would misstate proof — cost if wrong: readers compare unlike denominators; label modes/source/versions and retain blocked/errors in8, actualSQL/rawroots verification nottrustflag. No duplicatepaid CLIchat.

## 28

- Ruling: Task9 minimal understandingguard may restore raw only when strict-valid modelquery equals literal rawsuffix after known leading socialgreeting+delimiter, no keyword/domain/semantic inference; capturedfailure+realresolution/change counterexamplesRED/GREEN, then single18onepoint<=2calls, nofurtherloop — explicit completequery unchangedcontract, general harmless cosmetic protection — cost if wrong: suppressing intendednormalization, prevented by exactsuffix restriction and counterexamples. Actualbrowser active freezescodeuntilterminal; finalproduct changed requires one aggregatefull after finalreviewwave decision, notanotherfullnow.

## 29

- Ruling: Task9 confirmed ownedNode112044 execFileSync hang fromdetachedserver inheritedstdio can terminateonlyverifiedownedNode and fixstdioignore;strictcasewhitelist/resume onlyunexecuted4–8 with originalsourceevidence, no rechargingcompleted1–3 — reversiblelocalinfra repair, waiting cannotclosepipe whileverified8003server49912alive — cost if wrong: lostin-progressbrowserstate/accounting; preserveSQL/SSE/logs and actualpausedroots, neverzero hiddenpaidpause.8002untouched.

## 30

- Ruling: Task9 actualcompletedoffer in conversation59/assistant240/root1f1c8aae-719b-61f9-800b-22df2f9c9e18 may be restored via actualstructurallocators+serverGET forformscenario — observedlegalpermission, avoids duplicatepaidchat; no fakepolicy/SQL — cost if wrong: evidencecrossscenarioambiguity, recordsourceidentities andactualGET.

## 31

- Ruling: Task9 blockingidempotence defect permits minimal repository equivalence for ONLY advisory finitepolicyfloat scores under actualMySQLJSON roundtrip; identity/reason/order/amount/status/decision/text/structure remainexact; strictsmallULP or justifieddeterministicnormalization, realMySQLsame-root/response-loss and negativebusiness/policydriftRED→GREEN — exactsameoffer must returnexistingreceipt, precisionartifactisnot changedsubmission — cost if wrong: overbroadcomparison acceptingchangedfacts; negativeboundaries+independentreview, neverrewriterow/disableguard.

## 32

- Ruling: Task9 correct1001 erroneous product_name台灯 to canonicalMH-LP200智能猫砂盆Max verifiedactualchunk109/repospec; preserveid/date/amount/model, matchinghistoryfixture factualnameonly ifconsistencyrequired, neverlabels/questions/split — Task1briefspec requiremodelnot台灯, samefactcontractmustmatchKB — cost if wrong: benchmarkversionchange; preserveoldsamplehash/reports, no posthocindependent48claim.

## 33

- Ruling: Task9 repaircasecannotrequireAgentnot_applicable ifearliergatelegitimatelyrefused; retain gateblockedfunctionalshortfall andactualqueries/scores, no thresholdlowering/bypass/invention — mandatedgateprecedesAgent — cost if wrong: maskingretrievalweakness, reportrefusal separately/notfullfunctionalpass. Thirdlogisticsinvalid_answer safe currenttoolguardstands; diagnosecapturedcontrol/Prompt andfixonlyactualintegrationdefect/instruction, notbroadretryfallback. Bundleofflinefixes, namedfailedpoints once, finalaggregateonceafterreviewwave.

## 34

- Ruling: Task9Step7 task-spec/quality gate and whole-branch backend review use ONE mostcapable independent reviewpass with separate explicitverdicts — finalTask9itself requires broadreview; duplicatedreviewerseats rereadthe same finalbackendandliveevidence without additional independence benefit — cost if wrong: broaderattentiondilutesTask9detail; supply exactTask9brief/report plus fullimmutablebackenddiff/globalconstraints/finalreviewfocus and require bothspecandqualityverdicts. Finalfixwaveonce+scopedrereview, noformalfrontendcodereview.

## 35

- Ruling: finalwave include M2/M3 alongside sixblockingfindings, deferM1because no newunsigned-shippeddefaultfixture/currentdemoimpact; explicitstatussupport required beforeexpandingprovider — focusedexistingstorage/evaluatorfilesalreadytouchedavoidduplicatetask; cost if wrong: hypotheticalfutureinjectedorderstillmisdescribed, documentedandnoproductreadinessclaim. Repairqualityremainsactuallegitimategateblockedlimitation pendingdisposition, cannotpaintPASS.

## 36

- Ruling: FinalI2 approved Agent-internal requiredcurrentread for validatedbusinessintent物流/订单 + exactlyone trusted currentorder, when legalcontrol attempts finalizationwithoutmatchingcurrentread. Synthesizecanonicalexistingquery tool via normaltool_node/accounting/SQLpairs, keepmodelselectedvalidtools and max4/max_decisions/budgets. Toolmatchname+target+pairedsuccess; failedmatchingattemptrejects/noretry, missing/ambiguoususerinfo legitimateclarification. Successful completecurrentread may factualanswer verifiedresult/followup, no inventedcompleteness — userrequiresAgentcurrentbusinessread; oldPromptaloneallowed factualhistorywithoutobservation, insideAgentconstraintpreservesouterrouting/oldtools — cost if wrong: over-constrainingbroadorderintent, coveractualmissinginfo/switch/pronoun/failedtool and preservemodeltoolpath. No SDK/networkretry or newdecisionloop. Finalusage reservebeforeboundary/finallysyncsnapshot/no customevent, concreteactualreplacement/cancelisolationtests required.

## 37

- Ruling: newhelper mustrefuse legacy8003withoutownerJSON; one manualstop of knownTask9PID47276 may precede firstnewhelperstart onlyafteroffline/frozen gates and revalidation exactCreationDate/featurecommand/knownstartlogPID — existingservicewasexplicitlylaunchedbythisTask9, cannotauto-adoptarbitraryport justtomigratemetadata — cost if wrong: terminatingunrelatedservice; samecreationidentity+command+trustedlogrequired,8002neverstop. I2missinginfo coverage includesexplicitunselectedorder evenuniquehistoricalorder, no guessingunderrequired-readpolicy.

## 38

- Ruling: makeone-line aggregate-receivedchunkbeforedeadlinecheck pluspermanentzero-delta/actualreplacementregression; newdemonstratedproductionedge warrants ONE necessary final-sourcefullafterfocusedGREEN, preserve2148/143pre-lastfix andneverclaimitfinalsource — actualusageavailablemustreplaceestimateevenonboundary, noSDK/model/guardchange — cost if wrong: ~6minextraverification; avoidsfalsefinalclaim, noMySQLrepeatforstream-onlyreorder. Exactnamedcid58livecommand approved onlyafternewfullGREEN+ownedidentityrestart, singleturn/no prefix/refundPOST/othercases, oldmodel/budgets0retry. No furtherbatches/paidloops.

## 39

- Ruling: perform ONE bounded extra OFFLINE-ONLY scorer closure despite skill one-final-wave cap, transparentlyrecordedexception — currentuserauthorized completeimplementation/evaluation and higher-priorityautonomy requires finishingroutinealreadyauthorizedfixes ratherthanparkingknownfalsepasses oraskingpermissiononlybecause localguideline cap; no modelcalls, runtimecode/helper/server/data/model/threshold changes — cost if wrong: additionallocaltest/reviewtime andover-restrictivemetric. Restricttofixed-casewhole-querysemantics/aliases, not growingblacklist; negativepolarity/time/prefix/suffix tests plus observedvalidoutputs, append-onlyoffline reassess, focusedtests+ONEcurrent-sourcefull, oneI4-onlyreview. No broader secondimplementationwave orpaidtrial. Originalfailures/denominatorsretained.

## 40

- Ruling: close implementation tasks and hand over the reviewable feature branch while explicitly retaining repair useful-answer failure and mixed-version quality limitations, rather than lowering the calibrated gate or claiming full acceptance — chapter6 deterministic orchestration and guards are verified; further retrieval quality tuning has no uniquely demonstrated fix within this bounded validation scope — cost if wrong: users can still receive a refusal for a supported repair question; top acceptance summary and final response disclose this, no production-ready or independent48/8 all-pass claim, no merge/push without integration choice. M1 unsigned in-transit support remains deferred before adding such fixtures.

