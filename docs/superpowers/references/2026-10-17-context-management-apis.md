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

- [AsyncSession 并发任务约束](https://docs.sqlalchemy.org/en/20/orm/extensions/asyncio.html#using-asyncsession-with-concurrent-tasks)：每个并发任务独立Session。项目锁定2.0.54；计划阶段重查官方2.0页已标2.0.55，实际用法仍核对本地2.0.54，不跟随网站版本自动升级。
- 摘要生成不持有聊天事务或数据库行锁；保存分段与推进覆盖边界放在独立短事务，并核对生成时的边界快照。具体锁/CAS接口在确定实施方案后继续核对，不把此处概述当成已写代码。
- 已补查[SQLAlchemy官方DML说明](https://docs.sqlalchemy.org/en/20/core/dml.html)，用于短事务内更新边界；实施具体`select(...).with_for_update()`及条件更新前仍须按实际使用的方法核对锁定版本签名。

## 计划阶段补充核对

- [FOR UPDATE官方接口](https://docs.sqlalchemy.org/en/20/core/selectable.html#sqlalchemy.sql.expression.Select.with_for_update)：当前网页为2.0.55；本地2.0.54的`sql/selectable.py:4009`签名为`with_for_update(self, *, nowait=False, read=False, of=None, skip_locked=False, key_share=False)`。计划只用无参数行锁，不把其他数据库的NOWAIT行为套到MySQL。
- [MySQL8.4隐式提交](https://dev.mysql.com/doc/refman/8.4/en/implicit-commit.html)：项目compose同为mysql:8.4；ALTER TABLE等DDL会隐式提交，迁移必须识别部分完成状态，不宣称包在SQLAlchemy事务里就能整体回滚。
- [CompiledStateGraph官方成员列表](https://reference.langchain.com/python/langgraph/graph/state/CompiledStateGraph)确认历史读取继承`aget_state_history`；锁定1.2.15的`pregel/main.py:1554`为`aget_state_history(config, *, filter=None, before=None, limit=None) -> AsyncIterator[StateSnapshot]`，SQLite saver3.1.2的`aio.py:448`为`alist(config, *, filter=None, before=None, limit=None) -> AsyncIterator[CheckpointTuple]`。GET历史装饰器使用真实方法，不能编造`alist_state_history`。旧graphs/锚点地址及单方法页抓取失败已区分，不能把这些失败页计为签名核对成功。
- 本次工具元数据重新检查仍无Context7，继续使用本章已批准的官方资料＋锁定源码方式。真实费用HTTP钩子的用法在任务10实现前另核对HTTPX0.28.1官方事件钩子和安装签名。

## 任务1实施前：Pydantic显式配置与别名

- [BaseModel官方属性](https://pydantic.dev/docs/validation/latest/api/pydantic/base_model/)及[Settings环境变量命名](https://pydantic.dev/docs/validation/latest/concepts/pydantic_settings/)已先读取；旧docs.pydantic.dev地址重定向到该官方站点，不以站点latest标签替代本地版本核对。
- 本地pydantic2.13.5的`main.py:307`：`model_fields_set(self) -> set[str]`返回显式赋值字段（非默认填充）；pydantic-settings2.15.0的`main.py:132/193`确认现有BaseSettings构造入口。新旧工具步数别名以及“缺省推导/显式费用上限”需要区别默认值与显式环境值，不能仅比较是否等于旧默认数值。具体新增validator仍需实现者按实际使用接口核对，不借此改动未接线的旧消费者。

## FastAPI：后台任务生命周期

- [lifespan 官方说明](https://fastapi.tiangolo.com/advanced/events/)：应用启动/关闭资源在同一生命周期内管理，项目已有该接线。拟用它拥有后台摘要任务及关闭清理，避免请求取消或应用退出留下无主任务。
- [BackgroundTasks](https://fastapi.tiangolo.com/tutorial/background-tasks/)在响应返回后运行。对于需要显式追踪并发、关闭和重启的摘要任务，设计优先采用应用拥有的异步管理器；不引入Celery、Redis或其他新组件。

## 当前模型窗口

官方智谱域名下精确搜索`GLM-5.3-Flash`未得到可用窗口规格。这不证明该模型不支持现有调用，也不作为更换模型的理由。窗口必须由部署配置明确给出，不能在设计文档中虚构已验证的供应商上限。既有密钥与模型保持，任何窗口默认值须在设计阶段交代依据。

## 任务2实施：独立Session、唯一键冲突与MySQL默认值

- 实施前重读[SQLAlchemy异步并发约束](https://docs.sqlalchemy.org/en/20/orm/extensions/asyncio.html#using-asyncsession-with-concurrent-tasks)、[IntegrityError与原始DBAPI异常](https://docs.sqlalchemy.org/en/20/core/exceptions.html#sqlalchemy.exc.IntegrityError)和[MySQL8.4隐式提交](https://dev.mysql.com/doc/refman/8.4/en/implicit-commit.html)。网页SQLAlchemy为2.0.55，实际使用锁定2.0.54，不升级依赖。
- 锁定源码`sqlalchemy/sql/selectable.py:4009`再次确认无参`with_for_update()`；`ext/asyncio/session.py:779/940`确认`await flush()`与`async with session.begin()`；`exc.py:550`附近确认DBAPI异常保存在`orig`；PyMySQL1.2.3的`constants/ER.py:64`定义`DUP_ENTRY=1062`。只在上下文退出、事务回滚后把1062转成None竞争结果，其他完整性错误继续抛出。
- MySQL服务器生成的`created_at`在flush后可能仍未加载，不能同步属性访问触发异步惰性IO。真实3308测试复现MissingGreenlet后，改用已有显式异步SELECT读取整段集合，再构造不可变返回值；不依赖MySQL未提供的INSERT RETURNING，也不加入新Session共享。
- MySQL把ORM编译的INTEGER规范为INT；锁定`dialects/mysql/base.py:2470`确认INTEGER编译规则。用户SQL中seq仍原样INT、有符号，映射只做该同义类型比较，不能误改成INT UNSIGNED。
- 两个用户DDL原文由控制者补入本计划scratch/task-2-user-ddl.md，实施文件`sql/ch07.sql`与`sql/ch07-layers.sql`保留其完整字段、中文注释、SET NAMES、索引、顺序及无FK设计。迁移契约从这些SQL读取，先核验全部已有结构再执行缺失项；不宣称事务能回滚已提交DDL。
