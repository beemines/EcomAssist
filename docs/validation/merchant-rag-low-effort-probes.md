# 评估专用 low：两条实际有界探针

2026-10-11，两条获准真实模型请求各执行一次，均合法结束。探针 ID `abcfea557efd4b62a5741fd65bfafa12`；这是失败样例的阶段验证，不能充当固定10题pilot、四策略质量比较或full门槛。[安全JSON](merchant-rag-low-effort-probes.json)保留实际配置、重建证明、请求数和时间。

| 原失败路由 / 本次阶段 | 实际结果 | UTC开始 / 结束 | 耗时 |
| --- | --- | --- | --- |
| A21/bm25 / judge | stop、严格完整JSON、p1/p2完整唯一；2/2要点覆盖、5/5断言支持 | 03:33:12.503903 / 03:33:19.305494 | 6.8015866999秒 |
| B3/bm25 / answer | stop、449字符、严格引用校验通过 | 03:33:19.307060 / 03:33:23.616220 | 4.3091686000秒 |

实际HTTP计数：judge1、answer1；rewrite/self_check/embedding/rerank/Milvus均0。retry0；出站请求均顶层 `reasoning_effort=low`、模型 `glm-5.3-flash`，裁判max_tokens2048/JSON模式，回答max_tokens512/真实流。由生产OwnedResources创建模型并借用生产GenerationJudge、FinalAnswerStream和validate_answer；没有受控HTTP替身、追加请求或更改合法性要求。客户端cleanup为ok=true/errors=[]/unverified=[]；未调用prepare、检索、自检或写入质量台账。

裁判HTTP200实际usage为prompt1454、completion430，其中reasoning111、total1884；回答沿用关闭额外usage帧的生产设置，没有使用量证据，不估算成本或reasoning消费。以上只是两条实际结果，不能证明原失败全由默认思考引起，也不能保证固定40条全部合法。

先离线完成两条重建，再执行任一请求：A21复用原224字符回答、7条实际Citation、2个AnswerPoint；B3从原50来源map及actual ranking/score/kind/candidate_count重建FAQ，通过原grounded system、空历史、eval-faq工具申请和生产build_evidence；10个Citation逐值等于原记录。生成输入不含gold/rubric。原生成消息没有独立保存，本次是同生产者/证据重建，不能宣称与原消息字节hash相等。估计输入预算分别5638/6666，实际裁判prompt usage以提供商1454为准；这两种计数方法不同。

生产源码 `cfc65fdb99e44de68c2727e05743a384bba6e89e` 已独立规格PASS/质量Approved；启动checkout `51edf90120010ceaa7ca0a5fa35c6954d3a25b1a` 仅后续root文档。新配置指纹 `191d53c027323fa8005327336e6ec0e737f7d196eebd6ad05f2dea7258f60913` 捕获专用low；剔除新effort字段与fingerprint后与原pilot配置逐值相等。模型、512/2048预算、所有期限/输入预算、重试0、冻结300题/50块、Prompt/端点均保持。在线模型参数不变。

原pilot `52678f9492114f1789466442e575c168` 与公开文件不改写：JSON SHA `b2865bbd127305bf2436b28c69fc1bdd35ac14a39f065f42bb5a9b9028725501`、Markdown SHA `48e5eeee19f0a20c0470fa90da92c28b3e12b96e66ef3ef84d20742bf72bc352` 已离线核对。两条探针没有补入原9/40分母或删除31条错误。

紧接两条合法探针的新环境检查发现3307/3308 MySQL及19530 Milvus均拒绝连接（10061），只读基线为OperationalError，独占8002启动因MilvusException2失败并退出；此时新pilot/full未启动，没有额外收费。Root随后明确授权仅恢复已有Docker Desktop/已核验容器与原卷，无pull/rebuild/migrate/reseed；恢复与新pilot状态另见[交付状态](rag-evaluation-delivery.md)，这段保留初次实际环境失败。任何后续新pilot必须40条全合法、同低思考配置/实际map/audit与cleanup匹配后才允许full一次；本探针本身不授权full。

完整消息、生成正文、裁判原响应仅在忽略的 `.cache/task10-low-probes`，公开文件仅安全元数据。两条once标记和出站计数保存，后续无需也不允许重复探针。当前Task10尚未完成，不宣称策略胜者。
