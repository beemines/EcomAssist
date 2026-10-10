# 单次真实pilot页面证据

2026-10-10，已复核生产源码42bd812；自有真实单worker服务 http://127.0.0.1:8002/rag-eval，启动PID95580，原8000/8001未操作。Chrome实际页面启动固定pilot按钮一次，run `52678f9492114f1789466442e575c168`；无控制夹具、无模型替身、无重跑/full/额外聊天调用。实际结果与限制见[交付状态](rag-evaluation-delivery.md)。

![原pilot进行中2/40](images/rag-evaluation-actual/pilot-running.jpg)

![原pilot终态40尝试、9完成、31错误、清理成功、full锁定](images/rag-evaluation-actual/pilot-final-gate.jpg)

真实DOM与API都显示completed_with_errors、40/40 attempted、9 completed、31 errors、not_attempted0、cleanup成功；只读GET datasets返回matching_pilot=false/available_scopes=[pilot]。重跑按钮终态可用但没有点击；取消按钮终态disabled，原运行/清理期间启动与重跑锁定。取消/新ID组合边界沿用Task9已保存受控证据，本次没有用重复收费任务补测。

指标选择“答案要点覆盖”实际显示bm25 1.000/n=1，其他n=0及全部排除原因；共同子集D1/D3，不适用/zero_claims保持N/A。真实分页从第1/2至第2/2，E2搜索匹配4条且第1/1；历史切换显示原v1 120记录/101完成/19错误、旧口径提示及重跑disabled。导航至聊天页显示“服务已就绪”和空输入，不发送消息；返回工作台重新加载同一原pilot终态。

详情加载读取实际audit-v1/source-map，清理后仍可查看完整来源、稳定组、标准要点条件/同义、实际score/kind、Prompt引用、生成及判定。B54/bm25合法判定2points/7claims；E2/bm25保留三组标准、退款时效缺Prompt、refused=true及judge_error，不填生成分数。

![B54真实BM25分数与类型](images/rag-evaluation-actual/b54-rubric-view.jpg)

![E2真实标准要点条件与BM25分数](images/rag-evaluation-actual/e2-stable-gold-rubric.jpg)

JSON和Markdown导出按钮各点击一次，实际服务日志两个GET均200；自动化download事件等待JSON超时，未声称读取浏览器下载路径。公共交付文件用同一实际服务GET200下载，字节与runtime已提交public报告一致，不复制私有records原文。一个body Control+Home定位超时保留观察，改用已记录原生快捷键取得终态截图，没有模型重试。

用户确认该run期间曾休眠/合盖，原长时钟/超时记录未删除。截图可核对状态，不证明模型质量；后续配置与真实验证尚未执行。本页面保持为可查看交付，当前服务由本代理拥有，后续控制端须在配置更新后管理这一个自有进程，不操作原8000/8001。
