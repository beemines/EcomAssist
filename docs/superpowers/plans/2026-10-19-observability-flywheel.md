# 本地可观测性与数据飞轮 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 在本地 Langfuse 展开客服完整链路和意图 Token 花销，让三路知识缺口经人工审核回写知识库，并实际保存两轮可对比的评估结果。

**Architecture:** 独立 Compose 管理 Langfuse；现有 LangGraph 构造时统一配置追踪，业务执行通过 Runtime 中的可选适配器增加子 observation。MySQL 问题池是后台工作的恢复来源，标准化查重与知识发布使用受管任务和短事务，评估复用 ch04 的冻结资料与指标而不改旧四策略工作台。

**Tech Stack:** Python>=3.11,<3.14；现有 FastAPI0.142.2、SQLAlchemy2.0.54、MySQL8.4、LangGraph1.2.15、langchain-core1.6.6、SQLite checkpoint、Milvus3.0.2、MCP1.30.0 / adapters0.3.2；新增 langfuse==5.0.2，服务端 v4.63.0；原生 HTML/CSS/JavaScript。

**Spec:** [已批准设计](../specs/2026-10-19-observability-flywheel-design.md)。用户于2026-10-19批准本文，选择“Native 顺序实现，新建第九步隔离 worktree”；实施分支feat/observability-flywheel，起点6d0f646。当前产品基线为 `f44e4f9`，实施起点包含其后的已批准设计和本计划文档提交。

## Global Constraints

- 本地 Docker Compose 自部署，默认 http://127.0.0.1:3000；不回落到 Langfuse Cloud，不购买云服务器。SDK5.0.2、服务端v4.63.0和既有核心依赖不自行替换。
- 镜像全部锁版本或digest；官方Compose浮动tag不直接投入使用。正式镜像不可得或依赖冲突时，按用户要求停止说明，不换技术方案。
- 统一追踪使用图构造处 compile(...).with_config(callbacks=[handler])，不改变 checkpoint / add_messages；实际工具执行不因追踪失败被重放。
- 用户原始ch09 DDL完整保留，必要补充字段严格按spec第6节；迁移只增量、先测试3308再业务3307，旧数据和工具审计不删除。
- 正式规则的校准和留出不能混用；校准文件签名与模型 / Top-K / 预算一致。空证据拒答，依赖故障不得伪装为知识缺口。
- 同一助手消息同一source入池幂等；同一逻辑用户轮次同一缺口只计一次出现次数。反馈只读原轮，不能重新检索或猜相邻问题。
- AI示例答案仅供备查；非空人工核准答案才能发布。审核通过与索引ready分开，重复提交不重复知识，仅发布本缺口关联的知识ID。
- 后台最多三个持久化尝试；只重试临时故障。余额不足 / 鉴权错误暂停，不自动消耗后续记录。命名锁连接失效后不得继续提交旧任务。
- 后端TDD；Prompt以标注样例 / 评估集验证；前端Vibe Coding，不安排前端brainstorm、TDD或code review。
- 每个任务完成即时更新dev-notes/ch09.md的原话、产物/结果、纠偏、翻车返工，和任务一起提交；不收尾集中补写。
- 保留8004 / 8005、8101 / 8102及其归属记录。新客服8006、独立checkpoint；只管理本章自有进程和Compose项目，Start-Process使用Hidden。
- 本计划批准前只核对源码和写文档，不安装、部署、迁移或外发模型请求。具体框架API使用前继续核对[官方与固定源码记录](../research/2026-10-19-observability-flywheel-apis.md)。

## Review Focus

1. 已有quality严格核验遇到合法ch09扩展：只接受本章精确列 / 索引 / 外键，不把所有结构漂移放开。任务3固定测试。
2. 👎点在旧轮、两轮文字相同、完成根缺失或已变更：匹配原助手和用户身份，保留真快照，不能用最新轮或相邻SQL猜配对。任务4固定测试。
3. 模型返回队列外ID、审批与查重并发、命名锁丢失、重启恢复：不错误归并、不重复计数，失去所有权立即停止提交。任务3、5固定测试。
4. 审核成功但向量失败 / 响应丢失 / 其他pending混在库里：只处理原知识ID，未ready不宣称可检索；重试不新建行。任务7固定测试。
5. 回调并发、resume、分类前用量、usage缺失及API游标重复：不串会话、不双计Token，不把未知费用画成零；导出故障不影响回复。任务1、2、8固定测试。

## 文件、类型与验证约定

仓库根为 `D:/shixi/ecommerce-customer-service`。以下路径相对实施工作区；执行时所有命令在该工作区运行。产品逻辑放在专责模块，main.py / workflow.service.py只增加绑定和生命周期胶水。

| 单元 | 文件职责 |
| --- | --- |
| 本地部署与追踪资源 | compose.langfuse.yaml；app/observability/runtime.py；scripts/start-langfuse.ps1；专用ignored环境文件 |
| 执行追踪与汇总 | app/observability/tracing.py、intent_usage.py、demo.py；app/api/observability.py |
| 数据与状态 | sql/ch09-ddl.sql、ch09-runtime.sql；app/flywheel/types.py、migration.py、repository.py |
| 快照与反馈 | app/flywheel/snapshots.py、feedback.py；app/api/feedback.py |
| 后台处理 | app/flywheel/prompts.py、processing.py、worker.py、runtime.py、cli.py |
| 置信度 | app/quality/evidence_confidence.py、calibration.py；冻结split/rule产物 |
| 审核发布 | app/flywheel/publication.py；app/api/review_queue.py；现有knowledge仓储及HybridKnowledgeJobs的受限入口 |
| 评估流水线 | app/eval_pipeline/types.py、runner.py、manager.py、store.py、schedule.py、cli.py；app/api/eval_runs.py |
| 页面与交付 | app/static/review-queue.html / .css / .js，chat.js反馈；docs/ch09-local-demo.md、ch09-manual-acceptance.md、ch09-pycharm-acceptance.md |

跨任务接口在各任务Interfaces块定义，HTTP与领域ID均用十进制字符串；SQL落库处校验并转换。UTC带时区字符串保存任务JSON时间，界面和定时解释时区Asia/Shanghai。新包按需要增加__init__.py，不能为了凑文件先建空产品框架。

纯转换/指标函数同步；仓储、网络服务和close方法异步。Worker.start同步创建受管任务。测试文件中的构造fixture由对应测试实现，不能为让测试通过而向产品加入专用分支；缺少新模块的首次RED必须再经最小实现运行到具体行为断言。

`PY`表示实施工作区的 `.venv/Scripts/python.exe`；下文命令给出完整相对可执行路径。现有pytest真实开关是 `--run-mysql` / `--run-milvus`。新增真实本地Langfuse测试使用任务1添加的 `--run-langfuse`；普通pytest不访问收费接口。所有实际结果以当次输出记入dev-notes，不预填通过数量。

## 执行环境与外部调用边界

实施先沿用Native；是否建立新worktree在计划审阅时确认。选择隔离时，先检查当前git-dir / common-dir及app附件，优先对本仓库使用原生create_worktree，显式从本地master开始，以包含未推送的设计 / 计划文档，不使用默认远程旧起点。已有隔离则复用。原生工具对目标仓库不可用时才用技能允许的Git fallback；沙箱拒绝则报告并按技能在当前工作区分支继续，不能绕过拒绝。

新环境不得复用或更新正在服务8005的venv。只将本项目已使用的.env复制到新工作区的ignored位置，不输出Key，不读取其他账号凭据。真实API继续使用项目当前模型与端点，不为分数换模型、窗口或Agent步数。

本次真实验收只发送：冻结ch04演示资料与问题、已列出的Prompt标注用例、新建模拟会话中的问句、模拟订单1001 / 2002，以及明确标记的验收专用FAQ。Langfuse接收这些新执行的本地trace；不批量上传旧会话、不处理processing=NULL的历史问题、不发送真实联系方式。准入前检查所有新HTTP客户端都接入同一计数器。

| 上游 | 本计划总硬上限 | 分项规划（失败也计数） |
| --- | --- | --- |
| GLM模型HTTP | 280次 | 标注Prompt最多24；页面闭环含后台处理最多80；两轮20题各最多80，合计160；余下16仅用于同范围定点复验 |
| 嵌入HTTP | 450次 | 冻结语料种子、300题校准/留出检索、额外回归、40题评估、页面检索和专用FAQ发布全部合计 |
| 重排HTTP | 450次 | 与上述检索对应，不因失败重新获得额度 |

复用AcceptanceCallCap的三provider持久化SQLite账本，run_id固定为 `ch09-local-20261019`，路径为 `runtime/ch09-evidence/call-ledger.sqlite`。所有聊天、后台、CLI和评估资源共用该run_id / 路径；重启不清零，不增加上限，不换run_id绕过。SDK模型自动重试为0；后台受控重试仍计数。Langfuse本地HTTP和纯SQL不算模型额度。超限或余额错误立即停止相关真实验收，如实交付未完成项，追加消费须再取得授权。

本次不执行两轮full_300，不开启每日真实收费调度。实现并验证这两个入口，但额外运行不包含在本计划调用授权里。30元是用户此前服务器预算，不保证上述模型用量折合30元；本地部署没有云主机租费。

## Task 1：可独立启动的本地Langfuse及追踪资源

**Files:** Create compose.langfuse.yaml、app/observability/runtime.py、app/observability/local_stack.py、scripts/start-langfuse.ps1；Modify pyproject.toml、uv.lock、.env.example、.gitignore、app/config.py、tests/conftest.py；Test tests/test_langfuse_runtime.py、tests/integration/test_langfuse_transport.py。

**Interfaces:**
- `validate_local_langfuse_url(value: str) -> str`只接受显式回环HTTP(S) URL。
- `LangfuseRuntime.from_settings(settings: Settings) -> LangfuseRuntime`；属性`handler`；`async close(timeout_seconds: float = 5) -> None`。关闭幂等、导出失败不抛到聊天；测试可注入client / exporter。
- 此任务只提供可注入的client / handler资源；执行scope及其类型完全由任务2增加，任务1不能导入尚未创建的tracing模块。
- `python -m app.observability.local_stack prepare|up|status|stop --port 3000`统一生成本地配置及调用固定Compose项目；PowerShell脚本只转发到该入口，`-PrepareOnly`对应prepare。stop保留数据卷，up先检查端口和项目归属。

- [x] **1. 建立已同意的工作区并跑基线。** 读取using-git-worktrees；核对AGENTS、git分支/状态、.worktrees忽略和已存在服务。同步现有锁定依赖到独立venv后，运行`.venv/Scripts/python.exe -m pytest -q`，保存基线日志；基线失败先报告原因，不把旧问题归到本章。
- [x] **2. 编写失败测试。** `test_rejects_cloud_destination`断言下例；另测缺BASE_URL、凭据被异常/日志隐藏、关闭超时有界且不反转业务结果。只对这些行为做TDD，不写镜像名称镜像式单测。

```python
def test_rejects_cloud_destination():
    with pytest.raises(ValueError):
        validate_local_langfuse_url('https://cloud.langfuse.com')
```

- [x] **3. 运行RED。** `.venv/Scripts/python.exe -m pytest tests/test_langfuse_runtime.py -q`；确认因尚未实现的本地地址/生命周期行为失败，记录失败断言，不接受拼错测试路径。
- [x] **4. 最小实现并集成。** 以`uv add --no-sync langfuse==5.0.2`更新锁，核对原核心版本未变后`uv sync --frozen`；若冲突停止。按固定官方Compose核对正式镜像tag/digest，写独立项目/网络/卷、回环3000、有界容器日志及关闭遥测。脚本生成ignored密钥环境文件、官方headless初始化、只检查/管理本项目；SDK仅注入必要LANGFUSE变量，不能把Compose的所有Postgres/Redis变量塞入严格Settings的.env。不打印密码。实现Runtime及`--run-langfuse`测试开关。
- [x] **5. 验证GREEN与本地栈。** 重跑上述单测；先`pwsh -NoProfile -File scripts/start-langfuse.ps1 -PrepareOnly`生成ignored环境文件，再`docker compose --env-file runtime/langfuse/local.env -f compose.langfuse.yaml -p ecs-ch09-langfuse config --quiet`，最后`pwsh -NoProfile -File scripts/start-langfuse.ps1`。运行`.venv/Scripts/python.exe -m pytest tests/integration/test_langfuse_transport.py --run-langfuse -q`，写入非LLM测试span并经本地API读回；服务端/SDK版本、UI可登录、端口、镜像/卷基线保存。不调用模型。
- [x] **6. 即时记录并提交。** 更新dev-notes的四项、本文复选框和实际镜像版本，提交`feat(ch09): bootstrap local Langfuse`。此后所有任务完成均同样即时记录。

## Task 2：图追踪与意图Token汇总

**Files:** Create app/observability/tracing.py、intent_usage.py、app/api/observability.py；Modify app/workflow/graph.py、runtime.py、nodes.py、service.py、app/tools/executor.py、app/main.py。实际接线补充app/observability/runtime.py、app/context/summarizer.py / manager.py、app/retrieval/service.py，覆盖既有后台摘要与Agent FAQ；Agent本身通过共享引擎与检索入口获得追踪，未为凑文件单独改动。Test tests/test_workflow_observability.py、tests/test_intent_usage.py、tests/integration/test_langfuse_workflow.py，扩展tests/test_langfuse_runtime.py / test_context_manager.py及相应旧测试边界。

**Interfaces:**
- `ExecutionIdentity(conversation_id: str, user_message_id: str, execution_id: str, purpose: str, replay: bool=False)`。
- `begin_execution(runtime: LangfuseRuntime, identity: ExecutionIdentity) -> ExecutionTrace`创建任务隔离的根scope，负责结束/异常/取消收回，不改变业务返回值。
- `ExecutionTrace.set_intent(intent: str, confidence: float|None, route: str) -> None`；`finish(outcome: str) -> None`；`operation(name: str, *, input: dict, metadata: dict) -> context manager`。上下文按执行隔离。
- `summarize_intent_usage(roots: Sequence[dict], observations: Sequence[dict]) -> list[dict]`消费规范化SDK副本；`IntentUsageReader.read(from_time, to_time) -> dict`负责游标、去重、缓存和服务错误。

- [x] **1. 编写失败测试。** `test_preclassification_generations_belong_to_final_intent`用root intent=物流和g1(10输入/2输出)、g2(3/1)，对返回列表的物流行断言`row['actual_tokens'] == 16`、`row['model_calls'] == 2`，重复g1不增加；父span的汇总不累加。另测缺usage单列、未知价格无货币数值、分页游标重复不死循环、并发/取消不串根、replay不产生新generation、resume关联同一逻辑轮次但新execution、exporter故障回复仍成功。
- [x] **2. 运行RED。** `.venv/Scripts/python.exe -m pytest tests/test_workflow_observability.py tests/test_intent_usage.py -q`，确认目标断言失败。
- [x] **3. 实现统一绑定与业务span。** 图构造处绑定一次handler；每次_produce/恢复请求建立execution scope，分类后更新根，结束前封存意图。自定义检索、Workflow工具和统一引擎记录子操作；模型usage只由generation记一次。Runtime仅加可选适配器，关闭本章时旧行为保持。后台链使用独立purpose根。不得复制Secret或整个Runtime到trace。
- [x] **4. 实现只读统计接口。** GET /api/observability/intent-usage接受带时区时间范围，默认最近7天、最长90天，SDK分页读取根和generation并按trace关联最终意图；缓存60秒。未知usage和进行中执行单列，缺页/重复游标报不完整，不返回伪全零。
- [x] **5. 验证并提交。** 重跑单测和本地Langfuse集成；集成用注入模型/工具运行真实LangGraph和本地导出，不消耗模型额度。复验现有workflow/工单确认测试，更新记录，提交`feat(ch09): trace workflows and aggregate intent usage`。

## Task 3：原DDL、补充迁移和事务仓储

**Files:** Create sql/ch09-ddl.sql、sql/ch09-runtime.sql、app/flywheel/types.py、migration.py、repository.py、cli.py；Modify app/db/models.py、app/quality/migration.py、tests/conftest.py；Test tests/test_flywheel_state_types.py、tests/integration/test_flywheel_migration.py、tests/integration/test_flywheel_repository.py；Extend tests/integration/test_quality_migration.py。

**Interfaces:**
- `ProcessingState` / `PublicationState`严格实现spec第6节的JSON键、状态、版本和最多3次尝试。
- `NormalizedDraft(normalized_question: str, ai_suggested_answer: str)`、`ReviewCandidate(id: str, normalized_question: str)`、`SemanticMatch(matched_review_id: str|None)`在types.py定义，仓储本任务已使用draft，后续Prompt任务直接复用。
- `RetrievalSnapshot`封装snapshot_status和可为NULL的payload；`PoolInput`含可信会话/用户消息/助手消息ID、raw_question、source、reason、snapshot。
- `FlywheelRepository.enqueue(item: PoolInput) -> PoolReceipt(id: str, created: bool)`；`enqueue_in_session(session: AsyncSession, item: PoolInput) -> PoolReceipt`不自行commit。
- `ReviewAssignment(pool_id: str, review_id: str, occurrence_count: int, created: bool)`；`assign(pool_id: str, *, matched_review_id: str|None, draft: NormalizedDraft) -> ReviewAssignment`原子创建/归并。
- `get_review(review_id: str) -> dict`；`list_reviews(*, status: str, offset: int=0, limit: int=20) -> dict`返回items/total；`review_details(review_id: str, *, offset: int=0, limit: int=50) -> dict`返回review/raw_questions/total，分页limit最高100。
- `migrate_flywheel(database: Database) -> None` / `verify_flywheel(database: Database) -> None`；CLI `python -m app.flywheel.cli migrate --database test|configured`，test固定3308且校验库名，configured显式使用当前业务库。

- [x] **1. 编写失败测试。** `test_ch09_extension_is_exactly_verified`覆盖新建/重复执行原DDL和补充迁移、部分结构/错误ENUM/错误外键拒绝、utf8mb4中文、旧数据保留；旧quality核验只接受精确已知扩展，未知列/索引继续报漂移。`test_two_sources_share_one_occurrence`断言`len(raw_rows) == 2`且`review['occurrence_count'] == 1`；另测同助手同source并发唯一、归并中断整体回滚、超过2**53的合法BIGINT ID保持字符串、非法JSON版本拒绝。
- [x] **2. 运行RED。** `.venv/Scripts/python.exe -m pytest tests/test_flywheel_state_types.py tests/integration/test_flywheel_migration.py tests/integration/test_flywheel_repository.py --run-mysql -q`；使用独立测试库/自有行，确认功能缺失而失败。
- [x] **3. 实现迁移和类型。** 原DDL按spec第13节用户原文逐字段保留，补充迁移按已批准spec第6节落7个必要字段及索引。实现严格结构契约与已知扩展识别，启动校验不暗中ALTER。扩展quality核验只投影已验证的已知附加项，不宽松忽略任意列。新代码连接不完整schema须明确提示迁移。
- [x] **4. 实现短事务仓储与CLI。** 所有归并状态、计数和matched_review_id同一事务提交；锁目标仍待审，目标已审核返回ReviewChanged错误。唯一冲突重新读原回执，不能以捕获异常后盲插新行解决。新processing初始化，旧NULL默认不自动发给模型。
- [x] **5. 验证并提交。** 重跑RED集合及`.venv/Scripts/python.exe -m pytest tests/integration/test_quality_migration.py tests/integration/test_quality_repository.py --run-mysql -q`。只在3308应用验证迁移；业务3307留任务10显式应用。更新记录，提交`feat(ch09): persist flywheel state and safe migrations`。

## Task 4：原轮快照、拒答入池及👎后端

**Files:** Create app/flywheel/snapshots.py、feedback.py、app/api/feedback.py；Modify app/workflow/state.py、nodes.py、agent.py、persistence.py、app/quality/repository.py、app/context/history_reader.py、app/main.py；Test tests/test_retrieval_snapshots.py、tests/test_feedback_api.py、tests/integration/test_feedback_storage.py。

**Interfaces:**
- `capture_retrieval_snapshot(payload: dict, *, prompt_ids: Sequence[str], strategy: str, retrieved_at: datetime) -> RetrievalSnapshot`最多10条、先按rerank排序，保留原文/得分/送模标记。
- `FeedbackService.submit(conversation_id: str, *, user_id: str, assistant_message_id: str, checkpoint_id: str|None=None) -> PoolReceipt`只使用服务端原根与SQL。
- `QualityRepository.commit_refusal`增加可选的可信`user_message_id`和`snapshot`；有本章上下文时助手消息与enqueue_in_session同一事务，保留旧调用兼容。

- [x] **1. 编写失败测试。** `test_feedback_reads_original_turn`构造同问句不同证据的两轮，对旧助手反馈断言`stored_snapshot == original_snapshot`且不等于新轮快照；修改知识原文后仍取旧片段。`test_no_retrieval_is_not_zero_recall`断言未检索payload为None、零召回payload['chunks']==[]。另测旧payload缺失unavailable、整根缺失409、越权会话/助手ID、伪checkpoint、未完成回答、重复点击、入池事务失败不能留半条助手/假成功、Agent追加FAQ也能回捞。
- [x] **2. 运行RED。** `.venv/Scripts/python.exe -m pytest tests/test_retrieval_snapshots.py tests/test_feedback_api.py tests/integration/test_feedback_storage.py --run-mysql -q`。
- [x] **3. 实现快照与拒答接线。** State新增每轮重置的retrieval_snapshot / retrieval_performed；在成功精排后、预算投影前捕获Top-K，以真实prompt_ids打标。Widget引用字段不变。历史完成根核验包含新快照身份；新轮可追溯，旧轮按明确兼容规则处理。两种拒答来源均写原始问句和快照。
- [x] **4. 实现反馈接口。** POST /api/conversations/{id}/feedback仅接受assistant_message_id和可选checkpoint_id；严格JSON，服务端demo-user归属、SQL正文及完成根核验，不能从页面接raw_question或chunks。不让查找根的游标持有期间再调用同saver其他接口造成死锁。
- [x] **5. 验证并提交。** 重跑集合及现有会话读取/引用/拒答测试，确认SSE done的原两字段契约未破坏；更新记录，提交`feat(ch09): collect turn-bound feedback and evidence snapshots`。

## Task 5：Prompt标准化、分页语义查重与受管worker

**Files:** Create app/flywheel/prompts.py、processing.py、worker.py、runtime.py；Extend types.py、repository.py、cli.py、app/main.py；Create evals/flywheel_cases.jsonl、evals/evaluate_flywheel.py；Test tests/test_flywheel_processing.py、tests/test_flywheel_worker.py、tests/integration/test_flywheel_recovery.py。

**Interfaces:**
- 消费任务3的NormalizedDraft / ReviewCandidate / SemanticMatch；模型ID不得来自批外。
- `FlywheelProcessor.process(pool_id: str) -> ReviewAssignment|None`用注入模型、仓储、时钟、调用计数；`FlywheelWorker.start() -> None` / `async close(timeout_seconds: float=30) -> None`管理强引用任务和数据库锁。
- `FlywheelRuntime`是main生命周期绑定器，拥有独立后台资源；聊天不等待process。`record_retry`持久化status/attempt_count/next_attempt_at/安全错误，后台暂停原因可读。

- [x] **1. 先固化Prompt评估材料。** 创建12组标注用例，覆盖同义/不同型号/不同条件/否定/实时订单/无依据/注入。每组声明标准化必须保留事实、是否应匹配和人工示例答案边界；提供CPU离线schema检查。本任务不以解析测试代替语义验证，真实最多24次Prompt调用统一留任务10执行。
- [x] **2. 编写并运行RED。** `test_out_of_batch_match_does_not_mutate_queue`断言队列/归并ID均不变；`test_quota_error_pauses_worker`断言首条1113后`model_calls == 1`且下一条未处理；`test_lost_lock_cannot_commit`断言丢锁后无归并。另测字符串布尔/额外字段、超预算候选分页全扫才新建、审批同时发生则重验、模型调用不持SQL事务、进程取消/重启不重复计数、最多3次临时重试。运行`.venv/Scripts/python.exe -m pytest tests/test_flywheel_processing.py tests/test_flywheel_worker.py tests/integration/test_flywheel_recovery.py --run-mysql -q`。
- [x] **3. 实现Prompt及处理器。** 标准化和查重严格JSON，示例明确为待审草稿；候选每批最多20条且输入最多12000估算Token，保存draft/cursor/fingerprint以恢复。每次process至多6次模型调用且总期限120秒，超预算保留游标、停留未归并，不能把未扫描部分当作无重复；最多三个持久化尝试使重启也不能无限重发。标准化材料优先原始问题和预算内完整证据块，完整快照仍保留供人工看。只处理待审候选，模型返回ID须属于本批。队列空时直接新建，不为此多调一次模型。配额/鉴权及无效结构不做自动修复循环。
- [x] **4. 实现worker和生命周期。** MySQL命名锁绑定独占连接，取任务/递增尝试/提交分别用短事务。临时失败退避5秒、30秒，第三次失败进入failed；永久失败立即failed。恢复遗留running要先获得唯一所有权。余额/鉴权错误暂停后台，显式管理重试或服务重启后才再尝试；统一账本不重置。关闭有界收回子任务，不只丢失create_task引用。
- [x] **5. 验证并提交。** 重跑TDD与标注材料离线检查，mock模型同时压测不同会话以证明聊天不等后台；更新记录，提交`feat(ch09): normalize and deduplicate knowledge gaps in background`。

## Task 6：可复现校准与正式证据检查

**Files:** Create app/quality/evidence_confidence.py、calibration.py；Extend app/flywheel/cli.py、app/workflow/nodes.py、agent.py、runtime.py、app/main.py、app/core/sufficiency.py；Create tests/fixtures/flywheel/calibration_rankings.json；Test tests/test_evidence_confidence.py、tests/test_evidence_calibration.py、tests/test_confidence_gate_integration.py。

**Interfaces:**
- `ConfidenceRule`严格保存版本、数据/模型/预算hash、经验分布、权重、阈值；`EvidenceDecision(useful: bool, evidence_confidence: float, features: dict, reason: str, rule_version: str)`。
- `CalibrationSample`含eval_id / group_id / bucket、特征、充分性标签和排名来源；`CalibrationSplit`含calibration_ids / held_out_ids及fingerprint；`CalibrationResult`含rule、两侧混淆矩阵/分母和来源。均在calibration.py明确定义。
- `evaluate_evidence(payload: dict, rule: ConfidenceRule, *, top_k: int, budget_fingerprint: str) -> EvidenceDecision`只读实际送模证据。
- `build_calibration_split(dataset: FrozenDataset) -> CalibrationSplit`；`fit_confidence_rule(samples: Sequence[CalibrationSample], split: CalibrationSplit) -> CalibrationResult`只用calibration侧；`verify_rule`负责线上签名。
- CLI `python -m app.flywheel.cli calibrate --database test --output runtime/ch09-evidence/calibration --acceptance-run ch09-local-20261019`运行真实检索但不调答案模型；默认dry-run只列范围，不连接上游，实际执行需要显式`--execute`。

- [ ] **1. 编写失败测试。** `test_single_evidence_has_no_infinite_gap`断言`decision.features['gap'] == 0`且confidence有限；`test_held_out_labels_do_not_change_fit`断言仅改变留出标签后`new_result.rule == original_result.rule`。另测display夹心顺序不得当作Top1/2、空集拒答/非有限值错误、重复chunk不加count、常量特征仍可复现且不虚报好分、手填0.25/0.5不能代替校准来源、hash分组/回归不跨集合、权重平局/0权重、签名不符、内容自评不叠旧门槛及工具异常不入池。
- [ ] **2. 运行RED。** `.venv/Scripts/python.exe -m pytest tests/test_evidence_confidence.py tests/test_evidence_calibration.py tests/test_confidence_gate_integration.py -q`。
- [ ] **3. 实现规则与校准。** 按已批准spec精确执行分层split、百分位候选、经验分布、0～3非负权重与观察阈值搜索及平局决策。在线、校准和新评估共用prepare_workflow_evidence及同一实际evidence_token_budget / Top-K，不能各自截不同证据再算分。缺正/负标签或非法样本预检失败；保存calibration与held-out的原始特征/混淆矩阵/版本，不反向调留出。
- [ ] **4. 接入闸门。** 统一Workflow与Agent知识证据检查器；保持订单/政策顺序和业务数据路由。充分性服务在本章模式只做内容自评；旧calibrated_score和旧工作台行为保持。未产生真实校准前只用测试注入rule，不声称线上已校准。
- [ ] **5. 验证并提交。** 重跑TDD及现有sufficiency、after_sales、context预算用例，CPU样例确认可复现；真实300题检索和规则产出留任务10有计数执行。更新记录，提交`feat(ch09): calibrate and enforce evidence confidence`。

## Task 7：人工审核、按ID发布和失败恢复

**Files:** Create app/flywheel/publication.py、app/api/review_queue.py；Extend repository.py、types.py、runtime.py、cli.py、app/repositories/knowledge.py、app/knowledge/hybrid_jobs.py、app/main.py；Test tests/test_review_queue_api.py、tests/test_flywheel_publication.py、tests/integration/test_review_queue_storage.py、tests/integration/test_flywheel_publication_storage.py。

**Interfaces:**
- `KnowledgeRepository.add_chunks_in_session(session: AsyncSession, drafts: list[ChunkDraft]) -> list[int]`复用原插入校验，不自行commit；`pending_by_ids(ids: Sequence[int]) -> list[ChunkRecord]`限定目标。
- `HybridKnowledgeJobs.vectorize_ids(ids: Sequence[int]) -> int`复用原_write / ACK / readback / mark_done，调用方持既有knowledge作业锁；不扫其他pending。
- `PublicationReceipt(review_id: str, knowledge_chunk_id: str|None, status: str)`在flywheel/types.py补充定义，status只允许pending / running / ready / failed。
- `ReviewService.approve(review_id: str, *, approved_answer: str, normalized_question: str|None=None) -> PublicationReceipt`；`reject(review_id: str, *, reason: str) -> None`；`PublicationWorker.publish(review_id: str) -> PublicationReceipt`；`retry_publication`恢复原ID。

- [ ] **1. 编写并运行RED。** `test_duplicate_approval_keeps_one_knowledge_id`断言`first.knowledge_chunk_id == second.knowledge_chunk_id`且仅一条知识；`test_publication_does_not_consume_unrelated_pending`断言无关ID不在嵌入/向量写入集合。另测空核准答案422、相同内容重放/不同内容409、事务回滚无孤立知识、嵌入超时或Milvus ACK/readback失败保持pending/failed、响应丢失不重复。运行`.venv/Scripts/python.exe -m pytest tests/test_review_queue_api.py tests/test_flywheel_publication.py tests/integration/test_review_queue_storage.py tests/integration/test_flywheel_publication_storage.py --run-mysql -q`。
- [ ] **2. 实现审核事务。** 锁待审行，同一MySQL事务保存核准答案、pending知识、唯一knowledge_chunk_id和publication。驳回保留原话/片段。读接口分页，BIGINT字符串。管理写接口沿用显式本机Host/Origin、JSON与开关，不能仅靠按钮禁用防重复。
- [ ] **3. 实现受限发布。** 新公开按ID入口复用现有流程并持同一knowledge命名锁；只在done及索引读回完成后ready。临时错误最多3次、5/30秒退避；余额和鉴权停止，显式重试保留原知识ID。任务取消/重启不谎称就绪。
- [ ] **4. 验证GREEN及真实本地向量适配。** 重跑上述集合，再`.venv/Scripts/python.exe -m pytest tests/integration/test_flywheel_publication_storage.py --run-mysql --run-milvus -q`，使用注入确定性嵌入向量测试真实Milvus，不调付费嵌入。旧knowledge任务、撤权工单和退款流仍通过。
- [ ] **5. 即时记录并提交。** 提交`feat(ch09): review and publish approved knowledge idempotently`。

## Task 8：单策略评估、落表和受控定时

**Files:** Create app/eval_pipeline/types.py、runner.py、manager.py、store.py、schedule.py、cli.py、app/api/eval_runs.py；Extend app/flywheel/runtime.py、app/main.py；Test tests/test_eval_pipeline_metrics.py、tests/test_eval_pipeline_manager.py、tests/test_eval_pipeline_schedule.py、tests/integration/test_eval_runs_storage.py。

**Interfaces:**
- `EvalScope = Literal['smoke_20','full_300']`；`PipelineCaseResult`包含eval_id、状态/阶段、候选/精排/送模ID、实际引用、decision、answer、claims/points、usage、error。
- `PipelineReport`在types.py定义，含run_key、scope、dataset_size、dataset/config/corpus fingerprint、status、records、metrics、usage及资源归属；`RunView`是其去敏状态投影，含run_key / status / progress / dataset_size / metrics。
- `PipelineRunner.run(dataset: FrozenDataset, *, scope: EvalScope, rule: ConfidenceRule, resources, cancel_event) -> PipelineReport`复用现有RetrievalService、SufficiencyService内容模式、grounded生成/FinalAnswerStream、GenerationJudge及完整组retrieval_metrics。
- `EvalPipelineManager.start(*, run_key: str, scope: EvalScope, triggered_by: Literal['手动','定时']) -> RunView`；`get_run`、`list_runs`、`close(timeout_seconds=30)`；`EvalRunRepository.publish(report: PipelineReport) -> str`run_key唯一。
- `EvaluationSchedule.next_due(now: datetime) -> datetime`按Asia/Shanghai每天03:00；`tick(now) -> str|None`注入时钟，开关默认关闭。
- CLI `python -m app.eval_pipeline.cli run --scope smoke_20 --run-key <UUID> --acceptance-run ch09-local-20261019 --execute`；缺execute只显示预检。full_300命令同接口，不属于本次真实运行额度。

- [ ] **1. 编写并运行RED。** `test_no_claims_is_not_perfect_faithfulness`断言`metrics['faithfulness']['value'] is None`且valid_n==0；`test_replaying_run_key_does_not_dispatch`断言第二次start后请求计数不变；`test_schedule_is_disabled_by_default`断言tick返回None。另测固定样例Recall/MRR等于ch04公共指标、错误/未执行分母、发布补存、重启不重放、03:00边界、手动/定时互斥、配置标记与scope分组。运行`.venv/Scripts/python.exe -m pytest tests/test_eval_pipeline_metrics.py tests/test_eval_pipeline_manager.py tests/test_eval_pipeline_schedule.py tests/integration/test_eval_runs_storage.py --run-mysql -q`。
- [ ] **2. 实现冻结范围及运行器。** 从留出侧每桶hash前4题组成smoke_20，full_300保留300题；冻结清单在收费前校验。最多2题并发，每题最多4次GLM（改写/自评/生成/裁判），规则拒答可少于4次，模型SDK零重试；同源共享全局call cap。评估用3308自有行和临时集合，结果写当前业务eval_runs；评估拒答只进入独立评估产物/测试库，不自动制造生产待审任务，不触碰生产知识正文或原四策略报告。
- [ ] **3. 实现持久化管理及调度。** runtime manifest先记录run_key/归属/配置，再异步执行，终态幂等落eval_runs；数据库级互斥，关闭收回、重启修复中断。定时开关默认关闭，每轮也有本地上限，API不允许任意文件路径/模型/预算覆盖。
- [ ] **4. 验证GREEN与旧工作台兼容。** 重跑集合，以及现有rag_evaluation数据装载/指标/报告/manager/API测试；以注入模型跑两个完整smoke_20流程核对落表与清理，不将其称为真模型结果。
- [ ] **5. 即时记录并提交。** 提交`feat(ch09): persist evaluation runs and schedule bounded regressions`。

## Task 9：前端Vibe Coding与可操作的演示入口

**Files:** Create app/static/review-queue.html、.css、.js、app/observability/demo.py、scripts/start-observability-demo.ps1、scripts/observability-process-ownership.ps1、scripts/ch09-storage-evidence.py、scripts/ch09-offline-ui.py；Modify app/static/chat.js、必要导航及app/main.py静态路由；Create .run/CH09_01_Local_Langfuse.run.xml、.run/CH09_02_Customer_8006.run.xml、.run/CH09_03_Offline_Checks.run.xml；Test仅涉及后端/进程归属的tests/test_observability_startup_guards.py、tests/test_ch09_acceptance_cap.py。

**Interfaces:**
- `create_observability_app()`只读已批准本地配置；普通模式无验收cap，显式CH09_ACCEPTANCE才绑定本计划280/450/450持久化账本。
- `start-observability-demo.ps1 -Acceptance`启动8006且默认不启动真实定时；没有-Acceptance时不得带着耗尽账本作为普通服务。若已有8101/8102则只核对，不接管不明PID。
- `ch09-storage-evidence.py --conversation-id <id> --review-id <id> --run-key <UUID>`只读输出白名单事实，不输出Key或全库历史。

- [ ] **1. 直接实现页面。** 沿用现有视觉样式；聊天👎提交assistant_message_id，成功才锁定“已反馈”，失败可重试；历史回答使用原消息ID。后台列表、原话/证据详情、人工答案编辑、通过/驳回、发布状态与重试、意图Token表/图及评估趋势可操作。全部外来文本按textContent渲染。无前端brainstorm/TDD/code review。
- [ ] **2. 编写并跑后端守卫RED。** `test_restart_keeps_used_allowance`断言重新构造同run cap后counts不变；`test_ordinary_mode_has_no_acceptance_cap`断言普通模式health响应JSON不含验收run。另测cap覆盖后台/评估、PID复用和命令/路径不符拒绝终止，不结束真实不明进程。`.venv/Scripts/python.exe -m pytest tests/test_observability_startup_guards.py tests/test_ch09_acceptance_cap.py -q`。
- [ ] **3. 实现演示脚本及配置。** PyCharm本地栈配置使用Python模块app.observability.local_stack参数up，不依赖额外Shell插件；8006使用uvicorn factory，离线检查用pytest模块。运行配置只存设置文件路径，不存密钥。后台Start-Process使用Hidden，持久化真实进程身份。普通、验收配置分明；模型请求hook覆盖GLM、嵌入、重排的每个实际HTTP客户端。
- [ ] **4. 浏览器离线效果核验。** ch09-offline-ui.py在3308受控行上注入模型/规则/固定数据并标明离线预览，禁止真实上游dispatch；走反馈成功/失败、空队列、片段详情、审批验证、发布失败/ready和两轮图表，修正显示及交互。后端守卫重跑GREEN；该预览不作为最终普通服务。
- [ ] **5. 即时记录并提交。** 提交`feat(ch09): add flywheel admin and local acceptance entrypoints`。

## Task 10：整分支审查、真实闭环与交付

**Files:** Update dev-notes/ch09.md、本计划及API研究；Create docs/ch09-local-demo.md、docs/ch09-manual-acceptance.md、docs/ch09-pycharm-acceptance.md、docs/superpowers/reports/2026-10-19-observability-flywheel-acceptance.md；实际证据留runtime/ch09-evidence，不将密钥/旧会话提交。

**Interfaces:** 沿用任务1～9全部公共入口，不在验收脚本另造绕过正式检查器、权限或仓储的实现。一次独立后端整分支审查，前端按用户例外排除。

- [ ] **1. 提交前核对与一次独立审查。** 使用requesting-code-review，审查范围为后端/API/迁移/部署资源/计数/评估，检查五项Review Focus及spec覆盖；Native不做逐任务子代理。若有反馈，按receiving-code-review验证并补失败测试后修复，记录结论，不能仅根据代理口头结论宣称通过。
- [ ] **2. 跑最新自动回归。** `.venv/Scripts/python.exe -m pytest -q`保存全量结果；再运行本章integration文件加`--run-mysql --run-milvus --run-langfuse`，以及现有quality / context / tool-audit / ticket-confirmation关键集成。测试临时资源只清理有本轮归属的行/集合；临时目录位于工作区runtime，沙箱不能读本地服务时只对明确检查提升。
- [ ] **3. 应用业务增量迁移并准备计数。** 保存3307现状结构，运行`.venv/Scripts/python.exe -m app.flywheel.cli migrate --database configured`，再只读verify；不清表/重建。检查本轮账本初始状态、模型名称/端点和三个provider hooks，未覆盖不得发收费请求。
- [ ] **4. 在同一计数账本执行真实校准。** 运行任务6的calibrate命令加`--execute`，冻结split与rule，输出新旧闸门留出结果；运行旧八题的有限回归或明确其离线范围。将真实rule配置给8006，不改模型/窗口/步数来掩盖问题；记录嵌入/重排实际用量。
- [ ] **5. 执行有标注的Prompt评估。** `evals/evaluate_flywheel.py`以12组规范化/查重标注运行，最多24次GLM且零SDK重试；输出保留型号/否定/条件、查重命中/拒绝和草稿边界结果。仅改Prompt时按该集验证；若需额外请求从剩余额度记账，不自动扩容。
- [ ] **6. 页面真实闭环。** `pwsh -NoProfile -File scripts/start-observability-demo.ps1 -Acceptance`，仅新会话：问验收专用缺失FAQ→兜底→后台出现原话及当时片段→人工填明确标记为模拟政策的核准答案并通过→等待ready→新会话再问，依据真实检索核准答案回答。另对一条回答点👎、重复点/刷新重试验证幂等；同义问合并，不同型号/否定不误合。保留每轮trace URL、原话/快照/队列/知识ID及截图。
- [ ] **7. 核对多意图花销和旧章主链路。** 真实物流1001通过MCP、知识咨询、闲聊等新增问句产生完整trace；read-only统计与generation去重汇总对账，分类前消耗纳入最终意图，缺usage明确标记。工单确认/取消和退款的写入约束以自动回归证明，真实页面本轮不额外建工单/退款。页面及后台总计最多80次GLM，超限停止。
- [ ] **8. 两轮真实评估。** 通过正式评估API/CLI，以两个不同UUID run_key连续运行同一smoke_20和rule，所有资源共用本轮cap；单轮最多80次GLM，两轮最多160。核对eval_runs恰有两行、各20题、真实逐题裁判及非零Faithfulness有效分母、趋势/分母/失败点。不得复用旧报告填第二轮，也不承诺第二轮分数必然上涨。失败先保留产物，不静默重跑整轮。
- [ ] **9. 收尾与普通模式。** 只清理本轮受控临时评估资源，保留必要演示FAQ与trace及归属记录。记录Docker镜像/卷相对3.649/1.513GB的实际增量。把8006重启为普通模式，health确认无验收cap、定时收费仍关闭，本地Langfuse保留可查。用户手工重跑走明确命令，不再留“额度耗尽但服务就绪”的验收配置。
- [ ] **10. 验证文档并提交交付。** 使用verification-before-completion，按真实证据分别标注自动/本地集成/Prompt/页面/两轮评估结论、实际请求数、已知失败和未执行的full_300。提供PowerShell及PyCharm逐步流程，中文HTTP输出兼容Windows PowerShell5.1，优先用storage-evidence脚本避免乱码。更新dev-notes四项与finish记录，提交`docs(ch09): deliver verified local observability and flywheel`。分支集成/推送由用户后续明确指示，不把文档或测试完成等同于功能已验收。

## 内联计划自审与执行交接

| spec内容 | 任务 |
| --- | --- |
| 本地固定版本、资源/密钥/端口 | 1、9、10 |
| 统一trace、失败隔离、意图Token | 1、2、10 |
| 原DDL和补充字段、旧表严格兼容 | 3 |
| 三路来源、原轮快照与👎 | 3、4、9、10 |
| 后台标准化/语义查重/恢复 | 3、5 |
| 数据校准与内容自评边界 | 6、8、10 |
| 人工审核、同ID发布和读回 | 7、9、10 |
| 定时/手动评估、eval_runs趋势 | 8、9、10 |
| 前端Vibe Coding例外 | 9；后端API与守卫仍TDD |
| 六项真实验收、额度与交付留痕 | 10 |

已完成内联自审：每项任务列出可检查产物与验证命令；已修正跨任务类型先后依赖，后续任务沿用Interfaces中的同名接口；没有另造ch04指标或全库pending发布；五项Review Focus均指定失败测试；注入模型结果与真实验收分别留证；依赖、schema、全量评估和收费定时边界已列明。此结论仅指计划文档自审，不是产品测试或功能验收。计划审阅通过及工作区方式确认后，才调用executing-plans开始任务1。
