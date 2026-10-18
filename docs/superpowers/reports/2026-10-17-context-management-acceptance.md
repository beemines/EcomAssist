# 第七章上下文管理实际验收记录（2026-10-18）

**最新交付状态：功能实现、历史回忆与本轮业务读取、重启续聊及两屏引用回载已验证；严格“不申请退款”明确复述项 NOT MET。** 所有真实测试已停止。最终产品源码 `9303848288d0dd0c1d785b23f9cd363f67830574`；保留原demo固定批20/21失败与后续各次定点结果，不宣称全绿或最终同版本重新跑完21轮。原失败没有被覆盖，分支/worktree/scratch保留，不merge/push。

基线 `e73eb57410aa417b56305ddd27d8331e635d7acf`；StageA产品 `cdd141f630185bae33b625adfb3368b3b2418470`；集中修复产品 `a82f27e84810247e70d2ee82186c266e51137038`，其验收文档HEAD `ba7db6906116e73feec9d0b649b92f05d4f0397b`；追加首候选仅摘要提示产品 `0a502c073027cbc78aa65ea61acb505b8f47337f`，真实对照HEAD `62868c23b6fdefadac118c487dda02da633a5da4`。最后提示产品 `0221b71c8fec3302a0eed0414776159c8d284471`，R1实测HEAD `1916cbb4775515162582a260115e9a9b3d8977c5`。本次收口只改文档，无merge/push。

## 最新分项验收（2026-10-18，R3实际收口）

| 项目 | 实际结果与范围 |
| --- | --- |
| 源码全量 | `55b28c1`：2725 passed / 184 skipped，417.96s，exit0，`.cache/ch07-final-full-20261018.txt`；不冒充后续Prompt源码全量 |
| 最终R3窄覆盖 | `9303848`：215 passed，14.49s，exit0，`.cache/final-understanding-recall-r3-focused.txt`，含既有两profile离线21覆盖 |
| 分类输入修复 | `55b28c1`真实生产packet六例6/6；原Prompt单例其他0.95失败保留 |
| R2两例 | 正例正确1001/两问但缺显式物流主题，strict FAIL；遗漏首段误选1002被生产实体guard拒绝，FAIL |
| R3缺首段单例 | 原问题原样返回、不选后段订单、两问保留，PASS；正例standalone gold未调用，不写2/2 |
| R3原会话独立正例 | conv70/user588：实际理解“订单1001的物流后来怎么说？我当时反映未收到包裹的诉求是什么？”，分类物流0.95；seq1实际进入wire、本轮query_logistics1001、回答未找到包裹/核实去向/尚未解决，HTTP200 done |
| 严格否定复述项 | 最终正文未明确复述“不申请退款”，**NOT MET / strict FAIL保持**。seq1原否定仍被注入，未反转为退款、控制字段null/无actions；原result.semantic_gate没有填成true |
| 有界例外后续聊 | 独立`continuation-adjudication.json`准入；exact-owned重启后user592唯一1002页实际query_logistics1002，HTTP200 done；旧SQL/摘要/checkpoint一致、桌面及390原引用正文逐字相等、窄屏无横溢，PASS |

最终同一demo账本149/16/16（硬150/50/25、余1/34/9）；small46/2/2、default126/18/18，合计**321/36/36**。从先前125起新增24GLM：首分类失败1、R1分类6、R1页失败4、R2两例2、R3缺首段1、原页5、重启续聊5。所有启动/后台与失败均计入原账本；最终这些重启增量0，没有新run、重置或自动SDK重试。

最终证据根：`runtime/context-evidence/ch07-demo-21-20261017/final-understanding-recall-r3/`，包含`understanding-omitted-case/result.json`、`original-final/targeted-inspection.json`、`continuation-adjudication.json`、`restart-continuation/manifest.json`、`continuation/result.json`及桌面/窄屏截图。旧584及全部旧原文/段落哈希不变。R1/R2失败、依赖恢复与版本细节见[最终修复报告](2026-10-18-final-intent-recall.md)。以下早期阶段记录保留历史语境，其“最终/未执行”仅指该阶段。

## 早期版本验证记录

| 版本/范围 | 已保存的实际结果 | 实际覆盖界限 |
| --- | --- | --- |
| a82最终全量 | 2720 passed / 184 skipped，427.06s，exit0；`.cache/final-fix-source-final-full.txt` | 该阶段全分支pytest；不含后续摘要/分类/理解修订 |
| a82集中修复定向 | 340项、history40；上下文浏览器13/13 | 原四项发现source-addressed，定向复审无新P1/P2 |
| 3308指定集成 | 41 passed，14.89s | 本章三个指定文件、fixture拥有的随机schema；后续纯prompt/UI未重复此未受影响集 |
| 两套受控浏览器 | 上下文最终13/13；意图11/11 | 最终历史工具徽章、未完成历史等覆盖；不是付费实测 |
| 0a502摘要提示 | 192 passed，31.61s，exit0；`.cache/summary-prompt-fix-focused.txt` | 摘要/前缀/预算/生命周期/manager/两profile离线21；未再跑full |
| 0a502人工标注 | 13原负例仍拒绝，13人工规范参考被守卫接受 | 人工参考不是新模型输出；不能推断真实质量 |
| 0a502真实对照 | 第一个来源504–523失败，后两项未调用 | 旧失败独立保留 |
| 0221 R1定向 | 192 passed，34.74s；原14负例拒绝/14人工参考接受 | `.cache/summary-prompt-fix-r1-focused.txt`；不是第二次full |
| 0221 R1真实限定复验 | 三来源3/3有效、正常startup seq3提交；原末句200done但分类其他 | 无1001当前读取，最终语义门槛失败，未执行条件续聊 |

整分支单次审查及集中修复定向复审已由父控完成；追加摘要提示只有一次独立范围审查，结论SOURCE APPROVED、无新增可行动问题。同一summary reviewer已evidence-only关闭：bounded actual SUMMARY gate PASS、startup PASS、E2E FAIL；未新扫源码或新增调用。测试日志只按各自源码和范围报告，不将子集相加冒充全量。

## 不可变真实调用账本

账本 `runtime/context-evidence/call-ledger.sqlite`。最后已结算：

| run | 固定硬上限 GLM/嵌入/重排 | 累计已用 | 物理余额 |
| --- | --- | --- | --- |
| ch07-small-20261017 | 60/12/6 | 46/2/2 | 14/10/4 |
| ch07-default-21-20261017 | 150/50/25 | 126/18/18 | 24/32/7 |
| ch07-demo-21-20261017 | 150/50/25 | 149/16/16 | 1/34/9 |
| 合计 | 三个独立既定run | **321/36/36** | 余额不构成新页面授权 |

包括所有失败、后台摘要和探针；未重置run、提升上限、另开run掩盖费用。SDK自动重试为0；生产的后续notify是不同后台job，确实可再次生成相同或扩展的来源，不能笼统称“没有任何重试”。没有工单/退款业务提交，旧8002/8003未操作。

## 默认实际21轮与重启续聊

同一default run分开保留四部分：

| 部分 | 会话 | 页面结果 | GLM/嵌入/重排增量 | 累计 |
| --- | --- | --- | --- | --- |
| 原失败批 | 68 | 2done/3attempted，第三句理解JSON契约失败 | 11/1/1 | 11/1/1 |
| a82原句定点 | 68 | “运费怎么算？”一次done | 5/1/1 | 16/2/2 |
| a82新固定批 corrected-attempt-1 | 69 | 固定21/21 done | 105/16/16 | 121/18/18 |
| 单独post-batch-continuation-1 | 69 | exact-owned重启后“订单1002现在是什么状态？”一次done | 5/0/0 | 126/18/18 |

原失败HTTP200/stop内容是 `{"kind":"tool_call","name":"query_faq","arguments":{"keyword":"运费怎么算？"}}`，缺少唯一query字段且含额外字段，strict schema正确拒绝；是否由native历史工具对诱导未被证明。a82只明确理解输出角色/协议，未放宽schema。原文件、403–411行含失败行、原native工具对均未改写。定点请求真实返回query契约，原失败仍保留。

会话69固定21每轮原文未变、SQL/checkpoint相等，S/L始终null、摘要0。末轮实际新调用 `query_logistics({"order_id":"1001"})`，恢复最早订单1001、未找到包裹、不申请退款；不能把实际物流工具名改写成夹具中预想的query_order。此前最新其他订单为1002。105个物理请求对应账本增量，84个非流usage的prompt_tokens合计1071282；流usage未知。

固定21结果先封存，随后重启同run再单独续聊1002，实际新query_order；原固定批文件哈希不变。桌面/390窄屏旧会话、原政策引用正文相同，pageErrors空，无横向溢出，截图已查看。证据在default run的 `corrected-attempt-1/semantic-inspection.json` 和 `post-batch-continuation-1/result.json`，第22页不计入固定21。

语义观察仍保留：会话68修后运费回答额外提及“订单1001金额199元，已满99元包邮门槛”，来自历史成功tool405，并未在该政策轮重新读取订单。协议通过不代表所有答复事实都来自当前读取，不能补造一次新业务工具成功。

## demo实际20/21与后台摘要失败

a82、会话70，同一demo150/50/25：原 `original-attempt-1/results.json` 保存前6轮done与helper暂停；获父控纠正后，`resumed-turns-7-21/results.json` 只续7–21，14done加末轮HTTP422。没有重播1–6、重启或新会话。原六轮文件哈希全部保持，不能将原暂停文件覆盖成clean21。

第6轮以前的首次摘要将59900分表达为599元，保守词法守卫因新token599拒绝；随后同轮正常完成通知启动另一job，157字合法seq1提交。页面6一直done，前台classification发生于首个后台job期间。最初ignored helper“任意summary_failed即整批停止”比spec更严格；父控查明后撤销该额外条件，允许原会话继续，原暂停证据仍在。

截至第20轮：seq1覆盖504–523，含1001、MH-LP200、未找到包裹、不申请退款；seq2覆盖524–547。后续实际冻结snapshot和understanding包注入过seq1/2，未省略最早段。共有18个独立生产摘要job，**2 committed、16 rejected**：seq1一次失败后成功；seq2四次失败后成功；seq3十一项均失败。每个body、task ID、时间与来源区间均保留。失败原因包括FAQ工具事实缺“当时/曾/历史”、59900分转599元，以及原“9:00 至 22:00”变为“9:00-22:00”产生不在原文中的词法token00-22；不是只有金额一种原因。

**第21轮实际失败**：原句“最开始那个订单后来怎么说？我当时的诉求是什么？”返回HTTP422，body为 `{"code":"context_capacity","message":"当前上下文无法放入部署窗口，请检查上下文预算配置。"}`。S547/L579，H2691/H1=1883/H2=808；将548–583全部合法压为Layer2仍2744>2691。离线对原保存行调用未改plan_layers得到同一ContextCapacityError。user584没有任何前台model_ctx，原始用户行保存在SQL；最新完成checkpoint仍user580/第20轮，故该失败状态SQL/checkpoint不相等。wrapper随后SQL相等断言覆盖了错误摘要，但实际422 body早已单独保存；二者不可混为一项生产数据丢失。

此时demo账本118/16/16：100个前台物理GLM（20done），18个后台摘要。第21轮容量拒绝还触发最后一个正常notify，已计入18且失败结束；无后台未结算尾巴。最早段在第20轮被注入，不等于末轮已恢复1001；末轮未进入模型、没有本轮1001工具调用。demo批后重启/续聊未进行。

主要证据：`original-attempt-1/summary-failure-analysis.json`、`resumed-turns-7-21/final-failure-analysis.json`、每轮raw/history/storage/context、全部summary-request/response-*。最终原批20done/21attempted及容量负例保留。

## 追加最小摘要提示及真实定点失败

人类明确批准在原demo余32GLM内仅修改SUMMARY_SYSTEM并定点复验，不再跑21、不改guard/schema/模型/容量/SDKretry。产品0a502只补工具含FAQ的历史标记、原金额单位与时间分隔表达；prompt SHA `5d826ba18a7a3c43de1214dc7131081a9bd0b8ac458a2a447202909f0dae5d27`。保存的[修订来源与离线报告](2026-10-18-summary-prompt-fix.md)记录192项及人工标注。

计划只取三个实际失败来源：request27[504–523]、request61[524–539]、request118[548–579]，各一次、不得append旧段。控制器最初将第二范围误称524–547，核对后纠正为真实失败61，未拿已成功源替代负例，也未增加第四例。

实际只执行第一个对照，HTTP200/stop；prompt_tokens4320、completion_tokens91。内容为：

> 用户称订单1001未找到包裹、明确不申请退款，当时查得模拟数据已签收（签收2026-10-13，运单MOCK1001）。另查订单1002明辉饮水机MH-WD100模拟已签收（2026-09-15，59900分）。当时咨询退换货政策、运费及电子商品保修12个月。

它保留了当时、模拟及59900分，但**遗漏必需型号MH-LP200**，未改guard报 `Summary omitted a source entity; use smaller complete batches.`。首失败即停，后两源未调用；未重启、未触发启动恢复、未重发原末句、未做条件1002续聊。没有DBappend或旧段重压。此次+1/0/0，demo最终119/16/16，总291/36/36。此候选的真实有效性门槛未通过；当时严格停止，后续R1为同一人类授权下控制器明确放行的最后候选，见下。

证据 `runtime/context-evidence/ch07-demo-21-20261017/extra-minimum-validation/source-contrasts/result.json`，含版本、原源文件SHA、完整wire/usage、前后计数和旧文件哈希不变。三个固定源中仅1 attempted/0 valid；不能写成3项已复验。

## R1最后候选：摘要恢复通过，末句分类门槛未通过

R1产品0221，仅在SUMMARY_SYSTEM补已有required_entities的逐项完整性检查；schema/guard/模型/窗口/阈值不改。prompt SHA `58dd217fec066d1328851591690354425c66dcdf9461bbf2543de695e782ca64`，独立范围复审SOURCE APPROVED。真实运行绑定clean HEAD1916cbb，与旧v3输出目录分开；没有第三候选或新完整21批。

| 明确授权步骤 | 实际结果 | GLM增量 | demo累计 |
| --- | --- | ---: | --- |
| 来源27[504–523]一次 | VALID，含1001/1002/MH-LP200/MH-WD100及原否定 | 1 | 120/16/16 |
| 来源61[524–539]一次 | VALID，FAQ保留当时及MH-LP200 | 1 | 121/16/16 |
| 来源118[548–579]一次 | VALID，原单位59900分/时间9:00 至 22:00/型号/模拟保留 | 1 | 122/16/16 |
| exact-owned重启的正常startup扫描 | 新seq3覆盖548–579 committed；未直接notify或更改锚点 | 1 | 123/16/16 |
| 同会话70原末句一次 | HTTP200 done，理解恢复1001，分类其他，无本轮业务工具 | 2 | 125/16/16 |
| 条件重启/1002续聊/桌面窄屏原引用 | 语义前置失败，全部未执行 | 0 | 125/16/16 |

R1三对照只调用SummaryGenerator，没有DBappend或回炉旧段；旧v3失败、原六轮暂停与7–21文件哈希均不变。正常startup从SQL待摘要范围自然恢复，新seq3正文，旧seq1/2逐字不变，旧原文包括失败user584不变。所有调用在原150/50/25内；R1共6GLM，连同v3失败1次，该追加范围实际消耗7GLM，非32全部花完。

原末句的新user585为“最开始那个订单后来怎么说？我当时的诉求是什么？”。实际understanding HTTP200/stop JSON：`{"query":"最开始那个订单1001（智能猫砂盆Max，MH-LP200）后来物流怎么说？我当时的诉求是什么？"}`。随后实际classification为 `{"intent":"其他","confidence":0.6}`，页面最终固定澄清“抱歉，我不太确定您的意思。请说明您想咨询的具体问题或办理的事项，例如查询订单、物流、商品或售后问题。”，没有query_order/query_logistics。

实际history_ctx及wire均证明seq1被消费，snapshot选择seq1/2/3、omitted为空；原订单指代已经恢复。最终S=L579，SQL/checkpoint再次相等，旧失败user584原样保留。**该事实不能替代要求的本轮1001重新读取及诉求回答**；语义门槛false，立即停止，没有扩展classifier修复、继续问句或条件续聊。原固定批仍20/21失败，这次单页200done也不是新source完整21通过。

证据：demo run的 `extra-minimum-validation-v4/source-contrasts/result.json`、`startup-recovery/manifest.json`、`original-final/result.json` 与 `original-final/targeted-inspection.json`，分别保留请求/响应/usage、物理capture offset/session、源码/提示SHA、旧文件哈希和最终只读账本。当前demo生产后台累计19个独立job（旧18+恢复1）：16拒绝、3提交；另4个隔离来源对照（v3失败1+R1有效3）从未append。SDK自动重试0，正常后台通知与人类明确批准的新候选对照分开计数。

## 真实小额账本

不可变run `ch07-small-20261017`，数据库 `runtime/context-evidence/call-ledger.sqlite`。限额60GLM/12嵌入/6重排，原六页用36/1/1后，人类明确批准两页追加；最终已用 **46GLM/2嵌入/2重排**，物理余额14/10/4。已完成 **8个付费页面轮次**，未继续用余额发新页面。包括失败、15次摘要和1次理解探针；没有重置run、业务工单或退款提交。

| 项目 | 结果 | GLM |
|---|---|---:|
| 页面1：一般商品七天无理由政策 | done，真实BGE嵌入1/重排1，原引用可回载 | 5 |
| 页面2：1001没找到/没收到/没申请退款，请查物流 | control_schema失败，原控制正文未捕获 | 3 |
| 页面3：1002物流现在到哪里 | done，本轮query_logistics；控制两退款字段均null | 5 |
| 页面4：退货退款请选择订单 | paused，刷新后恢复选择卡 | 2 |
| 免费“你好” | done，取消旧选择，物理计数不增 | 0 |
| 页面5：阿巴阿巴，月亮会不会打喷嚏 | done，但实际意图闲聊，OTHER目标未通过 | 2 |
| 页面6：原页面2完整问句，恢复相同会话65 | 再次control_schema，捕获非空decision_reason | 3 |
| 获批页面7：修订提示后的同一完整1001句 | done，本轮query_logistics，退款字段均null | 5 |
| 获批页面8：原成功七天退货政策对照 | done，knowledge控制退款字段均null，嵌入/重排各1 | 5 |
| 12个标注摘要各一次 | 9/12被validator接受 | 12 |
| 新摘要提示下三负例各一次 | 3/3被validator接受；不是全12同版本复测 | 3 |
| 真实O-101摘要指代理解 | 实际provenance及QueryUnderstanding恢复O-101 | 1 |
| 合计 | 无后台摘要额外调用 | 46 |

原失败完整输入为“订单1001的包裹没找到，我没有收到，也没有申请退款，请查物流。”。页面6实际模型控制为：

```json
{"decision_reason":"已提供订单号，需查询实际物流轨迹核实包裹状态。","refund_decision":null,"reply_mode":"answer","suggested_actions":[]}
```

业务route要求reason和refund_decision都为null，因此拒绝正确。页面2未捕获正文，不能以页面6回填其根因。页面3的成功不证明页面2修复；修订提示后的页面7才是原句定点复验。页面5理解复述了此前退款请求，实际分类为闲聊；原离题幻想问句也可归闲聊，记录为有限理解/分类边界、OTHER未充分证明，未顺手修改意图提示。

## 摘要样例与版本

首版prompt SHA256 `a86153da21bcac9f9a3bd456c06376874dd6b43bafbfdc030928299a2a7cb189`；修订版 `e0f3c9a0452c9005c49a8455d2720f9f11808b79a497e9a294bd026065fcf91b`。

| 标注 | 首次实际结果 | 新提示定点结果 |
|---|---|---|
| single_order | 通过，typed订单O-101可被真实理解消费 | 未重跑 |
| switch_order | “明确否定…指定查询”不匹配改选守卫 | “不是订单O-101，改查订单O-202”通过 |
| ambiguous_orders | “未指明是哪单”不匹配歧义守卫 | “待确认查哪一单”通过 |
| model | 通过，保留KX-700/断电 | 未重跑 |
| phone | 通过，保留13800138000/联系售后诉求 | 未重跑 |
| negation | 通过，保留不想退款 | 未重跑 |
| missing_package | 通过，保留未找到/未收到 | 未重跑 |
| mock_history | 通过，保留模拟/当时/运输中 | 未重跑 |
| unresolved_fault | 通过，保留无法开机/未解决 | 未重跑 |
| form_cancelled | “表单已打开但随后取消”不匹配短距离取消词法 | “打开退款表单，取消表单，没有提交”通过 |
| requested_not_paid | 通过，区分已申请与尚未退款 | 未重跑 |
| social | 通过，content为空 | 未重跑 |

“通过”是实际SummaryGenerator及其validator接受，不代表任意语言忠实度已证明。原生成内容、字面must_keep缺项、拒绝理由和每次wire/usage均保留。O-101单例真实理解恢复的是实际生成摘要，未伪造摘要、未放宽类型来源守卫；它不等同于真实21轮1001保留证明。

## 校准、预算与保留限制

首最多三付费页面内取得11组真实非流prompt_tokens配对，合计14351；平均绝对误差1217.09、相对误差+81.83%至+114.35%，估计约实际1.82–2.14倍。保持cjk-ascii-protocol-v1参数。流式usage未知，不填0；有限样本不是供应商128000窗口或通用tokenizer精度证明。

决策提示早期F2811，补售后字段语义后F2890；该阶段prompt SHA从153d527bc471791ab82f174f4d238209a228bbcf9868a70267ef5b6c9ddd4b16变为dc05070ed551e1d37b7066fd1150ec0229666461dad30214a446388a8735d69b。a82理解提示SHA ebe42f1b40f1e0b49ab1968479b821ae252c9b550c13e94367b4b1d681a4c5bb。原校准保留其旧source版本，不假称新增开销已同包校准。

| Profile | H | H1 | H2 | G | 最新派生每轮累计额度 |
| --- | ---: | ---: | ---: | ---: | ---: |
| default W128000 | 59880 | 41916 | 17964 | 2000 | 1136727 |
| demo W18000 | 2691 | 1883 | 808 | 563 | 175671 |

早期1135519/174463是旧理解提示下历史数值。v3摘要prefix830→1024（+194）；R1再到1163（+139、累计+333），三个来源估算输入7052/7193/12236，最大12236+输出512+安全540=13288<18000。该摘要阶段主工作流H和费用未变；后续分类F1305、R3理解F3005使最终派生费用更新为1136727/175671，H不变，不改变阈值补偿质量问题。累计额度是应用容量，不是实际token费用或请求次数。

已完成边界：3307/customer_service迁移前在同一DDL连接核对容器、hostname/server_uuid、数据库、端口、连接与身份，migrate/verify通过；8004重启使用exact-owned创建时间/解释器/完整命令/祖先/监听守卫和Hidden窗口；未触碰8002/8003。历史API/SQL原始工具流水保留，UI仅user/最终assistant气泡，工具徽章沿用原完成根元数据。原始JSON气泡缺陷的桌面/窄屏RED8/10、修后10/10及最终集中修复13/13均有独立版本证据。

历史返工不隐藏：两次旧full因后续确认的prompt/UI修订而Ctrl+C中断于69%/64%，不是pass。随后2698 passed/184 skipped/1 failed，唯一长原话夹具8000<新增系统开销后8073（原7904）；单例RED后仅该例显式9000，保留2104字符/手填description/票据断言，Actions40通过。StageA修后full2699/184，551.94s；其后a82最终full2720/184，427.06s。两定向修复absolute_error与live-finally先RED，再26项Python和2/2故障harness通过；2/2 Green仅原exec stdout“live failure evidence preservation 2/2 PASS”，没有独立原始日志，不为补路径重跑。

原真实摘要日志出现langchain-openai customtransport禁用proxy autodetection警告，追加对照同样出现；实际响应/usage独立保存，不作为新的服务失败、不改变transport。最早ignored wrapper跨VM realm导致health对象比较失败时计数0/0/0；改为同realm模块加载后保留严格cap核验，无产品代码绕过。

剩余限制：真实demo原21轮容量失败；后续R3定点已通过历史物流回忆/当前读取与重启续聊，但明确“不申请退款”复述仍NOT MET；v3漏型号负例保留，R1三对照不证明任意摘要的语义忠实；首12摘要只9/12、旧提示三负例定点3/3不等于最终全12重测；早期幻想问句归social的边界保留，后续六分类对照中的不可理解输入OTHER通过，但不证明任意输入。200字离线摘要遗漏最早段时安全澄清的负例保留，无最早主题固定保留、无旧段回炉。历史O(N)锁内读取性能minor未改。两项停放P3为回载等待选单旧提示可能保留至刷新，以及启动minimum_reservation漏一个理解输出预留；保守上界及runtime guard仍有效，未放宽费用限制。

所有运行内容、SQL、日志、截图和捕获helper留忽略目录，不进Git。真实调用当前已停止，物理余额不构成继续授权。同一评审只做实际证据关闭；功能交付与strict qualified结论分开，本报告不宣称Task11严格验收全通过。
