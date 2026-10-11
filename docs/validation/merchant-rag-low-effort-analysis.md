# 低思考单次真实pilot：实际指标与解释

运行 `201215b02b874feea7e866db10ee23db`，40尝试、39完整完成、1回答错误，清理成功；full未运行。以下是已保存实际报告的离线派生说明，不增加模型调用、不重判或修改原分母。完整未舍入数值与全部excluded见[派生JSON](merchant-rag-low-effort-analysis.json)；[原始服务JSON](merchant-rag-low-effort-pilot.json)/[原始Markdown](merchant-rag-low-effort-pilot.md)字节保持服务发布原样。

## 总体与各桶：所有40条保留

| 桶 / 策略 | Recall@5 / n | Recall@10 / n | MRR@10 / n | Prompt / n | 要点 / n | Faith / n | 库外拒答 / n | 可答误拒答 / n |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| overall / dense | 1.000000 / 8 | 1.000000 / 8 | 1.000000 / 8 | 1.000000 / 8 | 1.000000 / 7 | 0.906250 / 8 | 0.500000 / 2 | 0.000000 / 7 |
| overall / bm25 | 0.916667 / 8 | 0.958333 / 8 | 0.916667 / 8 | 0.958333 / 8 | 0.750000 / 8 | 0.876190 / 7 | 1.000000 / 2 | 0.250000 / 8 |
| overall / hybrid | 0.958333 / 8 | 1.000000 / 8 | 0.937500 / 8 | 1.000000 / 8 | 1.000000 / 8 | 1.000000 / 8 | 1.000000 / 2 | 0.000000 / 8 |
| overall / hybrid_rerank | 1.000000 / 8 | 1.000000 / 8 | 1.000000 / 8 | 1.000000 / 8 | 0.833333 / 8 | 0.952381 / 7 | 1.000000 / 2 | 0.125000 / 8 |
| A_policy / dense | 1.000000 / 2 | 1.000000 / 2 | 1.000000 / 2 | 1.000000 / 2 | 1.000000 / 2 | 1.000000 / 2 | N/A / 0 | 0.000000 / 2 |
| A_policy / bm25 | 1.000000 / 2 | 1.000000 / 2 | 1.000000 / 2 | 1.000000 / 2 | 0.500000 / 2 | 1.000000 / 1 | N/A / 0 | 0.500000 / 2 |
| A_policy / hybrid | 1.000000 / 2 | 1.000000 / 2 | 1.000000 / 2 | 1.000000 / 2 | 1.000000 / 2 | 1.000000 / 2 | N/A / 0 | 0.000000 / 2 |
| A_policy / hybrid_rerank | 1.000000 / 2 | 1.000000 / 2 | 1.000000 / 2 | 1.000000 / 2 | 0.500000 / 2 | 0.666667 / 1 | N/A / 0 | 0.500000 / 2 |
| B_model / dense | 1.000000 / 2 | 1.000000 / 2 | 1.000000 / 2 | 1.000000 / 2 | 1.000000 / 2 | 1.000000 / 2 | N/A / 0 | 0.000000 / 2 |
| B_model / bm25 | 1.000000 / 2 | 1.000000 / 2 | 1.000000 / 2 | 1.000000 / 2 | 1.000000 / 2 | 1.000000 / 2 | N/A / 0 | 0.000000 / 2 |
| B_model / hybrid | 1.000000 / 2 | 1.000000 / 2 | 1.000000 / 2 | 1.000000 / 2 | 1.000000 / 2 | 1.000000 / 2 | N/A / 0 | 0.000000 / 2 |
| B_model / hybrid_rerank | 1.000000 / 2 | 1.000000 / 2 | 1.000000 / 2 | 1.000000 / 2 | 1.000000 / 2 | 1.000000 / 2 | N/A / 0 | 0.000000 / 2 |
| C_colloquial / dense | 1.000000 / 2 | 1.000000 / 2 | 1.000000 / 2 | 1.000000 / 2 | 1.000000 / 1 | 1.000000 / 1 | N/A / 0 | 0.000000 / 1 |
| C_colloquial / bm25 | 1.000000 / 2 | 1.000000 / 2 | 0.666667 / 2 | 1.000000 / 2 | 1.000000 / 2 | 0.900000 / 2 | N/A / 0 | 0.000000 / 2 |
| C_colloquial / hybrid | 1.000000 / 2 | 1.000000 / 2 | 0.750000 / 2 | 1.000000 / 2 | 1.000000 / 2 | 1.000000 / 2 | N/A / 0 | 0.000000 / 2 |
| C_colloquial / hybrid_rerank | 1.000000 / 2 | 1.000000 / 2 | 1.000000 / 2 | 1.000000 / 2 | 1.000000 / 2 | 1.000000 / 2 | N/A / 0 | 0.000000 / 2 |
| D_unanswerable / dense | N/A / 0 | N/A / 0 | N/A / 0 | N/A / 0 | N/A / 0 | 0.250000 / 1 | 0.500000 / 2 | N/A / 0 |
| D_unanswerable / bm25 | N/A / 0 | N/A / 0 | N/A / 0 | N/A / 0 | N/A / 0 | 0.333333 / 1 | 1.000000 / 2 | N/A / 0 |
| D_unanswerable / hybrid | N/A / 0 | N/A / 0 | N/A / 0 | N/A / 0 | N/A / 0 | N/A / 0 | 1.000000 / 2 | N/A / 0 |
| D_unanswerable / hybrid_rerank | N/A / 0 | N/A / 0 | N/A / 0 | N/A / 0 | N/A / 0 | N/A / 0 | 1.000000 / 2 | N/A / 0 |
| E_multi / dense | 1.000000 / 2 | 1.000000 / 2 | 1.000000 / 2 | 1.000000 / 2 | 1.000000 / 2 | 1.000000 / 2 | N/A / 0 | 0.000000 / 2 |
| E_multi / bm25 | 0.666667 / 2 | 0.833333 / 2 | 1.000000 / 2 | 0.833333 / 2 | 0.500000 / 2 | 1.000000 / 1 | N/A / 0 | 0.500000 / 2 |
| E_multi / hybrid | 0.833333 / 2 | 1.000000 / 2 | 1.000000 / 2 | 1.000000 / 2 | 1.000000 / 2 | 1.000000 / 2 | N/A / 0 | 0.000000 / 2 |
| E_multi / hybrid_rerank | 1.000000 / 2 | 1.000000 / 2 | 1.000000 / 2 | 1.000000 / 2 | 0.833333 / 2 | 1.000000 / 2 | N/A / 0 | 0.000000 / 2 |

## 每行排除原因（未列指标表示无排除）

- overall/dense — recall_at_5: expected_refusal=2；recall_at_10: expected_refusal=2；mrr_at_10: expected_refusal=2；prompt_group_coverage: expected_refusal=2；answer_point_coverage: answer_error=1,expected_refusal=2；faithfulness: answer_error=1,zero_claims=1；absent_refusal_rate: answerable=8；answerable_false_refusal_rate: answer_error=1,expected_refusal=2
- overall/bm25 — recall_at_5: expected_refusal=2；recall_at_10: expected_refusal=2；mrr_at_10: expected_refusal=2；prompt_group_coverage: expected_refusal=2；answer_point_coverage: expected_refusal=2；faithfulness: zero_claims=3；absent_refusal_rate: answerable=8；answerable_false_refusal_rate: expected_refusal=2
- overall/hybrid — recall_at_5: expected_refusal=2；recall_at_10: expected_refusal=2；mrr_at_10: expected_refusal=2；prompt_group_coverage: expected_refusal=2；answer_point_coverage: expected_refusal=2；faithfulness: zero_claims=2；absent_refusal_rate: answerable=8；answerable_false_refusal_rate: expected_refusal=2
- overall/hybrid_rerank — recall_at_5: expected_refusal=2；recall_at_10: expected_refusal=2；mrr_at_10: expected_refusal=2；prompt_group_coverage: expected_refusal=2；answer_point_coverage: expected_refusal=2；faithfulness: zero_claims=3；absent_refusal_rate: answerable=8；answerable_false_refusal_rate: expected_refusal=2
- A_policy/dense — absent_refusal_rate: answerable=2
- A_policy/bm25 — faithfulness: zero_claims=1；absent_refusal_rate: answerable=2
- A_policy/hybrid — absent_refusal_rate: answerable=2
- A_policy/hybrid_rerank — faithfulness: zero_claims=1；absent_refusal_rate: answerable=2
- B_model/dense — absent_refusal_rate: answerable=2
- B_model/bm25 — absent_refusal_rate: answerable=2
- B_model/hybrid — absent_refusal_rate: answerable=2
- B_model/hybrid_rerank — absent_refusal_rate: answerable=2
- C_colloquial/dense — answer_point_coverage: answer_error=1；faithfulness: answer_error=1；absent_refusal_rate: answerable=2；answerable_false_refusal_rate: answer_error=1
- C_colloquial/bm25 — absent_refusal_rate: answerable=2
- C_colloquial/hybrid — absent_refusal_rate: answerable=2
- C_colloquial/hybrid_rerank — absent_refusal_rate: answerable=2
- D_unanswerable/dense — recall_at_5: expected_refusal=2；recall_at_10: expected_refusal=2；mrr_at_10: expected_refusal=2；prompt_group_coverage: expected_refusal=2；answer_point_coverage: expected_refusal=2；faithfulness: zero_claims=1；answerable_false_refusal_rate: expected_refusal=2
- D_unanswerable/bm25 — recall_at_5: expected_refusal=2；recall_at_10: expected_refusal=2；mrr_at_10: expected_refusal=2；prompt_group_coverage: expected_refusal=2；answer_point_coverage: expected_refusal=2；faithfulness: zero_claims=1；answerable_false_refusal_rate: expected_refusal=2
- D_unanswerable/hybrid — recall_at_5: expected_refusal=2；recall_at_10: expected_refusal=2；mrr_at_10: expected_refusal=2；prompt_group_coverage: expected_refusal=2；answer_point_coverage: expected_refusal=2；faithfulness: zero_claims=2；answerable_false_refusal_rate: expected_refusal=2
- D_unanswerable/hybrid_rerank — recall_at_5: expected_refusal=2；recall_at_10: expected_refusal=2；mrr_at_10: expected_refusal=2；prompt_group_coverage: expected_refusal=2；answer_point_coverage: expected_refusal=2；faithfulness: zero_claims=2；answerable_false_refusal_rate: expected_refusal=2
- E_multi/dense — absent_refusal_rate: answerable=2
- E_multi/bm25 — faithfulness: zero_claims=1；absent_refusal_rate: answerable=2
- E_multi/hybrid — absent_refusal_rate: answerable=2
- E_multi/hybrid_rerank — absent_refusal_rate: answerable=2

要点覆盖对可答题按全部标准要点计算；拒答仍覆盖0，不从分母删除。Faith是逐题断言支持比例宏平均，零断言为N/A并单独排除，不填满分。D桶在运行中名为D_unanswerable，页面为D_absent/库外问题。candidate50覆盖全部50块，各策略候选组覆盖都是1/n8，属于饱和的合成资料边界。

## 四路共同合法集合及其中可答题

四路共同完整完成9题：A21、A43、B3、B54、C35、D1、D3、E2、E19。唯一缺席C5/dense因回答错误，使整题不进入共同集合；原40条总体仍保留。

| 桶 / 策略 | Recall@5 / n | Recall@10 / n | MRR@10 / n | Prompt / n | 要点 / n | Faith / n | 库外拒答 / n | 可答误拒答 / n |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| dense | 1.000000 / 7 | 1.000000 / 7 | 1.000000 / 7 | 1.000000 / 7 | 1.000000 / 7 | 0.906250 / 8 | 0.500000 / 2 | 0.000000 / 7 |
| bm25 | 0.904762 / 7 | 0.952381 / 7 | 0.904762 / 7 | 0.952381 / 7 | 0.714286 / 7 | 0.855556 / 6 | 1.000000 / 2 | 0.285714 / 7 |
| hybrid | 0.952381 / 7 | 1.000000 / 7 | 0.928571 / 7 | 1.000000 / 7 | 1.000000 / 7 | 1.000000 / 7 | 1.000000 / 2 | 0.000000 / 7 |
| hybrid_rerank | 1.000000 / 7 | 1.000000 / 7 | 1.000000 / 7 | 1.000000 / 7 | 0.809524 / 7 | 0.944444 / 6 | 1.000000 / 2 | 0.142857 / 7 |

共同集合中预先由gold.should_refuse界定的可答7题为A21、A43、B3、B54、C35、E2、E19；下表仅是这一明确子集，包含可答误拒答，不替代上表与D1/D3风险。该子集由生产summarize_records离线聚合，无新裁判、无按高分筛选。

| 桶 / 策略 | Recall@5 / n | Recall@10 / n | MRR@10 / n | Prompt / n | 要点 / n | Faith / n | 库外拒答 / n | 可答误拒答 / n |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| dense | 1.000000 / 7 | 1.000000 / 7 | 1.000000 / 7 | 1.000000 / 7 | 1.000000 / 7 | 1.000000 / 7 | N/A / 0 | 0.000000 / 7 |
| bm25 | 0.904762 / 7 | 0.952381 / 7 | 0.904762 / 7 | 0.952381 / 7 | 0.714286 / 7 | 0.960000 / 5 | N/A / 0 | 0.285714 / 7 |
| hybrid | 0.952381 / 7 | 1.000000 / 7 | 0.928571 / 7 | 1.000000 / 7 | 1.000000 / 7 | 1.000000 / 7 | N/A / 0 | 0.000000 / 7 |
| hybrid_rerank | 1.000000 / 7 | 1.000000 / 7 | 1.000000 / 7 | 1.000000 / 7 | 0.809524 / 7 | 0.944444 / 6 | N/A / 0 | 0.142857 / 7 |

该7题Faith排除仅bm25零断言2、rerank零断言1；dense/hybrid无排除。库外拒答n0、answerable排除7不适用于此子集。共同9题Faith的不同分母则分别8/6/7/6，排除零断言1/3/2/3。hybrid在共同9题要点/Faith为1/n7、1/n7；rerank为0.8095238095/n7、0.9444444444/n6。不能把不同分母或单一检索领先称为总体冠军。

## 具体型号、口语与跨节证据

B3/bm25的MH-LP50 Lite金标块候选/最终均第1，B54/bm25的MH-W20/MH-W60两块第2/1，全部进入实际Prompt；两题四路均完整完成。C35故障自查的最终位次为BM25第3、hybrid第2、dense/重排第1（重排候选第2、最终第1）；BM25虽然覆盖要点，但新增“可创建人工工单”被裁判判为无证据。

E2/bm25的运费第1、退货范围第6（FAQ替代第11）、退款时效第17；时效未进最终前十或Prompt，三组Recall@5=1/3、@10和Prompt=2/3，实际自评后固定拒答。hybrid退款时效第8，@5=2/3、@10和Prompt完整；dense/重排检索完整，但重排本题要点只覆盖2/3。排序、Prompt、生成覆盖因此应分开解释；完整来源rank证据见派生JSON。

## 唯一错误与裁判语义边界

C5/dense在answer阶段为ServiceError，保存的安全code仅answer_error、固定消息“该阶段执行失败”，耗时5446.778299752623ms；answer/refused/verdicts/judge_snapshot均null。实际self-check为useful=true，10引用有运费金标且检索/Prompt指标均1；原流正文、finish_reason及底层ServiceError.code未捕获，不能归因为length、引用或网络子原因。没有追加收费诊断、提高预算或重复pilot。

D1/dense自评useful=true，但理由说没有活体宠物证据；正文表达不确定仍是模型生成，协议实际refused=false，不将它重标为固定拒答。裁判4断言中3不支持，Faith0.25/n1，导致dense库外拒答率0.5/n2；不能因答复语气谨慎删除此风险。

D3四路均使用逐字相同的固定拒答；bm25裁判提取3断言并判2条建议不支持，其他路claims=[]。这是证据相关的模型裁判噪声，需人工语义核查；仍保留原判定和实际0.3333333333/n1，不能称人工真值编造。新低思考轮实际39/40合法完成，旧轮9/40；这不是原失败因果证明，也不保证裁判语义准确。

四条实际不支持快照对应3308合法faith台账新增：A43/rerank1、C35/bm251、D1/dense3、D3/bm252；原4条外来台账逐hash保持。资源证明见[只读对比](merchant-rag-low-effort-resource-proof.json)，未由人工重标或删台账洗分。

这版材料参考同gold构造，八篇50块/candidate50、每桶仅2道pilot题；本轮可描述检索与回答行为，不能外推真实商店或300题策略优劣。39/40使服务matching_pilot=false，全量没有run/manifest/comparison文件，不造1200条not_attempted。
