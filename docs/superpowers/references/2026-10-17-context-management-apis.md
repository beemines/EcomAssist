# ch07 · 官方接口核对记录

日期：2026-10-17。用户已批准本章以官方文档和锁定版本源码替代当前不可调用的Context7。以下是设计期核对，未修改产品实现，也不是测试报告。

## LangGraph：消息增量与持久化

- [add_messages 官方定义](https://reference.langchain.com/python/langgraph/graph/message/add_messages)：接收left/right，按消息ID合并，新ID追加、相同ID更新。引用的在线版本1.2.15与项目锁定版本相同。
- 本地`.venv/Lib/site-packages/langgraph/graph/message.py:64`签名：`add_messages(left: Messages, right: Messages, *, format: Literal["langchain-openai"] | None = None) -> Messages`。
- [Graph API 消息State](https://docs.langchain.com/oss/python/langgraph/graph-api)：State字段通过reducer处理节点增量。原始历史必须保留稳定SQL消息ID，不能把裁剪视图写回messages，也不能在每个节点重复回传全量历史。
- [Persistence](https://docs.langchain.com/oss/python/langgraph/persistence)：继续沿用thread/checkpointer，不新增跨会话记忆。现有SQLite saver锁定3.1.2，安装源码`aget_tuple(config)`、`aput(config, checkpoint, metadata, new_versions)`、`aput_writes(config, writes, task_id, task_path="")`与当前项目接线核对；后台摘要不并发篡改活跃图消息。
- [官方 Overwrite 用法](https://docs.langchain.com/oss/python/langgraph/use-graph-api#bypass-reducers-with-overwrite)：可绕过 reducer 直接设置完整值；同一 super-step 只允许一个覆盖写者。安装版本1.2.15的`langgraph/types.py:1050`含`Overwrite(value: Any)`。仅为旧checkpoint缺失较早SQL消息时建立完整、按SQL ID排序的初始化快照使用，不用于层级压缩或常规节点。单独的reference页抓取因content-type失败，实际依据为上述官方Graph API页及安装源码，未把失败页当作成功读取。

## LangChain：trim_messages

- [官方接口](https://reference.langchain.com/python/langchain-core/messages/utils/trim_messages)：支持自定义token_counter、strategy、allow_partial、start_on/end_on、include_system。在线页标v1.6.2，项目langchain-core锁定1.6.6，不能只按网页版本猜测。
- 本地`.venv/Lib/site-packages/langchain_core/messages/utils.py:1146`实参包括`messages, *, max_tokens, token_counter, strategy="last", allow_partial=False, end_on=None, start_on=None, include_system=False, text_splitter=None`。
- 拟在独立模型视图使用自定义校准计数器，并校验完整轮次/工具配对；最近层不允许截半条。trim_messages不用于删除checkpoint或SQL中的原始历史。

## SQLAlchemy：并发异步事务

- [AsyncSession 并发任务约束](https://docs.sqlalchemy.org/en/20/orm/extensions/asyncio.html#using-asyncsession-with-concurrent-tasks)：每个并发任务独立Session。官方2.0.54与项目相同。
- 摘要生成不持有聊天事务或数据库行锁；保存分段与推进覆盖边界放在独立短事务，并核对生成时的边界快照。具体锁/CAS接口在确定实施方案后继续核对，不把此处概述当成已写代码。
- 已补查[SQLAlchemy官方DML说明](https://docs.sqlalchemy.org/en/20/core/dml.html)，用于短事务内更新边界；实施具体`select(...).with_for_update()`及条件更新前仍须按实际使用的方法核对锁定版本签名。

## FastAPI：后台任务生命周期

- [lifespan 官方说明](https://fastapi.tiangolo.com/advanced/events/)：应用启动/关闭资源在同一生命周期内管理，项目已有该接线。拟用它拥有后台摘要任务及关闭清理，避免请求取消或应用退出留下无主任务。
- [BackgroundTasks](https://fastapi.tiangolo.com/tutorial/background-tasks/)在响应返回后运行。对于需要显式追踪并发、关闭和重启的摘要任务，设计优先采用应用拥有的异步管理器；不引入Celery、Redis或其他新组件。

## 当前模型窗口

官方智谱域名下精确搜索`GLM-5.3-Flash`未得到可用窗口规格。这不证明该模型不支持现有调用，也不作为更换模型的理由。窗口必须由部署配置明确给出，不能在设计文档中虚构已验证的供应商上限。既有密钥与模型保持，任何窗口默认值须在设计阶段交代依据。
