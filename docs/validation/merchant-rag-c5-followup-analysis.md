# 新授权固定试跑的实际分析

Run `b1af9aadc0094141aa5df5ae0ec91bd1`；40实际记录/32completed/8rewrite_error，full未运行。此文为保存结果的离线派生说明；原服务器JSON/Markdown逐字节保留。

B54和E19各一次共享改写失败影响四路，elapsed分别1422.989800106734ms、1839.666800107807ms。原具体ServiceError.code、finish/raw未捕获；不能从安全rewrite_error投影确定根因，也不能算作8次改写调用。

共同四路合法8题：A21, A43, B3, C35, C5, D1, D3, E2；共同可答6题：A21, A43, B3, C35, C5, E2。原40总体保留所有错误；各指标自己的valid_n和排除原因完整保存。

| 策略 | completed/errors | Recall5 | Recall10 | MRR10 | Prompt | 要点 | Faith | 库外拒答 | 可答误拒答 |
|---|---|---|---|---|---|---|---|---|---|
| dense | 8/2 | 1.0 / n=6 | 1.0 / n=6 | 1.0 / n=6 | 1.0 / n=6 | 1.0 / n=6 | 0.8571428571428571 / n=7 | 1.0 / n=2 | 0.0 / n=6 |
| bm25 | 8/2 | 0.8888888888888888 / n=6 | 0.9444444444444445 / n=6 | 0.8888888888888888 / n=6 | 0.9444444444444445 / n=6 | 0.6666666666666666 / n=6 | 1.0 / n=5 | 1.0 / n=2 | 0.3333333333333333 / n=6 |
| hybrid | 8/2 | 0.9444444444444445 / n=6 | 1.0 / n=6 | 0.9166666666666666 / n=6 | 1.0 / n=6 | 1.0 / n=6 | 0.7 / n=8 | 1.0 / n=2 | 0.0 / n=6 |
| hybrid_rerank | 8/2 | 1.0 / n=6 | 1.0 / n=6 | 1.0 / n=6 | 1.0 / n=6 | 0.8611111111111112 / n=6 | 0.9821428571428571 / n=7 | 1.0 / n=2 | 0.0 / n=6 |

总体检索/要点/可答误拒答：expected_refusal2+rewrite_error2各路排除；Faith排除rewrite_error2各路，另zero_claims dense1/bm253/rerank1，hybrid0。库外拒答n2各路，N/A保持不填满分。candidate Top50 coverage=1/n6各路，但候选50与语料50饱和，不证明真实大语料效果。

| 共同可答策略 | 要点 | Faith | 误拒答 |
|---|---|---|---|
| dense | 1.0 / n=6 | 1.0 / n=6 | 0.0 / n=6 |
| bm25 | 0.6666666666666666 / n=6 | 1.0 / n=4 | 0.3333333333333333 / n=6 |
| hybrid | 1.0 / n=6 | 0.9333333333333332 / n=6 | 0.0 / n=6 |
| hybrid_rerank | 0.8611111111111112 / n=6 | 0.9791666666666666 / n=6 | 0.0 / n=6 |

C5本轮四路均completed/useful=true/refused=false，point2/2，dense claims5、另外各3，unsupported均0，32次合法裁判finish均stop。本次诊断与本轮C5记录独立，不补原失败。

D1/D3四路协议均refused=true；实际裁判对相同固定拒答的claims拆分和support存在差异。原裁判结果保留，不能重标人工真值；详细每路计数见analysis JSON。bm25总体Faith=1/n5仍有可答误拒答2/6；rerank要点约.861/Faith约.982和hybrid要点1/Faith.7是本轮观察，不设总体赢家、不外推300题。

| 实际unsupported | 策略 | unsupported / claims |
|---|---|---|
| A21 | hybrid_rerank | 1/8 |
| C35 | hybrid | 2/5 |
| D1 | dense | 2/2 |
| D1 | hybrid | 1/1 |
| D3 | hybrid | 2/2 |

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
| overall | dense | faithfulness | 0.8571428571428571 / n=7 | {"rewrite_error": 2, "zero_claims": 1} |
| overall | dense | absent_refusal_rate | 1.0 / n=2 | {"answerable": 8} |
| overall | dense | answerable_false_refusal_rate | 0.0 / n=6 | {"expected_refusal": 2, "rewrite_error": 2} |
| overall | bm25 | recall_at_5 | 0.8888888888888888 / n=6 | {"expected_refusal": 2, "rewrite_error": 2} |
| overall | bm25 | recall_at_10 | 0.9444444444444445 / n=6 | {"expected_refusal": 2, "rewrite_error": 2} |
| overall | bm25 | mrr_at_10 | 0.8888888888888888 / n=6 | {"expected_refusal": 2, "rewrite_error": 2} |
| overall | bm25 | all_groups_hit_at_5 | 0.8333333333333334 / n=6 | {"expected_refusal": 2, "rewrite_error": 2} |
| overall | bm25 | all_groups_hit_at_10 | 0.8333333333333334 / n=6 | {"expected_refusal": 2, "rewrite_error": 2} |
| overall | bm25 | candidate_group_coverage | 1.0 / n=6 | {"expected_refusal": 2, "rewrite_error": 2} |
| overall | bm25 | prompt_group_coverage | 0.9444444444444445 / n=6 | {"expected_refusal": 2, "rewrite_error": 2} |
| overall | bm25 | answer_point_coverage | 0.6666666666666666 / n=6 | {"expected_refusal": 2, "rewrite_error": 2} |
| overall | bm25 | faithfulness | 1.0 / n=5 | {"rewrite_error": 2, "zero_claims": 3} |
| overall | bm25 | absent_refusal_rate | 1.0 / n=2 | {"answerable": 8} |
| overall | bm25 | answerable_false_refusal_rate | 0.3333333333333333 / n=6 | {"expected_refusal": 2, "rewrite_error": 2} |
| overall | hybrid | recall_at_5 | 0.9444444444444445 / n=6 | {"expected_refusal": 2, "rewrite_error": 2} |
| overall | hybrid | recall_at_10 | 1.0 / n=6 | {"expected_refusal": 2, "rewrite_error": 2} |
| overall | hybrid | mrr_at_10 | 0.9166666666666666 / n=6 | {"expected_refusal": 2, "rewrite_error": 2} |
| overall | hybrid | all_groups_hit_at_5 | 0.8333333333333334 / n=6 | {"expected_refusal": 2, "rewrite_error": 2} |
| overall | hybrid | all_groups_hit_at_10 | 1.0 / n=6 | {"expected_refusal": 2, "rewrite_error": 2} |
| overall | hybrid | candidate_group_coverage | 1.0 / n=6 | {"expected_refusal": 2, "rewrite_error": 2} |
| overall | hybrid | prompt_group_coverage | 1.0 / n=6 | {"expected_refusal": 2, "rewrite_error": 2} |
| overall | hybrid | answer_point_coverage | 1.0 / n=6 | {"expected_refusal": 2, "rewrite_error": 2} |
| overall | hybrid | faithfulness | 0.7 / n=8 | {"rewrite_error": 2} |
| overall | hybrid | absent_refusal_rate | 1.0 / n=2 | {"answerable": 8} |
| overall | hybrid | answerable_false_refusal_rate | 0.0 / n=6 | {"expected_refusal": 2, "rewrite_error": 2} |
| overall | hybrid_rerank | recall_at_5 | 1.0 / n=6 | {"expected_refusal": 2, "rewrite_error": 2} |
| overall | hybrid_rerank | recall_at_10 | 1.0 / n=6 | {"expected_refusal": 2, "rewrite_error": 2} |
| overall | hybrid_rerank | mrr_at_10 | 1.0 / n=6 | {"expected_refusal": 2, "rewrite_error": 2} |
| overall | hybrid_rerank | all_groups_hit_at_5 | 1.0 / n=6 | {"expected_refusal": 2, "rewrite_error": 2} |
| overall | hybrid_rerank | all_groups_hit_at_10 | 1.0 / n=6 | {"expected_refusal": 2, "rewrite_error": 2} |
| overall | hybrid_rerank | candidate_group_coverage | 1.0 / n=6 | {"expected_refusal": 2, "rewrite_error": 2} |
| overall | hybrid_rerank | prompt_group_coverage | 1.0 / n=6 | {"expected_refusal": 2, "rewrite_error": 2} |
| overall | hybrid_rerank | answer_point_coverage | 0.8611111111111112 / n=6 | {"expected_refusal": 2, "rewrite_error": 2} |
| overall | hybrid_rerank | faithfulness | 0.9821428571428571 / n=7 | {"rewrite_error": 2, "zero_claims": 1} |
| overall | hybrid_rerank | absent_refusal_rate | 1.0 / n=2 | {"answerable": 8} |
| overall | hybrid_rerank | answerable_false_refusal_rate | 0.0 / n=6 | {"expected_refusal": 2, "rewrite_error": 2} |
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
| A_policy | bm25 | answer_point_coverage | 0.5 / n=2 | {} |
| A_policy | bm25 | faithfulness | 1.0 / n=1 | {"zero_claims": 1} |
| A_policy | bm25 | absent_refusal_rate | N/A / n=0 | {"answerable": 2} |
| A_policy | bm25 | answerable_false_refusal_rate | 0.5 / n=2 | {} |
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
| A_policy | hybrid_rerank | faithfulness | 0.9375 / n=2 | {} |
| A_policy | hybrid_rerank | absent_refusal_rate | N/A / n=0 | {"answerable": 2} |
| A_policy | hybrid_rerank | answerable_false_refusal_rate | 0.0 / n=2 | {} |
| B_model | dense | recall_at_5 | 1.0 / n=1 | {"rewrite_error": 1} |
| B_model | dense | recall_at_10 | 1.0 / n=1 | {"rewrite_error": 1} |
| B_model | dense | mrr_at_10 | 1.0 / n=1 | {"rewrite_error": 1} |
| B_model | dense | all_groups_hit_at_5 | 1.0 / n=1 | {"rewrite_error": 1} |
| B_model | dense | all_groups_hit_at_10 | 1.0 / n=1 | {"rewrite_error": 1} |
| B_model | dense | candidate_group_coverage | 1.0 / n=1 | {"rewrite_error": 1} |
| B_model | dense | prompt_group_coverage | 1.0 / n=1 | {"rewrite_error": 1} |
| B_model | dense | answer_point_coverage | 1.0 / n=1 | {"rewrite_error": 1} |
| B_model | dense | faithfulness | 1.0 / n=1 | {"rewrite_error": 1} |
| B_model | dense | absent_refusal_rate | N/A / n=0 | {"answerable": 2} |
| B_model | dense | answerable_false_refusal_rate | 0.0 / n=1 | {"rewrite_error": 1} |
| B_model | bm25 | recall_at_5 | 1.0 / n=1 | {"rewrite_error": 1} |
| B_model | bm25 | recall_at_10 | 1.0 / n=1 | {"rewrite_error": 1} |
| B_model | bm25 | mrr_at_10 | 1.0 / n=1 | {"rewrite_error": 1} |
| B_model | bm25 | all_groups_hit_at_5 | 1.0 / n=1 | {"rewrite_error": 1} |
| B_model | bm25 | all_groups_hit_at_10 | 1.0 / n=1 | {"rewrite_error": 1} |
| B_model | bm25 | candidate_group_coverage | 1.0 / n=1 | {"rewrite_error": 1} |
| B_model | bm25 | prompt_group_coverage | 1.0 / n=1 | {"rewrite_error": 1} |
| B_model | bm25 | answer_point_coverage | 1.0 / n=1 | {"rewrite_error": 1} |
| B_model | bm25 | faithfulness | 1.0 / n=1 | {"rewrite_error": 1} |
| B_model | bm25 | absent_refusal_rate | N/A / n=0 | {"answerable": 2} |
| B_model | bm25 | answerable_false_refusal_rate | 0.0 / n=1 | {"rewrite_error": 1} |
| B_model | hybrid | recall_at_5 | 1.0 / n=1 | {"rewrite_error": 1} |
| B_model | hybrid | recall_at_10 | 1.0 / n=1 | {"rewrite_error": 1} |
| B_model | hybrid | mrr_at_10 | 1.0 / n=1 | {"rewrite_error": 1} |
| B_model | hybrid | all_groups_hit_at_5 | 1.0 / n=1 | {"rewrite_error": 1} |
| B_model | hybrid | all_groups_hit_at_10 | 1.0 / n=1 | {"rewrite_error": 1} |
| B_model | hybrid | candidate_group_coverage | 1.0 / n=1 | {"rewrite_error": 1} |
| B_model | hybrid | prompt_group_coverage | 1.0 / n=1 | {"rewrite_error": 1} |
| B_model | hybrid | answer_point_coverage | 1.0 / n=1 | {"rewrite_error": 1} |
| B_model | hybrid | faithfulness | 1.0 / n=1 | {"rewrite_error": 1} |
| B_model | hybrid | absent_refusal_rate | N/A / n=0 | {"answerable": 2} |
| B_model | hybrid | answerable_false_refusal_rate | 0.0 / n=1 | {"rewrite_error": 1} |
| B_model | hybrid_rerank | recall_at_5 | 1.0 / n=1 | {"rewrite_error": 1} |
| B_model | hybrid_rerank | recall_at_10 | 1.0 / n=1 | {"rewrite_error": 1} |
| B_model | hybrid_rerank | mrr_at_10 | 1.0 / n=1 | {"rewrite_error": 1} |
| B_model | hybrid_rerank | all_groups_hit_at_5 | 1.0 / n=1 | {"rewrite_error": 1} |
| B_model | hybrid_rerank | all_groups_hit_at_10 | 1.0 / n=1 | {"rewrite_error": 1} |
| B_model | hybrid_rerank | candidate_group_coverage | 1.0 / n=1 | {"rewrite_error": 1} |
| B_model | hybrid_rerank | prompt_group_coverage | 1.0 / n=1 | {"rewrite_error": 1} |
| B_model | hybrid_rerank | answer_point_coverage | 1.0 / n=1 | {"rewrite_error": 1} |
| B_model | hybrid_rerank | faithfulness | 1.0 / n=1 | {"rewrite_error": 1} |
| B_model | hybrid_rerank | absent_refusal_rate | N/A / n=0 | {"answerable": 2} |
| B_model | hybrid_rerank | answerable_false_refusal_rate | 0.0 / n=1 | {"rewrite_error": 1} |
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
| C_colloquial | hybrid | faithfulness | 0.8 / n=2 | {} |
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
| D_unanswerable | dense | faithfulness | 0.0 / n=1 | {"zero_claims": 1} |
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
| D_unanswerable | hybrid | faithfulness | 0.0 / n=2 | {} |
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
| D_unanswerable | hybrid_rerank | faithfulness | 1.0 / n=1 | {"zero_claims": 1} |
| D_unanswerable | hybrid_rerank | absent_refusal_rate | 1.0 / n=2 | {} |
| D_unanswerable | hybrid_rerank | answerable_false_refusal_rate | N/A / n=0 | {"expected_refusal": 2} |
| E_multi | dense | recall_at_5 | 1.0 / n=1 | {"rewrite_error": 1} |
| E_multi | dense | recall_at_10 | 1.0 / n=1 | {"rewrite_error": 1} |
| E_multi | dense | mrr_at_10 | 1.0 / n=1 | {"rewrite_error": 1} |
| E_multi | dense | all_groups_hit_at_5 | 1.0 / n=1 | {"rewrite_error": 1} |
| E_multi | dense | all_groups_hit_at_10 | 1.0 / n=1 | {"rewrite_error": 1} |
| E_multi | dense | candidate_group_coverage | 1.0 / n=1 | {"rewrite_error": 1} |
| E_multi | dense | prompt_group_coverage | 1.0 / n=1 | {"rewrite_error": 1} |
| E_multi | dense | answer_point_coverage | 1.0 / n=1 | {"rewrite_error": 1} |
| E_multi | dense | faithfulness | 1.0 / n=1 | {"rewrite_error": 1} |
| E_multi | dense | absent_refusal_rate | N/A / n=0 | {"answerable": 2} |
| E_multi | dense | answerable_false_refusal_rate | 0.0 / n=1 | {"rewrite_error": 1} |
| E_multi | bm25 | recall_at_5 | 0.3333333333333333 / n=1 | {"rewrite_error": 1} |
| E_multi | bm25 | recall_at_10 | 0.6666666666666666 / n=1 | {"rewrite_error": 1} |
| E_multi | bm25 | mrr_at_10 | 1.0 / n=1 | {"rewrite_error": 1} |
| E_multi | bm25 | all_groups_hit_at_5 | 0.0 / n=1 | {"rewrite_error": 1} |
| E_multi | bm25 | all_groups_hit_at_10 | 0.0 / n=1 | {"rewrite_error": 1} |
| E_multi | bm25 | candidate_group_coverage | 1.0 / n=1 | {"rewrite_error": 1} |
| E_multi | bm25 | prompt_group_coverage | 0.6666666666666666 / n=1 | {"rewrite_error": 1} |
| E_multi | bm25 | answer_point_coverage | 0.0 / n=1 | {"rewrite_error": 1} |
| E_multi | bm25 | faithfulness | N/A / n=0 | {"rewrite_error": 1, "zero_claims": 1} |
| E_multi | bm25 | absent_refusal_rate | N/A / n=0 | {"answerable": 2} |
| E_multi | bm25 | answerable_false_refusal_rate | 1.0 / n=1 | {"rewrite_error": 1} |
| E_multi | hybrid | recall_at_5 | 0.6666666666666666 / n=1 | {"rewrite_error": 1} |
| E_multi | hybrid | recall_at_10 | 1.0 / n=1 | {"rewrite_error": 1} |
| E_multi | hybrid | mrr_at_10 | 1.0 / n=1 | {"rewrite_error": 1} |
| E_multi | hybrid | all_groups_hit_at_5 | 0.0 / n=1 | {"rewrite_error": 1} |
| E_multi | hybrid | all_groups_hit_at_10 | 1.0 / n=1 | {"rewrite_error": 1} |
| E_multi | hybrid | candidate_group_coverage | 1.0 / n=1 | {"rewrite_error": 1} |
| E_multi | hybrid | prompt_group_coverage | 1.0 / n=1 | {"rewrite_error": 1} |
| E_multi | hybrid | answer_point_coverage | 1.0 / n=1 | {"rewrite_error": 1} |
| E_multi | hybrid | faithfulness | 1.0 / n=1 | {"rewrite_error": 1} |
| E_multi | hybrid | absent_refusal_rate | N/A / n=0 | {"answerable": 2} |
| E_multi | hybrid | answerable_false_refusal_rate | 0.0 / n=1 | {"rewrite_error": 1} |
| E_multi | hybrid_rerank | recall_at_5 | 1.0 / n=1 | {"rewrite_error": 1} |
| E_multi | hybrid_rerank | recall_at_10 | 1.0 / n=1 | {"rewrite_error": 1} |
| E_multi | hybrid_rerank | mrr_at_10 | 1.0 / n=1 | {"rewrite_error": 1} |
| E_multi | hybrid_rerank | all_groups_hit_at_5 | 1.0 / n=1 | {"rewrite_error": 1} |
| E_multi | hybrid_rerank | all_groups_hit_at_10 | 1.0 / n=1 | {"rewrite_error": 1} |
| E_multi | hybrid_rerank | candidate_group_coverage | 1.0 / n=1 | {"rewrite_error": 1} |
| E_multi | hybrid_rerank | prompt_group_coverage | 1.0 / n=1 | {"rewrite_error": 1} |
| E_multi | hybrid_rerank | answer_point_coverage | 0.6666666666666666 / n=1 | {"rewrite_error": 1} |
| E_multi | hybrid_rerank | faithfulness | 1.0 / n=1 | {"rewrite_error": 1} |
| E_multi | hybrid_rerank | absent_refusal_rate | N/A / n=0 | {"answerable": 2} |
| E_multi | hybrid_rerank | answerable_false_refusal_rate | 0.0 / n=1 | {"rewrite_error": 1} |

排名证据（B3/C35/C5/E2）逐组candidate/final位置与Prompt是否保留见analysis JSON。B54/E19无合法改写/检索，不捏造排名。资源只变更质量台账，全部精确合法upsert/外来行保持/业务摘要见resource-proof；full GET matching_pilot=false，available_scopes仅pilot。
