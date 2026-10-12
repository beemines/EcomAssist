# 原改写协议与显式降级留证

Run `aecdf615794d4ccdad984c9caeda979f`；scope `pilot`；源码 `05ca796090ba1c0d2e3c5fff8ce310e3548bb941`；方法SHA `2030d7686f97bb7bc902dfc65c8e88c7ff23a24386de1267339d5845b86391dd`。原请求/返回对象/严格校验保持，旁路不增加上游调用。实际共享rewrite请求 10，按题声明 `{"attempted_n": 10, "success_n": 10, "degraded_n": 0, "error_n": 0, "success_rate": 1.0, "unreported_n": 0}`。

| 题号 | 原 planner 合法 | 原错误码 | runner 状态 | 四路声明一致 | 原 query/空扩展 |
|---|---|---|---|---|---|
| A21 | True | None | success | True | True |
| A43 | True | None | success | True | True |
| B3 | True | None | success | True | True |
| B54 | True | None | success | True | True |
| C35 | True | None | success | True | True |
| C5 | True | None | success | True | True |
| D1 | True | None | success | True | True |
| D3 | True | None | success | True | True |
| E19 | True | None | success | True | True |
| E2 | True | None | success | True | True |

原planner无效结构仍记录失败；runner仅按已审查policy明示degraded，使用原query/空expansions继续四路，不将降级计作改写成功。HTTP200/stop不能替代严格结构合法性。原始正文/解析cause只私存，安全JSON保留类型、finish、长度、脱敏schema形状和真实声明；不反推旧失败。

实际状态 completed；counts `{"completed": 40, "rewrite_error": 0, "retrieval_error": 0, "self_check_error": 0, "answer_error": 0, "judge_error": 0, "cancelled": 0, "not_attempted": 0, "running": 0, "total": 40, "attempted": 40, "errors": 0}`；cleanup `{"ok": true, "errors": [], "unverified": []}`。此旁路不是质量记录，原质量pair逐字节保留。

[安全JSON](merchant-rag-degraded-rewrite-evidence.json) · [原质量JSON](merchant-rag-degraded-pilot.json)
