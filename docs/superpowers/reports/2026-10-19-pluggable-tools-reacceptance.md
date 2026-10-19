# 第八步 · 2026-10-19真实页面复验

后续用户原会话暴露了编号简写、建单建议来源和补订单号的覆盖缺口；本页仅记录当时7轮结果，不代表任意会话均已通过。最新1001补号故障已在原会话实测恢复，完整记录、测试范围及尚未重跑的整章范围见[原会话83/84修复记录](2026-10-19-compact-order-fix.md)。

用户要求：“你先测试验收一下，然后再告诉我应该怎么验收”。在b957ea0工作树上执行，产品代码仍是39659c6，未修改产品、模型、窗口、步数或权限规则。普通8005、物流8101、售后8102保持原PID；同版本独立8006只注入官方原有验收cap和独立checkpoint，避免给普通页面留下调用限额。

## 本次结论

按用户参考截图的物流→追问→预览→确认主流程通过，取消、只转人工、刷新恢复和此前两个组合失败原句均通过。7轮真实对话全部完成，实际28/30次GLM、0嵌入、0重排，没有失败调用或自动扩批。旧38与20的账本未重置，第八步累计86次GLM。

| 场景 | 本次证据 | 结果 |
| --- | --- | --- |
| 物流MCP | 会话79；query_logistics / mcp:logistics / success / retry0，页面签收状态、运单号MOCK17759278、上海轨迹与实际结果一致 | PASS |
| 缺问题描述 | “帮我建个工单”先追问；补充前没有工单 | PASS |
| 预览、刷新、确认 | “物流信息异常”出现预览；刷新仍可确认，预览阶段SQL为0；确认后恰好1张 | PASS |
| 实际工单回执 | T11db874262a83d898808c969e689329；SQL类型咨询、描述原文；builtin / success / retry0 / 29ms，页面单号相同 | PASS |
| 取消 | 新预览取消，SQL仍1张；builtin / permission_denied / retry0 / 1ms | PASS |
| 普通组合原句 | 会话80；在保与退货进度两项均mcp:aftersales / success / retry0；完整回答“已过保、12个月、待寄回”与工具结果一致 | PASS |
| 顺序组合原句 | 会话81；两个MCP读取、完整最终回复，字段与SQL结果一致 | PASS |
| 仅转人工、否定建单 | 会话80；投诉路径无工具写调用，主题弹窗→独立接入通知→人工新气泡，tickets为0 | PASS |
| 窄屏视觉 | 浏览器实际截图宽319px；预览、确认/取消、主题弹窗、长单号换行均可见，无水平溢出 | PASS（仅该实际宽度） |

会话79、80、81最终共7条工具审计、1张工单、0张退款申请。两个在保/退货组合的控制响应这次都是合法json_control；不据此声称真实模型一定覆盖native_read_stop分支，该分支仍由离线反例验证。

## 用量明细

| 对话轮次 | GLM请求数 |
| --- | ---: |
| 物流查询 | 5 |
| 要求建工单但没描述 | 3 |
| 补充“物流信息异常”并生成预览 | 3 |
| 第二张预览，用于取消 | 3 |
| 普通组合查询 | 6 |
| 仅转人工投诉 | 2 |
| 顺序组合查询 | 6 |
| 合计 | 28 |

确认、取消、刷新和前端模拟人工接入没有增加GLM调用。剩余2次不再使用。用户这次新请求是本批授权依据，不倒改2026-10-18“尚未复验”的历史记录。

## 后端与证据范围

本轮命令：

```powershell
.venv/Scripts/python.exe -m pytest tests/test_tool_execution_policy.py tests/test_tool_result_normalization.py tests/test_mcp_execution.py tests/test_native_read_completion.py -q
```

34通过，16.91秒；本地真实mock MCP和脚本模型，零付费模型调用。覆盖参数/权限拒绝、读暂时故障重试、写超时不重试、审计状态、错误投影和读取结束协议。上一轮全量2930通过188跳过、MySQL专项4通过仍按当时版本/命令记录；本轮没有产品变更，未重复整章全量。

热注册内置工具、新MCP工具及客服不重启的PID/core哈希证据沿用[2026-10-18报告](2026-10-18-pluggable-tools-acceptance.md)，本轮没有再次改策略或重启Server，也不冒称所有旧场景都重新跑过。随机mock结果不能当作真实物流/售后承诺。

本地证据位于runtime/tool-system-evidence/：20261019-logistics.png、20261019-preview.png、20261019-confirmed.png、20261019-cancelled.png、20261019-combined.png、20261019-handoff-dialog.png、20261019-handoff-connected.png、20261019-final-storage.json、20261019-backend-acceptance.log及本轮独立日志和持久账本。证据不入Git，不保存密钥。

用户操作步骤：[ch08-manual-acceptance.md](../../ch08-manual-acceptance.md)；过程记录：[ch08.md](../../../dev-notes/ch08.md)。普通入口为http://127.0.0.1:8005/，本轮验收完成后8006退出。工作树保留，没有合并/推送。
