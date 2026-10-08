# 第四步设计：混合检索、重排与质量评估

日期：2026-10-08。用户先以“继续”确认会话中的设计方案，再以“是的，继续”确认本书面 Spec。当前进入正式实现计划审阅阶段，产品实现尚未开始。

## 1. 目的与验收范围

本项目是用于学习和简历展示的电商智能客服系统。第四步在现有聊天入口中提高知识检索和回答质量，既要让“邮费”这样的口语问法找到政策，也要让具体型号命中对应商品知识，同时对无依据的问题明确拒答并留下改进线索。四策略报告用于观察真实差异，不预设混合重排一定胜出。

用户确定的边界：FastAPI、SQLAlchemy、MySQL、LangChain 不变；Dense 继续使用 BGE-M3；BM25 必须是 Milvus 原生函数，中文使用内置 chinese analyzer；融合使用 hybrid_search/RRF；重排模型固定 bge-reranker-v2-m3。每条消息仍最多一次工具选择、一个逻辑工具，不增加 Agent Loop。查询理解只使用本轮原话，不做指代消解或多轮改写。

会话中已确认的实现方向：新建混合集合，保留旧集合；两路各取 50，RRF 融合取 50，重排取 10；问题池只在 useful=false 时写入；满意度仅在前端采集。重排服务沿用现有 SiliconFlow 云端，这是按现有配置作出的部署选择，模型名称保持不变。

验收必须提供真实证据：四策略数字及分桶报告；具体型号的 BM25 命中；流式回答中的引用能在聊天页查看原文和章节路径；无答案问题得到拒答，并在 MySQL 中找到对应原话、会话及原因。服务故障、取消、受控测试数据不能充当真实模型验收结果。

## 2. 当前项目与改动边界

当前 master 的 Milvus 集合 knowledge 只有 id 和 embedding，FAQ 最多 Dense Top-3；MySQL knowledge_chunks 是权威原文，向量化状态为 pending/done。线上先保存 user，再保存 assistant 工具申请、tool 结果及完整 assistant 回答，正常提交后才发送 SSE done。当前工具统一 5 秒超时，工具申请与结果不可拆散，历史按完整轮次裁剪。

第四步增加专门的查询理解、混合索引、重排、证据组装、充分性判断及评估模块，复用现有知识仓储、外层离线任务锁与消息流水。保留 query_faq 的工具名、keyword 参数及原话片段校验；返回仍有 found/matches，在 matches 中增加引用所需元数据，结果数由最多 3 提升为最多 10。其余四个工具继续使用现有实现，售后结构化提取接口继续可用。

代码、配置及脚本使用 UTF-8；新增或修改函数均有中文说明，关键分支解释业务目的和失败边界。分支采用 feat/hybrid-retrieval，提交标题不用 ch04 前缀；开发记录按用户明确要求保存 dev-notes/ch04.md。prompt.md 保留用户第四步提示词及 DDL。

## 3. MySQL 与集合迁移

### 3.1 用户 DDL

保存用户提供的两表 SQL 为 sql/ch04-ddl.sql，保留全部列、ENUM、默认值、索引、外键及中文 COMMENT，明确执行 SET NAMES utf8mb4。low_confidence_questions 不增加 useful 列，faith_cases 的 citations 保留 JSON 类型。迁移沿用显式 DDL 执行和结构核验方式，不使用 ORM create_all/drop_all 代替原 SQL，也不清空已有数据。

迁移支持两表均不存在时执行、两表均存在时验证；单表存在、结构不一致或目标库不符时非零退出。迁移不是 MySQL 原子 DDL：部分建表失败必须报告实际状态，由明确的修复操作处理，不能假称自动回滚完成。

### 3.2 新混合集合

创建 knowledge_hybrid，主键与 MySQL 正 INT64 chunk id 对齐，auto_id=false、动态字段关闭，使用 Strong 一致性。字段为 id、embedding（FLOAT_VECTOR，1024）、text（TEXT，启用 analyzer）、category（VARCHAR，1020 UTF-8 字节；逻辑限 255 字符）和 sparse（SPARSE_FLOAT_VECTOR）。TEXT 选择基于当前服务/SDK 3.0.2，避免将 MySQL 合法长文本偷偷截成 VARCHAR 长度。

text 与 Dense 嵌入输入同源：category、questions、answer 按现有 embedding_text 格式拼接，不加入 section_path、content_type、is_key_clause 或邻块指针。category 同时作为独立过滤字段保存。text 使用 analyzer_params={type: chinese}；挂 FunctionType.BM25 生成 sparse；稀疏索引使用 SPARSE_INVERTED_INDEX/BM25、DAAT_MAXSCORE，k1=1.2、b=0.75。Dense 延续 FLAT/COSINE，避免把索引近似误差引入本次四策略比较。

初始化与启动核验字段、维度、函数、analyzer、索引与一致性。结构不兼容时报错，不删除重建已有同名集合。对中文夹英文/数字及带连字符型号运行真实 analyzer 和检索验证；不能仅由分词器名称推断型号一定命中。

用户 2026-10-08 回复“继续啊”批准运行配置调整：Docker 的 standalone 通过 /milvus/configs/user.yaml 只读覆盖 common.storage.useLoonFFI=true 后重启，沿用 3.0.2 镜像、现有卷和集合。真实探测确认 TEXT/BM25 与旧 Dense 可用后继续。StorageV3 会用于新写入和后台压缩输出；关闭开关不立即还原数据，不当作版本降级/回滚。分类 VARCHAR 的 max_length 按 UTF-8 字节计数，因此预留 1020 字节以保持 MySQL 255 字符原文契约。这两项来自真实 API 核对，不换 BM25 或模型。

### 3.3 重建、切换与增量写入

在现有外层 job_lock 内逐批读取所有 done 行，向新集合写入文本、category 和 Dense 向量。旧 done 行不能靠 pending 扫描补齐新集合。按 MySQL id upsert，返回主键核验成功后再继续；中断后重跑同一命令，允许重算但不产生重复知识或重复向量。不得将旧 done 改回 pending 来制造迁移进度。

重建期间 pending 行维持原状态。切换前，在同一任务锁内核对所有 done 主键及新集合字段内容，验证模型维度、索引、必要示例查询；仅总数量相等不算迁移通过。通过后显式配置 MILVUS_COLLECTION=knowledge_hybrid，并重启线上服务及离线任务，使两者选择同一索引实现。

切换后的 vectorize-pending/run-daily 写入同一新集合的 Dense、text 和 category；服务端确认后回填 vector_id，并把 pending 转 done。失败保留 pending，稳定主键重试。旧 knowledge 集合保留作核查；重新启用旧链路前需要补齐切换后新增的知识，不能将保留集合等同于随时完整回退。

## 4. 查询理解、过滤与检索

### 4.1 本轮查询理解

保持用户原话不变，模型的 query_faq.keyword 必须是原话的连续片段，长度和校验沿用既有契约。查询理解服务接收可信的本轮完整问题，输出标准问法与最多 4 个扩展词。扩展只用于检索请求，不回写 knowledge_chunks，不生成额外入库副本，也不读历史来补指代。

结构化输出需限制长度和字段，保护数字、型号、品牌、否定词、金额及条件；不得把“会不会”改成肯定前提。与原话中的关键标识冲突时使用确定性的原话查询并记录该验证结果；API 超时、鉴权或 Schema 不合法属于服务失败，不假称改写成功。离线标注样例覆盖口语、否定、多条件、型号保真和扩展边界。

四种评估策略使用同一份已冻结的查询理解结果：Dense 嵌入标准问法；BM25 输入标准问法加扩展词，并保留原始型号字面信息。报告同时保存原问法、标准问法及扩展结果，便于区分改写与检索贡献。

### 4.2 品类过滤

聊天请求增加可选 category 字符串，表示现有知识表中的完整分类值，缺省不筛选。服务端限制长度为 1–255，拒绝空白、非字符串和额外过滤表达式；通过参数绑定构造 category 等值过滤，不接受用户提供的 Milvus expr。品类可以作为分类值使用；本步不另造与既有分类冲突的标签体系。

同一过滤条件传给 Dense 与 BM25 的 AnnSearchRequest，并在从 MySQL 取权威正文后复核分类及 done 状态。过滤是召回前约束，不能先从全库召回 50 条再过滤。CLI/评估输入也使用同一受限分类契约。

### 4.3 候选、融合与重排

Dense 和 BM25 每路 limit=50，hybrid_search 使用 RRFRanker(k=60)，融合 limit=50；对重复 id 去重，并仅保留可从 MySQL 读取的合法 done 块。线上对融合候选的 category/questions/answer 文本调用 SiliconFlow /v1/rerank，模型 BAAI/bge-reranker-v2-m3，top_n=10、return_documents=false。

严格校验重排 index 对应本轮候选、无重复、在范围内且分数为有限数；按分数从高到低选 Top-10，同分保持服务返回顺序，再关联 MySQL 权威原文。不同指标的原始分数不互相比较，RRF 分数不当成概率。重排置信度下限由独立校准样例选择，作为显式 RERANK_MIN_SCORE 配置；判断低分使用本轮最高重排分数，小于下限为低分，等于下限可进入模型内容自评。校准结果及选择方法写入报告，不能凭空声称某个固定值具有通用置信度。线上混合重排启用前必须配置该有限数阈值；校准命令自身不依赖已选阈值。

增加 FAQ 单独超时：整条查询理解/嵌入/检索/重排链路上限 90 秒，重试为 0；改写 15 秒、嵌入 20 秒、Milvus 沿用 5 秒、重排 20 秒。其余工具保持既有超时及有限重试策略。模型充分性判断单独上限 20 秒；每轮总处理上限 240 秒，取消传播到底层客户端。应用、模型和 SDK RPC 不额外重试。用户 2026-10-08 回复“继续啊”批准一个明确例外：保留 PyMilvus 3.0.2 无公开禁用选项的 Schema 缓存刷新重试，最多一次，写入仍使用相同主键；不声称严格一次物理 upsert。所有逻辑操作受取消感知的总超时约束。

## 5. 证据、生成与问题池

### 5.1 预算与稳定编号

先得到重排 Top-10，再按相关性挑选能完整放入当前输入预算的块。预算计入 System Prompt、本轮原话、工具申请/结果、证据元数据和历史；历史优先按完整轮次淘汰，证据仅整块保留或移除，不截断政策条款。不把未喂给模型的候选伪装成已引用证据。JSON 工具结果同时受现有 20000 字符及 MySQL TEXT UTF-8 字节上限约束。

保留下来的证据按相关性赋予稳定编号 1..N；编号与 chunk_id 一一对应。Prompt 展示按“最相关在首、次相关在尾、其余按相关性交替分布到两侧”的规则重排，但编号不变。ToolMessage 保存本轮真实证据及 section_path，聊天 SSE 和评估使用同一份证据对象。faith_cases.citations 保存这份实际输入全集，而不是 Top-50 候选或答案实际引用的子集。

如果所有候选因预算无法放入，不把它归因于知识库缺失：返回明确预算错误，不入问题池。允许足够预算下少于 10 条；报告须记录重排数量、实际喂入数量和预算删减数量。

### 5.2 生成前充分性判断

对知识回答先进行一次结构化判断：useful 布尔、reason 文本，以及 response_kind（knowledge/social/clarification）。输入包括本轮原话、真实证据和禁止承诺的约束。判断依据是证据是否覆盖问题的关键条件，而不是是否召回到任意相似文本。

知识回答无证据或未达到校准下限时，不能被 useful=true 放行；最终有效决定为 useful=false。证据分数足够仍需模型自评内容是否足够。预算失败、外部故障和非法自评输出发送服务错误，不转成 useful=false，也不写问题池。

业务知识问题在工具选择 Prompt 中要求查询 query_faq。未调用工具的知识问题也执行充分性检查，不能把模型直接回答当成已检索；social/clarification 仅允许寒暄或询问缺失条件，不得借该分类作业务事实承诺。订单、商品、物流及工单仍遵守既有工具证据边界，不将模拟结果冒充真实业务。

useful=false 时流式发送固定拒答文本，说明当前资料不足以确认并引导补充问题或联系人工；不再让模型自由编出替代政策。useful=true 时最终模型不绑定工具，逐增量输出回答；Prompt 要求知识事实附合法 [n]，每项承诺必须有依据，明确禁止保证退款到账时间、保证配送日期或把待处理工单说成已退款。

成功回答必须满足既有正常结束、非空、长度及取消校验；知识回答还要检查引用编号存在于本轮证据，且至少使用一条引用。非法引用发送 error，不保存为完整成功回答；流中已显示的文字标为未完成。引用有效不等于事实忠实，Faithfulness 另行评估。

### 5.3 入池与最终提交

仅有效决定 useful=false 可写 low_confidence_questions。无召回/低证据分数使用 source=retrieval_low_conf；有可用候选但模型判覆盖不足使用 self_check。raw_question 保留用户原话，conversation_id 使用可信会话主键，reason 保留安全的判不能原因。useful 不另建列。

拒答最终 assistant 和本轮问题池记录在同一个短事务中提交，每次处理至多一条；不在模型等待期间持有事务。取消或事务失败不发送 done，不自动重试该最终事务。成功后 done 增加字符串 message_id，conversation_id 继续为字符串，兼容旧客户端。

前端满意度不会写 source=user_feedback；该 ENUM 值按用户原 DDL 保留作后续入口。正常有依据回答和服务故障均不写问题池。

## 6. SSE 与前端

保留现有 status/delta/done/error；增加 checking 阶段提示与 citations 事件。citations 在第一段答案 delta 前发送，包含本轮证据列表：n、chunk_id（字符串）、section_path、question、answer；会话/消息身份以当前请求及成功 done 对齐。编号以本轮为作用域，不引用历史轮次的映射。

聊天页把已知 [n] 构造成按钮，点击打开来源面板，显示章节路径和权威 chunk 原文；未知编号保持普通文字并使该回答不能作为完整验收成功。解析能跨 SSE/网络块与逐字显示队列处理完整编号。使用 DOM/textContent 写入原文，避免把知识内容作为 HTML 执行；来源面板可关闭、可键盘操作。

每条成功完成的回答左下角显示 👍/👎。首次点击后点亮所选、显示“已反馈”并禁用两按钮；同一回复不能反复切换。以会话、最终消息身份关联前端采集状态，拒答也可反馈；取消/错误的未完成回复不出现可提交反馈。该信号保存为页面本地状态，不发后端请求。

前端按用户 Vibe Coding 例外直接迭代并做浏览器手工验收，不套 brainstorm、TDD 或前端代码审查流程。新增后端 SSE 契约、引用身份及数据边界仍按后端测试和审查验证。

## 7. 四策略评估与编造台账

### 7.1 数据集与公平比较

新增提交到仓库的合成知识，包含具体型号及近似型号干扰项；既有演示政策与 FAQ 保留。评估集固定 30 题，分 A_policy、B_model、C_colloquial、D_unanswerable、E_multi 五桶，各 6 题；每桶 easy/medium/hard 各 2 题。每题有唯一 eval_id（最长 16）、原问、难度、分类约束、ground-truth 必需事实、相关章节标识或空集合、预期是否拒答。多条件题按多个必需证据标注，不能只命中一条就全过。

另设 8 条校准样例，与 30 题测试集隔离；按人工标注的证据足够/不足，在观察到的重排分数候选阈值中选择拒答 F1 最好的值，同分取较高阈值，并报告混淆矩阵。先冻结阈值再跑测试集，不用测试集反向调参。

四策略为 dense、bm25、hybrid、hybrid_rerank。前三种取得候选 Top-50，按各自排名选 Top-10；第四种对融合 Top-50 重排取 Top-10。相同语料快照、查询理解结果、分类过滤、预算、在线模型及生成约束；只改变检索策略。控制性单测与真实服务报告分开标识。

### 7.2 指标与报告

有正标注题：Recall@10 与 Recall@50 为前 K 命中相关 chunk 数/该题标注相关 chunk 总数；MRR@10 为首个相关 chunk 的排名倒数，未命中为 0；每题再统计所有必需证据是否齐全。重复 id 先去重。Recall@50 在候选召回阶段计算，因此 hybrid_rerank 与 hybrid 共用同一融合 Top-50；Recall@10/MRR@10 使用各策略最终 Top-10 排名，实际送入 Prompt 的召回覆盖另外记录。空 ground-truth 题不计入 Recall/MRR 分母，单独报告拒答正确率和错误放行数量。

生成 Faithfulness 以裁判对答案事实断言的逐项证据支持判断计算：supported_claims/total_claims。裁判同时输出断言、是否支持及原因，依据为实际送入生成模型的完整证据；答案的合法角标本身不能证明支持。固定裁判模型及 Prompt，报告模型、提示词版本、输入和判定结果。拒答或无事实断言标为不适用，不混成 100% 忠实；非法裁判输出标为 judge_error，不写编造个案。

分别输出总体与五桶结果，保留逐题原问、标准问法、排名/分数、相关知识映射、输入证据全集、最终答案、自评结论、裁判结论、耗时、错误及未执行数量。JSON 为机器原始记录，Markdown 为对照报告。外部前提或运行错误不得自动降级为伪造的可比较数字；未完成运行要明确缺失项和非零退出。

### 7.3 faith_cases 行为

每个被裁判判为含不受支持事实的答案写入用户给定 faith_cases；eval_id 是业务唯一键，strategy 记录当次策略。四策略都可产生个案，报告保留每次判定，台账保留同题最近一次编造快照，seen_count 统计累计判为编造次数。

首次写入 status=未解决、seen_count=1；再次编造原子更新 answer/reason/citations/strategy/judge_model/last_seen_at，seen_count 加一，保持 first_seen_at。已解决或无需解决的同题再次编造时改回未解决、清空 resolution，但保留 resolved_at 标记曾处置。一次后来通过的评估不自动把旧编造改成已解决。

本步提供台账命令行查询与人工处置入口；修改为已解决/无需解决必须提供 1–300 字符非空说明并记录 resolved_at；退回未解决清空 resolution，保留最近处置时间。SQL 写入使用参数绑定及事务，不能先读再无锁加次数。原文快照为实际输入的 [{n,chunk_id,section_path,question,answer}] 全集。

## 8. 验证、文档及过程留痕

后端可单测代码走 TDD：迁移核验与台账 upsert、集合 Schema/幂等重建、双路预过滤/RRF、重排返回校验、整块预算和稳定引用、自评拒答与入池事务、SSE 结束/取消/历史回放以及指标公式。纯 Prompt 与评估数据使用上述标注样例验证。受控假实现只验证协议和故障，不当成真实质量报告。

真实集成验证使用独立 MySQL 测试库 3308 与唯一命名的 Milvus 测试集合，登记本轮拥有的记录和资源；不清空业务库或现有集合。测试真实重建中断恢复、BM25 型号命中、分类先过滤、四策略数字、来源面板与无答案问题入池。真实调用失败保留失败证据，不隐式换模型或策略。实际部署迁移与测试库结果分开记录。

README 提供迁移、重建、切换、校准、四策略评估、服务启动和 curl 演示命令，文案使用“第几步”而非“第几章”。交付记录包含当前测试命令/结果、真实报告与限制、数据库/集合状态和 dev-notes/ch04.md 路径。每个阶段完成时现场追加四项过程记录，不能到收尾一次性补写。

## 9. 文档依据与 Spec 自审

本设计前已实际通过官方 Context7 MCP 查询 Milvus Schema/迁移、PyMilvus hybrid_search/RRF、SiliconFlow rerank；同时核对本地 3.0.2 SDK 签名。查询响应保存在忽略的 .cache/context7-*.txt。具体实现新的 FastAPI/SQLAlchemy/LangChain 接口时仍须先查询对应 Context7 文档，不能把设计核对当成所有 API 均已核查。

- [Milvus 全文检索](https://milvus.io/docs/full-text-search.md)：BM25 函数与稀疏字段。
- [Milvus Chinese analyzer](https://milvus.io/docs/chinese-analyzer.md)：内置 chinese 配置。
- [Milvus cnalphanumonly](https://milvus.io/docs/cnalphanumonly-filter.md)：中文、英文和数字过滤定义；型号实际命中仍需验证。
- [Milvus TEXT](https://milvus.io/docs/text.md)：当前版本全文检索文本字段。
- [PyMilvus Async API](https://github.com/milvus-io/pymilvus/blob/master/_autodocs/api-reference/async-milvus-client.md)：hybrid_search 与检索请求签名，已结合安装版本核对。
- [SiliconFlow Rerank](https://docs.siliconflow.cn/docs/api/rerank-post)：云端重排请求与结果索引定义。

自审结论：范围覆盖用户七项功能与两表 DDL；旧 done 行重建和新 pending 写入分别定义；候选 Top-10、实际输入及引用快照三者区分；评分阈值由独立数据决定；入池条件统一 useful=false；前端反馈没有后端写入。设计不存在未填占位符；阈值数值与真实报告属于必须通过后续校准/验收得到的实测产物，不伪写为设计事实。用户已批准本 Spec；对应计划为 [2026-10-08-hybrid-retrieval.md](../plans/2026-10-08-hybrid-retrieval.md)。
