# 开发与测试

## 两个依赖环境

```powershell
uv sync --locked
uv sync --project ml/topic_classifier --locked
```

根环境运行应用及业务测试。ML环境固定Python3.12.13及独立Torch/Transformers版本，代码仍从仓库根目录按`ml.topic_classifier...`模块运行。不要把两个环境的site-packages混用，也不要为文档整理顺手升级依赖。

命令依据已核对[uv官方CLI](https://docs.astral.sh/uv/reference/cli/)与[锁定/同步说明](https://docs.astral.sh/uv/concepts/projects/sync/)：`--project`选择项目与环境，不切换当前工作目录；`--locked`在锁文件不一致时失败，避免静默更新。本步骤既有库接口核对见[锁定源码与官方文档记录](superpowers/research/2026-10-21-topic-classifier-apis.md)。

## 默认回归

```powershell
uv run --locked python -m pytest -q
uv run --project ml/topic_classifier --locked python -m pytest ml/topic_classifier/tests -q
```

默认主套件使用测试模型/HTTP替身，真实MySQL、Milvus和Langfuse用例默认跳过。ML测试验证数据契约、评测、导出与本地服务，不进行真实全量训练。首次安装可能下载依赖，模型权重另按自己的数据/训练流程准备。

Windows长期运行大量异步用例时，若出现资源或套接字耗尽，应保留原失败日志，先定位原因。需要分进程执行完整清单时，记录收集的精确node ID、每批结果、所有跳过及源码hash；不把缺题或挑选通过的子集称完整回归。

## 真实存储测试

先按[首次部署](getting-started.md)启动Compose的test profile，并在自己的`.env`配置测试连接。以下开关显式启用真实服务：

```powershell
uv run --locked python -m pytest -q --run-mysql --run-milvus
# 需另行准备本地Langfuse及其测试配置
uv run --locked python -m pytest -q --run-langfuse
```

MySQL测试固定3308，使用随机自有schema/行；Milvus使用测试专用集合，清理只针对本次自有资源。涉及共享测试表的用例还需相应显式迁移，缺结构应修前置条件，不能改指向3307业务库或清空旧数据。

只验证第十步存储时：

```powershell
uv run --locked python -m pytest tests/integration/test_topic_storage.py tests/integration/test_topic_snapshot.py tests/integration/test_topic_distribution.py --run-mysql -q
```

## 前端检查

前端为静态资源，HTML由FastAPI提供；无需npm构建。修改后用浏览器检查目标页面、窄屏实际可用性、键盘页签、折叠区、错误/空态和确认流程；有真实业务副作用的按钮要在明确测试数据上操作。

```powershell
node --check app/static/workspace.js
node --check app/static/topic-acceptance.js
node --check app/static/topics.js
node --check app/static/review-queue.js
node --check app/topics/review_ui.js
git diff --check
```

Node只用于可选JS语法检查，不是应用运行依赖。人工截图保留视口与实际结果；不能把一次桌面截图称为所有尺寸已验证。

## 提交前

1. 运行与改动相关的测试；合并前核对完整回归与必要的集成范围。
2. 更新可复现命令、配置项和行为说明；步骤过程按约定追加到`dev-notes/chXX.md`。
3. 保留失败与返工、模型评估的样本数和有效分母，不用单元测试覆盖率替代真实质量。
4. 检查暂存清单，排除`.env`、私有语料、预算、checkpoint、模型权重和运行日志。
5. 对有模型/数据库费用或写入的操作，先明确范围；不让普通GET、页面刷新或安装步骤自动开启它们。

主仓库和其他步骤worktree可能有正在运行的服务。不要重置他人的未提交修改、删除被服务依赖的worktree或批量结束Python进程。
