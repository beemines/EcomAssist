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
