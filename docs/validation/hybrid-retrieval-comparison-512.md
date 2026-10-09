# 混合检索评估

运行类型：actual；模式：compare；通过：False。

hybrid_rerank 额外使用冻结重排门槛，其他三策略仅内容自评；生成变化不能全部归因于排序。

已尝试 0；未执行 120；错误 0；改写错误 0。
清理：owned_temporary_resources_removed_ledger_preserved。裁判版本：faithfulness-v1；拒答无断言的忠实度为 n/a。

各指标显示均值 / 有效分母；具体错误和未执行行见同名 JSON。

| 桶 | 策略 | 完成/总数 | 错误/未执行 | Recall10 | Recall50 | MRR10 | Prompt覆盖 | Faithfulness | 无答案拒答率 |
|---|---|---|---|---|---|---|---|---|---|
| overall | dense | 0/30 | 0/30 | n/a / 0 | n/a / 0 | n/a / 0 | n/a / 0 | n/a / 0 | n/a / 0 |
| overall | bm25 | 0/30 | 0/30 | n/a / 0 | n/a / 0 | n/a / 0 | n/a / 0 | n/a / 0 | n/a / 0 |
| overall | hybrid | 0/30 | 0/30 | n/a / 0 | n/a / 0 | n/a / 0 | n/a / 0 | n/a / 0 | n/a / 0 |
| overall | hybrid_rerank | 0/30 | 0/30 | n/a / 0 | n/a / 0 | n/a / 0 | n/a / 0 | n/a / 0 | n/a / 0 |
| A_policy | dense | 0/6 | 0/6 | n/a / 0 | n/a / 0 | n/a / 0 | n/a / 0 | n/a / 0 | n/a / 0 |
| A_policy | bm25 | 0/6 | 0/6 | n/a / 0 | n/a / 0 | n/a / 0 | n/a / 0 | n/a / 0 | n/a / 0 |
| A_policy | hybrid | 0/6 | 0/6 | n/a / 0 | n/a / 0 | n/a / 0 | n/a / 0 | n/a / 0 | n/a / 0 |
| A_policy | hybrid_rerank | 0/6 | 0/6 | n/a / 0 | n/a / 0 | n/a / 0 | n/a / 0 | n/a / 0 | n/a / 0 |
| B_model | dense | 0/6 | 0/6 | n/a / 0 | n/a / 0 | n/a / 0 | n/a / 0 | n/a / 0 | n/a / 0 |
| B_model | bm25 | 0/6 | 0/6 | n/a / 0 | n/a / 0 | n/a / 0 | n/a / 0 | n/a / 0 | n/a / 0 |
| B_model | hybrid | 0/6 | 0/6 | n/a / 0 | n/a / 0 | n/a / 0 | n/a / 0 | n/a / 0 | n/a / 0 |
| B_model | hybrid_rerank | 0/6 | 0/6 | n/a / 0 | n/a / 0 | n/a / 0 | n/a / 0 | n/a / 0 | n/a / 0 |
| C_colloquial | dense | 0/6 | 0/6 | n/a / 0 | n/a / 0 | n/a / 0 | n/a / 0 | n/a / 0 | n/a / 0 |
| C_colloquial | bm25 | 0/6 | 0/6 | n/a / 0 | n/a / 0 | n/a / 0 | n/a / 0 | n/a / 0 | n/a / 0 |
| C_colloquial | hybrid | 0/6 | 0/6 | n/a / 0 | n/a / 0 | n/a / 0 | n/a / 0 | n/a / 0 | n/a / 0 |
| C_colloquial | hybrid_rerank | 0/6 | 0/6 | n/a / 0 | n/a / 0 | n/a / 0 | n/a / 0 | n/a / 0 | n/a / 0 |
| D_unanswerable | dense | 0/6 | 0/6 | n/a / 0 | n/a / 0 | n/a / 0 | n/a / 0 | n/a / 0 | n/a / 0 |
| D_unanswerable | bm25 | 0/6 | 0/6 | n/a / 0 | n/a / 0 | n/a / 0 | n/a / 0 | n/a / 0 | n/a / 0 |
| D_unanswerable | hybrid | 0/6 | 0/6 | n/a / 0 | n/a / 0 | n/a / 0 | n/a / 0 | n/a / 0 | n/a / 0 |
| D_unanswerable | hybrid_rerank | 0/6 | 0/6 | n/a / 0 | n/a / 0 | n/a / 0 | n/a / 0 | n/a / 0 | n/a / 0 |
| E_multi | dense | 0/6 | 0/6 | n/a / 0 | n/a / 0 | n/a / 0 | n/a / 0 | n/a / 0 | n/a / 0 |
| E_multi | bm25 | 0/6 | 0/6 | n/a / 0 | n/a / 0 | n/a / 0 | n/a / 0 | n/a / 0 | n/a / 0 |
| E_multi | hybrid | 0/6 | 0/6 | n/a / 0 | n/a / 0 | n/a / 0 | n/a / 0 | n/a / 0 | n/a / 0 |
| E_multi | hybrid_rerank | 0/6 | 0/6 | n/a / 0 | n/a / 0 | n/a / 0 | n/a / 0 | n/a / 0 | n/a / 0 |
