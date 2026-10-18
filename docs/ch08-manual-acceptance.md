# 第八步手动验收步骤

2026-10-19。以下主流程已经在真实页面按顺序跑过；本次28次GLM、7轮对话全部完成，没有修改产品代码、模型、窗口或步数。具体证据见[本次报告](superpowers/reports/2026-10-19-pluggable-tools-reacceptance.md)。

## 先打开页面

当前普通服务已运行，直接打开 http://127.0.0.1:8005/ ，点击“开启新对话”（窄屏为右上角＋）。

若你以后关闭了服务，用PowerShell重新启动：

```powershell
cd D:/shixi/ecommerce-customer-service/.worktrees/pluggable-tools
pwsh -NoProfile -File scripts/start-tool-system-demo.ps1
```

启动结果应包含customer=8005、logistics=8101、aftersales=8102。不要把带次数上限的临时8006验收进程当作日常入口。首次配置环境/数据库另见[演示文档](tool-system-demo.md)。

## 一、按截图走物流到确认工单

同一个新对话中，依次做下面四步：

| 步骤 | 你输入或点击 | 应看到什么 |
| --- | --- | --- |
| 1 | `订单1001的物流到哪了` | “查询物流·已完成”，完整的物流状态、运单号及轨迹，带模拟数据说明；没有红色错误 |
| 2 | `帮我建个工单` | 先追问“请补充问题描述。”，这一步不应已经创建工单 |
| 3 | `物流信息异常` | 出现工单预览，能核对类型和问题描述，有“确认提交”“取消”两个按钮；未确认不写入 |
| 4 | 点击“确认提交” | 按钮禁用，下面独立的新回复给出实际工单号；数据库恰好新增1张 |

可以在第3步刷新一次：预览应恢复，仍要你亲自确认。工单类型可能按问题归到咨询或售后，描述应保留你提供的事实，不应编造损坏、赔偿或处理承诺。

物流Server返回的是mock数据，城市、签收状态、单号可能与教材截图或本次测试不同；核对是否来自工具、是否完整回答，不要求固定是某个城市或状态。

## 二、验收取消

在已完成确认后，再发：

> 帮我创建一个咨询工单：订单1001物流轨迹显示异常，请人工核对。

等新预览出现后点“取消”。应看到“已取消，本次未创建工单。”；已有那张工单仍保留，本次增量为0。审计应为create_ticket / permission_denied / retry_count=0。不要把“整个会话工单数为0”作为取消标准。

## 三、验收两个售后MCP读取

再开一个新对话，发送：

> 请查询订单1001目前的在保状态和退货处理进度，不申请退款。

应看到“查询在保信息·已完成”“查询退货进度·已完成”两条工具记录，并完整回答两项结果。mock状态可以变化；不应只出现“这次没有收到完整回复”，也不应出现退款申请表或新增退款记录。

上一轮另一个失败问句也已复验通过，可另开新对话测试：

> 请按顺序查询订单1001：先只查在保状态，收到结果后再查退货处理进度。不要并行，不申请退款。

## 四、验收转人工主题弹窗和独立气泡

发送：

> 我要投诉客服态度，只转人工，不要建工单。

点击“转人工”，应打开浅绿主题弹窗；再点“确认接入”，聊天中应分别出现“已接入人工客服”通知和“客服小猫·人工客服”的新气泡。此处为页面模拟接入，不表示连接了真实人工系统。

旧投诉回复仍保留“建工单”按钮，这是原先约定保留的手填表单入口；本例只点转人工，不应自动出现工单预览或创建工单。

## 五、核对来源和权限，而不只看页面勾勾

页面工具名称只能说明做过查询。要证明经过MCP，用仓库提供的只读脚本查审计：

```powershell
cd D:/shixi/ecommerce-customer-service/.worktrees/pluggable-tools
$env:PYTHONUTF8='1'
.venv/Scripts/python.exe scripts/tool-system-storage-evidence.py 79 80 81
```

79、80、81是这次已跑过的测试会话。你新开的对话请替换成自己的会话ID，可通过`GET /api/conversations`或log/app.log中的conversation_id确认。

核对：

- query_logistics的source是`mcp:logistics`。
- query_warranty、query_return_progress的source是`mcp:aftersales`。
- 确认create_ticket是`builtin / success / retry_count=0`。
- 取消create_ticket是`builtin / permission_denied / retry_count=0`。
- 每条审计都有tool_call_id和耗时；不要只凭助手文字认定已建单。

热注册新工具、仅重启某个Server及受控超时属于开发验收，已有独立证据和测试命令，见[演示文档](tool-system-demo.md)与[验收报告](superpowers/reports/2026-10-19-pluggable-tools-reacceptance.md)。普通页面验收不必故意关闭服务或大量调用模型。
