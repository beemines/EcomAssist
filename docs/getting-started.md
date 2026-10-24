# 首次部署

本指南面向新 checkout。所有命令在仓库根目录执行；运行前按自己的环境填写 `.env`。章节手册中的 `D:/shixi/...` 是原开发机位置，不必复制该目录结构。

## 环境

| 组件 | 要求 |
| --- | --- |
| 应用 Python | 3.11–3.13；原开发机使用3.13.5 |
| 依赖管理 | uv，使用仓库锁文件 |
| 本地存储 | Docker Compose；MySQL8.4、Milvus3.0.2 |
| 模型服务 | `.env.example`所定义的Chat Completions、嵌入和重排配置 |
| 主题ML（可选） | 独立Python3.12.13环境；原训练环境使用锁定的CUDA13.0版PyTorch，推理在CPU执行 |

源码没有生产身份认证与多租户部署方案。示例监听回环地址，并保持单worker。

## 1. 安装与配置

```powershell
uv sync --locked
if (-not (Test-Path -LiteralPath '.env')) { Copy-Item .env.example .env }
$env:PYTHONUTF8 = '1'
$env:PYTHONIOENCODING = 'utf-8'
```

至少检查以下配置，完整定义以[配置样例](../.env.example)和[`app/config.py`](../app/config.py)为准：

| 配置 | 说明 |
| --- | --- |
| `LLM_BASE_URL`、`LLM_MODEL`、`LLM_API_KEY` | 模型标准Chat Completions接口、模型名和密钥 |
| `SILICONFLOW_API_KEY` | 当前嵌入/重排提供方密钥 |
| `MYSQL_PASSWORD`、`MYSQL_ROOT_PASSWORD` | 本地数据库密码；初始化后不能仅修改环境变量就当作完成密码轮换 |
| `MYSQL_HOST/PORT/DATABASE` | 默认127.0.0.1:3307/customer_service |
| `MILVUS_URI`、`MILVUS_COLLECTION` | 默认本地19530及knowledge_hybrid集合 |
| `RERANK_MIN_SCORE`或`EVIDENCE_CONFIDENCE_RULE_PATH` | 有真实校准来源的知识证据门槛；启动前必须准备 |

`LANGFUSE_ENABLED`、`FLYWHEEL_ENABLED`、RAG/评估流水线开关按需配置，保持定时任务默认关闭。标准Chat Completions端点与供应商Coding端点不能混用。

## 2. 启动存储

```powershell
docker compose -p ecs-tool-calling --profile test up -d --wait --wait-timeout 120
docker compose -f compose.milvus.yaml -p ecs-knowledge up -d
```

MySQL业务库3307，隔离测试库3308。Milvus19530与健康接口9091仅绑定本机。`config/milvus-user.yaml`启用了当前TEXT/BM25方案所需StorageV3，已有卷应按当前版本迁移，不把关闭该选项当作回滚。

空MySQL卷自动执行基础schema、ch03DDL和种子；已有卷不会重复初始化。保留数据卷，日常停止不用`down -v`。

## 3. 显式迁移

当前默认聊天链路需要知识、质量、退款、上下文和审计结构。应用启动核验结构，不执行ORM自动建表。

```powershell
uv run --locked python -m app.knowledge.cli migrate
uv run --locked python -m app.quality.cli migrate
uv run --locked python -m app.refunds.cli init
uv run --locked python -m app.context.cli migrate
uv run --locked python -m app.tool_audit.cli init
```

启用飞轮与主题模块时继续：

```powershell
# 飞轮命令默认dry-run，execute才变更结构
uv run --locked python -m app.flywheel.cli migrate --database configured
uv run --locked python -m app.flywheel.cli migrate --database configured --execute
uv run --locked python -m app.topics.cli migrate --database configured
uv run --locked python -m app.topics.cli migrate --database configured --execute
uv run --locked python -m app.topics.cli verify --database configured
```

原始DDL在[`sql/`](../sql/)，运行时追溯列与恢复状态另有扩展文件。遇到结构漂移先核对目标库与备份，不删除旧表绕过。

## 4. 导入与校准知识

选择一份语料及独立集合，避免把互相矛盾的历史规则混在一起。以下为自带的早期演示资料；导入和向量化会新增知识行并调用已配置的嵌入服务：

```powershell
uv run --locked python -m app.knowledge.cli init-vectors
uv run --locked python -m app.knowledge.cli import-document --path knowledge-docs/demo-policy.md --type policy
uv run --locked python -m app.knowledge.cli import-document --path knowledge-docs/demo-faq.md --type faq
uv run --locked python -m app.knowledge.cli import-document --path knowledge-docs/demo-manual.md --type manual
uv run --locked python -m app.knowledge.cli import-document --path knowledge-docs/retrieval-models.md --type faq
uv run --locked python -m app.knowledge.cli vectorize-pending --batch-size 20
uv run --locked python -m app.knowledge.cli verify-hybrid --batch-size 20
```

导入CLI不去重，重复执行会新增行；中断恢复重跑`vectorize-pending`。MySQL主键与Milvus主键一致，向量读回核对后才标记完成。

### 为上述演示语料生成启动门槛

完成四份资料的导入与向量化后，在**同一配置库、集合和模型组合**上运行自带八题校准。它会请求配置的LLM改写、嵌入及重排服务，可能产生费用；这不是离线测试，也不属于安装依赖时自动执行的步骤。

```powershell
uv run --locked python -m evals.evaluate_retrieval --mode calibrate --database configured --output .cache/retrieval-calibration.json
```

默认题目来自`evals/retrieval_calibration.jsonl`，其原文金标定位对应随仓库提供的`retrieval-models.md`。命令读取当前done知识与当前集合，不重建或清空业务数据；新库应只包含自己选择的一致语料。`--database configured`与默认隔离测试库模式不同，不能把另一个库的实验门槛直接用到当前集合。

检查报告`passed=true`、八题实际有效且`calibration.threshold`为有限数，再将该值写入`.env`唯一的`RERANK_MIN_SCORE`项。报告失败时先处理其中的错误，不能填示例数字跳过检查。输出路径必须未被使用，后续校准另取文件名以保留历史。

这一步建立早期重排分数门槛，足以满足默认启动检查；它不是业务置信度概率，也不代表第九步正式多信号置信度已校准。正式证据规则的独立采集/留出流程见[第九步说明](ch09-local-demo.md)。使用商家资料或自己的知识库时，应使用与之匹配的校准题和金标，不能沿用此演示的八题或旧分数。

商家300题实验的八份资料在[`evals/datasets/merchant-rag-300/corpus/`](../evals/datasets/merchant-rag-300/corpus/)，它们属于另一套演示语料。已有混合数据库不能直接全库重建成商家子集；原50块发布与校准依据见[发布记录](validation/online-merchant-publication.json)及[校准记录](validation/online-merchant-calibration.json)。

## 5. 启动应用

```powershell
uv run --locked uvicorn app.main:create_app --factory --host 127.0.0.1 --port 8000 --workers 1
```

打开[聊天](http://127.0.0.1:8000/)、[后台](http://127.0.0.1:8000/admin)和[健康状态](http://127.0.0.1:8000/health)。聊天Enter发送、Shift+Enter换行，停止按钮取消当前生成；工单/退款预览确认后才写入。来源编号属于当前回复。

MCP物流与售后Server的启动、工具策略及连通验收见[工具系统指南](tool-system-demo.md)。Langfuse和飞轮需要额外的本地配置与校准产物，见[第九步指南](ch09-local-demo.md)。主题模型的独立环境、服务与演示配置见[分类器指南](topic-classifier.md)。

## 常见问题

| 现象 | 检查 |
| --- | --- |
| Settings缺配置或启动拒绝 | `.env`路径、必填模型项、真实门槛/规则文件、数据库结构及Milvus集合 |
| 端口被占用 | 先核对归属，只停止自己启动的进程，不结束所有Python或删除数据库卷 |
| 主题统计未启用 | 模型包/三字段profile未准备，或演示工厂未加载；克隆代码不会附送私有权重 |
| Langfuse没有项目或无费用数据 | 本地组织/项目、SDK配置、接入后的请求及查询时间；空页面不代表免费 |
| 中文输出乱码 | UTF-8终端、上述Python变量，以及MySQL客户端`SET NAMES utf8mb4` |
| 模型接口鉴权、余额或超时错误 | 核对供应商返回和阶段预算；保留失败，不把它记成“知识库无答案” |
