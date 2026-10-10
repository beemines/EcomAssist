# RAG 评估工作台实施计划 API 核对

日期：2026-10-10。用途：制定计划中的生命周期与事务边界；不表示已经实现或运行新后端。

## Context7 MCP 查询

沿用仓库 .cache/context7-request.ps1，以 query-docs 调用官方 Context7 MCP；仅发送公开库名和接口问题。原始结果存在忽略缓存。

| 查询 | 官方资料与计划结论 |
| --- | --- |
| /python/cpython，asyncio 与 msvcrt.locking | [asyncio 任务文档](https://github.com/python/cpython/blob/main/Doc/library/asyncio-task.rst)：后台任务要保留强引用；shield 保护内层任务，外层仍可能收到 CancelledError。不能把 shield 当成已清理或忽略取消的证明。 |
| /python/cpython，Windows 本地互斥 | [msvcrt 文档](https://github.com/python/cpython/blob/main/Doc/library/msvcrt.rst)：locking 锁从当前文件位置起的一段区域；LK_NBLCK 非阻塞，锁失败抛 OSError。计划用固定文件首字节与持有句柄实现 CLI/HTTP 排他，需真实子进程测试。 |
| /sqlalchemy/sqlalchemy，AsyncSession 事务 | [异步 ORM 文档](https://github.com/sqlalchemy/sqlalchemy/blob/main/doc/build/orm/extensions/asyncio.rst)：session.begin 管理短事务，flush 后可读取主键；每个并发任务独立 AsyncSession；expire_on_commit=False 与当前代码一致；独立引擎最终 dispose。 |
| /sqlalchemy/sqlalchemy，事务提交/回滚 | [事务文档](https://github.com/sqlalchemy/sqlalchemy/blob/main/doc/build/orm/session_transaction.rst)：事务成功提交，异常回滚。归属 manifest 应在 flush 后、commit 前持久化；callback 失败须使本批回滚。 |

缓存文件：context7-rag-plan-python-lifecycle-cpython.txt、context7-rag-plan-sqlalchemy-async.txt、context7-rag-plan-sqlalchemy-ownership.txt。先尝试 /websites/docs_python_org_3 时 Context7 返回库不存在；随后依据先前 resolve 结果改为 /python/cpython，得到官方文档。失败查询不作为 API 依据。

前一阶段的 FastAPI lifespan、Milvus 原生 BM25/hybrid_search、MDN 安全 DOM 查询仍是设计证据。实现各任务时继续先查具体 API 并核对锁定版本，不因最新文档引入未安装接口。

## 现有代码核对

- KnowledgeRepository.add_chunks 当前在 session.begin 内调用 _insert，_insert 执行 flush 返回主键；可用可选 before_commit 回调补持久归属，默认调用保持兼容。
- RetrievalService.retrieve 已接收冻结 QueryPlan，并分别保存 candidates 与 matches，50/10 上限存在；无需另造四套检索算法。
- 最终流守卫实际位于 app/core/answer_validation.py，复用 FinalAnswerStream、ensure_answer_active、close_answer_stream、validate_answer；不创建另一套流成功判断。
- 计划中的线上回归文件 tests/test_sufficiency.py、旧评估 tests/test_retrieval_evaluation.py 已核实存在。
- 新运行管理采用本地 OS 文件锁，与 app/knowledge/locking.py 的 MySQL 作业命名锁职责不同；不把既有库锁当成 HTTP/CLI 跨进程运行锁。

本次资料归档和计划检查不产生模型费用、不写业务知识库，也不代替后续代码 RED/GREEN 或真实试运行。

## 原始 300 题归档

从当前会话已读取的用户原消息（turn_id：01a120a8-a009-71e3-a5a3-26e964928679）截取六列 CSV，保存 evals/datasets/merchant-rag-300/original.csv。正文保持用户原始问题和标签，UTF-8、LF；不把发现的问题直接改进原表。

现场核验为 300 行、300 个唯一 ID，A_policy/B_model/C_colloquial/E_multi/D_absent 各 60 行；与提取原文逐字节一致。SHA-256 为 1c145124f298dc224210016e89bf3f1ed619bf18dea5f544616ebd4713053a09。此核验只证明原文归档，尚不证明题目标准答案正确；逐题审标是实施任务 1。

## 联合裁判 API 实现前预查（2026-10-10）

任务2进行时，控制端只读预查任务3的具体接口，没有提前修改其生产代码。通过Context7先resolve LangChain，再查询 /websites/reference_langchain 的 ChatOpenAI.with_structured_output、/pydantic/pydantic 的严格模型校验、/python/cpython 的 asyncio 超时与取消。原回包保存于忽略缓存 .cache/context7-workbench-judge-{langchain,langchain-raw,strict-pydantic,timeout}.txt，任务3代理在使用前必须读取完整回包及核对安装接口。

- [ChatOpenAI API](https://reference.langchain.com/python/langchain-openai/chat_models/base/ChatOpenAI/with_structured_output)说明include_raw返回raw/parsed/parsing_error；应使用原始AIMessage的finish_reason判定正常结束，不能仅信parsed。
- [Pydantic模型文档](https://github.com/pydantic/pydantic/blob/main/docs/concepts/models.md)区分默认转换与strict校验；字符串布尔不能当严格布尔。回包混有v1示例，不能将其直接搬进v2实现。
- [CPython超时文档](https://github.com/python/cpython/blob/main/Doc/library/asyncio-task.rst)区分局部超时转换的TimeoutError与外部取消；外部取消不能被一般错误处理吞掉。

只读importlib.metadata/inspect核实实际安装：langchain-core1.6.6、langchain-openai1.6.7、Pydantic2.13.5，与锁文件一致。安装的ChatOpenAI.with_structured_output默认method='json_schema'；Context7回包的一段示例写function_calling，因此不能凭那段默认值接入。后续实现需显式选择项目既有兼容方法并验证raw字段，不依赖默认值，不升级依赖或改模型。检查没有构造模型实例、读取.env或发出模型请求；解释器既存miniconda定位提示仍如实记录。

## 运行文件与 OS 文件锁实现前预查

任务3执行时，控制端经 Context7 `/python/cpython` 查询任务4的原子替换、路径和文件锁接口，原回包保存在 `.cache/context7-workbench-store-locking.txt`。默认网络沙箱拒绝套接字后，公开文档查询经窄范围提升成功；没有发送用户密钥或项目正文。

- [os.replace](https://github.com/python/cpython/blob/main/Doc/library/os.rst) 成功时原子替换；临时文件必须与目标同文件系统，跨文件系统失败不能覆盖旧快照。
- [msvcrt.locking](https://github.com/python/cpython/blob/main/PC/msvcrtmodule.c) 从当前文件位置锁定指定字节，`LK_NBLCK` 失败抛 `OSError`。固定首字节、保持句柄，不以 PID 删除重建锁文件；真实子进程测试验证进程退出释放。
- [fcntl.flock](https://github.com/python/cpython/blob/main/Doc/library/fcntl.rst) 的 `LOCK_EX | LOCK_NB` 提供 Unix 对应分支。当前验收以 Windows 安装运行时为准。

冻结接口衔接：隔离导入取得物理主键前，只在 manifest 保存计划 case keys；缺少的计划记录计为未执行。取得 id_map 后执行器再保存严格完整的 CaseRecord，不伪造金标主键。初始化失败保留计划数和错误；公共运行配置与清理结果单独白名单投影，不能绕过 report.py 的裁判快照过滤。

## 隔离向量资源实现前预查

控制端提前经 Context7 `/milvus-io/milvus-docs` 查询集合生命周期、显式主键upsert与原生BM25，结果在 `.cache/context7-workbench-resource-milvus.txt` 和 `-milvus-lifecycle.txt`。锁文件及项目依赖为 SQLAlchemy2.0.54 / PyMilvus3.0.2 / HTTPX0.28.1；实现者仍需核对安装的 AsyncMilvusClient 方法签名，不照搬不适用示例。

- [BM25混合RAG集合](https://github.com/milvus-io/milvus-docs/blob/v3.0.x/site/en/aiTools/rag_pipeline.md)在建集合时声明文本分析器、BM25函数和稀疏索引；本项目复用既有chinese analyzer集合实现，不替换成示例standard。
- [upsert](https://github.com/milvus-io/milvus-docs/blob/v3.0.x/site/en/userGuide/insert-and-delete/upsert-entities.md)按显式主键幂等写入；[drop_collection](https://github.com/milvus-io/milvus-docs/blob/v3.0.x/site/en/userGuide/collections/drop-collection.md)接收精确collection_name。不能按前缀批删或调用旧query_data/delete_by_pk示例。
- 回包混有旧客户端API和同步示例，另有连接超时单位表述；这些不证明当前异步客户端签名或单位。沿用既有5秒服务期限并读取安装实现核对；真实哨兵和中断测试仍是后续验收。

资源事务与清理追加预查 `.cache/context7-workbench-resource-sqlalchemy.txt` / `-cancellation.txt`：SQLAlchemy官方事务说明flush不提交、异常必须rollback/close；本次回包主要是同步示例，异步用法结合前面已保存的官方AsyncSession文档和安装签名核对。CPython官方说明CancelledError须在清理后传播、后台Task保留强引用、timeout取消内层等待；shield本身不代表所有资源清理已经结束。后续资源owner逐项限时清理并汇总错误，manager持锁至清理和终态持久化完成。

## 实际请求计数与流实现前预查

Context7先resolve HTTPX得到支持0.28.1的 `/encode/httpx`，再查询 `/encode/httpx/0.28.1`，保存 `.cache/context7-workbench-httpx-{resolve,hooks}.txt`。官方[事件钩子](https://github.com/encode/httpx/blob/0.28.1/docs/advanced/event-hooks.md)说明request在请求准备后、网络发出前运行，AsyncClient的hook必须async；[异步文档](https://github.com/encode/httpx/blob/0.28.1/docs/async.md)说明手动创建客户端最终await aclose。采用资源owner单一序列化计数器，执行器借用stage上下文，不由各题get再update推算。

Context7 `/websites/reference_langchain` 的ainvoke/astream结束元数据预查保存在 `.cache/context7-workbench-runner-stream.txt`。官方API定义astream返回AsyncIterator[AIMessageChunk]、末块response_metadata.finish_reason为stop；回包另混有await astream示例，必须以安装1.6.x形状及现有FinalAnswerStream调用核对，不能凭示例引入错误await。正常结束守卫继续复用，length/缺stop不视为有效回答。

任务5只读核对发现PyMilvus3.0.2单次方法包含握手、DescribeCollection/Upsert和可能的schema刷新重放，方法层次数不能冒充RPC次数。资源owner采用本客户端专属的最小固定版本连接/handler适配，在初始及重连channel安装grpc.aio拦截器；不全局patch或升级依赖。实现者须另查官方grpc接口并核对安装签名、验证实际本地RPC计数；固定版本私有接缝的维护约束会在实现报告披露。

补充gRPC预查与版本边界：任务5在实现前使用Context7定向查询grpc Python aio，缓存为context7-workbench-grpc-{resolve,interceptor,aio,python-resolve,python-aio}.txt。回包仍混有同步/Go片段，没有拿它们替代异步接口定义；结合安装官方grpc1.84.0的aio channel/continuation/close源码、PyMilvus3.0.2的连接/重放/重连接缝核对，并用本机真实gRPC服务观察实际RPC序列。局部适配严格固定3.0.2，不升级或全局补丁；若SDK变化须复核。官方[Python AsyncIO文档](https://github.com/grpc/grpc/blob/master/doc/python/sphinx/grpc_asyncio.rst)确认aio生命周期体系，不能把sync intercept_channel范例套入aio。

独立审查针对已安装重连代码发现：新channel在握手及发布锁等待前创建，外部CancelledError可能先于SDK发布到当前channel。资源拥有者必须追踪所有新建/退休/未发布通道，关闭不能只看当前通道或假设shield已结束。局部修复以真实channel两处取消和失败回归验证，所有close任务由同一owner强引用并等待，清理失败纳入结果；这一固定版本维护约束与审查结论保存在实施记录中。
## 运行管理与API后续实现前预查

任务6执行时，控制端提前通过Context7保存workbench-manager-task-lifecycle、workbench-api-lifespan、workbench-api-download原回包。CPython官方明确create_task须保留强引用、取消是协作式、CancelledError继承BaseException；最新签名包含更新版本选项，后续必须按安装3.13.5核对，不能跨版本照搬。FastAPI官方[lifespan](https://fastapi.tiangolo.com/advanced/events)由异步上下文拥有startup/shutdown，TestClient上下文验证全生命周期；不以请求BackgroundTasks持有评估资源。[FileResponse接口](https://fastapi.tiangolo.com/reference/responses)提供path、filename、media_type等参数，导出仍只采用固定受控路径和白名单内容。uv.lock为FastAPI0.142.2/Starlette1.7.0/Uvicorn0.54.0，具体使用前须查安装版本及缺少的参数校验资料。没有提前写Task7/8生产代码。
## 工作台 API 参数约束预检（Task 8 实现前）

2026-10-10 通过 Context7 MCP 查询 FastAPI 与 Pydantic 官方文档，完整回包保存于 `.cache/context7-workbench-api-query.txt`、`.cache/context7-workbench-api-pydantic.txt`。FastAPI 的 Query 模型支持 `Annotated[FilterParams, Query()]`、`extra=forbid`、整数范围与字符串长度约束；该功能自 0.115.0 提供，锁定 0.142.2 可用。Pydantic 模型须明确 `ConfigDict(extra="forbid")`，默认会忽略未知字段。分页 URL 参数本身是字符串，不能把 strict=True 整体照搬而拒绝合法的 offset/limit；JSON 请求字段可用严格约束。服务端按独立 Host/Origin 白名单拒绝收费写请求；返回错误使用白名单，不能把验证输入或异常原文直接回显。Task 8 仍需核对实际安装签名及原应用 lifespan 资源归属；这次查询没有修改生产代码。

## 工作台前端轮询与详情预检（Task 9 实现前）

Context7 `/mdn/content` 回包存于 `.cache/context7-workbench-ui-polling.txt`，结合原有 `context7-rag-admin-frontend-dom.txt`：正文采用 createElement/textContent；fetch 先验证 HTTP 状态再解析 JSON；轮询必须清除定时器，详情用原生 dialog.showModal()/close() 并恢复触发按钮焦点。回包混有 setHTMLUnsafe 示例，与本项目安全展示要求不符，不能照搬。页面卸载终止轮询、异步旧响应不覆盖新选择，具体实现时按浏览器实际支持与固定 API 契约验收。
