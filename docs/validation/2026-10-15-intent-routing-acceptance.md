# 意图分流：浏览器验收记录

## Task 8：受控 UI 验收（2026-10-15）

用户要求“前端部分用 Vibe Coding”。直接实现后用真实 Chromium 点击与截图检查；本阶段未运行前端 TDD、完整 pytest 或代码评审波次。没有启动真实 8003、调用模型、迁移或写入应用数据库，8002 保持原状。以下全部为受控接口数据的 UI 结果，不能作为真实业务或 SQL 落库通过。

入口：

```powershell
node --check app/static/chat.js
node --check scripts/verify-intent-routing-browser.cjs
node scripts/verify-intent-routing-browser.cjs --url http://127.0.0.1:8003/ --mode controlled
```

受控模式使用自有临时回环端口，`--url` 仅记录目标配置，不启动、改写或拦截该服务。分段 HTTP SSE 经过真实 UTF-8 解码与页面解析。浏览器使用本机既有 Playwright/Chromium，无新组件或依赖。

最终结果：**11/11 PASS，退出码 0**，全部场景 pageerror 为空。完整请求方法/正文/查询字符串和截图在：

`D:/shixi/ecommerce-customer-service/.worktrees/intent-routing/.cache/intent-routing-browser/controlled/96df48d8-3d88-47dc-a120-28acd00432a2/results.json`

| 场景 | 实际断言与请求次数 | 截图文件 |
| --- | --- | --- |
| paused-cards | paused 恢复输入，2 张只读摘要卡，无满意度；HTML 字符按文本显示 | paused-cards.png |
| refresh-pending-and-resume | 刷新 GET pending-order 1 次；双击只发选单 POST 1 次；四字段字符串准确，无新增用户问句 | refresh-pending-and-resume.png |
| selection-409-recovery | 首次 409 保持旧卡锁定；手动 GET 当前待选后继续，累计选单 POST 2 次 | selection-409-recovery.png |
| new-message-invalidates-cards | 新消息禁用旧卡；正文“申请退款”不能触发表单；选单 POST 0 次 | new-message-invalidates-cards.png |
| offer-terminal-and-disconnect | 收到 offer 但尚未 done 时隐藏入口；断连不显示许可 | offer-before-done.png、offer-terminal-and-disconnect.png |
| refund-cancel-escape-keyboard | 空白必选阻止提交、取消与 Esc 均退款 POST 0 次；恢复按钮焦点、焦点保持弹窗内 | refund-cancel-escape-keyboard.png |
| refund-submit-once-receipt | 只读 ¥299.00；双击退款 POST 1 次；只传原定位/offer/原因；原回答不改，独立“服务通知”显示申请号和待审核 | refund-submit-once-receipt.png |
| refund-failure-retains-reason | 首次 503 后原因“运输破损”保留；显式重试成功，累计退款 POST 2 次 | refund-failure-before-retry.png、refund-failure-retains-reason.png |
| refresh-refund-revalidated | sessionStorage 只有会话及两字段定位；刷新 GET refund-offer 使用原 SQL ID/检查点；服务器拒绝则无入口，退款 POST 0 次 | refresh-refund-revalidated.png |
| narrow-refund-dialog | 390×720，浅绿圆角主题，边界无横向溢出、下拉和提交按钮可见 | narrow-refund-dialog.png |
| existing-actions-citation-feedback | 引用原文、反馈锁定正常；人工取消/确认零附加 POST，独立通知/小猫气泡；工单取消 0、双击提交 1 POST | existing-actions-citation-feedback.png |

表内截图均位于上述 JSON 同目录。人工查看了 paused-cards、独立回执、桌面失败表单与窄屏表单；未把仅有断言当作截图视觉检查。

身份夹具刻意使用 `9007199254740993/995/997/999` 等大于 JS 安全整数的规范十进制字符串；请求 JSON 严格保持字符串，金额继续为整数分。

实现：卡片只有完整 paused 后可选择，同组锁定，恢复复用 SSE。退款入口仅来自服务器完成许可；六类原因初始空白必选，金额只读，提交中防重，失败保留原因，按钮标明“提交申请 · 待审核”。刷新不缓存订单/金额/owner/完整政策作为授权依据，不增加通用历史功能。

## 失败与返工

- 首次读取命令触发已知 PowerShell conda profile 警告，随后 `login=false`。一次只读文件探测使用不存在的 contracts/API 文件名，改为实际源码，无业务影响。
- CUA 首选已尝试：IAB 子代理不支持可见页；Chrome 两次因 request-header-policy / Statsig Cloudflare 403 无法创建页。按已授权回退使用既有 Chromium 自动化。
- 沙箱下缓存映射与浏览器启动失败；补齐真实用户缓存探测，`require_escalated` 启动既有 Chromium 成功，未下载浏览器。
- 首个实际浏览器运行仅 2/11 通过：夹具末段 SSE 字节重复导致大多数完成帧解析失败，已修复切片起点；原失败目录 `ef2f646e-5469-4775-98ca-58008c03d97b` 保留。
- 第二次 10/11 通过：未完成场景错误地查询了用户气泡而非助手正文，导致等待超时；修正定位，未以删除断言绕过。目录 `d0ee4c4b-e0ab-4883-8009-4d9aea8c0648` 保留。
- 最终 11/11 通过，同时收紧手动待选 GET 期间的输入锁，避免旧读取与新消息交错。全部运行独立目录，不覆盖失败证据。

## Task 9：真实联调待执行

真实运行入口已实现，**本阶段未执行**：

```powershell
node scripts/verify-intent-routing-browser.cjs --url http://127.0.0.1:8003/ --mode live
# Task 9 需要实际提交时：
node scripts/verify-intent-routing-browser.cjs --url http://127.0.0.1:8003/ --mode live --submit-refund
```

可用 `--message "具体审核用例"` 替换默认退货问句。live 无路由拦截，记录实际 API 响应、截图及请求计数；默认打开后取消，带提交参数才点击提交。结果始终标注 `sql_verified:false`，真实 SQL 需要 Task 9 另取证，不能靠 HTTP 回执推定。
