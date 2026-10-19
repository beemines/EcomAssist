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
