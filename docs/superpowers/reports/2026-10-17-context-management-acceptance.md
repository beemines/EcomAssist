# 第七章上下文管理验收：Stage A

状态：修后两页及最终full已通过；默认真实21批在第3轮理解器返回错误JSON契约后停止，仅2轮done、累计11/1/1；demo尚未运行。当前不能宣布本章真实验收完成。StageA产品HEAD `cdd141f630185bae33b625adfb3368b3b2418470`，基线 `e73eb57410aa417b56305ddd27d8331e635d7acf`，无合并或推送。

## 源码与边界

- 修正估算器 `absolute_error` 为绝对值，保留有符号 `relative_error` 与未知usage=null。
- live浏览器无论最终health或关闭浏览器是否失败，都先写已捕获轮次/pageErrors；优先报告原始轮次失败。未增加公开调试接口。
- 真实摘要三项被词法守卫拒绝后，仅规定改选、歧义、取消表单的表达短语，保持JSON协议及guard不变。
- 原物流完整问句定点复验捕获 `decision_reason` 被当作通用理由；仅补AGENT_SYSTEM售后字段含义，未修改schema/guard、模型、超时、自动重试或窗口参数。获批新增两轮已验证business/knowledge均使用null退款字段并done。
- 实际历史截图暴露原工具JSON正文被hydrateConversation直接渲染。按原设计修正为仅user与最终assistant气泡，工具状态沿用原轮metadata徽章；完整SQL/API工具记录不变，未增加调试折叠气泡。
- 本地3307/customer_service迁移前，在实际DDL连接内核对Docker映射、hostname/server_uuid、数据库、内部端口、CONNECTION_ID/CURRENT_USER/VERSION；迁移及verify通过。隐藏8004仅由现有创建身份/解释器/命令/祖先/监听守卫启动重启，8002/8003未操作。

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

## 校准与最终预算

前三付费页面轮得到11组实际非流式prompt_tokens，合计14351；平均绝对误差1217.09，带符号相对误差+81.83%至+114.35%，全部为保守高估。保持 `cjk-ascii-protocol-v1` 参数。流式最终回复usage未知，不计作0。样本很少，不证明供应商128000窗口或通用误差界。

真实小额运行的AGENT_SYSTEM SHA256为 `153d527bc471791ab82f174f4d238209a228bbcf9868a70267ef5b6c9ddd4b16`；新增售后字段提示后为 `dc05070ed551e1d37b7066fd1150ec0229666461dad30214a446388a8735d69b`，F2811→2890。校准样本保留原提示版本，不把最后新增79token开销伪称为同包实测。

| Profile | H | H1 | H2 | G | 派生单轮累计预算 |
|---|---:|---:|---:|---:|---:|
| default W128000 | 59880 | 41916 | 17964 | 2000 | 1135519 |
| demo W18000 | 2691 | 1883 | 808 | 563 | 174463 |

最终两profile离线固定21轮各通过，default105/demo110模型包；原SQL与checkpoint一致。demo触发降级/摘要并从实际注入summary恢复1001；200字摘要负例仍遗漏最早段并安全澄清，不隐藏负例、不固定保留首话题、不回炉旧摘要。

## 验证记录

- 两修复RED：低估absolute_error返回-984而非984；最终health失联覆盖原503。修后26项Python、2/2浏览器故障证据和cap/health参数守卫通过。
- 新摘要prompt标注/协议回归75 passed3.34s。
- 最后AGENT_SYSTEM修改后的prefix/budget/agent/cap/两profile及200字负例：123 passed20.72s。
- 3308本章指定三文件：41 passed14.89s；仅fixture拥有的随机schema，不操作3307。
- 受控上下文浏览器10/10；受控意图浏览器11/11。意图脚本首条命令漏必需--url，启动前用法拒绝；更正后通过。记录独立，不把子集累加成全量。
- 真实历史工具JSON缺陷新增浏览器RED桌面/窄屏2失败（8/10）；最小渲染修复后再次10/10和11/11，原API工具content、完成徽章、原引用、安全切换均保留。
- 修订前全量在69%时通过原exec Ctrl+C中断，因第6轮新增真实证据后获批变更prompt/F；第二次在64%因实际历史JSON缺陷中断。分别保留 `.cache/task11-final-full.txt`、`.cache/task11-final-source-full.txt`，均不计通过。随后冻结源码全量为2698 passed、184 skipped、1 failed（435.66s）；唯一长原话建单夹具旧预算8000小于新增提示后的8073（原7904）。单例RED复现后只将该例测试预算显式9000，原2104字符/手填描述/票据断言不变；动作模块40 passed10.90s。修后最终全量 **2699 passed、184 skipped，551.94s，exit0**（`.cache/task11-final-green-full.txt`）。

服务重启后页面选择旧会话65、点击原政策引用，与原SSE引用正文相同。修后390宽窄屏无横向溢出，pageErrors为空；桌面/窄屏截图已查看，另等待入场动画结束保存稳定图。原六页后的只读取证会话65/66/67各原文与最新checkpoint相等，S/L均null、段数0，不能称已经证明真实级联或真实跨摘要恢复。

## 已批准、待前置门槛执行

追加修订后两个页面复验已明确授权并执行成功。随后两组21轮也已明确批准，前置条件为这两个页面与最终full通过；最终full已通过；默认批第3轮失败已停止，demo尚未启动。small run剩余14GLM/10嵌入/4重排，没有授权继续增加小额页面。

按已批准条件，在最终离线全绿后，使用同一固定 `tests/fixtures/context/long_conversation.json` 原话先default21、再demo21。预计每组100–140GLM（含后台摘要），每组硬上限150GLM/50嵌入/25重排；到限或失败停止，保留原批次，不自动重跑或加额。原批准命令如下；默认已执行但第3轮失败，demo尚未执行：

```powershell
pwsh -NoProfile -File scripts/start-context-demo.ps1 -Profile default -RunId ch07-default-21-20261017 -MaxGlmCalls 150 -MaxEmbeddingCalls 50 -MaxRerankCalls 25
D:/vue/node.exe scripts/verify-context-browser.cjs --live --profile default --run-id ch07-default-21-20261017 --max-glm-calls 150 --max-embedding-calls 50 --max-rerank-calls 25 --output runtime/context-evidence/ch07-default-21-20261017
pwsh -NoProfile -File scripts/start-context-demo.ps1 -Profile demo -RunId ch07-demo-21-20261017 -MaxGlmCalls 150 -MaxEmbeddingCalls 50 -MaxRerankCalls 25
D:/vue/node.exe scripts/verify-context-browser.cjs --live --profile demo --run-id ch07-demo-21-20261017 --max-glm-calls 150 --max-embedding-calls 50 --max-rerank-calls 25 --output runtime/context-evidence/ch07-demo-21-20261017
```

每组须核对实际答案、done、调用账本、原文哈希、源范围/注入段、后台事件、SQL/checkpoint及本轮业务重新读取；重启owned8004后再回到两个旧会话继续聊并检查引用。预留的每组硬上限也涵盖这些同组后续调用，不能另开run逃逸计数。

开放限制：原1001物流提示仅一条修后真实复验通过，非普遍正确性证明；OTHER边界未充分验证；最终摘要版本只复验三题；默认仅2/21完成，demo未运行；原始订单跨摘要注入/真实后台不阻塞尚未验证；旧200字摘要遗漏风险仍存在；仓储全历史O(N)锁内读取为既有性能minor，未开展无关重构。

原始证据：`runtime/context-evidence/ch07-small-20261017/`、`task11-migration.json`、`task11-final-budget-*.json`、`task11-final-offline-*.json`、`.cache/task11-*`。真实内容/日志/截图/SQL证据均留忽略目录，不进Git。


取证形态与环境提示：故障harness的2/2 Green当时直接输出于exec stdout（`live failure evidence preservation 2/2 PASS`），没有单独日志文件，不补造路径或重复运行。真实摘要首轮与三项复验的日志首行有langchain-openai默认socket-options customtransport禁用系统proxy autodetection提示；实际响应及usage独立保留，未改transport。大批ignored wrapper首次因跨VM realm对象比较在health预检失败，计数仍0/0/0；改为同realm Node Module加载后原严格限额核验通过，产品源码/固定21句未变。Node v24.19.0当前运行时的_compile/_nodeModulePaths定义摘要保存于.cache/context-management/node-module-source.txt。


## 默认真实批：保留失败，未通过21轮验收

run `ch07-default-21-20261017` / 会话68，固定fixture原话未变；第1轮1001物流和第2轮政策done，第3轮“运费怎么算？”在understanding返回HTTP200/finish_reason=stop，但content为 `{"kind":"tool_call","name":"query_faq","arguments":{"keyword":"运费怎么算？"}}`。schema要求唯一query，实际缺query且三个额外字段被拒；这是新的理解输出契约失败，不是此前decision_reason问题。原request无tools，response_format=json_object，系统提示与当前源完全一致；历史合法native工具消息是否诱导模型只是未证假设。没有修改源码/栈/阈值、真实重试或整批重跑。

实际账本11GLM/1embedding/1rerank，剩余139/49/24；物理hook捕获11请求、9个非流usage（输入合计14151），流usage仍未知。两个done、第三个error均保存，逐轮所有原文哈希未变化，最终SQL/checkpoint相等，S/L为null、摘要0。尚未到21轮，不能据两轮推断默认全程锚点或跨摘要能力。原包/body/usage、SSE/health、每轮API原文、SQL/checkpoint和离线schema拒绝证据在run目录。demo尚未启动，不拿剩余额度视为自动重试授权。


实际默认调用入口为忽略脚本 `.cache/context-management/captured-live.cjs`，以同realm装载同一 `scripts/verify-context-browser.cjs` live函数，仅补每轮health/SSE、API原文和时间取证。完整参数与上述默认命令相同；未改fixture或任何生产协议。源/取证脚本SHA见该run的source-versions.json。父控已要求两批均暂停，等待最终整分支发现合并为一次修复/复验范围，不新增真实调用或修改产品源码；已用额度不重置。
