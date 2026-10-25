# 第九步：本地运行入口

本机当前验收服务使用的工作区：`D:\shixi\ecommerce-customer-service\.worktrees\observability-flywheel`。以下命令继续在此目录执行。第九步源码合并到master后，主目录也会具备相关代码；本机密钥、真实校准产物和运行记录被Git忽略，仍保留在该worktree，不随合并自动迁移或清理。从其他检出启动时须先按设计准备它自己的本地配置，不能把缺少配置当成源码未合并。

## 正常启动

先启动 Docker Desktop，等待引擎就绪。打开 PowerShell：

```powershell
Set-Location 'D:\shixi\ecommerce-customer-service\.worktrees\observability-flywheel'
$env:PYTHONUTF8='1'
$env:PYTHONIOENCODING='utf-8'
pwsh -NoProfile -File scripts/start-langfuse.ps1
pwsh -NoProfile -File scripts/start-observability-demo.ps1
```

Langfuse：<http://127.0.0.1:3000>；客服：<http://127.0.0.1:8006>；审核后台：<http://127.0.0.1:8006/review-queue>。

正常模式没有本次验收的累计调用账本限制；每次手动评估仍有自己的运行上限。定时评估关闭。旧8004/8005服务不会被本步骤脚本停止。已有8101/8102物流、售后MCP只核对，不接管；未启动时可用项目中的step08运行配置单独启动。

首次安装的结构与真实校准产物应按验收报告准备；缺少真实规则文件时8006会拒绝启用，不能拿测试fixture替代。这里的启动命令不会重新迁移数据库或重跑收费校准。

Langfuse登录邮箱为 `admin@ch09.local`；密码在当前工作区 `runtime/langfuse/local.env` 的 `LANGFUSE_INIT_USER_PASSWORD` 字段。SDK的本机连接配置在 `runtime/langfuse/sdk.env`，运行配置不保存密钥。关闭容器保留数据：

```powershell
.venv\Scripts\python.exe -m app.observability.local_stack stop --port 3000
```

## 日常验证与查证

```powershell
# 无模型请求的合同测试
.venv\Scripts\python.exe -m pytest tests/test_observability_startup_guards.py tests/test_ch09_acceptance_cap.py tests/test_eval_pipeline_metrics.py tests/test_eval_pipeline_schedule.py -q

# 只读查询选中的会话/审核记录；将编号换成自己的本轮编号
.venv\Scripts\python.exe scripts/ch09-storage-evidence.py --conversation-id 123 --review-id 45
```

证据脚本按UTF-8输出，避免Windows PowerShell5.1的Invoke-RestMethod误解码中文；直接在PyCharm终端读输出即可。它不外发数据、不运行模型、不更新记录。不能把示例编号当成本机实际编号。

重试单个标准化任务：

```powershell
# 默认dry-run；只有加--execute才改状态
.venv\Scripts\python.exe -m app.flywheel.cli retry --database configured --pool-id 123
.venv\Scripts\python.exe -m app.flywheel.cli retry --database configured --pool-id 123 --execute
.venv\Scripts\python.exe -m app.flywheel.cli process --database configured --pool-id 123 --execute
```

审核页“重试入库”保留原知识ID与累计次数。额度或鉴权恢复后，HTTP显式重试会唤醒受管消费者；验收硬额度不会被重试清零。

## 收费评估入口

先预检，不会请求模型：

```powershell
$runKey=[guid]::NewGuid().ToString()
.venv\Scripts\python.exe -m app.eval_pipeline.cli run --scope smoke_20 --run-key $runKey
```

确认本次要付费运行后，同一命令加 `--execute`。20题来自固定留出集合，每轮最多80次GLM调用，另有嵌入与重排；每次新一轮使用新的UUID，查询/重放原UUID不会自动补跑。查看已有轮次：

```powershell
.venv\Scripts\python.exe -m app.eval_pipeline.cli status --run-key $runKey
.venv\Scripts\python.exe scripts/ch09-storage-evidence.py --run-key $runKey
```

全量预检把 `--scope smoke_20` 换成 `--scope full_300`；真正执行300题最多1200次GLM，本次交付不自动执行。两轮趋势不保证上升；同一配置下也会有模型波动。N/A代表没有有效样本，不能当成0或100%。

推荐在8006审核页“评估趋势”启动，统一使用本地Langfuse连接。若确需CLI执行并记录本地trace，显式载入SDK文件（不打印Key）：

```powershell
.venv\Scripts\python.exe -c "from dotenv import load_dotenv; load_dotenv('runtime/langfuse/sdk.env'); from app.eval_pipeline.cli import main; main()" run --scope smoke_20 --run-key $runKey --execute
```

普通CLI按`.env`的Langfuse启用设置运行；没有开启时不会自动向Langfuse导出。上述收费命令不会因本步骤交付而自动执行。

本机已验收的两轮UUID分别为`1dca3ee1-5a49-4c60-a82c-7454d49b4be3`、`3ecfae0f-2897-434f-8ec9-b37df20fc3e4`。只读查询这些UUID可核对原结果，不会再花模型费用。

## 开发预览与本次验收模式

`scripts/ch09-offline-ui.py` 在8007启动明确标记的离线页面，使用3308随机自有schema、固定模型和模拟索引；两轮mock图表不是真模型成绩。正常结束后只清理本轮schema。可在另一个终端正常停止：

```powershell
Invoke-RestMethod -Method Post -Uri 'http://127.0.0.1:8007/api/offline/stop' -ContentType 'application/json' -Body '{}'
```

`start-observability-demo.ps1 -Acceptance` 专供已批准的 `ch09-local-20261019` 验收批次，GLM280、嵌入450、重排450，失败也计数，所有入口共享持久账本，重启不清零。不要把该模式作为正常聊天服务。切回正常模式前须先结束/排除该批次自己的未完成任务，不能带着未完测试任务继续无上限外发。

## 2026-10-20参考页补充

待审入口现为 http://127.0.0.1:8006/review，观测入口为 http://127.0.0.1:8006/observability；旧review-queue兼容保留。完整逐页步骤见ch09-manual-acceptance.md。

下面是无需收费调用的本地派生重算；保留原始采集，输出当前reference-calibration报告：

```powershell
.venv\Scripts\python.exe -m app.quality.confidence_report
```

历史问题批处理先只读预览（示例ID须换成明确授权范围）：

```powershell
.venv\Scripts\python.exe -m app.flywheel.cli batch --database test --from-id 1 --to-id 10 --limit 10 --preview
```

加--execute才会初始化并标准化指定范围；本次没有执行历史客户数据。当前实际累计278/280 GLM、383/450嵌入、367/450重排。旧两轮20题有错误，新20题完整；本轮停止付费，不切模式绕过额度补跑。
