# 第三步源码解析：Dense 知识库

前两步已经让客服能接收消息、保存会话、提取售后字段，再由模型申请工具、执行工具并把结果接回回答。第三步补的是工具背后的知识来源：一份 Markdown 怎么切成知识块，怎么经过嵌入和双写进入检索链路，历史对话里的通用问答又怎么进入同一条链。

这一步新开的是 `app/knowledge/`，离线建库和挖知识集中在这里；在线入口仍接第二步的 `query_faq`。下面按 master 的固定提交 `4f354f1c5fc71f4941e06c1e984a4ab5eb7721d6` 走读，前两步的模型工厂、结构化输出校验和工具执行器仍是被复用的基础，第三步没有把它们重新实现一遍，也没有混合检索或重排分支。

## 模块概览

| 文件 | 规模 | 职责 |
| --- | --- | --- |
| `app/knowledge/embeddings.py` | 64 行 | 硅基流动嵌入客户端与向量形状校验 |
| `app/knowledge/chunking.py` | 258 行 | 标题、FAQ、正文、围栏和表格切分 |
| `app/knowledge/types.py` | 89 行 | 知识类型、存储边界、三字段嵌入文本 |
| `app/knowledge/ingestion.py` | 11 行 | 整份文档校验后写 pending |
| `app/knowledge/migration.py` | 79 行 | 执行原 DDL，核对已有 MySQL schema |
| `app/knowledge/locking.py` | 57 行 | 离线任务共享的数据库命名锁 |
| `app/knowledge/vectorization.py` | 32 行 | pending 批处理、upsert 与 done 回填 |
| `app/knowledge/vectors.py` | 113 行 | 显式 Dense 集合、主键回包与 Top3 检索 |
| `app/knowledge/history.py` | 57 行 | 北京时间窗口内的已结束会话读取 |
| `app/knowledge/extraction.py` | 75 行 | 通用 QA 结构化提取与来源验证 |
| `app/knowledge/mining.py` | 62 行 | 批次身份、暂存、全局精确去重 |
| `app/knowledge/cli.py` | 107 行 | 迁移、导入、挖掘和每日任务入口 |
| `app/repositories/knowledge.py` | 125 行 | MySQL 原文、状态、邻块和暂存事务 |
| `app/repositories/faq.py` | 26 行 | Dense 召回后回 MySQL 取原文 |
| `app/db/models.py` | 90 行 | 六张表映射，本步增加知识块与 QA 暂存 |
| `app/tools/business.py` | 45 行 | 保留 `query_faq` 工具契约 |
| `app/main.py` | 104 行 | 应用生命周期内创建和释放检索资源 |
| `sql/ch03-ddl.sql` | 43 行 | 两张知识表的权威 DDL |
| `compose.milvus.yaml` | 87 行 | 本机 Milvus Standalone 及依赖服务 |
| `scripts/run-knowledge-daily.ps1` | 34 行 | 固定目录的每日任务启动与日志 |
| `knowledge-docs/demo-policy.md` | 13 行 | 合成政策示例 |
| `knowledge-docs/demo-faq.md` | 10 行 | 合成多问法 FAQ 示例 |
| `knowledge-docs/demo-manual.md` | 17 行 | 合成操作步骤和状态表示例 |
| `evals/evaluate_knowledge.py` | 223 行 | 实际嵌入、召回与应用回答验收 |
| `evals/evaluate_qa.py` | 107 行 | 合成会话 QA 标注评估 |
| `evals/knowledge_recovery.py` | 291 行 | 自建进程的两处实际中断恢复验收 |

规模按上述固定提交中 `git show <ref>:<文件>` 的完整行数统计，含空行和注释；共享文件列的是整文件规模。这个包把“知识怎么进库”独立出来，在线客服只需要一个可检索的仓储。

## 先验一件事：嵌入上游和维度

### `evaluate`：建库前的探针

文件：`evals/evaluate_knowledge.py`，以下是导入文档之前的连续选摘。

```python
                probe = await embedder.embed(['邮费是多少'])
                report['actual_embedding_dimensions'] = len(probe[0])
                await index.ensure_collection()
                report['schema_verified'] = True
```

探针放在实际验收入口里：先发一条合成问题，再核对集合，之后才导入三份 demo 文档。验证记录中这一步确实取得了 1024 维向量，1024 同时约束回包和 Milvus schema。模型在 `Settings` 中限定为 `BAAI/bge-m3`，实际请求直达硅基流动 embeddings 接口；聊天模型仍沿用前两步的模型工厂。

### `SiliconFlowEmbedder.embed`：复用客户端，核对回包

文件：`app/knowledge/embeddings.py`。

```python
    def __init__(self, settings: Settings, *, http_client=None):
        self.settings = settings
        self._owns_client = http_client is None
        self._client = http_client if http_client is not None else httpx.AsyncClient()
```

客户端跟着 embedder 实例走，不是每条文本新建一次连接池。外部注入的 HTTP 客户端归调用方，自建客户端才由 `aclose` 关闭；CLI 和应用 lifespan 都会登记清理回调。

```python
        response = await self._client.post(
            'https://api.siliconflow.cn/v1/embeddings',
            headers={'Authorization': f'Bearer {key.get_secret_value()}'},
            json={'model': self.settings.embedding_model, 'input': texts, 'encoding_format': 'float'},
            timeout=self.settings.embedding_timeout_seconds,
        )
```

一个 `embed` 口子同时接批量建库和单条在线问题。它先检查 Key 非空、输入确实是非空文本，再发请求；上游 HTTP 错误直接传播，适配器没有额外重试循环。

回包也不能照列表顺序直接拿。函数要求返回条数与输入一致，逐项检查 `index` 是有效、不重复的整数，最后按输入位置重新排序。即使上游把第 1 条排在第 0 条前面，向量也不会配错正文。

```python
def validate_vector(vector: list[float]) -> list[float]:
    if not isinstance(vector, list) or len(vector) != 1024:
        raise ValueError('embedding must contain exactly 1024 numbers')
    result = []
    for value in vector:
        if type(value) not in (int, float):
            raise ValueError('embedding values must be finite numbers')
```

后半段还会转为浮点数并用 `math.isfinite` 排除 NaN、Inf 和溢出。这里用精确的 `type` 判断，连 Python 中属于整数子类的 `bool` 也不接受。维度、数量或数值不合法就失败，不能让一批坏向量进入库后才发现。

## 切块：标题、长段落、整句重叠和表格

### `_sections`：先沿标题层级分小节

文件：`app/knowledge/chunking.py`，以下选摘标题分支。

```python
            level = len(heading[1])
            title = re.sub(r"[ \t]+#+[ \t]*$", "", heading[2] or "").strip()
            while stack and stack[-1][0] >= level:
                stack.pop()
            stack.append((level, title))
```

本项目没有调用 MarkdownHeaderTextSplitter，而是维护一个 ATX 标题栈，支持一到六级 `#`。遇到同级或更高层标题，先弹掉旧分支；遇到子标题，再压进去。`# 售后 → ## 退货 → #### 例外` 会得到“售后/退货/例外”，跳级也保留实际父路径。

标题离开正文，但路径会跟小节一起产出。围栏中的 `#` 不走标题分支，代码里的注释仍是代码；反引号与波浪线围栏都由 `_fence_state` 跟踪。它是有范围的解析器，不承诺覆盖完整 CommonMark。

### `_answers`：从块到整句的两层切分

文件：`app/knowledge/chunking.py`，以下连续选摘非表格分支。

```python
        units = [(value, False)] if kind == "code" or len(value) <= target else _sentences(value)
        for unit_index, (unit, _) in enumerate(units):
            separator = "\n\n" if unit_index == 0 else ""
            if current and len(current + separator + unit) > target:
                yield current.strip()
                suffix = _suffix(prose, overlap) if kind != "code" else ""
                current = suffix if len(suffix + separator + unit) <= target else ""
                prose = current
```

这里把切分粒度从段落降到句子：`_blocks` 先认正文段落、代码围栏和表格，短段落整段装进当前块，长段落才交给 `_sentences`。源码没有递归调用、字符分隔符清单或最后逐字硬切那一级。

默认目标是 1200 字符，重叠预算是 120 字符。目标不是硬上限：一条超长但不可继续分句的正文、完整代码块或一行表格都可以整条保留。若最终超出 MySQL TEXT 的 65535 UTF-8 字节限制，`ChunkDraft` 会拒绝，错误带文档与章节，整份文档不落库；不会截掉尾部凑长度。

`_sentences` 留住句末标点、闭合引号和空白，价格 `8.50` 不会被小数点拆成两句，`[!IMPORTANT]` 的感叹号也不会误当句末。这些细节都有切分测试对应，不是靠“中文大概能切”来验收。

### `_suffix`：只接预算内的完整句子

文件：`app/knowledge/chunking.py`。

```python
def _suffix(text: str, limit: int) -> str:
    result = ""
    for sentence, complete in reversed(_sentences(text)):
        if not complete or len(sentence + result) > limit:
            break
        result = sentence + result
    return result.strip()
```

它从正文末尾往前取整句，遇到未完成句或超过重叠预算就停止。单句超过 120 字符时不复制该句，原句仍在前块完整保留；下一块容不下“后缀＋新句”时也放弃重叠。这里没有“第一句无论多长都强收”的例外。

`prose` 只积累连续正文，代码和表格边界会清空。开发记录里曾出现关闭围栏被带进下一块的问题，当前实现把正文后缀单独记账，就是为了不从混合块里捞出孤立的代码标记。

### `_blocks`、`_answers`：表格按完整行切

文件：`app/knowledge/chunking.py`，以下选摘表格装块循环。

```python
            table = value
            has_row = False
            for row in rows:
                if has_row and len(table) + 1 + len(row) > target:
                    yield table
                    table, has_row = value, False
                table += "\n" + row
                has_row = True
            if has_row:
                yield table
```

`value` 已经是表头和分隔行，每次换块都从它重新开始。因此“待受理”那一行无论落在哪块，都仍带着“状态/演示说明”的列名。按字符目标累积整行，不是固定每表若干行；数据行不会因为复制表头而重复。

识别表格前，`_cells` 会跳过反斜线转义和 backtick 代码跨度里的竖线，`\|` 或 `` `代码|内容` `` 不会被认成额外列。表格前的说明先作为正文处理，表后继续处理正文；空表只有表头时不产出知识块。

## 组装字段：标题有去处，元数据不进向量

### `_qa_groups`、`chunk_markdown`：FAQ 用真实问法

文件：`app/knowledge/chunking.py`，以下选摘小节组装。

```python
            groups = _qa_groups(body, path[-1]) if content_type == "faq" else [(path[-1], body)]
            for questions, answer in groups:
                for part in _answers(answer, target_chars, overlap_chars):
                    chunks.append(ChunkDraft(category="/".join(path[:-1]) or document_name,
                                             questions=questions, answer=part, section_path=section_path,
                                             content_type=content_type,
                                             is_key_clause=_important(part)))
```

政策和手册没有天然问句，最后一级标题进 `questions`，上级路径进 `category`，完整路径进 `section_path`。没有上级时分类退回文件名；没有标题时文件名还会充当标题和路径。

FAQ 多走一层显式 `Q:`/`问：` 与 `A:`/`答：` 分组。连续多个问题是同一答案的不同问法，换行存入 `questions`；开始下一个问答组才分开。`demo-faq.md` 中“邮费是多少？”和“快递费用怎么收？”就是这样保留下来的。任意显式空问法或空答案都会拒绝整份文档，中间组与最后一组规则相同。

关键条款不靠搜“运费”“退货”猜出来。`_important` 只识别围栏外明确的 `> [!IMPORTANT]`，所以普通正文提到“重要”不打标，代码示例里的同一标记也不打标。

### `embedding_text`：只有三格变成语义

文件：`app/knowledge/types.py`。

```python
def embedding_text(chunk: ChunkDraft | ChunkRecord) -> str:
    return f"category: {chunk.category}\nquestions: {chunk.questions}\nanswer: {chunk.answer}"
```

字段名和正文一起传给嵌入模型。章节路径、内容类型、关键条款标记、前后块指针只是 MySQL 元数据，不参与向量。`ChunkDraft.__post_init__` 提前核对 category 255 字符、section_path 512 字符，以及 questions/answer 的 TEXT 字节上限。校验整个切分结果之后才会写库，后面一节失败不会留下前面半份文档。

## 落库与向量库：各守一份职责

### `migrate`：执行原 DDL，已有表必须比对

文件：`app/knowledge/migration.py`，以下选摘表存在性处理。

```python
        if existing and existing != {table.name for table in _TABLES}:
            raise RuntimeError("partial knowledge schema; explicit repair required")
        if not existing:
            # This fixed user script has no delimiters or semicolons inside literals.
            ddl = re.sub(r"(?m)^--.*$", "", _DDL.read_text(encoding="utf-8"))
            for statement in ddl.split(";"):
                if statement.strip():
                    await connection.exec_driver_sql(statement.strip())
        await _check(connection)
```

MySQL 的权威脚本仍是 `sql/ch03-ddl.sql`，ORM 在 `app/db/models.py` 映射它。两张表都不存在才执行脚本；只存在一张拒绝自动补齐；都存在就校验，不用 `create_all` 把差异遮过去。

`_check` 核对目标数据库、列顺序、类型、默认值、注释、索引、外键及引用数据库。曾有一次把 ENUM 字面值跟 SQL 语法一起转小写，错把 `Kept` 当作 `kept`；现在 `_normalize` 保留引号内的字面内容。状态拼错不能被“规范化”成合法 schema。

DDL 的分工很清楚：`knowledge_chunks` 保存原文、元数据和 pending/done，`qa_extraction_staging` 保存模型抽取的问答及来源。MySQL 原文是权威源；Milvus 只保留检索身份和向量。

### `MilvusIndex.ensure_collection`：显式 schema，FLAT/COSINE/Strong

文件：`app/knowledge/vectors.py`，以下选摘建集合分支。

```python
            schema = AsyncMilvusClient.create_schema(auto_id=False, enable_dynamic_field=False)
            schema.add_field('id', DataType.INT64, is_primary=True, auto_id=False)
            schema.add_field('embedding', DataType.FLOAT_VECTOR, dim=1024)
            indexes = AsyncMilvusClient.prepare_index_params()
            indexes.add_index(field_name='embedding', index_name='embedding', index_type='FLAT', metric_type='COSINE', params={})
            await client.create_collection(self.collection, schema=schema, index_params=indexes,
                                           consistency_level='Strong', timeout=self.timeout)
```

最要紧的是 `auto_id=False`：Milvus 主键直接使用 MySQL chunk id。同一知识块重跑时覆盖同一主键，恢复就不需要再找一份随机生成的 vector id。MySQL 虽然是 unsigned BIGINT，进入共享边界仍限制为正 INT64，避免越过 Milvus 能表示的范围。

集合恰好两个字段，索引固定为 FLAT/COSINE，读写一致性明确要求 Strong。已有集合也会 describe 并核对字段、维度、主键、动态字段和唯一索引，发现漂移就拒绝；`_ready` 只是在该实例完成校验后的缓存。

`compose.milvus.yaml` 固定 Milvus 3.0.2 Standalone，配 etcd、MinIO 和独立具名卷，Milvus 两个宿主端口绑定 `127.0.0.1`。本步使用异步 PyMilvus 客户端，没有同步客户端的线程执行器，也没有 sparse、BM25、AUTOINDEX 或混合召回字段。

## pending 双写：按主键恢复，不假装跨库事务

### `import_document`、`_insert`：先提交一份完整 pending

文件：`app/knowledge/ingestion.py`。

```python
async def import_document(path: Path, content_type: str, repository: KnowledgeRepository) -> list[int]:
    """Validate the whole UTF-8 document before the one atomic pending insert."""
    drafts = chunk_markdown(path.read_text(encoding="utf-8-sig"), document_name=path.stem,
                            content_type=content_type)
    return await repository.add_chunks(drafts, link_neighbors=True)
```

UTF-8 BOM 可接受，整份读取和切块发生在事务之前。仓储 `_insert` 先 add/flush 取得自增 id，再链接这次文档内的 prev/next，第二次 flush 后与插入一起提交。邻块写入失败会整份回滚，不会剩下有正文却少指针的半成品；不同导入之间也不会串成邻居。

### `PendingVectorizer.run`：网络结束后再回填

文件：`app/knowledge/vectorization.py`，以下选摘批处理后半段。

```python
            vectors = await self.embedder.embed([embedding_text(record) for record in records])
            if not isinstance(vectors, list) or len(vectors) != len(records):
                raise ValueError('embedding count differs from pending chunks')
            rows = list(zip(ids, [validate_vector(vector) for vector in vectors]))
            actual = await self.index.upsert(rows)
            validate_acknowledged_ids(actual, ids)
            # Every network operation is finished before this short MySQL transaction.
            await self.repository.mark_done(ids)
            count += len(ids)
```

前半段先拒绝非正整数 batch_size，再按 id 顺序取一批 pending，验证主键有效且不重复。每批嵌入、upsert、校验确认主键全部结束，才调用短 MySQL 事务；不会开着事务等待云端模型。

`MilvusIndex.upsert` 检查实际 upsert_count 和返回主键，SDK 的 Sequence 主键容器先转成 list；`validate_acknowledged_ids` 再要求数量、唯一性和主键集合完全一致。少一条、错一条或回包丢失都不会标 done。`mark_done` 锁住整批行，确认行齐全后写 `vector_id=str(id)` 和 `done`。

### `child`：两个中断窗口为什么都能补齐

文件：`evals/knowledge_recovery.py`，以下是第二个窗口的连续选摘。

```python
                        async def upsert(self, rows):
                            acknowledged = await index.upsert(rows)
                            await pause_at(args.checkpoint, {'phase': args.mode,
                                'owned_pid': __import__('os').getpid(), 'ids': ids,
                                'acknowledged_ids': acknowledged, 'upsert_returned': True})
                            return acknowledged
```

第一个窗口是 MySQL pending 已提交、还没向量化：重启重新读 pending，照常嵌入和 upsert。第二个窗口是实际 Milvus upsert 已返回、还没 mark_done：MySQL 仍是 pending，重启再 upsert 同一批 id，然后回填。这里保证的是每个主键只有一条有效可查询记录，不是没有任何物理历史版本。

验收入口只终止自己创建、且 checkpoint PID 与 Popen PID 相等的 worker，再启动正常 worker；不是只抛一个异常来代替断进程。首次 Windows venv 转发导致两个 PID 不同，验收按设计拒绝，后来改用实际 base 解释器，没有放宽身份检查。已有报告证明两个窗口均恢复，正文哈希不变、主键无重复，再跑向量化返回 0。

## CLI：恢复可重跑，文档导入有边界

### `run`、`job_lock`：所有离线写动作共用一把锁

文件：`app/knowledge/cli.py`、`app/knowledge/locking.py`，以下选摘 CLI 外层。

```python
        async with job_lock(database), AsyncExitStack() as resources:
            repository = KnowledgeRepository(database)
```

`migrate`、`import-document --path --type`、`init-vectors`、`vectorize-pending --batch-size` 和后面的挖掘命令都在这层里。`job_lock` 用数据库名派生锁名，独占连接执行 `GET_LOCK(...,0)`，占用时直接失败；退出释放锁，获取或释放结果不可靠时作废连接，取消也要等清理完成。

向量化按主键可重跑，文档导入却会重新 INSERT。CLI 没有 sources 清单、已存在块计数拦截、文档内容哈希或版本键；重复执行同一个 import-document 会增加新行。它不能代替 pending 恢复，修改 done 原文后的重新向量化和文档版本管理也不属于当前入口。

三份 `demo-*.md` 的 policy/faq/manual 类型由调用方显式传入；验收脚本自己的固定示例列表不是产品建库清单。它们共切出七块，8 元、满 99 元包邮都明确限定于合成演示店铺和指定配送范围，不能当真实商家政策。

## 从历史对话里挖知识

### `KnowledgeHistory.completed`：完整会话，半开时间窗

文件：`app/knowledge/history.py`，以下选摘会话筛选。

```python
            ids = (await session.scalars(select(Conversation.id).where(
                Conversation.status == '已结束', Conversation.updated_at >= stored_start,
                Conversation.updated_at < stored_end, Conversation.id > after_id,
            ).order_by(Conversation.id).limit(limit))).all()
```

只读已结束会话，按 updated_at 的 `[start,end)` 筛选，再按 id 分页，一批最多二十个，消息按 id 排序。无时区输入解释为北京时间；aware 输入先转北京时间，再通过 `NOW()/UTC_TIMESTAMP()` 得到当前 MySQL 时钟偏移，换成存储边界。已有实库测试覆盖当前 UTC MySQL 的窗口，不承诺修复历史混用时区或夏令时。

### `QAResult`、`QAExtractor.extract`：一条 QA 就是一组字段

文件：`app/knowledge/extraction.py`。

```python
class QASchema(BaseModel):
    model_config = ConfigDict(extra='forbid', strict=True, hide_input_in_errors=True)
    source_ref: str = Field(min_length=1, max_length=255)
    question: str = Field(min_length=1)
    answer: str = Field(min_length=1)


class QAResult(BaseModel):
    model_config = ConfigDict(extra='forbid', strict=True, hide_input_in_errors=True)
    qas: list[QASchema]
```

本项目用嵌套对象数组，不是 questions/answers 两个并列数组，因此没有“长度不等按较短截断”的处理。每条 QA 同时具有问题、答案和来源，缺字段、多字段或类型错都拒绝。

抽取器复用前一步模型工厂，调用 `with_structured_output(QAResult, method='json_mode', include_raw=True)`。先预检每个完整会话的输入预算，再按预算组合模型批次；单个会话超预算就失败，不剪掉聊天末尾凑数。

```python
            parsed = validate_structured_output(output, QAResult)
            allowed = {source_ref(c) for c in batch}
            for qa in parsed.qas:
                if qa.source_ref not in allowed or not qa.question.strip() or not qa.answer.strip():
                    raise invalid_output()
```

前两步的 `validate_structured_output` 会再验证未经修补的原始 JSON，拒绝 length 截断，并要求原始结果与 LangChain parsed 一致。这里再限制来源必须是当前输入批次的 `conversation:<id>:message:<末消息id>`，不能凭模型自己编一个来源。

`build_qa_messages` 要求仅抽 assistant 明确给出的通用规则，去除个案标识，排除 mock、无答案、用户愿望、无依据退款承诺和注入指令，保留每个不同真实问法及配对原文。结构校验能关住格式与来源，不能保证任意真实历史都抽得正确。

离线 QA 曾在 512 输出预算下实际截断，所以现在单独用 `qa_max_output_tokens=2048`，在线客服仍是 512。已有九类合成评估为 9/9；最新报告保存计数和严格问法/来源 scorer 结论，没有保存实际抽取字面串，不能把它称作真人逐条审核。

### `ConversationMiningJob.run`、`stage`：暂存重放的身份

文件：`app/knowledge/mining.py`，以下选摘每个历史批次的身份与暂存。

```python
            identity = [start.isoformat(), end.isoformat(), sources]
            batch_no = hashlib.sha256(json.dumps(identity, separators=(',', ':')).encode()).hexdigest()
            try:
                items = await self.extractor.extract(rows)
                counts['staged'] += await self.repository.stage(batch_no, items)
```

窗口、会话 id 和末消息 id 共同生成 batch_no。`KnowledgeRepository.stage` 在短事务里取同批所有行，包括已 kept/discarded 的行，用 `(source_ref,question,answer)` 原文三元组拦住同批重复及重放，不把已决定的 QA 再暂存一份。

这不是“这个窗口以后绝不再调用模型”的清单。重跑仍会抽取；相同来源若生成不同文本，可以形成新暂存行，再交整体去重。失败时 `MiningBatchError` 给出安全错误类型、批次、窗口和已验证 id，CLI 非零退出，不打印原对话或提供方原始异常。

### `normalize_qa`、`deduplicate_staging`：精确去重，冲突保留

文件：`app/knowledge/mining.py`。

```python
def normalize_qa(question: str, answer: str) -> tuple[str, str]:
    return tuple(' '.join(unicodedata.normalize('NFKC', value).split()) for value in (question, answer))
```

NFKC 统一兼容字符，再折叠空白，问题和答案组成一个键。不会统一大小写或删除所有标点，不把不同语义问法合并；同问题不同答案也保留，避免在这里悄悄裁决政策冲突。存储正文保持原文，规范化只用于比较。

```python
    seen = {normalize_qa(q, a) for questions, a in await repository.qa_pairs()
        for q in questions.splitlines() if q.strip()}
    kept, discarded = [], []
    for row in await repository.extracted():
        pair = normalize_qa(row.question, row.answer)
```

已有知识的多行问法要逐条展开，pending 和 done 都参与。遍历的是全部 extracted，按暂存 id 顺序同时挡住本批、跨批和存量重复；没有只圈定当前 batch_no，因为末尾要整体处理之前中断留下的未决定行。

### `KnowledgeRepository.promote`：去重决定与入库一起提交

文件：`app/repositories/knowledge.py`，以下连续选摘事务末段。

```python
            new_kept = [by_id[identifier] for identifier in kept_ids if by_id[identifier].status == "extracted"]
            new_ids = await _insert(session, [ChunkDraft("历史客服", row.question, row.answer, content_type="faq") for row in new_kept])
            for identifier in ids:
                by_id[identifier].status = "kept" if identifier in kept_ids else "discarded"
            return new_ids
```

保留项自动变成分类“历史客服”、类型 faq 的 pending 知识，暂存状态一起改成 kept；重复项改 discarded。插入或状态更新失败会一起回滚，同一决定再调用不会再插知识，已有相反决定则拒绝。

这里的 kept 已经意味着完成入库，没有人工采纳页、approve 端点或 rejected 状态。`source_ref` 留在暂存表，不进入最终 chunk。自动精确去重是当前选择，不能拿暂存表的存在暗示已经有人工质量审批。

### `previous_day`、`run-daily`：外部每日任务

文件：`app/knowledge/cli.py`、`scripts/run-knowledge-daily.ps1`。

```python
def previous_day(now: datetime | None = None) -> tuple[datetime, datetime]:
    now = now if now is not None else datetime.now(BEIJING)
    end = now.astimezone(BEIJING).replace(hour=0, minute=0, second=0, microsecond=0, tzinfo=None)
    return end - timedelta(days=1), end
```

`run-daily` 在一把外层 job_lock 内挖北京时间前一日，整体去重，随后向量化 pending；也能分别执行 mine-conversations、deduplicate-staging、vectorize-pending。Web 进程里没有定时器。

PowerShell 启动脚本固定项目目录，执行 `uv --directory ... run python -m app.knowledge.cli run-daily`，stdout/stderr 追加到 `.cache/knowledge-daily.log`，保存并转发子进程退出码。文件里给出 China Standard Time 宿主每日 02:00 的注册说明，脚本本身不注册任务。正式库建库和宿主计划任务仍未部署，已有验收使用合成会话与隔离测试库。

## 在线检索：先取主键，再回 MySQL 原文

### `FAQRepository.search`：Dense 决定顺序，MySQL 决定内容

文件：`app/repositories/faq.py`，以下选摘检索和旧字段投影。

```python
        vectors = await self.embedder.embed([keyword])
        hits = await self.index.search(vectors[0], limit=min(limit, 3))
        rows = await self.knowledge.get_done([hit.id for hit in hits])
        by_id = {row.id: row for row in rows}
        return [{"id": hit.id, "question": by_id[hit.id].questions,
                 "answer": by_id[hit.id].answer, "category": by_id[hit.id].category}
                for hit in hits if hit.id in by_id]
```

问题原文只嵌入一次，Milvus 用 COSINE/Strong 取最多三条 id 和 score，再查 MySQL done 行。原文不从向量库读；pending、缺失行都过滤，SQL 返回顺序即使不同，也按 hits 顺序重新投影。没有命中时 get_done 空列表直接返回，不发 SQL 查询。

没有 LIKE 回退、查询改写、阈值或重排，score 也没进入旧 matches 结构。已有六条召回标注中域内 5/5，全部 5/6：域外“火星今天的天气如何”仍召回三条不相关知识。Top3 包含目标章节只证明召回命中，不证明三条都相关，更不等同回答事实全对。

### `lifespan`：把检索资源接回应用

文件：`app/main.py`，以下选摘默认 FAQ 创建路径。

```python
            if faq_repository is None:
                embedder = SiliconFlowEmbedder(settings)
                resources.push_async_callback(embedder.aclose)
                index = MilvusIndex(str(settings.milvus_uri), timeout=settings.milvus_timeout_seconds)
                resources.push_async_callback(index.aclose)
                await index.ensure_collection()
                faq_repository = FAQRepository(database, embedder, index)
```

默认启动时校验集合，把 embedder/index 交给 FAQRepository，再交原工具注册入口。资源一创建就登记 AsyncExitStack，后续初始化失败也能释放前面已创建的资源；注入 FAQ 时不另建检索客户端，所有权仍归注入方。

已有实际应用验收证明“邮费是多少”经 query_faq、SSE 事件和消息持久化走通，并由控制器对照合成原文复核回答范围。HTTPX ASGITransport 会缓冲 SSE，这份证据不等于浏览器网络逐帧验收。

## `query_faq`：换实现，保留契约

### `contextual_tools`：调用方仍只交一个 keyword

文件：`app/tools/business.py`。

```python
    @tool(args_schema=FAQArgs)
    async def query_faq(keyword: str) -> dict:
        """使用当前问题的连续原文片段语义检索 FAQ，最多三条。"""
        if keyword not in context.user_question:
            return {"error": {"code": "invalid_keyword", "message": "关键词必须是当前用户问题中的连续原文片段。"}}
        matches = await faq.search(keyword, limit=3)
        return {"found": bool(matches), "matches": matches}
```

第二步的 keyword 参数、128 字符上限、当前问题连续原文片段校验，以及 found/matches 都保留；每条还是 id/question/answer/category。变化发生在 FAQRepository 内部：关键词查表变成 Dense 检索，装饰器的说明也跟着改成语义检索。

模型不用学一个新工具 schema，原工具执行器仍负责超时和有界工具重试。嵌入、向量或 SQL 失败就走原安全工具错误，没有偷偷返回旧 FAQ 表的结果；被取消的那次调用会停止后续检索。

## 小结

第三步把一条 Dense 链路接完整了：Markdown 按结构切块，三字段文本变成 1024 维向量，MySQL 先保存 pending 原文，Milvus 用同一主键 upsert，再回填 done；在线问题从向量召回主键，回 MySQL 取权威正文。历史会话则经过完整输入、结构与来源校验、暂存、成对精确去重，自动进入同一 pending 入口。

这条链能恢复和运行，质量边界也仍在：域外误召回、不同问法与冲突答案并存、重复文档导入缺少版本身份，正式建库和外部调度尚未部署。后续可以用更完整的评估集研究关键词与向量混合召回、重排或拒答策略，改善精确词命中和相关性；这些都是未来方向，当前源码只实现 Dense 单路。
