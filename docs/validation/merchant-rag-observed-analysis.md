# 透明观测试跑的实际指标与分母

Run `7d421bf017ff4c02afec385178848fde`；40attempted/32completed/8rewrite_error，原服务器质量pair逐字节保留。B3/B54各一次共享结构失败影响四路；具体新边界见[安全观测](merchant-rag-observed-rewrite-evidence.md)，不反推旧失败。full未运行，没有1200条虚构分母。

共同四路合法8题：A21, A43, C35, C5, D1, D3, E19, E2；共同可答6题：A21, A43, C35, C5, E19, E2。错误保留在40总体，各指标使用自己的valid_n/excluded。

| 策略 | completed/errors | Recall5 | Recall10 | MRR10 | Prompt | 要点 | Faith | 库外拒答 | 可答误拒答 |
|---|---|---|---|---|---|---|---|---|
| dense | 8/2 | 1.0 / n=6 | 1.0 / n=6 | 1.0 / n=6 | 1.0 / n=6 | 1.0 / n=6 | 1.0 / n=7 | 1.0 / n=2 | 0.0 / n=6 |
| bm25 | 8/2 | 0.8888888888888888 / n=6 | 0.9444444444444445 / n=6 | 0.8888888888888888 / n=6 | 0.9444444444444445 / n=6 | 0.9444444444444445 / n=6 | 1.0 / n=6 | 1.0 / n=2 | 0.0 / n=6 |
| hybrid | 8/2 | 0.9444444444444445 / n=6 | 1.0 / n=6 | 0.9166666666666666 / n=6 | 1.0 / n=6 | 1.0 / n=6 | 0.9523809523809524 / n=7 | 1.0 / n=2 | 0.0 / n=6 |
| hybrid_rerank | 8/2 | 1.0 / n=6 | 1.0 / n=6 | 1.0 / n=6 | 1.0 / n=6 | 0.75 / n=6 | 0.9642857142857143 / n=7 | 1.0 / n=2 | 0.16666666666666666 / n=6 |

候选Top50/语料50有饱和局限；检索与要点的领先只限本轮、相应合法分母，不设总体赢家或外推300题。忠实度仅有断言时适用，误拒答和zero_claims仍按生产定义分别计入/排除，不按分数挑样本。

| 共同可答策略 | 要点 | Faith | 误拒答 |
|---|---|---|---|
| dense | 1.0 / n=6 | 1.0 / n=6 | 0.0 / n=6 |
| bm25 | 0.9444444444444445 / n=6 | 1.0 / n=6 | 0.0 / n=6 |
| hybrid | 1.0 / n=6 | 0.9444444444444445 / n=6 | 0.0 / n=6 |
| hybrid_rerank | 0.75 / n=6 | 0.95 / n=5 | 0.16666666666666666 / n=6 |

## 原裁判语义噪声（不重标人工真值）

| 题号 | 四路实际回答相同 | 策略 | refused | claims / unsupported |
|---|---|---|---|---|
| D1 | True | dense | True | 0/0 |
| D1 | True | bm25 | True | 0/0 |
| D1 | True | hybrid | True | 0/0 |
| D1 | True | hybrid_rerank | True | 1/0 |
| D3 | True | dense | True | 2/0 |
| D3 | True | bm25 | True | 0/0 |
| D3 | True | hybrid | True | 2/0 |
| D3 | True | hybrid_rerank | True | 2/0 |

## 每桶、策略、指标的精确分母与排除

| 桶 | 策略 | 指标 | value / valid_n | excluded |
|---|---|---|---|---|
| overall | dense | recall_at_5 | 1.0 / n=6 | {"expected_refusal": 2, "rewrite_error": 2} |
| overall | dense | recall_at_10 | 1.0 / n=6 | {"expected_refusal": 2, "rewrite_error": 2} |
| overall | dense | mrr_at_10 | 1.0 / n=6 | {"expected_refusal": 2, "rewrite_error": 2} |
| overall | dense | all_groups_hit_at_5 | 1.0 / n=6 | {"expected_refusal": 2, "rewrite_error": 2} |
| overall | dense | all_groups_hit_at_10 | 1.0 / n=6 | {"expected_refusal": 2, "rewrite_error": 2} |
| overall | dense | candidate_group_coverage | 1.0 / n=6 | {"expected_refusal": 2, "rewrite_error": 2} |
| overall | dense | prompt_group_coverage | 1.0 / n=6 | {"expected_refusal": 2, "rewrite_error": 2} |
| overall | dense | answer_point_coverage | 1.0 / n=6 | {"expected_refusal": 2, "rewrite_error": 2} |
| overall | dense | faithfulness | 1.0 / n=7 | {"rewrite_error": 2, "zero_claims": 1} |
| overall | dense | absent_refusal_rate | 1.0 / n=2 | {"answerable": 8} |
| overall | dense | answerable_false_refusal_rate | 0.0 / n=6 | {"expected_refusal": 2, "rewrite_error": 2} |
| overall | bm25 | recall_at_5 | 0.8888888888888888 / n=6 | {"expected_refusal": 2, "rewrite_error": 2} |
| overall | bm25 | recall_at_10 | 0.9444444444444445 / n=6 | {"expected_refusal": 2, "rewrite_error": 2} |
| overall | bm25 | mrr_at_10 | 0.8888888888888888 / n=6 | {"expected_refusal": 2, "rewrite_error": 2} |
| overall | bm25 | all_groups_hit_at_5 | 0.8333333333333334 / n=6 | {"expected_refusal": 2, "rewrite_error": 2} |
| overall | bm25 | all_groups_hit_at_10 | 0.8333333333333334 / n=6 | {"expected_refusal": 2, "rewrite_error": 2} |
| overall | bm25 | candidate_group_coverage | 1.0 / n=6 | {"expected_refusal": 2, "rewrite_error": 2} |
| overall | bm25 | prompt_group_coverage | 0.9444444444444445 / n=6 | {"expected_refusal": 2, "rewrite_error": 2} |
| overall | bm25 | answer_point_coverage | 0.9444444444444445 / n=6 | {"expected_refusal": 2, "rewrite_error": 2} |
| overall | bm25 | faithfulness | 1.0 / n=6 | {"rewrite_error": 2, "zero_claims": 2} |
| overall | bm25 | absent_refusal_rate | 1.0 / n=2 | {"answerable": 8} |
| overall | bm25 | answerable_false_refusal_rate | 0.0 / n=6 | {"expected_refusal": 2, "rewrite_error": 2} |
| overall | hybrid | recall_at_5 | 0.9444444444444445 / n=6 | {"expected_refusal": 2, "rewrite_error": 2} |
| overall | hybrid | recall_at_10 | 1.0 / n=6 | {"expected_refusal": 2, "rewrite_error": 2} |
| overall | hybrid | mrr_at_10 | 0.9166666666666666 / n=6 | {"expected_refusal": 2, "rewrite_error": 2} |
| overall | hybrid | all_groups_hit_at_5 | 0.8333333333333334 / n=6 | {"expected_refusal": 2, "rewrite_error": 2} |
| overall | hybrid | all_groups_hit_at_10 | 1.0 / n=6 | {"expected_refusal": 2, "rewrite_error": 2} |
| overall | hybrid | candidate_group_coverage | 1.0 / n=6 | {"expected_refusal": 2, "rewrite_error": 2} |
| overall | hybrid | prompt_group_coverage | 1.0 / n=6 | {"expected_refusal": 2, "rewrite_error": 2} |
| overall | hybrid | answer_point_coverage | 1.0 / n=6 | {"expected_refusal": 2, "rewrite_error": 2} |
| overall | hybrid | faithfulness | 0.9523809523809524 / n=7 | {"rewrite_error": 2, "zero_claims": 1} |
| overall | hybrid | absent_refusal_rate | 1.0 / n=2 | {"answerable": 8} |
| overall | hybrid | answerable_false_refusal_rate | 0.0 / n=6 | {"expected_refusal": 2, "rewrite_error": 2} |
| overall | hybrid_rerank | recall_at_5 | 1.0 / n=6 | {"expected_refusal": 2, "rewrite_error": 2} |
| overall | hybrid_rerank | recall_at_10 | 1.0 / n=6 | {"expected_refusal": 2, "rewrite_error": 2} |
| overall | hybrid_rerank | mrr_at_10 | 1.0 / n=6 | {"expected_refusal": 2, "rewrite_error": 2} |
| overall | hybrid_rerank | all_groups_hit_at_5 | 1.0 / n=6 | {"expected_refusal": 2, "rewrite_error": 2} |
| overall | hybrid_rerank | all_groups_hit_at_10 | 1.0 / n=6 | {"expected_refusal": 2, "rewrite_error": 2} |
| overall | hybrid_rerank | candidate_group_coverage | 1.0 / n=6 | {"expected_refusal": 2, "rewrite_error": 2} |
| overall | hybrid_rerank | prompt_group_coverage | 1.0 / n=6 | {"expected_refusal": 2, "rewrite_error": 2} |
| overall | hybrid_rerank | answer_point_coverage | 0.75 / n=6 | {"expected_refusal": 2, "rewrite_error": 2} |
| overall | hybrid_rerank | faithfulness | 0.9642857142857143 / n=7 | {"rewrite_error": 2, "zero_claims": 1} |
| overall | hybrid_rerank | absent_refusal_rate | 1.0 / n=2 | {"answerable": 8} |
| overall | hybrid_rerank | answerable_false_refusal_rate | 0.16666666666666666 / n=6 | {"expected_refusal": 2, "rewrite_error": 2} |
| A_policy | dense | recall_at_5 | 1.0 / n=2 | {} |
| A_policy | dense | recall_at_10 | 1.0 / n=2 | {} |
| A_policy | dense | mrr_at_10 | 1.0 / n=2 | {} |
| A_policy | dense | all_groups_hit_at_5 | 1.0 / n=2 | {} |
| A_policy | dense | all_groups_hit_at_10 | 1.0 / n=2 | {} |
| A_policy | dense | candidate_group_coverage | 1.0 / n=2 | {} |
| A_policy | dense | prompt_group_coverage | 1.0 / n=2 | {} |
| A_policy | dense | answer_point_coverage | 1.0 / n=2 | {} |
| A_policy | dense | faithfulness | 1.0 / n=2 | {} |
| A_policy | dense | absent_refusal_rate | N/A / n=0 | {"answerable": 2} |
| A_policy | dense | answerable_false_refusal_rate | 0.0 / n=2 | {} |
| A_policy | bm25 | recall_at_5 | 1.0 / n=2 | {} |
| A_policy | bm25 | recall_at_10 | 1.0 / n=2 | {} |
| A_policy | bm25 | mrr_at_10 | 1.0 / n=2 | {} |
| A_policy | bm25 | all_groups_hit_at_5 | 1.0 / n=2 | {} |
| A_policy | bm25 | all_groups_hit_at_10 | 1.0 / n=2 | {} |
| A_policy | bm25 | candidate_group_coverage | 1.0 / n=2 | {} |
| A_policy | bm25 | prompt_group_coverage | 1.0 / n=2 | {} |
| A_policy | bm25 | answer_point_coverage | 1.0 / n=2 | {} |
| A_policy | bm25 | faithfulness | 1.0 / n=2 | {} |
| A_policy | bm25 | absent_refusal_rate | N/A / n=0 | {"answerable": 2} |
| A_policy | bm25 | answerable_false_refusal_rate | 0.0 / n=2 | {} |
| A_policy | hybrid | recall_at_5 | 1.0 / n=2 | {} |
| A_policy | hybrid | recall_at_10 | 1.0 / n=2 | {} |
| A_policy | hybrid | mrr_at_10 | 1.0 / n=2 | {} |
| A_policy | hybrid | all_groups_hit_at_5 | 1.0 / n=2 | {} |
| A_policy | hybrid | all_groups_hit_at_10 | 1.0 / n=2 | {} |
| A_policy | hybrid | candidate_group_coverage | 1.0 / n=2 | {} |
| A_policy | hybrid | prompt_group_coverage | 1.0 / n=2 | {} |
| A_policy | hybrid | answer_point_coverage | 1.0 / n=2 | {} |
| A_policy | hybrid | faithfulness | 1.0 / n=2 | {} |
| A_policy | hybrid | absent_refusal_rate | N/A / n=0 | {"answerable": 2} |
| A_policy | hybrid | answerable_false_refusal_rate | 0.0 / n=2 | {} |
| A_policy | hybrid_rerank | recall_at_5 | 1.0 / n=2 | {} |
| A_policy | hybrid_rerank | recall_at_10 | 1.0 / n=2 | {} |
| A_policy | hybrid_rerank | mrr_at_10 | 1.0 / n=2 | {} |
| A_policy | hybrid_rerank | all_groups_hit_at_5 | 1.0 / n=2 | {} |
| A_policy | hybrid_rerank | all_groups_hit_at_10 | 1.0 / n=2 | {} |
| A_policy | hybrid_rerank | candidate_group_coverage | 1.0 / n=2 | {} |
| A_policy | hybrid_rerank | prompt_group_coverage | 1.0 / n=2 | {} |
| A_policy | hybrid_rerank | answer_point_coverage | 0.75 / n=2 | {} |
| A_policy | hybrid_rerank | faithfulness | 1.0 / n=2 | {} |
| A_policy | hybrid_rerank | absent_refusal_rate | N/A / n=0 | {"answerable": 2} |
| A_policy | hybrid_rerank | answerable_false_refusal_rate | 0.0 / n=2 | {} |
| B_model | dense | recall_at_5 | N/A / n=0 | {"rewrite_error": 2} |
| B_model | dense | recall_at_10 | N/A / n=0 | {"rewrite_error": 2} |
| B_model | dense | mrr_at_10 | N/A / n=0 | {"rewrite_error": 2} |
| B_model | dense | all_groups_hit_at_5 | N/A / n=0 | {"rewrite_error": 2} |
| B_model | dense | all_groups_hit_at_10 | N/A / n=0 | {"rewrite_error": 2} |
| B_model | dense | candidate_group_coverage | N/A / n=0 | {"rewrite_error": 2} |
| B_model | dense | prompt_group_coverage | N/A / n=0 | {"rewrite_error": 2} |
| B_model | dense | answer_point_coverage | N/A / n=0 | {"rewrite_error": 2} |
| B_model | dense | faithfulness | N/A / n=0 | {"rewrite_error": 2} |
| B_model | dense | absent_refusal_rate | N/A / n=0 | {"answerable": 2} |
| B_model | dense | answerable_false_refusal_rate | N/A / n=0 | {"rewrite_error": 2} |
| B_model | bm25 | recall_at_5 | N/A / n=0 | {"rewrite_error": 2} |
| B_model | bm25 | recall_at_10 | N/A / n=0 | {"rewrite_error": 2} |
| B_model | bm25 | mrr_at_10 | N/A / n=0 | {"rewrite_error": 2} |
| B_model | bm25 | all_groups_hit_at_5 | N/A / n=0 | {"rewrite_error": 2} |
| B_model | bm25 | all_groups_hit_at_10 | N/A / n=0 | {"rewrite_error": 2} |
| B_model | bm25 | candidate_group_coverage | N/A / n=0 | {"rewrite_error": 2} |
| B_model | bm25 | prompt_group_coverage | N/A / n=0 | {"rewrite_error": 2} |
| B_model | bm25 | answer_point_coverage | N/A / n=0 | {"rewrite_error": 2} |
| B_model | bm25 | faithfulness | N/A / n=0 | {"rewrite_error": 2} |
| B_model | bm25 | absent_refusal_rate | N/A / n=0 | {"answerable": 2} |
| B_model | bm25 | answerable_false_refusal_rate | N/A / n=0 | {"rewrite_error": 2} |
| B_model | hybrid | recall_at_5 | N/A / n=0 | {"rewrite_error": 2} |
| B_model | hybrid | recall_at_10 | N/A / n=0 | {"rewrite_error": 2} |
| B_model | hybrid | mrr_at_10 | N/A / n=0 | {"rewrite_error": 2} |
| B_model | hybrid | all_groups_hit_at_5 | N/A / n=0 | {"rewrite_error": 2} |
| B_model | hybrid | all_groups_hit_at_10 | N/A / n=0 | {"rewrite_error": 2} |
| B_model | hybrid | candidate_group_coverage | N/A / n=0 | {"rewrite_error": 2} |
| B_model | hybrid | prompt_group_coverage | N/A / n=0 | {"rewrite_error": 2} |
| B_model | hybrid | answer_point_coverage | N/A / n=0 | {"rewrite_error": 2} |
| B_model | hybrid | faithfulness | N/A / n=0 | {"rewrite_error": 2} |
| B_model | hybrid | absent_refusal_rate | N/A / n=0 | {"answerable": 2} |
| B_model | hybrid | answerable_false_refusal_rate | N/A / n=0 | {"rewrite_error": 2} |
| B_model | hybrid_rerank | recall_at_5 | N/A / n=0 | {"rewrite_error": 2} |
| B_model | hybrid_rerank | recall_at_10 | N/A / n=0 | {"rewrite_error": 2} |
| B_model | hybrid_rerank | mrr_at_10 | N/A / n=0 | {"rewrite_error": 2} |
| B_model | hybrid_rerank | all_groups_hit_at_5 | N/A / n=0 | {"rewrite_error": 2} |
| B_model | hybrid_rerank | all_groups_hit_at_10 | N/A / n=0 | {"rewrite_error": 2} |
| B_model | hybrid_rerank | candidate_group_coverage | N/A / n=0 | {"rewrite_error": 2} |
| B_model | hybrid_rerank | prompt_group_coverage | N/A / n=0 | {"rewrite_error": 2} |
| B_model | hybrid_rerank | answer_point_coverage | N/A / n=0 | {"rewrite_error": 2} |
| B_model | hybrid_rerank | faithfulness | N/A / n=0 | {"rewrite_error": 2} |
| B_model | hybrid_rerank | absent_refusal_rate | N/A / n=0 | {"answerable": 2} |
| B_model | hybrid_rerank | answerable_false_refusal_rate | N/A / n=0 | {"rewrite_error": 2} |
| C_colloquial | dense | recall_at_5 | 1.0 / n=2 | {} |
| C_colloquial | dense | recall_at_10 | 1.0 / n=2 | {} |
| C_colloquial | dense | mrr_at_10 | 1.0 / n=2 | {} |
| C_colloquial | dense | all_groups_hit_at_5 | 1.0 / n=2 | {} |
| C_colloquial | dense | all_groups_hit_at_10 | 1.0 / n=2 | {} |
| C_colloquial | dense | candidate_group_coverage | 1.0 / n=2 | {} |
| C_colloquial | dense | prompt_group_coverage | 1.0 / n=2 | {} |
| C_colloquial | dense | answer_point_coverage | 1.0 / n=2 | {} |
| C_colloquial | dense | faithfulness | 1.0 / n=2 | {} |
| C_colloquial | dense | absent_refusal_rate | N/A / n=0 | {"answerable": 2} |
| C_colloquial | dense | answerable_false_refusal_rate | 0.0 / n=2 | {} |
| C_colloquial | bm25 | recall_at_5 | 1.0 / n=2 | {} |
| C_colloquial | bm25 | recall_at_10 | 1.0 / n=2 | {} |
| C_colloquial | bm25 | mrr_at_10 | 0.6666666666666666 / n=2 | {} |
| C_colloquial | bm25 | all_groups_hit_at_5 | 1.0 / n=2 | {} |
| C_colloquial | bm25 | all_groups_hit_at_10 | 1.0 / n=2 | {} |
| C_colloquial | bm25 | candidate_group_coverage | 1.0 / n=2 | {} |
| C_colloquial | bm25 | prompt_group_coverage | 1.0 / n=2 | {} |
| C_colloquial | bm25 | answer_point_coverage | 1.0 / n=2 | {} |
| C_colloquial | bm25 | faithfulness | 1.0 / n=2 | {} |
| C_colloquial | bm25 | absent_refusal_rate | N/A / n=0 | {"answerable": 2} |
| C_colloquial | bm25 | answerable_false_refusal_rate | 0.0 / n=2 | {} |
| C_colloquial | hybrid | recall_at_5 | 1.0 / n=2 | {} |
| C_colloquial | hybrid | recall_at_10 | 1.0 / n=2 | {} |
| C_colloquial | hybrid | mrr_at_10 | 0.75 / n=2 | {} |
| C_colloquial | hybrid | all_groups_hit_at_5 | 1.0 / n=2 | {} |
| C_colloquial | hybrid | all_groups_hit_at_10 | 1.0 / n=2 | {} |
| C_colloquial | hybrid | candidate_group_coverage | 1.0 / n=2 | {} |
| C_colloquial | hybrid | prompt_group_coverage | 1.0 / n=2 | {} |
| C_colloquial | hybrid | answer_point_coverage | 1.0 / n=2 | {} |
| C_colloquial | hybrid | faithfulness | 0.8333333333333333 / n=2 | {} |
| C_colloquial | hybrid | absent_refusal_rate | N/A / n=0 | {"answerable": 2} |
| C_colloquial | hybrid | answerable_false_refusal_rate | 0.0 / n=2 | {} |
| C_colloquial | hybrid_rerank | recall_at_5 | 1.0 / n=2 | {} |
| C_colloquial | hybrid_rerank | recall_at_10 | 1.0 / n=2 | {} |
| C_colloquial | hybrid_rerank | mrr_at_10 | 1.0 / n=2 | {} |
| C_colloquial | hybrid_rerank | all_groups_hit_at_5 | 1.0 / n=2 | {} |
| C_colloquial | hybrid_rerank | all_groups_hit_at_10 | 1.0 / n=2 | {} |
| C_colloquial | hybrid_rerank | candidate_group_coverage | 1.0 / n=2 | {} |
| C_colloquial | hybrid_rerank | prompt_group_coverage | 1.0 / n=2 | {} |
| C_colloquial | hybrid_rerank | answer_point_coverage | 1.0 / n=2 | {} |
| C_colloquial | hybrid_rerank | faithfulness | 0.875 / n=2 | {} |
| C_colloquial | hybrid_rerank | absent_refusal_rate | N/A / n=0 | {"answerable": 2} |
| C_colloquial | hybrid_rerank | answerable_false_refusal_rate | 0.0 / n=2 | {} |
| D_unanswerable | dense | recall_at_5 | N/A / n=0 | {"expected_refusal": 2} |
| D_unanswerable | dense | recall_at_10 | N/A / n=0 | {"expected_refusal": 2} |
| D_unanswerable | dense | mrr_at_10 | N/A / n=0 | {"expected_refusal": 2} |
| D_unanswerable | dense | all_groups_hit_at_5 | N/A / n=0 | {"expected_refusal": 2} |
| D_unanswerable | dense | all_groups_hit_at_10 | N/A / n=0 | {"expected_refusal": 2} |
| D_unanswerable | dense | candidate_group_coverage | N/A / n=0 | {"expected_refusal": 2} |
| D_unanswerable | dense | prompt_group_coverage | N/A / n=0 | {"expected_refusal": 2} |
| D_unanswerable | dense | answer_point_coverage | N/A / n=0 | {"expected_refusal": 2} |
| D_unanswerable | dense | faithfulness | 1.0 / n=1 | {"zero_claims": 1} |
| D_unanswerable | dense | absent_refusal_rate | 1.0 / n=2 | {} |
| D_unanswerable | dense | answerable_false_refusal_rate | N/A / n=0 | {"expected_refusal": 2} |
| D_unanswerable | bm25 | recall_at_5 | N/A / n=0 | {"expected_refusal": 2} |
| D_unanswerable | bm25 | recall_at_10 | N/A / n=0 | {"expected_refusal": 2} |
| D_unanswerable | bm25 | mrr_at_10 | N/A / n=0 | {"expected_refusal": 2} |
| D_unanswerable | bm25 | all_groups_hit_at_5 | N/A / n=0 | {"expected_refusal": 2} |
| D_unanswerable | bm25 | all_groups_hit_at_10 | N/A / n=0 | {"expected_refusal": 2} |
| D_unanswerable | bm25 | candidate_group_coverage | N/A / n=0 | {"expected_refusal": 2} |
| D_unanswerable | bm25 | prompt_group_coverage | N/A / n=0 | {"expected_refusal": 2} |
| D_unanswerable | bm25 | answer_point_coverage | N/A / n=0 | {"expected_refusal": 2} |
| D_unanswerable | bm25 | faithfulness | N/A / n=0 | {"zero_claims": 2} |
| D_unanswerable | bm25 | absent_refusal_rate | 1.0 / n=2 | {} |
| D_unanswerable | bm25 | answerable_false_refusal_rate | N/A / n=0 | {"expected_refusal": 2} |
| D_unanswerable | hybrid | recall_at_5 | N/A / n=0 | {"expected_refusal": 2} |
| D_unanswerable | hybrid | recall_at_10 | N/A / n=0 | {"expected_refusal": 2} |
| D_unanswerable | hybrid | mrr_at_10 | N/A / n=0 | {"expected_refusal": 2} |
| D_unanswerable | hybrid | all_groups_hit_at_5 | N/A / n=0 | {"expected_refusal": 2} |
| D_unanswerable | hybrid | all_groups_hit_at_10 | N/A / n=0 | {"expected_refusal": 2} |
| D_unanswerable | hybrid | candidate_group_coverage | N/A / n=0 | {"expected_refusal": 2} |
| D_unanswerable | hybrid | prompt_group_coverage | N/A / n=0 | {"expected_refusal": 2} |
| D_unanswerable | hybrid | answer_point_coverage | N/A / n=0 | {"expected_refusal": 2} |
| D_unanswerable | hybrid | faithfulness | 1.0 / n=1 | {"zero_claims": 1} |
| D_unanswerable | hybrid | absent_refusal_rate | 1.0 / n=2 | {} |
| D_unanswerable | hybrid | answerable_false_refusal_rate | N/A / n=0 | {"expected_refusal": 2} |
| D_unanswerable | hybrid_rerank | recall_at_5 | N/A / n=0 | {"expected_refusal": 2} |
| D_unanswerable | hybrid_rerank | recall_at_10 | N/A / n=0 | {"expected_refusal": 2} |
| D_unanswerable | hybrid_rerank | mrr_at_10 | N/A / n=0 | {"expected_refusal": 2} |
| D_unanswerable | hybrid_rerank | all_groups_hit_at_5 | N/A / n=0 | {"expected_refusal": 2} |
| D_unanswerable | hybrid_rerank | all_groups_hit_at_10 | N/A / n=0 | {"expected_refusal": 2} |
| D_unanswerable | hybrid_rerank | candidate_group_coverage | N/A / n=0 | {"expected_refusal": 2} |
| D_unanswerable | hybrid_rerank | prompt_group_coverage | N/A / n=0 | {"expected_refusal": 2} |
| D_unanswerable | hybrid_rerank | answer_point_coverage | N/A / n=0 | {"expected_refusal": 2} |
| D_unanswerable | hybrid_rerank | faithfulness | 1.0 / n=2 | {} |
| D_unanswerable | hybrid_rerank | absent_refusal_rate | 1.0 / n=2 | {} |
| D_unanswerable | hybrid_rerank | answerable_false_refusal_rate | N/A / n=0 | {"expected_refusal": 2} |
| E_multi | dense | recall_at_5 | 1.0 / n=2 | {} |
| E_multi | dense | recall_at_10 | 1.0 / n=2 | {} |
| E_multi | dense | mrr_at_10 | 1.0 / n=2 | {} |
| E_multi | dense | all_groups_hit_at_5 | 1.0 / n=2 | {} |
| E_multi | dense | all_groups_hit_at_10 | 1.0 / n=2 | {} |
| E_multi | dense | candidate_group_coverage | 1.0 / n=2 | {} |
| E_multi | dense | prompt_group_coverage | 1.0 / n=2 | {} |
| E_multi | dense | answer_point_coverage | 1.0 / n=2 | {} |
| E_multi | dense | faithfulness | 1.0 / n=2 | {} |
| E_multi | dense | absent_refusal_rate | N/A / n=0 | {"answerable": 2} |
| E_multi | dense | answerable_false_refusal_rate | 0.0 / n=2 | {} |
| E_multi | bm25 | recall_at_5 | 0.6666666666666666 / n=2 | {} |
| E_multi | bm25 | recall_at_10 | 0.8333333333333333 / n=2 | {} |
| E_multi | bm25 | mrr_at_10 | 1.0 / n=2 | {} |
| E_multi | bm25 | all_groups_hit_at_5 | 0.5 / n=2 | {} |
| E_multi | bm25 | all_groups_hit_at_10 | 0.5 / n=2 | {} |
| E_multi | bm25 | candidate_group_coverage | 1.0 / n=2 | {} |
| E_multi | bm25 | prompt_group_coverage | 0.8333333333333333 / n=2 | {} |
| E_multi | bm25 | answer_point_coverage | 0.8333333333333333 / n=2 | {} |
| E_multi | bm25 | faithfulness | 1.0 / n=2 | {} |
| E_multi | bm25 | absent_refusal_rate | N/A / n=0 | {"answerable": 2} |
| E_multi | bm25 | answerable_false_refusal_rate | 0.0 / n=2 | {} |
| E_multi | hybrid | recall_at_5 | 0.8333333333333333 / n=2 | {} |
| E_multi | hybrid | recall_at_10 | 1.0 / n=2 | {} |
| E_multi | hybrid | mrr_at_10 | 1.0 / n=2 | {} |
| E_multi | hybrid | all_groups_hit_at_5 | 0.5 / n=2 | {} |
| E_multi | hybrid | all_groups_hit_at_10 | 1.0 / n=2 | {} |
| E_multi | hybrid | candidate_group_coverage | 1.0 / n=2 | {} |
| E_multi | hybrid | prompt_group_coverage | 1.0 / n=2 | {} |
| E_multi | hybrid | answer_point_coverage | 1.0 / n=2 | {} |
| E_multi | hybrid | faithfulness | 1.0 / n=2 | {} |
| E_multi | hybrid | absent_refusal_rate | N/A / n=0 | {"answerable": 2} |
| E_multi | hybrid | answerable_false_refusal_rate | 0.0 / n=2 | {} |
| E_multi | hybrid_rerank | recall_at_5 | 1.0 / n=2 | {} |
| E_multi | hybrid_rerank | recall_at_10 | 1.0 / n=2 | {} |
| E_multi | hybrid_rerank | mrr_at_10 | 1.0 / n=2 | {} |
| E_multi | hybrid_rerank | all_groups_hit_at_5 | 1.0 / n=2 | {} |
| E_multi | hybrid_rerank | all_groups_hit_at_10 | 1.0 / n=2 | {} |
| E_multi | hybrid_rerank | candidate_group_coverage | 1.0 / n=2 | {} |
| E_multi | hybrid_rerank | prompt_group_coverage | 1.0 / n=2 | {} |
| E_multi | hybrid_rerank | answer_point_coverage | 0.5 / n=2 | {} |
| E_multi | hybrid_rerank | faithfulness | 1.0 / n=1 | {"zero_claims": 1} |
| E_multi | hybrid_rerank | absent_refusal_rate | N/A / n=0 | {"answerable": 2} |
| E_multi | hybrid_rerank | answerable_false_refusal_rate | 0.5 / n=2 | {} |

完整candidate/final金标组位置及Prompt保留在[派生JSON](merchant-rag-observed-analysis.json)。B3/B54检索未执行，不捏造排名；未支持断言造成的合法质量台账upsert另见[资源归因](merchant-rag-observed-resource-proof.json)，不声称全部16表不变。
