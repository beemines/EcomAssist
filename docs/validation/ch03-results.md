# 第三章 Dense 知识库验证记录

执行分支：`feat/ch03-dense-knowledge`，实施 worktree：`D:/shixi/ecommerce-customer-service/.worktrees/ch03-dense-knowledge`。Tasks 1–5 已由控制器独立审查通过。Task 6 实施与实证已落盘，整分支审查及集成/完结由控制器继续处理。

## 实际云端检索与应用回答

[完整合成数据报告](ch03-knowledge-live.json) 实际运行时间为 **2026-10-07 14:20:53–14:21:11 UTC**（北京时间 22:20:53–22:21:11）。固定测试 MySQL `127.0.0.1:3308/customer_service_test`，自建集合 `knowledge_test_5aa96bb0427f4887900fc5271370b592` 的完整 UUID 以报告为准；不是正式主库 `3307/customer_service` 或生产集合 `knowledge`。

先实际调用 SiliconFlow `BAAI/bge-m3` 验证 1024 维，再用产品适配器校验 INT64 显式主键、auto_id=False、1024 维、Strong、FLAT/COSINE；之后通过 import_document 导入 demo-policy/demo-faq/demo-manual 的 7 块，通过仅选择本次 IDs 的 PendingVectorizer 完成 7 块。未改写查询，未加入关键词分支、混合检索、重排或阈值。

| 标注原问法 | 预期章节 | 实际主键（Top3） | 结果 |
| --- | --- | --- | --- |
| 邮费是多少 | 合成演示政策/标准配送费用（80） | 82,80,81 | 命中 |
| 快递费用怎么收 | 同上（80） | 82,80,81 | 命中 |
| 发货运费标准 | 同上（80） | 80,82,81 | 命中 |
| 退货运费谁付 | 合成演示政策/退货申请（81） | 80,81,82 | 命中，规则为另确认 |
| 售后申请如何提交 | 合成演示操作手册/演示申请步骤（85） | 85,83,81 | 命中 |
| 火星今天的天气如何 | 无相关章节 | 86,82,81 | 域外误召回观察 |

attempted=6 / not_attempted=0；必需域内 5/5，全部标注 **5/6**。域外 required=false 是本章明确的无阈值 Dense 限制，仍记录 passed=false 和实际三条不相关结果。命中定义为 Top3 包含明确目标章节，不代表所有三条均相关，亦不宣称域外拒答已实现。退货问题不能从“8 元”推出退货责任；目标章节明确另确认。

通过真实 create_app lifespan、真实模型工厂、真实 MySQL/Milvus、应用 API 创建独立演示会话 `9007199254741164`，发送 **“邮费是多少”**。实际持久 query_faq 参数为 `{"keyword":"邮费是多少"}`，命中 82/80/81；HTTP 请求 2 次，done=1，101 个非空 delta，完整回答已持久化并与 SSE 文本一致。在线模型 `glm-5.3-flash`，原输出预算 **512** 保持。app 结构验收通过，耗时约 12.68 秒。上游请求数未单独观测，报告 model_request_count=null，不用理论次数充当实测。

实际完整回答保存在报告；控制器代理已逐项对照原 demo-policy 与 demo-faq 检查：8元、单笔商品实付满99包邮、大陆普通配送区域普通小件、港澳台/偏远/大件另确认、明确合成演示非真实商家政策、没有越界操作承诺，标记 `controller_fact_review_passed`。这是控制器代理事实复核，不是用户真人签字，也不是仅关键词自动评分。

HTTPX ASGITransport 会缓冲 SSE；本次证明实际应用事件协议及持久流水，不能证明浏览器/网络分帧或首 token 网络耗时。单个原问法成功不代表全部在线工具或所有问法质量。未额外重复已通过的 Task 5 八类云端调用。

## 真实进程中断恢复

[首次失败](ch03-recovery-launcher-failed.json)：2026-10-07 14:22:10–14:22:16 UTC，attempted=1 / not_attempted=1，ValueError，未取得有效 kill 验收。Windows `.venv/Scripts/python.exe` 是转发器，诊断的 Popen PID 47996 与执行 Python PID 16900 不同；checkpoint 按设计拒绝错 PID。仅终止 harness 自建句柄，没有对任意宿主机进程或生产服务执行 kill。按该次 UUID 检查未发现存活 worker。失败原报告保留，不用后续成功抹去。

真实 OS 子进程回归 RED：1 failed / 4.15s。最小修复为启动 `sys._base_executable`，显式提供当前 venv 的已安装 site-packages；Popen.pid 就是写 checkpoint 的执行 worker，不放宽 PID 相等校验。聚焦 GREEN：12 passed / 4.12s。

[完整恢复报告](ch03-recovery-live.json)：**2026-10-07 14:25:35–14:25:56 UTC**，attempted=2 / not_attempted=0，两个边界均通过。与异常模拟集成不同，这里确实终止自建 OS 进程并启动另一个正常 worker。

| 边界 | 被终止执行 PID | 重启 PID | 中断前 | 重启后 |
| --- | --- | --- | --- | --- |
| MySQL pending 已提交后 | 67484 | 96016 | IDs89/90，pending2、vector0 | done2、vector2、unique2、replay0 |
| 实际 Milvus upsert 返回但 mark_done 前 | 43912 | 54440 | 实际 ack91/92、pending2、vector2 | done2、vector2、unique2、replay0 |

checkpoint PID 与自建 Popen 句柄一致；Windows kill returncode=1，正常重启 exit0。每块正文 SHA256 前后相等，vector_id 与 MySQL id 一致；没有重复有效主键或丢正文。MySQL 测试行、UUID 集合和独立演示会话均已按所有权清理，未清空共享测试库或删卷。物理 Milvus 历史版本/存储压缩不在此次唯一可查询主键验收范围内。

## QA 提取证据与范围

最终整分支审查 R2 修正了 prompt 的同义合并指令：不同真实问题及配对答案/来源保留原文，只有必要隐私删除允许改变通用措辞。原八类标签保持，新增第九 `distinct_phrasings`：规范化“邮费是多少？”和“快递费用怎么收？”都必须出现，并分别保留 conversation:11:message:111 / conversation:12:message:121。该标签 scorer 的原问题相等和配对来源比较有定向反例测试，改写、缺失、错误/错配来源或不同答案均失败。

[当前 prompt 实际九类结果](ch03-qa-live-final9.json) 来自唯一一次完整运行，UTC 2026-10-07 15:32:13.6780720 至 15:32:57.8228298，glm-5.3-flash / QA2048，attempted9/not_attempted0/pass9/fail0，CLI exit0，无错误与 pooled retries；[当前受控九类结果](ch03-qa-controlled-final9.json) 为9/9。新双问法实际提取2条并通过严格规范化原问题/配对来源 scorer。报告仅保存计数和 scorer 判定，未保存实际抽取字面字符串，不宣称人为逐字审核或广泛模型质量保证。下列旧八类原证据独立保留，不能用旧8/8替代新9/9。

[Task 5 原始真实八类结果](ch03-qa-live.json) 原样复制出临时计划目录。原报告无内嵌运行时刻；源文件写入时刻为 **2026-10-07 14:04:06 UTC**，该时间是证据文件时间，不冒充请求起止时间。模型为既有 glm-5.3-flash，离线 QA 专用预算 2048，attempted8/pass8/fail0；gold/source/raw 严格校验保持。八类仅为提交的合成会话：通用1QA、重复1QA、冲突2QA；无答案、个案标识、虚构退款、mock工具、注入均0QA并通过。Task 6 没有修改抽取 Prompt/模型/代码，因此直接保留该真实验收，未再花费八次调用。此前 512 长度截断及多轮失败见 dev-notes/ch03.md，不把重试结果拼成原始8/8。

## 命令和限制

实测命令：

```powershell
$env:UV_CACHE_DIR = 'D:/shixi/ecommerce-customer-service/.cache/uv'
uv run --locked pytest tests/test_knowledge_evaluation.py -q
uv run --locked python -m evals.evaluate_knowledge --output docs/validation/ch03-knowledge-live.json
uv run --locked python -m evals.knowledge_recovery --output docs/validation/ch03-recovery-live.json
uv run --locked pytest tests/test_tool_evaluation.py tests/test_knowledge_evaluation.py -q
uv run --locked pytest -q
uv run --locked pytest tests/integration --run-mysql --run-milvus -q
git diff --check
```

报告统计/失败停机/恢复断言初始有效 RED 为10 failed/1.20s；初始 GREEN10 passed/3.34s。额外应用审计证明正常 SSE+持久回答仍不能让错误知识主键通过；与新增 PID 回归共12 passed/4.12s。修改邮费标注 expected_found=true 并更新旧审计受控夹具后，受影响24 passed/4.72s。受控边界测试不代表云端语义或实际答案质量。

API 核对：Context7 FastAPI lifespan、HTTPX0.28.1 ASGITransport 不自带 lifespan、SQLAlchemy2.0 AsyncSession 短事务/select/delete、PyMilvus async query/describe_collection；安装版 FastAPI0.142.2/httpx0.28.1/PyMilvus3.0.2/SQLAlchemy2.0.54 及 query 签名已本地确认。没有升级依赖。

最终回归结果：

| 实际命令/范围 | UTC 时间窗口 | 结果 |
| --- | --- | --- |
| uv run --locked pytest -q 首跑 | 14:34:01–14:34:36 | 2 failed,650 passed,62 skipped / 31.03s |
| 旧夹具修正后受影响三个测试文件 | 14:35–14:36 | 68 passed / 4.46s |
| uv run --locked pytest -q 最终树 | 14:36:16–14:36:47 | **652 passed,62 skipped / 26.89s** |
| uv run --locked pytest tests/integration --run-mysql --run-milvus -q | 14:34:30–14:35:14 | **60 passed,0 skips / 39.77s** |
| tests/test_knowledge_ingestion.py 中两个实库 node，--run-mysql --run-milvus | 14:37:09–14:37:13 | **2 passed,0 skips / 1.09s** |

首跑两个失败分别为 `test_annotated_cases_structure_and_controlled_reinjection[faq_shipping_dense]` 与 `test_annotated_cases_cover_exactly_eight_required_categories`。诊断确认旧 tests/tool_fakes.FAQ 仅退货返回结果，以及类别断言仍列“邮费 FAQ 预期未命中”；按新的实际 Dense 命中标注修正受控夹具与类别，没有修改产品或金标凑结果。这项新失败修复是复跑全离线的原因；60条实库集成未重复。

普通离线62次 gated skips＝tests/integration 的60条＋文件外2条真实 ingestion 用例。显式服务验收已将全部62条实际执行，不能把离线skips当通过。文件外两条的完整命令为：

```powershell
uv run --locked pytest tests/test_knowledge_ingestion.py::test_import_commits_pending_neighbors_isolated_per_document tests/test_knowledge_ingestion.py::test_import_pointer_write_failure_rolls_back_all_chunks --run-mysql --run-milvus -q
```

范围限制：尚未主库建库/部署/注册计划任务；没有读取生产私人会话，没有生产 mine/run-daily；无阈值 Dense 有域外误召回；精确去重不等同语义去重；时间窗口只验证当前固定 UTC MySQL。所有报告只含合成内容、公共配置、主键及错误类型；`.env` 与原始用户个人历史不入报告。原 DDL、产品 UI、在线模型配置和主 checkout prompt.md 保持。控制器独立 Task 6 审查、整分支审查、最终验证及 finish 决策仍待执行。

交付检查：候选17文件按配置SecretStr逐字安全扫描 secret_hits=false / matched_files=[]；QA证据副本与Task5原文件逐字相等；git diff --check通过。Task6没有DDL/UI/config差异。本地提交与独立审核结果由控制器的后续记录补充。
