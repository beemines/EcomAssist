# 用PyCharm运行和验收第九步

## 一、打开正确的目录

1. 在PyCharm左上角点“文件”→“打开”。
2. 选择 **`D:\shixi\ecommerce-customer-service\.worktrees\observability-flywheel`**，点“确定”；可选择“新窗口”。
3. 左侧项目树根目录应是这个worktree。展开后应看到 `app/observability`、`app/flywheel`、`app/eval_pipeline`、`business_mcp`、`scripts`、`.run`。
4. 主目录master与worktree是两个独立检出。只在终端cd到worktree不会改变左侧项目树；如果左边看不到新文件，先检查打开的目录，不用重新创建模块。

## 二、选Python解释器

1. “文件”→“设置”→“项目”→“Python解释器”。
2. 点“添加解释器”→“添加本地解释器”→“现有环境”。
3. 浏览并选择当前worktree的 **`.venv\Scripts\python.exe`**，应用。
4. 终端中执行以下命令，看到解释器路径落在本worktree即可：

```powershell
.venv\Scripts\python.exe -c "import sys; print(sys.executable)"
```

已有 `.env` 是业务数据库和模型配置；本地Langfuse SDK配置是 `runtime/langfuse/sdk.env`。运行配置只引用文件路径，不把Key写进XML。

## 三、启动Langfuse

1. 先打开Windows的Docker Desktop，等待显示引擎正在运行。
2. 在PyCharm右上角运行配置下拉框选择 **CH09 01 - 本地 Langfuse**。
3. 点绿色三角运行。该配置使用Python模块 `app.observability.local_stack`，参数 `up --port 3000`，不需要Shell插件。
4. 控制台显示服务就绪后，这个Python命令可以正常退出；Docker容器仍继续运行。
5. 浏览器打开 <http://127.0.0.1:3000>。邮箱是 `admin@ch09.local`，密码查看当前worktree中 `runtime/langfuse/local.env` 的 `LANGFUSE_INIT_USER_PASSWORD` 值。
6. 登录后选择 **EcomAssist CH09** 项目，后面在Observability → Tracing里查请求。

## 四、先跑离线检查

1. 右上角选择 **CH09 03 - 离线检查（不调模型）**。
2. 点绿色三角，控制台应出现pytest通过结果。
3. 这验证启动/额度/指标合同，不代表真实模型已验收；也不会生成收费模型请求。

如果下拉框没有CH09配置，点“运行”→“编辑配置”，确认项目根下有`.run`三份CH09 XML，再重新打开本worktree。也可手动新增Python配置：选择“模块名称”，填`pytest`，参数填 `tests/test_observability_startup_guards.py tests/test_ch09_acceptance_cap.py -q`，工作目录选择worktree。

## 五、启动客服8006

1. 右上角选 **CH09 02 - 客服 8006 普通模式**。
2. 核对运行配置：模块 `uvicorn`；参数 `app.observability.demo:create_observability_app --factory --host 127.0.0.1 --port 8006 --workers 1 --app-dir "$PROJECT_DIR$"`；工作目录为当前项目。
3. 点绿色三角。看到“Application startup complete”和8006监听后，保留此进程运行。
4. 浏览器打开 <http://127.0.0.1:8006>。待审页是 <http://127.0.0.1:8006/review>，观测页是 <http://127.0.0.1:8006/observability>。
5. 该配置是普通模式，`CH09_ACCEPTANCE`为空；默认不启用收费定时。真实校准规则必须存在，缺失时不要拿测试fixture替换。

如果8006已经由PowerShell脚本启动，PyCharm再次启动会报端口占用。继续使用已有8006，或只通过它原来的受管启动脚本重启；不要随意结束端口上的未知进程。

## 六、物流MCP怎么核验

1. 若8101、8102已运行，直接使用，不再启动第二份。
2. 未运行时，在另一个PyCharm运行配置选择 **CH08 01 - 物流 MCP 8101**，点运行；再启动 **CH08 02 - 售后 MCP 8102**。
3. 回8006新建会话，问“订单1001的物流到哪儿了”。
4. 在Langfuse展开该次请求，工具操作应标记 `source=mcp:logistics`。只有聊天中出现“查询物流”标签不足以证明它来自MCP。

## 七、在页面验收飞轮

1. 新对话问一条库中没有的验收模拟政策。
2. 得到兜底后，点侧栏“飞轮待审队列”，刷新列表。
3. 点列表中问题文字“展开原话与证据”，核对原问题和片段。
4. 点行内“通过”打开弹窗，AI草稿会预填；核对并修改“标准化问题”“知识分类”“人工核准答案”。分类与原提问的过滤分类一致；模拟答案标注“【验收模拟政策】”。
5. 点“确认通过”。详情点“刷新状态”，等待“已入库·可检索”；若失败，先看错误再点“重试入库”。
6. 返回客服，新建另一个会话再问同一问题，应检索新知识回答。
7. 对一条完整回答点👎，保存成功才显示“已反馈”；在审核详情核对归并原话。详细检查点见 `docs/ch09-manual-acceptance.md`。

## 八、在终端读数据库证据，不乱码

PyCharm底部点“终端”，复制以下命令。把示例编号替换成本次会话和审核记录：

```powershell
Set-Location 'D:\shixi\ecommerce-customer-service\.worktrees\observability-flywheel'
$env:PYTHONUTF8='1'
$env:PYTHONIOENCODING='utf-8'
.venv\Scripts\python.exe scripts/ch09-storage-evidence.py --conversation-id 123 --review-id 45
```

脚本只读指定记录。要查评估，用 `--run-key` 加该轮UUID。不要用示例编号认定本机已有记录。

## 九、看评估结果与停止

观测页“评估趋势”可看已存在的轮次，不会因刷新重跑模型。“运行所选评估（收费）”会启动收费模型并显示运行进度。本次已有两轮20题原始失败报告及一轮修正后完整20题。累计278/280 GLM，余量不够再跑一轮；本轮停止付费，不执行300题或收费定时。详细数字见实际报告。

停止客服时点它自己Run窗口的红色停止按钮；停止容器用本地栈的`stop`命令，保留数据卷。离线8007仅是开发预览，页面标有模拟模型，不能当作最后的8006服务或真实成绩。
