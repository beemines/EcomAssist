# 第十步 · PyCharm操作与人工抽审

当前实现工作树：`D:/shixi/ecommerce-customer-service/.worktrees/topic-classifier`。
业务解释器：该目录下`.venv/Scripts/python.exe`（Python3.13.5）。
独立训练解释器：该目录下`ml/topic_classifier/.venv/Scripts/python.exe`（Python3.12.13）。
证据、权重和共享预算：`D:/shixi/ecommerce-customer-service/.cache/ch10-evidence`。

第十步尚未完成训练、留出评测及实际分类验收。下文只记录已实现命令；小批人工抽审未完成前不能扩量训练。测试fixture、随机分类头和规则例子都不代表模型效果。

## 在PyCharm打开正确工作树

1. 菜单“文件 → 打开”，选择上述`topic-classifier`目录。不要在旧第八/九步工作树运行本章命令。
2. “设置 → 项目 → Python解释器 → 添加现有解释器”，先选择业务`.venv/Scripts/python.exe`。
3. “运行 → 编辑配置 → + → Python”，选择“模块名称”，工作目录填工作树完整路径。普通数据命令模块是`app.topics.data_cli`。
4. 环境变量添加`CH10_ENV_FILE=D:/shixi/ecommerce-customer-service/.env`、`PYTHONUTF8=1`、`PYTHONIOENCODING=utf-8`。只填环境文件路径；不要把Key复制进文档、聊天或截图。
5. 本章训练命令使用第二个解释器；不要往业务解释器装Torch。已有8006第九步服务保持原样。

## 先看预算和快照

PyCharm底部“终端”选PowerShell，逐行执行：

```powershell
Set-Location 'D:/shixi/ecommerce-customer-service/.worktrees/topic-classifier'
$AppPy = '.venv/Scripts/python.exe'
$MlPy = 'ml/topic_classifier/.venv/Scripts/python.exe'
$Evidence = 'D:/shixi/ecommerce-customer-service/.cache/ch10-evidence'
$env:CH10_ENV_FILE = 'D:/shixi/ecommerce-customer-service/.env'
$env:PYTHONUTF8 = '1'
$env:PYTHONIOENCODING = 'utf-8'
& $AppPy -m app.topics.data_cli budget-status
```

共享账本已初始化，勿再运行`budget-init --execute`，没有重置命令。`used_micro / 1000000`是保守预算占用，含未知请求预留，不等同于供应商实际扣费。硬上限10元、300次物理尝试，失败和重启不清零。

`$Evidence/pool/preview.json`和`snapshot.json`已保存29行有界只读快照，高水位31，原文去重21问。所有来源真实性均未核实；本地原话文件含隐私，不能提交Git。快照不会修改问题池，也不会自动发送模型。

## 生成小批抽审包

先免费预览：

```powershell
& $AppPy -m app.topics.data_cli pilot --snapshot "$Evidence/pool/snapshot.json" --output "$Evidence/pilot"
```

执行版本增加`--execute`，会使用10元共享账本并向标准智谱API发送经过本地复查的单句与术语表，也会生成合成题；不发送会话历史、检索快照和数据库凭据。用户现已明确允许本批最多20条去重脱敏单句发送到`https://open.bigmodel.cn/api/paas/v4/chat/completions`，使用`glm-5.3-flash`；该授权不代替后续人工抽审。

```powershell
& $AppPy -m app.topics.data_cli pilot --snapshot "$Evidence/pool/snapshot.json" --output "$Evidence/pilot" --execute
```

每个收费阶段会先留下检查点。已完成阶段重跑会复用；未完成、失败或范围变更会拒绝自动重复调用。不要删除journal或预算文件来“重新开始”。报错时先看安全错误代码和`budget-status`。

结构失败的响应会保存在本地私有`pilot/diagnostics/`，便于修复后离线重验，不提交Git。需要重新请求时，仅可在查明原因后显式指定`--retry-failed-stage`和`--retry-reason`恢复一个同范围failed阶段，原失败回执另行留存；in_flight不能用此方式重发。此选项不用于连续盲试，也不重置预算。

## 人工查看和填写

当前包已实际生成：68条、17类齐、32条多诉求；20条池句来源真实性未核实、48条合成。包hash为`6cb5bbbdaa3944feba577efd47e9a1e0b43d8b96f82dc80d2eda337d334b4225`，尚未人工审阅通过。文件在`D:/shixi/ecommerce-customer-service/.cache/ch10-evidence/pilot/`：

- `pilot/review.html`：只读审阅页。在PyCharm“文件 → 打开”选该完整路径，右键“在浏览器中打开”。逐条查看脱敏后的句子、独立预标标签、来源和边界说明。
- `pilot/decisions.jsonl`：待填写，每行一个样本。初始`decision=null`、审核人空、时间空，绝不会默认通过。
- `pilot/coverage.json`：实际是否达到68条、17类覆盖和至少17条多诉求。未满足就保留缺项，不能口头当通过。
- `pilot/pack.json`与`journal/`：冻结机器材料。不要改id、pack_hash、问题原句或机器材料。

在`decisions.jsonl`每一行填写：

| 字段 | 怎么填 |
| --- | --- |
| decision | 标签正确填`"accept"`；需改标签填`"correct"`；不应使用填`"exclude"` |
| final_labels | 接受时保留现有数组；修正时写最终全部标签；排除时写`[]` |
| reviewer | 填你自己的审核署名，不能空着 |
| reviewed_at | 填带时区的时间，如`"2026-10-21T20:00:00+08:00"`，应使用实际审核时间 |
| notes | 纠偏、疑难或排除原因；无则保留空字符串 |

标签只能取17类权威表的名称；“其他”不能与其他标签同时出现。不要替模型猜没有说出的诉求。例如“XL还有货吗”只问库存，“不要退，只想修”只标保修维修。“买大了想退”是保留的验收probe及其近重复，不进入训练集。

全部填写、保存后，先仅验证：

```powershell
& $AppPy -m app.topics.data_cli review-import --pack "$Evidence/pilot/pack.json" --decisions "$Evidence/pilot/decisions.jsonl" --output "$Evidence/pilot/review-receipt.json"
```

没有报错且接受/排除数量正确，再增加`--execute`保存回执。缺样本、重复ID、空审核人、默认同意、错hash和无时区时间都会拒绝。导入不调用收费模型。

也可在聊天明确回复“我已逐条审阅这个包，全部通过”，或按sample_id列出修正/排除项，由助手据你的实际决定填写回执。仅说“继续”不算人工抽审。扩量训练仍等待这份真实回执；后端旁路开发可以继续。

## 当前可复验的本地基线

模型底座与一次完整GPU优化器探测已完成，结果在`$Evidence/doctor.json`；探测权重已丢弃，训练将重新加载底座。

```powershell
& $AppPy -m pytest tests/test_topic_contracts.py tests/test_topic_cleaning.py tests/test_topic_budget.py tests/test_topic_teacher.py tests/test_topic_review_receipts.py -q --basetemp='.cache/ch10-tests/manual'
& $MlPy -m pytest ml/topic_classifier/tests/test_doctor.py -q --basetemp='.cache/ch10-tests/manual-ml'
```

这些命令不产生收费请求。训练、评测、serve、业务库实际迁移、批量归类与主题页的操作将在实际实现和验证后补入，不把尚未实现的命令写成可用验收流程。

## 已实现的表结构预检（不执行迁移）

以下命令只读，当前3307尚无topic_classifications表，输出stage=missing、preview=true、applied_count=0：

```powershell
& $AppPy -m app.topics.cli migrate --database configured
```

原DDL在`sql/ch10-ddl.sql`，四个nullable追溯字段在`sql/ch10-runtime.sql`；3308自有fixture已验证迁移、默认RESTRICT外键、question_id唯一性、旧行四列NULL及ORM往返。暂不对3307执行迁移或真实批量归类；原问题池保持原样。
