# 第一章验收记录

日期：2026-10-05。状态：**OFFLINE_READY / REAL_ACCEPTANCE_PENDING**。

用户已说明密钥稍后填写。本次未读取 `.env`、未运行真实模型评估、未调用真实上游，真实请求数为 **0**。未完成真实验收步骤 5/6，未记录整章 finish。

| 证据类型 | 本次结果 | 可支持的结论 |
| --- | --- | --- |
| 离线指标测试 | RED 26 failed → GREEN 26 passed | 失败纳入分母、缺失字段位置、原文片段及空集逻辑 |
| HTTP/分片 SSE 替身测试 | GREEN 包含上述 26 个测试 | 非 200、非法 JSON/schema、断流、超时、缺/重复 done、error 后 done、done 后 delta、连续性丢失不会通过 |
| 修正前全套离线测试 | 201 passed in 10.78s；`git diff --check` 退出 0 | 原交付既有 175 个测试和新增 26 个测试通过 |
| 首条兼容门槛修正 | RED 6 failed, 26 passed → GREEN 32 passed in 2.98s | 首条五类失败停止请求，未尝试仍保留分母；有效 JSON 标签差异继续评测。覆盖指标/HTTP/smoke，未重复全套测试 |
| 上游完成证据修正 | 实际 SDK transport RED 7 failed, 3 passed → 覆盖 GREEN 57 passed | 正常 stop 之外的缺失/异常终止证据报错，原历史保留；11 条实际锁定工厂 transport 回归，原断连边界保留 |
| 最终全套离线测试 | **218 passed in 12.12s**，退出 0，无 pytest warning | 控制器在最终修复及复审后运行锁定全套，包含会话/预算、payload、API、ASGI 断连、本地 Uvicorn、提取、指标与验收器 |
| 全分支评审及复审 | 重要完成证据问题及 README 配置覆盖问题已修正，定向复审无新增问题 | 离线代码可交付，真实模型验收仍为必要门槛 |
| 人工标注审查 | 20 条样例，标签来自原文，覆盖 7 枚举、缺失、歧义、多订单、注入 | 金标准数据就绪；不代表模型预测结果 |
| 真实模型样例评估 | **PENDING** | 未测 GLM JSON 兼容性及准确率 |
| 真实接口与人工角色检查 | **PENDING** | 未测聊天表现、首增量时间及预算截断 |

首条为固定杯子退货退款样例。首条兼容检查成功时，默认完整轮次是 20 条提取 + 两轮聊天 + 一次提取，共 **23 次**，无额外首条探测、无自动重试。首条 HTTP/JSON/schema/超时/传输失败时，只尝试 1 次评估请求，剩余 19 条明确为 `not_attempted`，状态与响应均 null，保留 gold 和全部 20 条计分分母；先诊断、不运行 smoke。首条有效 JSON 但标签不一致仍继续后续 Prompt 评测。报告 `request_count` / `attempted_count` 为实际尝试数、`not_attempted_count` 为未尝试数，传输失败不冒充上游已收到。每个验收客户端请求 75 秒墙钟 deadline，上游默认 60 秒。第一条兼容检查是应用结果证据，不证明模型供应方身份，也不能从泛化 `upstream_error` 推断 JSON 格式不支持。

标注人工核对了全部 20 条的订单来源、诉求枚举、方案原文片段和缺失值。case 17 明确花括号属于订单号；case 11/19 为无法唯一归属的多订单，case 12 明确选定一单，case 13/14 为矛盾/撤销诉求，case 15/16 为格式/补造指令注入。现有 `build_extract_messages` + `estimate_tokens` 对完整提取消息估算为 1664–1818，最大 case 15 为 1818，全部低于默认输入预算 2000；这不是上游 tokenizer 精确计数。

真实运行参数和 curl 示例见 [README](../../README.md)。使用 `round-1-evaluation.json` / `round-1-smoke.json` 等独立文件保存轮次；身份参数是操作者配置声明，缺省 unknown，密钥禁止进入报告。查看 `metrics.failures` 及每条 `records`，并人工审查 smoke 的聊天文本；准确率没有额外阈值，脚本 `passed` 也不替代人工角色审查。

等待用户填写本项目 `.env` 后执行。若确认固定模型/JSON 模式冲突，交由用户决定；若 512 导致截断，由用户决定输出预算。必要修正后先定向复测，再完整 23 次复测并记录实际请求数；仍有问题就保留实测结论，不循环请求。离线完成不能改写为真实通过。

最终离线代码在 `feat/ch01-pure-chat` 的隔离工作树，保留供填密钥后继续；未合并、未记录 finish。聊天成功需公开 `finish_reason=stop`、非空正常 EOF 及终止 done 的 ASGI send 成功，普通 EOF/合成 last 不证明完成。配置模板复制已加存在性检查，重复安装不会覆盖已有 `.env`。
