# 第九步合并与交付记录

日期：2026-10-21（Asia/Shanghai）。用户明确要求归档第九步完整提示词与DDL，并“合并提交推送”。本次只处理归档和集成，没有新一轮收费模型验收。

## 需求归档与集成范围

- [完整原始提示词与DDL](../../prompts/step-09-observability-flywheel.md)，prompt.md和README均有入口；原始需求与已批准实施口径分开保留。
- 原master为6d0f6466b1d330d497ee674fcc4b14019eb38e75，包含第九步已批准的设计和计划；它是feature分支的祖先。
- 获取远端后origin/master为f44e4f9eeadfca40a2531b43a62fe68f6352173d，没有新增远端提交。
- feature归档提交为de3d40e；源码逻辑沿用15a113e，归档阶段只改文档。
- 使用no-ff合并，合并提交为a045339aa63f748c92f199b54a7af9b866c02f02，无冲突；合并后完整文件树与已验证feature树一致，tree为6b3515d13f2a1cb614d786759c52908187b48ea3。
- 集成包括本地Langfuse、链路/成本、三路落池和原轮快照、标准化查重、审核补库、评估流水线、置信度校准、聊天风格后台、迁移及回归测试。手动验收文档补充了个人账号没有组织时的管理员登录步骤。

## 本次新运行的验证

| 范围 | 实际结果 | 本地证据 |
| --- | --- | --- |
| feature完整离线pytest | 3264通过、257跳过；407.95秒；退出0 | worktree/runtime/ch09-evidence/merge-20261021-offline.log |
| 本章改动涉及的本地MySQL3308/Milvus/Langfuse集成 | 108通过；83.06秒；退出0；使用隔离库/集合及模拟模型 | worktree/runtime/ch09-evidence/merge-20261021-integration.log |
| master合并后启动守卫/累计额度/指标/调度合同 | 18通过；8.82秒；退出0 | 主目录runtime/ch09-evidence/merge-20261021-master-checks.log |
| 原始DDL/文档链接/JS/Git差异 | 归档SQL与sql/ch09-ddl.sql忽略注释及空白后完全一致；Prompt章节/围栏/入口链接、Node语法、diff --check通过 | 合并前检查及开发记录 |

完整离线命令：`.venv/Scripts/python.exe -m pytest -q --basetemp=runtime/ch09-evidence/pytest-merge-20261021`。

集成回归仅选择相对master修改过的tests/integration文件，加`--run-mysql --run-milvus --run-langfuse`。没有把跳过的真实集成项算作通过，也没有用Scripted模型的trace冒充真实模型成绩。

合并后合同命令使用本worktree已锁定依赖的Python，在主目录执行：`python -m pytest tests/test_observability_startup_guards.py tests/test_ch09_acceptance_cap.py tests/test_eval_pipeline_metrics.py tests/test_eval_pipeline_schedule.py -q`。首次受限运行没有产出测试结果，已中止；以相同受管权限重跑得到上表18通过，不把中止运行计为通过。

## 运行数据与质量范围

工作区D:/shixi/ecommerce-customer-service/.worktrees/observability-flywheel继续保留：现有8006验收服务、本地SDK凭据、校准规则、账本及截图依赖该目录。没有因合并停止或重启8004/8005/8006、MCP8101/8102或数据库/观测容器，也没有迁移或清理本地运行数据。源码已进入master，Git不携带运行密钥或实际对话快照。

合并不表示全部模型质量通过：[实际验收报告](2026-10-20-reference-acceptance.md)仍保留旧两轮20题的9/8阶段错误、新配置仅一轮完整20题、Faithfulness0.875、留出4误放/9误拒及延期F08草稿质量项。自动验收累计账本仍278/280 GLM、383/450嵌入、367/450重排；本次没有增加收费请求或运行300题、收费定时。

[演示命令](../../ch09-local-demo.md) · [PyCharm步骤](../../ch09-pycharm-acceptance.md) · [逐页验收](../../ch09-manual-acceptance.md) · [阶段记录](../../../dev-notes/ch09.md)

## 远端交付回执

首次普通推送已成功：origin/master从f44e4f9前进到42c5751f63ed2a95a05b18a47d59ada007e17590，包含上述源码合并和交付记录；git ls-remote返回值与本地HEAD完全一致，git status显示master与origin/master同步。此段及对应finish开发记录作为后续纯文档提交推送，不改变任何已验证源码、DDL或运行数据。
