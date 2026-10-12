# RAG 300题合并比较（历史运行与补跑）

本报告由两次运行按整题四策略合并，并非单一连续运行。每题四路共用本题原生source-map；未重写物理ID或分数。

历史运行 `2486afc8e62e4550bdfec6d676a27d84` 保留 158 题；并发2。
补跑 `7adfc4c7dc3a4750885c23c94f3be671` 选择 142 题；辅助方法并发8，冻结配置预算仍为2且配置逐值完全相同。
为同题来源一致，重复评估原已完成 2 条；原6条明确失败均保留且未重试。

完整最终回答、排序、裁判及来源原文见 [历史中断JSON](merchant-rag-interrupted.json)、[历史Markdown](merchant-rag-interrupted.md)、[补跑JSON](merchant-rag-completion-remainder.json)、[补跑Markdown](merchant-rag-completion-remainder.md)。

合并JSON包含1200条原始公开记录和完整生产summary，50块原文仅在两份原生报告保存。

## 各桶及整体（数值 / 有效n）

| 桶 | 策略 | MRR@10 | Recall@10 | Recall@5 | 要点覆盖 | 忠实度 | 库外拒答率 | 可答误拒率 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| overall | dense | 0.9367 / 239 | 0.9979 / 239 | 0.9763 / 239 | 0.9240 / 239 | 0.9378 / 267 | 0.9667 / 60 | 0.0251 / 239 |
| overall | bm25 | 0.8819 / 240 | 0.9424 / 240 | 0.9097 / 240 | 0.8927 / 236 | 0.9571 / 242 | 0.9833 / 60 | 0.0763 / 236 |
| overall | hybrid | 0.9277 / 239 | 0.9770 / 239 | 0.9596 / 239 | 0.9191 / 237 | 0.9420 / 260 | 0.9667 / 60 | 0.0380 / 237 |
| overall | hybrid_rerank | 0.9826 / 240 | 0.9958 / 240 | 0.9924 / 240 | 0.9413 / 237 | 0.9642 / 252 | 0.9667 / 60 | 0.0210 / 238 |
| A_policy | dense | 0.9444 / 60 | 1.0000 / 60 | 1.0000 / 60 | 0.9333 / 60 | 0.9789 / 58 | N/A / 0 | 0.0333 / 60 |
| A_policy | bm25 | 0.9514 / 60 | 1.0000 / 60 | 0.9917 / 60 | 0.9667 / 60 | 0.9811 / 59 | N/A / 0 | 0.0167 / 60 |
| A_policy | hybrid | 0.9708 / 60 | 1.0000 / 60 | 1.0000 / 60 | 0.9250 / 60 | 0.9826 / 59 | N/A / 0 | 0.0167 / 60 |
| A_policy | hybrid_rerank | 0.9833 / 60 | 1.0000 / 60 | 1.0000 / 60 | 0.9194 / 60 | 0.9822 / 58 | N/A / 0 | 0.0333 / 60 |
| B_model | dense | 0.9339 / 60 | 1.0000 / 60 | 1.0000 / 60 | 0.9917 / 60 | 0.9861 / 60 | N/A / 0 | 0.0000 / 60 |
| B_model | bm25 | 0.9889 / 60 | 1.0000 / 60 | 1.0000 / 60 | 1.0000 / 59 | 0.9944 / 59 | N/A / 0 | 0.0000 / 59 |
| B_model | hybrid | 0.9806 / 60 | 1.0000 / 60 | 1.0000 / 60 | 1.0000 / 60 | 0.9921 / 60 | N/A / 0 | 0.0000 / 60 |
| B_model | hybrid_rerank | 1.0000 / 60 | 1.0000 / 60 | 1.0000 / 60 | 0.9833 / 60 | 0.9981 / 59 | N/A / 0 | 0.0167 / 60 |
| C_colloquial | dense | 0.9181 / 59 | 1.0000 / 59 | 1.0000 / 59 | 0.8814 / 59 | 0.9652 / 57 | N/A / 0 | 0.0339 / 59 |
| C_colloquial | bm25 | 0.6317 / 60 | 0.8333 / 60 | 0.7917 / 60 | 0.7797 / 59 | 0.9376 / 49 | N/A / 0 | 0.1864 / 59 |
| C_colloquial | hybrid | 0.7820 / 59 | 0.9492 / 59 | 0.9153 / 59 | 0.8621 / 58 | 0.9386 / 55 | N/A / 0 | 0.0690 / 58 |
| C_colloquial | hybrid_rerank | 0.9639 / 60 | 1.0000 / 60 | 1.0000 / 60 | 0.9612 / 58 | 0.9606 / 57 | N/A / 0 | 0.0172 / 58 |
| D_unanswerable | dense | N/A / 0 | N/A / 0 | N/A / 0 | N/A / 0 | 0.7010 / 34 | 0.9667 / 60 | N/A / 0 |
| D_unanswerable | bm25 | N/A / 0 | N/A / 0 | N/A / 0 | N/A / 0 | 0.8333 / 22 | 0.9833 / 60 | N/A / 0 |
| D_unanswerable | hybrid | N/A / 0 | N/A / 0 | N/A / 0 | N/A / 0 | 0.7639 / 30 | 0.9667 / 60 | N/A / 0 |
| D_unanswerable | hybrid_rerank | N/A / 0 | N/A / 0 | N/A / 0 | N/A / 0 | 0.8608 / 20 | 0.9667 / 60 | N/A / 0 |
| E_multi | dense | 0.9500 / 60 | 0.9917 / 60 | 0.9056 / 60 | 0.8889 / 60 | 0.9588 / 58 | N/A / 0 | 0.0333 / 60 |
| E_multi | bm25 | 0.9556 / 60 | 0.9361 / 60 | 0.8556 / 60 | 0.8218 / 58 | 0.9582 / 53 | N/A / 0 | 0.1034 / 58 |
| E_multi | hybrid | 0.9750 / 60 | 0.9583 / 60 | 0.9222 / 60 | 0.8870 / 59 | 0.9444 / 56 | N/A / 0 | 0.0678 / 59 |
| E_multi | hybrid_rerank | 0.9833 / 60 | 0.9833 / 60 | 0.9694 / 60 | 0.9011 / 59 | 0.9507 / 58 | N/A / 0 | 0.0167 / 60 |

## 状态、共同题集及改写统计

```json
{
  "counts": {
    "total": 1200,
    "attempted": 1200,
    "completed": 1188,
    "errors": 12,
    "status_counts": {
      "completed": 1188,
      "rewrite_error": 0,
      "retrieval_error": 2,
      "self_check_error": 2,
      "answer_error": 6,
      "judge_error": 2,
      "cancelled": 0,
      "not_attempted": 0,
      "running": 0
    }
  },
  "errors": {
    "retained_historical": [
      {
        "eval_id": "B43",
        "strategy": "bm25",
        "status": "answer_error",
        "stage": "answer",
        "error": {
          "code": "answer_error",
          "type": "ServiceError",
          "message": "该阶段执行失败"
        }
      },
      {
        "eval_id": "C33",
        "strategy": "bm25",
        "status": "answer_error",
        "stage": "answer",
        "error": {
          "code": "answer_error",
          "type": "ServiceError",
          "message": "该阶段执行失败"
        }
      },
      {
        "eval_id": "C34",
        "strategy": "hybrid_rerank",
        "status": "self_check_error",
        "stage": "self_check",
        "error": {
          "code": "self_check_error",
          "type": "ServiceError",
          "message": "该阶段执行失败"
        }
      },
      {
        "eval_id": "C35",
        "strategy": "hybrid_rerank",
        "status": "self_check_error",
        "stage": "self_check",
        "error": {
          "code": "self_check_error",
          "type": "ServiceError",
          "message": "该阶段执行失败"
        }
      },
      {
        "eval_id": "C36",
        "strategy": "hybrid",
        "status": "retrieval_error",
        "stage": "retrieval",
        "error": {
          "code": "retrieval_error",
          "type": "RemoteProtocolError",
          "message": "该阶段执行失败"
        }
      },
      {
        "eval_id": "C38",
        "strategy": "dense",
        "status": "retrieval_error",
        "stage": "retrieval",
        "error": {
          "code": "retrieval_error",
          "type": "TimeoutError",
          "message": "该阶段执行失败"
        }
      }
    ],
    "continuation": [
      {
        "eval_id": "C50",
        "strategy": "hybrid",
        "status": "answer_error",
        "stage": "answer",
        "error": {
          "code": "answer_error",
          "type": "ServiceError",
          "message": "该阶段执行失败"
        }
      },
      {
        "eval_id": "E17",
        "strategy": "bm25",
        "status": "answer_error",
        "stage": "answer",
        "error": {
          "code": "answer_error",
          "type": "ServiceError",
          "message": "该阶段执行失败"
        }
      },
      {
        "eval_id": "E17",
        "strategy": "hybrid",
        "status": "answer_error",
        "stage": "answer",
        "error": {
          "code": "answer_error",
          "type": "ServiceError",
          "message": "该阶段执行失败"
        }
      },
      {
        "eval_id": "E36",
        "strategy": "hybrid_rerank",
        "status": "judge_error",
        "stage": "judgment",
        "error": {
          "code": "judgment_error",
          "type": "JudgeError",
          "message": "该阶段执行失败"
        }
      },
      {
        "eval_id": "E48",
        "strategy": "bm25",
        "status": "answer_error",
        "stage": "answer",
        "error": {
          "code": "answer_error",
          "type": "ServiceError",
          "message": "该阶段执行失败"
        }
      },
      {
        "eval_id": "D24",
        "strategy": "hybrid_rerank",
        "status": "judge_error",
        "stage": "judgment",
        "error": {
          "code": "judgment_error",
          "type": "JudgeError",
          "message": "该阶段执行失败"
        }
      }
    ]
  },
  "rewrite": {
    "attempted_n": 300,
    "success_n": 285,
    "degraded_n": 15,
    "error_n": 0,
    "success_rate": 0.95,
    "unreported_n": 0
  },
  "common_generation": {
    "eval_ids": [
      "A1",
      "A10",
      "A11",
      "A12",
      "A13",
      "A14",
      "A15",
      "A16",
      "A17",
      "A18",
      "A19",
      "A2",
      "A20",
      "A21",
      "A22",
      "A23",
      "A24",
      "A25",
      "A26",
      "A27",
      "A28",
      "A29",
      "A3",
      "A30",
      "A31",
      "A32",
      "A33",
      "A34",
      "A35",
      "A36",
      "A37",
      "A38",
      "A39",
      "A4",
      "A40",
      "A41",
      "A42",
      "A43",
      "A44",
      "A45",
      "A46",
      "A47",
      "A48",
      "A49",
      "A5",
      "A50",
      "A51",
      "A52",
      "A53",
      "A54",
      "A55",
      "A56",
      "A57",
      "A58",
      "A59",
      "A6",
      "A60",
      "A7",
      "A8",
      "A9",
      "B1",
      "B10",
      "B11",
      "B12",
      "B13",
      "B14",
      "B15",
      "B16",
      "B17",
      "B18",
      "B19",
      "B2",
      "B20",
      "B21",
      "B22",
      "B23",
      "B24",
      "B25",
      "B26",
      "B27",
      "B28",
      "B29",
      "B3",
      "B30",
      "B31",
      "B32",
      "B33",
      "B34",
      "B35",
      "B36",
      "B37",
      "B38",
      "B39",
      "B4",
      "B40",
      "B41",
      "B42",
      "B44",
      "B45",
      "B46",
      "B47",
      "B48",
      "B49",
      "B5",
      "B50",
      "B51",
      "B52",
      "B53",
      "B54",
      "B55",
      "B56",
      "B57",
      "B58",
      "B59",
      "B6",
      "B60",
      "B7",
      "B8",
      "B9",
      "C1",
      "C10",
      "C11",
      "C12",
      "C13",
      "C14",
      "C15",
      "C16",
      "C17",
      "C18",
      "C19",
      "C2",
      "C20",
      "C21",
      "C22",
      "C23",
      "C24",
      "C25",
      "C26",
      "C27",
      "C28",
      "C29",
      "C3",
      "C30",
      "C31",
      "C32",
      "C37",
      "C39",
      "C4",
      "C40",
      "C41",
      "C42",
      "C43",
      "C44",
      "C45",
      "C46",
      "C47",
      "C48",
      "C49",
      "C5",
      "C51",
      "C52",
      "C53",
      "C54",
      "C55",
      "C56",
      "C57",
      "C58",
      "C59",
      "C6",
      "C60",
      "C7",
      "C8",
      "C9",
      "D1",
      "D10",
      "D11",
      "D12",
      "D13",
      "D14",
      "D15",
      "D16",
      "D17",
      "D18",
      "D19",
      "D2",
      "D20",
      "D21",
      "D22",
      "D23",
      "D25",
      "D26",
      "D27",
      "D28",
      "D29",
      "D3",
      "D30",
      "D31",
      "D32",
      "D33",
      "D34",
      "D35",
      "D36",
      "D37",
      "D38",
      "D39",
      "D4",
      "D40",
      "D41",
      "D42",
      "D43",
      "D44",
      "D45",
      "D46",
      "D47",
      "D48",
      "D49",
      "D5",
      "D50",
      "D51",
      "D52",
      "D53",
      "D54",
      "D55",
      "D56",
      "D57",
      "D58",
      "D59",
      "D6",
      "D60",
      "D7",
      "D8",
      "D9",
      "E1",
      "E10",
      "E11",
      "E12",
      "E13",
      "E14",
      "E15",
      "E16",
      "E18",
      "E19",
      "E2",
      "E20",
      "E21",
      "E22",
      "E23",
      "E24",
      "E25",
      "E26",
      "E27",
      "E28",
      "E29",
      "E3",
      "E30",
      "E31",
      "E32",
      "E33",
      "E34",
      "E35",
      "E37",
      "E38",
      "E39",
      "E4",
      "E40",
      "E41",
      "E42",
      "E43",
      "E44",
      "E45",
      "E46",
      "E47",
      "E49",
      "E5",
      "E50",
      "E51",
      "E52",
      "E53",
      "E54",
      "E55",
      "E56",
      "E57",
      "E58",
      "E59",
      "E6",
      "E60",
      "E7",
      "E8",
      "E9"
    ],
    "valid_n": 289,
    "rows": [
      {
        "bucket": "overall",
        "strategy": "dense",
        "total": 289,
        "attempted": 289,
        "completed": 289,
        "errors": 0,
        "not_attempted": 0,
        "status_counts": {
          "completed": 289,
          "rewrite_error": 0,
          "retrieval_error": 0,
          "self_check_error": 0,
          "answer_error": 0,
          "judge_error": 0,
          "cancelled": 0,
          "not_attempted": 0,
          "running": 0
        },
        "metrics": {
          "recall_at_5": {
            "value": 0.9753623188405798,
            "valid_n": 230,
            "excluded": {
              "expected_refusal": 59
            }
          },
          "recall_at_10": {
            "value": 0.9978260869565218,
            "valid_n": 230,
            "excluded": {
              "expected_refusal": 59
            }
          },
          "mrr_at_10": {
            "value": 0.9342028985507247,
            "valid_n": 230,
            "excluded": {
              "expected_refusal": 59
            }
          },
          "all_groups_hit_at_5": {
            "value": 0.9478260869565217,
            "valid_n": 230,
            "excluded": {
              "expected_refusal": 59
            }
          },
          "all_groups_hit_at_10": {
            "value": 0.9956521739130435,
            "valid_n": 230,
            "excluded": {
              "expected_refusal": 59
            }
          },
          "candidate_group_coverage": {
            "value": 1.0,
            "valid_n": 230,
            "excluded": {
              "expected_refusal": 59
            }
          },
          "prompt_group_coverage": {
            "value": 0.9978260869565218,
            "valid_n": 230,
            "excluded": {
              "expected_refusal": 59
            }
          },
          "answer_point_coverage": {
            "value": 0.9210144927536232,
            "valid_n": 230,
            "excluded": {
              "expected_refusal": 59
            }
          },
          "faithfulness": {
            "value": 0.9394293125810635,
            "valid_n": 257,
            "excluded": {
              "zero_claims": 32
            }
          },
          "absent_refusal_rate": {
            "value": 0.9661016949152542,
            "valid_n": 59,
            "excluded": {
              "answerable": 230
            }
          },
          "answerable_false_refusal_rate": {
            "value": 0.02608695652173913,
            "valid_n": 230,
            "excluded": {
              "expected_refusal": 59
            }
          }
        }
      },
      {
        "bucket": "overall",
        "strategy": "bm25",
        "total": 289,
        "attempted": 289,
        "completed": 289,
        "errors": 0,
        "not_attempted": 0,
        "status_counts": {
          "completed": 289,
          "rewrite_error": 0,
          "retrieval_error": 0,
          "self_check_error": 0,
          "answer_error": 0,
          "judge_error": 0,
          "cancelled": 0,
          "not_attempted": 0,
          "running": 0
        },
        "metrics": {
          "recall_at_5": {
            "value": 0.9123188405797101,
            "valid_n": 230,
            "excluded": {
              "expected_refusal": 59
            }
          },
          "recall_at_10": {
            "value": 0.9463768115942028,
            "valid_n": 230,
            "excluded": {
              "expected_refusal": 59
            }
          },
          "mrr_at_10": {
            "value": 0.8896376811594203,
            "valid_n": 230,
            "excluded": {
              "expected_refusal": 59
            }
          },
          "all_groups_hit_at_5": {
            "value": 0.8695652173913043,
            "valid_n": 230,
            "excluded": {
              "expected_refusal": 59
            }
          },
          "all_groups_hit_at_10": {
            "value": 0.9304347826086956,
            "valid_n": 230,
            "excluded": {
              "expected_refusal": 59
            }
          },
          "candidate_group_coverage": {
            "value": 0.967391304347826,
            "valid_n": 230,
            "excluded": {
              "expected_refusal": 59
            }
          },
          "prompt_group_coverage": {
            "value": 0.9463768115942028,
            "valid_n": 230,
            "excluded": {
              "expected_refusal": 59
            }
          },
          "answer_point_coverage": {
            "value": 0.8942028985507245,
            "valid_n": 230,
            "excluded": {
              "expected_refusal": 59
            }
          },
          "faithfulness": {
            "value": 0.9612893462469734,
            "valid_n": 236,
            "excluded": {
              "zero_claims": 53
            }
          },
          "absent_refusal_rate": {
            "value": 0.9830508474576272,
            "valid_n": 59,
            "excluded": {
              "answerable": 230
            }
          },
          "answerable_false_refusal_rate": {
            "value": 0.07391304347826087,
            "valid_n": 230,
            "excluded": {
              "expected_refusal": 59
            }
          }
        }
      },
      {
        "bucket": "overall",
        "strategy": "hybrid",
        "total": 289,
        "attempted": 289,
        "completed": 289,
        "errors": 0,
        "not_attempted": 0,
        "status_counts": {
          "completed": 289,
          "rewrite_error": 0,
          "retrieval_error": 0,
          "self_check_error": 0,
          "answer_error": 0,
          "judge_error": 0,
          "cancelled": 0,
          "not_attempted": 0,
          "running": 0
        },
        "metrics": {
          "recall_at_5": {
            "value": 0.9601449275362319,
            "valid_n": 230,
            "excluded": {
              "expected_refusal": 59
            }
          },
          "recall_at_10": {
            "value": 0.9760869565217392,
            "valid_n": 230,
            "excluded": {
              "expected_refusal": 59
            }
          },
          "mrr_at_10": {
            "value": 0.9292270531400967,
            "valid_n": 230,
            "excluded": {
              "expected_refusal": 59
            }
          },
          "all_groups_hit_at_5": {
            "value": 0.9391304347826087,
            "valid_n": 230,
            "excluded": {
              "expected_refusal": 59
            }
          },
          "all_groups_hit_at_10": {
            "value": 0.9652173913043478,
            "valid_n": 230,
            "excluded": {
              "expected_refusal": 59
            }
          },
          "candidate_group_coverage": {
            "value": 1.0,
            "valid_n": 230,
            "excluded": {
              "expected_refusal": 59
            }
          },
          "prompt_group_coverage": {
            "value": 0.9760869565217392,
            "valid_n": 230,
            "excluded": {
              "expected_refusal": 59
            }
          },
          "answer_point_coverage": {
            "value": 0.9166666666666667,
            "valid_n": 230,
            "excluded": {
              "expected_refusal": 59
            }
          },
          "faithfulness": {
            "value": 0.9438264633916807,
            "valid_n": 253,
            "excluded": {
              "zero_claims": 36
            }
          },
          "absent_refusal_rate": {
            "value": 0.9661016949152542,
            "valid_n": 59,
            "excluded": {
              "answerable": 230
            }
          },
          "answerable_false_refusal_rate": {
            "value": 0.0391304347826087,
            "valid_n": 230,
            "excluded": {
              "expected_refusal": 59
            }
          }
        }
      },
      {
        "bucket": "overall",
        "strategy": "hybrid_rerank",
        "total": 289,
        "attempted": 289,
        "completed": 289,
        "errors": 0,
        "not_attempted": 0,
        "status_counts": {
          "completed": 289,
          "rewrite_error": 0,
          "retrieval_error": 0,
          "self_check_error": 0,
          "answer_error": 0,
          "judge_error": 0,
          "cancelled": 0,
          "not_attempted": 0,
          "running": 0
        },
        "metrics": {
          "recall_at_5": {
            "value": 0.9920289855072464,
            "valid_n": 230,
            "excluded": {
              "expected_refusal": 59
            }
          },
          "recall_at_10": {
            "value": 0.9956521739130435,
            "valid_n": 230,
            "excluded": {
              "expected_refusal": 59
            }
          },
          "mrr_at_10": {
            "value": 0.9818840579710145,
            "valid_n": 230,
            "excluded": {
              "expected_refusal": 59
            }
          },
          "all_groups_hit_at_5": {
            "value": 0.9826086956521739,
            "valid_n": 230,
            "excluded": {
              "expected_refusal": 59
            }
          },
          "all_groups_hit_at_10": {
            "value": 0.991304347826087,
            "valid_n": 230,
            "excluded": {
              "expected_refusal": 59
            }
          },
          "candidate_group_coverage": {
            "value": 1.0,
            "valid_n": 230,
            "excluded": {
              "expected_refusal": 59
            }
          },
          "prompt_group_coverage": {
            "value": 0.9956521739130435,
            "valid_n": 230,
            "excluded": {
              "expected_refusal": 59
            }
          },
          "answer_point_coverage": {
            "value": 0.9394927536231884,
            "valid_n": 230,
            "excluded": {
              "expected_refusal": 59
            }
          },
          "faithfulness": {
            "value": 0.9648782283476162,
            "valid_n": 245,
            "excluded": {
              "zero_claims": 44
            }
          },
          "absent_refusal_rate": {
            "value": 0.9661016949152542,
            "valid_n": 59,
            "excluded": {
              "answerable": 230
            }
          },
          "answerable_false_refusal_rate": {
            "value": 0.021739130434782608,
            "valid_n": 230,
            "excluded": {
              "expected_refusal": 59
            }
          }
        }
      },
      {
        "bucket": "A_policy",
        "strategy": "dense",
        "total": 60,
        "attempted": 60,
        "completed": 60,
        "errors": 0,
        "not_attempted": 0,
        "status_counts": {
          "completed": 60,
          "rewrite_error": 0,
          "retrieval_error": 0,
          "self_check_error": 0,
          "answer_error": 0,
          "judge_error": 0,
          "cancelled": 0,
          "not_attempted": 0,
          "running": 0
        },
        "metrics": {
          "recall_at_5": {
            "value": 1.0,
            "valid_n": 60,
            "excluded": {}
          },
          "recall_at_10": {
            "value": 1.0,
            "valid_n": 60,
            "excluded": {}
          },
          "mrr_at_10": {
            "value": 0.9444444444444444,
            "valid_n": 60,
            "excluded": {}
          },
          "all_groups_hit_at_5": {
            "value": 1.0,
            "valid_n": 60,
            "excluded": {}
          },
          "all_groups_hit_at_10": {
            "value": 1.0,
            "valid_n": 60,
            "excluded": {}
          },
          "candidate_group_coverage": {
            "value": 1.0,
            "valid_n": 60,
            "excluded": {}
          },
          "prompt_group_coverage": {
            "value": 1.0,
            "valid_n": 60,
            "excluded": {}
          },
          "answer_point_coverage": {
            "value": 0.9333333333333333,
            "valid_n": 60,
            "excluded": {}
          },
          "faithfulness": {
            "value": 0.9788793103448276,
            "valid_n": 58,
            "excluded": {
              "zero_claims": 2
            }
          },
          "absent_refusal_rate": {
            "value": null,
            "valid_n": 0,
            "excluded": {
              "answerable": 60
            }
          },
          "answerable_false_refusal_rate": {
            "value": 0.03333333333333333,
            "valid_n": 60,
            "excluded": {}
          }
        }
      },
      {
        "bucket": "A_policy",
        "strategy": "bm25",
        "total": 60,
        "attempted": 60,
        "completed": 60,
        "errors": 0,
        "not_attempted": 0,
        "status_counts": {
          "completed": 60,
          "rewrite_error": 0,
          "retrieval_error": 0,
          "self_check_error": 0,
          "answer_error": 0,
          "judge_error": 0,
          "cancelled": 0,
          "not_attempted": 0,
          "running": 0
        },
        "metrics": {
          "recall_at_5": {
            "value": 0.9916666666666667,
            "valid_n": 60,
            "excluded": {}
          },
          "recall_at_10": {
            "value": 1.0,
            "valid_n": 60,
            "excluded": {}
          },
          "mrr_at_10": {
            "value": 0.951388888888889,
            "valid_n": 60,
            "excluded": {}
          },
          "all_groups_hit_at_5": {
            "value": 0.9833333333333333,
            "valid_n": 60,
            "excluded": {}
          },
          "all_groups_hit_at_10": {
            "value": 1.0,
            "valid_n": 60,
            "excluded": {}
          },
          "candidate_group_coverage": {
            "value": 1.0,
            "valid_n": 60,
            "excluded": {}
          },
          "prompt_group_coverage": {
            "value": 1.0,
            "valid_n": 60,
            "excluded": {}
          },
          "answer_point_coverage": {
            "value": 0.9666666666666667,
            "valid_n": 60,
            "excluded": {}
          },
          "faithfulness": {
            "value": 0.9810734463276836,
            "valid_n": 59,
            "excluded": {
              "zero_claims": 1
            }
          },
          "absent_refusal_rate": {
            "value": null,
            "valid_n": 0,
            "excluded": {
              "answerable": 60
            }
          },
          "answerable_false_refusal_rate": {
            "value": 0.016666666666666666,
            "valid_n": 60,
            "excluded": {}
          }
        }
      },
      {
        "bucket": "A_policy",
        "strategy": "hybrid",
        "total": 60,
        "attempted": 60,
        "completed": 60,
        "errors": 0,
        "not_attempted": 0,
        "status_counts": {
          "completed": 60,
          "rewrite_error": 0,
          "retrieval_error": 0,
          "self_check_error": 0,
          "answer_error": 0,
          "judge_error": 0,
          "cancelled": 0,
          "not_attempted": 0,
          "running": 0
        },
        "metrics": {
          "recall_at_5": {
            "value": 1.0,
            "valid_n": 60,
            "excluded": {}
          },
          "recall_at_10": {
            "value": 1.0,
            "valid_n": 60,
            "excluded": {}
          },
          "mrr_at_10": {
            "value": 0.9708333333333333,
            "valid_n": 60,
            "excluded": {}
          },
          "all_groups_hit_at_5": {
            "value": 1.0,
            "valid_n": 60,
            "excluded": {}
          },
          "all_groups_hit_at_10": {
            "value": 1.0,
            "valid_n": 60,
            "excluded": {}
          },
          "candidate_group_coverage": {
            "value": 1.0,
            "valid_n": 60,
            "excluded": {}
          },
          "prompt_group_coverage": {
            "value": 1.0,
            "valid_n": 60,
            "excluded": {}
          },
          "answer_point_coverage": {
            "value": 0.925,
            "valid_n": 60,
            "excluded": {}
          },
          "faithfulness": {
            "value": 0.9825800376647834,
            "valid_n": 59,
            "excluded": {
              "zero_claims": 1
            }
          },
          "absent_refusal_rate": {
            "value": null,
            "valid_n": 0,
            "excluded": {
              "answerable": 60
            }
          },
          "answerable_false_refusal_rate": {
            "value": 0.016666666666666666,
            "valid_n": 60,
            "excluded": {}
          }
        }
      },
      {
        "bucket": "A_policy",
        "strategy": "hybrid_rerank",
        "total": 60,
        "attempted": 60,
        "completed": 60,
        "errors": 0,
        "not_attempted": 0,
        "status_counts": {
          "completed": 60,
          "rewrite_error": 0,
          "retrieval_error": 0,
          "self_check_error": 0,
          "answer_error": 0,
          "judge_error": 0,
          "cancelled": 0,
          "not_attempted": 0,
          "running": 0
        },
        "metrics": {
          "recall_at_5": {
            "value": 1.0,
            "valid_n": 60,
            "excluded": {}
          },
          "recall_at_10": {
            "value": 1.0,
            "valid_n": 60,
            "excluded": {}
          },
          "mrr_at_10": {
            "value": 0.9833333333333333,
            "valid_n": 60,
            "excluded": {}
          },
          "all_groups_hit_at_5": {
            "value": 1.0,
            "valid_n": 60,
            "excluded": {}
          },
          "all_groups_hit_at_10": {
            "value": 1.0,
            "valid_n": 60,
            "excluded": {}
          },
          "candidate_group_coverage": {
            "value": 1.0,
            "valid_n": 60,
            "excluded": {}
          },
          "prompt_group_coverage": {
            "value": 1.0,
            "valid_n": 60,
            "excluded": {}
          },
          "answer_point_coverage": {
            "value": 0.9194444444444444,
            "valid_n": 60,
            "excluded": {}
          },
          "faithfulness": {
            "value": 0.982183908045977,
            "valid_n": 58,
            "excluded": {
              "zero_claims": 2
            }
          },
          "absent_refusal_rate": {
            "value": null,
            "valid_n": 0,
            "excluded": {
              "answerable": 60
            }
          },
          "answerable_false_refusal_rate": {
            "value": 0.03333333333333333,
            "valid_n": 60,
            "excluded": {}
          }
        }
      },
      {
        "bucket": "B_model",
        "strategy": "dense",
        "total": 59,
        "attempted": 59,
        "completed": 59,
        "errors": 0,
        "not_attempted": 0,
        "status_counts": {
          "completed": 59,
          "rewrite_error": 0,
          "retrieval_error": 0,
          "self_check_error": 0,
          "answer_error": 0,
          "judge_error": 0,
          "cancelled": 0,
          "not_attempted": 0,
          "running": 0
        },
        "metrics": {
          "recall_at_5": {
            "value": 1.0,
            "valid_n": 59,
            "excluded": {}
          },
          "recall_at_10": {
            "value": 1.0,
            "valid_n": 59,
            "excluded": {}
          },
          "mrr_at_10": {
            "value": 0.9327683615819209,
            "valid_n": 59,
            "excluded": {}
          },
          "all_groups_hit_at_5": {
            "value": 1.0,
            "valid_n": 59,
            "excluded": {}
          },
          "all_groups_hit_at_10": {
            "value": 1.0,
            "valid_n": 59,
            "excluded": {}
          },
          "candidate_group_coverage": {
            "value": 1.0,
            "valid_n": 59,
            "excluded": {}
          },
          "prompt_group_coverage": {
            "value": 1.0,
            "valid_n": 59,
            "excluded": {}
          },
          "answer_point_coverage": {
            "value": 0.9915254237288136,
            "valid_n": 59,
            "excluded": {}
          },
          "faithfulness": {
            "value": 0.9858757062146892,
            "valid_n": 59,
            "excluded": {}
          },
          "absent_refusal_rate": {
            "value": null,
            "valid_n": 0,
            "excluded": {
              "answerable": 59
            }
          },
          "answerable_false_refusal_rate": {
            "value": 0.0,
            "valid_n": 59,
            "excluded": {}
          }
        }
      },
      {
        "bucket": "B_model",
        "strategy": "bm25",
        "total": 59,
        "attempted": 59,
        "completed": 59,
        "errors": 0,
        "not_attempted": 0,
        "status_counts": {
          "completed": 59,
          "rewrite_error": 0,
          "retrieval_error": 0,
          "self_check_error": 0,
          "answer_error": 0,
          "judge_error": 0,
          "cancelled": 0,
          "not_attempted": 0,
          "running": 0
        },
        "metrics": {
          "recall_at_5": {
            "value": 1.0,
            "valid_n": 59,
            "excluded": {}
          },
          "recall_at_10": {
            "value": 1.0,
            "valid_n": 59,
            "excluded": {}
          },
          "mrr_at_10": {
            "value": 0.9887005649717514,
            "valid_n": 59,
            "excluded": {}
          },
          "all_groups_hit_at_5": {
            "value": 1.0,
            "valid_n": 59,
            "excluded": {}
          },
          "all_groups_hit_at_10": {
            "value": 1.0,
            "valid_n": 59,
            "excluded": {}
          },
          "candidate_group_coverage": {
            "value": 1.0,
            "valid_n": 59,
            "excluded": {}
          },
          "prompt_group_coverage": {
            "value": 1.0,
            "valid_n": 59,
            "excluded": {}
          },
          "answer_point_coverage": {
            "value": 1.0,
            "valid_n": 59,
            "excluded": {}
          },
          "faithfulness": {
            "value": 0.9943502824858756,
            "valid_n": 59,
            "excluded": {}
          },
          "absent_refusal_rate": {
            "value": null,
            "valid_n": 0,
            "excluded": {
              "answerable": 59
            }
          },
          "answerable_false_refusal_rate": {
            "value": 0.0,
            "valid_n": 59,
            "excluded": {}
          }
        }
      },
      {
        "bucket": "B_model",
        "strategy": "hybrid",
        "total": 59,
        "attempted": 59,
        "completed": 59,
        "errors": 0,
        "not_attempted": 0,
        "status_counts": {
          "completed": 59,
          "rewrite_error": 0,
          "retrieval_error": 0,
          "self_check_error": 0,
          "answer_error": 0,
          "judge_error": 0,
          "cancelled": 0,
          "not_attempted": 0,
          "running": 0
        },
        "metrics": {
          "recall_at_5": {
            "value": 1.0,
            "valid_n": 59,
            "excluded": {}
          },
          "recall_at_10": {
            "value": 1.0,
            "valid_n": 59,
            "excluded": {}
          },
          "mrr_at_10": {
            "value": 0.980225988700565,
            "valid_n": 59,
            "excluded": {}
          },
          "all_groups_hit_at_5": {
            "value": 1.0,
            "valid_n": 59,
            "excluded": {}
          },
          "all_groups_hit_at_10": {
            "value": 1.0,
            "valid_n": 59,
            "excluded": {}
          },
          "candidate_group_coverage": {
            "value": 1.0,
            "valid_n": 59,
            "excluded": {}
          },
          "prompt_group_coverage": {
            "value": 1.0,
            "valid_n": 59,
            "excluded": {}
          },
          "answer_point_coverage": {
            "value": 1.0,
            "valid_n": 59,
            "excluded": {}
          },
          "faithfulness": {
            "value": 0.9919289749798225,
            "valid_n": 59,
            "excluded": {}
          },
          "absent_refusal_rate": {
            "value": null,
            "valid_n": 0,
            "excluded": {
              "answerable": 59
            }
          },
          "answerable_false_refusal_rate": {
            "value": 0.0,
            "valid_n": 59,
            "excluded": {}
          }
        }
      },
      {
        "bucket": "B_model",
        "strategy": "hybrid_rerank",
        "total": 59,
        "attempted": 59,
        "completed": 59,
        "errors": 0,
        "not_attempted": 0,
        "status_counts": {
          "completed": 59,
          "rewrite_error": 0,
          "retrieval_error": 0,
          "self_check_error": 0,
          "answer_error": 0,
          "judge_error": 0,
          "cancelled": 0,
          "not_attempted": 0,
          "running": 0
        },
        "metrics": {
          "recall_at_5": {
            "value": 1.0,
            "valid_n": 59,
            "excluded": {}
          },
          "recall_at_10": {
            "value": 1.0,
            "valid_n": 59,
            "excluded": {}
          },
          "mrr_at_10": {
            "value": 1.0,
            "valid_n": 59,
            "excluded": {}
          },
          "all_groups_hit_at_5": {
            "value": 1.0,
            "valid_n": 59,
            "excluded": {}
          },
          "all_groups_hit_at_10": {
            "value": 1.0,
            "valid_n": 59,
            "excluded": {}
          },
          "candidate_group_coverage": {
            "value": 1.0,
            "valid_n": 59,
            "excluded": {}
          },
          "prompt_group_coverage": {
            "value": 1.0,
            "valid_n": 59,
            "excluded": {}
          },
          "answer_point_coverage": {
            "value": 0.9830508474576272,
            "valid_n": 59,
            "excluded": {}
          },
          "faithfulness": {
            "value": 0.9980842911877394,
            "valid_n": 58,
            "excluded": {
              "zero_claims": 1
            }
          },
          "absent_refusal_rate": {
            "value": null,
            "valid_n": 0,
            "excluded": {
              "answerable": 59
            }
          },
          "answerable_false_refusal_rate": {
            "value": 0.01694915254237288,
            "valid_n": 59,
            "excluded": {}
          }
        }
      },
      {
        "bucket": "C_colloquial",
        "strategy": "dense",
        "total": 54,
        "attempted": 54,
        "completed": 54,
        "errors": 0,
        "not_attempted": 0,
        "status_counts": {
          "completed": 54,
          "rewrite_error": 0,
          "retrieval_error": 0,
          "self_check_error": 0,
          "answer_error": 0,
          "judge_error": 0,
          "cancelled": 0,
          "not_attempted": 0,
          "running": 0
        },
        "metrics": {
          "recall_at_5": {
            "value": 1.0,
            "valid_n": 54,
            "excluded": {}
          },
          "recall_at_10": {
            "value": 1.0,
            "valid_n": 54,
            "excluded": {}
          },
          "mrr_at_10": {
            "value": 0.9104938271604938,
            "valid_n": 54,
            "excluded": {}
          },
          "all_groups_hit_at_5": {
            "value": 1.0,
            "valid_n": 54,
            "excluded": {}
          },
          "all_groups_hit_at_10": {
            "value": 1.0,
            "valid_n": 54,
            "excluded": {}
          },
          "candidate_group_coverage": {
            "value": 1.0,
            "valid_n": 54,
            "excluded": {}
          },
          "prompt_group_coverage": {
            "value": 1.0,
            "valid_n": 54,
            "excluded": {}
          },
          "answer_point_coverage": {
            "value": 0.8703703703703703,
            "valid_n": 54,
            "excluded": {}
          },
          "faithfulness": {
            "value": 0.971474358974359,
            "valid_n": 52,
            "excluded": {
              "zero_claims": 2
            }
          },
          "absent_refusal_rate": {
            "value": null,
            "valid_n": 0,
            "excluded": {
              "answerable": 54
            }
          },
          "answerable_false_refusal_rate": {
            "value": 0.037037037037037035,
            "valid_n": 54,
            "excluded": {}
          }
        }
      },
      {
        "bucket": "C_colloquial",
        "strategy": "bm25",
        "total": 54,
        "attempted": 54,
        "completed": 54,
        "errors": 0,
        "not_attempted": 0,
        "status_counts": {
          "completed": 54,
          "rewrite_error": 0,
          "retrieval_error": 0,
          "self_check_error": 0,
          "answer_error": 0,
          "judge_error": 0,
          "cancelled": 0,
          "not_attempted": 0,
          "running": 0
        },
        "metrics": {
          "recall_at_5": {
            "value": 0.7870370370370371,
            "valid_n": 54,
            "excluded": {}
          },
          "recall_at_10": {
            "value": 0.8333333333333334,
            "valid_n": 54,
            "excluded": {}
          },
          "mrr_at_10": {
            "value": 0.645679012345679,
            "valid_n": 54,
            "excluded": {}
          },
          "all_groups_hit_at_5": {
            "value": 0.7777777777777778,
            "valid_n": 54,
            "excluded": {}
          },
          "all_groups_hit_at_10": {
            "value": 0.8333333333333334,
            "valid_n": 54,
            "excluded": {}
          },
          "candidate_group_coverage": {
            "value": 0.8888888888888888,
            "valid_n": 54,
            "excluded": {}
          },
          "prompt_group_coverage": {
            "value": 0.8333333333333334,
            "valid_n": 54,
            "excluded": {}
          },
          "answer_point_coverage": {
            "value": 0.7777777777777778,
            "valid_n": 54,
            "excluded": {}
          },
          "faithfulness": {
            "value": 0.9376543209876543,
            "valid_n": 45,
            "excluded": {
              "zero_claims": 9
            }
          },
          "absent_refusal_rate": {
            "value": null,
            "valid_n": 0,
            "excluded": {
              "answerable": 54
            }
          },
          "answerable_false_refusal_rate": {
            "value": 0.18518518518518517,
            "valid_n": 54,
            "excluded": {}
          }
        }
      },
      {
        "bucket": "C_colloquial",
        "strategy": "hybrid",
        "total": 54,
        "attempted": 54,
        "completed": 54,
        "errors": 0,
        "not_attempted": 0,
        "status_counts": {
          "completed": 54,
          "rewrite_error": 0,
          "retrieval_error": 0,
          "self_check_error": 0,
          "answer_error": 0,
          "judge_error": 0,
          "cancelled": 0,
          "not_attempted": 0,
          "running": 0
        },
        "metrics": {
          "recall_at_5": {
            "value": 0.9074074074074074,
            "valid_n": 54,
            "excluded": {}
          },
          "recall_at_10": {
            "value": 0.9444444444444444,
            "valid_n": 54,
            "excluded": {}
          },
          "mrr_at_10": {
            "value": 0.7803497942386831,
            "valid_n": 54,
            "excluded": {}
          },
          "all_groups_hit_at_5": {
            "value": 0.9074074074074074,
            "valid_n": 54,
            "excluded": {}
          },
          "all_groups_hit_at_10": {
            "value": 0.9444444444444444,
            "valid_n": 54,
            "excluded": {}
          },
          "candidate_group_coverage": {
            "value": 1.0,
            "valid_n": 54,
            "excluded": {}
          },
          "prompt_group_coverage": {
            "value": 0.9444444444444444,
            "valid_n": 54,
            "excluded": {}
          },
          "answer_point_coverage": {
            "value": 0.8518518518518519,
            "valid_n": 54,
            "excluded": {}
          },
          "faithfulness": {
            "value": 0.9507936507936507,
            "valid_n": 51,
            "excluded": {
              "zero_claims": 3
            }
          },
          "absent_refusal_rate": {
            "value": null,
            "valid_n": 0,
            "excluded": {
              "answerable": 54
            }
          },
          "answerable_false_refusal_rate": {
            "value": 0.07407407407407407,
            "valid_n": 54,
            "excluded": {}
          }
        }
      },
      {
        "bucket": "C_colloquial",
        "strategy": "hybrid_rerank",
        "total": 54,
        "attempted": 54,
        "completed": 54,
        "errors": 0,
        "not_attempted": 0,
        "status_counts": {
          "completed": 54,
          "rewrite_error": 0,
          "retrieval_error": 0,
          "self_check_error": 0,
          "answer_error": 0,
          "judge_error": 0,
          "cancelled": 0,
          "not_attempted": 0,
          "running": 0
        },
        "metrics": {
          "recall_at_5": {
            "value": 1.0,
            "valid_n": 54,
            "excluded": {}
          },
          "recall_at_10": {
            "value": 1.0,
            "valid_n": 54,
            "excluded": {}
          },
          "mrr_at_10": {
            "value": 0.9598765432098766,
            "valid_n": 54,
            "excluded": {}
          },
          "all_groups_hit_at_5": {
            "value": 1.0,
            "valid_n": 54,
            "excluded": {}
          },
          "all_groups_hit_at_10": {
            "value": 1.0,
            "valid_n": 54,
            "excluded": {}
          },
          "candidate_group_coverage": {
            "value": 1.0,
            "valid_n": 54,
            "excluded": {}
          },
          "prompt_group_coverage": {
            "value": 1.0,
            "valid_n": 54,
            "excluded": {}
          },
          "answer_point_coverage": {
            "value": 0.9583333333333334,
            "valid_n": 54,
            "excluded": {}
          },
          "faithfulness": {
            "value": 0.9656783468104223,
            "valid_n": 53,
            "excluded": {
              "zero_claims": 1
            }
          },
          "absent_refusal_rate": {
            "value": null,
            "valid_n": 0,
            "excluded": {
              "answerable": 54
            }
          },
          "answerable_false_refusal_rate": {
            "value": 0.018518518518518517,
            "valid_n": 54,
            "excluded": {}
          }
        }
      },
      {
        "bucket": "D_unanswerable",
        "strategy": "dense",
        "total": 59,
        "attempted": 59,
        "completed": 59,
        "errors": 0,
        "not_attempted": 0,
        "status_counts": {
          "completed": 59,
          "rewrite_error": 0,
          "retrieval_error": 0,
          "self_check_error": 0,
          "answer_error": 0,
          "judge_error": 0,
          "cancelled": 0,
          "not_attempted": 0,
          "running": 0
        },
        "metrics": {
          "recall_at_5": {
            "value": null,
            "valid_n": 0,
            "excluded": {
              "expected_refusal": 59
            }
          },
          "recall_at_10": {
            "value": null,
            "valid_n": 0,
            "excluded": {
              "expected_refusal": 59
            }
          },
          "mrr_at_10": {
            "value": null,
            "valid_n": 0,
            "excluded": {
              "expected_refusal": 59
            }
          },
          "all_groups_hit_at_5": {
            "value": null,
            "valid_n": 0,
            "excluded": {
              "expected_refusal": 59
            }
          },
          "all_groups_hit_at_10": {
            "value": null,
            "valid_n": 0,
            "excluded": {
              "expected_refusal": 59
            }
          },
          "candidate_group_coverage": {
            "value": null,
            "valid_n": 0,
            "excluded": {
              "expected_refusal": 59
            }
          },
          "prompt_group_coverage": {
            "value": null,
            "valid_n": 0,
            "excluded": {
              "expected_refusal": 59
            }
          },
          "answer_point_coverage": {
            "value": null,
            "valid_n": 0,
            "excluded": {
              "expected_refusal": 59
            }
          },
          "faithfulness": {
            "value": 0.7020202020202021,
            "valid_n": 33,
            "excluded": {
              "zero_claims": 26
            }
          },
          "absent_refusal_rate": {
            "value": 0.9661016949152542,
            "valid_n": 59,
            "excluded": {}
          },
          "answerable_false_refusal_rate": {
            "value": null,
            "valid_n": 0,
            "excluded": {
              "expected_refusal": 59
            }
          }
        }
      },
      {
        "bucket": "D_unanswerable",
        "strategy": "bm25",
        "total": 59,
        "attempted": 59,
        "completed": 59,
        "errors": 0,
        "not_attempted": 0,
        "status_counts": {
          "completed": 59,
          "rewrite_error": 0,
          "retrieval_error": 0,
          "self_check_error": 0,
          "answer_error": 0,
          "judge_error": 0,
          "cancelled": 0,
          "not_attempted": 0,
          "running": 0
        },
        "metrics": {
          "recall_at_5": {
            "value": null,
            "valid_n": 0,
            "excluded": {
              "expected_refusal": 59
            }
          },
          "recall_at_10": {
            "value": null,
            "valid_n": 0,
            "excluded": {
              "expected_refusal": 59
            }
          },
          "mrr_at_10": {
            "value": null,
            "valid_n": 0,
            "excluded": {
              "expected_refusal": 59
            }
          },
          "all_groups_hit_at_5": {
            "value": null,
            "valid_n": 0,
            "excluded": {
              "expected_refusal": 59
            }
          },
          "all_groups_hit_at_10": {
            "value": null,
            "valid_n": 0,
            "excluded": {
              "expected_refusal": 59
            }
          },
          "candidate_group_coverage": {
            "value": null,
            "valid_n": 0,
            "excluded": {
              "expected_refusal": 59
            }
          },
          "prompt_group_coverage": {
            "value": null,
            "valid_n": 0,
            "excluded": {
              "expected_refusal": 59
            }
          },
          "answer_point_coverage": {
            "value": null,
            "valid_n": 0,
            "excluded": {
              "expected_refusal": 59
            }
          },
          "faithfulness": {
            "value": 0.8730158730158729,
            "valid_n": 21,
            "excluded": {
              "zero_claims": 38
            }
          },
          "absent_refusal_rate": {
            "value": 0.9830508474576272,
            "valid_n": 59,
            "excluded": {}
          },
          "answerable_false_refusal_rate": {
            "value": null,
            "valid_n": 0,
            "excluded": {
              "expected_refusal": 59
            }
          }
        }
      },
      {
        "bucket": "D_unanswerable",
        "strategy": "hybrid",
        "total": 59,
        "attempted": 59,
        "completed": 59,
        "errors": 0,
        "not_attempted": 0,
        "status_counts": {
          "completed": 59,
          "rewrite_error": 0,
          "retrieval_error": 0,
          "self_check_error": 0,
          "answer_error": 0,
          "judge_error": 0,
          "cancelled": 0,
          "not_attempted": 0,
          "running": 0
        },
        "metrics": {
          "recall_at_5": {
            "value": null,
            "valid_n": 0,
            "excluded": {
              "expected_refusal": 59
            }
          },
          "recall_at_10": {
            "value": null,
            "valid_n": 0,
            "excluded": {
              "expected_refusal": 59
            }
          },
          "mrr_at_10": {
            "value": null,
            "valid_n": 0,
            "excluded": {
              "expected_refusal": 59
            }
          },
          "all_groups_hit_at_5": {
            "value": null,
            "valid_n": 0,
            "excluded": {
              "expected_refusal": 59
            }
          },
          "all_groups_hit_at_10": {
            "value": null,
            "valid_n": 0,
            "excluded": {
              "expected_refusal": 59
            }
          },
          "candidate_group_coverage": {
            "value": null,
            "valid_n": 0,
            "excluded": {
              "expected_refusal": 59
            }
          },
          "prompt_group_coverage": {
            "value": null,
            "valid_n": 0,
            "excluded": {
              "expected_refusal": 59
            }
          },
          "answer_point_coverage": {
            "value": null,
            "valid_n": 0,
            "excluded": {
              "expected_refusal": 59
            }
          },
          "faithfulness": {
            "value": 0.763888888888889,
            "valid_n": 30,
            "excluded": {
              "zero_claims": 29
            }
          },
          "absent_refusal_rate": {
            "value": 0.9661016949152542,
            "valid_n": 59,
            "excluded": {}
          },
          "answerable_false_refusal_rate": {
            "value": null,
            "valid_n": 0,
            "excluded": {
              "expected_refusal": 59
            }
          }
        }
      },
      {
        "bucket": "D_unanswerable",
        "strategy": "hybrid_rerank",
        "total": 59,
        "attempted": 59,
        "completed": 59,
        "errors": 0,
        "not_attempted": 0,
        "status_counts": {
          "completed": 59,
          "rewrite_error": 0,
          "retrieval_error": 0,
          "self_check_error": 0,
          "answer_error": 0,
          "judge_error": 0,
          "cancelled": 0,
          "not_attempted": 0,
          "running": 0
        },
        "metrics": {
          "recall_at_5": {
            "value": null,
            "valid_n": 0,
            "excluded": {
              "expected_refusal": 59
            }
          },
          "recall_at_10": {
            "value": null,
            "valid_n": 0,
            "excluded": {
              "expected_refusal": 59
            }
          },
          "mrr_at_10": {
            "value": null,
            "valid_n": 0,
            "excluded": {
              "expected_refusal": 59
            }
          },
          "all_groups_hit_at_5": {
            "value": null,
            "valid_n": 0,
            "excluded": {
              "expected_refusal": 59
            }
          },
          "all_groups_hit_at_10": {
            "value": null,
            "valid_n": 0,
            "excluded": {
              "expected_refusal": 59
            }
          },
          "candidate_group_coverage": {
            "value": null,
            "valid_n": 0,
            "excluded": {
              "expected_refusal": 59
            }
          },
          "prompt_group_coverage": {
            "value": null,
            "valid_n": 0,
            "excluded": {
              "expected_refusal": 59
            }
          },
          "answer_point_coverage": {
            "value": null,
            "valid_n": 0,
            "excluded": {
              "expected_refusal": 59
            }
          },
          "faithfulness": {
            "value": 0.8608333333333332,
            "valid_n": 20,
            "excluded": {
              "zero_claims": 39
            }
          },
          "absent_refusal_rate": {
            "value": 0.9661016949152542,
            "valid_n": 59,
            "excluded": {}
          },
          "answerable_false_refusal_rate": {
            "value": null,
            "valid_n": 0,
            "excluded": {
              "expected_refusal": 59
            }
          }
        }
      },
      {
        "bucket": "E_multi",
        "strategy": "dense",
        "total": 57,
        "attempted": 57,
        "completed": 57,
        "errors": 0,
        "not_attempted": 0,
        "status_counts": {
          "completed": 57,
          "rewrite_error": 0,
          "retrieval_error": 0,
          "self_check_error": 0,
          "answer_error": 0,
          "judge_error": 0,
          "cancelled": 0,
          "not_attempted": 0,
          "running": 0
        },
        "metrics": {
          "recall_at_5": {
            "value": 0.9005847953216375,
            "valid_n": 57,
            "excluded": {}
          },
          "recall_at_10": {
            "value": 0.9912280701754386,
            "valid_n": 57,
            "excluded": {}
          },
          "mrr_at_10": {
            "value": 0.9473684210526315,
            "valid_n": 57,
            "excluded": {}
          },
          "all_groups_hit_at_5": {
            "value": 0.7894736842105263,
            "valid_n": 57,
            "excluded": {}
          },
          "all_groups_hit_at_10": {
            "value": 0.9824561403508771,
            "valid_n": 57,
            "excluded": {}
          },
          "candidate_group_coverage": {
            "value": 1.0,
            "valid_n": 57,
            "excluded": {}
          },
          "prompt_group_coverage": {
            "value": 0.9912280701754386,
            "valid_n": 57,
            "excluded": {}
          },
          "answer_point_coverage": {
            "value": 0.8830409356725146,
            "valid_n": 57,
            "excluded": {}
          },
          "faithfulness": {
            "value": 0.9601515151515151,
            "valid_n": 55,
            "excluded": {
              "zero_claims": 2
            }
          },
          "absent_refusal_rate": {
            "value": null,
            "valid_n": 0,
            "excluded": {
              "answerable": 57
            }
          },
          "answerable_false_refusal_rate": {
            "value": 0.03508771929824561,
            "valid_n": 57,
            "excluded": {}
          }
        }
      },
      {
        "bucket": "E_multi",
        "strategy": "bm25",
        "total": 57,
        "attempted": 57,
        "completed": 57,
        "errors": 0,
        "not_attempted": 0,
        "status_counts": {
          "completed": 57,
          "rewrite_error": 0,
          "retrieval_error": 0,
          "self_check_error": 0,
          "answer_error": 0,
          "judge_error": 0,
          "cancelled": 0,
          "not_attempted": 0,
          "running": 0
        },
        "metrics": {
          "recall_at_5": {
            "value": 0.8567251461988304,
            "valid_n": 57,
            "excluded": {}
          },
          "recall_at_10": {
            "value": 0.9415204678362573,
            "valid_n": 57,
            "excluded": {}
          },
          "mrr_at_10": {
            "value": 0.9532163742690059,
            "valid_n": 57,
            "excluded": {}
          },
          "all_groups_hit_at_5": {
            "value": 0.7017543859649122,
            "valid_n": 57,
            "excluded": {}
          },
          "all_groups_hit_at_10": {
            "value": 0.8771929824561403,
            "valid_n": 57,
            "excluded": {}
          },
          "candidate_group_coverage": {
            "value": 0.9736842105263158,
            "valid_n": 57,
            "excluded": {}
          },
          "prompt_group_coverage": {
            "value": 0.9415204678362573,
            "valid_n": 57,
            "excluded": {}
          },
          "answer_point_coverage": {
            "value": 0.8187134502923976,
            "valid_n": 57,
            "excluded": {}
          },
          "faithfulness": {
            "value": 0.957432844932845,
            "valid_n": 52,
            "excluded": {
              "zero_claims": 5
            }
          },
          "absent_refusal_rate": {
            "value": null,
            "valid_n": 0,
            "excluded": {
              "answerable": 57
            }
          },
          "answerable_false_refusal_rate": {
            "value": 0.10526315789473684,
            "valid_n": 57,
            "excluded": {}
          }
        }
      },
      {
        "bucket": "E_multi",
        "strategy": "hybrid",
        "total": 57,
        "attempted": 57,
        "completed": 57,
        "errors": 0,
        "not_attempted": 0,
        "status_counts": {
          "completed": 57,
          "rewrite_error": 0,
          "retrieval_error": 0,
          "self_check_error": 0,
          "answer_error": 0,
          "judge_error": 0,
          "cancelled": 0,
          "not_attempted": 0,
          "running": 0
        },
        "metrics": {
          "recall_at_5": {
            "value": 0.9269005847953217,
            "valid_n": 57,
            "excluded": {}
          },
          "recall_at_10": {
            "value": 0.956140350877193,
            "valid_n": 57,
            "excluded": {}
          },
          "mrr_at_10": {
            "value": 0.9736842105263158,
            "valid_n": 57,
            "excluded": {}
          },
          "all_groups_hit_at_5": {
            "value": 0.8421052631578947,
            "valid_n": 57,
            "excluded": {}
          },
          "all_groups_hit_at_10": {
            "value": 0.9122807017543859,
            "valid_n": 57,
            "excluded": {}
          },
          "candidate_group_coverage": {
            "value": 1.0,
            "valid_n": 57,
            "excluded": {}
          },
          "prompt_group_coverage": {
            "value": 0.956140350877193,
            "valid_n": 57,
            "excluded": {}
          },
          "answer_point_coverage": {
            "value": 0.8830409356725146,
            "valid_n": 57,
            "excluded": {}
          },
          "faithfulness": {
            "value": 0.9423133450911229,
            "valid_n": 54,
            "excluded": {
              "zero_claims": 3
            }
          },
          "absent_refusal_rate": {
            "value": null,
            "valid_n": 0,
            "excluded": {
              "answerable": 57
            }
          },
          "answerable_false_refusal_rate": {
            "value": 0.07017543859649122,
            "valid_n": 57,
            "excluded": {}
          }
        }
      },
      {
        "bucket": "E_multi",
        "strategy": "hybrid_rerank",
        "total": 57,
        "attempted": 57,
        "completed": 57,
        "errors": 0,
        "not_attempted": 0,
        "status_counts": {
          "completed": 57,
          "rewrite_error": 0,
          "retrieval_error": 0,
          "self_check_error": 0,
          "answer_error": 0,
          "judge_error": 0,
          "cancelled": 0,
          "not_attempted": 0,
          "running": 0
        },
        "metrics": {
          "recall_at_5": {
            "value": 0.9678362573099415,
            "valid_n": 57,
            "excluded": {}
          },
          "recall_at_10": {
            "value": 0.9824561403508771,
            "valid_n": 57,
            "excluded": {}
          },
          "mrr_at_10": {
            "value": 0.9824561403508771,
            "valid_n": 57,
            "excluded": {}
          },
          "all_groups_hit_at_5": {
            "value": 0.9298245614035088,
            "valid_n": 57,
            "excluded": {}
          },
          "all_groups_hit_at_10": {
            "value": 0.9649122807017544,
            "valid_n": 57,
            "excluded": {}
          },
          "candidate_group_coverage": {
            "value": 1.0,
            "valid_n": 57,
            "excluded": {}
          },
          "prompt_group_coverage": {
            "value": 0.9824561403508771,
            "valid_n": 57,
            "excluded": {}
          },
          "answer_point_coverage": {
            "value": 0.8976608187134503,
            "valid_n": 57,
            "excluded": {}
          },
          "faithfulness": {
            "value": 0.9489641311069883,
            "valid_n": 56,
            "excluded": {
              "zero_claims": 1
            }
          },
          "absent_refusal_rate": {
            "value": null,
            "valid_n": 0,
            "excluded": {
              "answerable": 57
            }
          },
          "answerable_false_refusal_rate": {
            "value": 0.017543859649122806,
            "valid_n": 57,
            "excluded": {}
          }
        }
      }
    ]
  },
  "source_runs": [
    {
      "run_id": "2486afc8e62e4550bdfec6d676a27d84",
      "selected_eval_ids": [
        "A1",
        "A2",
        "A3",
        "A4",
        "A5",
        "A6",
        "A7",
        "A8",
        "A9",
        "A10",
        "A11",
        "A12",
        "A13",
        "A14",
        "A15",
        "A16",
        "A17",
        "A18",
        "A19",
        "A20",
        "A21",
        "A22",
        "A23",
        "A24",
        "A25",
        "A26",
        "A27",
        "A28",
        "A29",
        "A30",
        "A31",
        "A32",
        "A33",
        "A34",
        "A35",
        "A36",
        "A37",
        "A38",
        "A39",
        "A40",
        "A41",
        "A42",
        "A43",
        "A44",
        "A45",
        "A46",
        "A47",
        "A48",
        "A49",
        "A50",
        "A51",
        "A52",
        "A53",
        "A54",
        "A55",
        "A56",
        "A57",
        "A58",
        "A59",
        "A60",
        "B1",
        "B2",
        "B3",
        "B4",
        "B5",
        "B6",
        "B7",
        "B8",
        "B9",
        "B10",
        "B11",
        "B12",
        "B13",
        "B14",
        "B15",
        "B16",
        "B17",
        "B18",
        "B19",
        "B20",
        "B21",
        "B22",
        "B23",
        "B24",
        "B25",
        "B26",
        "B27",
        "B28",
        "B29",
        "B30",
        "B31",
        "B32",
        "B33",
        "B34",
        "B35",
        "B36",
        "B37",
        "B38",
        "B39",
        "B40",
        "B41",
        "B42",
        "B43",
        "B44",
        "B45",
        "B46",
        "B47",
        "B48",
        "B49",
        "B50",
        "B51",
        "B52",
        "B53",
        "B54",
        "B55",
        "B56",
        "B57",
        "B58",
        "B59",
        "B60",
        "C1",
        "C2",
        "C3",
        "C4",
        "C5",
        "C6",
        "C7",
        "C8",
        "C9",
        "C10",
        "C11",
        "C12",
        "C13",
        "C14",
        "C15",
        "C16",
        "C17",
        "C18",
        "C19",
        "C20",
        "C21",
        "C22",
        "C23",
        "C24",
        "C25",
        "C26",
        "C27",
        "C28",
        "C29",
        "C30",
        "C31",
        "C32",
        "C33",
        "C34",
        "C35",
        "C36",
        "C37",
        "C38"
      ],
      "source_map_id": "eac708d18ae690253408ccb241ef2e633c2ebc75791479249337870952acdf4a",
      "report_json": "merchant-rag-interrupted.json",
      "report_markdown": "merchant-rag-interrupted.md",
      "report_sha256": {
        "json": "0b6f697cff08de71f1dd1d3d6de0f7efc7c54a0c69976316f4bbcf29470d678d",
        "md": "7e59f62c87476738ffe4e4442bed3f339805e1f038891af118a1faf5b327952c"
      },
      "config_fingerprint": "46d11df092ca2b803030fb7e227d971ef7530552bb5d18b4939bfc0c7f186ee7",
      "actual_case_concurrency": 2,
      "native_run": {
        "schema_version": 2,
        "run_id": "2486afc8e62e4550bdfec6d676a27d84",
        "config": {
          "dataset_id": "merchant-rag-300-v1",
          "scope": "full",
          "mode": "content_ablation",
          "models": {
            "answer": "glm-5.3-flash",
            "rewrite": "glm-5.3-flash",
            "self_check": "glm-5.3-flash",
            "judge": "glm-5.3-flash",
            "embedding": "BAAI/bge-m3",
            "rerank": "BAAI/bge-reranker-v2-m3"
          },
          "budgets": {
            "candidate_k": 50,
            "final_k": 10,
            "chunk_target_chars": 1200,
            "chunk_overlap_chars": 120,
            "case_concurrency": 2,
            "answer_output_tokens": 512,
            "rewrite_output_tokens": 2048,
            "self_check_output_tokens": 2048,
            "judge_input_tokens": 16000,
            "judge_output_tokens": 2048,
            "tool_input_tokens": 8000,
            "model_retries": 0,
            "rewrite_timeout_s": 60.0,
            "self_check_timeout_s": 20.0,
            "faq_timeout_s": 90.0,
            "chat_timeout_s": 240.0,
            "judge_timeout_s": 60.0,
            "embedding_timeout_s": 20.0,
            "rerank_timeout_s": 20.0,
            "milvus_timeout_s": 5.0
          },
          "prompt_versions": {
            "rewrite": "query-v1",
            "self_check": "sufficiency-v1",
            "answer": "grounded-answer-v1",
            "judge": "joint-generation-v2.1"
          },
          "upstream_summary": {
            "llm": "https://open.bigmodel.cn",
            "embedding": "https://api.siliconflow.cn",
            "rerank": "https://api.siliconflow.cn"
          },
          "provenance": {
            "dataset_fingerprint": "d4da3bd7b61c85bf236de955fadc0dcb806f2384c417dfe2b3dd686372f7476e",
            "corpus_hash": "c188bcabb1b3fa6a5e4e72284d0726f96e2b2cff6e0a1c48245dea85e792ef10",
            "cases_hash": "3b2901de79f80c54453805038e354aea9cadabf024fafe2802c78ce7a75c4f96",
            "annotation_hash": "b4015c5d11675137634fb8c0e186796aa3be94744c9081b9a661f9962e840925",
            "prompt_hashes": {
              "rewrite": "fb42af25925e21c523733a82c014bd6d2306bc6de1f92cb49e736354ff807a41",
              "self_check": "875f1a5e961ea425f2f38d5b7ed9f7adcc6174fdd9778916edcbef68bcfc5823",
              "answer": "9116e2a564bb6324cffddd4ed75dd161ebc7e9624cf52b69471e24750580b6de",
              "judge": "98e9edbee690224ef938a57c7b0678b86bc3ccf9646b3fe773ceb38af06f2b16"
            },
            "endpoint_hashes": {
              "llm": "2092337b5f19a5366b55f7ee7181d19dcf8a01e5bc332cd1a3c7aa5312dd9e19",
              "embedding": "2db45fecf782ae40de986dcec63be1e5ea701683e83799f7c047866de6cdf7b9",
              "rerank": "f42220d941061413c5aa874586c5219fbd905cfcf2c67a3b73c1127fd6d0a5a8",
              "milvus": "24a529ee666ff3935dd961bafc1b479bce137ec2b123a2ce92f314a9eb0243c8"
            },
            "llm_timeout_s": 60.0,
            "llm_token_limit_field": "max_tokens",
            "llm_reasoning_effort": "low",
            "rewrite_failure_policy": "original-query-on-invalid-v1"
          },
          "fingerprint": "46d11df092ca2b803030fb7e227d971ef7530552bb5d18b4939bfc0c7f186ee7"
        },
        "state": "failed",
        "outcome": "interrupted",
        "stage": "cleanup",
        "planned_cases": 300,
        "planned_strategies": 4,
        "planned_records": 1200,
        "counts": {
          "completed": 628,
          "rewrite_error": 0,
          "retrieval_error": 2,
          "self_check_error": 2,
          "answer_error": 2,
          "judge_error": 0,
          "cancelled": 2,
          "not_attempted": 564,
          "running": 0,
          "total": 1200,
          "attempted": 636,
          "errors": 6
        },
        "request_counts": {
          "rewrite": 160,
          "self_check": 634,
          "answer": 609,
          "judge": 628,
          "embedding": 480,
          "rerank": 158,
          "milvus": 668
        },
        "cleanup": {
          "ok": false,
          "errors": [
            "资源清理失败",
            "资源清理失败"
          ],
          "unverified": []
        },
        "created_at": "2026-10-11T06:15:28.298170+00:00",
        "updated_at": "2026-10-12T03:52:43.100308+00:00",
        "started_at": "2026-10-11T06:15:28.331240+00:00",
        "finished_at": "2026-10-12T03:52:43.117005+00:00",
        "error": {
          "code": "interrupted",
          "type": "RuntimeError",
          "message": "该阶段执行失败"
        }
      }
    },
    {
      "run_id": "7adfc4c7dc3a4750885c23c94f3be671",
      "selected_eval_ids": [
        "C39",
        "C40",
        "C41",
        "C42",
        "C43",
        "C44",
        "C45",
        "C46",
        "C47",
        "C48",
        "C49",
        "C50",
        "C51",
        "C52",
        "C53",
        "C54",
        "C55",
        "C56",
        "C57",
        "C58",
        "C59",
        "C60",
        "E1",
        "E2",
        "E3",
        "E4",
        "E5",
        "E6",
        "E7",
        "E8",
        "E9",
        "E10",
        "E11",
        "E12",
        "E13",
        "E14",
        "E15",
        "E16",
        "E17",
        "E18",
        "E19",
        "E20",
        "E21",
        "E22",
        "E23",
        "E24",
        "E25",
        "E26",
        "E27",
        "E28",
        "E29",
        "E30",
        "E31",
        "E32",
        "E33",
        "E34",
        "E35",
        "E36",
        "E37",
        "E38",
        "E39",
        "E40",
        "E41",
        "E42",
        "E43",
        "E44",
        "E45",
        "E46",
        "E47",
        "E48",
        "E49",
        "E50",
        "E51",
        "E52",
        "E53",
        "E54",
        "E55",
        "E56",
        "E57",
        "E58",
        "E59",
        "E60",
        "D1",
        "D2",
        "D3",
        "D4",
        "D5",
        "D6",
        "D7",
        "D8",
        "D9",
        "D10",
        "D11",
        "D12",
        "D13",
        "D14",
        "D15",
        "D16",
        "D17",
        "D18",
        "D19",
        "D20",
        "D21",
        "D22",
        "D23",
        "D24",
        "D25",
        "D26",
        "D27",
        "D28",
        "D29",
        "D30",
        "D31",
        "D32",
        "D33",
        "D34",
        "D35",
        "D36",
        "D37",
        "D38",
        "D39",
        "D40",
        "D41",
        "D42",
        "D43",
        "D44",
        "D45",
        "D46",
        "D47",
        "D48",
        "D49",
        "D50",
        "D51",
        "D52",
        "D53",
        "D54",
        "D55",
        "D56",
        "D57",
        "D58",
        "D59",
        "D60"
      ],
      "source_map_id": "2d33b192d47e446dbfde0df851279be3924441bb91bc932da390bc11aa98a590",
      "report_json": "merchant-rag-completion-remainder.json",
      "report_markdown": "merchant-rag-completion-remainder.md",
      "report_sha256": {
        "json": "c39af1c8749f095b3cefa243c3954be6593e9e7100b6f929150eb68488899894",
        "md": "e0aa0da2dbc22e184349dccc1a27286791d085a523d043adaf9d70eb3c45bb09"
      },
      "config_fingerprint": "46d11df092ca2b803030fb7e227d971ef7530552bb5d18b4939bfc0c7f186ee7",
      "actual_case_concurrency": 8,
      "native_run": {
        "schema_version": 2,
        "run_id": "7adfc4c7dc3a4750885c23c94f3be671",
        "config": {
          "dataset_id": "merchant-rag-300-v1",
          "scope": "full",
          "mode": "content_ablation",
          "models": {
            "answer": "glm-5.3-flash",
            "rewrite": "glm-5.3-flash",
            "self_check": "glm-5.3-flash",
            "judge": "glm-5.3-flash",
            "embedding": "BAAI/bge-m3",
            "rerank": "BAAI/bge-reranker-v2-m3"
          },
          "budgets": {
            "candidate_k": 50,
            "final_k": 10,
            "chunk_target_chars": 1200,
            "chunk_overlap_chars": 120,
            "case_concurrency": 2,
            "answer_output_tokens": 512,
            "rewrite_output_tokens": 2048,
            "self_check_output_tokens": 2048,
            "judge_input_tokens": 16000,
            "judge_output_tokens": 2048,
            "tool_input_tokens": 8000,
            "model_retries": 0,
            "rewrite_timeout_s": 60.0,
            "self_check_timeout_s": 20.0,
            "faq_timeout_s": 90.0,
            "chat_timeout_s": 240.0,
            "judge_timeout_s": 60.0,
            "embedding_timeout_s": 20.0,
            "rerank_timeout_s": 20.0,
            "milvus_timeout_s": 5.0
          },
          "prompt_versions": {
            "rewrite": "query-v1",
            "self_check": "sufficiency-v1",
            "answer": "grounded-answer-v1",
            "judge": "joint-generation-v2.1"
          },
          "upstream_summary": {
            "llm": "https://open.bigmodel.cn",
            "embedding": "https://api.siliconflow.cn",
            "rerank": "https://api.siliconflow.cn"
          },
          "provenance": {
            "dataset_fingerprint": "d4da3bd7b61c85bf236de955fadc0dcb806f2384c417dfe2b3dd686372f7476e",
            "corpus_hash": "c188bcabb1b3fa6a5e4e72284d0726f96e2b2cff6e0a1c48245dea85e792ef10",
            "cases_hash": "3b2901de79f80c54453805038e354aea9cadabf024fafe2802c78ce7a75c4f96",
            "annotation_hash": "b4015c5d11675137634fb8c0e186796aa3be94744c9081b9a661f9962e840925",
            "prompt_hashes": {
              "rewrite": "fb42af25925e21c523733a82c014bd6d2306bc6de1f92cb49e736354ff807a41",
              "self_check": "875f1a5e961ea425f2f38d5b7ed9f7adcc6174fdd9778916edcbef68bcfc5823",
              "answer": "9116e2a564bb6324cffddd4ed75dd161ebc7e9624cf52b69471e24750580b6de",
              "judge": "98e9edbee690224ef938a57c7b0678b86bc3ccf9646b3fe773ceb38af06f2b16"
            },
            "endpoint_hashes": {
              "llm": "2092337b5f19a5366b55f7ee7181d19dcf8a01e5bc332cd1a3c7aa5312dd9e19",
              "embedding": "2db45fecf782ae40de986dcec63be1e5ea701683e83799f7c047866de6cdf7b9",
              "rerank": "f42220d941061413c5aa874586c5219fbd905cfcf2c67a3b73c1127fd6d0a5a8",
              "milvus": "24a529ee666ff3935dd961bafc1b479bce137ec2b123a2ce92f314a9eb0243c8"
            },
            "llm_timeout_s": 60.0,
            "llm_token_limit_field": "max_tokens",
            "llm_reasoning_effort": "low",
            "rewrite_failure_policy": "original-query-on-invalid-v1"
          },
          "fingerprint": "46d11df092ca2b803030fb7e227d971ef7530552bb5d18b4939bfc0c7f186ee7"
        },
        "state": "completed_with_errors",
        "outcome": "completed_with_errors",
        "stage": "complete",
        "planned_cases": 142,
        "planned_strategies": 4,
        "planned_records": 568,
        "counts": {
          "completed": 562,
          "rewrite_error": 0,
          "retrieval_error": 0,
          "self_check_error": 0,
          "answer_error": 4,
          "judge_error": 2,
          "cancelled": 0,
          "not_attempted": 0,
          "running": 0,
          "total": 568,
          "attempted": 568,
          "errors": 6
        },
        "request_counts": {
          "rewrite": 142,
          "self_check": 568,
          "answer": 319,
          "judge": 564,
          "embedding": 429,
          "rerank": 142,
          "milvus": 603
        },
        "cleanup": {
          "ok": true,
          "errors": [],
          "unverified": []
        },
        "created_at": "2026-10-12T04:59:05.910180+00:00",
        "updated_at": "2026-10-12T05:10:27.802488+00:00",
        "started_at": "2026-10-12T04:59:05.946032+00:00",
        "finished_at": "2026-10-12T05:10:28.047263+00:00",
        "error": null
      }
    }
  ],
  "method": {
    "runner": {
      "ast_changes": [
        {
          "path": "run_cases.body[0].body[15].value.args[0].value",
          "before": 2,
          "after": 8
        }
      ],
      "changed_constant_count": 1,
      "original_function_sha256": "59200d0326ab6f6d6071820ad8150d4f3d55702f95320f8c8ed62843af985016",
      "original_ast_sha256": "6a53b089f9b880594c2603c86003b7a0008562f3bb3c17e8298e30bc999ee5fe",
      "fast_ast_sha256": "aed227e29cc74843404bb978e77532723f1cb5795ef17b0e85f9b7693523fff5",
      "original_case_concurrency": 2,
      "continuation_case_concurrency": 8,
      "configuration_case_concurrency": 2,
      "global_asyncio_unchanged": true,
      "query_route_and_other_methods_inherited": true
    },
    "observer": {
      "file": ".cache/task10_degraded_service.py",
      "reuse": "definition-only import; ObservedOwnedResources/CapturedPlanner pass-through; new OUT",
      "extra_model_requests": 0
    },
    "original_files_unchanged": true,
    "native_source_maps_validated_per_record": true,
    "physical_ids_and_scores_unchanged": true,
    "summary_function": "app.rag_evaluation.report.summarize_records"
  }
}
```
