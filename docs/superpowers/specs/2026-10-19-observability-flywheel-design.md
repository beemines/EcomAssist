# 第九步设计：本地可观测性与数据飞轮

## 2026-10-20 验收图补充（本节覆盖首版中的冲突约定）

用户在提供18张标准验收图后要求“按照验收标准继续完成”。沿用已批准的Native计划与隔离工作树，追加Task11–17。前端继续适用Vibe Coding例外。

- 页面入口为聊天 `/`、飞轮 `/review`、观测 `/observability`；保留旧入口。飞轮提供四状态、频次排序、AI草稿预填、原轮证据与三态快照。驳回缺口继续参与查重；重复只累计次数，审核状态仍为驳回。
- 置信度改为四信号固定权重0.5/0.2/0.2/0.1（Top1、有效数量、分差、条款命中），显式型号及带单位数值必须能在实际片段中找到。只在100题校准集选参，先最小化误放、再降低误拒，200题留出不参与调参。候选/在用版本、分布、扫描与真实误放均可查看；截图的0.26不是本项目预设值。新规则首次留出结果为误放4、误拒9，应如实报告，不能据此再拟合留出标签。
- 追踪根节点记录原问题和最终回答，整次模型消耗归入最终意图。generation层货币成本与节点耗时可查看；人民币标准刊例估算和Langfuse美元成本分开，日期/来源/汇率版本明确，未知不补零。可信运行配置标记actual/fixture；历史未标注数据不追认成真实请求。
- 评估的推理等级优先采用评估配置、否则继承线上值，进入指纹。生成/裁判失败保留安全终止诊断，不改模型、输出预算或失败样本。对比须同配置、同有效分母且无错误；含错误的有效子集满分不称为稳定。
- 历史问题仅提供明确ID范围、上限与preview/execute命令，本轮不处理历史客户原话。付费定时关闭，工单/退款不属于本轮写操作。
- 用户在本轮明确选择“保留原额度，只完成两轮各20题”：累计物理上限仍为GLM280、嵌入450、重排450，失败计数、重启不清零；不执行截图的两轮全量300题。此前190次GLM已消耗，追加真实定点复验1次后191；余量不足以保证两轮新的完整20题，应先补关键页面与错误定位证据，不伪造完整趋势验收。


日期：2026-10-19。基线：`master f44e4f9`，已包含第六至第八步。书面设计首版提交为 `a1e3222`；[实施计划](../plans/2026-10-19-observability-flywheel.md)提交为 `6d0f646`。用户已批准设计和计划，选择Native顺序实现、新建隔离worktree；当前在实施阶段。附录存档用户原始DDL，未变更已批准设计语义。

## 1. 目标、约束与选择

让开发者能在本地 Langfuse 看清客服每条请求的执行链路和 Token 消耗；让三种知识缺口统一进入问题池，经标准化、查重、人工审核后进入现有知识库；让重复运行的评估结果有可追溯的趋势。

用户已明确确认：

- Langfuse 采用本机 Docker Compose 自部署，链路不发送到 Langfuse Cloud。原业务模型、嵌入、重排仍使用项目现有上游，其调用费用另计。
- 当前没有 Context7 MCP 工具，允许本步骤使用官方文档和锁定版本源码核对接口，技术选型不变。
- 采用独立 Langfuse Compose、图构造处统一挂回调、应用内受管后台任务，复用现有 MySQL、知识入库和 step04 评估能力。
- 用户给出的两张新表及问题池 ALTER 保留；消息定位、反馈去重和发布恢复所需补充字段在本文列明，实施时使用独立补充迁移。
- 前端使用 Vibe Coding 例外，按页面效果直接实现和验证，不执行前端 brainstorm、TDD 或 code review；后端仍走 Superpowers、TDD 和独立审查。Prompt 使用标注样例验证。

本步骤不做主题分类微调、跨会话用户画像、自动发布 AI 示例答案，也不替换 MCP 工具系统、退款确认或三层上下文管理。

| 方案 | 取舍 |
| --- | --- |
| 本地独立 Compose + 应用内受管后台任务 | 采用。启动入口少，利用现有资源生命周期和 MySQL 恢复任务，适合本步骤规模 |
| 本地独立 Compose + 独立 Python Worker | 隔离更强，但增加进程管理；本步骤不额外引入 |

## 2. 本地部署与资源边界

选用 Langfuse 服务端 `v4.63.0`、Python SDK `langfuse==5.0.2`。项目现有 `langgraph==1.2.15`、`langchain-core==1.6.6` 等固定版本保留。SDK v5 要求 langchain-core >=1，与现有主版本一致；实施时仍须以实际依赖解析和集成测试确认。

新增 `compose.langfuse.yaml`，独立 Compose 项目名、网络及具名卷，包含官方方案的 web、worker、Postgres、ClickHouse、Redis、对象存储。所有镜像锁定可核验的版本或 digest。官方发布版 Compose 中的浮动 `:4`、`:7` 等不能直接当作已锁定依赖；若指定版本的正式镜像不可取得，停止并说明，不静默换版本。

Langfuse 界面与 SDK 默认连接 `http://127.0.0.1:3000`；不向局域网开放。数据库和队列只在独立容器网络内通信。只映射确有必要的回环端口，避开现有 Milvus 的 9091 / 19530、MySQL 的 3307 / 3308。若 3000 已被其他进程占用，启动脚本明确报冲突，由配置选择空闲端口，不结束不明进程。

Compose 的容器标准输出日志配置有界轮转。持久化 trace 与数据库数据不自动删除；部署报告分别记录镜像、业务数据和日志占用，不能把日志轮转说成已限制全部数据增长。

通过官方初始化机制创建本地组织、项目及管理员。密码、项目密钥及数据库凭据由本地生成并写入被 Git 忽略的专用环境文件；示例文件只含占位符。SDK 启用时必须显式设置本地 BASE_URL，禁止缺省回落到 Cloud。关闭产品遥测和本步骤无关的遥测导出。认证信息不进入 trace、普通日志、测试快照或提交。

新增第九步演示入口，客服建议端口 8006，独立 checkpoint 文件；使用新增验收会话，不让两个客服进程同时修改同一会话。保留现有 8004 / 8005 及 MCP Server。启动、停止只管理本步骤登记的进程和容器；不删除现有数据库或卷。

本机只读基线为：Docker 内存约 15.46 GiB，当前容器瞬时合计约 1.35 GiB；C / D 盘空闲约 191 / 154.2 GB；现有镜像 3.649 GB、卷 1.513 GB。部署后另报镜像与卷的新增占用。先前的 10～20 GB / 预留 30 GB 仅为规划估算，100 GiB 是官方 VM 容量建议示例，均不冒充实测。

## 3. 请求追踪与 Token 归属

### 3.1 统一接入

在图构造处使用 `compile(...).with_config(callbacks=[handler])` 挂一次 Langfuse 回调。已核对的 LangGraph 1.2.15 `compile()` 不接收 callbacks 参数；这一接法实现用户要求的构造时统一配置，保留图状态和 checkpoint 公共接口。各请求只补充运行身份，不在每个节点重复注册 handler。

每次实际 HTTP 图执行有独立 trace，带 conversation_id、user_message_id、execution_id、purpose、版本和结果状态。session_id 关联同一会话。订单选择、工单确认的 interrupt / resume 请求分别留 trace，以同一逻辑 turn_id 关联；用户等待时间与实际执行耗时分开标记。完成结果的只读重放标记 replay，不重记之前的模型调用。

节点和模型回调记录实际执行的输入、输出、prompt、模型名、usage、耗时及错误。统一工具引擎与 Workflow 的确定性检索、业务查询增加明确的子 observation，保留工具名、来源、重试与结果；不能只显示外层图就算完整链路。检索记录查询、候选 / 精排排名、得分类型和实际证据，避免把 RRF 与 rerank 分数混用。

自定义 span 与标准 LLM 回调分工：自定义 span 描述操作，LLM generation 记录收费调用，同一物理模型调用只记一份 usage。追踪不额外请求模型或重放工具。服务端 Runtime、连接对象和密钥不作为节点输入序列化。

Langfuse 故障时聊天继续运行，并在本地记录追踪降级；有界后台导出不在 SSE 路径逐轮 flush。关闭时先停止业务任务、再有界 flush / shutdown，超时不无限等待。追踪降级不能把尚未完成的写操作改成“成功”。后台模型链在构造时使用同一追踪适配器，任务执行另建有 purpose 的根，不冒用已经结束的用户请求上下文。

### 3.2 意图维度统计

意图识别结束后，将规范意图、分类置信度和 route 写入当次执行根 observation 的元数据；后续业务 observation 继承这些属性。未走 Agent 的闲聊和兜底也纳入；意图识别前失败的请求归“未识别”，不强塞到某个业务意图。

统计以 execution / trace 身份把该请求的 generation 与最终意图关联。因此，指代消解和意图识别本身发生在意图得出之前，也算入最终业务意图的花销。不能仅按 generation 创建时是否已有 intent 标签过滤，否则会漏掉前两个阶段。

从本地 Langfuse 的固定版本 observation 查询 API 分页读取，以 observation ID 去重，只累加 generation 的 input / output / total tokens，不累加父节点的重复汇总值。默认汇总已经结束的执行，进行中数量另列；根结束前写入最终意图，早期 generation 通过根身份归属。实际 usage、估算 usage 和未知 usage 分列；缺失 usage 不填零冒充实测。失败重试消耗与成功调用一并统计；只读重放不重复计入。后台飞轮、摘要和评估以 purpose 单列，不混为客服意图。

后台展示按意图的请求数、模型调用数、输入 / 输出 / 总 Token、估算或缺失次数及所选时间范围。Token 汇总是必交付；仅当模型价格已配置且币种、计价版本明确时显示货币成本，未知价格显示未配置，不编造账单。查询有界分页和短缓存，Langfuse 暂不可用时显示明确状态，不能画出全零成功统计。

## 4. 证据置信度闸门

位置保持为知识检索之后、Agent 之前；退款 / 售后的强制政策检索也使用该服务，不改变先查订单再检索政策的顺序。Agent 追加知识检索时，使用相同检查器。订单、物流等业务数据不误走知识分数闸门。

### 4.1 信号与决策

只消费本轮成功检索且经过权威原文核对的证据，按 chunk_id 去重、按 rerank 分数排序。展示用的夹心重排顺序不作为 Top1 / Top2 顺序。信号包含：

- Top1 rerank 相关性分；
- 超过校准有效分门槛的实际证据数，相对当前 Top-K 的比例；
- Top1 与 Top2 的分差。缺 Top2 时单独标记，分差信号取零，不制造无穷大的正面信号。

使用可解释的加权规则生成 0～1 的 evidence_confidence，同时记录原始特征、规则版本及阈值；它是规则强度，不宣称是真实正确概率。空证据直接拒答。非法 / 非有限得分或分数来源不符属于服务 / 契约错误，不伪装成“知识库缺口”入池。

达不到冻结规则阈值：返回原有知识兜底，source=retrieval_low_conf。通过规则后仍执行既有内容充分性自评；本步骤正式规则启用时，该服务仅判断内容，不再次叠加旧 Top1 门槛；旧入口和工作台的策略保持兼容。自评知识不足，source=self_check。证据足够不代表自动批准退款，具体这一单的判断继续交给既有 Agent。

### 4.2 校准与验证

复用 step04 `merchant-rag-300-v1` 的冻结语料、问题和完整证据组标注（实际五桶各 60 题）。先生成确定性分组、分层的校准 / 留出清单：按原始题号及 regressions 的内嵌 case.eval_id 与 original_eval_id 关联分组，关联题不跨集合；组沿用其原始题目的桶。每桶按 SHA-256(dataset fingerprint + group_id) 排序，组数 n>=2 时取前 min(n-1,max(1,floor(n/3))) 组校准，其余留出，单组桶全部留出。两侧必须都有可答 / 不可答标签，否则预检失败。清单、算法和 fingerprint 保存为产物，不能为了分数移动题目。既有独立八题校准集保留为额外回归，不代替本次多信号留出验证。

校准重放在线单次 FAQ 检索与同一证据预算，不调用答案模型替自己制作标签。证据充分标签要求：题目标注可答，且实际送模证据覆盖全部必要证据组；标注不可答及覆盖不全均为不足。

Top1 和 gap 按校准样本经验分布映射到有界信号，count 按实际 K 归一；有效分门槛取校准观察分数的 0 / 25 / 50 / 75 / 100 百分位对应的实际分数，去重形成候选。对非负整数权重 0～3（总和必须大于零）的归一化加权平均及观察到的组合分阈值做确定性网格搜索，以拒答为正类的 F1 选择，平分依次选择误放更少、阈值更高及参数字典序更小的配置。零权重允许数据证明某信号没有增益，并在报告中说明，不能谎称三个信号必然都提升效果。

留出集仅验证，不参与调阈值。报告新规则与原 Top1 闸门的混淆矩阵、拒答 F1、误放 / 误拒计数、有效样本和排除原因；不预设漂亮分数。新配置冻结数据集 / 语料、重排模型、Top-K、预算、特征算法、参数与来源 hash。线上缺配置或签名不匹配则拒绝启用本步骤配置，不能使用拍脑袋默认值；既有演示服务继续使用其原配置。

## 5. 三路入池与原轮证据

统一入池服务接收可信会话、用户 / 助手消息 ID、原始用户问句、source、reason 和证据快照，不接收前端提交的检索正文或模型自报的数据库身份。

| 入口 | 保存时点 | source |
| --- | --- | --- |
| 检索规则不足 | 保存兜底助手消息的同一短事务 | retrieval_low_conf |
| 内容充分性 / 生成知识自评不足 | 保存拒答助手消息的同一短事务 | self_check |
| 用户点击 👎 | 重新核验原轮完成身份后，短事务保存 | user_feedback |

同一助手回答、同一 source 唯一；接口重试和重复点击返回已存在记录，不新增流水。不同入口保留各自原因，不能用一条来源覆盖另一条。

retrieved_chunks 使用有版本的 JSON 对象，包含 schema_version、strategy、检索时间、版本和 chunks 数组。chunks 保存当轮精排 Top-K 的有界快照，最多十条原文：chunk_id、question、answer、section_path、score、score_kind、rank、是否进入 prompt。多个查询先按主键归并，得分来源明确；候选排名另在 trace / 逐题产物保留。不得仅保存 chunk_id，或事后读取已修改的知识正文代替历史快照。

👎 接口只接受 conversation_id 路径、assistant_message_id 和可选 checkpoint_id。服务端核对会话归属、原始 SQL 助手正文、已持久化完成根及其 user_message_id，然后从原轮 evidence_payload / 可信检索回执中尽力回捞；不能误用最新一轮，也不重新运行检索。无显式 checkpoint_id 时按助手消息找到原完成根。

三种证据状态明确区分：

- `captured`：确实检索过，保存原文与得分；真实零召回的 chunks 保存空数组。
- `not_retrieved`：原轮确实没有检索，retrieved_chunks 为 NULL。
- `unavailable`：原轮身份可验证，但旧版 checkpoint 的检索 payload 不完整，chunks 保存空数组及固定缺失说明，不把它谎称为“没检索”。新完成轮必须保有可回捞的 payload；该状态主要兼容历史记录。

整个原轮完成根已不可取得、因而无法验证消息配对的历史反馈，返回明确的原轮不可验证错误，不按相邻用户消息猜问题。原轮存在但旧检索 payload 缺失，才按 unavailable 入池。旧数据不无条件扫描外发；默认只自动处理启用本步骤后生成的任务元数据，历史补处理走显式、限定 ID 的管理命令。

## 6. MySQL 结构与必要补充迁移

第一份 `sql/ch09-ddl.sql` 保留用户 DDL 的表名、类型、默认值、ENUM、索引和外键语义，先建 review_queue，再建 eval_runs，再 ALTER 问题池。全部按 utf8mb4 执行。

- review_queue：id、normalized_question、ai_suggested_answer、occurrence_count、review_status（待审 / 通过 / 驳回）、approved_answer、created_at、updated_at。
- eval_runs：id、triggered_by（定时 / 手动）、dataset_size、metrics JSON、created_at。
- low_confidence_questions：新增 retrieved_chunks JSON、matched_review_id、其索引及 ON DELETE SET NULL 外键。

第二份补充迁移只新增以下运行所需信息，不改上述字段含义：

| 表 | 补充字段 / 索引 | 用途 |
| --- | --- | --- |
| low_confidence_questions | user_message_id、assistant_message_id：BIGINT UNSIGNED NULL | 定位原轮，旧行兼容 NULL；软引用，不阻止历史数据恢复 |
| low_confidence_questions | 唯一索引 (assistant_message_id, source) | 同一回答同一入口入池幂等，旧 NULL 行仍兼容 |
| low_confidence_questions | snapshot_status：ENUM('captured','not_retrieved','unavailable') NULL | 区分没检索、零召回与旧证据缺失；旧行 NULL 表示尚未核验 |
| low_confidence_questions | processing：JSON NULL | 有版本的内部任务状态，具体键见下文；NULL 旧行默认不自动处理 |
| review_queue | knowledge_chunk_id：BIGINT UNSIGNED NULL，唯一索引 | 本缺口对应的唯一知识块，防止重复审批重复插入 |
| review_queue | publication：JSON NULL | 有版本的发布状态、尝试数、下次重试时间、安全错误和 published_at；已审核不等于向量已就绪 |
| eval_runs | run_key：VARCHAR(64) NULL，唯一索引 | 同一轮结果重试写表幂等；实际新运行必须有 UUID，兼容既有行 |

JSON 元数据使用严格固定 schema，拒绝模型或页面填写状态、计数、时间和知识主键。时间使用带时区的 ISO 字符串；数据库原有 created_at 语义保留，报告声明时区。所有 BIGINT 对浏览器输出字符串。

processing 的键为 schema_version、status（pending / running / retry_wait / matched / failed）、attempt_count、next_attempt_at、last_error（安全错误码 / 阶段 / 说明）、prompt_versions、normalized_draft、dedup_cursor 和 candidate_fingerprint。publication 的键为 schema_version、status、attempt_count、next_attempt_at、last_error 和 published_at。新行完整初始化；未知版本停止处理，不猜默认值。获得唯一 worker 所有权后，重启时把遗留 running 记录转为可重试或已达上限的失败，不保留永久“处理中”。

迁移工具先核对实际列、索引、ENUM 和外键，区分未应用 / 完整应用 / 不完整或冲突；冲突停止，不重建表。旧拒答行、faith_cases 和知识原文不丢弃。测试迁移先在 3308 验证；业务库应用前只执行已批准的增量迁移并保存结构核对结果。

## 7. 标准化、语义查重与后台任务

### 7.1 任务生命周期

应用 lifespan 管理有强引用的后台任务和独立模型 / 数据库资源。入池请求只等待落池短事务，不等待 LLM。worker 轮询已启用且 matched_review_id 为 NULL 的记录；唤醒信号只作加速，MySQL 记录是恢复依据。

同一个数据库的处理 worker 使用会话绑定的 MySQL 命名锁，避免多个服务同时归并同一池。worker 获锁后逐条处理，模型调用不占数据库事务；短事务在调用前持久化尝试计数，最后才原子提交归并与计数。退出先停止取新任务，有限等待后取消并回收；重启后从未归并记录继续，不能依赖仅内存队列。

每条原话每轮最多三个持久化尝试。只对临时网络 / 超时故障退避重试；参数错误和无效结构结果保留失败，供人工重试。余额不足、鉴权失败或预算耗尽立即停止相关模型处理，不自动反复重试消耗额度，聊天主链路不被 worker 故障拖垮。

### 7.2 标准化与示例答案

复用当前模型客户端与配置，使用独立后台阶段和严格 JSON 输出 normalized_question / ai_suggested_answer。标准问题保留商品型号、条件、否定和诉求，去掉情绪表达；订单号、手机号等具体个案留在原话，不写进通用 FAQ 标题。

示例答案只供人工备查，显式显示 AI 草稿；依据不足时写明待核实、待补充，不能编造金额、时效、保修政策或工具查询结果。实时物流 / 订单问题的示例应说明需要实时查询，不把单次工具结果发布成长期 FAQ。原话、召回片段均作为待分析的数据，不能改变系统指令或触发业务工具。

Prompt 版本、输入边界和结构校验可追溯。标注样例覆盖同义问法、不同型号 / 条件、否定、投诉情绪、实时业务、无证据、超长问题和提示注入；记录实际模型评估结果，不以解析单测冒充语义验证。

### 7.3 待审队列语义查重

只与 review_status=待审的已有缺口做 LLM 语义判断。问题按有界批次提供，队列超预算就分页扫描，未检查完整候选范围前不能直接判为全新。保留分页进度和调用预算；预算不够则停留未归并，不能静默只看最近几条。

输出 matched_review_id 或 null，并严格检查返回 ID 来自本批候选；不能依据字符串相似度冒充语义查重。查重命中时锁定原话和目标 review 行，重验目标仍为待审，原子更新 matched_review_id 与 occurrence_count；目标已审核则重新核对剩余待审项，不把新反馈塞回已结束队列。

新缺口只插入一行 review_queue，初始出现次数为 1，并在同一事务连接原话。计数按“同一逻辑用户轮次在同一缺口出现一次”处理：同轮先拒答后 👎 两个来源都保留，但不重复加出现次数；没有消息定位的显式历史补处理按原话 ID 计数。重跑已归并记录不增加次数。

## 8. 人工审核与知识发布

后台列表按待审优先、出现次数降序，显示标准问题、示例答案、状态。详情分页显示所有归并原话、来源、时间、原轮定位和证据快照，并明确区分零召回、未检索与旧证据不可恢复。

通过时必须提交非空的人工核准答案，可以修改标准问题；不能因为点击“通过”就默认为 AI 草稿已正确。问题描述、示例、片段均以纯文本展示，避免把模型 / 用户内容当 HTML 执行。驳回保留原话与原因，不写知识库。

通过的 MySQL 短事务锁定 review 行，核验当前待审，在同一事务插入一个 FAQ 知识草稿（pending）、保存 knowledge_chunk_id、核准答案和 review_status=通过。复用 / 提取现有 KnowledgeRepository 的事务内插入能力，不另造不受控知识写入入口。相同答案的重复通过返回原知识 ID；已审核后提交不同答案返回冲突，不暗中改历史。

后台随后复用 step03 的“原文权威 + pending 恢复”以及当前 HybridKnowledgeJobs 路径：按同一知识主键嵌入、写入在线混合索引、检查 ACK 和读回，再置 done。沿用知识作业命名锁，与 CLI 重建 / 向量化互斥。失败保留原知识 ID 和 pending 状态；重试不再建知识块。

publication 状态明确为 pending / running / ready / failed，每次尝试持久化计数，最多三个自动临时错误重试；额度和鉴权错误立即暂停。只有实际知识行 done 且索引核验完成，才显示“已入库、可检索”。审核通过但未就绪时显示“已审核，入库中 / 入库失败”，允许人工重试。拒绝与发布就绪不能相互混淆。

原始外键保留 ON DELETE SET NULL，但后台不提供删除队列接口，以免删除落点后旧问题被意外再次归并。

## 9. 自动化评估与趋势

新增本步骤流水线，复用 step04 数据装载、完整证据组 Recall@5 / Recall@10、MRR@10、充分性、grounded 生成与联合裁判能力；使用当前 hybrid_rerank 和本步骤证据闸门。既有四策略工作台、历史 v1 / v2 报告和评估 CLI 行为保持兼容，不把旧物理块 Recall 与新完整组分数画在同一条趋势线上。

评估对象是冻结 step04 语料下的当前 RAG 实现，用独立测试数据库和专属临时集合重建，评完清理自有资源。它用于观察模型、Prompt、检索与闸门的回归，不冒称生产知识库全量覆盖率。人工审核补知识的闭环另用在线新会话实测，不能靠把答案预先塞入冻结评估资料来制造提升。

支持两种明确范围：

- `full_300`：完整 merchant-rag-300-v1，定时运行配置使用该范围。
- `smoke_20`：从同一数据集的留出侧五个桶各固定选四题，按同一 hash 排序取前四题；不足四题预检失败，不能从校准侧凑数。清单先冻结、同一清单连跑两轮，用于本步骤管道和趋势验收；页面和报告注明 20 题，不冒充全量成绩。

真实两轮默认使用 smoke_20，至少一题有可计算 Faithfulness；只生成拒答导致分母为零不能算生成段验收通过。全量命令必须可执行；是否在本次交付实际跑两轮 full_300，及各阶段模型请求硬上限，写入实施计划供用户明确审阅。服务器 30 元预算不当作模型消费授权，也不沿用 step08 已结束的调用额度。

校准只使用校准侧标签。若展示留出质量结论，单独提供 held_out 范围；不得把 smoke_20 或 full_300 中参与校准的题目当成独立泛化证据。完整数据集、留出、冒烟范围的分数分开显示。

每轮先生成 run_key、冻结范围、模型 / Prompt / 校准 / 数据集 fingerprint 和资源归属，再执行检索、闸门、内容自评、生成、裁判，输出逐题文件及指标。N/A、失败、未执行行分别计数，Faithfulness 的零断言行不计入有效分母；失败不能填 0 或 1 假装有效样本。

metrics JSON 包含：schema / metric 版本、run_key、scope、dataset_id / hash、配置和语料 fingerprint、状态、各指标 value / valid_n / 排除原因、完成 / 失败数、实际调用数 / Token、耗时和报告定位。eval_runs.dataset_size 是这轮选中的题数，不是“题数 × 策略数”。

同一 run_key 的重复发布只产生一行；因网络失败重新读取状态不会重新收费。运行中进度保存在受管 runtime manifest，轮次终止后幂等落 eval_runs；重启按 manifest 对账、补存终态，不重跑收费阶段。中断 / 失败也保存可核验的阶段结果。趋势主线按相同数据集、范围、语料及指标定义分组，允许对比模型 / Prompt / 闸门版本变化并在变化点明确标注，失败轮显示断点；每个点保留实际有效分母。两轮分数可以持平，不为演示上涨而改结果。

提供手动触发与应用内定时调度。调度时区 Asia/Shanghai，默认计划每天 03:00；实际收费定时开关默认关闭，实施计划列明预算后可显式启用。重启不补跑全部错过日期；已有运行时跳过重叠触发并记录。定时器与手动入口共享数据库级运行互斥和持久化状态，进程崩溃后标记原运行中断，不偷偷重放收费阶段。

## 10. 后端接口和前端配套

| 接口 | 行为 |
| --- | --- |
| POST /api/conversations/{id}/feedback | 只接 👎，定位并核验原助手回答，幂等入池；👍 保留前端现有行为 |
| GET /api/review-queue | 状态过滤、出现次数及分页 |
| GET /api/review-queue/{id} | 缺口详情、发布状态、分页原话与召回片段 |
| POST /api/review-queue/{id}/approve | 人工核准问题 / 答案，原子审核并进入发布 |
| POST /api/review-queue/{id}/reject | 保存驳回决定与原因 |
| POST /api/review-queue/{id}/retry-publication | 对同一知识 ID 显式恢复失败发布 |
| POST /api/low-confidence-questions/{id}/retry | 显式重试失败的标准化 / 查重任务 |
| GET /api/observability/intent-usage | 带时间范围的意图 Token 汇总，数据源为本地 Langfuse |
| POST /api/eval-runs | 手动启动冻结范围，携带幂等 run_key |
| GET /api/eval-runs、GET /api/eval-runs/{run_key} | 轮次、状态、指标、逐题报告定位和趋势 |

反馈写入成功后才显示“已反馈”；网络失败允许重试，不锁死为成功，不影响继续聊天。历史回载提供可反馈的原助手消息定位，未完成 / 错误 / 中断回答不出现反馈操作。

新增简单后台页，沿用现有样式：待审列表 / 详情和核准答案编辑、发布结果、意图 Token 汇总、评估趋势。前端不展示数据库主键等无助于用户决策的内部配置，但详情保留审核所需原话与片段。没有要求复制课程截图皮肤。

本步骤沿用现有本机演示的身份与写接口边界：会话归属从服务端取得，管理接口显式开关启用，仅允许配置的本机 Host / Origin，JSON 写请求，不信任代理头绕过。没有远程多用户管理角色系统；如以后对外部署，需另行设计身份授权。前端不持有 Langfuse Secret Key，统计和管理请求经本后端。

## 11. 验证、验收和交付

后端按 TDD 验证真实不变量；Prompt 用冻结标注样例 / 评估集，前端按 Vibe Coding 做浏览器效果验证，不额外套前端单测或审查流程。

| 用户验收 | 所需证据 |
| --- | --- |
| 任意请求可展开完整链路 | 新会话真实 trace URL；节点 / prompt / 自定义工具 / 检索 / usage / 耗时齐全；追踪故障不拖垮聊天的验证 |
| 知识缺口兜底并进待审 | 至少一条原话、来源、历史原文与得分快照、归并 ID；证明不是事后重检 |
| 人工审核后再问可答 | 验收专用模拟 FAQ 在审核前拒答；人工核准、同一知识 ID 完成索引核验后，新会话真实检索并依据核准答案回答 |
| 👎 入池且去重 | 原轮消息、问题池记录和 review 落点；重复点击不新增，同轮不同入口不重复计出现次数；无检索与零召回分开展示 |
| 按意图统计 Token | 至少多个意图的实际 generation 与汇总对账；包括分类前消耗，估算与未知单列，后台成本另列 |
| 至少两轮评估趋势 | 两次独立执行的 smoke_20 run_key、eval_runs 行、逐题报告、有效分母和趋势；全量命令另交付，未跑的全量不标通过 |

同时验证：校准 / 留出不混用；低分与服务故障不混淆；worker 重启恢复、并发去重及提交原子性；AI 返回非法结构 / 越权 ID 不污染队列；重复审核不重复知识；向量失败可恢复；余额不足停止自动重试；迁移完整性、旧会话与 step08 工单确认 / MCP 查询回归。

真实验收在新增模拟会话和带归属记录的专用 FAQ 上进行。每项外部模型 / 嵌入 / 重排请求按物理调用计数，含失败；计数上限、输入范围及清理归属在实施计划写明。不能用离线 mock 结果宣称真模型 / 真 trace 验收完成。

最终交付：本地 Langfuse 与客服启动命令、PyCharm 操作入口和浏览器地址；功能演示问句与审核 / 反馈 / SQL 核对步骤；真实两轮趋势与测试报告；实际新增存储占用；持续更新的 `dev-notes/ch09.md`。正式 spec 获批后再编写实施计划，计划获批并选择执行方式后开始实现。

## 12. 来源与当前边界

详细源码位置、官方 URL 和只读基线见 [接口核对](../research/2026-10-19-observability-flywheel-apis.md)。本文尚未证明依赖安装、镜像拉取、实际 Langfuse 初始化、阈值效果或真实评估通过；这些由实施及验收产物证明。

## 13. 用户原始 DDL（原文备查）

以下仅存档设计输入；实际sql文件在实施计划批准后创建并核对，不将本附录当成已迁移证据。

```sql
-- =============================================================
-- step09 · 可观测性与数据飞轮 · 建表 DDL
-- 本步骤新建:review_queue(待审队列,标准化去重后的知识缺口)
--          eval_runs(自动化评估流水线每轮结果,连起来看趋势)
-- 并给 step04 的 low_confidence_questions 加两列:
--   matched_review_id 记这条原话查重后归并到哪个缺口
--   retrieved_chunks  存落池时的召回片段快照,审核页给人看
-- 建表顺序:先 CREATE review_queue,再 ALTER low_confidence_questions 加外键指向它
-- =============================================================

-- 确保中文 ENUM 定义值/DEFAULT/COMMENT 按 utf8mb4 解析
-- (否则 latin1 默认的 mysql client 会把中文 double-encode,ENUM 值存成乱码)
SET NAMES utf8mb4;

-- 待审队列:一行 = 一个去重后的知识缺口;查重命中就累加 occurrence_count,不新建行
CREATE TABLE review_queue (
  id                  BIGINT UNSIGNED NOT NULL AUTO_INCREMENT COMMENT '缺口主键,也是查重命中要返回的 matched_question_id',
  normalized_question VARCHAR(512)    NOT NULL                COMMENT '标准化后的 FAQ 式问题',
  ai_suggested_answer TEXT            NULL                    COMMENT '模型生成的示例答案,备查',
  occurrence_count    INT UNSIGNED    NOT NULL DEFAULT 1      COMMENT '出现次数,查重命中累加,越高越该优先补',
  review_status       ENUM('待审','通过','驳回') NOT NULL DEFAULT '待审' COMMENT '人工审核状态',
  approved_answer     TEXT            NULL                    COMMENT '审核通过时补的核准答案,走 ch03 落库流程写回知识库',
  created_at          DATETIME        NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '首次入队时间',
  updated_at          DATETIME        NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
  PRIMARY KEY (id),
  KEY idx_review_status (review_status)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='飞轮待审队列';

-- 评估轮次:一行 = 评估流水线跑完的一轮,各指标分数收进 metrics JSON,按时间连起来就是趋势线
CREATE TABLE eval_runs (
  id           BIGINT UNSIGNED NOT NULL AUTO_INCREMENT COMMENT '评估轮次主键',
  triggered_by ENUM('定时','手动') NOT NULL DEFAULT '定时' COMMENT '这轮怎么起的:定时任务,或某次改动后手动跑',
  dataset_size INT UNSIGNED    NOT NULL                COMMENT '这轮跑的评估集条数',
  metrics      JSON            NOT NULL                COMMENT '各指标分数,如 {"recall_at_k":0.82,"mrr":0.71,"faithfulness":0.90}',
  created_at   DATETIME        NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '跑完落表时间',
  PRIMARY KEY (id),
  KEY idx_created_at (created_at)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='自动化评估流水线轮次结果';

-- 原话流水记归并落点:标准化查重后指向 review_queue 里的缺口行,NULL 表示尚未处理
-- 再存一份落池当时的召回片段快照(Top 几条的原文和得分),没走检索的入口为 NULL
ALTER TABLE low_confidence_questions
  ADD COLUMN retrieved_chunks  JSON            NULL COMMENT '落池时的召回片段快照:Top 几条的原文与得分,审核页展示用;没走检索为 NULL' AFTER reason,
  ADD COLUMN matched_review_id BIGINT UNSIGNED NULL COMMENT '查重后归并到的缺口,指向 review_queue.id' AFTER retrieved_chunks,
  ADD KEY idx_matched_review_id (matched_review_id),
  ADD CONSTRAINT fk_lcq_review FOREIGN KEY (matched_review_id) REFERENCES review_queue (id) ON DELETE SET NULL;
```

### 最终审查补充

数值单位漏检修正使用新算法版本ch09-four-signal-zero-allow-v3；kg/公斤/千克、L/升、ml/毫升等别名作同单位精确归一，不推断证据未写明的范围，也不把不同单位自动换算成等价。超大数值按字符串规范化，避免舍入变成相等。v1/v2历史语义保留供旧报告复现；线上使用当前已核验派生v3。校准与留出边界在JSON反序列化时校验唯一/互斥/分组/hash，重算再绑定冻结数据集划分、原始规则及校准样本hash。新的实际20题发生在v2阶段；v3仅做同一批已存证据的离线锚点回放（20条决策相同），不记作第二轮付费评估。

### 2026-10-20 页面风格纠偏

按用户最新原话“风格不要照抄他的，页面风格保留的像聊天界面那样的，借鉴即可”，此前参考图的奶油橙色、粗黑边框、方格纸不再作为视觉验收要求。功能、信息层次和实际数据继续保留；待审、观测与成本、原话证据、审核弹窗和图表统一沿用聊天页字体、浅灰绿底色、墨绿主色、细边框和圆角。前端按既定Vibe例外直接调整，不变更后端接口、评估指标或调用预算。
