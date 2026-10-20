# SDD ledger — plan: docs/superpowers/plans/2026-10-19-observability-flywheel.md

Original Task 1–10: complete at 0bd2a8c; original ledger and test logs archived under runtime/ch09-evidence/superpowers-execution-archive. Do not reimplement.

Continuation authorization: 2026-10-20 user “按照验收标准继续完成” after reviewing docs/ch09-reference-gap-analysis.md. Continue approved Native execution in the existing isolated worktree; Task11–17 are acceptance corrections.

Ruling: Reuse the approved design, amended original plan and Native execution for acceptance corrections — user explicitly approved the written gap baseline and continuing — cost if wrong: scope interpretation differs; all changes stay reviewable in the isolated branch.

Ruling: Use PowerShell-native brief and ledger bookkeeping after invoking sdd-workspace failed with MSYS NtCreateDirectoryObject access denial — no permission weakening or alternate shell deletion — cost if wrong: helper-generated formatting may differ, task identities and BASE remain explicit.

Pre-flight: 11→17 effective reasoning enters config fingerprint; changed runs must not compare as identical to old null-effort runs.
Pre-flight: 12→15→16 versioned confidence reports distinguish old v1 and new algorithm; labels never enter online features; no arbitrary report path API.
Pre-flight: 13→15→16 CNY provider tariff and Langfuse USD costs remain separate; missing usage/cost not zero.
Pre-flight: 14→16 draft prefill remains explicit human confirmation, rejected matching preserves state and turn idempotency.

Task 11: in_progress; BASE 0bd2a8c. Brief: appended Task11 in original plan. Inspect actual failures, RED request effort propagation and config identity, then minimally fix without changing model/window/output budgets/retries. Target tests: tests/test_eval_pipeline_resources.py tests/test_eval_pipeline_runner.py tests/test_rag_judgment.py.

Task 11: verification 47 passed in 14.30s, command .venv/Scripts/python.exe -m pytest tests/test_eval_pipeline_resources.py tests/test_eval_pipeline_runner.py tests/test_rag_judgment.py tests/test_eval_pipeline_metrics.py -q --basetemp=runtime/ch09-evidence/pytest-task11-final. Observed RED: missing online effort/fingerprint (2 failures), incomplete answer generic error (1 failure), missing safe diagnostics. Real paid verification pending.

Task 11: complete (commits 0bd2a8c..c383a04; targeted tests 47 passed; actual quality verification remains Task17).
Task 12: BASE c383a04; brief read from amended plan. RED missing modules, then concrete question wiring failure, then order-number anchor failure. GREEN 22 passed in 3.93s. Local frozen data recompute succeeded: calibration false_allow0/false_refusal3; heldout false_allow4/false_refusal9. External calls0. Online v1 remains active pending release validation.
Ruling: Keep the first v2 held-out result unchanged and disclose its four false allows — further fitting against this heldout would invalidate validation — cost if wrong: the zero-heldout-false-allow target remains unmet and needs fresh evidence or a separately approved policy change.
Task 12: implementation complete; remaining release-quality item carried to Task17.
Task 13: in_progress. Brief in amended plan: root IO/tags, provider tariff with explicit currency/version, de-duplicated costs and summary counters; TDD against real SDK exporter and pure aggregates.

Task 13: complete (ef73b2c..b67648a; targeted suite42 passed10.25s). Real SDK exporter validates cost_details USD plus CNY tariff metadata. Official price and ECB dated rate retained; actual paid probe pending.
Ruling: Show standard tariff estimates with date/source and keep native USD separate from CNY — provider invoices are not available and Langfuse cost_details uses USD — cost if wrong: estimates differ from account discounts; UI must state tariff estimate.
Task 14: complete; BASE b67648a; RED3 missing candidate/history behaviors, GREEN25 passed10.27s incl real3308 owned schema; no historical user data processed.
Task 15: in_progress; read amended plan brief. Fixed-path calibration read/recompute, same-config and valid-denominator-aware comparisons, standalone routes and observable active progress; existing write guards remain.

Task 15: complete; BASE8e4e8a2; 3RED then19passed9.32s. Same configuration but errors/changed denominator => no false stable delta. Calibration rederive uses no external providers. Task16 frontend Vibe begins after this commit.

Task16: frontend implementation and browser readback complete; Node syntax passes. Task17 live proof in_progress. ROOT source_kind and correct refusal key targeted39 passed13.53s. Task11 realE46 judge probe stop/477output/2268total; cumulative191/356/344. Task12 active v2 threshold0.280 derived onlycalibration; heldout4falseallow/9falserefusal disclosed.
Ruling: Prefer verified v2 artifact for demo while retaining v1 — requested four signals and zero-calibration-falseallow objective, heldout risk shown explicitly — cost if wrong: v2 heldout false refusal increases; no claim of quality acceptance.
Ruling: User declined budget expansion, retaining280/450/450 and20-case scope — cannot guarantee two additional full20s within89GLM — finish owned page proof and bounded corrected evaluation, preserve all old failures, no counter reset.
Task17 diagnostic: full3243pass/1fail/257skip (old RAG pilot29/40 execution_failed); single reproduction passed1/4.35s; fresh full run69711 in progress. Cause unconfirmed; no speculative old-manager patch.

Task16: complete (Task16 assets and related source/readback followups verified by Node --check and browser queue/modal/observability; 39 targeted backend tests passed; startup isolated fixture6passed14.80s). Task17 full suite remains pending. Browser94 missing→pool23,feedback24 both captured and matched3; same logical turn retains occurrence1; humanapproved→knowledge136ready; fresh95 answer14days/drycloth/no-water with citation and explicit mock disclaimer. Current202/359/346. New paid20-case run fa5625c9-c358-452b-b1b9-434088537b77 active; originalcap hardbound retained.
Ruling: Keep one occurrence per logical user turn despite two sources — original approved design avoids counting one question twice just because fallback plus feedback — cost if wrong: screenshot ×2 differs; detail shows both raw pool rows and sources explicitly.
Task17 failure diagnosis: secondfull3243pass/1fail/257skip isolated startup test read actual live owner/journal(false) and hit correct ordinary-mode guard; no production guard change. Test copies launcher plus full pure helper dependency chain into tmp root with open dummy journal. RED actual failure retained; GREEN6passed. Incomplete third full launched before dependency correction was stopped; do not count it as completed verification. Next complete suite uses distinct final4 root.

Final one-pass review fixes: 17 reproduced REDs, plus precision RED1. Legacy flat metrics guarded; quantity units canonicalized in new algorithm v3 while v2 retained; deserialized split disjoint/hash/group checks + deterministic frozen partition + verified source rule/calibration label hash; missing usage invalidates average/share; exact Windows WinError5/32/33 replace retry max4 with path recheck (no permission/model retry). GREEN94passed153.59s incl1200recordscale. Corrected real local rederive after mistakenly accessing absent old.held_out_ids; original no new result published on failed attempt. Full final5 and fresh local integration in progress.
Ruling: Version unit semantics asv3 instead of silently redefiningv2 — original paid20 and archived rule remain replayable — cost if wrong: no second paid20 onv3 because capremaining2; offline replay20 no gatechanges is supplemental evidence only.
Final: Ruling: Treat missing-usage average dilution asImportant — one100token request and oneunknown must not look like50tokens/request or full known share — fix in same pass; other users seeN/A until coverage complete.
Task17 paid20completed0errors70GLM,23embedding20rerank; physical278/383/367. Stop paid calls by explicit retainedcap, do not restore ordinary mode as a route to further agent paid tests. Original2errorful20 and newcomplete20 kept separately; no two-new-clean-run claim.

Final independent review completed originalheadf074dbc: 0Critical/4Important/0Minor; all4 entered one fix pass with RED→GREEN94targeted; originalF08 minor carried. Review resumed same interrupted reviewer, no second review. Declined-to-judge4 rulings permanently recorded docs/superpowers/reports/2026-10-20-reference-backend-review.md.
Final5 full3262pass/1fail/257skip: MCP child binding64942 Windows10013. New deterministic no-probe RED plus actual --port0 child GREEN27/20.49s. Scoped fixture fix only; existing8101/8102 untouched. Full final6 running; local integration133pass174.13s. Ordinary8006ownerPID63436 v3 loaded, allownedjobsclosed, no furtherpaidcalls; immutableledger278/383/367 retained.

Final fix pass verified: full .venv/Scripts/python.exe -m pytest -q --basetemp=runtime/ch09-evidence/pytest-reference-final6 →3264passed257skipped634.73s, exit0. Final local MySQL/Milvus/Langfuse133passed174.13s. All4Important fixed, noCritical/newMinor; oldF08minor retained. Full logs and actual receipts preserved.
Task17: bounded engineering verification delivered; live quality acceptance remains partial (no second new-config clean20, heldout4falseallow/9falserefusal, faithfulness.875 and judge scope review). User retained cap278/280; do not auto-resume paid work. Keep this plan workspace/ledger because quality tail remains pending; permanent execution/rulings copied into docs before any later cleanup.
Final: Ruling: Keep branch/worktree as originally approved, no merge/push or new integration menu — scope remains this isolated branch, and user did not authorize integratingChapter09 — cost if wrong: master still lacks chapter09. All changes locally reviewable and committed.
Final: Ruling: Distinguish engineering delivery from complete quality acceptance — cap expansion explicitly declined and new tests cannot manufacture a second paid round or refit heldout — cost if wrong: user may need to approve a future validation budget or redefine the remaining acceptance scope. No such approval presumed.
