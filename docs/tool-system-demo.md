# 第八步：可插拔工具演示

想按页面逐项验收，直接看[手动验收步骤](ch08-manual-acceptance.md)，其中物流、追问、预览确认/取消及组合查询已于2026-10-19真实复验。

在本章工作树、已配置项目.env且MySQL/Milvus可用的PowerShell7中运行：

```powershell
uv sync --locked
$env:PYTHONUTF8='1'
.venv/Scripts/python.exe -m app.tool_audit.cli init
.venv/Scripts/python.exe -m app.tool_audit.cli verify
pwsh -NoProfile -File scripts/start-tool-system-demo.ps1
```

打开 http://127.0.0.1:8005/ 。物流8101、售后8102、客服8005是三个独立Hidden进程。启动脚本只管理自身记录且重新核验身份的进程；未知占用会拒绝接管。普通演示没有验收次数上限，不自动执行DDL。8004及其工作树不受此脚本管理。

先问“帮我建个工单”，补充“饮水机一直漏水”，在预览中确认后才写tickets并返回真实单号。取消不建单，审计permission_denied。原投诉回复中的“建工单”仍打开用户表单。所有订单和MCP业务数据均为演示mock，不能当实际物流或退款承诺。

## 热注册

config/tool-policy.json是本地管理员策略。变更需写完整JSON后原子替换，下一轮加载；不接受Server自报权限。未知工具不开放，只有内置create_ticket可写。暂停中的会话固定原manifest，撤权仍即时拦截。

内置示例：将plugins加入`examples.builtin_dispatch_site`，tools追加：

```json
{"source":"builtin","name":"query_demo_dispatch_site","operation":"read","order_id_arg":"order_id"}
```

不用重启客服，问“订单1001的模拟发货站点在哪里”。示例模块只通过register登记定义/工厂，Agent核心没有名称分支。已有模块不做importlib.reload；修改同名模块须使用新的入口版本，避免运行期引用混杂。

MCP示例：本地tools追加：

```json
{"source":"mcp:logistics","name":"query_pickup_hours","operation":"read","order_id_arg":"order_id"}
```

仅重启物流Server：

```powershell
pwsh -NoProfile -File scripts/start-tool-system-demo.ps1 -Service logistics -LogisticsPlugin examples.mcp_extra_tools
```

问“订单1001的取件服务时间是什么”。客服PID不变，下一轮重新发现新工具。恢复初始演示时删除两条样例授权/plugins入口，单独以`-Service logistics`启动物流Server即可；历史及工单不删除。

## 验证与定位

```powershell
.venv/Scripts/python.exe -m pytest -q
.venv/Scripts/python.exe -m pytest tests/integration/test_tool_audit_storage.py tests/integration/test_ticket_confirmation_storage.py --run-mysql -q
.venv/Scripts/python.exe scripts/tool-system-storage-evidence.py 74
```

显式SQL集成使用3308自有随机测试库；不清理业务库。最后命令只读所指定会话的工单/审计，不发送模型。tool_audit_logs记录工具来源、五种状态、物理重试次数及耗时，审计连接失败不回滚业务。只读暂时故障最多重试一次；写操作零自动重试，超时表示结果未知。

少量页面验收使用`-Acceptance`显式开启同一持久账本40GLM/12嵌入/6重排（含失败与后台）。不要用验收模式留给用户日常聊天；恢复普通服务用`-Service customer`，/health应仅返回status=ok。

本章实际结果、失败及未执行范围见[验收报告](superpowers/reports/2026-10-18-pluggable-tools-acceptance.md)，过程见[开发记录](../dev-notes/ch08.md)。
