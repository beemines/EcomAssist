# RAG 评估报告

运行：b1af9aadc0094141aa5df5ae0ec91bd1

状态：completed_with_errors；范围：pilot

## 运行信息与汇总

```json
{
  "schema_version": 2,
  "summary": {
    "rows": [
      {
        "bucket": "overall",
        "strategy": "dense",
        "total": 10,
        "attempted": 10,
        "completed": 8,
        "errors": 2,
        "not_attempted": 0,
        "status_counts": {
          "completed": 8,
          "rewrite_error": 2,
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
            "valid_n": 6,
            "excluded": {
              "expected_refusal": 2,
              "rewrite_error": 2
            }
          },
          "recall_at_10": {
            "value": 1.0,
            "valid_n": 6,
            "excluded": {
              "expected_refusal": 2,
              "rewrite_error": 2
            }
          },
          "mrr_at_10": {
            "value": 1.0,
            "valid_n": 6,
            "excluded": {
              "expected_refusal": 2,
              "rewrite_error": 2
            }
          },
          "all_groups_hit_at_5": {
            "value": 1.0,
            "valid_n": 6,
            "excluded": {
              "expected_refusal": 2,
              "rewrite_error": 2
            }
          },
          "all_groups_hit_at_10": {
            "value": 1.0,
            "valid_n": 6,
            "excluded": {
              "expected_refusal": 2,
              "rewrite_error": 2
            }
          },
          "candidate_group_coverage": {
            "value": 1.0,
            "valid_n": 6,
            "excluded": {
              "expected_refusal": 2,
              "rewrite_error": 2
            }
          },
          "prompt_group_coverage": {
            "value": 1.0,
            "valid_n": 6,
            "excluded": {
              "expected_refusal": 2,
              "rewrite_error": 2
            }
          },
          "answer_point_coverage": {
            "value": 1.0,
            "valid_n": 6,
            "excluded": {
              "expected_refusal": 2,
              "rewrite_error": 2
            }
          },
          "faithfulness": {
            "value": 0.8571428571428571,
            "valid_n": 7,
            "excluded": {
              "rewrite_error": 2,
              "zero_claims": 1
            }
          },
          "absent_refusal_rate": {
            "value": 1.0,
            "valid_n": 2,
            "excluded": {
              "answerable": 8
            }
          },
          "answerable_false_refusal_rate": {
            "value": 0.0,
            "valid_n": 6,
            "excluded": {
              "expected_refusal": 2,
              "rewrite_error": 2
            }
          }
        }
      },
      {
        "bucket": "overall",
        "strategy": "bm25",
        "total": 10,
        "attempted": 10,
        "completed": 8,
        "errors": 2,
        "not_attempted": 0,
        "status_counts": {
          "completed": 8,
          "rewrite_error": 2,
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
            "value": 0.8888888888888888,
            "valid_n": 6,
            "excluded": {
              "expected_refusal": 2,
              "rewrite_error": 2
            }
          },
          "recall_at_10": {
            "value": 0.9444444444444445,
            "valid_n": 6,
            "excluded": {
              "expected_refusal": 2,
              "rewrite_error": 2
            }
          },
          "mrr_at_10": {
            "value": 0.8888888888888888,
            "valid_n": 6,
            "excluded": {
              "expected_refusal": 2,
              "rewrite_error": 2
            }
          },
          "all_groups_hit_at_5": {
            "value": 0.8333333333333334,
            "valid_n": 6,
            "excluded": {
              "expected_refusal": 2,
              "rewrite_error": 2
            }
          },
          "all_groups_hit_at_10": {
            "value": 0.8333333333333334,
            "valid_n": 6,
            "excluded": {
              "expected_refusal": 2,
              "rewrite_error": 2
            }
          },
          "candidate_group_coverage": {
            "value": 1.0,
            "valid_n": 6,
            "excluded": {
              "expected_refusal": 2,
              "rewrite_error": 2
            }
          },
          "prompt_group_coverage": {
            "value": 0.9444444444444445,
            "valid_n": 6,
            "excluded": {
              "expected_refusal": 2,
              "rewrite_error": 2
            }
          },
          "answer_point_coverage": {
            "value": 0.6666666666666666,
            "valid_n": 6,
            "excluded": {
              "expected_refusal": 2,
              "rewrite_error": 2
            }
          },
          "faithfulness": {
            "value": 1.0,
            "valid_n": 5,
            "excluded": {
              "rewrite_error": 2,
              "zero_claims": 3
            }
          },
          "absent_refusal_rate": {
            "value": 1.0,
            "valid_n": 2,
            "excluded": {
              "answerable": 8
            }
          },
          "answerable_false_refusal_rate": {
            "value": 0.3333333333333333,
            "valid_n": 6,
            "excluded": {
              "expected_refusal": 2,
              "rewrite_error": 2
            }
          }
        }
      },
      {
        "bucket": "overall",
        "strategy": "hybrid",
        "total": 10,
        "attempted": 10,
        "completed": 8,
        "errors": 2,
        "not_attempted": 0,
        "status_counts": {
          "completed": 8,
          "rewrite_error": 2,
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
            "value": 0.9444444444444445,
            "valid_n": 6,
            "excluded": {
              "expected_refusal": 2,
              "rewrite_error": 2
            }
          },
          "recall_at_10": {
            "value": 1.0,
            "valid_n": 6,
            "excluded": {
              "expected_refusal": 2,
              "rewrite_error": 2
            }
          },
          "mrr_at_10": {
            "value": 0.9166666666666666,
            "valid_n": 6,
            "excluded": {
              "expected_refusal": 2,
              "rewrite_error": 2
            }
          },
          "all_groups_hit_at_5": {
            "value": 0.8333333333333334,
            "valid_n": 6,
            "excluded": {
              "expected_refusal": 2,
              "rewrite_error": 2
            }
          },
          "all_groups_hit_at_10": {
            "value": 1.0,
            "valid_n": 6,
            "excluded": {
              "expected_refusal": 2,
              "rewrite_error": 2
            }
          },
          "candidate_group_coverage": {
            "value": 1.0,
            "valid_n": 6,
            "excluded": {
              "expected_refusal": 2,
              "rewrite_error": 2
            }
          },
          "prompt_group_coverage": {
            "value": 1.0,
            "valid_n": 6,
            "excluded": {
              "expected_refusal": 2,
              "rewrite_error": 2
            }
          },
          "answer_point_coverage": {
            "value": 1.0,
            "valid_n": 6,
            "excluded": {
              "expected_refusal": 2,
              "rewrite_error": 2
            }
          },
          "faithfulness": {
            "value": 0.7,
            "valid_n": 8,
            "excluded": {
              "rewrite_error": 2
            }
          },
          "absent_refusal_rate": {
            "value": 1.0,
            "valid_n": 2,
            "excluded": {
              "answerable": 8
            }
          },
          "answerable_false_refusal_rate": {
            "value": 0.0,
            "valid_n": 6,
            "excluded": {
              "expected_refusal": 2,
              "rewrite_error": 2
            }
          }
        }
      },
      {
        "bucket": "overall",
        "strategy": "hybrid_rerank",
        "total": 10,
        "attempted": 10,
        "completed": 8,
        "errors": 2,
        "not_attempted": 0,
        "status_counts": {
          "completed": 8,
          "rewrite_error": 2,
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
            "valid_n": 6,
            "excluded": {
              "expected_refusal": 2,
              "rewrite_error": 2
            }
          },
          "recall_at_10": {
            "value": 1.0,
            "valid_n": 6,
            "excluded": {
              "expected_refusal": 2,
              "rewrite_error": 2
            }
          },
          "mrr_at_10": {
            "value": 1.0,
            "valid_n": 6,
            "excluded": {
              "expected_refusal": 2,
              "rewrite_error": 2
            }
          },
          "all_groups_hit_at_5": {
            "value": 1.0,
            "valid_n": 6,
            "excluded": {
              "expected_refusal": 2,
              "rewrite_error": 2
            }
          },
          "all_groups_hit_at_10": {
            "value": 1.0,
            "valid_n": 6,
            "excluded": {
              "expected_refusal": 2,
              "rewrite_error": 2
            }
          },
          "candidate_group_coverage": {
            "value": 1.0,
            "valid_n": 6,
            "excluded": {
              "expected_refusal": 2,
              "rewrite_error": 2
            }
          },
          "prompt_group_coverage": {
            "value": 1.0,
            "valid_n": 6,
            "excluded": {
              "expected_refusal": 2,
              "rewrite_error": 2
            }
          },
          "answer_point_coverage": {
            "value": 0.8611111111111112,
            "valid_n": 6,
            "excluded": {
              "expected_refusal": 2,
              "rewrite_error": 2
            }
          },
          "faithfulness": {
            "value": 0.9821428571428571,
            "valid_n": 7,
            "excluded": {
              "rewrite_error": 2,
              "zero_claims": 1
            }
          },
          "absent_refusal_rate": {
            "value": 1.0,
            "valid_n": 2,
            "excluded": {
              "answerable": 8
            }
          },
          "answerable_false_refusal_rate": {
            "value": 0.0,
            "valid_n": 6,
            "excluded": {
              "expected_refusal": 2,
              "rewrite_error": 2
            }
          }
        }
      },
      {
        "bucket": "A_policy",
        "strategy": "dense",
        "total": 2,
        "attempted": 2,
        "completed": 2,
        "errors": 0,
        "not_attempted": 0,
        "status_counts": {
          "completed": 2,
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
            "valid_n": 2,
            "excluded": {}
          },
          "recall_at_10": {
            "value": 1.0,
            "valid_n": 2,
            "excluded": {}
          },
          "mrr_at_10": {
            "value": 1.0,
            "valid_n": 2,
            "excluded": {}
          },
          "all_groups_hit_at_5": {
            "value": 1.0,
            "valid_n": 2,
            "excluded": {}
          },
          "all_groups_hit_at_10": {
            "value": 1.0,
            "valid_n": 2,
            "excluded": {}
          },
          "candidate_group_coverage": {
            "value": 1.0,
            "valid_n": 2,
            "excluded": {}
          },
          "prompt_group_coverage": {
            "value": 1.0,
            "valid_n": 2,
            "excluded": {}
          },
          "answer_point_coverage": {
            "value": 1.0,
            "valid_n": 2,
            "excluded": {}
          },
          "faithfulness": {
            "value": 1.0,
            "valid_n": 2,
            "excluded": {}
          },
          "absent_refusal_rate": {
            "value": null,
            "valid_n": 0,
            "excluded": {
              "answerable": 2
            }
          },
          "answerable_false_refusal_rate": {
            "value": 0.0,
            "valid_n": 2,
            "excluded": {}
          }
        }
      },
      {
        "bucket": "A_policy",
        "strategy": "bm25",
        "total": 2,
        "attempted": 2,
        "completed": 2,
        "errors": 0,
        "not_attempted": 0,
        "status_counts": {
          "completed": 2,
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
            "valid_n": 2,
            "excluded": {}
          },
          "recall_at_10": {
            "value": 1.0,
            "valid_n": 2,
            "excluded": {}
          },
          "mrr_at_10": {
            "value": 1.0,
            "valid_n": 2,
            "excluded": {}
          },
          "all_groups_hit_at_5": {
            "value": 1.0,
            "valid_n": 2,
            "excluded": {}
          },
          "all_groups_hit_at_10": {
            "value": 1.0,
            "valid_n": 2,
            "excluded": {}
          },
          "candidate_group_coverage": {
            "value": 1.0,
            "valid_n": 2,
            "excluded": {}
          },
          "prompt_group_coverage": {
            "value": 1.0,
            "valid_n": 2,
            "excluded": {}
          },
          "answer_point_coverage": {
            "value": 0.5,
            "valid_n": 2,
            "excluded": {}
          },
          "faithfulness": {
            "value": 1.0,
            "valid_n": 1,
            "excluded": {
              "zero_claims": 1
            }
          },
          "absent_refusal_rate": {
            "value": null,
            "valid_n": 0,
            "excluded": {
              "answerable": 2
            }
          },
          "answerable_false_refusal_rate": {
            "value": 0.5,
            "valid_n": 2,
            "excluded": {}
          }
        }
      },
      {
        "bucket": "A_policy",
        "strategy": "hybrid",
        "total": 2,
        "attempted": 2,
        "completed": 2,
        "errors": 0,
        "not_attempted": 0,
        "status_counts": {
          "completed": 2,
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
            "valid_n": 2,
            "excluded": {}
          },
          "recall_at_10": {
            "value": 1.0,
            "valid_n": 2,
            "excluded": {}
          },
          "mrr_at_10": {
            "value": 1.0,
            "valid_n": 2,
            "excluded": {}
          },
          "all_groups_hit_at_5": {
            "value": 1.0,
            "valid_n": 2,
            "excluded": {}
          },
          "all_groups_hit_at_10": {
            "value": 1.0,
            "valid_n": 2,
            "excluded": {}
          },
          "candidate_group_coverage": {
            "value": 1.0,
            "valid_n": 2,
            "excluded": {}
          },
          "prompt_group_coverage": {
            "value": 1.0,
            "valid_n": 2,
            "excluded": {}
          },
          "answer_point_coverage": {
            "value": 1.0,
            "valid_n": 2,
            "excluded": {}
          },
          "faithfulness": {
            "value": 1.0,
            "valid_n": 2,
            "excluded": {}
          },
          "absent_refusal_rate": {
            "value": null,
            "valid_n": 0,
            "excluded": {
              "answerable": 2
            }
          },
          "answerable_false_refusal_rate": {
            "value": 0.0,
            "valid_n": 2,
            "excluded": {}
          }
        }
      },
      {
        "bucket": "A_policy",
        "strategy": "hybrid_rerank",
        "total": 2,
        "attempted": 2,
        "completed": 2,
        "errors": 0,
        "not_attempted": 0,
        "status_counts": {
          "completed": 2,
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
            "valid_n": 2,
            "excluded": {}
          },
          "recall_at_10": {
            "value": 1.0,
            "valid_n": 2,
            "excluded": {}
          },
          "mrr_at_10": {
            "value": 1.0,
            "valid_n": 2,
            "excluded": {}
          },
          "all_groups_hit_at_5": {
            "value": 1.0,
            "valid_n": 2,
            "excluded": {}
          },
          "all_groups_hit_at_10": {
            "value": 1.0,
            "valid_n": 2,
            "excluded": {}
          },
          "candidate_group_coverage": {
            "value": 1.0,
            "valid_n": 2,
            "excluded": {}
          },
          "prompt_group_coverage": {
            "value": 1.0,
            "valid_n": 2,
            "excluded": {}
          },
          "answer_point_coverage": {
            "value": 0.75,
            "valid_n": 2,
            "excluded": {}
          },
          "faithfulness": {
            "value": 0.9375,
            "valid_n": 2,
            "excluded": {}
          },
          "absent_refusal_rate": {
            "value": null,
            "valid_n": 0,
            "excluded": {
              "answerable": 2
            }
          },
          "answerable_false_refusal_rate": {
            "value": 0.0,
            "valid_n": 2,
            "excluded": {}
          }
        }
      },
      {
        "bucket": "B_model",
        "strategy": "dense",
        "total": 2,
        "attempted": 2,
        "completed": 1,
        "errors": 1,
        "not_attempted": 0,
        "status_counts": {
          "completed": 1,
          "rewrite_error": 1,
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
            "valid_n": 1,
            "excluded": {
              "rewrite_error": 1
            }
          },
          "recall_at_10": {
            "value": 1.0,
            "valid_n": 1,
            "excluded": {
              "rewrite_error": 1
            }
          },
          "mrr_at_10": {
            "value": 1.0,
            "valid_n": 1,
            "excluded": {
              "rewrite_error": 1
            }
          },
          "all_groups_hit_at_5": {
            "value": 1.0,
            "valid_n": 1,
            "excluded": {
              "rewrite_error": 1
            }
          },
          "all_groups_hit_at_10": {
            "value": 1.0,
            "valid_n": 1,
            "excluded": {
              "rewrite_error": 1
            }
          },
          "candidate_group_coverage": {
            "value": 1.0,
            "valid_n": 1,
            "excluded": {
              "rewrite_error": 1
            }
          },
          "prompt_group_coverage": {
            "value": 1.0,
            "valid_n": 1,
            "excluded": {
              "rewrite_error": 1
            }
          },
          "answer_point_coverage": {
            "value": 1.0,
            "valid_n": 1,
            "excluded": {
              "rewrite_error": 1
            }
          },
          "faithfulness": {
            "value": 1.0,
            "valid_n": 1,
            "excluded": {
              "rewrite_error": 1
            }
          },
          "absent_refusal_rate": {
            "value": null,
            "valid_n": 0,
            "excluded": {
              "answerable": 2
            }
          },
          "answerable_false_refusal_rate": {
            "value": 0.0,
            "valid_n": 1,
            "excluded": {
              "rewrite_error": 1
            }
          }
        }
      },
      {
        "bucket": "B_model",
        "strategy": "bm25",
        "total": 2,
        "attempted": 2,
        "completed": 1,
        "errors": 1,
        "not_attempted": 0,
        "status_counts": {
          "completed": 1,
          "rewrite_error": 1,
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
            "valid_n": 1,
            "excluded": {
              "rewrite_error": 1
            }
          },
          "recall_at_10": {
            "value": 1.0,
            "valid_n": 1,
            "excluded": {
              "rewrite_error": 1
            }
          },
          "mrr_at_10": {
            "value": 1.0,
            "valid_n": 1,
            "excluded": {
              "rewrite_error": 1
            }
          },
          "all_groups_hit_at_5": {
            "value": 1.0,
            "valid_n": 1,
            "excluded": {
              "rewrite_error": 1
            }
          },
          "all_groups_hit_at_10": {
            "value": 1.0,
            "valid_n": 1,
            "excluded": {
              "rewrite_error": 1
            }
          },
          "candidate_group_coverage": {
            "value": 1.0,
            "valid_n": 1,
            "excluded": {
              "rewrite_error": 1
            }
          },
          "prompt_group_coverage": {
            "value": 1.0,
            "valid_n": 1,
            "excluded": {
              "rewrite_error": 1
            }
          },
          "answer_point_coverage": {
            "value": 1.0,
            "valid_n": 1,
            "excluded": {
              "rewrite_error": 1
            }
          },
          "faithfulness": {
            "value": 1.0,
            "valid_n": 1,
            "excluded": {
              "rewrite_error": 1
            }
          },
          "absent_refusal_rate": {
            "value": null,
            "valid_n": 0,
            "excluded": {
              "answerable": 2
            }
          },
          "answerable_false_refusal_rate": {
            "value": 0.0,
            "valid_n": 1,
            "excluded": {
              "rewrite_error": 1
            }
          }
        }
      },
      {
        "bucket": "B_model",
        "strategy": "hybrid",
        "total": 2,
        "attempted": 2,
        "completed": 1,
        "errors": 1,
        "not_attempted": 0,
        "status_counts": {
          "completed": 1,
          "rewrite_error": 1,
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
            "valid_n": 1,
            "excluded": {
              "rewrite_error": 1
            }
          },
          "recall_at_10": {
            "value": 1.0,
            "valid_n": 1,
            "excluded": {
              "rewrite_error": 1
            }
          },
          "mrr_at_10": {
            "value": 1.0,
            "valid_n": 1,
            "excluded": {
              "rewrite_error": 1
            }
          },
          "all_groups_hit_at_5": {
            "value": 1.0,
            "valid_n": 1,
            "excluded": {
              "rewrite_error": 1
            }
          },
          "all_groups_hit_at_10": {
            "value": 1.0,
            "valid_n": 1,
            "excluded": {
              "rewrite_error": 1
            }
          },
          "candidate_group_coverage": {
            "value": 1.0,
            "valid_n": 1,
            "excluded": {
              "rewrite_error": 1
            }
          },
          "prompt_group_coverage": {
            "value": 1.0,
            "valid_n": 1,
            "excluded": {
              "rewrite_error": 1
            }
          },
          "answer_point_coverage": {
            "value": 1.0,
            "valid_n": 1,
            "excluded": {
              "rewrite_error": 1
            }
          },
          "faithfulness": {
            "value": 1.0,
            "valid_n": 1,
            "excluded": {
              "rewrite_error": 1
            }
          },
          "absent_refusal_rate": {
            "value": null,
            "valid_n": 0,
            "excluded": {
              "answerable": 2
            }
          },
          "answerable_false_refusal_rate": {
            "value": 0.0,
            "valid_n": 1,
            "excluded": {
              "rewrite_error": 1
            }
          }
        }
      },
      {
        "bucket": "B_model",
        "strategy": "hybrid_rerank",
        "total": 2,
        "attempted": 2,
        "completed": 1,
        "errors": 1,
        "not_attempted": 0,
        "status_counts": {
          "completed": 1,
          "rewrite_error": 1,
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
            "valid_n": 1,
            "excluded": {
              "rewrite_error": 1
            }
          },
          "recall_at_10": {
            "value": 1.0,
            "valid_n": 1,
            "excluded": {
              "rewrite_error": 1
            }
          },
          "mrr_at_10": {
            "value": 1.0,
            "valid_n": 1,
            "excluded": {
              "rewrite_error": 1
            }
          },
          "all_groups_hit_at_5": {
            "value": 1.0,
            "valid_n": 1,
            "excluded": {
              "rewrite_error": 1
            }
          },
          "all_groups_hit_at_10": {
            "value": 1.0,
            "valid_n": 1,
            "excluded": {
              "rewrite_error": 1
            }
          },
          "candidate_group_coverage": {
            "value": 1.0,
            "valid_n": 1,
            "excluded": {
              "rewrite_error": 1
            }
          },
          "prompt_group_coverage": {
            "value": 1.0,
            "valid_n": 1,
            "excluded": {
              "rewrite_error": 1
            }
          },
          "answer_point_coverage": {
            "value": 1.0,
            "valid_n": 1,
            "excluded": {
              "rewrite_error": 1
            }
          },
          "faithfulness": {
            "value": 1.0,
            "valid_n": 1,
            "excluded": {
              "rewrite_error": 1
            }
          },
          "absent_refusal_rate": {
            "value": null,
            "valid_n": 0,
            "excluded": {
              "answerable": 2
            }
          },
          "answerable_false_refusal_rate": {
            "value": 0.0,
            "valid_n": 1,
            "excluded": {
              "rewrite_error": 1
            }
          }
        }
      },
      {
        "bucket": "C_colloquial",
        "strategy": "dense",
        "total": 2,
        "attempted": 2,
        "completed": 2,
        "errors": 0,
        "not_attempted": 0,
        "status_counts": {
          "completed": 2,
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
            "valid_n": 2,
            "excluded": {}
          },
          "recall_at_10": {
            "value": 1.0,
            "valid_n": 2,
            "excluded": {}
          },
          "mrr_at_10": {
            "value": 1.0,
            "valid_n": 2,
            "excluded": {}
          },
          "all_groups_hit_at_5": {
            "value": 1.0,
            "valid_n": 2,
            "excluded": {}
          },
          "all_groups_hit_at_10": {
            "value": 1.0,
            "valid_n": 2,
            "excluded": {}
          },
          "candidate_group_coverage": {
            "value": 1.0,
            "valid_n": 2,
            "excluded": {}
          },
          "prompt_group_coverage": {
            "value": 1.0,
            "valid_n": 2,
            "excluded": {}
          },
          "answer_point_coverage": {
            "value": 1.0,
            "valid_n": 2,
            "excluded": {}
          },
          "faithfulness": {
            "value": 1.0,
            "valid_n": 2,
            "excluded": {}
          },
          "absent_refusal_rate": {
            "value": null,
            "valid_n": 0,
            "excluded": {
              "answerable": 2
            }
          },
          "answerable_false_refusal_rate": {
            "value": 0.0,
            "valid_n": 2,
            "excluded": {}
          }
        }
      },
      {
        "bucket": "C_colloquial",
        "strategy": "bm25",
        "total": 2,
        "attempted": 2,
        "completed": 2,
        "errors": 0,
        "not_attempted": 0,
        "status_counts": {
          "completed": 2,
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
            "valid_n": 2,
            "excluded": {}
          },
          "recall_at_10": {
            "value": 1.0,
            "valid_n": 2,
            "excluded": {}
          },
          "mrr_at_10": {
            "value": 0.6666666666666666,
            "valid_n": 2,
            "excluded": {}
          },
          "all_groups_hit_at_5": {
            "value": 1.0,
            "valid_n": 2,
            "excluded": {}
          },
          "all_groups_hit_at_10": {
            "value": 1.0,
            "valid_n": 2,
            "excluded": {}
          },
          "candidate_group_coverage": {
            "value": 1.0,
            "valid_n": 2,
            "excluded": {}
          },
          "prompt_group_coverage": {
            "value": 1.0,
            "valid_n": 2,
            "excluded": {}
          },
          "answer_point_coverage": {
            "value": 1.0,
            "valid_n": 2,
            "excluded": {}
          },
          "faithfulness": {
            "value": 1.0,
            "valid_n": 2,
            "excluded": {}
          },
          "absent_refusal_rate": {
            "value": null,
            "valid_n": 0,
            "excluded": {
              "answerable": 2
            }
          },
          "answerable_false_refusal_rate": {
            "value": 0.0,
            "valid_n": 2,
            "excluded": {}
          }
        }
      },
      {
        "bucket": "C_colloquial",
        "strategy": "hybrid",
        "total": 2,
        "attempted": 2,
        "completed": 2,
        "errors": 0,
        "not_attempted": 0,
        "status_counts": {
          "completed": 2,
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
            "valid_n": 2,
            "excluded": {}
          },
          "recall_at_10": {
            "value": 1.0,
            "valid_n": 2,
            "excluded": {}
          },
          "mrr_at_10": {
            "value": 0.75,
            "valid_n": 2,
            "excluded": {}
          },
          "all_groups_hit_at_5": {
            "value": 1.0,
            "valid_n": 2,
            "excluded": {}
          },
          "all_groups_hit_at_10": {
            "value": 1.0,
            "valid_n": 2,
            "excluded": {}
          },
          "candidate_group_coverage": {
            "value": 1.0,
            "valid_n": 2,
            "excluded": {}
          },
          "prompt_group_coverage": {
            "value": 1.0,
            "valid_n": 2,
            "excluded": {}
          },
          "answer_point_coverage": {
            "value": 1.0,
            "valid_n": 2,
            "excluded": {}
          },
          "faithfulness": {
            "value": 0.8,
            "valid_n": 2,
            "excluded": {}
          },
          "absent_refusal_rate": {
            "value": null,
            "valid_n": 0,
            "excluded": {
              "answerable": 2
            }
          },
          "answerable_false_refusal_rate": {
            "value": 0.0,
            "valid_n": 2,
            "excluded": {}
          }
        }
      },
      {
        "bucket": "C_colloquial",
        "strategy": "hybrid_rerank",
        "total": 2,
        "attempted": 2,
        "completed": 2,
        "errors": 0,
        "not_attempted": 0,
        "status_counts": {
          "completed": 2,
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
            "valid_n": 2,
            "excluded": {}
          },
          "recall_at_10": {
            "value": 1.0,
            "valid_n": 2,
            "excluded": {}
          },
          "mrr_at_10": {
            "value": 1.0,
            "valid_n": 2,
            "excluded": {}
          },
          "all_groups_hit_at_5": {
            "value": 1.0,
            "valid_n": 2,
            "excluded": {}
          },
          "all_groups_hit_at_10": {
            "value": 1.0,
            "valid_n": 2,
            "excluded": {}
          },
          "candidate_group_coverage": {
            "value": 1.0,
            "valid_n": 2,
            "excluded": {}
          },
          "prompt_group_coverage": {
            "value": 1.0,
            "valid_n": 2,
            "excluded": {}
          },
          "answer_point_coverage": {
            "value": 1.0,
            "valid_n": 2,
            "excluded": {}
          },
          "faithfulness": {
            "value": 1.0,
            "valid_n": 2,
            "excluded": {}
          },
          "absent_refusal_rate": {
            "value": null,
            "valid_n": 0,
            "excluded": {
              "answerable": 2
            }
          },
          "answerable_false_refusal_rate": {
            "value": 0.0,
            "valid_n": 2,
            "excluded": {}
          }
        }
      },
      {
        "bucket": "D_unanswerable",
        "strategy": "dense",
        "total": 2,
        "attempted": 2,
        "completed": 2,
        "errors": 0,
        "not_attempted": 0,
        "status_counts": {
          "completed": 2,
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
              "expected_refusal": 2
            }
          },
          "recall_at_10": {
            "value": null,
            "valid_n": 0,
            "excluded": {
              "expected_refusal": 2
            }
          },
          "mrr_at_10": {
            "value": null,
            "valid_n": 0,
            "excluded": {
              "expected_refusal": 2
            }
          },
          "all_groups_hit_at_5": {
            "value": null,
            "valid_n": 0,
            "excluded": {
              "expected_refusal": 2
            }
          },
          "all_groups_hit_at_10": {
            "value": null,
            "valid_n": 0,
            "excluded": {
              "expected_refusal": 2
            }
          },
          "candidate_group_coverage": {
            "value": null,
            "valid_n": 0,
            "excluded": {
              "expected_refusal": 2
            }
          },
          "prompt_group_coverage": {
            "value": null,
            "valid_n": 0,
            "excluded": {
              "expected_refusal": 2
            }
          },
          "answer_point_coverage": {
            "value": null,
            "valid_n": 0,
            "excluded": {
              "expected_refusal": 2
            }
          },
          "faithfulness": {
            "value": 0.0,
            "valid_n": 1,
            "excluded": {
              "zero_claims": 1
            }
          },
          "absent_refusal_rate": {
            "value": 1.0,
            "valid_n": 2,
            "excluded": {}
          },
          "answerable_false_refusal_rate": {
            "value": null,
            "valid_n": 0,
            "excluded": {
              "expected_refusal": 2
            }
          }
        }
      },
      {
        "bucket": "D_unanswerable",
        "strategy": "bm25",
        "total": 2,
        "attempted": 2,
        "completed": 2,
        "errors": 0,
        "not_attempted": 0,
        "status_counts": {
          "completed": 2,
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
              "expected_refusal": 2
            }
          },
          "recall_at_10": {
            "value": null,
            "valid_n": 0,
            "excluded": {
              "expected_refusal": 2
            }
          },
          "mrr_at_10": {
            "value": null,
            "valid_n": 0,
            "excluded": {
              "expected_refusal": 2
            }
          },
          "all_groups_hit_at_5": {
            "value": null,
            "valid_n": 0,
            "excluded": {
              "expected_refusal": 2
            }
          },
          "all_groups_hit_at_10": {
            "value": null,
            "valid_n": 0,
            "excluded": {
              "expected_refusal": 2
            }
          },
          "candidate_group_coverage": {
            "value": null,
            "valid_n": 0,
            "excluded": {
              "expected_refusal": 2
            }
          },
          "prompt_group_coverage": {
            "value": null,
            "valid_n": 0,
            "excluded": {
              "expected_refusal": 2
            }
          },
          "answer_point_coverage": {
            "value": null,
            "valid_n": 0,
            "excluded": {
              "expected_refusal": 2
            }
          },
          "faithfulness": {
            "value": 1.0,
            "valid_n": 1,
            "excluded": {
              "zero_claims": 1
            }
          },
          "absent_refusal_rate": {
            "value": 1.0,
            "valid_n": 2,
            "excluded": {}
          },
          "answerable_false_refusal_rate": {
            "value": null,
            "valid_n": 0,
            "excluded": {
              "expected_refusal": 2
            }
          }
        }
      },
      {
        "bucket": "D_unanswerable",
        "strategy": "hybrid",
        "total": 2,
        "attempted": 2,
        "completed": 2,
        "errors": 0,
        "not_attempted": 0,
        "status_counts": {
          "completed": 2,
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
              "expected_refusal": 2
            }
          },
          "recall_at_10": {
            "value": null,
            "valid_n": 0,
            "excluded": {
              "expected_refusal": 2
            }
          },
          "mrr_at_10": {
            "value": null,
            "valid_n": 0,
            "excluded": {
              "expected_refusal": 2
            }
          },
          "all_groups_hit_at_5": {
            "value": null,
            "valid_n": 0,
            "excluded": {
              "expected_refusal": 2
            }
          },
          "all_groups_hit_at_10": {
            "value": null,
            "valid_n": 0,
            "excluded": {
              "expected_refusal": 2
            }
          },
          "candidate_group_coverage": {
            "value": null,
            "valid_n": 0,
            "excluded": {
              "expected_refusal": 2
            }
          },
          "prompt_group_coverage": {
            "value": null,
            "valid_n": 0,
            "excluded": {
              "expected_refusal": 2
            }
          },
          "answer_point_coverage": {
            "value": null,
            "valid_n": 0,
            "excluded": {
              "expected_refusal": 2
            }
          },
          "faithfulness": {
            "value": 0.0,
            "valid_n": 2,
            "excluded": {}
          },
          "absent_refusal_rate": {
            "value": 1.0,
            "valid_n": 2,
            "excluded": {}
          },
          "answerable_false_refusal_rate": {
            "value": null,
            "valid_n": 0,
            "excluded": {
              "expected_refusal": 2
            }
          }
        }
      },
      {
        "bucket": "D_unanswerable",
        "strategy": "hybrid_rerank",
        "total": 2,
        "attempted": 2,
        "completed": 2,
        "errors": 0,
        "not_attempted": 0,
        "status_counts": {
          "completed": 2,
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
              "expected_refusal": 2
            }
          },
          "recall_at_10": {
            "value": null,
            "valid_n": 0,
            "excluded": {
              "expected_refusal": 2
            }
          },
          "mrr_at_10": {
            "value": null,
            "valid_n": 0,
            "excluded": {
              "expected_refusal": 2
            }
          },
          "all_groups_hit_at_5": {
            "value": null,
            "valid_n": 0,
            "excluded": {
              "expected_refusal": 2
            }
          },
          "all_groups_hit_at_10": {
            "value": null,
            "valid_n": 0,
            "excluded": {
              "expected_refusal": 2
            }
          },
          "candidate_group_coverage": {
            "value": null,
            "valid_n": 0,
            "excluded": {
              "expected_refusal": 2
            }
          },
          "prompt_group_coverage": {
            "value": null,
            "valid_n": 0,
            "excluded": {
              "expected_refusal": 2
            }
          },
          "answer_point_coverage": {
            "value": null,
            "valid_n": 0,
            "excluded": {
              "expected_refusal": 2
            }
          },
          "faithfulness": {
            "value": 1.0,
            "valid_n": 1,
            "excluded": {
              "zero_claims": 1
            }
          },
          "absent_refusal_rate": {
            "value": 1.0,
            "valid_n": 2,
            "excluded": {}
          },
          "answerable_false_refusal_rate": {
            "value": null,
            "valid_n": 0,
            "excluded": {
              "expected_refusal": 2
            }
          }
        }
      },
      {
        "bucket": "E_multi",
        "strategy": "dense",
        "total": 2,
        "attempted": 2,
        "completed": 1,
        "errors": 1,
        "not_attempted": 0,
        "status_counts": {
          "completed": 1,
          "rewrite_error": 1,
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
            "valid_n": 1,
            "excluded": {
              "rewrite_error": 1
            }
          },
          "recall_at_10": {
            "value": 1.0,
            "valid_n": 1,
            "excluded": {
              "rewrite_error": 1
            }
          },
          "mrr_at_10": {
            "value": 1.0,
            "valid_n": 1,
            "excluded": {
              "rewrite_error": 1
            }
          },
          "all_groups_hit_at_5": {
            "value": 1.0,
            "valid_n": 1,
            "excluded": {
              "rewrite_error": 1
            }
          },
          "all_groups_hit_at_10": {
            "value": 1.0,
            "valid_n": 1,
            "excluded": {
              "rewrite_error": 1
            }
          },
          "candidate_group_coverage": {
            "value": 1.0,
            "valid_n": 1,
            "excluded": {
              "rewrite_error": 1
            }
          },
          "prompt_group_coverage": {
            "value": 1.0,
            "valid_n": 1,
            "excluded": {
              "rewrite_error": 1
            }
          },
          "answer_point_coverage": {
            "value": 1.0,
            "valid_n": 1,
            "excluded": {
              "rewrite_error": 1
            }
          },
          "faithfulness": {
            "value": 1.0,
            "valid_n": 1,
            "excluded": {
              "rewrite_error": 1
            }
          },
          "absent_refusal_rate": {
            "value": null,
            "valid_n": 0,
            "excluded": {
              "answerable": 2
            }
          },
          "answerable_false_refusal_rate": {
            "value": 0.0,
            "valid_n": 1,
            "excluded": {
              "rewrite_error": 1
            }
          }
        }
      },
      {
        "bucket": "E_multi",
        "strategy": "bm25",
        "total": 2,
        "attempted": 2,
        "completed": 1,
        "errors": 1,
        "not_attempted": 0,
        "status_counts": {
          "completed": 1,
          "rewrite_error": 1,
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
            "value": 0.3333333333333333,
            "valid_n": 1,
            "excluded": {
              "rewrite_error": 1
            }
          },
          "recall_at_10": {
            "value": 0.6666666666666666,
            "valid_n": 1,
            "excluded": {
              "rewrite_error": 1
            }
          },
          "mrr_at_10": {
            "value": 1.0,
            "valid_n": 1,
            "excluded": {
              "rewrite_error": 1
            }
          },
          "all_groups_hit_at_5": {
            "value": 0.0,
            "valid_n": 1,
            "excluded": {
              "rewrite_error": 1
            }
          },
          "all_groups_hit_at_10": {
            "value": 0.0,
            "valid_n": 1,
            "excluded": {
              "rewrite_error": 1
            }
          },
          "candidate_group_coverage": {
            "value": 1.0,
            "valid_n": 1,
            "excluded": {
              "rewrite_error": 1
            }
          },
          "prompt_group_coverage": {
            "value": 0.6666666666666666,
            "valid_n": 1,
            "excluded": {
              "rewrite_error": 1
            }
          },
          "answer_point_coverage": {
            "value": 0.0,
            "valid_n": 1,
            "excluded": {
              "rewrite_error": 1
            }
          },
          "faithfulness": {
            "value": null,
            "valid_n": 0,
            "excluded": {
              "rewrite_error": 1,
              "zero_claims": 1
            }
          },
          "absent_refusal_rate": {
            "value": null,
            "valid_n": 0,
            "excluded": {
              "answerable": 2
            }
          },
          "answerable_false_refusal_rate": {
            "value": 1.0,
            "valid_n": 1,
            "excluded": {
              "rewrite_error": 1
            }
          }
        }
      },
      {
        "bucket": "E_multi",
        "strategy": "hybrid",
        "total": 2,
        "attempted": 2,
        "completed": 1,
        "errors": 1,
        "not_attempted": 0,
        "status_counts": {
          "completed": 1,
          "rewrite_error": 1,
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
            "value": 0.6666666666666666,
            "valid_n": 1,
            "excluded": {
              "rewrite_error": 1
            }
          },
          "recall_at_10": {
            "value": 1.0,
            "valid_n": 1,
            "excluded": {
              "rewrite_error": 1
            }
          },
          "mrr_at_10": {
            "value": 1.0,
            "valid_n": 1,
            "excluded": {
              "rewrite_error": 1
            }
          },
          "all_groups_hit_at_5": {
            "value": 0.0,
            "valid_n": 1,
            "excluded": {
              "rewrite_error": 1
            }
          },
          "all_groups_hit_at_10": {
            "value": 1.0,
            "valid_n": 1,
            "excluded": {
              "rewrite_error": 1
            }
          },
          "candidate_group_coverage": {
            "value": 1.0,
            "valid_n": 1,
            "excluded": {
              "rewrite_error": 1
            }
          },
          "prompt_group_coverage": {
            "value": 1.0,
            "valid_n": 1,
            "excluded": {
              "rewrite_error": 1
            }
          },
          "answer_point_coverage": {
            "value": 1.0,
            "valid_n": 1,
            "excluded": {
              "rewrite_error": 1
            }
          },
          "faithfulness": {
            "value": 1.0,
            "valid_n": 1,
            "excluded": {
              "rewrite_error": 1
            }
          },
          "absent_refusal_rate": {
            "value": null,
            "valid_n": 0,
            "excluded": {
              "answerable": 2
            }
          },
          "answerable_false_refusal_rate": {
            "value": 0.0,
            "valid_n": 1,
            "excluded": {
              "rewrite_error": 1
            }
          }
        }
      },
      {
        "bucket": "E_multi",
        "strategy": "hybrid_rerank",
        "total": 2,
        "attempted": 2,
        "completed": 1,
        "errors": 1,
        "not_attempted": 0,
        "status_counts": {
          "completed": 1,
          "rewrite_error": 1,
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
            "valid_n": 1,
            "excluded": {
              "rewrite_error": 1
            }
          },
          "recall_at_10": {
            "value": 1.0,
            "valid_n": 1,
            "excluded": {
              "rewrite_error": 1
            }
          },
          "mrr_at_10": {
            "value": 1.0,
            "valid_n": 1,
            "excluded": {
              "rewrite_error": 1
            }
          },
          "all_groups_hit_at_5": {
            "value": 1.0,
            "valid_n": 1,
            "excluded": {
              "rewrite_error": 1
            }
          },
          "all_groups_hit_at_10": {
            "value": 1.0,
            "valid_n": 1,
            "excluded": {
              "rewrite_error": 1
            }
          },
          "candidate_group_coverage": {
            "value": 1.0,
            "valid_n": 1,
            "excluded": {
              "rewrite_error": 1
            }
          },
          "prompt_group_coverage": {
            "value": 1.0,
            "valid_n": 1,
            "excluded": {
              "rewrite_error": 1
            }
          },
          "answer_point_coverage": {
            "value": 0.6666666666666666,
            "valid_n": 1,
            "excluded": {
              "rewrite_error": 1
            }
          },
          "faithfulness": {
            "value": 1.0,
            "valid_n": 1,
            "excluded": {
              "rewrite_error": 1
            }
          },
          "absent_refusal_rate": {
            "value": null,
            "valid_n": 0,
            "excluded": {
              "answerable": 2
            }
          },
          "answerable_false_refusal_rate": {
            "value": 0.0,
            "valid_n": 1,
            "excluded": {
              "rewrite_error": 1
            }
          }
        }
      }
    ],
    "common_generation": {
      "eval_ids": [
        "A21",
        "A43",
        "B3",
        "C35",
        "C5",
        "D1",
        "D3",
        "E2"
      ],
      "valid_n": 8,
      "rows": [
        {
          "bucket": "overall",
          "strategy": "dense",
          "total": 8,
          "attempted": 8,
          "completed": 8,
          "errors": 0,
          "not_attempted": 0,
          "status_counts": {
            "completed": 8,
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
              "valid_n": 6,
              "excluded": {
                "expected_refusal": 2
              }
            },
            "recall_at_10": {
              "value": 1.0,
              "valid_n": 6,
              "excluded": {
                "expected_refusal": 2
              }
            },
            "mrr_at_10": {
              "value": 1.0,
              "valid_n": 6,
              "excluded": {
                "expected_refusal": 2
              }
            },
            "all_groups_hit_at_5": {
              "value": 1.0,
              "valid_n": 6,
              "excluded": {
                "expected_refusal": 2
              }
            },
            "all_groups_hit_at_10": {
              "value": 1.0,
              "valid_n": 6,
              "excluded": {
                "expected_refusal": 2
              }
            },
            "candidate_group_coverage": {
              "value": 1.0,
              "valid_n": 6,
              "excluded": {
                "expected_refusal": 2
              }
            },
            "prompt_group_coverage": {
              "value": 1.0,
              "valid_n": 6,
              "excluded": {
                "expected_refusal": 2
              }
            },
            "answer_point_coverage": {
              "value": 1.0,
              "valid_n": 6,
              "excluded": {
                "expected_refusal": 2
              }
            },
            "faithfulness": {
              "value": 0.8571428571428571,
              "valid_n": 7,
              "excluded": {
                "zero_claims": 1
              }
            },
            "absent_refusal_rate": {
              "value": 1.0,
              "valid_n": 2,
              "excluded": {
                "answerable": 6
              }
            },
            "answerable_false_refusal_rate": {
              "value": 0.0,
              "valid_n": 6,
              "excluded": {
                "expected_refusal": 2
              }
            }
          }
        },
        {
          "bucket": "overall",
          "strategy": "bm25",
          "total": 8,
          "attempted": 8,
          "completed": 8,
          "errors": 0,
          "not_attempted": 0,
          "status_counts": {
            "completed": 8,
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
              "value": 0.8888888888888888,
              "valid_n": 6,
              "excluded": {
                "expected_refusal": 2
              }
            },
            "recall_at_10": {
              "value": 0.9444444444444445,
              "valid_n": 6,
              "excluded": {
                "expected_refusal": 2
              }
            },
            "mrr_at_10": {
              "value": 0.8888888888888888,
              "valid_n": 6,
              "excluded": {
                "expected_refusal": 2
              }
            },
            "all_groups_hit_at_5": {
              "value": 0.8333333333333334,
              "valid_n": 6,
              "excluded": {
                "expected_refusal": 2
              }
            },
            "all_groups_hit_at_10": {
              "value": 0.8333333333333334,
              "valid_n": 6,
              "excluded": {
                "expected_refusal": 2
              }
            },
            "candidate_group_coverage": {
              "value": 1.0,
              "valid_n": 6,
              "excluded": {
                "expected_refusal": 2
              }
            },
            "prompt_group_coverage": {
              "value": 0.9444444444444445,
              "valid_n": 6,
              "excluded": {
                "expected_refusal": 2
              }
            },
            "answer_point_coverage": {
              "value": 0.6666666666666666,
              "valid_n": 6,
              "excluded": {
                "expected_refusal": 2
              }
            },
            "faithfulness": {
              "value": 1.0,
              "valid_n": 5,
              "excluded": {
                "zero_claims": 3
              }
            },
            "absent_refusal_rate": {
              "value": 1.0,
              "valid_n": 2,
              "excluded": {
                "answerable": 6
              }
            },
            "answerable_false_refusal_rate": {
              "value": 0.3333333333333333,
              "valid_n": 6,
              "excluded": {
                "expected_refusal": 2
              }
            }
          }
        },
        {
          "bucket": "overall",
          "strategy": "hybrid",
          "total": 8,
          "attempted": 8,
          "completed": 8,
          "errors": 0,
          "not_attempted": 0,
          "status_counts": {
            "completed": 8,
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
              "value": 0.9444444444444445,
              "valid_n": 6,
              "excluded": {
                "expected_refusal": 2
              }
            },
            "recall_at_10": {
              "value": 1.0,
              "valid_n": 6,
              "excluded": {
                "expected_refusal": 2
              }
            },
            "mrr_at_10": {
              "value": 0.9166666666666666,
              "valid_n": 6,
              "excluded": {
                "expected_refusal": 2
              }
            },
            "all_groups_hit_at_5": {
              "value": 0.8333333333333334,
              "valid_n": 6,
              "excluded": {
                "expected_refusal": 2
              }
            },
            "all_groups_hit_at_10": {
              "value": 1.0,
              "valid_n": 6,
              "excluded": {
                "expected_refusal": 2
              }
            },
            "candidate_group_coverage": {
              "value": 1.0,
              "valid_n": 6,
              "excluded": {
                "expected_refusal": 2
              }
            },
            "prompt_group_coverage": {
              "value": 1.0,
              "valid_n": 6,
              "excluded": {
                "expected_refusal": 2
              }
            },
            "answer_point_coverage": {
              "value": 1.0,
              "valid_n": 6,
              "excluded": {
                "expected_refusal": 2
              }
            },
            "faithfulness": {
              "value": 0.7,
              "valid_n": 8,
              "excluded": {}
            },
            "absent_refusal_rate": {
              "value": 1.0,
              "valid_n": 2,
              "excluded": {
                "answerable": 6
              }
            },
            "answerable_false_refusal_rate": {
              "value": 0.0,
              "valid_n": 6,
              "excluded": {
                "expected_refusal": 2
              }
            }
          }
        },
        {
          "bucket": "overall",
          "strategy": "hybrid_rerank",
          "total": 8,
          "attempted": 8,
          "completed": 8,
          "errors": 0,
          "not_attempted": 0,
          "status_counts": {
            "completed": 8,
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
              "valid_n": 6,
              "excluded": {
                "expected_refusal": 2
              }
            },
            "recall_at_10": {
              "value": 1.0,
              "valid_n": 6,
              "excluded": {
                "expected_refusal": 2
              }
            },
            "mrr_at_10": {
              "value": 1.0,
              "valid_n": 6,
              "excluded": {
                "expected_refusal": 2
              }
            },
            "all_groups_hit_at_5": {
              "value": 1.0,
              "valid_n": 6,
              "excluded": {
                "expected_refusal": 2
              }
            },
            "all_groups_hit_at_10": {
              "value": 1.0,
              "valid_n": 6,
              "excluded": {
                "expected_refusal": 2
              }
            },
            "candidate_group_coverage": {
              "value": 1.0,
              "valid_n": 6,
              "excluded": {
                "expected_refusal": 2
              }
            },
            "prompt_group_coverage": {
              "value": 1.0,
              "valid_n": 6,
              "excluded": {
                "expected_refusal": 2
              }
            },
            "answer_point_coverage": {
              "value": 0.8611111111111112,
              "valid_n": 6,
              "excluded": {
                "expected_refusal": 2
              }
            },
            "faithfulness": {
              "value": 0.9821428571428571,
              "valid_n": 7,
              "excluded": {
                "zero_claims": 1
              }
            },
            "absent_refusal_rate": {
              "value": 1.0,
              "valid_n": 2,
              "excluded": {
                "answerable": 6
              }
            },
            "answerable_false_refusal_rate": {
              "value": 0.0,
              "valid_n": 6,
              "excluded": {
                "expected_refusal": 2
              }
            }
          }
        },
        {
          "bucket": "A_policy",
          "strategy": "dense",
          "total": 2,
          "attempted": 2,
          "completed": 2,
          "errors": 0,
          "not_attempted": 0,
          "status_counts": {
            "completed": 2,
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
              "valid_n": 2,
              "excluded": {}
            },
            "recall_at_10": {
              "value": 1.0,
              "valid_n": 2,
              "excluded": {}
            },
            "mrr_at_10": {
              "value": 1.0,
              "valid_n": 2,
              "excluded": {}
            },
            "all_groups_hit_at_5": {
              "value": 1.0,
              "valid_n": 2,
              "excluded": {}
            },
            "all_groups_hit_at_10": {
              "value": 1.0,
              "valid_n": 2,
              "excluded": {}
            },
            "candidate_group_coverage": {
              "value": 1.0,
              "valid_n": 2,
              "excluded": {}
            },
            "prompt_group_coverage": {
              "value": 1.0,
              "valid_n": 2,
              "excluded": {}
            },
            "answer_point_coverage": {
              "value": 1.0,
              "valid_n": 2,
              "excluded": {}
            },
            "faithfulness": {
              "value": 1.0,
              "valid_n": 2,
              "excluded": {}
            },
            "absent_refusal_rate": {
              "value": null,
              "valid_n": 0,
              "excluded": {
                "answerable": 2
              }
            },
            "answerable_false_refusal_rate": {
              "value": 0.0,
              "valid_n": 2,
              "excluded": {}
            }
          }
        },
        {
          "bucket": "A_policy",
          "strategy": "bm25",
          "total": 2,
          "attempted": 2,
          "completed": 2,
          "errors": 0,
          "not_attempted": 0,
          "status_counts": {
            "completed": 2,
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
              "valid_n": 2,
              "excluded": {}
            },
            "recall_at_10": {
              "value": 1.0,
              "valid_n": 2,
              "excluded": {}
            },
            "mrr_at_10": {
              "value": 1.0,
              "valid_n": 2,
              "excluded": {}
            },
            "all_groups_hit_at_5": {
              "value": 1.0,
              "valid_n": 2,
              "excluded": {}
            },
            "all_groups_hit_at_10": {
              "value": 1.0,
              "valid_n": 2,
              "excluded": {}
            },
            "candidate_group_coverage": {
              "value": 1.0,
              "valid_n": 2,
              "excluded": {}
            },
            "prompt_group_coverage": {
              "value": 1.0,
              "valid_n": 2,
              "excluded": {}
            },
            "answer_point_coverage": {
              "value": 0.5,
              "valid_n": 2,
              "excluded": {}
            },
            "faithfulness": {
              "value": 1.0,
              "valid_n": 1,
              "excluded": {
                "zero_claims": 1
              }
            },
            "absent_refusal_rate": {
              "value": null,
              "valid_n": 0,
              "excluded": {
                "answerable": 2
              }
            },
            "answerable_false_refusal_rate": {
              "value": 0.5,
              "valid_n": 2,
              "excluded": {}
            }
          }
        },
        {
          "bucket": "A_policy",
          "strategy": "hybrid",
          "total": 2,
          "attempted": 2,
          "completed": 2,
          "errors": 0,
          "not_attempted": 0,
          "status_counts": {
            "completed": 2,
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
              "valid_n": 2,
              "excluded": {}
            },
            "recall_at_10": {
              "value": 1.0,
              "valid_n": 2,
              "excluded": {}
            },
            "mrr_at_10": {
              "value": 1.0,
              "valid_n": 2,
              "excluded": {}
            },
            "all_groups_hit_at_5": {
              "value": 1.0,
              "valid_n": 2,
              "excluded": {}
            },
            "all_groups_hit_at_10": {
              "value": 1.0,
              "valid_n": 2,
              "excluded": {}
            },
            "candidate_group_coverage": {
              "value": 1.0,
              "valid_n": 2,
              "excluded": {}
            },
            "prompt_group_coverage": {
              "value": 1.0,
              "valid_n": 2,
              "excluded": {}
            },
            "answer_point_coverage": {
              "value": 1.0,
              "valid_n": 2,
              "excluded": {}
            },
            "faithfulness": {
              "value": 1.0,
              "valid_n": 2,
              "excluded": {}
            },
            "absent_refusal_rate": {
              "value": null,
              "valid_n": 0,
              "excluded": {
                "answerable": 2
              }
            },
            "answerable_false_refusal_rate": {
              "value": 0.0,
              "valid_n": 2,
              "excluded": {}
            }
          }
        },
        {
          "bucket": "A_policy",
          "strategy": "hybrid_rerank",
          "total": 2,
          "attempted": 2,
          "completed": 2,
          "errors": 0,
          "not_attempted": 0,
          "status_counts": {
            "completed": 2,
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
              "valid_n": 2,
              "excluded": {}
            },
            "recall_at_10": {
              "value": 1.0,
              "valid_n": 2,
              "excluded": {}
            },
            "mrr_at_10": {
              "value": 1.0,
              "valid_n": 2,
              "excluded": {}
            },
            "all_groups_hit_at_5": {
              "value": 1.0,
              "valid_n": 2,
              "excluded": {}
            },
            "all_groups_hit_at_10": {
              "value": 1.0,
              "valid_n": 2,
              "excluded": {}
            },
            "candidate_group_coverage": {
              "value": 1.0,
              "valid_n": 2,
              "excluded": {}
            },
            "prompt_group_coverage": {
              "value": 1.0,
              "valid_n": 2,
              "excluded": {}
            },
            "answer_point_coverage": {
              "value": 0.75,
              "valid_n": 2,
              "excluded": {}
            },
            "faithfulness": {
              "value": 0.9375,
              "valid_n": 2,
              "excluded": {}
            },
            "absent_refusal_rate": {
              "value": null,
              "valid_n": 0,
              "excluded": {
                "answerable": 2
              }
            },
            "answerable_false_refusal_rate": {
              "value": 0.0,
              "valid_n": 2,
              "excluded": {}
            }
          }
        },
        {
          "bucket": "B_model",
          "strategy": "dense",
          "total": 1,
          "attempted": 1,
          "completed": 1,
          "errors": 0,
          "not_attempted": 0,
          "status_counts": {
            "completed": 1,
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
              "valid_n": 1,
              "excluded": {}
            },
            "recall_at_10": {
              "value": 1.0,
              "valid_n": 1,
              "excluded": {}
            },
            "mrr_at_10": {
              "value": 1.0,
              "valid_n": 1,
              "excluded": {}
            },
            "all_groups_hit_at_5": {
              "value": 1.0,
              "valid_n": 1,
              "excluded": {}
            },
            "all_groups_hit_at_10": {
              "value": 1.0,
              "valid_n": 1,
              "excluded": {}
            },
            "candidate_group_coverage": {
              "value": 1.0,
              "valid_n": 1,
              "excluded": {}
            },
            "prompt_group_coverage": {
              "value": 1.0,
              "valid_n": 1,
              "excluded": {}
            },
            "answer_point_coverage": {
              "value": 1.0,
              "valid_n": 1,
              "excluded": {}
            },
            "faithfulness": {
              "value": 1.0,
              "valid_n": 1,
              "excluded": {}
            },
            "absent_refusal_rate": {
              "value": null,
              "valid_n": 0,
              "excluded": {
                "answerable": 1
              }
            },
            "answerable_false_refusal_rate": {
              "value": 0.0,
              "valid_n": 1,
              "excluded": {}
            }
          }
        },
        {
          "bucket": "B_model",
          "strategy": "bm25",
          "total": 1,
          "attempted": 1,
          "completed": 1,
          "errors": 0,
          "not_attempted": 0,
          "status_counts": {
            "completed": 1,
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
              "valid_n": 1,
              "excluded": {}
            },
            "recall_at_10": {
              "value": 1.0,
              "valid_n": 1,
              "excluded": {}
            },
            "mrr_at_10": {
              "value": 1.0,
              "valid_n": 1,
              "excluded": {}
            },
            "all_groups_hit_at_5": {
              "value": 1.0,
              "valid_n": 1,
              "excluded": {}
            },
            "all_groups_hit_at_10": {
              "value": 1.0,
              "valid_n": 1,
              "excluded": {}
            },
            "candidate_group_coverage": {
              "value": 1.0,
              "valid_n": 1,
              "excluded": {}
            },
            "prompt_group_coverage": {
              "value": 1.0,
              "valid_n": 1,
              "excluded": {}
            },
            "answer_point_coverage": {
              "value": 1.0,
              "valid_n": 1,
              "excluded": {}
            },
            "faithfulness": {
              "value": 1.0,
              "valid_n": 1,
              "excluded": {}
            },
            "absent_refusal_rate": {
              "value": null,
              "valid_n": 0,
              "excluded": {
                "answerable": 1
              }
            },
            "answerable_false_refusal_rate": {
              "value": 0.0,
              "valid_n": 1,
              "excluded": {}
            }
          }
        },
        {
          "bucket": "B_model",
          "strategy": "hybrid",
          "total": 1,
          "attempted": 1,
          "completed": 1,
          "errors": 0,
          "not_attempted": 0,
          "status_counts": {
            "completed": 1,
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
              "valid_n": 1,
              "excluded": {}
            },
            "recall_at_10": {
              "value": 1.0,
              "valid_n": 1,
              "excluded": {}
            },
            "mrr_at_10": {
              "value": 1.0,
              "valid_n": 1,
              "excluded": {}
            },
            "all_groups_hit_at_5": {
              "value": 1.0,
              "valid_n": 1,
              "excluded": {}
            },
            "all_groups_hit_at_10": {
              "value": 1.0,
              "valid_n": 1,
              "excluded": {}
            },
            "candidate_group_coverage": {
              "value": 1.0,
              "valid_n": 1,
              "excluded": {}
            },
            "prompt_group_coverage": {
              "value": 1.0,
              "valid_n": 1,
              "excluded": {}
            },
            "answer_point_coverage": {
              "value": 1.0,
              "valid_n": 1,
              "excluded": {}
            },
            "faithfulness": {
              "value": 1.0,
              "valid_n": 1,
              "excluded": {}
            },
            "absent_refusal_rate": {
              "value": null,
              "valid_n": 0,
              "excluded": {
                "answerable": 1
              }
            },
            "answerable_false_refusal_rate": {
              "value": 0.0,
              "valid_n": 1,
              "excluded": {}
            }
          }
        },
        {
          "bucket": "B_model",
          "strategy": "hybrid_rerank",
          "total": 1,
          "attempted": 1,
          "completed": 1,
          "errors": 0,
          "not_attempted": 0,
          "status_counts": {
            "completed": 1,
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
              "valid_n": 1,
              "excluded": {}
            },
            "recall_at_10": {
              "value": 1.0,
              "valid_n": 1,
              "excluded": {}
            },
            "mrr_at_10": {
              "value": 1.0,
              "valid_n": 1,
              "excluded": {}
            },
            "all_groups_hit_at_5": {
              "value": 1.0,
              "valid_n": 1,
              "excluded": {}
            },
            "all_groups_hit_at_10": {
              "value": 1.0,
              "valid_n": 1,
              "excluded": {}
            },
            "candidate_group_coverage": {
              "value": 1.0,
              "valid_n": 1,
              "excluded": {}
            },
            "prompt_group_coverage": {
              "value": 1.0,
              "valid_n": 1,
              "excluded": {}
            },
            "answer_point_coverage": {
              "value": 1.0,
              "valid_n": 1,
              "excluded": {}
            },
            "faithfulness": {
              "value": 1.0,
              "valid_n": 1,
              "excluded": {}
            },
            "absent_refusal_rate": {
              "value": null,
              "valid_n": 0,
              "excluded": {
                "answerable": 1
              }
            },
            "answerable_false_refusal_rate": {
              "value": 0.0,
              "valid_n": 1,
              "excluded": {}
            }
          }
        },
        {
          "bucket": "C_colloquial",
          "strategy": "dense",
          "total": 2,
          "attempted": 2,
          "completed": 2,
          "errors": 0,
          "not_attempted": 0,
          "status_counts": {
            "completed": 2,
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
              "valid_n": 2,
              "excluded": {}
            },
            "recall_at_10": {
              "value": 1.0,
              "valid_n": 2,
              "excluded": {}
            },
            "mrr_at_10": {
              "value": 1.0,
              "valid_n": 2,
              "excluded": {}
            },
            "all_groups_hit_at_5": {
              "value": 1.0,
              "valid_n": 2,
              "excluded": {}
            },
            "all_groups_hit_at_10": {
              "value": 1.0,
              "valid_n": 2,
              "excluded": {}
            },
            "candidate_group_coverage": {
              "value": 1.0,
              "valid_n": 2,
              "excluded": {}
            },
            "prompt_group_coverage": {
              "value": 1.0,
              "valid_n": 2,
              "excluded": {}
            },
            "answer_point_coverage": {
              "value": 1.0,
              "valid_n": 2,
              "excluded": {}
            },
            "faithfulness": {
              "value": 1.0,
              "valid_n": 2,
              "excluded": {}
            },
            "absent_refusal_rate": {
              "value": null,
              "valid_n": 0,
              "excluded": {
                "answerable": 2
              }
            },
            "answerable_false_refusal_rate": {
              "value": 0.0,
              "valid_n": 2,
              "excluded": {}
            }
          }
        },
        {
          "bucket": "C_colloquial",
          "strategy": "bm25",
          "total": 2,
          "attempted": 2,
          "completed": 2,
          "errors": 0,
          "not_attempted": 0,
          "status_counts": {
            "completed": 2,
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
              "valid_n": 2,
              "excluded": {}
            },
            "recall_at_10": {
              "value": 1.0,
              "valid_n": 2,
              "excluded": {}
            },
            "mrr_at_10": {
              "value": 0.6666666666666666,
              "valid_n": 2,
              "excluded": {}
            },
            "all_groups_hit_at_5": {
              "value": 1.0,
              "valid_n": 2,
              "excluded": {}
            },
            "all_groups_hit_at_10": {
              "value": 1.0,
              "valid_n": 2,
              "excluded": {}
            },
            "candidate_group_coverage": {
              "value": 1.0,
              "valid_n": 2,
              "excluded": {}
            },
            "prompt_group_coverage": {
              "value": 1.0,
              "valid_n": 2,
              "excluded": {}
            },
            "answer_point_coverage": {
              "value": 1.0,
              "valid_n": 2,
              "excluded": {}
            },
            "faithfulness": {
              "value": 1.0,
              "valid_n": 2,
              "excluded": {}
            },
            "absent_refusal_rate": {
              "value": null,
              "valid_n": 0,
              "excluded": {
                "answerable": 2
              }
            },
            "answerable_false_refusal_rate": {
              "value": 0.0,
              "valid_n": 2,
              "excluded": {}
            }
          }
        },
        {
          "bucket": "C_colloquial",
          "strategy": "hybrid",
          "total": 2,
          "attempted": 2,
          "completed": 2,
          "errors": 0,
          "not_attempted": 0,
          "status_counts": {
            "completed": 2,
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
              "valid_n": 2,
              "excluded": {}
            },
            "recall_at_10": {
              "value": 1.0,
              "valid_n": 2,
              "excluded": {}
            },
            "mrr_at_10": {
              "value": 0.75,
              "valid_n": 2,
              "excluded": {}
            },
            "all_groups_hit_at_5": {
              "value": 1.0,
              "valid_n": 2,
              "excluded": {}
            },
            "all_groups_hit_at_10": {
              "value": 1.0,
              "valid_n": 2,
              "excluded": {}
            },
            "candidate_group_coverage": {
              "value": 1.0,
              "valid_n": 2,
              "excluded": {}
            },
            "prompt_group_coverage": {
              "value": 1.0,
              "valid_n": 2,
              "excluded": {}
            },
            "answer_point_coverage": {
              "value": 1.0,
              "valid_n": 2,
              "excluded": {}
            },
            "faithfulness": {
              "value": 0.8,
              "valid_n": 2,
              "excluded": {}
            },
            "absent_refusal_rate": {
              "value": null,
              "valid_n": 0,
              "excluded": {
                "answerable": 2
              }
            },
            "answerable_false_refusal_rate": {
              "value": 0.0,
              "valid_n": 2,
              "excluded": {}
            }
          }
        },
        {
          "bucket": "C_colloquial",
          "strategy": "hybrid_rerank",
          "total": 2,
          "attempted": 2,
          "completed": 2,
          "errors": 0,
          "not_attempted": 0,
          "status_counts": {
            "completed": 2,
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
              "valid_n": 2,
              "excluded": {}
            },
            "recall_at_10": {
              "value": 1.0,
              "valid_n": 2,
              "excluded": {}
            },
            "mrr_at_10": {
              "value": 1.0,
              "valid_n": 2,
              "excluded": {}
            },
            "all_groups_hit_at_5": {
              "value": 1.0,
              "valid_n": 2,
              "excluded": {}
            },
            "all_groups_hit_at_10": {
              "value": 1.0,
              "valid_n": 2,
              "excluded": {}
            },
            "candidate_group_coverage": {
              "value": 1.0,
              "valid_n": 2,
              "excluded": {}
            },
            "prompt_group_coverage": {
              "value": 1.0,
              "valid_n": 2,
              "excluded": {}
            },
            "answer_point_coverage": {
              "value": 1.0,
              "valid_n": 2,
              "excluded": {}
            },
            "faithfulness": {
              "value": 1.0,
              "valid_n": 2,
              "excluded": {}
            },
            "absent_refusal_rate": {
              "value": null,
              "valid_n": 0,
              "excluded": {
                "answerable": 2
              }
            },
            "answerable_false_refusal_rate": {
              "value": 0.0,
              "valid_n": 2,
              "excluded": {}
            }
          }
        },
        {
          "bucket": "D_unanswerable",
          "strategy": "dense",
          "total": 2,
          "attempted": 2,
          "completed": 2,
          "errors": 0,
          "not_attempted": 0,
          "status_counts": {
            "completed": 2,
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
                "expected_refusal": 2
              }
            },
            "recall_at_10": {
              "value": null,
              "valid_n": 0,
              "excluded": {
                "expected_refusal": 2
              }
            },
            "mrr_at_10": {
              "value": null,
              "valid_n": 0,
              "excluded": {
                "expected_refusal": 2
              }
            },
            "all_groups_hit_at_5": {
              "value": null,
              "valid_n": 0,
              "excluded": {
                "expected_refusal": 2
              }
            },
            "all_groups_hit_at_10": {
              "value": null,
              "valid_n": 0,
              "excluded": {
                "expected_refusal": 2
              }
            },
            "candidate_group_coverage": {
              "value": null,
              "valid_n": 0,
              "excluded": {
                "expected_refusal": 2
              }
            },
            "prompt_group_coverage": {
              "value": null,
              "valid_n": 0,
              "excluded": {
                "expected_refusal": 2
              }
            },
            "answer_point_coverage": {
              "value": null,
              "valid_n": 0,
              "excluded": {
                "expected_refusal": 2
              }
            },
            "faithfulness": {
              "value": 0.0,
              "valid_n": 1,
              "excluded": {
                "zero_claims": 1
              }
            },
            "absent_refusal_rate": {
              "value": 1.0,
              "valid_n": 2,
              "excluded": {}
            },
            "answerable_false_refusal_rate": {
              "value": null,
              "valid_n": 0,
              "excluded": {
                "expected_refusal": 2
              }
            }
          }
        },
        {
          "bucket": "D_unanswerable",
          "strategy": "bm25",
          "total": 2,
          "attempted": 2,
          "completed": 2,
          "errors": 0,
          "not_attempted": 0,
          "status_counts": {
            "completed": 2,
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
                "expected_refusal": 2
              }
            },
            "recall_at_10": {
              "value": null,
              "valid_n": 0,
              "excluded": {
                "expected_refusal": 2
              }
            },
            "mrr_at_10": {
              "value": null,
              "valid_n": 0,
              "excluded": {
                "expected_refusal": 2
              }
            },
            "all_groups_hit_at_5": {
              "value": null,
              "valid_n": 0,
              "excluded": {
                "expected_refusal": 2
              }
            },
            "all_groups_hit_at_10": {
              "value": null,
              "valid_n": 0,
              "excluded": {
                "expected_refusal": 2
              }
            },
            "candidate_group_coverage": {
              "value": null,
              "valid_n": 0,
              "excluded": {
                "expected_refusal": 2
              }
            },
            "prompt_group_coverage": {
              "value": null,
              "valid_n": 0,
              "excluded": {
                "expected_refusal": 2
              }
            },
            "answer_point_coverage": {
              "value": null,
              "valid_n": 0,
              "excluded": {
                "expected_refusal": 2
              }
            },
            "faithfulness": {
              "value": 1.0,
              "valid_n": 1,
              "excluded": {
                "zero_claims": 1
              }
            },
            "absent_refusal_rate": {
              "value": 1.0,
              "valid_n": 2,
              "excluded": {}
            },
            "answerable_false_refusal_rate": {
              "value": null,
              "valid_n": 0,
              "excluded": {
                "expected_refusal": 2
              }
            }
          }
        },
        {
          "bucket": "D_unanswerable",
          "strategy": "hybrid",
          "total": 2,
          "attempted": 2,
          "completed": 2,
          "errors": 0,
          "not_attempted": 0,
          "status_counts": {
            "completed": 2,
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
                "expected_refusal": 2
              }
            },
            "recall_at_10": {
              "value": null,
              "valid_n": 0,
              "excluded": {
                "expected_refusal": 2
              }
            },
            "mrr_at_10": {
              "value": null,
              "valid_n": 0,
              "excluded": {
                "expected_refusal": 2
              }
            },
            "all_groups_hit_at_5": {
              "value": null,
              "valid_n": 0,
              "excluded": {
                "expected_refusal": 2
              }
            },
            "all_groups_hit_at_10": {
              "value": null,
              "valid_n": 0,
              "excluded": {
                "expected_refusal": 2
              }
            },
            "candidate_group_coverage": {
              "value": null,
              "valid_n": 0,
              "excluded": {
                "expected_refusal": 2
              }
            },
            "prompt_group_coverage": {
              "value": null,
              "valid_n": 0,
              "excluded": {
                "expected_refusal": 2
              }
            },
            "answer_point_coverage": {
              "value": null,
              "valid_n": 0,
              "excluded": {
                "expected_refusal": 2
              }
            },
            "faithfulness": {
              "value": 0.0,
              "valid_n": 2,
              "excluded": {}
            },
            "absent_refusal_rate": {
              "value": 1.0,
              "valid_n": 2,
              "excluded": {}
            },
            "answerable_false_refusal_rate": {
              "value": null,
              "valid_n": 0,
              "excluded": {
                "expected_refusal": 2
              }
            }
          }
        },
        {
          "bucket": "D_unanswerable",
          "strategy": "hybrid_rerank",
          "total": 2,
          "attempted": 2,
          "completed": 2,
          "errors": 0,
          "not_attempted": 0,
          "status_counts": {
            "completed": 2,
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
                "expected_refusal": 2
              }
            },
            "recall_at_10": {
              "value": null,
              "valid_n": 0,
              "excluded": {
                "expected_refusal": 2
              }
            },
            "mrr_at_10": {
              "value": null,
              "valid_n": 0,
              "excluded": {
                "expected_refusal": 2
              }
            },
            "all_groups_hit_at_5": {
              "value": null,
              "valid_n": 0,
              "excluded": {
                "expected_refusal": 2
              }
            },
            "all_groups_hit_at_10": {
              "value": null,
              "valid_n": 0,
              "excluded": {
                "expected_refusal": 2
              }
            },
            "candidate_group_coverage": {
              "value": null,
              "valid_n": 0,
              "excluded": {
                "expected_refusal": 2
              }
            },
            "prompt_group_coverage": {
              "value": null,
              "valid_n": 0,
              "excluded": {
                "expected_refusal": 2
              }
            },
            "answer_point_coverage": {
              "value": null,
              "valid_n": 0,
              "excluded": {
                "expected_refusal": 2
              }
            },
            "faithfulness": {
              "value": 1.0,
              "valid_n": 1,
              "excluded": {
                "zero_claims": 1
              }
            },
            "absent_refusal_rate": {
              "value": 1.0,
              "valid_n": 2,
              "excluded": {}
            },
            "answerable_false_refusal_rate": {
              "value": null,
              "valid_n": 0,
              "excluded": {
                "expected_refusal": 2
              }
            }
          }
        },
        {
          "bucket": "E_multi",
          "strategy": "dense",
          "total": 1,
          "attempted": 1,
          "completed": 1,
          "errors": 0,
          "not_attempted": 0,
          "status_counts": {
            "completed": 1,
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
              "valid_n": 1,
              "excluded": {}
            },
            "recall_at_10": {
              "value": 1.0,
              "valid_n": 1,
              "excluded": {}
            },
            "mrr_at_10": {
              "value": 1.0,
              "valid_n": 1,
              "excluded": {}
            },
            "all_groups_hit_at_5": {
              "value": 1.0,
              "valid_n": 1,
              "excluded": {}
            },
            "all_groups_hit_at_10": {
              "value": 1.0,
              "valid_n": 1,
              "excluded": {}
            },
            "candidate_group_coverage": {
              "value": 1.0,
              "valid_n": 1,
              "excluded": {}
            },
            "prompt_group_coverage": {
              "value": 1.0,
              "valid_n": 1,
              "excluded": {}
            },
            "answer_point_coverage": {
              "value": 1.0,
              "valid_n": 1,
              "excluded": {}
            },
            "faithfulness": {
              "value": 1.0,
              "valid_n": 1,
              "excluded": {}
            },
            "absent_refusal_rate": {
              "value": null,
              "valid_n": 0,
              "excluded": {
                "answerable": 1
              }
            },
            "answerable_false_refusal_rate": {
              "value": 0.0,
              "valid_n": 1,
              "excluded": {}
            }
          }
        },
        {
          "bucket": "E_multi",
          "strategy": "bm25",
          "total": 1,
          "attempted": 1,
          "completed": 1,
          "errors": 0,
          "not_attempted": 0,
          "status_counts": {
            "completed": 1,
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
              "value": 0.3333333333333333,
              "valid_n": 1,
              "excluded": {}
            },
            "recall_at_10": {
              "value": 0.6666666666666666,
              "valid_n": 1,
              "excluded": {}
            },
            "mrr_at_10": {
              "value": 1.0,
              "valid_n": 1,
              "excluded": {}
            },
            "all_groups_hit_at_5": {
              "value": 0.0,
              "valid_n": 1,
              "excluded": {}
            },
            "all_groups_hit_at_10": {
              "value": 0.0,
              "valid_n": 1,
              "excluded": {}
            },
            "candidate_group_coverage": {
              "value": 1.0,
              "valid_n": 1,
              "excluded": {}
            },
            "prompt_group_coverage": {
              "value": 0.6666666666666666,
              "valid_n": 1,
              "excluded": {}
            },
            "answer_point_coverage": {
              "value": 0.0,
              "valid_n": 1,
              "excluded": {}
            },
            "faithfulness": {
              "value": null,
              "valid_n": 0,
              "excluded": {
                "zero_claims": 1
              }
            },
            "absent_refusal_rate": {
              "value": null,
              "valid_n": 0,
              "excluded": {
                "answerable": 1
              }
            },
            "answerable_false_refusal_rate": {
              "value": 1.0,
              "valid_n": 1,
              "excluded": {}
            }
          }
        },
        {
          "bucket": "E_multi",
          "strategy": "hybrid",
          "total": 1,
          "attempted": 1,
          "completed": 1,
          "errors": 0,
          "not_attempted": 0,
          "status_counts": {
            "completed": 1,
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
              "value": 0.6666666666666666,
              "valid_n": 1,
              "excluded": {}
            },
            "recall_at_10": {
              "value": 1.0,
              "valid_n": 1,
              "excluded": {}
            },
            "mrr_at_10": {
              "value": 1.0,
              "valid_n": 1,
              "excluded": {}
            },
            "all_groups_hit_at_5": {
              "value": 0.0,
              "valid_n": 1,
              "excluded": {}
            },
            "all_groups_hit_at_10": {
              "value": 1.0,
              "valid_n": 1,
              "excluded": {}
            },
            "candidate_group_coverage": {
              "value": 1.0,
              "valid_n": 1,
              "excluded": {}
            },
            "prompt_group_coverage": {
              "value": 1.0,
              "valid_n": 1,
              "excluded": {}
            },
            "answer_point_coverage": {
              "value": 1.0,
              "valid_n": 1,
              "excluded": {}
            },
            "faithfulness": {
              "value": 1.0,
              "valid_n": 1,
              "excluded": {}
            },
            "absent_refusal_rate": {
              "value": null,
              "valid_n": 0,
              "excluded": {
                "answerable": 1
              }
            },
            "answerable_false_refusal_rate": {
              "value": 0.0,
              "valid_n": 1,
              "excluded": {}
            }
          }
        },
        {
          "bucket": "E_multi",
          "strategy": "hybrid_rerank",
          "total": 1,
          "attempted": 1,
          "completed": 1,
          "errors": 0,
          "not_attempted": 0,
          "status_counts": {
            "completed": 1,
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
              "valid_n": 1,
              "excluded": {}
            },
            "recall_at_10": {
              "value": 1.0,
              "valid_n": 1,
              "excluded": {}
            },
            "mrr_at_10": {
              "value": 1.0,
              "valid_n": 1,
              "excluded": {}
            },
            "all_groups_hit_at_5": {
              "value": 1.0,
              "valid_n": 1,
              "excluded": {}
            },
            "all_groups_hit_at_10": {
              "value": 1.0,
              "valid_n": 1,
              "excluded": {}
            },
            "candidate_group_coverage": {
              "value": 1.0,
              "valid_n": 1,
              "excluded": {}
            },
            "prompt_group_coverage": {
              "value": 1.0,
              "valid_n": 1,
              "excluded": {}
            },
            "answer_point_coverage": {
              "value": 0.6666666666666666,
              "valid_n": 1,
              "excluded": {}
            },
            "faithfulness": {
              "value": 1.0,
              "valid_n": 1,
              "excluded": {}
            },
            "absent_refusal_rate": {
              "value": null,
              "valid_n": 0,
              "excluded": {
                "answerable": 1
              }
            },
            "answerable_false_refusal_rate": {
              "value": 0.0,
              "valid_n": 1,
              "excluded": {}
            }
          }
        }
      ]
    }
  },
  "source_map": {
    "audit_version": 1,
    "dataset_id": "merchant-rag-300-v1",
    "provenance": {
      "dataset_fingerprint": "d4da3bd7b61c85bf236de955fadc0dcb806f2384c417dfe2b3dd686372f7476e",
      "corpus_hash": "c188bcabb1b3fa6a5e4e72284d0726f96e2b2cff6e0a1c48245dea85e792ef10",
      "cases_hash": "3b2901de79f80c54453805038e354aea9cadabf024fafe2802c78ce7a75c4f96",
      "annotation_hash": "b4015c5d11675137634fb8c0e186796aa3be94744c9081b9a661f9962e840925"
    },
    "sources": [
      {
        "chunk_key": "after-sales-manual.md:001:7202cf4ca7d2a5ce03a53a41c48b8c77bfcbf5718aca1876b15e1d1b34819e17",
        "chunk_id": 1831,
        "document": "after-sales-manual.md",
        "ordinal": 1,
        "draft": {
          "category": "售后手册",
          "questions": "常见问题处理时限",
          "answer": "| 问题类型 | 首次响应 | 处理时限 |\n| --- | --- | --- |\n| 退款 | 2 小时 | 3 个工作日 |\n| 换货 | 2 小时 | 5 个工作日 |\n| 维修 | 4 小时 | 7 个工作日 |\n| 投诉 | 1 小时 | 3 个工作日 |\n| 发票 | 4 小时 | 3 个工作日 |\n| 物流异常 | 2 小时 | 5 个工作日 |\n| 商品咨询 | 1 小时 | 当日 |\n| 价格保护 | 2 小时 | 3 个工作日 |\n| 账户问题 | 2 小时 | 3 个工作日 |\n| 退换货运费 | 2 小时 | 3 个工作日 |\n| 缺货补发 | 2 小时 | 5 个工作日 |\n| 其他 | 4 小时 | 7 个工作日 |",
          "section_path": "售后手册/常见问题处理时限",
          "content_type": "manual",
          "is_key_clause": false
        }
      },
      {
        "chunk_key": "after-sales-manual.md:002:0e26e68f417e9cddefe91d8cbf327ff579c57a44c5c6d7c6866eb6f5fcc5d525",
        "chunk_id": 1832,
        "document": "after-sales-manual.md",
        "ordinal": 2,
        "draft": {
          "category": "售后手册",
          "questions": "保修说明",
          "answer": "电子类商品保修 12 个月,自签收日起算;人为损坏不在保修范围。",
          "section_path": "售后手册/保修说明",
          "content_type": "manual",
          "is_key_clause": false
        }
      },
      {
        "chunk_key": "after-sales-manual.md:003:46f8825077b34437b1fa75eaedfad7a4fb0c0326b80a276c5c30d3b88e221e13",
        "chunk_id": 1833,
        "document": "after-sales-manual.md",
        "ordinal": 3,
        "draft": {
          "category": "售后手册",
          "questions": "设备安装与激活",
          "answer": "智能设备首次使用需下载「喵喵优选」App,按说明书扫码添加设备并连接 2.4G Wi-Fi 完成激活;猫爬架等非联网商品按随附图解自行组装。",
          "section_path": "售后手册/设备安装与激活",
          "content_type": "manual",
          "is_key_clause": false
        }
      },
      {
        "chunk_key": "after-sales-manual.md:004:e6c60fd9c73733a64750b8c14a2181e06fd5d21821e61bd6c8f3a23f12876244",
        "chunk_id": 1834,
        "document": "after-sales-manual.md",
        "ordinal": 4,
        "draft": {
          "category": "售后手册",
          "questions": "常见故障自查",
          "answer": "- 饮水机不出水:检查水位是否低于最低线、水泵是否卡阻,断电清洗水泵后重试。\n- 猫砂盆报错:清空废砂盒并检查滚筒是否卡砂,重启设备;仍报错联系售后。\n- 喂食器卡粮:检查粮食颗粒直径是否超 12mm、粮桶是否受潮结块,清理出粮口后重试。\n- 摄像头离线:确认 Wi-Fi 为 2.4G 频段、信号良好,重启设备或在 App 内重新配网。",
          "section_path": "售后手册/常见故障自查",
          "content_type": "manual",
          "is_key_clause": false
        }
      },
      {
        "chunk_key": "after-sales-manual.md:005:16e83da06b296764b24f5370aa6c3c5b447e7ada7eec424acb870e2fc137cd2a",
        "chunk_id": 1835,
        "document": "after-sales-manual.md",
        "ordinal": 5,
        "draft": {
          "category": "售后手册",
          "questions": "人工客服入口与时间",
          "answer": "App 内「我的」-「联系客服」可转接在线人工;人工客服服务时间为每日 9:00 至 22:00,高峰期请耐心等待或留言。",
          "section_path": "售后手册/人工客服入口与时间",
          "content_type": "manual",
          "is_key_clause": false
        }
      },
      {
        "chunk_key": "after-sales-manual.md:006:fc43f54cc8d385ae7519632591d2f82208c032cd97489b2bfbe565a6bb27a6ef",
        "chunk_id": 1836,
        "document": "after-sales-manual.md",
        "ordinal": 6,
        "draft": {
          "category": "售后手册",
          "questions": "维修寄修流程",
          "answer": "保修期内设备故障,联系客服登记后按指引将设备寄回指定维修点,核验后免费维修并寄回;超保或人为损坏维修可能收取工本费,费用会提前告知。",
          "section_path": "售后手册/维修寄修流程",
          "content_type": "manual",
          "is_key_clause": false
        }
      },
      {
        "chunk_key": "after-sales-manual.md:007:03b647141d60a612d03736cb40cd2d3c0ca7f6125fd4054912d2880d562259c7",
        "chunk_id": 1837,
        "document": "after-sales-manual.md",
        "ordinal": 7,
        "draft": {
          "category": "售后手册",
          "questions": "会员专属售后权益",
          "answer": "金卡会员享优先客服接入与上门取件退换货;银卡会员享退换货运费权益 1 次/月。具体权益以会员中心页面标注为准。",
          "section_path": "售后手册/会员专属售后权益",
          "content_type": "manual",
          "is_key_clause": false
        }
      },
      {
        "chunk_key": "product-faq.md:001:0d1a353c26224e8102a070fbd4262c6a1d8145084acc659b03d48e443645b094",
        "chunk_id": 1838,
        "document": "product-faq.md",
        "ordinal": 1,
        "draft": {
          "category": "商品与购物 FAQ",
          "questions": "退货政策是什么",
          "answer": "支持 7 天无理由退货,商品需保持完好、不影响二次销售,具体以平台售后规则为准。",
          "section_path": "商品与购物 FAQ/退货政策是什么",
          "content_type": "faq",
          "is_key_clause": false
        }
      },
      {
        "chunk_key": "product-faq.md:002:b54c0327c0b8204d90a44f51c42ee808b8511313d05d3772a7192805a6959650",
        "chunk_id": 1839,
        "document": "product-faq.md",
        "ordinal": 2,
        "draft": {
          "category": "商品与购物 FAQ",
          "questions": "如何申请退款",
          "answer": "在「我的订单」找到对应订单点击「申请退款」,按提示提交,审核通过后原路退回。",
          "section_path": "商品与购物 FAQ/如何申请退款",
          "content_type": "faq",
          "is_key_clause": false
        }
      },
      {
        "chunk_key": "product-faq.md:003:a1fed4fdf12d74a73079a3909678d91634df75f294328214f9f4798b6426e991",
        "chunk_id": 1840,
        "document": "product-faq.md",
        "ordinal": 3,
        "draft": {
          "category": "商品与购物 FAQ",
          "questions": "换货流程怎么走",
          "answer": "收到商品 7 天内可申请换货,联系客服登记后将商品寄回,平台核验无误后补发新品。",
          "section_path": "商品与购物 FAQ/换货流程怎么走",
          "content_type": "faq",
          "is_key_clause": false
        }
      },
      {
        "chunk_key": "product-faq.md:004:fd54dbe9fee3d150a2241a4656b26927771c5eba7f373670d869c0eb22bc2f27",
        "chunk_id": 1841,
        "document": "product-faq.md",
        "ordinal": 4,
        "draft": {
          "category": "商品与购物 FAQ",
          "questions": "发货时效多久",
          "answer": "现货商品付款后 48 小时内发货,预售商品以商品详情页标注的发货时间为准。",
          "section_path": "商品与购物 FAQ/发货时效多久",
          "content_type": "faq",
          "is_key_clause": false
        }
      },
      {
        "chunk_key": "product-faq.md:005:a378cfa07513ed7b747b8870ef187c00e9e1ce815a4bac7cfd9bfda4c9e43805",
        "chunk_id": 1842,
        "document": "product-faq.md",
        "ordinal": 5,
        "draft": {
          "category": "商品与购物 FAQ",
          "questions": "运费怎么算",
          "answer": "单笔订单满 99 元包邮,未满收取 10 元运费,偏远地区运费另计。邮费即运费,按此规则收取。",
          "section_path": "商品与购物 FAQ/运费怎么算",
          "content_type": "faq",
          "is_key_clause": false
        }
      },
      {
        "chunk_key": "product-faq.md:006:9e6e422d50701b7ba2c3ccad183f67fc63cf0ce9caf42e2ef88b949a9f2ba840",
        "chunk_id": 1843,
        "document": "product-faq.md",
        "ordinal": 6,
        "draft": {
          "category": "商品与购物 FAQ",
          "questions": "发票如何开具",
          "answer": "在「我的订单」-「申请开票」提交抬头与税号,电子发票将于 3 个工作日内发送至邮箱。",
          "section_path": "商品与购物 FAQ/发票如何开具",
          "content_type": "faq",
          "is_key_clause": false
        }
      },
      {
        "chunk_key": "product-faq.md:007:6e08a30e41cf2d07ede67d7aa48422a28bda97ccc2fa74688fb872ca75142cba",
        "chunk_id": 1844,
        "document": "product-faq.md",
        "ordinal": 7,
        "draft": {
          "category": "商品与购物 FAQ",
          "questions": "支持哪些支付方式",
          "answer": "下单支持支付宝、微信支付与主流银行储蓄卡/信用卡在线支付。暂不支持线下汇款,支付遇到问题可重试或更换支付方式。",
          "section_path": "商品与购物 FAQ/支持哪些支付方式",
          "content_type": "faq",
          "is_key_clause": false
        }
      },
      {
        "chunk_key": "product-faq.md:008:266e3eef703549a3fe871982bdd1ea054837ff75874d0cf398bdf9e987c6c9ac",
        "chunk_id": 1845,
        "document": "product-faq.md",
        "ordinal": 8,
        "draft": {
          "category": "商品与购物 FAQ",
          "questions": "会员等级与积分规则",
          "answer": "会员分为普通、银卡、金卡三档,按累计消费自动升级。每消费 1 元得 1 积分,积分可在结算时抵扣,100 积分抵 1 元。",
          "section_path": "商品与购物 FAQ/会员等级与积分规则",
          "content_type": "faq",
          "is_key_clause": false
        }
      },
      {
        "chunk_key": "product-faq.md:009:632d97ce603b91dde4d8665a543c5858312a82aa840cf61a898b9f94052c6a53",
        "chunk_id": 1846,
        "document": "product-faq.md",
        "ordinal": 9,
        "draft": {
          "category": "商品与购物 FAQ",
          "questions": "优惠券和满减怎么用",
          "answer": "优惠券在结算页「使用优惠券」中勾选,满减活动自动叠加在商品页标示的门槛上;同一订单一般限用一张店铺券,活动细则以页面为准。",
          "section_path": "商品与购物 FAQ/优惠券和满减怎么用",
          "content_type": "faq",
          "is_key_clause": false
        }
      },
      {
        "chunk_key": "product-faq.md:010:c8e85d958ea046e515278627e795c27d9996a3c7cbf18e656b1778d31e29445f",
        "chunk_id": 1847,
        "document": "product-faq.md",
        "ordinal": 10,
        "draft": {
          "category": "商品与购物 FAQ",
          "questions": "配送范围与偏远地区",
          "answer": "全国大部分地区支持配送,新疆、西藏、内蒙古等偏远地区运费另计且时效顺延;港澳台及海外暂不支持自营配送。",
          "section_path": "商品与购物 FAQ/配送范围与偏远地区",
          "content_type": "faq",
          "is_key_clause": false
        }
      },
      {
        "chunk_key": "product-faq.md:011:10a8a7b8860e285b69f6994c8a087c2eae979eaf87846d9464780dbab56f8fa4",
        "chunk_id": 1848,
        "document": "product-faq.md",
        "ordinal": 11,
        "draft": {
          "category": "商品与购物 FAQ",
          "questions": "订单可以修改或取消吗",
          "answer": "订单未发货前可在「我的订单」自助取消;已发货订单无法修改收货信息,可拒收后走退款流程。修改商品数量需取消后重新下单。",
          "section_path": "商品与购物 FAQ/订单可以修改或取消吗",
          "content_type": "faq",
          "is_key_clause": false
        }
      },
      {
        "chunk_key": "product-faq.md:012:fe027c833b6de9248ff56e77e7975d453b36934d2f6225ff19c07e0ac246a329",
        "chunk_id": 1849,
        "document": "product-faq.md",
        "ordinal": 12,
        "draft": {
          "category": "商品与购物 FAQ",
          "questions": "商品缺货多久补货",
          "answer": "现货售罄的商品通常 3 至 7 天内补货,可在商品页点击「到货通知」,补货后系统会推送提醒。",
          "section_path": "商品与购物 FAQ/商品缺货多久补货",
          "content_type": "faq",
          "is_key_clause": false
        }
      },
      {
        "chunk_key": "product-faq.md:013:811b7bf2a0e8f0814024553fc91eea0c9607267cde1fd3dd45b951b6b9017516",
        "chunk_id": 1850,
        "document": "product-faq.md",
        "ordinal": 13,
        "draft": {
          "category": "商品与购物 FAQ",
          "questions": "价格保护怎么申请",
          "answer": "自营商品支持下单后 7 天内价保,期间若同款降价可在「我的订单」-「申请价保」提交,差价将退回原支付渠道。",
          "section_path": "商品与购物 FAQ/价格保护怎么申请",
          "content_type": "faq",
          "is_key_clause": false
        }
      },
      {
        "chunk_key": "product-faq.md:014:2df0cfc67e100b58d106ae3d96fcdfcfcc6e61f9ceda22edec382ba9eba305e8",
        "chunk_id": 1851,
        "document": "product-faq.md",
        "ordinal": 14,
        "draft": {
          "category": "商品与购物 FAQ",
          "questions": "会员运费权益",
          "answer": "金卡会员每月享 3 次免运费权益,银卡会员享 1 次;权益不与偏远地区附加运费冲抵,当月未用完不结转。",
          "section_path": "商品与购物 FAQ/会员运费权益",
          "content_type": "faq",
          "is_key_clause": false
        }
      },
      {
        "chunk_key": "product-specs.md:001:dc53084d66b22ac0b6b909e34a0e5b6f2c6ac35851c1722bd1e7f22b28b567e0",
        "chunk_id": 1852,
        "document": "product-specs.md",
        "ordinal": 1,
        "draft": {
          "category": "product-specs.md",
          "questions": "商品规格手册",
          "answer": "本手册收录喵喵优选自营智能硬件的型号、规格与使用要点,便于按具体型号查询。",
          "section_path": "商品规格手册",
          "content_type": "manual",
          "is_key_clause": false
        }
      },
      {
        "chunk_key": "product-specs.md:002:4b03c1ddd6cde11c032f3b94e81066ec8227045d930d76ac7e1af8fd8e71fd23",
        "chunk_id": 1853,
        "document": "product-specs.md",
        "ordinal": 2,
        "draft": {
          "category": "商品规格手册",
          "questions": "智能猫砂盆 Pro(型号 MH-LP100)",
          "answer": "- 型号:MH-LP100\n- 适用猫咪体重:1.5kg 至 8kg\n- 猫砂容量:9L,废砂盒容量约 7 天(单猫)\n- 核心功能:自动感应清理、活性炭除臭、App 远程监控与健康记录\n- 供电:220V 市电,断电后配置自动保存\n- 清理提示:废砂盒满时 App 推送提醒,建议每 5 至 7 天倾倒一次",
          "section_path": "商品规格手册/智能猫砂盆 Pro(型号 MH-LP100)",
          "content_type": "manual",
          "is_key_clause": false
        }
      },
      {
        "chunk_key": "product-specs.md:003:991276de42d44e06168ae7625057b9692cbc6be8149687ccf1a752da00b9f9f3",
        "chunk_id": 1854,
        "document": "product-specs.md",
        "ordinal": 3,
        "draft": {
          "category": "商品规格手册",
          "questions": "智能猫砂盆 Lite(型号 MH-LP50)",
          "answer": "- 型号:MH-LP50\n- 适用猫咪体重:1.5kg 至 6kg\n- 猫砂容量:6L\n- 核心功能:自动感应清理、物理除臭盖板;不含 App 联网功能\n- 与 Pro 差异:Lite 无 App 远程监控与健康记录,价格更低,适合单猫家庭",
          "section_path": "商品规格手册/智能猫砂盆 Lite(型号 MH-LP50)",
          "content_type": "manual",
          "is_key_clause": false
        }
      },
      {
        "chunk_key": "product-specs.md:004:3c911bcff026033058b5e3badaa187e7e3d87bf51b5471f70e40ea8089d63e8c",
        "chunk_id": 1855,
        "document": "product-specs.md",
        "ordinal": 4,
        "draft": {
          "category": "商品规格手册",
          "questions": "智能猫砂盆 Max(型号 MH-LP200)",
          "answer": "- 型号:MH-LP200\n- 适用猫咪体重:2kg 至 12kg,适合大型猫与多猫家庭\n- 猫砂容量:12L,废砂盒容量约 10 天(单猫)\n- 核心功能:超大滚筒、双重称重防夹、活性炭除臭、App 多猫健康档案\n- 供电:220V 市电\n- 清理提示:多猫家庭建议每 3 至 5 天倾倒一次废砂盒",
          "section_path": "商品规格手册/智能猫砂盆 Max(型号 MH-LP200)",
          "content_type": "manual",
          "is_key_clause": false
        }
      },
      {
        "chunk_key": "product-specs.md:005:58f10003acf72bef5aa921d603dc1a58bb0332dcd7f8735057266e573f01e11b",
        "chunk_id": 1856,
        "document": "product-specs.md",
        "ordinal": 5,
        "draft": {
          "category": "商品规格手册",
          "questions": "自动饮水机(型号 MH-W20)",
          "answer": "- 型号:MH-W20\n- 水箱容量:2L\n- 过滤:三重过滤棉,建议每 2 周更换一次滤芯\n- 核心功能:静音水泵、缺水断电保护、水位窗口\n- 清洗:水泵可拆卸,建议每周清洗一次",
          "section_path": "商品规格手册/自动饮水机(型号 MH-W20)",
          "content_type": "manual",
          "is_key_clause": false
        }
      },
      {
        "chunk_key": "product-specs.md:006:7bc85cbc0961a7f65bb02095525245853068b6933a24a48b0b06e1344a686d7d",
        "chunk_id": 1857,
        "document": "product-specs.md",
        "ordinal": 6,
        "draft": {
          "category": "商品规格手册",
          "questions": "自动饮水机 Plus(型号 MH-W40)",
          "answer": "- 型号:MH-W40\n- 水箱容量:4L\n- 过滤:五重过滤棉 + 椰壳活性炭,建议每 3 周更换一次滤芯\n- 核心功能:UV 紫外杀菌、静音变频水泵、缺水断电保护\n- 清洗:整机可拆分水洗,建议每周清洗一次",
          "section_path": "商品规格手册/自动饮水机 Plus(型号 MH-W40)",
          "content_type": "manual",
          "is_key_clause": false
        }
      },
      {
        "chunk_key": "product-specs.md:007:e9867a419061278a1bc0599bc3595ac01da4c561aea19bf0bf4c9bde5ba30e7f",
        "chunk_id": 1858,
        "document": "product-specs.md",
        "ordinal": 7,
        "draft": {
          "category": "商品规格手册",
          "questions": "自动饮水机 Pro 不锈钢(型号 MH-W60)",
          "answer": "- 型号:MH-W60\n- 水箱容量:6L,304 不锈钢表面盘\n- 过滤:双滤芯并联,建议每 4 周更换一次滤芯\n- 核心功能:双泵冗余、无线水位提醒推送 App、缺水断电保护\n- 清洗:不锈钢面盘可高温消毒,建议每周清洗一次",
          "section_path": "商品规格手册/自动饮水机 Pro 不锈钢(型号 MH-W60)",
          "content_type": "manual",
          "is_key_clause": false
        }
      },
      {
        "chunk_key": "product-specs.md:008:1802857d937ad7bc2d80ab37efde2da586defc78bb6a00d73f8b5ed62601bc42",
        "chunk_id": 1859,
        "document": "product-specs.md",
        "ordinal": 8,
        "draft": {
          "category": "商品规格手册",
          "questions": "大型猫爬架(型号 MH-CT30)",
          "answer": "- 型号:MH-CT30\n- 高度:1.6m,共四层带顶层吊床\n- 承重:单层最大 10kg\n- 材质:剑麻柱身、绒布平台\n- 安装:需自行组装,随附六角扳手与图解说明书",
          "section_path": "商品规格手册/大型猫爬架(型号 MH-CT30)",
          "content_type": "manual",
          "is_key_clause": false
        }
      },
      {
        "chunk_key": "product-specs.md:009:d696b670457f1d69b4d9e16d3c8efdd0defd0e53c1832c93a8fd85c560551699",
        "chunk_id": 1860,
        "document": "product-specs.md",
        "ordinal": 9,
        "draft": {
          "category": "商品规格手册",
          "questions": "恒温加热垫(型号 MH-HP12)",
          "answer": "- 型号:MH-HP12\n- 尺寸:40cm × 30cm\n- 温控:恒温 38℃,内置过热保护,连续通电不超过 12 小时为宜\n- 防护:防水防抓咬电线套管\n- 适用:幼猫、老年猫及冬季保暖",
          "section_path": "商品规格手册/恒温加热垫(型号 MH-HP12)",
          "content_type": "manual",
          "is_key_clause": false
        }
      },
      {
        "chunk_key": "product-specs.md:010:1be9c972a5dd1efa00120aad837503c2c7b9ee14be4b23ad1cf50d789ba81506",
        "chunk_id": 1861,
        "document": "product-specs.md",
        "ordinal": 10,
        "draft": {
          "category": "商品规格手册",
          "questions": "大号三档加热垫(型号 MH-HP20)",
          "answer": "- 型号:MH-HP20\n- 尺寸:60cm × 45cm\n- 温控:三档可调 30℃ / 38℃ / 45℃,内置过热保护与定时关机\n- 防护:防水防抓咬电线套管,表面绒布可拆洗\n- 适用:大型猫、多猫窝及冬季保暖",
          "section_path": "商品规格手册/大号三档加热垫(型号 MH-HP20)",
          "content_type": "manual",
          "is_key_clause": false
        }
      },
      {
        "chunk_key": "product-specs.md:011:83f334c91d091c9c733956564d0d5fa24078df26b3553ae3461ffebb67e04538",
        "chunk_id": 1862,
        "document": "product-specs.md",
        "ordinal": 11,
        "draft": {
          "category": "商品规格手册",
          "questions": "自动喂食器 基础版(型号 MH-FD10)",
          "answer": "- 型号:MH-FD10\n- 粮桶容量:4L\n- 核心功能:定时定量投喂,每日最多 6 餐,语音呼唤进食\n- 供电:市电供电 + 4 节 5 号电池断电应急\n- 说明:基础版不含摄像头与 App 远程投喂",
          "section_path": "商品规格手册/自动喂食器 基础版(型号 MH-FD10)",
          "content_type": "manual",
          "is_key_clause": false
        }
      },
      {
        "chunk_key": "product-specs.md:012:5a6c6a0399d4b5fff33062f2e79da99a7312aec4531707bd3da0255a835c22cc",
        "chunk_id": 1863,
        "document": "product-specs.md",
        "ordinal": 12,
        "draft": {
          "category": "商品规格手册",
          "questions": "自动喂食器 摄像头版(型号 MH-FD30)",
          "answer": "- 型号:MH-FD30\n- 粮桶容量:6L\n- 核心功能:1080P 摄像头、双向语音、App 远程手动投喂与定时投喂\n- 供电:市电供电 + 内置应急电池\n- 说明:摄像头版支持视频回看,需连接 2.4G Wi-Fi",
          "section_path": "商品规格手册/自动喂食器 摄像头版(型号 MH-FD30)",
          "content_type": "manual",
          "is_key_clause": false
        }
      },
      {
        "chunk_key": "product-specs.md:013:21004ee51514e767b4dc31e21841ba8ac9dc6bee54516311fdc99678210846f9",
        "chunk_id": 1864,
        "document": "product-specs.md",
        "ordinal": 13,
        "draft": {
          "category": "商品规格手册",
          "questions": "全景看护摄像头(型号 MH-CAM1)",
          "answer": "- 型号:MH-CAM1\n- 画质:2K 分辨率,355° 水平旋转、90° 俯仰\n- 核心功能:移动侦测报警、夜视、双向语音、逗猫激光\n- 存储:支持最大 128G TF 卡或云存储\n- 供电:Type-C 供电,需连接 2.4G Wi-Fi",
          "section_path": "商品规格手册/全景看护摄像头(型号 MH-CAM1)",
          "content_type": "manual",
          "is_key_clause": false
        }
      },
      {
        "chunk_key": "returns-policy.md:001:49f98ddcaa9cc42419073cd7ac3a116b24bd3c537d004512b6c2daa596054c21",
        "chunk_id": 1865,
        "document": "returns-policy.md",
        "ordinal": 1,
        "draft": {
          "category": "退货退款政策/无理由退货",
          "questions": "适用范围",
          "answer": "自签收之日起 7 天内,商品完好、不影响二次销售的,支持无理由退货。定制类、生鲜类商品除外。",
          "section_path": "退货退款政策/无理由退货/适用范围",
          "content_type": "policy",
          "is_key_clause": false
        }
      },
      {
        "chunk_key": "returns-policy.md:002:790d978e46084d3c89e96e1e75a4db8309b5d24c47b4be722652b8cc0facd375",
        "chunk_id": 1866,
        "document": "returns-policy.md",
        "ordinal": 2,
        "draft": {
          "category": "退货退款政策/无理由退货",
          "questions": "退款时效",
          "answer": "退货商品经平台核验通过后,退款原路退回,到账时效以平台售后规则为准。",
          "section_path": "退货退款政策/无理由退货/退款时效",
          "content_type": "policy",
          "is_key_clause": false
        }
      },
      {
        "chunk_key": "returns-policy.md:003:c88e0b7d32913aef1b6c47a7438e8a665d0b24e4686691459641019fbc0aaa74",
        "chunk_id": 1867,
        "document": "returns-policy.md",
        "ordinal": 3,
        "draft": {
          "category": "退货退款政策/换货政策",
          "questions": "换货条件",
          "answer": "收到商品 7 天内,商品完好且配件齐全的,可申请一次同款换货;不同型号或颜色需先退货再重新下单。",
          "section_path": "退货退款政策/换货政策/换货条件",
          "content_type": "policy",
          "is_key_clause": false
        }
      },
      {
        "chunk_key": "returns-policy.md:004:0b4a2e6b1f20639b7f966a0bba31c735dc55faa1d51d6f29e9b0bb1be15603dc",
        "chunk_id": 1868,
        "document": "returns-policy.md",
        "ordinal": 4,
        "draft": {
          "category": "退货退款政策/换货政策",
          "questions": "换货运费",
          "answer": "非质量问题的换货,往返运费由买家承担;因质量问题或发错货的换货,往返运费由平台承担。",
          "section_path": "退货退款政策/换货政策/换货运费",
          "content_type": "policy",
          "is_key_clause": false
        }
      },
      {
        "chunk_key": "returns-policy.md:005:4d4b2ea9115f9f9c717e0b83cded75c9048bc1b04a4621131131a6e1d023f11c",
        "chunk_id": 1869,
        "document": "returns-policy.md",
        "ordinal": 5,
        "draft": {
          "category": "退货退款政策",
          "questions": "退换货运费承担",
          "answer": "无理由退货的退回运费由买家承担;因商品质量问题、发错货、少发漏发导致的退换货,运费由平台承担。运费承担以平台售后规则最终判定为准。",
          "section_path": "退货退款政策/退换货运费承担",
          "content_type": "policy",
          "is_key_clause": false
        }
      },
      {
        "chunk_key": "returns-policy.md:006:eea36146abe1a220cecf96e8c13d4ee748fcc98e1313aceb840b7ec2d1617423",
        "chunk_id": 1870,
        "document": "returns-policy.md",
        "ordinal": 6,
        "draft": {
          "category": "退货退款政策",
          "questions": "质量问题与保修",
          "answer": "电子类商品自签收起保修 12 个月,保修期内非人为损坏可申请免费维修或换货;人为损坏、超保商品维修可能收取工本费。",
          "section_path": "退货退款政策/质量问题与保修",
          "content_type": "policy",
          "is_key_clause": false
        }
      },
      {
        "chunk_key": "returns-policy.md:007:7996ea6d62a17336c125f1f473f9888754f548b63469d944b93b2203f20c2f1b",
        "chunk_id": 1871,
        "document": "returns-policy.md",
        "ordinal": 7,
        "draft": {
          "category": "退货退款政策",
          "questions": "运输破损处理",
          "answer": "商品运输途中破损的,请在签收后 48 小时内联系客服并提供开箱视频与照片,核实后可免费补发或退款,相关运费由平台承担。",
          "section_path": "退货退款政策/运输破损处理",
          "content_type": "policy",
          "is_key_clause": false
        }
      },
      {
        "chunk_key": "returns-policy.md:008:a6a014b5592a7c58f854c41e4e2d6ff189171b0bfb326db5dcd0c06f26c7fb6e",
        "chunk_id": 1872,
        "document": "returns-policy.md",
        "ordinal": 8,
        "draft": {
          "category": "退货退款政策",
          "questions": "不支持退货的商品",
          "answer": "定制类、生鲜类、已拆封的猫砂等消耗品,以及标注「不支持无理由退货」的商品,非质量问题不支持退货。",
          "section_path": "退货退款政策/不支持退货的商品",
          "content_type": "policy",
          "is_key_clause": false
        }
      },
      {
        "chunk_key": "returns-policy.md:009:d5da6eaa37d40c190b7f5b7257c5da242285eb95e09b274aea29ef6f8dbe7f1c",
        "chunk_id": 1873,
        "document": "returns-policy.md",
        "ordinal": 9,
        "draft": {
          "category": "退货退款政策",
          "questions": "预售与定金",
          "answer": "预售商品以详情页标注的时间发货;定金支付后不支持无理由退定金,尾款未按时支付的,定金按活动规则处理。",
          "section_path": "退货退款政策/预售与定金",
          "content_type": "policy",
          "is_key_clause": false
        }
      },
      {
        "chunk_key": "membership-benefits.md:001:0e401c77a9b672d13f8b19cff2c0db798e72167d869d0b9107819fa281fb34f3",
        "chunk_id": 1874,
        "document": "membership-benefits.md",
        "ordinal": 1,
        "draft": {
          "category": "会员权益",
          "questions": "会员等级",
          "answer": "会员分为普通、银卡和金卡三档，按有效累计消费金额自动升级，不按年度消费金额计算。累计消费未满 1000 元为普通会员，满 1000 元起为银卡，满 5000 元起为金卡。\n\n有效累计消费指已完成订单的商品实际支付金额，不含配送费；退货退款部分从有效累计消费中扣除。退款后根据更新的累计消费重新计算等级，未达到原门槛时可能降级。等级与适用权益在会员中心展示。\n\n银卡在参与会员折扣的商品上享 95 折，金卡享 9 折。折扣适用商品和活动范围以结算页面标注为准。会员折扣、优惠券与满减是否叠加也以当次活动页面为准，不能一概承诺全部优惠同时生效。",
          "section_path": "会员权益/会员等级",
          "content_type": "policy",
          "is_key_clause": false
        }
      },
      {
        "chunk_key": "membership-benefits.md:002:c9a7d21f43bfd7f6a83ec9116841139c65e10365b0a347be54443c42fd024acc",
        "chunk_id": 1875,
        "document": "membership-benefits.md",
        "ordinal": 2,
        "draft": {
          "category": "会员权益",
          "questions": "生日礼",
          "answer": "银卡会员生日当月可领取一份猫零食小样，金卡会员生日当月可领取一份猫罐头礼盒。需在会员中心领取，礼品规格与领取期限以页面标注为准，不承诺额外折现或补偿。",
          "section_path": "会员权益/生日礼",
          "content_type": "policy",
          "is_key_clause": false
        }
      },
      {
        "chunk_key": "integral-rules.md:001:da14206bfa6e6c5f3eb7e3d050070d976a96002eece7dd3d430bb6609dac25f3",
        "chunk_id": 1876,
        "document": "integral-rules.md",
        "ordinal": 1,
        "draft": {
          "category": "积分规则",
          "questions": "积分怎么攒",
          "answer": "已完成订单每实际支付 1 元商品金额累计 1 积分，不计配送费；退款后按对应商品金额同步扣回积分。活动期间的双倍积分属于额外积分奖励，不计入会员等级升级；会员等级仍按有效累计消费金额计算。",
          "section_path": "积分规则/积分怎么攒",
          "content_type": "policy",
          "is_key_clause": false
        }
      },
      {
        "chunk_key": "integral-rules.md:002:3edab91392d486a8a56a372151878ef83573c16222740e3691e976b4afa9e383",
        "chunk_id": 1877,
        "document": "integral-rules.md",
        "ordinal": 2,
        "draft": {
          "category": "积分规则",
          "questions": "积分怎么用",
          "answer": "积分可在结算时抵扣商品金额，100 积分抵 1 元现金，单笔订单最多抵 30 元，不用于抵扣偏远地区附加运费，也不支持直接提现。\n\n2000 积分可兑换自动饮水机滤芯 3 片，该兑换套装适用于 MH-W40，普通配送地区包邮；偏远地区附加配送费仍需按页面规则确认。MH-W40 的滤芯更换周期以商品规格手册为准。\n\n800 积分可兑换猫零食小样，普通配送地区另收 6 元运费；该兑换不直接套用普通购物订单的满 99 元包邮规则。兑换商品、可用库存及偏远地区配送规则以兑换页面标注为准。",
          "section_path": "积分规则/积分怎么用",
          "content_type": "policy",
          "is_key_clause": false
        }
      },
      {
        "chunk_key": "invoice-policy.md:001:d1b6ab4da5b7eef835b5d40febf77279bccce3f21ea810a250d578acd4073bfd",
        "chunk_id": 1878,
        "document": "invoice-policy.md",
        "ordinal": 1,
        "draft": {
          "category": "开票细则",
          "questions": "可开票类型",
          "answer": "本演示店提供电子普通发票、电子专用发票和纸质专用发票。电子普通发票可按订单申请；电子专票需要企业账户，申请前准备发票抬头及有效纳税人识别号，按申请页面提交资料。\n\n纸质专票仅企业账户可申请，申请时需提供企业开票资料、收件人和邮寄地址，快递费到付。资料审核通过后按开票流程寄出，不承诺快递送达日期。",
          "section_path": "开票细则/可开票类型",
          "content_type": "policy",
          "is_key_clause": false
        }
      },
      {
        "chunk_key": "invoice-policy.md:002:a0218d5877a9cff0bb861b79b48eec9d1195948dbac5f6cf30bec16516b4b051",
        "chunk_id": 1879,
        "document": "invoice-policy.md",
        "ordinal": 2,
        "draft": {
          "category": "开票细则",
          "questions": "开票时效",
          "answer": "订单完成后 30 天内可在「我的订单」申请开票，超过 30 天需联系客服核实补开条件，不能直接承诺一定补开。\n\n有效资料审核通过后 3 个工作日内开出发票，电子发票发送至申请邮箱；纸质专票开出后安排邮寄，邮寄耗时不计入开票时限。发票抬头或税号填错时联系客服核实更正，不保证无需审核即可重开。",
          "section_path": "开票细则/开票时效",
          "content_type": "policy",
          "is_key_clause": false
        }
      },
      {
        "chunk_key": "cat-bed-care.md:001:98b746ad8c2deace9e43237f16a81392acdb1dc8e895479cdd075ad6329de2ce",
        "chunk_id": 1880,
        "document": "cat-bed-care.md",
        "ordinal": 1,
        "draft": {
          "category": "猫窝清洗说明",
          "questions": "猫窝是否可以机洗",
          "answer": "普通布艺猫窝清洗前拆掉内部垫芯，外套放入洗衣袋，使用轻柔模式冷水洗，自然晾干。不可直接将整只猫窝连垫芯一起机洗，商品另有清洗标签时优先遵循标签。\n\n带加热模块的猫窝不可机洗，应先断电，并按说明书局部擦洗；不得将加热模块、电源或线路浸水。未按清洗说明操作导致的损坏不直接认定为商品质量问题，需要客服核验。\n\n退货仍需符合商品完好、不影响二次销售等适用条件。售后手册中的电子类商品 12 个月保修不能直接套用到普通布艺猫窝；本清洗说明未给出布艺猫窝的独立保修期限。",
          "section_path": "猫窝清洗说明/猫窝是否可以机洗",
          "content_type": "manual",
          "is_key_clause": false
        }
      }
    ],
    "source_map_id": "d2dd350d860b8141e52306cbbcafb22f97d091194eb1cdc839a528c2990715eb"
  },
  "run_id": "b1af9aadc0094141aa5df5ae0ec91bd1",
  "dataset_id": "merchant-rag-300-v1",
  "fingerprint": "191d53c027323fa8005327336e6ec0e737f7d196eebd6ad05f2dea7258f60913",
  "scope": "pilot",
  "run": {
    "schema_version": 2,
    "run_id": "b1af9aadc0094141aa5df5ae0ec91bd1",
    "config": {
      "dataset_id": "merchant-rag-300-v1",
      "scope": "pilot",
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
        "llm_reasoning_effort": "low"
      },
      "fingerprint": "191d53c027323fa8005327336e6ec0e737f7d196eebd6ad05f2dea7258f60913"
    },
    "state": "completed_with_errors",
    "outcome": "completed_with_errors",
    "stage": "complete",
    "planned_cases": 10,
    "planned_strategies": 4,
    "planned_records": 40,
    "counts": {
      "completed": 32,
      "rewrite_error": 8,
      "retrieval_error": 0,
      "self_check_error": 0,
      "answer_error": 0,
      "judge_error": 0,
      "cancelled": 0,
      "not_attempted": 0,
      "running": 0,
      "total": 40,
      "attempted": 40,
      "errors": 8
    },
    "request_counts": {
      "rewrite": 10,
      "self_check": 32,
      "answer": 22,
      "judge": 32,
      "embedding": 27,
      "rerank": 8,
      "milvus": 67
    },
    "cleanup": {
      "ok": true,
      "errors": [],
      "unverified": []
    },
    "created_at": "2026-10-11T04:06:05.071221+00:00",
    "updated_at": "2026-10-11T04:08:59.324386+00:00",
    "started_at": "2026-10-11T04:06:05.095395+00:00",
    "finished_at": "2026-10-11T04:08:59.360426+00:00",
    "error": null
  }
}
```

## 逐题结果

### A21 / dense

````json
{
  "eval_id": "A21",
  "strategy": "dense",
  "bucket": "A_policy",
  "difficulty": "policy",
  "category": null,
  "should_refuse": false,
  "refused": false,
  "status": "completed",
  "stage": "complete",
  "query": "喵金等级要年消费多少钱,有什么生日礼",
  "query_plan": {
    "standard": "喵金等级要年消费多少钱,有什么生日礼",
    "expansions": []
  },
  "mapped_groups": [
    {
      "group_id": "g1",
      "alternatives": [
        [
          1874
        ]
      ]
    },
    {
      "group_id": "g2",
      "alternatives": [
        [
          1875
        ]
      ]
    }
  ],
  "candidate_ids": [
    1875,
    1845,
    1874,
    1877,
    1853,
    1854,
    1833,
    1855,
    1851,
    1837,
    1859,
    1876,
    1852,
    1861,
    1860,
    1842,
    1862,
    1844,
    1857,
    1850,
    1872,
    1863,
    1846,
    1864,
    1858,
    1847,
    1834,
    1878,
    1856,
    1832,
    1870,
    1840,
    1838,
    1843,
    1873,
    1879,
    1831,
    1865,
    1867,
    1871,
    1868,
    1836,
    1880,
    1835,
    1849,
    1841,
    1869,
    1866,
    1839,
    1848
  ],
  "final_ids": [
    1875,
    1845,
    1874,
    1877,
    1853,
    1854,
    1833,
    1855,
    1851,
    1837
  ],
  "prompt_citations": [
    {
      "n": 1,
      "chunk_id": "1875",
      "section_path": "会员权益/生日礼",
      "question": "生日礼",
      "answer": "银卡会员生日当月可领取一份猫零食小样，金卡会员生日当月可领取一份猫罐头礼盒。需在会员中心领取，礼品规格与领取期限以页面标注为准，不承诺额外折现或补偿。"
    },
    {
      "n": 3,
      "chunk_id": "1874",
      "section_path": "会员权益/会员等级",
      "question": "会员等级",
      "answer": "会员分为普通、银卡和金卡三档，按有效累计消费金额自动升级，不按年度消费金额计算。累计消费未满 1000 元为普通会员，满 1000 元起为银卡，满 5000 元起为金卡。\n\n有效累计消费指已完成订单的商品实际支付金额，不含配送费；退货退款部分从有效累计消费中扣除。退款后根据更新的累计消费重新计算等级，未达到原门槛时可能降级。等级与适用权益在会员中心展示。\n\n银卡在参与会员折扣的商品上享 95 折，金卡享 9 折。折扣适用商品和活动范围以结算页面标注为准。会员折扣、优惠券与满减是否叠加也以当次活动页面为准，不能一概承诺全部优惠同时生效。"
    },
    {
      "n": 5,
      "chunk_id": "1853",
      "section_path": "商品规格手册/智能猫砂盆 Pro(型号 MH-LP100)",
      "question": "智能猫砂盆 Pro(型号 MH-LP100)",
      "answer": "- 型号:MH-LP100\n- 适用猫咪体重:1.5kg 至 8kg\n- 猫砂容量:9L,废砂盒容量约 7 天(单猫)\n- 核心功能:自动感应清理、活性炭除臭、App 远程监控与健康记录\n- 供电:220V 市电,断电后配置自动保存\n- 清理提示:废砂盒满时 App 推送提醒,建议每 5 至 7 天倾倒一次"
    },
    {
      "n": 7,
      "chunk_id": "1833",
      "section_path": "售后手册/设备安装与激活",
      "question": "设备安装与激活",
      "answer": "智能设备首次使用需下载「喵喵优选」App,按说明书扫码添加设备并连接 2.4G Wi-Fi 完成激活;猫爬架等非联网商品按随附图解自行组装。"
    },
    {
      "n": 9,
      "chunk_id": "1851",
      "section_path": "商品与购物 FAQ/会员运费权益",
      "question": "会员运费权益",
      "answer": "金卡会员每月享 3 次免运费权益,银卡会员享 1 次;权益不与偏远地区附加运费冲抵,当月未用完不结转。"
    },
    {
      "n": 10,
      "chunk_id": "1837",
      "section_path": "售后手册/会员专属售后权益",
      "question": "会员专属售后权益",
      "answer": "金卡会员享优先客服接入与上门取件退换货;银卡会员享退换货运费权益 1 次/月。具体权益以会员中心页面标注为准。"
    },
    {
      "n": 8,
      "chunk_id": "1855",
      "section_path": "商品规格手册/智能猫砂盆 Max(型号 MH-LP200)",
      "question": "智能猫砂盆 Max(型号 MH-LP200)",
      "answer": "- 型号:MH-LP200\n- 适用猫咪体重:2kg 至 12kg,适合大型猫与多猫家庭\n- 猫砂容量:12L,废砂盒容量约 10 天(单猫)\n- 核心功能:超大滚筒、双重称重防夹、活性炭除臭、App 多猫健康档案\n- 供电:220V 市电\n- 清理提示:多猫家庭建议每 3 至 5 天倾倒一次废砂盒"
    },
    {
      "n": 6,
      "chunk_id": "1854",
      "section_path": "商品规格手册/智能猫砂盆 Lite(型号 MH-LP50)",
      "question": "智能猫砂盆 Lite(型号 MH-LP50)",
      "answer": "- 型号:MH-LP50\n- 适用猫咪体重:1.5kg 至 6kg\n- 猫砂容量:6L\n- 核心功能:自动感应清理、物理除臭盖板;不含 App 联网功能\n- 与 Pro 差异:Lite 无 App 远程监控与健康记录,价格更低,适合单猫家庭"
    },
    {
      "n": 4,
      "chunk_id": "1877",
      "section_path": "积分规则/积分怎么用",
      "question": "积分怎么用",
      "answer": "积分可在结算时抵扣商品金额，100 积分抵 1 元现金，单笔订单最多抵 30 元，不用于抵扣偏远地区附加运费，也不支持直接提现。\n\n2000 积分可兑换自动饮水机滤芯 3 片，该兑换套装适用于 MH-W40，普通配送地区包邮；偏远地区附加配送费仍需按页面规则确认。MH-W40 的滤芯更换周期以商品规格手册为准。\n\n800 积分可兑换猫零食小样，普通配送地区另收 6 元运费；该兑换不直接套用普通购物订单的满 99 元包邮规则。兑换商品、可用库存及偏远地区配送规则以兑换页面标注为准。"
    },
    {
      "n": 2,
      "chunk_id": "1845",
      "section_path": "商品与购物 FAQ/会员等级与积分规则",
      "question": "会员等级与积分规则",
      "answer": "会员分为普通、银卡、金卡三档,按累计消费自动升级。每消费 1 元得 1 积分,积分可在结算时抵扣,100 积分抵 1 元。"
    }
  ],
  "decision": {
    "useful": true,
    "reason": "会员等级门槛与金卡生日礼均有证据",
    "response_kind": "knowledge",
    "source": null
  },
  "answer": "您好！根据会员规则，会员等级是按**有效累计消费金额**自动升级的，不是按年度消费计算：累计消费满 5000 元起即为金卡（满 1000 元起为银卡）[3]。\n\n生日礼方面：**金卡会员生日当月可领取一份猫罐头礼盒**（银卡为猫零食小样），需在会员中心领取，礼品规格与领取期限以页面标注为准，不承诺额外折现或补偿[1]。\n\n如需了解其他会员权益（如金卡每月 3 次免运费[9]），欢迎随时咨询～",
  "point_verdicts": [
    {
      "point_id": "p1",
      "covered": true,
      "reason": "回答明确说明等级按有效累计消费金额自动升级、不按年度计算，并给出满5000元起为金卡，核心事实与适用条件（有效累计消费）已保留"
    },
    {
      "point_id": "p2",
      "covered": true,
      "reason": "回答说明金卡生日当月可在会员中心领取猫罐头礼盒，规格与领取期限以页面标注为准，条件完整"
    }
  ],
  "claim_verdicts": [
    {
      "claim": "会员等级按有效累计消费金额自动升级，不是按年度消费计算",
      "supported": true,
      "reason": "证据3明确说明按有效累计消费金额自动升级，不按年度消费金额计算"
    },
    {
      "claim": "累计消费满5000元起为金卡，满1000元起为银卡",
      "supported": true,
      "reason": "证据3明确列出满1000元为银卡、满5000元为金卡的门槛"
    },
    {
      "claim": "金卡会员生日当月可领取一份猫罐头礼盒，银卡为猫零食小样",
      "supported": true,
      "reason": "证据1明确银卡生日当月领猫零食小样、金卡生日当月领猫罐头礼盒"
    },
    {
      "claim": "生日礼需在会员中心领取，礼品规格与领取期限以页面标注为准，不承诺额外折现或补偿",
      "supported": true,
      "reason": "证据1原文包含需在会员中心领取、规格期限以页面为准、不承诺额外折现或补偿"
    },
    {
      "claim": "金卡会员每月享3次免运费权益",
      "supported": true,
      "reason": "证据9明确金卡会员每月享3次免运费权益"
    }
  ],
  "metrics": {
    "recall_at_5": 1.0,
    "recall_at_10": 1.0,
    "mrr_at_10": 1.0,
    "all_groups_hit_at_5": 1.0,
    "all_groups_hit_at_10": 1.0,
    "candidate_group_coverage": 1.0,
    "prompt_group_coverage": 1.0,
    "answer_point_coverage": 1.0,
    "faithfulness": 1.0,
    "absent_refusal_rate": null,
    "answerable_false_refusal_rate": 0.0
  },
  "error": null,
  "elapsed_ms": 14581.986000062898,
  "judge_snapshot": {
    "prompt_version": "joint-generation-v2.1",
    "finish_reason": "stop"
  },
  "audit": {
    "audit_version": 1,
    "source_map_id": "d2dd350d860b8141e52306cbbcafb22f97d091194eb1cdc839a528c2990715eb",
    "gold_groups": [
      {
        "group_id": "g1",
        "alternatives": [
          [
            "membership-benefits.md:001:0e401c77a9b672d13f8b19cff2c0db798e72167d869d0b9107819fa281fb34f3"
          ]
        ]
      },
      {
        "group_id": "g2",
        "alternatives": [
          [
            "membership-benefits.md:002:c9a7d21f43bfd7f6a83ec9116841139c65e10365b0a347be54443c42fd024acc"
          ]
        ]
      }
    ],
    "answer_points": [
      {
        "point_id": "p1",
        "text": "金卡按有效累计消费满 5000 元升级，不按年消费计算",
        "condition": "有效累计商品实付、不含运费、扣除退款；折扣活动范围以页面为准",
        "aliases": []
      },
      {
        "point_id": "p2",
        "text": "金卡生日当月可在会员中心领取猫罐头礼盒，规格与期限以页面为准",
        "condition": "生日当月在会员中心领取，规格期限以页面为准",
        "aliases": []
      }
    ],
    "candidate_ranking": [
      {
        "chunk_id": 1875,
        "score": 0.6760553121566772,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1845,
        "score": 0.5822025537490845,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1874,
        "score": 0.5763506293296814,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1877,
        "score": 0.5374670624732971,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1853,
        "score": 0.5195725560188293,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1854,
        "score": 0.518894612789154,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1833,
        "score": 0.5055581331253052,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1855,
        "score": 0.503264307975769,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1851,
        "score": 0.4963505268096924,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1837,
        "score": 0.4895363450050354,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1859,
        "score": 0.4893115758895874,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1876,
        "score": 0.469903826713562,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1852,
        "score": 0.46209853887557983,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1861,
        "score": 0.45657604932785034,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1860,
        "score": 0.4554552435874939,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1842,
        "score": 0.42638900876045227,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1862,
        "score": 0.41876304149627686,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1844,
        "score": 0.41226792335510254,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1857,
        "score": 0.4030781090259552,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1850,
        "score": 0.40096351504325867,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1872,
        "score": 0.39702826738357544,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1863,
        "score": 0.3951106071472168,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1846,
        "score": 0.3892870843410492,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1864,
        "score": 0.38606271147727966,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1858,
        "score": 0.38367190957069397,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1847,
        "score": 0.3831542134284973,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1834,
        "score": 0.3783602714538574,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1878,
        "score": 0.37430787086486816,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1856,
        "score": 0.3706478476524353,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1832,
        "score": 0.3674589693546295,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1870,
        "score": 0.365822970867157,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1840,
        "score": 0.3642715513706207,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1838,
        "score": 0.3617609143257141,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1843,
        "score": 0.36141517758369446,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1873,
        "score": 0.35819584131240845,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1879,
        "score": 0.35550302267074585,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1831,
        "score": 0.35342466831207275,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1865,
        "score": 0.35225149989128113,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1867,
        "score": 0.34625908732414246,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1871,
        "score": 0.3423440456390381,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1868,
        "score": 0.34111252427101135,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1836,
        "score": 0.3411083519458771,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1880,
        "score": 0.33881208300590515,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1835,
        "score": 0.33717459440231323,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1849,
        "score": 0.3304835259914398,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1841,
        "score": 0.32148316502571106,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1869,
        "score": 0.2996777892112732,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1866,
        "score": 0.29863446950912476,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1839,
        "score": 0.29349204897880554,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1848,
        "score": 0.2662397623062134,
        "score_kind": "cosine"
      }
    ],
    "final_ranking": [
      {
        "chunk_id": 1875,
        "score": 0.6760553121566772,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1845,
        "score": 0.5822025537490845,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1874,
        "score": 0.5763506293296814,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1877,
        "score": 0.5374670624732971,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1853,
        "score": 0.5195725560188293,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1854,
        "score": 0.518894612789154,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1833,
        "score": 0.5055581331253052,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1855,
        "score": 0.503264307975769,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1851,
        "score": 0.4963505268096924,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1837,
        "score": 0.4895363450050354,
        "score_kind": "cosine"
      }
    ]
  }
}
````

### A21 / bm25

````json
{
  "eval_id": "A21",
  "strategy": "bm25",
  "bucket": "A_policy",
  "difficulty": "policy",
  "category": null,
  "should_refuse": false,
  "refused": true,
  "status": "completed",
  "stage": "complete",
  "query": "喵金等级要年消费多少钱,有什么生日礼",
  "query_plan": {
    "standard": "喵金等级要年消费多少钱,有什么生日礼",
    "expansions": []
  },
  "mapped_groups": [
    {
      "group_id": "g1",
      "alternatives": [
        [
          1874
        ]
      ]
    },
    {
      "group_id": "g2",
      "alternatives": [
        [
          1875
        ]
      ]
    }
  ],
  "candidate_ids": [
    1875,
    1874,
    1845,
    1876,
    1852,
    1833,
    1838
  ],
  "final_ids": [
    1875,
    1874,
    1845,
    1876,
    1852,
    1833,
    1838
  ],
  "prompt_citations": [
    {
      "n": 1,
      "chunk_id": "1875",
      "section_path": "会员权益/生日礼",
      "question": "生日礼",
      "answer": "银卡会员生日当月可领取一份猫零食小样，金卡会员生日当月可领取一份猫罐头礼盒。需在会员中心领取，礼品规格与领取期限以页面标注为准，不承诺额外折现或补偿。"
    },
    {
      "n": 3,
      "chunk_id": "1845",
      "section_path": "商品与购物 FAQ/会员等级与积分规则",
      "question": "会员等级与积分规则",
      "answer": "会员分为普通、银卡、金卡三档,按累计消费自动升级。每消费 1 元得 1 积分,积分可在结算时抵扣,100 积分抵 1 元。"
    },
    {
      "n": 5,
      "chunk_id": "1852",
      "section_path": "商品规格手册",
      "question": "商品规格手册",
      "answer": "本手册收录喵喵优选自营智能硬件的型号、规格与使用要点,便于按具体型号查询。"
    },
    {
      "n": 7,
      "chunk_id": "1838",
      "section_path": "商品与购物 FAQ/退货政策是什么",
      "question": "退货政策是什么",
      "answer": "支持 7 天无理由退货,商品需保持完好、不影响二次销售,具体以平台售后规则为准。"
    },
    {
      "n": 6,
      "chunk_id": "1833",
      "section_path": "售后手册/设备安装与激活",
      "question": "设备安装与激活",
      "answer": "智能设备首次使用需下载「喵喵优选」App,按说明书扫码添加设备并连接 2.4G Wi-Fi 完成激活;猫爬架等非联网商品按随附图解自行组装。"
    },
    {
      "n": 4,
      "chunk_id": "1876",
      "section_path": "积分规则/积分怎么攒",
      "question": "积分怎么攒",
      "answer": "已完成订单每实际支付 1 元商品金额累计 1 积分，不计配送费；退款后按对应商品金额同步扣回积分。活动期间的双倍积分属于额外积分奖励，不计入会员等级升级；会员等级仍按有效累计消费金额计算。"
    },
    {
      "n": 2,
      "chunk_id": "1874",
      "section_path": "会员权益/会员等级",
      "question": "会员等级",
      "answer": "会员分为普通、银卡和金卡三档，按有效累计消费金额自动升级，不按年度消费金额计算。累计消费未满 1000 元为普通会员，满 1000 元起为银卡，满 5000 元起为金卡。\n\n有效累计消费指已完成订单的商品实际支付金额，不含配送费；退货退款部分从有效累计消费中扣除。退款后根据更新的累计消费重新计算等级，未达到原门槛时可能降级。等级与适用权益在会员中心展示。\n\n银卡在参与会员折扣的商品上享 95 折，金卡享 9 折。折扣适用商品和活动范围以结算页面标注为准。会员折扣、优惠券与满减是否叠加也以当次活动页面为准，不能一概承诺全部优惠同时生效。"
    }
  ],
  "decision": {
    "useful": false,
    "reason": "金卡为累计消费满5000元且无年消费门槛，生日礼证据未覆盖金卡生日礼内容",
    "response_kind": "knowledge",
    "source": "self_check"
  },
  "answer": "目前的知识资料不足以确认这个问题，我无法给出可靠答案。请补充具体商品或适用条件，或联系人工客服确认。",
  "point_verdicts": [
    {
      "point_id": "p1",
      "covered": false,
      "reason": "回答为拒答，未提及金卡按有效累计消费满5000元升级且不按年计算"
    },
    {
      "point_id": "p2",
      "covered": false,
      "reason": "回答为拒答，未提及生日当月会员中心领取猫罐头礼盒及规格期限以页面为准"
    }
  ],
  "claim_verdicts": [],
  "metrics": {
    "recall_at_5": 1.0,
    "recall_at_10": 1.0,
    "mrr_at_10": 1.0,
    "all_groups_hit_at_5": 1.0,
    "all_groups_hit_at_10": 1.0,
    "candidate_group_coverage": 1.0,
    "prompt_group_coverage": 1.0,
    "answer_point_coverage": 0.0,
    "faithfulness": null,
    "absent_refusal_rate": null,
    "answerable_false_refusal_rate": 1.0
  },
  "error": null,
  "elapsed_ms": 5153.349699918181,
  "judge_snapshot": {
    "prompt_version": "joint-generation-v2.1",
    "finish_reason": "stop"
  },
  "audit": {
    "audit_version": 1,
    "source_map_id": "d2dd350d860b8141e52306cbbcafb22f97d091194eb1cdc839a528c2990715eb",
    "gold_groups": [
      {
        "group_id": "g1",
        "alternatives": [
          [
            "membership-benefits.md:001:0e401c77a9b672d13f8b19cff2c0db798e72167d869d0b9107819fa281fb34f3"
          ]
        ]
      },
      {
        "group_id": "g2",
        "alternatives": [
          [
            "membership-benefits.md:002:c9a7d21f43bfd7f6a83ec9116841139c65e10365b0a347be54443c42fd024acc"
          ]
        ]
      }
    ],
    "answer_points": [
      {
        "point_id": "p1",
        "text": "金卡按有效累计消费满 5000 元升级，不按年消费计算",
        "condition": "有效累计商品实付、不含运费、扣除退款；折扣活动范围以页面为准",
        "aliases": []
      },
      {
        "point_id": "p2",
        "text": "金卡生日当月可在会员中心领取猫罐头礼盒，规格与期限以页面为准",
        "condition": "生日当月在会员中心领取，规格期限以页面为准",
        "aliases": []
      }
    ],
    "candidate_ranking": [
      {
        "chunk_id": 1875,
        "score": 9.339435577392578,
        "score_kind": "bm25"
      },
      {
        "chunk_id": 1874,
        "score": 7.171276092529297,
        "score_kind": "bm25"
      },
      {
        "chunk_id": 1845,
        "score": 6.90592098236084,
        "score_kind": "bm25"
      },
      {
        "chunk_id": 1876,
        "score": 6.212222576141357,
        "score_kind": "bm25"
      },
      {
        "chunk_id": 1852,
        "score": 4.681387424468994,
        "score_kind": "bm25"
      },
      {
        "chunk_id": 1833,
        "score": 4.314119338989258,
        "score_kind": "bm25"
      },
      {
        "chunk_id": 1838,
        "score": 4.2695698738098145,
        "score_kind": "bm25"
      }
    ],
    "final_ranking": [
      {
        "chunk_id": 1875,
        "score": 9.339435577392578,
        "score_kind": "bm25"
      },
      {
        "chunk_id": 1874,
        "score": 7.171276092529297,
        "score_kind": "bm25"
      },
      {
        "chunk_id": 1845,
        "score": 6.90592098236084,
        "score_kind": "bm25"
      },
      {
        "chunk_id": 1876,
        "score": 6.212222576141357,
        "score_kind": "bm25"
      },
      {
        "chunk_id": 1852,
        "score": 4.681387424468994,
        "score_kind": "bm25"
      },
      {
        "chunk_id": 1833,
        "score": 4.314119338989258,
        "score_kind": "bm25"
      },
      {
        "chunk_id": 1838,
        "score": 4.2695698738098145,
        "score_kind": "bm25"
      }
    ]
  }
}
````

### A21 / hybrid

````json
{
  "eval_id": "A21",
  "strategy": "hybrid",
  "bucket": "A_policy",
  "difficulty": "policy",
  "category": null,
  "should_refuse": false,
  "refused": false,
  "status": "completed",
  "stage": "complete",
  "query": "喵金等级要年消费多少钱,有什么生日礼",
  "query_plan": {
    "standard": "喵金等级要年消费多少钱,有什么生日礼",
    "expansions": []
  },
  "mapped_groups": [
    {
      "group_id": "g1",
      "alternatives": [
        [
          1874
        ]
      ]
    },
    {
      "group_id": "g2",
      "alternatives": [
        [
          1875
        ]
      ]
    }
  ],
  "candidate_ids": [
    1875,
    1845,
    1874,
    1833,
    1876,
    1852,
    1838,
    1877,
    1853,
    1854,
    1855,
    1851,
    1837,
    1859,
    1861,
    1860,
    1842,
    1862,
    1844,
    1857,
    1850,
    1872,
    1863,
    1846,
    1864,
    1858,
    1847,
    1834,
    1878,
    1856,
    1832,
    1870,
    1840,
    1843,
    1873,
    1879,
    1831,
    1865,
    1867,
    1871,
    1868,
    1836,
    1880,
    1835,
    1849,
    1841,
    1869,
    1866,
    1839,
    1848
  ],
  "final_ids": [
    1875,
    1845,
    1874,
    1833,
    1876,
    1852,
    1838,
    1877,
    1853,
    1854
  ],
  "prompt_citations": [
    {
      "n": 1,
      "chunk_id": "1875",
      "section_path": "会员权益/生日礼",
      "question": "生日礼",
      "answer": "银卡会员生日当月可领取一份猫零食小样，金卡会员生日当月可领取一份猫罐头礼盒。需在会员中心领取，礼品规格与领取期限以页面标注为准，不承诺额外折现或补偿。"
    },
    {
      "n": 3,
      "chunk_id": "1874",
      "section_path": "会员权益/会员等级",
      "question": "会员等级",
      "answer": "会员分为普通、银卡和金卡三档，按有效累计消费金额自动升级，不按年度消费金额计算。累计消费未满 1000 元为普通会员，满 1000 元起为银卡，满 5000 元起为金卡。\n\n有效累计消费指已完成订单的商品实际支付金额，不含配送费；退货退款部分从有效累计消费中扣除。退款后根据更新的累计消费重新计算等级，未达到原门槛时可能降级。等级与适用权益在会员中心展示。\n\n银卡在参与会员折扣的商品上享 95 折，金卡享 9 折。折扣适用商品和活动范围以结算页面标注为准。会员折扣、优惠券与满减是否叠加也以当次活动页面为准，不能一概承诺全部优惠同时生效。"
    },
    {
      "n": 5,
      "chunk_id": "1876",
      "section_path": "积分规则/积分怎么攒",
      "question": "积分怎么攒",
      "answer": "已完成订单每实际支付 1 元商品金额累计 1 积分，不计配送费；退款后按对应商品金额同步扣回积分。活动期间的双倍积分属于额外积分奖励，不计入会员等级升级；会员等级仍按有效累计消费金额计算。"
    },
    {
      "n": 7,
      "chunk_id": "1838",
      "section_path": "商品与购物 FAQ/退货政策是什么",
      "question": "退货政策是什么",
      "answer": "支持 7 天无理由退货,商品需保持完好、不影响二次销售,具体以平台售后规则为准。"
    },
    {
      "n": 9,
      "chunk_id": "1853",
      "section_path": "商品规格手册/智能猫砂盆 Pro(型号 MH-LP100)",
      "question": "智能猫砂盆 Pro(型号 MH-LP100)",
      "answer": "- 型号:MH-LP100\n- 适用猫咪体重:1.5kg 至 8kg\n- 猫砂容量:9L,废砂盒容量约 7 天(单猫)\n- 核心功能:自动感应清理、活性炭除臭、App 远程监控与健康记录\n- 供电:220V 市电,断电后配置自动保存\n- 清理提示:废砂盒满时 App 推送提醒,建议每 5 至 7 天倾倒一次"
    },
    {
      "n": 10,
      "chunk_id": "1854",
      "section_path": "商品规格手册/智能猫砂盆 Lite(型号 MH-LP50)",
      "question": "智能猫砂盆 Lite(型号 MH-LP50)",
      "answer": "- 型号:MH-LP50\n- 适用猫咪体重:1.5kg 至 6kg\n- 猫砂容量:6L\n- 核心功能:自动感应清理、物理除臭盖板;不含 App 联网功能\n- 与 Pro 差异:Lite 无 App 远程监控与健康记录,价格更低,适合单猫家庭"
    },
    {
      "n": 8,
      "chunk_id": "1877",
      "section_path": "积分规则/积分怎么用",
      "question": "积分怎么用",
      "answer": "积分可在结算时抵扣商品金额，100 积分抵 1 元现金，单笔订单最多抵 30 元，不用于抵扣偏远地区附加运费，也不支持直接提现。\n\n2000 积分可兑换自动饮水机滤芯 3 片，该兑换套装适用于 MH-W40，普通配送地区包邮；偏远地区附加配送费仍需按页面规则确认。MH-W40 的滤芯更换周期以商品规格手册为准。\n\n800 积分可兑换猫零食小样，普通配送地区另收 6 元运费；该兑换不直接套用普通购物订单的满 99 元包邮规则。兑换商品、可用库存及偏远地区配送规则以兑换页面标注为准。"
    },
    {
      "n": 6,
      "chunk_id": "1852",
      "section_path": "商品规格手册",
      "question": "商品规格手册",
      "answer": "本手册收录喵喵优选自营智能硬件的型号、规格与使用要点,便于按具体型号查询。"
    },
    {
      "n": 4,
      "chunk_id": "1833",
      "section_path": "售后手册/设备安装与激活",
      "question": "设备安装与激活",
      "answer": "智能设备首次使用需下载「喵喵优选」App,按说明书扫码添加设备并连接 2.4G Wi-Fi 完成激活;猫爬架等非联网商品按随附图解自行组装。"
    },
    {
      "n": 2,
      "chunk_id": "1845",
      "section_path": "商品与购物 FAQ/会员等级与积分规则",
      "question": "会员等级与积分规则",
      "answer": "会员分为普通、银卡、金卡三档,按累计消费自动升级。每消费 1 元得 1 积分,积分可在结算时抵扣,100 积分抵 1 元。"
    }
  ],
  "decision": {
    "useful": true,
    "reason": "等级按累计消费非年消费，金卡满5000元；金卡生日礼为猫罐头礼盒",
    "response_kind": "knowledge",
    "source": null
  },
  "answer": "您好，为您解答如下：\n\n**会员等级（金卡）**[3]\n会员等级按“有效累计消费金额”计算，并非按年度消费：\n- 累计消费满 5000 元起为金卡（满 1000 元为银卡，未满 1000 元为普通会员）\n- 有效累计消费指已完成订单的商品实际支付金额，不含配送费，退货退款部分会扣除\n\n**生日礼**[1]\n- 金卡会员生日当月可领取一份猫罐头礼盒（银卡为猫零食小样）\n- 需在会员中心领取，礼品规格与领取期限以页面标注为准\n\n如还有其他问题，欢迎随时咨询～",
  "point_verdicts": [
    {
      "point_id": "p1",
      "covered": true,
      "reason": "回答说明金卡按有效累计消费满5000元升级，不按年消费，并保留商品实付、不含配送费、退款扣除等条件，覆盖完整"
    },
    {
      "point_id": "p2",
      "covered": true,
      "reason": "回答说明金卡生日当月可在会员中心领取猫罐头礼盒，并注明规格与领取期限以页面为准，条件保留"
    }
  ],
  "claim_verdicts": [
    {
      "claim": "会员等级按有效累计消费金额计算，不按年度消费",
      "supported": true,
      "reason": "证据3明确说明按有效累计消费金额自动升级，不按年度消费金额计算"
    },
    {
      "claim": "累计消费满5000元起为金卡，满1000元为银卡，未满1000元为普通会员",
      "supported": true,
      "reason": "证据3列明三档门槛与金额一致"
    },
    {
      "claim": "有效累计消费指已完成订单的商品实际支付金额，不含配送费，退货退款部分会扣除",
      "supported": true,
      "reason": "证据3明确该定义及扣除规则"
    },
    {
      "claim": "金卡会员生日当月可领取一份猫罐头礼盒",
      "supported": true,
      "reason": "证据1说明金卡会员生日当月可领猫罐头礼盒"
    },
    {
      "claim": "银卡会员生日礼为猫零食小样",
      "supported": true,
      "reason": "证据1说明银卡会员生日当月可领猫零食小样"
    },
    {
      "claim": "生日礼需在会员中心领取，礼品规格与领取期限以页面标注为准",
      "supported": true,
      "reason": "证据1明确领取方式及以页面标注为准"
    }
  ],
  "metrics": {
    "recall_at_5": 1.0,
    "recall_at_10": 1.0,
    "mrr_at_10": 1.0,
    "all_groups_hit_at_5": 1.0,
    "all_groups_hit_at_10": 1.0,
    "candidate_group_coverage": 1.0,
    "prompt_group_coverage": 1.0,
    "answer_point_coverage": 1.0,
    "faithfulness": 1.0,
    "absent_refusal_rate": null,
    "answerable_false_refusal_rate": 0.0
  },
  "error": null,
  "elapsed_ms": 11001.921199960634,
  "judge_snapshot": {
    "prompt_version": "joint-generation-v2.1",
    "finish_reason": "stop"
  },
  "audit": {
    "audit_version": 1,
    "source_map_id": "d2dd350d860b8141e52306cbbcafb22f97d091194eb1cdc839a528c2990715eb",
    "gold_groups": [
      {
        "group_id": "g1",
        "alternatives": [
          [
            "membership-benefits.md:001:0e401c77a9b672d13f8b19cff2c0db798e72167d869d0b9107819fa281fb34f3"
          ]
        ]
      },
      {
        "group_id": "g2",
        "alternatives": [
          [
            "membership-benefits.md:002:c9a7d21f43bfd7f6a83ec9116841139c65e10365b0a347be54443c42fd024acc"
          ]
        ]
      }
    ],
    "answer_points": [
      {
        "point_id": "p1",
        "text": "金卡按有效累计消费满 5000 元升级，不按年消费计算",
        "condition": "有效累计商品实付、不含运费、扣除退款；折扣活动范围以页面为准",
        "aliases": []
      },
      {
        "point_id": "p2",
        "text": "金卡生日当月可在会员中心领取猫罐头礼盒，规格与期限以页面为准",
        "condition": "生日当月在会员中心领取，规格期限以页面为准",
        "aliases": []
      }
    ],
    "candidate_ranking": [
      {
        "chunk_id": 1875,
        "score": 0.032786883413791656,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1845,
        "score": 0.0320020467042923,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1874,
        "score": 0.0320020467042923,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1833,
        "score": 0.03007688745856285,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1876,
        "score": 0.0295138880610466,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1852,
        "score": 0.029083244502544403,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1838,
        "score": 0.025678060948848724,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1877,
        "score": 0.015625,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1853,
        "score": 0.015384615398943424,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1854,
        "score": 0.01515151560306549,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1855,
        "score": 0.014705882407724857,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1851,
        "score": 0.014492753893136978,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1837,
        "score": 0.014285714365541935,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1859,
        "score": 0.014084506779909134,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1861,
        "score": 0.013513513840734959,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1860,
        "score": 0.013333333656191826,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1842,
        "score": 0.01315789483487606,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1862,
        "score": 0.012987012974917889,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1844,
        "score": 0.012820512987673283,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1857,
        "score": 0.012658228166401386,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1850,
        "score": 0.012500000186264515,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1872,
        "score": 0.012345679104328156,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1863,
        "score": 0.012195121496915817,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1846,
        "score": 0.012048192322254181,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1864,
        "score": 0.011904762126505375,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1858,
        "score": 0.0117647061124444,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1847,
        "score": 0.011627906933426857,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1834,
        "score": 0.01149425283074379,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1878,
        "score": 0.011363636702299118,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1856,
        "score": 0.01123595517128706,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1832,
        "score": 0.011111111380159855,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1870,
        "score": 0.010989011265337467,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1840,
        "score": 0.010869565419852734,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1843,
        "score": 0.010638297535479069,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1873,
        "score": 0.010526316240429878,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1879,
        "score": 0.010416666977107525,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1831,
        "score": 0.010309278033673763,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1865,
        "score": 0.010204081423580647,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1867,
        "score": 0.010101010091602802,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1871,
        "score": 0.009999999776482582,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1868,
        "score": 0.009900989942252636,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1836,
        "score": 0.009803921915590763,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1880,
        "score": 0.009708737954497337,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1835,
        "score": 0.009615384973585606,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1849,
        "score": 0.009523809887468815,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1841,
        "score": 0.009433962404727936,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1869,
        "score": 0.009345794096589088,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1866,
        "score": 0.009259259328246117,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1839,
        "score": 0.00917431153357029,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1848,
        "score": 0.00909090880304575,
        "score_kind": "rrf"
      }
    ],
    "final_ranking": [
      {
        "chunk_id": 1875,
        "score": 0.032786883413791656,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1845,
        "score": 0.0320020467042923,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1874,
        "score": 0.0320020467042923,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1833,
        "score": 0.03007688745856285,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1876,
        "score": 0.0295138880610466,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1852,
        "score": 0.029083244502544403,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1838,
        "score": 0.025678060948848724,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1877,
        "score": 0.015625,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1853,
        "score": 0.015384615398943424,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1854,
        "score": 0.01515151560306549,
        "score_kind": "rrf"
      }
    ]
  }
}
````

### A21 / hybrid_rerank

````json
{
  "eval_id": "A21",
  "strategy": "hybrid_rerank",
  "bucket": "A_policy",
  "difficulty": "policy",
  "category": null,
  "should_refuse": false,
  "refused": false,
  "status": "completed",
  "stage": "complete",
  "query": "喵金等级要年消费多少钱,有什么生日礼",
  "query_plan": {
    "standard": "喵金等级要年消费多少钱,有什么生日礼",
    "expansions": []
  },
  "mapped_groups": [
    {
      "group_id": "g1",
      "alternatives": [
        [
          1874
        ]
      ]
    },
    {
      "group_id": "g2",
      "alternatives": [
        [
          1875
        ]
      ]
    }
  ],
  "candidate_ids": [
    1875,
    1845,
    1874,
    1833,
    1876,
    1852,
    1838,
    1877,
    1853,
    1854,
    1855,
    1851,
    1837,
    1859,
    1861,
    1860,
    1842,
    1862,
    1844,
    1857,
    1850,
    1872,
    1863,
    1846,
    1864,
    1858,
    1847,
    1834,
    1878,
    1856,
    1832,
    1870,
    1840,
    1843,
    1873,
    1879,
    1831,
    1865,
    1867,
    1871,
    1868,
    1836,
    1880,
    1835,
    1849,
    1841,
    1869,
    1866,
    1839,
    1848
  ],
  "final_ids": [
    1874,
    1875,
    1845,
    1876,
    1877,
    1837,
    1851,
    1833,
    1852,
    1842
  ],
  "prompt_citations": [
    {
      "n": 1,
      "chunk_id": "1874",
      "section_path": "会员权益/会员等级",
      "question": "会员等级",
      "answer": "会员分为普通、银卡和金卡三档，按有效累计消费金额自动升级，不按年度消费金额计算。累计消费未满 1000 元为普通会员，满 1000 元起为银卡，满 5000 元起为金卡。\n\n有效累计消费指已完成订单的商品实际支付金额，不含配送费；退货退款部分从有效累计消费中扣除。退款后根据更新的累计消费重新计算等级，未达到原门槛时可能降级。等级与适用权益在会员中心展示。\n\n银卡在参与会员折扣的商品上享 95 折，金卡享 9 折。折扣适用商品和活动范围以结算页面标注为准。会员折扣、优惠券与满减是否叠加也以当次活动页面为准，不能一概承诺全部优惠同时生效。"
    },
    {
      "n": 3,
      "chunk_id": "1845",
      "section_path": "商品与购物 FAQ/会员等级与积分规则",
      "question": "会员等级与积分规则",
      "answer": "会员分为普通、银卡、金卡三档,按累计消费自动升级。每消费 1 元得 1 积分,积分可在结算时抵扣,100 积分抵 1 元。"
    },
    {
      "n": 5,
      "chunk_id": "1877",
      "section_path": "积分规则/积分怎么用",
      "question": "积分怎么用",
      "answer": "积分可在结算时抵扣商品金额，100 积分抵 1 元现金，单笔订单最多抵 30 元，不用于抵扣偏远地区附加运费，也不支持直接提现。\n\n2000 积分可兑换自动饮水机滤芯 3 片，该兑换套装适用于 MH-W40，普通配送地区包邮；偏远地区附加配送费仍需按页面规则确认。MH-W40 的滤芯更换周期以商品规格手册为准。\n\n800 积分可兑换猫零食小样，普通配送地区另收 6 元运费；该兑换不直接套用普通购物订单的满 99 元包邮规则。兑换商品、可用库存及偏远地区配送规则以兑换页面标注为准。"
    },
    {
      "n": 7,
      "chunk_id": "1851",
      "section_path": "商品与购物 FAQ/会员运费权益",
      "question": "会员运费权益",
      "answer": "金卡会员每月享 3 次免运费权益,银卡会员享 1 次;权益不与偏远地区附加运费冲抵,当月未用完不结转。"
    },
    {
      "n": 9,
      "chunk_id": "1852",
      "section_path": "商品规格手册",
      "question": "商品规格手册",
      "answer": "本手册收录喵喵优选自营智能硬件的型号、规格与使用要点,便于按具体型号查询。"
    },
    {
      "n": 10,
      "chunk_id": "1842",
      "section_path": "商品与购物 FAQ/运费怎么算",
      "question": "运费怎么算",
      "answer": "单笔订单满 99 元包邮,未满收取 10 元运费,偏远地区运费另计。邮费即运费,按此规则收取。"
    },
    {
      "n": 8,
      "chunk_id": "1833",
      "section_path": "售后手册/设备安装与激活",
      "question": "设备安装与激活",
      "answer": "智能设备首次使用需下载「喵喵优选」App,按说明书扫码添加设备并连接 2.4G Wi-Fi 完成激活;猫爬架等非联网商品按随附图解自行组装。"
    },
    {
      "n": 6,
      "chunk_id": "1837",
      "section_path": "售后手册/会员专属售后权益",
      "question": "会员专属售后权益",
      "answer": "金卡会员享优先客服接入与上门取件退换货;银卡会员享退换货运费权益 1 次/月。具体权益以会员中心页面标注为准。"
    },
    {
      "n": 4,
      "chunk_id": "1876",
      "section_path": "积分规则/积分怎么攒",
      "question": "积分怎么攒",
      "answer": "已完成订单每实际支付 1 元商品金额累计 1 积分，不计配送费；退款后按对应商品金额同步扣回积分。活动期间的双倍积分属于额外积分奖励，不计入会员等级升级；会员等级仍按有效累计消费金额计算。"
    },
    {
      "n": 2,
      "chunk_id": "1875",
      "section_path": "会员权益/生日礼",
      "question": "生日礼",
      "answer": "银卡会员生日当月可领取一份猫零食小样，金卡会员生日当月可领取一份猫罐头礼盒。需在会员中心领取，礼品规格与领取期限以页面标注为准，不承诺额外折现或补偿。"
    }
  ],
  "decision": {
    "useful": true,
    "reason": "证据覆盖等级门槛和生日礼",
    "response_kind": "knowledge",
    "source": null
  },
  "answer": "您好！根据查询结果，目前会员等级分为普通、银卡和金卡三档，暂无“喵金”等级，等级按累计消费金额计算，并非按年度消费：\n\n- 累计消费满 1000 元起为银卡，满 5000 元起为金卡 [1]。\n- 生日礼：银卡会员生日当月可领取猫零食小样一份，金卡会员生日当月可领取猫罐头礼盒一份，需在会员中心领取，礼品规格与领取期限以页面标注为准 [2]。\n\n如有其他问题，欢迎随时咨询~",
  "point_verdicts": [
    {
      "point_id": "p1",
      "covered": false,
      "reason": "回答提到满5000元为金卡且按累计非年度消费，但缺失条件：有效累计指商品实付、不含运费、扣除退款，仅覆盖部分事实"
    },
    {
      "point_id": "p2",
      "covered": true,
      "reason": "回答说明金卡生日当月在会员中心领取猫罐头礼盒，规格与期限以页面为准，条件完整"
    }
  ],
  "claim_verdicts": [
    {
      "claim": "会员等级分为普通、银卡和金卡三档",
      "supported": true,
      "reason": "证据1明确会员分普通、银卡、金卡三档"
    },
    {
      "claim": "暂无“喵金”等级",
      "supported": false,
      "reason": "证据仅列出三档等级，未提及“喵金”，证据沉默不证明否定"
    },
    {
      "claim": "等级按累计消费金额计算，并非按年度消费",
      "supported": true,
      "reason": "证据1明确按有效累计消费金额升级，不按年度消费金额计算"
    },
    {
      "claim": "累计消费满1000元起为银卡",
      "supported": true,
      "reason": "证据1明确满1000元起为银卡"
    },
    {
      "claim": "累计消费满5000元起为金卡",
      "supported": true,
      "reason": "证据1明确满5000元起为金卡"
    },
    {
      "claim": "银卡会员生日当月可领取猫零食小样一份",
      "supported": true,
      "reason": "证据2明确银卡生日当月可领取猫零食小样一份"
    },
    {
      "claim": "金卡会员生日当月可领取猫罐头礼盒一份",
      "supported": true,
      "reason": "证据2明确金卡生日当月可领取猫罐头礼盒一份"
    },
    {
      "claim": "生日礼需在会员中心领取，礼品规格与领取期限以页面标注为准",
      "supported": true,
      "reason": "证据2明确需在会员中心领取，规格与期限以页面标注为准"
    }
  ],
  "metrics": {
    "recall_at_5": 1.0,
    "recall_at_10": 1.0,
    "mrr_at_10": 1.0,
    "all_groups_hit_at_5": 1.0,
    "all_groups_hit_at_10": 1.0,
    "candidate_group_coverage": 1.0,
    "prompt_group_coverage": 1.0,
    "answer_point_coverage": 0.5,
    "faithfulness": 0.875,
    "absent_refusal_rate": null,
    "answerable_false_refusal_rate": 0.0
  },
  "error": null,
  "elapsed_ms": 17184.074700111523,
  "judge_snapshot": {
    "prompt_version": "joint-generation-v2.1",
    "finish_reason": "stop"
  },
  "audit": {
    "audit_version": 1,
    "source_map_id": "d2dd350d860b8141e52306cbbcafb22f97d091194eb1cdc839a528c2990715eb",
    "gold_groups": [
      {
        "group_id": "g1",
        "alternatives": [
          [
            "membership-benefits.md:001:0e401c77a9b672d13f8b19cff2c0db798e72167d869d0b9107819fa281fb34f3"
          ]
        ]
      },
      {
        "group_id": "g2",
        "alternatives": [
          [
            "membership-benefits.md:002:c9a7d21f43bfd7f6a83ec9116841139c65e10365b0a347be54443c42fd024acc"
          ]
        ]
      }
    ],
    "answer_points": [
      {
        "point_id": "p1",
        "text": "金卡按有效累计消费满 5000 元升级，不按年消费计算",
        "condition": "有效累计商品实付、不含运费、扣除退款；折扣活动范围以页面为准",
        "aliases": []
      },
      {
        "point_id": "p2",
        "text": "金卡生日当月可在会员中心领取猫罐头礼盒，规格与期限以页面为准",
        "condition": "生日当月在会员中心领取，规格期限以页面为准",
        "aliases": []
      }
    ],
    "candidate_ranking": [
      {
        "chunk_id": 1875,
        "score": 0.032786883413791656,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1845,
        "score": 0.0320020467042923,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1874,
        "score": 0.0320020467042923,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1833,
        "score": 0.03007688745856285,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1876,
        "score": 0.0295138880610466,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1852,
        "score": 0.029083244502544403,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1838,
        "score": 0.025678060948848724,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1877,
        "score": 0.015625,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1853,
        "score": 0.015384615398943424,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1854,
        "score": 0.01515151560306549,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1855,
        "score": 0.014705882407724857,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1851,
        "score": 0.014492753893136978,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1837,
        "score": 0.014285714365541935,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1859,
        "score": 0.014084506779909134,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1861,
        "score": 0.013513513840734959,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1860,
        "score": 0.013333333656191826,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1842,
        "score": 0.01315789483487606,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1862,
        "score": 0.012987012974917889,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1844,
        "score": 0.012820512987673283,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1857,
        "score": 0.012658228166401386,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1850,
        "score": 0.012500000186264515,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1872,
        "score": 0.012345679104328156,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1863,
        "score": 0.012195121496915817,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1846,
        "score": 0.012048192322254181,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1864,
        "score": 0.011904762126505375,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1858,
        "score": 0.0117647061124444,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1847,
        "score": 0.011627906933426857,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1834,
        "score": 0.01149425283074379,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1878,
        "score": 0.011363636702299118,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1856,
        "score": 0.01123595517128706,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1832,
        "score": 0.011111111380159855,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1870,
        "score": 0.010989011265337467,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1840,
        "score": 0.010869565419852734,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1843,
        "score": 0.010638297535479069,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1873,
        "score": 0.010526316240429878,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1879,
        "score": 0.010416666977107525,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1831,
        "score": 0.010309278033673763,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1865,
        "score": 0.010204081423580647,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1867,
        "score": 0.010101010091602802,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1871,
        "score": 0.009999999776482582,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1868,
        "score": 0.009900989942252636,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1836,
        "score": 0.009803921915590763,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1880,
        "score": 0.009708737954497337,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1835,
        "score": 0.009615384973585606,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1849,
        "score": 0.009523809887468815,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1841,
        "score": 0.009433962404727936,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1869,
        "score": 0.009345794096589088,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1866,
        "score": 0.009259259328246117,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1839,
        "score": 0.00917431153357029,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1848,
        "score": 0.00909090880304575,
        "score_kind": "rrf"
      }
    ],
    "final_ranking": [
      {
        "chunk_id": 1874,
        "score": 0.13225547969341278,
        "score_kind": "rerank"
      },
      {
        "chunk_id": 1875,
        "score": 0.10479357093572617,
        "score_kind": "rerank"
      },
      {
        "chunk_id": 1845,
        "score": 0.024253156036138535,
        "score_kind": "rerank"
      },
      {
        "chunk_id": 1876,
        "score": 0.002775798784568906,
        "score_kind": "rerank"
      },
      {
        "chunk_id": 1877,
        "score": 0.0017447700956836343,
        "score_kind": "rerank"
      },
      {
        "chunk_id": 1837,
        "score": 0.00041021808283403516,
        "score_kind": "rerank"
      },
      {
        "chunk_id": 1851,
        "score": 0.0003726145951077342,
        "score_kind": "rerank"
      },
      {
        "chunk_id": 1833,
        "score": 0.00016411140677519143,
        "score_kind": "rerank"
      },
      {
        "chunk_id": 1852,
        "score": 5.7113637012662366e-05,
        "score_kind": "rerank"
      },
      {
        "chunk_id": 1842,
        "score": 5.597442213911563e-05,
        "score_kind": "rerank"
      }
    ]
  }
}
````

### A43 / dense

````json
{
  "eval_id": "A43",
  "strategy": "dense",
  "bucket": "A_policy",
  "difficulty": "policy",
  "category": null,
  "should_refuse": false,
  "refused": false,
  "status": "completed",
  "stage": "complete",
  "query": "少发漏发导致的退换货,运费由谁承担",
  "query_plan": {
    "standard": "少发漏发导致的退换货,运费由谁承担",
    "expansions": []
  },
  "mapped_groups": [
    {
      "group_id": "g1",
      "alternatives": [
        [
          1869
        ]
      ]
    }
  ],
  "candidate_ids": [
    1869,
    1868,
    1871,
    1842,
    1840,
    1836,
    1837,
    1847,
    1867,
    1870,
    1851,
    1849,
    1865,
    1873,
    1866,
    1831,
    1838,
    1848,
    1877,
    1839,
    1832,
    1876,
    1841,
    1850,
    1872,
    1879,
    1844,
    1843,
    1834,
    1878,
    1846,
    1874,
    1845,
    1857,
    1875,
    1833,
    1835,
    1855,
    1853,
    1858,
    1856,
    1854,
    1880,
    1862,
    1852,
    1863,
    1860,
    1861,
    1864,
    1859
  ],
  "final_ids": [
    1869,
    1868,
    1871,
    1842,
    1840,
    1836,
    1837,
    1847,
    1867,
    1870
  ],
  "prompt_citations": [
    {
      "n": 1,
      "chunk_id": "1869",
      "section_path": "退货退款政策/退换货运费承担",
      "question": "退换货运费承担",
      "answer": "无理由退货的退回运费由买家承担;因商品质量问题、发错货、少发漏发导致的退换货,运费由平台承担。运费承担以平台售后规则最终判定为准。"
    },
    {
      "n": 3,
      "chunk_id": "1871",
      "section_path": "退货退款政策/运输破损处理",
      "question": "运输破损处理",
      "answer": "商品运输途中破损的,请在签收后 48 小时内联系客服并提供开箱视频与照片,核实后可免费补发或退款,相关运费由平台承担。"
    },
    {
      "n": 5,
      "chunk_id": "1840",
      "section_path": "商品与购物 FAQ/换货流程怎么走",
      "question": "换货流程怎么走",
      "answer": "收到商品 7 天内可申请换货,联系客服登记后将商品寄回,平台核验无误后补发新品。"
    },
    {
      "n": 7,
      "chunk_id": "1837",
      "section_path": "售后手册/会员专属售后权益",
      "question": "会员专属售后权益",
      "answer": "金卡会员享优先客服接入与上门取件退换货;银卡会员享退换货运费权益 1 次/月。具体权益以会员中心页面标注为准。"
    },
    {
      "n": 9,
      "chunk_id": "1867",
      "section_path": "退货退款政策/换货政策/换货条件",
      "question": "换货条件",
      "answer": "收到商品 7 天内,商品完好且配件齐全的,可申请一次同款换货;不同型号或颜色需先退货再重新下单。"
    },
    {
      "n": 10,
      "chunk_id": "1870",
      "section_path": "退货退款政策/质量问题与保修",
      "question": "质量问题与保修",
      "answer": "电子类商品自签收起保修 12 个月,保修期内非人为损坏可申请免费维修或换货;人为损坏、超保商品维修可能收取工本费。"
    },
    {
      "n": 8,
      "chunk_id": "1847",
      "section_path": "商品与购物 FAQ/配送范围与偏远地区",
      "question": "配送范围与偏远地区",
      "answer": "全国大部分地区支持配送,新疆、西藏、内蒙古等偏远地区运费另计且时效顺延;港澳台及海外暂不支持自营配送。"
    },
    {
      "n": 6,
      "chunk_id": "1836",
      "section_path": "售后手册/维修寄修流程",
      "question": "维修寄修流程",
      "answer": "保修期内设备故障,联系客服登记后按指引将设备寄回指定维修点,核验后免费维修并寄回;超保或人为损坏维修可能收取工本费,费用会提前告知。"
    },
    {
      "n": 4,
      "chunk_id": "1842",
      "section_path": "商品与购物 FAQ/运费怎么算",
      "question": "运费怎么算",
      "answer": "单笔订单满 99 元包邮,未满收取 10 元运费,偏远地区运费另计。邮费即运费,按此规则收取。"
    },
    {
      "n": 2,
      "chunk_id": "1868",
      "section_path": "退货退款政策/换货政策/换货运费",
      "question": "换货运费",
      "answer": "非质量问题的换货,往返运费由买家承担;因质量问题或发错货的换货,往返运费由平台承担。"
    }
  ],
  "decision": {
    "useful": true,
    "reason": "少发漏发运费由平台承担有直接证据",
    "response_kind": "knowledge",
    "source": null
  },
  "answer": "您好！因少发漏发导致的退换货，运费由平台承担[1]。具体以平台售后规则的最终判定为准[1]。如需处理，请提供订单号，我可以为您进一步协助～",
  "point_verdicts": [
    {
      "point_id": "p1",
      "covered": true,
      "reason": "回答明确指出少发漏发导致的退换货运费由平台承担，并提及以平台售后规则最终判定为准，条件与事实均覆盖。"
    }
  ],
  "claim_verdicts": [
    {
      "claim": "因少发漏发导致的退换货，运费由平台承担",
      "supported": true,
      "reason": "证据1明确：因商品质量问题、发错货、少发漏发导致的退换货，运费由平台承担。"
    },
    {
      "claim": "运费承担以平台售后规则最终判定为准",
      "supported": true,
      "reason": "证据1明确：运费承担以平台售后规则最终判定为准。"
    }
  ],
  "metrics": {
    "recall_at_5": 1.0,
    "recall_at_10": 1.0,
    "mrr_at_10": 1.0,
    "all_groups_hit_at_5": 1.0,
    "all_groups_hit_at_10": 1.0,
    "candidate_group_coverage": 1.0,
    "prompt_group_coverage": 1.0,
    "answer_point_coverage": 1.0,
    "faithfulness": 1.0,
    "absent_refusal_rate": null,
    "answerable_false_refusal_rate": 0.0
  },
  "error": null,
  "elapsed_ms": 7367.090600077063,
  "judge_snapshot": {
    "prompt_version": "joint-generation-v2.1",
    "finish_reason": "stop"
  },
  "audit": {
    "audit_version": 1,
    "source_map_id": "d2dd350d860b8141e52306cbbcafb22f97d091194eb1cdc839a528c2990715eb",
    "gold_groups": [
      {
        "group_id": "g1",
        "alternatives": [
          [
            "returns-policy.md:005:4d4b2ea9115f9f9c717e0b83cded75c9048bc1b04a4621131131a6e1d023f11c"
          ]
        ]
      }
    ],
    "answer_points": [
      {
        "point_id": "p1",
        "text": "少发漏发导致的退换货运费由平台承担，以售后规则最终判定为准",
        "condition": "运费按退换货原因与平台最终判定区分",
        "aliases": []
      }
    ],
    "candidate_ranking": [
      {
        "chunk_id": 1869,
        "score": 0.7039955854415894,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1868,
        "score": 0.6646378636360168,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1871,
        "score": 0.6263620257377625,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1842,
        "score": 0.575890839099884,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1840,
        "score": 0.5652117133140564,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1836,
        "score": 0.5471986532211304,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1837,
        "score": 0.5470176339149475,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1847,
        "score": 0.5431363582611084,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1867,
        "score": 0.5423271059989929,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1870,
        "score": 0.5404635071754456,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1851,
        "score": 0.5344502925872803,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1849,
        "score": 0.5340436697006226,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1865,
        "score": 0.5290358066558838,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1873,
        "score": 0.5246568322181702,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1866,
        "score": 0.5235435366630554,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1831,
        "score": 0.520516574382782,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1838,
        "score": 0.517553448677063,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1848,
        "score": 0.5175460577011108,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1877,
        "score": 0.511620283126831,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1839,
        "score": 0.5046658515930176,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1832,
        "score": 0.5022866725921631,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1876,
        "score": 0.49774226546287537,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1841,
        "score": 0.4967568516731262,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1850,
        "score": 0.492765873670578,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1872,
        "score": 0.4752086102962494,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1879,
        "score": 0.4687517285346985,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1844,
        "score": 0.46612662076950073,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1843,
        "score": 0.46289175748825073,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1834,
        "score": 0.45831504464149475,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1878,
        "score": 0.4470350742340088,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1846,
        "score": 0.44225388765335083,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1874,
        "score": 0.42225074768066406,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1845,
        "score": 0.42026203870773315,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1857,
        "score": 0.41022181510925293,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1875,
        "score": 0.40304166078567505,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1833,
        "score": 0.39646226167678833,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1835,
        "score": 0.39401930570602417,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1855,
        "score": 0.3927266299724579,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1853,
        "score": 0.3845040202140808,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1858,
        "score": 0.3826260566711426,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1856,
        "score": 0.3788939118385315,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1854,
        "score": 0.37215909361839294,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1880,
        "score": 0.36426985263824463,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1862,
        "score": 0.3576604723930359,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1852,
        "score": 0.34681951999664307,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1863,
        "score": 0.3358815014362335,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1860,
        "score": 0.31172996759414673,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1861,
        "score": 0.30607473850250244,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1864,
        "score": 0.28341490030288696,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1859,
        "score": 0.26807937026023865,
        "score_kind": "cosine"
      }
    ],
    "final_ranking": [
      {
        "chunk_id": 1869,
        "score": 0.7039955854415894,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1868,
        "score": 0.6646378636360168,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1871,
        "score": 0.6263620257377625,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1842,
        "score": 0.575890839099884,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1840,
        "score": 0.5652117133140564,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1836,
        "score": 0.5471986532211304,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1837,
        "score": 0.5470176339149475,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1847,
        "score": 0.5431363582611084,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1867,
        "score": 0.5423271059989929,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1870,
        "score": 0.5404635071754456,
        "score_kind": "cosine"
      }
    ]
  }
}
````

### A43 / bm25

````json
{
  "eval_id": "A43",
  "strategy": "bm25",
  "bucket": "A_policy",
  "difficulty": "policy",
  "category": null,
  "should_refuse": false,
  "refused": false,
  "status": "completed",
  "stage": "complete",
  "query": "少发漏发导致的退换货,运费由谁承担",
  "query_plan": {
    "standard": "少发漏发导致的退换货,运费由谁承担",
    "expansions": []
  },
  "mapped_groups": [
    {
      "group_id": "g1",
      "alternatives": [
        [
          1869
        ]
      ]
    }
  ],
  "candidate_ids": [
    1869,
    1868,
    1837,
    1871,
    1831,
    1867,
    1842,
    1840,
    1880,
    1851,
    1877,
    1870,
    1847,
    1872,
    1873,
    1839,
    1841,
    1852,
    1843,
    1874,
    1849,
    1865,
    1850,
    1835,
    1846,
    1848,
    1876,
    1879
  ],
  "final_ids": [
    1869,
    1868,
    1837,
    1871,
    1831,
    1867,
    1842,
    1840,
    1880,
    1851
  ],
  "prompt_citations": [
    {
      "n": 1,
      "chunk_id": "1869",
      "section_path": "退货退款政策/退换货运费承担",
      "question": "退换货运费承担",
      "answer": "无理由退货的退回运费由买家承担;因商品质量问题、发错货、少发漏发导致的退换货,运费由平台承担。运费承担以平台售后规则最终判定为准。"
    },
    {
      "n": 3,
      "chunk_id": "1837",
      "section_path": "售后手册/会员专属售后权益",
      "question": "会员专属售后权益",
      "answer": "金卡会员享优先客服接入与上门取件退换货;银卡会员享退换货运费权益 1 次/月。具体权益以会员中心页面标注为准。"
    },
    {
      "n": 5,
      "chunk_id": "1831",
      "section_path": "售后手册/常见问题处理时限",
      "question": "常见问题处理时限",
      "answer": "| 问题类型 | 首次响应 | 处理时限 |\n| --- | --- | --- |\n| 退款 | 2 小时 | 3 个工作日 |\n| 换货 | 2 小时 | 5 个工作日 |\n| 维修 | 4 小时 | 7 个工作日 |\n| 投诉 | 1 小时 | 3 个工作日 |\n| 发票 | 4 小时 | 3 个工作日 |\n| 物流异常 | 2 小时 | 5 个工作日 |\n| 商品咨询 | 1 小时 | 当日 |\n| 价格保护 | 2 小时 | 3 个工作日 |\n| 账户问题 | 2 小时 | 3 个工作日 |\n| 退换货运费 | 2 小时 | 3 个工作日 |\n| 缺货补发 | 2 小时 | 5 个工作日 |\n| 其他 | 4 小时 | 7 个工作日 |"
    },
    {
      "n": 7,
      "chunk_id": "1842",
      "section_path": "商品与购物 FAQ/运费怎么算",
      "question": "运费怎么算",
      "answer": "单笔订单满 99 元包邮,未满收取 10 元运费,偏远地区运费另计。邮费即运费,按此规则收取。"
    },
    {
      "n": 9,
      "chunk_id": "1880",
      "section_path": "猫窝清洗说明/猫窝是否可以机洗",
      "question": "猫窝是否可以机洗",
      "answer": "普通布艺猫窝清洗前拆掉内部垫芯，外套放入洗衣袋，使用轻柔模式冷水洗，自然晾干。不可直接将整只猫窝连垫芯一起机洗，商品另有清洗标签时优先遵循标签。\n\n带加热模块的猫窝不可机洗，应先断电，并按说明书局部擦洗；不得将加热模块、电源或线路浸水。未按清洗说明操作导致的损坏不直接认定为商品质量问题，需要客服核验。\n\n退货仍需符合商品完好、不影响二次销售等适用条件。售后手册中的电子类商品 12 个月保修不能直接套用到普通布艺猫窝；本清洗说明未给出布艺猫窝的独立保修期限。"
    },
    {
      "n": 10,
      "chunk_id": "1851",
      "section_path": "商品与购物 FAQ/会员运费权益",
      "question": "会员运费权益",
      "answer": "金卡会员每月享 3 次免运费权益,银卡会员享 1 次;权益不与偏远地区附加运费冲抵,当月未用完不结转。"
    },
    {
      "n": 8,
      "chunk_id": "1840",
      "section_path": "商品与购物 FAQ/换货流程怎么走",
      "question": "换货流程怎么走",
      "answer": "收到商品 7 天内可申请换货,联系客服登记后将商品寄回,平台核验无误后补发新品。"
    },
    {
      "n": 6,
      "chunk_id": "1867",
      "section_path": "退货退款政策/换货政策/换货条件",
      "question": "换货条件",
      "answer": "收到商品 7 天内,商品完好且配件齐全的,可申请一次同款换货;不同型号或颜色需先退货再重新下单。"
    },
    {
      "n": 4,
      "chunk_id": "1871",
      "section_path": "退货退款政策/运输破损处理",
      "question": "运输破损处理",
      "answer": "商品运输途中破损的,请在签收后 48 小时内联系客服并提供开箱视频与照片,核实后可免费补发或退款,相关运费由平台承担。"
    },
    {
      "n": 2,
      "chunk_id": "1868",
      "section_path": "退货退款政策/换货政策/换货运费",
      "question": "换货运费",
      "answer": "非质量问题的换货,往返运费由买家承担;因质量问题或发错货的换货,往返运费由平台承担。"
    }
  ],
  "decision": {
    "useful": true,
    "reason": "少发漏发运费由平台承担有明确证据",
    "response_kind": "knowledge",
    "source": null
  },
  "answer": "您好！根据平台规则，因商品质量问题、发错货、少发漏发导致的退换货，运费由平台承担；无理由退货的退回运费则由买家承担，最终以平台售后规则判定为准 [1]。\n\n如您遇到少发漏发情况，请提供订单号，我可以帮您进一步核实处理。",
  "point_verdicts": [
    {
      "point_id": "p1",
      "covered": true,
      "reason": "回答明确指出少发漏发导致的退换货运费由平台承担，并说明以平台售后规则最终判定为准，覆盖要点及条件"
    }
  ],
  "claim_verdicts": [
    {
      "claim": "因商品质量问题、发错货、少发漏发导致的退换货，运费由平台承担",
      "supported": true,
      "reason": "证据[1]明确说明因质量问题、发错货、少发漏发导致的退换货运费由平台承担"
    },
    {
      "claim": "无理由退货的退回运费由买家承担",
      "supported": true,
      "reason": "证据[1]明确说明无理由退货的退回运费由买家承担"
    },
    {
      "claim": "运费承担以平台售后规则最终判定为准",
      "supported": true,
      "reason": "证据[1]明确说明运费承担以平台售后规则最终判定为准"
    }
  ],
  "metrics": {
    "recall_at_5": 1.0,
    "recall_at_10": 1.0,
    "mrr_at_10": 1.0,
    "all_groups_hit_at_5": 1.0,
    "all_groups_hit_at_10": 1.0,
    "candidate_group_coverage": 1.0,
    "prompt_group_coverage": 1.0,
    "answer_point_coverage": 1.0,
    "faithfulness": 1.0,
    "absent_refusal_rate": null,
    "answerable_false_refusal_rate": 0.0
  },
  "error": null,
  "elapsed_ms": 10233.201100258157,
  "judge_snapshot": {
    "prompt_version": "joint-generation-v2.1",
    "finish_reason": "stop"
  },
  "audit": {
    "audit_version": 1,
    "source_map_id": "d2dd350d860b8141e52306cbbcafb22f97d091194eb1cdc839a528c2990715eb",
    "gold_groups": [
      {
        "group_id": "g1",
        "alternatives": [
          [
            "returns-policy.md:005:4d4b2ea9115f9f9c717e0b83cded75c9048bc1b04a4621131131a6e1d023f11c"
          ]
        ]
      }
    ],
    "answer_points": [
      {
        "point_id": "p1",
        "text": "少发漏发导致的退换货运费由平台承担，以售后规则最终判定为准",
        "condition": "运费按退换货原因与平台最终判定区分",
        "aliases": []
      }
    ],
    "candidate_ranking": [
      {
        "chunk_id": 1869,
        "score": 33.115447998046875,
        "score_kind": "bm25"
      },
      {
        "chunk_id": 1868,
        "score": 15.512645721435547,
        "score_kind": "bm25"
      },
      {
        "chunk_id": 1837,
        "score": 12.489039421081543,
        "score_kind": "bm25"
      },
      {
        "chunk_id": 1871,
        "score": 8.663971900939941,
        "score_kind": "bm25"
      },
      {
        "chunk_id": 1831,
        "score": 7.032027721405029,
        "score_kind": "bm25"
      },
      {
        "chunk_id": 1867,
        "score": 4.239816188812256,
        "score_kind": "bm25"
      },
      {
        "chunk_id": 1842,
        "score": 3.048265218734741,
        "score_kind": "bm25"
      },
      {
        "chunk_id": 1840,
        "score": 2.9758758544921875,
        "score_kind": "bm25"
      },
      {
        "chunk_id": 1880,
        "score": 2.8859429359436035,
        "score_kind": "bm25"
      },
      {
        "chunk_id": 1851,
        "score": 2.8167614936828613,
        "score_kind": "bm25"
      },
      {
        "chunk_id": 1877,
        "score": 2.4655652046203613,
        "score_kind": "bm25"
      },
      {
        "chunk_id": 1870,
        "score": 2.101652145385742,
        "score_kind": "bm25"
      },
      {
        "chunk_id": 1847,
        "score": 1.8113679885864258,
        "score_kind": "bm25"
      },
      {
        "chunk_id": 1872,
        "score": 1.4414697885513306,
        "score_kind": "bm25"
      },
      {
        "chunk_id": 1873,
        "score": 1.2937390804290771,
        "score_kind": "bm25"
      },
      {
        "chunk_id": 1839,
        "score": 1.0660427808761597,
        "score_kind": "bm25"
      },
      {
        "chunk_id": 1841,
        "score": 1.0558345317840576,
        "score_kind": "bm25"
      },
      {
        "chunk_id": 1852,
        "score": 1.0359933376312256,
        "score_kind": "bm25"
      },
      {
        "chunk_id": 1843,
        "score": 1.0168840885162354,
        "score_kind": "bm25"
      },
      {
        "chunk_id": 1874,
        "score": 1.0009245872497559,
        "score_kind": "bm25"
      },
      {
        "chunk_id": 1849,
        "score": 0.998467206954956,
        "score_kind": "bm25"
      },
      {
        "chunk_id": 1865,
        "score": 0.9895066618919373,
        "score_kind": "bm25"
      },
      {
        "chunk_id": 1850,
        "score": 0.9807054996490479,
        "score_kind": "bm25"
      },
      {
        "chunk_id": 1835,
        "score": 0.9720594882965088,
        "score_kind": "bm25"
      },
      {
        "chunk_id": 1846,
        "score": 0.9155580401420593,
        "score_kind": "bm25"
      },
      {
        "chunk_id": 1848,
        "score": 0.9155580401420593,
        "score_kind": "bm25"
      },
      {
        "chunk_id": 1876,
        "score": 0.8389298319816589,
        "score_kind": "bm25"
      },
      {
        "chunk_id": 1879,
        "score": 0.7139831781387329,
        "score_kind": "bm25"
      }
    ],
    "final_ranking": [
      {
        "chunk_id": 1869,
        "score": 33.115447998046875,
        "score_kind": "bm25"
      },
      {
        "chunk_id": 1868,
        "score": 15.512645721435547,
        "score_kind": "bm25"
      },
      {
        "chunk_id": 1837,
        "score": 12.489039421081543,
        "score_kind": "bm25"
      },
      {
        "chunk_id": 1871,
        "score": 8.663971900939941,
        "score_kind": "bm25"
      },
      {
        "chunk_id": 1831,
        "score": 7.032027721405029,
        "score_kind": "bm25"
      },
      {
        "chunk_id": 1867,
        "score": 4.239816188812256,
        "score_kind": "bm25"
      },
      {
        "chunk_id": 1842,
        "score": 3.048265218734741,
        "score_kind": "bm25"
      },
      {
        "chunk_id": 1840,
        "score": 2.9758758544921875,
        "score_kind": "bm25"
      },
      {
        "chunk_id": 1880,
        "score": 2.8859429359436035,
        "score_kind": "bm25"
      },
      {
        "chunk_id": 1851,
        "score": 2.8167614936828613,
        "score_kind": "bm25"
      }
    ]
  }
}
````

### A43 / hybrid

````json
{
  "eval_id": "A43",
  "strategy": "hybrid",
  "bucket": "A_policy",
  "difficulty": "policy",
  "category": null,
  "should_refuse": false,
  "refused": false,
  "status": "completed",
  "stage": "complete",
  "query": "少发漏发导致的退换货,运费由谁承担",
  "query_plan": {
    "standard": "少发漏发导致的退换货,运费由谁承担",
    "expansions": []
  },
  "mapped_groups": [
    {
      "group_id": "g1",
      "alternatives": [
        [
          1869
        ]
      ]
    }
  ],
  "candidate_ids": [
    1869,
    1868,
    1871,
    1837,
    1842,
    1840,
    1867,
    1831,
    1847,
    1851,
    1870,
    1873,
    1877,
    1849,
    1865,
    1839,
    1872,
    1841,
    1848,
    1880,
    1843,
    1850,
    1876,
    1874,
    1879,
    1846,
    1852,
    1835,
    1836,
    1866,
    1838,
    1832,
    1844,
    1834,
    1878,
    1845,
    1857,
    1875,
    1833,
    1855,
    1853,
    1858,
    1856,
    1854,
    1862,
    1863,
    1860,
    1861,
    1864,
    1859
  ],
  "final_ids": [
    1869,
    1868,
    1871,
    1837,
    1842,
    1840,
    1867,
    1831,
    1847,
    1851
  ],
  "prompt_citations": [
    {
      "n": 1,
      "chunk_id": "1869",
      "section_path": "退货退款政策/退换货运费承担",
      "question": "退换货运费承担",
      "answer": "无理由退货的退回运费由买家承担;因商品质量问题、发错货、少发漏发导致的退换货,运费由平台承担。运费承担以平台售后规则最终判定为准。"
    },
    {
      "n": 3,
      "chunk_id": "1871",
      "section_path": "退货退款政策/运输破损处理",
      "question": "运输破损处理",
      "answer": "商品运输途中破损的,请在签收后 48 小时内联系客服并提供开箱视频与照片,核实后可免费补发或退款,相关运费由平台承担。"
    },
    {
      "n": 5,
      "chunk_id": "1842",
      "section_path": "商品与购物 FAQ/运费怎么算",
      "question": "运费怎么算",
      "answer": "单笔订单满 99 元包邮,未满收取 10 元运费,偏远地区运费另计。邮费即运费,按此规则收取。"
    },
    {
      "n": 7,
      "chunk_id": "1867",
      "section_path": "退货退款政策/换货政策/换货条件",
      "question": "换货条件",
      "answer": "收到商品 7 天内,商品完好且配件齐全的,可申请一次同款换货;不同型号或颜色需先退货再重新下单。"
    },
    {
      "n": 9,
      "chunk_id": "1847",
      "section_path": "商品与购物 FAQ/配送范围与偏远地区",
      "question": "配送范围与偏远地区",
      "answer": "全国大部分地区支持配送,新疆、西藏、内蒙古等偏远地区运费另计且时效顺延;港澳台及海外暂不支持自营配送。"
    },
    {
      "n": 10,
      "chunk_id": "1851",
      "section_path": "商品与购物 FAQ/会员运费权益",
      "question": "会员运费权益",
      "answer": "金卡会员每月享 3 次免运费权益,银卡会员享 1 次;权益不与偏远地区附加运费冲抵,当月未用完不结转。"
    },
    {
      "n": 8,
      "chunk_id": "1831",
      "section_path": "售后手册/常见问题处理时限",
      "question": "常见问题处理时限",
      "answer": "| 问题类型 | 首次响应 | 处理时限 |\n| --- | --- | --- |\n| 退款 | 2 小时 | 3 个工作日 |\n| 换货 | 2 小时 | 5 个工作日 |\n| 维修 | 4 小时 | 7 个工作日 |\n| 投诉 | 1 小时 | 3 个工作日 |\n| 发票 | 4 小时 | 3 个工作日 |\n| 物流异常 | 2 小时 | 5 个工作日 |\n| 商品咨询 | 1 小时 | 当日 |\n| 价格保护 | 2 小时 | 3 个工作日 |\n| 账户问题 | 2 小时 | 3 个工作日 |\n| 退换货运费 | 2 小时 | 3 个工作日 |\n| 缺货补发 | 2 小时 | 5 个工作日 |\n| 其他 | 4 小时 | 7 个工作日 |"
    },
    {
      "n": 6,
      "chunk_id": "1840",
      "section_path": "商品与购物 FAQ/换货流程怎么走",
      "question": "换货流程怎么走",
      "answer": "收到商品 7 天内可申请换货,联系客服登记后将商品寄回,平台核验无误后补发新品。"
    },
    {
      "n": 4,
      "chunk_id": "1837",
      "section_path": "售后手册/会员专属售后权益",
      "question": "会员专属售后权益",
      "answer": "金卡会员享优先客服接入与上门取件退换货;银卡会员享退换货运费权益 1 次/月。具体权益以会员中心页面标注为准。"
    },
    {
      "n": 2,
      "chunk_id": "1868",
      "section_path": "退货退款政策/换货政策/换货运费",
      "question": "换货运费",
      "answer": "非质量问题的换货,往返运费由买家承担;因质量问题或发错货的换货,往返运费由平台承担。"
    }
  ],
  "decision": {
    "useful": true,
    "reason": "证据明确：少发漏发退换货运费由平台承担",
    "response_kind": "knowledge",
    "source": null
  },
  "answer": "您好！因**少发漏发**导致的退换货，运费由**平台承担**[1]；如涉及换货，因质量问题或发错货的换货往返运费也由平台承担[2]。最终运费承担以平台售后规则判定为准[1]。\n\n如需申请，欢迎提供订单号，我可以为您进一步协助~",
  "point_verdicts": [
    {
      "point_id": "p1",
      "covered": true,
      "reason": "回答明确指出少发漏发退换货运费由平台承担，并以平台售后规则最终判定为准，覆盖条件中按原因区分及最终判定要求"
    }
  ],
  "claim_verdicts": [
    {
      "claim": "因少发漏发导致的退换货运费由平台承担",
      "supported": true,
      "reason": "证据1明确说明因少发漏发导致的退换货运费由平台承担"
    },
    {
      "claim": "因质量问题或发错货的换货往返运费由平台承担",
      "supported": true,
      "reason": "证据2明确说明因质量问题或发错货的换货往返运费由平台承担"
    },
    {
      "claim": "最终运费承担以平台售后规则判定为准",
      "supported": true,
      "reason": "证据1明确说明运费承担以平台售后规则最终判定为准"
    }
  ],
  "metrics": {
    "recall_at_5": 1.0,
    "recall_at_10": 1.0,
    "mrr_at_10": 1.0,
    "all_groups_hit_at_5": 1.0,
    "all_groups_hit_at_10": 1.0,
    "candidate_group_coverage": 1.0,
    "prompt_group_coverage": 1.0,
    "answer_point_coverage": 1.0,
    "faithfulness": 1.0,
    "absent_refusal_rate": null,
    "answerable_false_refusal_rate": 0.0
  },
  "error": null,
  "elapsed_ms": 9003.043600125238,
  "judge_snapshot": {
    "prompt_version": "joint-generation-v2.1",
    "finish_reason": "stop"
  },
  "audit": {
    "audit_version": 1,
    "source_map_id": "d2dd350d860b8141e52306cbbcafb22f97d091194eb1cdc839a528c2990715eb",
    "gold_groups": [
      {
        "group_id": "g1",
        "alternatives": [
          [
            "returns-policy.md:005:4d4b2ea9115f9f9c717e0b83cded75c9048bc1b04a4621131131a6e1d023f11c"
          ]
        ]
      }
    ],
    "answer_points": [
      {
        "point_id": "p1",
        "text": "少发漏发导致的退换货运费由平台承担，以售后规则最终判定为准",
        "condition": "运费按退换货原因与平台最终判定区分",
        "aliases": []
      }
    ],
    "candidate_ranking": [
      {
        "chunk_id": 1869,
        "score": 0.032786883413791656,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1868,
        "score": 0.032258063554763794,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1871,
        "score": 0.0314980149269104,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1837,
        "score": 0.03079839050769806,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1842,
        "score": 0.03055037185549736,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1840,
        "score": 0.03009049780666828,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1867,
        "score": 0.02964426949620247,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1831,
        "score": 0.02854251116514206,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1847,
        "score": 0.028404511511325836,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1851,
        "score": 0.028370220214128494,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1870,
        "score": 0.02817460335791111,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1873,
        "score": 0.02684684842824936,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1877,
        "score": 0.026742734014987946,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1849,
        "score": 0.026234567165374756,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1865,
        "score": 0.02589375153183937,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1839,
        "score": 0.02565789595246315,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1872,
        "score": 0.02527821995317936,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1841,
        "score": 0.025035206228494644,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1848,
        "score": 0.024448420852422714,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1880,
        "score": 0.024201491847634315,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1843,
        "score": 0.02402186393737793,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1850,
        "score": 0.02395295351743698,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1876,
        "score": 0.023689374327659607,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1874,
        "score": 0.02336956560611725,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1879,
        "score": 0.022991543635725975,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1846,
        "score": 0.022753717377781868,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1852,
        "score": 0.022344322875142097,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1835,
        "score": 0.022214040160179138,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1836,
        "score": 0.01515151560306549,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1866,
        "score": 0.013333333656191826,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1838,
        "score": 0.012987012974917889,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1832,
        "score": 0.012345679104328156,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1844,
        "score": 0.01149425283074379,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1834,
        "score": 0.01123595517128706,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1878,
        "score": 0.011111111380159855,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1845,
        "score": 0.01075268816202879,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1857,
        "score": 0.010638297535479069,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1875,
        "score": 0.010526316240429878,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1833,
        "score": 0.010416666977107525,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1855,
        "score": 0.010204081423580647,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1853,
        "score": 0.010101010091602802,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1858,
        "score": 0.009999999776482582,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1856,
        "score": 0.009900989942252636,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1854,
        "score": 0.009803921915590763,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1862,
        "score": 0.009615384973585606,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1863,
        "score": 0.009433962404727936,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1860,
        "score": 0.009345794096589088,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1861,
        "score": 0.009259259328246117,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1864,
        "score": 0.00917431153357029,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1859,
        "score": 0.00909090880304575,
        "score_kind": "rrf"
      }
    ],
    "final_ranking": [
      {
        "chunk_id": 1869,
        "score": 0.032786883413791656,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1868,
        "score": 0.032258063554763794,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1871,
        "score": 0.0314980149269104,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1837,
        "score": 0.03079839050769806,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1842,
        "score": 0.03055037185549736,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1840,
        "score": 0.03009049780666828,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1867,
        "score": 0.02964426949620247,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1831,
        "score": 0.02854251116514206,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1847,
        "score": 0.028404511511325836,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1851,
        "score": 0.028370220214128494,
        "score_kind": "rrf"
      }
    ]
  }
}
````

### A43 / hybrid_rerank

````json
{
  "eval_id": "A43",
  "strategy": "hybrid_rerank",
  "bucket": "A_policy",
  "difficulty": "policy",
  "category": null,
  "should_refuse": false,
  "refused": false,
  "status": "completed",
  "stage": "complete",
  "query": "少发漏发导致的退换货,运费由谁承担",
  "query_plan": {
    "standard": "少发漏发导致的退换货,运费由谁承担",
    "expansions": []
  },
  "mapped_groups": [
    {
      "group_id": "g1",
      "alternatives": [
        [
          1869
        ]
      ]
    }
  ],
  "candidate_ids": [
    1869,
    1868,
    1871,
    1837,
    1842,
    1840,
    1867,
    1831,
    1847,
    1851,
    1870,
    1873,
    1877,
    1849,
    1865,
    1839,
    1872,
    1841,
    1848,
    1880,
    1843,
    1850,
    1876,
    1874,
    1879,
    1846,
    1852,
    1835,
    1836,
    1866,
    1838,
    1832,
    1844,
    1834,
    1878,
    1845,
    1857,
    1875,
    1833,
    1855,
    1853,
    1858,
    1856,
    1854,
    1862,
    1863,
    1860,
    1861,
    1864,
    1859
  ],
  "final_ids": [
    1869,
    1868,
    1871,
    1837,
    1842,
    1873,
    1878,
    1870,
    1874,
    1847
  ],
  "prompt_citations": [
    {
      "n": 1,
      "chunk_id": "1869",
      "section_path": "退货退款政策/退换货运费承担",
      "question": "退换货运费承担",
      "answer": "无理由退货的退回运费由买家承担;因商品质量问题、发错货、少发漏发导致的退换货,运费由平台承担。运费承担以平台售后规则最终判定为准。"
    },
    {
      "n": 3,
      "chunk_id": "1871",
      "section_path": "退货退款政策/运输破损处理",
      "question": "运输破损处理",
      "answer": "商品运输途中破损的,请在签收后 48 小时内联系客服并提供开箱视频与照片,核实后可免费补发或退款,相关运费由平台承担。"
    },
    {
      "n": 5,
      "chunk_id": "1842",
      "section_path": "商品与购物 FAQ/运费怎么算",
      "question": "运费怎么算",
      "answer": "单笔订单满 99 元包邮,未满收取 10 元运费,偏远地区运费另计。邮费即运费,按此规则收取。"
    },
    {
      "n": 7,
      "chunk_id": "1878",
      "section_path": "开票细则/可开票类型",
      "question": "可开票类型",
      "answer": "本演示店提供电子普通发票、电子专用发票和纸质专用发票。电子普通发票可按订单申请；电子专票需要企业账户，申请前准备发票抬头及有效纳税人识别号，按申请页面提交资料。\n\n纸质专票仅企业账户可申请，申请时需提供企业开票资料、收件人和邮寄地址，快递费到付。资料审核通过后按开票流程寄出，不承诺快递送达日期。"
    },
    {
      "n": 9,
      "chunk_id": "1874",
      "section_path": "会员权益/会员等级",
      "question": "会员等级",
      "answer": "会员分为普通、银卡和金卡三档，按有效累计消费金额自动升级，不按年度消费金额计算。累计消费未满 1000 元为普通会员，满 1000 元起为银卡，满 5000 元起为金卡。\n\n有效累计消费指已完成订单的商品实际支付金额，不含配送费；退货退款部分从有效累计消费中扣除。退款后根据更新的累计消费重新计算等级，未达到原门槛时可能降级。等级与适用权益在会员中心展示。\n\n银卡在参与会员折扣的商品上享 95 折，金卡享 9 折。折扣适用商品和活动范围以结算页面标注为准。会员折扣、优惠券与满减是否叠加也以当次活动页面为准，不能一概承诺全部优惠同时生效。"
    },
    {
      "n": 10,
      "chunk_id": "1847",
      "section_path": "商品与购物 FAQ/配送范围与偏远地区",
      "question": "配送范围与偏远地区",
      "answer": "全国大部分地区支持配送,新疆、西藏、内蒙古等偏远地区运费另计且时效顺延;港澳台及海外暂不支持自营配送。"
    },
    {
      "n": 8,
      "chunk_id": "1870",
      "section_path": "退货退款政策/质量问题与保修",
      "question": "质量问题与保修",
      "answer": "电子类商品自签收起保修 12 个月,保修期内非人为损坏可申请免费维修或换货;人为损坏、超保商品维修可能收取工本费。"
    },
    {
      "n": 6,
      "chunk_id": "1873",
      "section_path": "退货退款政策/预售与定金",
      "question": "预售与定金",
      "answer": "预售商品以详情页标注的时间发货;定金支付后不支持无理由退定金,尾款未按时支付的,定金按活动规则处理。"
    },
    {
      "n": 4,
      "chunk_id": "1837",
      "section_path": "售后手册/会员专属售后权益",
      "question": "会员专属售后权益",
      "answer": "金卡会员享优先客服接入与上门取件退换货;银卡会员享退换货运费权益 1 次/月。具体权益以会员中心页面标注为准。"
    },
    {
      "n": 2,
      "chunk_id": "1868",
      "section_path": "退货退款政策/换货政策/换货运费",
      "question": "换货运费",
      "answer": "非质量问题的换货,往返运费由买家承担;因质量问题或发错货的换货,往返运费由平台承担。"
    }
  ],
  "decision": {
    "useful": true,
    "reason": "证据明确少发漏发运费由平台承担",
    "response_kind": "knowledge",
    "source": null
  },
  "answer": "您好！根据商家政策：因商品质量问题、发错货、**少发漏发**导致的退换货，运费由**平台承担**；无理由退货的退回运费则由买家承担，最终以平台售后规则判定为准 [1]。换货方面，因质量问题或发错货的换货，往返运费也由平台承担 [2]。\n\n请问还有其他需要帮助的吗？",
  "point_verdicts": [
    {
      "point_id": "p1",
      "covered": true,
      "reason": "回答明确少发漏发导致的退换货运费由平台承担，并说明以平台售后规则最终判定为准，覆盖条件"
    }
  ],
  "claim_verdicts": [
    {
      "claim": "因商品质量问题、发错货、少发漏发导致的退换货，运费由平台承担",
      "supported": true,
      "reason": "证据1明确说明该类退换货运费由平台承担"
    },
    {
      "claim": "无理由退货的退回运费由买家承担",
      "supported": true,
      "reason": "证据1明确说明无理由退货的退回运费由买家承担"
    },
    {
      "claim": "运费承担以平台售后规则最终判定为准",
      "supported": true,
      "reason": "证据1明确说明以平台售后规则最终判定为准"
    },
    {
      "claim": "因质量问题或发错货的换货，往返运费由平台承担",
      "supported": true,
      "reason": "证据2明确说明该情形换货往返运费由平台承担"
    }
  ],
  "metrics": {
    "recall_at_5": 1.0,
    "recall_at_10": 1.0,
    "mrr_at_10": 1.0,
    "all_groups_hit_at_5": 1.0,
    "all_groups_hit_at_10": 1.0,
    "candidate_group_coverage": 1.0,
    "prompt_group_coverage": 1.0,
    "answer_point_coverage": 1.0,
    "faithfulness": 1.0,
    "absent_refusal_rate": null,
    "answerable_false_refusal_rate": 0.0
  },
  "error": null,
  "elapsed_ms": 10703.775699948892,
  "judge_snapshot": {
    "prompt_version": "joint-generation-v2.1",
    "finish_reason": "stop"
  },
  "audit": {
    "audit_version": 1,
    "source_map_id": "d2dd350d860b8141e52306cbbcafb22f97d091194eb1cdc839a528c2990715eb",
    "gold_groups": [
      {
        "group_id": "g1",
        "alternatives": [
          [
            "returns-policy.md:005:4d4b2ea9115f9f9c717e0b83cded75c9048bc1b04a4621131131a6e1d023f11c"
          ]
        ]
      }
    ],
    "answer_points": [
      {
        "point_id": "p1",
        "text": "少发漏发导致的退换货运费由平台承担，以售后规则最终判定为准",
        "condition": "运费按退换货原因与平台最终判定区分",
        "aliases": []
      }
    ],
    "candidate_ranking": [
      {
        "chunk_id": 1869,
        "score": 0.032786883413791656,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1868,
        "score": 0.032258063554763794,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1871,
        "score": 0.0314980149269104,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1837,
        "score": 0.03079839050769806,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1842,
        "score": 0.03055037185549736,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1840,
        "score": 0.03009049780666828,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1867,
        "score": 0.02964426949620247,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1831,
        "score": 0.02854251116514206,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1847,
        "score": 0.028404511511325836,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1851,
        "score": 0.028370220214128494,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1870,
        "score": 0.02817460335791111,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1873,
        "score": 0.02684684842824936,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1877,
        "score": 0.026742734014987946,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1849,
        "score": 0.026234567165374756,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1865,
        "score": 0.02589375153183937,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1839,
        "score": 0.02565789595246315,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1872,
        "score": 0.02527821995317936,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1841,
        "score": 0.025035206228494644,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1848,
        "score": 0.024448420852422714,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1880,
        "score": 0.024201491847634315,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1843,
        "score": 0.02402186393737793,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1850,
        "score": 0.02395295351743698,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1876,
        "score": 0.023689374327659607,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1874,
        "score": 0.02336956560611725,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1879,
        "score": 0.022991543635725975,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1846,
        "score": 0.022753717377781868,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1852,
        "score": 0.022344322875142097,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1835,
        "score": 0.022214040160179138,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1836,
        "score": 0.01515151560306549,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1866,
        "score": 0.013333333656191826,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1838,
        "score": 0.012987012974917889,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1832,
        "score": 0.012345679104328156,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1844,
        "score": 0.01149425283074379,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1834,
        "score": 0.01123595517128706,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1878,
        "score": 0.011111111380159855,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1845,
        "score": 0.01075268816202879,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1857,
        "score": 0.010638297535479069,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1875,
        "score": 0.010526316240429878,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1833,
        "score": 0.010416666977107525,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1855,
        "score": 0.010204081423580647,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1853,
        "score": 0.010101010091602802,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1858,
        "score": 0.009999999776482582,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1856,
        "score": 0.009900989942252636,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1854,
        "score": 0.009803921915590763,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1862,
        "score": 0.009615384973585606,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1863,
        "score": 0.009433962404727936,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1860,
        "score": 0.009345794096589088,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1861,
        "score": 0.009259259328246117,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1864,
        "score": 0.00917431153357029,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1859,
        "score": 0.00909090880304575,
        "score_kind": "rrf"
      }
    ],
    "final_ranking": [
      {
        "chunk_id": 1869,
        "score": 0.9927054047584534,
        "score_kind": "rerank"
      },
      {
        "chunk_id": 1868,
        "score": 0.8051902651786804,
        "score_kind": "rerank"
      },
      {
        "chunk_id": 1871,
        "score": 0.2777271568775177,
        "score_kind": "rerank"
      },
      {
        "chunk_id": 1837,
        "score": 0.042139433324337006,
        "score_kind": "rerank"
      },
      {
        "chunk_id": 1842,
        "score": 0.03397957980632782,
        "score_kind": "rerank"
      },
      {
        "chunk_id": 1873,
        "score": 0.00973587017506361,
        "score_kind": "rerank"
      },
      {
        "chunk_id": 1878,
        "score": 0.008264950476586819,
        "score_kind": "rerank"
      },
      {
        "chunk_id": 1870,
        "score": 0.006317650433629751,
        "score_kind": "rerank"
      },
      {
        "chunk_id": 1874,
        "score": 0.00597203616052866,
        "score_kind": "rerank"
      },
      {
        "chunk_id": 1847,
        "score": 0.004723845049738884,
        "score_kind": "rerank"
      }
    ]
  }
}
````

### B3 / dense

````json
{
  "eval_id": "B3",
  "strategy": "dense",
  "bucket": "B_model",
  "difficulty": "model",
  "category": null,
  "should_refuse": false,
  "refused": false,
  "status": "completed",
  "stage": "complete",
  "query": "MH-LP50 和 Pro 版有什么区别",
  "query_plan": {
    "standard": "MH-LP50 和 Pro 版有什么区别",
    "expansions": []
  },
  "mapped_groups": [
    {
      "group_id": "g1",
      "alternatives": [
        [
          1854
        ]
      ]
    }
  ],
  "candidate_ids": [
    1854,
    1853,
    1858,
    1863,
    1862,
    1857,
    1855,
    1864,
    1861,
    1859,
    1856,
    1860,
    1877,
    1874,
    1845,
    1873,
    1852,
    1837,
    1870,
    1878,
    1832,
    1836,
    1831,
    1848,
    1844,
    1835,
    1867,
    1846,
    1833,
    1841,
    1850,
    1847,
    1851,
    1842,
    1865,
    1871,
    1866,
    1868,
    1834,
    1876,
    1875,
    1838,
    1840,
    1843,
    1879,
    1839,
    1880,
    1872,
    1869,
    1849
  ],
  "final_ids": [
    1854,
    1853,
    1858,
    1863,
    1862,
    1857,
    1855,
    1864,
    1861,
    1859
  ],
  "prompt_citations": [
    {
      "n": 1,
      "chunk_id": "1854",
      "section_path": "商品规格手册/智能猫砂盆 Lite(型号 MH-LP50)",
      "question": "智能猫砂盆 Lite(型号 MH-LP50)",
      "answer": "- 型号:MH-LP50\n- 适用猫咪体重:1.5kg 至 6kg\n- 猫砂容量:6L\n- 核心功能:自动感应清理、物理除臭盖板;不含 App 联网功能\n- 与 Pro 差异:Lite 无 App 远程监控与健康记录,价格更低,适合单猫家庭"
    },
    {
      "n": 3,
      "chunk_id": "1858",
      "section_path": "商品规格手册/自动饮水机 Pro 不锈钢(型号 MH-W60)",
      "question": "自动饮水机 Pro 不锈钢(型号 MH-W60)",
      "answer": "- 型号:MH-W60\n- 水箱容量:6L,304 不锈钢表面盘\n- 过滤:双滤芯并联,建议每 4 周更换一次滤芯\n- 核心功能:双泵冗余、无线水位提醒推送 App、缺水断电保护\n- 清洗:不锈钢面盘可高温消毒,建议每周清洗一次"
    },
    {
      "n": 5,
      "chunk_id": "1862",
      "section_path": "商品规格手册/自动喂食器 基础版(型号 MH-FD10)",
      "question": "自动喂食器 基础版(型号 MH-FD10)",
      "answer": "- 型号:MH-FD10\n- 粮桶容量:4L\n- 核心功能:定时定量投喂,每日最多 6 餐,语音呼唤进食\n- 供电:市电供电 + 4 节 5 号电池断电应急\n- 说明:基础版不含摄像头与 App 远程投喂"
    },
    {
      "n": 7,
      "chunk_id": "1855",
      "section_path": "商品规格手册/智能猫砂盆 Max(型号 MH-LP200)",
      "question": "智能猫砂盆 Max(型号 MH-LP200)",
      "answer": "- 型号:MH-LP200\n- 适用猫咪体重:2kg 至 12kg,适合大型猫与多猫家庭\n- 猫砂容量:12L,废砂盒容量约 10 天(单猫)\n- 核心功能:超大滚筒、双重称重防夹、活性炭除臭、App 多猫健康档案\n- 供电:220V 市电\n- 清理提示:多猫家庭建议每 3 至 5 天倾倒一次废砂盒"
    },
    {
      "n": 9,
      "chunk_id": "1861",
      "section_path": "商品规格手册/大号三档加热垫(型号 MH-HP20)",
      "question": "大号三档加热垫(型号 MH-HP20)",
      "answer": "- 型号:MH-HP20\n- 尺寸:60cm × 45cm\n- 温控:三档可调 30℃ / 38℃ / 45℃,内置过热保护与定时关机\n- 防护:防水防抓咬电线套管,表面绒布可拆洗\n- 适用:大型猫、多猫窝及冬季保暖"
    },
    {
      "n": 10,
      "chunk_id": "1859",
      "section_path": "商品规格手册/大型猫爬架(型号 MH-CT30)",
      "question": "大型猫爬架(型号 MH-CT30)",
      "answer": "- 型号:MH-CT30\n- 高度:1.6m,共四层带顶层吊床\n- 承重:单层最大 10kg\n- 材质:剑麻柱身、绒布平台\n- 安装:需自行组装,随附六角扳手与图解说明书"
    },
    {
      "n": 8,
      "chunk_id": "1864",
      "section_path": "商品规格手册/全景看护摄像头(型号 MH-CAM1)",
      "question": "全景看护摄像头(型号 MH-CAM1)",
      "answer": "- 型号:MH-CAM1\n- 画质:2K 分辨率,355° 水平旋转、90° 俯仰\n- 核心功能:移动侦测报警、夜视、双向语音、逗猫激光\n- 存储:支持最大 128G TF 卡或云存储\n- 供电:Type-C 供电,需连接 2.4G Wi-Fi"
    },
    {
      "n": 6,
      "chunk_id": "1857",
      "section_path": "商品规格手册/自动饮水机 Plus(型号 MH-W40)",
      "question": "自动饮水机 Plus(型号 MH-W40)",
      "answer": "- 型号:MH-W40\n- 水箱容量:4L\n- 过滤:五重过滤棉 + 椰壳活性炭,建议每 3 周更换一次滤芯\n- 核心功能:UV 紫外杀菌、静音变频水泵、缺水断电保护\n- 清洗:整机可拆分水洗,建议每周清洗一次"
    },
    {
      "n": 4,
      "chunk_id": "1863",
      "section_path": "商品规格手册/自动喂食器 摄像头版(型号 MH-FD30)",
      "question": "自动喂食器 摄像头版(型号 MH-FD30)",
      "answer": "- 型号:MH-FD30\n- 粮桶容量:6L\n- 核心功能:1080P 摄像头、双向语音、App 远程手动投喂与定时投喂\n- 供电:市电供电 + 内置应急电池\n- 说明:摄像头版支持视频回看,需连接 2.4G Wi-Fi"
    },
    {
      "n": 2,
      "chunk_id": "1853",
      "section_path": "商品规格手册/智能猫砂盆 Pro(型号 MH-LP100)",
      "question": "智能猫砂盆 Pro(型号 MH-LP100)",
      "answer": "- 型号:MH-LP100\n- 适用猫咪体重:1.5kg 至 8kg\n- 猫砂容量:9L,废砂盒容量约 7 天(单猫)\n- 核心功能:自动感应清理、活性炭除臭、App 远程监控与健康记录\n- 供电:220V 市电,断电后配置自动保存\n- 清理提示:废砂盒满时 App 推送提醒,建议每 5 至 7 天倾倒一次"
    }
  ],
  "decision": {
    "useful": true,
    "reason": "两条证据分别覆盖MH-LP50与Pro(MH-LP100)关键差异",
    "response_kind": "knowledge",
    "source": null
  },
  "answer": "您好！根据商品规格手册，两者的主要区别如下：\n\n**智能猫砂盆 Lite（MH-LP50）**[1]\n- 适用体重：1.5–6kg\n- 猫砂容量：6L\n- 功能：自动感应清理、物理除臭盖板，不含 App 联网\n\n**智能猫砂盆 Pro（MH-LP100）**[2]\n- 适用体重：1.5–8kg\n- 猫砂容量：9L，废砂盒约 7 天（单猫）\n- 功能：自动感应清理、活性炭除臭、App 远程监控与健康记录；废砂盒满时 App 推送提醒\n\n**核心差异**[1]：Lite 无 App 远程监控与健康记录，价格更低，适合单猫家庭。\n\n请问还有什么可以帮您的吗？",
  "point_verdicts": [
    {
      "point_id": "p1",
      "covered": true,
      "reason": "回答明确说明Lite(MH-LP50)不含App联网，并指出其无Pro的App远程监控与健康记录，条件范围保留"
    },
    {
      "point_id": "p2",
      "covered": true,
      "reason": "回答指出Lite价格更低，适合单猫家庭，且限定于Lite型号范围"
    }
  ],
  "claim_verdicts": [
    {
      "claim": "智能猫砂盆Lite(MH-LP50)适用体重1.5–6kg",
      "supported": true,
      "reason": "证据[1]明确列出适用猫咪体重1.5kg至6kg"
    },
    {
      "claim": "智能猫砂盆Lite(MH-LP50)猫砂容量6L",
      "supported": true,
      "reason": "证据[1]明确猫砂容量6L"
    },
    {
      "claim": "智能猫砂盆Lite(MH-LP50)具有自动感应清理与物理除臭盖板，不含App联网功能",
      "supported": true,
      "reason": "证据[1]核心功能原文完全支持"
    },
    {
      "claim": "智能猫砂盆Pro(MH-LP100)适用体重1.5–8kg",
      "supported": true,
      "reason": "证据[2]明确适用猫咪体重1.5kg至8kg"
    },
    {
      "claim": "智能猫砂盆Pro(MH-LP100)猫砂容量9L，废砂盒约7天（单猫）",
      "supported": true,
      "reason": "证据[2]明确猫砂容量9L，废砂盒容量约7天（单猫）"
    },
    {
      "claim": "智能猫砂盆Pro(MH-LP100)具有自动感应清理、活性炭除臭、App远程监控与健康记录功能",
      "supported": true,
      "reason": "证据[2]核心功能原文完全支持"
    },
    {
      "claim": "智能猫砂盆Pro废砂盒满时App推送提醒",
      "supported": true,
      "reason": "证据[2]清理提示明确废砂盒满时App推送提醒"
    },
    {
      "claim": "智能猫砂盆Lite(MH-LP50)无App远程监控与健康记录",
      "supported": true,
      "reason": "证据[1]与Pro差异部分明确此内容"
    },
    {
      "claim": "智能猫砂盆Lite(MH-LP50)价格更低",
      "supported": true,
      "reason": "证据[1]与Pro差异部分明确价格更低"
    },
    {
      "claim": "智能猫砂盆Lite(MH-LP50)适合单猫家庭",
      "supported": true,
      "reason": "证据[1]与Pro差异部分明确适合单猫家庭"
    }
  ],
  "metrics": {
    "recall_at_5": 1.0,
    "recall_at_10": 1.0,
    "mrr_at_10": 1.0,
    "all_groups_hit_at_5": 1.0,
    "all_groups_hit_at_10": 1.0,
    "candidate_group_coverage": 1.0,
    "prompt_group_coverage": 1.0,
    "answer_point_coverage": 1.0,
    "faithfulness": 1.0,
    "absent_refusal_rate": null,
    "answerable_false_refusal_rate": 0.0
  },
  "error": null,
  "elapsed_ms": 15202.17699999921,
  "judge_snapshot": {
    "prompt_version": "joint-generation-v2.1",
    "finish_reason": "stop"
  },
  "audit": {
    "audit_version": 1,
    "source_map_id": "d2dd350d860b8141e52306cbbcafb22f97d091194eb1cdc839a528c2990715eb",
    "gold_groups": [
      {
        "group_id": "g1",
        "alternatives": [
          [
            "product-specs.md:003:991276de42d44e06168ae7625057b9692cbc6be8149687ccf1a752da00b9f9f3"
          ]
        ]
      }
    ],
    "answer_points": [
      {
        "point_id": "p1",
        "text": "MH-LP50 不含 App 联网，少了 Pro 的远程监控与健康记录",
        "condition": "仅适用于智能猫砂盆 Lite(型号 MH-LP50)所述范围",
        "aliases": []
      },
      {
        "point_id": "p2",
        "text": "Lite 价格更低，适合单猫家庭",
        "condition": "仅适用于智能猫砂盆 Lite(型号 MH-LP50)所述范围",
        "aliases": []
      }
    ],
    "candidate_ranking": [
      {
        "chunk_id": 1854,
        "score": 0.541698694229126,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1853,
        "score": 0.4923565983772278,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1858,
        "score": 0.46168503165245056,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1863,
        "score": 0.4484211206436157,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1862,
        "score": 0.4474903643131256,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1857,
        "score": 0.4428067207336426,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1855,
        "score": 0.4374600052833557,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1864,
        "score": 0.4352439045906067,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1861,
        "score": 0.42067670822143555,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1859,
        "score": 0.41280311346054077,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1856,
        "score": 0.3966814875602722,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1860,
        "score": 0.3892975449562073,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1877,
        "score": 0.3642714023590088,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1874,
        "score": 0.3369862139225006,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1845,
        "score": 0.32716214656829834,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1873,
        "score": 0.3230932354927063,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1852,
        "score": 0.32005393505096436,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1837,
        "score": 0.31760919094085693,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1870,
        "score": 0.3175802230834961,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1878,
        "score": 0.30909478664398193,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1832,
        "score": 0.30891913175582886,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1836,
        "score": 0.29683154821395874,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1831,
        "score": 0.28847962617874146,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1848,
        "score": 0.2840690314769745,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1844,
        "score": 0.28290611505508423,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1835,
        "score": 0.28186357021331787,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1867,
        "score": 0.27828240394592285,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1846,
        "score": 0.2723686695098877,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1833,
        "score": 0.27169930934906006,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1841,
        "score": 0.26915642619132996,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1850,
        "score": 0.26893630623817444,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1847,
        "score": 0.25857019424438477,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1851,
        "score": 0.25743919610977173,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1842,
        "score": 0.2489739954471588,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1865,
        "score": 0.24817746877670288,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1871,
        "score": 0.2441561073064804,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1866,
        "score": 0.24131108820438385,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1868,
        "score": 0.23721975088119507,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1834,
        "score": 0.23596227169036865,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1876,
        "score": 0.23535418510437012,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1875,
        "score": 0.23405808210372925,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1838,
        "score": 0.23046962916851044,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1840,
        "score": 0.228411003947258,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1843,
        "score": 0.2269769310951233,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1879,
        "score": 0.22343984246253967,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1839,
        "score": 0.2231275886297226,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1880,
        "score": 0.22140991687774658,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1872,
        "score": 0.21503949165344238,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1869,
        "score": 0.19469712674617767,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1849,
        "score": 0.18200039863586426,
        "score_kind": "cosine"
      }
    ],
    "final_ranking": [
      {
        "chunk_id": 1854,
        "score": 0.541698694229126,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1853,
        "score": 0.4923565983772278,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1858,
        "score": 0.46168503165245056,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1863,
        "score": 0.4484211206436157,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1862,
        "score": 0.4474903643131256,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1857,
        "score": 0.4428067207336426,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1855,
        "score": 0.4374600052833557,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1864,
        "score": 0.4352439045906067,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1861,
        "score": 0.42067670822143555,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1859,
        "score": 0.41280311346054077,
        "score_kind": "cosine"
      }
    ]
  }
}
````

### B3 / bm25

````json
{
  "eval_id": "B3",
  "strategy": "bm25",
  "bucket": "B_model",
  "difficulty": "model",
  "category": null,
  "should_refuse": false,
  "refused": false,
  "status": "completed",
  "stage": "complete",
  "query": "MH-LP50 和 Pro 版有什么区别",
  "query_plan": {
    "standard": "MH-LP50 和 Pro 版有什么区别",
    "expansions": []
  },
  "mapped_groups": [
    {
      "group_id": "g1",
      "alternatives": [
        [
          1854
        ]
      ]
    }
  ],
  "candidate_ids": [
    1854,
    1838,
    1858,
    1853,
    1878,
    1846,
    1874,
    1859,
    1860,
    1856,
    1861,
    1857,
    1864,
    1862,
    1863,
    1855,
    1877
  ],
  "final_ids": [
    1854,
    1838,
    1858,
    1853,
    1878,
    1846,
    1874,
    1859,
    1860,
    1856
  ],
  "prompt_citations": [
    {
      "n": 1,
      "chunk_id": "1854",
      "section_path": "商品规格手册/智能猫砂盆 Lite(型号 MH-LP50)",
      "question": "智能猫砂盆 Lite(型号 MH-LP50)",
      "answer": "- 型号:MH-LP50\n- 适用猫咪体重:1.5kg 至 6kg\n- 猫砂容量:6L\n- 核心功能:自动感应清理、物理除臭盖板;不含 App 联网功能\n- 与 Pro 差异:Lite 无 App 远程监控与健康记录,价格更低,适合单猫家庭"
    },
    {
      "n": 3,
      "chunk_id": "1858",
      "section_path": "商品规格手册/自动饮水机 Pro 不锈钢(型号 MH-W60)",
      "question": "自动饮水机 Pro 不锈钢(型号 MH-W60)",
      "answer": "- 型号:MH-W60\n- 水箱容量:6L,304 不锈钢表面盘\n- 过滤:双滤芯并联,建议每 4 周更换一次滤芯\n- 核心功能:双泵冗余、无线水位提醒推送 App、缺水断电保护\n- 清洗:不锈钢面盘可高温消毒,建议每周清洗一次"
    },
    {
      "n": 5,
      "chunk_id": "1878",
      "section_path": "开票细则/可开票类型",
      "question": "可开票类型",
      "answer": "本演示店提供电子普通发票、电子专用发票和纸质专用发票。电子普通发票可按订单申请；电子专票需要企业账户，申请前准备发票抬头及有效纳税人识别号，按申请页面提交资料。\n\n纸质专票仅企业账户可申请，申请时需提供企业开票资料、收件人和邮寄地址，快递费到付。资料审核通过后按开票流程寄出，不承诺快递送达日期。"
    },
    {
      "n": 7,
      "chunk_id": "1874",
      "section_path": "会员权益/会员等级",
      "question": "会员等级",
      "answer": "会员分为普通、银卡和金卡三档，按有效累计消费金额自动升级，不按年度消费金额计算。累计消费未满 1000 元为普通会员，满 1000 元起为银卡，满 5000 元起为金卡。\n\n有效累计消费指已完成订单的商品实际支付金额，不含配送费；退货退款部分从有效累计消费中扣除。退款后根据更新的累计消费重新计算等级，未达到原门槛时可能降级。等级与适用权益在会员中心展示。\n\n银卡在参与会员折扣的商品上享 95 折，金卡享 9 折。折扣适用商品和活动范围以结算页面标注为准。会员折扣、优惠券与满减是否叠加也以当次活动页面为准，不能一概承诺全部优惠同时生效。"
    },
    {
      "n": 9,
      "chunk_id": "1860",
      "section_path": "商品规格手册/恒温加热垫(型号 MH-HP12)",
      "question": "恒温加热垫(型号 MH-HP12)",
      "answer": "- 型号:MH-HP12\n- 尺寸:40cm × 30cm\n- 温控:恒温 38℃,内置过热保护,连续通电不超过 12 小时为宜\n- 防护:防水防抓咬电线套管\n- 适用:幼猫、老年猫及冬季保暖"
    },
    {
      "n": 10,
      "chunk_id": "1856",
      "section_path": "商品规格手册/自动饮水机(型号 MH-W20)",
      "question": "自动饮水机(型号 MH-W20)",
      "answer": "- 型号:MH-W20\n- 水箱容量:2L\n- 过滤:三重过滤棉,建议每 2 周更换一次滤芯\n- 核心功能:静音水泵、缺水断电保护、水位窗口\n- 清洗:水泵可拆卸,建议每周清洗一次"
    },
    {
      "n": 8,
      "chunk_id": "1859",
      "section_path": "商品规格手册/大型猫爬架(型号 MH-CT30)",
      "question": "大型猫爬架(型号 MH-CT30)",
      "answer": "- 型号:MH-CT30\n- 高度:1.6m,共四层带顶层吊床\n- 承重:单层最大 10kg\n- 材质:剑麻柱身、绒布平台\n- 安装:需自行组装,随附六角扳手与图解说明书"
    },
    {
      "n": 6,
      "chunk_id": "1846",
      "section_path": "商品与购物 FAQ/优惠券和满减怎么用",
      "question": "优惠券和满减怎么用",
      "answer": "优惠券在结算页「使用优惠券」中勾选,满减活动自动叠加在商品页标示的门槛上;同一订单一般限用一张店铺券,活动细则以页面为准。"
    },
    {
      "n": 4,
      "chunk_id": "1853",
      "section_path": "商品规格手册/智能猫砂盆 Pro(型号 MH-LP100)",
      "question": "智能猫砂盆 Pro(型号 MH-LP100)",
      "answer": "- 型号:MH-LP100\n- 适用猫咪体重:1.5kg 至 8kg\n- 猫砂容量:9L,废砂盒容量约 7 天(单猫)\n- 核心功能:自动感应清理、活性炭除臭、App 远程监控与健康记录\n- 供电:220V 市电,断电后配置自动保存\n- 清理提示:废砂盒满时 App 推送提醒,建议每 5 至 7 天倾倒一次"
    },
    {
      "n": 2,
      "chunk_id": "1838",
      "section_path": "商品与购物 FAQ/退货政策是什么",
      "question": "退货政策是什么",
      "answer": "支持 7 天无理由退货,商品需保持完好、不影响二次销售,具体以平台售后规则为准。"
    }
  ],
  "decision": {
    "useful": true,
    "reason": "Lite与Pro规格证据均覆盖",
    "response_kind": "knowledge",
    "source": null
  },
  "answer": "您好！根据商品规格信息，MH-LP50（Lite 版）与 Pro 版（MH-LP100）的主要区别如下[1][4]：\n\n| 项目 | Lite（MH-LP50） | Pro（MH-LP100） |\n|---|---|---|\n| 适用猫咪体重 | 1.5–6kg | 1.5–8kg |\n| 猫砂容量 | 6L | 9L |\n| 除臭方式 | 物理除臭盖板 | 活性炭除臭 |\n| App 功能 | 无联网功能 | App 远程监控与健康记录 |\n| 废砂盒 | — | 约 7 天（单猫），App 推送提醒 |\n\n总结：Lite 无 App 远程监控与健康记录，价格更低，适合单猫家庭[1]。\n\n请问还有什么可以帮您的吗？",
  "point_verdicts": [
    {
      "point_id": "p1",
      "covered": true,
      "reason": "回答明确说明 Lite 无联网功能、无 App 远程监控与健康记录，并保留智能猫砂盆 Lite(MH-LP50)适用条件，覆盖完整"
    },
    {
      "point_id": "p2",
      "covered": true,
      "reason": "总结中说明 Lite 价格更低、适合单猫家庭，与要点一致"
    }
  ],
  "claim_verdicts": [
    {
      "claim": "MH-LP50 适用猫咪体重为 1.5–6kg",
      "supported": true,
      "reason": "证据[1]列明适用体重 1.5kg 至 6kg"
    },
    {
      "claim": "MH-LP100 适用猫咪体重为 1.5–8kg",
      "supported": true,
      "reason": "证据[4]列明适用体重 1.5kg 至 8kg"
    },
    {
      "claim": "MH-LP50 猫砂容量为 6L",
      "supported": true,
      "reason": "证据[1]写明猫砂容量 6L"
    },
    {
      "claim": "MH-LP100 猫砂容量为 9L",
      "supported": true,
      "reason": "证据[4]写明猫砂容量 9L"
    },
    {
      "claim": "MH-LP50 采用物理除臭盖板",
      "supported": true,
      "reason": "证据[1]核心功能含物理除臭盖板"
    },
    {
      "claim": "MH-LP100 采用活性炭除臭",
      "supported": true,
      "reason": "证据[4]核心功能含活性炭除臭"
    },
    {
      "claim": "MH-LP50 不含 App 联网功能",
      "supported": true,
      "reason": "证据[1]明确不含 App 联网功能"
    },
    {
      "claim": "MH-LP100 支持 App 远程监控与健康记录",
      "supported": true,
      "reason": "证据[4]核心功能含 App 远程监控与健康记录"
    },
    {
      "claim": "MH-LP100 废砂盒容量约 7 天（单猫）且满时 App 推送提醒",
      "supported": true,
      "reason": "证据[4]写明废砂盒约 7 天(单猫)，满时 App 推送提醒"
    },
    {
      "claim": "Lite 无 App 远程监控与健康记录，价格更低，适合单猫家庭",
      "supported": true,
      "reason": "证据[1]与 Pro 差异部分原句明确"
    }
  ],
  "metrics": {
    "recall_at_5": 1.0,
    "recall_at_10": 1.0,
    "mrr_at_10": 1.0,
    "all_groups_hit_at_5": 1.0,
    "all_groups_hit_at_10": 1.0,
    "candidate_group_coverage": 1.0,
    "prompt_group_coverage": 1.0,
    "answer_point_coverage": 1.0,
    "faithfulness": 1.0,
    "absent_refusal_rate": null,
    "answerable_false_refusal_rate": 0.0
  },
  "error": null,
  "elapsed_ms": 15360.466099809855,
  "judge_snapshot": {
    "prompt_version": "joint-generation-v2.1",
    "finish_reason": "stop"
  },
  "audit": {
    "audit_version": 1,
    "source_map_id": "d2dd350d860b8141e52306cbbcafb22f97d091194eb1cdc839a528c2990715eb",
    "gold_groups": [
      {
        "group_id": "g1",
        "alternatives": [
          [
            "product-specs.md:003:991276de42d44e06168ae7625057b9692cbc6be8149687ccf1a752da00b9f9f3"
          ]
        ]
      }
    ],
    "answer_points": [
      {
        "point_id": "p1",
        "text": "MH-LP50 不含 App 联网，少了 Pro 的远程监控与健康记录",
        "condition": "仅适用于智能猫砂盆 Lite(型号 MH-LP50)所述范围",
        "aliases": []
      },
      {
        "point_id": "p2",
        "text": "Lite 价格更低，适合单猫家庭",
        "condition": "仅适用于智能猫砂盆 Lite(型号 MH-LP50)所述范围",
        "aliases": []
      }
    ],
    "candidate_ranking": [
      {
        "chunk_id": 1854,
        "score": 9.145109176635742,
        "score_kind": "bm25"
      },
      {
        "chunk_id": 1838,
        "score": 4.2695698738098145,
        "score_kind": "bm25"
      },
      {
        "chunk_id": 1858,
        "score": 4.2516913414001465,
        "score_kind": "bm25"
      },
      {
        "chunk_id": 1853,
        "score": 3.9712343215942383,
        "score_kind": "bm25"
      },
      {
        "chunk_id": 1878,
        "score": 3.088531494140625,
        "score_kind": "bm25"
      },
      {
        "chunk_id": 1846,
        "score": 2.839679002761841,
        "score_kind": "bm25"
      },
      {
        "chunk_id": 1874,
        "score": 2.5103907585144043,
        "score_kind": "bm25"
      },
      {
        "chunk_id": 1859,
        "score": 1.9122194051742554,
        "score_kind": "bm25"
      },
      {
        "chunk_id": 1860,
        "score": 1.9122194051742554,
        "score_kind": "bm25"
      },
      {
        "chunk_id": 1856,
        "score": 1.880428671836853,
        "score_kind": "bm25"
      },
      {
        "chunk_id": 1861,
        "score": 1.8496778011322021,
        "score_kind": "bm25"
      },
      {
        "chunk_id": 1857,
        "score": 1.8102076053619385,
        "score_kind": "bm25"
      },
      {
        "chunk_id": 1864,
        "score": 1.7910975217819214,
        "score_kind": "bm25"
      },
      {
        "chunk_id": 1862,
        "score": 1.7816929817199707,
        "score_kind": "bm25"
      },
      {
        "chunk_id": 1863,
        "score": 1.7540630102157593,
        "score_kind": "bm25"
      },
      {
        "chunk_id": 1855,
        "score": 1.6596899032592773,
        "score_kind": "bm25"
      },
      {
        "chunk_id": 1877,
        "score": 1.2880016565322876,
        "score_kind": "bm25"
      }
    ],
    "final_ranking": [
      {
        "chunk_id": 1854,
        "score": 9.145109176635742,
        "score_kind": "bm25"
      },
      {
        "chunk_id": 1838,
        "score": 4.2695698738098145,
        "score_kind": "bm25"
      },
      {
        "chunk_id": 1858,
        "score": 4.2516913414001465,
        "score_kind": "bm25"
      },
      {
        "chunk_id": 1853,
        "score": 3.9712343215942383,
        "score_kind": "bm25"
      },
      {
        "chunk_id": 1878,
        "score": 3.088531494140625,
        "score_kind": "bm25"
      },
      {
        "chunk_id": 1846,
        "score": 2.839679002761841,
        "score_kind": "bm25"
      },
      {
        "chunk_id": 1874,
        "score": 2.5103907585144043,
        "score_kind": "bm25"
      },
      {
        "chunk_id": 1859,
        "score": 1.9122194051742554,
        "score_kind": "bm25"
      },
      {
        "chunk_id": 1860,
        "score": 1.9122194051742554,
        "score_kind": "bm25"
      },
      {
        "chunk_id": 1856,
        "score": 1.880428671836853,
        "score_kind": "bm25"
      }
    ]
  }
}
````

### B3 / hybrid

````json
{
  "eval_id": "B3",
  "strategy": "hybrid",
  "bucket": "B_model",
  "difficulty": "model",
  "category": null,
  "should_refuse": false,
  "refused": false,
  "status": "completed",
  "stage": "complete",
  "query": "MH-LP50 和 Pro 版有什么区别",
  "query_plan": {
    "standard": "MH-LP50 和 Pro 版有什么区别",
    "expansions": []
  },
  "mapped_groups": [
    {
      "group_id": "g1",
      "alternatives": [
        [
          1854
        ]
      ]
    }
  ],
  "candidate_ids": [
    1854,
    1853,
    1858,
    1857,
    1859,
    1863,
    1862,
    1861,
    1874,
    1864,
    1860,
    1856,
    1855,
    1878,
    1877,
    1846,
    1838,
    1845,
    1873,
    1852,
    1837,
    1870,
    1832,
    1836,
    1831,
    1848,
    1844,
    1835,
    1867,
    1833,
    1841,
    1850,
    1847,
    1851,
    1842,
    1865,
    1871,
    1866,
    1868,
    1834,
    1876,
    1875,
    1840,
    1843,
    1879,
    1839,
    1880,
    1872,
    1869,
    1849
  ],
  "final_ids": [
    1854,
    1853,
    1858,
    1857,
    1859,
    1863,
    1862,
    1861,
    1874,
    1864
  ],
  "prompt_citations": [
    {
      "n": 1,
      "chunk_id": "1854",
      "section_path": "商品规格手册/智能猫砂盆 Lite(型号 MH-LP50)",
      "question": "智能猫砂盆 Lite(型号 MH-LP50)",
      "answer": "- 型号:MH-LP50\n- 适用猫咪体重:1.5kg 至 6kg\n- 猫砂容量:6L\n- 核心功能:自动感应清理、物理除臭盖板;不含 App 联网功能\n- 与 Pro 差异:Lite 无 App 远程监控与健康记录,价格更低,适合单猫家庭"
    },
    {
      "n": 3,
      "chunk_id": "1858",
      "section_path": "商品规格手册/自动饮水机 Pro 不锈钢(型号 MH-W60)",
      "question": "自动饮水机 Pro 不锈钢(型号 MH-W60)",
      "answer": "- 型号:MH-W60\n- 水箱容量:6L,304 不锈钢表面盘\n- 过滤:双滤芯并联,建议每 4 周更换一次滤芯\n- 核心功能:双泵冗余、无线水位提醒推送 App、缺水断电保护\n- 清洗:不锈钢面盘可高温消毒,建议每周清洗一次"
    },
    {
      "n": 5,
      "chunk_id": "1859",
      "section_path": "商品规格手册/大型猫爬架(型号 MH-CT30)",
      "question": "大型猫爬架(型号 MH-CT30)",
      "answer": "- 型号:MH-CT30\n- 高度:1.6m,共四层带顶层吊床\n- 承重:单层最大 10kg\n- 材质:剑麻柱身、绒布平台\n- 安装:需自行组装,随附六角扳手与图解说明书"
    },
    {
      "n": 7,
      "chunk_id": "1862",
      "section_path": "商品规格手册/自动喂食器 基础版(型号 MH-FD10)",
      "question": "自动喂食器 基础版(型号 MH-FD10)",
      "answer": "- 型号:MH-FD10\n- 粮桶容量:4L\n- 核心功能:定时定量投喂,每日最多 6 餐,语音呼唤进食\n- 供电:市电供电 + 4 节 5 号电池断电应急\n- 说明:基础版不含摄像头与 App 远程投喂"
    },
    {
      "n": 9,
      "chunk_id": "1874",
      "section_path": "会员权益/会员等级",
      "question": "会员等级",
      "answer": "会员分为普通、银卡和金卡三档，按有效累计消费金额自动升级，不按年度消费金额计算。累计消费未满 1000 元为普通会员，满 1000 元起为银卡，满 5000 元起为金卡。\n\n有效累计消费指已完成订单的商品实际支付金额，不含配送费；退货退款部分从有效累计消费中扣除。退款后根据更新的累计消费重新计算等级，未达到原门槛时可能降级。等级与适用权益在会员中心展示。\n\n银卡在参与会员折扣的商品上享 95 折，金卡享 9 折。折扣适用商品和活动范围以结算页面标注为准。会员折扣、优惠券与满减是否叠加也以当次活动页面为准，不能一概承诺全部优惠同时生效。"
    },
    {
      "n": 10,
      "chunk_id": "1864",
      "section_path": "商品规格手册/全景看护摄像头(型号 MH-CAM1)",
      "question": "全景看护摄像头(型号 MH-CAM1)",
      "answer": "- 型号:MH-CAM1\n- 画质:2K 分辨率,355° 水平旋转、90° 俯仰\n- 核心功能:移动侦测报警、夜视、双向语音、逗猫激光\n- 存储:支持最大 128G TF 卡或云存储\n- 供电:Type-C 供电,需连接 2.4G Wi-Fi"
    },
    {
      "n": 8,
      "chunk_id": "1861",
      "section_path": "商品规格手册/大号三档加热垫(型号 MH-HP20)",
      "question": "大号三档加热垫(型号 MH-HP20)",
      "answer": "- 型号:MH-HP20\n- 尺寸:60cm × 45cm\n- 温控:三档可调 30℃ / 38℃ / 45℃,内置过热保护与定时关机\n- 防护:防水防抓咬电线套管,表面绒布可拆洗\n- 适用:大型猫、多猫窝及冬季保暖"
    },
    {
      "n": 6,
      "chunk_id": "1863",
      "section_path": "商品规格手册/自动喂食器 摄像头版(型号 MH-FD30)",
      "question": "自动喂食器 摄像头版(型号 MH-FD30)",
      "answer": "- 型号:MH-FD30\n- 粮桶容量:6L\n- 核心功能:1080P 摄像头、双向语音、App 远程手动投喂与定时投喂\n- 供电:市电供电 + 内置应急电池\n- 说明:摄像头版支持视频回看,需连接 2.4G Wi-Fi"
    },
    {
      "n": 4,
      "chunk_id": "1857",
      "section_path": "商品规格手册/自动饮水机 Plus(型号 MH-W40)",
      "question": "自动饮水机 Plus(型号 MH-W40)",
      "answer": "- 型号:MH-W40\n- 水箱容量:4L\n- 过滤:五重过滤棉 + 椰壳活性炭,建议每 3 周更换一次滤芯\n- 核心功能:UV 紫外杀菌、静音变频水泵、缺水断电保护\n- 清洗:整机可拆分水洗,建议每周清洗一次"
    },
    {
      "n": 2,
      "chunk_id": "1853",
      "section_path": "商品规格手册/智能猫砂盆 Pro(型号 MH-LP100)",
      "question": "智能猫砂盆 Pro(型号 MH-LP100)",
      "answer": "- 型号:MH-LP100\n- 适用猫咪体重:1.5kg 至 8kg\n- 猫砂容量:9L,废砂盒容量约 7 天(单猫)\n- 核心功能:自动感应清理、活性炭除臭、App 远程监控与健康记录\n- 供电:220V 市电,断电后配置自动保存\n- 清理提示:废砂盒满时 App 推送提醒,建议每 5 至 7 天倾倒一次"
    }
  ],
  "decision": {
    "useful": true,
    "reason": "含MH-LP50与Pro规格及差异说明",
    "response_kind": "knowledge",
    "source": null
  },
  "answer": "您好！根据商品规格资料，MH-LP50（Lite）与 Pro 版（MH-LP100）的主要区别如下：\n\n**智能猫砂盆 Lite（MH-LP50）**[1]\n- 适用猫咪体重：1.5kg 至 6kg\n- 猫砂容量：6L\n- 核心功能：自动感应清理、物理除臭盖板；**不含 App 联网功能**\n- 适合单猫家庭，价格更低\n\n**智能猫砂盆 Pro（MH-LP100）**[2]\n- 适用猫咪体重：1.5kg 至 8kg\n- 猫砂容量：9L，废砂盒约 7 天容量（单猫）\n- 核心功能：自动感应清理、活性炭除臭、**App 远程监控与健康记录**\n- 220V 市电供电，断电后配置自动保存；废砂盒满时 App 推送提醒\n\n简单来说：Pro 版适用体重范围更大、猫砂容量更多，并支持 App 远程监控与健康记录，除臭方式为活性炭；Lite 版无联网功能，价格更低[1][2]。\n\n请问还有什么可以帮您的吗？",
  "point_verdicts": [
    {
      "point_id": "p1",
      "covered": true,
      "reason": "回答明确说明Lite不含App联网功能，并指出Pro支持App远程监控与健康记录，覆盖差异要点及适用型号条件。"
    },
    {
      "point_id": "p2",
      "covered": true,
      "reason": "回答在Lite规格和总结中均指出价格更低、适合单猫家庭，条件限定于MH-LP50被保留。"
    }
  ],
  "claim_verdicts": [
    {
      "claim": "MH-LP50适用猫咪体重为1.5kg至6kg",
      "supported": true,
      "reason": "证据[1]明确记载该型号适用体重1.5kg至6kg。"
    },
    {
      "claim": "MH-LP50猫砂容量为6L",
      "supported": true,
      "reason": "证据[1]明确记载猫砂容量6L。"
    },
    {
      "claim": "MH-LP50核心功能为自动感应清理、物理除臭盖板，不含App联网功能",
      "supported": true,
      "reason": "证据[1]记载核心功能及不含App联网功能，与回答一致。"
    },
    {
      "claim": "MH-LP100适用猫咪体重为1.5kg至8kg",
      "supported": true,
      "reason": "证据[2]明确记载该型号适用体重1.5kg至8kg。"
    },
    {
      "claim": "MH-LP100猫砂容量9L，废砂盒约7天容量（单猫）",
      "supported": true,
      "reason": "证据[2]记载猫砂容量9L，废砂盒容量约7天（单猫）。"
    },
    {
      "claim": "MH-LP100核心功能为自动感应清理、活性炭除臭、App远程监控与健康记录",
      "supported": true,
      "reason": "证据[2]明确记载上述核心功能。"
    },
    {
      "claim": "MH-LP100为220V市电供电，断电后配置自动保存，废砂盒满时App推送提醒",
      "supported": true,
      "reason": "证据[2]记载220V市电、断电后配置自动保存、废砂盒满时App推送提醒。"
    },
    {
      "claim": "Lite版无App远程监控与健康记录，价格更低，适合单猫家庭",
      "supported": true,
      "reason": "证据[1]在与Pro差异部分明确记载Lite无App远程监控与健康记录、价格更低、适合单猫家庭。"
    }
  ],
  "metrics": {
    "recall_at_5": 1.0,
    "recall_at_10": 1.0,
    "mrr_at_10": 1.0,
    "all_groups_hit_at_5": 1.0,
    "all_groups_hit_at_10": 1.0,
    "candidate_group_coverage": 1.0,
    "prompt_group_coverage": 1.0,
    "answer_point_coverage": 1.0,
    "faithfulness": 1.0,
    "absent_refusal_rate": null,
    "answerable_false_refusal_rate": 0.0
  },
  "error": null,
  "elapsed_ms": 18345.342499902472,
  "judge_snapshot": {
    "prompt_version": "joint-generation-v2.1",
    "finish_reason": "stop"
  },
  "audit": {
    "audit_version": 1,
    "source_map_id": "d2dd350d860b8141e52306cbbcafb22f97d091194eb1cdc839a528c2990715eb",
    "gold_groups": [
      {
        "group_id": "g1",
        "alternatives": [
          [
            "product-specs.md:003:991276de42d44e06168ae7625057b9692cbc6be8149687ccf1a752da00b9f9f3"
          ]
        ]
      }
    ],
    "answer_points": [
      {
        "point_id": "p1",
        "text": "MH-LP50 不含 App 联网，少了 Pro 的远程监控与健康记录",
        "condition": "仅适用于智能猫砂盆 Lite(型号 MH-LP50)所述范围",
        "aliases": []
      },
      {
        "point_id": "p2",
        "text": "Lite 价格更低，适合单猫家庭",
        "condition": "仅适用于智能猫砂盆 Lite(型号 MH-LP50)所述范围",
        "aliases": []
      }
    ],
    "candidate_ranking": [
      {
        "chunk_id": 1854,
        "score": 0.032786883413791656,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1853,
        "score": 0.0317540317773819,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1858,
        "score": 0.0317460335791111,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1857,
        "score": 0.02904040366411209,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1859,
        "score": 0.028991596773266792,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1863,
        "score": 0.028958333656191826,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1862,
        "score": 0.028898129239678383,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1861,
        "score": 0.028577260673046112,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1874,
        "score": 0.028438886627554893,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1864,
        "score": 0.028404511511325836,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1860,
        "score": 0.02838164195418358,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1856,
        "score": 0.028370220214128494,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1855,
        "score": 0.02808326855301857,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1878,
        "score": 0.02788461558520794,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1877,
        "score": 0.026685643941164017,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1846,
        "score": 0.02651515230536461,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1838,
        "score": 0.025932952761650085,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1845,
        "score": 0.013333333656191826,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1873,
        "score": 0.01315789483487606,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1852,
        "score": 0.012987012974917889,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1837,
        "score": 0.012820512987673283,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1870,
        "score": 0.012658228166401386,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1832,
        "score": 0.012345679104328156,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1836,
        "score": 0.012195121496915817,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1831,
        "score": 0.012048192322254181,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1848,
        "score": 0.011904762126505375,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1844,
        "score": 0.0117647061124444,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1835,
        "score": 0.011627906933426857,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1867,
        "score": 0.01149425283074379,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1833,
        "score": 0.01123595517128706,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1841,
        "score": 0.011111111380159855,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1850,
        "score": 0.010989011265337467,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1847,
        "score": 0.010869565419852734,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1851,
        "score": 0.01075268816202879,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1842,
        "score": 0.010638297535479069,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1865,
        "score": 0.010526316240429878,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1871,
        "score": 0.010416666977107525,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1866,
        "score": 0.010309278033673763,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1868,
        "score": 0.010204081423580647,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1834,
        "score": 0.010101010091602802,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1876,
        "score": 0.009999999776482582,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1875,
        "score": 0.009900989942252636,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1840,
        "score": 0.009708737954497337,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1843,
        "score": 0.009615384973585606,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1879,
        "score": 0.009523809887468815,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1839,
        "score": 0.009433962404727936,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1880,
        "score": 0.009345794096589088,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1872,
        "score": 0.009259259328246117,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1869,
        "score": 0.00917431153357029,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1849,
        "score": 0.00909090880304575,
        "score_kind": "rrf"
      }
    ],
    "final_ranking": [
      {
        "chunk_id": 1854,
        "score": 0.032786883413791656,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1853,
        "score": 0.0317540317773819,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1858,
        "score": 0.0317460335791111,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1857,
        "score": 0.02904040366411209,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1859,
        "score": 0.028991596773266792,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1863,
        "score": 0.028958333656191826,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1862,
        "score": 0.028898129239678383,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1861,
        "score": 0.028577260673046112,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1874,
        "score": 0.028438886627554893,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1864,
        "score": 0.028404511511325836,
        "score_kind": "rrf"
      }
    ]
  }
}
````

### B3 / hybrid_rerank

````json
{
  "eval_id": "B3",
  "strategy": "hybrid_rerank",
  "bucket": "B_model",
  "difficulty": "model",
  "category": null,
  "should_refuse": false,
  "refused": false,
  "status": "completed",
  "stage": "complete",
  "query": "MH-LP50 和 Pro 版有什么区别",
  "query_plan": {
    "standard": "MH-LP50 和 Pro 版有什么区别",
    "expansions": []
  },
  "mapped_groups": [
    {
      "group_id": "g1",
      "alternatives": [
        [
          1854
        ]
      ]
    }
  ],
  "candidate_ids": [
    1854,
    1853,
    1858,
    1857,
    1859,
    1863,
    1862,
    1861,
    1874,
    1864,
    1860,
    1856,
    1855,
    1878,
    1877,
    1846,
    1838,
    1845,
    1873,
    1852,
    1837,
    1870,
    1832,
    1836,
    1831,
    1848,
    1844,
    1835,
    1867,
    1833,
    1841,
    1850,
    1847,
    1851,
    1842,
    1865,
    1871,
    1866,
    1868,
    1834,
    1876,
    1875,
    1840,
    1843,
    1879,
    1839,
    1880,
    1872,
    1869,
    1849
  ],
  "final_ids": [
    1854,
    1853,
    1858,
    1862,
    1855,
    1864,
    1863,
    1874,
    1857,
    1837
  ],
  "prompt_citations": [
    {
      "n": 1,
      "chunk_id": "1854",
      "section_path": "商品规格手册/智能猫砂盆 Lite(型号 MH-LP50)",
      "question": "智能猫砂盆 Lite(型号 MH-LP50)",
      "answer": "- 型号:MH-LP50\n- 适用猫咪体重:1.5kg 至 6kg\n- 猫砂容量:6L\n- 核心功能:自动感应清理、物理除臭盖板;不含 App 联网功能\n- 与 Pro 差异:Lite 无 App 远程监控与健康记录,价格更低,适合单猫家庭"
    },
    {
      "n": 3,
      "chunk_id": "1858",
      "section_path": "商品规格手册/自动饮水机 Pro 不锈钢(型号 MH-W60)",
      "question": "自动饮水机 Pro 不锈钢(型号 MH-W60)",
      "answer": "- 型号:MH-W60\n- 水箱容量:6L,304 不锈钢表面盘\n- 过滤:双滤芯并联,建议每 4 周更换一次滤芯\n- 核心功能:双泵冗余、无线水位提醒推送 App、缺水断电保护\n- 清洗:不锈钢面盘可高温消毒,建议每周清洗一次"
    },
    {
      "n": 5,
      "chunk_id": "1855",
      "section_path": "商品规格手册/智能猫砂盆 Max(型号 MH-LP200)",
      "question": "智能猫砂盆 Max(型号 MH-LP200)",
      "answer": "- 型号:MH-LP200\n- 适用猫咪体重:2kg 至 12kg,适合大型猫与多猫家庭\n- 猫砂容量:12L,废砂盒容量约 10 天(单猫)\n- 核心功能:超大滚筒、双重称重防夹、活性炭除臭、App 多猫健康档案\n- 供电:220V 市电\n- 清理提示:多猫家庭建议每 3 至 5 天倾倒一次废砂盒"
    },
    {
      "n": 7,
      "chunk_id": "1863",
      "section_path": "商品规格手册/自动喂食器 摄像头版(型号 MH-FD30)",
      "question": "自动喂食器 摄像头版(型号 MH-FD30)",
      "answer": "- 型号:MH-FD30\n- 粮桶容量:6L\n- 核心功能:1080P 摄像头、双向语音、App 远程手动投喂与定时投喂\n- 供电:市电供电 + 内置应急电池\n- 说明:摄像头版支持视频回看,需连接 2.4G Wi-Fi"
    },
    {
      "n": 9,
      "chunk_id": "1857",
      "section_path": "商品规格手册/自动饮水机 Plus(型号 MH-W40)",
      "question": "自动饮水机 Plus(型号 MH-W40)",
      "answer": "- 型号:MH-W40\n- 水箱容量:4L\n- 过滤:五重过滤棉 + 椰壳活性炭,建议每 3 周更换一次滤芯\n- 核心功能:UV 紫外杀菌、静音变频水泵、缺水断电保护\n- 清洗:整机可拆分水洗,建议每周清洗一次"
    },
    {
      "n": 10,
      "chunk_id": "1837",
      "section_path": "售后手册/会员专属售后权益",
      "question": "会员专属售后权益",
      "answer": "金卡会员享优先客服接入与上门取件退换货;银卡会员享退换货运费权益 1 次/月。具体权益以会员中心页面标注为准。"
    },
    {
      "n": 8,
      "chunk_id": "1874",
      "section_path": "会员权益/会员等级",
      "question": "会员等级",
      "answer": "会员分为普通、银卡和金卡三档，按有效累计消费金额自动升级，不按年度消费金额计算。累计消费未满 1000 元为普通会员，满 1000 元起为银卡，满 5000 元起为金卡。\n\n有效累计消费指已完成订单的商品实际支付金额，不含配送费；退货退款部分从有效累计消费中扣除。退款后根据更新的累计消费重新计算等级，未达到原门槛时可能降级。等级与适用权益在会员中心展示。\n\n银卡在参与会员折扣的商品上享 95 折，金卡享 9 折。折扣适用商品和活动范围以结算页面标注为准。会员折扣、优惠券与满减是否叠加也以当次活动页面为准，不能一概承诺全部优惠同时生效。"
    },
    {
      "n": 6,
      "chunk_id": "1864",
      "section_path": "商品规格手册/全景看护摄像头(型号 MH-CAM1)",
      "question": "全景看护摄像头(型号 MH-CAM1)",
      "answer": "- 型号:MH-CAM1\n- 画质:2K 分辨率,355° 水平旋转、90° 俯仰\n- 核心功能:移动侦测报警、夜视、双向语音、逗猫激光\n- 存储:支持最大 128G TF 卡或云存储\n- 供电:Type-C 供电,需连接 2.4G Wi-Fi"
    },
    {
      "n": 4,
      "chunk_id": "1862",
      "section_path": "商品规格手册/自动喂食器 基础版(型号 MH-FD10)",
      "question": "自动喂食器 基础版(型号 MH-FD10)",
      "answer": "- 型号:MH-FD10\n- 粮桶容量:4L\n- 核心功能:定时定量投喂,每日最多 6 餐,语音呼唤进食\n- 供电:市电供电 + 4 节 5 号电池断电应急\n- 说明:基础版不含摄像头与 App 远程投喂"
    },
    {
      "n": 2,
      "chunk_id": "1853",
      "section_path": "商品规格手册/智能猫砂盆 Pro(型号 MH-LP100)",
      "question": "智能猫砂盆 Pro(型号 MH-LP100)",
      "answer": "- 型号:MH-LP100\n- 适用猫咪体重:1.5kg 至 8kg\n- 猫砂容量:9L,废砂盒容量约 7 天(单猫)\n- 核心功能:自动感应清理、活性炭除臭、App 远程监控与健康记录\n- 供电:220V 市电,断电后配置自动保存\n- 清理提示:废砂盒满时 App 推送提醒,建议每 5 至 7 天倾倒一次"
    }
  ],
  "decision": {
    "useful": true,
    "reason": "有MH-LP50与Pro差异说明",
    "response_kind": "knowledge",
    "source": null
  },
  "answer": "您好！根据商品资料，两者主要区别如下：\n\n**智能猫砂盆 Lite（MH-LP50）**[1]\n- 适用猫咪体重：1.5–6kg\n- 猫砂容量：6L\n- 核心功能：自动感应清理、物理除臭盖板，**不含 App 联网功能**\n- 适合单猫家庭，价格更低[1]\n\n**智能猫砂盆 Pro（MH-LP100）**[2]\n- 适用猫咪体重：1.5–8kg\n- 猫砂容量：9L，废砂盒容量约 7 天（单猫）\n- 核心功能：自动感应清理、活性炭除臭、**App 远程监控与健康记录**\n- 断电后配置自动保存，废砂盒满时 App 推送提醒[2]\n\n简单来说：Pro 版容量更大、适用猫咪更重，且多了 App 联网与健康记录功能；Lite 版更经济实惠。如需了解价格或库存，我可以为您查询～",
  "point_verdicts": [
    {
      "point_id": "p1",
      "covered": true,
      "reason": "回答明确指出 Lite(MH-LP50)不含App联网，少了Pro的远程监控与健康记录，且限定于该型号，符合条件"
    },
    {
      "point_id": "p2",
      "covered": true,
      "reason": "回答明确说明Lite价格更低、适合单猫家庭，限定于MH-LP50，符合覆盖标准"
    }
  ],
  "claim_verdicts": [
    {
      "claim": "智能猫砂盆 Lite(MH-LP50)适用猫咪体重为1.5–6kg",
      "supported": true,
      "reason": "证据1明确列出适用体重1.5kg至6kg"
    },
    {
      "claim": "智能猫砂盆 Lite猫砂容量为6L",
      "supported": true,
      "reason": "证据1列出猫砂容量6L"
    },
    {
      "claim": "Lite核心功能为自动感应清理、物理除臭盖板，不含App联网功能",
      "supported": true,
      "reason": "证据1核心功能部分明确该表述"
    },
    {
      "claim": "Lite不含App联网，少了Pro的App远程监控与健康记录功能",
      "supported": true,
      "reason": "证据1的与Pro差异部分明确Lite无App远程监控与健康记录"
    },
    {
      "claim": "Lite适合单猫家庭，价格更低",
      "supported": true,
      "reason": "证据1明确写出价格更低、适合单猫家庭"
    },
    {
      "claim": "智能猫砂盆 Pro(MH-LP100)适用猫咪体重为1.5–8kg",
      "supported": true,
      "reason": "证据2列出适用体重1.5kg至8kg"
    },
    {
      "claim": "Pro猫砂容量为9L，废砂盒容量约7天(单猫)",
      "supported": true,
      "reason": "证据2明确9L及废砂盒约7天(单猫)"
    },
    {
      "claim": "Pro核心功能为自动感应清理、活性炭除臭、App远程监控与健康记录",
      "supported": true,
      "reason": "证据2核心功能部分明确该表述"
    },
    {
      "claim": "Pro断电后配置自动保存",
      "supported": true,
      "reason": "证据2供电部分明确断电后配置自动保存"
    },
    {
      "claim": "Pro废砂盒满时App推送提醒",
      "supported": true,
      "reason": "证据2清理提示明确废砂盒满时App推送提醒"
    },
    {
      "claim": "Pro版容量更大、适用猫咪更重，多了App联网与健康记录功能，Lite版更经济实惠",
      "supported": true,
      "reason": "由证据1、2对比可得：Pro容量9L大于6L，体重上限8kg高于6kg，且有App功能，Lite价格更低"
    }
  ],
  "metrics": {
    "recall_at_5": 1.0,
    "recall_at_10": 1.0,
    "mrr_at_10": 1.0,
    "all_groups_hit_at_5": 1.0,
    "all_groups_hit_at_10": 1.0,
    "candidate_group_coverage": 1.0,
    "prompt_group_coverage": 1.0,
    "answer_point_coverage": 1.0,
    "faithfulness": 1.0,
    "absent_refusal_rate": null,
    "answerable_false_refusal_rate": 0.0
  },
  "error": null,
  "elapsed_ms": 16591.041499981657,
  "judge_snapshot": {
    "prompt_version": "joint-generation-v2.1",
    "finish_reason": "stop"
  },
  "audit": {
    "audit_version": 1,
    "source_map_id": "d2dd350d860b8141e52306cbbcafb22f97d091194eb1cdc839a528c2990715eb",
    "gold_groups": [
      {
        "group_id": "g1",
        "alternatives": [
          [
            "product-specs.md:003:991276de42d44e06168ae7625057b9692cbc6be8149687ccf1a752da00b9f9f3"
          ]
        ]
      }
    ],
    "answer_points": [
      {
        "point_id": "p1",
        "text": "MH-LP50 不含 App 联网，少了 Pro 的远程监控与健康记录",
        "condition": "仅适用于智能猫砂盆 Lite(型号 MH-LP50)所述范围",
        "aliases": []
      },
      {
        "point_id": "p2",
        "text": "Lite 价格更低，适合单猫家庭",
        "condition": "仅适用于智能猫砂盆 Lite(型号 MH-LP50)所述范围",
        "aliases": []
      }
    ],
    "candidate_ranking": [
      {
        "chunk_id": 1854,
        "score": 0.032786883413791656,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1853,
        "score": 0.0317540317773819,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1858,
        "score": 0.0317460335791111,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1857,
        "score": 0.02904040366411209,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1859,
        "score": 0.028991596773266792,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1863,
        "score": 0.028958333656191826,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1862,
        "score": 0.028898129239678383,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1861,
        "score": 0.028577260673046112,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1874,
        "score": 0.028438886627554893,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1864,
        "score": 0.028404511511325836,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1860,
        "score": 0.02838164195418358,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1856,
        "score": 0.028370220214128494,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1855,
        "score": 0.02808326855301857,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1878,
        "score": 0.02788461558520794,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1877,
        "score": 0.026685643941164017,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1846,
        "score": 0.02651515230536461,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1838,
        "score": 0.025932952761650085,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1845,
        "score": 0.013333333656191826,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1873,
        "score": 0.01315789483487606,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1852,
        "score": 0.012987012974917889,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1837,
        "score": 0.012820512987673283,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1870,
        "score": 0.012658228166401386,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1832,
        "score": 0.012345679104328156,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1836,
        "score": 0.012195121496915817,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1831,
        "score": 0.012048192322254181,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1848,
        "score": 0.011904762126505375,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1844,
        "score": 0.0117647061124444,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1835,
        "score": 0.011627906933426857,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1867,
        "score": 0.01149425283074379,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1833,
        "score": 0.01123595517128706,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1841,
        "score": 0.011111111380159855,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1850,
        "score": 0.010989011265337467,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1847,
        "score": 0.010869565419852734,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1851,
        "score": 0.01075268816202879,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1842,
        "score": 0.010638297535479069,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1865,
        "score": 0.010526316240429878,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1871,
        "score": 0.010416666977107525,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1866,
        "score": 0.010309278033673763,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1868,
        "score": 0.010204081423580647,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1834,
        "score": 0.010101010091602802,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1876,
        "score": 0.009999999776482582,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1875,
        "score": 0.009900989942252636,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1840,
        "score": 0.009708737954497337,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1843,
        "score": 0.009615384973585606,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1879,
        "score": 0.009523809887468815,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1839,
        "score": 0.009433962404727936,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1880,
        "score": 0.009345794096589088,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1872,
        "score": 0.009259259328246117,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1869,
        "score": 0.00917431153357029,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1849,
        "score": 0.00909090880304575,
        "score_kind": "rrf"
      }
    ],
    "final_ranking": [
      {
        "chunk_id": 1854,
        "score": 0.9742347002029419,
        "score_kind": "rerank"
      },
      {
        "chunk_id": 1853,
        "score": 0.12143407762050629,
        "score_kind": "rerank"
      },
      {
        "chunk_id": 1858,
        "score": 0.015294485725462437,
        "score_kind": "rerank"
      },
      {
        "chunk_id": 1862,
        "score": 0.00871511921286583,
        "score_kind": "rerank"
      },
      {
        "chunk_id": 1855,
        "score": 0.008358011953532696,
        "score_kind": "rerank"
      },
      {
        "chunk_id": 1864,
        "score": 0.004421382676810026,
        "score_kind": "rerank"
      },
      {
        "chunk_id": 1863,
        "score": 0.003608993487432599,
        "score_kind": "rerank"
      },
      {
        "chunk_id": 1874,
        "score": 0.0033694501034915447,
        "score_kind": "rerank"
      },
      {
        "chunk_id": 1857,
        "score": 0.0017507974989712238,
        "score_kind": "rerank"
      },
      {
        "chunk_id": 1837,
        "score": 0.0016310299979522824,
        "score_kind": "rerank"
      }
    ]
  }
}
````

### B54 / dense

````json
{
  "eval_id": "B54",
  "strategy": "dense",
  "bucket": "B_model",
  "difficulty": "model",
  "category": null,
  "should_refuse": false,
  "refused": null,
  "status": "rewrite_error",
  "stage": "rewrite",
  "query": "MH-W20 和 MH-W60 换滤芯的周期一样吗",
  "query_plan": null,
  "mapped_groups": [
    {
      "group_id": "g1",
      "alternatives": [
        [
          1856
        ]
      ]
    },
    {
      "group_id": "g2",
      "alternatives": [
        [
          1858
        ]
      ]
    }
  ],
  "candidate_ids": null,
  "final_ids": null,
  "prompt_citations": null,
  "decision": null,
  "answer": null,
  "point_verdicts": null,
  "claim_verdicts": null,
  "metrics": {
    "recall_at_5": null,
    "recall_at_10": null,
    "mrr_at_10": null,
    "all_groups_hit_at_5": null,
    "all_groups_hit_at_10": null,
    "candidate_group_coverage": null,
    "prompt_group_coverage": null,
    "answer_point_coverage": null,
    "faithfulness": null,
    "absent_refusal_rate": null,
    "answerable_false_refusal_rate": null
  },
  "error": {
    "code": "rewrite_error",
    "type": "ServiceError",
    "message": "该阶段执行失败"
  },
  "elapsed_ms": 1422.989800106734,
  "judge_snapshot": null,
  "audit": {
    "audit_version": 1,
    "source_map_id": "d2dd350d860b8141e52306cbbcafb22f97d091194eb1cdc839a528c2990715eb",
    "gold_groups": [
      {
        "group_id": "g1",
        "alternatives": [
          [
            "product-specs.md:005:58f10003acf72bef5aa921d603dc1a58bb0332dcd7f8735057266e573f01e11b"
          ]
        ]
      },
      {
        "group_id": "g2",
        "alternatives": [
          [
            "product-specs.md:007:e9867a419061278a1bc0599bc3595ac01da4c561aea19bf0bf4c9bde5ba30e7f"
          ]
        ]
      }
    ],
    "answer_points": [
      {
        "point_id": "p1",
        "text": "MH-W20 建议每 2 周换滤芯",
        "condition": "仅适用于自动饮水机(型号 MH-W20)所述范围",
        "aliases": []
      },
      {
        "point_id": "p2",
        "text": "MH-W60 建议每 4 周换滤芯，两款周期不同",
        "condition": "仅适用于自动饮水机 Pro 不锈钢(型号 MH-W60)所述范围",
        "aliases": []
      }
    ],
    "candidate_ranking": null,
    "final_ranking": null
  }
}
````

### B54 / bm25

````json
{
  "eval_id": "B54",
  "strategy": "bm25",
  "bucket": "B_model",
  "difficulty": "model",
  "category": null,
  "should_refuse": false,
  "refused": null,
  "status": "rewrite_error",
  "stage": "rewrite",
  "query": "MH-W20 和 MH-W60 换滤芯的周期一样吗",
  "query_plan": null,
  "mapped_groups": [
    {
      "group_id": "g1",
      "alternatives": [
        [
          1856
        ]
      ]
    },
    {
      "group_id": "g2",
      "alternatives": [
        [
          1858
        ]
      ]
    }
  ],
  "candidate_ids": null,
  "final_ids": null,
  "prompt_citations": null,
  "decision": null,
  "answer": null,
  "point_verdicts": null,
  "claim_verdicts": null,
  "metrics": {
    "recall_at_5": null,
    "recall_at_10": null,
    "mrr_at_10": null,
    "all_groups_hit_at_5": null,
    "all_groups_hit_at_10": null,
    "candidate_group_coverage": null,
    "prompt_group_coverage": null,
    "answer_point_coverage": null,
    "faithfulness": null,
    "absent_refusal_rate": null,
    "answerable_false_refusal_rate": null
  },
  "error": {
    "code": "rewrite_error",
    "type": "ServiceError",
    "message": "该阶段执行失败"
  },
  "elapsed_ms": 1422.989800106734,
  "judge_snapshot": null,
  "audit": {
    "audit_version": 1,
    "source_map_id": "d2dd350d860b8141e52306cbbcafb22f97d091194eb1cdc839a528c2990715eb",
    "gold_groups": [
      {
        "group_id": "g1",
        "alternatives": [
          [
            "product-specs.md:005:58f10003acf72bef5aa921d603dc1a58bb0332dcd7f8735057266e573f01e11b"
          ]
        ]
      },
      {
        "group_id": "g2",
        "alternatives": [
          [
            "product-specs.md:007:e9867a419061278a1bc0599bc3595ac01da4c561aea19bf0bf4c9bde5ba30e7f"
          ]
        ]
      }
    ],
    "answer_points": [
      {
        "point_id": "p1",
        "text": "MH-W20 建议每 2 周换滤芯",
        "condition": "仅适用于自动饮水机(型号 MH-W20)所述范围",
        "aliases": []
      },
      {
        "point_id": "p2",
        "text": "MH-W60 建议每 4 周换滤芯，两款周期不同",
        "condition": "仅适用于自动饮水机 Pro 不锈钢(型号 MH-W60)所述范围",
        "aliases": []
      }
    ],
    "candidate_ranking": null,
    "final_ranking": null
  }
}
````

### B54 / hybrid

````json
{
  "eval_id": "B54",
  "strategy": "hybrid",
  "bucket": "B_model",
  "difficulty": "model",
  "category": null,
  "should_refuse": false,
  "refused": null,
  "status": "rewrite_error",
  "stage": "rewrite",
  "query": "MH-W20 和 MH-W60 换滤芯的周期一样吗",
  "query_plan": null,
  "mapped_groups": [
    {
      "group_id": "g1",
      "alternatives": [
        [
          1856
        ]
      ]
    },
    {
      "group_id": "g2",
      "alternatives": [
        [
          1858
        ]
      ]
    }
  ],
  "candidate_ids": null,
  "final_ids": null,
  "prompt_citations": null,
  "decision": null,
  "answer": null,
  "point_verdicts": null,
  "claim_verdicts": null,
  "metrics": {
    "recall_at_5": null,
    "recall_at_10": null,
    "mrr_at_10": null,
    "all_groups_hit_at_5": null,
    "all_groups_hit_at_10": null,
    "candidate_group_coverage": null,
    "prompt_group_coverage": null,
    "answer_point_coverage": null,
    "faithfulness": null,
    "absent_refusal_rate": null,
    "answerable_false_refusal_rate": null
  },
  "error": {
    "code": "rewrite_error",
    "type": "ServiceError",
    "message": "该阶段执行失败"
  },
  "elapsed_ms": 1422.989800106734,
  "judge_snapshot": null,
  "audit": {
    "audit_version": 1,
    "source_map_id": "d2dd350d860b8141e52306cbbcafb22f97d091194eb1cdc839a528c2990715eb",
    "gold_groups": [
      {
        "group_id": "g1",
        "alternatives": [
          [
            "product-specs.md:005:58f10003acf72bef5aa921d603dc1a58bb0332dcd7f8735057266e573f01e11b"
          ]
        ]
      },
      {
        "group_id": "g2",
        "alternatives": [
          [
            "product-specs.md:007:e9867a419061278a1bc0599bc3595ac01da4c561aea19bf0bf4c9bde5ba30e7f"
          ]
        ]
      }
    ],
    "answer_points": [
      {
        "point_id": "p1",
        "text": "MH-W20 建议每 2 周换滤芯",
        "condition": "仅适用于自动饮水机(型号 MH-W20)所述范围",
        "aliases": []
      },
      {
        "point_id": "p2",
        "text": "MH-W60 建议每 4 周换滤芯，两款周期不同",
        "condition": "仅适用于自动饮水机 Pro 不锈钢(型号 MH-W60)所述范围",
        "aliases": []
      }
    ],
    "candidate_ranking": null,
    "final_ranking": null
  }
}
````

### B54 / hybrid_rerank

````json
{
  "eval_id": "B54",
  "strategy": "hybrid_rerank",
  "bucket": "B_model",
  "difficulty": "model",
  "category": null,
  "should_refuse": false,
  "refused": null,
  "status": "rewrite_error",
  "stage": "rewrite",
  "query": "MH-W20 和 MH-W60 换滤芯的周期一样吗",
  "query_plan": null,
  "mapped_groups": [
    {
      "group_id": "g1",
      "alternatives": [
        [
          1856
        ]
      ]
    },
    {
      "group_id": "g2",
      "alternatives": [
        [
          1858
        ]
      ]
    }
  ],
  "candidate_ids": null,
  "final_ids": null,
  "prompt_citations": null,
  "decision": null,
  "answer": null,
  "point_verdicts": null,
  "claim_verdicts": null,
  "metrics": {
    "recall_at_5": null,
    "recall_at_10": null,
    "mrr_at_10": null,
    "all_groups_hit_at_5": null,
    "all_groups_hit_at_10": null,
    "candidate_group_coverage": null,
    "prompt_group_coverage": null,
    "answer_point_coverage": null,
    "faithfulness": null,
    "absent_refusal_rate": null,
    "answerable_false_refusal_rate": null
  },
  "error": {
    "code": "rewrite_error",
    "type": "ServiceError",
    "message": "该阶段执行失败"
  },
  "elapsed_ms": 1422.989800106734,
  "judge_snapshot": null,
  "audit": {
    "audit_version": 1,
    "source_map_id": "d2dd350d860b8141e52306cbbcafb22f97d091194eb1cdc839a528c2990715eb",
    "gold_groups": [
      {
        "group_id": "g1",
        "alternatives": [
          [
            "product-specs.md:005:58f10003acf72bef5aa921d603dc1a58bb0332dcd7f8735057266e573f01e11b"
          ]
        ]
      },
      {
        "group_id": "g2",
        "alternatives": [
          [
            "product-specs.md:007:e9867a419061278a1bc0599bc3595ac01da4c561aea19bf0bf4c9bde5ba30e7f"
          ]
        ]
      }
    ],
    "answer_points": [
      {
        "point_id": "p1",
        "text": "MH-W20 建议每 2 周换滤芯",
        "condition": "仅适用于自动饮水机(型号 MH-W20)所述范围",
        "aliases": []
      },
      {
        "point_id": "p2",
        "text": "MH-W60 建议每 4 周换滤芯，两款周期不同",
        "condition": "仅适用于自动饮水机 Pro 不锈钢(型号 MH-W60)所述范围",
        "aliases": []
      }
    ],
    "candidate_ranking": null,
    "final_ranking": null
  }
}
````

### C5 / dense

````json
{
  "eval_id": "C5",
  "strategy": "dense",
  "bucket": "C_colloquial",
  "difficulty": "colloquial",
  "category": null,
  "should_refuse": false,
  "refused": false,
  "status": "completed",
  "stage": "complete",
  "query": "那个邮费到底要给多少钱啊",
  "query_plan": {
    "standard": "那个邮费到底要给多少钱啊",
    "expansions": []
  },
  "mapped_groups": [
    {
      "group_id": "g1",
      "alternatives": [
        [
          1842
        ]
      ]
    }
  ],
  "candidate_ids": [
    1842,
    1877,
    1851,
    1868,
    1876,
    1869,
    1847,
    1836,
    1871,
    1845,
    1843,
    1874,
    1837,
    1870,
    1878,
    1850,
    1875,
    1831,
    1841,
    1879,
    1873,
    1844,
    1840,
    1867,
    1853,
    1865,
    1854,
    1832,
    1848,
    1846,
    1839,
    1855,
    1858,
    1838,
    1857,
    1862,
    1866,
    1835,
    1849,
    1856,
    1863,
    1861,
    1860,
    1833,
    1859,
    1872,
    1834,
    1852,
    1864,
    1880
  ],
  "final_ids": [
    1842,
    1877,
    1851,
    1868,
    1876,
    1869,
    1847,
    1836,
    1871,
    1845
  ],
  "prompt_citations": [
    {
      "n": 1,
      "chunk_id": "1842",
      "section_path": "商品与购物 FAQ/运费怎么算",
      "question": "运费怎么算",
      "answer": "单笔订单满 99 元包邮,未满收取 10 元运费,偏远地区运费另计。邮费即运费,按此规则收取。"
    },
    {
      "n": 3,
      "chunk_id": "1851",
      "section_path": "商品与购物 FAQ/会员运费权益",
      "question": "会员运费权益",
      "answer": "金卡会员每月享 3 次免运费权益,银卡会员享 1 次;权益不与偏远地区附加运费冲抵,当月未用完不结转。"
    },
    {
      "n": 5,
      "chunk_id": "1876",
      "section_path": "积分规则/积分怎么攒",
      "question": "积分怎么攒",
      "answer": "已完成订单每实际支付 1 元商品金额累计 1 积分，不计配送费；退款后按对应商品金额同步扣回积分。活动期间的双倍积分属于额外积分奖励，不计入会员等级升级；会员等级仍按有效累计消费金额计算。"
    },
    {
      "n": 7,
      "chunk_id": "1847",
      "section_path": "商品与购物 FAQ/配送范围与偏远地区",
      "question": "配送范围与偏远地区",
      "answer": "全国大部分地区支持配送,新疆、西藏、内蒙古等偏远地区运费另计且时效顺延;港澳台及海外暂不支持自营配送。"
    },
    {
      "n": 9,
      "chunk_id": "1871",
      "section_path": "退货退款政策/运输破损处理",
      "question": "运输破损处理",
      "answer": "商品运输途中破损的,请在签收后 48 小时内联系客服并提供开箱视频与照片,核实后可免费补发或退款,相关运费由平台承担。"
    },
    {
      "n": 10,
      "chunk_id": "1845",
      "section_path": "商品与购物 FAQ/会员等级与积分规则",
      "question": "会员等级与积分规则",
      "answer": "会员分为普通、银卡、金卡三档,按累计消费自动升级。每消费 1 元得 1 积分,积分可在结算时抵扣,100 积分抵 1 元。"
    },
    {
      "n": 8,
      "chunk_id": "1836",
      "section_path": "售后手册/维修寄修流程",
      "question": "维修寄修流程",
      "answer": "保修期内设备故障,联系客服登记后按指引将设备寄回指定维修点,核验后免费维修并寄回;超保或人为损坏维修可能收取工本费,费用会提前告知。"
    },
    {
      "n": 6,
      "chunk_id": "1869",
      "section_path": "退货退款政策/退换货运费承担",
      "question": "退换货运费承担",
      "answer": "无理由退货的退回运费由买家承担;因商品质量问题、发错货、少发漏发导致的退换货,运费由平台承担。运费承担以平台售后规则最终判定为准。"
    },
    {
      "n": 4,
      "chunk_id": "1868",
      "section_path": "退货退款政策/换货政策/换货运费",
      "question": "换货运费",
      "answer": "非质量问题的换货,往返运费由买家承担;因质量问题或发错货的换货,往返运费由平台承担。"
    },
    {
      "n": 2,
      "chunk_id": "1877",
      "section_path": "积分规则/积分怎么用",
      "question": "积分怎么用",
      "answer": "积分可在结算时抵扣商品金额，100 积分抵 1 元现金，单笔订单最多抵 30 元，不用于抵扣偏远地区附加运费，也不支持直接提现。\n\n2000 积分可兑换自动饮水机滤芯 3 片，该兑换套装适用于 MH-W40，普通配送地区包邮；偏远地区附加配送费仍需按页面规则确认。MH-W40 的滤芯更换周期以商品规格手册为准。\n\n800 积分可兑换猫零食小样，普通配送地区另收 6 元运费；该兑换不直接套用普通购物订单的满 99 元包邮规则。兑换商品、可用库存及偏远地区配送规则以兑换页面标注为准。"
    }
  ],
  "decision": {
    "useful": true,
    "reason": "运费规则有直接证据",
    "response_kind": "knowledge",
    "source": null
  },
  "answer": "您好！根据商家规则[1]：**单笔订单满 99 元包邮**，未满则收取 **10 元运费**；偏远地区（如新疆、西藏、内蒙古等）运费另计[1][7]。\n\n另外，会员有免运费权益：金卡会员每月 3 次、银卡会员 1 次[3]。\n\n请问您是咨询普通购物的运费，还是退换货/积分兑换的运费呢？如果是退换货运费，需视是否为质量问题而定[6][4]。",
  "point_verdicts": [
    {
      "point_id": "p1",
      "covered": true,
      "reason": "回答明确说明单笔订单满99元包邮，未满收10元，与要点一致。"
    },
    {
      "point_id": "p2",
      "covered": true,
      "reason": "回答提到偏远地区（新疆、西藏、内蒙古等）运费另计，覆盖要点及条件。"
    }
  ],
  "claim_verdicts": [
    {
      "claim": "单笔订单满99元包邮，未满收取10元运费",
      "supported": true,
      "reason": "证据1明确写明满99元包邮，未满收10元运费。"
    },
    {
      "claim": "偏远地区（如新疆、西藏、内蒙古等）运费另计",
      "supported": true,
      "reason": "证据1和证据7均支持偏远地区运费另计，且列有新疆、西藏、内蒙古。"
    },
    {
      "claim": "金卡会员每月有3次免运费权益",
      "supported": true,
      "reason": "证据3明确金卡会员每月享3次免运费权益。"
    },
    {
      "claim": "银卡会员每月有1次免运费权益",
      "supported": true,
      "reason": "证据3明确银卡会员享1次免运费权益。"
    },
    {
      "claim": "退换货运费需视是否为质量问题而定",
      "supported": true,
      "reason": "证据6和证据4说明质量问题由平台承担、无理由退货由买家承担。"
    }
  ],
  "metrics": {
    "recall_at_5": 1.0,
    "recall_at_10": 1.0,
    "mrr_at_10": 1.0,
    "all_groups_hit_at_5": 1.0,
    "all_groups_hit_at_10": 1.0,
    "candidate_group_coverage": 1.0,
    "prompt_group_coverage": 1.0,
    "answer_point_coverage": 1.0,
    "faithfulness": 1.0,
    "absent_refusal_rate": null,
    "answerable_false_refusal_rate": 0.0
  },
  "error": null,
  "elapsed_ms": 12739.672400057316,
  "judge_snapshot": {
    "prompt_version": "joint-generation-v2.1",
    "finish_reason": "stop"
  },
  "audit": {
    "audit_version": 1,
    "source_map_id": "d2dd350d860b8141e52306cbbcafb22f97d091194eb1cdc839a528c2990715eb",
    "gold_groups": [
      {
        "group_id": "g1",
        "alternatives": [
          [
            "product-faq.md:005:a378cfa07513ed7b747b8870ef187c00e9e1ce815a4bac7cfd9bfda4c9e43805"
          ]
        ]
      }
    ],
    "answer_points": [
      {
        "point_id": "p1",
        "text": "普通地区订单满 99 元包邮，未满收 10 元",
        "condition": "普通订单基础运费；偏远地区另计",
        "aliases": []
      },
      {
        "point_id": "p2",
        "text": "偏远地区运费另计",
        "condition": "普通订单基础运费；偏远地区另计",
        "aliases": []
      }
    ],
    "candidate_ranking": [
      {
        "chunk_id": 1842,
        "score": 0.7382994890213013,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1877,
        "score": 0.5855824947357178,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1851,
        "score": 0.5739358067512512,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1868,
        "score": 0.5729373693466187,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1876,
        "score": 0.565174400806427,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1869,
        "score": 0.5578080415725708,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1847,
        "score": 0.5497187972068787,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1836,
        "score": 0.5388888716697693,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1871,
        "score": 0.5263242721557617,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1845,
        "score": 0.526046097278595,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1843,
        "score": 0.5228790044784546,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1874,
        "score": 0.5203941464424133,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1837,
        "score": 0.5191847085952759,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1870,
        "score": 0.509453296661377,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1878,
        "score": 0.4977514445781708,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1850,
        "score": 0.4867149889469147,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1875,
        "score": 0.48516929149627686,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1831,
        "score": 0.48189276456832886,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1841,
        "score": 0.48042619228363037,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1879,
        "score": 0.47809720039367676,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1873,
        "score": 0.47534236311912537,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1844,
        "score": 0.4640308618545532,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1840,
        "score": 0.4589749574661255,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1867,
        "score": 0.44900161027908325,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1853,
        "score": 0.443844735622406,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1865,
        "score": 0.44309836626052856,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1854,
        "score": 0.43892401456832886,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1832,
        "score": 0.4369591772556305,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1848,
        "score": 0.4322296977043152,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1846,
        "score": 0.4301239252090454,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1839,
        "score": 0.42482614517211914,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1855,
        "score": 0.42323747277259827,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1858,
        "score": 0.42318934202194214,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1838,
        "score": 0.4230842590332031,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1857,
        "score": 0.42298126220703125,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1862,
        "score": 0.4166148900985718,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1866,
        "score": 0.416207492351532,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1835,
        "score": 0.4151606261730194,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1849,
        "score": 0.4088750183582306,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1856,
        "score": 0.4075733721256256,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1863,
        "score": 0.4062274098396301,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1861,
        "score": 0.40373897552490234,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1860,
        "score": 0.3983946442604065,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1833,
        "score": 0.3978709578514099,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1859,
        "score": 0.39473581314086914,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1872,
        "score": 0.3898211121559143,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1834,
        "score": 0.38612908124923706,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1852,
        "score": 0.3702229857444763,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1864,
        "score": 0.3483118414878845,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1880,
        "score": 0.33238232135772705,
        "score_kind": "cosine"
      }
    ],
    "final_ranking": [
      {
        "chunk_id": 1842,
        "score": 0.7382994890213013,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1877,
        "score": 0.5855824947357178,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1851,
        "score": 0.5739358067512512,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1868,
        "score": 0.5729373693466187,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1876,
        "score": 0.565174400806427,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1869,
        "score": 0.5578080415725708,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1847,
        "score": 0.5497187972068787,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1836,
        "score": 0.5388888716697693,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1871,
        "score": 0.5263242721557617,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1845,
        "score": 0.526046097278595,
        "score_kind": "cosine"
      }
    ]
  }
}
````

### C5 / bm25

````json
{
  "eval_id": "C5",
  "strategy": "bm25",
  "bucket": "C_colloquial",
  "difficulty": "colloquial",
  "category": null,
  "should_refuse": false,
  "refused": false,
  "status": "completed",
  "stage": "complete",
  "query": "那个邮费到底要给多少钱啊",
  "query_plan": {
    "standard": "那个邮费到底要给多少钱啊",
    "expansions": []
  },
  "mapped_groups": [
    {
      "group_id": "g1",
      "alternatives": [
        [
          1842
        ]
      ]
    }
  ],
  "candidate_ids": [
    1842
  ],
  "final_ids": [
    1842
  ],
  "prompt_citations": [
    {
      "n": 1,
      "chunk_id": "1842",
      "section_path": "商品与购物 FAQ/运费怎么算",
      "question": "运费怎么算",
      "answer": "单笔订单满 99 元包邮,未满收取 10 元运费,偏远地区运费另计。邮费即运费,按此规则收取。"
    }
  ],
  "decision": {
    "useful": true,
    "reason": "运费规则已给出",
    "response_kind": "knowledge",
    "source": null
  },
  "answer": "您好！根据运费规则[1]：\n- 单笔订单满 99 元包邮；\n- 未满 99 元收取 10 元运费；\n- 偏远地区运费另计。\n\n如有其他问题，欢迎随时咨询~",
  "point_verdicts": [
    {
      "point_id": "p1",
      "covered": true,
      "reason": "回答明确说明满99元包邮、未满收取10元运费，覆盖普通订单基础运费规则"
    },
    {
      "point_id": "p2",
      "covered": true,
      "reason": "回答提及偏远地区运费另计，覆盖该要点"
    }
  ],
  "claim_verdicts": [
    {
      "claim": "单笔订单满99元包邮",
      "supported": true,
      "reason": "证据[1]明确写明单笔订单满99元包邮"
    },
    {
      "claim": "未满99元收取10元运费",
      "supported": true,
      "reason": "证据[1]明确写明未满收取10元运费"
    },
    {
      "claim": "偏远地区运费另计",
      "supported": true,
      "reason": "证据[1]明确写明偏远地区运费另计"
    }
  ],
  "metrics": {
    "recall_at_5": 1.0,
    "recall_at_10": 1.0,
    "mrr_at_10": 1.0,
    "all_groups_hit_at_5": 1.0,
    "all_groups_hit_at_10": 1.0,
    "candidate_group_coverage": 1.0,
    "prompt_group_coverage": 1.0,
    "answer_point_coverage": 1.0,
    "faithfulness": 1.0,
    "absent_refusal_rate": null,
    "answerable_false_refusal_rate": 0.0
  },
  "error": null,
  "elapsed_ms": 7800.854300148785,
  "judge_snapshot": {
    "prompt_version": "joint-generation-v2.1",
    "finish_reason": "stop"
  },
  "audit": {
    "audit_version": 1,
    "source_map_id": "d2dd350d860b8141e52306cbbcafb22f97d091194eb1cdc839a528c2990715eb",
    "gold_groups": [
      {
        "group_id": "g1",
        "alternatives": [
          [
            "product-faq.md:005:a378cfa07513ed7b747b8870ef187c00e9e1ce815a4bac7cfd9bfda4c9e43805"
          ]
        ]
      }
    ],
    "answer_points": [
      {
        "point_id": "p1",
        "text": "普通地区订单满 99 元包邮，未满收 10 元",
        "condition": "普通订单基础运费；偏远地区另计",
        "aliases": []
      },
      {
        "point_id": "p2",
        "text": "偏远地区运费另计",
        "condition": "普通订单基础运费；偏远地区另计",
        "aliases": []
      }
    ],
    "candidate_ranking": [
      {
        "chunk_id": 1842,
        "score": 4.1900835037231445,
        "score_kind": "bm25"
      }
    ],
    "final_ranking": [
      {
        "chunk_id": 1842,
        "score": 4.1900835037231445,
        "score_kind": "bm25"
      }
    ]
  }
}
````

### C5 / hybrid

````json
{
  "eval_id": "C5",
  "strategy": "hybrid",
  "bucket": "C_colloquial",
  "difficulty": "colloquial",
  "category": null,
  "should_refuse": false,
  "refused": false,
  "status": "completed",
  "stage": "complete",
  "query": "那个邮费到底要给多少钱啊",
  "query_plan": {
    "standard": "那个邮费到底要给多少钱啊",
    "expansions": []
  },
  "mapped_groups": [
    {
      "group_id": "g1",
      "alternatives": [
        [
          1842
        ]
      ]
    }
  ],
  "candidate_ids": [
    1842,
    1877,
    1851,
    1868,
    1876,
    1869,
    1847,
    1836,
    1871,
    1845,
    1843,
    1874,
    1837,
    1870,
    1878,
    1850,
    1875,
    1831,
    1841,
    1879,
    1873,
    1844,
    1840,
    1867,
    1853,
    1865,
    1854,
    1832,
    1848,
    1846,
    1839,
    1855,
    1858,
    1838,
    1857,
    1862,
    1866,
    1835,
    1849,
    1856,
    1863,
    1861,
    1860,
    1833,
    1859,
    1872,
    1834,
    1852,
    1864,
    1880
  ],
  "final_ids": [
    1842,
    1877,
    1851,
    1868,
    1876,
    1869,
    1847,
    1836,
    1871,
    1845
  ],
  "prompt_citations": [
    {
      "n": 1,
      "chunk_id": "1842",
      "section_path": "商品与购物 FAQ/运费怎么算",
      "question": "运费怎么算",
      "answer": "单笔订单满 99 元包邮,未满收取 10 元运费,偏远地区运费另计。邮费即运费,按此规则收取。"
    },
    {
      "n": 3,
      "chunk_id": "1851",
      "section_path": "商品与购物 FAQ/会员运费权益",
      "question": "会员运费权益",
      "answer": "金卡会员每月享 3 次免运费权益,银卡会员享 1 次;权益不与偏远地区附加运费冲抵,当月未用完不结转。"
    },
    {
      "n": 5,
      "chunk_id": "1876",
      "section_path": "积分规则/积分怎么攒",
      "question": "积分怎么攒",
      "answer": "已完成订单每实际支付 1 元商品金额累计 1 积分，不计配送费；退款后按对应商品金额同步扣回积分。活动期间的双倍积分属于额外积分奖励，不计入会员等级升级；会员等级仍按有效累计消费金额计算。"
    },
    {
      "n": 7,
      "chunk_id": "1847",
      "section_path": "商品与购物 FAQ/配送范围与偏远地区",
      "question": "配送范围与偏远地区",
      "answer": "全国大部分地区支持配送,新疆、西藏、内蒙古等偏远地区运费另计且时效顺延;港澳台及海外暂不支持自营配送。"
    },
    {
      "n": 9,
      "chunk_id": "1871",
      "section_path": "退货退款政策/运输破损处理",
      "question": "运输破损处理",
      "answer": "商品运输途中破损的,请在签收后 48 小时内联系客服并提供开箱视频与照片,核实后可免费补发或退款,相关运费由平台承担。"
    },
    {
      "n": 10,
      "chunk_id": "1845",
      "section_path": "商品与购物 FAQ/会员等级与积分规则",
      "question": "会员等级与积分规则",
      "answer": "会员分为普通、银卡、金卡三档,按累计消费自动升级。每消费 1 元得 1 积分,积分可在结算时抵扣,100 积分抵 1 元。"
    },
    {
      "n": 8,
      "chunk_id": "1836",
      "section_path": "售后手册/维修寄修流程",
      "question": "维修寄修流程",
      "answer": "保修期内设备故障,联系客服登记后按指引将设备寄回指定维修点,核验后免费维修并寄回;超保或人为损坏维修可能收取工本费,费用会提前告知。"
    },
    {
      "n": 6,
      "chunk_id": "1869",
      "section_path": "退货退款政策/退换货运费承担",
      "question": "退换货运费承担",
      "answer": "无理由退货的退回运费由买家承担;因商品质量问题、发错货、少发漏发导致的退换货,运费由平台承担。运费承担以平台售后规则最终判定为准。"
    },
    {
      "n": 4,
      "chunk_id": "1868",
      "section_path": "退货退款政策/换货政策/换货运费",
      "question": "换货运费",
      "answer": "非质量问题的换货,往返运费由买家承担;因质量问题或发错货的换货,往返运费由平台承担。"
    },
    {
      "n": 2,
      "chunk_id": "1877",
      "section_path": "积分规则/积分怎么用",
      "question": "积分怎么用",
      "answer": "积分可在结算时抵扣商品金额，100 积分抵 1 元现金，单笔订单最多抵 30 元，不用于抵扣偏远地区附加运费，也不支持直接提现。\n\n2000 积分可兑换自动饮水机滤芯 3 片，该兑换套装适用于 MH-W40，普通配送地区包邮；偏远地区附加配送费仍需按页面规则确认。MH-W40 的滤芯更换周期以商品规格手册为准。\n\n800 积分可兑换猫零食小样，普通配送地区另收 6 元运费；该兑换不直接套用普通购物订单的满 99 元包邮规则。兑换商品、可用库存及偏远地区配送规则以兑换页面标注为准。"
    }
  ],
  "decision": {
    "useful": true,
    "reason": "运费规则有明确证据：满99包邮，未满收10元，偏远另计",
    "response_kind": "knowledge",
    "source": null
  },
  "answer": "您好！根据商家规则：单笔订单满 99 元包邮，未满则收取 10 元运费，偏远地区（如新疆、西藏、内蒙古等）运费另计[1]。\n\n另外，金卡会员每月有 3 次免运费权益，银卡会员有 1 次[3]。\n\n如您能告知订单情况或配送地区，我可以帮您进一步确认哦～",
  "point_verdicts": [
    {
      "point_id": "p1",
      "covered": true,
      "reason": "回答明确说明满99元包邮、未满收10元运费，条件与规则一致"
    },
    {
      "point_id": "p2",
      "covered": true,
      "reason": "回答明确说明偏远地区（如新疆、西藏、内蒙古等）运费另计"
    }
  ],
  "claim_verdicts": [
    {
      "claim": "单笔订单满99元包邮，未满则收取10元运费",
      "supported": true,
      "reason": "证据[1]明确：单笔订单满99元包邮，未满收取10元运费"
    },
    {
      "claim": "偏远地区（如新疆、西藏、内蒙古等）运费另计",
      "supported": true,
      "reason": "证据[1]说明偏远地区运费另计，证据[7]列举新疆、西藏、内蒙古等为偏远地区"
    },
    {
      "claim": "金卡会员每月有3次免运费权益，银卡会员有1次",
      "supported": true,
      "reason": "证据[3]明确：金卡会员每月享3次免运费权益，银卡会员享1次"
    }
  ],
  "metrics": {
    "recall_at_5": 1.0,
    "recall_at_10": 1.0,
    "mrr_at_10": 1.0,
    "all_groups_hit_at_5": 1.0,
    "all_groups_hit_at_10": 1.0,
    "candidate_group_coverage": 1.0,
    "prompt_group_coverage": 1.0,
    "answer_point_coverage": 1.0,
    "faithfulness": 1.0,
    "absent_refusal_rate": null,
    "answerable_false_refusal_rate": 0.0
  },
  "error": null,
  "elapsed_ms": 10727.132400032133,
  "judge_snapshot": {
    "prompt_version": "joint-generation-v2.1",
    "finish_reason": "stop"
  },
  "audit": {
    "audit_version": 1,
    "source_map_id": "d2dd350d860b8141e52306cbbcafb22f97d091194eb1cdc839a528c2990715eb",
    "gold_groups": [
      {
        "group_id": "g1",
        "alternatives": [
          [
            "product-faq.md:005:a378cfa07513ed7b747b8870ef187c00e9e1ce815a4bac7cfd9bfda4c9e43805"
          ]
        ]
      }
    ],
    "answer_points": [
      {
        "point_id": "p1",
        "text": "普通地区订单满 99 元包邮，未满收 10 元",
        "condition": "普通订单基础运费；偏远地区另计",
        "aliases": []
      },
      {
        "point_id": "p2",
        "text": "偏远地区运费另计",
        "condition": "普通订单基础运费；偏远地区另计",
        "aliases": []
      }
    ],
    "candidate_ranking": [
      {
        "chunk_id": 1842,
        "score": 0.032786883413791656,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1877,
        "score": 0.016129031777381897,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1851,
        "score": 0.01587301678955555,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1868,
        "score": 0.015625,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1876,
        "score": 0.015384615398943424,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1869,
        "score": 0.01515151560306549,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1847,
        "score": 0.014925372786819935,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1836,
        "score": 0.014705882407724857,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1871,
        "score": 0.014492753893136978,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1845,
        "score": 0.014285714365541935,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1843,
        "score": 0.014084506779909134,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1874,
        "score": 0.013888888992369175,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1837,
        "score": 0.013698630034923553,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1870,
        "score": 0.013513513840734959,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1878,
        "score": 0.013333333656191826,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1850,
        "score": 0.01315789483487606,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1875,
        "score": 0.012987012974917889,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1831,
        "score": 0.012820512987673283,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1841,
        "score": 0.012658228166401386,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1879,
        "score": 0.012500000186264515,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1873,
        "score": 0.012345679104328156,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1844,
        "score": 0.012195121496915817,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1840,
        "score": 0.012048192322254181,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1867,
        "score": 0.011904762126505375,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1853,
        "score": 0.0117647061124444,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1865,
        "score": 0.011627906933426857,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1854,
        "score": 0.01149425283074379,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1832,
        "score": 0.011363636702299118,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1848,
        "score": 0.01123595517128706,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1846,
        "score": 0.011111111380159855,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1839,
        "score": 0.010989011265337467,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1855,
        "score": 0.010869565419852734,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1858,
        "score": 0.01075268816202879,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1838,
        "score": 0.010638297535479069,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1857,
        "score": 0.010526316240429878,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1862,
        "score": 0.010416666977107525,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1866,
        "score": 0.010309278033673763,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1835,
        "score": 0.010204081423580647,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1849,
        "score": 0.010101010091602802,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1856,
        "score": 0.009999999776482582,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1863,
        "score": 0.009900989942252636,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1861,
        "score": 0.009803921915590763,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1860,
        "score": 0.009708737954497337,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1833,
        "score": 0.009615384973585606,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1859,
        "score": 0.009523809887468815,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1872,
        "score": 0.009433962404727936,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1834,
        "score": 0.009345794096589088,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1852,
        "score": 0.009259259328246117,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1864,
        "score": 0.00917431153357029,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1880,
        "score": 0.00909090880304575,
        "score_kind": "rrf"
      }
    ],
    "final_ranking": [
      {
        "chunk_id": 1842,
        "score": 0.032786883413791656,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1877,
        "score": 0.016129031777381897,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1851,
        "score": 0.01587301678955555,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1868,
        "score": 0.015625,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1876,
        "score": 0.015384615398943424,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1869,
        "score": 0.01515151560306549,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1847,
        "score": 0.014925372786819935,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1836,
        "score": 0.014705882407724857,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1871,
        "score": 0.014492753893136978,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1845,
        "score": 0.014285714365541935,
        "score_kind": "rrf"
      }
    ]
  }
}
````

### C5 / hybrid_rerank

````json
{
  "eval_id": "C5",
  "strategy": "hybrid_rerank",
  "bucket": "C_colloquial",
  "difficulty": "colloquial",
  "category": null,
  "should_refuse": false,
  "refused": false,
  "status": "completed",
  "stage": "complete",
  "query": "那个邮费到底要给多少钱啊",
  "query_plan": {
    "standard": "那个邮费到底要给多少钱啊",
    "expansions": []
  },
  "mapped_groups": [
    {
      "group_id": "g1",
      "alternatives": [
        [
          1842
        ]
      ]
    }
  ],
  "candidate_ids": [
    1842,
    1877,
    1851,
    1868,
    1876,
    1869,
    1847,
    1836,
    1871,
    1845,
    1843,
    1874,
    1837,
    1870,
    1878,
    1850,
    1875,
    1831,
    1841,
    1879,
    1873,
    1844,
    1840,
    1867,
    1853,
    1865,
    1854,
    1832,
    1848,
    1846,
    1839,
    1855,
    1858,
    1838,
    1857,
    1862,
    1866,
    1835,
    1849,
    1856,
    1863,
    1861,
    1860,
    1833,
    1859,
    1872,
    1834,
    1852,
    1864,
    1880
  ],
  "final_ids": [
    1842,
    1874,
    1876,
    1878,
    1877,
    1869,
    1851,
    1868,
    1837,
    1847
  ],
  "prompt_citations": [
    {
      "n": 1,
      "chunk_id": "1842",
      "section_path": "商品与购物 FAQ/运费怎么算",
      "question": "运费怎么算",
      "answer": "单笔订单满 99 元包邮,未满收取 10 元运费,偏远地区运费另计。邮费即运费,按此规则收取。"
    },
    {
      "n": 3,
      "chunk_id": "1876",
      "section_path": "积分规则/积分怎么攒",
      "question": "积分怎么攒",
      "answer": "已完成订单每实际支付 1 元商品金额累计 1 积分，不计配送费；退款后按对应商品金额同步扣回积分。活动期间的双倍积分属于额外积分奖励，不计入会员等级升级；会员等级仍按有效累计消费金额计算。"
    },
    {
      "n": 5,
      "chunk_id": "1877",
      "section_path": "积分规则/积分怎么用",
      "question": "积分怎么用",
      "answer": "积分可在结算时抵扣商品金额，100 积分抵 1 元现金，单笔订单最多抵 30 元，不用于抵扣偏远地区附加运费，也不支持直接提现。\n\n2000 积分可兑换自动饮水机滤芯 3 片，该兑换套装适用于 MH-W40，普通配送地区包邮；偏远地区附加配送费仍需按页面规则确认。MH-W40 的滤芯更换周期以商品规格手册为准。\n\n800 积分可兑换猫零食小样，普通配送地区另收 6 元运费；该兑换不直接套用普通购物订单的满 99 元包邮规则。兑换商品、可用库存及偏远地区配送规则以兑换页面标注为准。"
    },
    {
      "n": 7,
      "chunk_id": "1851",
      "section_path": "商品与购物 FAQ/会员运费权益",
      "question": "会员运费权益",
      "answer": "金卡会员每月享 3 次免运费权益,银卡会员享 1 次;权益不与偏远地区附加运费冲抵,当月未用完不结转。"
    },
    {
      "n": 9,
      "chunk_id": "1837",
      "section_path": "售后手册/会员专属售后权益",
      "question": "会员专属售后权益",
      "answer": "金卡会员享优先客服接入与上门取件退换货;银卡会员享退换货运费权益 1 次/月。具体权益以会员中心页面标注为准。"
    },
    {
      "n": 10,
      "chunk_id": "1847",
      "section_path": "商品与购物 FAQ/配送范围与偏远地区",
      "question": "配送范围与偏远地区",
      "answer": "全国大部分地区支持配送,新疆、西藏、内蒙古等偏远地区运费另计且时效顺延;港澳台及海外暂不支持自营配送。"
    },
    {
      "n": 8,
      "chunk_id": "1868",
      "section_path": "退货退款政策/换货政策/换货运费",
      "question": "换货运费",
      "answer": "非质量问题的换货,往返运费由买家承担;因质量问题或发错货的换货,往返运费由平台承担。"
    },
    {
      "n": 6,
      "chunk_id": "1869",
      "section_path": "退货退款政策/退换货运费承担",
      "question": "退换货运费承担",
      "answer": "无理由退货的退回运费由买家承担;因商品质量问题、发错货、少发漏发导致的退换货,运费由平台承担。运费承担以平台售后规则最终判定为准。"
    },
    {
      "n": 4,
      "chunk_id": "1878",
      "section_path": "开票细则/可开票类型",
      "question": "可开票类型",
      "answer": "本演示店提供电子普通发票、电子专用发票和纸质专用发票。电子普通发票可按订单申请；电子专票需要企业账户，申请前准备发票抬头及有效纳税人识别号，按申请页面提交资料。\n\n纸质专票仅企业账户可申请，申请时需提供企业开票资料、收件人和邮寄地址，快递费到付。资料审核通过后按开票流程寄出，不承诺快递送达日期。"
    },
    {
      "n": 2,
      "chunk_id": "1874",
      "section_path": "会员权益/会员等级",
      "question": "会员等级",
      "answer": "会员分为普通、银卡和金卡三档，按有效累计消费金额自动升级，不按年度消费金额计算。累计消费未满 1000 元为普通会员，满 1000 元起为银卡，满 5000 元起为金卡。\n\n有效累计消费指已完成订单的商品实际支付金额，不含配送费；退货退款部分从有效累计消费中扣除。退款后根据更新的累计消费重新计算等级，未达到原门槛时可能降级。等级与适用权益在会员中心展示。\n\n银卡在参与会员折扣的商品上享 95 折，金卡享 9 折。折扣适用商品和活动范围以结算页面标注为准。会员折扣、优惠券与满减是否叠加也以当次活动页面为准，不能一概承诺全部优惠同时生效。"
    }
  ],
  "decision": {
    "useful": true,
    "reason": "有运费规则证据",
    "response_kind": "knowledge",
    "source": null
  },
  "answer": "您好！根据运费规则[1]：\n\n- 单笔订单满 99 元：包邮\n- 单笔订单未满 99 元：收取 10 元运费\n- 偏远地区（如新疆、西藏、内蒙古等）运费另计[10]\n\n如果您想确认具体订单的运费，可以告诉我订单号，我帮您查询～",
  "point_verdicts": [
    {
      "point_id": "p1",
      "covered": true,
      "reason": "回答明确说明满99元包邮、未满收10元，覆盖普通订单运费规则及条件"
    },
    {
      "point_id": "p2",
      "covered": true,
      "reason": "回答提及偏远地区（新疆、西藏、内蒙古等）运费另计，覆盖该要点"
    }
  ],
  "claim_verdicts": [
    {
      "claim": "单笔订单满99元包邮",
      "supported": true,
      "reason": "证据[1]明确说明单笔订单满99元包邮"
    },
    {
      "claim": "单笔订单未满99元收取10元运费",
      "supported": true,
      "reason": "证据[1]明确未满99元收取10元运费"
    },
    {
      "claim": "偏远地区（如新疆、西藏、内蒙古等）运费另计",
      "supported": true,
      "reason": "证据[1]说明偏远地区运费另计，证据[10]列出新疆、西藏、内蒙古等属偏远地区且运费另计"
    }
  ],
  "metrics": {
    "recall_at_5": 1.0,
    "recall_at_10": 1.0,
    "mrr_at_10": 1.0,
    "all_groups_hit_at_5": 1.0,
    "all_groups_hit_at_10": 1.0,
    "candidate_group_coverage": 1.0,
    "prompt_group_coverage": 1.0,
    "answer_point_coverage": 1.0,
    "faithfulness": 1.0,
    "absent_refusal_rate": null,
    "answerable_false_refusal_rate": 0.0
  },
  "error": null,
  "elapsed_ms": 10641.141300089657,
  "judge_snapshot": {
    "prompt_version": "joint-generation-v2.1",
    "finish_reason": "stop"
  },
  "audit": {
    "audit_version": 1,
    "source_map_id": "d2dd350d860b8141e52306cbbcafb22f97d091194eb1cdc839a528c2990715eb",
    "gold_groups": [
      {
        "group_id": "g1",
        "alternatives": [
          [
            "product-faq.md:005:a378cfa07513ed7b747b8870ef187c00e9e1ce815a4bac7cfd9bfda4c9e43805"
          ]
        ]
      }
    ],
    "answer_points": [
      {
        "point_id": "p1",
        "text": "普通地区订单满 99 元包邮，未满收 10 元",
        "condition": "普通订单基础运费；偏远地区另计",
        "aliases": []
      },
      {
        "point_id": "p2",
        "text": "偏远地区运费另计",
        "condition": "普通订单基础运费；偏远地区另计",
        "aliases": []
      }
    ],
    "candidate_ranking": [
      {
        "chunk_id": 1842,
        "score": 0.032786883413791656,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1877,
        "score": 0.016129031777381897,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1851,
        "score": 0.01587301678955555,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1868,
        "score": 0.015625,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1876,
        "score": 0.015384615398943424,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1869,
        "score": 0.01515151560306549,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1847,
        "score": 0.014925372786819935,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1836,
        "score": 0.014705882407724857,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1871,
        "score": 0.014492753893136978,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1845,
        "score": 0.014285714365541935,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1843,
        "score": 0.014084506779909134,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1874,
        "score": 0.013888888992369175,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1837,
        "score": 0.013698630034923553,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1870,
        "score": 0.013513513840734959,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1878,
        "score": 0.013333333656191826,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1850,
        "score": 0.01315789483487606,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1875,
        "score": 0.012987012974917889,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1831,
        "score": 0.012820512987673283,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1841,
        "score": 0.012658228166401386,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1879,
        "score": 0.012500000186264515,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1873,
        "score": 0.012345679104328156,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1844,
        "score": 0.012195121496915817,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1840,
        "score": 0.012048192322254181,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1867,
        "score": 0.011904762126505375,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1853,
        "score": 0.0117647061124444,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1865,
        "score": 0.011627906933426857,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1854,
        "score": 0.01149425283074379,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1832,
        "score": 0.011363636702299118,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1848,
        "score": 0.01123595517128706,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1846,
        "score": 0.011111111380159855,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1839,
        "score": 0.010989011265337467,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1855,
        "score": 0.010869565419852734,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1858,
        "score": 0.01075268816202879,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1838,
        "score": 0.010638297535479069,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1857,
        "score": 0.010526316240429878,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1862,
        "score": 0.010416666977107525,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1866,
        "score": 0.010309278033673763,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1835,
        "score": 0.010204081423580647,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1849,
        "score": 0.010101010091602802,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1856,
        "score": 0.009999999776482582,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1863,
        "score": 0.009900989942252636,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1861,
        "score": 0.009803921915590763,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1860,
        "score": 0.009708737954497337,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1833,
        "score": 0.009615384973585606,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1859,
        "score": 0.009523809887468815,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1872,
        "score": 0.009433962404727936,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1834,
        "score": 0.009345794096589088,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1852,
        "score": 0.009259259328246117,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1864,
        "score": 0.00917431153357029,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1880,
        "score": 0.00909090880304575,
        "score_kind": "rrf"
      }
    ],
    "final_ranking": [
      {
        "chunk_id": 1842,
        "score": 0.41983529925346375,
        "score_kind": "rerank"
      },
      {
        "chunk_id": 1874,
        "score": 0.0025972246658056974,
        "score_kind": "rerank"
      },
      {
        "chunk_id": 1876,
        "score": 0.0022953518200665712,
        "score_kind": "rerank"
      },
      {
        "chunk_id": 1878,
        "score": 0.0021258187480270863,
        "score_kind": "rerank"
      },
      {
        "chunk_id": 1877,
        "score": 0.0021134696435183287,
        "score_kind": "rerank"
      },
      {
        "chunk_id": 1869,
        "score": 0.0017125793965533376,
        "score_kind": "rerank"
      },
      {
        "chunk_id": 1851,
        "score": 0.001685375813394785,
        "score_kind": "rerank"
      },
      {
        "chunk_id": 1868,
        "score": 0.0009891499066725373,
        "score_kind": "rerank"
      },
      {
        "chunk_id": 1837,
        "score": 0.0008439415832981467,
        "score_kind": "rerank"
      },
      {
        "chunk_id": 1847,
        "score": 0.0006853169179521501,
        "score_kind": "rerank"
      }
    ]
  }
}
````

### C35 / dense

````json
{
  "eval_id": "C35",
  "strategy": "dense",
  "bucket": "C_colloquial",
  "difficulty": "colloquial",
  "category": null,
  "should_refuse": false,
  "refused": false,
  "status": "completed",
  "stage": "complete",
  "query": "喂食那玩意儿老堵着不下粮咋办",
  "query_plan": {
    "standard": "喂食那玩意儿老堵着不下粮咋办",
    "expansions": []
  },
  "mapped_groups": [
    {
      "group_id": "g1",
      "alternatives": [
        [
          1834
        ]
      ]
    }
  ],
  "candidate_ids": [
    1834,
    1862,
    1863,
    1860,
    1833,
    1853,
    1861,
    1849,
    1855,
    1836,
    1831,
    1877,
    1871,
    1844,
    1847,
    1872,
    1875,
    1858,
    1854,
    1859,
    1835,
    1857,
    1856,
    1880,
    1876,
    1879,
    1840,
    1873,
    1867,
    1850,
    1846,
    1848,
    1839,
    1868,
    1841,
    1845,
    1852,
    1851,
    1837,
    1838,
    1865,
    1870,
    1878,
    1843,
    1866,
    1864,
    1869,
    1842,
    1874,
    1832
  ],
  "final_ids": [
    1834,
    1862,
    1863,
    1860,
    1833,
    1853,
    1861,
    1849,
    1855,
    1836
  ],
  "prompt_citations": [
    {
      "n": 1,
      "chunk_id": "1834",
      "section_path": "售后手册/常见故障自查",
      "question": "常见故障自查",
      "answer": "- 饮水机不出水:检查水位是否低于最低线、水泵是否卡阻,断电清洗水泵后重试。\n- 猫砂盆报错:清空废砂盒并检查滚筒是否卡砂,重启设备;仍报错联系售后。\n- 喂食器卡粮:检查粮食颗粒直径是否超 12mm、粮桶是否受潮结块,清理出粮口后重试。\n- 摄像头离线:确认 Wi-Fi 为 2.4G 频段、信号良好,重启设备或在 App 内重新配网。"
    },
    {
      "n": 3,
      "chunk_id": "1863",
      "section_path": "商品规格手册/自动喂食器 摄像头版(型号 MH-FD30)",
      "question": "自动喂食器 摄像头版(型号 MH-FD30)",
      "answer": "- 型号:MH-FD30\n- 粮桶容量:6L\n- 核心功能:1080P 摄像头、双向语音、App 远程手动投喂与定时投喂\n- 供电:市电供电 + 内置应急电池\n- 说明:摄像头版支持视频回看,需连接 2.4G Wi-Fi"
    },
    {
      "n": 5,
      "chunk_id": "1833",
      "section_path": "售后手册/设备安装与激活",
      "question": "设备安装与激活",
      "answer": "智能设备首次使用需下载「喵喵优选」App,按说明书扫码添加设备并连接 2.4G Wi-Fi 完成激活;猫爬架等非联网商品按随附图解自行组装。"
    },
    {
      "n": 7,
      "chunk_id": "1861",
      "section_path": "商品规格手册/大号三档加热垫(型号 MH-HP20)",
      "question": "大号三档加热垫(型号 MH-HP20)",
      "answer": "- 型号:MH-HP20\n- 尺寸:60cm × 45cm\n- 温控:三档可调 30℃ / 38℃ / 45℃,内置过热保护与定时关机\n- 防护:防水防抓咬电线套管,表面绒布可拆洗\n- 适用:大型猫、多猫窝及冬季保暖"
    },
    {
      "n": 9,
      "chunk_id": "1855",
      "section_path": "商品规格手册/智能猫砂盆 Max(型号 MH-LP200)",
      "question": "智能猫砂盆 Max(型号 MH-LP200)",
      "answer": "- 型号:MH-LP200\n- 适用猫咪体重:2kg 至 12kg,适合大型猫与多猫家庭\n- 猫砂容量:12L,废砂盒容量约 10 天(单猫)\n- 核心功能:超大滚筒、双重称重防夹、活性炭除臭、App 多猫健康档案\n- 供电:220V 市电\n- 清理提示:多猫家庭建议每 3 至 5 天倾倒一次废砂盒"
    },
    {
      "n": 10,
      "chunk_id": "1836",
      "section_path": "售后手册/维修寄修流程",
      "question": "维修寄修流程",
      "answer": "保修期内设备故障,联系客服登记后按指引将设备寄回指定维修点,核验后免费维修并寄回;超保或人为损坏维修可能收取工本费,费用会提前告知。"
    },
    {
      "n": 8,
      "chunk_id": "1849",
      "section_path": "商品与购物 FAQ/商品缺货多久补货",
      "question": "商品缺货多久补货",
      "answer": "现货售罄的商品通常 3 至 7 天内补货,可在商品页点击「到货通知」,补货后系统会推送提醒。"
    },
    {
      "n": 6,
      "chunk_id": "1853",
      "section_path": "商品规格手册/智能猫砂盆 Pro(型号 MH-LP100)",
      "question": "智能猫砂盆 Pro(型号 MH-LP100)",
      "answer": "- 型号:MH-LP100\n- 适用猫咪体重:1.5kg 至 8kg\n- 猫砂容量:9L,废砂盒容量约 7 天(单猫)\n- 核心功能:自动感应清理、活性炭除臭、App 远程监控与健康记录\n- 供电:220V 市电,断电后配置自动保存\n- 清理提示:废砂盒满时 App 推送提醒,建议每 5 至 7 天倾倒一次"
    },
    {
      "n": 4,
      "chunk_id": "1860",
      "section_path": "商品规格手册/恒温加热垫(型号 MH-HP12)",
      "question": "恒温加热垫(型号 MH-HP12)",
      "answer": "- 型号:MH-HP12\n- 尺寸:40cm × 30cm\n- 温控:恒温 38℃,内置过热保护,连续通电不超过 12 小时为宜\n- 防护:防水防抓咬电线套管\n- 适用:幼猫、老年猫及冬季保暖"
    },
    {
      "n": 2,
      "chunk_id": "1862",
      "section_path": "商品规格手册/自动喂食器 基础版(型号 MH-FD10)",
      "question": "自动喂食器 基础版(型号 MH-FD10)",
      "answer": "- 型号:MH-FD10\n- 粮桶容量:4L\n- 核心功能:定时定量投喂,每日最多 6 餐,语音呼唤进食\n- 供电:市电供电 + 4 节 5 号电池断电应急\n- 说明:基础版不含摄像头与 App 远程投喂"
    }
  ],
  "decision": {
    "useful": true,
    "reason": "卡粮故障自查已有直接证据",
    "response_kind": "knowledge",
    "source": null
  },
  "answer": "您好！关于喂食器卡粮不下粮，可按以下方法自查 [1]：\n\n1. 检查粮食颗粒直径是否超过 12mm，过大颗粒容易卡住出粮口；\n2. 检查粮桶内粮食是否受潮结块；\n3. 清理出粮口后重试。\n\n如果按上述步骤处理后仍然卡粮，建议联系客服进一步处理。请问还有什么可以帮您的吗？",
  "point_verdicts": [
    {
      "point_id": "p1",
      "covered": true,
      "reason": "回答完整覆盖检查颗粒直径是否超12mm、粮桶受潮结块、清理出粮口后重试三个要点，且未保证根因修复，符合排查类条件。"
    }
  ],
  "claim_verdicts": [
    {
      "claim": "喂食器卡粮时应检查粮食颗粒直径是否超过12mm，过大颗粒容易卡住出粮口",
      "supported": true,
      "reason": "证据[1]喂食器卡粮条目明确写明检查粮食颗粒直径是否超12mm，支持该排查建议。"
    },
    {
      "claim": "喂食器卡粮时应检查粮桶内粮食是否受潮结块",
      "supported": true,
      "reason": "证据[1]喂食器卡粮条目包含检查粮桶是否受潮结块的排查步骤。"
    },
    {
      "claim": "清理出粮口后重试可解决卡粮情况",
      "supported": true,
      "reason": "证据[1]明确给出清理出粮口后重试的自查步骤。"
    },
    {
      "claim": "按步骤处理后仍卡粮建议联系客服进一步处理",
      "supported": true,
      "reason": "证据[1]其他故障条目显示处理后仍异常联系售后，同类喂食器排查逻辑一致，且回答仅作建议表述，与证据的自查框架相符。"
    }
  ],
  "metrics": {
    "recall_at_5": 1.0,
    "recall_at_10": 1.0,
    "mrr_at_10": 1.0,
    "all_groups_hit_at_5": 1.0,
    "all_groups_hit_at_10": 1.0,
    "candidate_group_coverage": 1.0,
    "prompt_group_coverage": 1.0,
    "answer_point_coverage": 1.0,
    "faithfulness": 1.0,
    "absent_refusal_rate": null,
    "answerable_false_refusal_rate": 0.0
  },
  "error": null,
  "elapsed_ms": 9920.245799934492,
  "judge_snapshot": {
    "prompt_version": "joint-generation-v2.1",
    "finish_reason": "stop"
  },
  "audit": {
    "audit_version": 1,
    "source_map_id": "d2dd350d860b8141e52306cbbcafb22f97d091194eb1cdc839a528c2990715eb",
    "gold_groups": [
      {
        "group_id": "g1",
        "alternatives": [
          [
            "after-sales-manual.md:004:e6c60fd9c73733a64750b8c14a2181e06fd5d21821e61bd6c8f3a23f12876244"
          ]
        ]
      }
    ],
    "answer_points": [
      {
        "point_id": "p1",
        "text": "检查颗粒是否超 12mm、粮桶受潮结块，清理出粮口后重试",
        "condition": "按对应设备故障类型排查，不保证根因或自行修复",
        "aliases": []
      }
    ],
    "candidate_ranking": [
      {
        "chunk_id": 1834,
        "score": 0.5772529244422913,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1862,
        "score": 0.5685988068580627,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1863,
        "score": 0.5516100525856018,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1860,
        "score": 0.4419667422771454,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1833,
        "score": 0.4325045645236969,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1853,
        "score": 0.4301389753818512,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1861,
        "score": 0.4249976575374603,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1849,
        "score": 0.42119717597961426,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1855,
        "score": 0.42034223675727844,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1836,
        "score": 0.4171714782714844,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1831,
        "score": 0.41137444972991943,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1877,
        "score": 0.40876007080078125,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1871,
        "score": 0.4044782221317291,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1844,
        "score": 0.40205860137939453,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1847,
        "score": 0.4005569815635681,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1872,
        "score": 0.39917227625846863,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1875,
        "score": 0.3987771272659302,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1858,
        "score": 0.3984760642051697,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1854,
        "score": 0.39638108015060425,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1859,
        "score": 0.39340728521347046,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1835,
        "score": 0.39167726039886475,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1857,
        "score": 0.3915807008743286,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1856,
        "score": 0.39115414023399353,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1880,
        "score": 0.39097651839256287,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1876,
        "score": 0.39064010977745056,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1879,
        "score": 0.38086429238319397,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1840,
        "score": 0.3758910298347473,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1873,
        "score": 0.37508946657180786,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1867,
        "score": 0.3739817142486572,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1850,
        "score": 0.37022215127944946,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1846,
        "score": 0.3654598295688629,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1848,
        "score": 0.36215317249298096,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1839,
        "score": 0.3583248555660248,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1868,
        "score": 0.35787448287010193,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1841,
        "score": 0.3557622730731964,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1845,
        "score": 0.3545067012310028,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1852,
        "score": 0.35270148515701294,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1851,
        "score": 0.35104477405548096,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1837,
        "score": 0.34910643100738525,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1838,
        "score": 0.3463031053543091,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1865,
        "score": 0.3458736836910248,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1870,
        "score": 0.3453841805458069,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1878,
        "score": 0.3429238200187683,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1843,
        "score": 0.3407789468765259,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1866,
        "score": 0.3372115194797516,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1864,
        "score": 0.3327294886112213,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1869,
        "score": 0.3229714035987854,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1842,
        "score": 0.3220908045768738,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1874,
        "score": 0.3202211856842041,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1832,
        "score": 0.31455177068710327,
        "score_kind": "cosine"
      }
    ],
    "final_ranking": [
      {
        "chunk_id": 1834,
        "score": 0.5772529244422913,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1862,
        "score": 0.5685988068580627,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1863,
        "score": 0.5516100525856018,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1860,
        "score": 0.4419667422771454,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1833,
        "score": 0.4325045645236969,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1853,
        "score": 0.4301389753818512,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1861,
        "score": 0.4249976575374603,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1849,
        "score": 0.42119717597961426,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1855,
        "score": 0.42034223675727844,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1836,
        "score": 0.4171714782714844,
        "score_kind": "cosine"
      }
    ]
  }
}
````

### C35 / bm25

````json
{
  "eval_id": "C35",
  "strategy": "bm25",
  "bucket": "C_colloquial",
  "difficulty": "colloquial",
  "category": null,
  "should_refuse": false,
  "refused": false,
  "status": "completed",
  "stage": "complete",
  "query": "喂食那玩意儿老堵着不下粮咋办",
  "query_plan": {
    "standard": "喂食那玩意儿老堵着不下粮咋办",
    "expansions": []
  },
  "mapped_groups": [
    {
      "group_id": "g1",
      "alternatives": [
        [
          1834
        ]
      ]
    }
  ],
  "candidate_ids": [
    1862,
    1863,
    1834
  ],
  "final_ids": [
    1862,
    1863,
    1834
  ],
  "prompt_citations": [
    {
      "n": 1,
      "chunk_id": "1862",
      "section_path": "商品规格手册/自动喂食器 基础版(型号 MH-FD10)",
      "question": "自动喂食器 基础版(型号 MH-FD10)",
      "answer": "- 型号:MH-FD10\n- 粮桶容量:4L\n- 核心功能:定时定量投喂,每日最多 6 餐,语音呼唤进食\n- 供电:市电供电 + 4 节 5 号电池断电应急\n- 说明:基础版不含摄像头与 App 远程投喂"
    },
    {
      "n": 3,
      "chunk_id": "1834",
      "section_path": "售后手册/常见故障自查",
      "question": "常见故障自查",
      "answer": "- 饮水机不出水:检查水位是否低于最低线、水泵是否卡阻,断电清洗水泵后重试。\n- 猫砂盆报错:清空废砂盒并检查滚筒是否卡砂,重启设备;仍报错联系售后。\n- 喂食器卡粮:检查粮食颗粒直径是否超 12mm、粮桶是否受潮结块,清理出粮口后重试。\n- 摄像头离线:确认 Wi-Fi 为 2.4G 频段、信号良好,重启设备或在 App 内重新配网。"
    },
    {
      "n": 2,
      "chunk_id": "1863",
      "section_path": "商品规格手册/自动喂食器 摄像头版(型号 MH-FD30)",
      "question": "自动喂食器 摄像头版(型号 MH-FD30)",
      "answer": "- 型号:MH-FD30\n- 粮桶容量:6L\n- 核心功能:1080P 摄像头、双向语音、App 远程手动投喂与定时投喂\n- 供电:市电供电 + 内置应急电池\n- 说明:摄像头版支持视频回看,需连接 2.4G Wi-Fi"
    }
  ],
  "decision": {
    "useful": true,
    "reason": "故障自查含喂食器卡粮处理",
    "response_kind": "knowledge",
    "source": null
  },
  "answer": "您好！关于喂食器卡粮不下粮的问题，建议您先按以下方法自查 [3]：\n\n1. 检查粮食颗粒直径是否超过 12mm，颗粒过大容易卡粮 [3]\n2. 检查粮桶内粮食是否受潮结块，如有结块请更换干燥的粮食 [3]\n3. 清理出粮口后再重试 [3]\n\n如果按上述方法处理后仍然卡粮，建议联系售后进一步处理 [3]。\n\n请问您使用的是哪款喂食器（如基础版 MH-FD10 或摄像头版 MH-FD30）？如果自查后仍无法解决，我可以为您创建人工工单转售后处理。",
  "point_verdicts": [
    {
      "point_id": "p1",
      "covered": true,
      "reason": "回答完整覆盖检查颗粒直径超12mm、粮桶受潮结块、清理出粮口后重试，且以自查建议形式呈现并建议联系售后，未承诺根因或修复，符合条件"
    }
  ],
  "claim_verdicts": [
    {
      "claim": "喂食器卡粮时可检查粮食颗粒直径是否超过12mm，颗粒过大容易卡粮",
      "supported": true,
      "reason": "证据3明确写明喂食器卡粮需检查颗粒直径是否超12mm"
    },
    {
      "claim": "粮桶内粮食可能受潮结块导致卡粮，如有结块应更换干燥粮食",
      "supported": true,
      "reason": "证据3提到检查粮桶是否受潮结块，更换干燥粮食为合理排查建议"
    },
    {
      "claim": "清理出粮口后重试可处理卡粮问题",
      "supported": true,
      "reason": "证据3明确写明清理出粮口后重试"
    },
    {
      "claim": "按上述方法处理后仍卡粮建议联系售后处理",
      "supported": true,
      "reason": "证据3该故障排查条目以仍报错联系售后的同类模式处理，售后建议与排查流程一致"
    }
  ],
  "metrics": {
    "recall_at_5": 1.0,
    "recall_at_10": 1.0,
    "mrr_at_10": 0.3333333333333333,
    "all_groups_hit_at_5": 1.0,
    "all_groups_hit_at_10": 1.0,
    "candidate_group_coverage": 1.0,
    "prompt_group_coverage": 1.0,
    "answer_point_coverage": 1.0,
    "faithfulness": 1.0,
    "absent_refusal_rate": null,
    "answerable_false_refusal_rate": 0.0
  },
  "error": null,
  "elapsed_ms": 10941.837900085375,
  "judge_snapshot": {
    "prompt_version": "joint-generation-v2.1",
    "finish_reason": "stop"
  },
  "audit": {
    "audit_version": 1,
    "source_map_id": "d2dd350d860b8141e52306cbbcafb22f97d091194eb1cdc839a528c2990715eb",
    "gold_groups": [
      {
        "group_id": "g1",
        "alternatives": [
          [
            "after-sales-manual.md:004:e6c60fd9c73733a64750b8c14a2181e06fd5d21821e61bd6c8f3a23f12876244"
          ]
        ]
      }
    ],
    "answer_points": [
      {
        "point_id": "p1",
        "text": "检查颗粒是否超 12mm、粮桶受潮结块，清理出粮口后重试",
        "condition": "按对应设备故障类型排查，不保证根因或自行修复",
        "aliases": []
      }
    ],
    "candidate_ranking": [
      {
        "chunk_id": 1862,
        "score": 2.582362174987793,
        "score_kind": "bm25"
      },
      {
        "chunk_id": 1863,
        "score": 2.525158166885376,
        "score_kind": "bm25"
      },
      {
        "chunk_id": 1834,
        "score": 2.158566951751709,
        "score_kind": "bm25"
      }
    ],
    "final_ranking": [
      {
        "chunk_id": 1862,
        "score": 2.582362174987793,
        "score_kind": "bm25"
      },
      {
        "chunk_id": 1863,
        "score": 2.525158166885376,
        "score_kind": "bm25"
      },
      {
        "chunk_id": 1834,
        "score": 2.158566951751709,
        "score_kind": "bm25"
      }
    ]
  }
}
````

### C35 / hybrid

````json
{
  "eval_id": "C35",
  "strategy": "hybrid",
  "bucket": "C_colloquial",
  "difficulty": "colloquial",
  "category": null,
  "should_refuse": false,
  "refused": false,
  "status": "completed",
  "stage": "complete",
  "query": "喂食那玩意儿老堵着不下粮咋办",
  "query_plan": {
    "standard": "喂食那玩意儿老堵着不下粮咋办",
    "expansions": []
  },
  "mapped_groups": [
    {
      "group_id": "g1",
      "alternatives": [
        [
          1834
        ]
      ]
    }
  ],
  "candidate_ids": [
    1862,
    1834,
    1863,
    1860,
    1833,
    1853,
    1861,
    1849,
    1855,
    1836,
    1831,
    1877,
    1871,
    1844,
    1847,
    1872,
    1875,
    1858,
    1854,
    1859,
    1835,
    1857,
    1856,
    1880,
    1876,
    1879,
    1840,
    1873,
    1867,
    1850,
    1846,
    1848,
    1839,
    1868,
    1841,
    1845,
    1852,
    1851,
    1837,
    1838,
    1865,
    1870,
    1878,
    1843,
    1866,
    1864,
    1869,
    1842,
    1874,
    1832
  ],
  "final_ids": [
    1862,
    1834,
    1863,
    1860,
    1833,
    1853,
    1861,
    1849,
    1855,
    1836
  ],
  "prompt_citations": [
    {
      "n": 1,
      "chunk_id": "1862",
      "section_path": "商品规格手册/自动喂食器 基础版(型号 MH-FD10)",
      "question": "自动喂食器 基础版(型号 MH-FD10)",
      "answer": "- 型号:MH-FD10\n- 粮桶容量:4L\n- 核心功能:定时定量投喂,每日最多 6 餐,语音呼唤进食\n- 供电:市电供电 + 4 节 5 号电池断电应急\n- 说明:基础版不含摄像头与 App 远程投喂"
    },
    {
      "n": 3,
      "chunk_id": "1863",
      "section_path": "商品规格手册/自动喂食器 摄像头版(型号 MH-FD30)",
      "question": "自动喂食器 摄像头版(型号 MH-FD30)",
      "answer": "- 型号:MH-FD30\n- 粮桶容量:6L\n- 核心功能:1080P 摄像头、双向语音、App 远程手动投喂与定时投喂\n- 供电:市电供电 + 内置应急电池\n- 说明:摄像头版支持视频回看,需连接 2.4G Wi-Fi"
    },
    {
      "n": 5,
      "chunk_id": "1833",
      "section_path": "售后手册/设备安装与激活",
      "question": "设备安装与激活",
      "answer": "智能设备首次使用需下载「喵喵优选」App,按说明书扫码添加设备并连接 2.4G Wi-Fi 完成激活;猫爬架等非联网商品按随附图解自行组装。"
    },
    {
      "n": 7,
      "chunk_id": "1861",
      "section_path": "商品规格手册/大号三档加热垫(型号 MH-HP20)",
      "question": "大号三档加热垫(型号 MH-HP20)",
      "answer": "- 型号:MH-HP20\n- 尺寸:60cm × 45cm\n- 温控:三档可调 30℃ / 38℃ / 45℃,内置过热保护与定时关机\n- 防护:防水防抓咬电线套管,表面绒布可拆洗\n- 适用:大型猫、多猫窝及冬季保暖"
    },
    {
      "n": 9,
      "chunk_id": "1855",
      "section_path": "商品规格手册/智能猫砂盆 Max(型号 MH-LP200)",
      "question": "智能猫砂盆 Max(型号 MH-LP200)",
      "answer": "- 型号:MH-LP200\n- 适用猫咪体重:2kg 至 12kg,适合大型猫与多猫家庭\n- 猫砂容量:12L,废砂盒容量约 10 天(单猫)\n- 核心功能:超大滚筒、双重称重防夹、活性炭除臭、App 多猫健康档案\n- 供电:220V 市电\n- 清理提示:多猫家庭建议每 3 至 5 天倾倒一次废砂盒"
    },
    {
      "n": 10,
      "chunk_id": "1836",
      "section_path": "售后手册/维修寄修流程",
      "question": "维修寄修流程",
      "answer": "保修期内设备故障,联系客服登记后按指引将设备寄回指定维修点,核验后免费维修并寄回;超保或人为损坏维修可能收取工本费,费用会提前告知。"
    },
    {
      "n": 8,
      "chunk_id": "1849",
      "section_path": "商品与购物 FAQ/商品缺货多久补货",
      "question": "商品缺货多久补货",
      "answer": "现货售罄的商品通常 3 至 7 天内补货,可在商品页点击「到货通知」,补货后系统会推送提醒。"
    },
    {
      "n": 6,
      "chunk_id": "1853",
      "section_path": "商品规格手册/智能猫砂盆 Pro(型号 MH-LP100)",
      "question": "智能猫砂盆 Pro(型号 MH-LP100)",
      "answer": "- 型号:MH-LP100\n- 适用猫咪体重:1.5kg 至 8kg\n- 猫砂容量:9L,废砂盒容量约 7 天(单猫)\n- 核心功能:自动感应清理、活性炭除臭、App 远程监控与健康记录\n- 供电:220V 市电,断电后配置自动保存\n- 清理提示:废砂盒满时 App 推送提醒,建议每 5 至 7 天倾倒一次"
    },
    {
      "n": 4,
      "chunk_id": "1860",
      "section_path": "商品规格手册/恒温加热垫(型号 MH-HP12)",
      "question": "恒温加热垫(型号 MH-HP12)",
      "answer": "- 型号:MH-HP12\n- 尺寸:40cm × 30cm\n- 温控:恒温 38℃,内置过热保护,连续通电不超过 12 小时为宜\n- 防护:防水防抓咬电线套管\n- 适用:幼猫、老年猫及冬季保暖"
    },
    {
      "n": 2,
      "chunk_id": "1834",
      "section_path": "售后手册/常见故障自查",
      "question": "常见故障自查",
      "answer": "- 饮水机不出水:检查水位是否低于最低线、水泵是否卡阻,断电清洗水泵后重试。\n- 猫砂盆报错:清空废砂盒并检查滚筒是否卡砂,重启设备;仍报错联系售后。\n- 喂食器卡粮:检查粮食颗粒直径是否超 12mm、粮桶是否受潮结块,清理出粮口后重试。\n- 摄像头离线:确认 Wi-Fi 为 2.4G 频段、信号良好,重启设备或在 App 内重新配网。"
    }
  ],
  "decision": {
    "useful": true,
    "reason": "故障自查含喂食器卡粮处理",
    "response_kind": "knowledge",
    "source": null
  },
  "answer": "您好！关于喂食器卡粮不下粮的问题，可以按以下方法自查[2]：\n\n- 检查粮食颗粒直径是否超过 12mm，过大的颗粒容易卡住[2]\n- 检查粮桶内的粮食是否受潮结块，如有请更换干燥的粮食[2]\n- 清理出粮口后再重试[2]\n\n如果按以上方法处理后仍然卡粮，建议联系售后处理。若设备还在保修期内，可登记后按指引寄回维修点，核验后免费维修[10]。\n\n请问您方便告诉我具体的设备型号吗（如基础版 MH-FD10 或摄像头版 MH-FD30）？这样我可以为您提供更准确的帮助~",
  "point_verdicts": [
    {
      "point_id": "p1",
      "covered": true,
      "reason": "回答涵盖检查颗粒是否超12mm、粮桶受潮结块、清理出粮口后重试，并保留不保证根因的条件（仍卡粮建议联系售后）"
    }
  ],
  "claim_verdicts": [
    {
      "claim": "喂食器卡粮可检查粮食颗粒直径是否超过12mm，过大颗粒容易卡住",
      "supported": true,
      "reason": "证据[2]明确写明喂食器卡粮需检查粮食颗粒直径是否超12mm"
    },
    {
      "claim": "检查粮桶内粮食是否受潮结块，如有应更换干燥粮食",
      "supported": false,
      "reason": "证据[2]提到检查粮桶是否受潮结块，但未提到更换干燥粮食"
    },
    {
      "claim": "清理出粮口后重试可解决卡粮",
      "supported": false,
      "reason": "证据[2]提到清理出粮口后重试，但未保证能解决，回答表述为方法步骤尚可，但清理后重试作为断言依赖证据仅列出步骤，判定支持不足"
    },
    {
      "claim": "仍卡粮建议联系售后处理",
      "supported": true,
      "reason": "证据[2]指出仍报错类故障联系售后，证据[10]支持保修期内登记寄修免费维修"
    },
    {
      "claim": "保修期内可登记后按指引寄回维修点，核验后免费维修",
      "supported": true,
      "reason": "证据[10]明确写明保修期内联系客服登记后寄回指定维修点，核验后免费维修"
    }
  ],
  "metrics": {
    "recall_at_5": 1.0,
    "recall_at_10": 1.0,
    "mrr_at_10": 0.5,
    "all_groups_hit_at_5": 1.0,
    "all_groups_hit_at_10": 1.0,
    "candidate_group_coverage": 1.0,
    "prompt_group_coverage": 1.0,
    "answer_point_coverage": 1.0,
    "faithfulness": 0.6,
    "absent_refusal_rate": null,
    "answerable_false_refusal_rate": 0.0
  },
  "error": null,
  "elapsed_ms": 12792.356899939477,
  "judge_snapshot": {
    "prompt_version": "joint-generation-v2.1",
    "finish_reason": "stop"
  },
  "audit": {
    "audit_version": 1,
    "source_map_id": "d2dd350d860b8141e52306cbbcafb22f97d091194eb1cdc839a528c2990715eb",
    "gold_groups": [
      {
        "group_id": "g1",
        "alternatives": [
          [
            "after-sales-manual.md:004:e6c60fd9c73733a64750b8c14a2181e06fd5d21821e61bd6c8f3a23f12876244"
          ]
        ]
      }
    ],
    "answer_points": [
      {
        "point_id": "p1",
        "text": "检查颗粒是否超 12mm、粮桶受潮结块，清理出粮口后重试",
        "condition": "按对应设备故障类型排查，不保证根因或自行修复",
        "aliases": []
      }
    ],
    "candidate_ranking": [
      {
        "chunk_id": 1862,
        "score": 0.032522473484277725,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1834,
        "score": 0.03226646035909653,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1863,
        "score": 0.0320020467042923,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1860,
        "score": 0.015625,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1833,
        "score": 0.015384615398943424,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1853,
        "score": 0.01515151560306549,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1861,
        "score": 0.014925372786819935,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1849,
        "score": 0.014705882407724857,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1855,
        "score": 0.014492753893136978,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1836,
        "score": 0.014285714365541935,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1831,
        "score": 0.014084506779909134,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1877,
        "score": 0.013888888992369175,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1871,
        "score": 0.013698630034923553,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1844,
        "score": 0.013513513840734959,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1847,
        "score": 0.013333333656191826,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1872,
        "score": 0.01315789483487606,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1875,
        "score": 0.012987012974917889,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1858,
        "score": 0.012820512987673283,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1854,
        "score": 0.012658228166401386,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1859,
        "score": 0.012500000186264515,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1835,
        "score": 0.012345679104328156,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1857,
        "score": 0.012195121496915817,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1856,
        "score": 0.012048192322254181,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1880,
        "score": 0.011904762126505375,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1876,
        "score": 0.0117647061124444,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1879,
        "score": 0.011627906933426857,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1840,
        "score": 0.01149425283074379,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1873,
        "score": 0.011363636702299118,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1867,
        "score": 0.01123595517128706,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1850,
        "score": 0.011111111380159855,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1846,
        "score": 0.010989011265337467,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1848,
        "score": 0.010869565419852734,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1839,
        "score": 0.01075268816202879,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1868,
        "score": 0.010638297535479069,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1841,
        "score": 0.010526316240429878,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1845,
        "score": 0.010416666977107525,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1852,
        "score": 0.010309278033673763,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1851,
        "score": 0.010204081423580647,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1837,
        "score": 0.010101010091602802,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1838,
        "score": 0.009999999776482582,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1865,
        "score": 0.009900989942252636,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1870,
        "score": 0.009803921915590763,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1878,
        "score": 0.009708737954497337,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1843,
        "score": 0.009615384973585606,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1866,
        "score": 0.009523809887468815,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1864,
        "score": 0.009433962404727936,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1869,
        "score": 0.009345794096589088,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1842,
        "score": 0.009259259328246117,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1874,
        "score": 0.00917431153357029,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1832,
        "score": 0.00909090880304575,
        "score_kind": "rrf"
      }
    ],
    "final_ranking": [
      {
        "chunk_id": 1862,
        "score": 0.032522473484277725,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1834,
        "score": 0.03226646035909653,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1863,
        "score": 0.0320020467042923,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1860,
        "score": 0.015625,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1833,
        "score": 0.015384615398943424,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1853,
        "score": 0.01515151560306549,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1861,
        "score": 0.014925372786819935,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1849,
        "score": 0.014705882407724857,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1855,
        "score": 0.014492753893136978,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1836,
        "score": 0.014285714365541935,
        "score_kind": "rrf"
      }
    ]
  }
}
````

### C35 / hybrid_rerank

````json
{
  "eval_id": "C35",
  "strategy": "hybrid_rerank",
  "bucket": "C_colloquial",
  "difficulty": "colloquial",
  "category": null,
  "should_refuse": false,
  "refused": false,
  "status": "completed",
  "stage": "complete",
  "query": "喂食那玩意儿老堵着不下粮咋办",
  "query_plan": {
    "standard": "喂食那玩意儿老堵着不下粮咋办",
    "expansions": []
  },
  "mapped_groups": [
    {
      "group_id": "g1",
      "alternatives": [
        [
          1834
        ]
      ]
    }
  ],
  "candidate_ids": [
    1862,
    1834,
    1863,
    1860,
    1833,
    1853,
    1861,
    1849,
    1855,
    1836,
    1831,
    1877,
    1871,
    1844,
    1847,
    1872,
    1858,
    1875,
    1854,
    1859,
    1835,
    1857,
    1880,
    1856,
    1876,
    1879,
    1840,
    1873,
    1867,
    1850,
    1846,
    1848,
    1839,
    1868,
    1841,
    1845,
    1852,
    1851,
    1837,
    1838,
    1865,
    1870,
    1878,
    1843,
    1866,
    1864,
    1869,
    1842,
    1874,
    1832
  ],
  "final_ids": [
    1834,
    1862,
    1863,
    1853,
    1855,
    1836,
    1854,
    1833,
    1880,
    1875
  ],
  "prompt_citations": [
    {
      "n": 1,
      "chunk_id": "1834",
      "section_path": "售后手册/常见故障自查",
      "question": "常见故障自查",
      "answer": "- 饮水机不出水:检查水位是否低于最低线、水泵是否卡阻,断电清洗水泵后重试。\n- 猫砂盆报错:清空废砂盒并检查滚筒是否卡砂,重启设备;仍报错联系售后。\n- 喂食器卡粮:检查粮食颗粒直径是否超 12mm、粮桶是否受潮结块,清理出粮口后重试。\n- 摄像头离线:确认 Wi-Fi 为 2.4G 频段、信号良好,重启设备或在 App 内重新配网。"
    },
    {
      "n": 3,
      "chunk_id": "1863",
      "section_path": "商品规格手册/自动喂食器 摄像头版(型号 MH-FD30)",
      "question": "自动喂食器 摄像头版(型号 MH-FD30)",
      "answer": "- 型号:MH-FD30\n- 粮桶容量:6L\n- 核心功能:1080P 摄像头、双向语音、App 远程手动投喂与定时投喂\n- 供电:市电供电 + 内置应急电池\n- 说明:摄像头版支持视频回看,需连接 2.4G Wi-Fi"
    },
    {
      "n": 5,
      "chunk_id": "1855",
      "section_path": "商品规格手册/智能猫砂盆 Max(型号 MH-LP200)",
      "question": "智能猫砂盆 Max(型号 MH-LP200)",
      "answer": "- 型号:MH-LP200\n- 适用猫咪体重:2kg 至 12kg,适合大型猫与多猫家庭\n- 猫砂容量:12L,废砂盒容量约 10 天(单猫)\n- 核心功能:超大滚筒、双重称重防夹、活性炭除臭、App 多猫健康档案\n- 供电:220V 市电\n- 清理提示:多猫家庭建议每 3 至 5 天倾倒一次废砂盒"
    },
    {
      "n": 7,
      "chunk_id": "1854",
      "section_path": "商品规格手册/智能猫砂盆 Lite(型号 MH-LP50)",
      "question": "智能猫砂盆 Lite(型号 MH-LP50)",
      "answer": "- 型号:MH-LP50\n- 适用猫咪体重:1.5kg 至 6kg\n- 猫砂容量:6L\n- 核心功能:自动感应清理、物理除臭盖板;不含 App 联网功能\n- 与 Pro 差异:Lite 无 App 远程监控与健康记录,价格更低,适合单猫家庭"
    },
    {
      "n": 9,
      "chunk_id": "1880",
      "section_path": "猫窝清洗说明/猫窝是否可以机洗",
      "question": "猫窝是否可以机洗",
      "answer": "普通布艺猫窝清洗前拆掉内部垫芯，外套放入洗衣袋，使用轻柔模式冷水洗，自然晾干。不可直接将整只猫窝连垫芯一起机洗，商品另有清洗标签时优先遵循标签。\n\n带加热模块的猫窝不可机洗，应先断电，并按说明书局部擦洗；不得将加热模块、电源或线路浸水。未按清洗说明操作导致的损坏不直接认定为商品质量问题，需要客服核验。\n\n退货仍需符合商品完好、不影响二次销售等适用条件。售后手册中的电子类商品 12 个月保修不能直接套用到普通布艺猫窝；本清洗说明未给出布艺猫窝的独立保修期限。"
    },
    {
      "n": 10,
      "chunk_id": "1875",
      "section_path": "会员权益/生日礼",
      "question": "生日礼",
      "answer": "银卡会员生日当月可领取一份猫零食小样，金卡会员生日当月可领取一份猫罐头礼盒。需在会员中心领取，礼品规格与领取期限以页面标注为准，不承诺额外折现或补偿。"
    },
    {
      "n": 8,
      "chunk_id": "1833",
      "section_path": "售后手册/设备安装与激活",
      "question": "设备安装与激活",
      "answer": "智能设备首次使用需下载「喵喵优选」App,按说明书扫码添加设备并连接 2.4G Wi-Fi 完成激活;猫爬架等非联网商品按随附图解自行组装。"
    },
    {
      "n": 6,
      "chunk_id": "1836",
      "section_path": "售后手册/维修寄修流程",
      "question": "维修寄修流程",
      "answer": "保修期内设备故障,联系客服登记后按指引将设备寄回指定维修点,核验后免费维修并寄回;超保或人为损坏维修可能收取工本费,费用会提前告知。"
    },
    {
      "n": 4,
      "chunk_id": "1853",
      "section_path": "商品规格手册/智能猫砂盆 Pro(型号 MH-LP100)",
      "question": "智能猫砂盆 Pro(型号 MH-LP100)",
      "answer": "- 型号:MH-LP100\n- 适用猫咪体重:1.5kg 至 8kg\n- 猫砂容量:9L,废砂盒容量约 7 天(单猫)\n- 核心功能:自动感应清理、活性炭除臭、App 远程监控与健康记录\n- 供电:220V 市电,断电后配置自动保存\n- 清理提示:废砂盒满时 App 推送提醒,建议每 5 至 7 天倾倒一次"
    },
    {
      "n": 2,
      "chunk_id": "1862",
      "section_path": "商品规格手册/自动喂食器 基础版(型号 MH-FD10)",
      "question": "自动喂食器 基础版(型号 MH-FD10)",
      "answer": "- 型号:MH-FD10\n- 粮桶容量:4L\n- 核心功能:定时定量投喂,每日最多 6 餐,语音呼唤进食\n- 供电:市电供电 + 4 节 5 号电池断电应急\n- 说明:基础版不含摄像头与 App 远程投喂"
    }
  ],
  "decision": {
    "useful": true,
    "reason": "故障自查含喂食器卡粮处理方法",
    "response_kind": "knowledge",
    "source": null
  },
  "answer": "您好！喂食器卡粮不下粮，可以先按以下方法自查[1]：\n\n1. 检查粮食颗粒直径是否超过 12mm，过大易卡粮[1]；\n2. 查看粮桶里的粮食是否受潮结块，如有请更换干燥的粮食[1]；\n3. 清理出粮口后重新试机[1]。\n\n如果以上操作后仍然卡粮，建议联系售后进一步处理[1]。请问这样能帮到您吗？",
  "point_verdicts": [
    {
      "point_id": "p1",
      "covered": true,
      "reason": "回答覆盖颗粒超12mm、粮桶受潮结块、清理出粮口后重试三项排查，并保持联系售后的条件性表述，未承诺根因或自行修复"
    }
  ],
  "claim_verdicts": [
    {
      "claim": "粮食颗粒直径超过12mm易导致喂食器卡粮",
      "supported": true,
      "reason": "证据1明确：喂食器卡粮需检查颗粒直径是否超12mm"
    },
    {
      "claim": "粮桶里的粮食受潮结块会导致卡粮，如有应更换干燥粮食",
      "supported": true,
      "reason": "证据1指出粮桶受潮结块需检查，更换干燥粮食为合理建议，属同一排查步骤"
    },
    {
      "claim": "清理出粮口后重新试机可排查卡粮",
      "supported": true,
      "reason": "证据1明确：清理出粮口后重试"
    },
    {
      "claim": "按上述方法仍卡粮时建议联系售后进一步处理",
      "supported": true,
      "reason": "证据1同类故障条目（猫砂盆）含仍报错联系售后，且该建议为流程性表述；可视为由证据1的自查场景支持"
    }
  ],
  "metrics": {
    "recall_at_5": 1.0,
    "recall_at_10": 1.0,
    "mrr_at_10": 1.0,
    "all_groups_hit_at_5": 1.0,
    "all_groups_hit_at_10": 1.0,
    "candidate_group_coverage": 1.0,
    "prompt_group_coverage": 1.0,
    "answer_point_coverage": 1.0,
    "faithfulness": 1.0,
    "absent_refusal_rate": null,
    "answerable_false_refusal_rate": 0.0
  },
  "error": null,
  "elapsed_ms": 11008.22430010885,
  "judge_snapshot": {
    "prompt_version": "joint-generation-v2.1",
    "finish_reason": "stop"
  },
  "audit": {
    "audit_version": 1,
    "source_map_id": "d2dd350d860b8141e52306cbbcafb22f97d091194eb1cdc839a528c2990715eb",
    "gold_groups": [
      {
        "group_id": "g1",
        "alternatives": [
          [
            "after-sales-manual.md:004:e6c60fd9c73733a64750b8c14a2181e06fd5d21821e61bd6c8f3a23f12876244"
          ]
        ]
      }
    ],
    "answer_points": [
      {
        "point_id": "p1",
        "text": "检查颗粒是否超 12mm、粮桶受潮结块，清理出粮口后重试",
        "condition": "按对应设备故障类型排查，不保证根因或自行修复",
        "aliases": []
      }
    ],
    "candidate_ranking": [
      {
        "chunk_id": 1862,
        "score": 0.032522473484277725,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1834,
        "score": 0.03226646035909653,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1863,
        "score": 0.0320020467042923,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1860,
        "score": 0.015625,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1833,
        "score": 0.015384615398943424,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1853,
        "score": 0.01515151560306549,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1861,
        "score": 0.014925372786819935,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1849,
        "score": 0.014705882407724857,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1855,
        "score": 0.014492753893136978,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1836,
        "score": 0.014285714365541935,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1831,
        "score": 0.014084506779909134,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1877,
        "score": 0.013888888992369175,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1871,
        "score": 0.013698630034923553,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1844,
        "score": 0.013513513840734959,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1847,
        "score": 0.013333333656191826,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1872,
        "score": 0.01315789483487606,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1858,
        "score": 0.012987012974917889,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1875,
        "score": 0.012820512987673283,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1854,
        "score": 0.012658228166401386,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1859,
        "score": 0.012500000186264515,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1835,
        "score": 0.012345679104328156,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1857,
        "score": 0.012195121496915817,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1880,
        "score": 0.012048192322254181,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1856,
        "score": 0.011904762126505375,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1876,
        "score": 0.0117647061124444,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1879,
        "score": 0.011627906933426857,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1840,
        "score": 0.01149425283074379,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1873,
        "score": 0.011363636702299118,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1867,
        "score": 0.01123595517128706,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1850,
        "score": 0.011111111380159855,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1846,
        "score": 0.010989011265337467,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1848,
        "score": 0.010869565419852734,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1839,
        "score": 0.01075268816202879,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1868,
        "score": 0.010638297535479069,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1841,
        "score": 0.010526316240429878,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1845,
        "score": 0.010416666977107525,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1852,
        "score": 0.010309278033673763,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1851,
        "score": 0.010204081423580647,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1837,
        "score": 0.010101010091602802,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1838,
        "score": 0.009999999776482582,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1865,
        "score": 0.009900989942252636,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1870,
        "score": 0.009803921915590763,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1878,
        "score": 0.009708737954497337,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1843,
        "score": 0.009615384973585606,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1866,
        "score": 0.009523809887468815,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1864,
        "score": 0.009433962404727936,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1869,
        "score": 0.009345794096589088,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1842,
        "score": 0.009259259328246117,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1874,
        "score": 0.00917431153357029,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1832,
        "score": 0.00909090880304575,
        "score_kind": "rrf"
      }
    ],
    "final_ranking": [
      {
        "chunk_id": 1834,
        "score": 0.12740954756736755,
        "score_kind": "rerank"
      },
      {
        "chunk_id": 1862,
        "score": 0.0020471573807299137,
        "score_kind": "rerank"
      },
      {
        "chunk_id": 1863,
        "score": 0.0018050847575068474,
        "score_kind": "rerank"
      },
      {
        "chunk_id": 1853,
        "score": 0.0006794504006393254,
        "score_kind": "rerank"
      },
      {
        "chunk_id": 1855,
        "score": 0.0006053760298527777,
        "score_kind": "rerank"
      },
      {
        "chunk_id": 1836,
        "score": 0.0004933086456730962,
        "score_kind": "rerank"
      },
      {
        "chunk_id": 1854,
        "score": 0.0004053457814734429,
        "score_kind": "rerank"
      },
      {
        "chunk_id": 1833,
        "score": 0.0002738673356361687,
        "score_kind": "rerank"
      },
      {
        "chunk_id": 1880,
        "score": 0.0002618345897644758,
        "score_kind": "rerank"
      },
      {
        "chunk_id": 1875,
        "score": 0.00011801818618550897,
        "score_kind": "rerank"
      }
    ]
  }
}
````

### D1 / dense

````json
{
  "eval_id": "D1",
  "strategy": "dense",
  "bucket": "D_unanswerable",
  "difficulty": "absent",
  "category": null,
  "should_refuse": true,
  "refused": true,
  "status": "completed",
  "stage": "complete",
  "query": "你们卖不卖活体宠物,能在这买猫吗",
  "query_plan": {
    "standard": "你们卖不卖活体宠物,能在这买猫吗",
    "expansions": []
  },
  "mapped_groups": [],
  "candidate_ids": [
    1833,
    1875,
    1859,
    1854,
    1880,
    1855,
    1860,
    1844,
    1852,
    1847,
    1853,
    1872,
    1861,
    1877,
    1834,
    1878,
    1840,
    1863,
    1845,
    1835,
    1874,
    1838,
    1837,
    1867,
    1862,
    1868,
    1842,
    1865,
    1870,
    1836,
    1850,
    1841,
    1851,
    1857,
    1839,
    1856,
    1876,
    1871,
    1858,
    1832,
    1848,
    1831,
    1873,
    1869,
    1849,
    1864,
    1846,
    1843,
    1879,
    1866
  ],
  "final_ids": [
    1833,
    1875,
    1859,
    1854,
    1880,
    1855,
    1860,
    1844,
    1852,
    1847
  ],
  "prompt_citations": [
    {
      "n": 1,
      "chunk_id": "1833",
      "section_path": "售后手册/设备安装与激活",
      "question": "设备安装与激活",
      "answer": "智能设备首次使用需下载「喵喵优选」App,按说明书扫码添加设备并连接 2.4G Wi-Fi 完成激活;猫爬架等非联网商品按随附图解自行组装。"
    },
    {
      "n": 3,
      "chunk_id": "1859",
      "section_path": "商品规格手册/大型猫爬架(型号 MH-CT30)",
      "question": "大型猫爬架(型号 MH-CT30)",
      "answer": "- 型号:MH-CT30\n- 高度:1.6m,共四层带顶层吊床\n- 承重:单层最大 10kg\n- 材质:剑麻柱身、绒布平台\n- 安装:需自行组装,随附六角扳手与图解说明书"
    },
    {
      "n": 5,
      "chunk_id": "1880",
      "section_path": "猫窝清洗说明/猫窝是否可以机洗",
      "question": "猫窝是否可以机洗",
      "answer": "普通布艺猫窝清洗前拆掉内部垫芯，外套放入洗衣袋，使用轻柔模式冷水洗，自然晾干。不可直接将整只猫窝连垫芯一起机洗，商品另有清洗标签时优先遵循标签。\n\n带加热模块的猫窝不可机洗，应先断电，并按说明书局部擦洗；不得将加热模块、电源或线路浸水。未按清洗说明操作导致的损坏不直接认定为商品质量问题，需要客服核验。\n\n退货仍需符合商品完好、不影响二次销售等适用条件。售后手册中的电子类商品 12 个月保修不能直接套用到普通布艺猫窝；本清洗说明未给出布艺猫窝的独立保修期限。"
    },
    {
      "n": 7,
      "chunk_id": "1860",
      "section_path": "商品规格手册/恒温加热垫(型号 MH-HP12)",
      "question": "恒温加热垫(型号 MH-HP12)",
      "answer": "- 型号:MH-HP12\n- 尺寸:40cm × 30cm\n- 温控:恒温 38℃,内置过热保护,连续通电不超过 12 小时为宜\n- 防护:防水防抓咬电线套管\n- 适用:幼猫、老年猫及冬季保暖"
    },
    {
      "n": 9,
      "chunk_id": "1852",
      "section_path": "商品规格手册",
      "question": "商品规格手册",
      "answer": "本手册收录喵喵优选自营智能硬件的型号、规格与使用要点,便于按具体型号查询。"
    },
    {
      "n": 10,
      "chunk_id": "1847",
      "section_path": "商品与购物 FAQ/配送范围与偏远地区",
      "question": "配送范围与偏远地区",
      "answer": "全国大部分地区支持配送,新疆、西藏、内蒙古等偏远地区运费另计且时效顺延;港澳台及海外暂不支持自营配送。"
    },
    {
      "n": 8,
      "chunk_id": "1844",
      "section_path": "商品与购物 FAQ/支持哪些支付方式",
      "question": "支持哪些支付方式",
      "answer": "下单支持支付宝、微信支付与主流银行储蓄卡/信用卡在线支付。暂不支持线下汇款,支付遇到问题可重试或更换支付方式。"
    },
    {
      "n": 6,
      "chunk_id": "1855",
      "section_path": "商品规格手册/智能猫砂盆 Max(型号 MH-LP200)",
      "question": "智能猫砂盆 Max(型号 MH-LP200)",
      "answer": "- 型号:MH-LP200\n- 适用猫咪体重:2kg 至 12kg,适合大型猫与多猫家庭\n- 猫砂容量:12L,废砂盒容量约 10 天(单猫)\n- 核心功能:超大滚筒、双重称重防夹、活性炭除臭、App 多猫健康档案\n- 供电:220V 市电\n- 清理提示:多猫家庭建议每 3 至 5 天倾倒一次废砂盒"
    },
    {
      "n": 4,
      "chunk_id": "1854",
      "section_path": "商品规格手册/智能猫砂盆 Lite(型号 MH-LP50)",
      "question": "智能猫砂盆 Lite(型号 MH-LP50)",
      "answer": "- 型号:MH-LP50\n- 适用猫咪体重:1.5kg 至 6kg\n- 猫砂容量:6L\n- 核心功能:自动感应清理、物理除臭盖板;不含 App 联网功能\n- 与 Pro 差异:Lite 无 App 远程监控与健康记录,价格更低,适合单猫家庭"
    },
    {
      "n": 2,
      "chunk_id": "1875",
      "section_path": "会员权益/生日礼",
      "question": "生日礼",
      "answer": "银卡会员生日当月可领取一份猫零食小样，金卡会员生日当月可领取一份猫罐头礼盒。需在会员中心领取，礼品规格与领取期限以页面标注为准，不承诺额外折现或补偿。"
    }
  ],
  "decision": {
    "useful": false,
    "reason": "证据只涉及宠物用品，无活体宠物销售信息",
    "response_kind": "knowledge",
    "source": "self_check"
  },
  "answer": "目前的知识资料不足以确认这个问题，我无法给出可靠答案。请补充具体商品或适用条件，或联系人工客服确认。",
  "point_verdicts": [],
  "claim_verdicts": [
    {
      "claim": "目前的知识资料不足以确认是否售卖活体宠物及能否购买猫",
      "supported": false,
      "reason": "supporting_evidence中无任何关于售卖活体宠物或销售猫咪的资料，无法支持该断言"
    },
    {
      "claim": "可联系人工客服确认",
      "supported": false,
      "reason": "所给证据中均未提及联系人工客服渠道，证据沉默不能支持该断言"
    }
  ],
  "metrics": {
    "recall_at_5": null,
    "recall_at_10": null,
    "mrr_at_10": null,
    "all_groups_hit_at_5": null,
    "all_groups_hit_at_10": null,
    "candidate_group_coverage": null,
    "prompt_group_coverage": null,
    "answer_point_coverage": null,
    "faithfulness": 0.0,
    "absent_refusal_rate": 1.0,
    "answerable_false_refusal_rate": null
  },
  "error": null,
  "elapsed_ms": 5402.939799707383,
  "judge_snapshot": {
    "prompt_version": "joint-generation-v2.1",
    "finish_reason": "stop"
  },
  "audit": {
    "audit_version": 1,
    "source_map_id": "d2dd350d860b8141e52306cbbcafb22f97d091194eb1cdc839a528c2990715eb",
    "gold_groups": [],
    "answer_points": [],
    "candidate_ranking": [
      {
        "chunk_id": 1833,
        "score": 0.5230516195297241,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1875,
        "score": 0.5179657936096191,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1859,
        "score": 0.5065388679504395,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1854,
        "score": 0.48598092794418335,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1880,
        "score": 0.4831678867340088,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1855,
        "score": 0.47691166400909424,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1860,
        "score": 0.4717397689819336,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1844,
        "score": 0.4711533784866333,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1852,
        "score": 0.46646931767463684,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1847,
        "score": 0.46494314074516296,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1853,
        "score": 0.463568776845932,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1872,
        "score": 0.46218544244766235,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1861,
        "score": 0.46162259578704834,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1877,
        "score": 0.4522022306919098,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1834,
        "score": 0.41445615887641907,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1878,
        "score": 0.4099642038345337,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1840,
        "score": 0.40904730558395386,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1863,
        "score": 0.3981292247772217,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1845,
        "score": 0.3965839445590973,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1835,
        "score": 0.396505743265152,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1874,
        "score": 0.3954104483127594,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1838,
        "score": 0.3926236033439636,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1837,
        "score": 0.38972947001457214,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1867,
        "score": 0.3888472020626068,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1862,
        "score": 0.38517123460769653,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1868,
        "score": 0.38374242186546326,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1842,
        "score": 0.3832646608352661,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1865,
        "score": 0.38103967905044556,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1870,
        "score": 0.3807104229927063,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1836,
        "score": 0.37865543365478516,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1850,
        "score": 0.37787264585494995,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1841,
        "score": 0.37357136607170105,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1851,
        "score": 0.3725582957267761,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1857,
        "score": 0.3710084855556488,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1839,
        "score": 0.3690685033798218,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1856,
        "score": 0.36683714389801025,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1876,
        "score": 0.3662397265434265,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1871,
        "score": 0.3630025088787079,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1858,
        "score": 0.3616905212402344,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1832,
        "score": 0.3609623312950134,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1848,
        "score": 0.3583538830280304,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1831,
        "score": 0.3537989854812622,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1873,
        "score": 0.3536772131919861,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1869,
        "score": 0.3531789481639862,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1849,
        "score": 0.35167378187179565,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1864,
        "score": 0.34869906306266785,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1846,
        "score": 0.34145939350128174,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1843,
        "score": 0.33695530891418457,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1879,
        "score": 0.3166200518608093,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1866,
        "score": 0.31439435482025146,
        "score_kind": "cosine"
      }
    ],
    "final_ranking": [
      {
        "chunk_id": 1833,
        "score": 0.5230516195297241,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1875,
        "score": 0.5179657936096191,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1859,
        "score": 0.5065388679504395,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1854,
        "score": 0.48598092794418335,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1880,
        "score": 0.4831678867340088,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1855,
        "score": 0.47691166400909424,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1860,
        "score": 0.4717397689819336,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1844,
        "score": 0.4711533784866333,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1852,
        "score": 0.46646931767463684,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1847,
        "score": 0.46494314074516296,
        "score_kind": "cosine"
      }
    ]
  }
}
````

### D1 / bm25

````json
{
  "eval_id": "D1",
  "strategy": "bm25",
  "bucket": "D_unanswerable",
  "difficulty": "absent",
  "category": null,
  "should_refuse": true,
  "refused": true,
  "status": "completed",
  "stage": "complete",
  "query": "你们卖不卖活体宠物,能在这买猫吗",
  "query_plan": {
    "standard": "你们卖不卖活体宠物,能在这买猫吗",
    "expansions": []
  },
  "mapped_groups": [],
  "candidate_ids": [
    1848,
    1880,
    1834,
    1855,
    1875,
    1846,
    1832,
    1877,
    1839,
    1872,
    1843,
    1849,
    1850,
    1859,
    1860,
    1833,
    1845,
    1871,
    1861,
    1854,
    1874,
    1853,
    1879
  ],
  "final_ids": [
    1848,
    1880,
    1834,
    1855,
    1875,
    1846,
    1832,
    1877,
    1839,
    1872
  ],
  "prompt_citations": [
    {
      "n": 1,
      "chunk_id": "1848",
      "section_path": "商品与购物 FAQ/订单可以修改或取消吗",
      "question": "订单可以修改或取消吗",
      "answer": "订单未发货前可在「我的订单」自助取消;已发货订单无法修改收货信息,可拒收后走退款流程。修改商品数量需取消后重新下单。"
    },
    {
      "n": 3,
      "chunk_id": "1834",
      "section_path": "售后手册/常见故障自查",
      "question": "常见故障自查",
      "answer": "- 饮水机不出水:检查水位是否低于最低线、水泵是否卡阻,断电清洗水泵后重试。\n- 猫砂盆报错:清空废砂盒并检查滚筒是否卡砂,重启设备;仍报错联系售后。\n- 喂食器卡粮:检查粮食颗粒直径是否超 12mm、粮桶是否受潮结块,清理出粮口后重试。\n- 摄像头离线:确认 Wi-Fi 为 2.4G 频段、信号良好,重启设备或在 App 内重新配网。"
    },
    {
      "n": 5,
      "chunk_id": "1875",
      "section_path": "会员权益/生日礼",
      "question": "生日礼",
      "answer": "银卡会员生日当月可领取一份猫零食小样，金卡会员生日当月可领取一份猫罐头礼盒。需在会员中心领取，礼品规格与领取期限以页面标注为准，不承诺额外折现或补偿。"
    },
    {
      "n": 7,
      "chunk_id": "1832",
      "section_path": "售后手册/保修说明",
      "question": "保修说明",
      "answer": "电子类商品保修 12 个月,自签收日起算;人为损坏不在保修范围。"
    },
    {
      "n": 9,
      "chunk_id": "1839",
      "section_path": "商品与购物 FAQ/如何申请退款",
      "question": "如何申请退款",
      "answer": "在「我的订单」找到对应订单点击「申请退款」,按提示提交,审核通过后原路退回。"
    },
    {
      "n": 10,
      "chunk_id": "1872",
      "section_path": "退货退款政策/不支持退货的商品",
      "question": "不支持退货的商品",
      "answer": "定制类、生鲜类、已拆封的猫砂等消耗品,以及标注「不支持无理由退货」的商品,非质量问题不支持退货。"
    },
    {
      "n": 8,
      "chunk_id": "1877",
      "section_path": "积分规则/积分怎么用",
      "question": "积分怎么用",
      "answer": "积分可在结算时抵扣商品金额，100 积分抵 1 元现金，单笔订单最多抵 30 元，不用于抵扣偏远地区附加运费，也不支持直接提现。\n\n2000 积分可兑换自动饮水机滤芯 3 片，该兑换套装适用于 MH-W40，普通配送地区包邮；偏远地区附加配送费仍需按页面规则确认。MH-W40 的滤芯更换周期以商品规格手册为准。\n\n800 积分可兑换猫零食小样，普通配送地区另收 6 元运费；该兑换不直接套用普通购物订单的满 99 元包邮规则。兑换商品、可用库存及偏远地区配送规则以兑换页面标注为准。"
    },
    {
      "n": 6,
      "chunk_id": "1846",
      "section_path": "商品与购物 FAQ/优惠券和满减怎么用",
      "question": "优惠券和满减怎么用",
      "answer": "优惠券在结算页「使用优惠券」中勾选,满减活动自动叠加在商品页标示的门槛上;同一订单一般限用一张店铺券,活动细则以页面为准。"
    },
    {
      "n": 4,
      "chunk_id": "1855",
      "section_path": "商品规格手册/智能猫砂盆 Max(型号 MH-LP200)",
      "question": "智能猫砂盆 Max(型号 MH-LP200)",
      "answer": "- 型号:MH-LP200\n- 适用猫咪体重:2kg 至 12kg,适合大型猫与多猫家庭\n- 猫砂容量:12L,废砂盒容量约 10 天(单猫)\n- 核心功能:超大滚筒、双重称重防夹、活性炭除臭、App 多猫健康档案\n- 供电:220V 市电\n- 清理提示:多猫家庭建议每 3 至 5 天倾倒一次废砂盒"
    },
    {
      "n": 2,
      "chunk_id": "1880",
      "section_path": "猫窝清洗说明/猫窝是否可以机洗",
      "question": "猫窝是否可以机洗",
      "answer": "普通布艺猫窝清洗前拆掉内部垫芯，外套放入洗衣袋，使用轻柔模式冷水洗，自然晾干。不可直接将整只猫窝连垫芯一起机洗，商品另有清洗标签时优先遵循标签。\n\n带加热模块的猫窝不可机洗，应先断电，并按说明书局部擦洗；不得将加热模块、电源或线路浸水。未按清洗说明操作导致的损坏不直接认定为商品质量问题，需要客服核验。\n\n退货仍需符合商品完好、不影响二次销售等适用条件。售后手册中的电子类商品 12 个月保修不能直接套用到普通布艺猫窝；本清洗说明未给出布艺猫窝的独立保修期限。"
    }
  ],
  "decision": {
    "useful": false,
    "reason": "无售卖活体宠物相关证据",
    "response_kind": "knowledge",
    "source": "self_check"
  },
  "answer": "目前的知识资料不足以确认这个问题，我无法给出可靠答案。请补充具体商品或适用条件，或联系人工客服确认。",
  "point_verdicts": [],
  "claim_verdicts": [
    {
      "claim": "目前的知识资料不足以确认是否销售活体宠物（能否买猫）",
      "supported": true,
      "reason": "supporting_evidence 中无任何关于活体宠物销售的条目，回答为拒答且断言的是资料不足以确认，与证据沉默状态一致。"
    }
  ],
  "metrics": {
    "recall_at_5": null,
    "recall_at_10": null,
    "mrr_at_10": null,
    "all_groups_hit_at_5": null,
    "all_groups_hit_at_10": null,
    "candidate_group_coverage": null,
    "prompt_group_coverage": null,
    "answer_point_coverage": null,
    "faithfulness": 1.0,
    "absent_refusal_rate": 1.0,
    "answerable_false_refusal_rate": null
  },
  "error": null,
  "elapsed_ms": 5670.897799776867,
  "judge_snapshot": {
    "prompt_version": "joint-generation-v2.1",
    "finish_reason": "stop"
  },
  "audit": {
    "audit_version": 1,
    "source_map_id": "d2dd350d860b8141e52306cbbcafb22f97d091194eb1cdc839a528c2990715eb",
    "gold_groups": [],
    "answer_points": [],
    "candidate_ranking": [
      {
        "chunk_id": 1848,
        "score": 5.146595478057861,
        "score_kind": "bm25"
      },
      {
        "chunk_id": 1880,
        "score": 2.217597484588623,
        "score_kind": "bm25"
      },
      {
        "chunk_id": 1834,
        "score": 2.203824281692505,
        "score_kind": "bm25"
      },
      {
        "chunk_id": 1855,
        "score": 2.051485300064087,
        "score_kind": "bm25"
      },
      {
        "chunk_id": 1875,
        "score": 1.9893113374710083,
        "score_kind": "bm25"
      },
      {
        "chunk_id": 1846,
        "score": 1.9015036821365356,
        "score_kind": "bm25"
      },
      {
        "chunk_id": 1832,
        "score": 1.7063724994659424,
        "score_kind": "bm25"
      },
      {
        "chunk_id": 1877,
        "score": 1.6996121406555176,
        "score_kind": "bm25"
      },
      {
        "chunk_id": 1839,
        "score": 1.6403803825378418,
        "score_kind": "bm25"
      },
      {
        "chunk_id": 1872,
        "score": 1.5823721885681152,
        "score_kind": "bm25"
      },
      {
        "chunk_id": 1843,
        "score": 1.5647372007369995,
        "score_kind": "bm25"
      },
      {
        "chunk_id": 1849,
        "score": 1.536397933959961,
        "score_kind": "bm25"
      },
      {
        "chunk_id": 1850,
        "score": 1.5090670585632324,
        "score_kind": "bm25"
      },
      {
        "chunk_id": 1859,
        "score": 1.5028752088546753,
        "score_kind": "bm25"
      },
      {
        "chunk_id": 1860,
        "score": 1.5028752088546753,
        "score_kind": "bm25"
      },
      {
        "chunk_id": 1833,
        "score": 1.4903959035873413,
        "score_kind": "bm25"
      },
      {
        "chunk_id": 1845,
        "score": 1.469846248626709,
        "score_kind": "bm25"
      },
      {
        "chunk_id": 1871,
        "score": 1.4572218656539917,
        "score_kind": "bm25"
      },
      {
        "chunk_id": 1861,
        "score": 1.4309837818145752,
        "score_kind": "bm25"
      },
      {
        "chunk_id": 1854,
        "score": 1.3656563758850098,
        "score_kind": "bm25"
      },
      {
        "chunk_id": 1874,
        "score": 1.2454544305801392,
        "score_kind": "bm25"
      },
      {
        "chunk_id": 1853,
        "score": 1.217445969581604,
        "score_kind": "bm25"
      },
      {
        "chunk_id": 1879,
        "score": 1.0986462831497192,
        "score_kind": "bm25"
      }
    ],
    "final_ranking": [
      {
        "chunk_id": 1848,
        "score": 5.146595478057861,
        "score_kind": "bm25"
      },
      {
        "chunk_id": 1880,
        "score": 2.217597484588623,
        "score_kind": "bm25"
      },
      {
        "chunk_id": 1834,
        "score": 2.203824281692505,
        "score_kind": "bm25"
      },
      {
        "chunk_id": 1855,
        "score": 2.051485300064087,
        "score_kind": "bm25"
      },
      {
        "chunk_id": 1875,
        "score": 1.9893113374710083,
        "score_kind": "bm25"
      },
      {
        "chunk_id": 1846,
        "score": 1.9015036821365356,
        "score_kind": "bm25"
      },
      {
        "chunk_id": 1832,
        "score": 1.7063724994659424,
        "score_kind": "bm25"
      },
      {
        "chunk_id": 1877,
        "score": 1.6996121406555176,
        "score_kind": "bm25"
      },
      {
        "chunk_id": 1839,
        "score": 1.6403803825378418,
        "score_kind": "bm25"
      },
      {
        "chunk_id": 1872,
        "score": 1.5823721885681152,
        "score_kind": "bm25"
      }
    ]
  }
}
````

### D1 / hybrid

````json
{
  "eval_id": "D1",
  "strategy": "hybrid",
  "bucket": "D_unanswerable",
  "difficulty": "absent",
  "category": null,
  "should_refuse": true,
  "refused": true,
  "status": "completed",
  "stage": "complete",
  "query": "你们卖不卖活体宠物,能在这买猫吗",
  "query_plan": {
    "standard": "你们卖不卖活体宠物,能在这买猫吗",
    "expansions": []
  },
  "mapped_groups": [],
  "candidate_ids": [
    1875,
    1880,
    1855,
    1833,
    1859,
    1834,
    1860,
    1877,
    1872,
    1854,
    1861,
    1848,
    1853,
    1845,
    1839,
    1832,
    1874,
    1850,
    1846,
    1849,
    1843,
    1871,
    1879,
    1844,
    1852,
    1847,
    1878,
    1840,
    1863,
    1835,
    1838,
    1837,
    1867,
    1862,
    1868,
    1842,
    1865,
    1870,
    1836,
    1841,
    1851,
    1857,
    1856,
    1876,
    1858,
    1831,
    1873,
    1869,
    1864,
    1866
  ],
  "final_ids": [
    1875,
    1880,
    1855,
    1833,
    1859,
    1834,
    1860,
    1877,
    1872,
    1854
  ],
  "prompt_citations": [
    {
      "n": 1,
      "chunk_id": "1875",
      "section_path": "会员权益/生日礼",
      "question": "生日礼",
      "answer": "银卡会员生日当月可领取一份猫零食小样，金卡会员生日当月可领取一份猫罐头礼盒。需在会员中心领取，礼品规格与领取期限以页面标注为准，不承诺额外折现或补偿。"
    },
    {
      "n": 3,
      "chunk_id": "1855",
      "section_path": "商品规格手册/智能猫砂盆 Max(型号 MH-LP200)",
      "question": "智能猫砂盆 Max(型号 MH-LP200)",
      "answer": "- 型号:MH-LP200\n- 适用猫咪体重:2kg 至 12kg,适合大型猫与多猫家庭\n- 猫砂容量:12L,废砂盒容量约 10 天(单猫)\n- 核心功能:超大滚筒、双重称重防夹、活性炭除臭、App 多猫健康档案\n- 供电:220V 市电\n- 清理提示:多猫家庭建议每 3 至 5 天倾倒一次废砂盒"
    },
    {
      "n": 5,
      "chunk_id": "1859",
      "section_path": "商品规格手册/大型猫爬架(型号 MH-CT30)",
      "question": "大型猫爬架(型号 MH-CT30)",
      "answer": "- 型号:MH-CT30\n- 高度:1.6m,共四层带顶层吊床\n- 承重:单层最大 10kg\n- 材质:剑麻柱身、绒布平台\n- 安装:需自行组装,随附六角扳手与图解说明书"
    },
    {
      "n": 7,
      "chunk_id": "1860",
      "section_path": "商品规格手册/恒温加热垫(型号 MH-HP12)",
      "question": "恒温加热垫(型号 MH-HP12)",
      "answer": "- 型号:MH-HP12\n- 尺寸:40cm × 30cm\n- 温控:恒温 38℃,内置过热保护,连续通电不超过 12 小时为宜\n- 防护:防水防抓咬电线套管\n- 适用:幼猫、老年猫及冬季保暖"
    },
    {
      "n": 9,
      "chunk_id": "1872",
      "section_path": "退货退款政策/不支持退货的商品",
      "question": "不支持退货的商品",
      "answer": "定制类、生鲜类、已拆封的猫砂等消耗品,以及标注「不支持无理由退货」的商品,非质量问题不支持退货。"
    },
    {
      "n": 10,
      "chunk_id": "1854",
      "section_path": "商品规格手册/智能猫砂盆 Lite(型号 MH-LP50)",
      "question": "智能猫砂盆 Lite(型号 MH-LP50)",
      "answer": "- 型号:MH-LP50\n- 适用猫咪体重:1.5kg 至 6kg\n- 猫砂容量:6L\n- 核心功能:自动感应清理、物理除臭盖板;不含 App 联网功能\n- 与 Pro 差异:Lite 无 App 远程监控与健康记录,价格更低,适合单猫家庭"
    },
    {
      "n": 8,
      "chunk_id": "1877",
      "section_path": "积分规则/积分怎么用",
      "question": "积分怎么用",
      "answer": "积分可在结算时抵扣商品金额，100 积分抵 1 元现金，单笔订单最多抵 30 元，不用于抵扣偏远地区附加运费，也不支持直接提现。\n\n2000 积分可兑换自动饮水机滤芯 3 片，该兑换套装适用于 MH-W40，普通配送地区包邮；偏远地区附加配送费仍需按页面规则确认。MH-W40 的滤芯更换周期以商品规格手册为准。\n\n800 积分可兑换猫零食小样，普通配送地区另收 6 元运费；该兑换不直接套用普通购物订单的满 99 元包邮规则。兑换商品、可用库存及偏远地区配送规则以兑换页面标注为准。"
    },
    {
      "n": 6,
      "chunk_id": "1834",
      "section_path": "售后手册/常见故障自查",
      "question": "常见故障自查",
      "answer": "- 饮水机不出水:检查水位是否低于最低线、水泵是否卡阻,断电清洗水泵后重试。\n- 猫砂盆报错:清空废砂盒并检查滚筒是否卡砂,重启设备;仍报错联系售后。\n- 喂食器卡粮:检查粮食颗粒直径是否超 12mm、粮桶是否受潮结块,清理出粮口后重试。\n- 摄像头离线:确认 Wi-Fi 为 2.4G 频段、信号良好,重启设备或在 App 内重新配网。"
    },
    {
      "n": 4,
      "chunk_id": "1833",
      "section_path": "售后手册/设备安装与激活",
      "question": "设备安装与激活",
      "answer": "智能设备首次使用需下载「喵喵优选」App,按说明书扫码添加设备并连接 2.4G Wi-Fi 完成激活;猫爬架等非联网商品按随附图解自行组装。"
    },
    {
      "n": 2,
      "chunk_id": "1880",
      "section_path": "猫窝清洗说明/猫窝是否可以机洗",
      "question": "猫窝是否可以机洗",
      "answer": "普通布艺猫窝清洗前拆掉内部垫芯，外套放入洗衣袋，使用轻柔模式冷水洗，自然晾干。不可直接将整只猫窝连垫芯一起机洗，商品另有清洗标签时优先遵循标签。\n\n带加热模块的猫窝不可机洗，应先断电，并按说明书局部擦洗；不得将加热模块、电源或线路浸水。未按清洗说明操作导致的损坏不直接认定为商品质量问题，需要客服核验。\n\n退货仍需符合商品完好、不影响二次销售等适用条件。售后手册中的电子类商品 12 个月保修不能直接套用到普通布艺猫窝；本清洗说明未给出布艺猫窝的独立保修期限。"
    }
  ],
  "decision": {
    "useful": false,
    "reason": "无销售活体宠物相关证据",
    "response_kind": "knowledge",
    "source": "self_check"
  },
  "answer": "目前的知识资料不足以确认这个问题，我无法给出可靠答案。请补充具体商品或适用条件，或联系人工客服确认。",
  "point_verdicts": [],
  "claim_verdicts": [
    {
      "claim": "目前的知识资料不足以确认是否售卖活体宠物/能否购买猫",
      "supported": false,
      "reason": "该断言属于拒答表述，支持证据中无任何关于活体宠物或售猫的信息，证据沉默不能证明知识不足"
    }
  ],
  "metrics": {
    "recall_at_5": null,
    "recall_at_10": null,
    "mrr_at_10": null,
    "all_groups_hit_at_5": null,
    "all_groups_hit_at_10": null,
    "candidate_group_coverage": null,
    "prompt_group_coverage": null,
    "answer_point_coverage": null,
    "faithfulness": 0.0,
    "absent_refusal_rate": 1.0,
    "answerable_false_refusal_rate": null
  },
  "error": null,
  "elapsed_ms": 5170.495299855247,
  "judge_snapshot": {
    "prompt_version": "joint-generation-v2.1",
    "finish_reason": "stop"
  },
  "audit": {
    "audit_version": 1,
    "source_map_id": "d2dd350d860b8141e52306cbbcafb22f97d091194eb1cdc839a528c2990715eb",
    "gold_groups": [],
    "answer_points": [],
    "candidate_ranking": [
      {
        "chunk_id": 1875,
        "score": 0.03151364624500275,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1880,
        "score": 0.03151364624500275,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1855,
        "score": 0.03077651560306549,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1833,
        "score": 0.02955133654177189,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1859,
        "score": 0.029386531561613083,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1834,
        "score": 0.029206350445747375,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1860,
        "score": 0.028258707374334335,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1877,
        "score": 0.028219396248459816,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1872,
        "score": 0.02817460335791111,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1854,
        "score": 0.02812499925494194,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1861,
        "score": 0.026356857270002365,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1848,
        "score": 0.02629443258047104,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1853,
        "score": 0.02627962827682495,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1845,
        "score": 0.025645241141319275,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1839,
        "score": 0.025019070133566856,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1832,
        "score": 0.02492537349462509,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1874,
        "score": 0.02469135820865631,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1850,
        "score": 0.024687640368938446,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1846,
        "score": 0.02449730969965458,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1849,
        "score": 0.02341269887983799,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1843,
        "score": 0.02334376610815525,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1871,
        "score": 0.02302459441125393,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1879,
        "score": 0.02122250385582447,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1844,
        "score": 0.014705882407724857,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1852,
        "score": 0.014492753893136978,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1847,
        "score": 0.014285714365541935,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1878,
        "score": 0.01315789483487606,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1840,
        "score": 0.012987012974917889,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1863,
        "score": 0.012820512987673283,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1835,
        "score": 0.012500000186264515,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1838,
        "score": 0.012195121496915817,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1837,
        "score": 0.012048192322254181,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1867,
        "score": 0.011904762126505375,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1862,
        "score": 0.0117647061124444,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1868,
        "score": 0.011627906933426857,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1842,
        "score": 0.01149425283074379,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1865,
        "score": 0.011363636702299118,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1870,
        "score": 0.01123595517128706,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1836,
        "score": 0.011111111380159855,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1841,
        "score": 0.010869565419852734,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1851,
        "score": 0.01075268816202879,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1857,
        "score": 0.010638297535479069,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1856,
        "score": 0.010416666977107525,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1876,
        "score": 0.010309278033673763,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1858,
        "score": 0.010101010091602802,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1831,
        "score": 0.009803921915590763,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1873,
        "score": 0.009708737954497337,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1869,
        "score": 0.009615384973585606,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1864,
        "score": 0.009433962404727936,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1866,
        "score": 0.00909090880304575,
        "score_kind": "rrf"
      }
    ],
    "final_ranking": [
      {
        "chunk_id": 1875,
        "score": 0.03151364624500275,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1880,
        "score": 0.03151364624500275,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1855,
        "score": 0.03077651560306549,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1833,
        "score": 0.02955133654177189,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1859,
        "score": 0.029386531561613083,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1834,
        "score": 0.029206350445747375,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1860,
        "score": 0.028258707374334335,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1877,
        "score": 0.028219396248459816,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1872,
        "score": 0.02817460335791111,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1854,
        "score": 0.02812499925494194,
        "score_kind": "rrf"
      }
    ]
  }
}
````

### D1 / hybrid_rerank

````json
{
  "eval_id": "D1",
  "strategy": "hybrid_rerank",
  "bucket": "D_unanswerable",
  "difficulty": "absent",
  "category": null,
  "should_refuse": true,
  "refused": true,
  "status": "completed",
  "stage": "complete",
  "query": "你们卖不卖活体宠物,能在这买猫吗",
  "query_plan": {
    "standard": "你们卖不卖活体宠物,能在这买猫吗",
    "expansions": []
  },
  "mapped_groups": [],
  "candidate_ids": [
    1875,
    1880,
    1855,
    1833,
    1859,
    1834,
    1860,
    1877,
    1872,
    1854,
    1861,
    1848,
    1853,
    1845,
    1839,
    1832,
    1874,
    1850,
    1846,
    1849,
    1843,
    1871,
    1879,
    1844,
    1852,
    1847,
    1878,
    1840,
    1863,
    1835,
    1838,
    1837,
    1867,
    1862,
    1868,
    1842,
    1865,
    1870,
    1836,
    1841,
    1851,
    1857,
    1856,
    1876,
    1858,
    1831,
    1873,
    1869,
    1864,
    1866
  ],
  "final_ids": [
    1875,
    1872,
    1847,
    1838,
    1869,
    1865,
    1874,
    1868,
    1837,
    1873
  ],
  "prompt_citations": [
    {
      "n": 1,
      "chunk_id": "1875",
      "section_path": "会员权益/生日礼",
      "question": "生日礼",
      "answer": "银卡会员生日当月可领取一份猫零食小样，金卡会员生日当月可领取一份猫罐头礼盒。需在会员中心领取，礼品规格与领取期限以页面标注为准，不承诺额外折现或补偿。"
    },
    {
      "n": 3,
      "chunk_id": "1847",
      "section_path": "商品与购物 FAQ/配送范围与偏远地区",
      "question": "配送范围与偏远地区",
      "answer": "全国大部分地区支持配送,新疆、西藏、内蒙古等偏远地区运费另计且时效顺延;港澳台及海外暂不支持自营配送。"
    },
    {
      "n": 5,
      "chunk_id": "1869",
      "section_path": "退货退款政策/退换货运费承担",
      "question": "退换货运费承担",
      "answer": "无理由退货的退回运费由买家承担;因商品质量问题、发错货、少发漏发导致的退换货,运费由平台承担。运费承担以平台售后规则最终判定为准。"
    },
    {
      "n": 7,
      "chunk_id": "1874",
      "section_path": "会员权益/会员等级",
      "question": "会员等级",
      "answer": "会员分为普通、银卡和金卡三档，按有效累计消费金额自动升级，不按年度消费金额计算。累计消费未满 1000 元为普通会员，满 1000 元起为银卡，满 5000 元起为金卡。\n\n有效累计消费指已完成订单的商品实际支付金额，不含配送费；退货退款部分从有效累计消费中扣除。退款后根据更新的累计消费重新计算等级，未达到原门槛时可能降级。等级与适用权益在会员中心展示。\n\n银卡在参与会员折扣的商品上享 95 折，金卡享 9 折。折扣适用商品和活动范围以结算页面标注为准。会员折扣、优惠券与满减是否叠加也以当次活动页面为准，不能一概承诺全部优惠同时生效。"
    },
    {
      "n": 9,
      "chunk_id": "1837",
      "section_path": "售后手册/会员专属售后权益",
      "question": "会员专属售后权益",
      "answer": "金卡会员享优先客服接入与上门取件退换货;银卡会员享退换货运费权益 1 次/月。具体权益以会员中心页面标注为准。"
    },
    {
      "n": 10,
      "chunk_id": "1873",
      "section_path": "退货退款政策/预售与定金",
      "question": "预售与定金",
      "answer": "预售商品以详情页标注的时间发货;定金支付后不支持无理由退定金,尾款未按时支付的,定金按活动规则处理。"
    },
    {
      "n": 8,
      "chunk_id": "1868",
      "section_path": "退货退款政策/换货政策/换货运费",
      "question": "换货运费",
      "answer": "非质量问题的换货,往返运费由买家承担;因质量问题或发错货的换货,往返运费由平台承担。"
    },
    {
      "n": 6,
      "chunk_id": "1865",
      "section_path": "退货退款政策/无理由退货/适用范围",
      "question": "适用范围",
      "answer": "自签收之日起 7 天内,商品完好、不影响二次销售的,支持无理由退货。定制类、生鲜类商品除外。"
    },
    {
      "n": 4,
      "chunk_id": "1838",
      "section_path": "商品与购物 FAQ/退货政策是什么",
      "question": "退货政策是什么",
      "answer": "支持 7 天无理由退货,商品需保持完好、不影响二次销售,具体以平台售后规则为准。"
    },
    {
      "n": 2,
      "chunk_id": "1872",
      "section_path": "退货退款政策/不支持退货的商品",
      "question": "不支持退货的商品",
      "answer": "定制类、生鲜类、已拆封的猫砂等消耗品,以及标注「不支持无理由退货」的商品,非质量问题不支持退货。"
    }
  ],
  "decision": {
    "useful": false,
    "reason": "无活体宠物销售相关证据",
    "response_kind": "knowledge",
    "source": "self_check"
  },
  "answer": "目前的知识资料不足以确认这个问题，我无法给出可靠答案。请补充具体商品或适用条件，或联系人工客服确认。",
  "point_verdicts": [],
  "claim_verdicts": [
    {
      "claim": "目前的知识资料不足以确认是否售卖活体宠物/能否购买猫",
      "supported": true,
      "reason": "支持证据中无任何关于活体宠物或售卖猫的内容，回答为拒答，不构成与证据矛盾的事实断言"
    },
    {
      "claim": "建议补充具体商品或适用条件，或联系人工客服确认",
      "supported": true,
      "reason": "这是流程性建议而非可验证事实断言，与支持证据无冲突"
    }
  ],
  "metrics": {
    "recall_at_5": null,
    "recall_at_10": null,
    "mrr_at_10": null,
    "all_groups_hit_at_5": null,
    "all_groups_hit_at_10": null,
    "candidate_group_coverage": null,
    "prompt_group_coverage": null,
    "answer_point_coverage": null,
    "faithfulness": 1.0,
    "absent_refusal_rate": 1.0,
    "answerable_false_refusal_rate": null
  },
  "error": null,
  "elapsed_ms": 6228.283199714497,
  "judge_snapshot": {
    "prompt_version": "joint-generation-v2.1",
    "finish_reason": "stop"
  },
  "audit": {
    "audit_version": 1,
    "source_map_id": "d2dd350d860b8141e52306cbbcafb22f97d091194eb1cdc839a528c2990715eb",
    "gold_groups": [],
    "answer_points": [],
    "candidate_ranking": [
      {
        "chunk_id": 1875,
        "score": 0.03151364624500275,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1880,
        "score": 0.03151364624500275,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1855,
        "score": 0.03077651560306549,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1833,
        "score": 0.02955133654177189,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1859,
        "score": 0.029386531561613083,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1834,
        "score": 0.029206350445747375,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1860,
        "score": 0.028258707374334335,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1877,
        "score": 0.028219396248459816,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1872,
        "score": 0.02817460335791111,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1854,
        "score": 0.02812499925494194,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1861,
        "score": 0.026356857270002365,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1848,
        "score": 0.02629443258047104,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1853,
        "score": 0.02627962827682495,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1845,
        "score": 0.025645241141319275,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1839,
        "score": 0.025019070133566856,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1832,
        "score": 0.02492537349462509,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1874,
        "score": 0.02469135820865631,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1850,
        "score": 0.024687640368938446,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1846,
        "score": 0.02449730969965458,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1849,
        "score": 0.02341269887983799,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1843,
        "score": 0.02334376610815525,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1871,
        "score": 0.02302459441125393,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1879,
        "score": 0.02122250385582447,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1844,
        "score": 0.014705882407724857,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1852,
        "score": 0.014492753893136978,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1847,
        "score": 0.014285714365541935,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1878,
        "score": 0.01315789483487606,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1840,
        "score": 0.012987012974917889,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1863,
        "score": 0.012820512987673283,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1835,
        "score": 0.012500000186264515,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1838,
        "score": 0.012195121496915817,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1837,
        "score": 0.012048192322254181,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1867,
        "score": 0.011904762126505375,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1862,
        "score": 0.0117647061124444,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1868,
        "score": 0.011627906933426857,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1842,
        "score": 0.01149425283074379,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1865,
        "score": 0.011363636702299118,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1870,
        "score": 0.01123595517128706,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1836,
        "score": 0.011111111380159855,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1841,
        "score": 0.010869565419852734,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1851,
        "score": 0.01075268816202879,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1857,
        "score": 0.010638297535479069,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1856,
        "score": 0.010416666977107525,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1876,
        "score": 0.010309278033673763,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1858,
        "score": 0.010101010091602802,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1831,
        "score": 0.009803921915590763,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1873,
        "score": 0.009708737954497337,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1869,
        "score": 0.009615384973585606,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1864,
        "score": 0.009433962404727936,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1866,
        "score": 0.00909090880304575,
        "score_kind": "rrf"
      }
    ],
    "final_ranking": [
      {
        "chunk_id": 1875,
        "score": 0.0023051647003740072,
        "score_kind": "rerank"
      },
      {
        "chunk_id": 1872,
        "score": 0.002274215454235673,
        "score_kind": "rerank"
      },
      {
        "chunk_id": 1847,
        "score": 0.000764955417253077,
        "score_kind": "rerank"
      },
      {
        "chunk_id": 1838,
        "score": 0.000689350999891758,
        "score_kind": "rerank"
      },
      {
        "chunk_id": 1869,
        "score": 0.0006385192391462624,
        "score_kind": "rerank"
      },
      {
        "chunk_id": 1865,
        "score": 0.0005955551750957966,
        "score_kind": "rerank"
      },
      {
        "chunk_id": 1874,
        "score": 0.000558023399207741,
        "score_kind": "rerank"
      },
      {
        "chunk_id": 1868,
        "score": 0.0005302883801050484,
        "score_kind": "rerank"
      },
      {
        "chunk_id": 1837,
        "score": 0.00047907227417454123,
        "score_kind": "rerank"
      },
      {
        "chunk_id": 1873,
        "score": 0.00047448326949961483,
        "score_kind": "rerank"
      }
    ]
  }
}
````

### D3 / dense

````json
{
  "eval_id": "D3",
  "strategy": "dense",
  "bucket": "D_unanswerable",
  "difficulty": "absent",
  "category": null,
  "should_refuse": true,
  "refused": true,
  "status": "completed",
  "stage": "complete",
  "query": "纸质发票遗失后能申请挂失证明吗",
  "query_plan": {
    "standard": "纸质发票遗失后能申请挂失证明吗",
    "expansions": []
  },
  "mapped_groups": [],
  "candidate_ids": [
    1878,
    1843,
    1879,
    1871,
    1839,
    1836,
    1831,
    1832,
    1873,
    1867,
    1870,
    1865,
    1837,
    1848,
    1840,
    1850,
    1868,
    1866,
    1877,
    1838,
    1869,
    1849,
    1872,
    1835,
    1841,
    1844,
    1851,
    1846,
    1834,
    1876,
    1842,
    1847,
    1875,
    1852,
    1874,
    1858,
    1833,
    1857,
    1845,
    1856,
    1862,
    1863,
    1861,
    1880,
    1864,
    1853,
    1855,
    1859,
    1854,
    1860
  ],
  "final_ids": [
    1878,
    1843,
    1879,
    1871,
    1839,
    1836,
    1831,
    1832,
    1873,
    1867
  ],
  "prompt_citations": [
    {
      "n": 1,
      "chunk_id": "1878",
      "section_path": "开票细则/可开票类型",
      "question": "可开票类型",
      "answer": "本演示店提供电子普通发票、电子专用发票和纸质专用发票。电子普通发票可按订单申请；电子专票需要企业账户，申请前准备发票抬头及有效纳税人识别号，按申请页面提交资料。\n\n纸质专票仅企业账户可申请，申请时需提供企业开票资料、收件人和邮寄地址，快递费到付。资料审核通过后按开票流程寄出，不承诺快递送达日期。"
    },
    {
      "n": 3,
      "chunk_id": "1879",
      "section_path": "开票细则/开票时效",
      "question": "开票时效",
      "answer": "订单完成后 30 天内可在「我的订单」申请开票，超过 30 天需联系客服核实补开条件，不能直接承诺一定补开。\n\n有效资料审核通过后 3 个工作日内开出发票，电子发票发送至申请邮箱；纸质专票开出后安排邮寄，邮寄耗时不计入开票时限。发票抬头或税号填错时联系客服核实更正，不保证无需审核即可重开。"
    },
    {
      "n": 5,
      "chunk_id": "1839",
      "section_path": "商品与购物 FAQ/如何申请退款",
      "question": "如何申请退款",
      "answer": "在「我的订单」找到对应订单点击「申请退款」,按提示提交,审核通过后原路退回。"
    },
    {
      "n": 7,
      "chunk_id": "1831",
      "section_path": "售后手册/常见问题处理时限",
      "question": "常见问题处理时限",
      "answer": "| 问题类型 | 首次响应 | 处理时限 |\n| --- | --- | --- |\n| 退款 | 2 小时 | 3 个工作日 |\n| 换货 | 2 小时 | 5 个工作日 |\n| 维修 | 4 小时 | 7 个工作日 |\n| 投诉 | 1 小时 | 3 个工作日 |\n| 发票 | 4 小时 | 3 个工作日 |\n| 物流异常 | 2 小时 | 5 个工作日 |\n| 商品咨询 | 1 小时 | 当日 |\n| 价格保护 | 2 小时 | 3 个工作日 |\n| 账户问题 | 2 小时 | 3 个工作日 |\n| 退换货运费 | 2 小时 | 3 个工作日 |\n| 缺货补发 | 2 小时 | 5 个工作日 |\n| 其他 | 4 小时 | 7 个工作日 |"
    },
    {
      "n": 9,
      "chunk_id": "1873",
      "section_path": "退货退款政策/预售与定金",
      "question": "预售与定金",
      "answer": "预售商品以详情页标注的时间发货;定金支付后不支持无理由退定金,尾款未按时支付的,定金按活动规则处理。"
    },
    {
      "n": 10,
      "chunk_id": "1867",
      "section_path": "退货退款政策/换货政策/换货条件",
      "question": "换货条件",
      "answer": "收到商品 7 天内,商品完好且配件齐全的,可申请一次同款换货;不同型号或颜色需先退货再重新下单。"
    },
    {
      "n": 8,
      "chunk_id": "1832",
      "section_path": "售后手册/保修说明",
      "question": "保修说明",
      "answer": "电子类商品保修 12 个月,自签收日起算;人为损坏不在保修范围。"
    },
    {
      "n": 6,
      "chunk_id": "1836",
      "section_path": "售后手册/维修寄修流程",
      "question": "维修寄修流程",
      "answer": "保修期内设备故障,联系客服登记后按指引将设备寄回指定维修点,核验后免费维修并寄回;超保或人为损坏维修可能收取工本费,费用会提前告知。"
    },
    {
      "n": 4,
      "chunk_id": "1871",
      "section_path": "退货退款政策/运输破损处理",
      "question": "运输破损处理",
      "answer": "商品运输途中破损的,请在签收后 48 小时内联系客服并提供开箱视频与照片,核实后可免费补发或退款,相关运费由平台承担。"
    },
    {
      "n": 2,
      "chunk_id": "1843",
      "section_path": "商品与购物 FAQ/发票如何开具",
      "question": "发票如何开具",
      "answer": "在「我的订单」-「申请开票」提交抬头与税号,电子发票将于 3 个工作日内发送至邮箱。"
    }
  ],
  "decision": {
    "useful": false,
    "reason": "证据无挂失证明内容",
    "response_kind": "knowledge",
    "source": "self_check"
  },
  "answer": "目前的知识资料不足以确认这个问题，我无法给出可靠答案。请补充具体商品或适用条件，或联系人工客服确认。",
  "point_verdicts": [],
  "claim_verdicts": [],
  "metrics": {
    "recall_at_5": null,
    "recall_at_10": null,
    "mrr_at_10": null,
    "all_groups_hit_at_5": null,
    "all_groups_hit_at_10": null,
    "candidate_group_coverage": null,
    "prompt_group_coverage": null,
    "answer_point_coverage": null,
    "faithfulness": null,
    "absent_refusal_rate": 1.0,
    "answerable_false_refusal_rate": null
  },
  "error": null,
  "elapsed_ms": 4088.2258999627084,
  "judge_snapshot": {
    "prompt_version": "joint-generation-v2.1",
    "finish_reason": "stop"
  },
  "audit": {
    "audit_version": 1,
    "source_map_id": "d2dd350d860b8141e52306cbbcafb22f97d091194eb1cdc839a528c2990715eb",
    "gold_groups": [],
    "answer_points": [],
    "candidate_ranking": [
      {
        "chunk_id": 1878,
        "score": 0.6452586054801941,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1843,
        "score": 0.5758640766143799,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1879,
        "score": 0.5663228034973145,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1871,
        "score": 0.5103285312652588,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1839,
        "score": 0.4919954538345337,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1836,
        "score": 0.47299909591674805,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1831,
        "score": 0.47143441438674927,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1832,
        "score": 0.4686456620693207,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1873,
        "score": 0.4644458293914795,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1867,
        "score": 0.4631301164627075,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1870,
        "score": 0.45953524112701416,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1865,
        "score": 0.45065855979919434,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1837,
        "score": 0.4483277499675751,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1848,
        "score": 0.44779449701309204,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1840,
        "score": 0.4439329504966736,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1850,
        "score": 0.44006818532943726,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1868,
        "score": 0.4373803436756134,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1866,
        "score": 0.43106693029403687,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1877,
        "score": 0.42871958017349243,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1838,
        "score": 0.4221780300140381,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1869,
        "score": 0.4220655858516693,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1849,
        "score": 0.41479384899139404,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1872,
        "score": 0.41221368312835693,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1835,
        "score": 0.4005711078643799,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1841,
        "score": 0.3995623290538788,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1844,
        "score": 0.3971923589706421,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1851,
        "score": 0.39589112997055054,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1846,
        "score": 0.3933674097061157,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1834,
        "score": 0.3871292173862457,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1876,
        "score": 0.3857405185699463,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1842,
        "score": 0.3832434415817261,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1847,
        "score": 0.3829110562801361,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1875,
        "score": 0.37594008445739746,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1852,
        "score": 0.36977824568748474,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1874,
        "score": 0.3679296672344208,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1858,
        "score": 0.36692681908607483,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1833,
        "score": 0.3643520474433899,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1857,
        "score": 0.36350396275520325,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1845,
        "score": 0.36295390129089355,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1856,
        "score": 0.35462862253189087,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1862,
        "score": 0.3532634675502777,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1863,
        "score": 0.33457714319229126,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1861,
        "score": 0.3302253782749176,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1880,
        "score": 0.3273769021034241,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1864,
        "score": 0.32489070296287537,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1853,
        "score": 0.3189391791820526,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1855,
        "score": 0.30531826615333557,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1859,
        "score": 0.29268166422843933,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1854,
        "score": 0.2893209159374237,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1860,
        "score": 0.28825312852859497,
        "score_kind": "cosine"
      }
    ],
    "final_ranking": [
      {
        "chunk_id": 1878,
        "score": 0.6452586054801941,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1843,
        "score": 0.5758640766143799,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1879,
        "score": 0.5663228034973145,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1871,
        "score": 0.5103285312652588,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1839,
        "score": 0.4919954538345337,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1836,
        "score": 0.47299909591674805,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1831,
        "score": 0.47143441438674927,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1832,
        "score": 0.4686456620693207,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1873,
        "score": 0.4644458293914795,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1867,
        "score": 0.4631301164627075,
        "score_kind": "cosine"
      }
    ]
  }
}
````

### D3 / bm25

````json
{
  "eval_id": "D3",
  "strategy": "bm25",
  "bucket": "D_unanswerable",
  "difficulty": "absent",
  "category": null,
  "should_refuse": true,
  "refused": true,
  "status": "completed",
  "stage": "complete",
  "query": "纸质发票遗失后能申请挂失证明吗",
  "query_plan": {
    "standard": "纸质发票遗失后能申请挂失证明吗",
    "expansions": []
  },
  "mapped_groups": [],
  "candidate_ids": [
    1878,
    1879,
    1843,
    1848,
    1839,
    1850,
    1840,
    1867,
    1870,
    1831
  ],
  "final_ids": [
    1878,
    1879,
    1843,
    1848,
    1839,
    1850,
    1840,
    1867,
    1870,
    1831
  ],
  "prompt_citations": [
    {
      "n": 1,
      "chunk_id": "1878",
      "section_path": "开票细则/可开票类型",
      "question": "可开票类型",
      "answer": "本演示店提供电子普通发票、电子专用发票和纸质专用发票。电子普通发票可按订单申请；电子专票需要企业账户，申请前准备发票抬头及有效纳税人识别号，按申请页面提交资料。\n\n纸质专票仅企业账户可申请，申请时需提供企业开票资料、收件人和邮寄地址，快递费到付。资料审核通过后按开票流程寄出，不承诺快递送达日期。"
    },
    {
      "n": 3,
      "chunk_id": "1843",
      "section_path": "商品与购物 FAQ/发票如何开具",
      "question": "发票如何开具",
      "answer": "在「我的订单」-「申请开票」提交抬头与税号,电子发票将于 3 个工作日内发送至邮箱。"
    },
    {
      "n": 5,
      "chunk_id": "1839",
      "section_path": "商品与购物 FAQ/如何申请退款",
      "question": "如何申请退款",
      "answer": "在「我的订单」找到对应订单点击「申请退款」,按提示提交,审核通过后原路退回。"
    },
    {
      "n": 7,
      "chunk_id": "1840",
      "section_path": "商品与购物 FAQ/换货流程怎么走",
      "question": "换货流程怎么走",
      "answer": "收到商品 7 天内可申请换货,联系客服登记后将商品寄回,平台核验无误后补发新品。"
    },
    {
      "n": 9,
      "chunk_id": "1870",
      "section_path": "退货退款政策/质量问题与保修",
      "question": "质量问题与保修",
      "answer": "电子类商品自签收起保修 12 个月,保修期内非人为损坏可申请免费维修或换货;人为损坏、超保商品维修可能收取工本费。"
    },
    {
      "n": 10,
      "chunk_id": "1831",
      "section_path": "售后手册/常见问题处理时限",
      "question": "常见问题处理时限",
      "answer": "| 问题类型 | 首次响应 | 处理时限 |\n| --- | --- | --- |\n| 退款 | 2 小时 | 3 个工作日 |\n| 换货 | 2 小时 | 5 个工作日 |\n| 维修 | 4 小时 | 7 个工作日 |\n| 投诉 | 1 小时 | 3 个工作日 |\n| 发票 | 4 小时 | 3 个工作日 |\n| 物流异常 | 2 小时 | 5 个工作日 |\n| 商品咨询 | 1 小时 | 当日 |\n| 价格保护 | 2 小时 | 3 个工作日 |\n| 账户问题 | 2 小时 | 3 个工作日 |\n| 退换货运费 | 2 小时 | 3 个工作日 |\n| 缺货补发 | 2 小时 | 5 个工作日 |\n| 其他 | 4 小时 | 7 个工作日 |"
    },
    {
      "n": 8,
      "chunk_id": "1867",
      "section_path": "退货退款政策/换货政策/换货条件",
      "question": "换货条件",
      "answer": "收到商品 7 天内,商品完好且配件齐全的,可申请一次同款换货;不同型号或颜色需先退货再重新下单。"
    },
    {
      "n": 6,
      "chunk_id": "1850",
      "section_path": "商品与购物 FAQ/价格保护怎么申请",
      "question": "价格保护怎么申请",
      "answer": "自营商品支持下单后 7 天内价保,期间若同款降价可在「我的订单」-「申请价保」提交,差价将退回原支付渠道。"
    },
    {
      "n": 4,
      "chunk_id": "1848",
      "section_path": "商品与购物 FAQ/订单可以修改或取消吗",
      "question": "订单可以修改或取消吗",
      "answer": "订单未发货前可在「我的订单」自助取消;已发货订单无法修改收货信息,可拒收后走退款流程。修改商品数量需取消后重新下单。"
    },
    {
      "n": 2,
      "chunk_id": "1879",
      "section_path": "开票细则/开票时效",
      "question": "开票时效",
      "answer": "订单完成后 30 天内可在「我的订单」申请开票，超过 30 天需联系客服核实补开条件，不能直接承诺一定补开。\n\n有效资料审核通过后 3 个工作日内开出发票，电子发票发送至申请邮箱；纸质专票开出后安排邮寄，邮寄耗时不计入开票时限。发票抬头或税号填错时联系客服核实更正，不保证无需审核即可重开。"
    }
  ],
  "decision": {
    "useful": false,
    "reason": "无纸质发票遗失挂失证明的证据",
    "response_kind": "knowledge",
    "source": "self_check"
  },
  "answer": "目前的知识资料不足以确认这个问题，我无法给出可靠答案。请补充具体商品或适用条件，或联系人工客服确认。",
  "point_verdicts": [],
  "claim_verdicts": [],
  "metrics": {
    "recall_at_5": null,
    "recall_at_10": null,
    "mrr_at_10": null,
    "all_groups_hit_at_5": null,
    "all_groups_hit_at_10": null,
    "candidate_group_coverage": null,
    "prompt_group_coverage": null,
    "answer_point_coverage": null,
    "faithfulness": null,
    "absent_refusal_rate": 1.0,
    "answerable_false_refusal_rate": null
  },
  "error": null,
  "elapsed_ms": 6769.891900010407,
  "judge_snapshot": {
    "prompt_version": "joint-generation-v2.1",
    "finish_reason": "stop"
  },
  "audit": {
    "audit_version": 1,
    "source_map_id": "d2dd350d860b8141e52306cbbcafb22f97d091194eb1cdc839a528c2990715eb",
    "gold_groups": [],
    "answer_points": [],
    "candidate_ranking": [
      {
        "chunk_id": 1878,
        "score": 10.285421371459961,
        "score_kind": "bm25"
      },
      {
        "chunk_id": 1879,
        "score": 8.083020210266113,
        "score_kind": "bm25"
      },
      {
        "chunk_id": 1843,
        "score": 5.832973480224609,
        "score_kind": "bm25"
      },
      {
        "chunk_id": 1848,
        "score": 3.737774610519409,
        "score_kind": "bm25"
      },
      {
        "chunk_id": 1839,
        "score": 2.8332555294036865,
        "score_kind": "bm25"
      },
      {
        "chunk_id": 1850,
        "score": 2.6836564540863037,
        "score_kind": "bm25"
      },
      {
        "chunk_id": 1840,
        "score": 2.1490039825439453,
        "score_kind": "bm25"
      },
      {
        "chunk_id": 1867,
        "score": 2.071161985397339,
        "score_kind": "bm25"
      },
      {
        "chunk_id": 1870,
        "score": 1.9644274711608887,
        "score_kind": "bm25"
      },
      {
        "chunk_id": 1831,
        "score": 1.7175705432891846,
        "score_kind": "bm25"
      }
    ],
    "final_ranking": [
      {
        "chunk_id": 1878,
        "score": 10.285421371459961,
        "score_kind": "bm25"
      },
      {
        "chunk_id": 1879,
        "score": 8.083020210266113,
        "score_kind": "bm25"
      },
      {
        "chunk_id": 1843,
        "score": 5.832973480224609,
        "score_kind": "bm25"
      },
      {
        "chunk_id": 1848,
        "score": 3.737774610519409,
        "score_kind": "bm25"
      },
      {
        "chunk_id": 1839,
        "score": 2.8332555294036865,
        "score_kind": "bm25"
      },
      {
        "chunk_id": 1850,
        "score": 2.6836564540863037,
        "score_kind": "bm25"
      },
      {
        "chunk_id": 1840,
        "score": 2.1490039825439453,
        "score_kind": "bm25"
      },
      {
        "chunk_id": 1867,
        "score": 2.071161985397339,
        "score_kind": "bm25"
      },
      {
        "chunk_id": 1870,
        "score": 1.9644274711608887,
        "score_kind": "bm25"
      },
      {
        "chunk_id": 1831,
        "score": 1.7175705432891846,
        "score_kind": "bm25"
      }
    ]
  }
}
````

### D3 / hybrid

````json
{
  "eval_id": "D3",
  "strategy": "hybrid",
  "bucket": "D_unanswerable",
  "difficulty": "absent",
  "category": null,
  "should_refuse": true,
  "refused": true,
  "status": "completed",
  "stage": "complete",
  "query": "纸质发票遗失后能申请挂失证明吗",
  "query_plan": {
    "standard": "纸质发票遗失后能申请挂失证明吗",
    "expansions": []
  },
  "mapped_groups": [],
  "candidate_ids": [
    1878,
    1843,
    1879,
    1839,
    1831,
    1848,
    1867,
    1870,
    1850,
    1840,
    1871,
    1836,
    1832,
    1873,
    1865,
    1837,
    1868,
    1866,
    1877,
    1838,
    1869,
    1849,
    1872,
    1835,
    1841,
    1844,
    1851,
    1846,
    1834,
    1876,
    1842,
    1847,
    1875,
    1852,
    1874,
    1858,
    1833,
    1857,
    1845,
    1856,
    1862,
    1863,
    1861,
    1880,
    1864,
    1853,
    1855,
    1859,
    1854,
    1860
  ],
  "final_ids": [
    1878,
    1843,
    1879,
    1839,
    1831,
    1848,
    1867,
    1870,
    1850,
    1840
  ],
  "prompt_citations": [
    {
      "n": 1,
      "chunk_id": "1878",
      "section_path": "开票细则/可开票类型",
      "question": "可开票类型",
      "answer": "本演示店提供电子普通发票、电子专用发票和纸质专用发票。电子普通发票可按订单申请；电子专票需要企业账户，申请前准备发票抬头及有效纳税人识别号，按申请页面提交资料。\n\n纸质专票仅企业账户可申请，申请时需提供企业开票资料、收件人和邮寄地址，快递费到付。资料审核通过后按开票流程寄出，不承诺快递送达日期。"
    },
    {
      "n": 3,
      "chunk_id": "1879",
      "section_path": "开票细则/开票时效",
      "question": "开票时效",
      "answer": "订单完成后 30 天内可在「我的订单」申请开票，超过 30 天需联系客服核实补开条件，不能直接承诺一定补开。\n\n有效资料审核通过后 3 个工作日内开出发票，电子发票发送至申请邮箱；纸质专票开出后安排邮寄，邮寄耗时不计入开票时限。发票抬头或税号填错时联系客服核实更正，不保证无需审核即可重开。"
    },
    {
      "n": 5,
      "chunk_id": "1831",
      "section_path": "售后手册/常见问题处理时限",
      "question": "常见问题处理时限",
      "answer": "| 问题类型 | 首次响应 | 处理时限 |\n| --- | --- | --- |\n| 退款 | 2 小时 | 3 个工作日 |\n| 换货 | 2 小时 | 5 个工作日 |\n| 维修 | 4 小时 | 7 个工作日 |\n| 投诉 | 1 小时 | 3 个工作日 |\n| 发票 | 4 小时 | 3 个工作日 |\n| 物流异常 | 2 小时 | 5 个工作日 |\n| 商品咨询 | 1 小时 | 当日 |\n| 价格保护 | 2 小时 | 3 个工作日 |\n| 账户问题 | 2 小时 | 3 个工作日 |\n| 退换货运费 | 2 小时 | 3 个工作日 |\n| 缺货补发 | 2 小时 | 5 个工作日 |\n| 其他 | 4 小时 | 7 个工作日 |"
    },
    {
      "n": 7,
      "chunk_id": "1867",
      "section_path": "退货退款政策/换货政策/换货条件",
      "question": "换货条件",
      "answer": "收到商品 7 天内,商品完好且配件齐全的,可申请一次同款换货;不同型号或颜色需先退货再重新下单。"
    },
    {
      "n": 9,
      "chunk_id": "1850",
      "section_path": "商品与购物 FAQ/价格保护怎么申请",
      "question": "价格保护怎么申请",
      "answer": "自营商品支持下单后 7 天内价保,期间若同款降价可在「我的订单」-「申请价保」提交,差价将退回原支付渠道。"
    },
    {
      "n": 10,
      "chunk_id": "1840",
      "section_path": "商品与购物 FAQ/换货流程怎么走",
      "question": "换货流程怎么走",
      "answer": "收到商品 7 天内可申请换货,联系客服登记后将商品寄回,平台核验无误后补发新品。"
    },
    {
      "n": 8,
      "chunk_id": "1870",
      "section_path": "退货退款政策/质量问题与保修",
      "question": "质量问题与保修",
      "answer": "电子类商品自签收起保修 12 个月,保修期内非人为损坏可申请免费维修或换货;人为损坏、超保商品维修可能收取工本费。"
    },
    {
      "n": 6,
      "chunk_id": "1848",
      "section_path": "商品与购物 FAQ/订单可以修改或取消吗",
      "question": "订单可以修改或取消吗",
      "answer": "订单未发货前可在「我的订单」自助取消;已发货订单无法修改收货信息,可拒收后走退款流程。修改商品数量需取消后重新下单。"
    },
    {
      "n": 4,
      "chunk_id": "1839",
      "section_path": "商品与购物 FAQ/如何申请退款",
      "question": "如何申请退款",
      "answer": "在「我的订单」找到对应订单点击「申请退款」,按提示提交,审核通过后原路退回。"
    },
    {
      "n": 2,
      "chunk_id": "1843",
      "section_path": "商品与购物 FAQ/发票如何开具",
      "question": "发票如何开具",
      "answer": "在「我的订单」-「申请开票」提交抬头与税号,电子发票将于 3 个工作日内发送至邮箱。"
    }
  ],
  "decision": {
    "useful": false,
    "reason": "无纸质发票挂失证明相关证据",
    "response_kind": "knowledge",
    "source": "self_check"
  },
  "answer": "目前的知识资料不足以确认这个问题，我无法给出可靠答案。请补充具体商品或适用条件，或联系人工客服确认。",
  "point_verdicts": [],
  "claim_verdicts": [
    {
      "claim": "目前的知识资料不足以确认纸质发票遗失后能否申请挂失证明",
      "supported": false,
      "reason": "证据中无任何关于发票挂失或遗失证明的内容，仅凭证据沉默不能证明资料不足的断言，故不支持"
    },
    {
      "claim": "无法给出可靠答案",
      "supported": false,
      "reason": "该断言依赖资料不足这一前提，而支持证据未能证明资料不足以回答该问题，故不支持"
    }
  ],
  "metrics": {
    "recall_at_5": null,
    "recall_at_10": null,
    "mrr_at_10": null,
    "all_groups_hit_at_5": null,
    "all_groups_hit_at_10": null,
    "candidate_group_coverage": null,
    "prompt_group_coverage": null,
    "answer_point_coverage": null,
    "faithfulness": 0.0,
    "absent_refusal_rate": 1.0,
    "answerable_false_refusal_rate": null
  },
  "error": null,
  "elapsed_ms": 7034.243899863213,
  "judge_snapshot": {
    "prompt_version": "joint-generation-v2.1",
    "finish_reason": "stop"
  },
  "audit": {
    "audit_version": 1,
    "source_map_id": "d2dd350d860b8141e52306cbbcafb22f97d091194eb1cdc839a528c2990715eb",
    "gold_groups": [],
    "answer_points": [],
    "candidate_ranking": [
      {
        "chunk_id": 1878,
        "score": 0.032786883413791656,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1843,
        "score": 0.0320020467042923,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1879,
        "score": 0.0320020467042923,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1839,
        "score": 0.03076923079788685,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1831,
        "score": 0.02921108715236187,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1848,
        "score": 0.029138512909412384,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1867,
        "score": 0.028991596773266792,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1870,
        "score": 0.028577260673046112,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1850,
        "score": 0.02830941043794155,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1840,
        "score": 0.028258707374334335,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1871,
        "score": 0.015625,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1836,
        "score": 0.01515151560306549,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1832,
        "score": 0.014705882407724857,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1873,
        "score": 0.014492753893136978,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1865,
        "score": 0.013888888992369175,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1837,
        "score": 0.013698630034923553,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1868,
        "score": 0.012987012974917889,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1866,
        "score": 0.012820512987673283,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1877,
        "score": 0.012658228166401386,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1838,
        "score": 0.012500000186264515,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1869,
        "score": 0.012345679104328156,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1849,
        "score": 0.012195121496915817,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1872,
        "score": 0.012048192322254181,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1835,
        "score": 0.011904762126505375,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1841,
        "score": 0.0117647061124444,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1844,
        "score": 0.011627906933426857,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1851,
        "score": 0.01149425283074379,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1846,
        "score": 0.011363636702299118,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1834,
        "score": 0.01123595517128706,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1876,
        "score": 0.011111111380159855,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1842,
        "score": 0.010989011265337467,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1847,
        "score": 0.010869565419852734,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1875,
        "score": 0.01075268816202879,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1852,
        "score": 0.010638297535479069,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1874,
        "score": 0.010526316240429878,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1858,
        "score": 0.010416666977107525,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1833,
        "score": 0.010309278033673763,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1857,
        "score": 0.010204081423580647,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1845,
        "score": 0.010101010091602802,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1856,
        "score": 0.009999999776482582,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1862,
        "score": 0.009900989942252636,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1863,
        "score": 0.009803921915590763,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1861,
        "score": 0.009708737954497337,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1880,
        "score": 0.009615384973585606,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1864,
        "score": 0.009523809887468815,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1853,
        "score": 0.009433962404727936,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1855,
        "score": 0.009345794096589088,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1859,
        "score": 0.009259259328246117,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1854,
        "score": 0.00917431153357029,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1860,
        "score": 0.00909090880304575,
        "score_kind": "rrf"
      }
    ],
    "final_ranking": [
      {
        "chunk_id": 1878,
        "score": 0.032786883413791656,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1843,
        "score": 0.0320020467042923,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1879,
        "score": 0.0320020467042923,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1839,
        "score": 0.03076923079788685,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1831,
        "score": 0.02921108715236187,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1848,
        "score": 0.029138512909412384,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1867,
        "score": 0.028991596773266792,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1870,
        "score": 0.028577260673046112,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1850,
        "score": 0.02830941043794155,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1840,
        "score": 0.028258707374334335,
        "score_kind": "rrf"
      }
    ]
  }
}
````

### D3 / hybrid_rerank

````json
{
  "eval_id": "D3",
  "strategy": "hybrid_rerank",
  "bucket": "D_unanswerable",
  "difficulty": "absent",
  "category": null,
  "should_refuse": true,
  "refused": true,
  "status": "completed",
  "stage": "complete",
  "query": "纸质发票遗失后能申请挂失证明吗",
  "query_plan": {
    "standard": "纸质发票遗失后能申请挂失证明吗",
    "expansions": []
  },
  "mapped_groups": [],
  "candidate_ids": [
    1878,
    1843,
    1879,
    1839,
    1831,
    1848,
    1867,
    1870,
    1850,
    1840,
    1871,
    1836,
    1832,
    1873,
    1865,
    1837,
    1868,
    1866,
    1877,
    1838,
    1869,
    1849,
    1872,
    1835,
    1841,
    1844,
    1851,
    1846,
    1834,
    1876,
    1842,
    1847,
    1875,
    1852,
    1874,
    1858,
    1833,
    1857,
    1845,
    1856,
    1862,
    1863,
    1861,
    1880,
    1864,
    1853,
    1855,
    1859,
    1854,
    1860
  ],
  "final_ids": [
    1879,
    1878,
    1843,
    1870,
    1871,
    1839,
    1865,
    1866,
    1832,
    1831
  ],
  "prompt_citations": [
    {
      "n": 1,
      "chunk_id": "1879",
      "section_path": "开票细则/开票时效",
      "question": "开票时效",
      "answer": "订单完成后 30 天内可在「我的订单」申请开票，超过 30 天需联系客服核实补开条件，不能直接承诺一定补开。\n\n有效资料审核通过后 3 个工作日内开出发票，电子发票发送至申请邮箱；纸质专票开出后安排邮寄，邮寄耗时不计入开票时限。发票抬头或税号填错时联系客服核实更正，不保证无需审核即可重开。"
    },
    {
      "n": 3,
      "chunk_id": "1843",
      "section_path": "商品与购物 FAQ/发票如何开具",
      "question": "发票如何开具",
      "answer": "在「我的订单」-「申请开票」提交抬头与税号,电子发票将于 3 个工作日内发送至邮箱。"
    },
    {
      "n": 5,
      "chunk_id": "1871",
      "section_path": "退货退款政策/运输破损处理",
      "question": "运输破损处理",
      "answer": "商品运输途中破损的,请在签收后 48 小时内联系客服并提供开箱视频与照片,核实后可免费补发或退款,相关运费由平台承担。"
    },
    {
      "n": 7,
      "chunk_id": "1865",
      "section_path": "退货退款政策/无理由退货/适用范围",
      "question": "适用范围",
      "answer": "自签收之日起 7 天内,商品完好、不影响二次销售的,支持无理由退货。定制类、生鲜类商品除外。"
    },
    {
      "n": 9,
      "chunk_id": "1832",
      "section_path": "售后手册/保修说明",
      "question": "保修说明",
      "answer": "电子类商品保修 12 个月,自签收日起算;人为损坏不在保修范围。"
    },
    {
      "n": 10,
      "chunk_id": "1831",
      "section_path": "售后手册/常见问题处理时限",
      "question": "常见问题处理时限",
      "answer": "| 问题类型 | 首次响应 | 处理时限 |\n| --- | --- | --- |\n| 退款 | 2 小时 | 3 个工作日 |\n| 换货 | 2 小时 | 5 个工作日 |\n| 维修 | 4 小时 | 7 个工作日 |\n| 投诉 | 1 小时 | 3 个工作日 |\n| 发票 | 4 小时 | 3 个工作日 |\n| 物流异常 | 2 小时 | 5 个工作日 |\n| 商品咨询 | 1 小时 | 当日 |\n| 价格保护 | 2 小时 | 3 个工作日 |\n| 账户问题 | 2 小时 | 3 个工作日 |\n| 退换货运费 | 2 小时 | 3 个工作日 |\n| 缺货补发 | 2 小时 | 5 个工作日 |\n| 其他 | 4 小时 | 7 个工作日 |"
    },
    {
      "n": 8,
      "chunk_id": "1866",
      "section_path": "退货退款政策/无理由退货/退款时效",
      "question": "退款时效",
      "answer": "退货商品经平台核验通过后,退款原路退回,到账时效以平台售后规则为准。"
    },
    {
      "n": 6,
      "chunk_id": "1839",
      "section_path": "商品与购物 FAQ/如何申请退款",
      "question": "如何申请退款",
      "answer": "在「我的订单」找到对应订单点击「申请退款」,按提示提交,审核通过后原路退回。"
    },
    {
      "n": 4,
      "chunk_id": "1870",
      "section_path": "退货退款政策/质量问题与保修",
      "question": "质量问题与保修",
      "answer": "电子类商品自签收起保修 12 个月,保修期内非人为损坏可申请免费维修或换货;人为损坏、超保商品维修可能收取工本费。"
    },
    {
      "n": 2,
      "chunk_id": "1878",
      "section_path": "开票细则/可开票类型",
      "question": "可开票类型",
      "answer": "本演示店提供电子普通发票、电子专用发票和纸质专用发票。电子普通发票可按订单申请；电子专票需要企业账户，申请前准备发票抬头及有效纳税人识别号，按申请页面提交资料。\n\n纸质专票仅企业账户可申请，申请时需提供企业开票资料、收件人和邮寄地址，快递费到付。资料审核通过后按开票流程寄出，不承诺快递送达日期。"
    }
  ],
  "decision": {
    "useful": false,
    "reason": "无发票挂失证明相关证据",
    "response_kind": "knowledge",
    "source": "self_check"
  },
  "answer": "目前的知识资料不足以确认这个问题，我无法给出可靠答案。请补充具体商品或适用条件，或联系人工客服确认。",
  "point_verdicts": [],
  "claim_verdicts": [],
  "metrics": {
    "recall_at_5": null,
    "recall_at_10": null,
    "mrr_at_10": null,
    "all_groups_hit_at_5": null,
    "all_groups_hit_at_10": null,
    "candidate_group_coverage": null,
    "prompt_group_coverage": null,
    "answer_point_coverage": null,
    "faithfulness": null,
    "absent_refusal_rate": 1.0,
    "answerable_false_refusal_rate": null
  },
  "error": null,
  "elapsed_ms": 5389.364399947226,
  "judge_snapshot": {
    "prompt_version": "joint-generation-v2.1",
    "finish_reason": "stop"
  },
  "audit": {
    "audit_version": 1,
    "source_map_id": "d2dd350d860b8141e52306cbbcafb22f97d091194eb1cdc839a528c2990715eb",
    "gold_groups": [],
    "answer_points": [],
    "candidate_ranking": [
      {
        "chunk_id": 1878,
        "score": 0.032786883413791656,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1843,
        "score": 0.0320020467042923,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1879,
        "score": 0.0320020467042923,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1839,
        "score": 0.03076923079788685,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1831,
        "score": 0.02921108715236187,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1848,
        "score": 0.029138512909412384,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1867,
        "score": 0.028991596773266792,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1870,
        "score": 0.028577260673046112,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1850,
        "score": 0.02830941043794155,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1840,
        "score": 0.028258707374334335,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1871,
        "score": 0.015625,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1836,
        "score": 0.01515151560306549,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1832,
        "score": 0.014705882407724857,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1873,
        "score": 0.014492753893136978,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1865,
        "score": 0.013888888992369175,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1837,
        "score": 0.013698630034923553,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1868,
        "score": 0.012987012974917889,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1866,
        "score": 0.012820512987673283,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1877,
        "score": 0.012658228166401386,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1838,
        "score": 0.012500000186264515,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1869,
        "score": 0.012345679104328156,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1849,
        "score": 0.012195121496915817,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1872,
        "score": 0.012048192322254181,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1835,
        "score": 0.011904762126505375,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1841,
        "score": 0.0117647061124444,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1844,
        "score": 0.011627906933426857,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1851,
        "score": 0.01149425283074379,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1846,
        "score": 0.011363636702299118,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1834,
        "score": 0.01123595517128706,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1876,
        "score": 0.011111111380159855,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1842,
        "score": 0.010989011265337467,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1847,
        "score": 0.010869565419852734,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1875,
        "score": 0.01075268816202879,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1852,
        "score": 0.010638297535479069,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1874,
        "score": 0.010526316240429878,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1858,
        "score": 0.010416666977107525,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1833,
        "score": 0.010309278033673763,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1857,
        "score": 0.010204081423580647,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1845,
        "score": 0.010101010091602802,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1856,
        "score": 0.009999999776482582,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1862,
        "score": 0.009900989942252636,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1863,
        "score": 0.009803921915590763,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1861,
        "score": 0.009708737954497337,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1880,
        "score": 0.009615384973585606,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1864,
        "score": 0.009523809887468815,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1853,
        "score": 0.009433962404727936,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1855,
        "score": 0.009345794096589088,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1859,
        "score": 0.009259259328246117,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1854,
        "score": 0.00917431153357029,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1860,
        "score": 0.00909090880304575,
        "score_kind": "rrf"
      }
    ],
    "final_ranking": [
      {
        "chunk_id": 1879,
        "score": 0.08952348679304123,
        "score_kind": "rerank"
      },
      {
        "chunk_id": 1878,
        "score": 0.039517004042863846,
        "score_kind": "rerank"
      },
      {
        "chunk_id": 1843,
        "score": 0.0009940483141690493,
        "score_kind": "rerank"
      },
      {
        "chunk_id": 1870,
        "score": 0.000634574331343174,
        "score_kind": "rerank"
      },
      {
        "chunk_id": 1871,
        "score": 0.00040183847886510193,
        "score_kind": "rerank"
      },
      {
        "chunk_id": 1839,
        "score": 0.00023717487056273967,
        "score_kind": "rerank"
      },
      {
        "chunk_id": 1865,
        "score": 0.00023339962353929877,
        "score_kind": "rerank"
      },
      {
        "chunk_id": 1866,
        "score": 0.00021644022490363568,
        "score_kind": "rerank"
      },
      {
        "chunk_id": 1832,
        "score": 0.00020946025324519724,
        "score_kind": "rerank"
      },
      {
        "chunk_id": 1831,
        "score": 0.00016952886653598398,
        "score_kind": "rerank"
      }
    ]
  }
}
````

### E2 / dense

````json
{
  "eval_id": "E2",
  "strategy": "dense",
  "bucket": "E_multi",
  "difficulty": "multi",
  "category": null,
  "should_refuse": false,
  "refused": false,
  "status": "completed",
  "stage": "complete",
  "query": "东西不想要了要退货,寄回去的运费谁承担,钱多久回来",
  "query_plan": {
    "standard": "东西不想要了要退货,寄回去的运费谁承担,钱多久回来",
    "expansions": []
  },
  "mapped_groups": [
    {
      "group_id": "g1",
      "alternatives": [
        [
          1865
        ],
        [
          1838
        ]
      ]
    },
    {
      "group_id": "g2",
      "alternatives": [
        [
          1869
        ]
      ]
    },
    {
      "group_id": "g3",
      "alternatives": [
        [
          1866
        ]
      ]
    }
  ],
  "candidate_ids": [
    1869,
    1871,
    1868,
    1865,
    1866,
    1838,
    1840,
    1873,
    1842,
    1870,
    1831,
    1841,
    1867,
    1836,
    1839,
    1837,
    1849,
    1850,
    1847,
    1851,
    1872,
    1879,
    1832,
    1848,
    1876,
    1843,
    1877,
    1835,
    1844,
    1874,
    1845,
    1875,
    1878,
    1846,
    1834,
    1853,
    1855,
    1858,
    1857,
    1856,
    1854,
    1833,
    1862,
    1880,
    1852,
    1860,
    1863,
    1861,
    1864,
    1859
  ],
  "final_ids": [
    1869,
    1871,
    1868,
    1865,
    1866,
    1838,
    1840,
    1873,
    1842,
    1870
  ],
  "prompt_citations": [
    {
      "n": 1,
      "chunk_id": "1869",
      "section_path": "退货退款政策/退换货运费承担",
      "question": "退换货运费承担",
      "answer": "无理由退货的退回运费由买家承担;因商品质量问题、发错货、少发漏发导致的退换货,运费由平台承担。运费承担以平台售后规则最终判定为准。"
    },
    {
      "n": 3,
      "chunk_id": "1868",
      "section_path": "退货退款政策/换货政策/换货运费",
      "question": "换货运费",
      "answer": "非质量问题的换货,往返运费由买家承担;因质量问题或发错货的换货,往返运费由平台承担。"
    },
    {
      "n": 5,
      "chunk_id": "1866",
      "section_path": "退货退款政策/无理由退货/退款时效",
      "question": "退款时效",
      "answer": "退货商品经平台核验通过后,退款原路退回,到账时效以平台售后规则为准。"
    },
    {
      "n": 7,
      "chunk_id": "1840",
      "section_path": "商品与购物 FAQ/换货流程怎么走",
      "question": "换货流程怎么走",
      "answer": "收到商品 7 天内可申请换货,联系客服登记后将商品寄回,平台核验无误后补发新品。"
    },
    {
      "n": 9,
      "chunk_id": "1842",
      "section_path": "商品与购物 FAQ/运费怎么算",
      "question": "运费怎么算",
      "answer": "单笔订单满 99 元包邮,未满收取 10 元运费,偏远地区运费另计。邮费即运费,按此规则收取。"
    },
    {
      "n": 10,
      "chunk_id": "1870",
      "section_path": "退货退款政策/质量问题与保修",
      "question": "质量问题与保修",
      "answer": "电子类商品自签收起保修 12 个月,保修期内非人为损坏可申请免费维修或换货;人为损坏、超保商品维修可能收取工本费。"
    },
    {
      "n": 8,
      "chunk_id": "1873",
      "section_path": "退货退款政策/预售与定金",
      "question": "预售与定金",
      "answer": "预售商品以详情页标注的时间发货;定金支付后不支持无理由退定金,尾款未按时支付的,定金按活动规则处理。"
    },
    {
      "n": 6,
      "chunk_id": "1838",
      "section_path": "商品与购物 FAQ/退货政策是什么",
      "question": "退货政策是什么",
      "answer": "支持 7 天无理由退货,商品需保持完好、不影响二次销售,具体以平台售后规则为准。"
    },
    {
      "n": 4,
      "chunk_id": "1865",
      "section_path": "退货退款政策/无理由退货/适用范围",
      "question": "适用范围",
      "answer": "自签收之日起 7 天内,商品完好、不影响二次销售的,支持无理由退货。定制类、生鲜类商品除外。"
    },
    {
      "n": 2,
      "chunk_id": "1871",
      "section_path": "退货退款政策/运输破损处理",
      "question": "运输破损处理",
      "answer": "商品运输途中破损的,请在签收后 48 小时内联系客服并提供开箱视频与照片,核实后可免费补发或退款,相关运费由平台承担。"
    }
  ],
  "decision": {
    "useful": true,
    "reason": "运费承担有明确证据；退款时效仅称以平台规则为准，无具体天数",
    "response_kind": "knowledge",
    "source": null
  },
  "answer": "您好！关于您的退货问题，为您说明如下：\n\n**关于运费承担**：无理由退货（即不想要了）的退回运费由买家承担；如因商品质量问题、发错货、少发漏发导致的退货，运费由平台承担，具体以平台售后规则最终判定为准。[1]\n\n**关于退款时效**：退货商品经平台核验通过后，退款将原路退回，到账时效以平台售后规则为准，我们无法承诺具体到账日期。[5]\n\n另外提醒您：自签收之日起 7 天内、商品完好且不影响二次销售的，支持无理由退货（定制类、生鲜类除外）。[4][6]\n\n如需办理退货，请提供订单号，我可以为您进一步查询～",
  "point_verdicts": [
    {
      "point_id": "p1",
      "covered": true,
      "reason": "回答提及自签收之日起7天内、商品完好不影响二次销售支持无理由退货，定制类生鲜类除外，条件完整保留"
    },
    {
      "point_id": "p2",
      "covered": true,
      "reason": "回答说明无理由退货运费买家承担，质量问题等由平台承担，以平台售后规则最终判定为准，区分条件完整"
    },
    {
      "point_id": "p3",
      "covered": true,
      "reason": "回答说明平台核验通过后退款原路退回，到账时效以平台售后规则为准，未给固定天数，与要点一致"
    }
  ],
  "claim_verdicts": [
    {
      "claim": "无理由退货的退回运费由买家承担",
      "supported": true,
      "reason": "证据1明确无理由退货退回运费由买家承担"
    },
    {
      "claim": "因商品质量问题、发错货、少发漏发导致的退货，运费由平台承担",
      "supported": true,
      "reason": "证据1明确质量、发错货、少发漏发退货运费由平台承担"
    },
    {
      "claim": "运费承担以平台售后规则最终判定为准",
      "supported": true,
      "reason": "证据1明确运费承担以平台售后规则最终判定为准"
    },
    {
      "claim": "退货商品经平台核验通过后，退款将原路退回",
      "supported": true,
      "reason": "证据5明确核验通过后退款原路退回"
    },
    {
      "claim": "退款到账时效以平台售后规则为准，无法承诺具体到账日期",
      "supported": true,
      "reason": "证据5明确到账时效以平台售后规则为准，未给固定天数"
    },
    {
      "claim": "自签收之日起7天内、商品完好且不影响二次销售的，支持无理由退货（定制类、生鲜类除外）",
      "supported": true,
      "reason": "证据4明确7天内商品完好不影响二次销售支持无理由退货，定制类生鲜类除外"
    }
  ],
  "metrics": {
    "recall_at_5": 1.0,
    "recall_at_10": 1.0,
    "mrr_at_10": 1.0,
    "all_groups_hit_at_5": 1.0,
    "all_groups_hit_at_10": 1.0,
    "candidate_group_coverage": 1.0,
    "prompt_group_coverage": 1.0,
    "answer_point_coverage": 1.0,
    "faithfulness": 1.0,
    "absent_refusal_rate": null,
    "answerable_false_refusal_rate": 0.0
  },
  "error": null,
  "elapsed_ms": 12160.678999964148,
  "judge_snapshot": {
    "prompt_version": "joint-generation-v2.1",
    "finish_reason": "stop"
  },
  "audit": {
    "audit_version": 1,
    "source_map_id": "d2dd350d860b8141e52306cbbcafb22f97d091194eb1cdc839a528c2990715eb",
    "gold_groups": [
      {
        "group_id": "g1",
        "alternatives": [
          [
            "returns-policy.md:001:49f98ddcaa9cc42419073cd7ac3a116b24bd3c537d004512b6c2daa596054c21"
          ],
          [
            "product-faq.md:001:0d1a353c26224e8102a070fbd4262c6a1d8145084acc659b03d48e443645b094"
          ]
        ]
      },
      {
        "group_id": "g2",
        "alternatives": [
          [
            "returns-policy.md:005:4d4b2ea9115f9f9c717e0b83cded75c9048bc1b04a4621131131a6e1d023f11c"
          ]
        ]
      },
      {
        "group_id": "g3",
        "alternatives": [
          [
            "returns-policy.md:002:790d978e46084d3c89e96e1e75a4db8309b5d24c47b4be722652b8cc0facd375"
          ]
        ]
      }
    ],
    "answer_points": [
      {
        "point_id": "p1",
        "text": "7 天无理由退货需商品完好、不影响二次销售",
        "condition": "签收起7天内、商品完好不影响二次销售；定制和生鲜排除；7天内且商品完好、不影响二次销售，具体以平台规则为准",
        "aliases": []
      },
      {
        "point_id": "p2",
        "text": "无理由退货寄回运费买家承担",
        "condition": "运费按退换货原因与平台最终判定区分",
        "aliases": []
      },
      {
        "point_id": "p3",
        "text": "核验通过后原路退款，到账时效按平台规则，资料未给固定天数",
        "condition": "平台核验通过后，到账时间按平台售后规则",
        "aliases": []
      }
    ],
    "candidate_ranking": [
      {
        "chunk_id": 1869,
        "score": 0.7373634576797485,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1871,
        "score": 0.723166286945343,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1868,
        "score": 0.7017114162445068,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1865,
        "score": 0.6783213019371033,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1866,
        "score": 0.676337480545044,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1838,
        "score": 0.6754489541053772,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1840,
        "score": 0.6569998264312744,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1873,
        "score": 0.6457274556159973,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1842,
        "score": 0.6393616795539856,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1870,
        "score": 0.6388071775436401,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1831,
        "score": 0.6368440389633179,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1841,
        "score": 0.6317943930625916,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1867,
        "score": 0.6229962110519409,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1836,
        "score": 0.6189490556716919,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1839,
        "score": 0.6125789284706116,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1837,
        "score": 0.6121077537536621,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1849,
        "score": 0.6097642183303833,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1850,
        "score": 0.6039755344390869,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1847,
        "score": 0.6020753979682922,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1851,
        "score": 0.595655083656311,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1872,
        "score": 0.5915417671203613,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1879,
        "score": 0.5711824893951416,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1832,
        "score": 0.5709993839263916,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1848,
        "score": 0.5658526420593262,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1876,
        "score": 0.5494536757469177,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1843,
        "score": 0.5331028699874878,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1877,
        "score": 0.521675705909729,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1835,
        "score": 0.4981663227081299,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1844,
        "score": 0.49812501668930054,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1874,
        "score": 0.46601760387420654,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1845,
        "score": 0.4591333270072937,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1875,
        "score": 0.4568917751312256,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1878,
        "score": 0.45109814405441284,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1846,
        "score": 0.44950807094573975,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1834,
        "score": 0.43748342990875244,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1853,
        "score": 0.43006861209869385,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1855,
        "score": 0.4208238124847412,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1858,
        "score": 0.4117301106452942,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1857,
        "score": 0.4051203727722168,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1856,
        "score": 0.39627736806869507,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1854,
        "score": 0.38977864384651184,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1833,
        "score": 0.38788095116615295,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1862,
        "score": 0.36595216393470764,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1880,
        "score": 0.36394211649894714,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1852,
        "score": 0.358730673789978,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1860,
        "score": 0.3510386347770691,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1863,
        "score": 0.3437598645687103,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1861,
        "score": 0.33526667952537537,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1864,
        "score": 0.3319590091705322,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1859,
        "score": 0.3228994905948639,
        "score_kind": "cosine"
      }
    ],
    "final_ranking": [
      {
        "chunk_id": 1869,
        "score": 0.7373634576797485,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1871,
        "score": 0.723166286945343,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1868,
        "score": 0.7017114162445068,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1865,
        "score": 0.6783213019371033,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1866,
        "score": 0.676337480545044,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1838,
        "score": 0.6754489541053772,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1840,
        "score": 0.6569998264312744,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1873,
        "score": 0.6457274556159973,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1842,
        "score": 0.6393616795539856,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1870,
        "score": 0.6388071775436401,
        "score_kind": "cosine"
      }
    ]
  }
}
````

### E2 / bm25

````json
{
  "eval_id": "E2",
  "strategy": "bm25",
  "bucket": "E_multi",
  "difficulty": "multi",
  "category": null,
  "should_refuse": false,
  "refused": true,
  "status": "completed",
  "stage": "complete",
  "query": "东西不想要了要退货,寄回去的运费谁承担,钱多久回来",
  "query_plan": {
    "standard": "东西不想要了要退货,寄回去的运费谁承担,钱多久回来",
    "expansions": []
  },
  "mapped_groups": [
    {
      "group_id": "g1",
      "alternatives": [
        [
          1865
        ],
        [
          1838
        ]
      ]
    },
    {
      "group_id": "g2",
      "alternatives": [
        [
          1869
        ]
      ]
    },
    {
      "group_id": "g3",
      "alternatives": [
        [
          1866
        ]
      ]
    }
  ],
  "candidate_ids": [
    1869,
    1868,
    1871,
    1872,
    1841,
    1865,
    1849,
    1851,
    1873,
    1877,
    1838,
    1867,
    1842,
    1847,
    1880,
    1874,
    1866,
    1879,
    1837,
    1876,
    1870,
    1832,
    1831,
    1844,
    1860,
    1839,
    1875,
    1852,
    1843,
    1854,
    1850,
    1835,
    1846,
    1848,
    1834,
    1878
  ],
  "final_ids": [
    1869,
    1868,
    1871,
    1872,
    1841,
    1865,
    1849,
    1851,
    1873,
    1877
  ],
  "prompt_citations": [
    {
      "n": 1,
      "chunk_id": "1869",
      "section_path": "退货退款政策/退换货运费承担",
      "question": "退换货运费承担",
      "answer": "无理由退货的退回运费由买家承担;因商品质量问题、发错货、少发漏发导致的退换货,运费由平台承担。运费承担以平台售后规则最终判定为准。"
    },
    {
      "n": 3,
      "chunk_id": "1871",
      "section_path": "退货退款政策/运输破损处理",
      "question": "运输破损处理",
      "answer": "商品运输途中破损的,请在签收后 48 小时内联系客服并提供开箱视频与照片,核实后可免费补发或退款,相关运费由平台承担。"
    },
    {
      "n": 5,
      "chunk_id": "1841",
      "section_path": "商品与购物 FAQ/发货时效多久",
      "question": "发货时效多久",
      "answer": "现货商品付款后 48 小时内发货,预售商品以商品详情页标注的发货时间为准。"
    },
    {
      "n": 7,
      "chunk_id": "1849",
      "section_path": "商品与购物 FAQ/商品缺货多久补货",
      "question": "商品缺货多久补货",
      "answer": "现货售罄的商品通常 3 至 7 天内补货,可在商品页点击「到货通知」,补货后系统会推送提醒。"
    },
    {
      "n": 9,
      "chunk_id": "1873",
      "section_path": "退货退款政策/预售与定金",
      "question": "预售与定金",
      "answer": "预售商品以详情页标注的时间发货;定金支付后不支持无理由退定金,尾款未按时支付的,定金按活动规则处理。"
    },
    {
      "n": 10,
      "chunk_id": "1877",
      "section_path": "积分规则/积分怎么用",
      "question": "积分怎么用",
      "answer": "积分可在结算时抵扣商品金额，100 积分抵 1 元现金，单笔订单最多抵 30 元，不用于抵扣偏远地区附加运费，也不支持直接提现。\n\n2000 积分可兑换自动饮水机滤芯 3 片，该兑换套装适用于 MH-W40，普通配送地区包邮；偏远地区附加配送费仍需按页面规则确认。MH-W40 的滤芯更换周期以商品规格手册为准。\n\n800 积分可兑换猫零食小样，普通配送地区另收 6 元运费；该兑换不直接套用普通购物订单的满 99 元包邮规则。兑换商品、可用库存及偏远地区配送规则以兑换页面标注为准。"
    },
    {
      "n": 8,
      "chunk_id": "1851",
      "section_path": "商品与购物 FAQ/会员运费权益",
      "question": "会员运费权益",
      "answer": "金卡会员每月享 3 次免运费权益,银卡会员享 1 次;权益不与偏远地区附加运费冲抵,当月未用完不结转。"
    },
    {
      "n": 6,
      "chunk_id": "1865",
      "section_path": "退货退款政策/无理由退货/适用范围",
      "question": "适用范围",
      "answer": "自签收之日起 7 天内,商品完好、不影响二次销售的,支持无理由退货。定制类、生鲜类商品除外。"
    },
    {
      "n": 4,
      "chunk_id": "1872",
      "section_path": "退货退款政策/不支持退货的商品",
      "question": "不支持退货的商品",
      "answer": "定制类、生鲜类、已拆封的猫砂等消耗品,以及标注「不支持无理由退货」的商品,非质量问题不支持退货。"
    },
    {
      "n": 2,
      "chunk_id": "1868",
      "section_path": "退货退款政策/换货政策/换货运费",
      "question": "换货运费",
      "answer": "非质量问题的换货,往返运费由买家承担;因质量问题或发错货的换货,往返运费由平台承担。"
    }
  ],
  "decision": {
    "useful": false,
    "reason": "退款到账时间无证据",
    "response_kind": "knowledge",
    "source": "self_check"
  },
  "answer": "目前的知识资料不足以确认这个问题，我无法给出可靠答案。请补充具体商品或适用条件，或联系人工客服确认。",
  "point_verdicts": [
    {
      "point_id": "p1",
      "covered": false,
      "reason": "回答为拒答，未提及7天无理由退货及商品完好、不影响二次销售等条件"
    },
    {
      "point_id": "p2",
      "covered": false,
      "reason": "回答为拒答，未说明无理由退货寄回运费由买家承担"
    },
    {
      "point_id": "p3",
      "covered": false,
      "reason": "回答为拒答，未提及核验通过后原路退款及到账时效按平台规则"
    }
  ],
  "claim_verdicts": [],
  "metrics": {
    "recall_at_5": 0.3333333333333333,
    "recall_at_10": 0.6666666666666666,
    "mrr_at_10": 1.0,
    "all_groups_hit_at_5": 0.0,
    "all_groups_hit_at_10": 0.0,
    "candidate_group_coverage": 1.0,
    "prompt_group_coverage": 0.6666666666666666,
    "answer_point_coverage": 0.0,
    "faithfulness": null,
    "absent_refusal_rate": null,
    "answerable_false_refusal_rate": 1.0
  },
  "error": null,
  "elapsed_ms": 5291.51859995909,
  "judge_snapshot": {
    "prompt_version": "joint-generation-v2.1",
    "finish_reason": "stop"
  },
  "audit": {
    "audit_version": 1,
    "source_map_id": "d2dd350d860b8141e52306cbbcafb22f97d091194eb1cdc839a528c2990715eb",
    "gold_groups": [
      {
        "group_id": "g1",
        "alternatives": [
          [
            "returns-policy.md:001:49f98ddcaa9cc42419073cd7ac3a116b24bd3c537d004512b6c2daa596054c21"
          ],
          [
            "product-faq.md:001:0d1a353c26224e8102a070fbd4262c6a1d8145084acc659b03d48e443645b094"
          ]
        ]
      },
      {
        "group_id": "g2",
        "alternatives": [
          [
            "returns-policy.md:005:4d4b2ea9115f9f9c717e0b83cded75c9048bc1b04a4621131131a6e1d023f11c"
          ]
        ]
      },
      {
        "group_id": "g3",
        "alternatives": [
          [
            "returns-policy.md:002:790d978e46084d3c89e96e1e75a4db8309b5d24c47b4be722652b8cc0facd375"
          ]
        ]
      }
    ],
    "answer_points": [
      {
        "point_id": "p1",
        "text": "7 天无理由退货需商品完好、不影响二次销售",
        "condition": "签收起7天内、商品完好不影响二次销售；定制和生鲜排除；7天内且商品完好、不影响二次销售，具体以平台规则为准",
        "aliases": []
      },
      {
        "point_id": "p2",
        "text": "无理由退货寄回运费买家承担",
        "condition": "运费按退换货原因与平台最终判定区分",
        "aliases": []
      },
      {
        "point_id": "p3",
        "text": "核验通过后原路退款，到账时效按平台规则，资料未给固定天数",
        "condition": "平台核验通过后，到账时间按平台售后规则",
        "aliases": []
      }
    ],
    "candidate_ranking": [
      {
        "chunk_id": 1869,
        "score": 10.676090240478516,
        "score_kind": "bm25"
      },
      {
        "chunk_id": 1868,
        "score": 9.836376190185547,
        "score_kind": "bm25"
      },
      {
        "chunk_id": 1871,
        "score": 7.268333435058594,
        "score_kind": "bm25"
      },
      {
        "chunk_id": 1872,
        "score": 5.63097620010376,
        "score_kind": "bm25"
      },
      {
        "chunk_id": 1841,
        "score": 4.741880416870117,
        "score_kind": "bm25"
      },
      {
        "chunk_id": 1865,
        "score": 4.518306732177734,
        "score_kind": "bm25"
      },
      {
        "chunk_id": 1849,
        "score": 4.484236717224121,
        "score_kind": "bm25"
      },
      {
        "chunk_id": 1851,
        "score": 4.33558988571167,
        "score_kind": "bm25"
      },
      {
        "chunk_id": 1873,
        "score": 4.041518211364746,
        "score_kind": "bm25"
      },
      {
        "chunk_id": 1877,
        "score": 3.6735312938690186,
        "score_kind": "bm25"
      },
      {
        "chunk_id": 1838,
        "score": 3.423988103866577,
        "score_kind": "bm25"
      },
      {
        "chunk_id": 1867,
        "score": 3.1294915676116943,
        "score_kind": "bm25"
      },
      {
        "chunk_id": 1842,
        "score": 3.048265218734741,
        "score_kind": "bm25"
      },
      {
        "chunk_id": 1847,
        "score": 2.904369831085205,
        "score_kind": "bm25"
      },
      {
        "chunk_id": 1880,
        "score": 2.8818564414978027,
        "score_kind": "bm25"
      },
      {
        "chunk_id": 1874,
        "score": 2.7881808280944824,
        "score_kind": "bm25"
      },
      {
        "chunk_id": 1866,
        "score": 2.4312641620635986,
        "score_kind": "bm25"
      },
      {
        "chunk_id": 1879,
        "score": 1.9325504302978516,
        "score_kind": "bm25"
      },
      {
        "chunk_id": 1837,
        "score": 1.8424832820892334,
        "score_kind": "bm25"
      },
      {
        "chunk_id": 1876,
        "score": 1.823819637298584,
        "score_kind": "bm25"
      },
      {
        "chunk_id": 1870,
        "score": 1.5415995121002197,
        "score_kind": "bm25"
      },
      {
        "chunk_id": 1832,
        "score": 1.3018649816513062,
        "score_kind": "bm25"
      },
      {
        "chunk_id": 1831,
        "score": 1.1889352798461914,
        "score_kind": "bm25"
      },
      {
        "chunk_id": 1844,
        "score": 1.1214089393615723,
        "score_kind": "bm25"
      },
      {
        "chunk_id": 1860,
        "score": 1.0838499069213867,
        "score_kind": "bm25"
      },
      {
        "chunk_id": 1839,
        "score": 1.0660427808761597,
        "score_kind": "bm25"
      },
      {
        "chunk_id": 1875,
        "score": 1.0572911500930786,
        "score_kind": "bm25"
      },
      {
        "chunk_id": 1852,
        "score": 1.0359933376312256,
        "score_kind": "bm25"
      },
      {
        "chunk_id": 1843,
        "score": 1.0168840885162354,
        "score_kind": "bm25"
      },
      {
        "chunk_id": 1854,
        "score": 0.984889805316925,
        "score_kind": "bm25"
      },
      {
        "chunk_id": 1850,
        "score": 0.9807054996490479,
        "score_kind": "bm25"
      },
      {
        "chunk_id": 1835,
        "score": 0.9720594882965088,
        "score_kind": "bm25"
      },
      {
        "chunk_id": 1846,
        "score": 0.9155580401420593,
        "score_kind": "bm25"
      },
      {
        "chunk_id": 1848,
        "score": 0.9155580401420593,
        "score_kind": "bm25"
      },
      {
        "chunk_id": 1834,
        "score": 0.8170415759086609,
        "score_kind": "bm25"
      },
      {
        "chunk_id": 1878,
        "score": 0.7920446395874023,
        "score_kind": "bm25"
      }
    ],
    "final_ranking": [
      {
        "chunk_id": 1869,
        "score": 10.676090240478516,
        "score_kind": "bm25"
      },
      {
        "chunk_id": 1868,
        "score": 9.836376190185547,
        "score_kind": "bm25"
      },
      {
        "chunk_id": 1871,
        "score": 7.268333435058594,
        "score_kind": "bm25"
      },
      {
        "chunk_id": 1872,
        "score": 5.63097620010376,
        "score_kind": "bm25"
      },
      {
        "chunk_id": 1841,
        "score": 4.741880416870117,
        "score_kind": "bm25"
      },
      {
        "chunk_id": 1865,
        "score": 4.518306732177734,
        "score_kind": "bm25"
      },
      {
        "chunk_id": 1849,
        "score": 4.484236717224121,
        "score_kind": "bm25"
      },
      {
        "chunk_id": 1851,
        "score": 4.33558988571167,
        "score_kind": "bm25"
      },
      {
        "chunk_id": 1873,
        "score": 4.041518211364746,
        "score_kind": "bm25"
      },
      {
        "chunk_id": 1877,
        "score": 3.6735312938690186,
        "score_kind": "bm25"
      }
    ]
  }
}
````

### E2 / hybrid

````json
{
  "eval_id": "E2",
  "strategy": "hybrid",
  "bucket": "E_multi",
  "difficulty": "multi",
  "category": null,
  "should_refuse": false,
  "refused": false,
  "status": "completed",
  "stage": "complete",
  "query": "东西不想要了要退货,寄回去的运费谁承担,钱多久回来",
  "query_plan": {
    "standard": "东西不想要了要退货,寄回去的运费谁承担,钱多久回来",
    "expansions": []
  },
  "mapped_groups": [
    {
      "group_id": "g1",
      "alternatives": [
        [
          1865
        ],
        [
          1838
        ]
      ]
    },
    {
      "group_id": "g2",
      "alternatives": [
        [
          1869
        ]
      ]
    },
    {
      "group_id": "g3",
      "alternatives": [
        [
          1866
        ]
      ]
    }
  ],
  "candidate_ids": [
    1869,
    1868,
    1871,
    1865,
    1841,
    1838,
    1873,
    1866,
    1842,
    1872,
    1849,
    1867,
    1851,
    1870,
    1847,
    1831,
    1837,
    1877,
    1879,
    1839,
    1874,
    1876,
    1832,
    1850,
    1844,
    1880,
    1843,
    1848,
    1875,
    1835,
    1846,
    1860,
    1878,
    1834,
    1854,
    1852,
    1840,
    1836,
    1845,
    1853,
    1855,
    1858,
    1857,
    1856,
    1833,
    1862,
    1863,
    1861,
    1864,
    1859
  ],
  "final_ids": [
    1869,
    1868,
    1871,
    1865,
    1841,
    1838,
    1873,
    1866,
    1842,
    1872
  ],
  "prompt_citations": [
    {
      "n": 1,
      "chunk_id": "1869",
      "section_path": "退货退款政策/退换货运费承担",
      "question": "退换货运费承担",
      "answer": "无理由退货的退回运费由买家承担;因商品质量问题、发错货、少发漏发导致的退换货,运费由平台承担。运费承担以平台售后规则最终判定为准。"
    },
    {
      "n": 3,
      "chunk_id": "1871",
      "section_path": "退货退款政策/运输破损处理",
      "question": "运输破损处理",
      "answer": "商品运输途中破损的,请在签收后 48 小时内联系客服并提供开箱视频与照片,核实后可免费补发或退款,相关运费由平台承担。"
    },
    {
      "n": 5,
      "chunk_id": "1841",
      "section_path": "商品与购物 FAQ/发货时效多久",
      "question": "发货时效多久",
      "answer": "现货商品付款后 48 小时内发货,预售商品以商品详情页标注的发货时间为准。"
    },
    {
      "n": 7,
      "chunk_id": "1873",
      "section_path": "退货退款政策/预售与定金",
      "question": "预售与定金",
      "answer": "预售商品以详情页标注的时间发货;定金支付后不支持无理由退定金,尾款未按时支付的,定金按活动规则处理。"
    },
    {
      "n": 9,
      "chunk_id": "1842",
      "section_path": "商品与购物 FAQ/运费怎么算",
      "question": "运费怎么算",
      "answer": "单笔订单满 99 元包邮,未满收取 10 元运费,偏远地区运费另计。邮费即运费,按此规则收取。"
    },
    {
      "n": 10,
      "chunk_id": "1872",
      "section_path": "退货退款政策/不支持退货的商品",
      "question": "不支持退货的商品",
      "answer": "定制类、生鲜类、已拆封的猫砂等消耗品,以及标注「不支持无理由退货」的商品,非质量问题不支持退货。"
    },
    {
      "n": 8,
      "chunk_id": "1866",
      "section_path": "退货退款政策/无理由退货/退款时效",
      "question": "退款时效",
      "answer": "退货商品经平台核验通过后,退款原路退回,到账时效以平台售后规则为准。"
    },
    {
      "n": 6,
      "chunk_id": "1838",
      "section_path": "商品与购物 FAQ/退货政策是什么",
      "question": "退货政策是什么",
      "answer": "支持 7 天无理由退货,商品需保持完好、不影响二次销售,具体以平台售后规则为准。"
    },
    {
      "n": 4,
      "chunk_id": "1865",
      "section_path": "退货退款政策/无理由退货/适用范围",
      "question": "适用范围",
      "answer": "自签收之日起 7 天内,商品完好、不影响二次销售的,支持无理由退货。定制类、生鲜类商品除外。"
    },
    {
      "n": 2,
      "chunk_id": "1868",
      "section_path": "退货退款政策/换货政策/换货运费",
      "question": "换货运费",
      "answer": "非质量问题的换货,往返运费由买家承担;因质量问题或发错货的换货,往返运费由平台承担。"
    }
  ],
  "decision": {
    "useful": true,
    "reason": "运费承担有明确规则，退款到账以平台规则为准",
    "response_kind": "knowledge",
    "source": null
  },
  "answer": "您好！很高兴为您解答～\n\n**关于退货运费：**\n- 无理由退货（不想要了）的退回运费由买家承担[1]\n- 如是质量问题、发错货、少发漏发，运费由平台承担[1]\n\n**关于退款到账：**\n退货商品经平台核验通过后，退款会原路退回，具体到账时效以平台售后规则为准[8]，我无法保证具体到账日期，还请谅解。\n\n**温馨提示：**\n- 自签收之日起 7 天内、商品完好不影响二次销售，可申请无理由退货[4]\n- 定制类、生鲜类及标注「不支持无理由退货」的商品除外[10]\n\n请问您方便提供订单号吗？我可以帮您进一步查询订单情况～",
  "point_verdicts": [
    {
      "point_id": "p1",
      "covered": true,
      "reason": "回答提到7天内、商品完好不影响二次销售、定制生鲜及标注不支持的商品除外，条件完整"
    },
    {
      "point_id": "p2",
      "covered": true,
      "reason": "回答说明无理由退货运费买家承担，质量等问题由平台承担，按原因区分"
    },
    {
      "point_id": "p3",
      "covered": true,
      "reason": "回答说明核验通过后原路退回，时效以平台规则为准，未编造固定天数"
    }
  ],
  "claim_verdicts": [
    {
      "claim": "无理由退货的退回运费由买家承担",
      "supported": true,
      "reason": "证据1明确无理由退货退回运费由买家承担"
    },
    {
      "claim": "质量问题、发错货、少发漏发导致的退货运费由平台承担",
      "supported": true,
      "reason": "证据1明确该情形运费由平台承担"
    },
    {
      "claim": "退货商品经平台核验通过后退款原路退回",
      "supported": true,
      "reason": "证据8明确核验通过后退款原路退回"
    },
    {
      "claim": "退款到账时效以平台售后规则为准",
      "supported": true,
      "reason": "证据8明确到账时效以平台售后规则为准"
    },
    {
      "claim": "自签收之日起7天内、商品完好不影响二次销售可申请无理由退货",
      "supported": true,
      "reason": "证据4及证据6均支持该条件"
    },
    {
      "claim": "定制类、生鲜类及标注不支持无理由退货的商品不支持无理由退货",
      "supported": true,
      "reason": "证据4和证据10支持定制、生鲜除外及标注不支持的商品"
    }
  ],
  "metrics": {
    "recall_at_5": 0.6666666666666666,
    "recall_at_10": 1.0,
    "mrr_at_10": 1.0,
    "all_groups_hit_at_5": 0.0,
    "all_groups_hit_at_10": 1.0,
    "candidate_group_coverage": 1.0,
    "prompt_group_coverage": 1.0,
    "answer_point_coverage": 1.0,
    "faithfulness": 1.0,
    "absent_refusal_rate": null,
    "answerable_false_refusal_rate": 0.0
  },
  "error": null,
  "elapsed_ms": 15384.172799997032,
  "judge_snapshot": {
    "prompt_version": "joint-generation-v2.1",
    "finish_reason": "stop"
  },
  "audit": {
    "audit_version": 1,
    "source_map_id": "d2dd350d860b8141e52306cbbcafb22f97d091194eb1cdc839a528c2990715eb",
    "gold_groups": [
      {
        "group_id": "g1",
        "alternatives": [
          [
            "returns-policy.md:001:49f98ddcaa9cc42419073cd7ac3a116b24bd3c537d004512b6c2daa596054c21"
          ],
          [
            "product-faq.md:001:0d1a353c26224e8102a070fbd4262c6a1d8145084acc659b03d48e443645b094"
          ]
        ]
      },
      {
        "group_id": "g2",
        "alternatives": [
          [
            "returns-policy.md:005:4d4b2ea9115f9f9c717e0b83cded75c9048bc1b04a4621131131a6e1d023f11c"
          ]
        ]
      },
      {
        "group_id": "g3",
        "alternatives": [
          [
            "returns-policy.md:002:790d978e46084d3c89e96e1e75a4db8309b5d24c47b4be722652b8cc0facd375"
          ]
        ]
      }
    ],
    "answer_points": [
      {
        "point_id": "p1",
        "text": "7 天无理由退货需商品完好、不影响二次销售",
        "condition": "签收起7天内、商品完好不影响二次销售；定制和生鲜排除；7天内且商品完好、不影响二次销售，具体以平台规则为准",
        "aliases": []
      },
      {
        "point_id": "p2",
        "text": "无理由退货寄回运费买家承担",
        "condition": "运费按退换货原因与平台最终判定区分",
        "aliases": []
      },
      {
        "point_id": "p3",
        "text": "核验通过后原路退款，到账时效按平台规则，资料未给固定天数",
        "condition": "平台核验通过后，到账时间按平台售后规则",
        "aliases": []
      }
    ],
    "candidate_ranking": [
      {
        "chunk_id": 1869,
        "score": 0.032786883413791656,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1868,
        "score": 0.0320020467042923,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1871,
        "score": 0.0320020467042923,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1865,
        "score": 0.03077651560306549,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1841,
        "score": 0.0292735043913126,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1838,
        "score": 0.029236022382974625,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1873,
        "score": 0.02919863536953926,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1866,
        "score": 0.028371628373861313,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1842,
        "score": 0.02819138392806053,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1872,
        "score": 0.027970679104328156,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1849,
        "score": 0.027912385761737823,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1867,
        "score": 0.027587518095970154,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1851,
        "score": 0.027205882593989372,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1870,
        "score": 0.026631392538547516,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1847,
        "score": 0.026171742007136345,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1831,
        "score": 0.026132699102163315,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1837,
        "score": 0.02581612393260002,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1877,
        "score": 0.02577996626496315,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1879,
        "score": 0.025015633553266525,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1839,
        "score": 0.024961240589618683,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1874,
        "score": 0.02426900714635849,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1876,
        "score": 0.024264706298708916,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1832,
        "score": 0.024243313819169998,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1850,
        "score": 0.02380952425301075,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1844,
        "score": 0.023140717297792435,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1880,
        "score": 0.022948719561100006,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1843,
        "score": 0.022863861173391342,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1848,
        "score": 0.022543059661984444,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1875,
        "score": 0.022363819181919098,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1835,
        "score": 0.022233203053474426,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1846,
        "score": 0.02139098569750786,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1860,
        "score": 0.021198667585849762,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1878,
        "score": 0.021169355139136314,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1834,
        "score": 0.021052632480859756,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1854,
        "score": 0.02101210132241249,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1852,
        "score": 0.02088744565844536,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1840,
        "score": 0.014925372786819935,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1836,
        "score": 0.013513513840734959,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1845,
        "score": 0.010989011265337467,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1853,
        "score": 0.010416666977107525,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1855,
        "score": 0.010309278033673763,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1858,
        "score": 0.010204081423580647,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1857,
        "score": 0.010101010091602802,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1856,
        "score": 0.009999999776482582,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1833,
        "score": 0.009803921915590763,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1862,
        "score": 0.009708737954497337,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1863,
        "score": 0.009345794096589088,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1861,
        "score": 0.009259259328246117,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1864,
        "score": 0.00917431153357029,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1859,
        "score": 0.00909090880304575,
        "score_kind": "rrf"
      }
    ],
    "final_ranking": [
      {
        "chunk_id": 1869,
        "score": 0.032786883413791656,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1868,
        "score": 0.0320020467042923,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1871,
        "score": 0.0320020467042923,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1865,
        "score": 0.03077651560306549,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1841,
        "score": 0.0292735043913126,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1838,
        "score": 0.029236022382974625,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1873,
        "score": 0.02919863536953926,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1866,
        "score": 0.028371628373861313,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1842,
        "score": 0.02819138392806053,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1872,
        "score": 0.027970679104328156,
        "score_kind": "rrf"
      }
    ]
  }
}
````

### E2 / hybrid_rerank

````json
{
  "eval_id": "E2",
  "strategy": "hybrid_rerank",
  "bucket": "E_multi",
  "difficulty": "multi",
  "category": null,
  "should_refuse": false,
  "refused": false,
  "status": "completed",
  "stage": "complete",
  "query": "东西不想要了要退货,寄回去的运费谁承担,钱多久回来",
  "query_plan": {
    "standard": "东西不想要了要退货,寄回去的运费谁承担,钱多久回来",
    "expansions": []
  },
  "mapped_groups": [
    {
      "group_id": "g1",
      "alternatives": [
        [
          1865
        ],
        [
          1838
        ]
      ]
    },
    {
      "group_id": "g2",
      "alternatives": [
        [
          1869
        ]
      ]
    },
    {
      "group_id": "g3",
      "alternatives": [
        [
          1866
        ]
      ]
    }
  ],
  "candidate_ids": [
    1869,
    1868,
    1871,
    1865,
    1841,
    1838,
    1873,
    1866,
    1842,
    1872,
    1849,
    1867,
    1851,
    1870,
    1847,
    1831,
    1837,
    1877,
    1879,
    1839,
    1874,
    1876,
    1832,
    1850,
    1844,
    1880,
    1843,
    1848,
    1875,
    1835,
    1846,
    1860,
    1878,
    1834,
    1854,
    1852,
    1840,
    1836,
    1845,
    1853,
    1855,
    1858,
    1857,
    1856,
    1833,
    1862,
    1863,
    1861,
    1864,
    1859
  ],
  "final_ids": [
    1869,
    1868,
    1871,
    1865,
    1866,
    1838,
    1840,
    1837,
    1842,
    1870
  ],
  "prompt_citations": [
    {
      "n": 1,
      "chunk_id": "1869",
      "section_path": "退货退款政策/退换货运费承担",
      "question": "退换货运费承担",
      "answer": "无理由退货的退回运费由买家承担;因商品质量问题、发错货、少发漏发导致的退换货,运费由平台承担。运费承担以平台售后规则最终判定为准。"
    },
    {
      "n": 3,
      "chunk_id": "1871",
      "section_path": "退货退款政策/运输破损处理",
      "question": "运输破损处理",
      "answer": "商品运输途中破损的,请在签收后 48 小时内联系客服并提供开箱视频与照片,核实后可免费补发或退款,相关运费由平台承担。"
    },
    {
      "n": 5,
      "chunk_id": "1866",
      "section_path": "退货退款政策/无理由退货/退款时效",
      "question": "退款时效",
      "answer": "退货商品经平台核验通过后,退款原路退回,到账时效以平台售后规则为准。"
    },
    {
      "n": 7,
      "chunk_id": "1840",
      "section_path": "商品与购物 FAQ/换货流程怎么走",
      "question": "换货流程怎么走",
      "answer": "收到商品 7 天内可申请换货,联系客服登记后将商品寄回,平台核验无误后补发新品。"
    },
    {
      "n": 9,
      "chunk_id": "1842",
      "section_path": "商品与购物 FAQ/运费怎么算",
      "question": "运费怎么算",
      "answer": "单笔订单满 99 元包邮,未满收取 10 元运费,偏远地区运费另计。邮费即运费,按此规则收取。"
    },
    {
      "n": 10,
      "chunk_id": "1870",
      "section_path": "退货退款政策/质量问题与保修",
      "question": "质量问题与保修",
      "answer": "电子类商品自签收起保修 12 个月,保修期内非人为损坏可申请免费维修或换货;人为损坏、超保商品维修可能收取工本费。"
    },
    {
      "n": 8,
      "chunk_id": "1837",
      "section_path": "售后手册/会员专属售后权益",
      "question": "会员专属售后权益",
      "answer": "金卡会员享优先客服接入与上门取件退换货;银卡会员享退换货运费权益 1 次/月。具体权益以会员中心页面标注为准。"
    },
    {
      "n": 6,
      "chunk_id": "1838",
      "section_path": "商品与购物 FAQ/退货政策是什么",
      "question": "退货政策是什么",
      "answer": "支持 7 天无理由退货,商品需保持完好、不影响二次销售,具体以平台售后规则为准。"
    },
    {
      "n": 4,
      "chunk_id": "1865",
      "section_path": "退货退款政策/无理由退货/适用范围",
      "question": "适用范围",
      "answer": "自签收之日起 7 天内,商品完好、不影响二次销售的,支持无理由退货。定制类、生鲜类商品除外。"
    },
    {
      "n": 2,
      "chunk_id": "1868",
      "section_path": "退货退款政策/换货政策/换货运费",
      "question": "换货运费",
      "answer": "非质量问题的换货,往返运费由买家承担;因质量问题或发错货的换货,往返运费由平台承担。"
    }
  ],
  "decision": {
    "useful": true,
    "reason": "无理由退货运费买家承担有证据；退款时效只说核验后退回，到账日期不可承诺",
    "response_kind": "knowledge",
    "source": null
  },
  "answer": "您好，为您解答退货相关问题：\n\n**运费承担：**\n- 无理由退货（不想要了）的退回运费由买家承担[1]\n- 若是商品质量问题、发错货、少发漏发导致的退货，运费由平台承担[1]\n- 最终以平台售后规则判定为准[1]\n\n**退款到账：**\n退货商品经平台核验通过后，退款将原路退回，具体到账时效以平台售后规则为准[5]。我无法保证具体到账日期，请您理解。\n\n另外温馨提示：自签收起7天内、商品完好不影响二次销售的无理由退货是被支持的[4][6]。请问还有什么可以帮您？",
  "point_verdicts": [
    {
      "point_id": "p1",
      "covered": false,
      "reason": "回答提到签收7天内、商品完好、不影响二次销售，但未提及定制类、生鲜类商品除外这一排除条件，条件覆盖不完整"
    },
    {
      "point_id": "p2",
      "covered": true,
      "reason": "回答明确无理由退货退回运费由买家承担，并区分质量问题等由平台承担、以平台规则判定为准，条件完整"
    },
    {
      "point_id": "p3",
      "covered": true,
      "reason": "回答说明平台核验通过后原路退回，到账时效以平台售后规则为准，且未编造固定天数，与条件一致"
    }
  ],
  "claim_verdicts": [
    {
      "claim": "无理由退货（不想要了）的退回运费由买家承担",
      "supported": true,
      "reason": "证据[1]明确无理由退货的退回运费由买家承担"
    },
    {
      "claim": "商品质量问题、发错货、少发漏发导致的退货，运费由平台承担",
      "supported": true,
      "reason": "证据[1]明确上述原因导致的退换货运费由平台承担"
    },
    {
      "claim": "运费承担以平台售后规则最终判定为准",
      "supported": true,
      "reason": "证据[1]明确运费承担以平台售后规则最终判定为准"
    },
    {
      "claim": "退货商品经平台核验通过后，退款原路退回",
      "supported": true,
      "reason": "证据[5]明确核验通过后退款原路退回"
    },
    {
      "claim": "退款具体到账时效以平台售后规则为准，无固定天数保证",
      "supported": true,
      "reason": "证据[5]明确到账时效以平台售后规则为准，未给出固定天数"
    },
    {
      "claim": "自签收起7天内、商品完好不影响二次销售的无理由退货是被支持的",
      "supported": true,
      "reason": "证据[4][6]均支持签收起7天内、商品完好、不影响二次销售可无理由退货"
    }
  ],
  "metrics": {
    "recall_at_5": 1.0,
    "recall_at_10": 1.0,
    "mrr_at_10": 1.0,
    "all_groups_hit_at_5": 1.0,
    "all_groups_hit_at_10": 1.0,
    "candidate_group_coverage": 1.0,
    "prompt_group_coverage": 1.0,
    "answer_point_coverage": 0.6666666666666666,
    "faithfulness": 1.0,
    "absent_refusal_rate": null,
    "answerable_false_refusal_rate": 0.0
  },
  "error": null,
  "elapsed_ms": 18487.41089995019,
  "judge_snapshot": {
    "prompt_version": "joint-generation-v2.1",
    "finish_reason": "stop"
  },
  "audit": {
    "audit_version": 1,
    "source_map_id": "d2dd350d860b8141e52306cbbcafb22f97d091194eb1cdc839a528c2990715eb",
    "gold_groups": [
      {
        "group_id": "g1",
        "alternatives": [
          [
            "returns-policy.md:001:49f98ddcaa9cc42419073cd7ac3a116b24bd3c537d004512b6c2daa596054c21"
          ],
          [
            "product-faq.md:001:0d1a353c26224e8102a070fbd4262c6a1d8145084acc659b03d48e443645b094"
          ]
        ]
      },
      {
        "group_id": "g2",
        "alternatives": [
          [
            "returns-policy.md:005:4d4b2ea9115f9f9c717e0b83cded75c9048bc1b04a4621131131a6e1d023f11c"
          ]
        ]
      },
      {
        "group_id": "g3",
        "alternatives": [
          [
            "returns-policy.md:002:790d978e46084d3c89e96e1e75a4db8309b5d24c47b4be722652b8cc0facd375"
          ]
        ]
      }
    ],
    "answer_points": [
      {
        "point_id": "p1",
        "text": "7 天无理由退货需商品完好、不影响二次销售",
        "condition": "签收起7天内、商品完好不影响二次销售；定制和生鲜排除；7天内且商品完好、不影响二次销售，具体以平台规则为准",
        "aliases": []
      },
      {
        "point_id": "p2",
        "text": "无理由退货寄回运费买家承担",
        "condition": "运费按退换货原因与平台最终判定区分",
        "aliases": []
      },
      {
        "point_id": "p3",
        "text": "核验通过后原路退款，到账时效按平台规则，资料未给固定天数",
        "condition": "平台核验通过后，到账时间按平台售后规则",
        "aliases": []
      }
    ],
    "candidate_ranking": [
      {
        "chunk_id": 1869,
        "score": 0.032786883413791656,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1868,
        "score": 0.0320020467042923,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1871,
        "score": 0.0320020467042923,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1865,
        "score": 0.03077651560306549,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1841,
        "score": 0.0292735043913126,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1838,
        "score": 0.029236022382974625,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1873,
        "score": 0.02919863536953926,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1866,
        "score": 0.028371628373861313,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1842,
        "score": 0.02819138392806053,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1872,
        "score": 0.027970679104328156,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1849,
        "score": 0.027912385761737823,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1867,
        "score": 0.027587518095970154,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1851,
        "score": 0.027205882593989372,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1870,
        "score": 0.026631392538547516,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1847,
        "score": 0.026171742007136345,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1831,
        "score": 0.026132699102163315,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1837,
        "score": 0.02581612393260002,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1877,
        "score": 0.02577996626496315,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1879,
        "score": 0.025015633553266525,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1839,
        "score": 0.024961240589618683,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1874,
        "score": 0.02426900714635849,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1876,
        "score": 0.024264706298708916,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1832,
        "score": 0.024243313819169998,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1850,
        "score": 0.02380952425301075,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1844,
        "score": 0.023140717297792435,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1880,
        "score": 0.022948719561100006,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1843,
        "score": 0.022863861173391342,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1848,
        "score": 0.022543059661984444,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1875,
        "score": 0.022363819181919098,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1835,
        "score": 0.022233203053474426,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1846,
        "score": 0.02139098569750786,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1860,
        "score": 0.021198667585849762,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1878,
        "score": 0.021169355139136314,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1834,
        "score": 0.021052632480859756,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1854,
        "score": 0.02101210132241249,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1852,
        "score": 0.02088744565844536,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1840,
        "score": 0.014925372786819935,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1836,
        "score": 0.013513513840734959,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1845,
        "score": 0.010989011265337467,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1853,
        "score": 0.010416666977107525,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1855,
        "score": 0.010309278033673763,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1858,
        "score": 0.010204081423580647,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1857,
        "score": 0.010101010091602802,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1856,
        "score": 0.009999999776482582,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1833,
        "score": 0.009803921915590763,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1862,
        "score": 0.009708737954497337,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1863,
        "score": 0.009345794096589088,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1861,
        "score": 0.009259259328246117,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1864,
        "score": 0.00917431153357029,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1859,
        "score": 0.00909090880304575,
        "score_kind": "rrf"
      }
    ],
    "final_ranking": [
      {
        "chunk_id": 1869,
        "score": 0.7566613554954529,
        "score_kind": "rerank"
      },
      {
        "chunk_id": 1868,
        "score": 0.2801871597766876,
        "score_kind": "rerank"
      },
      {
        "chunk_id": 1871,
        "score": 0.27925536036491394,
        "score_kind": "rerank"
      },
      {
        "chunk_id": 1865,
        "score": 0.07364001125097275,
        "score_kind": "rerank"
      },
      {
        "chunk_id": 1866,
        "score": 0.04948786646127701,
        "score_kind": "rerank"
      },
      {
        "chunk_id": 1838,
        "score": 0.044801924377679825,
        "score_kind": "rerank"
      },
      {
        "chunk_id": 1840,
        "score": 0.03869559243321419,
        "score_kind": "rerank"
      },
      {
        "chunk_id": 1837,
        "score": 0.031828515231609344,
        "score_kind": "rerank"
      },
      {
        "chunk_id": 1842,
        "score": 0.030970364809036255,
        "score_kind": "rerank"
      },
      {
        "chunk_id": 1870,
        "score": 0.023854728788137436,
        "score_kind": "rerank"
      }
    ]
  }
}
````

### E19 / dense

````json
{
  "eval_id": "E19",
  "strategy": "dense",
  "bucket": "E_multi",
  "difficulty": "multi",
  "category": null,
  "should_refuse": false,
  "refused": null,
  "status": "rewrite_error",
  "stage": "rewrite",
  "query": "饮水机 MH-W20 和 MH-W60 的水箱和换滤芯周期分别是多少",
  "query_plan": null,
  "mapped_groups": [
    {
      "group_id": "g1",
      "alternatives": [
        [
          1856
        ]
      ]
    },
    {
      "group_id": "g2",
      "alternatives": [
        [
          1858
        ]
      ]
    }
  ],
  "candidate_ids": null,
  "final_ids": null,
  "prompt_citations": null,
  "decision": null,
  "answer": null,
  "point_verdicts": null,
  "claim_verdicts": null,
  "metrics": {
    "recall_at_5": null,
    "recall_at_10": null,
    "mrr_at_10": null,
    "all_groups_hit_at_5": null,
    "all_groups_hit_at_10": null,
    "candidate_group_coverage": null,
    "prompt_group_coverage": null,
    "answer_point_coverage": null,
    "faithfulness": null,
    "absent_refusal_rate": null,
    "answerable_false_refusal_rate": null
  },
  "error": {
    "code": "rewrite_error",
    "type": "ServiceError",
    "message": "该阶段执行失败"
  },
  "elapsed_ms": 1839.666800107807,
  "judge_snapshot": null,
  "audit": {
    "audit_version": 1,
    "source_map_id": "d2dd350d860b8141e52306cbbcafb22f97d091194eb1cdc839a528c2990715eb",
    "gold_groups": [
      {
        "group_id": "g1",
        "alternatives": [
          [
            "product-specs.md:005:58f10003acf72bef5aa921d603dc1a58bb0332dcd7f8735057266e573f01e11b"
          ]
        ]
      },
      {
        "group_id": "g2",
        "alternatives": [
          [
            "product-specs.md:007:e9867a419061278a1bc0599bc3595ac01da4c561aea19bf0bf4c9bde5ba30e7f"
          ]
        ]
      }
    ],
    "answer_points": [
      {
        "point_id": "p1",
        "text": "MH-W20 水箱 2L，滤芯建议每 2 周换",
        "condition": "仅适用于自动饮水机(型号 MH-W20)所述范围",
        "aliases": []
      },
      {
        "point_id": "p2",
        "text": "MH-W60 水箱 6L，滤芯建议每 4 周换",
        "condition": "仅适用于自动饮水机 Pro 不锈钢(型号 MH-W60)所述范围",
        "aliases": []
      }
    ],
    "candidate_ranking": null,
    "final_ranking": null
  }
}
````

### E19 / bm25

````json
{
  "eval_id": "E19",
  "strategy": "bm25",
  "bucket": "E_multi",
  "difficulty": "multi",
  "category": null,
  "should_refuse": false,
  "refused": null,
  "status": "rewrite_error",
  "stage": "rewrite",
  "query": "饮水机 MH-W20 和 MH-W60 的水箱和换滤芯周期分别是多少",
  "query_plan": null,
  "mapped_groups": [
    {
      "group_id": "g1",
      "alternatives": [
        [
          1856
        ]
      ]
    },
    {
      "group_id": "g2",
      "alternatives": [
        [
          1858
        ]
      ]
    }
  ],
  "candidate_ids": null,
  "final_ids": null,
  "prompt_citations": null,
  "decision": null,
  "answer": null,
  "point_verdicts": null,
  "claim_verdicts": null,
  "metrics": {
    "recall_at_5": null,
    "recall_at_10": null,
    "mrr_at_10": null,
    "all_groups_hit_at_5": null,
    "all_groups_hit_at_10": null,
    "candidate_group_coverage": null,
    "prompt_group_coverage": null,
    "answer_point_coverage": null,
    "faithfulness": null,
    "absent_refusal_rate": null,
    "answerable_false_refusal_rate": null
  },
  "error": {
    "code": "rewrite_error",
    "type": "ServiceError",
    "message": "该阶段执行失败"
  },
  "elapsed_ms": 1839.666800107807,
  "judge_snapshot": null,
  "audit": {
    "audit_version": 1,
    "source_map_id": "d2dd350d860b8141e52306cbbcafb22f97d091194eb1cdc839a528c2990715eb",
    "gold_groups": [
      {
        "group_id": "g1",
        "alternatives": [
          [
            "product-specs.md:005:58f10003acf72bef5aa921d603dc1a58bb0332dcd7f8735057266e573f01e11b"
          ]
        ]
      },
      {
        "group_id": "g2",
        "alternatives": [
          [
            "product-specs.md:007:e9867a419061278a1bc0599bc3595ac01da4c561aea19bf0bf4c9bde5ba30e7f"
          ]
        ]
      }
    ],
    "answer_points": [
      {
        "point_id": "p1",
        "text": "MH-W20 水箱 2L，滤芯建议每 2 周换",
        "condition": "仅适用于自动饮水机(型号 MH-W20)所述范围",
        "aliases": []
      },
      {
        "point_id": "p2",
        "text": "MH-W60 水箱 6L，滤芯建议每 4 周换",
        "condition": "仅适用于自动饮水机 Pro 不锈钢(型号 MH-W60)所述范围",
        "aliases": []
      }
    ],
    "candidate_ranking": null,
    "final_ranking": null
  }
}
````

### E19 / hybrid

````json
{
  "eval_id": "E19",
  "strategy": "hybrid",
  "bucket": "E_multi",
  "difficulty": "multi",
  "category": null,
  "should_refuse": false,
  "refused": null,
  "status": "rewrite_error",
  "stage": "rewrite",
  "query": "饮水机 MH-W20 和 MH-W60 的水箱和换滤芯周期分别是多少",
  "query_plan": null,
  "mapped_groups": [
    {
      "group_id": "g1",
      "alternatives": [
        [
          1856
        ]
      ]
    },
    {
      "group_id": "g2",
      "alternatives": [
        [
          1858
        ]
      ]
    }
  ],
  "candidate_ids": null,
  "final_ids": null,
  "prompt_citations": null,
  "decision": null,
  "answer": null,
  "point_verdicts": null,
  "claim_verdicts": null,
  "metrics": {
    "recall_at_5": null,
    "recall_at_10": null,
    "mrr_at_10": null,
    "all_groups_hit_at_5": null,
    "all_groups_hit_at_10": null,
    "candidate_group_coverage": null,
    "prompt_group_coverage": null,
    "answer_point_coverage": null,
    "faithfulness": null,
    "absent_refusal_rate": null,
    "answerable_false_refusal_rate": null
  },
  "error": {
    "code": "rewrite_error",
    "type": "ServiceError",
    "message": "该阶段执行失败"
  },
  "elapsed_ms": 1839.666800107807,
  "judge_snapshot": null,
  "audit": {
    "audit_version": 1,
    "source_map_id": "d2dd350d860b8141e52306cbbcafb22f97d091194eb1cdc839a528c2990715eb",
    "gold_groups": [
      {
        "group_id": "g1",
        "alternatives": [
          [
            "product-specs.md:005:58f10003acf72bef5aa921d603dc1a58bb0332dcd7f8735057266e573f01e11b"
          ]
        ]
      },
      {
        "group_id": "g2",
        "alternatives": [
          [
            "product-specs.md:007:e9867a419061278a1bc0599bc3595ac01da4c561aea19bf0bf4c9bde5ba30e7f"
          ]
        ]
      }
    ],
    "answer_points": [
      {
        "point_id": "p1",
        "text": "MH-W20 水箱 2L，滤芯建议每 2 周换",
        "condition": "仅适用于自动饮水机(型号 MH-W20)所述范围",
        "aliases": []
      },
      {
        "point_id": "p2",
        "text": "MH-W60 水箱 6L，滤芯建议每 4 周换",
        "condition": "仅适用于自动饮水机 Pro 不锈钢(型号 MH-W60)所述范围",
        "aliases": []
      }
    ],
    "candidate_ranking": null,
    "final_ranking": null
  }
}
````

### E19 / hybrid_rerank

````json
{
  "eval_id": "E19",
  "strategy": "hybrid_rerank",
  "bucket": "E_multi",
  "difficulty": "multi",
  "category": null,
  "should_refuse": false,
  "refused": null,
  "status": "rewrite_error",
  "stage": "rewrite",
  "query": "饮水机 MH-W20 和 MH-W60 的水箱和换滤芯周期分别是多少",
  "query_plan": null,
  "mapped_groups": [
    {
      "group_id": "g1",
      "alternatives": [
        [
          1856
        ]
      ]
    },
    {
      "group_id": "g2",
      "alternatives": [
        [
          1858
        ]
      ]
    }
  ],
  "candidate_ids": null,
  "final_ids": null,
  "prompt_citations": null,
  "decision": null,
  "answer": null,
  "point_verdicts": null,
  "claim_verdicts": null,
  "metrics": {
    "recall_at_5": null,
    "recall_at_10": null,
    "mrr_at_10": null,
    "all_groups_hit_at_5": null,
    "all_groups_hit_at_10": null,
    "candidate_group_coverage": null,
    "prompt_group_coverage": null,
    "answer_point_coverage": null,
    "faithfulness": null,
    "absent_refusal_rate": null,
    "answerable_false_refusal_rate": null
  },
  "error": {
    "code": "rewrite_error",
    "type": "ServiceError",
    "message": "该阶段执行失败"
  },
  "elapsed_ms": 1839.666800107807,
  "judge_snapshot": null,
  "audit": {
    "audit_version": 1,
    "source_map_id": "d2dd350d860b8141e52306cbbcafb22f97d091194eb1cdc839a528c2990715eb",
    "gold_groups": [
      {
        "group_id": "g1",
        "alternatives": [
          [
            "product-specs.md:005:58f10003acf72bef5aa921d603dc1a58bb0332dcd7f8735057266e573f01e11b"
          ]
        ]
      },
      {
        "group_id": "g2",
        "alternatives": [
          [
            "product-specs.md:007:e9867a419061278a1bc0599bc3595ac01da4c561aea19bf0bf4c9bde5ba30e7f"
          ]
        ]
      }
    ],
    "answer_points": [
      {
        "point_id": "p1",
        "text": "MH-W20 水箱 2L，滤芯建议每 2 周换",
        "condition": "仅适用于自动饮水机(型号 MH-W20)所述范围",
        "aliases": []
      },
      {
        "point_id": "p2",
        "text": "MH-W60 水箱 6L，滤芯建议每 4 周换",
        "condition": "仅适用于自动饮水机 Pro 不锈钢(型号 MH-W60)所述范围",
        "aliases": []
      }
    ],
    "candidate_ranking": null,
    "final_ranking": null
  }
}
````
