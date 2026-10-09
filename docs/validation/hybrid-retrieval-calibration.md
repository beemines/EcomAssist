# 混合检索评估

运行类型：actual；模式：calibrate；通过：True。

hybrid_rerank 额外使用冻结重排门槛，其他三策略仅内容自评；生成变化不能全部归因于排序。

已尝试 8；未执行 0；错误 0；改写错误 0。
清理：owned_temporary_resources_removed_ledger_preserved。裁判版本：faithfulness-v1；拒答无断言的忠实度为 n/a。

```json
{
  "threshold": 0.8201608061790466,
  "refusal_f1": 1.0,
  "confusion": {
    "tp": 4,
    "fp": 0,
    "fn": 0,
    "tn": 4
  },
  "samples": 8,
  "candidates": [
    {
      "threshold": 0.165904700756073,
      "refusal_f1": 0.0,
      "confusion": {
        "tp": 0,
        "fp": 0,
        "fn": 4,
        "tn": 4
      }
    },
    {
      "threshold": 0.24131107330322266,
      "refusal_f1": 0.4,
      "confusion": {
        "tp": 1,
        "fp": 0,
        "fn": 3,
        "tn": 4
      }
    },
    {
      "threshold": 0.24626420438289642,
      "refusal_f1": 0.6666666666666666,
      "confusion": {
        "tp": 2,
        "fp": 0,
        "fn": 2,
        "tn": 4
      }
    },
    {
      "threshold": 0.25693240761756897,
      "refusal_f1": 0.8571428571428571,
      "confusion": {
        "tp": 3,
        "fp": 0,
        "fn": 1,
        "tn": 4
      }
    },
    {
      "threshold": 0.8201608061790466,
      "refusal_f1": 1.0,
      "confusion": {
        "tp": 4,
        "fp": 0,
        "fn": 0,
        "tn": 4
      }
    },
    {
      "threshold": 0.995098888874054,
      "refusal_f1": 0.8888888888888888,
      "confusion": {
        "tp": 4,
        "fp": 1,
        "fn": 0,
        "tn": 3
      }
    },
    {
      "threshold": 0.9951274394989014,
      "refusal_f1": 0.8,
      "confusion": {
        "tp": 4,
        "fp": 2,
        "fn": 0,
        "tn": 2
      }
    },
    {
      "threshold": 0.9968904852867126,
      "refusal_f1": 0.7272727272727273,
      "confusion": {
        "tp": 4,
        "fp": 3,
        "fn": 0,
        "tn": 1
      }
    }
  ],
  "method": "observed scores; refusal positive; score < threshold; ties choose higher threshold"
}
```

各指标显示均值 / 有效分母；具体错误和未执行行见同名 JSON。

| 桶 | 策略 | 完成/总数 | 错误/未执行 | Recall10 | Recall50 | MRR10 | Prompt覆盖 | Faithfulness | 无答案拒答率 |
|---|---|---|---|---|---|---|---|---|---|
| overall | dense | 0/0 | 0/0 | n/a / 0 | n/a / 0 | n/a / 0 | n/a / 0 | n/a / 0 | n/a / 0 |
| overall | bm25 | 0/0 | 0/0 | n/a / 0 | n/a / 0 | n/a / 0 | n/a / 0 | n/a / 0 | n/a / 0 |
| overall | hybrid | 0/0 | 0/0 | n/a / 0 | n/a / 0 | n/a / 0 | n/a / 0 | n/a / 0 | n/a / 0 |
| overall | hybrid_rerank | 8/8 | 0/0 | n/a / 0 | n/a / 0 | n/a / 0 | n/a / 0 | n/a / 0 | n/a / 0 |
| A_policy | dense | 0/0 | 0/0 | n/a / 0 | n/a / 0 | n/a / 0 | n/a / 0 | n/a / 0 | n/a / 0 |
| A_policy | bm25 | 0/0 | 0/0 | n/a / 0 | n/a / 0 | n/a / 0 | n/a / 0 | n/a / 0 | n/a / 0 |
| A_policy | hybrid | 0/0 | 0/0 | n/a / 0 | n/a / 0 | n/a / 0 | n/a / 0 | n/a / 0 | n/a / 0 |
| A_policy | hybrid_rerank | 0/0 | 0/0 | n/a / 0 | n/a / 0 | n/a / 0 | n/a / 0 | n/a / 0 | n/a / 0 |
| B_model | dense | 0/0 | 0/0 | n/a / 0 | n/a / 0 | n/a / 0 | n/a / 0 | n/a / 0 | n/a / 0 |
| B_model | bm25 | 0/0 | 0/0 | n/a / 0 | n/a / 0 | n/a / 0 | n/a / 0 | n/a / 0 | n/a / 0 |
| B_model | hybrid | 0/0 | 0/0 | n/a / 0 | n/a / 0 | n/a / 0 | n/a / 0 | n/a / 0 | n/a / 0 |
| B_model | hybrid_rerank | 0/0 | 0/0 | n/a / 0 | n/a / 0 | n/a / 0 | n/a / 0 | n/a / 0 | n/a / 0 |
| C_colloquial | dense | 0/0 | 0/0 | n/a / 0 | n/a / 0 | n/a / 0 | n/a / 0 | n/a / 0 | n/a / 0 |
| C_colloquial | bm25 | 0/0 | 0/0 | n/a / 0 | n/a / 0 | n/a / 0 | n/a / 0 | n/a / 0 | n/a / 0 |
| C_colloquial | hybrid | 0/0 | 0/0 | n/a / 0 | n/a / 0 | n/a / 0 | n/a / 0 | n/a / 0 | n/a / 0 |
| C_colloquial | hybrid_rerank | 0/0 | 0/0 | n/a / 0 | n/a / 0 | n/a / 0 | n/a / 0 | n/a / 0 | n/a / 0 |
| D_unanswerable | dense | 0/0 | 0/0 | n/a / 0 | n/a / 0 | n/a / 0 | n/a / 0 | n/a / 0 | n/a / 0 |
| D_unanswerable | bm25 | 0/0 | 0/0 | n/a / 0 | n/a / 0 | n/a / 0 | n/a / 0 | n/a / 0 | n/a / 0 |
| D_unanswerable | hybrid | 0/0 | 0/0 | n/a / 0 | n/a / 0 | n/a / 0 | n/a / 0 | n/a / 0 | n/a / 0 |
| D_unanswerable | hybrid_rerank | 0/0 | 0/0 | n/a / 0 | n/a / 0 | n/a / 0 | n/a / 0 | n/a / 0 | n/a / 0 |
| E_multi | dense | 0/0 | 0/0 | n/a / 0 | n/a / 0 | n/a / 0 | n/a / 0 | n/a / 0 | n/a / 0 |
| E_multi | bm25 | 0/0 | 0/0 | n/a / 0 | n/a / 0 | n/a / 0 | n/a / 0 | n/a / 0 | n/a / 0 |
| E_multi | hybrid | 0/0 | 0/0 | n/a / 0 | n/a / 0 | n/a / 0 | n/a / 0 | n/a / 0 | n/a / 0 |
| E_multi | hybrid_rerank | 0/0 | 0/0 | n/a / 0 | n/a / 0 | n/a / 0 | n/a / 0 | n/a / 0 | n/a / 0 |
