# 冻结 300 题 RAG 评估交付状态

2026-10-10：**N1/N2 最小修复与专项验证进行中；真实 pilot/full 未运行，收费门禁关闭。Task10 尚未完成。** 本文交付当前工程证据、已知限制与复现命令，不包含模型质量分数或策略胜者。

本文采用已复核生产提交 `77d7d02ef1fb500e3ae00f069c368fd204135b3a` 的接口与测试证据；初次文档读取 checkout 为 root 文档提交 `2bdb84c43c39b8934a4bfb36c9aa92ecf91d1806`，未改变其生产源码。后续最小修复的源码、专项结果与放行结论须由控制端补齐后，才能恢复真实阶段。本次仅写文档，没有启动应用、数据库生命周期、模型或重复回归。

## 实际运行与待交付内容

| 阶段 | 冻结计划规模 | 本次实际状态 | 实际运行 ID / 新质量结果 |
| --- | --- | --- | --- |
| Pilot | 固定10题 × 4策略 = 40条 | 未启动 | 未生成 |
| Full | 300题 × 4策略 = 1200条 | 未启动，门禁关闭 | 未生成 |

这里的计划规模不是已持久化记录数。没有新运行 manifest，不能将尚未启动的计划写成1200条 `not_attempted` 或虚构有效分母。没有生成 `merchant-rag-pilot.json/.md` 或 `merchant-rag-comparison.json/.md`；Task9受控页面夹具、1200条受控规模报告和真实服务检索测试都不计收费试运行，也不授权全量。

后续获准真实运行后，公共交付文件位于本目录，保留同一真实run的JSON/Markdown、指纹、请求数、完成/错误/未执行阶段、逐桶/总体和四路共同有效子集；原始裁判及归属快照只留本地忽略目录。部分错误如实交付，禁止重复收费全量洗分。若pilot出错，保存公共pilot报告并保持full锁定，不用空白或控制数据填成比较分数。

## 工程证据与仍关闭的门禁

| 验证范围 | 已存在的原始结果 | 解释 |
| --- | --- | --- |
| Task10初次工程提交 `ab25215` 默认 / 显式集成 | 1358 passed、116 skipped / 1474 passed、0 skipped | 历史工程证据，包含遗留10ms累计期限进入/关闭诊断；不替代后续修复回归。 |
| `77d7d02` 生产修复的默认完整套件 | 1386 passed、116 skipped，250.03秒 | 默认服务开关造成的116skip保留。 |
| 显式集成首轮 | 4 failed、1498 passed，376.57秒 | 四个真实子进程死亡窗口fixture缺少出处接线，原失败保留。 |
| 最小fixture修正后的四参数专项 | 4 passed，46.49秒 | 使用真实配置生产者，未改变生产期限或放松断言。 |
| 最后获准的显式完整套件 | 1502 passed、0 failed、0 skipped，388.30秒 | `--run-mysql --run-milvus`；默认套件对应生产源码未变，没有再跑默认洗掉旧失败。 |
| 真实隔离服务检索证明 | 50块、B1/E5×4策略8条、cleanup成功，Milvus RPC44 | 业务84块、旁置知识/台账与其他集合保持；六类模型/嵌入/重排请求均0。 |

原始日志保留于本地 `.cache/final-fix-full-default.log`、`final-fix-full-integrations.log`、`final-fix-child-provenance-green.log`、`final-fix-full-integrations-green.log`；服务证明为 `.cache/final-fix-service-proof.json`。本文读取这些已有证据，没有执行新套件。受控模型与确定性向量替身使真实MySQL/Milvus行为可验证，仍不证明GLM答案与裁判语义质量。

整分支审查的原 I1–I4 已处理：资料出处与独立配置指纹正确接线；保存稳定逻辑组、精确答案要点、完整来源及实际排序分数；原raw历史迁出静态目录；在线固定拒答遵守原绝对期限/取消。后续唯一范围复核发现两个直接新增问题：

- **N1：合法裁判要点逆序导致发布失败。** 裁判接受完整唯一的point-ID集合，但新审计校验误要求返回列表与rubric同序。多要点题合法的 `[p2,p1]` 会在保存时抛错，可能丢失已完成判定并使run失败。需要最小ID关联修复及“逆序合法判定实际持久化完成”的专项证明，仍严格拒绝缺失/重复/未知ID。
- **N2：审计升级前v2报告下载409。** 旧公开JSON没有新 `audit:null` / `source_map:null` 字段，当前严格导出比较将合法旧成对报告判为不一致。需要限定旧缺省字段的兼容，以及两个格式HTTP下载成功、所有原文件SHA/mtime不变的专项证明；保留canonical字节、Markdown一致性、终态与白名单要求，不在GET中补写历史审计。

两项最小修复与专项验证正在进行。已有套件绿色不覆盖这两个组合触发点，不能证明收费门禁已解除。修复、定点复核及控制端明确放行均完成后，才可启动真实pilot；本交付文档不授权模型调用、另起审查、合并或推送。

## 冻结资料与解释边界

版本 `merchant-rag-300-v1`，资料位于 `evals/datasets/merchant-rag-300`。A_policy、B_model、C_colloquial、E_multi、D_absent各60题，共300题；D在内部保留兼容名 `D_unanswerable`。八篇实际50块，切分1200/120；319个证据组、411个要点。原CSV、修订版、逐题审计与运行JSONL分开，原标签未被覆盖。固定pilot为 `A21,A43,B3,B54,C5,C35,D1,D3,E2,E19`，每桶两题，未按分数抽样。

| 冻结对象 | SHA-256 |
| --- | --- |
| Dataset指纹 | `d4da3bd7b61c85bf236de955fadc0dcb806f2384c417dfe2b3dd686372f7476e` |
| 语料摘要 | `c188bcabb1b3fa6a5e4e72284d0726f96e2b2cff6e0a1c48245dea85e792ef10` |
| 运行题摘要 | `3b2901de79f80c54453805038e354aea9cadabf024fafe2802c78ce7a75c4f96` |
| 审标摘要 | `b4015c5d11675137634fb8c0e186796aa3be94744c9081b9a661f9962e840925` |
| 原CSV | `1c145124f298dc224210016e89bf3f1ed619bf18dea5f544616ebd4713053a09` |

详细审标与六个联合裁判人工样例见[材料审计](rag-evaluation-materials-audit.md)及[标注样例](joint-generation-v2.1-labeled.json)。材料参考同一金标题库构造，结果仅支持这版合成语料的受控比较。candidate_k=50恰好覆盖全部50块，候选覆盖饱和不证明检索泛化；实际报告还需分别核对首命中、Top-5/10完整组、Prompt引用覆盖、生成要点、忠实度、拒答和每指标valid_n/excluded。四策略生成共同子集须四条都合法完成，不能用单路分母替代。

当前没有新真实逐题数据，无法给出具体型号BM25排名、口语/跨节遗漏或某策略优势；不能套用教程分数。历史30题的120条、101完成/19错误和原指标保留，与新300题分开。原始历史字节移至 `evals/legacy/rag-evaluation-history.json`，SHA为 `4fcbf4d3d6ffbd7957caecbbbe0fce8efaffd3aebf0286ba67fabe846c2f1bcd`，安全历史API继续展示，静态原raw不再公开。

## PowerShell复现命令

命令在当前checkout根目录执行，沿用本地 `.env` 的实际模型、密钥、校准值与预算。只读配置参考如下，本阶段未执行启动命令；已有8000/8001服务保留。换端口时来源也须显式匹配。

```powershell
$env:PYTHONUTF8 = '1'
$env:PYTHONIOENCODING = 'utf-8'
$env:RAG_EVALUATION_ENABLED = 'false'
$env:RAG_EVALUATION_ALLOWED_ORIGINS = '["http://127.0.0.1:8002","http://localhost:8002"]'
uv run --locked uvicorn app.main:create_app --factory --host 127.0.0.1 --port 8002 --workers 1
```

`/`为聊天，`/rag-eval`为工作台。只读HTTP不补写旧manifest或审计。CLI的实际参数为：

```powershell
uv run --locked python -m evals.rag_workbench validate --dataset merchant-rag-300-v1
uv run --locked python -m evals.rag_workbench show --run-id '<已有实际32位run_id>'
```

validate全离线；show通过存储读取已有检查点，不启动模型，但CLI存储读取可调和计数，不能用它代替严格不写盘的HTTP历史检查。下面仅给出明确放行后可用的运行命令；实际Task10先从浏览器启动固定pilot一次，再凭同run的合法服务端门槛启动full一次，不能另用CLI重复同批。

```powershell
# 收费门禁明确放行后，才启用并重启自有单worker服务。
$env:RAG_EVALUATION_ENABLED = 'true'
uv run --locked python -m evals.rag_workbench run --dataset merchant-rag-300-v1 --scope pilot
uv run --locked python -m evals.rag_workbench run --dataset merchant-rag-300-v1 --scope full
```

CLI与HTTP共用OS锁，只允许一个运行，题并发最多2；取消后持锁直至清理与终态发布，重启保留中断，不自动续收费任务。HTTP基址 `/api/rag-evaluations`；启动仅接受 `{"dataset_id":"merchant-rag-300-v1","scope":"pilot"}` 或合法full，取消发送空JSON `{}`；不开放模型、预算或任意输出路径。

本地 `runtime/rag-evaluation/{run_id}/` 已忽略，不提交raw、连接信息或所有者快照。新 `source-map.json` 捕获实际50块完整来源与本轮主键，逐题audit捕获逻辑AND/OR组合、精确要点和实际候选/最终score/kind；公共报告只嵌一份map，单题详情也可在清理后解释遗漏组与非Prompt候选。旧未捕获数据保持null/N/A，不用今日资料补成历史证据。原2MiB单文件与128MiB导出上限保持。

运行继续沿用GLM `glm-5.3-flash`、BGE-M3与既有重排模型；最终回答512、改写/自评/裁判输出各2048、裁判输入16000、证据8000；改写/自评/FAQ/聊天/裁判期限60/20/90/240/60秒，模型零重试，不自动提高预算或换模型。真实报告将冻结当时配置和Prompt/端点摘要。隔离资源限定3308/customer_service_test与本run UUID知识集合；3307业务库、knowledge_hybrid和其他资源保持。合法判定的faith台账新增必须与异常资源变更区分。
