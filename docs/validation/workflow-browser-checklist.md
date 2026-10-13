# Workflow 聊天页面浏览器验收

Task8 的受控验收证明页面解析与交互，不代表真实模型、数据库或工单服务验收。Task9 负责真实服务与模型的有界验收。

## 受控模式

```powershell
node scripts/verify-workflow-browser.cjs --url http://127.0.0.1:8002/ --mode controlled
```

脚本在真实 Chromium 页面上输入、点击和操作原生确认框。仅精确拦截同源 `/api/conversations`、`/api/chat` 和当前受控会话的 `/actions/ticket`；聊天转发到脚本自有回环流夹具。静态文件与健康探测正常请求。8002 空闲时启动隐藏的测试静态服务器，若被占用保留已有进程；不触碰8001。自有静态/随机端口流服务器均在退出时关闭。

Playwright 优先从项目或 `NODE_PATH` 加载，然后探测用户桌面运行时。Chromium 优先采用 `WORKFLOW_CHROMIUM_PATH`，其次 Playwright 默认缓存、`PLAYWRIGHT_BROWSERS_PATH` 和用户缓存；不绑定某台机器的唯一路径。当前检测为 Playwright1.62.1、Chromium1234。

验收输出每个场景 PASS/FAIL；JSON 和截图在 `.cache/workflow-browser/controlled/`。首次失败截图另存 `.cache/workflow-browser/red/`。

| 验收项 | 页面/网络断言 |
| --- | --- |
| 订单→物流 | 两个按调用ID独立完成的徽章 |
| Workflow知识查询 | 显示知识检索 |
| 投诉建议 | 完成后出现两按钮，初始零工单请求 |
| 转人工取消/确认 | 取消不锁定；确认零网络请求，只锁自身按钮，准确显示两句固定文案 |
| 工单取消/确认 | 取消不锁定/不请求；确认一次POST仅两字段，显示编号，只锁自身按钮 |
| 只建工单 | 无人工转接文案，转人工按钮仍可用 |
| 旧回复 | 后续不同最终消息ID完成后，旧动作仍提交原消息ID/检查点 |
| 失败重试 | 恢复自身按钮，重试使用同一身份 |
| 真正延迟的SSE | actions帧已收到，done前零按钮；done和EOF后才有确认入口 |
| 异常/断开/停止 | 不发布按钮；未完成工具显示结果未确认 |
| 动作协议故障 | 重复帧、错序、错误身份、非UUID、任意选项/标签/额外字段拒绝 |
| 空选项 | 成功无按钮，不当成错误 |
| 引用原文 | 键盘打开dialog、Escape恢复引用焦点，原文HTML保持纯文本 |
| 一次反馈 | 👍选择后👍/👎整组锁定，零工单请求 |
| 窄屏 | 390×844无水平溢出，输入框可见，徽章/按钮换行，键盘确认可取消 |

## 真实模式

```powershell
node scripts/verify-workflow-browser.cjs --url http://127.0.0.1:8001/ --mode live
```

live 不注册任何路由拦截，也不启动夹具服务器。默认只打开实际页面并截图；**不声称已验证真实聊天**。Task9 如需真实聊天，应显式设置 `WORKFLOW_LIVE_MESSAGE`；脚本会从输入框发送原文并检查错误/有效回答，单次页面等待默认245秒，可通过 `WORKFLOW_BROWSER_TIMEOUT_MS` 有界覆盖。脚本不自动点击真实工单确认、不自动重试模型失败。截图与结果在 `.cache/workflow-browser/live/`，标签明确区别于受控结果。

## 本次结果

当前受控25/25 PASS；`node --check app/static/chat.js`、`node --check scripts/verify-workflow-browser.cjs`、`git diff --check`通过。人工检查390×844截图：输入固定底部，多徽章完整，操作按钮换行，焦点可见。未读取真实 `.env`，未调用真实模型，未运行Python全套或300题RAG评估。
