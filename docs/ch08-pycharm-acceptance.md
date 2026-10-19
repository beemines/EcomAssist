# 第八步：用 PyCharm 验收 MCP

## 打开正确的项目

在 PyCharm 用 File → Open 打开：

```text
D:\shixi\ecommerce-customer-service\.worktrees\pluggable-tools
```

这是第八步的工作树。解释器使用这个目录下的 `.venv\Scripts\python.exe`，工作目录为项目根目录。应用会从根目录加载已有 `.env`，不要把 Key 复制到运行配置或截图里。

项目 `.run/` 中已经保存五个 Python 运行配置。打开项目后从右上角下拉框选择；若未显示，重新打开项目，或在 Run → Edit Configurations 按下表建立 Python 配置，目标选择 **Module name**。配置方式参考 [JetBrains Python 运行配置文档](https://www.jetbrains.com/help/pycharm/run-debug-configuration-python.html)。

| 配置 | Module name | Parameters |
| --- | --- | --- |
| CH08 01 - 物流 MCP 8101 | `business_mcp.logistics` | `--port 8101` |
| CH08 02 - 售后 MCP 8102 | `business_mcp.aftersales` | `--port 8102` |
| CH08 03 - 客服 8005 | `uvicorn` | `app.tools.demo:create_tool_system_app --factory --host 127.0.0.1 --port 8005 --workers 1` |
| CH08 04 - MCP 协议验收（不调用大模型） | `pytest` | `tests/test_business_mcp_servers.py tests/test_mcp_execution.py tests/test_mcp_discovery.py -v` |
| CH08 05 - 物流 MCP 新工具演示（替换01） | `business_mcp.logistics` | `--port 8101 --plugin-module examples.mcp_extra_tools` |

共同环境变量为 `PYTHONUTF8=1;PYTHONUNBUFFERED=1`。客服配置另有 `WORKFLOW_CHECKPOINT_PATH=$PROJECT_DIR$/runtime/workflow/tool-system-8005.sqlite`，继续使用原8005检查点；`TOOL_SYSTEM_ACCEPTANCE` 留空，运行普通模式。不要给客服加 `--reload`，避免额外进程与重复启动。

## 先做不消耗模型额度的协议验收

选 **CH08 04**，点击绿色三角。它会自行启动临时、独立的物流/售后进程，在临时端口通过真实 Streamable HTTP 发现并调用工具，并验证未知工具的本地授权、参数、来源及连接故障处理。无需先启动01～03，也不需要关闭现有8005。

Run 窗口应显示全部测试 PASSED、退出码0。此项证明真实 MCP 协议/执行引擎链路，尚不等于大模型在聊天中选对工具。

## 把三个服务切换到 PyCharm Run 窗口

若8005/8101/8102已经由旧启动脚本运行，先关闭这些旧实例，再从PyCharm启动，不能让两个进程争用同一端口。下面在 **PyCharm Terminal 的 PowerShell** 中执行一次：只停止启动器记录且命令、创建时间、解释器、父子关系均匹配的旧实例；任一身份不符就停止操作，不按端口强杀。不涉及8004，不删历史或数据库。

```powershell
Set-Location 'D:/shixi/ecommerce-customer-service/.worktrees/pluggable-tools'
$taskRoot = (Get-Location).Path
. ./scripts/tool-system-process-ownership.ps1
$pythonHome = (Get-Content .venv/pyvenv.cfg | Where-Object { $_ -match '^home = ' }) -replace '^home = ', ''
$interpreter = Join-Path $pythonHome 'python.exe'
foreach ($service in @('customer','logistics','aftersales')) {
    $ownerPath = Join-Path $taskRoot ".cache/tool-system/$service-owner.json"
    if (!(Test-Path -LiteralPath $ownerPath)) { continue }
    $owner = Get-Content -LiteralPath $ownerPath -Raw | ConvertFrom-Json
    $process = Get-CimInstance Win32_Process -Filter "ProcessId=$($owner.listener.pid)"
    if ($null -eq $process) { continue }
    $plugin = if ($owner.plugin) { $owner.plugin } else { '' }
    $expected = Get-ToolSystemCommand $taskRoot $service $plugin
    if (!(Test-ToolSystemOwner $process $owner $taskRoot $interpreter $expected @(Get-CimInstance Win32_Process))) {
        throw "Cannot verify $service owner; no stop performed for this service"
    }
    $again = Get-CimInstance Win32_Process -Filter "ProcessId=$($process.ProcessId)"
    if (!(Test-ToolSystemOwner $again $owner $taskRoot $interpreter $expected @(Get-CimInstance Win32_Process))) {
        throw "Process identity changed; no stop performed for $service"
    }
    Stop-Process -Id $again.ProcessId
}
```

然后依次运行 **01物流 → 02售后 → 03客服**，每项启动成功后再启动下一项。底部保留三个Run窗口，各自显示对应端口的启动日志。后续在PyCharm中通过红色停止按钮管理这些进程；旧PowerShell启动器不会接管PyCharm启动的实例。不要混用两种方式重启。

## 对照截图验收聊天与来源

1. 打开 http://127.0.0.1:8005/ ，新对话发送“订单1001的物流到哪了”。应获得完整物流回答。
2. 再开一个对话发送“请查询订单1001目前的在保状态和退货处理进度，不申请退款。”。应完整回答两项。
3. PyCharm Terminal中列出会话编号：

```powershell
$response = Invoke-WebRequest 'http://127.0.0.1:8005/api/conversations' -UseBasicParsing
$data = [System.Text.Encoding]::UTF8.GetString($response.RawContentStream.ToArray()) | ConvertFrom-Json
$data.items | Select-Object id,first_question_preview | Format-Table -AutoSize -Wrap
```

PyCharm终端若使用Windows PowerShell 5.1，直接Invoke-RestMethod会把当前无charset的JSON响应解码错误；上面从原始字节明确按UTF-8解码。2026-10-19对同一8005会话列表实测，默认预览乱码，显式UTF-8正常显示“订单1001的物流到哪了”。这是客户端解码问题，数据库内容与MCP调用不受这条查询影响。

4. 查本次会话审计，下面90/91需替换成实际编号：

```powershell
.venv/Scripts/python.exe scripts/tool-system-storage-evidence.py 90 91
```

应分别看到 `query_logistics / mcp:logistics / success`，以及 `query_warranty`、`query_return_progress / mcp:aftersales / success`，每条含 `tool_call_id`、重试次数与耗时。页面勾勾和助手声称调用过工具都不能代替这些审计记录。当前仓库使用审计表记录来源，不要求控制台逐字出现教材截图的 `tool run ...` 文本。

客服实际上下文在项目 `log/app.log`，可直接在PyCharm打开，搜索 `model_ctx`、`history_ctx`。物流/售后Run窗口显示各自收到的HTTP请求；来源和执行结果以审计表核对。

## 验证只重启物流就增加新工具

保持02售后和03客服运行。在本地 `config/tool-policy.json` 的 `tools` 数组中授权以下项，保留已有条目，按[演示文档](tool-system-demo.md)完整写好JSON后原子替换：

```json
{"source":"mcp:logistics","name":"query_pickup_hours","operation":"read","order_id_arg":"order_id"}
```

停止 **01物流**，运行 **05物流新工具演示**；二者都用8101，不能同时运行。客服03保持原进程。新对话问“订单1001的取件服务时间是什么？”，应回答09:00–18:00，审计出现 `query_pickup_hours / mcp:logistics / success`。这一步同时验证Server新增工具、下一轮发现、本地策略热加载；客服未重启。

恢复时停止05，启动01，并移除刚加的该项授权。确认/取消工单的页面步骤及SQL增量标准见[手动验收](ch08-manual-acceptance.md)。
