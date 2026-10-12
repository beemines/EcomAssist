# RAG 评估报告

运行：aecdf615794d4ccdad984c9caeda979f

状态：completed；范围：pilot

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
        "completed": 10,
        "errors": 0,
        "not_attempted": 0,
        "status_counts": {
          "completed": 10,
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
            "valid_n": 8,
            "excluded": {
              "expected_refusal": 2
            }
          },
          "recall_at_10": {
            "value": 1.0,
            "valid_n": 8,
            "excluded": {
              "expected_refusal": 2
            }
          },
          "mrr_at_10": {
            "value": 1.0,
            "valid_n": 8,
            "excluded": {
              "expected_refusal": 2
            }
          },
          "all_groups_hit_at_5": {
            "value": 1.0,
            "valid_n": 8,
            "excluded": {
              "expected_refusal": 2
            }
          },
          "all_groups_hit_at_10": {
            "value": 1.0,
            "valid_n": 8,
            "excluded": {
              "expected_refusal": 2
            }
          },
          "candidate_group_coverage": {
            "value": 1.0,
            "valid_n": 8,
            "excluded": {
              "expected_refusal": 2
            }
          },
          "prompt_group_coverage": {
            "value": 1.0,
            "valid_n": 8,
            "excluded": {
              "expected_refusal": 2
            }
          },
          "answer_point_coverage": {
            "value": 0.9583333333333334,
            "valid_n": 8,
            "excluded": {
              "expected_refusal": 2
            }
          },
          "faithfulness": {
            "value": 0.9722222222222222,
            "valid_n": 9,
            "excluded": {
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
            "valid_n": 8,
            "excluded": {
              "expected_refusal": 2
            }
          }
        }
      },
      {
        "bucket": "overall",
        "strategy": "bm25",
        "total": 10,
        "attempted": 10,
        "completed": 10,
        "errors": 0,
        "not_attempted": 0,
        "status_counts": {
          "completed": 10,
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
            "value": 0.9166666666666666,
            "valid_n": 8,
            "excluded": {
              "expected_refusal": 2
            }
          },
          "recall_at_10": {
            "value": 0.9583333333333334,
            "valid_n": 8,
            "excluded": {
              "expected_refusal": 2
            }
          },
          "mrr_at_10": {
            "value": 0.9166666666666666,
            "valid_n": 8,
            "excluded": {
              "expected_refusal": 2
            }
          },
          "all_groups_hit_at_5": {
            "value": 0.875,
            "valid_n": 8,
            "excluded": {
              "expected_refusal": 2
            }
          },
          "all_groups_hit_at_10": {
            "value": 0.875,
            "valid_n": 8,
            "excluded": {
              "expected_refusal": 2
            }
          },
          "candidate_group_coverage": {
            "value": 1.0,
            "valid_n": 8,
            "excluded": {
              "expected_refusal": 2
            }
          },
          "prompt_group_coverage": {
            "value": 0.9583333333333334,
            "valid_n": 8,
            "excluded": {
              "expected_refusal": 2
            }
          },
          "answer_point_coverage": {
            "value": 0.8125,
            "valid_n": 8,
            "excluded": {
              "expected_refusal": 2
            }
          },
          "faithfulness": {
            "value": 1.0,
            "valid_n": 8,
            "excluded": {
              "zero_claims": 2
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
            "value": 0.125,
            "valid_n": 8,
            "excluded": {
              "expected_refusal": 2
            }
          }
        }
      },
      {
        "bucket": "overall",
        "strategy": "hybrid",
        "total": 10,
        "attempted": 10,
        "completed": 10,
        "errors": 0,
        "not_attempted": 0,
        "status_counts": {
          "completed": 10,
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
            "value": 0.9583333333333334,
            "valid_n": 8,
            "excluded": {
              "expected_refusal": 2
            }
          },
          "recall_at_10": {
            "value": 1.0,
            "valid_n": 8,
            "excluded": {
              "expected_refusal": 2
            }
          },
          "mrr_at_10": {
            "value": 0.9375,
            "valid_n": 8,
            "excluded": {
              "expected_refusal": 2
            }
          },
          "all_groups_hit_at_5": {
            "value": 0.875,
            "valid_n": 8,
            "excluded": {
              "expected_refusal": 2
            }
          },
          "all_groups_hit_at_10": {
            "value": 1.0,
            "valid_n": 8,
            "excluded": {
              "expected_refusal": 2
            }
          },
          "candidate_group_coverage": {
            "value": 1.0,
            "valid_n": 8,
            "excluded": {
              "expected_refusal": 2
            }
          },
          "prompt_group_coverage": {
            "value": 1.0,
            "valid_n": 8,
            "excluded": {
              "expected_refusal": 2
            }
          },
          "answer_point_coverage": {
            "value": 0.9375,
            "valid_n": 8,
            "excluded": {
              "expected_refusal": 2
            }
          },
          "faithfulness": {
            "value": 1.0,
            "valid_n": 8,
            "excluded": {
              "zero_claims": 2
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
            "valid_n": 8,
            "excluded": {
              "expected_refusal": 2
            }
          }
        }
      },
      {
        "bucket": "overall",
        "strategy": "hybrid_rerank",
        "total": 10,
        "attempted": 10,
        "completed": 10,
        "errors": 0,
        "not_attempted": 0,
        "status_counts": {
          "completed": 10,
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
            "valid_n": 8,
            "excluded": {
              "expected_refusal": 2
            }
          },
          "recall_at_10": {
            "value": 1.0,
            "valid_n": 8,
            "excluded": {
              "expected_refusal": 2
            }
          },
          "mrr_at_10": {
            "value": 1.0,
            "valid_n": 8,
            "excluded": {
              "expected_refusal": 2
            }
          },
          "all_groups_hit_at_5": {
            "value": 1.0,
            "valid_n": 8,
            "excluded": {
              "expected_refusal": 2
            }
          },
          "all_groups_hit_at_10": {
            "value": 1.0,
            "valid_n": 8,
            "excluded": {
              "expected_refusal": 2
            }
          },
          "candidate_group_coverage": {
            "value": 1.0,
            "valid_n": 8,
            "excluded": {
              "expected_refusal": 2
            }
          },
          "prompt_group_coverage": {
            "value": 1.0,
            "valid_n": 8,
            "excluded": {
              "expected_refusal": 2
            }
          },
          "answer_point_coverage": {
            "value": 0.9375,
            "valid_n": 8,
            "excluded": {
              "expected_refusal": 2
            }
          },
          "faithfulness": {
            "value": 1.0,
            "valid_n": 8,
            "excluded": {
              "zero_claims": 2
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
            "valid_n": 8,
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
            "value": 0.75,
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
            "value": 0.75,
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
        "bucket": "B_model",
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
        "bucket": "B_model",
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
        "bucket": "B_model",
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
        "bucket": "B_model",
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
            "value": 0.875,
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
            "value": null,
            "valid_n": 0,
            "excluded": {
              "zero_claims": 2
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
            "value": null,
            "valid_n": 0,
            "excluded": {
              "zero_claims": 2
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
            "value": 0.8333333333333333,
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
        "bucket": "E_multi",
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
            "value": 0.6666666666666666,
            "valid_n": 2,
            "excluded": {}
          },
          "recall_at_10": {
            "value": 0.8333333333333333,
            "valid_n": 2,
            "excluded": {}
          },
          "mrr_at_10": {
            "value": 1.0,
            "valid_n": 2,
            "excluded": {}
          },
          "all_groups_hit_at_5": {
            "value": 0.5,
            "valid_n": 2,
            "excluded": {}
          },
          "all_groups_hit_at_10": {
            "value": 0.5,
            "valid_n": 2,
            "excluded": {}
          },
          "candidate_group_coverage": {
            "value": 1.0,
            "valid_n": 2,
            "excluded": {}
          },
          "prompt_group_coverage": {
            "value": 0.8333333333333333,
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
        "bucket": "E_multi",
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
            "value": 0.8333333333333333,
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
            "value": 0.5,
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
        "bucket": "E_multi",
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
      }
    ],
    "common_generation": {
      "eval_ids": [
        "A21",
        "A43",
        "B3",
        "B54",
        "C35",
        "C5",
        "D1",
        "D3",
        "E19",
        "E2"
      ],
      "valid_n": 10,
      "rows": [
        {
          "bucket": "overall",
          "strategy": "dense",
          "total": 10,
          "attempted": 10,
          "completed": 10,
          "errors": 0,
          "not_attempted": 0,
          "status_counts": {
            "completed": 10,
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
              "valid_n": 8,
              "excluded": {
                "expected_refusal": 2
              }
            },
            "recall_at_10": {
              "value": 1.0,
              "valid_n": 8,
              "excluded": {
                "expected_refusal": 2
              }
            },
            "mrr_at_10": {
              "value": 1.0,
              "valid_n": 8,
              "excluded": {
                "expected_refusal": 2
              }
            },
            "all_groups_hit_at_5": {
              "value": 1.0,
              "valid_n": 8,
              "excluded": {
                "expected_refusal": 2
              }
            },
            "all_groups_hit_at_10": {
              "value": 1.0,
              "valid_n": 8,
              "excluded": {
                "expected_refusal": 2
              }
            },
            "candidate_group_coverage": {
              "value": 1.0,
              "valid_n": 8,
              "excluded": {
                "expected_refusal": 2
              }
            },
            "prompt_group_coverage": {
              "value": 1.0,
              "valid_n": 8,
              "excluded": {
                "expected_refusal": 2
              }
            },
            "answer_point_coverage": {
              "value": 0.9583333333333334,
              "valid_n": 8,
              "excluded": {
                "expected_refusal": 2
              }
            },
            "faithfulness": {
              "value": 0.9722222222222222,
              "valid_n": 9,
              "excluded": {
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
              "valid_n": 8,
              "excluded": {
                "expected_refusal": 2
              }
            }
          }
        },
        {
          "bucket": "overall",
          "strategy": "bm25",
          "total": 10,
          "attempted": 10,
          "completed": 10,
          "errors": 0,
          "not_attempted": 0,
          "status_counts": {
            "completed": 10,
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
              "value": 0.9166666666666666,
              "valid_n": 8,
              "excluded": {
                "expected_refusal": 2
              }
            },
            "recall_at_10": {
              "value": 0.9583333333333334,
              "valid_n": 8,
              "excluded": {
                "expected_refusal": 2
              }
            },
            "mrr_at_10": {
              "value": 0.9166666666666666,
              "valid_n": 8,
              "excluded": {
                "expected_refusal": 2
              }
            },
            "all_groups_hit_at_5": {
              "value": 0.875,
              "valid_n": 8,
              "excluded": {
                "expected_refusal": 2
              }
            },
            "all_groups_hit_at_10": {
              "value": 0.875,
              "valid_n": 8,
              "excluded": {
                "expected_refusal": 2
              }
            },
            "candidate_group_coverage": {
              "value": 1.0,
              "valid_n": 8,
              "excluded": {
                "expected_refusal": 2
              }
            },
            "prompt_group_coverage": {
              "value": 0.9583333333333334,
              "valid_n": 8,
              "excluded": {
                "expected_refusal": 2
              }
            },
            "answer_point_coverage": {
              "value": 0.8125,
              "valid_n": 8,
              "excluded": {
                "expected_refusal": 2
              }
            },
            "faithfulness": {
              "value": 1.0,
              "valid_n": 8,
              "excluded": {
                "zero_claims": 2
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
              "value": 0.125,
              "valid_n": 8,
              "excluded": {
                "expected_refusal": 2
              }
            }
          }
        },
        {
          "bucket": "overall",
          "strategy": "hybrid",
          "total": 10,
          "attempted": 10,
          "completed": 10,
          "errors": 0,
          "not_attempted": 0,
          "status_counts": {
            "completed": 10,
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
              "value": 0.9583333333333334,
              "valid_n": 8,
              "excluded": {
                "expected_refusal": 2
              }
            },
            "recall_at_10": {
              "value": 1.0,
              "valid_n": 8,
              "excluded": {
                "expected_refusal": 2
              }
            },
            "mrr_at_10": {
              "value": 0.9375,
              "valid_n": 8,
              "excluded": {
                "expected_refusal": 2
              }
            },
            "all_groups_hit_at_5": {
              "value": 0.875,
              "valid_n": 8,
              "excluded": {
                "expected_refusal": 2
              }
            },
            "all_groups_hit_at_10": {
              "value": 1.0,
              "valid_n": 8,
              "excluded": {
                "expected_refusal": 2
              }
            },
            "candidate_group_coverage": {
              "value": 1.0,
              "valid_n": 8,
              "excluded": {
                "expected_refusal": 2
              }
            },
            "prompt_group_coverage": {
              "value": 1.0,
              "valid_n": 8,
              "excluded": {
                "expected_refusal": 2
              }
            },
            "answer_point_coverage": {
              "value": 0.9375,
              "valid_n": 8,
              "excluded": {
                "expected_refusal": 2
              }
            },
            "faithfulness": {
              "value": 1.0,
              "valid_n": 8,
              "excluded": {
                "zero_claims": 2
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
              "valid_n": 8,
              "excluded": {
                "expected_refusal": 2
              }
            }
          }
        },
        {
          "bucket": "overall",
          "strategy": "hybrid_rerank",
          "total": 10,
          "attempted": 10,
          "completed": 10,
          "errors": 0,
          "not_attempted": 0,
          "status_counts": {
            "completed": 10,
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
              "valid_n": 8,
              "excluded": {
                "expected_refusal": 2
              }
            },
            "recall_at_10": {
              "value": 1.0,
              "valid_n": 8,
              "excluded": {
                "expected_refusal": 2
              }
            },
            "mrr_at_10": {
              "value": 1.0,
              "valid_n": 8,
              "excluded": {
                "expected_refusal": 2
              }
            },
            "all_groups_hit_at_5": {
              "value": 1.0,
              "valid_n": 8,
              "excluded": {
                "expected_refusal": 2
              }
            },
            "all_groups_hit_at_10": {
              "value": 1.0,
              "valid_n": 8,
              "excluded": {
                "expected_refusal": 2
              }
            },
            "candidate_group_coverage": {
              "value": 1.0,
              "valid_n": 8,
              "excluded": {
                "expected_refusal": 2
              }
            },
            "prompt_group_coverage": {
              "value": 1.0,
              "valid_n": 8,
              "excluded": {
                "expected_refusal": 2
              }
            },
            "answer_point_coverage": {
              "value": 0.9375,
              "valid_n": 8,
              "excluded": {
                "expected_refusal": 2
              }
            },
            "faithfulness": {
              "value": 1.0,
              "valid_n": 8,
              "excluded": {
                "zero_claims": 2
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
              "valid_n": 8,
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
              "value": 0.75,
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
              "value": 0.75,
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
          "bucket": "B_model",
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
          "bucket": "B_model",
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
          "bucket": "B_model",
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
          "bucket": "B_model",
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
              "value": 0.875,
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
              "value": null,
              "valid_n": 0,
              "excluded": {
                "zero_claims": 2
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
              "value": null,
              "valid_n": 0,
              "excluded": {
                "zero_claims": 2
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
              "value": 0.8333333333333333,
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
          "bucket": "E_multi",
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
              "value": 0.6666666666666666,
              "valid_n": 2,
              "excluded": {}
            },
            "recall_at_10": {
              "value": 0.8333333333333333,
              "valid_n": 2,
              "excluded": {}
            },
            "mrr_at_10": {
              "value": 1.0,
              "valid_n": 2,
              "excluded": {}
            },
            "all_groups_hit_at_5": {
              "value": 0.5,
              "valid_n": 2,
              "excluded": {}
            },
            "all_groups_hit_at_10": {
              "value": 0.5,
              "valid_n": 2,
              "excluded": {}
            },
            "candidate_group_coverage": {
              "value": 1.0,
              "valid_n": 2,
              "excluded": {}
            },
            "prompt_group_coverage": {
              "value": 0.8333333333333333,
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
          "bucket": "E_multi",
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
              "value": 0.8333333333333333,
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
              "value": 0.5,
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
          "bucket": "E_multi",
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
        }
      ]
    },
    "rewrite": {
      "attempted_n": 10,
      "success_n": 10,
      "degraded_n": 0,
      "error_n": 0,
      "success_rate": 1.0,
      "unreported_n": 0
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
        "chunk_id": 1931,
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
        "chunk_id": 1932,
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
        "chunk_id": 1933,
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
        "chunk_id": 1934,
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
        "chunk_id": 1935,
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
        "chunk_id": 1936,
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
        "chunk_id": 1937,
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
        "chunk_id": 1938,
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
        "chunk_id": 1939,
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
        "chunk_id": 1940,
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
        "chunk_id": 1941,
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
        "chunk_id": 1942,
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
        "chunk_id": 1943,
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
        "chunk_id": 1944,
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
        "chunk_id": 1945,
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
        "chunk_id": 1946,
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
        "chunk_id": 1947,
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
        "chunk_id": 1948,
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
        "chunk_id": 1949,
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
        "chunk_id": 1950,
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
        "chunk_id": 1951,
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
        "chunk_id": 1952,
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
        "chunk_id": 1953,
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
        "chunk_id": 1954,
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
        "chunk_id": 1955,
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
        "chunk_id": 1956,
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
        "chunk_id": 1957,
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
        "chunk_id": 1958,
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
        "chunk_id": 1959,
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
        "chunk_id": 1960,
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
        "chunk_id": 1961,
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
        "chunk_id": 1962,
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
        "chunk_id": 1963,
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
        "chunk_id": 1964,
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
        "chunk_id": 1965,
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
        "chunk_id": 1966,
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
        "chunk_id": 1967,
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
        "chunk_id": 1968,
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
        "chunk_id": 1969,
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
        "chunk_id": 1970,
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
        "chunk_id": 1971,
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
        "chunk_id": 1972,
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
        "chunk_id": 1973,
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
        "chunk_id": 1974,
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
        "chunk_id": 1975,
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
        "chunk_id": 1976,
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
        "chunk_id": 1977,
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
        "chunk_id": 1978,
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
        "chunk_id": 1979,
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
        "chunk_id": 1980,
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
    "source_map_id": "af6590ab401319d942bddff0b30213a4cd888b8cf115ebd5cdec3adb87687e55"
  },
  "run_id": "aecdf615794d4ccdad984c9caeda979f",
  "dataset_id": "merchant-rag-300-v1",
  "fingerprint": "46d11df092ca2b803030fb7e227d971ef7530552bb5d18b4939bfc0c7f186ee7",
  "scope": "pilot",
  "run": {
    "schema_version": 2,
    "run_id": "aecdf615794d4ccdad984c9caeda979f",
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
        "llm_reasoning_effort": "low",
        "rewrite_failure_policy": "original-query-on-invalid-v1"
      },
      "fingerprint": "46d11df092ca2b803030fb7e227d971ef7530552bb5d18b4939bfc0c7f186ee7"
    },
    "state": "completed",
    "outcome": "completed",
    "stage": "complete",
    "planned_cases": 10,
    "planned_strategies": 4,
    "planned_records": 40,
    "counts": {
      "completed": 40,
      "rewrite_error": 0,
      "retrieval_error": 0,
      "self_check_error": 0,
      "answer_error": 0,
      "judge_error": 0,
      "cancelled": 0,
      "not_attempted": 0,
      "running": 0,
      "total": 40,
      "attempted": 40,
      "errors": 0
    },
    "request_counts": {
      "rewrite": 10,
      "self_check": 40,
      "answer": 31,
      "judge": 40,
      "embedding": 33,
      "rerank": 10,
      "milvus": 74
    },
    "cleanup": {
      "ok": true,
      "errors": [],
      "unverified": []
    },
    "created_at": "2026-10-11T06:09:32.227568+00:00",
    "updated_at": "2026-10-11T06:12:58.653668+00:00",
    "started_at": "2026-10-11T06:09:32.250669+00:00",
    "finished_at": "2026-10-11T06:12:58.688304+00:00",
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
          1974
        ]
      ]
    },
    {
      "group_id": "g2",
      "alternatives": [
        [
          1975
        ]
      ]
    }
  ],
  "candidate_ids": [
    1975,
    1945,
    1974,
    1977,
    1953,
    1954,
    1933,
    1955,
    1951,
    1937,
    1959,
    1976,
    1952,
    1961,
    1960,
    1942,
    1962,
    1944,
    1957,
    1950,
    1972,
    1963,
    1946,
    1964,
    1958,
    1947,
    1934,
    1978,
    1956,
    1932,
    1970,
    1940,
    1938,
    1943,
    1973,
    1979,
    1931,
    1965,
    1967,
    1971,
    1936,
    1968,
    1980,
    1935,
    1949,
    1941,
    1969,
    1966,
    1939,
    1948
  ],
  "final_ids": [
    1975,
    1945,
    1974,
    1977,
    1953,
    1954,
    1933,
    1955,
    1951,
    1937
  ],
  "prompt_citations": [
    {
      "n": 1,
      "chunk_id": "1975",
      "section_path": "会员权益/生日礼",
      "question": "生日礼",
      "answer": "银卡会员生日当月可领取一份猫零食小样，金卡会员生日当月可领取一份猫罐头礼盒。需在会员中心领取，礼品规格与领取期限以页面标注为准，不承诺额外折现或补偿。"
    },
    {
      "n": 3,
      "chunk_id": "1974",
      "section_path": "会员权益/会员等级",
      "question": "会员等级",
      "answer": "会员分为普通、银卡和金卡三档，按有效累计消费金额自动升级，不按年度消费金额计算。累计消费未满 1000 元为普通会员，满 1000 元起为银卡，满 5000 元起为金卡。\n\n有效累计消费指已完成订单的商品实际支付金额，不含配送费；退货退款部分从有效累计消费中扣除。退款后根据更新的累计消费重新计算等级，未达到原门槛时可能降级。等级与适用权益在会员中心展示。\n\n银卡在参与会员折扣的商品上享 95 折，金卡享 9 折。折扣适用商品和活动范围以结算页面标注为准。会员折扣、优惠券与满减是否叠加也以当次活动页面为准，不能一概承诺全部优惠同时生效。"
    },
    {
      "n": 5,
      "chunk_id": "1953",
      "section_path": "商品规格手册/智能猫砂盆 Pro(型号 MH-LP100)",
      "question": "智能猫砂盆 Pro(型号 MH-LP100)",
      "answer": "- 型号:MH-LP100\n- 适用猫咪体重:1.5kg 至 8kg\n- 猫砂容量:9L,废砂盒容量约 7 天(单猫)\n- 核心功能:自动感应清理、活性炭除臭、App 远程监控与健康记录\n- 供电:220V 市电,断电后配置自动保存\n- 清理提示:废砂盒满时 App 推送提醒,建议每 5 至 7 天倾倒一次"
    },
    {
      "n": 7,
      "chunk_id": "1933",
      "section_path": "售后手册/设备安装与激活",
      "question": "设备安装与激活",
      "answer": "智能设备首次使用需下载「喵喵优选」App,按说明书扫码添加设备并连接 2.4G Wi-Fi 完成激活;猫爬架等非联网商品按随附图解自行组装。"
    },
    {
      "n": 9,
      "chunk_id": "1951",
      "section_path": "商品与购物 FAQ/会员运费权益",
      "question": "会员运费权益",
      "answer": "金卡会员每月享 3 次免运费权益,银卡会员享 1 次;权益不与偏远地区附加运费冲抵,当月未用完不结转。"
    },
    {
      "n": 10,
      "chunk_id": "1937",
      "section_path": "售后手册/会员专属售后权益",
      "question": "会员专属售后权益",
      "answer": "金卡会员享优先客服接入与上门取件退换货;银卡会员享退换货运费权益 1 次/月。具体权益以会员中心页面标注为准。"
    },
    {
      "n": 8,
      "chunk_id": "1955",
      "section_path": "商品规格手册/智能猫砂盆 Max(型号 MH-LP200)",
      "question": "智能猫砂盆 Max(型号 MH-LP200)",
      "answer": "- 型号:MH-LP200\n- 适用猫咪体重:2kg 至 12kg,适合大型猫与多猫家庭\n- 猫砂容量:12L,废砂盒容量约 10 天(单猫)\n- 核心功能:超大滚筒、双重称重防夹、活性炭除臭、App 多猫健康档案\n- 供电:220V 市电\n- 清理提示:多猫家庭建议每 3 至 5 天倾倒一次废砂盒"
    },
    {
      "n": 6,
      "chunk_id": "1954",
      "section_path": "商品规格手册/智能猫砂盆 Lite(型号 MH-LP50)",
      "question": "智能猫砂盆 Lite(型号 MH-LP50)",
      "answer": "- 型号:MH-LP50\n- 适用猫咪体重:1.5kg 至 6kg\n- 猫砂容量:6L\n- 核心功能:自动感应清理、物理除臭盖板;不含 App 联网功能\n- 与 Pro 差异:Lite 无 App 远程监控与健康记录,价格更低,适合单猫家庭"
    },
    {
      "n": 4,
      "chunk_id": "1977",
      "section_path": "积分规则/积分怎么用",
      "question": "积分怎么用",
      "answer": "积分可在结算时抵扣商品金额，100 积分抵 1 元现金，单笔订单最多抵 30 元，不用于抵扣偏远地区附加运费，也不支持直接提现。\n\n2000 积分可兑换自动饮水机滤芯 3 片，该兑换套装适用于 MH-W40，普通配送地区包邮；偏远地区附加配送费仍需按页面规则确认。MH-W40 的滤芯更换周期以商品规格手册为准。\n\n800 积分可兑换猫零食小样，普通配送地区另收 6 元运费；该兑换不直接套用普通购物订单的满 99 元包邮规则。兑换商品、可用库存及偏远地区配送规则以兑换页面标注为准。"
    },
    {
      "n": 2,
      "chunk_id": "1945",
      "section_path": "商品与购物 FAQ/会员等级与积分规则",
      "question": "会员等级与积分规则",
      "answer": "会员分为普通、银卡、金卡三档,按累计消费自动升级。每消费 1 元得 1 积分,积分可在结算时抵扣,100 积分抵 1 元。"
    }
  ],
  "decision": {
    "useful": true,
    "reason": "等级按累计消费5000元为金卡，生日礼有证据",
    "response_kind": "knowledge",
    "source": null
  },
  "answer": "您好！为您解答如下：\n\n**金卡等级门槛**：会员按有效累计消费金额自动升级（不按年度计算），累计消费满 5000 元起为金卡[3]。有效累计消费指已完成订单的商品实际支付金额，不含配送费，退货退款部分会扣除[3]。\n\n**生日礼**：金卡会员生日当月可在会员中心领取一份猫罐头礼盒（银卡为猫零食小样），礼品规格与领取期限以页面标注为准[1]。\n\n祝您购物愉快！",
  "point_verdicts": [
    {
      "point_id": "p1",
      "covered": true,
      "reason": "回答明确金卡按有效累计消费满5000元升级、不按年度计算，并说明实付金额、不含配送费、退款扣除[3]"
    },
    {
      "point_id": "p2",
      "covered": true,
      "reason": "回答说明金卡生日当月在会员中心领取猫罐头礼盒，规格与领取期限以页面标注为准[1]"
    }
  ],
  "claim_verdicts": [
    {
      "claim": "会员按有效累计消费金额自动升级，不按年度计算，累计消费满5000元起为金卡",
      "supported": true,
      "reason": "证据[3]明确按有效累计消费自动升级、不按年度计算，满5000元为金卡"
    },
    {
      "claim": "有效累计消费指已完成订单的商品实际支付金额，不含配送费，退货退款部分会扣除",
      "supported": true,
      "reason": "证据[3]明确该定义与退款扣除规则"
    },
    {
      "claim": "金卡会员生日当月可在会员中心领取一份猫罐头礼盒",
      "supported": true,
      "reason": "证据[1]明确金卡生日当月可在会员中心领取猫罐头礼盒"
    },
    {
      "claim": "银卡会员生日礼为猫零食小样",
      "supported": true,
      "reason": "证据[1]明确银卡生日当月领取猫零食小样"
    },
    {
      "claim": "生日礼品规格与领取期限以页面标注为准",
      "supported": true,
      "reason": "证据[1]明确礼品规格与领取期限以页面标注为准"
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
  "elapsed_ms": 11410.867400001734,
  "judge_snapshot": {
    "prompt_version": "joint-generation-v2.1",
    "finish_reason": "stop"
  },
  "rewrite": {
    "policy_version": "original-query-on-invalid-v1",
    "status": "success",
    "error": null
  },
  "audit": {
    "audit_version": 1,
    "source_map_id": "af6590ab401319d942bddff0b30213a4cd888b8cf115ebd5cdec3adb87687e55",
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
        "chunk_id": 1975,
        "score": 0.6760553121566772,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1945,
        "score": 0.5822025537490845,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1974,
        "score": 0.5763506293296814,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1977,
        "score": 0.5374670624732971,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1953,
        "score": 0.5198246836662292,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1954,
        "score": 0.5181712508201599,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1933,
        "score": 0.5055581331253052,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1955,
        "score": 0.503547191619873,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1951,
        "score": 0.4964491128921509,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1937,
        "score": 0.4895363450050354,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1959,
        "score": 0.4892578721046448,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1976,
        "score": 0.469903826713562,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1952,
        "score": 0.4606747031211853,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1961,
        "score": 0.45703068375587463,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1960,
        "score": 0.45518824458122253,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1942,
        "score": 0.42638900876045227,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1962,
        "score": 0.41891855001449585,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1944,
        "score": 0.41226792335510254,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1957,
        "score": 0.40209293365478516,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1950,
        "score": 0.40096351504325867,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1972,
        "score": 0.39702826738357544,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1963,
        "score": 0.3952715992927551,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1946,
        "score": 0.3892870843410492,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1964,
        "score": 0.38561660051345825,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1958,
        "score": 0.38431379199028015,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1947,
        "score": 0.3831542134284973,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1934,
        "score": 0.3783602714538574,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1978,
        "score": 0.37430787086486816,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1956,
        "score": 0.3707234859466553,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1932,
        "score": 0.3675485849380493,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1970,
        "score": 0.36556193232536316,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1940,
        "score": 0.3642715513706207,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1938,
        "score": 0.3617609143257141,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1943,
        "score": 0.36141517758369446,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1973,
        "score": 0.35819584131240845,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1979,
        "score": 0.35550302267074585,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1931,
        "score": 0.35342466831207275,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1965,
        "score": 0.35231781005859375,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1967,
        "score": 0.34561458230018616,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1971,
        "score": 0.3423440456390381,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1936,
        "score": 0.3411083519458771,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1968,
        "score": 0.34092679619789124,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1980,
        "score": 0.33881208300590515,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1935,
        "score": 0.33717459440231323,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1949,
        "score": 0.3304835259914398,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1941,
        "score": 0.32148316502571106,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1969,
        "score": 0.3008221387863159,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1966,
        "score": 0.298246294260025,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1939,
        "score": 0.29349204897880554,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1948,
        "score": 0.2662397623062134,
        "score_kind": "cosine"
      }
    ],
    "final_ranking": [
      {
        "chunk_id": 1975,
        "score": 0.6760553121566772,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1945,
        "score": 0.5822025537490845,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1974,
        "score": 0.5763506293296814,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1977,
        "score": 0.5374670624732971,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1953,
        "score": 0.5198246836662292,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1954,
        "score": 0.5181712508201599,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1933,
        "score": 0.5055581331253052,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1955,
        "score": 0.503547191619873,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1951,
        "score": 0.4964491128921509,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1937,
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
          1974
        ]
      ]
    },
    {
      "group_id": "g2",
      "alternatives": [
        [
          1975
        ]
      ]
    }
  ],
  "candidate_ids": [
    1975,
    1974,
    1945,
    1976,
    1952,
    1933,
    1938
  ],
  "final_ids": [
    1975,
    1974,
    1945,
    1976,
    1952,
    1933,
    1938
  ],
  "prompt_citations": [
    {
      "n": 1,
      "chunk_id": "1975",
      "section_path": "会员权益/生日礼",
      "question": "生日礼",
      "answer": "银卡会员生日当月可领取一份猫零食小样，金卡会员生日当月可领取一份猫罐头礼盒。需在会员中心领取，礼品规格与领取期限以页面标注为准，不承诺额外折现或补偿。"
    },
    {
      "n": 3,
      "chunk_id": "1945",
      "section_path": "商品与购物 FAQ/会员等级与积分规则",
      "question": "会员等级与积分规则",
      "answer": "会员分为普通、银卡、金卡三档,按累计消费自动升级。每消费 1 元得 1 积分,积分可在结算时抵扣,100 积分抵 1 元。"
    },
    {
      "n": 5,
      "chunk_id": "1952",
      "section_path": "商品规格手册",
      "question": "商品规格手册",
      "answer": "本手册收录喵喵优选自营智能硬件的型号、规格与使用要点,便于按具体型号查询。"
    },
    {
      "n": 7,
      "chunk_id": "1938",
      "section_path": "商品与购物 FAQ/退货政策是什么",
      "question": "退货政策是什么",
      "answer": "支持 7 天无理由退货,商品需保持完好、不影响二次销售,具体以平台售后规则为准。"
    },
    {
      "n": 6,
      "chunk_id": "1933",
      "section_path": "售后手册/设备安装与激活",
      "question": "设备安装与激活",
      "answer": "智能设备首次使用需下载「喵喵优选」App,按说明书扫码添加设备并连接 2.4G Wi-Fi 完成激活;猫爬架等非联网商品按随附图解自行组装。"
    },
    {
      "n": 4,
      "chunk_id": "1976",
      "section_path": "积分规则/积分怎么攒",
      "question": "积分怎么攒",
      "answer": "已完成订单每实际支付 1 元商品金额累计 1 积分，不计配送费；退款后按对应商品金额同步扣回积分。活动期间的双倍积分属于额外积分奖励，不计入会员等级升级；会员等级仍按有效累计消费金额计算。"
    },
    {
      "n": 2,
      "chunk_id": "1974",
      "section_path": "会员权益/会员等级",
      "question": "会员等级",
      "answer": "会员分为普通、银卡和金卡三档，按有效累计消费金额自动升级，不按年度消费金额计算。累计消费未满 1000 元为普通会员，满 1000 元起为银卡，满 5000 元起为金卡。\n\n有效累计消费指已完成订单的商品实际支付金额，不含配送费；退货退款部分从有效累计消费中扣除。退款后根据更新的累计消费重新计算等级，未达到原门槛时可能降级。等级与适用权益在会员中心展示。\n\n银卡在参与会员折扣的商品上享 95 折，金卡享 9 折。折扣适用商品和活动范围以结算页面标注为准。会员折扣、优惠券与满减是否叠加也以当次活动页面为准，不能一概承诺全部优惠同时生效。"
    }
  ],
  "decision": {
    "useful": true,
    "reason": "等级按累计消费而非年消费，金卡门槛及生日礼均有证据",
    "response_kind": "knowledge",
    "source": null
  },
  "answer": "您好！根据查询结果为您说明：\n\n**喵金（金卡）等级**：会员按累计消费金额（有效累计消费，非年度消费）自动升级，累计消费满 **5000 元** 起为金卡（银卡为满 1000 元起）[2]。有效累计消费指已完成订单的商品实际支付金额，不含配送费，退货退款部分会扣除。\n\n**金卡生日礼**：金卡会员生日当月可领取一份**猫罐头礼盒**，需在会员中心领取，礼品规格与领取期限以页面标注为准，不承诺额外折现或补偿[1]。\n\n如有其他问题，欢迎随时咨询～",
  "point_verdicts": [
    {
      "point_id": "p1",
      "covered": false,
      "reason": "回答覆盖了满5000元起金卡、有效累计非年度消费、实付不含配送费、退款扣除等事实，但条件中'折扣活动范围以页面为准'未在回答中保留，缺条件判为false"
    },
    {
      "point_id": "p2",
      "covered": true,
      "reason": "回答明确金卡生日当月可在会员中心领取猫罐头礼盒，且规格与领取期限以页面标注为准，条件完整覆盖"
    }
  ],
  "claim_verdicts": [
    {
      "claim": "会员按累计消费金额自动升级，累计消费满5000元起为金卡（银卡为满1000元起）",
      "supported": true,
      "reason": "证据[2]明确会员按有效累计消费金额自动升级，满5000元起为金卡，满1000元起为银卡"
    },
    {
      "claim": "升级按累计消费而非年度消费计算",
      "supported": true,
      "reason": "证据[2]明确'不按年度消费金额计算'，按有效累计消费金额升级"
    },
    {
      "claim": "有效累计消费指已完成订单的商品实际支付金额，不含配送费，退货退款部分会扣除",
      "supported": true,
      "reason": "证据[2]明确有效累计消费为已完成订单商品实际支付金额，不含配送费，退货退款部分扣除"
    },
    {
      "claim": "金卡会员生日当月可领取一份猫罐头礼盒",
      "supported": true,
      "reason": "证据[1]明确金卡会员生日当月可领取一份猫罐头礼盒"
    },
    {
      "claim": "生日礼需在会员中心领取，礼品规格与领取期限以页面标注为准，不承诺额外折现或补偿",
      "supported": true,
      "reason": "证据[1]明确需在会员中心领取，规格与期限以页面标注为准，不承诺额外折现或补偿"
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
    "faithfulness": 1.0,
    "absent_refusal_rate": null,
    "answerable_false_refusal_rate": 0.0
  },
  "error": null,
  "elapsed_ms": 19022.62849989347,
  "judge_snapshot": {
    "prompt_version": "joint-generation-v2.1",
    "finish_reason": "stop"
  },
  "rewrite": {
    "policy_version": "original-query-on-invalid-v1",
    "status": "success",
    "error": null
  },
  "audit": {
    "audit_version": 1,
    "source_map_id": "af6590ab401319d942bddff0b30213a4cd888b8cf115ebd5cdec3adb87687e55",
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
        "chunk_id": 1975,
        "score": 9.339435577392578,
        "score_kind": "bm25"
      },
      {
        "chunk_id": 1974,
        "score": 7.171276092529297,
        "score_kind": "bm25"
      },
      {
        "chunk_id": 1945,
        "score": 6.90592098236084,
        "score_kind": "bm25"
      },
      {
        "chunk_id": 1976,
        "score": 6.212222576141357,
        "score_kind": "bm25"
      },
      {
        "chunk_id": 1952,
        "score": 4.681387424468994,
        "score_kind": "bm25"
      },
      {
        "chunk_id": 1933,
        "score": 4.314119338989258,
        "score_kind": "bm25"
      },
      {
        "chunk_id": 1938,
        "score": 4.2695698738098145,
        "score_kind": "bm25"
      }
    ],
    "final_ranking": [
      {
        "chunk_id": 1975,
        "score": 9.339435577392578,
        "score_kind": "bm25"
      },
      {
        "chunk_id": 1974,
        "score": 7.171276092529297,
        "score_kind": "bm25"
      },
      {
        "chunk_id": 1945,
        "score": 6.90592098236084,
        "score_kind": "bm25"
      },
      {
        "chunk_id": 1976,
        "score": 6.212222576141357,
        "score_kind": "bm25"
      },
      {
        "chunk_id": 1952,
        "score": 4.681387424468994,
        "score_kind": "bm25"
      },
      {
        "chunk_id": 1933,
        "score": 4.314119338989258,
        "score_kind": "bm25"
      },
      {
        "chunk_id": 1938,
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
          1974
        ]
      ]
    },
    {
      "group_id": "g2",
      "alternatives": [
        [
          1975
        ]
      ]
    }
  ],
  "candidate_ids": [
    1975,
    1945,
    1974,
    1933,
    1976,
    1952,
    1938,
    1977,
    1953,
    1954,
    1955,
    1951,
    1937,
    1959,
    1961,
    1960,
    1942,
    1962,
    1944,
    1957,
    1950,
    1972,
    1963,
    1946,
    1964,
    1958,
    1947,
    1934,
    1978,
    1956,
    1932,
    1970,
    1940,
    1943,
    1973,
    1979,
    1931,
    1965,
    1967,
    1971,
    1936,
    1968,
    1980,
    1935,
    1949,
    1941,
    1969,
    1966,
    1939,
    1948
  ],
  "final_ids": [
    1975,
    1945,
    1974,
    1933,
    1976,
    1952,
    1938,
    1977,
    1953,
    1954
  ],
  "prompt_citations": [
    {
      "n": 1,
      "chunk_id": "1975",
      "section_path": "会员权益/生日礼",
      "question": "生日礼",
      "answer": "银卡会员生日当月可领取一份猫零食小样，金卡会员生日当月可领取一份猫罐头礼盒。需在会员中心领取，礼品规格与领取期限以页面标注为准，不承诺额外折现或补偿。"
    },
    {
      "n": 3,
      "chunk_id": "1974",
      "section_path": "会员权益/会员等级",
      "question": "会员等级",
      "answer": "会员分为普通、银卡和金卡三档，按有效累计消费金额自动升级，不按年度消费金额计算。累计消费未满 1000 元为普通会员，满 1000 元起为银卡，满 5000 元起为金卡。\n\n有效累计消费指已完成订单的商品实际支付金额，不含配送费；退货退款部分从有效累计消费中扣除。退款后根据更新的累计消费重新计算等级，未达到原门槛时可能降级。等级与适用权益在会员中心展示。\n\n银卡在参与会员折扣的商品上享 95 折，金卡享 9 折。折扣适用商品和活动范围以结算页面标注为准。会员折扣、优惠券与满减是否叠加也以当次活动页面为准，不能一概承诺全部优惠同时生效。"
    },
    {
      "n": 5,
      "chunk_id": "1976",
      "section_path": "积分规则/积分怎么攒",
      "question": "积分怎么攒",
      "answer": "已完成订单每实际支付 1 元商品金额累计 1 积分，不计配送费；退款后按对应商品金额同步扣回积分。活动期间的双倍积分属于额外积分奖励，不计入会员等级升级；会员等级仍按有效累计消费金额计算。"
    },
    {
      "n": 7,
      "chunk_id": "1938",
      "section_path": "商品与购物 FAQ/退货政策是什么",
      "question": "退货政策是什么",
      "answer": "支持 7 天无理由退货,商品需保持完好、不影响二次销售,具体以平台售后规则为准。"
    },
    {
      "n": 9,
      "chunk_id": "1953",
      "section_path": "商品规格手册/智能猫砂盆 Pro(型号 MH-LP100)",
      "question": "智能猫砂盆 Pro(型号 MH-LP100)",
      "answer": "- 型号:MH-LP100\n- 适用猫咪体重:1.5kg 至 8kg\n- 猫砂容量:9L,废砂盒容量约 7 天(单猫)\n- 核心功能:自动感应清理、活性炭除臭、App 远程监控与健康记录\n- 供电:220V 市电,断电后配置自动保存\n- 清理提示:废砂盒满时 App 推送提醒,建议每 5 至 7 天倾倒一次"
    },
    {
      "n": 10,
      "chunk_id": "1954",
      "section_path": "商品规格手册/智能猫砂盆 Lite(型号 MH-LP50)",
      "question": "智能猫砂盆 Lite(型号 MH-LP50)",
      "answer": "- 型号:MH-LP50\n- 适用猫咪体重:1.5kg 至 6kg\n- 猫砂容量:6L\n- 核心功能:自动感应清理、物理除臭盖板;不含 App 联网功能\n- 与 Pro 差异:Lite 无 App 远程监控与健康记录,价格更低,适合单猫家庭"
    },
    {
      "n": 8,
      "chunk_id": "1977",
      "section_path": "积分规则/积分怎么用",
      "question": "积分怎么用",
      "answer": "积分可在结算时抵扣商品金额，100 积分抵 1 元现金，单笔订单最多抵 30 元，不用于抵扣偏远地区附加运费，也不支持直接提现。\n\n2000 积分可兑换自动饮水机滤芯 3 片，该兑换套装适用于 MH-W40，普通配送地区包邮；偏远地区附加配送费仍需按页面规则确认。MH-W40 的滤芯更换周期以商品规格手册为准。\n\n800 积分可兑换猫零食小样，普通配送地区另收 6 元运费；该兑换不直接套用普通购物订单的满 99 元包邮规则。兑换商品、可用库存及偏远地区配送规则以兑换页面标注为准。"
    },
    {
      "n": 6,
      "chunk_id": "1952",
      "section_path": "商品规格手册",
      "question": "商品规格手册",
      "answer": "本手册收录喵喵优选自营智能硬件的型号、规格与使用要点,便于按具体型号查询。"
    },
    {
      "n": 4,
      "chunk_id": "1933",
      "section_path": "售后手册/设备安装与激活",
      "question": "设备安装与激活",
      "answer": "智能设备首次使用需下载「喵喵优选」App,按说明书扫码添加设备并连接 2.4G Wi-Fi 完成激活;猫爬架等非联网商品按随附图解自行组装。"
    },
    {
      "n": 2,
      "chunk_id": "1945",
      "section_path": "商品与购物 FAQ/会员等级与积分规则",
      "question": "会员等级与积分规则",
      "answer": "会员分为普通、银卡、金卡三档,按累计消费自动升级。每消费 1 元得 1 积分,积分可在结算时抵扣,100 积分抵 1 元。"
    }
  ],
  "decision": {
    "useful": true,
    "reason": "证据覆盖会员等级门槛与生日礼，且说明按累计而非年消费",
    "response_kind": "knowledge",
    "source": null
  },
  "answer": "您好！根据我们的会员规则，等级并不是按年消费计算的，而是按有效累计消费金额自动升级：\n\n- 累计消费满 **5000 元**起为金卡会员（银卡为满 1000 元起）[3]\n- 有效累计消费指已完成订单的商品实际支付金额，不含配送费；退货退款部分会从中扣除，退款后若未达门槛可能降级 [3]\n\n**生日礼方面**：金卡会员在生日当月可领取一份**猫罐头礼盒**，需在会员中心领取，礼品规格与领取期限以页面标注为准，不承诺额外折现或补偿 [1]\n\n如有其他问题，欢迎随时咨询！",
  "point_verdicts": [
    {
      "point_id": "p1",
      "covered": false,
      "reason": "回答覆盖了满5000元升级金卡、不按年消费、有效累计消费为实付不含配送费及扣除退款等要点，但遗漏了适用条件中'折扣活动范围以页面为准'这一条件，属于仅覆盖部分事实。"
    },
    {
      "point_id": "p2",
      "covered": true,
      "reason": "回答说明金卡生日当月可在会员中心领取猫罐头礼盒，礼品规格与领取期限以页面标注为准，完整保留适用条件。"
    }
  ],
  "claim_verdicts": [
    {
      "claim": "会员等级按有效累计消费金额自动升级，不按年度消费金额计算",
      "supported": true,
      "reason": "证据3明确写明会员按有效累计消费金额自动升级，不按年度消费金额计算。"
    },
    {
      "claim": "累计消费满5000元起为金卡会员",
      "supported": true,
      "reason": "证据3写明满5000元起为金卡。"
    },
    {
      "claim": "银卡为累计消费满1000元起",
      "supported": true,
      "reason": "证据3写明满1000元起为银卡。"
    },
    {
      "claim": "有效累计消费指已完成订单的商品实际支付金额，不含配送费",
      "supported": true,
      "reason": "证据3明确有效累计消费为已完成订单商品实付金额且不含配送费。"
    },
    {
      "claim": "退货退款部分会从有效累计消费中扣除，退款后若未达门槛可能降级",
      "supported": true,
      "reason": "证据3写明退货退款部分从有效累计消费中扣除，退款后重新计算等级，未达门槛时可能降级。"
    },
    {
      "claim": "金卡会员生日当月可领取一份猫罐头礼盒，需在会员中心领取，规格与期限以页面标注为准，不承诺额外折现或补偿",
      "supported": true,
      "reason": "证据1明确金卡生日当月可领猫罐头礼盒，需在会员中心领取，规格期限以页面为准且不承诺折现补偿。"
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
    "faithfulness": 1.0,
    "absent_refusal_rate": null,
    "answerable_false_refusal_rate": 0.0
  },
  "error": null,
  "elapsed_ms": 19127.876499900594,
  "judge_snapshot": {
    "prompt_version": "joint-generation-v2.1",
    "finish_reason": "stop"
  },
  "rewrite": {
    "policy_version": "original-query-on-invalid-v1",
    "status": "success",
    "error": null
  },
  "audit": {
    "audit_version": 1,
    "source_map_id": "af6590ab401319d942bddff0b30213a4cd888b8cf115ebd5cdec3adb87687e55",
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
        "chunk_id": 1975,
        "score": 0.032786883413791656,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1945,
        "score": 0.0320020467042923,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1974,
        "score": 0.0320020467042923,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1933,
        "score": 0.03007688745856285,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1976,
        "score": 0.0295138880610466,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1952,
        "score": 0.029083244502544403,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1938,
        "score": 0.025678060948848724,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1977,
        "score": 0.015625,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1953,
        "score": 0.015384615398943424,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1954,
        "score": 0.01515151560306549,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1955,
        "score": 0.014705882407724857,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1951,
        "score": 0.014492753893136978,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1937,
        "score": 0.014285714365541935,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1959,
        "score": 0.014084506779909134,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1961,
        "score": 0.013513513840734959,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1960,
        "score": 0.013333333656191826,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1942,
        "score": 0.01315789483487606,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1962,
        "score": 0.012987012974917889,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1944,
        "score": 0.012820512987673283,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1957,
        "score": 0.012658228166401386,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1950,
        "score": 0.012500000186264515,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1972,
        "score": 0.012345679104328156,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1963,
        "score": 0.012195121496915817,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1946,
        "score": 0.012048192322254181,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1964,
        "score": 0.011904762126505375,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1958,
        "score": 0.0117647061124444,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1947,
        "score": 0.011627906933426857,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1934,
        "score": 0.01149425283074379,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1978,
        "score": 0.011363636702299118,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1956,
        "score": 0.01123595517128706,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1932,
        "score": 0.011111111380159855,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1970,
        "score": 0.010989011265337467,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1940,
        "score": 0.010869565419852734,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1943,
        "score": 0.010638297535479069,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1973,
        "score": 0.010526316240429878,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1979,
        "score": 0.010416666977107525,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1931,
        "score": 0.010309278033673763,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1965,
        "score": 0.010204081423580647,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1967,
        "score": 0.010101010091602802,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1971,
        "score": 0.009999999776482582,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1936,
        "score": 0.009900989942252636,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1968,
        "score": 0.009803921915590763,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1980,
        "score": 0.009708737954497337,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1935,
        "score": 0.009615384973585606,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1949,
        "score": 0.009523809887468815,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1941,
        "score": 0.009433962404727936,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1969,
        "score": 0.009345794096589088,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1966,
        "score": 0.009259259328246117,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1939,
        "score": 0.00917431153357029,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1948,
        "score": 0.00909090880304575,
        "score_kind": "rrf"
      }
    ],
    "final_ranking": [
      {
        "chunk_id": 1975,
        "score": 0.032786883413791656,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1945,
        "score": 0.0320020467042923,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1974,
        "score": 0.0320020467042923,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1933,
        "score": 0.03007688745856285,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1976,
        "score": 0.0295138880610466,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1952,
        "score": 0.029083244502544403,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1938,
        "score": 0.025678060948848724,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1977,
        "score": 0.015625,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1953,
        "score": 0.015384615398943424,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1954,
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
          1974
        ]
      ]
    },
    {
      "group_id": "g2",
      "alternatives": [
        [
          1975
        ]
      ]
    }
  ],
  "candidate_ids": [
    1975,
    1945,
    1974,
    1933,
    1976,
    1952,
    1938,
    1977,
    1953,
    1954,
    1955,
    1951,
    1937,
    1959,
    1961,
    1960,
    1942,
    1962,
    1944,
    1957,
    1950,
    1972,
    1963,
    1946,
    1964,
    1958,
    1947,
    1934,
    1978,
    1956,
    1932,
    1970,
    1940,
    1943,
    1973,
    1979,
    1931,
    1965,
    1967,
    1971,
    1936,
    1968,
    1980,
    1935,
    1949,
    1941,
    1969,
    1966,
    1939,
    1948
  ],
  "final_ids": [
    1974,
    1975,
    1945,
    1976,
    1977,
    1937,
    1951,
    1933,
    1952,
    1942
  ],
  "prompt_citations": [
    {
      "n": 1,
      "chunk_id": "1974",
      "section_path": "会员权益/会员等级",
      "question": "会员等级",
      "answer": "会员分为普通、银卡和金卡三档，按有效累计消费金额自动升级，不按年度消费金额计算。累计消费未满 1000 元为普通会员，满 1000 元起为银卡，满 5000 元起为金卡。\n\n有效累计消费指已完成订单的商品实际支付金额，不含配送费；退货退款部分从有效累计消费中扣除。退款后根据更新的累计消费重新计算等级，未达到原门槛时可能降级。等级与适用权益在会员中心展示。\n\n银卡在参与会员折扣的商品上享 95 折，金卡享 9 折。折扣适用商品和活动范围以结算页面标注为准。会员折扣、优惠券与满减是否叠加也以当次活动页面为准，不能一概承诺全部优惠同时生效。"
    },
    {
      "n": 3,
      "chunk_id": "1945",
      "section_path": "商品与购物 FAQ/会员等级与积分规则",
      "question": "会员等级与积分规则",
      "answer": "会员分为普通、银卡、金卡三档,按累计消费自动升级。每消费 1 元得 1 积分,积分可在结算时抵扣,100 积分抵 1 元。"
    },
    {
      "n": 5,
      "chunk_id": "1977",
      "section_path": "积分规则/积分怎么用",
      "question": "积分怎么用",
      "answer": "积分可在结算时抵扣商品金额，100 积分抵 1 元现金，单笔订单最多抵 30 元，不用于抵扣偏远地区附加运费，也不支持直接提现。\n\n2000 积分可兑换自动饮水机滤芯 3 片，该兑换套装适用于 MH-W40，普通配送地区包邮；偏远地区附加配送费仍需按页面规则确认。MH-W40 的滤芯更换周期以商品规格手册为准。\n\n800 积分可兑换猫零食小样，普通配送地区另收 6 元运费；该兑换不直接套用普通购物订单的满 99 元包邮规则。兑换商品、可用库存及偏远地区配送规则以兑换页面标注为准。"
    },
    {
      "n": 7,
      "chunk_id": "1951",
      "section_path": "商品与购物 FAQ/会员运费权益",
      "question": "会员运费权益",
      "answer": "金卡会员每月享 3 次免运费权益,银卡会员享 1 次;权益不与偏远地区附加运费冲抵,当月未用完不结转。"
    },
    {
      "n": 9,
      "chunk_id": "1952",
      "section_path": "商品规格手册",
      "question": "商品规格手册",
      "answer": "本手册收录喵喵优选自营智能硬件的型号、规格与使用要点,便于按具体型号查询。"
    },
    {
      "n": 10,
      "chunk_id": "1942",
      "section_path": "商品与购物 FAQ/运费怎么算",
      "question": "运费怎么算",
      "answer": "单笔订单满 99 元包邮,未满收取 10 元运费,偏远地区运费另计。邮费即运费,按此规则收取。"
    },
    {
      "n": 8,
      "chunk_id": "1933",
      "section_path": "售后手册/设备安装与激活",
      "question": "设备安装与激活",
      "answer": "智能设备首次使用需下载「喵喵优选」App,按说明书扫码添加设备并连接 2.4G Wi-Fi 完成激活;猫爬架等非联网商品按随附图解自行组装。"
    },
    {
      "n": 6,
      "chunk_id": "1937",
      "section_path": "售后手册/会员专属售后权益",
      "question": "会员专属售后权益",
      "answer": "金卡会员享优先客服接入与上门取件退换货;银卡会员享退换货运费权益 1 次/月。具体权益以会员中心页面标注为准。"
    },
    {
      "n": 4,
      "chunk_id": "1976",
      "section_path": "积分规则/积分怎么攒",
      "question": "积分怎么攒",
      "answer": "已完成订单每实际支付 1 元商品金额累计 1 积分，不计配送费；退款后按对应商品金额同步扣回积分。活动期间的双倍积分属于额外积分奖励，不计入会员等级升级；会员等级仍按有效累计消费金额计算。"
    },
    {
      "n": 2,
      "chunk_id": "1975",
      "section_path": "会员权益/生日礼",
      "question": "生日礼",
      "answer": "银卡会员生日当月可领取一份猫零食小样，金卡会员生日当月可领取一份猫罐头礼盒。需在会员中心领取，礼品规格与领取期限以页面标注为准，不承诺额外折现或补偿。"
    }
  ],
  "decision": {
    "useful": true,
    "reason": "等级门槛与生日礼均有证据",
    "response_kind": "knowledge",
    "source": null
  },
  "answer": "您好！目前会员等级没有“喵金”这一档，等级分为普通、银卡、金卡三档，按**累计消费**（而非年消费）自动升级：满 1000 元起为银卡，满 5000 元起为金卡 [1]。\n\n生日礼规则如下：\n- 银卡会员：生日当月可领取猫零食小样一份 [2]\n- 金卡会员：生日当月可领取猫罐头礼盒一份 [2]\n\n需在会员中心领取，礼品规格与领取期限以页面标注为准 [2]。请问还有什么可以帮您？",
  "point_verdicts": [
    {
      "point_id": "p1",
      "covered": false,
      "reason": "回答提到金卡按累计消费满5000元升级且非年消费，但缺少condition中的适用条件：有效累计商品实付、不含运费、扣除退款，以及折扣活动范围以页面为准，条件未保留"
    },
    {
      "point_id": "p2",
      "covered": true,
      "reason": "回答完整说明金卡生日当月在会员中心领取猫罐头礼盒，且规格与领取期限以页面标注为准，符合要点及条件"
    }
  ],
  "claim_verdicts": [
    {
      "claim": "会员等级分为普通、银卡、金卡三档",
      "supported": true,
      "reason": "证据[1]明确会员分普通、银卡、金卡三档"
    },
    {
      "claim": "会员等级按累计消费（而非年消费）自动升级",
      "supported": true,
      "reason": "证据[1]说明按有效累计消费金额自动升级，不按年度消费金额计算"
    },
    {
      "claim": "累计消费满1000元起为银卡",
      "supported": true,
      "reason": "证据[1]写明满1000元起为银卡"
    },
    {
      "claim": "累计消费满5000元起为金卡",
      "supported": true,
      "reason": "证据[1]写明满5000元起为金卡"
    },
    {
      "claim": "银卡会员生日当月可领取猫零食小样一份",
      "supported": true,
      "reason": "证据[2]明确银卡会员生日当月可领取一份猫零食小样"
    },
    {
      "claim": "金卡会员生日当月可领取猫罐头礼盒一份",
      "supported": true,
      "reason": "证据[2]明确金卡会员生日当月可领取一份猫罐头礼盒"
    },
    {
      "claim": "生日礼需在会员中心领取，礼品规格与领取期限以页面标注为准",
      "supported": true,
      "reason": "证据[2]写明需在会员中心领取，礼品规格与领取期限以页面标注为准"
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
    "faithfulness": 1.0,
    "absent_refusal_rate": null,
    "answerable_false_refusal_rate": 0.0
  },
  "error": null,
  "elapsed_ms": 15891.294399974868,
  "judge_snapshot": {
    "prompt_version": "joint-generation-v2.1",
    "finish_reason": "stop"
  },
  "rewrite": {
    "policy_version": "original-query-on-invalid-v1",
    "status": "success",
    "error": null
  },
  "audit": {
    "audit_version": 1,
    "source_map_id": "af6590ab401319d942bddff0b30213a4cd888b8cf115ebd5cdec3adb87687e55",
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
        "chunk_id": 1975,
        "score": 0.032786883413791656,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1945,
        "score": 0.0320020467042923,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1974,
        "score": 0.0320020467042923,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1933,
        "score": 0.03007688745856285,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1976,
        "score": 0.0295138880610466,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1952,
        "score": 0.029083244502544403,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1938,
        "score": 0.025678060948848724,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1977,
        "score": 0.015625,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1953,
        "score": 0.015384615398943424,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1954,
        "score": 0.01515151560306549,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1955,
        "score": 0.014705882407724857,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1951,
        "score": 0.014492753893136978,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1937,
        "score": 0.014285714365541935,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1959,
        "score": 0.014084506779909134,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1961,
        "score": 0.013513513840734959,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1960,
        "score": 0.013333333656191826,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1942,
        "score": 0.01315789483487606,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1962,
        "score": 0.012987012974917889,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1944,
        "score": 0.012820512987673283,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1957,
        "score": 0.012658228166401386,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1950,
        "score": 0.012500000186264515,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1972,
        "score": 0.012345679104328156,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1963,
        "score": 0.012195121496915817,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1946,
        "score": 0.012048192322254181,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1964,
        "score": 0.011904762126505375,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1958,
        "score": 0.0117647061124444,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1947,
        "score": 0.011627906933426857,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1934,
        "score": 0.01149425283074379,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1978,
        "score": 0.011363636702299118,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1956,
        "score": 0.01123595517128706,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1932,
        "score": 0.011111111380159855,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1970,
        "score": 0.010989011265337467,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1940,
        "score": 0.010869565419852734,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1943,
        "score": 0.010638297535479069,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1973,
        "score": 0.010526316240429878,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1979,
        "score": 0.010416666977107525,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1931,
        "score": 0.010309278033673763,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1965,
        "score": 0.010204081423580647,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1967,
        "score": 0.010101010091602802,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1971,
        "score": 0.009999999776482582,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1936,
        "score": 0.009900989942252636,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1968,
        "score": 0.009803921915590763,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1980,
        "score": 0.009708737954497337,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1935,
        "score": 0.009615384973585606,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1949,
        "score": 0.009523809887468815,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1941,
        "score": 0.009433962404727936,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1969,
        "score": 0.009345794096589088,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1966,
        "score": 0.009259259328246117,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1939,
        "score": 0.00917431153357029,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1948,
        "score": 0.00909090880304575,
        "score_kind": "rrf"
      }
    ],
    "final_ranking": [
      {
        "chunk_id": 1974,
        "score": 0.1314775049686432,
        "score_kind": "rerank"
      },
      {
        "chunk_id": 1975,
        "score": 0.1071121096611023,
        "score_kind": "rerank"
      },
      {
        "chunk_id": 1945,
        "score": 0.02354610711336136,
        "score_kind": "rerank"
      },
      {
        "chunk_id": 1976,
        "score": 0.0028411138337105513,
        "score_kind": "rerank"
      },
      {
        "chunk_id": 1977,
        "score": 0.0017970968037843704,
        "score_kind": "rerank"
      },
      {
        "chunk_id": 1937,
        "score": 0.000398652337025851,
        "score_kind": "rerank"
      },
      {
        "chunk_id": 1951,
        "score": 0.00036723734228871763,
        "score_kind": "rerank"
      },
      {
        "chunk_id": 1933,
        "score": 0.00016082375077530742,
        "score_kind": "rerank"
      },
      {
        "chunk_id": 1952,
        "score": 5.7160548749379814e-05,
        "score_kind": "rerank"
      },
      {
        "chunk_id": 1942,
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
          1969
        ]
      ]
    }
  ],
  "candidate_ids": [
    1969,
    1968,
    1971,
    1942,
    1940,
    1936,
    1937,
    1947,
    1967,
    1970,
    1951,
    1949,
    1965,
    1973,
    1966,
    1931,
    1938,
    1948,
    1977,
    1939,
    1932,
    1976,
    1941,
    1950,
    1972,
    1979,
    1944,
    1943,
    1934,
    1978,
    1946,
    1974,
    1945,
    1957,
    1975,
    1933,
    1935,
    1955,
    1953,
    1958,
    1956,
    1954,
    1980,
    1962,
    1952,
    1963,
    1960,
    1961,
    1964,
    1959
  ],
  "final_ids": [
    1969,
    1968,
    1971,
    1942,
    1940,
    1936,
    1937,
    1947,
    1967,
    1970
  ],
  "prompt_citations": [
    {
      "n": 1,
      "chunk_id": "1969",
      "section_path": "退货退款政策/退换货运费承担",
      "question": "退换货运费承担",
      "answer": "无理由退货的退回运费由买家承担;因商品质量问题、发错货、少发漏发导致的退换货,运费由平台承担。运费承担以平台售后规则最终判定为准。"
    },
    {
      "n": 3,
      "chunk_id": "1971",
      "section_path": "退货退款政策/运输破损处理",
      "question": "运输破损处理",
      "answer": "商品运输途中破损的,请在签收后 48 小时内联系客服并提供开箱视频与照片,核实后可免费补发或退款,相关运费由平台承担。"
    },
    {
      "n": 5,
      "chunk_id": "1940",
      "section_path": "商品与购物 FAQ/换货流程怎么走",
      "question": "换货流程怎么走",
      "answer": "收到商品 7 天内可申请换货,联系客服登记后将商品寄回,平台核验无误后补发新品。"
    },
    {
      "n": 7,
      "chunk_id": "1937",
      "section_path": "售后手册/会员专属售后权益",
      "question": "会员专属售后权益",
      "answer": "金卡会员享优先客服接入与上门取件退换货;银卡会员享退换货运费权益 1 次/月。具体权益以会员中心页面标注为准。"
    },
    {
      "n": 9,
      "chunk_id": "1967",
      "section_path": "退货退款政策/换货政策/换货条件",
      "question": "换货条件",
      "answer": "收到商品 7 天内,商品完好且配件齐全的,可申请一次同款换货;不同型号或颜色需先退货再重新下单。"
    },
    {
      "n": 10,
      "chunk_id": "1970",
      "section_path": "退货退款政策/质量问题与保修",
      "question": "质量问题与保修",
      "answer": "电子类商品自签收起保修 12 个月,保修期内非人为损坏可申请免费维修或换货;人为损坏、超保商品维修可能收取工本费。"
    },
    {
      "n": 8,
      "chunk_id": "1947",
      "section_path": "商品与购物 FAQ/配送范围与偏远地区",
      "question": "配送范围与偏远地区",
      "answer": "全国大部分地区支持配送,新疆、西藏、内蒙古等偏远地区运费另计且时效顺延;港澳台及海外暂不支持自营配送。"
    },
    {
      "n": 6,
      "chunk_id": "1936",
      "section_path": "售后手册/维修寄修流程",
      "question": "维修寄修流程",
      "answer": "保修期内设备故障,联系客服登记后按指引将设备寄回指定维修点,核验后免费维修并寄回;超保或人为损坏维修可能收取工本费,费用会提前告知。"
    },
    {
      "n": 4,
      "chunk_id": "1942",
      "section_path": "商品与购物 FAQ/运费怎么算",
      "question": "运费怎么算",
      "answer": "单笔订单满 99 元包邮,未满收取 10 元运费,偏远地区运费另计。邮费即运费,按此规则收取。"
    },
    {
      "n": 2,
      "chunk_id": "1968",
      "section_path": "退货退款政策/换货政策/换货运费",
      "question": "换货运费",
      "answer": "非质量问题的换货,往返运费由买家承担;因质量问题或发错货的换货,往返运费由平台承担。"
    }
  ],
  "decision": {
    "useful": true,
    "reason": "证据明确：少发漏发运费由平台承担",
    "response_kind": "knowledge",
    "source": null
  },
  "answer": "您好！根据平台售后规则：因商品质量问题、发错货、少发漏发导致的退换货，运费由平台承担；最终以平台售后规则判定为准[1]。\n\n如需办理，请提供订单号，我可以为您进一步核实～",
  "point_verdicts": [
    {
      "point_id": "p1",
      "covered": true,
      "reason": "回答明确说明少发漏发导致的退换货运费由平台承担，并保留以平台售后规则最终判定为准的条件。"
    }
  ],
  "claim_verdicts": [
    {
      "claim": "因商品质量问题、发错货、少发漏发导致的退换货，运费由平台承担",
      "supported": true,
      "reason": "证据1明确列出因质量问题、发错货、少发漏发导致的退换货运费由平台承担，支持该断言。"
    },
    {
      "claim": "运费承担最终以平台售后规则判定为准",
      "supported": true,
      "reason": "证据1末句明确说明运费承担以平台售后规则最终判定为准，支持该断言。"
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
  "elapsed_ms": 8346.683599753305,
  "judge_snapshot": {
    "prompt_version": "joint-generation-v2.1",
    "finish_reason": "stop"
  },
  "rewrite": {
    "policy_version": "original-query-on-invalid-v1",
    "status": "success",
    "error": null
  },
  "audit": {
    "audit_version": 1,
    "source_map_id": "af6590ab401319d942bddff0b30213a4cd888b8cf115ebd5cdec3adb87687e55",
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
        "chunk_id": 1969,
        "score": 0.7046358585357666,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1968,
        "score": 0.6642881631851196,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1971,
        "score": 0.6263620257377625,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1942,
        "score": 0.575890839099884,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1940,
        "score": 0.5652117133140564,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1936,
        "score": 0.5471986532211304,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1937,
        "score": 0.5470176339149475,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1947,
        "score": 0.5431363582611084,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1967,
        "score": 0.5417925119400024,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1970,
        "score": 0.5401856303215027,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1951,
        "score": 0.5350643396377563,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1949,
        "score": 0.5340436697006226,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1965,
        "score": 0.5290241241455078,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1973,
        "score": 0.5246568322181702,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1966,
        "score": 0.5240338444709778,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1931,
        "score": 0.520516574382782,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1938,
        "score": 0.517553448677063,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1948,
        "score": 0.5175460577011108,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1977,
        "score": 0.511620283126831,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1939,
        "score": 0.5046658515930176,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1932,
        "score": 0.5018535852432251,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1976,
        "score": 0.49774226546287537,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1941,
        "score": 0.4967568516731262,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1950,
        "score": 0.492765873670578,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1972,
        "score": 0.4752086102962494,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1979,
        "score": 0.4687517285346985,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1944,
        "score": 0.46612662076950073,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1943,
        "score": 0.46289175748825073,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1934,
        "score": 0.45831504464149475,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1978,
        "score": 0.4470350742340088,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1946,
        "score": 0.44225388765335083,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1974,
        "score": 0.42225074768066406,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1945,
        "score": 0.42026203870773315,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1957,
        "score": 0.4093003273010254,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1975,
        "score": 0.40304166078567505,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1933,
        "score": 0.39646226167678833,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1935,
        "score": 0.39401930570602417,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1955,
        "score": 0.39233294129371643,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1953,
        "score": 0.38525596261024475,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1958,
        "score": 0.383177250623703,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1956,
        "score": 0.3790184557437897,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1954,
        "score": 0.3717654347419739,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1980,
        "score": 0.36426985263824463,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1962,
        "score": 0.3571329116821289,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1952,
        "score": 0.3459285795688629,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1963,
        "score": 0.3358844518661499,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1960,
        "score": 0.3118942677974701,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1961,
        "score": 0.3062795400619507,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1964,
        "score": 0.2829532325267792,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1959,
        "score": 0.26851511001586914,
        "score_kind": "cosine"
      }
    ],
    "final_ranking": [
      {
        "chunk_id": 1969,
        "score": 0.7046358585357666,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1968,
        "score": 0.6642881631851196,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1971,
        "score": 0.6263620257377625,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1942,
        "score": 0.575890839099884,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1940,
        "score": 0.5652117133140564,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1936,
        "score": 0.5471986532211304,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1937,
        "score": 0.5470176339149475,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1947,
        "score": 0.5431363582611084,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1967,
        "score": 0.5417925119400024,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1970,
        "score": 0.5401856303215027,
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
          1969
        ]
      ]
    }
  ],
  "candidate_ids": [
    1969,
    1968,
    1937,
    1971,
    1931,
    1967,
    1942,
    1940,
    1980,
    1951,
    1977,
    1970,
    1947,
    1972,
    1973,
    1939,
    1941,
    1952,
    1943,
    1974,
    1949,
    1965,
    1950,
    1935,
    1946,
    1948,
    1976,
    1979
  ],
  "final_ids": [
    1969,
    1968,
    1937,
    1971,
    1931,
    1967,
    1942,
    1940,
    1980,
    1951
  ],
  "prompt_citations": [
    {
      "n": 1,
      "chunk_id": "1969",
      "section_path": "退货退款政策/退换货运费承担",
      "question": "退换货运费承担",
      "answer": "无理由退货的退回运费由买家承担;因商品质量问题、发错货、少发漏发导致的退换货,运费由平台承担。运费承担以平台售后规则最终判定为准。"
    },
    {
      "n": 3,
      "chunk_id": "1937",
      "section_path": "售后手册/会员专属售后权益",
      "question": "会员专属售后权益",
      "answer": "金卡会员享优先客服接入与上门取件退换货;银卡会员享退换货运费权益 1 次/月。具体权益以会员中心页面标注为准。"
    },
    {
      "n": 5,
      "chunk_id": "1931",
      "section_path": "售后手册/常见问题处理时限",
      "question": "常见问题处理时限",
      "answer": "| 问题类型 | 首次响应 | 处理时限 |\n| --- | --- | --- |\n| 退款 | 2 小时 | 3 个工作日 |\n| 换货 | 2 小时 | 5 个工作日 |\n| 维修 | 4 小时 | 7 个工作日 |\n| 投诉 | 1 小时 | 3 个工作日 |\n| 发票 | 4 小时 | 3 个工作日 |\n| 物流异常 | 2 小时 | 5 个工作日 |\n| 商品咨询 | 1 小时 | 当日 |\n| 价格保护 | 2 小时 | 3 个工作日 |\n| 账户问题 | 2 小时 | 3 个工作日 |\n| 退换货运费 | 2 小时 | 3 个工作日 |\n| 缺货补发 | 2 小时 | 5 个工作日 |\n| 其他 | 4 小时 | 7 个工作日 |"
    },
    {
      "n": 7,
      "chunk_id": "1942",
      "section_path": "商品与购物 FAQ/运费怎么算",
      "question": "运费怎么算",
      "answer": "单笔订单满 99 元包邮,未满收取 10 元运费,偏远地区运费另计。邮费即运费,按此规则收取。"
    },
    {
      "n": 9,
      "chunk_id": "1980",
      "section_path": "猫窝清洗说明/猫窝是否可以机洗",
      "question": "猫窝是否可以机洗",
      "answer": "普通布艺猫窝清洗前拆掉内部垫芯，外套放入洗衣袋，使用轻柔模式冷水洗，自然晾干。不可直接将整只猫窝连垫芯一起机洗，商品另有清洗标签时优先遵循标签。\n\n带加热模块的猫窝不可机洗，应先断电，并按说明书局部擦洗；不得将加热模块、电源或线路浸水。未按清洗说明操作导致的损坏不直接认定为商品质量问题，需要客服核验。\n\n退货仍需符合商品完好、不影响二次销售等适用条件。售后手册中的电子类商品 12 个月保修不能直接套用到普通布艺猫窝；本清洗说明未给出布艺猫窝的独立保修期限。"
    },
    {
      "n": 10,
      "chunk_id": "1951",
      "section_path": "商品与购物 FAQ/会员运费权益",
      "question": "会员运费权益",
      "answer": "金卡会员每月享 3 次免运费权益,银卡会员享 1 次;权益不与偏远地区附加运费冲抵,当月未用完不结转。"
    },
    {
      "n": 8,
      "chunk_id": "1940",
      "section_path": "商品与购物 FAQ/换货流程怎么走",
      "question": "换货流程怎么走",
      "answer": "收到商品 7 天内可申请换货,联系客服登记后将商品寄回,平台核验无误后补发新品。"
    },
    {
      "n": 6,
      "chunk_id": "1967",
      "section_path": "退货退款政策/换货政策/换货条件",
      "question": "换货条件",
      "answer": "收到商品 7 天内,商品完好且配件齐全的,可申请一次同款换货;不同型号或颜色需先退货再重新下单。"
    },
    {
      "n": 4,
      "chunk_id": "1971",
      "section_path": "退货退款政策/运输破损处理",
      "question": "运输破损处理",
      "answer": "商品运输途中破损的,请在签收后 48 小时内联系客服并提供开箱视频与照片,核实后可免费补发或退款,相关运费由平台承担。"
    },
    {
      "n": 2,
      "chunk_id": "1968",
      "section_path": "退货退款政策/换货政策/换货运费",
      "question": "换货运费",
      "answer": "非质量问题的换货,往返运费由买家承担;因质量问题或发错货的换货,往返运费由平台承担。"
    }
  ],
  "decision": {
    "useful": true,
    "reason": "证据1969明确少发漏发运费由平台承担",
    "response_kind": "knowledge",
    "source": null
  },
  "answer": "您好！因**少发漏发**导致的退换货，运费由**平台承担**[1]。同样，因质量问题或发错货的换货，往返运费也由平台承担[2]。\n\n（注：无理由退货的退回运费才由买家承担[1]，最终以平台售后规则判定为准[1]。）\n\n请问您遇到的具体情况是什么？如需处理，可提供订单号，我来为您进一步核实。",
  "point_verdicts": [
    {
      "point_id": "p1",
      "covered": true,
      "reason": "回答明确说明少发漏发退换货运费由平台承担，并提及以平台售后规则最终判定为准，条件保留完整"
    }
  ],
  "claim_verdicts": [
    {
      "claim": "因少发漏发导致的退换货运费由平台承担",
      "supported": true,
      "reason": "证据1明确写明因少发漏发导致的退换货运费由平台承担"
    },
    {
      "claim": "因质量问题或发错货的换货，往返运费由平台承担",
      "supported": true,
      "reason": "证据2明确写明因质量问题或发错货的换货往返运费由平台承担"
    },
    {
      "claim": "无理由退货的退回运费由买家承担",
      "supported": true,
      "reason": "证据1明确写明无理由退货的退回运费由买家承担"
    },
    {
      "claim": "运费承担以平台售后规则最终判定为准",
      "supported": true,
      "reason": "证据1明确写明运费承担以平台售后规则最终判定为准"
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
  "elapsed_ms": 10035.887599922717,
  "judge_snapshot": {
    "prompt_version": "joint-generation-v2.1",
    "finish_reason": "stop"
  },
  "rewrite": {
    "policy_version": "original-query-on-invalid-v1",
    "status": "success",
    "error": null
  },
  "audit": {
    "audit_version": 1,
    "source_map_id": "af6590ab401319d942bddff0b30213a4cd888b8cf115ebd5cdec3adb87687e55",
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
        "chunk_id": 1969,
        "score": 33.115447998046875,
        "score_kind": "bm25"
      },
      {
        "chunk_id": 1968,
        "score": 15.512645721435547,
        "score_kind": "bm25"
      },
      {
        "chunk_id": 1937,
        "score": 12.489039421081543,
        "score_kind": "bm25"
      },
      {
        "chunk_id": 1971,
        "score": 8.663971900939941,
        "score_kind": "bm25"
      },
      {
        "chunk_id": 1931,
        "score": 7.032027721405029,
        "score_kind": "bm25"
      },
      {
        "chunk_id": 1967,
        "score": 4.239816188812256,
        "score_kind": "bm25"
      },
      {
        "chunk_id": 1942,
        "score": 3.048265218734741,
        "score_kind": "bm25"
      },
      {
        "chunk_id": 1940,
        "score": 2.9758758544921875,
        "score_kind": "bm25"
      },
      {
        "chunk_id": 1980,
        "score": 2.8859429359436035,
        "score_kind": "bm25"
      },
      {
        "chunk_id": 1951,
        "score": 2.8167614936828613,
        "score_kind": "bm25"
      },
      {
        "chunk_id": 1977,
        "score": 2.4655652046203613,
        "score_kind": "bm25"
      },
      {
        "chunk_id": 1970,
        "score": 2.101652145385742,
        "score_kind": "bm25"
      },
      {
        "chunk_id": 1947,
        "score": 1.8113679885864258,
        "score_kind": "bm25"
      },
      {
        "chunk_id": 1972,
        "score": 1.4414697885513306,
        "score_kind": "bm25"
      },
      {
        "chunk_id": 1973,
        "score": 1.2937390804290771,
        "score_kind": "bm25"
      },
      {
        "chunk_id": 1939,
        "score": 1.0660427808761597,
        "score_kind": "bm25"
      },
      {
        "chunk_id": 1941,
        "score": 1.0558345317840576,
        "score_kind": "bm25"
      },
      {
        "chunk_id": 1952,
        "score": 1.0359933376312256,
        "score_kind": "bm25"
      },
      {
        "chunk_id": 1943,
        "score": 1.0168840885162354,
        "score_kind": "bm25"
      },
      {
        "chunk_id": 1974,
        "score": 1.0009245872497559,
        "score_kind": "bm25"
      },
      {
        "chunk_id": 1949,
        "score": 0.998467206954956,
        "score_kind": "bm25"
      },
      {
        "chunk_id": 1965,
        "score": 0.9895066618919373,
        "score_kind": "bm25"
      },
      {
        "chunk_id": 1950,
        "score": 0.9807054996490479,
        "score_kind": "bm25"
      },
      {
        "chunk_id": 1935,
        "score": 0.9720594882965088,
        "score_kind": "bm25"
      },
      {
        "chunk_id": 1946,
        "score": 0.9155580401420593,
        "score_kind": "bm25"
      },
      {
        "chunk_id": 1948,
        "score": 0.9155580401420593,
        "score_kind": "bm25"
      },
      {
        "chunk_id": 1976,
        "score": 0.8389298319816589,
        "score_kind": "bm25"
      },
      {
        "chunk_id": 1979,
        "score": 0.7139831781387329,
        "score_kind": "bm25"
      }
    ],
    "final_ranking": [
      {
        "chunk_id": 1969,
        "score": 33.115447998046875,
        "score_kind": "bm25"
      },
      {
        "chunk_id": 1968,
        "score": 15.512645721435547,
        "score_kind": "bm25"
      },
      {
        "chunk_id": 1937,
        "score": 12.489039421081543,
        "score_kind": "bm25"
      },
      {
        "chunk_id": 1971,
        "score": 8.663971900939941,
        "score_kind": "bm25"
      },
      {
        "chunk_id": 1931,
        "score": 7.032027721405029,
        "score_kind": "bm25"
      },
      {
        "chunk_id": 1967,
        "score": 4.239816188812256,
        "score_kind": "bm25"
      },
      {
        "chunk_id": 1942,
        "score": 3.048265218734741,
        "score_kind": "bm25"
      },
      {
        "chunk_id": 1940,
        "score": 2.9758758544921875,
        "score_kind": "bm25"
      },
      {
        "chunk_id": 1980,
        "score": 2.8859429359436035,
        "score_kind": "bm25"
      },
      {
        "chunk_id": 1951,
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
          1969
        ]
      ]
    }
  ],
  "candidate_ids": [
    1969,
    1968,
    1971,
    1937,
    1942,
    1940,
    1967,
    1931,
    1947,
    1951,
    1970,
    1973,
    1977,
    1949,
    1965,
    1939,
    1972,
    1941,
    1948,
    1980,
    1943,
    1950,
    1976,
    1974,
    1979,
    1946,
    1952,
    1935,
    1936,
    1966,
    1938,
    1932,
    1944,
    1934,
    1978,
    1945,
    1957,
    1975,
    1933,
    1955,
    1953,
    1958,
    1956,
    1954,
    1962,
    1963,
    1960,
    1961,
    1964,
    1959
  ],
  "final_ids": [
    1969,
    1968,
    1971,
    1937,
    1942,
    1940,
    1967,
    1931,
    1947,
    1951
  ],
  "prompt_citations": [
    {
      "n": 1,
      "chunk_id": "1969",
      "section_path": "退货退款政策/退换货运费承担",
      "question": "退换货运费承担",
      "answer": "无理由退货的退回运费由买家承担;因商品质量问题、发错货、少发漏发导致的退换货,运费由平台承担。运费承担以平台售后规则最终判定为准。"
    },
    {
      "n": 3,
      "chunk_id": "1971",
      "section_path": "退货退款政策/运输破损处理",
      "question": "运输破损处理",
      "answer": "商品运输途中破损的,请在签收后 48 小时内联系客服并提供开箱视频与照片,核实后可免费补发或退款,相关运费由平台承担。"
    },
    {
      "n": 5,
      "chunk_id": "1942",
      "section_path": "商品与购物 FAQ/运费怎么算",
      "question": "运费怎么算",
      "answer": "单笔订单满 99 元包邮,未满收取 10 元运费,偏远地区运费另计。邮费即运费,按此规则收取。"
    },
    {
      "n": 7,
      "chunk_id": "1967",
      "section_path": "退货退款政策/换货政策/换货条件",
      "question": "换货条件",
      "answer": "收到商品 7 天内,商品完好且配件齐全的,可申请一次同款换货;不同型号或颜色需先退货再重新下单。"
    },
    {
      "n": 9,
      "chunk_id": "1947",
      "section_path": "商品与购物 FAQ/配送范围与偏远地区",
      "question": "配送范围与偏远地区",
      "answer": "全国大部分地区支持配送,新疆、西藏、内蒙古等偏远地区运费另计且时效顺延;港澳台及海外暂不支持自营配送。"
    },
    {
      "n": 10,
      "chunk_id": "1951",
      "section_path": "商品与购物 FAQ/会员运费权益",
      "question": "会员运费权益",
      "answer": "金卡会员每月享 3 次免运费权益,银卡会员享 1 次;权益不与偏远地区附加运费冲抵,当月未用完不结转。"
    },
    {
      "n": 8,
      "chunk_id": "1931",
      "section_path": "售后手册/常见问题处理时限",
      "question": "常见问题处理时限",
      "answer": "| 问题类型 | 首次响应 | 处理时限 |\n| --- | --- | --- |\n| 退款 | 2 小时 | 3 个工作日 |\n| 换货 | 2 小时 | 5 个工作日 |\n| 维修 | 4 小时 | 7 个工作日 |\n| 投诉 | 1 小时 | 3 个工作日 |\n| 发票 | 4 小时 | 3 个工作日 |\n| 物流异常 | 2 小时 | 5 个工作日 |\n| 商品咨询 | 1 小时 | 当日 |\n| 价格保护 | 2 小时 | 3 个工作日 |\n| 账户问题 | 2 小时 | 3 个工作日 |\n| 退换货运费 | 2 小时 | 3 个工作日 |\n| 缺货补发 | 2 小时 | 5 个工作日 |\n| 其他 | 4 小时 | 7 个工作日 |"
    },
    {
      "n": 6,
      "chunk_id": "1940",
      "section_path": "商品与购物 FAQ/换货流程怎么走",
      "question": "换货流程怎么走",
      "answer": "收到商品 7 天内可申请换货,联系客服登记后将商品寄回,平台核验无误后补发新品。"
    },
    {
      "n": 4,
      "chunk_id": "1937",
      "section_path": "售后手册/会员专属售后权益",
      "question": "会员专属售后权益",
      "answer": "金卡会员享优先客服接入与上门取件退换货;银卡会员享退换货运费权益 1 次/月。具体权益以会员中心页面标注为准。"
    },
    {
      "n": 2,
      "chunk_id": "1968",
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
  "answer": "您好！根据平台售后规则，因商品质量问题、发错货、少发漏发导致的退换货，运费由平台承担；最终以平台售后规则判定为准[1]。若是换货，因质量问题或发错货的换货，往返运费同样由平台承担[2]。\n\n如需申请退换货，欢迎提供订单号，我可以为您查询或协助转人工处理。",
  "point_verdicts": [
    {
      "point_id": "p1",
      "covered": true,
      "reason": "回答明确指出少发漏发导致的退换货运费由平台承担，并说明以平台售后规则最终判定为准，条件与事实均覆盖。"
    }
  ],
  "claim_verdicts": [
    {
      "claim": "因商品质量问题、发错货、少发漏发导致的退换货，运费由平台承担，最终以平台售后规则判定为准",
      "supported": true,
      "reason": "证据[1]明确说明因商品质量问题、发错货、少发漏发导致的退换货运费由平台承担，且以平台售后规则最终判定为准。"
    },
    {
      "claim": "因质量问题或发错货的换货，往返运费由平台承担",
      "supported": true,
      "reason": "证据[2]明确说明因质量问题或发错货的换货，往返运费由平台承担。"
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
  "elapsed_ms": 9680.407299892977,
  "judge_snapshot": {
    "prompt_version": "joint-generation-v2.1",
    "finish_reason": "stop"
  },
  "rewrite": {
    "policy_version": "original-query-on-invalid-v1",
    "status": "success",
    "error": null
  },
  "audit": {
    "audit_version": 1,
    "source_map_id": "af6590ab401319d942bddff0b30213a4cd888b8cf115ebd5cdec3adb87687e55",
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
        "chunk_id": 1969,
        "score": 0.032786883413791656,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1968,
        "score": 0.032258063554763794,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1971,
        "score": 0.0314980149269104,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1937,
        "score": 0.03079839050769806,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1942,
        "score": 0.03055037185549736,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1940,
        "score": 0.03009049780666828,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1967,
        "score": 0.02964426949620247,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1931,
        "score": 0.02854251116514206,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1947,
        "score": 0.028404511511325836,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1951,
        "score": 0.028370220214128494,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1970,
        "score": 0.02817460335791111,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1973,
        "score": 0.02684684842824936,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1977,
        "score": 0.026742734014987946,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1949,
        "score": 0.026234567165374756,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1965,
        "score": 0.02589375153183937,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1939,
        "score": 0.02565789595246315,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1972,
        "score": 0.02527821995317936,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1941,
        "score": 0.025035206228494644,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1948,
        "score": 0.02461491897702217,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1980,
        "score": 0.024201491847634315,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1943,
        "score": 0.02402186393737793,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1950,
        "score": 0.02395295351743698,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1976,
        "score": 0.023689374327659607,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1974,
        "score": 0.02336956560611725,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1979,
        "score": 0.022991543635725975,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1946,
        "score": 0.022753717377781868,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1952,
        "score": 0.022344322875142097,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1935,
        "score": 0.022214040160179138,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1936,
        "score": 0.01515151560306549,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1966,
        "score": 0.013333333656191826,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1938,
        "score": 0.012820512987673283,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1932,
        "score": 0.012345679104328156,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1944,
        "score": 0.01149425283074379,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1934,
        "score": 0.01123595517128706,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1978,
        "score": 0.011111111380159855,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1945,
        "score": 0.01075268816202879,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1957,
        "score": 0.010638297535479069,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1975,
        "score": 0.010526316240429878,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1933,
        "score": 0.010416666977107525,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1955,
        "score": 0.010204081423580647,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1953,
        "score": 0.010101010091602802,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1958,
        "score": 0.009999999776482582,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1956,
        "score": 0.009900989942252636,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1954,
        "score": 0.009803921915590763,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1962,
        "score": 0.009615384973585606,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1963,
        "score": 0.009433962404727936,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1960,
        "score": 0.009345794096589088,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1961,
        "score": 0.009259259328246117,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1964,
        "score": 0.00917431153357029,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1959,
        "score": 0.00909090880304575,
        "score_kind": "rrf"
      }
    ],
    "final_ranking": [
      {
        "chunk_id": 1969,
        "score": 0.032786883413791656,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1968,
        "score": 0.032258063554763794,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1971,
        "score": 0.0314980149269104,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1937,
        "score": 0.03079839050769806,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1942,
        "score": 0.03055037185549736,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1940,
        "score": 0.03009049780666828,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1967,
        "score": 0.02964426949620247,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1931,
        "score": 0.02854251116514206,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1947,
        "score": 0.028404511511325836,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1951,
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
          1969
        ]
      ]
    }
  ],
  "candidate_ids": [
    1969,
    1968,
    1971,
    1937,
    1942,
    1940,
    1967,
    1931,
    1947,
    1951,
    1970,
    1973,
    1977,
    1949,
    1965,
    1939,
    1972,
    1941,
    1948,
    1980,
    1943,
    1950,
    1976,
    1974,
    1979,
    1946,
    1952,
    1935,
    1936,
    1966,
    1938,
    1932,
    1944,
    1934,
    1978,
    1945,
    1957,
    1975,
    1933,
    1955,
    1953,
    1958,
    1956,
    1954,
    1962,
    1963,
    1960,
    1961,
    1964,
    1959
  ],
  "final_ids": [
    1969,
    1968,
    1971,
    1937,
    1942,
    1973,
    1978,
    1970,
    1974,
    1947
  ],
  "prompt_citations": [
    {
      "n": 1,
      "chunk_id": "1969",
      "section_path": "退货退款政策/退换货运费承担",
      "question": "退换货运费承担",
      "answer": "无理由退货的退回运费由买家承担;因商品质量问题、发错货、少发漏发导致的退换货,运费由平台承担。运费承担以平台售后规则最终判定为准。"
    },
    {
      "n": 3,
      "chunk_id": "1971",
      "section_path": "退货退款政策/运输破损处理",
      "question": "运输破损处理",
      "answer": "商品运输途中破损的,请在签收后 48 小时内联系客服并提供开箱视频与照片,核实后可免费补发或退款,相关运费由平台承担。"
    },
    {
      "n": 5,
      "chunk_id": "1942",
      "section_path": "商品与购物 FAQ/运费怎么算",
      "question": "运费怎么算",
      "answer": "单笔订单满 99 元包邮,未满收取 10 元运费,偏远地区运费另计。邮费即运费,按此规则收取。"
    },
    {
      "n": 7,
      "chunk_id": "1978",
      "section_path": "开票细则/可开票类型",
      "question": "可开票类型",
      "answer": "本演示店提供电子普通发票、电子专用发票和纸质专用发票。电子普通发票可按订单申请；电子专票需要企业账户，申请前准备发票抬头及有效纳税人识别号，按申请页面提交资料。\n\n纸质专票仅企业账户可申请，申请时需提供企业开票资料、收件人和邮寄地址，快递费到付。资料审核通过后按开票流程寄出，不承诺快递送达日期。"
    },
    {
      "n": 9,
      "chunk_id": "1974",
      "section_path": "会员权益/会员等级",
      "question": "会员等级",
      "answer": "会员分为普通、银卡和金卡三档，按有效累计消费金额自动升级，不按年度消费金额计算。累计消费未满 1000 元为普通会员，满 1000 元起为银卡，满 5000 元起为金卡。\n\n有效累计消费指已完成订单的商品实际支付金额，不含配送费；退货退款部分从有效累计消费中扣除。退款后根据更新的累计消费重新计算等级，未达到原门槛时可能降级。等级与适用权益在会员中心展示。\n\n银卡在参与会员折扣的商品上享 95 折，金卡享 9 折。折扣适用商品和活动范围以结算页面标注为准。会员折扣、优惠券与满减是否叠加也以当次活动页面为准，不能一概承诺全部优惠同时生效。"
    },
    {
      "n": 10,
      "chunk_id": "1947",
      "section_path": "商品与购物 FAQ/配送范围与偏远地区",
      "question": "配送范围与偏远地区",
      "answer": "全国大部分地区支持配送,新疆、西藏、内蒙古等偏远地区运费另计且时效顺延;港澳台及海外暂不支持自营配送。"
    },
    {
      "n": 8,
      "chunk_id": "1970",
      "section_path": "退货退款政策/质量问题与保修",
      "question": "质量问题与保修",
      "answer": "电子类商品自签收起保修 12 个月,保修期内非人为损坏可申请免费维修或换货;人为损坏、超保商品维修可能收取工本费。"
    },
    {
      "n": 6,
      "chunk_id": "1973",
      "section_path": "退货退款政策/预售与定金",
      "question": "预售与定金",
      "answer": "预售商品以详情页标注的时间发货;定金支付后不支持无理由退定金,尾款未按时支付的,定金按活动规则处理。"
    },
    {
      "n": 4,
      "chunk_id": "1937",
      "section_path": "售后手册/会员专属售后权益",
      "question": "会员专属售后权益",
      "answer": "金卡会员享优先客服接入与上门取件退换货;银卡会员享退换货运费权益 1 次/月。具体权益以会员中心页面标注为准。"
    },
    {
      "n": 2,
      "chunk_id": "1968",
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
  "answer": "您好！根据平台售后政策，**因少发漏发导致的退换货，运费由平台承担**[1]。换货情形下，因发错货或质量问题的换货，往返运费同样由平台承担[2]。\n\n最终运费承担以平台售后规则判定为准[1]。如需处理，请提供订单号，我可以为您进一步协助。",
  "point_verdicts": [
    {
      "point_id": "p1",
      "covered": true,
      "reason": "回答明确指出少发漏发导致的退换货运费由平台承担，并保留以平台售后规则最终判定为准的条件，覆盖完整。"
    }
  ],
  "claim_verdicts": [
    {
      "claim": "因少发漏发导致的退换货，运费由平台承担",
      "supported": true,
      "reason": "证据1明确说明因商品质量问题、发错货、少发漏发导致的退换货运费由平台承担。"
    },
    {
      "claim": "换货情形下，因发错货或质量问题的换货，往返运费由平台承担",
      "supported": true,
      "reason": "证据2说明因质量问题或发错货的换货，往返运费由平台承担。"
    },
    {
      "claim": "最终运费承担以平台售后规则判定为准",
      "supported": true,
      "reason": "证据1说明运费承担以平台售后规则最终判定为准。"
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
  "elapsed_ms": 12674.754199804738,
  "judge_snapshot": {
    "prompt_version": "joint-generation-v2.1",
    "finish_reason": "stop"
  },
  "rewrite": {
    "policy_version": "original-query-on-invalid-v1",
    "status": "success",
    "error": null
  },
  "audit": {
    "audit_version": 1,
    "source_map_id": "af6590ab401319d942bddff0b30213a4cd888b8cf115ebd5cdec3adb87687e55",
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
        "chunk_id": 1969,
        "score": 0.032786883413791656,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1968,
        "score": 0.032258063554763794,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1971,
        "score": 0.0314980149269104,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1937,
        "score": 0.03079839050769806,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1942,
        "score": 0.03055037185549736,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1940,
        "score": 0.03009049780666828,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1967,
        "score": 0.02964426949620247,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1931,
        "score": 0.02854251116514206,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1947,
        "score": 0.028404511511325836,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1951,
        "score": 0.028370220214128494,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1970,
        "score": 0.02817460335791111,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1973,
        "score": 0.02684684842824936,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1977,
        "score": 0.026742734014987946,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1949,
        "score": 0.026234567165374756,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1965,
        "score": 0.02589375153183937,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1939,
        "score": 0.02565789595246315,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1972,
        "score": 0.02527821995317936,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1941,
        "score": 0.025035206228494644,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1948,
        "score": 0.024448420852422714,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1980,
        "score": 0.024201491847634315,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1943,
        "score": 0.02402186393737793,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1950,
        "score": 0.02395295351743698,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1976,
        "score": 0.023689374327659607,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1974,
        "score": 0.02336956560611725,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1979,
        "score": 0.022991543635725975,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1946,
        "score": 0.022753717377781868,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1952,
        "score": 0.022344322875142097,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1935,
        "score": 0.022214040160179138,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1936,
        "score": 0.01515151560306549,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1966,
        "score": 0.013333333656191826,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1938,
        "score": 0.012987012974917889,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1932,
        "score": 0.012345679104328156,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1944,
        "score": 0.01149425283074379,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1934,
        "score": 0.01123595517128706,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1978,
        "score": 0.011111111380159855,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1945,
        "score": 0.01075268816202879,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1957,
        "score": 0.010638297535479069,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1975,
        "score": 0.010526316240429878,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1933,
        "score": 0.010416666977107525,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1955,
        "score": 0.010204081423580647,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1953,
        "score": 0.010101010091602802,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1958,
        "score": 0.009999999776482582,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1956,
        "score": 0.009900989942252636,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1954,
        "score": 0.009803921915590763,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1962,
        "score": 0.009615384973585606,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1963,
        "score": 0.009433962404727936,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1960,
        "score": 0.009345794096589088,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1961,
        "score": 0.009259259328246117,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1964,
        "score": 0.00917431153357029,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1959,
        "score": 0.00909090880304575,
        "score_kind": "rrf"
      }
    ],
    "final_ranking": [
      {
        "chunk_id": 1969,
        "score": 0.992693305015564,
        "score_kind": "rerank"
      },
      {
        "chunk_id": 1968,
        "score": 0.8044406175613403,
        "score_kind": "rerank"
      },
      {
        "chunk_id": 1971,
        "score": 0.2798999547958374,
        "score_kind": "rerank"
      },
      {
        "chunk_id": 1937,
        "score": 0.041017722338438034,
        "score_kind": "rerank"
      },
      {
        "chunk_id": 1942,
        "score": 0.032720427960157394,
        "score_kind": "rerank"
      },
      {
        "chunk_id": 1973,
        "score": 0.00962748471647501,
        "score_kind": "rerank"
      },
      {
        "chunk_id": 1978,
        "score": 0.008264950476586819,
        "score_kind": "rerank"
      },
      {
        "chunk_id": 1970,
        "score": 0.006330976262688637,
        "score_kind": "rerank"
      },
      {
        "chunk_id": 1974,
        "score": 0.00597203616052866,
        "score_kind": "rerank"
      },
      {
        "chunk_id": 1947,
        "score": 0.004701713565737009,
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
          1954
        ]
      ]
    }
  ],
  "candidate_ids": [
    1954,
    1953,
    1958,
    1963,
    1962,
    1957,
    1955,
    1964,
    1961,
    1959,
    1956,
    1960,
    1977,
    1974,
    1945,
    1973,
    1952,
    1970,
    1937,
    1978,
    1932,
    1936,
    1931,
    1948,
    1944,
    1935,
    1967,
    1946,
    1933,
    1941,
    1950,
    1947,
    1951,
    1942,
    1965,
    1971,
    1966,
    1968,
    1934,
    1976,
    1975,
    1938,
    1940,
    1943,
    1979,
    1939,
    1980,
    1972,
    1969,
    1949
  ],
  "final_ids": [
    1954,
    1953,
    1958,
    1963,
    1962,
    1957,
    1955,
    1964,
    1961,
    1959
  ],
  "prompt_citations": [
    {
      "n": 1,
      "chunk_id": "1954",
      "section_path": "商品规格手册/智能猫砂盆 Lite(型号 MH-LP50)",
      "question": "智能猫砂盆 Lite(型号 MH-LP50)",
      "answer": "- 型号:MH-LP50\n- 适用猫咪体重:1.5kg 至 6kg\n- 猫砂容量:6L\n- 核心功能:自动感应清理、物理除臭盖板;不含 App 联网功能\n- 与 Pro 差异:Lite 无 App 远程监控与健康记录,价格更低,适合单猫家庭"
    },
    {
      "n": 3,
      "chunk_id": "1958",
      "section_path": "商品规格手册/自动饮水机 Pro 不锈钢(型号 MH-W60)",
      "question": "自动饮水机 Pro 不锈钢(型号 MH-W60)",
      "answer": "- 型号:MH-W60\n- 水箱容量:6L,304 不锈钢表面盘\n- 过滤:双滤芯并联,建议每 4 周更换一次滤芯\n- 核心功能:双泵冗余、无线水位提醒推送 App、缺水断电保护\n- 清洗:不锈钢面盘可高温消毒,建议每周清洗一次"
    },
    {
      "n": 5,
      "chunk_id": "1962",
      "section_path": "商品规格手册/自动喂食器 基础版(型号 MH-FD10)",
      "question": "自动喂食器 基础版(型号 MH-FD10)",
      "answer": "- 型号:MH-FD10\n- 粮桶容量:4L\n- 核心功能:定时定量投喂,每日最多 6 餐,语音呼唤进食\n- 供电:市电供电 + 4 节 5 号电池断电应急\n- 说明:基础版不含摄像头与 App 远程投喂"
    },
    {
      "n": 7,
      "chunk_id": "1955",
      "section_path": "商品规格手册/智能猫砂盆 Max(型号 MH-LP200)",
      "question": "智能猫砂盆 Max(型号 MH-LP200)",
      "answer": "- 型号:MH-LP200\n- 适用猫咪体重:2kg 至 12kg,适合大型猫与多猫家庭\n- 猫砂容量:12L,废砂盒容量约 10 天(单猫)\n- 核心功能:超大滚筒、双重称重防夹、活性炭除臭、App 多猫健康档案\n- 供电:220V 市电\n- 清理提示:多猫家庭建议每 3 至 5 天倾倒一次废砂盒"
    },
    {
      "n": 9,
      "chunk_id": "1961",
      "section_path": "商品规格手册/大号三档加热垫(型号 MH-HP20)",
      "question": "大号三档加热垫(型号 MH-HP20)",
      "answer": "- 型号:MH-HP20\n- 尺寸:60cm × 45cm\n- 温控:三档可调 30℃ / 38℃ / 45℃,内置过热保护与定时关机\n- 防护:防水防抓咬电线套管,表面绒布可拆洗\n- 适用:大型猫、多猫窝及冬季保暖"
    },
    {
      "n": 10,
      "chunk_id": "1959",
      "section_path": "商品规格手册/大型猫爬架(型号 MH-CT30)",
      "question": "大型猫爬架(型号 MH-CT30)",
      "answer": "- 型号:MH-CT30\n- 高度:1.6m,共四层带顶层吊床\n- 承重:单层最大 10kg\n- 材质:剑麻柱身、绒布平台\n- 安装:需自行组装,随附六角扳手与图解说明书"
    },
    {
      "n": 8,
      "chunk_id": "1964",
      "section_path": "商品规格手册/全景看护摄像头(型号 MH-CAM1)",
      "question": "全景看护摄像头(型号 MH-CAM1)",
      "answer": "- 型号:MH-CAM1\n- 画质:2K 分辨率,355° 水平旋转、90° 俯仰\n- 核心功能:移动侦测报警、夜视、双向语音、逗猫激光\n- 存储:支持最大 128G TF 卡或云存储\n- 供电:Type-C 供电,需连接 2.4G Wi-Fi"
    },
    {
      "n": 6,
      "chunk_id": "1957",
      "section_path": "商品规格手册/自动饮水机 Plus(型号 MH-W40)",
      "question": "自动饮水机 Plus(型号 MH-W40)",
      "answer": "- 型号:MH-W40\n- 水箱容量:4L\n- 过滤:五重过滤棉 + 椰壳活性炭,建议每 3 周更换一次滤芯\n- 核心功能:UV 紫外杀菌、静音变频水泵、缺水断电保护\n- 清洗:整机可拆分水洗,建议每周清洗一次"
    },
    {
      "n": 4,
      "chunk_id": "1963",
      "section_path": "商品规格手册/自动喂食器 摄像头版(型号 MH-FD30)",
      "question": "自动喂食器 摄像头版(型号 MH-FD30)",
      "answer": "- 型号:MH-FD30\n- 粮桶容量:6L\n- 核心功能:1080P 摄像头、双向语音、App 远程手动投喂与定时投喂\n- 供电:市电供电 + 内置应急电池\n- 说明:摄像头版支持视频回看,需连接 2.4G Wi-Fi"
    },
    {
      "n": 2,
      "chunk_id": "1953",
      "section_path": "商品规格手册/智能猫砂盆 Pro(型号 MH-LP100)",
      "question": "智能猫砂盆 Pro(型号 MH-LP100)",
      "answer": "- 型号:MH-LP100\n- 适用猫咪体重:1.5kg 至 8kg\n- 猫砂容量:9L,废砂盒容量约 7 天(单猫)\n- 核心功能:自动感应清理、活性炭除臭、App 远程监控与健康记录\n- 供电:220V 市电,断电后配置自动保存\n- 清理提示:废砂盒满时 App 推送提醒,建议每 5 至 7 天倾倒一次"
    }
  ],
  "decision": {
    "useful": true,
    "reason": "两型号规格证据齐全",
    "response_kind": "knowledge",
    "source": null
  },
  "answer": "您好！根据商品规格资料，MH-LP50 与 Pro 版的主要区别如下：\n\n**智能猫砂盆 Lite（MH-LP50）**[1]\n- 适用猫咪体重：1.5kg–6kg\n- 猫砂容量：6L\n- 核心功能：自动感应清理、物理除臭盖板\n- 不含 App 联网功能，适合单猫家庭，价格更低[1]\n\n**智能猫砂盆 Pro（MH-LP100）**[2]\n- 适用猫咪体重：1.5kg–8kg\n- 猫砂容量：9L，废砂盒约 7 天（单猫）\n- 核心功能：自动感应清理、活性炭除臭、App 远程监控与健康记录\n- 废砂盒满时 App 推送提醒[2]\n\n简单来说：Pro 版体重适用范围更广、猫砂容量更大，并支持 App 远程监控与健康记录；Lite 版则更经济实惠，但没有联网功能[1][2]。\n\n请问还需要了解价格或库存信息吗？",
  "point_verdicts": [
    {
      "point_id": "p1",
      "covered": true,
      "reason": "回答明确说明 Lite 版不含 App 联网功能，且 Pro 支持远程监控与健康记录，条件限定在 MH-LP50，已覆盖"
    },
    {
      "point_id": "p2",
      "covered": true,
      "reason": "回答指出 Lite 价格更低、适合单猫家庭，与证据[1]一致，已覆盖"
    }
  ],
  "claim_verdicts": [
    {
      "claim": "智能猫砂盆 Lite（MH-LP50）适用猫咪体重为1.5kg至6kg",
      "supported": true,
      "reason": "证据[1]明确列出适用猫咪体重1.5kg至6kg"
    },
    {
      "claim": "智能猫砂盆 Lite（MH-LP50）猫砂容量为6L",
      "supported": true,
      "reason": "证据[1]列出猫砂容量6L"
    },
    {
      "claim": "Lite 版核心功能为自动感应清理、物理除臭盖板",
      "supported": true,
      "reason": "证据[1]列出核心功能：自动感应清理、物理除臭盖板"
    },
    {
      "claim": "Lite 版不含 App 联网功能",
      "supported": true,
      "reason": "证据[1]明确写明不含App联网功能"
    },
    {
      "claim": "Lite 版适合单猫家庭，价格更低",
      "supported": true,
      "reason": "证据[1]明确写明价格更低、适合单猫家庭"
    },
    {
      "claim": "智能猫砂盆 Pro（MH-LP100）适用猫咪体重为1.5kg至8kg",
      "supported": true,
      "reason": "证据[2]列出适用猫咪体重1.5kg至8kg"
    },
    {
      "claim": "Pro 版猫砂容量为9L，废砂盒约7天（单猫）",
      "supported": true,
      "reason": "证据[2]列出猫砂容量9L，废砂盒容量约7天(单猫)"
    },
    {
      "claim": "Pro 版核心功能为自动感应清理、活性炭除臭、App 远程监控与健康记录",
      "supported": true,
      "reason": "证据[2]列出核心功能与回答一致"
    },
    {
      "claim": "Pro 版废砂盒满时 App 推送提醒",
      "supported": true,
      "reason": "证据[2]清理提示写明废砂盒满时App推送提醒"
    },
    {
      "claim": "Pro 版体重适用范围更广、猫砂容量更大",
      "supported": true,
      "reason": "由证据[1]与[2]对比可支持：8kg>6kg，9L>6L"
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
  "elapsed_ms": 16208.823600085452,
  "judge_snapshot": {
    "prompt_version": "joint-generation-v2.1",
    "finish_reason": "stop"
  },
  "rewrite": {
    "policy_version": "original-query-on-invalid-v1",
    "status": "success",
    "error": null
  },
  "audit": {
    "audit_version": 1,
    "source_map_id": "af6590ab401319d942bddff0b30213a4cd888b8cf115ebd5cdec3adb87687e55",
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
        "chunk_id": 1954,
        "score": 0.541914701461792,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1953,
        "score": 0.49221447110176086,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1958,
        "score": 0.4623093008995056,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1963,
        "score": 0.4484242796897888,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1962,
        "score": 0.4472969174385071,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1957,
        "score": 0.44213002920150757,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1955,
        "score": 0.4366154074668884,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1964,
        "score": 0.4358614385128021,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1961,
        "score": 0.42101719975471497,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1959,
        "score": 0.412375271320343,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1956,
        "score": 0.39626580476760864,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1960,
        "score": 0.3895488977432251,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1977,
        "score": 0.3642714023590088,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1974,
        "score": 0.3369862139225006,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1945,
        "score": 0.32716214656829834,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1973,
        "score": 0.3230932354927063,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1952,
        "score": 0.32006973028182983,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1970,
        "score": 0.31767943501472473,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1937,
        "score": 0.31760919094085693,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1978,
        "score": 0.30909478664398193,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1932,
        "score": 0.30889827013015747,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1936,
        "score": 0.29683154821395874,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1931,
        "score": 0.28847962617874146,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1948,
        "score": 0.2840690314769745,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1944,
        "score": 0.28290611505508423,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1935,
        "score": 0.28186357021331787,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1967,
        "score": 0.27789217233657837,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1946,
        "score": 0.2723686695098877,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1933,
        "score": 0.27169930934906006,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1941,
        "score": 0.26915642619132996,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1950,
        "score": 0.26893630623817444,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1947,
        "score": 0.25857019424438477,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1951,
        "score": 0.25779059529304504,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1942,
        "score": 0.2489739954471588,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1965,
        "score": 0.248498797416687,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1971,
        "score": 0.2441561073064804,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1966,
        "score": 0.24142827093601227,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1968,
        "score": 0.2373632788658142,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1934,
        "score": 0.23596227169036865,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1976,
        "score": 0.23535418510437012,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1975,
        "score": 0.23405808210372925,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1938,
        "score": 0.23046962916851044,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1940,
        "score": 0.228411003947258,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1943,
        "score": 0.2269769310951233,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1979,
        "score": 0.22343984246253967,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1939,
        "score": 0.2231275886297226,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1980,
        "score": 0.22140991687774658,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1972,
        "score": 0.21503949165344238,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1969,
        "score": 0.19571532309055328,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1949,
        "score": 0.18200039863586426,
        "score_kind": "cosine"
      }
    ],
    "final_ranking": [
      {
        "chunk_id": 1954,
        "score": 0.541914701461792,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1953,
        "score": 0.49221447110176086,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1958,
        "score": 0.4623093008995056,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1963,
        "score": 0.4484242796897888,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1962,
        "score": 0.4472969174385071,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1957,
        "score": 0.44213002920150757,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1955,
        "score": 0.4366154074668884,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1964,
        "score": 0.4358614385128021,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1961,
        "score": 0.42101719975471497,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1959,
        "score": 0.412375271320343,
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
          1954
        ]
      ]
    }
  ],
  "candidate_ids": [
    1954,
    1938,
    1958,
    1953,
    1978,
    1946,
    1974,
    1959,
    1960,
    1956,
    1961,
    1957,
    1964,
    1962,
    1963,
    1955,
    1977
  ],
  "final_ids": [
    1954,
    1938,
    1958,
    1953,
    1978,
    1946,
    1974,
    1959,
    1960,
    1956
  ],
  "prompt_citations": [
    {
      "n": 1,
      "chunk_id": "1954",
      "section_path": "商品规格手册/智能猫砂盆 Lite(型号 MH-LP50)",
      "question": "智能猫砂盆 Lite(型号 MH-LP50)",
      "answer": "- 型号:MH-LP50\n- 适用猫咪体重:1.5kg 至 6kg\n- 猫砂容量:6L\n- 核心功能:自动感应清理、物理除臭盖板;不含 App 联网功能\n- 与 Pro 差异:Lite 无 App 远程监控与健康记录,价格更低,适合单猫家庭"
    },
    {
      "n": 3,
      "chunk_id": "1958",
      "section_path": "商品规格手册/自动饮水机 Pro 不锈钢(型号 MH-W60)",
      "question": "自动饮水机 Pro 不锈钢(型号 MH-W60)",
      "answer": "- 型号:MH-W60\n- 水箱容量:6L,304 不锈钢表面盘\n- 过滤:双滤芯并联,建议每 4 周更换一次滤芯\n- 核心功能:双泵冗余、无线水位提醒推送 App、缺水断电保护\n- 清洗:不锈钢面盘可高温消毒,建议每周清洗一次"
    },
    {
      "n": 5,
      "chunk_id": "1978",
      "section_path": "开票细则/可开票类型",
      "question": "可开票类型",
      "answer": "本演示店提供电子普通发票、电子专用发票和纸质专用发票。电子普通发票可按订单申请；电子专票需要企业账户，申请前准备发票抬头及有效纳税人识别号，按申请页面提交资料。\n\n纸质专票仅企业账户可申请，申请时需提供企业开票资料、收件人和邮寄地址，快递费到付。资料审核通过后按开票流程寄出，不承诺快递送达日期。"
    },
    {
      "n": 7,
      "chunk_id": "1974",
      "section_path": "会员权益/会员等级",
      "question": "会员等级",
      "answer": "会员分为普通、银卡和金卡三档，按有效累计消费金额自动升级，不按年度消费金额计算。累计消费未满 1000 元为普通会员，满 1000 元起为银卡，满 5000 元起为金卡。\n\n有效累计消费指已完成订单的商品实际支付金额，不含配送费；退货退款部分从有效累计消费中扣除。退款后根据更新的累计消费重新计算等级，未达到原门槛时可能降级。等级与适用权益在会员中心展示。\n\n银卡在参与会员折扣的商品上享 95 折，金卡享 9 折。折扣适用商品和活动范围以结算页面标注为准。会员折扣、优惠券与满减是否叠加也以当次活动页面为准，不能一概承诺全部优惠同时生效。"
    },
    {
      "n": 9,
      "chunk_id": "1960",
      "section_path": "商品规格手册/恒温加热垫(型号 MH-HP12)",
      "question": "恒温加热垫(型号 MH-HP12)",
      "answer": "- 型号:MH-HP12\n- 尺寸:40cm × 30cm\n- 温控:恒温 38℃,内置过热保护,连续通电不超过 12 小时为宜\n- 防护:防水防抓咬电线套管\n- 适用:幼猫、老年猫及冬季保暖"
    },
    {
      "n": 10,
      "chunk_id": "1956",
      "section_path": "商品规格手册/自动饮水机(型号 MH-W20)",
      "question": "自动饮水机(型号 MH-W20)",
      "answer": "- 型号:MH-W20\n- 水箱容量:2L\n- 过滤:三重过滤棉,建议每 2 周更换一次滤芯\n- 核心功能:静音水泵、缺水断电保护、水位窗口\n- 清洗:水泵可拆卸,建议每周清洗一次"
    },
    {
      "n": 8,
      "chunk_id": "1959",
      "section_path": "商品规格手册/大型猫爬架(型号 MH-CT30)",
      "question": "大型猫爬架(型号 MH-CT30)",
      "answer": "- 型号:MH-CT30\n- 高度:1.6m,共四层带顶层吊床\n- 承重:单层最大 10kg\n- 材质:剑麻柱身、绒布平台\n- 安装:需自行组装,随附六角扳手与图解说明书"
    },
    {
      "n": 6,
      "chunk_id": "1946",
      "section_path": "商品与购物 FAQ/优惠券和满减怎么用",
      "question": "优惠券和满减怎么用",
      "answer": "优惠券在结算页「使用优惠券」中勾选,满减活动自动叠加在商品页标示的门槛上;同一订单一般限用一张店铺券,活动细则以页面为准。"
    },
    {
      "n": 4,
      "chunk_id": "1953",
      "section_path": "商品规格手册/智能猫砂盆 Pro(型号 MH-LP100)",
      "question": "智能猫砂盆 Pro(型号 MH-LP100)",
      "answer": "- 型号:MH-LP100\n- 适用猫咪体重:1.5kg 至 8kg\n- 猫砂容量:9L,废砂盒容量约 7 天(单猫)\n- 核心功能:自动感应清理、活性炭除臭、App 远程监控与健康记录\n- 供电:220V 市电,断电后配置自动保存\n- 清理提示:废砂盒满时 App 推送提醒,建议每 5 至 7 天倾倒一次"
    },
    {
      "n": 2,
      "chunk_id": "1938",
      "section_path": "商品与购物 FAQ/退货政策是什么",
      "question": "退货政策是什么",
      "answer": "支持 7 天无理由退货,商品需保持完好、不影响二次销售,具体以平台售后规则为准。"
    }
  ],
  "decision": {
    "useful": true,
    "reason": "已含MH-LP50与Pro规格差异证据",
    "response_kind": "knowledge",
    "source": null
  },
  "answer": "您好！根据商品规格手册，两款智能猫砂盆的区别如下：\n\n**Lite（MH-LP50）**[1]\n- 适用猫咪体重：1.5kg–6kg\n- 猫砂容量：6L\n- 功能：自动感应清理、物理除臭盖板，**无 App 联网功能**\n- 价格更低，适合单猫家庭\n\n**Pro（MH-LP100）**[4]\n- 适用猫咪体重：1.5kg–8kg\n- 猫砂容量：9L，废砂盒约可用 7 天（单猫）\n- 功能：自动感应清理、活性炭除臭、**App 远程监控与健康记录**，废砂盒满时 App 推送提醒\n- 供电：220V 市电，断电后自动保存配置\n\n主要差异：Pro 体型适用范围更大、猫砂容量更高、除臭方式不同，且支持 App 远程监控与健康记录；Lite 更经济实惠[1]。\n\n如需了解价格或库存，我可以为您进一步查询哦～",
  "point_verdicts": [
    {
      "point_id": "p1",
      "covered": true,
      "reason": "回答明确说明Lite无App联网功能，Pro有App远程监控与健康记录，覆盖差异且限定于MH-LP50"
    },
    {
      "point_id": "p2",
      "covered": true,
      "reason": "回答明确说明Lite价格更低、适合单猫家庭，且限定于Lite型号范围"
    }
  ],
  "claim_verdicts": [
    {
      "claim": "Lite（MH-LP50）适用猫咪体重为1.5kg–6kg",
      "supported": true,
      "reason": "证据1明确适用猫咪体重1.5kg至6kg"
    },
    {
      "claim": "Lite猫砂容量为6L",
      "supported": true,
      "reason": "证据1写明猫砂容量6L"
    },
    {
      "claim": "Lite具有自动感应清理、物理除臭盖板功能",
      "supported": true,
      "reason": "证据1核心功能列出自动感应清理、物理除臭盖板"
    },
    {
      "claim": "Lite不含App联网功能",
      "supported": true,
      "reason": "证据1明确写不含App联网功能"
    },
    {
      "claim": "Lite价格更低、适合单猫家庭",
      "supported": true,
      "reason": "证据1与Pro差异部分写明价格更低，适合单猫家庭"
    },
    {
      "claim": "Pro（MH-LP100）适用猫咪体重为1.5kg–8kg",
      "supported": true,
      "reason": "证据4写明适用体重1.5kg至8kg"
    },
    {
      "claim": "Pro猫砂容量为9L，废砂盒约可用7天（单猫）",
      "supported": true,
      "reason": "证据4写明猫砂容量9L，废砂盒约7天（单猫）"
    },
    {
      "claim": "Pro具有自动感应清理、活性炭除臭、App远程监控与健康记录功能",
      "supported": true,
      "reason": "证据4核心功能列出这些功能"
    },
    {
      "claim": "Pro废砂盒满时App推送提醒",
      "supported": true,
      "reason": "证据4清理提示写明废砂盒满时App推送提醒"
    },
    {
      "claim": "Pro供电为220V市电，断电后自动保存配置",
      "supported": true,
      "reason": "证据4写明220V市电，断电后配置自动保存"
    },
    {
      "claim": "Pro体型适用范围更大、猫砂容量更高、除臭方式与Lite不同",
      "supported": true,
      "reason": "由证据1与4对比可得：体重范围与容量更大，物理除臭与活性炭除臭不同"
    },
    {
      "claim": "Pro支持App远程监控与健康记录",
      "supported": true,
      "reason": "证据4核心功能明确列出"
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
  "elapsed_ms": 14945.595900062472,
  "judge_snapshot": {
    "prompt_version": "joint-generation-v2.1",
    "finish_reason": "stop"
  },
  "rewrite": {
    "policy_version": "original-query-on-invalid-v1",
    "status": "success",
    "error": null
  },
  "audit": {
    "audit_version": 1,
    "source_map_id": "af6590ab401319d942bddff0b30213a4cd888b8cf115ebd5cdec3adb87687e55",
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
        "chunk_id": 1954,
        "score": 9.145109176635742,
        "score_kind": "bm25"
      },
      {
        "chunk_id": 1938,
        "score": 4.2695698738098145,
        "score_kind": "bm25"
      },
      {
        "chunk_id": 1958,
        "score": 4.2516913414001465,
        "score_kind": "bm25"
      },
      {
        "chunk_id": 1953,
        "score": 3.9712343215942383,
        "score_kind": "bm25"
      },
      {
        "chunk_id": 1978,
        "score": 3.088531494140625,
        "score_kind": "bm25"
      },
      {
        "chunk_id": 1946,
        "score": 2.839679002761841,
        "score_kind": "bm25"
      },
      {
        "chunk_id": 1974,
        "score": 2.5103907585144043,
        "score_kind": "bm25"
      },
      {
        "chunk_id": 1959,
        "score": 1.9122194051742554,
        "score_kind": "bm25"
      },
      {
        "chunk_id": 1960,
        "score": 1.9122194051742554,
        "score_kind": "bm25"
      },
      {
        "chunk_id": 1956,
        "score": 1.880428671836853,
        "score_kind": "bm25"
      },
      {
        "chunk_id": 1961,
        "score": 1.8496778011322021,
        "score_kind": "bm25"
      },
      {
        "chunk_id": 1957,
        "score": 1.8102076053619385,
        "score_kind": "bm25"
      },
      {
        "chunk_id": 1964,
        "score": 1.7910975217819214,
        "score_kind": "bm25"
      },
      {
        "chunk_id": 1962,
        "score": 1.7816929817199707,
        "score_kind": "bm25"
      },
      {
        "chunk_id": 1963,
        "score": 1.7540630102157593,
        "score_kind": "bm25"
      },
      {
        "chunk_id": 1955,
        "score": 1.6596899032592773,
        "score_kind": "bm25"
      },
      {
        "chunk_id": 1977,
        "score": 1.2880016565322876,
        "score_kind": "bm25"
      }
    ],
    "final_ranking": [
      {
        "chunk_id": 1954,
        "score": 9.145109176635742,
        "score_kind": "bm25"
      },
      {
        "chunk_id": 1938,
        "score": 4.2695698738098145,
        "score_kind": "bm25"
      },
      {
        "chunk_id": 1958,
        "score": 4.2516913414001465,
        "score_kind": "bm25"
      },
      {
        "chunk_id": 1953,
        "score": 3.9712343215942383,
        "score_kind": "bm25"
      },
      {
        "chunk_id": 1978,
        "score": 3.088531494140625,
        "score_kind": "bm25"
      },
      {
        "chunk_id": 1946,
        "score": 2.839679002761841,
        "score_kind": "bm25"
      },
      {
        "chunk_id": 1974,
        "score": 2.5103907585144043,
        "score_kind": "bm25"
      },
      {
        "chunk_id": 1959,
        "score": 1.9122194051742554,
        "score_kind": "bm25"
      },
      {
        "chunk_id": 1960,
        "score": 1.9122194051742554,
        "score_kind": "bm25"
      },
      {
        "chunk_id": 1956,
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
          1954
        ]
      ]
    }
  ],
  "candidate_ids": [
    1954,
    1953,
    1958,
    1957,
    1959,
    1963,
    1962,
    1961,
    1974,
    1964,
    1960,
    1956,
    1955,
    1978,
    1977,
    1946,
    1938,
    1945,
    1973,
    1952,
    1970,
    1937,
    1932,
    1936,
    1931,
    1948,
    1944,
    1935,
    1967,
    1933,
    1941,
    1950,
    1947,
    1951,
    1942,
    1965,
    1971,
    1966,
    1968,
    1934,
    1976,
    1975,
    1940,
    1943,
    1979,
    1939,
    1980,
    1972,
    1969,
    1949
  ],
  "final_ids": [
    1954,
    1953,
    1958,
    1957,
    1959,
    1963,
    1962,
    1961,
    1974,
    1964
  ],
  "prompt_citations": [
    {
      "n": 1,
      "chunk_id": "1954",
      "section_path": "商品规格手册/智能猫砂盆 Lite(型号 MH-LP50)",
      "question": "智能猫砂盆 Lite(型号 MH-LP50)",
      "answer": "- 型号:MH-LP50\n- 适用猫咪体重:1.5kg 至 6kg\n- 猫砂容量:6L\n- 核心功能:自动感应清理、物理除臭盖板;不含 App 联网功能\n- 与 Pro 差异:Lite 无 App 远程监控与健康记录,价格更低,适合单猫家庭"
    },
    {
      "n": 3,
      "chunk_id": "1958",
      "section_path": "商品规格手册/自动饮水机 Pro 不锈钢(型号 MH-W60)",
      "question": "自动饮水机 Pro 不锈钢(型号 MH-W60)",
      "answer": "- 型号:MH-W60\n- 水箱容量:6L,304 不锈钢表面盘\n- 过滤:双滤芯并联,建议每 4 周更换一次滤芯\n- 核心功能:双泵冗余、无线水位提醒推送 App、缺水断电保护\n- 清洗:不锈钢面盘可高温消毒,建议每周清洗一次"
    },
    {
      "n": 5,
      "chunk_id": "1959",
      "section_path": "商品规格手册/大型猫爬架(型号 MH-CT30)",
      "question": "大型猫爬架(型号 MH-CT30)",
      "answer": "- 型号:MH-CT30\n- 高度:1.6m,共四层带顶层吊床\n- 承重:单层最大 10kg\n- 材质:剑麻柱身、绒布平台\n- 安装:需自行组装,随附六角扳手与图解说明书"
    },
    {
      "n": 7,
      "chunk_id": "1962",
      "section_path": "商品规格手册/自动喂食器 基础版(型号 MH-FD10)",
      "question": "自动喂食器 基础版(型号 MH-FD10)",
      "answer": "- 型号:MH-FD10\n- 粮桶容量:4L\n- 核心功能:定时定量投喂,每日最多 6 餐,语音呼唤进食\n- 供电:市电供电 + 4 节 5 号电池断电应急\n- 说明:基础版不含摄像头与 App 远程投喂"
    },
    {
      "n": 9,
      "chunk_id": "1974",
      "section_path": "会员权益/会员等级",
      "question": "会员等级",
      "answer": "会员分为普通、银卡和金卡三档，按有效累计消费金额自动升级，不按年度消费金额计算。累计消费未满 1000 元为普通会员，满 1000 元起为银卡，满 5000 元起为金卡。\n\n有效累计消费指已完成订单的商品实际支付金额，不含配送费；退货退款部分从有效累计消费中扣除。退款后根据更新的累计消费重新计算等级，未达到原门槛时可能降级。等级与适用权益在会员中心展示。\n\n银卡在参与会员折扣的商品上享 95 折，金卡享 9 折。折扣适用商品和活动范围以结算页面标注为准。会员折扣、优惠券与满减是否叠加也以当次活动页面为准，不能一概承诺全部优惠同时生效。"
    },
    {
      "n": 10,
      "chunk_id": "1964",
      "section_path": "商品规格手册/全景看护摄像头(型号 MH-CAM1)",
      "question": "全景看护摄像头(型号 MH-CAM1)",
      "answer": "- 型号:MH-CAM1\n- 画质:2K 分辨率,355° 水平旋转、90° 俯仰\n- 核心功能:移动侦测报警、夜视、双向语音、逗猫激光\n- 存储:支持最大 128G TF 卡或云存储\n- 供电:Type-C 供电,需连接 2.4G Wi-Fi"
    },
    {
      "n": 8,
      "chunk_id": "1961",
      "section_path": "商品规格手册/大号三档加热垫(型号 MH-HP20)",
      "question": "大号三档加热垫(型号 MH-HP20)",
      "answer": "- 型号:MH-HP20\n- 尺寸:60cm × 45cm\n- 温控:三档可调 30℃ / 38℃ / 45℃,内置过热保护与定时关机\n- 防护:防水防抓咬电线套管,表面绒布可拆洗\n- 适用:大型猫、多猫窝及冬季保暖"
    },
    {
      "n": 6,
      "chunk_id": "1963",
      "section_path": "商品规格手册/自动喂食器 摄像头版(型号 MH-FD30)",
      "question": "自动喂食器 摄像头版(型号 MH-FD30)",
      "answer": "- 型号:MH-FD30\n- 粮桶容量:6L\n- 核心功能:1080P 摄像头、双向语音、App 远程手动投喂与定时投喂\n- 供电:市电供电 + 内置应急电池\n- 说明:摄像头版支持视频回看,需连接 2.4G Wi-Fi"
    },
    {
      "n": 4,
      "chunk_id": "1957",
      "section_path": "商品规格手册/自动饮水机 Plus(型号 MH-W40)",
      "question": "自动饮水机 Plus(型号 MH-W40)",
      "answer": "- 型号:MH-W40\n- 水箱容量:4L\n- 过滤:五重过滤棉 + 椰壳活性炭,建议每 3 周更换一次滤芯\n- 核心功能:UV 紫外杀菌、静音变频水泵、缺水断电保护\n- 清洗:整机可拆分水洗,建议每周清洗一次"
    },
    {
      "n": 2,
      "chunk_id": "1953",
      "section_path": "商品规格手册/智能猫砂盆 Pro(型号 MH-LP100)",
      "question": "智能猫砂盆 Pro(型号 MH-LP100)",
      "answer": "- 型号:MH-LP100\n- 适用猫咪体重:1.5kg 至 8kg\n- 猫砂容量:9L,废砂盒容量约 7 天(单猫)\n- 核心功能:自动感应清理、活性炭除臭、App 远程监控与健康记录\n- 供电:220V 市电,断电后配置自动保存\n- 清理提示:废砂盒满时 App 推送提醒,建议每 5 至 7 天倾倒一次"
    }
  ],
  "decision": {
    "useful": true,
    "reason": "证据含Lite与Pro猫砂盆规格，可回答差异",
    "response_kind": "knowledge",
    "source": null
  },
  "answer": "您好！根据商品规格手册，MH-LP50（Lite）与 Pro 版（MH-LP100）的主要区别如下：\n\n**智能猫砂盆 Lite（MH-LP50）** [1]\n- 适用猫咪体重：1.5kg 至 6kg\n- 猫砂容量：6L\n- 核心功能：自动感应清理、物理除臭盖板；不含 App 联网功能\n- 价格更低，适合单猫家庭\n\n**智能猫砂盆 Pro（MH-LP100）** [2]\n- 适用猫咪体重：1.5kg 至 8kg\n- 猫砂容量：9L，废砂盒容量约 7 天（单猫）\n- 核心功能：自动感应清理、活性炭除臭、App 远程监控与健康记录\n- 断电后配置自动保存，废砂盒满时 App 推送提醒\n\n**总结**：Pro 版体型适用范围更广、猫砂容量更大，并额外支持 App 远程监控与健康记录；Lite 版功能更基础、价格更低。请问还有什么可以帮您的吗？",
  "point_verdicts": [
    {
      "point_id": "p1",
      "covered": true,
      "reason": "回答明确指出 Lite 不含 App 联网功能，并在总结中说明少了 Pro 的 App 远程监控与健康记录，条件限定于 MH-LP50，覆盖完整"
    },
    {
      "point_id": "p2",
      "covered": true,
      "reason": "回答列出 Lite 价格更低、适合单猫家庭，且条件限定于智能猫砂盆 Lite MH-LP50，覆盖完整"
    }
  ],
  "claim_verdicts": [
    {
      "claim": "MH-LP50 适用猫咪体重为 1.5kg 至 6kg",
      "supported": true,
      "reason": "证据[1]明确列出该型号适用体重 1.5kg 至 6kg"
    },
    {
      "claim": "MH-LP50 猫砂容量为 6L",
      "supported": true,
      "reason": "证据[1]明确猫砂容量为 6L"
    },
    {
      "claim": "MH-LP50 核心功能为自动感应清理、物理除臭盖板，且不含 App 联网功能",
      "supported": true,
      "reason": "证据[1]核心功能项明确写出这些内容并注明不含 App 联网功能"
    },
    {
      "claim": "MH-LP50 价格更低，适合单猫家庭",
      "supported": true,
      "reason": "证据[1]与 Pro 差异项写明价格更低、适合单猫家庭"
    },
    {
      "claim": "MH-LP100（Pro）适用猫咪体重为 1.5kg 至 8kg",
      "supported": true,
      "reason": "证据[2]明确列出该型号适用体重 1.5kg 至 8kg"
    },
    {
      "claim": "MH-LP100 猫砂容量为 9L，废砂盒容量约 7 天（单猫）",
      "supported": true,
      "reason": "证据[2]明确写出猫砂容量 9L、废砂盒容量约 7 天（单猫）"
    },
    {
      "claim": "MH-LP100 核心功能为自动感应清理、活性炭除臭、App 远程监控与健康记录",
      "supported": true,
      "reason": "证据[2]核心功能项逐项对应"
    },
    {
      "claim": "MH-LP100 断电后配置自动保存",
      "supported": true,
      "reason": "证据[2]供电项写明断电后配置自动保存"
    },
    {
      "claim": "MH-LP100 废砂盒满时 App 推送提醒",
      "supported": true,
      "reason": "证据[2]清理提示项写明废砂盒满时 App 推送提醒"
    },
    {
      "claim": "Pro 版体型适用范围更广、猫砂容量更大，并额外支持 App 远程监控与健康记录",
      "supported": true,
      "reason": "由证据[1][2]对比：8kg 大于 6kg，9L 大于 6L，且仅 Pro 有 App 远程监控与健康记录"
    },
    {
      "claim": "Lite 版功能更基础、价格更低",
      "supported": true,
      "reason": "证据[1]与 Pro 差异项支持价格更低及功能差异"
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
  "elapsed_ms": 13417.2803000547,
  "judge_snapshot": {
    "prompt_version": "joint-generation-v2.1",
    "finish_reason": "stop"
  },
  "rewrite": {
    "policy_version": "original-query-on-invalid-v1",
    "status": "success",
    "error": null
  },
  "audit": {
    "audit_version": 1,
    "source_map_id": "af6590ab401319d942bddff0b30213a4cd888b8cf115ebd5cdec3adb87687e55",
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
        "chunk_id": 1954,
        "score": 0.032786883413791656,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1953,
        "score": 0.0317540317773819,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1958,
        "score": 0.0317460335791111,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1957,
        "score": 0.02904040366411209,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1959,
        "score": 0.028991596773266792,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1963,
        "score": 0.028958333656191826,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1962,
        "score": 0.028898129239678383,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1961,
        "score": 0.028577260673046112,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1974,
        "score": 0.028438886627554893,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1964,
        "score": 0.028404511511325836,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1960,
        "score": 0.02838164195418358,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1956,
        "score": 0.028370220214128494,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1955,
        "score": 0.02808326855301857,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1978,
        "score": 0.02788461558520794,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1977,
        "score": 0.026685643941164017,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1946,
        "score": 0.02651515230536461,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1938,
        "score": 0.025932952761650085,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1945,
        "score": 0.013333333656191826,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1973,
        "score": 0.01315789483487606,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1952,
        "score": 0.012987012974917889,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1970,
        "score": 0.012820512987673283,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1937,
        "score": 0.012658228166401386,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1932,
        "score": 0.012345679104328156,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1936,
        "score": 0.012195121496915817,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1931,
        "score": 0.012048192322254181,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1948,
        "score": 0.011904762126505375,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1944,
        "score": 0.0117647061124444,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1935,
        "score": 0.011627906933426857,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1967,
        "score": 0.01149425283074379,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1933,
        "score": 0.01123595517128706,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1941,
        "score": 0.011111111380159855,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1950,
        "score": 0.010989011265337467,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1947,
        "score": 0.010869565419852734,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1951,
        "score": 0.01075268816202879,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1942,
        "score": 0.010638297535479069,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1965,
        "score": 0.010526316240429878,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1971,
        "score": 0.010416666977107525,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1966,
        "score": 0.010309278033673763,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1968,
        "score": 0.010204081423580647,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1934,
        "score": 0.010101010091602802,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1976,
        "score": 0.009999999776482582,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1975,
        "score": 0.009900989942252636,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1940,
        "score": 0.009708737954497337,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1943,
        "score": 0.009615384973585606,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1979,
        "score": 0.009523809887468815,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1939,
        "score": 0.009433962404727936,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1980,
        "score": 0.009345794096589088,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1972,
        "score": 0.009259259328246117,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1969,
        "score": 0.00917431153357029,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1949,
        "score": 0.00909090880304575,
        "score_kind": "rrf"
      }
    ],
    "final_ranking": [
      {
        "chunk_id": 1954,
        "score": 0.032786883413791656,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1953,
        "score": 0.0317540317773819,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1958,
        "score": 0.0317460335791111,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1957,
        "score": 0.02904040366411209,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1959,
        "score": 0.028991596773266792,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1963,
        "score": 0.028958333656191826,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1962,
        "score": 0.028898129239678383,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1961,
        "score": 0.028577260673046112,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1974,
        "score": 0.028438886627554893,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1964,
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
          1954
        ]
      ]
    }
  ],
  "candidate_ids": [
    1954,
    1953,
    1958,
    1957,
    1959,
    1963,
    1962,
    1961,
    1974,
    1964,
    1960,
    1956,
    1955,
    1978,
    1977,
    1946,
    1938,
    1945,
    1973,
    1952,
    1970,
    1937,
    1932,
    1936,
    1931,
    1948,
    1944,
    1935,
    1967,
    1933,
    1941,
    1950,
    1947,
    1951,
    1942,
    1965,
    1971,
    1966,
    1968,
    1934,
    1976,
    1975,
    1940,
    1943,
    1979,
    1939,
    1980,
    1972,
    1969,
    1949
  ],
  "final_ids": [
    1954,
    1953,
    1958,
    1962,
    1955,
    1964,
    1963,
    1974,
    1957,
    1937
  ],
  "prompt_citations": [
    {
      "n": 1,
      "chunk_id": "1954",
      "section_path": "商品规格手册/智能猫砂盆 Lite(型号 MH-LP50)",
      "question": "智能猫砂盆 Lite(型号 MH-LP50)",
      "answer": "- 型号:MH-LP50\n- 适用猫咪体重:1.5kg 至 6kg\n- 猫砂容量:6L\n- 核心功能:自动感应清理、物理除臭盖板;不含 App 联网功能\n- 与 Pro 差异:Lite 无 App 远程监控与健康记录,价格更低,适合单猫家庭"
    },
    {
      "n": 3,
      "chunk_id": "1958",
      "section_path": "商品规格手册/自动饮水机 Pro 不锈钢(型号 MH-W60)",
      "question": "自动饮水机 Pro 不锈钢(型号 MH-W60)",
      "answer": "- 型号:MH-W60\n- 水箱容量:6L,304 不锈钢表面盘\n- 过滤:双滤芯并联,建议每 4 周更换一次滤芯\n- 核心功能:双泵冗余、无线水位提醒推送 App、缺水断电保护\n- 清洗:不锈钢面盘可高温消毒,建议每周清洗一次"
    },
    {
      "n": 5,
      "chunk_id": "1955",
      "section_path": "商品规格手册/智能猫砂盆 Max(型号 MH-LP200)",
      "question": "智能猫砂盆 Max(型号 MH-LP200)",
      "answer": "- 型号:MH-LP200\n- 适用猫咪体重:2kg 至 12kg,适合大型猫与多猫家庭\n- 猫砂容量:12L,废砂盒容量约 10 天(单猫)\n- 核心功能:超大滚筒、双重称重防夹、活性炭除臭、App 多猫健康档案\n- 供电:220V 市电\n- 清理提示:多猫家庭建议每 3 至 5 天倾倒一次废砂盒"
    },
    {
      "n": 7,
      "chunk_id": "1963",
      "section_path": "商品规格手册/自动喂食器 摄像头版(型号 MH-FD30)",
      "question": "自动喂食器 摄像头版(型号 MH-FD30)",
      "answer": "- 型号:MH-FD30\n- 粮桶容量:6L\n- 核心功能:1080P 摄像头、双向语音、App 远程手动投喂与定时投喂\n- 供电:市电供电 + 内置应急电池\n- 说明:摄像头版支持视频回看,需连接 2.4G Wi-Fi"
    },
    {
      "n": 9,
      "chunk_id": "1957",
      "section_path": "商品规格手册/自动饮水机 Plus(型号 MH-W40)",
      "question": "自动饮水机 Plus(型号 MH-W40)",
      "answer": "- 型号:MH-W40\n- 水箱容量:4L\n- 过滤:五重过滤棉 + 椰壳活性炭,建议每 3 周更换一次滤芯\n- 核心功能:UV 紫外杀菌、静音变频水泵、缺水断电保护\n- 清洗:整机可拆分水洗,建议每周清洗一次"
    },
    {
      "n": 10,
      "chunk_id": "1937",
      "section_path": "售后手册/会员专属售后权益",
      "question": "会员专属售后权益",
      "answer": "金卡会员享优先客服接入与上门取件退换货;银卡会员享退换货运费权益 1 次/月。具体权益以会员中心页面标注为准。"
    },
    {
      "n": 8,
      "chunk_id": "1974",
      "section_path": "会员权益/会员等级",
      "question": "会员等级",
      "answer": "会员分为普通、银卡和金卡三档，按有效累计消费金额自动升级，不按年度消费金额计算。累计消费未满 1000 元为普通会员，满 1000 元起为银卡，满 5000 元起为金卡。\n\n有效累计消费指已完成订单的商品实际支付金额，不含配送费；退货退款部分从有效累计消费中扣除。退款后根据更新的累计消费重新计算等级，未达到原门槛时可能降级。等级与适用权益在会员中心展示。\n\n银卡在参与会员折扣的商品上享 95 折，金卡享 9 折。折扣适用商品和活动范围以结算页面标注为准。会员折扣、优惠券与满减是否叠加也以当次活动页面为准，不能一概承诺全部优惠同时生效。"
    },
    {
      "n": 6,
      "chunk_id": "1964",
      "section_path": "商品规格手册/全景看护摄像头(型号 MH-CAM1)",
      "question": "全景看护摄像头(型号 MH-CAM1)",
      "answer": "- 型号:MH-CAM1\n- 画质:2K 分辨率,355° 水平旋转、90° 俯仰\n- 核心功能:移动侦测报警、夜视、双向语音、逗猫激光\n- 存储:支持最大 128G TF 卡或云存储\n- 供电:Type-C 供电,需连接 2.4G Wi-Fi"
    },
    {
      "n": 4,
      "chunk_id": "1962",
      "section_path": "商品规格手册/自动喂食器 基础版(型号 MH-FD10)",
      "question": "自动喂食器 基础版(型号 MH-FD10)",
      "answer": "- 型号:MH-FD10\n- 粮桶容量:4L\n- 核心功能:定时定量投喂,每日最多 6 餐,语音呼唤进食\n- 供电:市电供电 + 4 节 5 号电池断电应急\n- 说明:基础版不含摄像头与 App 远程投喂"
    },
    {
      "n": 2,
      "chunk_id": "1953",
      "section_path": "商品规格手册/智能猫砂盆 Pro(型号 MH-LP100)",
      "question": "智能猫砂盆 Pro(型号 MH-LP100)",
      "answer": "- 型号:MH-LP100\n- 适用猫咪体重:1.5kg 至 8kg\n- 猫砂容量:9L,废砂盒容量约 7 天(单猫)\n- 核心功能:自动感应清理、活性炭除臭、App 远程监控与健康记录\n- 供电:220V 市电,断电后配置自动保存\n- 清理提示:废砂盒满时 App 推送提醒,建议每 5 至 7 天倾倒一次"
    }
  ],
  "decision": {
    "useful": true,
    "reason": "有Lite与Pro猫砂盆规格证据可直接对比",
    "response_kind": "knowledge",
    "source": null
  },
  "answer": "您好！根据商品规格手册，两者主要区别如下：\n\n**智能猫砂盆 Lite（MH-LP50）**[1]\n- 适用猫咪体重：1.5kg–6kg\n- 猫砂容量：6L\n- 功能：自动感应清理、物理除臭盖板；**不含 App 联网功能**\n- 适合单猫家庭，价格更低\n\n**智能猫砂盆 Pro（MH-LP100）**[2]\n- 适用猫咪体重：1.5kg–8kg\n- 猫砂容量：9L，废砂盒约 7 天（单猫）\n- 功能：自动感应清理、活性炭除臭、**App 远程监控与健康记录**\n- 供电：220V 市电，断电后配置自动保存；废砂盒满时 App 推送提醒\n\n简单来说：Pro 容量更大、适用体重范围更广，并多了 App 远程监控与健康记录功能；Lite 更经济实惠。如需了解具体价格和库存，我可以为您查询哦。",
  "point_verdicts": [
    {
      "point_id": "p1",
      "covered": true,
      "reason": "回答明确指出 Lite 不含 App 联网，Pro 有 App 远程监控与健康记录，条件限定 MH-LP50 已保留"
    },
    {
      "point_id": "p2",
      "covered": true,
      "reason": "回答明确指出 Lite 适合单猫家庭、价格更低，条件限定已保留"
    }
  ],
  "claim_verdicts": [
    {
      "claim": "智能猫砂盆 Lite(MH-LP50) 适用猫咪体重为 1.5kg–6kg",
      "supported": true,
      "reason": "证据1明确列出适用体重 1.5kg 至 6kg"
    },
    {
      "claim": "智能猫砂盆 Lite(MH-LP50) 猫砂容量为 6L",
      "supported": true,
      "reason": "证据1明确猫砂容量 6L"
    },
    {
      "claim": "智能猫砂盆 Lite(MH-LP50) 具备自动感应清理、物理除臭盖板功能，不含 App 联网功能",
      "supported": true,
      "reason": "证据1核心功能栏明确该描述，包括不含 App 联网"
    },
    {
      "claim": "智能猫砂盆 Lite 适合单猫家庭且价格更低",
      "supported": true,
      "reason": "证据1与 Pro 差异栏明确价格更低、适合单猫家庭"
    },
    {
      "claim": "智能猫砂盆 Pro(MH-LP100) 适用猫咪体重为 1.5kg–8kg",
      "supported": true,
      "reason": "证据2明确适用体重 1.5kg 至 8kg"
    },
    {
      "claim": "智能猫砂盆 Pro(MH-LP100) 猫砂容量 9L，废砂盒约 7 天(单猫)",
      "supported": true,
      "reason": "证据2明确猫砂容量 9L，废砂盒容量约 7 天(单猫)"
    },
    {
      "claim": "智能猫砂盆 Pro(MH-LP100) 具备自动感应清理、活性炭除臭、App 远程监控与健康记录功能",
      "supported": true,
      "reason": "证据2核心功能栏明确列出该三项功能"
    },
    {
      "claim": "智能猫砂盆 Pro(MH-LP100) 供电为 220V 市电，断电后配置自动保存",
      "supported": true,
      "reason": "证据2供电栏明确 220V 市电，断电后配置自动保存"
    },
    {
      "claim": "智能猫砂盆 Pro(MH-LP100) 废砂盒满时 App 推送提醒",
      "supported": true,
      "reason": "证据2清理提示明确废砂盒满时 App 推送提醒"
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
  "elapsed_ms": 17217.016200069338,
  "judge_snapshot": {
    "prompt_version": "joint-generation-v2.1",
    "finish_reason": "stop"
  },
  "rewrite": {
    "policy_version": "original-query-on-invalid-v1",
    "status": "success",
    "error": null
  },
  "audit": {
    "audit_version": 1,
    "source_map_id": "af6590ab401319d942bddff0b30213a4cd888b8cf115ebd5cdec3adb87687e55",
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
        "chunk_id": 1954,
        "score": 0.032786883413791656,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1953,
        "score": 0.0317540317773819,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1958,
        "score": 0.0317460335791111,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1957,
        "score": 0.02904040366411209,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1959,
        "score": 0.028991596773266792,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1963,
        "score": 0.028958333656191826,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1962,
        "score": 0.028898129239678383,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1961,
        "score": 0.028577260673046112,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1974,
        "score": 0.028438886627554893,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1964,
        "score": 0.028404511511325836,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1960,
        "score": 0.02838164195418358,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1956,
        "score": 0.028370220214128494,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1955,
        "score": 0.02808326855301857,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1978,
        "score": 0.02788461558520794,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1977,
        "score": 0.026685643941164017,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1946,
        "score": 0.02651515230536461,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1938,
        "score": 0.025932952761650085,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1945,
        "score": 0.013333333656191826,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1973,
        "score": 0.01315789483487606,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1952,
        "score": 0.012987012974917889,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1970,
        "score": 0.012820512987673283,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1937,
        "score": 0.012658228166401386,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1932,
        "score": 0.012345679104328156,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1936,
        "score": 0.012195121496915817,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1931,
        "score": 0.012048192322254181,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1948,
        "score": 0.011904762126505375,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1944,
        "score": 0.0117647061124444,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1935,
        "score": 0.011627906933426857,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1967,
        "score": 0.01149425283074379,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1933,
        "score": 0.01123595517128706,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1941,
        "score": 0.011111111380159855,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1950,
        "score": 0.010989011265337467,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1947,
        "score": 0.010869565419852734,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1951,
        "score": 0.01075268816202879,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1942,
        "score": 0.010638297535479069,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1965,
        "score": 0.010526316240429878,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1971,
        "score": 0.010416666977107525,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1966,
        "score": 0.010309278033673763,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1968,
        "score": 0.010204081423580647,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1934,
        "score": 0.010101010091602802,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1976,
        "score": 0.009999999776482582,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1975,
        "score": 0.009900989942252636,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1940,
        "score": 0.009708737954497337,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1943,
        "score": 0.009615384973585606,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1979,
        "score": 0.009523809887468815,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1939,
        "score": 0.009433962404727936,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1980,
        "score": 0.009345794096589088,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1972,
        "score": 0.009259259328246117,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1969,
        "score": 0.00917431153357029,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1949,
        "score": 0.00909090880304575,
        "score_kind": "rrf"
      }
    ],
    "final_ranking": [
      {
        "chunk_id": 1954,
        "score": 0.9742347002029419,
        "score_kind": "rerank"
      },
      {
        "chunk_id": 1953,
        "score": 0.12143407762050629,
        "score_kind": "rerank"
      },
      {
        "chunk_id": 1958,
        "score": 0.015294485725462437,
        "score_kind": "rerank"
      },
      {
        "chunk_id": 1962,
        "score": 0.00871511921286583,
        "score_kind": "rerank"
      },
      {
        "chunk_id": 1955,
        "score": 0.008358011953532696,
        "score_kind": "rerank"
      },
      {
        "chunk_id": 1964,
        "score": 0.004421382676810026,
        "score_kind": "rerank"
      },
      {
        "chunk_id": 1963,
        "score": 0.003608993487432599,
        "score_kind": "rerank"
      },
      {
        "chunk_id": 1974,
        "score": 0.0033694501034915447,
        "score_kind": "rerank"
      },
      {
        "chunk_id": 1957,
        "score": 0.0017507974989712238,
        "score_kind": "rerank"
      },
      {
        "chunk_id": 1937,
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
  "refused": false,
  "status": "completed",
  "stage": "complete",
  "query": "MH-W20 和 MH-W60 换滤芯的周期一样吗",
  "query_plan": {
    "standard": "MH-W20 和 MH-W60 换滤芯的周期一样吗",
    "expansions": []
  },
  "mapped_groups": [
    {
      "group_id": "g1",
      "alternatives": [
        [
          1956
        ]
      ]
    },
    {
      "group_id": "g2",
      "alternatives": [
        [
          1958
        ]
      ]
    }
  ],
  "candidate_ids": [
    1956,
    1957,
    1958,
    1977,
    1955,
    1954,
    1953,
    1961,
    1962,
    1963,
    1936,
    1960,
    1970,
    1967,
    1931,
    1932,
    1940,
    1959,
    1964,
    1965,
    1934,
    1935,
    1980,
    1937,
    1952,
    1979,
    1933,
    1968,
    1941,
    1938,
    1971,
    1949,
    1951,
    1973,
    1945,
    1966,
    1948,
    1950,
    1972,
    1974,
    1975,
    1944,
    1947,
    1978,
    1943,
    1969,
    1942,
    1939,
    1946,
    1976
  ],
  "final_ids": [
    1956,
    1957,
    1958,
    1977,
    1955,
    1954,
    1953,
    1961,
    1962,
    1963
  ],
  "prompt_citations": [
    {
      "n": 1,
      "chunk_id": "1956",
      "section_path": "商品规格手册/自动饮水机(型号 MH-W20)",
      "question": "自动饮水机(型号 MH-W20)",
      "answer": "- 型号:MH-W20\n- 水箱容量:2L\n- 过滤:三重过滤棉,建议每 2 周更换一次滤芯\n- 核心功能:静音水泵、缺水断电保护、水位窗口\n- 清洗:水泵可拆卸,建议每周清洗一次"
    },
    {
      "n": 3,
      "chunk_id": "1958",
      "section_path": "商品规格手册/自动饮水机 Pro 不锈钢(型号 MH-W60)",
      "question": "自动饮水机 Pro 不锈钢(型号 MH-W60)",
      "answer": "- 型号:MH-W60\n- 水箱容量:6L,304 不锈钢表面盘\n- 过滤:双滤芯并联,建议每 4 周更换一次滤芯\n- 核心功能:双泵冗余、无线水位提醒推送 App、缺水断电保护\n- 清洗:不锈钢面盘可高温消毒,建议每周清洗一次"
    },
    {
      "n": 5,
      "chunk_id": "1955",
      "section_path": "商品规格手册/智能猫砂盆 Max(型号 MH-LP200)",
      "question": "智能猫砂盆 Max(型号 MH-LP200)",
      "answer": "- 型号:MH-LP200\n- 适用猫咪体重:2kg 至 12kg,适合大型猫与多猫家庭\n- 猫砂容量:12L,废砂盒容量约 10 天(单猫)\n- 核心功能:超大滚筒、双重称重防夹、活性炭除臭、App 多猫健康档案\n- 供电:220V 市电\n- 清理提示:多猫家庭建议每 3 至 5 天倾倒一次废砂盒"
    },
    {
      "n": 7,
      "chunk_id": "1953",
      "section_path": "商品规格手册/智能猫砂盆 Pro(型号 MH-LP100)",
      "question": "智能猫砂盆 Pro(型号 MH-LP100)",
      "answer": "- 型号:MH-LP100\n- 适用猫咪体重:1.5kg 至 8kg\n- 猫砂容量:9L,废砂盒容量约 7 天(单猫)\n- 核心功能:自动感应清理、活性炭除臭、App 远程监控与健康记录\n- 供电:220V 市电,断电后配置自动保存\n- 清理提示:废砂盒满时 App 推送提醒,建议每 5 至 7 天倾倒一次"
    },
    {
      "n": 9,
      "chunk_id": "1962",
      "section_path": "商品规格手册/自动喂食器 基础版(型号 MH-FD10)",
      "question": "自动喂食器 基础版(型号 MH-FD10)",
      "answer": "- 型号:MH-FD10\n- 粮桶容量:4L\n- 核心功能:定时定量投喂,每日最多 6 餐,语音呼唤进食\n- 供电:市电供电 + 4 节 5 号电池断电应急\n- 说明:基础版不含摄像头与 App 远程投喂"
    },
    {
      "n": 10,
      "chunk_id": "1963",
      "section_path": "商品规格手册/自动喂食器 摄像头版(型号 MH-FD30)",
      "question": "自动喂食器 摄像头版(型号 MH-FD30)",
      "answer": "- 型号:MH-FD30\n- 粮桶容量:6L\n- 核心功能:1080P 摄像头、双向语音、App 远程手动投喂与定时投喂\n- 供电:市电供电 + 内置应急电池\n- 说明:摄像头版支持视频回看,需连接 2.4G Wi-Fi"
    },
    {
      "n": 8,
      "chunk_id": "1961",
      "section_path": "商品规格手册/大号三档加热垫(型号 MH-HP20)",
      "question": "大号三档加热垫(型号 MH-HP20)",
      "answer": "- 型号:MH-HP20\n- 尺寸:60cm × 45cm\n- 温控:三档可调 30℃ / 38℃ / 45℃,内置过热保护与定时关机\n- 防护:防水防抓咬电线套管,表面绒布可拆洗\n- 适用:大型猫、多猫窝及冬季保暖"
    },
    {
      "n": 6,
      "chunk_id": "1954",
      "section_path": "商品规格手册/智能猫砂盆 Lite(型号 MH-LP50)",
      "question": "智能猫砂盆 Lite(型号 MH-LP50)",
      "answer": "- 型号:MH-LP50\n- 适用猫咪体重:1.5kg 至 6kg\n- 猫砂容量:6L\n- 核心功能:自动感应清理、物理除臭盖板;不含 App 联网功能\n- 与 Pro 差异:Lite 无 App 远程监控与健康记录,价格更低,适合单猫家庭"
    },
    {
      "n": 4,
      "chunk_id": "1977",
      "section_path": "积分规则/积分怎么用",
      "question": "积分怎么用",
      "answer": "积分可在结算时抵扣商品金额，100 积分抵 1 元现金，单笔订单最多抵 30 元，不用于抵扣偏远地区附加运费，也不支持直接提现。\n\n2000 积分可兑换自动饮水机滤芯 3 片，该兑换套装适用于 MH-W40，普通配送地区包邮；偏远地区附加配送费仍需按页面规则确认。MH-W40 的滤芯更换周期以商品规格手册为准。\n\n800 积分可兑换猫零食小样，普通配送地区另收 6 元运费；该兑换不直接套用普通购物订单的满 99 元包邮规则。兑换商品、可用库存及偏远地区配送规则以兑换页面标注为准。"
    },
    {
      "n": 2,
      "chunk_id": "1957",
      "section_path": "商品规格手册/自动饮水机 Plus(型号 MH-W40)",
      "question": "自动饮水机 Plus(型号 MH-W40)",
      "answer": "- 型号:MH-W40\n- 水箱容量:4L\n- 过滤:五重过滤棉 + 椰壳活性炭,建议每 3 周更换一次滤芯\n- 核心功能:UV 紫外杀菌、静音变频水泵、缺水断电保护\n- 清洗:整机可拆分水洗,建议每周清洗一次"
    }
  ],
  "decision": {
    "useful": true,
    "reason": "两款滤芯更换周期均有证据：W20每2周，W60每4周",
    "response_kind": "knowledge",
    "source": null
  },
  "answer": "您好！两款饮水机的滤芯更换周期不一样：\n\n- **MH-W20**：三重过滤棉，建议每 **2 周**更换一次滤芯 [1]\n- **MH-W60**：双滤芯并联，建议每 **4 周**更换一次滤芯 [3]\n\n两款机器均建议每周清洗一次 [1][3]。如有其他问题，欢迎随时咨询~",
  "point_verdicts": [
    {
      "point_id": "p1",
      "covered": true,
      "reason": "回答指出MH-W20建议每2周更换一次滤芯，且限定于自动饮水机MH-W20，与要点及条件一致。"
    },
    {
      "point_id": "p2",
      "covered": true,
      "reason": "回答指出MH-W60建议每4周更换一次滤芯并明确两款周期不一样，限定于MH-W60，覆盖完整。"
    }
  ],
  "claim_verdicts": [
    {
      "claim": "MH-W20为三重过滤棉，建议每2周更换一次滤芯",
      "supported": true,
      "reason": "证据[1]MH-W20规格明确三重过滤棉建议每2周更换一次滤芯，完全支持。"
    },
    {
      "claim": "MH-W60为双滤芯并联，建议每4周更换一次滤芯",
      "supported": true,
      "reason": "证据[3]MH-W60规格明确双滤芯并联建议每4周更换一次滤芯，完全支持。"
    },
    {
      "claim": "MH-W20与MH-W60的滤芯更换周期不一样",
      "supported": true,
      "reason": "证据[1]为2周、证据[3]为4周，两证据结合支持周期不同的比较断言。"
    },
    {
      "claim": "两款机器均建议每周清洗一次",
      "supported": true,
      "reason": "证据[1]与[3]均建议每周清洗一次，支持该断言。"
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
  "elapsed_ms": 14189.805600093678,
  "judge_snapshot": {
    "prompt_version": "joint-generation-v2.1",
    "finish_reason": "stop"
  },
  "rewrite": {
    "policy_version": "original-query-on-invalid-v1",
    "status": "success",
    "error": null
  },
  "audit": {
    "audit_version": 1,
    "source_map_id": "af6590ab401319d942bddff0b30213a4cd888b8cf115ebd5cdec3adb87687e55",
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
    "candidate_ranking": [
      {
        "chunk_id": 1956,
        "score": 0.6372488737106323,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1957,
        "score": 0.6065855026245117,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1958,
        "score": 0.6055154800415039,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1977,
        "score": 0.4763084352016449,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1955,
        "score": 0.46994495391845703,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1954,
        "score": 0.45940762758255005,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1953,
        "score": 0.44774460792541504,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1961,
        "score": 0.4433952271938324,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1962,
        "score": 0.43820053339004517,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1963,
        "score": 0.43427425622940063,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1936,
        "score": 0.4185059666633606,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1960,
        "score": 0.4105088412761688,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1970,
        "score": 0.40560293197631836,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1967,
        "score": 0.3989255726337433,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1931,
        "score": 0.39590340852737427,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1932,
        "score": 0.394534707069397,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1940,
        "score": 0.3905488848686218,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1959,
        "score": 0.3741084933280945,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1964,
        "score": 0.36377912759780884,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1965,
        "score": 0.36040210723876953,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1934,
        "score": 0.35968276858329773,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1935,
        "score": 0.35635748505592346,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1980,
        "score": 0.3514554500579834,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1937,
        "score": 0.3506259620189667,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1952,
        "score": 0.3477201461791992,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1979,
        "score": 0.34456151723861694,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1933,
        "score": 0.33749300241470337,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1968,
        "score": 0.3339157998561859,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1941,
        "score": 0.33388233184814453,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1938,
        "score": 0.3259001076221466,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1971,
        "score": 0.318137526512146,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1949,
        "score": 0.3136257529258728,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1951,
        "score": 0.3077421486377716,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1973,
        "score": 0.30662479996681213,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1945,
        "score": 0.29876255989074707,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1966,
        "score": 0.29794302582740784,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1948,
        "score": 0.2969576120376587,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1950,
        "score": 0.27952128648757935,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1972,
        "score": 0.2792452573776245,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1974,
        "score": 0.27878156304359436,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1975,
        "score": 0.27489328384399414,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1944,
        "score": 0.2708907127380371,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1947,
        "score": 0.27039021253585815,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1978,
        "score": 0.26244521141052246,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1943,
        "score": 0.260103315114975,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1969,
        "score": 0.2599169909954071,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1942,
        "score": 0.24458271265029907,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1939,
        "score": 0.24380430579185486,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1946,
        "score": 0.23986023664474487,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1976,
        "score": 0.23938995599746704,
        "score_kind": "cosine"
      }
    ],
    "final_ranking": [
      {
        "chunk_id": 1956,
        "score": 0.6372488737106323,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1957,
        "score": 0.6065855026245117,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1958,
        "score": 0.6055154800415039,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1977,
        "score": 0.4763084352016449,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1955,
        "score": 0.46994495391845703,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1954,
        "score": 0.45940762758255005,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1953,
        "score": 0.44774460792541504,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1961,
        "score": 0.4433952271938324,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1962,
        "score": 0.43820053339004517,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1963,
        "score": 0.43427425622940063,
        "score_kind": "cosine"
      }
    ]
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
  "refused": false,
  "status": "completed",
  "stage": "complete",
  "query": "MH-W20 和 MH-W60 换滤芯的周期一样吗",
  "query_plan": {
    "standard": "MH-W20 和 MH-W60 换滤芯的周期一样吗",
    "expansions": []
  },
  "mapped_groups": [
    {
      "group_id": "g1",
      "alternatives": [
        [
          1956
        ]
      ]
    },
    {
      "group_id": "g2",
      "alternatives": [
        [
          1958
        ]
      ]
    }
  ],
  "candidate_ids": [
    1958,
    1956,
    1977,
    1957,
    1968,
    1948,
    1959,
    1960,
    1946,
    1961,
    1954,
    1964,
    1962,
    1974,
    1963,
    1955,
    1953,
    1978,
    1972,
    1973,
    1969,
    1980,
    1939,
    1941,
    1952,
    1943,
    1949,
    1967,
    1965,
    1950,
    1935,
    1971,
    1976,
    1979
  ],
  "final_ids": [
    1958,
    1956,
    1977,
    1957,
    1968,
    1948,
    1959,
    1960,
    1946,
    1961
  ],
  "prompt_citations": [
    {
      "n": 1,
      "chunk_id": "1958",
      "section_path": "商品规格手册/自动饮水机 Pro 不锈钢(型号 MH-W60)",
      "question": "自动饮水机 Pro 不锈钢(型号 MH-W60)",
      "answer": "- 型号:MH-W60\n- 水箱容量:6L,304 不锈钢表面盘\n- 过滤:双滤芯并联,建议每 4 周更换一次滤芯\n- 核心功能:双泵冗余、无线水位提醒推送 App、缺水断电保护\n- 清洗:不锈钢面盘可高温消毒,建议每周清洗一次"
    },
    {
      "n": 3,
      "chunk_id": "1977",
      "section_path": "积分规则/积分怎么用",
      "question": "积分怎么用",
      "answer": "积分可在结算时抵扣商品金额，100 积分抵 1 元现金，单笔订单最多抵 30 元，不用于抵扣偏远地区附加运费，也不支持直接提现。\n\n2000 积分可兑换自动饮水机滤芯 3 片，该兑换套装适用于 MH-W40，普通配送地区包邮；偏远地区附加配送费仍需按页面规则确认。MH-W40 的滤芯更换周期以商品规格手册为准。\n\n800 积分可兑换猫零食小样，普通配送地区另收 6 元运费；该兑换不直接套用普通购物订单的满 99 元包邮规则。兑换商品、可用库存及偏远地区配送规则以兑换页面标注为准。"
    },
    {
      "n": 5,
      "chunk_id": "1968",
      "section_path": "退货退款政策/换货政策/换货运费",
      "question": "换货运费",
      "answer": "非质量问题的换货,往返运费由买家承担;因质量问题或发错货的换货,往返运费由平台承担。"
    },
    {
      "n": 7,
      "chunk_id": "1959",
      "section_path": "商品规格手册/大型猫爬架(型号 MH-CT30)",
      "question": "大型猫爬架(型号 MH-CT30)",
      "answer": "- 型号:MH-CT30\n- 高度:1.6m,共四层带顶层吊床\n- 承重:单层最大 10kg\n- 材质:剑麻柱身、绒布平台\n- 安装:需自行组装,随附六角扳手与图解说明书"
    },
    {
      "n": 9,
      "chunk_id": "1946",
      "section_path": "商品与购物 FAQ/优惠券和满减怎么用",
      "question": "优惠券和满减怎么用",
      "answer": "优惠券在结算页「使用优惠券」中勾选,满减活动自动叠加在商品页标示的门槛上;同一订单一般限用一张店铺券,活动细则以页面为准。"
    },
    {
      "n": 10,
      "chunk_id": "1961",
      "section_path": "商品规格手册/大号三档加热垫(型号 MH-HP20)",
      "question": "大号三档加热垫(型号 MH-HP20)",
      "answer": "- 型号:MH-HP20\n- 尺寸:60cm × 45cm\n- 温控:三档可调 30℃ / 38℃ / 45℃,内置过热保护与定时关机\n- 防护:防水防抓咬电线套管,表面绒布可拆洗\n- 适用:大型猫、多猫窝及冬季保暖"
    },
    {
      "n": 8,
      "chunk_id": "1960",
      "section_path": "商品规格手册/恒温加热垫(型号 MH-HP12)",
      "question": "恒温加热垫(型号 MH-HP12)",
      "answer": "- 型号:MH-HP12\n- 尺寸:40cm × 30cm\n- 温控:恒温 38℃,内置过热保护,连续通电不超过 12 小时为宜\n- 防护:防水防抓咬电线套管\n- 适用:幼猫、老年猫及冬季保暖"
    },
    {
      "n": 6,
      "chunk_id": "1948",
      "section_path": "商品与购物 FAQ/订单可以修改或取消吗",
      "question": "订单可以修改或取消吗",
      "answer": "订单未发货前可在「我的订单」自助取消;已发货订单无法修改收货信息,可拒收后走退款流程。修改商品数量需取消后重新下单。"
    },
    {
      "n": 4,
      "chunk_id": "1957",
      "section_path": "商品规格手册/自动饮水机 Plus(型号 MH-W40)",
      "question": "自动饮水机 Plus(型号 MH-W40)",
      "answer": "- 型号:MH-W40\n- 水箱容量:4L\n- 过滤:五重过滤棉 + 椰壳活性炭,建议每 3 周更换一次滤芯\n- 核心功能:UV 紫外杀菌、静音变频水泵、缺水断电保护\n- 清洗:整机可拆分水洗,建议每周清洗一次"
    },
    {
      "n": 2,
      "chunk_id": "1956",
      "section_path": "商品规格手册/自动饮水机(型号 MH-W20)",
      "question": "自动饮水机(型号 MH-W20)",
      "answer": "- 型号:MH-W20\n- 水箱容量:2L\n- 过滤:三重过滤棉,建议每 2 周更换一次滤芯\n- 核心功能:静音水泵、缺水断电保护、水位窗口\n- 清洗:水泵可拆卸,建议每周清洗一次"
    }
  ],
  "decision": {
    "useful": true,
    "reason": "两个型号滤芯周期均有证据：MH-W20为2周，MH-W60为4周，不一样",
    "response_kind": "knowledge",
    "source": null
  },
  "answer": "您好！两款滤芯更换周期不一样：\n\n- **MH-W20**（自动饮水机）：三重过滤棉，建议**每 2 周**更换一次滤芯 [2]\n- **MH-W60**（自动饮水机 Pro 不锈钢）：双滤芯并联，建议**每 4 周**更换一次滤芯 [1]\n\n如有其他问题，欢迎随时咨询～",
  "point_verdicts": [
    {
      "point_id": "p1",
      "covered": true,
      "reason": "回答明确说明MH-W20建议每2周更换一次滤芯，并保留了自动饮水机适用条件"
    },
    {
      "point_id": "p2",
      "covered": true,
      "reason": "回答明确说明MH-W60建议每4周更换一次滤芯且两款周期不一样，条件范围保留"
    }
  ],
  "claim_verdicts": [
    {
      "claim": "MH-W20是自动饮水机，采用三重过滤棉，建议每2周更换一次滤芯",
      "supported": true,
      "reason": "证据[2]为MH-W20规格手册，载明三重过滤棉、每2周更换滤芯"
    },
    {
      "claim": "MH-W60是自动饮水机Pro不锈钢，双滤芯并联，建议每4周更换一次滤芯",
      "supported": true,
      "reason": "证据[1]为MH-W60规格手册，载明双滤芯并联、每4周更换滤芯"
    },
    {
      "claim": "两款滤芯更换周期不一样",
      "supported": true,
      "reason": "证据[2]为每2周、证据[1]为每4周，可支持周期不同"
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
  "elapsed_ms": 10391.758299898356,
  "judge_snapshot": {
    "prompt_version": "joint-generation-v2.1",
    "finish_reason": "stop"
  },
  "rewrite": {
    "policy_version": "original-query-on-invalid-v1",
    "status": "success",
    "error": null
  },
  "audit": {
    "audit_version": 1,
    "source_map_id": "af6590ab401319d942bddff0b30213a4cd888b8cf115ebd5cdec3adb87687e55",
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
    "candidate_ranking": [
      {
        "chunk_id": 1958,
        "score": 11.307323455810547,
        "score_kind": "bm25"
      },
      {
        "chunk_id": 1956,
        "score": 11.281126022338867,
        "score_kind": "bm25"
      },
      {
        "chunk_id": 1977,
        "score": 7.956859111785889,
        "score_kind": "bm25"
      },
      {
        "chunk_id": 1957,
        "score": 6.014775276184082,
        "score_kind": "bm25"
      },
      {
        "chunk_id": 1968,
        "score": 5.385351181030273,
        "score_kind": "bm25"
      },
      {
        "chunk_id": 1948,
        "score": 4.653332710266113,
        "score_kind": "bm25"
      },
      {
        "chunk_id": 1959,
        "score": 3.8244388103485107,
        "score_kind": "bm25"
      },
      {
        "chunk_id": 1960,
        "score": 3.8244388103485107,
        "score_kind": "bm25"
      },
      {
        "chunk_id": 1946,
        "score": 3.755237102508545,
        "score_kind": "bm25"
      },
      {
        "chunk_id": 1961,
        "score": 3.6993556022644043,
        "score_kind": "bm25"
      },
      {
        "chunk_id": 1954,
        "score": 3.5821950435638428,
        "score_kind": "bm25"
      },
      {
        "chunk_id": 1964,
        "score": 3.5821950435638428,
        "score_kind": "bm25"
      },
      {
        "chunk_id": 1962,
        "score": 3.5633859634399414,
        "score_kind": "bm25"
      },
      {
        "chunk_id": 1974,
        "score": 3.51131534576416,
        "score_kind": "bm25"
      },
      {
        "chunk_id": 1963,
        "score": 3.5081260204315186,
        "score_kind": "bm25"
      },
      {
        "chunk_id": 1955,
        "score": 3.3193798065185547,
        "score_kind": "bm25"
      },
      {
        "chunk_id": 1953,
        "score": 3.3032233715057373,
        "score_kind": "bm25"
      },
      {
        "chunk_id": 1978,
        "score": 3.088531494140625,
        "score_kind": "bm25"
      },
      {
        "chunk_id": 1972,
        "score": 1.4414697885513306,
        "score_kind": "bm25"
      },
      {
        "chunk_id": 1973,
        "score": 1.2937390804290771,
        "score_kind": "bm25"
      },
      {
        "chunk_id": 1969,
        "score": 1.215309500694275,
        "score_kind": "bm25"
      },
      {
        "chunk_id": 1980,
        "score": 1.1236776113510132,
        "score_kind": "bm25"
      },
      {
        "chunk_id": 1939,
        "score": 1.0660427808761597,
        "score_kind": "bm25"
      },
      {
        "chunk_id": 1941,
        "score": 1.0558345317840576,
        "score_kind": "bm25"
      },
      {
        "chunk_id": 1952,
        "score": 1.0359933376312256,
        "score_kind": "bm25"
      },
      {
        "chunk_id": 1943,
        "score": 1.0168840885162354,
        "score_kind": "bm25"
      },
      {
        "chunk_id": 1949,
        "score": 0.998467206954956,
        "score_kind": "bm25"
      },
      {
        "chunk_id": 1967,
        "score": 0.998467206954956,
        "score_kind": "bm25"
      },
      {
        "chunk_id": 1965,
        "score": 0.9895066618919373,
        "score_kind": "bm25"
      },
      {
        "chunk_id": 1950,
        "score": 0.9807054996490479,
        "score_kind": "bm25"
      },
      {
        "chunk_id": 1935,
        "score": 0.9720594882965088,
        "score_kind": "bm25"
      },
      {
        "chunk_id": 1971,
        "score": 0.9470126032829285,
        "score_kind": "bm25"
      },
      {
        "chunk_id": 1976,
        "score": 0.8389298319816589,
        "score_kind": "bm25"
      },
      {
        "chunk_id": 1979,
        "score": 0.7139831781387329,
        "score_kind": "bm25"
      }
    ],
    "final_ranking": [
      {
        "chunk_id": 1958,
        "score": 11.307323455810547,
        "score_kind": "bm25"
      },
      {
        "chunk_id": 1956,
        "score": 11.281126022338867,
        "score_kind": "bm25"
      },
      {
        "chunk_id": 1977,
        "score": 7.956859111785889,
        "score_kind": "bm25"
      },
      {
        "chunk_id": 1957,
        "score": 6.014775276184082,
        "score_kind": "bm25"
      },
      {
        "chunk_id": 1968,
        "score": 5.385351181030273,
        "score_kind": "bm25"
      },
      {
        "chunk_id": 1948,
        "score": 4.653332710266113,
        "score_kind": "bm25"
      },
      {
        "chunk_id": 1959,
        "score": 3.8244388103485107,
        "score_kind": "bm25"
      },
      {
        "chunk_id": 1960,
        "score": 3.8244388103485107,
        "score_kind": "bm25"
      },
      {
        "chunk_id": 1946,
        "score": 3.755237102508545,
        "score_kind": "bm25"
      },
      {
        "chunk_id": 1961,
        "score": 3.6993556022644043,
        "score_kind": "bm25"
      }
    ]
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
  "refused": false,
  "status": "completed",
  "stage": "complete",
  "query": "MH-W20 和 MH-W60 换滤芯的周期一样吗",
  "query_plan": {
    "standard": "MH-W20 和 MH-W60 换滤芯的周期一样吗",
    "expansions": []
  },
  "mapped_groups": [
    {
      "group_id": "g1",
      "alternatives": [
        [
          1956
        ]
      ]
    },
    {
      "group_id": "g2",
      "alternatives": [
        [
          1958
        ]
      ]
    }
  ],
  "candidate_ids": [
    1956,
    1958,
    1957,
    1977,
    1954,
    1961,
    1960,
    1955,
    1962,
    1953,
    1959,
    1963,
    1968,
    1964,
    1948,
    1967,
    1980,
    1965,
    1946,
    1952,
    1974,
    1935,
    1941,
    1973,
    1972,
    1978,
    1949,
    1979,
    1971,
    1969,
    1950,
    1939,
    1943,
    1976,
    1936,
    1970,
    1931,
    1932,
    1940,
    1934,
    1937,
    1933,
    1938,
    1951,
    1945,
    1966,
    1975,
    1944,
    1947,
    1942
  ],
  "final_ids": [
    1956,
    1958,
    1957,
    1977,
    1954,
    1961,
    1960,
    1955,
    1962,
    1953
  ],
  "prompt_citations": [
    {
      "n": 1,
      "chunk_id": "1956",
      "section_path": "商品规格手册/自动饮水机(型号 MH-W20)",
      "question": "自动饮水机(型号 MH-W20)",
      "answer": "- 型号:MH-W20\n- 水箱容量:2L\n- 过滤:三重过滤棉,建议每 2 周更换一次滤芯\n- 核心功能:静音水泵、缺水断电保护、水位窗口\n- 清洗:水泵可拆卸,建议每周清洗一次"
    },
    {
      "n": 3,
      "chunk_id": "1957",
      "section_path": "商品规格手册/自动饮水机 Plus(型号 MH-W40)",
      "question": "自动饮水机 Plus(型号 MH-W40)",
      "answer": "- 型号:MH-W40\n- 水箱容量:4L\n- 过滤:五重过滤棉 + 椰壳活性炭,建议每 3 周更换一次滤芯\n- 核心功能:UV 紫外杀菌、静音变频水泵、缺水断电保护\n- 清洗:整机可拆分水洗,建议每周清洗一次"
    },
    {
      "n": 5,
      "chunk_id": "1954",
      "section_path": "商品规格手册/智能猫砂盆 Lite(型号 MH-LP50)",
      "question": "智能猫砂盆 Lite(型号 MH-LP50)",
      "answer": "- 型号:MH-LP50\n- 适用猫咪体重:1.5kg 至 6kg\n- 猫砂容量:6L\n- 核心功能:自动感应清理、物理除臭盖板;不含 App 联网功能\n- 与 Pro 差异:Lite 无 App 远程监控与健康记录,价格更低,适合单猫家庭"
    },
    {
      "n": 7,
      "chunk_id": "1960",
      "section_path": "商品规格手册/恒温加热垫(型号 MH-HP12)",
      "question": "恒温加热垫(型号 MH-HP12)",
      "answer": "- 型号:MH-HP12\n- 尺寸:40cm × 30cm\n- 温控:恒温 38℃,内置过热保护,连续通电不超过 12 小时为宜\n- 防护:防水防抓咬电线套管\n- 适用:幼猫、老年猫及冬季保暖"
    },
    {
      "n": 9,
      "chunk_id": "1962",
      "section_path": "商品规格手册/自动喂食器 基础版(型号 MH-FD10)",
      "question": "自动喂食器 基础版(型号 MH-FD10)",
      "answer": "- 型号:MH-FD10\n- 粮桶容量:4L\n- 核心功能:定时定量投喂,每日最多 6 餐,语音呼唤进食\n- 供电:市电供电 + 4 节 5 号电池断电应急\n- 说明:基础版不含摄像头与 App 远程投喂"
    },
    {
      "n": 10,
      "chunk_id": "1953",
      "section_path": "商品规格手册/智能猫砂盆 Pro(型号 MH-LP100)",
      "question": "智能猫砂盆 Pro(型号 MH-LP100)",
      "answer": "- 型号:MH-LP100\n- 适用猫咪体重:1.5kg 至 8kg\n- 猫砂容量:9L,废砂盒容量约 7 天(单猫)\n- 核心功能:自动感应清理、活性炭除臭、App 远程监控与健康记录\n- 供电:220V 市电,断电后配置自动保存\n- 清理提示:废砂盒满时 App 推送提醒,建议每 5 至 7 天倾倒一次"
    },
    {
      "n": 8,
      "chunk_id": "1955",
      "section_path": "商品规格手册/智能猫砂盆 Max(型号 MH-LP200)",
      "question": "智能猫砂盆 Max(型号 MH-LP200)",
      "answer": "- 型号:MH-LP200\n- 适用猫咪体重:2kg 至 12kg,适合大型猫与多猫家庭\n- 猫砂容量:12L,废砂盒容量约 10 天(单猫)\n- 核心功能:超大滚筒、双重称重防夹、活性炭除臭、App 多猫健康档案\n- 供电:220V 市电\n- 清理提示:多猫家庭建议每 3 至 5 天倾倒一次废砂盒"
    },
    {
      "n": 6,
      "chunk_id": "1961",
      "section_path": "商品规格手册/大号三档加热垫(型号 MH-HP20)",
      "question": "大号三档加热垫(型号 MH-HP20)",
      "answer": "- 型号:MH-HP20\n- 尺寸:60cm × 45cm\n- 温控:三档可调 30℃ / 38℃ / 45℃,内置过热保护与定时关机\n- 防护:防水防抓咬电线套管,表面绒布可拆洗\n- 适用:大型猫、多猫窝及冬季保暖"
    },
    {
      "n": 4,
      "chunk_id": "1977",
      "section_path": "积分规则/积分怎么用",
      "question": "积分怎么用",
      "answer": "积分可在结算时抵扣商品金额，100 积分抵 1 元现金，单笔订单最多抵 30 元，不用于抵扣偏远地区附加运费，也不支持直接提现。\n\n2000 积分可兑换自动饮水机滤芯 3 片，该兑换套装适用于 MH-W40，普通配送地区包邮；偏远地区附加配送费仍需按页面规则确认。MH-W40 的滤芯更换周期以商品规格手册为准。\n\n800 积分可兑换猫零食小样，普通配送地区另收 6 元运费；该兑换不直接套用普通购物订单的满 99 元包邮规则。兑换商品、可用库存及偏远地区配送规则以兑换页面标注为准。"
    },
    {
      "n": 2,
      "chunk_id": "1958",
      "section_path": "商品规格手册/自动饮水机 Pro 不锈钢(型号 MH-W60)",
      "question": "自动饮水机 Pro 不锈钢(型号 MH-W60)",
      "answer": "- 型号:MH-W60\n- 水箱容量:6L,304 不锈钢表面盘\n- 过滤:双滤芯并联,建议每 4 周更换一次滤芯\n- 核心功能:双泵冗余、无线水位提醒推送 App、缺水断电保护\n- 清洗:不锈钢面盘可高温消毒,建议每周清洗一次"
    }
  ],
  "decision": {
    "useful": true,
    "reason": "两款滤芯周期均有证据：W20每2周，W60每4周",
    "response_kind": "knowledge",
    "source": null
  },
  "answer": "您好，两款换滤芯的周期不一样：\n\n- **MH-W20**：三重过滤棉，建议每 **2 周**更换一次滤芯 [1]\n- **MH-W60**：双滤芯并联，建议每 **4 周**更换一次滤芯 [2]\n\n如有其他问题，欢迎随时咨询~",
  "point_verdicts": [
    {
      "point_id": "p1",
      "covered": true,
      "reason": "回答明确说明MH-W20建议每2周更换一次滤芯，与要点一致。"
    },
    {
      "point_id": "p2",
      "covered": true,
      "reason": "回答说明MH-W60建议每4周更换且开头明确两款周期不一样，覆盖要点及比较。"
    }
  ],
  "claim_verdicts": [
    {
      "claim": "MH-W20建议每2周更换一次滤芯",
      "supported": true,
      "reason": "证据[1]为MH-W20规格，写明三重过滤棉建议每2周更换一次滤芯。"
    },
    {
      "claim": "MH-W60建议每4周更换一次滤芯",
      "supported": true,
      "reason": "证据[2]为MH-W60规格，写明双滤芯并联建议每4周更换一次滤芯。"
    },
    {
      "claim": "MH-W20与MH-W60换滤芯周期不一样",
      "supported": true,
      "reason": "由证据[1]的每2周与证据[2]的每4周可推出两者周期不同。"
    },
    {
      "claim": "MH-W20为三重过滤棉",
      "supported": true,
      "reason": "证据[1]过滤项写明三重过滤棉。"
    },
    {
      "claim": "MH-W60为双滤芯并联",
      "supported": true,
      "reason": "证据[2]过滤项写明双滤芯并联。"
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
  "elapsed_ms": 9454.351000022143,
  "judge_snapshot": {
    "prompt_version": "joint-generation-v2.1",
    "finish_reason": "stop"
  },
  "rewrite": {
    "policy_version": "original-query-on-invalid-v1",
    "status": "success",
    "error": null
  },
  "audit": {
    "audit_version": 1,
    "source_map_id": "af6590ab401319d942bddff0b30213a4cd888b8cf115ebd5cdec3adb87687e55",
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
    "candidate_ranking": [
      {
        "chunk_id": 1956,
        "score": 0.032522473484277725,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1958,
        "score": 0.03226646035909653,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1957,
        "score": 0.0317540317773819,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1977,
        "score": 0.0314980149269104,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1954,
        "score": 0.029236022382974625,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1961,
        "score": 0.028991596773266792,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1960,
        "score": 0.028594771400094032,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1955,
        "score": 0.02854251116514206,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1962,
        "score": 0.02819138392806053,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1953,
        "score": 0.027912385761737823,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1959,
        "score": 0.027745885774493217,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1963,
        "score": 0.027619048953056335,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1968,
        "score": 0.026748251169919968,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1964,
        "score": 0.02654711715877056,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1948,
        "score": 0.02546079456806183,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1967,
        "score": 0.024877149611711502,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1980,
        "score": 0.024243313819169998,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1965,
        "score": 0.023735955357551575,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1946,
        "score": 0.023667065426707268,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1952,
        "score": 0.0235294122248888,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1974,
        "score": 0.023513514548540115,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1935,
        "score": 0.02318413183093071,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1941,
        "score": 0.023140717297792435,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1973,
        "score": 0.023138297721743584,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1972,
        "score": 0.02275923825800419,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1978,
        "score": 0.022435897961258888,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1949,
        "score": 0.022363819181919098,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1979,
        "score": 0.0222662054002285,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1971,
        "score": 0.0218585766851902,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1969,
        "score": 0.02177964150905609,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1950,
        "score": 0.0213151928037405,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1939,
        "score": 0.021307451650500298,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1943,
        "score": 0.021151717752218246,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1976,
        "score": 0.01984359696507454,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1936,
        "score": 0.014084506779909134,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1970,
        "score": 0.013698630034923553,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1931,
        "score": 0.013333333656191826,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1932,
        "score": 0.01315789483487606,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1940,
        "score": 0.012987012974917889,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1934,
        "score": 0.012345679104328156,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1937,
        "score": 0.011904762126505375,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1933,
        "score": 0.01149425283074379,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1938,
        "score": 0.011111111380159855,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1951,
        "score": 0.01075268816202879,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1945,
        "score": 0.010526316240429878,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1966,
        "score": 0.010416666977107525,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1975,
        "score": 0.009900989942252636,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1944,
        "score": 0.009803921915590763,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1947,
        "score": 0.009708737954497337,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1942,
        "score": 0.009345794096589088,
        "score_kind": "rrf"
      }
    ],
    "final_ranking": [
      {
        "chunk_id": 1956,
        "score": 0.032522473484277725,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1958,
        "score": 0.03226646035909653,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1957,
        "score": 0.0317540317773819,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1977,
        "score": 0.0314980149269104,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1954,
        "score": 0.029236022382974625,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1961,
        "score": 0.028991596773266792,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1960,
        "score": 0.028594771400094032,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1955,
        "score": 0.02854251116514206,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1962,
        "score": 0.02819138392806053,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1953,
        "score": 0.027912385761737823,
        "score_kind": "rrf"
      }
    ]
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
  "refused": false,
  "status": "completed",
  "stage": "complete",
  "query": "MH-W20 和 MH-W60 换滤芯的周期一样吗",
  "query_plan": {
    "standard": "MH-W20 和 MH-W60 换滤芯的周期一样吗",
    "expansions": []
  },
  "mapped_groups": [
    {
      "group_id": "g1",
      "alternatives": [
        [
          1956
        ]
      ]
    },
    {
      "group_id": "g2",
      "alternatives": [
        [
          1958
        ]
      ]
    }
  ],
  "candidate_ids": [
    1956,
    1958,
    1957,
    1977,
    1954,
    1961,
    1960,
    1955,
    1962,
    1953,
    1959,
    1963,
    1968,
    1964,
    1948,
    1967,
    1980,
    1965,
    1946,
    1952,
    1974,
    1935,
    1941,
    1973,
    1972,
    1978,
    1949,
    1979,
    1971,
    1969,
    1950,
    1939,
    1943,
    1976,
    1936,
    1970,
    1931,
    1932,
    1940,
    1934,
    1937,
    1933,
    1938,
    1951,
    1945,
    1966,
    1975,
    1944,
    1947,
    1942
  ],
  "final_ids": [
    1956,
    1958,
    1977,
    1957,
    1961,
    1970,
    1932,
    1967,
    1936,
    1934
  ],
  "prompt_citations": [
    {
      "n": 1,
      "chunk_id": "1956",
      "section_path": "商品规格手册/自动饮水机(型号 MH-W20)",
      "question": "自动饮水机(型号 MH-W20)",
      "answer": "- 型号:MH-W20\n- 水箱容量:2L\n- 过滤:三重过滤棉,建议每 2 周更换一次滤芯\n- 核心功能:静音水泵、缺水断电保护、水位窗口\n- 清洗:水泵可拆卸,建议每周清洗一次"
    },
    {
      "n": 3,
      "chunk_id": "1977",
      "section_path": "积分规则/积分怎么用",
      "question": "积分怎么用",
      "answer": "积分可在结算时抵扣商品金额，100 积分抵 1 元现金，单笔订单最多抵 30 元，不用于抵扣偏远地区附加运费，也不支持直接提现。\n\n2000 积分可兑换自动饮水机滤芯 3 片，该兑换套装适用于 MH-W40，普通配送地区包邮；偏远地区附加配送费仍需按页面规则确认。MH-W40 的滤芯更换周期以商品规格手册为准。\n\n800 积分可兑换猫零食小样，普通配送地区另收 6 元运费；该兑换不直接套用普通购物订单的满 99 元包邮规则。兑换商品、可用库存及偏远地区配送规则以兑换页面标注为准。"
    },
    {
      "n": 5,
      "chunk_id": "1961",
      "section_path": "商品规格手册/大号三档加热垫(型号 MH-HP20)",
      "question": "大号三档加热垫(型号 MH-HP20)",
      "answer": "- 型号:MH-HP20\n- 尺寸:60cm × 45cm\n- 温控:三档可调 30℃ / 38℃ / 45℃,内置过热保护与定时关机\n- 防护:防水防抓咬电线套管,表面绒布可拆洗\n- 适用:大型猫、多猫窝及冬季保暖"
    },
    {
      "n": 7,
      "chunk_id": "1932",
      "section_path": "售后手册/保修说明",
      "question": "保修说明",
      "answer": "电子类商品保修 12 个月,自签收日起算;人为损坏不在保修范围。"
    },
    {
      "n": 9,
      "chunk_id": "1936",
      "section_path": "售后手册/维修寄修流程",
      "question": "维修寄修流程",
      "answer": "保修期内设备故障,联系客服登记后按指引将设备寄回指定维修点,核验后免费维修并寄回;超保或人为损坏维修可能收取工本费,费用会提前告知。"
    },
    {
      "n": 10,
      "chunk_id": "1934",
      "section_path": "售后手册/常见故障自查",
      "question": "常见故障自查",
      "answer": "- 饮水机不出水:检查水位是否低于最低线、水泵是否卡阻,断电清洗水泵后重试。\n- 猫砂盆报错:清空废砂盒并检查滚筒是否卡砂,重启设备;仍报错联系售后。\n- 喂食器卡粮:检查粮食颗粒直径是否超 12mm、粮桶是否受潮结块,清理出粮口后重试。\n- 摄像头离线:确认 Wi-Fi 为 2.4G 频段、信号良好,重启设备或在 App 内重新配网。"
    },
    {
      "n": 8,
      "chunk_id": "1967",
      "section_path": "退货退款政策/换货政策/换货条件",
      "question": "换货条件",
      "answer": "收到商品 7 天内,商品完好且配件齐全的,可申请一次同款换货;不同型号或颜色需先退货再重新下单。"
    },
    {
      "n": 6,
      "chunk_id": "1970",
      "section_path": "退货退款政策/质量问题与保修",
      "question": "质量问题与保修",
      "answer": "电子类商品自签收起保修 12 个月,保修期内非人为损坏可申请免费维修或换货;人为损坏、超保商品维修可能收取工本费。"
    },
    {
      "n": 4,
      "chunk_id": "1957",
      "section_path": "商品规格手册/自动饮水机 Plus(型号 MH-W40)",
      "question": "自动饮水机 Plus(型号 MH-W40)",
      "answer": "- 型号:MH-W40\n- 水箱容量:4L\n- 过滤:五重过滤棉 + 椰壳活性炭,建议每 3 周更换一次滤芯\n- 核心功能:UV 紫外杀菌、静音变频水泵、缺水断电保护\n- 清洗:整机可拆分水洗,建议每周清洗一次"
    },
    {
      "n": 2,
      "chunk_id": "1958",
      "section_path": "商品规格手册/自动饮水机 Pro 不锈钢(型号 MH-W60)",
      "question": "自动饮水机 Pro 不锈钢(型号 MH-W60)",
      "answer": "- 型号:MH-W60\n- 水箱容量:6L,304 不锈钢表面盘\n- 过滤:双滤芯并联,建议每 4 周更换一次滤芯\n- 核心功能:双泵冗余、无线水位提醒推送 App、缺水断电保护\n- 清洗:不锈钢面盘可高温消毒,建议每周清洗一次"
    }
  ],
  "decision": {
    "useful": true,
    "reason": "两个型号滤芯周期均有证据：W20为2周，W60为4周",
    "response_kind": "knowledge",
    "source": null
  },
  "answer": "您好！两款型号的滤芯更换周期不一样：\n\n- **MH-W20**：三重过滤棉，建议每 **2 周**更换一次滤芯[1]\n- **MH-W60**：双滤芯并联，建议每 **4 周**更换一次滤芯[2]\n\n请问还有其他可以帮您的吗？",
  "point_verdicts": [
    {
      "point_id": "p1",
      "covered": true,
      "reason": "回答明确说明 MH-W20 建议每 2 周更换一次滤芯，覆盖该要点及其适用条件"
    },
    {
      "point_id": "p2",
      "covered": true,
      "reason": "回答说明 MH-W60 建议每 4 周更换并明确两款周期不一样，覆盖该要点"
    }
  ],
  "claim_verdicts": [
    {
      "claim": "MH-W20 采用三重过滤棉，建议每 2 周更换一次滤芯",
      "supported": true,
      "reason": "证据[1] MH-W20 规格明确：三重过滤棉，建议每 2 周更换一次滤芯"
    },
    {
      "claim": "MH-W60 采用双滤芯并联，建议每 4 周更换一次滤芯",
      "supported": true,
      "reason": "证据[2] MH-W60 规格明确：双滤芯并联，建议每 4 周更换一次滤芯"
    },
    {
      "claim": "MH-W20 和 MH-W60 的滤芯更换周期不一样",
      "supported": true,
      "reason": "证据[1]为每2周、证据[2]为每4周，周期确不相同，由两条证据共同支持"
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
  "elapsed_ms": 11972.943099914119,
  "judge_snapshot": {
    "prompt_version": "joint-generation-v2.1",
    "finish_reason": "stop"
  },
  "rewrite": {
    "policy_version": "original-query-on-invalid-v1",
    "status": "success",
    "error": null
  },
  "audit": {
    "audit_version": 1,
    "source_map_id": "af6590ab401319d942bddff0b30213a4cd888b8cf115ebd5cdec3adb87687e55",
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
    "candidate_ranking": [
      {
        "chunk_id": 1956,
        "score": 0.032522473484277725,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1958,
        "score": 0.03226646035909653,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1957,
        "score": 0.0317540317773819,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1977,
        "score": 0.0314980149269104,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1954,
        "score": 0.029236022382974625,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1961,
        "score": 0.028991596773266792,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1960,
        "score": 0.028594771400094032,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1955,
        "score": 0.02854251116514206,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1962,
        "score": 0.02819138392806053,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1953,
        "score": 0.027912385761737823,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1959,
        "score": 0.027745885774493217,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1963,
        "score": 0.027619048953056335,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1968,
        "score": 0.026748251169919968,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1964,
        "score": 0.02654711715877056,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1948,
        "score": 0.02546079456806183,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1967,
        "score": 0.024877149611711502,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1980,
        "score": 0.024243313819169998,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1965,
        "score": 0.023735955357551575,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1946,
        "score": 0.023667065426707268,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1952,
        "score": 0.0235294122248888,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1974,
        "score": 0.023513514548540115,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1935,
        "score": 0.02318413183093071,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1941,
        "score": 0.023140717297792435,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1973,
        "score": 0.023138297721743584,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1972,
        "score": 0.02275923825800419,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1978,
        "score": 0.022435897961258888,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1949,
        "score": 0.022363819181919098,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1979,
        "score": 0.0222662054002285,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1971,
        "score": 0.0218585766851902,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1969,
        "score": 0.02177964150905609,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1950,
        "score": 0.0213151928037405,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1939,
        "score": 0.021307451650500298,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1943,
        "score": 0.021151717752218246,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1976,
        "score": 0.01984359696507454,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1936,
        "score": 0.014084506779909134,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1970,
        "score": 0.013698630034923553,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1931,
        "score": 0.013333333656191826,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1932,
        "score": 0.01315789483487606,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1940,
        "score": 0.012987012974917889,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1934,
        "score": 0.012345679104328156,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1937,
        "score": 0.011904762126505375,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1933,
        "score": 0.01149425283074379,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1938,
        "score": 0.011111111380159855,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1951,
        "score": 0.01075268816202879,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1945,
        "score": 0.010526316240429878,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1966,
        "score": 0.010416666977107525,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1975,
        "score": 0.009900989942252636,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1944,
        "score": 0.009803921915590763,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1947,
        "score": 0.009708737954497337,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1942,
        "score": 0.009345794096589088,
        "score_kind": "rrf"
      }
    ],
    "final_ranking": [
      {
        "chunk_id": 1956,
        "score": 0.9685534834861755,
        "score_kind": "rerank"
      },
      {
        "chunk_id": 1958,
        "score": 0.8904611468315125,
        "score_kind": "rerank"
      },
      {
        "chunk_id": 1977,
        "score": 0.1640932559967041,
        "score_kind": "rerank"
      },
      {
        "chunk_id": 1957,
        "score": 0.1134628877043724,
        "score_kind": "rerank"
      },
      {
        "chunk_id": 1961,
        "score": 0.004922160413116217,
        "score_kind": "rerank"
      },
      {
        "chunk_id": 1970,
        "score": 0.0016978556523099542,
        "score_kind": "rerank"
      },
      {
        "chunk_id": 1932,
        "score": 0.0013380321906879544,
        "score_kind": "rerank"
      },
      {
        "chunk_id": 1967,
        "score": 0.001235267729498446,
        "score_kind": "rerank"
      },
      {
        "chunk_id": 1936,
        "score": 0.001129837823100388,
        "score_kind": "rerank"
      },
      {
        "chunk_id": 1934,
        "score": 0.0009722719551064074,
        "score_kind": "rerank"
      }
    ]
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
          1942
        ]
      ]
    }
  ],
  "candidate_ids": [
    1942,
    1977,
    1951,
    1968,
    1976,
    1969,
    1947,
    1936,
    1971,
    1945,
    1943,
    1974,
    1937,
    1970,
    1978,
    1950,
    1975,
    1931,
    1941,
    1979,
    1973,
    1944,
    1940,
    1967,
    1953,
    1965,
    1954,
    1932,
    1948,
    1946,
    1939,
    1958,
    1938,
    1955,
    1957,
    1966,
    1962,
    1935,
    1949,
    1956,
    1963,
    1961,
    1960,
    1933,
    1959,
    1972,
    1934,
    1952,
    1964,
    1980
  ],
  "final_ids": [
    1942,
    1977,
    1951,
    1968,
    1976,
    1969,
    1947,
    1936,
    1971,
    1945
  ],
  "prompt_citations": [
    {
      "n": 1,
      "chunk_id": "1942",
      "section_path": "商品与购物 FAQ/运费怎么算",
      "question": "运费怎么算",
      "answer": "单笔订单满 99 元包邮,未满收取 10 元运费,偏远地区运费另计。邮费即运费,按此规则收取。"
    },
    {
      "n": 3,
      "chunk_id": "1951",
      "section_path": "商品与购物 FAQ/会员运费权益",
      "question": "会员运费权益",
      "answer": "金卡会员每月享 3 次免运费权益,银卡会员享 1 次;权益不与偏远地区附加运费冲抵,当月未用完不结转。"
    },
    {
      "n": 5,
      "chunk_id": "1976",
      "section_path": "积分规则/积分怎么攒",
      "question": "积分怎么攒",
      "answer": "已完成订单每实际支付 1 元商品金额累计 1 积分，不计配送费；退款后按对应商品金额同步扣回积分。活动期间的双倍积分属于额外积分奖励，不计入会员等级升级；会员等级仍按有效累计消费金额计算。"
    },
    {
      "n": 7,
      "chunk_id": "1947",
      "section_path": "商品与购物 FAQ/配送范围与偏远地区",
      "question": "配送范围与偏远地区",
      "answer": "全国大部分地区支持配送,新疆、西藏、内蒙古等偏远地区运费另计且时效顺延;港澳台及海外暂不支持自营配送。"
    },
    {
      "n": 9,
      "chunk_id": "1971",
      "section_path": "退货退款政策/运输破损处理",
      "question": "运输破损处理",
      "answer": "商品运输途中破损的,请在签收后 48 小时内联系客服并提供开箱视频与照片,核实后可免费补发或退款,相关运费由平台承担。"
    },
    {
      "n": 10,
      "chunk_id": "1945",
      "section_path": "商品与购物 FAQ/会员等级与积分规则",
      "question": "会员等级与积分规则",
      "answer": "会员分为普通、银卡、金卡三档,按累计消费自动升级。每消费 1 元得 1 积分,积分可在结算时抵扣,100 积分抵 1 元。"
    },
    {
      "n": 8,
      "chunk_id": "1936",
      "section_path": "售后手册/维修寄修流程",
      "question": "维修寄修流程",
      "answer": "保修期内设备故障,联系客服登记后按指引将设备寄回指定维修点,核验后免费维修并寄回;超保或人为损坏维修可能收取工本费,费用会提前告知。"
    },
    {
      "n": 6,
      "chunk_id": "1969",
      "section_path": "退货退款政策/退换货运费承担",
      "question": "退换货运费承担",
      "answer": "无理由退货的退回运费由买家承担;因商品质量问题、发错货、少发漏发导致的退换货,运费由平台承担。运费承担以平台售后规则最终判定为准。"
    },
    {
      "n": 4,
      "chunk_id": "1968",
      "section_path": "退货退款政策/换货政策/换货运费",
      "question": "换货运费",
      "answer": "非质量问题的换货,往返运费由买家承担;因质量问题或发错货的换货,往返运费由平台承担。"
    },
    {
      "n": 2,
      "chunk_id": "1977",
      "section_path": "积分规则/积分怎么用",
      "question": "积分怎么用",
      "answer": "积分可在结算时抵扣商品金额，100 积分抵 1 元现金，单笔订单最多抵 30 元，不用于抵扣偏远地区附加运费，也不支持直接提现。\n\n2000 积分可兑换自动饮水机滤芯 3 片，该兑换套装适用于 MH-W40，普通配送地区包邮；偏远地区附加配送费仍需按页面规则确认。MH-W40 的滤芯更换周期以商品规格手册为准。\n\n800 积分可兑换猫零食小样，普通配送地区另收 6 元运费；该兑换不直接套用普通购物订单的满 99 元包邮规则。兑换商品、可用库存及偏远地区配送规则以兑换页面标注为准。"
    }
  ],
  "decision": {
    "useful": true,
    "reason": "有运费规则证据：满99包邮未满10元，偏远另计",
    "response_kind": "knowledge",
    "source": null
  },
  "answer": "您好！根据商家政策：单笔订单满 99 元包邮，未满 99 元收取 10 元运费，偏远地区（如新疆、西藏、内蒙古等）运费另计 [1]。\n\n如果您是会员，金卡每月有 3 次免运费权益，银卡有 1 次（偏远地区附加运费不可冲抵）[3]。\n\n请问您是想查询购物订单的运费，还是退换货的运费呢？如需更具体的说明，欢迎告诉我您的订单号或具体情况～",
  "point_verdicts": [
    {
      "point_id": "p1",
      "covered": true,
      "reason": "回答明确说明满99元包邮、未满收10元，符合普通订单基础运费条件"
    },
    {
      "point_id": "p2",
      "covered": true,
      "reason": "回答说明偏远地区（如新疆、西藏、内蒙古等）运费另计，符合条件"
    }
  ],
  "claim_verdicts": [
    {
      "claim": "单笔订单满99元包邮，未满99元收取10元运费",
      "supported": true,
      "reason": "证据[1]明确写明单笔订单满99元包邮，未满收取10元运费"
    },
    {
      "claim": "偏远地区（如新疆、西藏、内蒙古等）运费另计",
      "supported": true,
      "reason": "证据[1]说明偏远地区运费另计，证据[7]列明新疆、西藏、内蒙古等属偏远地区且运费另计"
    },
    {
      "claim": "金卡会员每月有3次免运费权益，银卡会员有1次",
      "supported": true,
      "reason": "证据[3]明确金卡每月3次、银卡1次免运费权益"
    },
    {
      "claim": "会员免运费权益不可冲抵偏远地区附加运费",
      "supported": true,
      "reason": "证据[3]写明权益不与偏远地区附加运费冲抵"
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
  "elapsed_ms": 10557.157799834386,
  "judge_snapshot": {
    "prompt_version": "joint-generation-v2.1",
    "finish_reason": "stop"
  },
  "rewrite": {
    "policy_version": "original-query-on-invalid-v1",
    "status": "success",
    "error": null
  },
  "audit": {
    "audit_version": 1,
    "source_map_id": "af6590ab401319d942bddff0b30213a4cd888b8cf115ebd5cdec3adb87687e55",
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
        "chunk_id": 1942,
        "score": 0.7382994890213013,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1977,
        "score": 0.5855824947357178,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1951,
        "score": 0.5743529200553894,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1968,
        "score": 0.5729867815971375,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1976,
        "score": 0.565174400806427,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1969,
        "score": 0.5586050152778625,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1947,
        "score": 0.5497187972068787,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1936,
        "score": 0.5388888716697693,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1971,
        "score": 0.5263242721557617,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1945,
        "score": 0.526046097278595,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1943,
        "score": 0.5228790044784546,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1974,
        "score": 0.5203941464424133,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1937,
        "score": 0.5191847085952759,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1970,
        "score": 0.509336531162262,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1978,
        "score": 0.4977514445781708,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1950,
        "score": 0.4867149889469147,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1975,
        "score": 0.48516929149627686,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1931,
        "score": 0.48189276456832886,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1941,
        "score": 0.48042619228363037,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1979,
        "score": 0.47809720039367676,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1973,
        "score": 0.47534236311912537,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1944,
        "score": 0.4640308618545532,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1940,
        "score": 0.4589749574661255,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1967,
        "score": 0.44827958941459656,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1953,
        "score": 0.44386354088783264,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1965,
        "score": 0.4432941973209381,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1954,
        "score": 0.43861809372901917,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1932,
        "score": 0.43656039237976074,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1948,
        "score": 0.4322296977043152,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1946,
        "score": 0.4301239252090454,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1939,
        "score": 0.42482614517211914,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1958,
        "score": 0.42353710532188416,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1938,
        "score": 0.4230842590332031,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1955,
        "score": 0.42296504974365234,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1957,
        "score": 0.42240235209465027,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1966,
        "score": 0.41644591093063354,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1962,
        "score": 0.41639894247055054,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1935,
        "score": 0.4151606261730194,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1949,
        "score": 0.4088750183582306,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1956,
        "score": 0.40778520703315735,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1963,
        "score": 0.40576887130737305,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1961,
        "score": 0.40419161319732666,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1960,
        "score": 0.3984825015068054,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1933,
        "score": 0.3978709578514099,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1959,
        "score": 0.39533427357673645,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1972,
        "score": 0.3898211121559143,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1934,
        "score": 0.38612908124923706,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1952,
        "score": 0.36874842643737793,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1964,
        "score": 0.3483802080154419,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1980,
        "score": 0.33238232135772705,
        "score_kind": "cosine"
      }
    ],
    "final_ranking": [
      {
        "chunk_id": 1942,
        "score": 0.7382994890213013,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1977,
        "score": 0.5855824947357178,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1951,
        "score": 0.5743529200553894,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1968,
        "score": 0.5729867815971375,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1976,
        "score": 0.565174400806427,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1969,
        "score": 0.5586050152778625,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1947,
        "score": 0.5497187972068787,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1936,
        "score": 0.5388888716697693,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1971,
        "score": 0.5263242721557617,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1945,
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
          1942
        ]
      ]
    }
  ],
  "candidate_ids": [
    1942
  ],
  "final_ids": [
    1942
  ],
  "prompt_citations": [
    {
      "n": 1,
      "chunk_id": "1942",
      "section_path": "商品与购物 FAQ/运费怎么算",
      "question": "运费怎么算",
      "answer": "单笔订单满 99 元包邮,未满收取 10 元运费,偏远地区运费另计。邮费即运费,按此规则收取。"
    }
  ],
  "decision": {
    "useful": true,
    "reason": "运费规则证据覆盖邮费标准",
    "response_kind": "knowledge",
    "source": null
  },
  "answer": "您好！根据运费规则[1]：单笔订单满 99 元包邮，未满 99 元收取 10 元运费，偏远地区运费另计[1]。\n\n如您需要了解具体某笔订单的邮费，请提供订单号，我帮您查询～",
  "point_verdicts": [
    {
      "point_id": "p1",
      "covered": true,
      "reason": "回答明确说明满99元包邮、未满收10元运费，属于普通订单基础运费，条件保留完整"
    },
    {
      "point_id": "p2",
      "covered": true,
      "reason": "回答提到偏远地区运费另计，覆盖该要点及其适用条件"
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
  "elapsed_ms": 9095.753399888054,
  "judge_snapshot": {
    "prompt_version": "joint-generation-v2.1",
    "finish_reason": "stop"
  },
  "rewrite": {
    "policy_version": "original-query-on-invalid-v1",
    "status": "success",
    "error": null
  },
  "audit": {
    "audit_version": 1,
    "source_map_id": "af6590ab401319d942bddff0b30213a4cd888b8cf115ebd5cdec3adb87687e55",
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
        "chunk_id": 1942,
        "score": 4.1900835037231445,
        "score_kind": "bm25"
      }
    ],
    "final_ranking": [
      {
        "chunk_id": 1942,
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
          1942
        ]
      ]
    }
  ],
  "candidate_ids": [
    1942,
    1977,
    1951,
    1968,
    1976,
    1969,
    1947,
    1936,
    1971,
    1945,
    1943,
    1974,
    1937,
    1970,
    1978,
    1950,
    1975,
    1931,
    1941,
    1979,
    1973,
    1944,
    1940,
    1967,
    1953,
    1965,
    1954,
    1932,
    1948,
    1946,
    1939,
    1958,
    1938,
    1955,
    1957,
    1966,
    1962,
    1935,
    1949,
    1956,
    1963,
    1961,
    1960,
    1933,
    1959,
    1972,
    1934,
    1952,
    1964,
    1980
  ],
  "final_ids": [
    1942,
    1977,
    1951,
    1968,
    1976,
    1969,
    1947,
    1936,
    1971,
    1945
  ],
  "prompt_citations": [
    {
      "n": 1,
      "chunk_id": "1942",
      "section_path": "商品与购物 FAQ/运费怎么算",
      "question": "运费怎么算",
      "answer": "单笔订单满 99 元包邮,未满收取 10 元运费,偏远地区运费另计。邮费即运费,按此规则收取。"
    },
    {
      "n": 3,
      "chunk_id": "1951",
      "section_path": "商品与购物 FAQ/会员运费权益",
      "question": "会员运费权益",
      "answer": "金卡会员每月享 3 次免运费权益,银卡会员享 1 次;权益不与偏远地区附加运费冲抵,当月未用完不结转。"
    },
    {
      "n": 5,
      "chunk_id": "1976",
      "section_path": "积分规则/积分怎么攒",
      "question": "积分怎么攒",
      "answer": "已完成订单每实际支付 1 元商品金额累计 1 积分，不计配送费；退款后按对应商品金额同步扣回积分。活动期间的双倍积分属于额外积分奖励，不计入会员等级升级；会员等级仍按有效累计消费金额计算。"
    },
    {
      "n": 7,
      "chunk_id": "1947",
      "section_path": "商品与购物 FAQ/配送范围与偏远地区",
      "question": "配送范围与偏远地区",
      "answer": "全国大部分地区支持配送,新疆、西藏、内蒙古等偏远地区运费另计且时效顺延;港澳台及海外暂不支持自营配送。"
    },
    {
      "n": 9,
      "chunk_id": "1971",
      "section_path": "退货退款政策/运输破损处理",
      "question": "运输破损处理",
      "answer": "商品运输途中破损的,请在签收后 48 小时内联系客服并提供开箱视频与照片,核实后可免费补发或退款,相关运费由平台承担。"
    },
    {
      "n": 10,
      "chunk_id": "1945",
      "section_path": "商品与购物 FAQ/会员等级与积分规则",
      "question": "会员等级与积分规则",
      "answer": "会员分为普通、银卡、金卡三档,按累计消费自动升级。每消费 1 元得 1 积分,积分可在结算时抵扣,100 积分抵 1 元。"
    },
    {
      "n": 8,
      "chunk_id": "1936",
      "section_path": "售后手册/维修寄修流程",
      "question": "维修寄修流程",
      "answer": "保修期内设备故障,联系客服登记后按指引将设备寄回指定维修点,核验后免费维修并寄回;超保或人为损坏维修可能收取工本费,费用会提前告知。"
    },
    {
      "n": 6,
      "chunk_id": "1969",
      "section_path": "退货退款政策/退换货运费承担",
      "question": "退换货运费承担",
      "answer": "无理由退货的退回运费由买家承担;因商品质量问题、发错货、少发漏发导致的退换货,运费由平台承担。运费承担以平台售后规则最终判定为准。"
    },
    {
      "n": 4,
      "chunk_id": "1968",
      "section_path": "退货退款政策/换货政策/换货运费",
      "question": "换货运费",
      "answer": "非质量问题的换货,往返运费由买家承担;因质量问题或发错货的换货,往返运费由平台承担。"
    },
    {
      "n": 2,
      "chunk_id": "1977",
      "section_path": "积分规则/积分怎么用",
      "question": "积分怎么用",
      "answer": "积分可在结算时抵扣商品金额，100 积分抵 1 元现金，单笔订单最多抵 30 元，不用于抵扣偏远地区附加运费，也不支持直接提现。\n\n2000 积分可兑换自动饮水机滤芯 3 片，该兑换套装适用于 MH-W40，普通配送地区包邮；偏远地区附加配送费仍需按页面规则确认。MH-W40 的滤芯更换周期以商品规格手册为准。\n\n800 积分可兑换猫零食小样，普通配送地区另收 6 元运费；该兑换不直接套用普通购物订单的满 99 元包邮规则。兑换商品、可用库存及偏远地区配送规则以兑换页面标注为准。"
    }
  ],
  "decision": {
    "useful": true,
    "reason": "运费规则证据充分",
    "response_kind": "knowledge",
    "source": null
  },
  "answer": "您好！根据运费规则：单笔订单满 99 元包邮，未满 99 元收取 10 元运费，偏远地区（如新疆、西藏、内蒙古等）运费另计 [1]。\n\n另外，如果您是会员：金卡会员每月有 3 次免运费权益，银卡会员每月 1 次 [3]。\n\n请问您方便告诉我订单金额或所在地区吗？这样我可以帮您更准确判断。",
  "point_verdicts": [
    {
      "point_id": "p1",
      "covered": true,
      "reason": "回答明确说明单笔订单满99元包邮，未满收取10元运费，涵盖基础运费规则全部事实。"
    },
    {
      "point_id": "p2",
      "covered": true,
      "reason": "回答说明偏远地区（如新疆、西藏、内蒙古等）运费另计，完整覆盖该要点。"
    }
  ],
  "claim_verdicts": [
    {
      "claim": "单笔订单满99元包邮，未满99元收取10元运费",
      "supported": true,
      "reason": "证据[1]明确说明单笔订单满99元包邮，未满收取10元运费，完全支持该断言。"
    },
    {
      "claim": "偏远地区（如新疆、西藏、内蒙古等）运费另计",
      "supported": true,
      "reason": "证据[1]说明偏远地区运费另计，证据[7]确认新疆、西藏、内蒙古等偏远地区运费另计，支持该断言。"
    },
    {
      "claim": "金卡会员每月有3次免运费权益",
      "supported": true,
      "reason": "证据[3]明确金卡会员每月享3次免运费权益，支持该断言。"
    },
    {
      "claim": "银卡会员每月有1次免运费权益",
      "supported": true,
      "reason": "证据[3]明确银卡会员每月享1次免运费权益，支持该断言。"
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
  "elapsed_ms": 12021.624299930409,
  "judge_snapshot": {
    "prompt_version": "joint-generation-v2.1",
    "finish_reason": "stop"
  },
  "rewrite": {
    "policy_version": "original-query-on-invalid-v1",
    "status": "success",
    "error": null
  },
  "audit": {
    "audit_version": 1,
    "source_map_id": "af6590ab401319d942bddff0b30213a4cd888b8cf115ebd5cdec3adb87687e55",
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
        "chunk_id": 1942,
        "score": 0.032786883413791656,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1977,
        "score": 0.016129031777381897,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1951,
        "score": 0.01587301678955555,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1968,
        "score": 0.015625,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1976,
        "score": 0.015384615398943424,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1969,
        "score": 0.01515151560306549,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1947,
        "score": 0.014925372786819935,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1936,
        "score": 0.014705882407724857,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1971,
        "score": 0.014492753893136978,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1945,
        "score": 0.014285714365541935,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1943,
        "score": 0.014084506779909134,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1974,
        "score": 0.013888888992369175,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1937,
        "score": 0.013698630034923553,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1970,
        "score": 0.013513513840734959,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1978,
        "score": 0.013333333656191826,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1950,
        "score": 0.01315789483487606,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1975,
        "score": 0.012987012974917889,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1931,
        "score": 0.012820512987673283,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1941,
        "score": 0.012658228166401386,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1979,
        "score": 0.012500000186264515,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1973,
        "score": 0.012345679104328156,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1944,
        "score": 0.012195121496915817,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1940,
        "score": 0.012048192322254181,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1967,
        "score": 0.011904762126505375,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1953,
        "score": 0.0117647061124444,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1965,
        "score": 0.011627906933426857,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1954,
        "score": 0.01149425283074379,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1932,
        "score": 0.011363636702299118,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1948,
        "score": 0.01123595517128706,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1946,
        "score": 0.011111111380159855,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1939,
        "score": 0.010989011265337467,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1958,
        "score": 0.010869565419852734,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1938,
        "score": 0.01075268816202879,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1955,
        "score": 0.010638297535479069,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1957,
        "score": 0.010526316240429878,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1966,
        "score": 0.010416666977107525,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1962,
        "score": 0.010309278033673763,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1935,
        "score": 0.010204081423580647,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1949,
        "score": 0.010101010091602802,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1956,
        "score": 0.009999999776482582,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1963,
        "score": 0.009900989942252636,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1961,
        "score": 0.009803921915590763,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1960,
        "score": 0.009708737954497337,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1933,
        "score": 0.009615384973585606,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1959,
        "score": 0.009523809887468815,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1972,
        "score": 0.009433962404727936,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1934,
        "score": 0.009345794096589088,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1952,
        "score": 0.009259259328246117,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1964,
        "score": 0.00917431153357029,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1980,
        "score": 0.00909090880304575,
        "score_kind": "rrf"
      }
    ],
    "final_ranking": [
      {
        "chunk_id": 1942,
        "score": 0.032786883413791656,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1977,
        "score": 0.016129031777381897,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1951,
        "score": 0.01587301678955555,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1968,
        "score": 0.015625,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1976,
        "score": 0.015384615398943424,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1969,
        "score": 0.01515151560306549,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1947,
        "score": 0.014925372786819935,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1936,
        "score": 0.014705882407724857,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1971,
        "score": 0.014492753893136978,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1945,
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
          1942
        ]
      ]
    }
  ],
  "candidate_ids": [
    1942,
    1977,
    1951,
    1968,
    1976,
    1969,
    1947,
    1936,
    1971,
    1945,
    1943,
    1974,
    1937,
    1970,
    1978,
    1950,
    1975,
    1931,
    1941,
    1979,
    1973,
    1944,
    1940,
    1967,
    1953,
    1965,
    1954,
    1932,
    1948,
    1946,
    1939,
    1958,
    1938,
    1955,
    1957,
    1966,
    1962,
    1935,
    1949,
    1956,
    1963,
    1961,
    1960,
    1933,
    1959,
    1972,
    1934,
    1952,
    1964,
    1980
  ],
  "final_ids": [
    1942,
    1974,
    1976,
    1978,
    1977,
    1969,
    1951,
    1968,
    1937,
    1947
  ],
  "prompt_citations": [
    {
      "n": 1,
      "chunk_id": "1942",
      "section_path": "商品与购物 FAQ/运费怎么算",
      "question": "运费怎么算",
      "answer": "单笔订单满 99 元包邮,未满收取 10 元运费,偏远地区运费另计。邮费即运费,按此规则收取。"
    },
    {
      "n": 3,
      "chunk_id": "1976",
      "section_path": "积分规则/积分怎么攒",
      "question": "积分怎么攒",
      "answer": "已完成订单每实际支付 1 元商品金额累计 1 积分，不计配送费；退款后按对应商品金额同步扣回积分。活动期间的双倍积分属于额外积分奖励，不计入会员等级升级；会员等级仍按有效累计消费金额计算。"
    },
    {
      "n": 5,
      "chunk_id": "1977",
      "section_path": "积分规则/积分怎么用",
      "question": "积分怎么用",
      "answer": "积分可在结算时抵扣商品金额，100 积分抵 1 元现金，单笔订单最多抵 30 元，不用于抵扣偏远地区附加运费，也不支持直接提现。\n\n2000 积分可兑换自动饮水机滤芯 3 片，该兑换套装适用于 MH-W40，普通配送地区包邮；偏远地区附加配送费仍需按页面规则确认。MH-W40 的滤芯更换周期以商品规格手册为准。\n\n800 积分可兑换猫零食小样，普通配送地区另收 6 元运费；该兑换不直接套用普通购物订单的满 99 元包邮规则。兑换商品、可用库存及偏远地区配送规则以兑换页面标注为准。"
    },
    {
      "n": 7,
      "chunk_id": "1951",
      "section_path": "商品与购物 FAQ/会员运费权益",
      "question": "会员运费权益",
      "answer": "金卡会员每月享 3 次免运费权益,银卡会员享 1 次;权益不与偏远地区附加运费冲抵,当月未用完不结转。"
    },
    {
      "n": 9,
      "chunk_id": "1937",
      "section_path": "售后手册/会员专属售后权益",
      "question": "会员专属售后权益",
      "answer": "金卡会员享优先客服接入与上门取件退换货;银卡会员享退换货运费权益 1 次/月。具体权益以会员中心页面标注为准。"
    },
    {
      "n": 10,
      "chunk_id": "1947",
      "section_path": "商品与购物 FAQ/配送范围与偏远地区",
      "question": "配送范围与偏远地区",
      "answer": "全国大部分地区支持配送,新疆、西藏、内蒙古等偏远地区运费另计且时效顺延;港澳台及海外暂不支持自营配送。"
    },
    {
      "n": 8,
      "chunk_id": "1968",
      "section_path": "退货退款政策/换货政策/换货运费",
      "question": "换货运费",
      "answer": "非质量问题的换货,往返运费由买家承担;因质量问题或发错货的换货,往返运费由平台承担。"
    },
    {
      "n": 6,
      "chunk_id": "1969",
      "section_path": "退货退款政策/退换货运费承担",
      "question": "退换货运费承担",
      "answer": "无理由退货的退回运费由买家承担;因商品质量问题、发错货、少发漏发导致的退换货,运费由平台承担。运费承担以平台售后规则最终判定为准。"
    },
    {
      "n": 4,
      "chunk_id": "1978",
      "section_path": "开票细则/可开票类型",
      "question": "可开票类型",
      "answer": "本演示店提供电子普通发票、电子专用发票和纸质专用发票。电子普通发票可按订单申请；电子专票需要企业账户，申请前准备发票抬头及有效纳税人识别号，按申请页面提交资料。\n\n纸质专票仅企业账户可申请，申请时需提供企业开票资料、收件人和邮寄地址，快递费到付。资料审核通过后按开票流程寄出，不承诺快递送达日期。"
    },
    {
      "n": 2,
      "chunk_id": "1974",
      "section_path": "会员权益/会员等级",
      "question": "会员等级",
      "answer": "会员分为普通、银卡和金卡三档，按有效累计消费金额自动升级，不按年度消费金额计算。累计消费未满 1000 元为普通会员，满 1000 元起为银卡，满 5000 元起为金卡。\n\n有效累计消费指已完成订单的商品实际支付金额，不含配送费；退货退款部分从有效累计消费中扣除。退款后根据更新的累计消费重新计算等级，未达到原门槛时可能降级。等级与适用权益在会员中心展示。\n\n银卡在参与会员折扣的商品上享 95 折，金卡享 9 折。折扣适用商品和活动范围以结算页面标注为准。会员折扣、优惠券与满减是否叠加也以当次活动页面为准，不能一概承诺全部优惠同时生效。"
    }
  ],
  "decision": {
    "useful": true,
    "reason": "运费规则直接覆盖：满99包邮否则10元，偏远另计",
    "response_kind": "knowledge",
    "source": null
  },
  "answer": "您好！运费规则如下：单笔订单满 99 元包邮，未满则收取 10 元运费；新疆、西藏、内蒙古等偏远地区运费另计 [1]。\n\n如您有具体订单想确认实际邮费，请提供订单号，我可以帮您查询。",
  "point_verdicts": [
    {
      "point_id": "p1",
      "covered": true,
      "reason": "回答明确说明满99元包邮、未满收10元运费，覆盖要点及普通订单条件"
    },
    {
      "point_id": "p2",
      "covered": true,
      "reason": "回答说明新疆、西藏、内蒙古等偏远地区运费另计，覆盖要点"
    }
  ],
  "claim_verdicts": [
    {
      "claim": "单笔订单满99元包邮，未满收取10元运费",
      "supported": true,
      "reason": "证据1明确单笔订单满99元包邮，未满收取10元运费"
    },
    {
      "claim": "新疆、西藏、内蒙古等偏远地区运费另计",
      "supported": true,
      "reason": "证据1说明偏远地区运费另计，证据10明确新疆、西藏、内蒙古等偏远地区运费另计"
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
  "elapsed_ms": 10110.783699667081,
  "judge_snapshot": {
    "prompt_version": "joint-generation-v2.1",
    "finish_reason": "stop"
  },
  "rewrite": {
    "policy_version": "original-query-on-invalid-v1",
    "status": "success",
    "error": null
  },
  "audit": {
    "audit_version": 1,
    "source_map_id": "af6590ab401319d942bddff0b30213a4cd888b8cf115ebd5cdec3adb87687e55",
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
        "chunk_id": 1942,
        "score": 0.032786883413791656,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1977,
        "score": 0.016129031777381897,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1951,
        "score": 0.01587301678955555,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1968,
        "score": 0.015625,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1976,
        "score": 0.015384615398943424,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1969,
        "score": 0.01515151560306549,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1947,
        "score": 0.014925372786819935,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1936,
        "score": 0.014705882407724857,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1971,
        "score": 0.014492753893136978,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1945,
        "score": 0.014285714365541935,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1943,
        "score": 0.014084506779909134,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1974,
        "score": 0.013888888992369175,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1937,
        "score": 0.013698630034923553,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1970,
        "score": 0.013513513840734959,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1978,
        "score": 0.013333333656191826,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1950,
        "score": 0.01315789483487606,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1975,
        "score": 0.012987012974917889,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1931,
        "score": 0.012820512987673283,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1941,
        "score": 0.012658228166401386,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1979,
        "score": 0.012500000186264515,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1973,
        "score": 0.012345679104328156,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1944,
        "score": 0.012195121496915817,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1940,
        "score": 0.012048192322254181,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1967,
        "score": 0.011904762126505375,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1953,
        "score": 0.0117647061124444,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1965,
        "score": 0.011627906933426857,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1954,
        "score": 0.01149425283074379,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1932,
        "score": 0.011363636702299118,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1948,
        "score": 0.01123595517128706,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1946,
        "score": 0.011111111380159855,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1939,
        "score": 0.010989011265337467,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1958,
        "score": 0.010869565419852734,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1938,
        "score": 0.01075268816202879,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1955,
        "score": 0.010638297535479069,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1957,
        "score": 0.010526316240429878,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1966,
        "score": 0.010416666977107525,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1962,
        "score": 0.010309278033673763,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1935,
        "score": 0.010204081423580647,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1949,
        "score": 0.010101010091602802,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1956,
        "score": 0.009999999776482582,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1963,
        "score": 0.009900989942252636,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1961,
        "score": 0.009803921915590763,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1960,
        "score": 0.009708737954497337,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1933,
        "score": 0.009615384973585606,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1959,
        "score": 0.009523809887468815,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1972,
        "score": 0.009433962404727936,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1934,
        "score": 0.009345794096589088,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1952,
        "score": 0.009259259328246117,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1964,
        "score": 0.00917431153357029,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1980,
        "score": 0.00909090880304575,
        "score_kind": "rrf"
      }
    ],
    "final_ranking": [
      {
        "chunk_id": 1942,
        "score": 0.42253774404525757,
        "score_kind": "rerank"
      },
      {
        "chunk_id": 1974,
        "score": 0.0025972246658056974,
        "score_kind": "rerank"
      },
      {
        "chunk_id": 1976,
        "score": 0.0022758350241929293,
        "score_kind": "rerank"
      },
      {
        "chunk_id": 1978,
        "score": 0.0021258187480270863,
        "score_kind": "rerank"
      },
      {
        "chunk_id": 1977,
        "score": 0.0021101937163621187,
        "score_kind": "rerank"
      },
      {
        "chunk_id": 1969,
        "score": 0.0017548224423080683,
        "score_kind": "rerank"
      },
      {
        "chunk_id": 1951,
        "score": 0.0016951002180576324,
        "score_kind": "rerank"
      },
      {
        "chunk_id": 1968,
        "score": 0.000958225573413074,
        "score_kind": "rerank"
      },
      {
        "chunk_id": 1937,
        "score": 0.0008439415832981467,
        "score_kind": "rerank"
      },
      {
        "chunk_id": 1947,
        "score": 0.0007063436787575483,
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
          1934
        ]
      ]
    }
  ],
  "candidate_ids": [
    1934,
    1962,
    1963,
    1960,
    1933,
    1953,
    1961,
    1949,
    1955,
    1936,
    1931,
    1977,
    1971,
    1944,
    1947,
    1958,
    1972,
    1975,
    1954,
    1959,
    1935,
    1957,
    1980,
    1956,
    1976,
    1979,
    1940,
    1973,
    1967,
    1950,
    1946,
    1948,
    1939,
    1968,
    1941,
    1945,
    1952,
    1951,
    1937,
    1938,
    1965,
    1970,
    1978,
    1943,
    1966,
    1964,
    1969,
    1942,
    1974,
    1932
  ],
  "final_ids": [
    1934,
    1962,
    1963,
    1960,
    1933,
    1953,
    1961,
    1949,
    1955,
    1936
  ],
  "prompt_citations": [
    {
      "n": 1,
      "chunk_id": "1934",
      "section_path": "售后手册/常见故障自查",
      "question": "常见故障自查",
      "answer": "- 饮水机不出水:检查水位是否低于最低线、水泵是否卡阻,断电清洗水泵后重试。\n- 猫砂盆报错:清空废砂盒并检查滚筒是否卡砂,重启设备;仍报错联系售后。\n- 喂食器卡粮:检查粮食颗粒直径是否超 12mm、粮桶是否受潮结块,清理出粮口后重试。\n- 摄像头离线:确认 Wi-Fi 为 2.4G 频段、信号良好,重启设备或在 App 内重新配网。"
    },
    {
      "n": 3,
      "chunk_id": "1963",
      "section_path": "商品规格手册/自动喂食器 摄像头版(型号 MH-FD30)",
      "question": "自动喂食器 摄像头版(型号 MH-FD30)",
      "answer": "- 型号:MH-FD30\n- 粮桶容量:6L\n- 核心功能:1080P 摄像头、双向语音、App 远程手动投喂与定时投喂\n- 供电:市电供电 + 内置应急电池\n- 说明:摄像头版支持视频回看,需连接 2.4G Wi-Fi"
    },
    {
      "n": 5,
      "chunk_id": "1933",
      "section_path": "售后手册/设备安装与激活",
      "question": "设备安装与激活",
      "answer": "智能设备首次使用需下载「喵喵优选」App,按说明书扫码添加设备并连接 2.4G Wi-Fi 完成激活;猫爬架等非联网商品按随附图解自行组装。"
    },
    {
      "n": 7,
      "chunk_id": "1961",
      "section_path": "商品规格手册/大号三档加热垫(型号 MH-HP20)",
      "question": "大号三档加热垫(型号 MH-HP20)",
      "answer": "- 型号:MH-HP20\n- 尺寸:60cm × 45cm\n- 温控:三档可调 30℃ / 38℃ / 45℃,内置过热保护与定时关机\n- 防护:防水防抓咬电线套管,表面绒布可拆洗\n- 适用:大型猫、多猫窝及冬季保暖"
    },
    {
      "n": 9,
      "chunk_id": "1955",
      "section_path": "商品规格手册/智能猫砂盆 Max(型号 MH-LP200)",
      "question": "智能猫砂盆 Max(型号 MH-LP200)",
      "answer": "- 型号:MH-LP200\n- 适用猫咪体重:2kg 至 12kg,适合大型猫与多猫家庭\n- 猫砂容量:12L,废砂盒容量约 10 天(单猫)\n- 核心功能:超大滚筒、双重称重防夹、活性炭除臭、App 多猫健康档案\n- 供电:220V 市电\n- 清理提示:多猫家庭建议每 3 至 5 天倾倒一次废砂盒"
    },
    {
      "n": 10,
      "chunk_id": "1936",
      "section_path": "售后手册/维修寄修流程",
      "question": "维修寄修流程",
      "answer": "保修期内设备故障,联系客服登记后按指引将设备寄回指定维修点,核验后免费维修并寄回;超保或人为损坏维修可能收取工本费,费用会提前告知。"
    },
    {
      "n": 8,
      "chunk_id": "1949",
      "section_path": "商品与购物 FAQ/商品缺货多久补货",
      "question": "商品缺货多久补货",
      "answer": "现货售罄的商品通常 3 至 7 天内补货,可在商品页点击「到货通知」,补货后系统会推送提醒。"
    },
    {
      "n": 6,
      "chunk_id": "1953",
      "section_path": "商品规格手册/智能猫砂盆 Pro(型号 MH-LP100)",
      "question": "智能猫砂盆 Pro(型号 MH-LP100)",
      "answer": "- 型号:MH-LP100\n- 适用猫咪体重:1.5kg 至 8kg\n- 猫砂容量:9L,废砂盒容量约 7 天(单猫)\n- 核心功能:自动感应清理、活性炭除臭、App 远程监控与健康记录\n- 供电:220V 市电,断电后配置自动保存\n- 清理提示:废砂盒满时 App 推送提醒,建议每 5 至 7 天倾倒一次"
    },
    {
      "n": 4,
      "chunk_id": "1960",
      "section_path": "商品规格手册/恒温加热垫(型号 MH-HP12)",
      "question": "恒温加热垫(型号 MH-HP12)",
      "answer": "- 型号:MH-HP12\n- 尺寸:40cm × 30cm\n- 温控:恒温 38℃,内置过热保护,连续通电不超过 12 小时为宜\n- 防护:防水防抓咬电线套管\n- 适用:幼猫、老年猫及冬季保暖"
    },
    {
      "n": 2,
      "chunk_id": "1962",
      "section_path": "商品规格手册/自动喂食器 基础版(型号 MH-FD10)",
      "question": "自动喂食器 基础版(型号 MH-FD10)",
      "answer": "- 型号:MH-FD10\n- 粮桶容量:4L\n- 核心功能:定时定量投喂,每日最多 6 餐,语音呼唤进食\n- 供电:市电供电 + 4 节 5 号电池断电应急\n- 说明:基础版不含摄像头与 App 远程投喂"
    }
  ],
  "decision": {
    "useful": true,
    "reason": "喂食器卡粮故障自查有覆盖",
    "response_kind": "knowledge",
    "source": null
  },
  "answer": "您好！关于喂食器卡粮不下粮，可以按以下方法自查[1]：\n\n1. 检查粮食颗粒直径是否超过 12mm；\n2. 检查粮桶是否受潮结块；\n3. 清理出粮口后重新尝试。\n\n如果按以上方法处理后仍然卡粮，建议联系售后进一步处理[1]。请问还需要帮您其他忙吗？",
  "point_verdicts": [
    {
      "point_id": "p1",
      "covered": true,
      "reason": "回答完整覆盖检查颗粒直径是否超12mm、粮桶受潮结块、清理出粮口后重试，且以建议联系售后保留不保证自行修复的条件"
    }
  ],
  "claim_verdicts": [
    {
      "claim": "喂食器卡粮可检查粮食颗粒直径是否超过12mm",
      "supported": true,
      "reason": "证据1明确写明喂食器卡粮检查粮食颗粒直径是否超12mm"
    },
    {
      "claim": "喂食器卡粮可检查粮桶是否受潮结块",
      "supported": true,
      "reason": "证据1明确写明检查粮桶是否受潮结块"
    },
    {
      "claim": "清理出粮口后重新尝试可解决卡粮",
      "supported": true,
      "reason": "证据1明确写明清理出粮口后重试"
    },
    {
      "claim": "按以上方法处理后仍然卡粮建议联系售后进一步处理",
      "supported": false,
      "reason": "证据1仅写清理出粮口后重试，未提及仍卡粮时联系售后；证据10的寄修流程不构成该具体建议的支持"
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
    "faithfulness": 0.75,
    "absent_refusal_rate": null,
    "answerable_false_refusal_rate": 0.0
  },
  "error": null,
  "elapsed_ms": 9671.414999989793,
  "judge_snapshot": {
    "prompt_version": "joint-generation-v2.1",
    "finish_reason": "stop"
  },
  "rewrite": {
    "policy_version": "original-query-on-invalid-v1",
    "status": "success",
    "error": null
  },
  "audit": {
    "audit_version": 1,
    "source_map_id": "af6590ab401319d942bddff0b30213a4cd888b8cf115ebd5cdec3adb87687e55",
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
        "chunk_id": 1934,
        "score": 0.5772529244422913,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1962,
        "score": 0.5681241750717163,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1963,
        "score": 0.5519284605979919,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1960,
        "score": 0.44144922494888306,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1933,
        "score": 0.4325045645236969,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1953,
        "score": 0.4311125874519348,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1961,
        "score": 0.425503134727478,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1949,
        "score": 0.42119717597961426,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1955,
        "score": 0.4190990626811981,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1936,
        "score": 0.4171714782714844,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1931,
        "score": 0.41137444972991943,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1977,
        "score": 0.40876007080078125,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1971,
        "score": 0.4044782221317291,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1944,
        "score": 0.40205860137939453,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1947,
        "score": 0.4005569815635681,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1958,
        "score": 0.3997158408164978,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1972,
        "score": 0.39917227625846863,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1975,
        "score": 0.3987771272659302,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1954,
        "score": 0.3967640995979309,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1959,
        "score": 0.3930070698261261,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1935,
        "score": 0.39167726039886475,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1957,
        "score": 0.39126795530319214,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1980,
        "score": 0.39097651839256287,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1956,
        "score": 0.3908694386482239,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1976,
        "score": 0.39064010977745056,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1979,
        "score": 0.38086429238319397,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1940,
        "score": 0.3758910298347473,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1973,
        "score": 0.37508946657180786,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1967,
        "score": 0.3737112879753113,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1950,
        "score": 0.37022215127944946,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1946,
        "score": 0.3654598295688629,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1948,
        "score": 0.36215317249298096,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1939,
        "score": 0.3583248555660248,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1968,
        "score": 0.35749560594558716,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1941,
        "score": 0.3557622730731964,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1945,
        "score": 0.3545067012310028,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1952,
        "score": 0.35215047001838684,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1951,
        "score": 0.35150402784347534,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1937,
        "score": 0.34910643100738525,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1938,
        "score": 0.3463031053543091,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1965,
        "score": 0.34621840715408325,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1970,
        "score": 0.34575554728507996,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1978,
        "score": 0.3429238200187683,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1943,
        "score": 0.3407789468765259,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1966,
        "score": 0.3372826874256134,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1964,
        "score": 0.33206331729888916,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1969,
        "score": 0.32385486364364624,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1942,
        "score": 0.3220908045768738,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1974,
        "score": 0.3202211856842041,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1932,
        "score": 0.31397026777267456,
        "score_kind": "cosine"
      }
    ],
    "final_ranking": [
      {
        "chunk_id": 1934,
        "score": 0.5772529244422913,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1962,
        "score": 0.5681241750717163,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1963,
        "score": 0.5519284605979919,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1960,
        "score": 0.44144922494888306,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1933,
        "score": 0.4325045645236969,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1953,
        "score": 0.4311125874519348,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1961,
        "score": 0.425503134727478,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1949,
        "score": 0.42119717597961426,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1955,
        "score": 0.4190990626811981,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1936,
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
          1934
        ]
      ]
    }
  ],
  "candidate_ids": [
    1962,
    1963,
    1934
  ],
  "final_ids": [
    1962,
    1963,
    1934
  ],
  "prompt_citations": [
    {
      "n": 1,
      "chunk_id": "1962",
      "section_path": "商品规格手册/自动喂食器 基础版(型号 MH-FD10)",
      "question": "自动喂食器 基础版(型号 MH-FD10)",
      "answer": "- 型号:MH-FD10\n- 粮桶容量:4L\n- 核心功能:定时定量投喂,每日最多 6 餐,语音呼唤进食\n- 供电:市电供电 + 4 节 5 号电池断电应急\n- 说明:基础版不含摄像头与 App 远程投喂"
    },
    {
      "n": 3,
      "chunk_id": "1934",
      "section_path": "售后手册/常见故障自查",
      "question": "常见故障自查",
      "answer": "- 饮水机不出水:检查水位是否低于最低线、水泵是否卡阻,断电清洗水泵后重试。\n- 猫砂盆报错:清空废砂盒并检查滚筒是否卡砂,重启设备;仍报错联系售后。\n- 喂食器卡粮:检查粮食颗粒直径是否超 12mm、粮桶是否受潮结块,清理出粮口后重试。\n- 摄像头离线:确认 Wi-Fi 为 2.4G 频段、信号良好,重启设备或在 App 内重新配网。"
    },
    {
      "n": 2,
      "chunk_id": "1963",
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
  "answer": "您好！关于喂食器堵粮不下粮的问题，可参考以下自查方法[3]：\n\n1. **检查粮食颗粒**：确认颗粒直径是否超过 12mm，过大的颗粒容易卡住；\n2. **检查粮桶**：看是否受潮结块，如有结块需清理；\n3. **清理出粮口**：清理后重新试机。\n\n以上处理仍无法解决的话，建议联系售后处理哦。另外方便告知您的设备型号吗（如 MH-FD10 基础版或 MH-FD30 摄像头版）？方便我提供更准确的帮助～",
  "point_verdicts": [
    {
      "point_id": "p1",
      "covered": true,
      "reason": "回答覆盖检查颗粒直径是否超12mm、粮桶受潮结块需清理、清理出粮口后重试，并以建议联系售后保留不保证自行修复的条件"
    }
  ],
  "claim_verdicts": [
    {
      "claim": "喂食器卡粮可检查粮食颗粒直径是否超过12mm",
      "supported": true,
      "reason": "证据3明确记载喂食器卡粮需检查颗粒直径是否超12mm"
    },
    {
      "claim": "粮桶受潮结块会导致堵粮，如有结块需清理",
      "supported": true,
      "reason": "证据3记载喂食器卡粮需检查粮桶是否受潮结块"
    },
    {
      "claim": "清理出粮口后重新试机可排查堵粮问题",
      "supported": true,
      "reason": "证据3记载清理出粮口后重试"
    },
    {
      "claim": "以上处理仍无法解决建议联系售后处理",
      "supported": true,
      "reason": "证据3的自查流程对应兜底为联系售后，回答该建议与证据一致"
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
  "elapsed_ms": 10591.542999725789,
  "judge_snapshot": {
    "prompt_version": "joint-generation-v2.1",
    "finish_reason": "stop"
  },
  "rewrite": {
    "policy_version": "original-query-on-invalid-v1",
    "status": "success",
    "error": null
  },
  "audit": {
    "audit_version": 1,
    "source_map_id": "af6590ab401319d942bddff0b30213a4cd888b8cf115ebd5cdec3adb87687e55",
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
        "chunk_id": 1962,
        "score": 2.582362174987793,
        "score_kind": "bm25"
      },
      {
        "chunk_id": 1963,
        "score": 2.525158166885376,
        "score_kind": "bm25"
      },
      {
        "chunk_id": 1934,
        "score": 2.158566951751709,
        "score_kind": "bm25"
      }
    ],
    "final_ranking": [
      {
        "chunk_id": 1962,
        "score": 2.582362174987793,
        "score_kind": "bm25"
      },
      {
        "chunk_id": 1963,
        "score": 2.525158166885376,
        "score_kind": "bm25"
      },
      {
        "chunk_id": 1934,
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
          1934
        ]
      ]
    }
  ],
  "candidate_ids": [
    1962,
    1934,
    1963,
    1960,
    1933,
    1953,
    1961,
    1949,
    1955,
    1936,
    1931,
    1977,
    1971,
    1944,
    1947,
    1958,
    1972,
    1975,
    1954,
    1959,
    1935,
    1957,
    1980,
    1956,
    1976,
    1979,
    1940,
    1973,
    1967,
    1950,
    1946,
    1948,
    1939,
    1968,
    1941,
    1945,
    1952,
    1951,
    1937,
    1938,
    1965,
    1970,
    1978,
    1943,
    1966,
    1964,
    1969,
    1942,
    1974,
    1932
  ],
  "final_ids": [
    1962,
    1934,
    1963,
    1960,
    1933,
    1953,
    1961,
    1949,
    1955,
    1936
  ],
  "prompt_citations": [
    {
      "n": 1,
      "chunk_id": "1962",
      "section_path": "商品规格手册/自动喂食器 基础版(型号 MH-FD10)",
      "question": "自动喂食器 基础版(型号 MH-FD10)",
      "answer": "- 型号:MH-FD10\n- 粮桶容量:4L\n- 核心功能:定时定量投喂,每日最多 6 餐,语音呼唤进食\n- 供电:市电供电 + 4 节 5 号电池断电应急\n- 说明:基础版不含摄像头与 App 远程投喂"
    },
    {
      "n": 3,
      "chunk_id": "1963",
      "section_path": "商品规格手册/自动喂食器 摄像头版(型号 MH-FD30)",
      "question": "自动喂食器 摄像头版(型号 MH-FD30)",
      "answer": "- 型号:MH-FD30\n- 粮桶容量:6L\n- 核心功能:1080P 摄像头、双向语音、App 远程手动投喂与定时投喂\n- 供电:市电供电 + 内置应急电池\n- 说明:摄像头版支持视频回看,需连接 2.4G Wi-Fi"
    },
    {
      "n": 5,
      "chunk_id": "1933",
      "section_path": "售后手册/设备安装与激活",
      "question": "设备安装与激活",
      "answer": "智能设备首次使用需下载「喵喵优选」App,按说明书扫码添加设备并连接 2.4G Wi-Fi 完成激活;猫爬架等非联网商品按随附图解自行组装。"
    },
    {
      "n": 7,
      "chunk_id": "1961",
      "section_path": "商品规格手册/大号三档加热垫(型号 MH-HP20)",
      "question": "大号三档加热垫(型号 MH-HP20)",
      "answer": "- 型号:MH-HP20\n- 尺寸:60cm × 45cm\n- 温控:三档可调 30℃ / 38℃ / 45℃,内置过热保护与定时关机\n- 防护:防水防抓咬电线套管,表面绒布可拆洗\n- 适用:大型猫、多猫窝及冬季保暖"
    },
    {
      "n": 9,
      "chunk_id": "1955",
      "section_path": "商品规格手册/智能猫砂盆 Max(型号 MH-LP200)",
      "question": "智能猫砂盆 Max(型号 MH-LP200)",
      "answer": "- 型号:MH-LP200\n- 适用猫咪体重:2kg 至 12kg,适合大型猫与多猫家庭\n- 猫砂容量:12L,废砂盒容量约 10 天(单猫)\n- 核心功能:超大滚筒、双重称重防夹、活性炭除臭、App 多猫健康档案\n- 供电:220V 市电\n- 清理提示:多猫家庭建议每 3 至 5 天倾倒一次废砂盒"
    },
    {
      "n": 10,
      "chunk_id": "1936",
      "section_path": "售后手册/维修寄修流程",
      "question": "维修寄修流程",
      "answer": "保修期内设备故障,联系客服登记后按指引将设备寄回指定维修点,核验后免费维修并寄回;超保或人为损坏维修可能收取工本费,费用会提前告知。"
    },
    {
      "n": 8,
      "chunk_id": "1949",
      "section_path": "商品与购物 FAQ/商品缺货多久补货",
      "question": "商品缺货多久补货",
      "answer": "现货售罄的商品通常 3 至 7 天内补货,可在商品页点击「到货通知」,补货后系统会推送提醒。"
    },
    {
      "n": 6,
      "chunk_id": "1953",
      "section_path": "商品规格手册/智能猫砂盆 Pro(型号 MH-LP100)",
      "question": "智能猫砂盆 Pro(型号 MH-LP100)",
      "answer": "- 型号:MH-LP100\n- 适用猫咪体重:1.5kg 至 8kg\n- 猫砂容量:9L,废砂盒容量约 7 天(单猫)\n- 核心功能:自动感应清理、活性炭除臭、App 远程监控与健康记录\n- 供电:220V 市电,断电后配置自动保存\n- 清理提示:废砂盒满时 App 推送提醒,建议每 5 至 7 天倾倒一次"
    },
    {
      "n": 4,
      "chunk_id": "1960",
      "section_path": "商品规格手册/恒温加热垫(型号 MH-HP12)",
      "question": "恒温加热垫(型号 MH-HP12)",
      "answer": "- 型号:MH-HP12\n- 尺寸:40cm × 30cm\n- 温控:恒温 38℃,内置过热保护,连续通电不超过 12 小时为宜\n- 防护:防水防抓咬电线套管\n- 适用:幼猫、老年猫及冬季保暖"
    },
    {
      "n": 2,
      "chunk_id": "1934",
      "section_path": "售后手册/常见故障自查",
      "question": "常见故障自查",
      "answer": "- 饮水机不出水:检查水位是否低于最低线、水泵是否卡阻,断电清洗水泵后重试。\n- 猫砂盆报错:清空废砂盒并检查滚筒是否卡砂,重启设备;仍报错联系售后。\n- 喂食器卡粮:检查粮食颗粒直径是否超 12mm、粮桶是否受潮结块,清理出粮口后重试。\n- 摄像头离线:确认 Wi-Fi 为 2.4G 频段、信号良好,重启设备或在 App 内重新配网。"
    }
  ],
  "decision": {
    "useful": true,
    "reason": "有喂食器卡粮自查方案",
    "response_kind": "knowledge",
    "source": null
  },
  "answer": "您好！喂食器卡粮不下粮，可以按官方自查方法处理：检查粮食颗粒直径是否超过 12mm、粮桶是否受潮结块，清理出粮口后重试[2]。\n\n如果按以上方法处理后仍无法正常出粮，可联系客服登记后按指引寄修：保修期内核验后免费维修并寄回，超保或人为损坏可能收取工本费，费用会提前告知[10]。\n\n请问还有什么可以帮您的吗？",
  "point_verdicts": [
    {
      "point_id": "p1",
      "covered": true,
      "reason": "回答完整覆盖检查颗粒直径超12mm、粮桶受潮结块、清理出粮口后重试的排查步骤，仅作为自查指引未保证修复，符合条件。"
    }
  ],
  "claim_verdicts": [
    {
      "claim": "喂食器卡粮可检查粮食颗粒直径是否超过12mm、粮桶是否受潮结块，清理出粮口后重试",
      "supported": true,
      "reason": "证据[2]喂食器卡粮自查项与此断言完全一致，支持全部排查步骤。"
    },
    {
      "claim": "若按方法处理后仍无法正常出粮，可联系客服登记后按指引寄修",
      "supported": true,
      "reason": "证据[10]载明保修期内设备故障可联系客服登记后按指引寄回维修点。"
    },
    {
      "claim": "保修期内核验后免费维修并寄回",
      "supported": true,
      "reason": "证据[10]明确保修期内核验后免费维修并寄回。"
    },
    {
      "claim": "超保或人为损坏维修可能收取工本费，费用会提前告知",
      "supported": true,
      "reason": "证据[10]明确超保或人为损坏维修可能收取工本费且费用会提前告知。"
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
    "faithfulness": 1.0,
    "absent_refusal_rate": null,
    "answerable_false_refusal_rate": 0.0
  },
  "error": null,
  "elapsed_ms": 11691.222299821675,
  "judge_snapshot": {
    "prompt_version": "joint-generation-v2.1",
    "finish_reason": "stop"
  },
  "rewrite": {
    "policy_version": "original-query-on-invalid-v1",
    "status": "success",
    "error": null
  },
  "audit": {
    "audit_version": 1,
    "source_map_id": "af6590ab401319d942bddff0b30213a4cd888b8cf115ebd5cdec3adb87687e55",
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
        "chunk_id": 1962,
        "score": 0.032522473484277725,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1934,
        "score": 0.03226646035909653,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1963,
        "score": 0.0320020467042923,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1960,
        "score": 0.015625,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1933,
        "score": 0.015384615398943424,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1953,
        "score": 0.01515151560306549,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1961,
        "score": 0.014925372786819935,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1949,
        "score": 0.014705882407724857,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1955,
        "score": 0.014492753893136978,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1936,
        "score": 0.014285714365541935,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1931,
        "score": 0.014084506779909134,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1977,
        "score": 0.013888888992369175,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1971,
        "score": 0.013698630034923553,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1944,
        "score": 0.013513513840734959,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1947,
        "score": 0.013333333656191826,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1958,
        "score": 0.01315789483487606,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1972,
        "score": 0.012987012974917889,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1975,
        "score": 0.012820512987673283,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1954,
        "score": 0.012658228166401386,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1959,
        "score": 0.012500000186264515,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1935,
        "score": 0.012345679104328156,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1957,
        "score": 0.012195121496915817,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1980,
        "score": 0.012048192322254181,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1956,
        "score": 0.011904762126505375,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1976,
        "score": 0.0117647061124444,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1979,
        "score": 0.011627906933426857,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1940,
        "score": 0.01149425283074379,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1973,
        "score": 0.011363636702299118,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1967,
        "score": 0.01123595517128706,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1950,
        "score": 0.011111111380159855,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1946,
        "score": 0.010989011265337467,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1948,
        "score": 0.010869565419852734,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1939,
        "score": 0.01075268816202879,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1968,
        "score": 0.010638297535479069,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1941,
        "score": 0.010526316240429878,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1945,
        "score": 0.010416666977107525,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1952,
        "score": 0.010309278033673763,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1951,
        "score": 0.010204081423580647,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1937,
        "score": 0.010101010091602802,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1938,
        "score": 0.009999999776482582,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1965,
        "score": 0.009900989942252636,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1970,
        "score": 0.009803921915590763,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1978,
        "score": 0.009708737954497337,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1943,
        "score": 0.009615384973585606,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1966,
        "score": 0.009523809887468815,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1964,
        "score": 0.009433962404727936,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1969,
        "score": 0.009345794096589088,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1942,
        "score": 0.009259259328246117,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1974,
        "score": 0.00917431153357029,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1932,
        "score": 0.00909090880304575,
        "score_kind": "rrf"
      }
    ],
    "final_ranking": [
      {
        "chunk_id": 1962,
        "score": 0.032522473484277725,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1934,
        "score": 0.03226646035909653,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1963,
        "score": 0.0320020467042923,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1960,
        "score": 0.015625,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1933,
        "score": 0.015384615398943424,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1953,
        "score": 0.01515151560306549,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1961,
        "score": 0.014925372786819935,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1949,
        "score": 0.014705882407724857,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1955,
        "score": 0.014492753893136978,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1936,
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
          1934
        ]
      ]
    }
  ],
  "candidate_ids": [
    1962,
    1934,
    1963,
    1960,
    1933,
    1953,
    1961,
    1949,
    1955,
    1936,
    1931,
    1977,
    1971,
    1944,
    1947,
    1958,
    1972,
    1975,
    1954,
    1959,
    1935,
    1957,
    1980,
    1956,
    1976,
    1979,
    1940,
    1973,
    1967,
    1950,
    1946,
    1948,
    1939,
    1968,
    1941,
    1945,
    1952,
    1951,
    1937,
    1938,
    1965,
    1970,
    1978,
    1943,
    1966,
    1964,
    1969,
    1942,
    1974,
    1932
  ],
  "final_ids": [
    1934,
    1962,
    1963,
    1953,
    1955,
    1936,
    1954,
    1933,
    1980,
    1975
  ],
  "prompt_citations": [
    {
      "n": 1,
      "chunk_id": "1934",
      "section_path": "售后手册/常见故障自查",
      "question": "常见故障自查",
      "answer": "- 饮水机不出水:检查水位是否低于最低线、水泵是否卡阻,断电清洗水泵后重试。\n- 猫砂盆报错:清空废砂盒并检查滚筒是否卡砂,重启设备;仍报错联系售后。\n- 喂食器卡粮:检查粮食颗粒直径是否超 12mm、粮桶是否受潮结块,清理出粮口后重试。\n- 摄像头离线:确认 Wi-Fi 为 2.4G 频段、信号良好,重启设备或在 App 内重新配网。"
    },
    {
      "n": 3,
      "chunk_id": "1963",
      "section_path": "商品规格手册/自动喂食器 摄像头版(型号 MH-FD30)",
      "question": "自动喂食器 摄像头版(型号 MH-FD30)",
      "answer": "- 型号:MH-FD30\n- 粮桶容量:6L\n- 核心功能:1080P 摄像头、双向语音、App 远程手动投喂与定时投喂\n- 供电:市电供电 + 内置应急电池\n- 说明:摄像头版支持视频回看,需连接 2.4G Wi-Fi"
    },
    {
      "n": 5,
      "chunk_id": "1955",
      "section_path": "商品规格手册/智能猫砂盆 Max(型号 MH-LP200)",
      "question": "智能猫砂盆 Max(型号 MH-LP200)",
      "answer": "- 型号:MH-LP200\n- 适用猫咪体重:2kg 至 12kg,适合大型猫与多猫家庭\n- 猫砂容量:12L,废砂盒容量约 10 天(单猫)\n- 核心功能:超大滚筒、双重称重防夹、活性炭除臭、App 多猫健康档案\n- 供电:220V 市电\n- 清理提示:多猫家庭建议每 3 至 5 天倾倒一次废砂盒"
    },
    {
      "n": 7,
      "chunk_id": "1954",
      "section_path": "商品规格手册/智能猫砂盆 Lite(型号 MH-LP50)",
      "question": "智能猫砂盆 Lite(型号 MH-LP50)",
      "answer": "- 型号:MH-LP50\n- 适用猫咪体重:1.5kg 至 6kg\n- 猫砂容量:6L\n- 核心功能:自动感应清理、物理除臭盖板;不含 App 联网功能\n- 与 Pro 差异:Lite 无 App 远程监控与健康记录,价格更低,适合单猫家庭"
    },
    {
      "n": 9,
      "chunk_id": "1980",
      "section_path": "猫窝清洗说明/猫窝是否可以机洗",
      "question": "猫窝是否可以机洗",
      "answer": "普通布艺猫窝清洗前拆掉内部垫芯，外套放入洗衣袋，使用轻柔模式冷水洗，自然晾干。不可直接将整只猫窝连垫芯一起机洗，商品另有清洗标签时优先遵循标签。\n\n带加热模块的猫窝不可机洗，应先断电，并按说明书局部擦洗；不得将加热模块、电源或线路浸水。未按清洗说明操作导致的损坏不直接认定为商品质量问题，需要客服核验。\n\n退货仍需符合商品完好、不影响二次销售等适用条件。售后手册中的电子类商品 12 个月保修不能直接套用到普通布艺猫窝；本清洗说明未给出布艺猫窝的独立保修期限。"
    },
    {
      "n": 10,
      "chunk_id": "1975",
      "section_path": "会员权益/生日礼",
      "question": "生日礼",
      "answer": "银卡会员生日当月可领取一份猫零食小样，金卡会员生日当月可领取一份猫罐头礼盒。需在会员中心领取，礼品规格与领取期限以页面标注为准，不承诺额外折现或补偿。"
    },
    {
      "n": 8,
      "chunk_id": "1933",
      "section_path": "售后手册/设备安装与激活",
      "question": "设备安装与激活",
      "answer": "智能设备首次使用需下载「喵喵优选」App,按说明书扫码添加设备并连接 2.4G Wi-Fi 完成激活;猫爬架等非联网商品按随附图解自行组装。"
    },
    {
      "n": 6,
      "chunk_id": "1936",
      "section_path": "售后手册/维修寄修流程",
      "question": "维修寄修流程",
      "answer": "保修期内设备故障,联系客服登记后按指引将设备寄回指定维修点,核验后免费维修并寄回;超保或人为损坏维修可能收取工本费,费用会提前告知。"
    },
    {
      "n": 4,
      "chunk_id": "1953",
      "section_path": "商品规格手册/智能猫砂盆 Pro(型号 MH-LP100)",
      "question": "智能猫砂盆 Pro(型号 MH-LP100)",
      "answer": "- 型号:MH-LP100\n- 适用猫咪体重:1.5kg 至 8kg\n- 猫砂容量:9L,废砂盒容量约 7 天(单猫)\n- 核心功能:自动感应清理、活性炭除臭、App 远程监控与健康记录\n- 供电:220V 市电,断电后配置自动保存\n- 清理提示:废砂盒满时 App 推送提醒,建议每 5 至 7 天倾倒一次"
    },
    {
      "n": 2,
      "chunk_id": "1962",
      "section_path": "商品规格手册/自动喂食器 基础版(型号 MH-FD10)",
      "question": "自动喂食器 基础版(型号 MH-FD10)",
      "answer": "- 型号:MH-FD10\n- 粮桶容量:4L\n- 核心功能:定时定量投喂,每日最多 6 餐,语音呼唤进食\n- 供电:市电供电 + 4 节 5 号电池断电应急\n- 说明:基础版不含摄像头与 App 远程投喂"
    }
  ],
  "decision": {
    "useful": true,
    "reason": "有喂食器卡粮自查步骤",
    "response_kind": "knowledge",
    "source": null
  },
  "answer": "您好！关于喂食器卡粮不下粮的问题，可以按以下方法自查[1]：\n\n1. 检查粮食颗粒直径是否超过 12mm，过大的颗粒容易卡住[1]；\n2. 查看粮桶内的粮食是否受潮结块，如有结块请更换干燥的粮食[1]；\n3. 清理出粮口后重试[1]。\n\n如果按上述方法处理后仍无法解决，建议联系售后进一步处理[1]。请问还有什么可以帮您的吗？",
  "point_verdicts": [
    {
      "point_id": "p1",
      "covered": true,
      "reason": "回答覆盖检查颗粒直径是否超12mm、粮桶受潮结块、清理出粮口后重试三项排查，并保留不保证解决的边界（仍无法解决建议联系售后）。"
    }
  ],
  "claim_verdicts": [
    {
      "claim": "检查粮食颗粒直径是否超过12mm，过大的颗粒容易卡住",
      "supported": true,
      "reason": "证据1明确：喂食器卡粮需检查颗粒直径是否超12mm。"
    },
    {
      "claim": "查看粮桶内的粮食是否受潮结块，如有结块请更换干燥的粮食",
      "supported": true,
      "reason": "证据1提到检查粮桶是否受潮结块；更换干燥粮食为合理排查建议，结块与受潮对应。"
    },
    {
      "claim": "清理出粮口后重试",
      "supported": true,
      "reason": "证据1原文包含清理出粮口后重试。"
    },
    {
      "claim": "如果按上述方法处理后仍无法解决，建议联系售后进一步处理",
      "supported": true,
      "reason": "同类故障处理建议，证据1为官方自查流程，联系售后为证据6支持的合理建议。"
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
  "elapsed_ms": 11392.09880004637,
  "judge_snapshot": {
    "prompt_version": "joint-generation-v2.1",
    "finish_reason": "stop"
  },
  "rewrite": {
    "policy_version": "original-query-on-invalid-v1",
    "status": "success",
    "error": null
  },
  "audit": {
    "audit_version": 1,
    "source_map_id": "af6590ab401319d942bddff0b30213a4cd888b8cf115ebd5cdec3adb87687e55",
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
        "chunk_id": 1962,
        "score": 0.032522473484277725,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1934,
        "score": 0.03226646035909653,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1963,
        "score": 0.0320020467042923,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1960,
        "score": 0.015625,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1933,
        "score": 0.015384615398943424,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1953,
        "score": 0.01515151560306549,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1961,
        "score": 0.014925372786819935,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1949,
        "score": 0.014705882407724857,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1955,
        "score": 0.014492753893136978,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1936,
        "score": 0.014285714365541935,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1931,
        "score": 0.014084506779909134,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1977,
        "score": 0.013888888992369175,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1971,
        "score": 0.013698630034923553,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1944,
        "score": 0.013513513840734959,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1947,
        "score": 0.013333333656191826,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1958,
        "score": 0.01315789483487606,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1972,
        "score": 0.012987012974917889,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1975,
        "score": 0.012820512987673283,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1954,
        "score": 0.012658228166401386,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1959,
        "score": 0.012500000186264515,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1935,
        "score": 0.012345679104328156,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1957,
        "score": 0.012195121496915817,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1980,
        "score": 0.012048192322254181,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1956,
        "score": 0.011904762126505375,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1976,
        "score": 0.0117647061124444,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1979,
        "score": 0.011627906933426857,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1940,
        "score": 0.01149425283074379,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1973,
        "score": 0.011363636702299118,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1967,
        "score": 0.01123595517128706,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1950,
        "score": 0.011111111380159855,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1946,
        "score": 0.010989011265337467,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1948,
        "score": 0.010869565419852734,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1939,
        "score": 0.01075268816202879,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1968,
        "score": 0.010638297535479069,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1941,
        "score": 0.010526316240429878,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1945,
        "score": 0.010416666977107525,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1952,
        "score": 0.010309278033673763,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1951,
        "score": 0.010204081423580647,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1937,
        "score": 0.010101010091602802,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1938,
        "score": 0.009999999776482582,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1965,
        "score": 0.009900989942252636,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1970,
        "score": 0.009803921915590763,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1978,
        "score": 0.009708737954497337,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1943,
        "score": 0.009615384973585606,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1966,
        "score": 0.009523809887468815,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1964,
        "score": 0.009433962404727936,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1969,
        "score": 0.009345794096589088,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1942,
        "score": 0.009259259328246117,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1974,
        "score": 0.00917431153357029,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1932,
        "score": 0.00909090880304575,
        "score_kind": "rrf"
      }
    ],
    "final_ranking": [
      {
        "chunk_id": 1934,
        "score": 0.12065878510475159,
        "score_kind": "rerank"
      },
      {
        "chunk_id": 1962,
        "score": 0.0020288387313485146,
        "score_kind": "rerank"
      },
      {
        "chunk_id": 1963,
        "score": 0.001830295310355723,
        "score_kind": "rerank"
      },
      {
        "chunk_id": 1953,
        "score": 0.0006677493220195174,
        "score_kind": "rerank"
      },
      {
        "chunk_id": 1955,
        "score": 0.0006053760298527777,
        "score_kind": "rerank"
      },
      {
        "chunk_id": 1936,
        "score": 0.0004933086456730962,
        "score_kind": "rerank"
      },
      {
        "chunk_id": 1954,
        "score": 0.0004009127151221037,
        "score_kind": "rerank"
      },
      {
        "chunk_id": 1933,
        "score": 0.0002773849118966609,
        "score_kind": "rerank"
      },
      {
        "chunk_id": 1980,
        "score": 0.00026314170099794865,
        "score_kind": "rerank"
      },
      {
        "chunk_id": 1975,
        "score": 0.0001150245952885598,
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
    1933,
    1975,
    1959,
    1954,
    1980,
    1955,
    1960,
    1944,
    1952,
    1947,
    1953,
    1961,
    1972,
    1977,
    1934,
    1978,
    1940,
    1963,
    1945,
    1935,
    1974,
    1938,
    1937,
    1967,
    1962,
    1968,
    1942,
    1965,
    1970,
    1936,
    1950,
    1941,
    1951,
    1957,
    1939,
    1956,
    1976,
    1971,
    1958,
    1932,
    1948,
    1969,
    1931,
    1973,
    1949,
    1964,
    1946,
    1943,
    1979,
    1966
  ],
  "final_ids": [
    1933,
    1975,
    1959,
    1954,
    1980,
    1955,
    1960,
    1944,
    1952,
    1947
  ],
  "prompt_citations": [
    {
      "n": 1,
      "chunk_id": "1933",
      "section_path": "售后手册/设备安装与激活",
      "question": "设备安装与激活",
      "answer": "智能设备首次使用需下载「喵喵优选」App,按说明书扫码添加设备并连接 2.4G Wi-Fi 完成激活;猫爬架等非联网商品按随附图解自行组装。"
    },
    {
      "n": 3,
      "chunk_id": "1959",
      "section_path": "商品规格手册/大型猫爬架(型号 MH-CT30)",
      "question": "大型猫爬架(型号 MH-CT30)",
      "answer": "- 型号:MH-CT30\n- 高度:1.6m,共四层带顶层吊床\n- 承重:单层最大 10kg\n- 材质:剑麻柱身、绒布平台\n- 安装:需自行组装,随附六角扳手与图解说明书"
    },
    {
      "n": 5,
      "chunk_id": "1980",
      "section_path": "猫窝清洗说明/猫窝是否可以机洗",
      "question": "猫窝是否可以机洗",
      "answer": "普通布艺猫窝清洗前拆掉内部垫芯，外套放入洗衣袋，使用轻柔模式冷水洗，自然晾干。不可直接将整只猫窝连垫芯一起机洗，商品另有清洗标签时优先遵循标签。\n\n带加热模块的猫窝不可机洗，应先断电，并按说明书局部擦洗；不得将加热模块、电源或线路浸水。未按清洗说明操作导致的损坏不直接认定为商品质量问题，需要客服核验。\n\n退货仍需符合商品完好、不影响二次销售等适用条件。售后手册中的电子类商品 12 个月保修不能直接套用到普通布艺猫窝；本清洗说明未给出布艺猫窝的独立保修期限。"
    },
    {
      "n": 7,
      "chunk_id": "1960",
      "section_path": "商品规格手册/恒温加热垫(型号 MH-HP12)",
      "question": "恒温加热垫(型号 MH-HP12)",
      "answer": "- 型号:MH-HP12\n- 尺寸:40cm × 30cm\n- 温控:恒温 38℃,内置过热保护,连续通电不超过 12 小时为宜\n- 防护:防水防抓咬电线套管\n- 适用:幼猫、老年猫及冬季保暖"
    },
    {
      "n": 9,
      "chunk_id": "1952",
      "section_path": "商品规格手册",
      "question": "商品规格手册",
      "answer": "本手册收录喵喵优选自营智能硬件的型号、规格与使用要点,便于按具体型号查询。"
    },
    {
      "n": 10,
      "chunk_id": "1947",
      "section_path": "商品与购物 FAQ/配送范围与偏远地区",
      "question": "配送范围与偏远地区",
      "answer": "全国大部分地区支持配送,新疆、西藏、内蒙古等偏远地区运费另计且时效顺延;港澳台及海外暂不支持自营配送。"
    },
    {
      "n": 8,
      "chunk_id": "1944",
      "section_path": "商品与购物 FAQ/支持哪些支付方式",
      "question": "支持哪些支付方式",
      "answer": "下单支持支付宝、微信支付与主流银行储蓄卡/信用卡在线支付。暂不支持线下汇款,支付遇到问题可重试或更换支付方式。"
    },
    {
      "n": 6,
      "chunk_id": "1955",
      "section_path": "商品规格手册/智能猫砂盆 Max(型号 MH-LP200)",
      "question": "智能猫砂盆 Max(型号 MH-LP200)",
      "answer": "- 型号:MH-LP200\n- 适用猫咪体重:2kg 至 12kg,适合大型猫与多猫家庭\n- 猫砂容量:12L,废砂盒容量约 10 天(单猫)\n- 核心功能:超大滚筒、双重称重防夹、活性炭除臭、App 多猫健康档案\n- 供电:220V 市电\n- 清理提示:多猫家庭建议每 3 至 5 天倾倒一次废砂盒"
    },
    {
      "n": 4,
      "chunk_id": "1954",
      "section_path": "商品规格手册/智能猫砂盆 Lite(型号 MH-LP50)",
      "question": "智能猫砂盆 Lite(型号 MH-LP50)",
      "answer": "- 型号:MH-LP50\n- 适用猫咪体重:1.5kg 至 6kg\n- 猫砂容量:6L\n- 核心功能:自动感应清理、物理除臭盖板;不含 App 联网功能\n- 与 Pro 差异:Lite 无 App 远程监控与健康记录,价格更低,适合单猫家庭"
    },
    {
      "n": 2,
      "chunk_id": "1975",
      "section_path": "会员权益/生日礼",
      "question": "生日礼",
      "answer": "银卡会员生日当月可领取一份猫零食小样，金卡会员生日当月可领取一份猫罐头礼盒。需在会员中心领取，礼品规格与领取期限以页面标注为准，不承诺额外折现或补偿。"
    }
  ],
  "decision": {
    "useful": false,
    "reason": "证据只涉及宠物用品，无售卖活体宠物的信息",
    "response_kind": "knowledge",
    "source": "self_check"
  },
  "answer": "目前的知识资料不足以确认这个问题，我无法给出可靠答案。请补充具体商品或适用条件，或联系人工客服确认。",
  "point_verdicts": [],
  "claim_verdicts": [
    {
      "claim": "目前的知识资料不足以确认是否售卖活体宠物（能否买猫）",
      "supported": true,
      "reason": "supporting_evidence 中没有任何资料涉及活体宠物销售，证据整体沉默，该无法确认的表述与证据状态一致"
    },
    {
      "claim": "建议补充具体商品或适用条件，或联系人工客服确认",
      "supported": true,
      "reason": "这是无事实前提的建议性话术，证据中商品资料均为具体型号商品，建议与证据不冲突"
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
  "elapsed_ms": 6220.617699902505,
  "judge_snapshot": {
    "prompt_version": "joint-generation-v2.1",
    "finish_reason": "stop"
  },
  "rewrite": {
    "policy_version": "original-query-on-invalid-v1",
    "status": "success",
    "error": null
  },
  "audit": {
    "audit_version": 1,
    "source_map_id": "af6590ab401319d942bddff0b30213a4cd888b8cf115ebd5cdec3adb87687e55",
    "gold_groups": [],
    "answer_points": [],
    "candidate_ranking": [
      {
        "chunk_id": 1933,
        "score": 0.5230516195297241,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1975,
        "score": 0.5179657936096191,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1959,
        "score": 0.5067923069000244,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1954,
        "score": 0.4862222671508789,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1980,
        "score": 0.4831678867340088,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1955,
        "score": 0.4767383337020874,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1960,
        "score": 0.4722388684749603,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1944,
        "score": 0.4711533784866333,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1952,
        "score": 0.46554359793663025,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1947,
        "score": 0.46494314074516296,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1953,
        "score": 0.4634160101413727,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1961,
        "score": 0.4622555077075958,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1972,
        "score": 0.46218544244766235,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1977,
        "score": 0.4522022306919098,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1934,
        "score": 0.41445615887641907,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1978,
        "score": 0.4099642038345337,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1940,
        "score": 0.40904730558395386,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1963,
        "score": 0.39853614568710327,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1945,
        "score": 0.3965839445590973,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1935,
        "score": 0.396505743265152,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1974,
        "score": 0.3954104483127594,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1938,
        "score": 0.3926236033439636,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1937,
        "score": 0.38972947001457214,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1967,
        "score": 0.38856935501098633,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1962,
        "score": 0.3846847414970398,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1968,
        "score": 0.3840557634830475,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1942,
        "score": 0.3832646608352661,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1965,
        "score": 0.3810376524925232,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1970,
        "score": 0.3806926906108856,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1936,
        "score": 0.37865543365478516,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1950,
        "score": 0.37787264585494995,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1941,
        "score": 0.37357136607170105,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1951,
        "score": 0.373079389333725,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1957,
        "score": 0.3704777956008911,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1939,
        "score": 0.3690685033798218,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1956,
        "score": 0.3668852746486664,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1976,
        "score": 0.3662397265434265,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1971,
        "score": 0.3630025088787079,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1958,
        "score": 0.36236444115638733,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1932,
        "score": 0.3607848882675171,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1948,
        "score": 0.3583538830280304,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1969,
        "score": 0.35454055666923523,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1931,
        "score": 0.3537989854812622,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1973,
        "score": 0.3536772131919861,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1949,
        "score": 0.35167378187179565,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1964,
        "score": 0.34836363792419434,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1946,
        "score": 0.34145939350128174,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1943,
        "score": 0.33695530891418457,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1979,
        "score": 0.3166200518608093,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1966,
        "score": 0.31414279341697693,
        "score_kind": "cosine"
      }
    ],
    "final_ranking": [
      {
        "chunk_id": 1933,
        "score": 0.5230516195297241,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1975,
        "score": 0.5179657936096191,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1959,
        "score": 0.5067923069000244,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1954,
        "score": 0.4862222671508789,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1980,
        "score": 0.4831678867340088,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1955,
        "score": 0.4767383337020874,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1960,
        "score": 0.4722388684749603,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1944,
        "score": 0.4711533784866333,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1952,
        "score": 0.46554359793663025,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1947,
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
    1948,
    1980,
    1934,
    1955,
    1975,
    1946,
    1932,
    1977,
    1939,
    1972,
    1943,
    1949,
    1950,
    1959,
    1960,
    1933,
    1945,
    1971,
    1961,
    1954,
    1974,
    1953,
    1979
  ],
  "final_ids": [
    1948,
    1980,
    1934,
    1955,
    1975,
    1946,
    1932,
    1977,
    1939,
    1972
  ],
  "prompt_citations": [
    {
      "n": 1,
      "chunk_id": "1948",
      "section_path": "商品与购物 FAQ/订单可以修改或取消吗",
      "question": "订单可以修改或取消吗",
      "answer": "订单未发货前可在「我的订单」自助取消;已发货订单无法修改收货信息,可拒收后走退款流程。修改商品数量需取消后重新下单。"
    },
    {
      "n": 3,
      "chunk_id": "1934",
      "section_path": "售后手册/常见故障自查",
      "question": "常见故障自查",
      "answer": "- 饮水机不出水:检查水位是否低于最低线、水泵是否卡阻,断电清洗水泵后重试。\n- 猫砂盆报错:清空废砂盒并检查滚筒是否卡砂,重启设备;仍报错联系售后。\n- 喂食器卡粮:检查粮食颗粒直径是否超 12mm、粮桶是否受潮结块,清理出粮口后重试。\n- 摄像头离线:确认 Wi-Fi 为 2.4G 频段、信号良好,重启设备或在 App 内重新配网。"
    },
    {
      "n": 5,
      "chunk_id": "1975",
      "section_path": "会员权益/生日礼",
      "question": "生日礼",
      "answer": "银卡会员生日当月可领取一份猫零食小样，金卡会员生日当月可领取一份猫罐头礼盒。需在会员中心领取，礼品规格与领取期限以页面标注为准，不承诺额外折现或补偿。"
    },
    {
      "n": 7,
      "chunk_id": "1932",
      "section_path": "售后手册/保修说明",
      "question": "保修说明",
      "answer": "电子类商品保修 12 个月,自签收日起算;人为损坏不在保修范围。"
    },
    {
      "n": 9,
      "chunk_id": "1939",
      "section_path": "商品与购物 FAQ/如何申请退款",
      "question": "如何申请退款",
      "answer": "在「我的订单」找到对应订单点击「申请退款」,按提示提交,审核通过后原路退回。"
    },
    {
      "n": 10,
      "chunk_id": "1972",
      "section_path": "退货退款政策/不支持退货的商品",
      "question": "不支持退货的商品",
      "answer": "定制类、生鲜类、已拆封的猫砂等消耗品,以及标注「不支持无理由退货」的商品,非质量问题不支持退货。"
    },
    {
      "n": 8,
      "chunk_id": "1977",
      "section_path": "积分规则/积分怎么用",
      "question": "积分怎么用",
      "answer": "积分可在结算时抵扣商品金额，100 积分抵 1 元现金，单笔订单最多抵 30 元，不用于抵扣偏远地区附加运费，也不支持直接提现。\n\n2000 积分可兑换自动饮水机滤芯 3 片，该兑换套装适用于 MH-W40，普通配送地区包邮；偏远地区附加配送费仍需按页面规则确认。MH-W40 的滤芯更换周期以商品规格手册为准。\n\n800 积分可兑换猫零食小样，普通配送地区另收 6 元运费；该兑换不直接套用普通购物订单的满 99 元包邮规则。兑换商品、可用库存及偏远地区配送规则以兑换页面标注为准。"
    },
    {
      "n": 6,
      "chunk_id": "1946",
      "section_path": "商品与购物 FAQ/优惠券和满减怎么用",
      "question": "优惠券和满减怎么用",
      "answer": "优惠券在结算页「使用优惠券」中勾选,满减活动自动叠加在商品页标示的门槛上;同一订单一般限用一张店铺券,活动细则以页面为准。"
    },
    {
      "n": 4,
      "chunk_id": "1955",
      "section_path": "商品规格手册/智能猫砂盆 Max(型号 MH-LP200)",
      "question": "智能猫砂盆 Max(型号 MH-LP200)",
      "answer": "- 型号:MH-LP200\n- 适用猫咪体重:2kg 至 12kg,适合大型猫与多猫家庭\n- 猫砂容量:12L,废砂盒容量约 10 天(单猫)\n- 核心功能:超大滚筒、双重称重防夹、活性炭除臭、App 多猫健康档案\n- 供电:220V 市电\n- 清理提示:多猫家庭建议每 3 至 5 天倾倒一次废砂盒"
    },
    {
      "n": 2,
      "chunk_id": "1980",
      "section_path": "猫窝清洗说明/猫窝是否可以机洗",
      "question": "猫窝是否可以机洗",
      "answer": "普通布艺猫窝清洗前拆掉内部垫芯，外套放入洗衣袋，使用轻柔模式冷水洗，自然晾干。不可直接将整只猫窝连垫芯一起机洗，商品另有清洗标签时优先遵循标签。\n\n带加热模块的猫窝不可机洗，应先断电，并按说明书局部擦洗；不得将加热模块、电源或线路浸水。未按清洗说明操作导致的损坏不直接认定为商品质量问题，需要客服核验。\n\n退货仍需符合商品完好、不影响二次销售等适用条件。售后手册中的电子类商品 12 个月保修不能直接套用到普通布艺猫窝；本清洗说明未给出布艺猫窝的独立保修期限。"
    }
  ],
  "decision": {
    "useful": false,
    "reason": "无证据说明是否售卖活体宠物",
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
  "elapsed_ms": 4276.310400106013,
  "judge_snapshot": {
    "prompt_version": "joint-generation-v2.1",
    "finish_reason": "stop"
  },
  "rewrite": {
    "policy_version": "original-query-on-invalid-v1",
    "status": "success",
    "error": null
  },
  "audit": {
    "audit_version": 1,
    "source_map_id": "af6590ab401319d942bddff0b30213a4cd888b8cf115ebd5cdec3adb87687e55",
    "gold_groups": [],
    "answer_points": [],
    "candidate_ranking": [
      {
        "chunk_id": 1948,
        "score": 5.146595478057861,
        "score_kind": "bm25"
      },
      {
        "chunk_id": 1980,
        "score": 2.217597484588623,
        "score_kind": "bm25"
      },
      {
        "chunk_id": 1934,
        "score": 2.203824281692505,
        "score_kind": "bm25"
      },
      {
        "chunk_id": 1955,
        "score": 2.051485300064087,
        "score_kind": "bm25"
      },
      {
        "chunk_id": 1975,
        "score": 1.9893113374710083,
        "score_kind": "bm25"
      },
      {
        "chunk_id": 1946,
        "score": 1.9015036821365356,
        "score_kind": "bm25"
      },
      {
        "chunk_id": 1932,
        "score": 1.7063724994659424,
        "score_kind": "bm25"
      },
      {
        "chunk_id": 1977,
        "score": 1.6996121406555176,
        "score_kind": "bm25"
      },
      {
        "chunk_id": 1939,
        "score": 1.6403803825378418,
        "score_kind": "bm25"
      },
      {
        "chunk_id": 1972,
        "score": 1.5823721885681152,
        "score_kind": "bm25"
      },
      {
        "chunk_id": 1943,
        "score": 1.5647372007369995,
        "score_kind": "bm25"
      },
      {
        "chunk_id": 1949,
        "score": 1.536397933959961,
        "score_kind": "bm25"
      },
      {
        "chunk_id": 1950,
        "score": 1.5090670585632324,
        "score_kind": "bm25"
      },
      {
        "chunk_id": 1959,
        "score": 1.5028752088546753,
        "score_kind": "bm25"
      },
      {
        "chunk_id": 1960,
        "score": 1.5028752088546753,
        "score_kind": "bm25"
      },
      {
        "chunk_id": 1933,
        "score": 1.4903959035873413,
        "score_kind": "bm25"
      },
      {
        "chunk_id": 1945,
        "score": 1.469846248626709,
        "score_kind": "bm25"
      },
      {
        "chunk_id": 1971,
        "score": 1.4572218656539917,
        "score_kind": "bm25"
      },
      {
        "chunk_id": 1961,
        "score": 1.4309837818145752,
        "score_kind": "bm25"
      },
      {
        "chunk_id": 1954,
        "score": 1.3656563758850098,
        "score_kind": "bm25"
      },
      {
        "chunk_id": 1974,
        "score": 1.2454544305801392,
        "score_kind": "bm25"
      },
      {
        "chunk_id": 1953,
        "score": 1.217445969581604,
        "score_kind": "bm25"
      },
      {
        "chunk_id": 1979,
        "score": 1.0986462831497192,
        "score_kind": "bm25"
      }
    ],
    "final_ranking": [
      {
        "chunk_id": 1948,
        "score": 5.146595478057861,
        "score_kind": "bm25"
      },
      {
        "chunk_id": 1980,
        "score": 2.217597484588623,
        "score_kind": "bm25"
      },
      {
        "chunk_id": 1934,
        "score": 2.203824281692505,
        "score_kind": "bm25"
      },
      {
        "chunk_id": 1955,
        "score": 2.051485300064087,
        "score_kind": "bm25"
      },
      {
        "chunk_id": 1975,
        "score": 1.9893113374710083,
        "score_kind": "bm25"
      },
      {
        "chunk_id": 1946,
        "score": 1.9015036821365356,
        "score_kind": "bm25"
      },
      {
        "chunk_id": 1932,
        "score": 1.7063724994659424,
        "score_kind": "bm25"
      },
      {
        "chunk_id": 1977,
        "score": 1.6996121406555176,
        "score_kind": "bm25"
      },
      {
        "chunk_id": 1939,
        "score": 1.6403803825378418,
        "score_kind": "bm25"
      },
      {
        "chunk_id": 1972,
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
    1975,
    1980,
    1955,
    1933,
    1959,
    1934,
    1960,
    1977,
    1954,
    1972,
    1961,
    1948,
    1953,
    1945,
    1939,
    1932,
    1974,
    1950,
    1946,
    1949,
    1943,
    1971,
    1979,
    1944,
    1952,
    1947,
    1978,
    1940,
    1963,
    1935,
    1938,
    1937,
    1967,
    1962,
    1968,
    1942,
    1965,
    1970,
    1936,
    1941,
    1951,
    1957,
    1956,
    1976,
    1958,
    1969,
    1931,
    1973,
    1964,
    1966
  ],
  "final_ids": [
    1975,
    1980,
    1955,
    1933,
    1959,
    1934,
    1960,
    1977,
    1954,
    1972
  ],
  "prompt_citations": [
    {
      "n": 1,
      "chunk_id": "1975",
      "section_path": "会员权益/生日礼",
      "question": "生日礼",
      "answer": "银卡会员生日当月可领取一份猫零食小样，金卡会员生日当月可领取一份猫罐头礼盒。需在会员中心领取，礼品规格与领取期限以页面标注为准，不承诺额外折现或补偿。"
    },
    {
      "n": 3,
      "chunk_id": "1955",
      "section_path": "商品规格手册/智能猫砂盆 Max(型号 MH-LP200)",
      "question": "智能猫砂盆 Max(型号 MH-LP200)",
      "answer": "- 型号:MH-LP200\n- 适用猫咪体重:2kg 至 12kg,适合大型猫与多猫家庭\n- 猫砂容量:12L,废砂盒容量约 10 天(单猫)\n- 核心功能:超大滚筒、双重称重防夹、活性炭除臭、App 多猫健康档案\n- 供电:220V 市电\n- 清理提示:多猫家庭建议每 3 至 5 天倾倒一次废砂盒"
    },
    {
      "n": 5,
      "chunk_id": "1959",
      "section_path": "商品规格手册/大型猫爬架(型号 MH-CT30)",
      "question": "大型猫爬架(型号 MH-CT30)",
      "answer": "- 型号:MH-CT30\n- 高度:1.6m,共四层带顶层吊床\n- 承重:单层最大 10kg\n- 材质:剑麻柱身、绒布平台\n- 安装:需自行组装,随附六角扳手与图解说明书"
    },
    {
      "n": 7,
      "chunk_id": "1960",
      "section_path": "商品规格手册/恒温加热垫(型号 MH-HP12)",
      "question": "恒温加热垫(型号 MH-HP12)",
      "answer": "- 型号:MH-HP12\n- 尺寸:40cm × 30cm\n- 温控:恒温 38℃,内置过热保护,连续通电不超过 12 小时为宜\n- 防护:防水防抓咬电线套管\n- 适用:幼猫、老年猫及冬季保暖"
    },
    {
      "n": 9,
      "chunk_id": "1954",
      "section_path": "商品规格手册/智能猫砂盆 Lite(型号 MH-LP50)",
      "question": "智能猫砂盆 Lite(型号 MH-LP50)",
      "answer": "- 型号:MH-LP50\n- 适用猫咪体重:1.5kg 至 6kg\n- 猫砂容量:6L\n- 核心功能:自动感应清理、物理除臭盖板;不含 App 联网功能\n- 与 Pro 差异:Lite 无 App 远程监控与健康记录,价格更低,适合单猫家庭"
    },
    {
      "n": 10,
      "chunk_id": "1972",
      "section_path": "退货退款政策/不支持退货的商品",
      "question": "不支持退货的商品",
      "answer": "定制类、生鲜类、已拆封的猫砂等消耗品,以及标注「不支持无理由退货」的商品,非质量问题不支持退货。"
    },
    {
      "n": 8,
      "chunk_id": "1977",
      "section_path": "积分规则/积分怎么用",
      "question": "积分怎么用",
      "answer": "积分可在结算时抵扣商品金额，100 积分抵 1 元现金，单笔订单最多抵 30 元，不用于抵扣偏远地区附加运费，也不支持直接提现。\n\n2000 积分可兑换自动饮水机滤芯 3 片，该兑换套装适用于 MH-W40，普通配送地区包邮；偏远地区附加配送费仍需按页面规则确认。MH-W40 的滤芯更换周期以商品规格手册为准。\n\n800 积分可兑换猫零食小样，普通配送地区另收 6 元运费；该兑换不直接套用普通购物订单的满 99 元包邮规则。兑换商品、可用库存及偏远地区配送规则以兑换页面标注为准。"
    },
    {
      "n": 6,
      "chunk_id": "1934",
      "section_path": "售后手册/常见故障自查",
      "question": "常见故障自查",
      "answer": "- 饮水机不出水:检查水位是否低于最低线、水泵是否卡阻,断电清洗水泵后重试。\n- 猫砂盆报错:清空废砂盒并检查滚筒是否卡砂,重启设备;仍报错联系售后。\n- 喂食器卡粮:检查粮食颗粒直径是否超 12mm、粮桶是否受潮结块,清理出粮口后重试。\n- 摄像头离线:确认 Wi-Fi 为 2.4G 频段、信号良好,重启设备或在 App 内重新配网。"
    },
    {
      "n": 4,
      "chunk_id": "1933",
      "section_path": "售后手册/设备安装与激活",
      "question": "设备安装与激活",
      "answer": "智能设备首次使用需下载「喵喵优选」App,按说明书扫码添加设备并连接 2.4G Wi-Fi 完成激活;猫爬架等非联网商品按随附图解自行组装。"
    },
    {
      "n": 2,
      "chunk_id": "1980",
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
  "elapsed_ms": 4487.043700180948,
  "judge_snapshot": {
    "prompt_version": "joint-generation-v2.1",
    "finish_reason": "stop"
  },
  "rewrite": {
    "policy_version": "original-query-on-invalid-v1",
    "status": "success",
    "error": null
  },
  "audit": {
    "audit_version": 1,
    "source_map_id": "af6590ab401319d942bddff0b30213a4cd888b8cf115ebd5cdec3adb87687e55",
    "gold_groups": [],
    "answer_points": [],
    "candidate_ranking": [
      {
        "chunk_id": 1975,
        "score": 0.03151364624500275,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1980,
        "score": 0.03151364624500275,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1955,
        "score": 0.03077651560306549,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1933,
        "score": 0.02955133654177189,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1959,
        "score": 0.029386531561613083,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1934,
        "score": 0.029206350445747375,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1960,
        "score": 0.028258707374334335,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1977,
        "score": 0.028219396248459816,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1954,
        "score": 0.02812499925494194,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1972,
        "score": 0.027984343469142914,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1961,
        "score": 0.02654711715877056,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1948,
        "score": 0.02629443258047104,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1953,
        "score": 0.02627962827682495,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1945,
        "score": 0.025645241141319275,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1939,
        "score": 0.025019070133566856,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1932,
        "score": 0.02492537349462509,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1974,
        "score": 0.02469135820865631,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1950,
        "score": 0.024687640368938446,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1946,
        "score": 0.02449730969965458,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1949,
        "score": 0.02341269887983799,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1943,
        "score": 0.02334376610815525,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1971,
        "score": 0.02302459441125393,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1979,
        "score": 0.02122250385582447,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1944,
        "score": 0.014705882407724857,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1952,
        "score": 0.014492753893136978,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1947,
        "score": 0.014285714365541935,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1978,
        "score": 0.01315789483487606,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1940,
        "score": 0.012987012974917889,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1963,
        "score": 0.012820512987673283,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1935,
        "score": 0.012500000186264515,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1938,
        "score": 0.012195121496915817,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1937,
        "score": 0.012048192322254181,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1967,
        "score": 0.011904762126505375,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1962,
        "score": 0.0117647061124444,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1968,
        "score": 0.011627906933426857,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1942,
        "score": 0.01149425283074379,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1965,
        "score": 0.011363636702299118,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1970,
        "score": 0.01123595517128706,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1936,
        "score": 0.011111111380159855,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1941,
        "score": 0.010869565419852734,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1951,
        "score": 0.01075268816202879,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1957,
        "score": 0.010638297535479069,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1956,
        "score": 0.010416666977107525,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1976,
        "score": 0.010309278033673763,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1958,
        "score": 0.010101010091602802,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1969,
        "score": 0.009803921915590763,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1931,
        "score": 0.009708737954497337,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1973,
        "score": 0.009615384973585606,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1964,
        "score": 0.009433962404727936,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1966,
        "score": 0.00909090880304575,
        "score_kind": "rrf"
      }
    ],
    "final_ranking": [
      {
        "chunk_id": 1975,
        "score": 0.03151364624500275,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1980,
        "score": 0.03151364624500275,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1955,
        "score": 0.03077651560306549,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1933,
        "score": 0.02955133654177189,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1959,
        "score": 0.029386531561613083,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1934,
        "score": 0.029206350445747375,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1960,
        "score": 0.028258707374334335,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1977,
        "score": 0.028219396248459816,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1954,
        "score": 0.02812499925494194,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1972,
        "score": 0.027984343469142914,
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
    1975,
    1980,
    1955,
    1933,
    1959,
    1934,
    1960,
    1977,
    1954,
    1972,
    1961,
    1948,
    1953,
    1945,
    1939,
    1932,
    1974,
    1950,
    1946,
    1949,
    1943,
    1971,
    1979,
    1944,
    1952,
    1947,
    1978,
    1940,
    1963,
    1935,
    1938,
    1937,
    1967,
    1962,
    1968,
    1942,
    1965,
    1970,
    1936,
    1941,
    1951,
    1957,
    1956,
    1976,
    1958,
    1969,
    1931,
    1973,
    1964,
    1966
  ],
  "final_ids": [
    1975,
    1972,
    1947,
    1938,
    1969,
    1965,
    1974,
    1968,
    1937,
    1945
  ],
  "prompt_citations": [
    {
      "n": 1,
      "chunk_id": "1975",
      "section_path": "会员权益/生日礼",
      "question": "生日礼",
      "answer": "银卡会员生日当月可领取一份猫零食小样，金卡会员生日当月可领取一份猫罐头礼盒。需在会员中心领取，礼品规格与领取期限以页面标注为准，不承诺额外折现或补偿。"
    },
    {
      "n": 3,
      "chunk_id": "1947",
      "section_path": "商品与购物 FAQ/配送范围与偏远地区",
      "question": "配送范围与偏远地区",
      "answer": "全国大部分地区支持配送,新疆、西藏、内蒙古等偏远地区运费另计且时效顺延;港澳台及海外暂不支持自营配送。"
    },
    {
      "n": 5,
      "chunk_id": "1969",
      "section_path": "退货退款政策/退换货运费承担",
      "question": "退换货运费承担",
      "answer": "无理由退货的退回运费由买家承担;因商品质量问题、发错货、少发漏发导致的退换货,运费由平台承担。运费承担以平台售后规则最终判定为准。"
    },
    {
      "n": 7,
      "chunk_id": "1974",
      "section_path": "会员权益/会员等级",
      "question": "会员等级",
      "answer": "会员分为普通、银卡和金卡三档，按有效累计消费金额自动升级，不按年度消费金额计算。累计消费未满 1000 元为普通会员，满 1000 元起为银卡，满 5000 元起为金卡。\n\n有效累计消费指已完成订单的商品实际支付金额，不含配送费；退货退款部分从有效累计消费中扣除。退款后根据更新的累计消费重新计算等级，未达到原门槛时可能降级。等级与适用权益在会员中心展示。\n\n银卡在参与会员折扣的商品上享 95 折，金卡享 9 折。折扣适用商品和活动范围以结算页面标注为准。会员折扣、优惠券与满减是否叠加也以当次活动页面为准，不能一概承诺全部优惠同时生效。"
    },
    {
      "n": 9,
      "chunk_id": "1937",
      "section_path": "售后手册/会员专属售后权益",
      "question": "会员专属售后权益",
      "answer": "金卡会员享优先客服接入与上门取件退换货;银卡会员享退换货运费权益 1 次/月。具体权益以会员中心页面标注为准。"
    },
    {
      "n": 10,
      "chunk_id": "1945",
      "section_path": "商品与购物 FAQ/会员等级与积分规则",
      "question": "会员等级与积分规则",
      "answer": "会员分为普通、银卡、金卡三档,按累计消费自动升级。每消费 1 元得 1 积分,积分可在结算时抵扣,100 积分抵 1 元。"
    },
    {
      "n": 8,
      "chunk_id": "1968",
      "section_path": "退货退款政策/换货政策/换货运费",
      "question": "换货运费",
      "answer": "非质量问题的换货,往返运费由买家承担;因质量问题或发错货的换货,往返运费由平台承担。"
    },
    {
      "n": 6,
      "chunk_id": "1965",
      "section_path": "退货退款政策/无理由退货/适用范围",
      "question": "适用范围",
      "answer": "自签收之日起 7 天内,商品完好、不影响二次销售的,支持无理由退货。定制类、生鲜类商品除外。"
    },
    {
      "n": 4,
      "chunk_id": "1938",
      "section_path": "商品与购物 FAQ/退货政策是什么",
      "question": "退货政策是什么",
      "answer": "支持 7 天无理由退货,商品需保持完好、不影响二次销售,具体以平台售后规则为准。"
    },
    {
      "n": 2,
      "chunk_id": "1972",
      "section_path": "退货退款政策/不支持退货的商品",
      "question": "不支持退货的商品",
      "answer": "定制类、生鲜类、已拆封的猫砂等消耗品,以及标注「不支持无理由退货」的商品,非质量问题不支持退货。"
    }
  ],
  "decision": {
    "useful": false,
    "reason": "无证据说明是否销售活体宠物",
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
  "elapsed_ms": 5454.951399937272,
  "judge_snapshot": {
    "prompt_version": "joint-generation-v2.1",
    "finish_reason": "stop"
  },
  "rewrite": {
    "policy_version": "original-query-on-invalid-v1",
    "status": "success",
    "error": null
  },
  "audit": {
    "audit_version": 1,
    "source_map_id": "af6590ab401319d942bddff0b30213a4cd888b8cf115ebd5cdec3adb87687e55",
    "gold_groups": [],
    "answer_points": [],
    "candidate_ranking": [
      {
        "chunk_id": 1975,
        "score": 0.03151364624500275,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1980,
        "score": 0.03151364624500275,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1955,
        "score": 0.03077651560306549,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1933,
        "score": 0.02955133654177189,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1959,
        "score": 0.029386531561613083,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1934,
        "score": 0.029206350445747375,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1960,
        "score": 0.028258707374334335,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1977,
        "score": 0.028219396248459816,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1954,
        "score": 0.02812499925494194,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1972,
        "score": 0.027984343469142914,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1961,
        "score": 0.02654711715877056,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1948,
        "score": 0.02629443258047104,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1953,
        "score": 0.02627962827682495,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1945,
        "score": 0.025645241141319275,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1939,
        "score": 0.025019070133566856,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1932,
        "score": 0.02492537349462509,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1974,
        "score": 0.02469135820865631,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1950,
        "score": 0.024687640368938446,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1946,
        "score": 0.02449730969965458,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1949,
        "score": 0.02341269887983799,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1943,
        "score": 0.02334376610815525,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1971,
        "score": 0.02302459441125393,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1979,
        "score": 0.02122250385582447,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1944,
        "score": 0.014705882407724857,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1952,
        "score": 0.014492753893136978,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1947,
        "score": 0.014285714365541935,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1978,
        "score": 0.01315789483487606,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1940,
        "score": 0.012987012974917889,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1963,
        "score": 0.012820512987673283,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1935,
        "score": 0.012500000186264515,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1938,
        "score": 0.012195121496915817,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1937,
        "score": 0.012048192322254181,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1967,
        "score": 0.011904762126505375,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1962,
        "score": 0.0117647061124444,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1968,
        "score": 0.011627906933426857,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1942,
        "score": 0.01149425283074379,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1965,
        "score": 0.011363636702299118,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1970,
        "score": 0.01123595517128706,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1936,
        "score": 0.011111111380159855,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1941,
        "score": 0.010869565419852734,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1951,
        "score": 0.01075268816202879,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1957,
        "score": 0.010638297535479069,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1956,
        "score": 0.010416666977107525,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1976,
        "score": 0.010309278033673763,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1958,
        "score": 0.010101010091602802,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1969,
        "score": 0.009803921915590763,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1931,
        "score": 0.009708737954497337,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1973,
        "score": 0.009615384973585606,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1964,
        "score": 0.009433962404727936,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1966,
        "score": 0.00909090880304575,
        "score_kind": "rrf"
      }
    ],
    "final_ranking": [
      {
        "chunk_id": 1975,
        "score": 0.002305577974766493,
        "score_kind": "rerank"
      },
      {
        "chunk_id": 1972,
        "score": 0.0022078740876168013,
        "score_kind": "rerank"
      },
      {
        "chunk_id": 1947,
        "score": 0.0007817724253982306,
        "score_kind": "rerank"
      },
      {
        "chunk_id": 1938,
        "score": 0.0006711307214573026,
        "score_kind": "rerank"
      },
      {
        "chunk_id": 1969,
        "score": 0.0006385192391462624,
        "score_kind": "rerank"
      },
      {
        "chunk_id": 1965,
        "score": 0.0005955551750957966,
        "score_kind": "rerank"
      },
      {
        "chunk_id": 1974,
        "score": 0.0005537996185012162,
        "score_kind": "rerank"
      },
      {
        "chunk_id": 1968,
        "score": 0.0005302883801050484,
        "score_kind": "rerank"
      },
      {
        "chunk_id": 1937,
        "score": 0.00048264750512316823,
        "score_kind": "rerank"
      },
      {
        "chunk_id": 1945,
        "score": 0.00048140966100618243,
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
    1978,
    1943,
    1979,
    1971,
    1939,
    1936,
    1931,
    1932,
    1973,
    1967,
    1970,
    1965,
    1937,
    1948,
    1940,
    1950,
    1968,
    1966,
    1977,
    1969,
    1938,
    1949,
    1972,
    1935,
    1941,
    1944,
    1951,
    1946,
    1934,
    1976,
    1942,
    1947,
    1975,
    1952,
    1974,
    1958,
    1933,
    1945,
    1957,
    1956,
    1962,
    1963,
    1961,
    1980,
    1964,
    1953,
    1955,
    1959,
    1954,
    1960
  ],
  "final_ids": [
    1978,
    1943,
    1979,
    1971,
    1939,
    1936,
    1931,
    1932,
    1973,
    1967
  ],
  "prompt_citations": [
    {
      "n": 1,
      "chunk_id": "1978",
      "section_path": "开票细则/可开票类型",
      "question": "可开票类型",
      "answer": "本演示店提供电子普通发票、电子专用发票和纸质专用发票。电子普通发票可按订单申请；电子专票需要企业账户，申请前准备发票抬头及有效纳税人识别号，按申请页面提交资料。\n\n纸质专票仅企业账户可申请，申请时需提供企业开票资料、收件人和邮寄地址，快递费到付。资料审核通过后按开票流程寄出，不承诺快递送达日期。"
    },
    {
      "n": 3,
      "chunk_id": "1979",
      "section_path": "开票细则/开票时效",
      "question": "开票时效",
      "answer": "订单完成后 30 天内可在「我的订单」申请开票，超过 30 天需联系客服核实补开条件，不能直接承诺一定补开。\n\n有效资料审核通过后 3 个工作日内开出发票，电子发票发送至申请邮箱；纸质专票开出后安排邮寄，邮寄耗时不计入开票时限。发票抬头或税号填错时联系客服核实更正，不保证无需审核即可重开。"
    },
    {
      "n": 5,
      "chunk_id": "1939",
      "section_path": "商品与购物 FAQ/如何申请退款",
      "question": "如何申请退款",
      "answer": "在「我的订单」找到对应订单点击「申请退款」,按提示提交,审核通过后原路退回。"
    },
    {
      "n": 7,
      "chunk_id": "1931",
      "section_path": "售后手册/常见问题处理时限",
      "question": "常见问题处理时限",
      "answer": "| 问题类型 | 首次响应 | 处理时限 |\n| --- | --- | --- |\n| 退款 | 2 小时 | 3 个工作日 |\n| 换货 | 2 小时 | 5 个工作日 |\n| 维修 | 4 小时 | 7 个工作日 |\n| 投诉 | 1 小时 | 3 个工作日 |\n| 发票 | 4 小时 | 3 个工作日 |\n| 物流异常 | 2 小时 | 5 个工作日 |\n| 商品咨询 | 1 小时 | 当日 |\n| 价格保护 | 2 小时 | 3 个工作日 |\n| 账户问题 | 2 小时 | 3 个工作日 |\n| 退换货运费 | 2 小时 | 3 个工作日 |\n| 缺货补发 | 2 小时 | 5 个工作日 |\n| 其他 | 4 小时 | 7 个工作日 |"
    },
    {
      "n": 9,
      "chunk_id": "1973",
      "section_path": "退货退款政策/预售与定金",
      "question": "预售与定金",
      "answer": "预售商品以详情页标注的时间发货;定金支付后不支持无理由退定金,尾款未按时支付的,定金按活动规则处理。"
    },
    {
      "n": 10,
      "chunk_id": "1967",
      "section_path": "退货退款政策/换货政策/换货条件",
      "question": "换货条件",
      "answer": "收到商品 7 天内,商品完好且配件齐全的,可申请一次同款换货;不同型号或颜色需先退货再重新下单。"
    },
    {
      "n": 8,
      "chunk_id": "1932",
      "section_path": "售后手册/保修说明",
      "question": "保修说明",
      "answer": "电子类商品保修 12 个月,自签收日起算;人为损坏不在保修范围。"
    },
    {
      "n": 6,
      "chunk_id": "1936",
      "section_path": "售后手册/维修寄修流程",
      "question": "维修寄修流程",
      "answer": "保修期内设备故障,联系客服登记后按指引将设备寄回指定维修点,核验后免费维修并寄回;超保或人为损坏维修可能收取工本费,费用会提前告知。"
    },
    {
      "n": 4,
      "chunk_id": "1971",
      "section_path": "退货退款政策/运输破损处理",
      "question": "运输破损处理",
      "answer": "商品运输途中破损的,请在签收后 48 小时内联系客服并提供开箱视频与照片,核实后可免费补发或退款,相关运费由平台承担。"
    },
    {
      "n": 2,
      "chunk_id": "1943",
      "section_path": "商品与购物 FAQ/发票如何开具",
      "question": "发票如何开具",
      "answer": "在「我的订单」-「申请开票」提交抬头与税号,电子发票将于 3 个工作日内发送至邮箱。"
    }
  ],
  "decision": {
    "useful": false,
    "reason": "证据未涉及纸质发票遗失挂失证明政策",
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
  "elapsed_ms": 3948.1683000922203,
  "judge_snapshot": {
    "prompt_version": "joint-generation-v2.1",
    "finish_reason": "stop"
  },
  "rewrite": {
    "policy_version": "original-query-on-invalid-v1",
    "status": "success",
    "error": null
  },
  "audit": {
    "audit_version": 1,
    "source_map_id": "af6590ab401319d942bddff0b30213a4cd888b8cf115ebd5cdec3adb87687e55",
    "gold_groups": [],
    "answer_points": [],
    "candidate_ranking": [
      {
        "chunk_id": 1978,
        "score": 0.6452586054801941,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1943,
        "score": 0.5758640766143799,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1979,
        "score": 0.5663228034973145,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1971,
        "score": 0.5103285312652588,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1939,
        "score": 0.4919954538345337,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1936,
        "score": 0.47299909591674805,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1931,
        "score": 0.47143441438674927,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1932,
        "score": 0.4683113396167755,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1973,
        "score": 0.4644458293914795,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1967,
        "score": 0.4627034664154053,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1970,
        "score": 0.45970097184181213,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1965,
        "score": 0.4505119323730469,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1937,
        "score": 0.4483277499675751,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1948,
        "score": 0.44779449701309204,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1940,
        "score": 0.4439329504966736,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1950,
        "score": 0.44006818532943726,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1968,
        "score": 0.43696826696395874,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1966,
        "score": 0.43148547410964966,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1977,
        "score": 0.42871958017349243,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1969,
        "score": 0.42254409193992615,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1938,
        "score": 0.4221780300140381,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1949,
        "score": 0.41479384899139404,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1972,
        "score": 0.41221368312835693,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1935,
        "score": 0.4005711078643799,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1941,
        "score": 0.3995623290538788,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1944,
        "score": 0.3971923589706421,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1951,
        "score": 0.39671066403388977,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1946,
        "score": 0.3933674097061157,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1934,
        "score": 0.3871292173862457,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1976,
        "score": 0.3857405185699463,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1942,
        "score": 0.3832434415817261,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1947,
        "score": 0.3829110562801361,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1975,
        "score": 0.37594008445739746,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1952,
        "score": 0.3689400255680084,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1974,
        "score": 0.3679296672344208,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1958,
        "score": 0.36721402406692505,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1933,
        "score": 0.3643520474433899,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1945,
        "score": 0.36295390129089355,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1957,
        "score": 0.36286771297454834,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1956,
        "score": 0.3550981879234314,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1962,
        "score": 0.35357603430747986,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1963,
        "score": 0.33424344658851624,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1961,
        "score": 0.3296428322792053,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1980,
        "score": 0.3273769021034241,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1964,
        "score": 0.3247159421443939,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1953,
        "score": 0.3195827603340149,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1955,
        "score": 0.3047650158405304,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1959,
        "score": 0.29277303814888,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1954,
        "score": 0.28896254301071167,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1960,
        "score": 0.28842511773109436,
        "score_kind": "cosine"
      }
    ],
    "final_ranking": [
      {
        "chunk_id": 1978,
        "score": 0.6452586054801941,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1943,
        "score": 0.5758640766143799,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1979,
        "score": 0.5663228034973145,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1971,
        "score": 0.5103285312652588,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1939,
        "score": 0.4919954538345337,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1936,
        "score": 0.47299909591674805,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1931,
        "score": 0.47143441438674927,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1932,
        "score": 0.4683113396167755,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1973,
        "score": 0.4644458293914795,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1967,
        "score": 0.4627034664154053,
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
    1978,
    1979,
    1943,
    1948,
    1939,
    1950,
    1940,
    1967,
    1970,
    1931
  ],
  "final_ids": [
    1978,
    1979,
    1943,
    1948,
    1939,
    1950,
    1940,
    1967,
    1970,
    1931
  ],
  "prompt_citations": [
    {
      "n": 1,
      "chunk_id": "1978",
      "section_path": "开票细则/可开票类型",
      "question": "可开票类型",
      "answer": "本演示店提供电子普通发票、电子专用发票和纸质专用发票。电子普通发票可按订单申请；电子专票需要企业账户，申请前准备发票抬头及有效纳税人识别号，按申请页面提交资料。\n\n纸质专票仅企业账户可申请，申请时需提供企业开票资料、收件人和邮寄地址，快递费到付。资料审核通过后按开票流程寄出，不承诺快递送达日期。"
    },
    {
      "n": 3,
      "chunk_id": "1943",
      "section_path": "商品与购物 FAQ/发票如何开具",
      "question": "发票如何开具",
      "answer": "在「我的订单」-「申请开票」提交抬头与税号,电子发票将于 3 个工作日内发送至邮箱。"
    },
    {
      "n": 5,
      "chunk_id": "1939",
      "section_path": "商品与购物 FAQ/如何申请退款",
      "question": "如何申请退款",
      "answer": "在「我的订单」找到对应订单点击「申请退款」,按提示提交,审核通过后原路退回。"
    },
    {
      "n": 7,
      "chunk_id": "1940",
      "section_path": "商品与购物 FAQ/换货流程怎么走",
      "question": "换货流程怎么走",
      "answer": "收到商品 7 天内可申请换货,联系客服登记后将商品寄回,平台核验无误后补发新品。"
    },
    {
      "n": 9,
      "chunk_id": "1970",
      "section_path": "退货退款政策/质量问题与保修",
      "question": "质量问题与保修",
      "answer": "电子类商品自签收起保修 12 个月,保修期内非人为损坏可申请免费维修或换货;人为损坏、超保商品维修可能收取工本费。"
    },
    {
      "n": 10,
      "chunk_id": "1931",
      "section_path": "售后手册/常见问题处理时限",
      "question": "常见问题处理时限",
      "answer": "| 问题类型 | 首次响应 | 处理时限 |\n| --- | --- | --- |\n| 退款 | 2 小时 | 3 个工作日 |\n| 换货 | 2 小时 | 5 个工作日 |\n| 维修 | 4 小时 | 7 个工作日 |\n| 投诉 | 1 小时 | 3 个工作日 |\n| 发票 | 4 小时 | 3 个工作日 |\n| 物流异常 | 2 小时 | 5 个工作日 |\n| 商品咨询 | 1 小时 | 当日 |\n| 价格保护 | 2 小时 | 3 个工作日 |\n| 账户问题 | 2 小时 | 3 个工作日 |\n| 退换货运费 | 2 小时 | 3 个工作日 |\n| 缺货补发 | 2 小时 | 5 个工作日 |\n| 其他 | 4 小时 | 7 个工作日 |"
    },
    {
      "n": 8,
      "chunk_id": "1967",
      "section_path": "退货退款政策/换货政策/换货条件",
      "question": "换货条件",
      "answer": "收到商品 7 天内,商品完好且配件齐全的,可申请一次同款换货;不同型号或颜色需先退货再重新下单。"
    },
    {
      "n": 6,
      "chunk_id": "1950",
      "section_path": "商品与购物 FAQ/价格保护怎么申请",
      "question": "价格保护怎么申请",
      "answer": "自营商品支持下单后 7 天内价保,期间若同款降价可在「我的订单」-「申请价保」提交,差价将退回原支付渠道。"
    },
    {
      "n": 4,
      "chunk_id": "1948",
      "section_path": "商品与购物 FAQ/订单可以修改或取消吗",
      "question": "订单可以修改或取消吗",
      "answer": "订单未发货前可在「我的订单」自助取消;已发货订单无法修改收货信息,可拒收后走退款流程。修改商品数量需取消后重新下单。"
    },
    {
      "n": 2,
      "chunk_id": "1979",
      "section_path": "开票细则/开票时效",
      "question": "开票时效",
      "answer": "订单完成后 30 天内可在「我的订单」申请开票，超过 30 天需联系客服核实补开条件，不能直接承诺一定补开。\n\n有效资料审核通过后 3 个工作日内开出发票，电子发票发送至申请邮箱；纸质专票开出后安排邮寄，邮寄耗时不计入开票时限。发票抬头或税号填错时联系客服核实更正，不保证无需审核即可重开。"
    }
  ],
  "decision": {
    "useful": false,
    "reason": "无挂失证明相关证据",
    "response_kind": "knowledge",
    "source": "self_check"
  },
  "answer": "目前的知识资料不足以确认这个问题，我无法给出可靠答案。请补充具体商品或适用条件，或联系人工客服确认。",
  "point_verdicts": [],
  "claim_verdicts": [
    {
      "claim": "目前的知识资料不足以确认纸质发票遗失后能否申请挂失证明",
      "supported": true,
      "reason": "所有提供的证据均未涉及发票挂失或遗失证明，证据沉默，回答的拒答性陈述成立"
    },
    {
      "claim": "无法给出可靠答案，请补充具体商品或适用条件，或联系人工客服确认",
      "supported": true,
      "reason": "证据中无发票挂失相关内容，建议补充信息或联系人工客服属于拒答性表述，与证据缺失情况一致"
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
  "elapsed_ms": 5334.918899694458,
  "judge_snapshot": {
    "prompt_version": "joint-generation-v2.1",
    "finish_reason": "stop"
  },
  "rewrite": {
    "policy_version": "original-query-on-invalid-v1",
    "status": "success",
    "error": null
  },
  "audit": {
    "audit_version": 1,
    "source_map_id": "af6590ab401319d942bddff0b30213a4cd888b8cf115ebd5cdec3adb87687e55",
    "gold_groups": [],
    "answer_points": [],
    "candidate_ranking": [
      {
        "chunk_id": 1978,
        "score": 10.285421371459961,
        "score_kind": "bm25"
      },
      {
        "chunk_id": 1979,
        "score": 8.083020210266113,
        "score_kind": "bm25"
      },
      {
        "chunk_id": 1943,
        "score": 5.832973480224609,
        "score_kind": "bm25"
      },
      {
        "chunk_id": 1948,
        "score": 3.737774610519409,
        "score_kind": "bm25"
      },
      {
        "chunk_id": 1939,
        "score": 2.8332555294036865,
        "score_kind": "bm25"
      },
      {
        "chunk_id": 1950,
        "score": 2.6836564540863037,
        "score_kind": "bm25"
      },
      {
        "chunk_id": 1940,
        "score": 2.1490039825439453,
        "score_kind": "bm25"
      },
      {
        "chunk_id": 1967,
        "score": 2.071161985397339,
        "score_kind": "bm25"
      },
      {
        "chunk_id": 1970,
        "score": 1.9644274711608887,
        "score_kind": "bm25"
      },
      {
        "chunk_id": 1931,
        "score": 1.7175705432891846,
        "score_kind": "bm25"
      }
    ],
    "final_ranking": [
      {
        "chunk_id": 1978,
        "score": 10.285421371459961,
        "score_kind": "bm25"
      },
      {
        "chunk_id": 1979,
        "score": 8.083020210266113,
        "score_kind": "bm25"
      },
      {
        "chunk_id": 1943,
        "score": 5.832973480224609,
        "score_kind": "bm25"
      },
      {
        "chunk_id": 1948,
        "score": 3.737774610519409,
        "score_kind": "bm25"
      },
      {
        "chunk_id": 1939,
        "score": 2.8332555294036865,
        "score_kind": "bm25"
      },
      {
        "chunk_id": 1950,
        "score": 2.6836564540863037,
        "score_kind": "bm25"
      },
      {
        "chunk_id": 1940,
        "score": 2.1490039825439453,
        "score_kind": "bm25"
      },
      {
        "chunk_id": 1967,
        "score": 2.071161985397339,
        "score_kind": "bm25"
      },
      {
        "chunk_id": 1970,
        "score": 1.9644274711608887,
        "score_kind": "bm25"
      },
      {
        "chunk_id": 1931,
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
    1978,
    1943,
    1979,
    1939,
    1931,
    1948,
    1967,
    1970,
    1950,
    1940,
    1971,
    1936,
    1932,
    1973,
    1965,
    1937,
    1968,
    1966,
    1977,
    1969,
    1938,
    1949,
    1972,
    1935,
    1941,
    1944,
    1951,
    1946,
    1934,
    1976,
    1942,
    1947,
    1975,
    1952,
    1974,
    1958,
    1933,
    1945,
    1957,
    1956,
    1962,
    1963,
    1961,
    1980,
    1964,
    1953,
    1955,
    1959,
    1954,
    1960
  ],
  "final_ids": [
    1978,
    1943,
    1979,
    1939,
    1931,
    1948,
    1967,
    1970,
    1950,
    1940
  ],
  "prompt_citations": [
    {
      "n": 1,
      "chunk_id": "1978",
      "section_path": "开票细则/可开票类型",
      "question": "可开票类型",
      "answer": "本演示店提供电子普通发票、电子专用发票和纸质专用发票。电子普通发票可按订单申请；电子专票需要企业账户，申请前准备发票抬头及有效纳税人识别号，按申请页面提交资料。\n\n纸质专票仅企业账户可申请，申请时需提供企业开票资料、收件人和邮寄地址，快递费到付。资料审核通过后按开票流程寄出，不承诺快递送达日期。"
    },
    {
      "n": 3,
      "chunk_id": "1979",
      "section_path": "开票细则/开票时效",
      "question": "开票时效",
      "answer": "订单完成后 30 天内可在「我的订单」申请开票，超过 30 天需联系客服核实补开条件，不能直接承诺一定补开。\n\n有效资料审核通过后 3 个工作日内开出发票，电子发票发送至申请邮箱；纸质专票开出后安排邮寄，邮寄耗时不计入开票时限。发票抬头或税号填错时联系客服核实更正，不保证无需审核即可重开。"
    },
    {
      "n": 5,
      "chunk_id": "1931",
      "section_path": "售后手册/常见问题处理时限",
      "question": "常见问题处理时限",
      "answer": "| 问题类型 | 首次响应 | 处理时限 |\n| --- | --- | --- |\n| 退款 | 2 小时 | 3 个工作日 |\n| 换货 | 2 小时 | 5 个工作日 |\n| 维修 | 4 小时 | 7 个工作日 |\n| 投诉 | 1 小时 | 3 个工作日 |\n| 发票 | 4 小时 | 3 个工作日 |\n| 物流异常 | 2 小时 | 5 个工作日 |\n| 商品咨询 | 1 小时 | 当日 |\n| 价格保护 | 2 小时 | 3 个工作日 |\n| 账户问题 | 2 小时 | 3 个工作日 |\n| 退换货运费 | 2 小时 | 3 个工作日 |\n| 缺货补发 | 2 小时 | 5 个工作日 |\n| 其他 | 4 小时 | 7 个工作日 |"
    },
    {
      "n": 7,
      "chunk_id": "1967",
      "section_path": "退货退款政策/换货政策/换货条件",
      "question": "换货条件",
      "answer": "收到商品 7 天内,商品完好且配件齐全的,可申请一次同款换货;不同型号或颜色需先退货再重新下单。"
    },
    {
      "n": 9,
      "chunk_id": "1950",
      "section_path": "商品与购物 FAQ/价格保护怎么申请",
      "question": "价格保护怎么申请",
      "answer": "自营商品支持下单后 7 天内价保,期间若同款降价可在「我的订单」-「申请价保」提交,差价将退回原支付渠道。"
    },
    {
      "n": 10,
      "chunk_id": "1940",
      "section_path": "商品与购物 FAQ/换货流程怎么走",
      "question": "换货流程怎么走",
      "answer": "收到商品 7 天内可申请换货,联系客服登记后将商品寄回,平台核验无误后补发新品。"
    },
    {
      "n": 8,
      "chunk_id": "1970",
      "section_path": "退货退款政策/质量问题与保修",
      "question": "质量问题与保修",
      "answer": "电子类商品自签收起保修 12 个月,保修期内非人为损坏可申请免费维修或换货;人为损坏、超保商品维修可能收取工本费。"
    },
    {
      "n": 6,
      "chunk_id": "1948",
      "section_path": "商品与购物 FAQ/订单可以修改或取消吗",
      "question": "订单可以修改或取消吗",
      "answer": "订单未发货前可在「我的订单」自助取消;已发货订单无法修改收货信息,可拒收后走退款流程。修改商品数量需取消后重新下单。"
    },
    {
      "n": 4,
      "chunk_id": "1939",
      "section_path": "商品与购物 FAQ/如何申请退款",
      "question": "如何申请退款",
      "answer": "在「我的订单」找到对应订单点击「申请退款」,按提示提交,审核通过后原路退回。"
    },
    {
      "n": 2,
      "chunk_id": "1943",
      "section_path": "商品与购物 FAQ/发票如何开具",
      "question": "发票如何开具",
      "answer": "在「我的订单」-「申请开票」提交抬头与税号,电子发票将于 3 个工作日内发送至邮箱。"
    }
  ],
  "decision": {
    "useful": false,
    "reason": "无纸质发票遗失挂失证明的相关证据",
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
  "elapsed_ms": 4301.685699960217,
  "judge_snapshot": {
    "prompt_version": "joint-generation-v2.1",
    "finish_reason": "stop"
  },
  "rewrite": {
    "policy_version": "original-query-on-invalid-v1",
    "status": "success",
    "error": null
  },
  "audit": {
    "audit_version": 1,
    "source_map_id": "af6590ab401319d942bddff0b30213a4cd888b8cf115ebd5cdec3adb87687e55",
    "gold_groups": [],
    "answer_points": [],
    "candidate_ranking": [
      {
        "chunk_id": 1978,
        "score": 0.032786883413791656,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1943,
        "score": 0.0320020467042923,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1979,
        "score": 0.0320020467042923,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1939,
        "score": 0.03076923079788685,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1931,
        "score": 0.02921108715236187,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1948,
        "score": 0.029138512909412384,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1967,
        "score": 0.028991596773266792,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1970,
        "score": 0.028577260673046112,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1950,
        "score": 0.02830941043794155,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1940,
        "score": 0.028258707374334335,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1971,
        "score": 0.015625,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1936,
        "score": 0.01515151560306549,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1932,
        "score": 0.014705882407724857,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1973,
        "score": 0.014492753893136978,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1965,
        "score": 0.013888888992369175,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1937,
        "score": 0.013698630034923553,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1968,
        "score": 0.012987012974917889,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1966,
        "score": 0.012820512987673283,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1977,
        "score": 0.012658228166401386,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1969,
        "score": 0.012500000186264515,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1938,
        "score": 0.012345679104328156,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1949,
        "score": 0.012195121496915817,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1972,
        "score": 0.012048192322254181,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1935,
        "score": 0.011904762126505375,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1941,
        "score": 0.0117647061124444,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1944,
        "score": 0.011627906933426857,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1951,
        "score": 0.01149425283074379,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1946,
        "score": 0.011363636702299118,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1934,
        "score": 0.01123595517128706,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1976,
        "score": 0.011111111380159855,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1942,
        "score": 0.010989011265337467,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1947,
        "score": 0.010869565419852734,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1975,
        "score": 0.01075268816202879,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1952,
        "score": 0.010638297535479069,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1974,
        "score": 0.010526316240429878,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1958,
        "score": 0.010416666977107525,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1933,
        "score": 0.010309278033673763,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1945,
        "score": 0.010204081423580647,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1957,
        "score": 0.010101010091602802,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1956,
        "score": 0.009999999776482582,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1962,
        "score": 0.009900989942252636,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1963,
        "score": 0.009803921915590763,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1961,
        "score": 0.009708737954497337,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1980,
        "score": 0.009615384973585606,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1964,
        "score": 0.009523809887468815,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1953,
        "score": 0.009433962404727936,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1955,
        "score": 0.009345794096589088,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1959,
        "score": 0.009259259328246117,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1954,
        "score": 0.00917431153357029,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1960,
        "score": 0.00909090880304575,
        "score_kind": "rrf"
      }
    ],
    "final_ranking": [
      {
        "chunk_id": 1978,
        "score": 0.032786883413791656,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1943,
        "score": 0.0320020467042923,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1979,
        "score": 0.0320020467042923,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1939,
        "score": 0.03076923079788685,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1931,
        "score": 0.02921108715236187,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1948,
        "score": 0.029138512909412384,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1967,
        "score": 0.028991596773266792,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1970,
        "score": 0.028577260673046112,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1950,
        "score": 0.02830941043794155,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1940,
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
    1978,
    1943,
    1979,
    1939,
    1931,
    1948,
    1967,
    1970,
    1950,
    1940,
    1971,
    1936,
    1932,
    1973,
    1965,
    1937,
    1968,
    1966,
    1977,
    1969,
    1938,
    1949,
    1972,
    1935,
    1941,
    1944,
    1951,
    1946,
    1934,
    1976,
    1942,
    1947,
    1975,
    1952,
    1974,
    1958,
    1933,
    1945,
    1957,
    1956,
    1962,
    1963,
    1961,
    1980,
    1964,
    1953,
    1955,
    1959,
    1954,
    1960
  ],
  "final_ids": [
    1979,
    1978,
    1943,
    1970,
    1971,
    1939,
    1965,
    1966,
    1932,
    1931
  ],
  "prompt_citations": [
    {
      "n": 1,
      "chunk_id": "1979",
      "section_path": "开票细则/开票时效",
      "question": "开票时效",
      "answer": "订单完成后 30 天内可在「我的订单」申请开票，超过 30 天需联系客服核实补开条件，不能直接承诺一定补开。\n\n有效资料审核通过后 3 个工作日内开出发票，电子发票发送至申请邮箱；纸质专票开出后安排邮寄，邮寄耗时不计入开票时限。发票抬头或税号填错时联系客服核实更正，不保证无需审核即可重开。"
    },
    {
      "n": 3,
      "chunk_id": "1943",
      "section_path": "商品与购物 FAQ/发票如何开具",
      "question": "发票如何开具",
      "answer": "在「我的订单」-「申请开票」提交抬头与税号,电子发票将于 3 个工作日内发送至邮箱。"
    },
    {
      "n": 5,
      "chunk_id": "1971",
      "section_path": "退货退款政策/运输破损处理",
      "question": "运输破损处理",
      "answer": "商品运输途中破损的,请在签收后 48 小时内联系客服并提供开箱视频与照片,核实后可免费补发或退款,相关运费由平台承担。"
    },
    {
      "n": 7,
      "chunk_id": "1965",
      "section_path": "退货退款政策/无理由退货/适用范围",
      "question": "适用范围",
      "answer": "自签收之日起 7 天内,商品完好、不影响二次销售的,支持无理由退货。定制类、生鲜类商品除外。"
    },
    {
      "n": 9,
      "chunk_id": "1932",
      "section_path": "售后手册/保修说明",
      "question": "保修说明",
      "answer": "电子类商品保修 12 个月,自签收日起算;人为损坏不在保修范围。"
    },
    {
      "n": 10,
      "chunk_id": "1931",
      "section_path": "售后手册/常见问题处理时限",
      "question": "常见问题处理时限",
      "answer": "| 问题类型 | 首次响应 | 处理时限 |\n| --- | --- | --- |\n| 退款 | 2 小时 | 3 个工作日 |\n| 换货 | 2 小时 | 5 个工作日 |\n| 维修 | 4 小时 | 7 个工作日 |\n| 投诉 | 1 小时 | 3 个工作日 |\n| 发票 | 4 小时 | 3 个工作日 |\n| 物流异常 | 2 小时 | 5 个工作日 |\n| 商品咨询 | 1 小时 | 当日 |\n| 价格保护 | 2 小时 | 3 个工作日 |\n| 账户问题 | 2 小时 | 3 个工作日 |\n| 退换货运费 | 2 小时 | 3 个工作日 |\n| 缺货补发 | 2 小时 | 5 个工作日 |\n| 其他 | 4 小时 | 7 个工作日 |"
    },
    {
      "n": 8,
      "chunk_id": "1966",
      "section_path": "退货退款政策/无理由退货/退款时效",
      "question": "退款时效",
      "answer": "退货商品经平台核验通过后,退款原路退回,到账时效以平台售后规则为准。"
    },
    {
      "n": 6,
      "chunk_id": "1939",
      "section_path": "商品与购物 FAQ/如何申请退款",
      "question": "如何申请退款",
      "answer": "在「我的订单」找到对应订单点击「申请退款」,按提示提交,审核通过后原路退回。"
    },
    {
      "n": 4,
      "chunk_id": "1970",
      "section_path": "退货退款政策/质量问题与保修",
      "question": "质量问题与保修",
      "answer": "电子类商品自签收起保修 12 个月,保修期内非人为损坏可申请免费维修或换货;人为损坏、超保商品维修可能收取工本费。"
    },
    {
      "n": 2,
      "chunk_id": "1978",
      "section_path": "开票细则/可开票类型",
      "question": "可开票类型",
      "answer": "本演示店提供电子普通发票、电子专用发票和纸质专用发票。电子普通发票可按订单申请；电子专票需要企业账户，申请前准备发票抬头及有效纳税人识别号，按申请页面提交资料。\n\n纸质专票仅企业账户可申请，申请时需提供企业开票资料、收件人和邮寄地址，快递费到付。资料审核通过后按开票流程寄出，不承诺快递送达日期。"
    }
  ],
  "decision": {
    "useful": false,
    "reason": "证据无挂失证明相关内容",
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
  "elapsed_ms": 5035.609999904409,
  "judge_snapshot": {
    "prompt_version": "joint-generation-v2.1",
    "finish_reason": "stop"
  },
  "rewrite": {
    "policy_version": "original-query-on-invalid-v1",
    "status": "success",
    "error": null
  },
  "audit": {
    "audit_version": 1,
    "source_map_id": "af6590ab401319d942bddff0b30213a4cd888b8cf115ebd5cdec3adb87687e55",
    "gold_groups": [],
    "answer_points": [],
    "candidate_ranking": [
      {
        "chunk_id": 1978,
        "score": 0.032786883413791656,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1943,
        "score": 0.0320020467042923,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1979,
        "score": 0.0320020467042923,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1939,
        "score": 0.03076923079788685,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1931,
        "score": 0.02921108715236187,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1948,
        "score": 0.029138512909412384,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1967,
        "score": 0.028991596773266792,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1970,
        "score": 0.028577260673046112,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1950,
        "score": 0.02830941043794155,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1940,
        "score": 0.028258707374334335,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1971,
        "score": 0.015625,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1936,
        "score": 0.01515151560306549,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1932,
        "score": 0.014705882407724857,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1973,
        "score": 0.014492753893136978,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1965,
        "score": 0.013888888992369175,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1937,
        "score": 0.013698630034923553,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1968,
        "score": 0.012987012974917889,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1966,
        "score": 0.012820512987673283,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1977,
        "score": 0.012658228166401386,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1969,
        "score": 0.012500000186264515,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1938,
        "score": 0.012345679104328156,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1949,
        "score": 0.012195121496915817,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1972,
        "score": 0.012048192322254181,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1935,
        "score": 0.011904762126505375,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1941,
        "score": 0.0117647061124444,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1944,
        "score": 0.011627906933426857,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1951,
        "score": 0.01149425283074379,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1946,
        "score": 0.011363636702299118,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1934,
        "score": 0.01123595517128706,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1976,
        "score": 0.011111111380159855,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1942,
        "score": 0.010989011265337467,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1947,
        "score": 0.010869565419852734,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1975,
        "score": 0.01075268816202879,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1952,
        "score": 0.010638297535479069,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1974,
        "score": 0.010526316240429878,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1958,
        "score": 0.010416666977107525,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1933,
        "score": 0.010309278033673763,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1945,
        "score": 0.010204081423580647,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1957,
        "score": 0.010101010091602802,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1956,
        "score": 0.009999999776482582,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1962,
        "score": 0.009900989942252636,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1963,
        "score": 0.009803921915590763,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1961,
        "score": 0.009708737954497337,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1980,
        "score": 0.009615384973585606,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1964,
        "score": 0.009523809887468815,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1953,
        "score": 0.009433962404727936,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1955,
        "score": 0.009345794096589088,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1959,
        "score": 0.009259259328246117,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1954,
        "score": 0.00917431153357029,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1960,
        "score": 0.00909090880304575,
        "score_kind": "rrf"
      }
    ],
    "final_ranking": [
      {
        "chunk_id": 1979,
        "score": 0.09102626144886017,
        "score_kind": "rerank"
      },
      {
        "chunk_id": 1978,
        "score": 0.03932482749223709,
        "score_kind": "rerank"
      },
      {
        "chunk_id": 1943,
        "score": 0.0009756985236890614,
        "score_kind": "rerank"
      },
      {
        "chunk_id": 1970,
        "score": 0.000585791771300137,
        "score_kind": "rerank"
      },
      {
        "chunk_id": 1971,
        "score": 0.0003885758633259684,
        "score_kind": "rerank"
      },
      {
        "chunk_id": 1939,
        "score": 0.00024433410726487637,
        "score_kind": "rerank"
      },
      {
        "chunk_id": 1965,
        "score": 0.00022400208399631083,
        "score_kind": "rerank"
      },
      {
        "chunk_id": 1966,
        "score": 0.00021449675841722637,
        "score_kind": "rerank"
      },
      {
        "chunk_id": 1932,
        "score": 0.0002099971752613783,
        "score_kind": "rerank"
      },
      {
        "chunk_id": 1931,
        "score": 0.0001697506377240643,
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
          1965
        ],
        [
          1938
        ]
      ]
    },
    {
      "group_id": "g2",
      "alternatives": [
        [
          1969
        ]
      ]
    },
    {
      "group_id": "g3",
      "alternatives": [
        [
          1966
        ]
      ]
    }
  ],
  "candidate_ids": [
    1969,
    1971,
    1968,
    1965,
    1966,
    1938,
    1940,
    1973,
    1942,
    1970,
    1931,
    1941,
    1967,
    1936,
    1939,
    1937,
    1949,
    1950,
    1947,
    1951,
    1972,
    1979,
    1932,
    1948,
    1976,
    1943,
    1977,
    1935,
    1944,
    1974,
    1945,
    1975,
    1978,
    1946,
    1934,
    1953,
    1955,
    1958,
    1957,
    1956,
    1954,
    1933,
    1962,
    1980,
    1952,
    1960,
    1963,
    1961,
    1964,
    1959
  ],
  "final_ids": [
    1969,
    1971,
    1968,
    1965,
    1966,
    1938,
    1940,
    1973,
    1942,
    1970
  ],
  "prompt_citations": [
    {
      "n": 1,
      "chunk_id": "1969",
      "section_path": "退货退款政策/退换货运费承担",
      "question": "退换货运费承担",
      "answer": "无理由退货的退回运费由买家承担;因商品质量问题、发错货、少发漏发导致的退换货,运费由平台承担。运费承担以平台售后规则最终判定为准。"
    },
    {
      "n": 3,
      "chunk_id": "1968",
      "section_path": "退货退款政策/换货政策/换货运费",
      "question": "换货运费",
      "answer": "非质量问题的换货,往返运费由买家承担;因质量问题或发错货的换货,往返运费由平台承担。"
    },
    {
      "n": 5,
      "chunk_id": "1966",
      "section_path": "退货退款政策/无理由退货/退款时效",
      "question": "退款时效",
      "answer": "退货商品经平台核验通过后,退款原路退回,到账时效以平台售后规则为准。"
    },
    {
      "n": 7,
      "chunk_id": "1940",
      "section_path": "商品与购物 FAQ/换货流程怎么走",
      "question": "换货流程怎么走",
      "answer": "收到商品 7 天内可申请换货,联系客服登记后将商品寄回,平台核验无误后补发新品。"
    },
    {
      "n": 9,
      "chunk_id": "1942",
      "section_path": "商品与购物 FAQ/运费怎么算",
      "question": "运费怎么算",
      "answer": "单笔订单满 99 元包邮,未满收取 10 元运费,偏远地区运费另计。邮费即运费,按此规则收取。"
    },
    {
      "n": 10,
      "chunk_id": "1970",
      "section_path": "退货退款政策/质量问题与保修",
      "question": "质量问题与保修",
      "answer": "电子类商品自签收起保修 12 个月,保修期内非人为损坏可申请免费维修或换货;人为损坏、超保商品维修可能收取工本费。"
    },
    {
      "n": 8,
      "chunk_id": "1973",
      "section_path": "退货退款政策/预售与定金",
      "question": "预售与定金",
      "answer": "预售商品以详情页标注的时间发货;定金支付后不支持无理由退定金,尾款未按时支付的,定金按活动规则处理。"
    },
    {
      "n": 6,
      "chunk_id": "1938",
      "section_path": "商品与购物 FAQ/退货政策是什么",
      "question": "退货政策是什么",
      "answer": "支持 7 天无理由退货,商品需保持完好、不影响二次销售,具体以平台售后规则为准。"
    },
    {
      "n": 4,
      "chunk_id": "1965",
      "section_path": "退货退款政策/无理由退货/适用范围",
      "question": "适用范围",
      "answer": "自签收之日起 7 天内,商品完好、不影响二次销售的,支持无理由退货。定制类、生鲜类商品除外。"
    },
    {
      "n": 2,
      "chunk_id": "1971",
      "section_path": "退货退款政策/运输破损处理",
      "question": "运输破损处理",
      "answer": "商品运输途中破损的,请在签收后 48 小时内联系客服并提供开箱视频与照片,核实后可免费补发或退款,相关运费由平台承担。"
    }
  ],
  "decision": {
    "useful": true,
    "reason": "有运费承担和退款时效政策证据",
    "response_kind": "knowledge",
    "source": null
  },
  "answer": "您好！根据平台政策为您说明：\n\n**运费承担**[1]\n- 无理由退货（商品没问题、只是不想要了）：寄回运费由**买家承担**。\n- 若是商品质量问题、发错货、少发漏发：运费由**平台承担**。\n\n**退款时效**[5]\n退货商品经平台核验通过后，退款原路退回，具体到账时效以平台售后规则为准，我无法保证具体到账日期。\n\n另提醒：无理由退货需在签收后 7 天内申请，商品需保持完好、不影响二次销售[4][6]。\n\n请问您的商品是存在质量问题还是无理由退货呢？如需进一步处理，可提供订单号，我为您查询。",
  "point_verdicts": [
    {
      "point_id": "p1",
      "covered": false,
      "reason": "回答提到签收后7天内、商品完好、不影响二次销售，但未提及定制类和生鲜类商品排除，condition中的适用条件未完整保留"
    },
    {
      "point_id": "p2",
      "covered": true,
      "reason": "回答按退货原因区分运费承担：无理由退货买家承担，质量问题、发错货、少发漏发平台承担"
    },
    {
      "point_id": "p3",
      "covered": true,
      "reason": "回答说明核验通过后退款原路退回，到账时效以平台售后规则为准，未编造固定天数"
    }
  ],
  "claim_verdicts": [
    {
      "claim": "无理由退货（商品没问题、只是不想要了）寄回运费由买家承担",
      "supported": true,
      "reason": "证据1明确无理由退货的退回运费由买家承担"
    },
    {
      "claim": "商品质量问题、发错货、少发漏发导致的退换货运费由平台承担",
      "supported": true,
      "reason": "证据1明确因质量问题、发错货、少发漏发的退换货运费由平台承担"
    },
    {
      "claim": "退货商品经平台核验通过后退款原路退回",
      "supported": true,
      "reason": "证据5明确核验通过后退款原路退回"
    },
    {
      "claim": "退款具体到账时效以平台售后规则为准，无法保证具体到账日期",
      "supported": true,
      "reason": "证据5明确到账时效以平台售后规则为准，未给出固定天数"
    },
    {
      "claim": "无理由退货需在签收后7天内申请",
      "supported": true,
      "reason": "证据4明确自签收之日起7天内支持无理由退货"
    },
    {
      "claim": "无理由退货商品需保持完好、不影响二次销售",
      "supported": true,
      "reason": "证据4和证据6均明确商品需完好、不影响二次销售"
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
  "elapsed_ms": 19270.165199879557,
  "judge_snapshot": {
    "prompt_version": "joint-generation-v2.1",
    "finish_reason": "stop"
  },
  "rewrite": {
    "policy_version": "original-query-on-invalid-v1",
    "status": "success",
    "error": null
  },
  "audit": {
    "audit_version": 1,
    "source_map_id": "af6590ab401319d942bddff0b30213a4cd888b8cf115ebd5cdec3adb87687e55",
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
        "chunk_id": 1969,
        "score": 0.7378194332122803,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1971,
        "score": 0.723166286945343,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1968,
        "score": 0.7016808390617371,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1965,
        "score": 0.6786966323852539,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1966,
        "score": 0.6770289540290833,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1938,
        "score": 0.6754489541053772,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1940,
        "score": 0.6569998264312744,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1973,
        "score": 0.6457274556159973,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1942,
        "score": 0.6393616795539856,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1970,
        "score": 0.6385987401008606,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1931,
        "score": 0.6368440389633179,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1941,
        "score": 0.6317943930625916,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1967,
        "score": 0.6219385862350464,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1936,
        "score": 0.6189490556716919,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1939,
        "score": 0.6125789284706116,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1937,
        "score": 0.6121077537536621,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1949,
        "score": 0.6097642183303833,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1950,
        "score": 0.6039755344390869,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1947,
        "score": 0.6020753979682922,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1951,
        "score": 0.5959298610687256,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1972,
        "score": 0.5915417671203613,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1979,
        "score": 0.5711824893951416,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1932,
        "score": 0.5705702900886536,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1948,
        "score": 0.5658526420593262,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1976,
        "score": 0.5494536757469177,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1943,
        "score": 0.5331028699874878,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1977,
        "score": 0.521675705909729,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1935,
        "score": 0.4981663227081299,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1944,
        "score": 0.49812501668930054,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1974,
        "score": 0.46601760387420654,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1945,
        "score": 0.4591333270072937,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1975,
        "score": 0.4568917751312256,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1978,
        "score": 0.45109814405441284,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1946,
        "score": 0.44950807094573975,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1934,
        "score": 0.43748342990875244,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1953,
        "score": 0.43106430768966675,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1955,
        "score": 0.42112255096435547,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1958,
        "score": 0.4119040369987488,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1957,
        "score": 0.40407881140708923,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1956,
        "score": 0.3967636227607727,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1954,
        "score": 0.3893398642539978,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1933,
        "score": 0.38788095116615295,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1962,
        "score": 0.3652048707008362,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1980,
        "score": 0.36394211649894714,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1952,
        "score": 0.357978492975235,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1960,
        "score": 0.3514482378959656,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1963,
        "score": 0.34335750341415405,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1961,
        "score": 0.33531469106674194,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1964,
        "score": 0.3317301273345947,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1959,
        "score": 0.3232440948486328,
        "score_kind": "cosine"
      }
    ],
    "final_ranking": [
      {
        "chunk_id": 1969,
        "score": 0.7378194332122803,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1971,
        "score": 0.723166286945343,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1968,
        "score": 0.7016808390617371,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1965,
        "score": 0.6786966323852539,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1966,
        "score": 0.6770289540290833,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1938,
        "score": 0.6754489541053772,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1940,
        "score": 0.6569998264312744,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1973,
        "score": 0.6457274556159973,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1942,
        "score": 0.6393616795539856,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1970,
        "score": 0.6385987401008606,
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
          1965
        ],
        [
          1938
        ]
      ]
    },
    {
      "group_id": "g2",
      "alternatives": [
        [
          1969
        ]
      ]
    },
    {
      "group_id": "g3",
      "alternatives": [
        [
          1966
        ]
      ]
    }
  ],
  "candidate_ids": [
    1969,
    1968,
    1971,
    1972,
    1941,
    1965,
    1949,
    1951,
    1973,
    1977,
    1938,
    1967,
    1942,
    1947,
    1980,
    1974,
    1966,
    1979,
    1937,
    1976,
    1970,
    1932,
    1931,
    1944,
    1960,
    1939,
    1975,
    1952,
    1943,
    1954,
    1950,
    1935,
    1946,
    1948,
    1934,
    1978
  ],
  "final_ids": [
    1969,
    1968,
    1971,
    1972,
    1941,
    1965,
    1949,
    1951,
    1973,
    1977
  ],
  "prompt_citations": [
    {
      "n": 1,
      "chunk_id": "1969",
      "section_path": "退货退款政策/退换货运费承担",
      "question": "退换货运费承担",
      "answer": "无理由退货的退回运费由买家承担;因商品质量问题、发错货、少发漏发导致的退换货,运费由平台承担。运费承担以平台售后规则最终判定为准。"
    },
    {
      "n": 3,
      "chunk_id": "1971",
      "section_path": "退货退款政策/运输破损处理",
      "question": "运输破损处理",
      "answer": "商品运输途中破损的,请在签收后 48 小时内联系客服并提供开箱视频与照片,核实后可免费补发或退款,相关运费由平台承担。"
    },
    {
      "n": 5,
      "chunk_id": "1941",
      "section_path": "商品与购物 FAQ/发货时效多久",
      "question": "发货时效多久",
      "answer": "现货商品付款后 48 小时内发货,预售商品以商品详情页标注的发货时间为准。"
    },
    {
      "n": 7,
      "chunk_id": "1949",
      "section_path": "商品与购物 FAQ/商品缺货多久补货",
      "question": "商品缺货多久补货",
      "answer": "现货售罄的商品通常 3 至 7 天内补货,可在商品页点击「到货通知」,补货后系统会推送提醒。"
    },
    {
      "n": 9,
      "chunk_id": "1973",
      "section_path": "退货退款政策/预售与定金",
      "question": "预售与定金",
      "answer": "预售商品以详情页标注的时间发货;定金支付后不支持无理由退定金,尾款未按时支付的,定金按活动规则处理。"
    },
    {
      "n": 10,
      "chunk_id": "1977",
      "section_path": "积分规则/积分怎么用",
      "question": "积分怎么用",
      "answer": "积分可在结算时抵扣商品金额，100 积分抵 1 元现金，单笔订单最多抵 30 元，不用于抵扣偏远地区附加运费，也不支持直接提现。\n\n2000 积分可兑换自动饮水机滤芯 3 片，该兑换套装适用于 MH-W40，普通配送地区包邮；偏远地区附加配送费仍需按页面规则确认。MH-W40 的滤芯更换周期以商品规格手册为准。\n\n800 积分可兑换猫零食小样，普通配送地区另收 6 元运费；该兑换不直接套用普通购物订单的满 99 元包邮规则。兑换商品、可用库存及偏远地区配送规则以兑换页面标注为准。"
    },
    {
      "n": 8,
      "chunk_id": "1951",
      "section_path": "商品与购物 FAQ/会员运费权益",
      "question": "会员运费权益",
      "answer": "金卡会员每月享 3 次免运费权益,银卡会员享 1 次;权益不与偏远地区附加运费冲抵,当月未用完不结转。"
    },
    {
      "n": 6,
      "chunk_id": "1965",
      "section_path": "退货退款政策/无理由退货/适用范围",
      "question": "适用范围",
      "answer": "自签收之日起 7 天内,商品完好、不影响二次销售的,支持无理由退货。定制类、生鲜类商品除外。"
    },
    {
      "n": 4,
      "chunk_id": "1972",
      "section_path": "退货退款政策/不支持退货的商品",
      "question": "不支持退货的商品",
      "answer": "定制类、生鲜类、已拆封的猫砂等消耗品,以及标注「不支持无理由退货」的商品,非质量问题不支持退货。"
    },
    {
      "n": 2,
      "chunk_id": "1968",
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
      "reason": "回答为拒答，未提及7天无理由退货及商品完好等条件"
    },
    {
      "point_id": "p2",
      "covered": false,
      "reason": "回答为拒答，未说明寄回运费由谁承担"
    },
    {
      "point_id": "p3",
      "covered": false,
      "reason": "回答为拒答，未说明退款原路及到账时效"
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
  "elapsed_ms": 5807.306700153276,
  "judge_snapshot": {
    "prompt_version": "joint-generation-v2.1",
    "finish_reason": "stop"
  },
  "rewrite": {
    "policy_version": "original-query-on-invalid-v1",
    "status": "success",
    "error": null
  },
  "audit": {
    "audit_version": 1,
    "source_map_id": "af6590ab401319d942bddff0b30213a4cd888b8cf115ebd5cdec3adb87687e55",
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
        "chunk_id": 1969,
        "score": 10.676090240478516,
        "score_kind": "bm25"
      },
      {
        "chunk_id": 1968,
        "score": 9.836376190185547,
        "score_kind": "bm25"
      },
      {
        "chunk_id": 1971,
        "score": 7.268333435058594,
        "score_kind": "bm25"
      },
      {
        "chunk_id": 1972,
        "score": 5.63097620010376,
        "score_kind": "bm25"
      },
      {
        "chunk_id": 1941,
        "score": 4.741880416870117,
        "score_kind": "bm25"
      },
      {
        "chunk_id": 1965,
        "score": 4.518306732177734,
        "score_kind": "bm25"
      },
      {
        "chunk_id": 1949,
        "score": 4.484236717224121,
        "score_kind": "bm25"
      },
      {
        "chunk_id": 1951,
        "score": 4.33558988571167,
        "score_kind": "bm25"
      },
      {
        "chunk_id": 1973,
        "score": 4.041518211364746,
        "score_kind": "bm25"
      },
      {
        "chunk_id": 1977,
        "score": 3.6735312938690186,
        "score_kind": "bm25"
      },
      {
        "chunk_id": 1938,
        "score": 3.423988103866577,
        "score_kind": "bm25"
      },
      {
        "chunk_id": 1967,
        "score": 3.1294915676116943,
        "score_kind": "bm25"
      },
      {
        "chunk_id": 1942,
        "score": 3.048265218734741,
        "score_kind": "bm25"
      },
      {
        "chunk_id": 1947,
        "score": 2.904369831085205,
        "score_kind": "bm25"
      },
      {
        "chunk_id": 1980,
        "score": 2.8818564414978027,
        "score_kind": "bm25"
      },
      {
        "chunk_id": 1974,
        "score": 2.7881808280944824,
        "score_kind": "bm25"
      },
      {
        "chunk_id": 1966,
        "score": 2.4312641620635986,
        "score_kind": "bm25"
      },
      {
        "chunk_id": 1979,
        "score": 1.9325504302978516,
        "score_kind": "bm25"
      },
      {
        "chunk_id": 1937,
        "score": 1.8424832820892334,
        "score_kind": "bm25"
      },
      {
        "chunk_id": 1976,
        "score": 1.823819637298584,
        "score_kind": "bm25"
      },
      {
        "chunk_id": 1970,
        "score": 1.5415995121002197,
        "score_kind": "bm25"
      },
      {
        "chunk_id": 1932,
        "score": 1.3018649816513062,
        "score_kind": "bm25"
      },
      {
        "chunk_id": 1931,
        "score": 1.1889352798461914,
        "score_kind": "bm25"
      },
      {
        "chunk_id": 1944,
        "score": 1.1214089393615723,
        "score_kind": "bm25"
      },
      {
        "chunk_id": 1960,
        "score": 1.0838499069213867,
        "score_kind": "bm25"
      },
      {
        "chunk_id": 1939,
        "score": 1.0660427808761597,
        "score_kind": "bm25"
      },
      {
        "chunk_id": 1975,
        "score": 1.0572911500930786,
        "score_kind": "bm25"
      },
      {
        "chunk_id": 1952,
        "score": 1.0359933376312256,
        "score_kind": "bm25"
      },
      {
        "chunk_id": 1943,
        "score": 1.0168840885162354,
        "score_kind": "bm25"
      },
      {
        "chunk_id": 1954,
        "score": 0.984889805316925,
        "score_kind": "bm25"
      },
      {
        "chunk_id": 1950,
        "score": 0.9807054996490479,
        "score_kind": "bm25"
      },
      {
        "chunk_id": 1935,
        "score": 0.9720594882965088,
        "score_kind": "bm25"
      },
      {
        "chunk_id": 1946,
        "score": 0.9155580401420593,
        "score_kind": "bm25"
      },
      {
        "chunk_id": 1948,
        "score": 0.9155580401420593,
        "score_kind": "bm25"
      },
      {
        "chunk_id": 1934,
        "score": 0.8170415759086609,
        "score_kind": "bm25"
      },
      {
        "chunk_id": 1978,
        "score": 0.7920446395874023,
        "score_kind": "bm25"
      }
    ],
    "final_ranking": [
      {
        "chunk_id": 1969,
        "score": 10.676090240478516,
        "score_kind": "bm25"
      },
      {
        "chunk_id": 1968,
        "score": 9.836376190185547,
        "score_kind": "bm25"
      },
      {
        "chunk_id": 1971,
        "score": 7.268333435058594,
        "score_kind": "bm25"
      },
      {
        "chunk_id": 1972,
        "score": 5.63097620010376,
        "score_kind": "bm25"
      },
      {
        "chunk_id": 1941,
        "score": 4.741880416870117,
        "score_kind": "bm25"
      },
      {
        "chunk_id": 1965,
        "score": 4.518306732177734,
        "score_kind": "bm25"
      },
      {
        "chunk_id": 1949,
        "score": 4.484236717224121,
        "score_kind": "bm25"
      },
      {
        "chunk_id": 1951,
        "score": 4.33558988571167,
        "score_kind": "bm25"
      },
      {
        "chunk_id": 1973,
        "score": 4.041518211364746,
        "score_kind": "bm25"
      },
      {
        "chunk_id": 1977,
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
          1965
        ],
        [
          1938
        ]
      ]
    },
    {
      "group_id": "g2",
      "alternatives": [
        [
          1969
        ]
      ]
    },
    {
      "group_id": "g3",
      "alternatives": [
        [
          1966
        ]
      ]
    }
  ],
  "candidate_ids": [
    1969,
    1968,
    1971,
    1965,
    1941,
    1938,
    1973,
    1966,
    1942,
    1972,
    1949,
    1967,
    1951,
    1970,
    1947,
    1931,
    1937,
    1977,
    1979,
    1939,
    1974,
    1976,
    1932,
    1950,
    1944,
    1980,
    1943,
    1948,
    1975,
    1935,
    1946,
    1960,
    1978,
    1934,
    1954,
    1952,
    1940,
    1936,
    1945,
    1953,
    1955,
    1958,
    1957,
    1956,
    1933,
    1962,
    1963,
    1961,
    1964,
    1959
  ],
  "final_ids": [
    1969,
    1968,
    1971,
    1965,
    1941,
    1938,
    1973,
    1966,
    1942,
    1972
  ],
  "prompt_citations": [
    {
      "n": 1,
      "chunk_id": "1969",
      "section_path": "退货退款政策/退换货运费承担",
      "question": "退换货运费承担",
      "answer": "无理由退货的退回运费由买家承担;因商品质量问题、发错货、少发漏发导致的退换货,运费由平台承担。运费承担以平台售后规则最终判定为准。"
    },
    {
      "n": 3,
      "chunk_id": "1971",
      "section_path": "退货退款政策/运输破损处理",
      "question": "运输破损处理",
      "answer": "商品运输途中破损的,请在签收后 48 小时内联系客服并提供开箱视频与照片,核实后可免费补发或退款,相关运费由平台承担。"
    },
    {
      "n": 5,
      "chunk_id": "1941",
      "section_path": "商品与购物 FAQ/发货时效多久",
      "question": "发货时效多久",
      "answer": "现货商品付款后 48 小时内发货,预售商品以商品详情页标注的发货时间为准。"
    },
    {
      "n": 7,
      "chunk_id": "1973",
      "section_path": "退货退款政策/预售与定金",
      "question": "预售与定金",
      "answer": "预售商品以详情页标注的时间发货;定金支付后不支持无理由退定金,尾款未按时支付的,定金按活动规则处理。"
    },
    {
      "n": 9,
      "chunk_id": "1942",
      "section_path": "商品与购物 FAQ/运费怎么算",
      "question": "运费怎么算",
      "answer": "单笔订单满 99 元包邮,未满收取 10 元运费,偏远地区运费另计。邮费即运费,按此规则收取。"
    },
    {
      "n": 10,
      "chunk_id": "1972",
      "section_path": "退货退款政策/不支持退货的商品",
      "question": "不支持退货的商品",
      "answer": "定制类、生鲜类、已拆封的猫砂等消耗品,以及标注「不支持无理由退货」的商品,非质量问题不支持退货。"
    },
    {
      "n": 8,
      "chunk_id": "1966",
      "section_path": "退货退款政策/无理由退货/退款时效",
      "question": "退款时效",
      "answer": "退货商品经平台核验通过后,退款原路退回,到账时效以平台售后规则为准。"
    },
    {
      "n": 6,
      "chunk_id": "1938",
      "section_path": "商品与购物 FAQ/退货政策是什么",
      "question": "退货政策是什么",
      "answer": "支持 7 天无理由退货,商品需保持完好、不影响二次销售,具体以平台售后规则为准。"
    },
    {
      "n": 4,
      "chunk_id": "1965",
      "section_path": "退货退款政策/无理由退货/适用范围",
      "question": "适用范围",
      "answer": "自签收之日起 7 天内,商品完好、不影响二次销售的,支持无理由退货。定制类、生鲜类商品除外。"
    },
    {
      "n": 2,
      "chunk_id": "1968",
      "section_path": "退货退款政策/换货政策/换货运费",
      "question": "换货运费",
      "answer": "非质量问题的换货,往返运费由买家承担;因质量问题或发错货的换货,往返运费由平台承担。"
    }
  ],
  "decision": {
    "useful": true,
    "reason": "运费承担有明确证据；退款时效仅说以规则为准，无具体时长，不能承诺到账日期",
    "response_kind": "knowledge",
    "source": null
  },
  "answer": "您好，很高兴为您解答：\n\n**关于退货运费：**\n- 无理由退货（如不想要了）的退回运费由买家承担 [1]\n- 因商品质量问题、发错货、少发漏发导致的退换货，运费由平台承担，以平台售后规则最终判定为准 [1]\n\n**关于退款时效：**\n退货商品经平台核验通过后，退款将原路退回，到账时效以平台售后规则为准 [8]，我们无法保证具体到账日期。\n\n**温馨提示：** 自签收之日起 7 天内、商品完好且不影响二次销售的，支持无理由退货（定制类、生鲜类商品除外）[4]。\n\n如需办理退货，请提供您的订单号，我可以帮您查询。若仍有疑问，也可为您创建人工工单转人工处理。",
  "point_verdicts": [
    {
      "point_id": "p1",
      "covered": true,
      "reason": "回答明确自签收起7天内、商品完好且不影响二次销售支持无理由退货，并注明定制类、生鲜类除外"
    },
    {
      "point_id": "p2",
      "covered": true,
      "reason": "回答说明无理由退货寄回运费由买家承担，质量等问题由平台承担，以平台售后规则最终判定为准"
    },
    {
      "point_id": "p3",
      "covered": true,
      "reason": "回答说明核验通过后退款原路退回，到账时效以平台售后规则为准，未编造固定天数"
    }
  ],
  "claim_verdicts": [
    {
      "claim": "无理由退货（如不想要了）的退回运费由买家承担",
      "supported": true,
      "reason": "证据1明确无理由退货的退回运费由买家承担"
    },
    {
      "claim": "因商品质量问题、发错货、少发漏发导致的退换货运费由平台承担",
      "supported": true,
      "reason": "证据1明确此类退换货运费由平台承担"
    },
    {
      "claim": "运费承担以平台售后规则最终判定为准",
      "supported": true,
      "reason": "证据1明确运费承担以平台售后规则最终判定为准"
    },
    {
      "claim": "退货商品经平台核验通过后，退款将原路退回",
      "supported": true,
      "reason": "证据8明确核验通过后退款原路退回"
    },
    {
      "claim": "退款到账时效以平台售后规则为准，无法保证具体到账日期",
      "supported": true,
      "reason": "证据8明确到账时效以平台售后规则为准，未给固定天数"
    },
    {
      "claim": "自签收之日起7天内、商品完好且不影响二次销售的，支持无理由退货",
      "supported": true,
      "reason": "证据4明确自签收起7天内、商品完好不影响二次销售支持无理由退货"
    },
    {
      "claim": "定制类、生鲜类商品除外，不支持无理由退货",
      "supported": true,
      "reason": "证据4明确定制类、生鲜类商品除外，证据10也支持"
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
  "elapsed_ms": 14088.406400056556,
  "judge_snapshot": {
    "prompt_version": "joint-generation-v2.1",
    "finish_reason": "stop"
  },
  "rewrite": {
    "policy_version": "original-query-on-invalid-v1",
    "status": "success",
    "error": null
  },
  "audit": {
    "audit_version": 1,
    "source_map_id": "af6590ab401319d942bddff0b30213a4cd888b8cf115ebd5cdec3adb87687e55",
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
        "chunk_id": 1969,
        "score": 0.032786883413791656,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1968,
        "score": 0.0320020467042923,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1971,
        "score": 0.0320020467042923,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1965,
        "score": 0.03077651560306549,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1941,
        "score": 0.0292735043913126,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1938,
        "score": 0.029236022382974625,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1973,
        "score": 0.02919863536953926,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1966,
        "score": 0.028371628373861313,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1942,
        "score": 0.02819138392806053,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1972,
        "score": 0.027970679104328156,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1949,
        "score": 0.027912385761737823,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1967,
        "score": 0.027587518095970154,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1951,
        "score": 0.027205882593989372,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1970,
        "score": 0.026631392538547516,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1947,
        "score": 0.026171742007136345,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1931,
        "score": 0.026132699102163315,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1937,
        "score": 0.02581612393260002,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1977,
        "score": 0.02577996626496315,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1979,
        "score": 0.025015633553266525,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1939,
        "score": 0.024961240589618683,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1974,
        "score": 0.02426900714635849,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1976,
        "score": 0.024264706298708916,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1932,
        "score": 0.024243313819169998,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1950,
        "score": 0.02380952425301075,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1944,
        "score": 0.023140717297792435,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1980,
        "score": 0.022948719561100006,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1943,
        "score": 0.022863861173391342,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1948,
        "score": 0.022543059661984444,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1975,
        "score": 0.022363819181919098,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1935,
        "score": 0.022233203053474426,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1946,
        "score": 0.02139098569750786,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1960,
        "score": 0.021198667585849762,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1978,
        "score": 0.021169355139136314,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1934,
        "score": 0.021052632480859756,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1954,
        "score": 0.02101210132241249,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1952,
        "score": 0.02088744565844536,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1940,
        "score": 0.014925372786819935,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1936,
        "score": 0.013513513840734959,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1945,
        "score": 0.010989011265337467,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1953,
        "score": 0.010416666977107525,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1955,
        "score": 0.010309278033673763,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1958,
        "score": 0.010204081423580647,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1957,
        "score": 0.010101010091602802,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1956,
        "score": 0.009999999776482582,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1933,
        "score": 0.009803921915590763,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1962,
        "score": 0.009708737954497337,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1963,
        "score": 0.009345794096589088,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1961,
        "score": 0.009259259328246117,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1964,
        "score": 0.00917431153357029,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1959,
        "score": 0.00909090880304575,
        "score_kind": "rrf"
      }
    ],
    "final_ranking": [
      {
        "chunk_id": 1969,
        "score": 0.032786883413791656,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1968,
        "score": 0.0320020467042923,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1971,
        "score": 0.0320020467042923,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1965,
        "score": 0.03077651560306549,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1941,
        "score": 0.0292735043913126,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1938,
        "score": 0.029236022382974625,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1973,
        "score": 0.02919863536953926,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1966,
        "score": 0.028371628373861313,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1942,
        "score": 0.02819138392806053,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1972,
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
          1965
        ],
        [
          1938
        ]
      ]
    },
    {
      "group_id": "g2",
      "alternatives": [
        [
          1969
        ]
      ]
    },
    {
      "group_id": "g3",
      "alternatives": [
        [
          1966
        ]
      ]
    }
  ],
  "candidate_ids": [
    1969,
    1968,
    1971,
    1965,
    1941,
    1938,
    1973,
    1966,
    1942,
    1972,
    1949,
    1967,
    1951,
    1970,
    1947,
    1931,
    1937,
    1977,
    1979,
    1939,
    1974,
    1976,
    1932,
    1950,
    1944,
    1980,
    1943,
    1948,
    1975,
    1935,
    1946,
    1960,
    1978,
    1934,
    1954,
    1952,
    1940,
    1936,
    1945,
    1953,
    1955,
    1958,
    1957,
    1956,
    1933,
    1962,
    1963,
    1961,
    1964,
    1959
  ],
  "final_ids": [
    1969,
    1971,
    1968,
    1965,
    1966,
    1938,
    1940,
    1937,
    1942,
    1931
  ],
  "prompt_citations": [
    {
      "n": 1,
      "chunk_id": "1969",
      "section_path": "退货退款政策/退换货运费承担",
      "question": "退换货运费承担",
      "answer": "无理由退货的退回运费由买家承担;因商品质量问题、发错货、少发漏发导致的退换货,运费由平台承担。运费承担以平台售后规则最终判定为准。"
    },
    {
      "n": 3,
      "chunk_id": "1968",
      "section_path": "退货退款政策/换货政策/换货运费",
      "question": "换货运费",
      "answer": "非质量问题的换货,往返运费由买家承担;因质量问题或发错货的换货,往返运费由平台承担。"
    },
    {
      "n": 5,
      "chunk_id": "1966",
      "section_path": "退货退款政策/无理由退货/退款时效",
      "question": "退款时效",
      "answer": "退货商品经平台核验通过后,退款原路退回,到账时效以平台售后规则为准。"
    },
    {
      "n": 7,
      "chunk_id": "1940",
      "section_path": "商品与购物 FAQ/换货流程怎么走",
      "question": "换货流程怎么走",
      "answer": "收到商品 7 天内可申请换货,联系客服登记后将商品寄回,平台核验无误后补发新品。"
    },
    {
      "n": 9,
      "chunk_id": "1942",
      "section_path": "商品与购物 FAQ/运费怎么算",
      "question": "运费怎么算",
      "answer": "单笔订单满 99 元包邮,未满收取 10 元运费,偏远地区运费另计。邮费即运费,按此规则收取。"
    },
    {
      "n": 10,
      "chunk_id": "1931",
      "section_path": "售后手册/常见问题处理时限",
      "question": "常见问题处理时限",
      "answer": "| 问题类型 | 首次响应 | 处理时限 |\n| --- | --- | --- |\n| 退款 | 2 小时 | 3 个工作日 |\n| 换货 | 2 小时 | 5 个工作日 |\n| 维修 | 4 小时 | 7 个工作日 |\n| 投诉 | 1 小时 | 3 个工作日 |\n| 发票 | 4 小时 | 3 个工作日 |\n| 物流异常 | 2 小时 | 5 个工作日 |\n| 商品咨询 | 1 小时 | 当日 |\n| 价格保护 | 2 小时 | 3 个工作日 |\n| 账户问题 | 2 小时 | 3 个工作日 |\n| 退换货运费 | 2 小时 | 3 个工作日 |\n| 缺货补发 | 2 小时 | 5 个工作日 |\n| 其他 | 4 小时 | 7 个工作日 |"
    },
    {
      "n": 8,
      "chunk_id": "1937",
      "section_path": "售后手册/会员专属售后权益",
      "question": "会员专属售后权益",
      "answer": "金卡会员享优先客服接入与上门取件退换货;银卡会员享退换货运费权益 1 次/月。具体权益以会员中心页面标注为准。"
    },
    {
      "n": 6,
      "chunk_id": "1938",
      "section_path": "商品与购物 FAQ/退货政策是什么",
      "question": "退货政策是什么",
      "answer": "支持 7 天无理由退货,商品需保持完好、不影响二次销售,具体以平台售后规则为准。"
    },
    {
      "n": 4,
      "chunk_id": "1965",
      "section_path": "退货退款政策/无理由退货/适用范围",
      "question": "适用范围",
      "answer": "自签收之日起 7 天内,商品完好、不影响二次销售的,支持无理由退货。定制类、生鲜类商品除外。"
    },
    {
      "n": 2,
      "chunk_id": "1971",
      "section_path": "退货退款政策/运输破损处理",
      "question": "运输破损处理",
      "answer": "商品运输途中破损的,请在签收后 48 小时内联系客服并提供开箱视频与照片,核实后可免费补发或退款,相关运费由平台承担。"
    }
  ],
  "decision": {
    "useful": true,
    "reason": "运费承担有证据，退款到账仅能说明核验后原路退回",
    "response_kind": "knowledge",
    "source": null
  },
  "answer": "您好，很高兴为您解答：\n\n**1. 运费承担**\n- 无理由退货（非质量问题）的寄回运费由买家承担；因质量问题、发错货、少发漏发的退换货运费由平台承担，最终以平台售后规则判定为准。[1]\n- 无理由退货需在签收后 7 天内、商品完好不影响二次销售（定制类、生鲜类除外）。[4][6]\n\n**2. 退款到账**\n退货商品经平台核验通过后，退款将原路退回，具体到账时效以平台售后规则为准，平台无法承诺具体到账日期。[5]\n\n另外，银卡会员每月可享 1 次退换货运费权益，金卡会员可享上门取件退换货，具体以会员中心页面标注为准。[8]\n\n如需进一步处理，请提供订单号，我可以帮您查询或创建人工工单跟进。",
  "point_verdicts": [
    {
      "point_id": "p1",
      "covered": true,
      "reason": "回答提及签收后7天内、商品完好不影响二次销售、定制类生鲜类除外，条件完整。"
    },
    {
      "point_id": "p2",
      "covered": true,
      "reason": "回答说明无理由退货运费买家承担，质量等问题由平台承担，并以平台售后规则判定为准，保留条件。"
    },
    {
      "point_id": "p3",
      "covered": true,
      "reason": "回答说明核验通过后原路退回，到账时效以平台售后规则为准，未虚构固定天数。"
    }
  ],
  "claim_verdicts": [
    {
      "claim": "无理由退货（非质量问题）的寄回运费由买家承担；因质量问题、发错货、少发漏发的退换货运费由平台承担，最终以平台售后规则判定为准",
      "supported": true,
      "reason": "证据1明确说明两种情形的运费承担及以平台售后规则最终判定为准。"
    },
    {
      "claim": "无理由退货需在签收后7天内、商品完好不影响二次销售（定制类、生鲜类除外）",
      "supported": true,
      "reason": "证据4说明自签收之日起7天内商品完好支持无理由退货，定制类生鲜类除外。"
    },
    {
      "claim": "退货商品经平台核验通过后，退款将原路退回，具体到账时效以平台售后规则为准，平台无法承诺具体到账日期",
      "supported": true,
      "reason": "证据5说明核验通过后退款原路退回，到账时效以平台售后规则为准，资料未给固定天数。"
    },
    {
      "claim": "银卡会员每月可享1次退换货运费权益，金卡会员可享上门取件退换货，具体以会员中心页面标注为准",
      "supported": true,
      "reason": "证据8明确银卡会员每月1次退换货运费权益、金卡会员上门取件，并以会员中心页面标注为准。"
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
  "elapsed_ms": 16715.89559991844,
  "judge_snapshot": {
    "prompt_version": "joint-generation-v2.1",
    "finish_reason": "stop"
  },
  "rewrite": {
    "policy_version": "original-query-on-invalid-v1",
    "status": "success",
    "error": null
  },
  "audit": {
    "audit_version": 1,
    "source_map_id": "af6590ab401319d942bddff0b30213a4cd888b8cf115ebd5cdec3adb87687e55",
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
        "chunk_id": 1969,
        "score": 0.032786883413791656,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1968,
        "score": 0.0320020467042923,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1971,
        "score": 0.0320020467042923,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1965,
        "score": 0.03077651560306549,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1941,
        "score": 0.0292735043913126,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1938,
        "score": 0.029236022382974625,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1973,
        "score": 0.02919863536953926,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1966,
        "score": 0.028371628373861313,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1942,
        "score": 0.02819138392806053,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1972,
        "score": 0.027970679104328156,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1949,
        "score": 0.027912385761737823,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1967,
        "score": 0.027587518095970154,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1951,
        "score": 0.027205882593989372,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1970,
        "score": 0.026631392538547516,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1947,
        "score": 0.026171742007136345,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1931,
        "score": 0.026132699102163315,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1937,
        "score": 0.02581612393260002,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1977,
        "score": 0.02577996626496315,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1979,
        "score": 0.025015633553266525,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1939,
        "score": 0.024961240589618683,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1974,
        "score": 0.02426900714635849,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1976,
        "score": 0.024264706298708916,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1932,
        "score": 0.024243313819169998,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1950,
        "score": 0.02380952425301075,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1944,
        "score": 0.023140717297792435,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1980,
        "score": 0.022948719561100006,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1943,
        "score": 0.022863861173391342,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1948,
        "score": 0.022543059661984444,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1975,
        "score": 0.022363819181919098,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1935,
        "score": 0.022233203053474426,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1946,
        "score": 0.02139098569750786,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1960,
        "score": 0.021198667585849762,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1978,
        "score": 0.021169355139136314,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1934,
        "score": 0.021052632480859756,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1954,
        "score": 0.02101210132241249,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1952,
        "score": 0.02088744565844536,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1940,
        "score": 0.014925372786819935,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1936,
        "score": 0.013513513840734959,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1945,
        "score": 0.010989011265337467,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1953,
        "score": 0.010416666977107525,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1955,
        "score": 0.010309278033673763,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1958,
        "score": 0.010204081423580647,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1957,
        "score": 0.010101010091602802,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1956,
        "score": 0.009999999776482582,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1933,
        "score": 0.009803921915590763,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1962,
        "score": 0.009708737954497337,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1963,
        "score": 0.009345794096589088,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1961,
        "score": 0.009259259328246117,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1964,
        "score": 0.00917431153357029,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1959,
        "score": 0.00909090880304575,
        "score_kind": "rrf"
      }
    ],
    "final_ranking": [
      {
        "chunk_id": 1969,
        "score": 0.755034327507019,
        "score_kind": "rerank"
      },
      {
        "chunk_id": 1971,
        "score": 0.2908751964569092,
        "score_kind": "rerank"
      },
      {
        "chunk_id": 1968,
        "score": 0.2785279154777527,
        "score_kind": "rerank"
      },
      {
        "chunk_id": 1965,
        "score": 0.07386193424463272,
        "score_kind": "rerank"
      },
      {
        "chunk_id": 1966,
        "score": 0.04878987371921539,
        "score_kind": "rerank"
      },
      {
        "chunk_id": 1938,
        "score": 0.044496260583400726,
        "score_kind": "rerank"
      },
      {
        "chunk_id": 1940,
        "score": 0.03836245834827423,
        "score_kind": "rerank"
      },
      {
        "chunk_id": 1937,
        "score": 0.03164609521627426,
        "score_kind": "rerank"
      },
      {
        "chunk_id": 1942,
        "score": 0.03162839636206627,
        "score_kind": "rerank"
      },
      {
        "chunk_id": 1931,
        "score": 0.02395847626030445,
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
  "refused": false,
  "status": "completed",
  "stage": "complete",
  "query": "饮水机 MH-W20 和 MH-W60 的水箱和换滤芯周期分别是多少",
  "query_plan": {
    "standard": "饮水机 MH-W20 和 MH-W60 的水箱和换滤芯周期分别是多少",
    "expansions": []
  },
  "mapped_groups": [
    {
      "group_id": "g1",
      "alternatives": [
        [
          1956
        ]
      ]
    },
    {
      "group_id": "g2",
      "alternatives": [
        [
          1958
        ]
      ]
    }
  ],
  "candidate_ids": [
    1956,
    1958,
    1957,
    1962,
    1955,
    1977,
    1963,
    1954,
    1953,
    1961,
    1934,
    1960,
    1936,
    1931,
    1932,
    1959,
    1970,
    1964,
    1940,
    1935,
    1952,
    1967,
    1937,
    1933,
    1965,
    1941,
    1980,
    1938,
    1968,
    1945,
    1949,
    1975,
    1979,
    1951,
    1974,
    1971,
    1973,
    1950,
    1966,
    1944,
    1948,
    1972,
    1943,
    1942,
    1947,
    1946,
    1976,
    1978,
    1969,
    1939
  ],
  "final_ids": [
    1956,
    1958,
    1957,
    1962,
    1955,
    1977,
    1963,
    1954,
    1953,
    1961
  ],
  "prompt_citations": [
    {
      "n": 1,
      "chunk_id": "1956",
      "section_path": "商品规格手册/自动饮水机(型号 MH-W20)",
      "question": "自动饮水机(型号 MH-W20)",
      "answer": "- 型号:MH-W20\n- 水箱容量:2L\n- 过滤:三重过滤棉,建议每 2 周更换一次滤芯\n- 核心功能:静音水泵、缺水断电保护、水位窗口\n- 清洗:水泵可拆卸,建议每周清洗一次"
    },
    {
      "n": 3,
      "chunk_id": "1957",
      "section_path": "商品规格手册/自动饮水机 Plus(型号 MH-W40)",
      "question": "自动饮水机 Plus(型号 MH-W40)",
      "answer": "- 型号:MH-W40\n- 水箱容量:4L\n- 过滤:五重过滤棉 + 椰壳活性炭,建议每 3 周更换一次滤芯\n- 核心功能:UV 紫外杀菌、静音变频水泵、缺水断电保护\n- 清洗:整机可拆分水洗,建议每周清洗一次"
    },
    {
      "n": 5,
      "chunk_id": "1955",
      "section_path": "商品规格手册/智能猫砂盆 Max(型号 MH-LP200)",
      "question": "智能猫砂盆 Max(型号 MH-LP200)",
      "answer": "- 型号:MH-LP200\n- 适用猫咪体重:2kg 至 12kg,适合大型猫与多猫家庭\n- 猫砂容量:12L,废砂盒容量约 10 天(单猫)\n- 核心功能:超大滚筒、双重称重防夹、活性炭除臭、App 多猫健康档案\n- 供电:220V 市电\n- 清理提示:多猫家庭建议每 3 至 5 天倾倒一次废砂盒"
    },
    {
      "n": 7,
      "chunk_id": "1963",
      "section_path": "商品规格手册/自动喂食器 摄像头版(型号 MH-FD30)",
      "question": "自动喂食器 摄像头版(型号 MH-FD30)",
      "answer": "- 型号:MH-FD30\n- 粮桶容量:6L\n- 核心功能:1080P 摄像头、双向语音、App 远程手动投喂与定时投喂\n- 供电:市电供电 + 内置应急电池\n- 说明:摄像头版支持视频回看,需连接 2.4G Wi-Fi"
    },
    {
      "n": 9,
      "chunk_id": "1953",
      "section_path": "商品规格手册/智能猫砂盆 Pro(型号 MH-LP100)",
      "question": "智能猫砂盆 Pro(型号 MH-LP100)",
      "answer": "- 型号:MH-LP100\n- 适用猫咪体重:1.5kg 至 8kg\n- 猫砂容量:9L,废砂盒容量约 7 天(单猫)\n- 核心功能:自动感应清理、活性炭除臭、App 远程监控与健康记录\n- 供电:220V 市电,断电后配置自动保存\n- 清理提示:废砂盒满时 App 推送提醒,建议每 5 至 7 天倾倒一次"
    },
    {
      "n": 10,
      "chunk_id": "1961",
      "section_path": "商品规格手册/大号三档加热垫(型号 MH-HP20)",
      "question": "大号三档加热垫(型号 MH-HP20)",
      "answer": "- 型号:MH-HP20\n- 尺寸:60cm × 45cm\n- 温控:三档可调 30℃ / 38℃ / 45℃,内置过热保护与定时关机\n- 防护:防水防抓咬电线套管,表面绒布可拆洗\n- 适用:大型猫、多猫窝及冬季保暖"
    },
    {
      "n": 8,
      "chunk_id": "1954",
      "section_path": "商品规格手册/智能猫砂盆 Lite(型号 MH-LP50)",
      "question": "智能猫砂盆 Lite(型号 MH-LP50)",
      "answer": "- 型号:MH-LP50\n- 适用猫咪体重:1.5kg 至 6kg\n- 猫砂容量:6L\n- 核心功能:自动感应清理、物理除臭盖板;不含 App 联网功能\n- 与 Pro 差异:Lite 无 App 远程监控与健康记录,价格更低,适合单猫家庭"
    },
    {
      "n": 6,
      "chunk_id": "1977",
      "section_path": "积分规则/积分怎么用",
      "question": "积分怎么用",
      "answer": "积分可在结算时抵扣商品金额，100 积分抵 1 元现金，单笔订单最多抵 30 元，不用于抵扣偏远地区附加运费，也不支持直接提现。\n\n2000 积分可兑换自动饮水机滤芯 3 片，该兑换套装适用于 MH-W40，普通配送地区包邮；偏远地区附加配送费仍需按页面规则确认。MH-W40 的滤芯更换周期以商品规格手册为准。\n\n800 积分可兑换猫零食小样，普通配送地区另收 6 元运费；该兑换不直接套用普通购物订单的满 99 元包邮规则。兑换商品、可用库存及偏远地区配送规则以兑换页面标注为准。"
    },
    {
      "n": 4,
      "chunk_id": "1962",
      "section_path": "商品规格手册/自动喂食器 基础版(型号 MH-FD10)",
      "question": "自动喂食器 基础版(型号 MH-FD10)",
      "answer": "- 型号:MH-FD10\n- 粮桶容量:4L\n- 核心功能:定时定量投喂,每日最多 6 餐,语音呼唤进食\n- 供电:市电供电 + 4 节 5 号电池断电应急\n- 说明:基础版不含摄像头与 App 远程投喂"
    },
    {
      "n": 2,
      "chunk_id": "1958",
      "section_path": "商品规格手册/自动饮水机 Pro 不锈钢(型号 MH-W60)",
      "question": "自动饮水机 Pro 不锈钢(型号 MH-W60)",
      "answer": "- 型号:MH-W60\n- 水箱容量:6L,304 不锈钢表面盘\n- 过滤:双滤芯并联,建议每 4 周更换一次滤芯\n- 核心功能:双泵冗余、无线水位提醒推送 App、缺水断电保护\n- 清洗:不锈钢面盘可高温消毒,建议每周清洗一次"
    }
  ],
  "decision": {
    "useful": true,
    "reason": "两型号规格均有证据",
    "response_kind": "knowledge",
    "source": null
  },
  "answer": "您好，为您查询到两款饮水机的参数如下：\n\n**MH-W20 自动饮水机**[1]\n- 水箱容量：2L\n- 滤芯：三重过滤棉，建议每 2 周更换一次\n- 另：水泵可拆卸，建议每周清洗一次\n\n**MH-W60 自动饮水机 Pro 不锈钢**[2]\n- 水箱容量：6L，304 不锈钢表面盘\n- 滤芯：双滤芯并联，建议每 4 周更换一次\n- 另：不锈钢面盘可高温消毒，建议每周清洗一次\n\n还有其他问题欢迎随时咨询~",
  "point_verdicts": [
    {
      "point_id": "p1",
      "covered": true,
      "reason": "回答明确MH-W20水箱2L、滤芯建议每2周更换，含条件范围，与证据[1]一致"
    },
    {
      "point_id": "p2",
      "covered": true,
      "reason": "回答明确MH-W60水箱6L、滤芯建议每4周更换，含Pro不锈钢条件，与证据[2]一致"
    }
  ],
  "claim_verdicts": [
    {
      "claim": "MH-W20自动饮水机水箱容量为2L",
      "supported": true,
      "reason": "证据[1] MH-W20规格明确水箱容量2L"
    },
    {
      "claim": "MH-W20滤芯为三重过滤棉，建议每2周更换一次",
      "supported": true,
      "reason": "证据[1]明确三重过滤棉，建议每2周更换一次滤芯"
    },
    {
      "claim": "MH-W20水泵可拆卸，建议每周清洗一次",
      "supported": true,
      "reason": "证据[1]清洗项明确水泵可拆卸、每周清洗一次"
    },
    {
      "claim": "MH-W60水箱容量为6L，304不锈钢表面盘",
      "supported": true,
      "reason": "证据[2]明确水箱容量6L，304不锈钢表面盘"
    },
    {
      "claim": "MH-W60滤芯为双滤芯并联，建议每4周更换一次",
      "supported": true,
      "reason": "证据[2]明确双滤芯并联，建议每4周更换一次滤芯"
    },
    {
      "claim": "MH-W60不锈钢面盘可高温消毒，建议每周清洗一次",
      "supported": true,
      "reason": "证据[2]清洗项明确不锈钢面盘可高温消毒、每周清洗一次"
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
  "elapsed_ms": 9672.576799988747,
  "judge_snapshot": {
    "prompt_version": "joint-generation-v2.1",
    "finish_reason": "stop"
  },
  "rewrite": {
    "policy_version": "original-query-on-invalid-v1",
    "status": "success",
    "error": null
  },
  "audit": {
    "audit_version": 1,
    "source_map_id": "af6590ab401319d942bddff0b30213a4cd888b8cf115ebd5cdec3adb87687e55",
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
    "candidate_ranking": [
      {
        "chunk_id": 1956,
        "score": 0.7491924166679382,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1958,
        "score": 0.7163623571395874,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1957,
        "score": 0.711978018283844,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1962,
        "score": 0.524499773979187,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1955,
        "score": 0.5220708250999451,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1977,
        "score": 0.5157341957092285,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1963,
        "score": 0.5126106142997742,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1954,
        "score": 0.5071249008178711,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1953,
        "score": 0.5027352571487427,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1961,
        "score": 0.4743978679180145,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1934,
        "score": 0.4701348543167114,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1960,
        "score": 0.4494839906692505,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1936,
        "score": 0.428796648979187,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1931,
        "score": 0.42380839586257935,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1932,
        "score": 0.42317119240760803,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1959,
        "score": 0.4148050546646118,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1970,
        "score": 0.4146609306335449,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1964,
        "score": 0.40818944573402405,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1940,
        "score": 0.39969393610954285,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1935,
        "score": 0.3915839195251465,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1952,
        "score": 0.38697028160095215,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1967,
        "score": 0.38325387239456177,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1937,
        "score": 0.3735676109790802,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1933,
        "score": 0.36839866638183594,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1965,
        "score": 0.36592555046081543,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1941,
        "score": 0.3603802025318146,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1980,
        "score": 0.3579448461532593,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1938,
        "score": 0.3404611051082611,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1968,
        "score": 0.33466318249702454,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1945,
        "score": 0.3336246609687805,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1949,
        "score": 0.332258403301239,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1975,
        "score": 0.3299570679664612,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1979,
        "score": 0.3231099247932434,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1951,
        "score": 0.3224828839302063,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1974,
        "score": 0.3146795332431793,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1971,
        "score": 0.31305229663848877,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1973,
        "score": 0.2995791435241699,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1950,
        "score": 0.2961851954460144,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1966,
        "score": 0.29556962847709656,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1944,
        "score": 0.29312318563461304,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1948,
        "score": 0.2925332486629486,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1972,
        "score": 0.288592129945755,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1943,
        "score": 0.2812553346157074,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1942,
        "score": 0.2784869074821472,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1947,
        "score": 0.27698642015457153,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1946,
        "score": 0.2711619436740875,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1976,
        "score": 0.26930639147758484,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1978,
        "score": 0.26704636216163635,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1969,
        "score": 0.2628505825996399,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1939,
        "score": 0.2585621178150177,
        "score_kind": "cosine"
      }
    ],
    "final_ranking": [
      {
        "chunk_id": 1956,
        "score": 0.7491924166679382,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1958,
        "score": 0.7163623571395874,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1957,
        "score": 0.711978018283844,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1962,
        "score": 0.524499773979187,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1955,
        "score": 0.5220708250999451,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1977,
        "score": 0.5157341957092285,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1963,
        "score": 0.5126106142997742,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1954,
        "score": 0.5071249008178711,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1953,
        "score": 0.5027352571487427,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1961,
        "score": 0.4743978679180145,
        "score_kind": "cosine"
      }
    ]
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
  "refused": false,
  "status": "completed",
  "stage": "complete",
  "query": "饮水机 MH-W20 和 MH-W60 的水箱和换滤芯周期分别是多少",
  "query_plan": {
    "standard": "饮水机 MH-W20 和 MH-W60 的水箱和换滤芯周期分别是多少",
    "expansions": []
  },
  "mapped_groups": [
    {
      "group_id": "g1",
      "alternatives": [
        [
          1956
        ]
      ]
    },
    {
      "group_id": "g2",
      "alternatives": [
        [
          1958
        ]
      ]
    }
  ],
  "candidate_ids": [
    1956,
    1958,
    1957,
    1977,
    1946,
    1978,
    1974,
    1968,
    1934,
    1938,
    1959,
    1960,
    1961,
    1954,
    1964,
    1962,
    1963,
    1955,
    1953,
    1972,
    1973,
    1969,
    1980,
    1939,
    1941,
    1952,
    1943,
    1949,
    1967,
    1965,
    1950,
    1935,
    1971,
    1948,
    1976,
    1979
  ],
  "final_ids": [
    1956,
    1958,
    1957,
    1977,
    1946,
    1978,
    1974,
    1968,
    1934,
    1938
  ],
  "prompt_citations": [
    {
      "n": 1,
      "chunk_id": "1956",
      "section_path": "商品规格手册/自动饮水机(型号 MH-W20)",
      "question": "自动饮水机(型号 MH-W20)",
      "answer": "- 型号:MH-W20\n- 水箱容量:2L\n- 过滤:三重过滤棉,建议每 2 周更换一次滤芯\n- 核心功能:静音水泵、缺水断电保护、水位窗口\n- 清洗:水泵可拆卸,建议每周清洗一次"
    },
    {
      "n": 3,
      "chunk_id": "1957",
      "section_path": "商品规格手册/自动饮水机 Plus(型号 MH-W40)",
      "question": "自动饮水机 Plus(型号 MH-W40)",
      "answer": "- 型号:MH-W40\n- 水箱容量:4L\n- 过滤:五重过滤棉 + 椰壳活性炭,建议每 3 周更换一次滤芯\n- 核心功能:UV 紫外杀菌、静音变频水泵、缺水断电保护\n- 清洗:整机可拆分水洗,建议每周清洗一次"
    },
    {
      "n": 5,
      "chunk_id": "1946",
      "section_path": "商品与购物 FAQ/优惠券和满减怎么用",
      "question": "优惠券和满减怎么用",
      "answer": "优惠券在结算页「使用优惠券」中勾选,满减活动自动叠加在商品页标示的门槛上;同一订单一般限用一张店铺券,活动细则以页面为准。"
    },
    {
      "n": 7,
      "chunk_id": "1974",
      "section_path": "会员权益/会员等级",
      "question": "会员等级",
      "answer": "会员分为普通、银卡和金卡三档，按有效累计消费金额自动升级，不按年度消费金额计算。累计消费未满 1000 元为普通会员，满 1000 元起为银卡，满 5000 元起为金卡。\n\n有效累计消费指已完成订单的商品实际支付金额，不含配送费；退货退款部分从有效累计消费中扣除。退款后根据更新的累计消费重新计算等级，未达到原门槛时可能降级。等级与适用权益在会员中心展示。\n\n银卡在参与会员折扣的商品上享 95 折，金卡享 9 折。折扣适用商品和活动范围以结算页面标注为准。会员折扣、优惠券与满减是否叠加也以当次活动页面为准，不能一概承诺全部优惠同时生效。"
    },
    {
      "n": 9,
      "chunk_id": "1934",
      "section_path": "售后手册/常见故障自查",
      "question": "常见故障自查",
      "answer": "- 饮水机不出水:检查水位是否低于最低线、水泵是否卡阻,断电清洗水泵后重试。\n- 猫砂盆报错:清空废砂盒并检查滚筒是否卡砂,重启设备;仍报错联系售后。\n- 喂食器卡粮:检查粮食颗粒直径是否超 12mm、粮桶是否受潮结块,清理出粮口后重试。\n- 摄像头离线:确认 Wi-Fi 为 2.4G 频段、信号良好,重启设备或在 App 内重新配网。"
    },
    {
      "n": 10,
      "chunk_id": "1938",
      "section_path": "商品与购物 FAQ/退货政策是什么",
      "question": "退货政策是什么",
      "answer": "支持 7 天无理由退货,商品需保持完好、不影响二次销售,具体以平台售后规则为准。"
    },
    {
      "n": 8,
      "chunk_id": "1968",
      "section_path": "退货退款政策/换货政策/换货运费",
      "question": "换货运费",
      "answer": "非质量问题的换货,往返运费由买家承担;因质量问题或发错货的换货,往返运费由平台承担。"
    },
    {
      "n": 6,
      "chunk_id": "1978",
      "section_path": "开票细则/可开票类型",
      "question": "可开票类型",
      "answer": "本演示店提供电子普通发票、电子专用发票和纸质专用发票。电子普通发票可按订单申请；电子专票需要企业账户，申请前准备发票抬头及有效纳税人识别号，按申请页面提交资料。\n\n纸质专票仅企业账户可申请，申请时需提供企业开票资料、收件人和邮寄地址，快递费到付。资料审核通过后按开票流程寄出，不承诺快递送达日期。"
    },
    {
      "n": 4,
      "chunk_id": "1977",
      "section_path": "积分规则/积分怎么用",
      "question": "积分怎么用",
      "answer": "积分可在结算时抵扣商品金额，100 积分抵 1 元现金，单笔订单最多抵 30 元，不用于抵扣偏远地区附加运费，也不支持直接提现。\n\n2000 积分可兑换自动饮水机滤芯 3 片，该兑换套装适用于 MH-W40，普通配送地区包邮；偏远地区附加配送费仍需按页面规则确认。MH-W40 的滤芯更换周期以商品规格手册为准。\n\n800 积分可兑换猫零食小样，普通配送地区另收 6 元运费；该兑换不直接套用普通购物订单的满 99 元包邮规则。兑换商品、可用库存及偏远地区配送规则以兑换页面标注为准。"
    },
    {
      "n": 2,
      "chunk_id": "1958",
      "section_path": "商品规格手册/自动饮水机 Pro 不锈钢(型号 MH-W60)",
      "question": "自动饮水机 Pro 不锈钢(型号 MH-W60)",
      "answer": "- 型号:MH-W60\n- 水箱容量:6L,304 不锈钢表面盘\n- 过滤:双滤芯并联,建议每 4 周更换一次滤芯\n- 核心功能:双泵冗余、无线水位提醒推送 App、缺水断电保护\n- 清洗:不锈钢面盘可高温消毒,建议每周清洗一次"
    }
  ],
  "decision": {
    "useful": true,
    "reason": "两型号水箱与换芯周期均有证据",
    "response_kind": "knowledge",
    "source": null
  },
  "answer": "您好！两款饮水机的水箱和滤芯周期如下：\n\n- **MH-W20 自动饮水机**：水箱容量 2L，三重过滤棉，建议每 2 周更换一次滤芯 [1]\n- **MH-W60 自动饮水机 Pro 不锈钢**：水箱容量 6L（304 不锈钢表面盘），双滤芯并联，建议每 4 周更换一次滤芯 [2]\n\n另外，两款均建议每周清洗一次 [1][2]。如还有其他问题，欢迎随时咨询！",
  "point_verdicts": [
    {
      "point_id": "p1",
      "covered": true,
      "reason": "回答说明MH-W20水箱2L、滤芯建议每2周更换，含条件适用范围，证据1支持"
    },
    {
      "point_id": "p2",
      "covered": true,
      "reason": "回答说明MH-W60 Pro不锈钢水箱6L、滤芯建议每4周更换，证据2支持"
    }
  ],
  "claim_verdicts": [
    {
      "claim": "MH-W20 自动饮水机水箱容量为2L",
      "supported": true,
      "reason": "证据1明确标注水箱容量2L"
    },
    {
      "claim": "MH-W20 采用三重过滤棉，建议每2周更换一次滤芯",
      "supported": true,
      "reason": "证据1明确标注过滤方式及2周更换建议"
    },
    {
      "claim": "MH-W60 Pro 不锈钢水箱容量为6L，304不锈钢表面盘",
      "supported": true,
      "reason": "证据2明确标注水箱容量6L及304不锈钢表面盘"
    },
    {
      "claim": "MH-W60 采用双滤芯并联，建议每4周更换一次滤芯",
      "supported": true,
      "reason": "证据2明确标注双滤芯并联及4周更换建议"
    },
    {
      "claim": "MH-W20 建议每周清洗一次",
      "supported": true,
      "reason": "证据1明确标注建议每周清洗一次"
    },
    {
      "claim": "MH-W60 建议每周清洗一次",
      "supported": true,
      "reason": "证据2明确标注建议每周清洗一次"
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
  "elapsed_ms": 9380.809900118038,
  "judge_snapshot": {
    "prompt_version": "joint-generation-v2.1",
    "finish_reason": "stop"
  },
  "rewrite": {
    "policy_version": "original-query-on-invalid-v1",
    "status": "success",
    "error": null
  },
  "audit": {
    "audit_version": 1,
    "source_map_id": "af6590ab401319d942bddff0b30213a4cd888b8cf115ebd5cdec3adb87687e55",
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
    "candidate_ranking": [
      {
        "chunk_id": 1956,
        "score": 21.04051399230957,
        "score_kind": "bm25"
      },
      {
        "chunk_id": 1958,
        "score": 20.065227508544922,
        "score_kind": "bm25"
      },
      {
        "chunk_id": 1957,
        "score": 15.246339797973633,
        "score_kind": "bm25"
      },
      {
        "chunk_id": 1977,
        "score": 12.108427047729492,
        "score_kind": "bm25"
      },
      {
        "chunk_id": 1946,
        "score": 6.594915866851807,
        "score_kind": "bm25"
      },
      {
        "chunk_id": 1978,
        "score": 6.17706298828125,
        "score_kind": "bm25"
      },
      {
        "chunk_id": 1974,
        "score": 6.0217061042785645,
        "score_kind": "bm25"
      },
      {
        "chunk_id": 1968,
        "score": 5.385351181030273,
        "score_kind": "bm25"
      },
      {
        "chunk_id": 1934,
        "score": 5.383184432983398,
        "score_kind": "bm25"
      },
      {
        "chunk_id": 1938,
        "score": 4.2695698738098145,
        "score_kind": "bm25"
      },
      {
        "chunk_id": 1959,
        "score": 3.8244388103485107,
        "score_kind": "bm25"
      },
      {
        "chunk_id": 1960,
        "score": 3.8244388103485107,
        "score_kind": "bm25"
      },
      {
        "chunk_id": 1961,
        "score": 3.6993556022644043,
        "score_kind": "bm25"
      },
      {
        "chunk_id": 1954,
        "score": 3.5821950435638428,
        "score_kind": "bm25"
      },
      {
        "chunk_id": 1964,
        "score": 3.5821950435638428,
        "score_kind": "bm25"
      },
      {
        "chunk_id": 1962,
        "score": 3.5633859634399414,
        "score_kind": "bm25"
      },
      {
        "chunk_id": 1963,
        "score": 3.5081260204315186,
        "score_kind": "bm25"
      },
      {
        "chunk_id": 1955,
        "score": 3.3193798065185547,
        "score_kind": "bm25"
      },
      {
        "chunk_id": 1953,
        "score": 3.3032233715057373,
        "score_kind": "bm25"
      },
      {
        "chunk_id": 1972,
        "score": 1.4414697885513306,
        "score_kind": "bm25"
      },
      {
        "chunk_id": 1973,
        "score": 1.2937390804290771,
        "score_kind": "bm25"
      },
      {
        "chunk_id": 1969,
        "score": 1.215309500694275,
        "score_kind": "bm25"
      },
      {
        "chunk_id": 1980,
        "score": 1.1236776113510132,
        "score_kind": "bm25"
      },
      {
        "chunk_id": 1939,
        "score": 1.0660427808761597,
        "score_kind": "bm25"
      },
      {
        "chunk_id": 1941,
        "score": 1.0558345317840576,
        "score_kind": "bm25"
      },
      {
        "chunk_id": 1952,
        "score": 1.0359933376312256,
        "score_kind": "bm25"
      },
      {
        "chunk_id": 1943,
        "score": 1.0168840885162354,
        "score_kind": "bm25"
      },
      {
        "chunk_id": 1949,
        "score": 0.998467206954956,
        "score_kind": "bm25"
      },
      {
        "chunk_id": 1967,
        "score": 0.998467206954956,
        "score_kind": "bm25"
      },
      {
        "chunk_id": 1965,
        "score": 0.9895066618919373,
        "score_kind": "bm25"
      },
      {
        "chunk_id": 1950,
        "score": 0.9807054996490479,
        "score_kind": "bm25"
      },
      {
        "chunk_id": 1935,
        "score": 0.9720594882965088,
        "score_kind": "bm25"
      },
      {
        "chunk_id": 1971,
        "score": 0.9470126032829285,
        "score_kind": "bm25"
      },
      {
        "chunk_id": 1948,
        "score": 0.9155580401420593,
        "score_kind": "bm25"
      },
      {
        "chunk_id": 1976,
        "score": 0.8389298319816589,
        "score_kind": "bm25"
      },
      {
        "chunk_id": 1979,
        "score": 0.7139831781387329,
        "score_kind": "bm25"
      }
    ],
    "final_ranking": [
      {
        "chunk_id": 1956,
        "score": 21.04051399230957,
        "score_kind": "bm25"
      },
      {
        "chunk_id": 1958,
        "score": 20.065227508544922,
        "score_kind": "bm25"
      },
      {
        "chunk_id": 1957,
        "score": 15.246339797973633,
        "score_kind": "bm25"
      },
      {
        "chunk_id": 1977,
        "score": 12.108427047729492,
        "score_kind": "bm25"
      },
      {
        "chunk_id": 1946,
        "score": 6.594915866851807,
        "score_kind": "bm25"
      },
      {
        "chunk_id": 1978,
        "score": 6.17706298828125,
        "score_kind": "bm25"
      },
      {
        "chunk_id": 1974,
        "score": 6.0217061042785645,
        "score_kind": "bm25"
      },
      {
        "chunk_id": 1968,
        "score": 5.385351181030273,
        "score_kind": "bm25"
      },
      {
        "chunk_id": 1934,
        "score": 5.383184432983398,
        "score_kind": "bm25"
      },
      {
        "chunk_id": 1938,
        "score": 4.2695698738098145,
        "score_kind": "bm25"
      }
    ]
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
  "refused": false,
  "status": "completed",
  "stage": "complete",
  "query": "饮水机 MH-W20 和 MH-W60 的水箱和换滤芯周期分别是多少",
  "query_plan": {
    "standard": "饮水机 MH-W20 和 MH-W60 的水箱和换滤芯周期分别是多少",
    "expansions": []
  },
  "mapped_groups": [
    {
      "group_id": "g1",
      "alternatives": [
        [
          1956
        ]
      ]
    },
    {
      "group_id": "g2",
      "alternatives": [
        [
          1958
        ]
      ]
    }
  ],
  "candidate_ids": [
    1956,
    1958,
    1957,
    1977,
    1962,
    1934,
    1954,
    1955,
    1961,
    1963,
    1960,
    1959,
    1953,
    1964,
    1968,
    1938,
    1974,
    1946,
    1978,
    1952,
    1980,
    1967,
    1941,
    1935,
    1965,
    1973,
    1949,
    1972,
    1969,
    1943,
    1950,
    1971,
    1979,
    1939,
    1948,
    1976,
    1936,
    1931,
    1932,
    1970,
    1940,
    1937,
    1933,
    1945,
    1975,
    1951,
    1966,
    1944,
    1942,
    1947
  ],
  "final_ids": [
    1956,
    1958,
    1957,
    1977,
    1962,
    1934,
    1954,
    1955,
    1961,
    1963
  ],
  "prompt_citations": [
    {
      "n": 1,
      "chunk_id": "1956",
      "section_path": "商品规格手册/自动饮水机(型号 MH-W20)",
      "question": "自动饮水机(型号 MH-W20)",
      "answer": "- 型号:MH-W20\n- 水箱容量:2L\n- 过滤:三重过滤棉,建议每 2 周更换一次滤芯\n- 核心功能:静音水泵、缺水断电保护、水位窗口\n- 清洗:水泵可拆卸,建议每周清洗一次"
    },
    {
      "n": 3,
      "chunk_id": "1957",
      "section_path": "商品规格手册/自动饮水机 Plus(型号 MH-W40)",
      "question": "自动饮水机 Plus(型号 MH-W40)",
      "answer": "- 型号:MH-W40\n- 水箱容量:4L\n- 过滤:五重过滤棉 + 椰壳活性炭,建议每 3 周更换一次滤芯\n- 核心功能:UV 紫外杀菌、静音变频水泵、缺水断电保护\n- 清洗:整机可拆分水洗,建议每周清洗一次"
    },
    {
      "n": 5,
      "chunk_id": "1962",
      "section_path": "商品规格手册/自动喂食器 基础版(型号 MH-FD10)",
      "question": "自动喂食器 基础版(型号 MH-FD10)",
      "answer": "- 型号:MH-FD10\n- 粮桶容量:4L\n- 核心功能:定时定量投喂,每日最多 6 餐,语音呼唤进食\n- 供电:市电供电 + 4 节 5 号电池断电应急\n- 说明:基础版不含摄像头与 App 远程投喂"
    },
    {
      "n": 7,
      "chunk_id": "1954",
      "section_path": "商品规格手册/智能猫砂盆 Lite(型号 MH-LP50)",
      "question": "智能猫砂盆 Lite(型号 MH-LP50)",
      "answer": "- 型号:MH-LP50\n- 适用猫咪体重:1.5kg 至 6kg\n- 猫砂容量:6L\n- 核心功能:自动感应清理、物理除臭盖板;不含 App 联网功能\n- 与 Pro 差异:Lite 无 App 远程监控与健康记录,价格更低,适合单猫家庭"
    },
    {
      "n": 9,
      "chunk_id": "1961",
      "section_path": "商品规格手册/大号三档加热垫(型号 MH-HP20)",
      "question": "大号三档加热垫(型号 MH-HP20)",
      "answer": "- 型号:MH-HP20\n- 尺寸:60cm × 45cm\n- 温控:三档可调 30℃ / 38℃ / 45℃,内置过热保护与定时关机\n- 防护:防水防抓咬电线套管,表面绒布可拆洗\n- 适用:大型猫、多猫窝及冬季保暖"
    },
    {
      "n": 10,
      "chunk_id": "1963",
      "section_path": "商品规格手册/自动喂食器 摄像头版(型号 MH-FD30)",
      "question": "自动喂食器 摄像头版(型号 MH-FD30)",
      "answer": "- 型号:MH-FD30\n- 粮桶容量:6L\n- 核心功能:1080P 摄像头、双向语音、App 远程手动投喂与定时投喂\n- 供电:市电供电 + 内置应急电池\n- 说明:摄像头版支持视频回看,需连接 2.4G Wi-Fi"
    },
    {
      "n": 8,
      "chunk_id": "1955",
      "section_path": "商品规格手册/智能猫砂盆 Max(型号 MH-LP200)",
      "question": "智能猫砂盆 Max(型号 MH-LP200)",
      "answer": "- 型号:MH-LP200\n- 适用猫咪体重:2kg 至 12kg,适合大型猫与多猫家庭\n- 猫砂容量:12L,废砂盒容量约 10 天(单猫)\n- 核心功能:超大滚筒、双重称重防夹、活性炭除臭、App 多猫健康档案\n- 供电:220V 市电\n- 清理提示:多猫家庭建议每 3 至 5 天倾倒一次废砂盒"
    },
    {
      "n": 6,
      "chunk_id": "1934",
      "section_path": "售后手册/常见故障自查",
      "question": "常见故障自查",
      "answer": "- 饮水机不出水:检查水位是否低于最低线、水泵是否卡阻,断电清洗水泵后重试。\n- 猫砂盆报错:清空废砂盒并检查滚筒是否卡砂,重启设备;仍报错联系售后。\n- 喂食器卡粮:检查粮食颗粒直径是否超 12mm、粮桶是否受潮结块,清理出粮口后重试。\n- 摄像头离线:确认 Wi-Fi 为 2.4G 频段、信号良好,重启设备或在 App 内重新配网。"
    },
    {
      "n": 4,
      "chunk_id": "1977",
      "section_path": "积分规则/积分怎么用",
      "question": "积分怎么用",
      "answer": "积分可在结算时抵扣商品金额，100 积分抵 1 元现金，单笔订单最多抵 30 元，不用于抵扣偏远地区附加运费，也不支持直接提现。\n\n2000 积分可兑换自动饮水机滤芯 3 片，该兑换套装适用于 MH-W40，普通配送地区包邮；偏远地区附加配送费仍需按页面规则确认。MH-W40 的滤芯更换周期以商品规格手册为准。\n\n800 积分可兑换猫零食小样，普通配送地区另收 6 元运费；该兑换不直接套用普通购物订单的满 99 元包邮规则。兑换商品、可用库存及偏远地区配送规则以兑换页面标注为准。"
    },
    {
      "n": 2,
      "chunk_id": "1958",
      "section_path": "商品规格手册/自动饮水机 Pro 不锈钢(型号 MH-W60)",
      "question": "自动饮水机 Pro 不锈钢(型号 MH-W60)",
      "answer": "- 型号:MH-W60\n- 水箱容量:6L,304 不锈钢表面盘\n- 过滤:双滤芯并联,建议每 4 周更换一次滤芯\n- 核心功能:双泵冗余、无线水位提醒推送 App、缺水断电保护\n- 清洗:不锈钢面盘可高温消毒,建议每周清洗一次"
    }
  ],
  "decision": {
    "useful": true,
    "reason": "两个型号的水箱容量与滤芯周期均有证据",
    "response_kind": "knowledge",
    "source": null
  },
  "answer": "您好！根据商品规格手册，为您解答：\n\n**MH-W20（自动饮水机）**[1]\n- 水箱容量：2L\n- 滤芯更换：三重过滤棉，建议每 2 周更换一次\n\n**MH-W60（自动饮水机 Pro 不锈钢）**[2]\n- 水箱容量：6L，304 不锈钢表面盘\n- 滤芯更换：双滤芯并联，建议每 4 周更换一次\n\n还有其他问题欢迎随时咨询～",
  "point_verdicts": [
    {
      "point_id": "p1",
      "covered": true,
      "reason": "回答明确MH-W20水箱2L、三重过滤棉建议每2周更换一次，含自动饮水机型号条件"
    },
    {
      "point_id": "p2",
      "covered": true,
      "reason": "回答明确MH-W60水箱6L、双滤芯并联建议每4周更换一次，含Pro不锈钢型号条件"
    }
  ],
  "claim_verdicts": [
    {
      "claim": "MH-W20水箱容量为2L",
      "supported": true,
      "reason": "证据[1]型号MH-W20水箱容量2L，完全支持"
    },
    {
      "claim": "MH-W20滤芯建议每2周更换一次",
      "supported": true,
      "reason": "证据[1]建议每2周更换一次滤芯，支持"
    },
    {
      "claim": "MH-W60水箱容量为6L，304不锈钢表面盘",
      "supported": true,
      "reason": "证据[2]水箱容量6L，304不锈钢表面盘，支持"
    },
    {
      "claim": "MH-W60滤芯为双滤芯并联，建议每4周更换一次",
      "supported": true,
      "reason": "证据[2]双滤芯并联，建议每4周更换一次滤芯，支持"
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
  "elapsed_ms": 8418.75599976629,
  "judge_snapshot": {
    "prompt_version": "joint-generation-v2.1",
    "finish_reason": "stop"
  },
  "rewrite": {
    "policy_version": "original-query-on-invalid-v1",
    "status": "success",
    "error": null
  },
  "audit": {
    "audit_version": 1,
    "source_map_id": "af6590ab401319d942bddff0b30213a4cd888b8cf115ebd5cdec3adb87687e55",
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
    "candidate_ranking": [
      {
        "chunk_id": 1956,
        "score": 0.032786883413791656,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1958,
        "score": 0.032258063554763794,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1957,
        "score": 0.0317460335791111,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1977,
        "score": 0.03077651560306549,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1962,
        "score": 0.02878289483487606,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1934,
        "score": 0.028577260673046112,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1954,
        "score": 0.028219396248459816,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1955,
        "score": 0.028205128386616707,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1961,
        "score": 0.027984343469142914,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1963,
        "score": 0.027912385761737823,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1960,
        "score": 0.02777777798473835,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1959,
        "score": 0.027242401614785194,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1953,
        "score": 0.02715098112821579,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1964,
        "score": 0.026153847575187683,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1968,
        "score": 0.025941837579011917,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1938,
        "score": 0.02564935013651848,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1974,
        "score": 0.025451689958572388,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1946,
        "score": 0.024818576872348785,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1978,
        "score": 0.024410774931311607,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1952,
        "score": 0.023973586037755013,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1980,
        "score": 0.02354244515299797,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1967,
        "score": 0.02343107759952545,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1941,
        "score": 0.023392613977193832,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1935,
        "score": 0.02336956560611725,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1965,
        "score": 0.022875817492604256,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1973,
        "score": 0.022654958069324493,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1949,
        "score": 0.02235264703631401,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1972,
        "score": 0.022303922101855278,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1969,
        "score": 0.021369433030486107,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1943,
        "score": 0.021202990785241127,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1950,
        "score": 0.021193092688918114,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1971,
        "score": 0.021169355139136314,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1979,
        "score": 0.021169355139136314,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1939,
        "score": 0.020995670929551125,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1948,
        "score": 0.020539287477731705,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1976,
        "score": 0.019872110337018967,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1936,
        "score": 0.013698630034923553,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1931,
        "score": 0.013513513840734959,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1932,
        "score": 0.013333333656191826,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1970,
        "score": 0.012987012974917889,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1940,
        "score": 0.012658228166401386,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1937,
        "score": 0.012048192322254181,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1933,
        "score": 0.011904762126505375,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1945,
        "score": 0.011111111380159855,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1975,
        "score": 0.010869565419852734,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1951,
        "score": 0.010638297535479069,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1966,
        "score": 0.010101010091602802,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1944,
        "score": 0.009999999776482582,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1942,
        "score": 0.009615384973585606,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1947,
        "score": 0.009523809887468815,
        "score_kind": "rrf"
      }
    ],
    "final_ranking": [
      {
        "chunk_id": 1956,
        "score": 0.032786883413791656,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1958,
        "score": 0.032258063554763794,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1957,
        "score": 0.0317460335791111,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1977,
        "score": 0.03077651560306549,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1962,
        "score": 0.02878289483487606,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1934,
        "score": 0.028577260673046112,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1954,
        "score": 0.028219396248459816,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1955,
        "score": 0.028205128386616707,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1961,
        "score": 0.027984343469142914,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1963,
        "score": 0.027912385761737823,
        "score_kind": "rrf"
      }
    ]
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
  "refused": false,
  "status": "completed",
  "stage": "complete",
  "query": "饮水机 MH-W20 和 MH-W60 的水箱和换滤芯周期分别是多少",
  "query_plan": {
    "standard": "饮水机 MH-W20 和 MH-W60 的水箱和换滤芯周期分别是多少",
    "expansions": []
  },
  "mapped_groups": [
    {
      "group_id": "g1",
      "alternatives": [
        [
          1956
        ]
      ]
    },
    {
      "group_id": "g2",
      "alternatives": [
        [
          1958
        ]
      ]
    }
  ],
  "candidate_ids": [
    1956,
    1958,
    1957,
    1977,
    1962,
    1934,
    1954,
    1955,
    1961,
    1963,
    1960,
    1959,
    1953,
    1964,
    1968,
    1938,
    1974,
    1946,
    1978,
    1952,
    1980,
    1967,
    1941,
    1935,
    1965,
    1973,
    1949,
    1972,
    1969,
    1943,
    1950,
    1971,
    1979,
    1939,
    1948,
    1976,
    1936,
    1931,
    1932,
    1970,
    1940,
    1937,
    1933,
    1945,
    1975,
    1951,
    1966,
    1944,
    1942,
    1947
  ],
  "final_ids": [
    1956,
    1958,
    1957,
    1977,
    1932,
    1961,
    1970,
    1967,
    1937,
    1934
  ],
  "prompt_citations": [
    {
      "n": 1,
      "chunk_id": "1956",
      "section_path": "商品规格手册/自动饮水机(型号 MH-W20)",
      "question": "自动饮水机(型号 MH-W20)",
      "answer": "- 型号:MH-W20\n- 水箱容量:2L\n- 过滤:三重过滤棉,建议每 2 周更换一次滤芯\n- 核心功能:静音水泵、缺水断电保护、水位窗口\n- 清洗:水泵可拆卸,建议每周清洗一次"
    },
    {
      "n": 3,
      "chunk_id": "1957",
      "section_path": "商品规格手册/自动饮水机 Plus(型号 MH-W40)",
      "question": "自动饮水机 Plus(型号 MH-W40)",
      "answer": "- 型号:MH-W40\n- 水箱容量:4L\n- 过滤:五重过滤棉 + 椰壳活性炭,建议每 3 周更换一次滤芯\n- 核心功能:UV 紫外杀菌、静音变频水泵、缺水断电保护\n- 清洗:整机可拆分水洗,建议每周清洗一次"
    },
    {
      "n": 5,
      "chunk_id": "1932",
      "section_path": "售后手册/保修说明",
      "question": "保修说明",
      "answer": "电子类商品保修 12 个月,自签收日起算;人为损坏不在保修范围。"
    },
    {
      "n": 7,
      "chunk_id": "1970",
      "section_path": "退货退款政策/质量问题与保修",
      "question": "质量问题与保修",
      "answer": "电子类商品自签收起保修 12 个月,保修期内非人为损坏可申请免费维修或换货;人为损坏、超保商品维修可能收取工本费。"
    },
    {
      "n": 9,
      "chunk_id": "1937",
      "section_path": "售后手册/会员专属售后权益",
      "question": "会员专属售后权益",
      "answer": "金卡会员享优先客服接入与上门取件退换货;银卡会员享退换货运费权益 1 次/月。具体权益以会员中心页面标注为准。"
    },
    {
      "n": 10,
      "chunk_id": "1934",
      "section_path": "售后手册/常见故障自查",
      "question": "常见故障自查",
      "answer": "- 饮水机不出水:检查水位是否低于最低线、水泵是否卡阻,断电清洗水泵后重试。\n- 猫砂盆报错:清空废砂盒并检查滚筒是否卡砂,重启设备;仍报错联系售后。\n- 喂食器卡粮:检查粮食颗粒直径是否超 12mm、粮桶是否受潮结块,清理出粮口后重试。\n- 摄像头离线:确认 Wi-Fi 为 2.4G 频段、信号良好,重启设备或在 App 内重新配网。"
    },
    {
      "n": 8,
      "chunk_id": "1967",
      "section_path": "退货退款政策/换货政策/换货条件",
      "question": "换货条件",
      "answer": "收到商品 7 天内,商品完好且配件齐全的,可申请一次同款换货;不同型号或颜色需先退货再重新下单。"
    },
    {
      "n": 6,
      "chunk_id": "1961",
      "section_path": "商品规格手册/大号三档加热垫(型号 MH-HP20)",
      "question": "大号三档加热垫(型号 MH-HP20)",
      "answer": "- 型号:MH-HP20\n- 尺寸:60cm × 45cm\n- 温控:三档可调 30℃ / 38℃ / 45℃,内置过热保护与定时关机\n- 防护:防水防抓咬电线套管,表面绒布可拆洗\n- 适用:大型猫、多猫窝及冬季保暖"
    },
    {
      "n": 4,
      "chunk_id": "1977",
      "section_path": "积分规则/积分怎么用",
      "question": "积分怎么用",
      "answer": "积分可在结算时抵扣商品金额，100 积分抵 1 元现金，单笔订单最多抵 30 元，不用于抵扣偏远地区附加运费，也不支持直接提现。\n\n2000 积分可兑换自动饮水机滤芯 3 片，该兑换套装适用于 MH-W40，普通配送地区包邮；偏远地区附加配送费仍需按页面规则确认。MH-W40 的滤芯更换周期以商品规格手册为准。\n\n800 积分可兑换猫零食小样，普通配送地区另收 6 元运费；该兑换不直接套用普通购物订单的满 99 元包邮规则。兑换商品、可用库存及偏远地区配送规则以兑换页面标注为准。"
    },
    {
      "n": 2,
      "chunk_id": "1958",
      "section_path": "商品规格手册/自动饮水机 Pro 不锈钢(型号 MH-W60)",
      "question": "自动饮水机 Pro 不锈钢(型号 MH-W60)",
      "answer": "- 型号:MH-W60\n- 水箱容量:6L,304 不锈钢表面盘\n- 过滤:双滤芯并联,建议每 4 周更换一次滤芯\n- 核心功能:双泵冗余、无线水位提醒推送 App、缺水断电保护\n- 清洗:不锈钢面盘可高温消毒,建议每周清洗一次"
    }
  ],
  "decision": {
    "useful": true,
    "reason": "两型号水箱与滤芯周期均有证据",
    "response_kind": "knowledge",
    "source": null
  },
  "answer": "您好！根据商品规格手册：\n\n- **MH-W20**：水箱容量 2L，三重过滤棉，建议每 2 周更换一次滤芯 [1]\n- **MH-W60**：水箱容量 6L（304 不锈钢表面盘），双滤芯并联，建议每 4 周更换一次滤芯 [2]\n\n如有其他问题，欢迎随时咨询~",
  "point_verdicts": [
    {
      "point_id": "p1",
      "covered": true,
      "reason": "回答明确说明 MH-W20 水箱 2L、建议每 2 周更换滤芯，与要点一致，适用条件为该型号范围，回答亦限定于此型号"
    },
    {
      "point_id": "p2",
      "covered": true,
      "reason": "回答明确说明 MH-W60 水箱 6L、建议每 4 周更换滤芯，与要点一致，且限定于该型号"
    }
  ],
  "claim_verdicts": [
    {
      "claim": "MH-W20 水箱容量为 2L",
      "supported": true,
      "reason": "证据 [1] 型号 MH-W20 规格明确水箱容量 2L"
    },
    {
      "claim": "MH-W20 为三重过滤棉",
      "supported": true,
      "reason": "证据 [1] 明确过滤为三重过滤棉"
    },
    {
      "claim": "MH-W20 建议每 2 周更换一次滤芯",
      "supported": true,
      "reason": "证据 [1] 明确建议每 2 周更换一次滤芯"
    },
    {
      "claim": "MH-W60 水箱容量为 6L",
      "supported": true,
      "reason": "证据 [2] 型号 MH-W60 规格明确水箱容量 6L"
    },
    {
      "claim": "MH-W60 具有 304 不锈钢表面盘",
      "supported": true,
      "reason": "证据 [2] 明确水箱容量 6L、304 不锈钢表面盘"
    },
    {
      "claim": "MH-W60 为双滤芯并联过滤",
      "supported": true,
      "reason": "证据 [2] 明确过滤为双滤芯并联"
    },
    {
      "claim": "MH-W60 建议每 4 周更换一次滤芯",
      "supported": true,
      "reason": "证据 [2] 明确建议每 4 周更换一次滤芯"
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
  "elapsed_ms": 11015.310100046918,
  "judge_snapshot": {
    "prompt_version": "joint-generation-v2.1",
    "finish_reason": "stop"
  },
  "rewrite": {
    "policy_version": "original-query-on-invalid-v1",
    "status": "success",
    "error": null
  },
  "audit": {
    "audit_version": 1,
    "source_map_id": "af6590ab401319d942bddff0b30213a4cd888b8cf115ebd5cdec3adb87687e55",
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
    "candidate_ranking": [
      {
        "chunk_id": 1956,
        "score": 0.032786883413791656,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1958,
        "score": 0.032258063554763794,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1957,
        "score": 0.0317460335791111,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1977,
        "score": 0.03077651560306549,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1962,
        "score": 0.02878289483487606,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1934,
        "score": 0.028577260673046112,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1954,
        "score": 0.028219396248459816,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1955,
        "score": 0.028205128386616707,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1961,
        "score": 0.027984343469142914,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1963,
        "score": 0.027912385761737823,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1960,
        "score": 0.02777777798473835,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1959,
        "score": 0.027242401614785194,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1953,
        "score": 0.02715098112821579,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1964,
        "score": 0.026153847575187683,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1968,
        "score": 0.025941837579011917,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1938,
        "score": 0.02564935013651848,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1974,
        "score": 0.025451689958572388,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1946,
        "score": 0.024818576872348785,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1978,
        "score": 0.024410774931311607,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1952,
        "score": 0.023973586037755013,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1980,
        "score": 0.02354244515299797,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1967,
        "score": 0.02343107759952545,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1941,
        "score": 0.023392613977193832,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1935,
        "score": 0.02336956560611725,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1965,
        "score": 0.022875817492604256,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1973,
        "score": 0.022654958069324493,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1949,
        "score": 0.02235264703631401,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1972,
        "score": 0.022303922101855278,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1969,
        "score": 0.021369433030486107,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1943,
        "score": 0.021202990785241127,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1950,
        "score": 0.021193092688918114,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1971,
        "score": 0.021169355139136314,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1979,
        "score": 0.021169355139136314,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1939,
        "score": 0.020995670929551125,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1948,
        "score": 0.020539287477731705,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1976,
        "score": 0.019872110337018967,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1936,
        "score": 0.013698630034923553,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1931,
        "score": 0.013513513840734959,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1932,
        "score": 0.013333333656191826,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1970,
        "score": 0.012987012974917889,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1940,
        "score": 0.012658228166401386,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1937,
        "score": 0.012048192322254181,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1933,
        "score": 0.011904762126505375,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1945,
        "score": 0.011111111380159855,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1975,
        "score": 0.010869565419852734,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1951,
        "score": 0.010638297535479069,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1966,
        "score": 0.010101010091602802,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1944,
        "score": 0.009999999776482582,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1942,
        "score": 0.009615384973585606,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1947,
        "score": 0.009523809887468815,
        "score_kind": "rrf"
      }
    ],
    "final_ranking": [
      {
        "chunk_id": 1956,
        "score": 0.9935537576675415,
        "score_kind": "rerank"
      },
      {
        "chunk_id": 1958,
        "score": 0.9705125689506531,
        "score_kind": "rerank"
      },
      {
        "chunk_id": 1957,
        "score": 0.40429964661598206,
        "score_kind": "rerank"
      },
      {
        "chunk_id": 1977,
        "score": 0.2962595522403717,
        "score_kind": "rerank"
      },
      {
        "chunk_id": 1932,
        "score": 0.006420794874429703,
        "score_kind": "rerank"
      },
      {
        "chunk_id": 1961,
        "score": 0.0054406397975981236,
        "score_kind": "rerank"
      },
      {
        "chunk_id": 1970,
        "score": 0.004989458713680506,
        "score_kind": "rerank"
      },
      {
        "chunk_id": 1967,
        "score": 0.003732342505827546,
        "score_kind": "rerank"
      },
      {
        "chunk_id": 1937,
        "score": 0.003608312923461199,
        "score_kind": "rerank"
      },
      {
        "chunk_id": 1934,
        "score": 0.003192730713635683,
        "score_kind": "rerank"
      }
    ]
  }
}
````
