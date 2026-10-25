# 技术栈与核对依据

核对日期：2026-10-24。README徽章按源码中的实际用途划分，依赖版本以两个`pyproject.toml`与对应`uv.lock`为准。图片可加载只说明徽章地址有效，不能作为技术已使用的证据。

## 客服业务数据库

**业务数据库为MySQL 8.4。** [Settings.database_url](../app/config.py#L166)明确构造`mysql+aiomysql`地址，[Database](../app/db/session.py#L11)将该地址传入SQLAlchemy异步引擎。[ORM模型](../app/db/models.py)使用MySQL方言，部署镜像为[mysql:8.4](../compose.yaml)。

本轮运行`tests/test_db_config.py`，**10项通过**，其中包括MySQL连接驱动、端口、字符集、密码特殊字符和脱敏检查。这是连接配置回归，没有新增真实数据库写入，也不代表重新完成全部存储集成验收。

SQLite用于[LangGraph检查点](../app/workflow/persistence.py)，Milvus用于[稠密/稀疏检索索引](../app/retrieval/milvus.py)；知识正文与业务记录仍以MySQL为权威数据源。

## README主标签的源码依据

| 范围 | 标签 | 使用位置与用途 |
| --- | --- | --- |
| 运行语言 | Python | [业务环境](../pyproject.toml)支持3.11–3.13；[ML环境](../ml/topic_classifier/pyproject.toml)固定3.12.13 |
| Web入口 | FastAPI、Uvicorn | [应用工厂](../app/main.py)与[启动命令](getting-started.md#5-启动应用)；Uvicorn为锁定运行依赖 |
| 数据校验与HTTP | Pydantic、HTTPX | [设置与校验](../app/config.py)、[模型客户端](../app/core/llm.py)、[HTTP教师客户端](../app/topics/teacher.py) |
| 工具契约 | JSON Schema | [工具目录](../app/tools/catalog.py)与[参数校验](../app/tools/validation.py)调用`jsonschema`校验器 |
| 模型编排 | LangChain、OpenAI compatible API | [ChatOpenAI客户端](../app/core/llm.py)与[LangChain消息/工具协议](../app/agent/bare.py)；兼容协议标签不表示当前模型服务由OpenAI提供 |
| 图编排 | LangGraph | [Workflow图](../app/workflow/graph.py)与[Agent图](../app/workflow/agent.py)使用`StateGraph` |
| 工具连接 | MCP | [MCP客户端](../app/tools/mcp_client.py)使用适配器；[业务MCP服务](../business_mcp/)使用FastMCP |
| 业务持久化 | MySQL、SQLAlchemy、aiomysql | [连接配置](../app/config.py)、[异步会话](../app/db/session.py)、[ORM](../app/db/models.py) |
| 状态持久化 | SQLite checkpoint | [检查点工厂](../app/workflow/persistence.py)使用`AsyncSqliteSaver` |
| 检索流程 | RAG、Milvus、BM25、RRF | [检索服务](../app/retrieval/service.py)与[Milvus适配](../app/retrieval/milvus.py)实现向量/中文BM25召回和RRF融合 |
| 检索模型 | BGE-M3、bge-reranker-v2-m3 | [固定模型配置](../app/config.py)、[嵌入客户端](../app/knowledge/embeddings.py)、[重排客户端](../app/retrieval/rerank.py)；不表示本地训练了这两个模型 |
| 可观测性 | Langfuse | [SDK生命周期](../app/observability/runtime.py)、[LangChain回调](../app/observability/tracing.py)、[自部署配置](../compose.langfuse.yaml) |
| 数据预标 | GLM-5.3-flash teacher | [教师客户端](../app/topics/teacher.py)明确锁定智谱接口和教师模型；该标签仅描述本步骤造数/预标用途 |
| 分类模型 | HFL RoBERTa-wwm-ext | [基座定义与下载](../ml/topic_classifier/doctor.py)固定`hfl/chinese-roberta-wwm-ext`，实际由`AutoModelForSequenceClassification`加载 |
| 训练框架 | PyTorch、Transformers、Accelerate | [训练实现](../ml/topic_classifier/train.py)使用PyTorch与Transformers Trainer；Accelerate为该独立训练环境的锁定依赖及Trainer后端 |
| 训练设备 | CUDA 13.0 | [ML锁定包](../ml/topic_classifier/pyproject.toml)为`torch==2.14.1+cu130`；本机已有doctor回执记录`torch_cuda=13.0`、`cuda_available=true`。本轮未重训，CPU推理见[独立服务](../ml/topic_classifier/service.py) |
| 数据与评测 | NumPy、scikit-learn、iterative-stratification | [数据划分](../ml/topic_classifier/data.py)调用多标签分层拆分器，[评测实现](../ml/topic_classifier/evaluation.py)调用分类指标与逐类混淆矩阵 |
| 模型文件与下载 | Safetensors、Hugging Face Hub | [产物加载](../ml/topic_classifier/artifacts.py)使用`safetensors`权重，[基座准备](../ml/topic_classifier/doctor.py)使用`snapshot_download` |
| 前端 | HTML5、CSS、JavaScript、SSE | [聊天HTML](../app/static/index.html)加载原生样式与脚本；[流式客户端](../app/static/chat.js)读取`text/event-stream`响应 |
| 开发与部署 | Docker Compose、uv | 三份Compose部署配置与[依赖同步/启动命令](getting-started.md)，`uv.lock`锁定依赖 |
| 测试 | pytest、pytest-asyncio | [测试配置](../pyproject.toml)与[夹具](../tests/conftest.py)；这两个是测试工具名称徽章，不是测试通过或覆盖率状态徽章 |

PyMySQL在锁定依赖中，并由aiomysql内部使用协议与异常类型；README不再把它作为另一套独立业务数据库客户端标签展示。

## 独立组件的内部依赖

| 组件 | 依赖与职责范围 | 配置依据 |
| --- | --- | --- |
| Langfuse | PostgreSQL 17、ClickHouse 25.12、Redis 7、MinIO均服务于Langfuse；应用通过Langfuse SDK/API访问该组件 | [compose.langfuse.yaml](../compose.langfuse.yaml) |
| Milvus | etcd 3.5.25与MinIO服务于Milvus；应用通过pymilvus访问检索索引 | [compose.milvus.yaml](../compose.milvus.yaml) |

这些依赖不在README主技术徽章表中展示。它们的存在以Compose配置为依据，不意味着客服业务库改用PostgreSQL，也不表示客服应用直接把Redis用作业务缓存。

## 本轮验证范围

- 逐项核对保留标签的源码调用、直接依赖或开发配置；带版本的徽章同时核对锁定配置，CUDA补查已有本机回执。
- 运行MySQL配置测试10项；检查Markdown引用、代码块、徽章覆盖与实际渲染。
- 没有新增训练、模型调用、知识发布、迁移或业务写入；没有用徽章宣称ONNX、LoRA、前端框架、CI或生产质量已通过。
