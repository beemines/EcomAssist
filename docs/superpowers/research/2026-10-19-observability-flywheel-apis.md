# 第九步接口与复用核对（设计阶段）

核对日期：2026-10-19。用户已允许本章用官方文档和锁定版本源码替代不可调用的 Context7。以下是设计依据，不是安装或验收完成记录。

## 本地部署

- 方向：用户明确选择本机 Docker Compose 自部署；未批准 Langfuse Cloud。
- 官方部署说明：https://langfuse.com/self-hosting/deployment/docker-compose 。其中 100 GiB 是 VM 存储建议示例，本地 Requirements 未给出 100 GiB 最低磁盘门槛。
- 候选服务端发布版本：`v4.63.0`，官方发布时间为 2026-10-16；发布记录：https://github.com/langfuse/langfuse/releases/tag/v4.63.0 。
- 固定发布的 Compose 原文：https://github.com/langfuse/langfuse/blob/v4.63.0/docker-compose.yml 。包含 web、worker、ClickHouse、MinIO、Redis、Postgres；原文仍使用浮动镜像 tag，实施计划需核对可用发布 tag / digest 后锁定，不能把引用固定版本的 Compose 等同于其所有镜像已固定。
- 现有 Milvus 占用宿主 9091 / 19530；新 Compose 必须使用独立项目、网络和数据卷并避开端口。

## Python SDK 与图回调

- 官方 PyPI 元数据：https://pypi.org/pypi/langfuse/json ，本次查询版本 `5.0.2`，Python 范围 `>=3.11,<4.0`，依赖范围允许现有 httpx / Pydantic；OpenTelemetry 等新增依赖仍须在实施阶段解析锁文件验证。
- 固定版本源码：https://github.com/langfuse/langfuse-python/tree/v5.0.2 ，回调实现为 `langfuse/langchain/CallbackHandler.py`，客户端为 `langfuse/_client/client.py`。
- 官方 LangChain / LangGraph 集成：https://langfuse.com/integrations/frameworks/langchain 。当前文档明确 SDK v5 需要 `langchain-core>=1`；不能照搬 v2 的导入路径或 trace API。
- 运行 worktree 实测现有 `langgraph==1.2.15`、`langchain-core==1.6.6`。已读安装源码：`StateGraph.compile()` 没有 callbacks 参数，编译结果的 `with_config()` 支持 RunnableConfig 合并。因此“编译时挂一次回调”应在图构造处使用 `compile(...).with_config(callbacks=[...])`，保留完整图对象及 checkpoint 行为，再验证调用路径和并发隔离。
- 自定义执行引擎与检索不是全部通过标准 LangChain Tool / Retriever 调用，完整 trace 验收必须检查这些操作的子 observation，不能只看到根节点就算通过。
- 已读 SDK 5.0.2 `langfuse/_client/client.py`：提供 start_observation / start_as_current_observation、update_current_span、flush、shutdown、get_trace_url；不应套用旧 update_current_trace。已读 `langfuse/api/observations/client.py`：同步 / 异步 get_many 支持 fields、limit、cursor、type、trace_id、时间范围和 filter。正式设计以 execution 根 observation 和 trace 身份关联前置模型调用的意图归属。

## 项目复用边界

- `app/quality/repository.py` 的拒答写入可将助手消息与原话入池放在同一短事务；现有来源已经涵盖 retrieval_low_conf / self_check / user_feedback。
- `app/core/evidence.py` 的完整 evidence payload 含正文与有限得分；公开 Citation 只含展示字段，没有得分。反馈快照应从原轮 checkpoint 的服务端 payload 提取，不重新检索，不信任页面提交的正文或分数。
- `app/context/history_reader.py` 已按 SQL final_message_id 和完成根 checkpoint 定位原轮，可复用其身份核验思路。没有检索与原始证据无法恢复应区分，不能都伪称“没有检索”。
- `app/knowledge/hybrid_jobs.py` 支持按 MySQL 主键重放 pending、检查 ACK 与向量读回，之后标记 done；审核入库应复用此恢复方式，并保证重复审批不会新增重复知识。
- Ch04 同时保留旧物理 chunk 指标与新版完整证据组指标。新趋势必须固定版本、分母、数据集和配置标识，失败 / 未执行行不能充当成功分数；校准集和验证集不可混用。
- 实际读取冻结 cases.jsonl 得到 300 题，A_policy / B_model / C_colloquial / E_multi / D_unanswerable 各 60 题；regressions.jsonl 有 2 条，字段是 case、condition_changes、original_eval_id、reason。分组关联应读取内嵌 case，不假设回归文件顶层就是普通题目。
- 已核对现有 SufficiencyService 的 content_ablation 模式可执行内容自评而不叠加 calibrated_score 模式的旧 Top1 门槛。本章启用正式规则后需用该内容判断能力，避免两套分数闸门叠加。

## 本机只读基线

- C 盘空闲约 191 GB，D 盘空闲约 154.2 GB。
- Docker 配额约 15.46 GiB 内存、32 个逻辑 CPU；本次五个运行容器瞬时内存合计约 1.35 GiB。
- 现有镜像 3.649 GB、数据卷 1.513 GB。后续按同一口径比较新增占用，部署前的 10～20 GB / 预留 30 GB 只作估算。
- 普通沙箱不能访问 Docker named pipe；只读受限提升查询已成功，不代表 Docker 故障。没有拉取镜像或修改现有容器。

## 实施核对（2026-10-19，Task 1进行中）

- 固定SDK源码再次核对：Langfuse构造器支持base_url / timeout / tracer_provider；CallbackHandler只接受public_key / trace_context，通过同public_key的已初始化client取资源。关闭使用flush / shutdown，本章有界异步回收。依赖解析与同步成功，仅新增11个SDK相关包，原固定核心版本未变。
- observations.get_many的fields支持core/basic/io/metadata/usage等组；IO字段总是原始字符串，parse_io_as_json=true已废弃并返回400，读回测试必须自行JSON解析。使用trace_id过滤以及cursor分页，metadata长值须按需expand_metadata，不能假设默认完整。固定源码：https://github.com/langfuse/langfuse-python/blob/v5.0.2/langfuse/api/observations/client.py 。
- Headless初始化按官方变量生成本地独立项目与用户，凭据存ignored的runtime/langfuse/local.env，应用仅使用四项sdk.env，来源：https://langfuse.com/self-hosting/administration/headless-initialization 。
- 官方注册表核对得到六个固定digest，均写入compose.langfuse.yaml：web/worker为4.63.0；基础服务沿固定发布Compose的ClickHouse25.12、Postgres17、Redis7、Chainguard MinIO分支解析digest。config --quiet已通过，真实容器和读回验收尚未完成。
- 后续本地验收：六容器启动、中文span导出和observations读回、headless用户登录session核对均通过。登录使用NextAuth公开REST的providers/csrf/callback/session，先检查provider回调为本机，再发送本章生成的凭据；不打印凭据或session。官方接口说明：https://next-auth.js.org/getting-started/rest-api 。

## Task 2追踪验证

- SDK5.0.2的propagate_attributes是模块级上下文接口，支持session_id和metadata；既写当前span，又传播trace维度。真实读回证实初始LangGraph回调产生的trace级intent会覆盖同名observation metadata，仅span.update不足。结束根前按持久化最终State核对，并用有界作用域propagate_attributes同步后，本地API读回意图正确。

## 原轮反馈与事务接口核对（2026-10-19）

- SQLAlchemy当前官方2.0文档已到2.0.55，项目继续锁定2.0.54；核对安装源码`ext/asyncio/session.py`的`begin`/`begin_nested`及异步Session归属，不为文档最新版本升级依赖。官方事务入口：https://docs.sqlalchemy.org/en/20/orm/extensions/asyncio.html 。
- FastAPI请求体使用Pydantic模型，路径参数单独绑定；官方文档：https://fastapi.tiangolo.com/tutorial/body/ 。核对已安装`fastapi/routing.py`的JSON请求解析路径；反馈沿用本机同源JSON写边界，不直接信任浏览器证据。
- Pydantic严格JSON模式允许已声明的datetime ISO字符串，而Python严格模式不自动从字符串转换；`model_validate_json`用于读取持久化JSON。核对安装`pydantic/main.py`与官方说明：https://docs.pydantic.dev/latest/concepts/json/ 。
- 已安装`langgraph/checkpoint/sqlite/aio.py`的`alist`持有同一saver锁直到异步迭代器结束；反馈定位原根后先用`aclosing`关闭迭代器，不在持游标期间对同saver调用`aget_tuple`。原完成根直接使用原始checkpoint channel_values，排除pending写投影。

## 后台worker租约与错误类型（2026-10-20）

- 再次发现当前工具列表仍无Context7，继续按用户授权使用官方与锁定源码。MySQL8.4命名锁按连接拥有，提交/回滚不释放，连接结束才释放；锁名最长64字符，IS_USED_LOCK返回拥有连接ID：https://dev.mysql.com/doc/refman/8.4/en/locking-functions.html 。
- JSON任务筛选使用JSON_EXTRACT/JSON_UNQUOTE，官方定义：https://dev.mysql.com/doc/refman/8.4/en/json-search-functions.html 。重试时间仍由严格UTC类型在Python核验，避免ISO字符串的字典序冒充时间比较。
- 已安装SQLAlchemy2.0.54 AsyncSession构造接受AsyncConnection bind；begin/close负责短事务但不拥有外部连接。租约每次写入均在同一连接的Session内重核拥有者，模型等待时无事务；没有把锁仅当作不同池连接写入前的一次性检查。
- 已安装OpenAI异常源码将结构化code放在APIStatusError.code；沿用项目1113判定，并按异常类型链识别本地AcceptanceLimitExceeded，SDK网络包装不应触发额外重试。未知异常只存固定安全说明，不把原始异常文本写入任务JSON。
- 固定CallbackHandler的on_chain_start/on_chat_model_start/on_tool_start/on_retriever_start均接收keyword-only metadata；本项目薄封装在每次start读取当前execution的最新意图，仍由官方Handler实现记录及usage，不在节点反复注册。
- SDK5.0.2的mask(data=...)处理SDK字段；mask_otel_spans(params=MaskOtelSpansParams)返回MaskOtelSpansResult，按OtelSpanIdentifier映射OtelSpanPatch，只修改导出属性、不原地改只读span。配置的SecretStr值及认证字段在两处遮盖，错误status_message也覆盖；固定源码为langfuse/types.py和_client/span_exporter.py。此处没有照搬旧SDK遮盖回调签名。

## 受限发布接口与HTTP错误（2026-10-20）

- 延用锁定SQLAlchemy2.0.54的短事务、已有KnowledgeRepository._insert、HybridKnowledgeJobs._write/ACK/readback；未凭新库猜接口。原知识锁名仍为ch03:+实际库名SHA256前48位，发布租约使用同名和独占连接；旧CLI与新发布互斥。
- SiliconFlow官方Embedding接口支持input字符串数组，故50份冻结语料按20批次只产生3次物理嵌入请求，无需缓存改造；BGE-M3输入上限8192，与原适配器一致：https://docs.siliconflow.cn/docs/api/embeddings-post 。未更改固定模型。
- 官方错误说明列401鉴权、403权限、429速率限制、503/504服务负载；发布采用401/403暂停、429和5xx有界5/30秒重试，参数/ACK/读回错误不自动重试：https://docs.siliconflow.cn/docs/userguide/capabilities/text-generation 。HTTP402作为计费拒绝的保守暂停分支，不宣称官方目前必定用它表示余额；无自由文本错误判断或自动换模型。

## 原生评估与受控调度（2026-10-20）

- Python3.13官方ZoneInfo文档明确Windows可能没有系统IANA数据，回退第一方tzdata；项目锁文件已带tzdata，继续Python3.13.13，不因文档标为3.13.16升级。03:00使用Asia/Shanghai的aware datetime，时钟注入可测：https://docs.python.org/3.13/library/zoneinfo.html 。
- LangChain官方模型接口说明ainvoke/astream和usage_metadata：https://docs.langchain.com/oss/python/langchain/models 。核对本工作区锁定chat_models.py及OpenAI适配器，使用独立每阶段callback采实际tokens，缺usage明确记estimated。真实SDK+MockTransport验证输出预算副本复用受控HTTP客户端、SDK零重试、同步调用入口在联网前拒绝。
- 锁定chat_models.py的agenerate在异常集合中用isinstance(res, Exception)筛选，CancelledError为BaseException，可再次触发AttributeError。请求钩子因此使用普通异常阻止外发，runner依据受管cancel_event恢复取消语义；未修改第三方库。双层账本和持锁验证均在实际HTTP请求钩子，端点指纹去凭据/查询串，恢复清理重核Milvus目标。

## 2026-10-20 验收补充核对
- 官方价格 https://docs.bigmodel.cn/cn/guide/start/pricing ：标准GLM5.3Flash每百万输入0.8/输出2.8/缓存0.23元；以日期版本标识刊例估算，非账单。
- ECB公开汇率 https://www.ecb.europa.eu/stats/eurofxref/eurofxref-daily.xml ：保留2026-10-19 EUR/USD1.1225及EUR/CNY7.4991原XML；CNY换USD按两者比例，不能直接把人民币写到Langfuse的USD字段。
- https://langfuse.com/docs/observability/features/token-and-cost-tracking 以及Python v5锁定源码 CallbackHandler.on_llm_end：在run detach之前补generation cost_details，根span.update写原问题/最终答；实际SDK exporter测试确认USD及独立CNY metadata。v5 SDK无prompt/output自动根IO兜底。
- https://docs.bigmodel.cn/cn/guide/start/migrate-to-glm-new ：low/high/max及默认max；评估继承线上low，输出预算不改。E46真实复验正常stop，不能外推所有样例都已修复。
