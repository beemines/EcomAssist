# 本轮实际质量、改写成功率与分母

Run `aecdf615794d4ccdad984c9caeda979f`；scope `pilot`；counts `{"completed": 40, "rewrite_error": 0, "retrieval_error": 0, "self_check_error": 0, "answer_error": 0, "judge_error": 0, "cancelled": 0, "not_attempted": 0, "running": 0, "total": 40, "attempted": 40, "errors": 0}`；按题rewrite `{"attempted_n": 10, "success_n": 10, "degraded_n": 0, "error_n": 0, "success_rate": 1.0, "unreported_n": 0}`。原pair按字节保留，degraded单列，不改旧报告。

四路共同完整 10 题；共同可答 8 题。各指标仍按原 valid_n/excluded，错误、零断言或不适用不手动填分。

| 策略 | completed/errors | Recall5 | Recall10 | MRR10 | Prompt | 要点 | Faith | 库外拒答 | 可答误拒答 |
|---|---|---|---|---|---|---|---|---|
| dense | 10/0 | 1.0 / n=8 | 1.0 / n=8 | 1.0 / n=8 | 1.0 / n=8 | 0.9583333333333334 / n=8 | 0.9722222222222222 / n=9 | 1.0 / n=2 | 0.0 / n=8 |
| bm25 | 10/0 | 0.9166666666666666 / n=8 | 0.9583333333333334 / n=8 | 0.9166666666666666 / n=8 | 0.9583333333333334 / n=8 | 0.8125 / n=8 | 1.0 / n=8 | 1.0 / n=2 | 0.125 / n=8 |
| hybrid | 10/0 | 0.9583333333333334 / n=8 | 1.0 / n=8 | 0.9375 / n=8 | 1.0 / n=8 | 0.9375 / n=8 | 1.0 / n=8 | 1.0 / n=2 | 0.0 / n=8 |
| hybrid_rerank | 10/0 | 1.0 / n=8 | 1.0 / n=8 | 1.0 / n=8 | 1.0 / n=8 | 0.9375 / n=8 | 1.0 / n=8 | 1.0 / n=2 | 0.0 / n=8 |

候选50/语料50有饱和局限；检索、要点和忠实度须看各自分母，误拒答越低越好，不设总体冠军。仅本run实测结果，不把试运行外推为300题。

| 共同可答策略 | 要点 | Faith | 误拒答 |
|---|---|---|---|
| dense | 0.9583333333333334 / n=8 | 0.96875 / n=8 | 0.0 / n=8 |
| bm25 | 0.8125 / n=8 | 1.0 / n=7 | 0.125 / n=8 |
| hybrid | 0.9375 / n=8 | 1.0 / n=8 | 0.0 / n=8 |
| hybrid_rerank | 0.9375 / n=8 | 1.0 / n=8 | 0.0 / n=8 |

## 裁判语义差异（保留原判定）

| 题号 | 四路实际回答相同 | 策略 | refused | claims / unsupported |
|---|---|---|---|---|
| D1 | True | dense | True | 2/0 |
| D1 | True | bm25 | True | 0/0 |
| D1 | True | hybrid | True | 0/0 |
| D1 | True | hybrid_rerank | True | 0/0 |
| D3 | True | dense | True | 0/0 |
| D3 | True | bm25 | True | 2/0 |
| D3 | True | hybrid | True | 0/0 |
| D3 | True | hybrid_rerank | True | 0/0 |

## 每桶、策略、指标精确值与分母

| 桶 | 策略 | 指标 | value / valid_n | excluded |
|---|---|---|---|---|
| overall | dense | recall_at_5 | 1.0 / n=8 | {"expected_refusal": 2} |
| overall | dense | recall_at_10 | 1.0 / n=8 | {"expected_refusal": 2} |
| overall | dense | mrr_at_10 | 1.0 / n=8 | {"expected_refusal": 2} |
| overall | dense | all_groups_hit_at_5 | 1.0 / n=8 | {"expected_refusal": 2} |
| overall | dense | all_groups_hit_at_10 | 1.0 / n=8 | {"expected_refusal": 2} |
| overall | dense | candidate_group_coverage | 1.0 / n=8 | {"expected_refusal": 2} |
| overall | dense | prompt_group_coverage | 1.0 / n=8 | {"expected_refusal": 2} |
| overall | dense | answer_point_coverage | 0.9583333333333334 / n=8 | {"expected_refusal": 2} |
| overall | dense | faithfulness | 0.9722222222222222 / n=9 | {"zero_claims": 1} |
| overall | dense | absent_refusal_rate | 1.0 / n=2 | {"answerable": 8} |
| overall | dense | answerable_false_refusal_rate | 0.0 / n=8 | {"expected_refusal": 2} |
| overall | bm25 | recall_at_5 | 0.9166666666666666 / n=8 | {"expected_refusal": 2} |
| overall | bm25 | recall_at_10 | 0.9583333333333334 / n=8 | {"expected_refusal": 2} |
| overall | bm25 | mrr_at_10 | 0.9166666666666666 / n=8 | {"expected_refusal": 2} |
| overall | bm25 | all_groups_hit_at_5 | 0.875 / n=8 | {"expected_refusal": 2} |
| overall | bm25 | all_groups_hit_at_10 | 0.875 / n=8 | {"expected_refusal": 2} |
| overall | bm25 | candidate_group_coverage | 1.0 / n=8 | {"expected_refusal": 2} |
| overall | bm25 | prompt_group_coverage | 0.9583333333333334 / n=8 | {"expected_refusal": 2} |
| overall | bm25 | answer_point_coverage | 0.8125 / n=8 | {"expected_refusal": 2} |
| overall | bm25 | faithfulness | 1.0 / n=8 | {"zero_claims": 2} |
| overall | bm25 | absent_refusal_rate | 1.0 / n=2 | {"answerable": 8} |
| overall | bm25 | answerable_false_refusal_rate | 0.125 / n=8 | {"expected_refusal": 2} |
| overall | hybrid | recall_at_5 | 0.9583333333333334 / n=8 | {"expected_refusal": 2} |
| overall | hybrid | recall_at_10 | 1.0 / n=8 | {"expected_refusal": 2} |
| overall | hybrid | mrr_at_10 | 0.9375 / n=8 | {"expected_refusal": 2} |
| overall | hybrid | all_groups_hit_at_5 | 0.875 / n=8 | {"expected_refusal": 2} |
| overall | hybrid | all_groups_hit_at_10 | 1.0 / n=8 | {"expected_refusal": 2} |
| overall | hybrid | candidate_group_coverage | 1.0 / n=8 | {"expected_refusal": 2} |
| overall | hybrid | prompt_group_coverage | 1.0 / n=8 | {"expected_refusal": 2} |
| overall | hybrid | answer_point_coverage | 0.9375 / n=8 | {"expected_refusal": 2} |
| overall | hybrid | faithfulness | 1.0 / n=8 | {"zero_claims": 2} |
| overall | hybrid | absent_refusal_rate | 1.0 / n=2 | {"answerable": 8} |
| overall | hybrid | answerable_false_refusal_rate | 0.0 / n=8 | {"expected_refusal": 2} |
| overall | hybrid_rerank | recall_at_5 | 1.0 / n=8 | {"expected_refusal": 2} |
| overall | hybrid_rerank | recall_at_10 | 1.0 / n=8 | {"expected_refusal": 2} |
| overall | hybrid_rerank | mrr_at_10 | 1.0 / n=8 | {"expected_refusal": 2} |
| overall | hybrid_rerank | all_groups_hit_at_5 | 1.0 / n=8 | {"expected_refusal": 2} |
| overall | hybrid_rerank | all_groups_hit_at_10 | 1.0 / n=8 | {"expected_refusal": 2} |
| overall | hybrid_rerank | candidate_group_coverage | 1.0 / n=8 | {"expected_refusal": 2} |
| overall | hybrid_rerank | prompt_group_coverage | 1.0 / n=8 | {"expected_refusal": 2} |
| overall | hybrid_rerank | answer_point_coverage | 0.9375 / n=8 | {"expected_refusal": 2} |
| overall | hybrid_rerank | faithfulness | 1.0 / n=8 | {"zero_claims": 2} |
| overall | hybrid_rerank | absent_refusal_rate | 1.0 / n=2 | {"answerable": 8} |
| overall | hybrid_rerank | answerable_false_refusal_rate | 0.0 / n=8 | {"expected_refusal": 2} |
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
| A_policy | bm25 | answer_point_coverage | 0.75 / n=2 | {} |
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
| A_policy | hybrid | answer_point_coverage | 0.75 / n=2 | {} |
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
| B_model | dense | recall_at_5 | 1.0 / n=2 | {} |
| B_model | dense | recall_at_10 | 1.0 / n=2 | {} |
| B_model | dense | mrr_at_10 | 1.0 / n=2 | {} |
| B_model | dense | all_groups_hit_at_5 | 1.0 / n=2 | {} |
| B_model | dense | all_groups_hit_at_10 | 1.0 / n=2 | {} |
| B_model | dense | candidate_group_coverage | 1.0 / n=2 | {} |
| B_model | dense | prompt_group_coverage | 1.0 / n=2 | {} |
| B_model | dense | answer_point_coverage | 1.0 / n=2 | {} |
| B_model | dense | faithfulness | 1.0 / n=2 | {} |
| B_model | dense | absent_refusal_rate | N/A / n=0 | {"answerable": 2} |
| B_model | dense | answerable_false_refusal_rate | 0.0 / n=2 | {} |
| B_model | bm25 | recall_at_5 | 1.0 / n=2 | {} |
| B_model | bm25 | recall_at_10 | 1.0 / n=2 | {} |
| B_model | bm25 | mrr_at_10 | 1.0 / n=2 | {} |
| B_model | bm25 | all_groups_hit_at_5 | 1.0 / n=2 | {} |
| B_model | bm25 | all_groups_hit_at_10 | 1.0 / n=2 | {} |
| B_model | bm25 | candidate_group_coverage | 1.0 / n=2 | {} |
| B_model | bm25 | prompt_group_coverage | 1.0 / n=2 | {} |
| B_model | bm25 | answer_point_coverage | 1.0 / n=2 | {} |
| B_model | bm25 | faithfulness | 1.0 / n=2 | {} |
| B_model | bm25 | absent_refusal_rate | N/A / n=0 | {"answerable": 2} |
| B_model | bm25 | answerable_false_refusal_rate | 0.0 / n=2 | {} |
| B_model | hybrid | recall_at_5 | 1.0 / n=2 | {} |
| B_model | hybrid | recall_at_10 | 1.0 / n=2 | {} |
| B_model | hybrid | mrr_at_10 | 1.0 / n=2 | {} |
| B_model | hybrid | all_groups_hit_at_5 | 1.0 / n=2 | {} |
| B_model | hybrid | all_groups_hit_at_10 | 1.0 / n=2 | {} |
| B_model | hybrid | candidate_group_coverage | 1.0 / n=2 | {} |
| B_model | hybrid | prompt_group_coverage | 1.0 / n=2 | {} |
| B_model | hybrid | answer_point_coverage | 1.0 / n=2 | {} |
| B_model | hybrid | faithfulness | 1.0 / n=2 | {} |
| B_model | hybrid | absent_refusal_rate | N/A / n=0 | {"answerable": 2} |
| B_model | hybrid | answerable_false_refusal_rate | 0.0 / n=2 | {} |
| B_model | hybrid_rerank | recall_at_5 | 1.0 / n=2 | {} |
| B_model | hybrid_rerank | recall_at_10 | 1.0 / n=2 | {} |
| B_model | hybrid_rerank | mrr_at_10 | 1.0 / n=2 | {} |
| B_model | hybrid_rerank | all_groups_hit_at_5 | 1.0 / n=2 | {} |
| B_model | hybrid_rerank | all_groups_hit_at_10 | 1.0 / n=2 | {} |
| B_model | hybrid_rerank | candidate_group_coverage | 1.0 / n=2 | {} |
| B_model | hybrid_rerank | prompt_group_coverage | 1.0 / n=2 | {} |
| B_model | hybrid_rerank | answer_point_coverage | 1.0 / n=2 | {} |
| B_model | hybrid_rerank | faithfulness | 1.0 / n=2 | {} |
| B_model | hybrid_rerank | absent_refusal_rate | N/A / n=0 | {"answerable": 2} |
| B_model | hybrid_rerank | answerable_false_refusal_rate | 0.0 / n=2 | {} |
| C_colloquial | dense | recall_at_5 | 1.0 / n=2 | {} |
| C_colloquial | dense | recall_at_10 | 1.0 / n=2 | {} |
| C_colloquial | dense | mrr_at_10 | 1.0 / n=2 | {} |
| C_colloquial | dense | all_groups_hit_at_5 | 1.0 / n=2 | {} |
| C_colloquial | dense | all_groups_hit_at_10 | 1.0 / n=2 | {} |
| C_colloquial | dense | candidate_group_coverage | 1.0 / n=2 | {} |
| C_colloquial | dense | prompt_group_coverage | 1.0 / n=2 | {} |
| C_colloquial | dense | answer_point_coverage | 1.0 / n=2 | {} |
| C_colloquial | dense | faithfulness | 0.875 / n=2 | {} |
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
| C_colloquial | hybrid | faithfulness | 1.0 / n=2 | {} |
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
| C_colloquial | hybrid_rerank | faithfulness | 1.0 / n=2 | {} |
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
| D_unanswerable | bm25 | faithfulness | 1.0 / n=1 | {"zero_claims": 1} |
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
| D_unanswerable | hybrid | faithfulness | N/A / n=0 | {"zero_claims": 2} |
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
| D_unanswerable | hybrid_rerank | faithfulness | N/A / n=0 | {"zero_claims": 2} |
| D_unanswerable | hybrid_rerank | absent_refusal_rate | 1.0 / n=2 | {} |
| D_unanswerable | hybrid_rerank | answerable_false_refusal_rate | N/A / n=0 | {"expected_refusal": 2} |
| E_multi | dense | recall_at_5 | 1.0 / n=2 | {} |
| E_multi | dense | recall_at_10 | 1.0 / n=2 | {} |
| E_multi | dense | mrr_at_10 | 1.0 / n=2 | {} |
| E_multi | dense | all_groups_hit_at_5 | 1.0 / n=2 | {} |
| E_multi | dense | all_groups_hit_at_10 | 1.0 / n=2 | {} |
| E_multi | dense | candidate_group_coverage | 1.0 / n=2 | {} |
| E_multi | dense | prompt_group_coverage | 1.0 / n=2 | {} |
| E_multi | dense | answer_point_coverage | 0.8333333333333333 / n=2 | {} |
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
| E_multi | bm25 | answer_point_coverage | 0.5 / n=2 | {} |
| E_multi | bm25 | faithfulness | 1.0 / n=1 | {"zero_claims": 1} |
| E_multi | bm25 | absent_refusal_rate | N/A / n=0 | {"answerable": 2} |
| E_multi | bm25 | answerable_false_refusal_rate | 0.5 / n=2 | {} |
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
| E_multi | hybrid_rerank | answer_point_coverage | 1.0 / n=2 | {} |
| E_multi | hybrid_rerank | faithfulness | 1.0 / n=2 | {} |
| E_multi | hybrid_rerank | absent_refusal_rate | N/A / n=0 | {"answerable": 2} |
| E_multi | hybrid_rerank | answerable_false_refusal_rate | 0.0 / n=2 | {} |

完整共同可答题号、候选/最终金标位置和Prompt证据见[JSON](merchant-rag-degraded-analysis.json)。质量台账合法upsert见[资源证明](merchant-rag-degraded-resource-proof.json)，不声称全部16表不变。
