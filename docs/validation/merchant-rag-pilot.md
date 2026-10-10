# RAG 评估报告

运行：52678f9492114f1789466442e575c168

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
        "completed": 2,
        "errors": 8,
        "not_attempted": 0,
        "status_counts": {
          "completed": 2,
          "rewrite_error": 0,
          "retrieval_error": 0,
          "self_check_error": 0,
          "answer_error": 0,
          "judge_error": 8,
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
            "value": null,
            "valid_n": 0,
            "excluded": {
              "expected_refusal": 2,
              "judge_error": 8
            }
          },
          "faithfulness": {
            "value": null,
            "valid_n": 0,
            "excluded": {
              "judge_error": 8,
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
        "strategy": "bm25",
        "total": 10,
        "attempted": 10,
        "completed": 3,
        "errors": 7,
        "not_attempted": 0,
        "status_counts": {
          "completed": 3,
          "rewrite_error": 0,
          "retrieval_error": 0,
          "self_check_error": 0,
          "answer_error": 1,
          "judge_error": 6,
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
            "value": 1.0,
            "valid_n": 1,
            "excluded": {
              "answer_error": 1,
              "expected_refusal": 2,
              "judge_error": 6
            }
          },
          "faithfulness": {
            "value": 1.0,
            "valid_n": 1,
            "excluded": {
              "answer_error": 1,
              "judge_error": 6,
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
            "value": 0.14285714285714285,
            "valid_n": 7,
            "excluded": {
              "answer_error": 1,
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
        "completed": 2,
        "errors": 8,
        "not_attempted": 0,
        "status_counts": {
          "completed": 2,
          "rewrite_error": 0,
          "retrieval_error": 1,
          "self_check_error": 0,
          "answer_error": 1,
          "judge_error": 6,
          "cancelled": 0,
          "not_attempted": 0,
          "running": 0
        },
        "metrics": {
          "recall_at_5": {
            "value": 0.9523809523809524,
            "valid_n": 7,
            "excluded": {
              "expected_refusal": 2,
              "retrieval_error": 1
            }
          },
          "recall_at_10": {
            "value": 1.0,
            "valid_n": 7,
            "excluded": {
              "expected_refusal": 2,
              "retrieval_error": 1
            }
          },
          "mrr_at_10": {
            "value": 0.9285714285714286,
            "valid_n": 7,
            "excluded": {
              "expected_refusal": 2,
              "retrieval_error": 1
            }
          },
          "all_groups_hit_at_5": {
            "value": 0.8571428571428571,
            "valid_n": 7,
            "excluded": {
              "expected_refusal": 2,
              "retrieval_error": 1
            }
          },
          "all_groups_hit_at_10": {
            "value": 1.0,
            "valid_n": 7,
            "excluded": {
              "expected_refusal": 2,
              "retrieval_error": 1
            }
          },
          "candidate_group_coverage": {
            "value": 1.0,
            "valid_n": 7,
            "excluded": {
              "expected_refusal": 2,
              "retrieval_error": 1
            }
          },
          "prompt_group_coverage": {
            "value": 1.0,
            "valid_n": 7,
            "excluded": {
              "expected_refusal": 2,
              "retrieval_error": 1
            }
          },
          "answer_point_coverage": {
            "value": null,
            "valid_n": 0,
            "excluded": {
              "answer_error": 1,
              "expected_refusal": 2,
              "judge_error": 6,
              "retrieval_error": 1
            }
          },
          "faithfulness": {
            "value": null,
            "valid_n": 0,
            "excluded": {
              "answer_error": 1,
              "judge_error": 6,
              "retrieval_error": 1,
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
            "valid_n": 6,
            "excluded": {
              "answer_error": 1,
              "expected_refusal": 2,
              "retrieval_error": 1
            }
          }
        }
      },
      {
        "bucket": "overall",
        "strategy": "hybrid_rerank",
        "total": 10,
        "attempted": 10,
        "completed": 2,
        "errors": 8,
        "not_attempted": 0,
        "status_counts": {
          "completed": 2,
          "rewrite_error": 0,
          "retrieval_error": 1,
          "self_check_error": 0,
          "answer_error": 0,
          "judge_error": 7,
          "cancelled": 0,
          "not_attempted": 0,
          "running": 0
        },
        "metrics": {
          "recall_at_5": {
            "value": 1.0,
            "valid_n": 7,
            "excluded": {
              "expected_refusal": 2,
              "retrieval_error": 1
            }
          },
          "recall_at_10": {
            "value": 1.0,
            "valid_n": 7,
            "excluded": {
              "expected_refusal": 2,
              "retrieval_error": 1
            }
          },
          "mrr_at_10": {
            "value": 1.0,
            "valid_n": 7,
            "excluded": {
              "expected_refusal": 2,
              "retrieval_error": 1
            }
          },
          "all_groups_hit_at_5": {
            "value": 1.0,
            "valid_n": 7,
            "excluded": {
              "expected_refusal": 2,
              "retrieval_error": 1
            }
          },
          "all_groups_hit_at_10": {
            "value": 1.0,
            "valid_n": 7,
            "excluded": {
              "expected_refusal": 2,
              "retrieval_error": 1
            }
          },
          "candidate_group_coverage": {
            "value": 1.0,
            "valid_n": 7,
            "excluded": {
              "expected_refusal": 2,
              "retrieval_error": 1
            }
          },
          "prompt_group_coverage": {
            "value": 1.0,
            "valid_n": 7,
            "excluded": {
              "expected_refusal": 2,
              "retrieval_error": 1
            }
          },
          "answer_point_coverage": {
            "value": null,
            "valid_n": 0,
            "excluded": {
              "expected_refusal": 2,
              "judge_error": 7,
              "retrieval_error": 1
            }
          },
          "faithfulness": {
            "value": null,
            "valid_n": 0,
            "excluded": {
              "judge_error": 7,
              "retrieval_error": 1,
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
            "valid_n": 7,
            "excluded": {
              "expected_refusal": 2,
              "retrieval_error": 1
            }
          }
        }
      },
      {
        "bucket": "A_policy",
        "strategy": "dense",
        "total": 2,
        "attempted": 2,
        "completed": 0,
        "errors": 2,
        "not_attempted": 0,
        "status_counts": {
          "completed": 0,
          "rewrite_error": 0,
          "retrieval_error": 0,
          "self_check_error": 0,
          "answer_error": 0,
          "judge_error": 2,
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
            "value": null,
            "valid_n": 0,
            "excluded": {
              "judge_error": 2
            }
          },
          "faithfulness": {
            "value": null,
            "valid_n": 0,
            "excluded": {
              "judge_error": 2
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
        "completed": 0,
        "errors": 2,
        "not_attempted": 0,
        "status_counts": {
          "completed": 0,
          "rewrite_error": 0,
          "retrieval_error": 0,
          "self_check_error": 0,
          "answer_error": 0,
          "judge_error": 2,
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
            "value": null,
            "valid_n": 0,
            "excluded": {
              "judge_error": 2
            }
          },
          "faithfulness": {
            "value": null,
            "valid_n": 0,
            "excluded": {
              "judge_error": 2
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
        "completed": 0,
        "errors": 2,
        "not_attempted": 0,
        "status_counts": {
          "completed": 0,
          "rewrite_error": 0,
          "retrieval_error": 0,
          "self_check_error": 0,
          "answer_error": 0,
          "judge_error": 2,
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
            "value": null,
            "valid_n": 0,
            "excluded": {
              "judge_error": 2
            }
          },
          "faithfulness": {
            "value": null,
            "valid_n": 0,
            "excluded": {
              "judge_error": 2
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
        "completed": 0,
        "errors": 2,
        "not_attempted": 0,
        "status_counts": {
          "completed": 0,
          "rewrite_error": 0,
          "retrieval_error": 0,
          "self_check_error": 0,
          "answer_error": 0,
          "judge_error": 2,
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
            "value": null,
            "valid_n": 0,
            "excluded": {
              "judge_error": 2
            }
          },
          "faithfulness": {
            "value": null,
            "valid_n": 0,
            "excluded": {
              "judge_error": 2
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
        "completed": 0,
        "errors": 2,
        "not_attempted": 0,
        "status_counts": {
          "completed": 0,
          "rewrite_error": 0,
          "retrieval_error": 0,
          "self_check_error": 0,
          "answer_error": 0,
          "judge_error": 2,
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
            "value": null,
            "valid_n": 0,
            "excluded": {
              "judge_error": 2
            }
          },
          "faithfulness": {
            "value": null,
            "valid_n": 0,
            "excluded": {
              "judge_error": 2
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
        "completed": 1,
        "errors": 1,
        "not_attempted": 0,
        "status_counts": {
          "completed": 1,
          "rewrite_error": 0,
          "retrieval_error": 0,
          "self_check_error": 0,
          "answer_error": 1,
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
            "valid_n": 1,
            "excluded": {
              "answer_error": 1
            }
          },
          "faithfulness": {
            "value": 1.0,
            "valid_n": 1,
            "excluded": {
              "answer_error": 1
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
              "answer_error": 1
            }
          }
        }
      },
      {
        "bucket": "B_model",
        "strategy": "hybrid",
        "total": 2,
        "attempted": 2,
        "completed": 0,
        "errors": 2,
        "not_attempted": 0,
        "status_counts": {
          "completed": 0,
          "rewrite_error": 0,
          "retrieval_error": 0,
          "self_check_error": 0,
          "answer_error": 1,
          "judge_error": 1,
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
            "value": null,
            "valid_n": 0,
            "excluded": {
              "answer_error": 1,
              "judge_error": 1
            }
          },
          "faithfulness": {
            "value": null,
            "valid_n": 0,
            "excluded": {
              "answer_error": 1,
              "judge_error": 1
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
              "answer_error": 1
            }
          }
        }
      },
      {
        "bucket": "B_model",
        "strategy": "hybrid_rerank",
        "total": 2,
        "attempted": 2,
        "completed": 0,
        "errors": 2,
        "not_attempted": 0,
        "status_counts": {
          "completed": 0,
          "rewrite_error": 0,
          "retrieval_error": 0,
          "self_check_error": 0,
          "answer_error": 0,
          "judge_error": 2,
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
            "value": null,
            "valid_n": 0,
            "excluded": {
              "judge_error": 2
            }
          },
          "faithfulness": {
            "value": null,
            "valid_n": 0,
            "excluded": {
              "judge_error": 2
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
        "completed": 0,
        "errors": 2,
        "not_attempted": 0,
        "status_counts": {
          "completed": 0,
          "rewrite_error": 0,
          "retrieval_error": 0,
          "self_check_error": 0,
          "answer_error": 0,
          "judge_error": 2,
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
            "value": null,
            "valid_n": 0,
            "excluded": {
              "judge_error": 2
            }
          },
          "faithfulness": {
            "value": null,
            "valid_n": 0,
            "excluded": {
              "judge_error": 2
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
        "completed": 0,
        "errors": 2,
        "not_attempted": 0,
        "status_counts": {
          "completed": 0,
          "rewrite_error": 0,
          "retrieval_error": 0,
          "self_check_error": 0,
          "answer_error": 0,
          "judge_error": 2,
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
            "value": null,
            "valid_n": 0,
            "excluded": {
              "judge_error": 2
            }
          },
          "faithfulness": {
            "value": null,
            "valid_n": 0,
            "excluded": {
              "judge_error": 2
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
        "completed": 0,
        "errors": 2,
        "not_attempted": 0,
        "status_counts": {
          "completed": 0,
          "rewrite_error": 0,
          "retrieval_error": 0,
          "self_check_error": 0,
          "answer_error": 0,
          "judge_error": 2,
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
            "value": null,
            "valid_n": 0,
            "excluded": {
              "judge_error": 2
            }
          },
          "faithfulness": {
            "value": null,
            "valid_n": 0,
            "excluded": {
              "judge_error": 2
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
        "completed": 0,
        "errors": 2,
        "not_attempted": 0,
        "status_counts": {
          "completed": 0,
          "rewrite_error": 0,
          "retrieval_error": 0,
          "self_check_error": 0,
          "answer_error": 0,
          "judge_error": 2,
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
            "value": null,
            "valid_n": 0,
            "excluded": {
              "judge_error": 2
            }
          },
          "faithfulness": {
            "value": null,
            "valid_n": 0,
            "excluded": {
              "judge_error": 2
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
        "completed": 0,
        "errors": 2,
        "not_attempted": 0,
        "status_counts": {
          "completed": 0,
          "rewrite_error": 0,
          "retrieval_error": 0,
          "self_check_error": 0,
          "answer_error": 0,
          "judge_error": 2,
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
            "value": null,
            "valid_n": 0,
            "excluded": {
              "judge_error": 2
            }
          },
          "faithfulness": {
            "value": null,
            "valid_n": 0,
            "excluded": {
              "judge_error": 2
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
        "completed": 0,
        "errors": 2,
        "not_attempted": 0,
        "status_counts": {
          "completed": 0,
          "rewrite_error": 0,
          "retrieval_error": 0,
          "self_check_error": 0,
          "answer_error": 0,
          "judge_error": 2,
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
            "value": null,
            "valid_n": 0,
            "excluded": {
              "judge_error": 2
            }
          },
          "faithfulness": {
            "value": null,
            "valid_n": 0,
            "excluded": {
              "judge_error": 2
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
        "completed": 0,
        "errors": 2,
        "not_attempted": 0,
        "status_counts": {
          "completed": 0,
          "rewrite_error": 0,
          "retrieval_error": 1,
          "self_check_error": 0,
          "answer_error": 0,
          "judge_error": 1,
          "cancelled": 0,
          "not_attempted": 0,
          "running": 0
        },
        "metrics": {
          "recall_at_5": {
            "value": 0.6666666666666666,
            "valid_n": 1,
            "excluded": {
              "retrieval_error": 1
            }
          },
          "recall_at_10": {
            "value": 1.0,
            "valid_n": 1,
            "excluded": {
              "retrieval_error": 1
            }
          },
          "mrr_at_10": {
            "value": 1.0,
            "valid_n": 1,
            "excluded": {
              "retrieval_error": 1
            }
          },
          "all_groups_hit_at_5": {
            "value": 0.0,
            "valid_n": 1,
            "excluded": {
              "retrieval_error": 1
            }
          },
          "all_groups_hit_at_10": {
            "value": 1.0,
            "valid_n": 1,
            "excluded": {
              "retrieval_error": 1
            }
          },
          "candidate_group_coverage": {
            "value": 1.0,
            "valid_n": 1,
            "excluded": {
              "retrieval_error": 1
            }
          },
          "prompt_group_coverage": {
            "value": 1.0,
            "valid_n": 1,
            "excluded": {
              "retrieval_error": 1
            }
          },
          "answer_point_coverage": {
            "value": null,
            "valid_n": 0,
            "excluded": {
              "judge_error": 1,
              "retrieval_error": 1
            }
          },
          "faithfulness": {
            "value": null,
            "valid_n": 0,
            "excluded": {
              "judge_error": 1,
              "retrieval_error": 1
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
              "retrieval_error": 1
            }
          }
        }
      },
      {
        "bucket": "E_multi",
        "strategy": "hybrid_rerank",
        "total": 2,
        "attempted": 2,
        "completed": 0,
        "errors": 2,
        "not_attempted": 0,
        "status_counts": {
          "completed": 0,
          "rewrite_error": 0,
          "retrieval_error": 1,
          "self_check_error": 0,
          "answer_error": 0,
          "judge_error": 1,
          "cancelled": 0,
          "not_attempted": 0,
          "running": 0
        },
        "metrics": {
          "recall_at_5": {
            "value": 1.0,
            "valid_n": 1,
            "excluded": {
              "retrieval_error": 1
            }
          },
          "recall_at_10": {
            "value": 1.0,
            "valid_n": 1,
            "excluded": {
              "retrieval_error": 1
            }
          },
          "mrr_at_10": {
            "value": 1.0,
            "valid_n": 1,
            "excluded": {
              "retrieval_error": 1
            }
          },
          "all_groups_hit_at_5": {
            "value": 1.0,
            "valid_n": 1,
            "excluded": {
              "retrieval_error": 1
            }
          },
          "all_groups_hit_at_10": {
            "value": 1.0,
            "valid_n": 1,
            "excluded": {
              "retrieval_error": 1
            }
          },
          "candidate_group_coverage": {
            "value": 1.0,
            "valid_n": 1,
            "excluded": {
              "retrieval_error": 1
            }
          },
          "prompt_group_coverage": {
            "value": 1.0,
            "valid_n": 1,
            "excluded": {
              "retrieval_error": 1
            }
          },
          "answer_point_coverage": {
            "value": null,
            "valid_n": 0,
            "excluded": {
              "judge_error": 1,
              "retrieval_error": 1
            }
          },
          "faithfulness": {
            "value": null,
            "valid_n": 0,
            "excluded": {
              "judge_error": 1,
              "retrieval_error": 1
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
              "retrieval_error": 1
            }
          }
        }
      }
    ],
    "common_generation": {
      "eval_ids": [
        "D1",
        "D3"
      ],
      "valid_n": 2,
      "rows": [
        {
          "bucket": "overall",
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
          "bucket": "overall",
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
          "bucket": "overall",
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
          "bucket": "overall",
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
        "chunk_id": 1731,
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
        "chunk_id": 1732,
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
        "chunk_id": 1733,
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
        "chunk_id": 1734,
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
        "chunk_id": 1735,
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
        "chunk_id": 1736,
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
        "chunk_id": 1737,
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
        "chunk_id": 1738,
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
        "chunk_id": 1739,
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
        "chunk_id": 1740,
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
        "chunk_id": 1741,
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
        "chunk_id": 1742,
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
        "chunk_id": 1743,
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
        "chunk_id": 1744,
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
        "chunk_id": 1745,
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
        "chunk_id": 1746,
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
        "chunk_id": 1747,
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
        "chunk_id": 1748,
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
        "chunk_id": 1749,
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
        "chunk_id": 1750,
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
        "chunk_id": 1751,
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
        "chunk_id": 1752,
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
        "chunk_id": 1753,
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
        "chunk_id": 1754,
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
        "chunk_id": 1755,
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
        "chunk_id": 1756,
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
        "chunk_id": 1757,
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
        "chunk_id": 1758,
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
        "chunk_id": 1759,
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
        "chunk_id": 1760,
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
        "chunk_id": 1761,
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
        "chunk_id": 1762,
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
        "chunk_id": 1763,
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
        "chunk_id": 1764,
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
        "chunk_id": 1765,
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
        "chunk_id": 1766,
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
        "chunk_id": 1767,
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
        "chunk_id": 1768,
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
        "chunk_id": 1769,
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
        "chunk_id": 1770,
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
        "chunk_id": 1771,
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
        "chunk_id": 1772,
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
        "chunk_id": 1773,
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
        "chunk_id": 1774,
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
        "chunk_id": 1775,
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
        "chunk_id": 1776,
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
        "chunk_id": 1777,
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
        "chunk_id": 1778,
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
        "chunk_id": 1779,
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
        "chunk_id": 1780,
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
    "source_map_id": "378ae65f4ee735c6a8079070fbfcb5c21800c93f3318029e5f19836c32b5c2b4"
  },
  "run_id": "52678f9492114f1789466442e575c168",
  "dataset_id": "merchant-rag-300-v1",
  "fingerprint": "b2e8fd23ff18b012e363ee7ccb25d995b1435040ea60d5f4a6b732003350317b",
  "scope": "pilot",
  "run": {
    "schema_version": 2,
    "run_id": "52678f9492114f1789466442e575c168",
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
        "llm_token_limit_field": "max_tokens"
      },
      "fingerprint": "b2e8fd23ff18b012e363ee7ccb25d995b1435040ea60d5f4a6b732003350317b"
    },
    "state": "completed_with_errors",
    "outcome": "completed_with_errors",
    "stage": "complete",
    "planned_cases": 10,
    "planned_strategies": 4,
    "planned_records": 40,
    "counts": {
      "completed": 9,
      "rewrite_error": 0,
      "retrieval_error": 2,
      "self_check_error": 0,
      "answer_error": 2,
      "judge_error": 27,
      "cancelled": 0,
      "not_attempted": 0,
      "running": 0,
      "total": 40,
      "attempted": 40,
      "errors": 31
    },
    "request_counts": {
      "rewrite": 10,
      "self_check": 38,
      "answer": 29,
      "judge": 36,
      "embedding": 33,
      "rerank": 9,
      "milvus": 73
    },
    "cleanup": {
      "ok": true,
      "errors": [],
      "unverified": []
    },
    "created_at": "2026-10-10T09:55:18.758965+00:00",
    "updated_at": "2026-10-10T10:44:44.915452+00:00",
    "started_at": "2026-10-10T09:55:18.784424+00:00",
    "finished_at": "2026-10-10T10:44:44.941180+00:00",
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
  "status": "judge_error",
  "stage": "judgment",
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
          1774
        ]
      ]
    },
    {
      "group_id": "g2",
      "alternatives": [
        [
          1775
        ]
      ]
    }
  ],
  "candidate_ids": [
    1775,
    1745,
    1774,
    1777,
    1753,
    1754,
    1733,
    1755,
    1751,
    1737,
    1759,
    1776,
    1752,
    1761,
    1760,
    1742,
    1762,
    1744,
    1757,
    1750,
    1772,
    1763,
    1746,
    1764,
    1758,
    1747,
    1734,
    1778,
    1756,
    1732,
    1770,
    1740,
    1738,
    1743,
    1773,
    1779,
    1731,
    1765,
    1767,
    1771,
    1768,
    1736,
    1780,
    1735,
    1749,
    1741,
    1769,
    1766,
    1739,
    1748
  ],
  "final_ids": [
    1775,
    1745,
    1774,
    1777,
    1753,
    1754,
    1733,
    1755,
    1751,
    1737
  ],
  "prompt_citations": [
    {
      "n": 1,
      "chunk_id": "1775",
      "section_path": "会员权益/生日礼",
      "question": "生日礼",
      "answer": "银卡会员生日当月可领取一份猫零食小样，金卡会员生日当月可领取一份猫罐头礼盒。需在会员中心领取，礼品规格与领取期限以页面标注为准，不承诺额外折现或补偿。"
    },
    {
      "n": 3,
      "chunk_id": "1774",
      "section_path": "会员权益/会员等级",
      "question": "会员等级",
      "answer": "会员分为普通、银卡和金卡三档，按有效累计消费金额自动升级，不按年度消费金额计算。累计消费未满 1000 元为普通会员，满 1000 元起为银卡，满 5000 元起为金卡。\n\n有效累计消费指已完成订单的商品实际支付金额，不含配送费；退货退款部分从有效累计消费中扣除。退款后根据更新的累计消费重新计算等级，未达到原门槛时可能降级。等级与适用权益在会员中心展示。\n\n银卡在参与会员折扣的商品上享 95 折，金卡享 9 折。折扣适用商品和活动范围以结算页面标注为准。会员折扣、优惠券与满减是否叠加也以当次活动页面为准，不能一概承诺全部优惠同时生效。"
    },
    {
      "n": 5,
      "chunk_id": "1753",
      "section_path": "商品规格手册/智能猫砂盆 Pro(型号 MH-LP100)",
      "question": "智能猫砂盆 Pro(型号 MH-LP100)",
      "answer": "- 型号:MH-LP100\n- 适用猫咪体重:1.5kg 至 8kg\n- 猫砂容量:9L,废砂盒容量约 7 天(单猫)\n- 核心功能:自动感应清理、活性炭除臭、App 远程监控与健康记录\n- 供电:220V 市电,断电后配置自动保存\n- 清理提示:废砂盒满时 App 推送提醒,建议每 5 至 7 天倾倒一次"
    },
    {
      "n": 7,
      "chunk_id": "1733",
      "section_path": "售后手册/设备安装与激活",
      "question": "设备安装与激活",
      "answer": "智能设备首次使用需下载「喵喵优选」App,按说明书扫码添加设备并连接 2.4G Wi-Fi 完成激活;猫爬架等非联网商品按随附图解自行组装。"
    },
    {
      "n": 9,
      "chunk_id": "1751",
      "section_path": "商品与购物 FAQ/会员运费权益",
      "question": "会员运费权益",
      "answer": "金卡会员每月享 3 次免运费权益,银卡会员享 1 次;权益不与偏远地区附加运费冲抵,当月未用完不结转。"
    },
    {
      "n": 10,
      "chunk_id": "1737",
      "section_path": "售后手册/会员专属售后权益",
      "question": "会员专属售后权益",
      "answer": "金卡会员享优先客服接入与上门取件退换货;银卡会员享退换货运费权益 1 次/月。具体权益以会员中心页面标注为准。"
    },
    {
      "n": 8,
      "chunk_id": "1755",
      "section_path": "商品规格手册/智能猫砂盆 Max(型号 MH-LP200)",
      "question": "智能猫砂盆 Max(型号 MH-LP200)",
      "answer": "- 型号:MH-LP200\n- 适用猫咪体重:2kg 至 12kg,适合大型猫与多猫家庭\n- 猫砂容量:12L,废砂盒容量约 10 天(单猫)\n- 核心功能:超大滚筒、双重称重防夹、活性炭除臭、App 多猫健康档案\n- 供电:220V 市电\n- 清理提示:多猫家庭建议每 3 至 5 天倾倒一次废砂盒"
    },
    {
      "n": 6,
      "chunk_id": "1754",
      "section_path": "商品规格手册/智能猫砂盆 Lite(型号 MH-LP50)",
      "question": "智能猫砂盆 Lite(型号 MH-LP50)",
      "answer": "- 型号:MH-LP50\n- 适用猫咪体重:1.5kg 至 6kg\n- 猫砂容量:6L\n- 核心功能:自动感应清理、物理除臭盖板;不含 App 联网功能\n- 与 Pro 差异:Lite 无 App 远程监控与健康记录,价格更低,适合单猫家庭"
    },
    {
      "n": 4,
      "chunk_id": "1777",
      "section_path": "积分规则/积分怎么用",
      "question": "积分怎么用",
      "answer": "积分可在结算时抵扣商品金额，100 积分抵 1 元现金，单笔订单最多抵 30 元，不用于抵扣偏远地区附加运费，也不支持直接提现。\n\n2000 积分可兑换自动饮水机滤芯 3 片，该兑换套装适用于 MH-W40，普通配送地区包邮；偏远地区附加配送费仍需按页面规则确认。MH-W40 的滤芯更换周期以商品规格手册为准。\n\n800 积分可兑换猫零食小样，普通配送地区另收 6 元运费；该兑换不直接套用普通购物订单的满 99 元包邮规则。兑换商品、可用库存及偏远地区配送规则以兑换页面标注为准。"
    },
    {
      "n": 2,
      "chunk_id": "1745",
      "section_path": "商品与购物 FAQ/会员等级与积分规则",
      "question": "会员等级与积分规则",
      "answer": "会员分为普通、银卡、金卡三档,按累计消费自动升级。每消费 1 元得 1 积分,积分可在结算时抵扣,100 积分抵 1 元。"
    }
  ],
  "decision": {
    "useful": true,
    "reason": "金卡门槛与生日礼均有证据",
    "response_kind": "knowledge",
    "source": null
  },
  "answer": "您好！很高兴为您解答 😊\n\n**关于金卡等级门槛**\n需要说明的是，会员等级不是按年度消费计算的，而是按有效累计消费金额自动升级：累计消费满 5000 元起即为金卡。有效累计消费指已完成订单的商品实际支付金额（不含配送费），退货退款部分会从中扣除，退款后等级可能根据更新后的累计消费重新计算。[3]\n\n**关于金卡生日礼**\n金卡会员可在生日当月领取一份猫罐头礼盒，需在会员中心领取，礼品规格与领取期限以页面标注为准，不承诺额外折现或补偿。[1]\n\n如有其他问题，欢迎随时咨询！",
  "point_verdicts": null,
  "claim_verdicts": null,
  "metrics": {
    "recall_at_5": 1.0,
    "recall_at_10": 1.0,
    "mrr_at_10": 1.0,
    "all_groups_hit_at_5": 1.0,
    "all_groups_hit_at_10": 1.0,
    "candidate_group_coverage": 1.0,
    "prompt_group_coverage": 1.0,
    "answer_point_coverage": null,
    "faithfulness": null,
    "absent_refusal_rate": null,
    "answerable_false_refusal_rate": 0.0
  },
  "error": {
    "code": "judgment_error",
    "type": "JudgeError",
    "message": "该阶段执行失败"
  },
  "elapsed_ms": 62286.61280032247,
  "judge_snapshot": {
    "prompt_version": "joint-generation-v2.1",
    "finish_reason": "length"
  },
  "audit": {
    "audit_version": 1,
    "source_map_id": "378ae65f4ee735c6a8079070fbfcb5c21800c93f3318029e5f19836c32b5c2b4",
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
        "chunk_id": 1775,
        "score": 0.6753654479980469,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1745,
        "score": 0.5822025537490845,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1774,
        "score": 0.5758759379386902,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1777,
        "score": 0.5373437404632568,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1753,
        "score": 0.520089864730835,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1754,
        "score": 0.518223226070404,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1733,
        "score": 0.5055581331253052,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1755,
        "score": 0.5037830471992493,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1751,
        "score": 0.49695706367492676,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1737,
        "score": 0.4895363450050354,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1759,
        "score": 0.48910945653915405,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1776,
        "score": 0.4698141813278198,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1752,
        "score": 0.46100926399230957,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1761,
        "score": 0.4571150243282318,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1760,
        "score": 0.4553759694099426,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1742,
        "score": 0.42638900876045227,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1762,
        "score": 0.4187183678150177,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1744,
        "score": 0.41226792335510254,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1757,
        "score": 0.40228867530822754,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1750,
        "score": 0.40096351504325867,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1772,
        "score": 0.39800524711608887,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1763,
        "score": 0.39630430936813354,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1746,
        "score": 0.3892870843410492,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1764,
        "score": 0.3856220841407776,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1758,
        "score": 0.3845815062522888,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1747,
        "score": 0.3831542134284973,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1734,
        "score": 0.3783602714538574,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1778,
        "score": 0.3739945888519287,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1756,
        "score": 0.37099963426589966,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1732,
        "score": 0.3675485849380493,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1770,
        "score": 0.36575639247894287,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1740,
        "score": 0.3642715513706207,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1738,
        "score": 0.3617609143257141,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1743,
        "score": 0.36141517758369446,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1773,
        "score": 0.35749733448028564,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1779,
        "score": 0.35588961839675903,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1731,
        "score": 0.35342466831207275,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1765,
        "score": 0.35272732377052307,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1767,
        "score": 0.34551167488098145,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1771,
        "score": 0.3421114385128021,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1768,
        "score": 0.34120291471481323,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1736,
        "score": 0.3411083519458771,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1780,
        "score": 0.33901524543762207,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1735,
        "score": 0.33717459440231323,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1749,
        "score": 0.3304835259914398,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1741,
        "score": 0.32148316502571106,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1769,
        "score": 0.3003855347633362,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1766,
        "score": 0.2982466518878937,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1739,
        "score": 0.29349204897880554,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1748,
        "score": 0.2662397623062134,
        "score_kind": "cosine"
      }
    ],
    "final_ranking": [
      {
        "chunk_id": 1775,
        "score": 0.6753654479980469,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1745,
        "score": 0.5822025537490845,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1774,
        "score": 0.5758759379386902,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1777,
        "score": 0.5373437404632568,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1753,
        "score": 0.520089864730835,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1754,
        "score": 0.518223226070404,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1733,
        "score": 0.5055581331253052,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1755,
        "score": 0.5037830471992493,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1751,
        "score": 0.49695706367492676,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1737,
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
  "status": "judge_error",
  "stage": "judgment",
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
          1774
        ]
      ]
    },
    {
      "group_id": "g2",
      "alternatives": [
        [
          1775
        ]
      ]
    }
  ],
  "candidate_ids": [
    1775,
    1774,
    1745,
    1776,
    1752,
    1733,
    1738
  ],
  "final_ids": [
    1775,
    1774,
    1745,
    1776,
    1752,
    1733,
    1738
  ],
  "prompt_citations": [
    {
      "n": 1,
      "chunk_id": "1775",
      "section_path": "会员权益/生日礼",
      "question": "生日礼",
      "answer": "银卡会员生日当月可领取一份猫零食小样，金卡会员生日当月可领取一份猫罐头礼盒。需在会员中心领取，礼品规格与领取期限以页面标注为准，不承诺额外折现或补偿。"
    },
    {
      "n": 3,
      "chunk_id": "1745",
      "section_path": "商品与购物 FAQ/会员等级与积分规则",
      "question": "会员等级与积分规则",
      "answer": "会员分为普通、银卡、金卡三档,按累计消费自动升级。每消费 1 元得 1 积分,积分可在结算时抵扣,100 积分抵 1 元。"
    },
    {
      "n": 5,
      "chunk_id": "1752",
      "section_path": "商品规格手册",
      "question": "商品规格手册",
      "answer": "本手册收录喵喵优选自营智能硬件的型号、规格与使用要点,便于按具体型号查询。"
    },
    {
      "n": 7,
      "chunk_id": "1738",
      "section_path": "商品与购物 FAQ/退货政策是什么",
      "question": "退货政策是什么",
      "answer": "支持 7 天无理由退货,商品需保持完好、不影响二次销售,具体以平台售后规则为准。"
    },
    {
      "n": 6,
      "chunk_id": "1733",
      "section_path": "售后手册/设备安装与激活",
      "question": "设备安装与激活",
      "answer": "智能设备首次使用需下载「喵喵优选」App,按说明书扫码添加设备并连接 2.4G Wi-Fi 完成激活;猫爬架等非联网商品按随附图解自行组装。"
    },
    {
      "n": 4,
      "chunk_id": "1776",
      "section_path": "积分规则/积分怎么攒",
      "question": "积分怎么攒",
      "answer": "已完成订单每实际支付 1 元商品金额累计 1 积分，不计配送费；退款后按对应商品金额同步扣回积分。活动期间的双倍积分属于额外积分奖励，不计入会员等级升级；会员等级仍按有效累计消费金额计算。"
    },
    {
      "n": 2,
      "chunk_id": "1774",
      "section_path": "会员权益/会员等级",
      "question": "会员等级",
      "answer": "会员分为普通、银卡和金卡三档，按有效累计消费金额自动升级，不按年度消费金额计算。累计消费未满 1000 元为普通会员，满 1000 元起为银卡，满 5000 元起为金卡。\n\n有效累计消费指已完成订单的商品实际支付金额，不含配送费；退货退款部分从有效累计消费中扣除。退款后根据更新的累计消费重新计算等级，未达到原门槛时可能降级。等级与适用权益在会员中心展示。\n\n银卡在参与会员折扣的商品上享 95 折，金卡享 9 折。折扣适用商品和活动范围以结算页面标注为准。会员折扣、优惠券与满减是否叠加也以当次活动页面为准，不能一概承诺全部优惠同时生效。"
    }
  ],
  "decision": {
    "useful": true,
    "reason": "金卡门槛及生日礼均有直接证据",
    "response_kind": "knowledge",
    "source": null
  },
  "answer": "您好～很高兴为您解答：\n\n**关于金卡等级门槛**\n会员等级并非按“年消费”计算，而是按**有效累计消费金额**自动升级，累计消费满 **5000 元**起为金卡[2]。有效累计消费指已完成订单的商品实际支付金额，不含配送费；退货退款部分会从累计消费中扣除，未达门槛时可能降级[2]。\n\n**关于金卡生日礼**\n金卡会员生日当月可领取一份**猫罐头礼盒**，需在会员中心领取，礼品规格与领取期限以页面标注为准[1]。\n\n如有其他问题，欢迎随时咨询～",
  "point_verdicts": null,
  "claim_verdicts": null,
  "metrics": {
    "recall_at_5": 1.0,
    "recall_at_10": 1.0,
    "mrr_at_10": 1.0,
    "all_groups_hit_at_5": 1.0,
    "all_groups_hit_at_10": 1.0,
    "candidate_group_coverage": 1.0,
    "prompt_group_coverage": 1.0,
    "answer_point_coverage": null,
    "faithfulness": null,
    "absent_refusal_rate": null,
    "answerable_false_refusal_rate": 0.0
  },
  "error": {
    "code": "judgment_error",
    "type": "JudgeError",
    "message": "该阶段执行失败"
  },
  "elapsed_ms": 46550.92880013399,
  "judge_snapshot": {
    "prompt_version": "joint-generation-v2.1",
    "finish_reason": "length"
  },
  "audit": {
    "audit_version": 1,
    "source_map_id": "378ae65f4ee735c6a8079070fbfcb5c21800c93f3318029e5f19836c32b5c2b4",
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
        "chunk_id": 1775,
        "score": 9.339435577392578,
        "score_kind": "bm25"
      },
      {
        "chunk_id": 1774,
        "score": 7.171276092529297,
        "score_kind": "bm25"
      },
      {
        "chunk_id": 1745,
        "score": 6.90592098236084,
        "score_kind": "bm25"
      },
      {
        "chunk_id": 1776,
        "score": 6.212222576141357,
        "score_kind": "bm25"
      },
      {
        "chunk_id": 1752,
        "score": 4.681387424468994,
        "score_kind": "bm25"
      },
      {
        "chunk_id": 1733,
        "score": 4.314119338989258,
        "score_kind": "bm25"
      },
      {
        "chunk_id": 1738,
        "score": 4.2695698738098145,
        "score_kind": "bm25"
      }
    ],
    "final_ranking": [
      {
        "chunk_id": 1775,
        "score": 9.339435577392578,
        "score_kind": "bm25"
      },
      {
        "chunk_id": 1774,
        "score": 7.171276092529297,
        "score_kind": "bm25"
      },
      {
        "chunk_id": 1745,
        "score": 6.90592098236084,
        "score_kind": "bm25"
      },
      {
        "chunk_id": 1776,
        "score": 6.212222576141357,
        "score_kind": "bm25"
      },
      {
        "chunk_id": 1752,
        "score": 4.681387424468994,
        "score_kind": "bm25"
      },
      {
        "chunk_id": 1733,
        "score": 4.314119338989258,
        "score_kind": "bm25"
      },
      {
        "chunk_id": 1738,
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
  "status": "judge_error",
  "stage": "judgment",
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
          1774
        ]
      ]
    },
    {
      "group_id": "g2",
      "alternatives": [
        [
          1775
        ]
      ]
    }
  ],
  "candidate_ids": [
    1775,
    1745,
    1774,
    1733,
    1776,
    1752,
    1738,
    1777,
    1753,
    1754,
    1755,
    1751,
    1737,
    1759,
    1761,
    1760,
    1742,
    1762,
    1744,
    1757,
    1750,
    1772,
    1763,
    1746,
    1764,
    1758,
    1747,
    1734,
    1778,
    1756,
    1732,
    1770,
    1740,
    1743,
    1773,
    1779,
    1731,
    1765,
    1767,
    1771,
    1768,
    1736,
    1780,
    1735,
    1749,
    1741,
    1769,
    1766,
    1739,
    1748
  ],
  "final_ids": [
    1775,
    1745,
    1774,
    1733,
    1776,
    1752,
    1738,
    1777,
    1753,
    1754
  ],
  "prompt_citations": [
    {
      "n": 1,
      "chunk_id": "1775",
      "section_path": "会员权益/生日礼",
      "question": "生日礼",
      "answer": "银卡会员生日当月可领取一份猫零食小样，金卡会员生日当月可领取一份猫罐头礼盒。需在会员中心领取，礼品规格与领取期限以页面标注为准，不承诺额外折现或补偿。"
    },
    {
      "n": 3,
      "chunk_id": "1774",
      "section_path": "会员权益/会员等级",
      "question": "会员等级",
      "answer": "会员分为普通、银卡和金卡三档，按有效累计消费金额自动升级，不按年度消费金额计算。累计消费未满 1000 元为普通会员，满 1000 元起为银卡，满 5000 元起为金卡。\n\n有效累计消费指已完成订单的商品实际支付金额，不含配送费；退货退款部分从有效累计消费中扣除。退款后根据更新的累计消费重新计算等级，未达到原门槛时可能降级。等级与适用权益在会员中心展示。\n\n银卡在参与会员折扣的商品上享 95 折，金卡享 9 折。折扣适用商品和活动范围以结算页面标注为准。会员折扣、优惠券与满减是否叠加也以当次活动页面为准，不能一概承诺全部优惠同时生效。"
    },
    {
      "n": 5,
      "chunk_id": "1776",
      "section_path": "积分规则/积分怎么攒",
      "question": "积分怎么攒",
      "answer": "已完成订单每实际支付 1 元商品金额累计 1 积分，不计配送费；退款后按对应商品金额同步扣回积分。活动期间的双倍积分属于额外积分奖励，不计入会员等级升级；会员等级仍按有效累计消费金额计算。"
    },
    {
      "n": 7,
      "chunk_id": "1738",
      "section_path": "商品与购物 FAQ/退货政策是什么",
      "question": "退货政策是什么",
      "answer": "支持 7 天无理由退货,商品需保持完好、不影响二次销售,具体以平台售后规则为准。"
    },
    {
      "n": 9,
      "chunk_id": "1753",
      "section_path": "商品规格手册/智能猫砂盆 Pro(型号 MH-LP100)",
      "question": "智能猫砂盆 Pro(型号 MH-LP100)",
      "answer": "- 型号:MH-LP100\n- 适用猫咪体重:1.5kg 至 8kg\n- 猫砂容量:9L,废砂盒容量约 7 天(单猫)\n- 核心功能:自动感应清理、活性炭除臭、App 远程监控与健康记录\n- 供电:220V 市电,断电后配置自动保存\n- 清理提示:废砂盒满时 App 推送提醒,建议每 5 至 7 天倾倒一次"
    },
    {
      "n": 10,
      "chunk_id": "1754",
      "section_path": "商品规格手册/智能猫砂盆 Lite(型号 MH-LP50)",
      "question": "智能猫砂盆 Lite(型号 MH-LP50)",
      "answer": "- 型号:MH-LP50\n- 适用猫咪体重:1.5kg 至 6kg\n- 猫砂容量:6L\n- 核心功能:自动感应清理、物理除臭盖板;不含 App 联网功能\n- 与 Pro 差异:Lite 无 App 远程监控与健康记录,价格更低,适合单猫家庭"
    },
    {
      "n": 8,
      "chunk_id": "1777",
      "section_path": "积分规则/积分怎么用",
      "question": "积分怎么用",
      "answer": "积分可在结算时抵扣商品金额，100 积分抵 1 元现金，单笔订单最多抵 30 元，不用于抵扣偏远地区附加运费，也不支持直接提现。\n\n2000 积分可兑换自动饮水机滤芯 3 片，该兑换套装适用于 MH-W40，普通配送地区包邮；偏远地区附加配送费仍需按页面规则确认。MH-W40 的滤芯更换周期以商品规格手册为准。\n\n800 积分可兑换猫零食小样，普通配送地区另收 6 元运费；该兑换不直接套用普通购物订单的满 99 元包邮规则。兑换商品、可用库存及偏远地区配送规则以兑换页面标注为准。"
    },
    {
      "n": 6,
      "chunk_id": "1752",
      "section_path": "商品规格手册",
      "question": "商品规格手册",
      "answer": "本手册收录喵喵优选自营智能硬件的型号、规格与使用要点,便于按具体型号查询。"
    },
    {
      "n": 4,
      "chunk_id": "1733",
      "section_path": "售后手册/设备安装与激活",
      "question": "设备安装与激活",
      "answer": "智能设备首次使用需下载「喵喵优选」App,按说明书扫码添加设备并连接 2.4G Wi-Fi 完成激活;猫爬架等非联网商品按随附图解自行组装。"
    },
    {
      "n": 2,
      "chunk_id": "1745",
      "section_path": "商品与购物 FAQ/会员等级与积分规则",
      "question": "会员等级与积分规则",
      "answer": "会员分为普通、银卡、金卡三档,按累计消费自动升级。每消费 1 元得 1 积分,积分可在结算时抵扣,100 积分抵 1 元。"
    }
  ],
  "decision": {
    "useful": true,
    "reason": "金卡门槛与生日礼均有直接证据",
    "response_kind": "knowledge",
    "source": null
  },
  "answer": "您好！很高兴为您解答：\n\n**关于金卡等级门槛**\n需要说明的是，会员等级不是按年度消费计算，而是按有效累计消费金额自动升级的：\n- 普通会员：累计消费未满 1000 元\n- 银卡会员：满 1000 元起\n- **金卡会员：满 5000 元起** [3]\n\n其中“有效累计消费”指已完成订单的商品实际支付金额（不含配送费），退货退款部分会扣除，退款后可能重新计算等级甚至降级 [3]。\n\n**关于金卡生日礼**\n金卡会员生日当月可领取一份**猫罐头礼盒**，需在会员中心领取。礼品规格与领取期限以页面标注为准，不承诺额外折现或补偿 [1]。\n\n请问还有其他需要帮助的吗？😊",
  "point_verdicts": null,
  "claim_verdicts": null,
  "metrics": {
    "recall_at_5": 1.0,
    "recall_at_10": 1.0,
    "mrr_at_10": 1.0,
    "all_groups_hit_at_5": 1.0,
    "all_groups_hit_at_10": 1.0,
    "candidate_group_coverage": 1.0,
    "prompt_group_coverage": 1.0,
    "answer_point_coverage": null,
    "faithfulness": null,
    "absent_refusal_rate": null,
    "answerable_false_refusal_rate": 0.0
  },
  "error": {
    "code": "judgment_error",
    "type": "JudgeError",
    "message": "该阶段执行失败"
  },
  "elapsed_ms": 60556.34910007939,
  "judge_snapshot": {
    "prompt_version": "joint-generation-v2.1",
    "finish_reason": "length"
  },
  "audit": {
    "audit_version": 1,
    "source_map_id": "378ae65f4ee735c6a8079070fbfcb5c21800c93f3318029e5f19836c32b5c2b4",
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
        "chunk_id": 1775,
        "score": 0.032786883413791656,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1745,
        "score": 0.0320020467042923,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1774,
        "score": 0.0320020467042923,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1733,
        "score": 0.03007688745856285,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1776,
        "score": 0.0295138880610466,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1752,
        "score": 0.029083244502544403,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1738,
        "score": 0.025678060948848724,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1777,
        "score": 0.015625,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1753,
        "score": 0.015384615398943424,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1754,
        "score": 0.01515151560306549,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1755,
        "score": 0.014705882407724857,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1751,
        "score": 0.014492753893136978,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1737,
        "score": 0.014285714365541935,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1759,
        "score": 0.014084506779909134,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1761,
        "score": 0.013513513840734959,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1760,
        "score": 0.013333333656191826,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1742,
        "score": 0.01315789483487606,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1762,
        "score": 0.012987012974917889,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1744,
        "score": 0.012820512987673283,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1757,
        "score": 0.012658228166401386,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1750,
        "score": 0.012500000186264515,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1772,
        "score": 0.012345679104328156,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1763,
        "score": 0.012195121496915817,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1746,
        "score": 0.012048192322254181,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1764,
        "score": 0.011904762126505375,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1758,
        "score": 0.0117647061124444,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1747,
        "score": 0.011627906933426857,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1734,
        "score": 0.01149425283074379,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1778,
        "score": 0.011363636702299118,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1756,
        "score": 0.01123595517128706,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1732,
        "score": 0.011111111380159855,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1770,
        "score": 0.010989011265337467,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1740,
        "score": 0.010869565419852734,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1743,
        "score": 0.010638297535479069,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1773,
        "score": 0.010526316240429878,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1779,
        "score": 0.010416666977107525,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1731,
        "score": 0.010309278033673763,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1765,
        "score": 0.010204081423580647,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1767,
        "score": 0.010101010091602802,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1771,
        "score": 0.009999999776482582,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1768,
        "score": 0.009900989942252636,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1736,
        "score": 0.009803921915590763,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1780,
        "score": 0.009708737954497337,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1735,
        "score": 0.009615384973585606,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1749,
        "score": 0.009523809887468815,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1741,
        "score": 0.009433962404727936,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1769,
        "score": 0.009345794096589088,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1766,
        "score": 0.009259259328246117,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1739,
        "score": 0.00917431153357029,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1748,
        "score": 0.00909090880304575,
        "score_kind": "rrf"
      }
    ],
    "final_ranking": [
      {
        "chunk_id": 1775,
        "score": 0.032786883413791656,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1745,
        "score": 0.0320020467042923,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1774,
        "score": 0.0320020467042923,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1733,
        "score": 0.03007688745856285,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1776,
        "score": 0.0295138880610466,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1752,
        "score": 0.029083244502544403,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1738,
        "score": 0.025678060948848724,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1777,
        "score": 0.015625,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1753,
        "score": 0.015384615398943424,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1754,
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
  "status": "judge_error",
  "stage": "judgment",
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
          1774
        ]
      ]
    },
    {
      "group_id": "g2",
      "alternatives": [
        [
          1775
        ]
      ]
    }
  ],
  "candidate_ids": [
    1775,
    1745,
    1774,
    1733,
    1776,
    1752,
    1738,
    1777,
    1753,
    1754,
    1755,
    1751,
    1737,
    1759,
    1761,
    1760,
    1742,
    1762,
    1744,
    1757,
    1750,
    1772,
    1763,
    1746,
    1764,
    1758,
    1747,
    1734,
    1778,
    1756,
    1732,
    1770,
    1740,
    1743,
    1773,
    1779,
    1731,
    1765,
    1767,
    1771,
    1768,
    1736,
    1780,
    1735,
    1749,
    1741,
    1769,
    1766,
    1739,
    1748
  ],
  "final_ids": [
    1774,
    1775,
    1745,
    1776,
    1777,
    1737,
    1751,
    1733,
    1742,
    1752
  ],
  "prompt_citations": [
    {
      "n": 1,
      "chunk_id": "1774",
      "section_path": "会员权益/会员等级",
      "question": "会员等级",
      "answer": "会员分为普通、银卡和金卡三档，按有效累计消费金额自动升级，不按年度消费金额计算。累计消费未满 1000 元为普通会员，满 1000 元起为银卡，满 5000 元起为金卡。\n\n有效累计消费指已完成订单的商品实际支付金额，不含配送费；退货退款部分从有效累计消费中扣除。退款后根据更新的累计消费重新计算等级，未达到原门槛时可能降级。等级与适用权益在会员中心展示。\n\n银卡在参与会员折扣的商品上享 95 折，金卡享 9 折。折扣适用商品和活动范围以结算页面标注为准。会员折扣、优惠券与满减是否叠加也以当次活动页面为准，不能一概承诺全部优惠同时生效。"
    },
    {
      "n": 3,
      "chunk_id": "1745",
      "section_path": "商品与购物 FAQ/会员等级与积分规则",
      "question": "会员等级与积分规则",
      "answer": "会员分为普通、银卡、金卡三档,按累计消费自动升级。每消费 1 元得 1 积分,积分可在结算时抵扣,100 积分抵 1 元。"
    },
    {
      "n": 5,
      "chunk_id": "1777",
      "section_path": "积分规则/积分怎么用",
      "question": "积分怎么用",
      "answer": "积分可在结算时抵扣商品金额，100 积分抵 1 元现金，单笔订单最多抵 30 元，不用于抵扣偏远地区附加运费，也不支持直接提现。\n\n2000 积分可兑换自动饮水机滤芯 3 片，该兑换套装适用于 MH-W40，普通配送地区包邮；偏远地区附加配送费仍需按页面规则确认。MH-W40 的滤芯更换周期以商品规格手册为准。\n\n800 积分可兑换猫零食小样，普通配送地区另收 6 元运费；该兑换不直接套用普通购物订单的满 99 元包邮规则。兑换商品、可用库存及偏远地区配送规则以兑换页面标注为准。"
    },
    {
      "n": 7,
      "chunk_id": "1751",
      "section_path": "商品与购物 FAQ/会员运费权益",
      "question": "会员运费权益",
      "answer": "金卡会员每月享 3 次免运费权益,银卡会员享 1 次;权益不与偏远地区附加运费冲抵,当月未用完不结转。"
    },
    {
      "n": 9,
      "chunk_id": "1742",
      "section_path": "商品与购物 FAQ/运费怎么算",
      "question": "运费怎么算",
      "answer": "单笔订单满 99 元包邮,未满收取 10 元运费,偏远地区运费另计。邮费即运费,按此规则收取。"
    },
    {
      "n": 10,
      "chunk_id": "1752",
      "section_path": "商品规格手册",
      "question": "商品规格手册",
      "answer": "本手册收录喵喵优选自营智能硬件的型号、规格与使用要点,便于按具体型号查询。"
    },
    {
      "n": 8,
      "chunk_id": "1733",
      "section_path": "售后手册/设备安装与激活",
      "question": "设备安装与激活",
      "answer": "智能设备首次使用需下载「喵喵优选」App,按说明书扫码添加设备并连接 2.4G Wi-Fi 完成激活;猫爬架等非联网商品按随附图解自行组装。"
    },
    {
      "n": 6,
      "chunk_id": "1737",
      "section_path": "售后手册/会员专属售后权益",
      "question": "会员专属售后权益",
      "answer": "金卡会员享优先客服接入与上门取件退换货;银卡会员享退换货运费权益 1 次/月。具体权益以会员中心页面标注为准。"
    },
    {
      "n": 4,
      "chunk_id": "1776",
      "section_path": "积分规则/积分怎么攒",
      "question": "积分怎么攒",
      "answer": "已完成订单每实际支付 1 元商品金额累计 1 积分，不计配送费；退款后按对应商品金额同步扣回积分。活动期间的双倍积分属于额外积分奖励，不计入会员等级升级；会员等级仍按有效累计消费金额计算。"
    },
    {
      "n": 2,
      "chunk_id": "1775",
      "section_path": "会员权益/生日礼",
      "question": "生日礼",
      "answer": "银卡会员生日当月可领取一份猫零食小样，金卡会员生日当月可领取一份猫罐头礼盒。需在会员中心领取，礼品规格与领取期限以页面标注为准，不承诺额外折现或补偿。"
    }
  ],
  "decision": {
    "useful": true,
    "reason": "金卡门槛与生日礼均有证据",
    "response_kind": "knowledge",
    "source": null
  },
  "answer": "您好～为您说明如下：\n\n**关于等级门槛**\n会员等级并非按“年消费”计算，而是按**有效累计消费金额**自动升级：累计消费满 5000 元即为金卡[1]。有效累计消费指已完成订单的商品实际支付金额（不含配送费），退货退款部分会扣除[1]。\n\n**关于生日礼**\n金卡会员生日当月可领取一份**猫罐头礼盒**，需在会员中心领取，礼品规格与领取期限以页面标注为准[2]。\n\n另外，金卡还享 9 折会员折扣[1]、每月 3 次免运费权益[7]等，可供您参考～",
  "point_verdicts": null,
  "claim_verdicts": null,
  "metrics": {
    "recall_at_5": 1.0,
    "recall_at_10": 1.0,
    "mrr_at_10": 1.0,
    "all_groups_hit_at_5": 1.0,
    "all_groups_hit_at_10": 1.0,
    "candidate_group_coverage": 1.0,
    "prompt_group_coverage": 1.0,
    "answer_point_coverage": null,
    "faithfulness": null,
    "absent_refusal_rate": null,
    "answerable_false_refusal_rate": 0.0
  },
  "error": {
    "code": "judgment_error",
    "type": "JudgeError",
    "message": "该阶段执行失败"
  },
  "elapsed_ms": 66148.40939990245,
  "judge_snapshot": {
    "prompt_version": "joint-generation-v2.1",
    "finish_reason": "length"
  },
  "audit": {
    "audit_version": 1,
    "source_map_id": "378ae65f4ee735c6a8079070fbfcb5c21800c93f3318029e5f19836c32b5c2b4",
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
        "chunk_id": 1775,
        "score": 0.032786883413791656,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1745,
        "score": 0.0320020467042923,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1774,
        "score": 0.0320020467042923,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1733,
        "score": 0.03007688745856285,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1776,
        "score": 0.0295138880610466,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1752,
        "score": 0.029083244502544403,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1738,
        "score": 0.025678060948848724,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1777,
        "score": 0.015625,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1753,
        "score": 0.015384615398943424,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1754,
        "score": 0.01515151560306549,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1755,
        "score": 0.014705882407724857,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1751,
        "score": 0.014492753893136978,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1737,
        "score": 0.014285714365541935,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1759,
        "score": 0.014084506779909134,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1761,
        "score": 0.013513513840734959,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1760,
        "score": 0.013333333656191826,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1742,
        "score": 0.01315789483487606,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1762,
        "score": 0.012987012974917889,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1744,
        "score": 0.012820512987673283,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1757,
        "score": 0.012658228166401386,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1750,
        "score": 0.012500000186264515,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1772,
        "score": 0.012345679104328156,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1763,
        "score": 0.012195121496915817,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1746,
        "score": 0.012048192322254181,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1764,
        "score": 0.011904762126505375,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1758,
        "score": 0.0117647061124444,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1747,
        "score": 0.011627906933426857,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1734,
        "score": 0.01149425283074379,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1778,
        "score": 0.011363636702299118,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1756,
        "score": 0.01123595517128706,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1732,
        "score": 0.011111111380159855,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1770,
        "score": 0.010989011265337467,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1740,
        "score": 0.010869565419852734,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1743,
        "score": 0.010638297535479069,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1773,
        "score": 0.010526316240429878,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1779,
        "score": 0.010416666977107525,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1731,
        "score": 0.010309278033673763,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1765,
        "score": 0.010204081423580647,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1767,
        "score": 0.010101010091602802,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1771,
        "score": 0.009999999776482582,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1768,
        "score": 0.009900989942252636,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1736,
        "score": 0.009803921915590763,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1780,
        "score": 0.009708737954497337,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1735,
        "score": 0.009615384973585606,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1749,
        "score": 0.009523809887468815,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1741,
        "score": 0.009433962404727936,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1769,
        "score": 0.009345794096589088,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1766,
        "score": 0.009259259328246117,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1739,
        "score": 0.00917431153357029,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1748,
        "score": 0.00909090880304575,
        "score_kind": "rrf"
      }
    ],
    "final_ranking": [
      {
        "chunk_id": 1774,
        "score": 0.1314775049686432,
        "score_kind": "rerank"
      },
      {
        "chunk_id": 1775,
        "score": 0.1071121096611023,
        "score_kind": "rerank"
      },
      {
        "chunk_id": 1745,
        "score": 0.02354610711336136,
        "score_kind": "rerank"
      },
      {
        "chunk_id": 1776,
        "score": 0.0028411138337105513,
        "score_kind": "rerank"
      },
      {
        "chunk_id": 1777,
        "score": 0.0017970968037843704,
        "score_kind": "rerank"
      },
      {
        "chunk_id": 1737,
        "score": 0.00041021808283403516,
        "score_kind": "rerank"
      },
      {
        "chunk_id": 1751,
        "score": 0.0003726145951077342,
        "score_kind": "rerank"
      },
      {
        "chunk_id": 1733,
        "score": 0.00016082375077530742,
        "score_kind": "rerank"
      },
      {
        "chunk_id": 1742,
        "score": 5.759889609180391e-05,
        "score_kind": "rerank"
      },
      {
        "chunk_id": 1752,
        "score": 5.7160548749379814e-05,
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
  "status": "judge_error",
  "stage": "judgment",
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
          1769
        ]
      ]
    }
  ],
  "candidate_ids": [
    1769,
    1768,
    1771,
    1742,
    1740,
    1736,
    1737,
    1747,
    1767,
    1770,
    1751,
    1749,
    1765,
    1773,
    1766,
    1731,
    1738,
    1748,
    1777,
    1739,
    1732,
    1776,
    1741,
    1750,
    1772,
    1779,
    1744,
    1743,
    1734,
    1778,
    1746,
    1774,
    1745,
    1757,
    1775,
    1733,
    1735,
    1755,
    1753,
    1758,
    1756,
    1754,
    1780,
    1762,
    1752,
    1763,
    1760,
    1761,
    1764,
    1759
  ],
  "final_ids": [
    1769,
    1768,
    1771,
    1742,
    1740,
    1736,
    1737,
    1747,
    1767,
    1770
  ],
  "prompt_citations": [
    {
      "n": 1,
      "chunk_id": "1769",
      "section_path": "退货退款政策/退换货运费承担",
      "question": "退换货运费承担",
      "answer": "无理由退货的退回运费由买家承担;因商品质量问题、发错货、少发漏发导致的退换货,运费由平台承担。运费承担以平台售后规则最终判定为准。"
    },
    {
      "n": 3,
      "chunk_id": "1771",
      "section_path": "退货退款政策/运输破损处理",
      "question": "运输破损处理",
      "answer": "商品运输途中破损的,请在签收后 48 小时内联系客服并提供开箱视频与照片,核实后可免费补发或退款,相关运费由平台承担。"
    },
    {
      "n": 5,
      "chunk_id": "1740",
      "section_path": "商品与购物 FAQ/换货流程怎么走",
      "question": "换货流程怎么走",
      "answer": "收到商品 7 天内可申请换货,联系客服登记后将商品寄回,平台核验无误后补发新品。"
    },
    {
      "n": 7,
      "chunk_id": "1737",
      "section_path": "售后手册/会员专属售后权益",
      "question": "会员专属售后权益",
      "answer": "金卡会员享优先客服接入与上门取件退换货;银卡会员享退换货运费权益 1 次/月。具体权益以会员中心页面标注为准。"
    },
    {
      "n": 9,
      "chunk_id": "1767",
      "section_path": "退货退款政策/换货政策/换货条件",
      "question": "换货条件",
      "answer": "收到商品 7 天内,商品完好且配件齐全的,可申请一次同款换货;不同型号或颜色需先退货再重新下单。"
    },
    {
      "n": 10,
      "chunk_id": "1770",
      "section_path": "退货退款政策/质量问题与保修",
      "question": "质量问题与保修",
      "answer": "电子类商品自签收起保修 12 个月,保修期内非人为损坏可申请免费维修或换货;人为损坏、超保商品维修可能收取工本费。"
    },
    {
      "n": 8,
      "chunk_id": "1747",
      "section_path": "商品与购物 FAQ/配送范围与偏远地区",
      "question": "配送范围与偏远地区",
      "answer": "全国大部分地区支持配送,新疆、西藏、内蒙古等偏远地区运费另计且时效顺延;港澳台及海外暂不支持自营配送。"
    },
    {
      "n": 6,
      "chunk_id": "1736",
      "section_path": "售后手册/维修寄修流程",
      "question": "维修寄修流程",
      "answer": "保修期内设备故障,联系客服登记后按指引将设备寄回指定维修点,核验后免费维修并寄回;超保或人为损坏维修可能收取工本费,费用会提前告知。"
    },
    {
      "n": 4,
      "chunk_id": "1742",
      "section_path": "商品与购物 FAQ/运费怎么算",
      "question": "运费怎么算",
      "answer": "单笔订单满 99 元包邮,未满收取 10 元运费,偏远地区运费另计。邮费即运费,按此规则收取。"
    },
    {
      "n": 2,
      "chunk_id": "1768",
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
  "answer": "您好！因少发、漏发导致的退换货，运费由平台承担[1]。\n\n温馨提示：具体运费承担以平台售后规则最终判定为准[1]。如您遇到少发漏发情况，可提供订单号，我们为您进一步核实处理。",
  "point_verdicts": null,
  "claim_verdicts": null,
  "metrics": {
    "recall_at_5": 1.0,
    "recall_at_10": 1.0,
    "mrr_at_10": 1.0,
    "all_groups_hit_at_5": 1.0,
    "all_groups_hit_at_10": 1.0,
    "candidate_group_coverage": 1.0,
    "prompt_group_coverage": 1.0,
    "answer_point_coverage": null,
    "faithfulness": null,
    "absent_refusal_rate": null,
    "answerable_false_refusal_rate": 0.0
  },
  "error": {
    "code": "judgment_error",
    "type": "JudgeError",
    "message": "该阶段执行失败"
  },
  "elapsed_ms": 69247.50380008481,
  "judge_snapshot": {
    "prompt_version": "joint-generation-v2.1",
    "finish_reason": "length"
  },
  "audit": {
    "audit_version": 1,
    "source_map_id": "378ae65f4ee735c6a8079070fbfcb5c21800c93f3318029e5f19836c32b5c2b4",
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
        "chunk_id": 1769,
        "score": 0.7040420770645142,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1768,
        "score": 0.6639959812164307,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1771,
        "score": 0.6257678270339966,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1742,
        "score": 0.575890839099884,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1740,
        "score": 0.5652117133140564,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1736,
        "score": 0.5471986532211304,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1737,
        "score": 0.5470176339149475,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1747,
        "score": 0.5431363582611084,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1767,
        "score": 0.5418092012405396,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1770,
        "score": 0.5398897528648376,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1751,
        "score": 0.5345059633255005,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1749,
        "score": 0.5340436697006226,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1765,
        "score": 0.5289136171340942,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1773,
        "score": 0.5243566632270813,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1766,
        "score": 0.5234106183052063,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1731,
        "score": 0.520516574382782,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1738,
        "score": 0.517553448677063,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1748,
        "score": 0.5175460577011108,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1777,
        "score": 0.5113711357116699,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1739,
        "score": 0.5046658515930176,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1732,
        "score": 0.5018535852432251,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1776,
        "score": 0.4978722631931305,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1741,
        "score": 0.4967568516731262,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1750,
        "score": 0.492765873670578,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1772,
        "score": 0.47643572092056274,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1779,
        "score": 0.46931469440460205,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1744,
        "score": 0.46612662076950073,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1743,
        "score": 0.46289175748825073,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1734,
        "score": 0.45831504464149475,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1778,
        "score": 0.44811394810676575,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1746,
        "score": 0.44225388765335083,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1774,
        "score": 0.42204421758651733,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1745,
        "score": 0.42026203870773315,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1757,
        "score": 0.40917807817459106,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1775,
        "score": 0.40313059091567993,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1733,
        "score": 0.39646226167678833,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1735,
        "score": 0.39401930570602417,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1755,
        "score": 0.392287015914917,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1753,
        "score": 0.38476184010505676,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1758,
        "score": 0.3827020525932312,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1756,
        "score": 0.378430038690567,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1754,
        "score": 0.37185344099998474,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1780,
        "score": 0.3646571636199951,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1762,
        "score": 0.35734739899635315,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1752,
        "score": 0.34617745876312256,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1763,
        "score": 0.3363617956638336,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1760,
        "score": 0.31159868836402893,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1761,
        "score": 0.3062039911746979,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1764,
        "score": 0.2835042178630829,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1759,
        "score": 0.2677757143974304,
        "score_kind": "cosine"
      }
    ],
    "final_ranking": [
      {
        "chunk_id": 1769,
        "score": 0.7040420770645142,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1768,
        "score": 0.6639959812164307,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1771,
        "score": 0.6257678270339966,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1742,
        "score": 0.575890839099884,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1740,
        "score": 0.5652117133140564,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1736,
        "score": 0.5471986532211304,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1737,
        "score": 0.5470176339149475,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1747,
        "score": 0.5431363582611084,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1767,
        "score": 0.5418092012405396,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1770,
        "score": 0.5398897528648376,
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
  "status": "judge_error",
  "stage": "judgment",
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
          1769
        ]
      ]
    }
  ],
  "candidate_ids": [
    1769,
    1768,
    1737,
    1771,
    1731,
    1767,
    1742,
    1740,
    1780,
    1751,
    1777,
    1770,
    1747,
    1772,
    1773,
    1739,
    1741,
    1752,
    1743,
    1774,
    1749,
    1765,
    1750,
    1735,
    1746,
    1748,
    1776,
    1779
  ],
  "final_ids": [
    1769,
    1768,
    1737,
    1771,
    1731,
    1767,
    1742,
    1740,
    1780,
    1751
  ],
  "prompt_citations": [
    {
      "n": 1,
      "chunk_id": "1769",
      "section_path": "退货退款政策/退换货运费承担",
      "question": "退换货运费承担",
      "answer": "无理由退货的退回运费由买家承担;因商品质量问题、发错货、少发漏发导致的退换货,运费由平台承担。运费承担以平台售后规则最终判定为准。"
    },
    {
      "n": 3,
      "chunk_id": "1737",
      "section_path": "售后手册/会员专属售后权益",
      "question": "会员专属售后权益",
      "answer": "金卡会员享优先客服接入与上门取件退换货;银卡会员享退换货运费权益 1 次/月。具体权益以会员中心页面标注为准。"
    },
    {
      "n": 5,
      "chunk_id": "1731",
      "section_path": "售后手册/常见问题处理时限",
      "question": "常见问题处理时限",
      "answer": "| 问题类型 | 首次响应 | 处理时限 |\n| --- | --- | --- |\n| 退款 | 2 小时 | 3 个工作日 |\n| 换货 | 2 小时 | 5 个工作日 |\n| 维修 | 4 小时 | 7 个工作日 |\n| 投诉 | 1 小时 | 3 个工作日 |\n| 发票 | 4 小时 | 3 个工作日 |\n| 物流异常 | 2 小时 | 5 个工作日 |\n| 商品咨询 | 1 小时 | 当日 |\n| 价格保护 | 2 小时 | 3 个工作日 |\n| 账户问题 | 2 小时 | 3 个工作日 |\n| 退换货运费 | 2 小时 | 3 个工作日 |\n| 缺货补发 | 2 小时 | 5 个工作日 |\n| 其他 | 4 小时 | 7 个工作日 |"
    },
    {
      "n": 7,
      "chunk_id": "1742",
      "section_path": "商品与购物 FAQ/运费怎么算",
      "question": "运费怎么算",
      "answer": "单笔订单满 99 元包邮,未满收取 10 元运费,偏远地区运费另计。邮费即运费,按此规则收取。"
    },
    {
      "n": 9,
      "chunk_id": "1780",
      "section_path": "猫窝清洗说明/猫窝是否可以机洗",
      "question": "猫窝是否可以机洗",
      "answer": "普通布艺猫窝清洗前拆掉内部垫芯，外套放入洗衣袋，使用轻柔模式冷水洗，自然晾干。不可直接将整只猫窝连垫芯一起机洗，商品另有清洗标签时优先遵循标签。\n\n带加热模块的猫窝不可机洗，应先断电，并按说明书局部擦洗；不得将加热模块、电源或线路浸水。未按清洗说明操作导致的损坏不直接认定为商品质量问题，需要客服核验。\n\n退货仍需符合商品完好、不影响二次销售等适用条件。售后手册中的电子类商品 12 个月保修不能直接套用到普通布艺猫窝；本清洗说明未给出布艺猫窝的独立保修期限。"
    },
    {
      "n": 10,
      "chunk_id": "1751",
      "section_path": "商品与购物 FAQ/会员运费权益",
      "question": "会员运费权益",
      "answer": "金卡会员每月享 3 次免运费权益,银卡会员享 1 次;权益不与偏远地区附加运费冲抵,当月未用完不结转。"
    },
    {
      "n": 8,
      "chunk_id": "1740",
      "section_path": "商品与购物 FAQ/换货流程怎么走",
      "question": "换货流程怎么走",
      "answer": "收到商品 7 天内可申请换货,联系客服登记后将商品寄回,平台核验无误后补发新品。"
    },
    {
      "n": 6,
      "chunk_id": "1767",
      "section_path": "退货退款政策/换货政策/换货条件",
      "question": "换货条件",
      "answer": "收到商品 7 天内,商品完好且配件齐全的,可申请一次同款换货;不同型号或颜色需先退货再重新下单。"
    },
    {
      "n": 4,
      "chunk_id": "1771",
      "section_path": "退货退款政策/运输破损处理",
      "question": "运输破损处理",
      "answer": "商品运输途中破损的,请在签收后 48 小时内联系客服并提供开箱视频与照片,核实后可免费补发或退款,相关运费由平台承担。"
    },
    {
      "n": 2,
      "chunk_id": "1768",
      "section_path": "退货退款政策/换货政策/换货运费",
      "question": "换货运费",
      "answer": "非质量问题的换货,往返运费由买家承担;因质量问题或发错货的换货,往返运费由平台承担。"
    }
  ],
  "decision": {
    "useful": true,
    "reason": "证据1769直接说明少发漏发导致的退换货运费由平台承担",
    "response_kind": "knowledge",
    "source": null
  },
  "answer": "您好！根据商家政策，因商品质量问题、发错货、少发漏发导致的退换货，运费由平台承担；最终以平台售后规则的判定为准 [1]。如需办理相关退换货，欢迎随时联系我们。",
  "point_verdicts": null,
  "claim_verdicts": null,
  "metrics": {
    "recall_at_5": 1.0,
    "recall_at_10": 1.0,
    "mrr_at_10": 1.0,
    "all_groups_hit_at_5": 1.0,
    "all_groups_hit_at_10": 1.0,
    "candidate_group_coverage": 1.0,
    "prompt_group_coverage": 1.0,
    "answer_point_coverage": null,
    "faithfulness": null,
    "absent_refusal_rate": null,
    "answerable_false_refusal_rate": 0.0
  },
  "error": {
    "code": "judgment_error",
    "type": "JudgeError",
    "message": "该阶段执行失败"
  },
  "elapsed_ms": 73812.34659976326,
  "judge_snapshot": {
    "prompt_version": "joint-generation-v2.1",
    "finish_reason": "length"
  },
  "audit": {
    "audit_version": 1,
    "source_map_id": "378ae65f4ee735c6a8079070fbfcb5c21800c93f3318029e5f19836c32b5c2b4",
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
        "chunk_id": 1769,
        "score": 33.115447998046875,
        "score_kind": "bm25"
      },
      {
        "chunk_id": 1768,
        "score": 15.512645721435547,
        "score_kind": "bm25"
      },
      {
        "chunk_id": 1737,
        "score": 12.489039421081543,
        "score_kind": "bm25"
      },
      {
        "chunk_id": 1771,
        "score": 8.663971900939941,
        "score_kind": "bm25"
      },
      {
        "chunk_id": 1731,
        "score": 7.032027721405029,
        "score_kind": "bm25"
      },
      {
        "chunk_id": 1767,
        "score": 4.239816188812256,
        "score_kind": "bm25"
      },
      {
        "chunk_id": 1742,
        "score": 3.048265218734741,
        "score_kind": "bm25"
      },
      {
        "chunk_id": 1740,
        "score": 2.9758758544921875,
        "score_kind": "bm25"
      },
      {
        "chunk_id": 1780,
        "score": 2.8859429359436035,
        "score_kind": "bm25"
      },
      {
        "chunk_id": 1751,
        "score": 2.8167614936828613,
        "score_kind": "bm25"
      },
      {
        "chunk_id": 1777,
        "score": 2.4655652046203613,
        "score_kind": "bm25"
      },
      {
        "chunk_id": 1770,
        "score": 2.101652145385742,
        "score_kind": "bm25"
      },
      {
        "chunk_id": 1747,
        "score": 1.8113679885864258,
        "score_kind": "bm25"
      },
      {
        "chunk_id": 1772,
        "score": 1.4414697885513306,
        "score_kind": "bm25"
      },
      {
        "chunk_id": 1773,
        "score": 1.2937390804290771,
        "score_kind": "bm25"
      },
      {
        "chunk_id": 1739,
        "score": 1.0660427808761597,
        "score_kind": "bm25"
      },
      {
        "chunk_id": 1741,
        "score": 1.0558345317840576,
        "score_kind": "bm25"
      },
      {
        "chunk_id": 1752,
        "score": 1.0359933376312256,
        "score_kind": "bm25"
      },
      {
        "chunk_id": 1743,
        "score": 1.0168840885162354,
        "score_kind": "bm25"
      },
      {
        "chunk_id": 1774,
        "score": 1.0009245872497559,
        "score_kind": "bm25"
      },
      {
        "chunk_id": 1749,
        "score": 0.998467206954956,
        "score_kind": "bm25"
      },
      {
        "chunk_id": 1765,
        "score": 0.9895066618919373,
        "score_kind": "bm25"
      },
      {
        "chunk_id": 1750,
        "score": 0.9807054996490479,
        "score_kind": "bm25"
      },
      {
        "chunk_id": 1735,
        "score": 0.9720594882965088,
        "score_kind": "bm25"
      },
      {
        "chunk_id": 1746,
        "score": 0.9155580401420593,
        "score_kind": "bm25"
      },
      {
        "chunk_id": 1748,
        "score": 0.9155580401420593,
        "score_kind": "bm25"
      },
      {
        "chunk_id": 1776,
        "score": 0.8389298319816589,
        "score_kind": "bm25"
      },
      {
        "chunk_id": 1779,
        "score": 0.7139831781387329,
        "score_kind": "bm25"
      }
    ],
    "final_ranking": [
      {
        "chunk_id": 1769,
        "score": 33.115447998046875,
        "score_kind": "bm25"
      },
      {
        "chunk_id": 1768,
        "score": 15.512645721435547,
        "score_kind": "bm25"
      },
      {
        "chunk_id": 1737,
        "score": 12.489039421081543,
        "score_kind": "bm25"
      },
      {
        "chunk_id": 1771,
        "score": 8.663971900939941,
        "score_kind": "bm25"
      },
      {
        "chunk_id": 1731,
        "score": 7.032027721405029,
        "score_kind": "bm25"
      },
      {
        "chunk_id": 1767,
        "score": 4.239816188812256,
        "score_kind": "bm25"
      },
      {
        "chunk_id": 1742,
        "score": 3.048265218734741,
        "score_kind": "bm25"
      },
      {
        "chunk_id": 1740,
        "score": 2.9758758544921875,
        "score_kind": "bm25"
      },
      {
        "chunk_id": 1780,
        "score": 2.8859429359436035,
        "score_kind": "bm25"
      },
      {
        "chunk_id": 1751,
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
  "status": "judge_error",
  "stage": "judgment",
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
          1769
        ]
      ]
    }
  ],
  "candidate_ids": [
    1769,
    1768,
    1771,
    1737,
    1742,
    1740,
    1767,
    1731,
    1747,
    1751,
    1770,
    1773,
    1777,
    1749,
    1765,
    1739,
    1772,
    1741,
    1748,
    1780,
    1743,
    1750,
    1776,
    1774,
    1779,
    1746,
    1752,
    1735,
    1736,
    1766,
    1738,
    1732,
    1744,
    1734,
    1778,
    1745,
    1757,
    1775,
    1733,
    1755,
    1753,
    1758,
    1756,
    1754,
    1762,
    1763,
    1760,
    1761,
    1764,
    1759
  ],
  "final_ids": [
    1769,
    1768,
    1771,
    1737,
    1742,
    1740,
    1767,
    1731,
    1747,
    1751
  ],
  "prompt_citations": [
    {
      "n": 1,
      "chunk_id": "1769",
      "section_path": "退货退款政策/退换货运费承担",
      "question": "退换货运费承担",
      "answer": "无理由退货的退回运费由买家承担;因商品质量问题、发错货、少发漏发导致的退换货,运费由平台承担。运费承担以平台售后规则最终判定为准。"
    },
    {
      "n": 3,
      "chunk_id": "1771",
      "section_path": "退货退款政策/运输破损处理",
      "question": "运输破损处理",
      "answer": "商品运输途中破损的,请在签收后 48 小时内联系客服并提供开箱视频与照片,核实后可免费补发或退款,相关运费由平台承担。"
    },
    {
      "n": 5,
      "chunk_id": "1742",
      "section_path": "商品与购物 FAQ/运费怎么算",
      "question": "运费怎么算",
      "answer": "单笔订单满 99 元包邮,未满收取 10 元运费,偏远地区运费另计。邮费即运费,按此规则收取。"
    },
    {
      "n": 7,
      "chunk_id": "1767",
      "section_path": "退货退款政策/换货政策/换货条件",
      "question": "换货条件",
      "answer": "收到商品 7 天内,商品完好且配件齐全的,可申请一次同款换货;不同型号或颜色需先退货再重新下单。"
    },
    {
      "n": 9,
      "chunk_id": "1747",
      "section_path": "商品与购物 FAQ/配送范围与偏远地区",
      "question": "配送范围与偏远地区",
      "answer": "全国大部分地区支持配送,新疆、西藏、内蒙古等偏远地区运费另计且时效顺延;港澳台及海外暂不支持自营配送。"
    },
    {
      "n": 10,
      "chunk_id": "1751",
      "section_path": "商品与购物 FAQ/会员运费权益",
      "question": "会员运费权益",
      "answer": "金卡会员每月享 3 次免运费权益,银卡会员享 1 次;权益不与偏远地区附加运费冲抵,当月未用完不结转。"
    },
    {
      "n": 8,
      "chunk_id": "1731",
      "section_path": "售后手册/常见问题处理时限",
      "question": "常见问题处理时限",
      "answer": "| 问题类型 | 首次响应 | 处理时限 |\n| --- | --- | --- |\n| 退款 | 2 小时 | 3 个工作日 |\n| 换货 | 2 小时 | 5 个工作日 |\n| 维修 | 4 小时 | 7 个工作日 |\n| 投诉 | 1 小时 | 3 个工作日 |\n| 发票 | 4 小时 | 3 个工作日 |\n| 物流异常 | 2 小时 | 5 个工作日 |\n| 商品咨询 | 1 小时 | 当日 |\n| 价格保护 | 2 小时 | 3 个工作日 |\n| 账户问题 | 2 小时 | 3 个工作日 |\n| 退换货运费 | 2 小时 | 3 个工作日 |\n| 缺货补发 | 2 小时 | 5 个工作日 |\n| 其他 | 4 小时 | 7 个工作日 |"
    },
    {
      "n": 6,
      "chunk_id": "1740",
      "section_path": "商品与购物 FAQ/换货流程怎么走",
      "question": "换货流程怎么走",
      "answer": "收到商品 7 天内可申请换货,联系客服登记后将商品寄回,平台核验无误后补发新品。"
    },
    {
      "n": 4,
      "chunk_id": "1737",
      "section_path": "售后手册/会员专属售后权益",
      "question": "会员专属售后权益",
      "answer": "金卡会员享优先客服接入与上门取件退换货;银卡会员享退换货运费权益 1 次/月。具体权益以会员中心页面标注为准。"
    },
    {
      "n": 2,
      "chunk_id": "1768",
      "section_path": "退货退款政策/换货政策/换货运费",
      "question": "换货运费",
      "answer": "非质量问题的换货,往返运费由买家承担;因质量问题或发错货的换货,往返运费由平台承担。"
    }
  ],
  "decision": {
    "useful": true,
    "reason": "证据明确少发漏发退换货运费由平台承担",
    "response_kind": "knowledge",
    "source": null
  },
  "answer": "您好！根据平台售后规则：因商品质量问题、发错货、少发漏发导致的退换货，运费由平台承担[1]；如属换货，往返运费同样由平台承担[2]。最终以平台售后规则判定为准[1]。\n\n如您遇到少发漏发情况，欢迎提供订单号，我可以进一步协助您处理~",
  "point_verdicts": null,
  "claim_verdicts": null,
  "metrics": {
    "recall_at_5": 1.0,
    "recall_at_10": 1.0,
    "mrr_at_10": 1.0,
    "all_groups_hit_at_5": 1.0,
    "all_groups_hit_at_10": 1.0,
    "candidate_group_coverage": 1.0,
    "prompt_group_coverage": 1.0,
    "answer_point_coverage": null,
    "faithfulness": null,
    "absent_refusal_rate": null,
    "answerable_false_refusal_rate": 0.0
  },
  "error": {
    "code": "judgment_error",
    "type": "JudgeError",
    "message": "该阶段执行失败"
  },
  "elapsed_ms": 75711.59959980287,
  "judge_snapshot": {
    "prompt_version": "joint-generation-v2.1",
    "finish_reason": "length"
  },
  "audit": {
    "audit_version": 1,
    "source_map_id": "378ae65f4ee735c6a8079070fbfcb5c21800c93f3318029e5f19836c32b5c2b4",
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
        "chunk_id": 1769,
        "score": 0.032786883413791656,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1768,
        "score": 0.032258063554763794,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1771,
        "score": 0.0314980149269104,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1737,
        "score": 0.03079839050769806,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1742,
        "score": 0.03055037185549736,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1740,
        "score": 0.03009049780666828,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1767,
        "score": 0.02964426949620247,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1731,
        "score": 0.02854251116514206,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1747,
        "score": 0.028404511511325836,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1751,
        "score": 0.028370220214128494,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1770,
        "score": 0.02817460335791111,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1773,
        "score": 0.02684684842824936,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1777,
        "score": 0.026742734014987946,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1749,
        "score": 0.026234567165374756,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1765,
        "score": 0.02589375153183937,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1739,
        "score": 0.02565789595246315,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1772,
        "score": 0.02527821995317936,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1741,
        "score": 0.025035206228494644,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1748,
        "score": 0.024448420852422714,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1780,
        "score": 0.024201491847634315,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1743,
        "score": 0.02402186393737793,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1750,
        "score": 0.02395295351743698,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1776,
        "score": 0.023689374327659607,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1774,
        "score": 0.02336956560611725,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1779,
        "score": 0.022991543635725975,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1746,
        "score": 0.022753717377781868,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1752,
        "score": 0.022344322875142097,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1735,
        "score": 0.022214040160179138,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1736,
        "score": 0.01515151560306549,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1766,
        "score": 0.013333333656191826,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1738,
        "score": 0.012987012974917889,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1732,
        "score": 0.012345679104328156,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1744,
        "score": 0.01149425283074379,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1734,
        "score": 0.01123595517128706,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1778,
        "score": 0.011111111380159855,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1745,
        "score": 0.01075268816202879,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1757,
        "score": 0.010638297535479069,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1775,
        "score": 0.010526316240429878,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1733,
        "score": 0.010416666977107525,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1755,
        "score": 0.010204081423580647,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1753,
        "score": 0.010101010091602802,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1758,
        "score": 0.009999999776482582,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1756,
        "score": 0.009900989942252636,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1754,
        "score": 0.009803921915590763,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1762,
        "score": 0.009615384973585606,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1763,
        "score": 0.009433962404727936,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1760,
        "score": 0.009345794096589088,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1761,
        "score": 0.009259259328246117,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1764,
        "score": 0.00917431153357029,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1759,
        "score": 0.00909090880304575,
        "score_kind": "rrf"
      }
    ],
    "final_ranking": [
      {
        "chunk_id": 1769,
        "score": 0.032786883413791656,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1768,
        "score": 0.032258063554763794,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1771,
        "score": 0.0314980149269104,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1737,
        "score": 0.03079839050769806,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1742,
        "score": 0.03055037185549736,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1740,
        "score": 0.03009049780666828,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1767,
        "score": 0.02964426949620247,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1731,
        "score": 0.02854251116514206,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1747,
        "score": 0.028404511511325836,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1751,
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
  "status": "judge_error",
  "stage": "judgment",
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
          1769
        ]
      ]
    }
  ],
  "candidate_ids": [
    1769,
    1768,
    1771,
    1737,
    1742,
    1740,
    1767,
    1731,
    1747,
    1751,
    1770,
    1773,
    1777,
    1749,
    1765,
    1739,
    1772,
    1741,
    1748,
    1780,
    1743,
    1750,
    1776,
    1774,
    1779,
    1746,
    1752,
    1735,
    1736,
    1766,
    1738,
    1732,
    1744,
    1734,
    1778,
    1745,
    1757,
    1775,
    1733,
    1755,
    1753,
    1758,
    1756,
    1754,
    1762,
    1763,
    1760,
    1761,
    1764,
    1759
  ],
  "final_ids": [
    1769,
    1768,
    1771,
    1737,
    1742,
    1773,
    1778,
    1770,
    1774,
    1747
  ],
  "prompt_citations": [
    {
      "n": 1,
      "chunk_id": "1769",
      "section_path": "退货退款政策/退换货运费承担",
      "question": "退换货运费承担",
      "answer": "无理由退货的退回运费由买家承担;因商品质量问题、发错货、少发漏发导致的退换货,运费由平台承担。运费承担以平台售后规则最终判定为准。"
    },
    {
      "n": 3,
      "chunk_id": "1771",
      "section_path": "退货退款政策/运输破损处理",
      "question": "运输破损处理",
      "answer": "商品运输途中破损的,请在签收后 48 小时内联系客服并提供开箱视频与照片,核实后可免费补发或退款,相关运费由平台承担。"
    },
    {
      "n": 5,
      "chunk_id": "1742",
      "section_path": "商品与购物 FAQ/运费怎么算",
      "question": "运费怎么算",
      "answer": "单笔订单满 99 元包邮,未满收取 10 元运费,偏远地区运费另计。邮费即运费,按此规则收取。"
    },
    {
      "n": 7,
      "chunk_id": "1778",
      "section_path": "开票细则/可开票类型",
      "question": "可开票类型",
      "answer": "本演示店提供电子普通发票、电子专用发票和纸质专用发票。电子普通发票可按订单申请；电子专票需要企业账户，申请前准备发票抬头及有效纳税人识别号，按申请页面提交资料。\n\n纸质专票仅企业账户可申请，申请时需提供企业开票资料、收件人和邮寄地址，快递费到付。资料审核通过后按开票流程寄出，不承诺快递送达日期。"
    },
    {
      "n": 9,
      "chunk_id": "1774",
      "section_path": "会员权益/会员等级",
      "question": "会员等级",
      "answer": "会员分为普通、银卡和金卡三档，按有效累计消费金额自动升级，不按年度消费金额计算。累计消费未满 1000 元为普通会员，满 1000 元起为银卡，满 5000 元起为金卡。\n\n有效累计消费指已完成订单的商品实际支付金额，不含配送费；退货退款部分从有效累计消费中扣除。退款后根据更新的累计消费重新计算等级，未达到原门槛时可能降级。等级与适用权益在会员中心展示。\n\n银卡在参与会员折扣的商品上享 95 折，金卡享 9 折。折扣适用商品和活动范围以结算页面标注为准。会员折扣、优惠券与满减是否叠加也以当次活动页面为准，不能一概承诺全部优惠同时生效。"
    },
    {
      "n": 10,
      "chunk_id": "1747",
      "section_path": "商品与购物 FAQ/配送范围与偏远地区",
      "question": "配送范围与偏远地区",
      "answer": "全国大部分地区支持配送,新疆、西藏、内蒙古等偏远地区运费另计且时效顺延;港澳台及海外暂不支持自营配送。"
    },
    {
      "n": 8,
      "chunk_id": "1770",
      "section_path": "退货退款政策/质量问题与保修",
      "question": "质量问题与保修",
      "answer": "电子类商品自签收起保修 12 个月,保修期内非人为损坏可申请免费维修或换货;人为损坏、超保商品维修可能收取工本费。"
    },
    {
      "n": 6,
      "chunk_id": "1773",
      "section_path": "退货退款政策/预售与定金",
      "question": "预售与定金",
      "answer": "预售商品以详情页标注的时间发货;定金支付后不支持无理由退定金,尾款未按时支付的,定金按活动规则处理。"
    },
    {
      "n": 4,
      "chunk_id": "1737",
      "section_path": "售后手册/会员专属售后权益",
      "question": "会员专属售后权益",
      "answer": "金卡会员享优先客服接入与上门取件退换货;银卡会员享退换货运费权益 1 次/月。具体权益以会员中心页面标注为准。"
    },
    {
      "n": 2,
      "chunk_id": "1768",
      "section_path": "退货退款政策/换货政策/换货运费",
      "question": "换货运费",
      "answer": "非质量问题的换货,往返运费由买家承担;因质量问题或发错货的换货,往返运费由平台承担。"
    }
  ],
  "decision": {
    "useful": true,
    "reason": "证据直接说明少发漏发退换货运费由平台承担",
    "response_kind": "knowledge",
    "source": null
  },
  "answer": "您好！根据平台售后规则：因**少发漏发**导致的退换货，运费由**平台承担**[1]；如涉及换货，往返运费同样由平台承担[2]。最终以平台售后规则的判定为准[1]。\n\n如您遇到少发漏发情况，可提供订单号，我来协助您进一步核实处理。",
  "point_verdicts": null,
  "claim_verdicts": null,
  "metrics": {
    "recall_at_5": 1.0,
    "recall_at_10": 1.0,
    "mrr_at_10": 1.0,
    "all_groups_hit_at_5": 1.0,
    "all_groups_hit_at_10": 1.0,
    "candidate_group_coverage": 1.0,
    "prompt_group_coverage": 1.0,
    "answer_point_coverage": null,
    "faithfulness": null,
    "absent_refusal_rate": null,
    "answerable_false_refusal_rate": 0.0
  },
  "error": {
    "code": "judgment_error",
    "type": "JudgeError",
    "message": "该阶段执行失败"
  },
  "elapsed_ms": 71871.79400003515,
  "judge_snapshot": {
    "prompt_version": "joint-generation-v2.1",
    "finish_reason": "length"
  },
  "audit": {
    "audit_version": 1,
    "source_map_id": "378ae65f4ee735c6a8079070fbfcb5c21800c93f3318029e5f19836c32b5c2b4",
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
        "chunk_id": 1769,
        "score": 0.032786883413791656,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1768,
        "score": 0.032258063554763794,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1771,
        "score": 0.0314980149269104,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1737,
        "score": 0.03079839050769806,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1742,
        "score": 0.03055037185549736,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1740,
        "score": 0.03009049780666828,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1767,
        "score": 0.02964426949620247,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1731,
        "score": 0.02854251116514206,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1747,
        "score": 0.028404511511325836,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1751,
        "score": 0.028370220214128494,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1770,
        "score": 0.02817460335791111,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1773,
        "score": 0.02684684842824936,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1777,
        "score": 0.026742734014987946,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1749,
        "score": 0.026234567165374756,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1765,
        "score": 0.02589375153183937,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1739,
        "score": 0.02565789595246315,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1772,
        "score": 0.02527821995317936,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1741,
        "score": 0.025035206228494644,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1748,
        "score": 0.024448420852422714,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1780,
        "score": 0.024201491847634315,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1743,
        "score": 0.02402186393737793,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1750,
        "score": 0.02395295351743698,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1776,
        "score": 0.023689374327659607,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1774,
        "score": 0.02336956560611725,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1779,
        "score": 0.022991543635725975,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1746,
        "score": 0.022753717377781868,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1752,
        "score": 0.022344322875142097,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1735,
        "score": 0.022214040160179138,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1736,
        "score": 0.01515151560306549,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1766,
        "score": 0.013333333656191826,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1738,
        "score": 0.012987012974917889,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1732,
        "score": 0.012345679104328156,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1744,
        "score": 0.01149425283074379,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1734,
        "score": 0.01123595517128706,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1778,
        "score": 0.011111111380159855,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1745,
        "score": 0.01075268816202879,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1757,
        "score": 0.010638297535479069,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1775,
        "score": 0.010526316240429878,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1733,
        "score": 0.010416666977107525,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1755,
        "score": 0.010204081423580647,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1753,
        "score": 0.010101010091602802,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1758,
        "score": 0.009999999776482582,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1756,
        "score": 0.009900989942252636,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1754,
        "score": 0.009803921915590763,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1762,
        "score": 0.009615384973585606,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1763,
        "score": 0.009433962404727936,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1760,
        "score": 0.009345794096589088,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1761,
        "score": 0.009259259328246117,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1764,
        "score": 0.00917431153357029,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1759,
        "score": 0.00909090880304575,
        "score_kind": "rrf"
      }
    ],
    "final_ranking": [
      {
        "chunk_id": 1769,
        "score": 0.9927343130111694,
        "score_kind": "rerank"
      },
      {
        "chunk_id": 1768,
        "score": 0.8071091175079346,
        "score_kind": "rerank"
      },
      {
        "chunk_id": 1771,
        "score": 0.280374675989151,
        "score_kind": "rerank"
      },
      {
        "chunk_id": 1737,
        "score": 0.04180710390210152,
        "score_kind": "rerank"
      },
      {
        "chunk_id": 1742,
        "score": 0.03382489085197449,
        "score_kind": "rerank"
      },
      {
        "chunk_id": 1773,
        "score": 0.00980372354388237,
        "score_kind": "rerank"
      },
      {
        "chunk_id": 1778,
        "score": 0.008264950476586819,
        "score_kind": "rerank"
      },
      {
        "chunk_id": 1770,
        "score": 0.006191947963088751,
        "score_kind": "rerank"
      },
      {
        "chunk_id": 1774,
        "score": 0.00597203616052866,
        "score_kind": "rerank"
      },
      {
        "chunk_id": 1747,
        "score": 0.004727485124021769,
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
  "status": "judge_error",
  "stage": "judgment",
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
          1754
        ]
      ]
    }
  ],
  "candidate_ids": [
    1754,
    1753,
    1758,
    1763,
    1762,
    1757,
    1764,
    1755,
    1761,
    1759,
    1756,
    1760,
    1777,
    1774,
    1745,
    1773,
    1752,
    1737,
    1770,
    1778,
    1732,
    1736,
    1731,
    1748,
    1744,
    1735,
    1767,
    1746,
    1733,
    1741,
    1750,
    1747,
    1751,
    1765,
    1742,
    1771,
    1766,
    1768,
    1776,
    1734,
    1775,
    1738,
    1740,
    1743,
    1779,
    1739,
    1780,
    1772,
    1769,
    1749
  ],
  "final_ids": [
    1754,
    1753,
    1758,
    1763,
    1762,
    1757,
    1764,
    1755,
    1761,
    1759
  ],
  "prompt_citations": [
    {
      "n": 1,
      "chunk_id": "1754",
      "section_path": "商品规格手册/智能猫砂盆 Lite(型号 MH-LP50)",
      "question": "智能猫砂盆 Lite(型号 MH-LP50)",
      "answer": "- 型号:MH-LP50\n- 适用猫咪体重:1.5kg 至 6kg\n- 猫砂容量:6L\n- 核心功能:自动感应清理、物理除臭盖板;不含 App 联网功能\n- 与 Pro 差异:Lite 无 App 远程监控与健康记录,价格更低,适合单猫家庭"
    },
    {
      "n": 3,
      "chunk_id": "1758",
      "section_path": "商品规格手册/自动饮水机 Pro 不锈钢(型号 MH-W60)",
      "question": "自动饮水机 Pro 不锈钢(型号 MH-W60)",
      "answer": "- 型号:MH-W60\n- 水箱容量:6L,304 不锈钢表面盘\n- 过滤:双滤芯并联,建议每 4 周更换一次滤芯\n- 核心功能:双泵冗余、无线水位提醒推送 App、缺水断电保护\n- 清洗:不锈钢面盘可高温消毒,建议每周清洗一次"
    },
    {
      "n": 5,
      "chunk_id": "1762",
      "section_path": "商品规格手册/自动喂食器 基础版(型号 MH-FD10)",
      "question": "自动喂食器 基础版(型号 MH-FD10)",
      "answer": "- 型号:MH-FD10\n- 粮桶容量:4L\n- 核心功能:定时定量投喂,每日最多 6 餐,语音呼唤进食\n- 供电:市电供电 + 4 节 5 号电池断电应急\n- 说明:基础版不含摄像头与 App 远程投喂"
    },
    {
      "n": 7,
      "chunk_id": "1764",
      "section_path": "商品规格手册/全景看护摄像头(型号 MH-CAM1)",
      "question": "全景看护摄像头(型号 MH-CAM1)",
      "answer": "- 型号:MH-CAM1\n- 画质:2K 分辨率,355° 水平旋转、90° 俯仰\n- 核心功能:移动侦测报警、夜视、双向语音、逗猫激光\n- 存储:支持最大 128G TF 卡或云存储\n- 供电:Type-C 供电,需连接 2.4G Wi-Fi"
    },
    {
      "n": 9,
      "chunk_id": "1761",
      "section_path": "商品规格手册/大号三档加热垫(型号 MH-HP20)",
      "question": "大号三档加热垫(型号 MH-HP20)",
      "answer": "- 型号:MH-HP20\n- 尺寸:60cm × 45cm\n- 温控:三档可调 30℃ / 38℃ / 45℃,内置过热保护与定时关机\n- 防护:防水防抓咬电线套管,表面绒布可拆洗\n- 适用:大型猫、多猫窝及冬季保暖"
    },
    {
      "n": 10,
      "chunk_id": "1759",
      "section_path": "商品规格手册/大型猫爬架(型号 MH-CT30)",
      "question": "大型猫爬架(型号 MH-CT30)",
      "answer": "- 型号:MH-CT30\n- 高度:1.6m,共四层带顶层吊床\n- 承重:单层最大 10kg\n- 材质:剑麻柱身、绒布平台\n- 安装:需自行组装,随附六角扳手与图解说明书"
    },
    {
      "n": 8,
      "chunk_id": "1755",
      "section_path": "商品规格手册/智能猫砂盆 Max(型号 MH-LP200)",
      "question": "智能猫砂盆 Max(型号 MH-LP200)",
      "answer": "- 型号:MH-LP200\n- 适用猫咪体重:2kg 至 12kg,适合大型猫与多猫家庭\n- 猫砂容量:12L,废砂盒容量约 10 天(单猫)\n- 核心功能:超大滚筒、双重称重防夹、活性炭除臭、App 多猫健康档案\n- 供电:220V 市电\n- 清理提示:多猫家庭建议每 3 至 5 天倾倒一次废砂盒"
    },
    {
      "n": 6,
      "chunk_id": "1757",
      "section_path": "商品规格手册/自动饮水机 Plus(型号 MH-W40)",
      "question": "自动饮水机 Plus(型号 MH-W40)",
      "answer": "- 型号:MH-W40\n- 水箱容量:4L\n- 过滤:五重过滤棉 + 椰壳活性炭,建议每 3 周更换一次滤芯\n- 核心功能:UV 紫外杀菌、静音变频水泵、缺水断电保护\n- 清洗:整机可拆分水洗,建议每周清洗一次"
    },
    {
      "n": 4,
      "chunk_id": "1763",
      "section_path": "商品规格手册/自动喂食器 摄像头版(型号 MH-FD30)",
      "question": "自动喂食器 摄像头版(型号 MH-FD30)",
      "answer": "- 型号:MH-FD30\n- 粮桶容量:6L\n- 核心功能:1080P 摄像头、双向语音、App 远程手动投喂与定时投喂\n- 供电:市电供电 + 内置应急电池\n- 说明:摄像头版支持视频回看,需连接 2.4G Wi-Fi"
    },
    {
      "n": 2,
      "chunk_id": "1753",
      "section_path": "商品规格手册/智能猫砂盆 Pro(型号 MH-LP100)",
      "question": "智能猫砂盆 Pro(型号 MH-LP100)",
      "answer": "- 型号:MH-LP100\n- 适用猫咪体重:1.5kg 至 8kg\n- 猫砂容量:9L,废砂盒容量约 7 天(单猫)\n- 核心功能:自动感应清理、活性炭除臭、App 远程监控与健康记录\n- 供电:220V 市电,断电后配置自动保存\n- 清理提示:废砂盒满时 App 推送提醒,建议每 5 至 7 天倾倒一次"
    }
  ],
  "decision": {
    "useful": true,
    "reason": "含MH-LP50与Pro(MH-LP100)规格及差异说明",
    "response_kind": "knowledge",
    "source": null
  },
  "answer": "您好！根据商品规格资料，为您对比这两款智能猫砂盆的区别：\n\n**智能猫砂盆 Lite（MH-LP50）**[1]\n- 适用猫咪体重：1.5kg 至 6kg\n- 猫砂容量：6L\n- 核心功能：自动感应清理、物理除臭盖板，不含 App 联网功能\n- 适合单猫家庭，价格更低\n\n**智能猫砂盆 Pro（MH-LP100）**[2]\n- 适用猫咪体重：1.5kg 至 8kg\n- 猫砂容量：9L，废砂盒容量约 7 天（单猫）\n- 核心功能：自动感应清理、活性炭除臭、App 远程监控与健康记录\n- 供电：220V 市电，断电后配置自动保存；废砂盒满时 App 推送提醒，建议每 5 至 7 天倾倒一次\n\n**主要区别**：Lite 相比 Pro 无 App 远程监控与健康记录功能，价格更低[1]；Pro 容量更大、适用体重范围更广，并支持活性炭除臭和 App 健康记录[2]。\n\n如需了解具体价格或库存，欢迎告诉我，我可以为您查询哦～",
  "point_verdicts": null,
  "claim_verdicts": null,
  "metrics": {
    "recall_at_5": 1.0,
    "recall_at_10": 1.0,
    "mrr_at_10": 1.0,
    "all_groups_hit_at_5": 1.0,
    "all_groups_hit_at_10": 1.0,
    "candidate_group_coverage": 1.0,
    "prompt_group_coverage": 1.0,
    "answer_point_coverage": null,
    "faithfulness": null,
    "absent_refusal_rate": null,
    "answerable_false_refusal_rate": 0.0
  },
  "error": {
    "code": "judgment_error",
    "type": "JudgeError",
    "message": "该阶段执行失败"
  },
  "elapsed_ms": 56638.86950002052,
  "judge_snapshot": {
    "prompt_version": "joint-generation-v2.1",
    "finish_reason": "length"
  },
  "audit": {
    "audit_version": 1,
    "source_map_id": "378ae65f4ee735c6a8079070fbfcb5c21800c93f3318029e5f19836c32b5c2b4",
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
        "chunk_id": 1754,
        "score": 0.5419842600822449,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1753,
        "score": 0.49217647314071655,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1758,
        "score": 0.46255189180374146,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1763,
        "score": 0.44939449429512024,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1762,
        "score": 0.44784003496170044,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1757,
        "score": 0.44224005937576294,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1764,
        "score": 0.43727946281433105,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1755,
        "score": 0.4368886947631836,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1761,
        "score": 0.42109018564224243,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1759,
        "score": 0.4126494526863098,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1756,
        "score": 0.3972925841808319,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1760,
        "score": 0.3896021246910095,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1777,
        "score": 0.36445069313049316,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1774,
        "score": 0.3364074230194092,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1745,
        "score": 0.32716214656829834,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1773,
        "score": 0.32262861728668213,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1752,
        "score": 0.31935518980026245,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1737,
        "score": 0.31760919094085693,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1770,
        "score": 0.31754040718078613,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1778,
        "score": 0.30929529666900635,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1732,
        "score": 0.30889827013015747,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1736,
        "score": 0.29683154821395874,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1731,
        "score": 0.28847962617874146,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1748,
        "score": 0.2840690314769745,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1744,
        "score": 0.28290611505508423,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1735,
        "score": 0.28186357021331787,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1767,
        "score": 0.27764856815338135,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1746,
        "score": 0.2723686695098877,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1733,
        "score": 0.27169930934906006,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1741,
        "score": 0.26915642619132996,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1750,
        "score": 0.26893630623817444,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1747,
        "score": 0.25857019424438477,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1751,
        "score": 0.2577333152294159,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1765,
        "score": 0.24913570284843445,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1742,
        "score": 0.2489739954471588,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1771,
        "score": 0.24401283264160156,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1766,
        "score": 0.241316020488739,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1768,
        "score": 0.23707813024520874,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1776,
        "score": 0.23603908717632294,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1734,
        "score": 0.23596227169036865,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1775,
        "score": 0.23497463762760162,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1738,
        "score": 0.23046962916851044,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1740,
        "score": 0.228411003947258,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1743,
        "score": 0.2269769310951233,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1779,
        "score": 0.22349539399147034,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1739,
        "score": 0.2231275886297226,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1780,
        "score": 0.2210521250963211,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1772,
        "score": 0.21493637561798096,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1769,
        "score": 0.19500106573104858,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1749,
        "score": 0.18200039863586426,
        "score_kind": "cosine"
      }
    ],
    "final_ranking": [
      {
        "chunk_id": 1754,
        "score": 0.5419842600822449,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1753,
        "score": 0.49217647314071655,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1758,
        "score": 0.46255189180374146,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1763,
        "score": 0.44939449429512024,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1762,
        "score": 0.44784003496170044,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1757,
        "score": 0.44224005937576294,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1764,
        "score": 0.43727946281433105,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1755,
        "score": 0.4368886947631836,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1761,
        "score": 0.42109018564224243,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1759,
        "score": 0.4126494526863098,
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
  "refused": null,
  "status": "answer_error",
  "stage": "answer",
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
          1754
        ]
      ]
    }
  ],
  "candidate_ids": [
    1754,
    1738,
    1758,
    1753,
    1778,
    1746,
    1774,
    1759,
    1760,
    1756,
    1761,
    1757,
    1764,
    1762,
    1763,
    1755,
    1777
  ],
  "final_ids": [
    1754,
    1738,
    1758,
    1753,
    1778,
    1746,
    1774,
    1759,
    1760,
    1756
  ],
  "prompt_citations": [
    {
      "n": 1,
      "chunk_id": "1754",
      "section_path": "商品规格手册/智能猫砂盆 Lite(型号 MH-LP50)",
      "question": "智能猫砂盆 Lite(型号 MH-LP50)",
      "answer": "- 型号:MH-LP50\n- 适用猫咪体重:1.5kg 至 6kg\n- 猫砂容量:6L\n- 核心功能:自动感应清理、物理除臭盖板;不含 App 联网功能\n- 与 Pro 差异:Lite 无 App 远程监控与健康记录,价格更低,适合单猫家庭"
    },
    {
      "n": 3,
      "chunk_id": "1758",
      "section_path": "商品规格手册/自动饮水机 Pro 不锈钢(型号 MH-W60)",
      "question": "自动饮水机 Pro 不锈钢(型号 MH-W60)",
      "answer": "- 型号:MH-W60\n- 水箱容量:6L,304 不锈钢表面盘\n- 过滤:双滤芯并联,建议每 4 周更换一次滤芯\n- 核心功能:双泵冗余、无线水位提醒推送 App、缺水断电保护\n- 清洗:不锈钢面盘可高温消毒,建议每周清洗一次"
    },
    {
      "n": 5,
      "chunk_id": "1778",
      "section_path": "开票细则/可开票类型",
      "question": "可开票类型",
      "answer": "本演示店提供电子普通发票、电子专用发票和纸质专用发票。电子普通发票可按订单申请；电子专票需要企业账户，申请前准备发票抬头及有效纳税人识别号，按申请页面提交资料。\n\n纸质专票仅企业账户可申请，申请时需提供企业开票资料、收件人和邮寄地址，快递费到付。资料审核通过后按开票流程寄出，不承诺快递送达日期。"
    },
    {
      "n": 7,
      "chunk_id": "1774",
      "section_path": "会员权益/会员等级",
      "question": "会员等级",
      "answer": "会员分为普通、银卡和金卡三档，按有效累计消费金额自动升级，不按年度消费金额计算。累计消费未满 1000 元为普通会员，满 1000 元起为银卡，满 5000 元起为金卡。\n\n有效累计消费指已完成订单的商品实际支付金额，不含配送费；退货退款部分从有效累计消费中扣除。退款后根据更新的累计消费重新计算等级，未达到原门槛时可能降级。等级与适用权益在会员中心展示。\n\n银卡在参与会员折扣的商品上享 95 折，金卡享 9 折。折扣适用商品和活动范围以结算页面标注为准。会员折扣、优惠券与满减是否叠加也以当次活动页面为准，不能一概承诺全部优惠同时生效。"
    },
    {
      "n": 9,
      "chunk_id": "1760",
      "section_path": "商品规格手册/恒温加热垫(型号 MH-HP12)",
      "question": "恒温加热垫(型号 MH-HP12)",
      "answer": "- 型号:MH-HP12\n- 尺寸:40cm × 30cm\n- 温控:恒温 38℃,内置过热保护,连续通电不超过 12 小时为宜\n- 防护:防水防抓咬电线套管\n- 适用:幼猫、老年猫及冬季保暖"
    },
    {
      "n": 10,
      "chunk_id": "1756",
      "section_path": "商品规格手册/自动饮水机(型号 MH-W20)",
      "question": "自动饮水机(型号 MH-W20)",
      "answer": "- 型号:MH-W20\n- 水箱容量:2L\n- 过滤:三重过滤棉,建议每 2 周更换一次滤芯\n- 核心功能:静音水泵、缺水断电保护、水位窗口\n- 清洗:水泵可拆卸,建议每周清洗一次"
    },
    {
      "n": 8,
      "chunk_id": "1759",
      "section_path": "商品规格手册/大型猫爬架(型号 MH-CT30)",
      "question": "大型猫爬架(型号 MH-CT30)",
      "answer": "- 型号:MH-CT30\n- 高度:1.6m,共四层带顶层吊床\n- 承重:单层最大 10kg\n- 材质:剑麻柱身、绒布平台\n- 安装:需自行组装,随附六角扳手与图解说明书"
    },
    {
      "n": 6,
      "chunk_id": "1746",
      "section_path": "商品与购物 FAQ/优惠券和满减怎么用",
      "question": "优惠券和满减怎么用",
      "answer": "优惠券在结算页「使用优惠券」中勾选,满减活动自动叠加在商品页标示的门槛上;同一订单一般限用一张店铺券,活动细则以页面为准。"
    },
    {
      "n": 4,
      "chunk_id": "1753",
      "section_path": "商品规格手册/智能猫砂盆 Pro(型号 MH-LP100)",
      "question": "智能猫砂盆 Pro(型号 MH-LP100)",
      "answer": "- 型号:MH-LP100\n- 适用猫咪体重:1.5kg 至 8kg\n- 猫砂容量:9L,废砂盒容量约 7 天(单猫)\n- 核心功能:自动感应清理、活性炭除臭、App 远程监控与健康记录\n- 供电:220V 市电,断电后配置自动保存\n- 清理提示:废砂盒满时 App 推送提醒,建议每 5 至 7 天倾倒一次"
    },
    {
      "n": 2,
      "chunk_id": "1738",
      "section_path": "商品与购物 FAQ/退货政策是什么",
      "question": "退货政策是什么",
      "answer": "支持 7 天无理由退货,商品需保持完好、不影响二次销售,具体以平台售后规则为准。"
    }
  ],
  "decision": {
    "useful": true,
    "reason": "同时命中MH-LP50与Pro(MH-LP100)规格及差异说明",
    "response_kind": "knowledge",
    "source": null
  },
  "answer": null,
  "point_verdicts": null,
  "claim_verdicts": null,
  "metrics": {
    "recall_at_5": 1.0,
    "recall_at_10": 1.0,
    "mrr_at_10": 1.0,
    "all_groups_hit_at_5": 1.0,
    "all_groups_hit_at_10": 1.0,
    "candidate_group_coverage": 1.0,
    "prompt_group_coverage": 1.0,
    "answer_point_coverage": null,
    "faithfulness": null,
    "absent_refusal_rate": null,
    "answerable_false_refusal_rate": null
  },
  "error": {
    "code": "answer_error",
    "type": "ServiceError",
    "message": "该阶段执行失败"
  },
  "elapsed_ms": 31702.57920003496,
  "judge_snapshot": null,
  "audit": {
    "audit_version": 1,
    "source_map_id": "378ae65f4ee735c6a8079070fbfcb5c21800c93f3318029e5f19836c32b5c2b4",
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
        "chunk_id": 1754,
        "score": 9.145109176635742,
        "score_kind": "bm25"
      },
      {
        "chunk_id": 1738,
        "score": 4.2695698738098145,
        "score_kind": "bm25"
      },
      {
        "chunk_id": 1758,
        "score": 4.2516913414001465,
        "score_kind": "bm25"
      },
      {
        "chunk_id": 1753,
        "score": 3.9712343215942383,
        "score_kind": "bm25"
      },
      {
        "chunk_id": 1778,
        "score": 3.088531494140625,
        "score_kind": "bm25"
      },
      {
        "chunk_id": 1746,
        "score": 2.839679002761841,
        "score_kind": "bm25"
      },
      {
        "chunk_id": 1774,
        "score": 2.5103907585144043,
        "score_kind": "bm25"
      },
      {
        "chunk_id": 1759,
        "score": 1.9122194051742554,
        "score_kind": "bm25"
      },
      {
        "chunk_id": 1760,
        "score": 1.9122194051742554,
        "score_kind": "bm25"
      },
      {
        "chunk_id": 1756,
        "score": 1.880428671836853,
        "score_kind": "bm25"
      },
      {
        "chunk_id": 1761,
        "score": 1.8496778011322021,
        "score_kind": "bm25"
      },
      {
        "chunk_id": 1757,
        "score": 1.8102076053619385,
        "score_kind": "bm25"
      },
      {
        "chunk_id": 1764,
        "score": 1.7910975217819214,
        "score_kind": "bm25"
      },
      {
        "chunk_id": 1762,
        "score": 1.7816929817199707,
        "score_kind": "bm25"
      },
      {
        "chunk_id": 1763,
        "score": 1.7540630102157593,
        "score_kind": "bm25"
      },
      {
        "chunk_id": 1755,
        "score": 1.6596899032592773,
        "score_kind": "bm25"
      },
      {
        "chunk_id": 1777,
        "score": 1.2880016565322876,
        "score_kind": "bm25"
      }
    ],
    "final_ranking": [
      {
        "chunk_id": 1754,
        "score": 9.145109176635742,
        "score_kind": "bm25"
      },
      {
        "chunk_id": 1738,
        "score": 4.2695698738098145,
        "score_kind": "bm25"
      },
      {
        "chunk_id": 1758,
        "score": 4.2516913414001465,
        "score_kind": "bm25"
      },
      {
        "chunk_id": 1753,
        "score": 3.9712343215942383,
        "score_kind": "bm25"
      },
      {
        "chunk_id": 1778,
        "score": 3.088531494140625,
        "score_kind": "bm25"
      },
      {
        "chunk_id": 1746,
        "score": 2.839679002761841,
        "score_kind": "bm25"
      },
      {
        "chunk_id": 1774,
        "score": 2.5103907585144043,
        "score_kind": "bm25"
      },
      {
        "chunk_id": 1759,
        "score": 1.9122194051742554,
        "score_kind": "bm25"
      },
      {
        "chunk_id": 1760,
        "score": 1.9122194051742554,
        "score_kind": "bm25"
      },
      {
        "chunk_id": 1756,
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
  "refused": null,
  "status": "answer_error",
  "stage": "answer",
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
          1754
        ]
      ]
    }
  ],
  "candidate_ids": [
    1754,
    1753,
    1758,
    1757,
    1759,
    1763,
    1762,
    1764,
    1761,
    1774,
    1760,
    1756,
    1778,
    1755,
    1777,
    1746,
    1738,
    1745,
    1773,
    1752,
    1737,
    1770,
    1732,
    1736,
    1731,
    1748,
    1744,
    1735,
    1767,
    1733,
    1741,
    1750,
    1747,
    1751,
    1765,
    1742,
    1771,
    1766,
    1768,
    1776,
    1734,
    1775,
    1740,
    1743,
    1779,
    1739,
    1780,
    1772,
    1769,
    1749
  ],
  "final_ids": [
    1754,
    1753,
    1758,
    1757,
    1759,
    1763,
    1762,
    1764,
    1761,
    1774
  ],
  "prompt_citations": [
    {
      "n": 1,
      "chunk_id": "1754",
      "section_path": "商品规格手册/智能猫砂盆 Lite(型号 MH-LP50)",
      "question": "智能猫砂盆 Lite(型号 MH-LP50)",
      "answer": "- 型号:MH-LP50\n- 适用猫咪体重:1.5kg 至 6kg\n- 猫砂容量:6L\n- 核心功能:自动感应清理、物理除臭盖板;不含 App 联网功能\n- 与 Pro 差异:Lite 无 App 远程监控与健康记录,价格更低,适合单猫家庭"
    },
    {
      "n": 3,
      "chunk_id": "1758",
      "section_path": "商品规格手册/自动饮水机 Pro 不锈钢(型号 MH-W60)",
      "question": "自动饮水机 Pro 不锈钢(型号 MH-W60)",
      "answer": "- 型号:MH-W60\n- 水箱容量:6L,304 不锈钢表面盘\n- 过滤:双滤芯并联,建议每 4 周更换一次滤芯\n- 核心功能:双泵冗余、无线水位提醒推送 App、缺水断电保护\n- 清洗:不锈钢面盘可高温消毒,建议每周清洗一次"
    },
    {
      "n": 5,
      "chunk_id": "1759",
      "section_path": "商品规格手册/大型猫爬架(型号 MH-CT30)",
      "question": "大型猫爬架(型号 MH-CT30)",
      "answer": "- 型号:MH-CT30\n- 高度:1.6m,共四层带顶层吊床\n- 承重:单层最大 10kg\n- 材质:剑麻柱身、绒布平台\n- 安装:需自行组装,随附六角扳手与图解说明书"
    },
    {
      "n": 7,
      "chunk_id": "1762",
      "section_path": "商品规格手册/自动喂食器 基础版(型号 MH-FD10)",
      "question": "自动喂食器 基础版(型号 MH-FD10)",
      "answer": "- 型号:MH-FD10\n- 粮桶容量:4L\n- 核心功能:定时定量投喂,每日最多 6 餐,语音呼唤进食\n- 供电:市电供电 + 4 节 5 号电池断电应急\n- 说明:基础版不含摄像头与 App 远程投喂"
    },
    {
      "n": 9,
      "chunk_id": "1761",
      "section_path": "商品规格手册/大号三档加热垫(型号 MH-HP20)",
      "question": "大号三档加热垫(型号 MH-HP20)",
      "answer": "- 型号:MH-HP20\n- 尺寸:60cm × 45cm\n- 温控:三档可调 30℃ / 38℃ / 45℃,内置过热保护与定时关机\n- 防护:防水防抓咬电线套管,表面绒布可拆洗\n- 适用:大型猫、多猫窝及冬季保暖"
    },
    {
      "n": 10,
      "chunk_id": "1774",
      "section_path": "会员权益/会员等级",
      "question": "会员等级",
      "answer": "会员分为普通、银卡和金卡三档，按有效累计消费金额自动升级，不按年度消费金额计算。累计消费未满 1000 元为普通会员，满 1000 元起为银卡，满 5000 元起为金卡。\n\n有效累计消费指已完成订单的商品实际支付金额，不含配送费；退货退款部分从有效累计消费中扣除。退款后根据更新的累计消费重新计算等级，未达到原门槛时可能降级。等级与适用权益在会员中心展示。\n\n银卡在参与会员折扣的商品上享 95 折，金卡享 9 折。折扣适用商品和活动范围以结算页面标注为准。会员折扣、优惠券与满减是否叠加也以当次活动页面为准，不能一概承诺全部优惠同时生效。"
    },
    {
      "n": 8,
      "chunk_id": "1764",
      "section_path": "商品规格手册/全景看护摄像头(型号 MH-CAM1)",
      "question": "全景看护摄像头(型号 MH-CAM1)",
      "answer": "- 型号:MH-CAM1\n- 画质:2K 分辨率,355° 水平旋转、90° 俯仰\n- 核心功能:移动侦测报警、夜视、双向语音、逗猫激光\n- 存储:支持最大 128G TF 卡或云存储\n- 供电:Type-C 供电,需连接 2.4G Wi-Fi"
    },
    {
      "n": 6,
      "chunk_id": "1763",
      "section_path": "商品规格手册/自动喂食器 摄像头版(型号 MH-FD30)",
      "question": "自动喂食器 摄像头版(型号 MH-FD30)",
      "answer": "- 型号:MH-FD30\n- 粮桶容量:6L\n- 核心功能:1080P 摄像头、双向语音、App 远程手动投喂与定时投喂\n- 供电:市电供电 + 内置应急电池\n- 说明:摄像头版支持视频回看,需连接 2.4G Wi-Fi"
    },
    {
      "n": 4,
      "chunk_id": "1757",
      "section_path": "商品规格手册/自动饮水机 Plus(型号 MH-W40)",
      "question": "自动饮水机 Plus(型号 MH-W40)",
      "answer": "- 型号:MH-W40\n- 水箱容量:4L\n- 过滤:五重过滤棉 + 椰壳活性炭,建议每 3 周更换一次滤芯\n- 核心功能:UV 紫外杀菌、静音变频水泵、缺水断电保护\n- 清洗:整机可拆分水洗,建议每周清洗一次"
    },
    {
      "n": 2,
      "chunk_id": "1753",
      "section_path": "商品规格手册/智能猫砂盆 Pro(型号 MH-LP100)",
      "question": "智能猫砂盆 Pro(型号 MH-LP100)",
      "answer": "- 型号:MH-LP100\n- 适用猫咪体重:1.5kg 至 8kg\n- 猫砂容量:9L,废砂盒容量约 7 天(单猫)\n- 核心功能:自动感应清理、活性炭除臭、App 远程监控与健康记录\n- 供电:220V 市电,断电后配置自动保存\n- 清理提示:废砂盒满时 App 推送提醒,建议每 5 至 7 天倾倒一次"
    }
  ],
  "decision": {
    "useful": true,
    "reason": "两个型号规格齐全可直接对比",
    "response_kind": "knowledge",
    "source": null
  },
  "answer": null,
  "point_verdicts": null,
  "claim_verdicts": null,
  "metrics": {
    "recall_at_5": 1.0,
    "recall_at_10": 1.0,
    "mrr_at_10": 1.0,
    "all_groups_hit_at_5": 1.0,
    "all_groups_hit_at_10": 1.0,
    "candidate_group_coverage": 1.0,
    "prompt_group_coverage": 1.0,
    "answer_point_coverage": null,
    "faithfulness": null,
    "absent_refusal_rate": null,
    "answerable_false_refusal_rate": null
  },
  "error": {
    "code": "answer_error",
    "type": "ServiceError",
    "message": "该阶段执行失败"
  },
  "elapsed_ms": 30193.511199904606,
  "judge_snapshot": null,
  "audit": {
    "audit_version": 1,
    "source_map_id": "378ae65f4ee735c6a8079070fbfcb5c21800c93f3318029e5f19836c32b5c2b4",
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
        "chunk_id": 1754,
        "score": 0.032786883413791656,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1753,
        "score": 0.0317540317773819,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1758,
        "score": 0.0317460335791111,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1757,
        "score": 0.02904040366411209,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1759,
        "score": 0.028991596773266792,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1763,
        "score": 0.028958333656191826,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1762,
        "score": 0.028898129239678383,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1764,
        "score": 0.028624001890420914,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1761,
        "score": 0.028577260673046112,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1774,
        "score": 0.028438886627554893,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1760,
        "score": 0.02838164195418358,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1756,
        "score": 0.028370220214128494,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1778,
        "score": 0.02788461558520794,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1755,
        "score": 0.027863778173923492,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1777,
        "score": 0.026685643941164017,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1746,
        "score": 0.02651515230536461,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1738,
        "score": 0.025932952761650085,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1745,
        "score": 0.013333333656191826,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1773,
        "score": 0.01315789483487606,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1752,
        "score": 0.012987012974917889,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1737,
        "score": 0.012820512987673283,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1770,
        "score": 0.012658228166401386,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1732,
        "score": 0.012345679104328156,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1736,
        "score": 0.012195121496915817,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1731,
        "score": 0.012048192322254181,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1748,
        "score": 0.011904762126505375,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1744,
        "score": 0.0117647061124444,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1735,
        "score": 0.011627906933426857,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1767,
        "score": 0.01149425283074379,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1733,
        "score": 0.01123595517128706,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1741,
        "score": 0.011111111380159855,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1750,
        "score": 0.010989011265337467,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1747,
        "score": 0.010869565419852734,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1751,
        "score": 0.01075268816202879,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1765,
        "score": 0.010638297535479069,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1742,
        "score": 0.010526316240429878,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1771,
        "score": 0.010416666977107525,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1766,
        "score": 0.010309278033673763,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1768,
        "score": 0.010204081423580647,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1776,
        "score": 0.010101010091602802,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1734,
        "score": 0.009999999776482582,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1775,
        "score": 0.009900989942252636,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1740,
        "score": 0.009708737954497337,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1743,
        "score": 0.009615384973585606,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1779,
        "score": 0.009523809887468815,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1739,
        "score": 0.009433962404727936,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1780,
        "score": 0.009345794096589088,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1772,
        "score": 0.009259259328246117,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1769,
        "score": 0.00917431153357029,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1749,
        "score": 0.00909090880304575,
        "score_kind": "rrf"
      }
    ],
    "final_ranking": [
      {
        "chunk_id": 1754,
        "score": 0.032786883413791656,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1753,
        "score": 0.0317540317773819,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1758,
        "score": 0.0317460335791111,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1757,
        "score": 0.02904040366411209,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1759,
        "score": 0.028991596773266792,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1763,
        "score": 0.028958333656191826,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1762,
        "score": 0.028898129239678383,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1764,
        "score": 0.028624001890420914,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1761,
        "score": 0.028577260673046112,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1774,
        "score": 0.028438886627554893,
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
  "status": "judge_error",
  "stage": "judgment",
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
          1754
        ]
      ]
    }
  ],
  "candidate_ids": [
    1754,
    1753,
    1758,
    1757,
    1759,
    1763,
    1762,
    1764,
    1761,
    1774,
    1760,
    1756,
    1778,
    1755,
    1777,
    1746,
    1738,
    1745,
    1773,
    1752,
    1737,
    1770,
    1732,
    1736,
    1731,
    1748,
    1744,
    1735,
    1767,
    1733,
    1741,
    1750,
    1747,
    1751,
    1765,
    1742,
    1771,
    1766,
    1768,
    1776,
    1734,
    1775,
    1740,
    1743,
    1779,
    1739,
    1780,
    1772,
    1769,
    1749
  ],
  "final_ids": [
    1754,
    1753,
    1758,
    1762,
    1755,
    1764,
    1763,
    1774,
    1757,
    1737
  ],
  "prompt_citations": [
    {
      "n": 1,
      "chunk_id": "1754",
      "section_path": "商品规格手册/智能猫砂盆 Lite(型号 MH-LP50)",
      "question": "智能猫砂盆 Lite(型号 MH-LP50)",
      "answer": "- 型号:MH-LP50\n- 适用猫咪体重:1.5kg 至 6kg\n- 猫砂容量:6L\n- 核心功能:自动感应清理、物理除臭盖板;不含 App 联网功能\n- 与 Pro 差异:Lite 无 App 远程监控与健康记录,价格更低,适合单猫家庭"
    },
    {
      "n": 3,
      "chunk_id": "1758",
      "section_path": "商品规格手册/自动饮水机 Pro 不锈钢(型号 MH-W60)",
      "question": "自动饮水机 Pro 不锈钢(型号 MH-W60)",
      "answer": "- 型号:MH-W60\n- 水箱容量:6L,304 不锈钢表面盘\n- 过滤:双滤芯并联,建议每 4 周更换一次滤芯\n- 核心功能:双泵冗余、无线水位提醒推送 App、缺水断电保护\n- 清洗:不锈钢面盘可高温消毒,建议每周清洗一次"
    },
    {
      "n": 5,
      "chunk_id": "1755",
      "section_path": "商品规格手册/智能猫砂盆 Max(型号 MH-LP200)",
      "question": "智能猫砂盆 Max(型号 MH-LP200)",
      "answer": "- 型号:MH-LP200\n- 适用猫咪体重:2kg 至 12kg,适合大型猫与多猫家庭\n- 猫砂容量:12L,废砂盒容量约 10 天(单猫)\n- 核心功能:超大滚筒、双重称重防夹、活性炭除臭、App 多猫健康档案\n- 供电:220V 市电\n- 清理提示:多猫家庭建议每 3 至 5 天倾倒一次废砂盒"
    },
    {
      "n": 7,
      "chunk_id": "1763",
      "section_path": "商品规格手册/自动喂食器 摄像头版(型号 MH-FD30)",
      "question": "自动喂食器 摄像头版(型号 MH-FD30)",
      "answer": "- 型号:MH-FD30\n- 粮桶容量:6L\n- 核心功能:1080P 摄像头、双向语音、App 远程手动投喂与定时投喂\n- 供电:市电供电 + 内置应急电池\n- 说明:摄像头版支持视频回看,需连接 2.4G Wi-Fi"
    },
    {
      "n": 9,
      "chunk_id": "1757",
      "section_path": "商品规格手册/自动饮水机 Plus(型号 MH-W40)",
      "question": "自动饮水机 Plus(型号 MH-W40)",
      "answer": "- 型号:MH-W40\n- 水箱容量:4L\n- 过滤:五重过滤棉 + 椰壳活性炭,建议每 3 周更换一次滤芯\n- 核心功能:UV 紫外杀菌、静音变频水泵、缺水断电保护\n- 清洗:整机可拆分水洗,建议每周清洗一次"
    },
    {
      "n": 10,
      "chunk_id": "1737",
      "section_path": "售后手册/会员专属售后权益",
      "question": "会员专属售后权益",
      "answer": "金卡会员享优先客服接入与上门取件退换货;银卡会员享退换货运费权益 1 次/月。具体权益以会员中心页面标注为准。"
    },
    {
      "n": 8,
      "chunk_id": "1774",
      "section_path": "会员权益/会员等级",
      "question": "会员等级",
      "answer": "会员分为普通、银卡和金卡三档，按有效累计消费金额自动升级，不按年度消费金额计算。累计消费未满 1000 元为普通会员，满 1000 元起为银卡，满 5000 元起为金卡。\n\n有效累计消费指已完成订单的商品实际支付金额，不含配送费；退货退款部分从有效累计消费中扣除。退款后根据更新的累计消费重新计算等级，未达到原门槛时可能降级。等级与适用权益在会员中心展示。\n\n银卡在参与会员折扣的商品上享 95 折，金卡享 9 折。折扣适用商品和活动范围以结算页面标注为准。会员折扣、优惠券与满减是否叠加也以当次活动页面为准，不能一概承诺全部优惠同时生效。"
    },
    {
      "n": 6,
      "chunk_id": "1764",
      "section_path": "商品规格手册/全景看护摄像头(型号 MH-CAM1)",
      "question": "全景看护摄像头(型号 MH-CAM1)",
      "answer": "- 型号:MH-CAM1\n- 画质:2K 分辨率,355° 水平旋转、90° 俯仰\n- 核心功能:移动侦测报警、夜视、双向语音、逗猫激光\n- 存储:支持最大 128G TF 卡或云存储\n- 供电:Type-C 供电,需连接 2.4G Wi-Fi"
    },
    {
      "n": 4,
      "chunk_id": "1762",
      "section_path": "商品规格手册/自动喂食器 基础版(型号 MH-FD10)",
      "question": "自动喂食器 基础版(型号 MH-FD10)",
      "answer": "- 型号:MH-FD10\n- 粮桶容量:4L\n- 核心功能:定时定量投喂,每日最多 6 餐,语音呼唤进食\n- 供电:市电供电 + 4 节 5 号电池断电应急\n- 说明:基础版不含摄像头与 App 远程投喂"
    },
    {
      "n": 2,
      "chunk_id": "1753",
      "section_path": "商品规格手册/智能猫砂盆 Pro(型号 MH-LP100)",
      "question": "智能猫砂盆 Pro(型号 MH-LP100)",
      "answer": "- 型号:MH-LP100\n- 适用猫咪体重:1.5kg 至 8kg\n- 猫砂容量:9L,废砂盒容量约 7 天(单猫)\n- 核心功能:自动感应清理、活性炭除臭、App 远程监控与健康记录\n- 供电:220V 市电,断电后配置自动保存\n- 清理提示:废砂盒满时 App 推送提醒,建议每 5 至 7 天倾倒一次"
    }
  ],
  "decision": {
    "useful": true,
    "reason": "含Lite与Pro规格及差异说明",
    "response_kind": "knowledge",
    "source": null
  },
  "answer": "您好！根据商品规格手册，MH-LP50（Lite 版）和 Pro 版（MH-LP100）的主要区别如下：\n\n**MH-LP50（Lite 版）**[1]\n- 适用猫咪体重：1.5kg 至 6kg\n- 猫砂容量：6L\n- 核心功能：自动感应清理、物理除臭盖板，**不含 App 联网功能**\n- 定位：价格更低，适合单猫家庭\n\n**MH-LP100（Pro 版）**[2]\n- 适用猫咪体重：1.5kg 至 8kg\n- 猫砂容量：9L，废砂盒约 7 天容量（单猫）\n- 核心功能：自动感应清理、活性炭除臭、**App 远程监控与健康记录**\n- 其他：220V 市电供电，断电后配置自动保存；废砂盒满时 App 推送提醒\n\n**总结**：两者核心都是自动感应清理，主要区别在于 Pro 版适用体重范围更广、猫砂容量更大，并支持 App 远程监控与健康记录；Lite 版则价格更低，适合追求基础功能的单猫家庭 [1][2]。\n\n如需了解这两款的具体价格或库存，请告诉我，我可以为您查询。",
  "point_verdicts": null,
  "claim_verdicts": null,
  "metrics": {
    "recall_at_5": 1.0,
    "recall_at_10": 1.0,
    "mrr_at_10": 1.0,
    "all_groups_hit_at_5": 1.0,
    "all_groups_hit_at_10": 1.0,
    "candidate_group_coverage": 1.0,
    "prompt_group_coverage": 1.0,
    "answer_point_coverage": null,
    "faithfulness": null,
    "absent_refusal_rate": null,
    "answerable_false_refusal_rate": 0.0
  },
  "error": {
    "code": "judgment_error",
    "type": "JudgeError",
    "message": "该阶段执行失败"
  },
  "elapsed_ms": 60727.34380001202,
  "judge_snapshot": {
    "prompt_version": "joint-generation-v2.1",
    "finish_reason": "length"
  },
  "audit": {
    "audit_version": 1,
    "source_map_id": "378ae65f4ee735c6a8079070fbfcb5c21800c93f3318029e5f19836c32b5c2b4",
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
        "chunk_id": 1754,
        "score": 0.032786883413791656,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1753,
        "score": 0.0317540317773819,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1758,
        "score": 0.0317460335791111,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1757,
        "score": 0.02904040366411209,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1759,
        "score": 0.028991596773266792,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1763,
        "score": 0.028958333656191826,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1762,
        "score": 0.028898129239678383,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1764,
        "score": 0.028624001890420914,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1761,
        "score": 0.028577260673046112,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1774,
        "score": 0.028438886627554893,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1760,
        "score": 0.02838164195418358,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1756,
        "score": 0.028370220214128494,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1778,
        "score": 0.02788461558520794,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1755,
        "score": 0.027863778173923492,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1777,
        "score": 0.026685643941164017,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1746,
        "score": 0.02651515230536461,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1738,
        "score": 0.025932952761650085,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1745,
        "score": 0.013333333656191826,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1773,
        "score": 0.01315789483487606,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1752,
        "score": 0.012987012974917889,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1737,
        "score": 0.012820512987673283,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1770,
        "score": 0.012658228166401386,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1732,
        "score": 0.012345679104328156,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1736,
        "score": 0.012195121496915817,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1731,
        "score": 0.012048192322254181,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1748,
        "score": 0.011904762126505375,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1744,
        "score": 0.0117647061124444,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1735,
        "score": 0.011627906933426857,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1767,
        "score": 0.01149425283074379,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1733,
        "score": 0.01123595517128706,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1741,
        "score": 0.011111111380159855,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1750,
        "score": 0.010989011265337467,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1747,
        "score": 0.010869565419852734,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1751,
        "score": 0.01075268816202879,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1765,
        "score": 0.010638297535479069,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1742,
        "score": 0.010526316240429878,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1771,
        "score": 0.010416666977107525,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1766,
        "score": 0.010309278033673763,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1768,
        "score": 0.010204081423580647,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1776,
        "score": 0.010101010091602802,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1734,
        "score": 0.009999999776482582,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1775,
        "score": 0.009900989942252636,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1740,
        "score": 0.009708737954497337,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1743,
        "score": 0.009615384973585606,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1779,
        "score": 0.009523809887468815,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1739,
        "score": 0.009433962404727936,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1780,
        "score": 0.009345794096589088,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1772,
        "score": 0.009259259328246117,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1769,
        "score": 0.00917431153357029,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1749,
        "score": 0.00909090880304575,
        "score_kind": "rrf"
      }
    ],
    "final_ranking": [
      {
        "chunk_id": 1754,
        "score": 0.9740792512893677,
        "score_kind": "rerank"
      },
      {
        "chunk_id": 1753,
        "score": 0.1215970516204834,
        "score_kind": "rerank"
      },
      {
        "chunk_id": 1758,
        "score": 0.015334940515458584,
        "score_kind": "rerank"
      },
      {
        "chunk_id": 1762,
        "score": 0.008323847316205502,
        "score_kind": "rerank"
      },
      {
        "chunk_id": 1755,
        "score": 0.008040961809456348,
        "score_kind": "rerank"
      },
      {
        "chunk_id": 1764,
        "score": 0.004510152153670788,
        "score_kind": "rerank"
      },
      {
        "chunk_id": 1763,
        "score": 0.0037229075096547604,
        "score_kind": "rerank"
      },
      {
        "chunk_id": 1774,
        "score": 0.0034091256093233824,
        "score_kind": "rerank"
      },
      {
        "chunk_id": 1757,
        "score": 0.0017593230586498976,
        "score_kind": "rerank"
      },
      {
        "chunk_id": 1737,
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
  "status": "judge_error",
  "stage": "judgment",
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
          1756
        ]
      ]
    },
    {
      "group_id": "g2",
      "alternatives": [
        [
          1758
        ]
      ]
    }
  ],
  "candidate_ids": [
    1756,
    1757,
    1758,
    1777,
    1755,
    1754,
    1753,
    1761,
    1762,
    1763,
    1736,
    1760,
    1770,
    1767,
    1731,
    1732,
    1740,
    1759,
    1764,
    1765,
    1734,
    1735,
    1780,
    1737,
    1752,
    1779,
    1733,
    1741,
    1768,
    1738,
    1771,
    1749,
    1751,
    1773,
    1745,
    1766,
    1748,
    1772,
    1750,
    1774,
    1775,
    1744,
    1747,
    1778,
    1743,
    1769,
    1742,
    1739,
    1746,
    1776
  ],
  "final_ids": [
    1756,
    1757,
    1758,
    1777,
    1755,
    1754,
    1753,
    1761,
    1762,
    1763
  ],
  "prompt_citations": [
    {
      "n": 1,
      "chunk_id": "1756",
      "section_path": "商品规格手册/自动饮水机(型号 MH-W20)",
      "question": "自动饮水机(型号 MH-W20)",
      "answer": "- 型号:MH-W20\n- 水箱容量:2L\n- 过滤:三重过滤棉,建议每 2 周更换一次滤芯\n- 核心功能:静音水泵、缺水断电保护、水位窗口\n- 清洗:水泵可拆卸,建议每周清洗一次"
    },
    {
      "n": 3,
      "chunk_id": "1758",
      "section_path": "商品规格手册/自动饮水机 Pro 不锈钢(型号 MH-W60)",
      "question": "自动饮水机 Pro 不锈钢(型号 MH-W60)",
      "answer": "- 型号:MH-W60\n- 水箱容量:6L,304 不锈钢表面盘\n- 过滤:双滤芯并联,建议每 4 周更换一次滤芯\n- 核心功能:双泵冗余、无线水位提醒推送 App、缺水断电保护\n- 清洗:不锈钢面盘可高温消毒,建议每周清洗一次"
    },
    {
      "n": 5,
      "chunk_id": "1755",
      "section_path": "商品规格手册/智能猫砂盆 Max(型号 MH-LP200)",
      "question": "智能猫砂盆 Max(型号 MH-LP200)",
      "answer": "- 型号:MH-LP200\n- 适用猫咪体重:2kg 至 12kg,适合大型猫与多猫家庭\n- 猫砂容量:12L,废砂盒容量约 10 天(单猫)\n- 核心功能:超大滚筒、双重称重防夹、活性炭除臭、App 多猫健康档案\n- 供电:220V 市电\n- 清理提示:多猫家庭建议每 3 至 5 天倾倒一次废砂盒"
    },
    {
      "n": 7,
      "chunk_id": "1753",
      "section_path": "商品规格手册/智能猫砂盆 Pro(型号 MH-LP100)",
      "question": "智能猫砂盆 Pro(型号 MH-LP100)",
      "answer": "- 型号:MH-LP100\n- 适用猫咪体重:1.5kg 至 8kg\n- 猫砂容量:9L,废砂盒容量约 7 天(单猫)\n- 核心功能:自动感应清理、活性炭除臭、App 远程监控与健康记录\n- 供电:220V 市电,断电后配置自动保存\n- 清理提示:废砂盒满时 App 推送提醒,建议每 5 至 7 天倾倒一次"
    },
    {
      "n": 9,
      "chunk_id": "1762",
      "section_path": "商品规格手册/自动喂食器 基础版(型号 MH-FD10)",
      "question": "自动喂食器 基础版(型号 MH-FD10)",
      "answer": "- 型号:MH-FD10\n- 粮桶容量:4L\n- 核心功能:定时定量投喂,每日最多 6 餐,语音呼唤进食\n- 供电:市电供电 + 4 节 5 号电池断电应急\n- 说明:基础版不含摄像头与 App 远程投喂"
    },
    {
      "n": 10,
      "chunk_id": "1763",
      "section_path": "商品规格手册/自动喂食器 摄像头版(型号 MH-FD30)",
      "question": "自动喂食器 摄像头版(型号 MH-FD30)",
      "answer": "- 型号:MH-FD30\n- 粮桶容量:6L\n- 核心功能:1080P 摄像头、双向语音、App 远程手动投喂与定时投喂\n- 供电:市电供电 + 内置应急电池\n- 说明:摄像头版支持视频回看,需连接 2.4G Wi-Fi"
    },
    {
      "n": 8,
      "chunk_id": "1761",
      "section_path": "商品规格手册/大号三档加热垫(型号 MH-HP20)",
      "question": "大号三档加热垫(型号 MH-HP20)",
      "answer": "- 型号:MH-HP20\n- 尺寸:60cm × 45cm\n- 温控:三档可调 30℃ / 38℃ / 45℃,内置过热保护与定时关机\n- 防护:防水防抓咬电线套管,表面绒布可拆洗\n- 适用:大型猫、多猫窝及冬季保暖"
    },
    {
      "n": 6,
      "chunk_id": "1754",
      "section_path": "商品规格手册/智能猫砂盆 Lite(型号 MH-LP50)",
      "question": "智能猫砂盆 Lite(型号 MH-LP50)",
      "answer": "- 型号:MH-LP50\n- 适用猫咪体重:1.5kg 至 6kg\n- 猫砂容量:6L\n- 核心功能:自动感应清理、物理除臭盖板;不含 App 联网功能\n- 与 Pro 差异:Lite 无 App 远程监控与健康记录,价格更低,适合单猫家庭"
    },
    {
      "n": 4,
      "chunk_id": "1777",
      "section_path": "积分规则/积分怎么用",
      "question": "积分怎么用",
      "answer": "积分可在结算时抵扣商品金额，100 积分抵 1 元现金，单笔订单最多抵 30 元，不用于抵扣偏远地区附加运费，也不支持直接提现。\n\n2000 积分可兑换自动饮水机滤芯 3 片，该兑换套装适用于 MH-W40，普通配送地区包邮；偏远地区附加配送费仍需按页面规则确认。MH-W40 的滤芯更换周期以商品规格手册为准。\n\n800 积分可兑换猫零食小样，普通配送地区另收 6 元运费；该兑换不直接套用普通购物订单的满 99 元包邮规则。兑换商品、可用库存及偏远地区配送规则以兑换页面标注为准。"
    },
    {
      "n": 2,
      "chunk_id": "1757",
      "section_path": "商品规格手册/自动饮水机 Plus(型号 MH-W40)",
      "question": "自动饮水机 Plus(型号 MH-W40)",
      "answer": "- 型号:MH-W40\n- 水箱容量:4L\n- 过滤:五重过滤棉 + 椰壳活性炭,建议每 3 周更换一次滤芯\n- 核心功能:UV 紫外杀菌、静音变频水泵、缺水断电保护\n- 清洗:整机可拆分水洗,建议每周清洗一次"
    }
  ],
  "decision": {
    "useful": true,
    "reason": "两条规格均含滤芯更换周期：MH-W20每2周，MH-W60每4周，不一样",
    "response_kind": "knowledge",
    "source": null
  },
  "answer": "您好！不一样哦，两款饮水机的滤芯更换周期如下：\n\n- **MH-W20**（自动饮水机）：三重过滤棉，建议每 **2 周**更换一次滤芯 [1]\n- **MH-W60**（自动饮水机 Pro 不锈钢）：双滤芯并联，建议每 **4 周**更换一次滤芯 [3]\n\n因此 MH-W60 的滤芯更换周期比 MH-W20 更长。两款机器均建议每周清洗一次相关部件 [1][3]。如还有其他问题，欢迎随时咨询～",
  "point_verdicts": null,
  "claim_verdicts": null,
  "metrics": {
    "recall_at_5": 1.0,
    "recall_at_10": 1.0,
    "mrr_at_10": 1.0,
    "all_groups_hit_at_5": 1.0,
    "all_groups_hit_at_10": 1.0,
    "candidate_group_coverage": 1.0,
    "prompt_group_coverage": 1.0,
    "answer_point_coverage": null,
    "faithfulness": null,
    "absent_refusal_rate": null,
    "answerable_false_refusal_rate": 0.0
  },
  "error": {
    "code": "judgment_error",
    "type": "JudgeError",
    "message": "该阶段执行失败"
  },
  "elapsed_ms": 40736.72960000113,
  "judge_snapshot": {
    "prompt_version": "joint-generation-v2.1",
    "finish_reason": "length"
  },
  "audit": {
    "audit_version": 1,
    "source_map_id": "378ae65f4ee735c6a8079070fbfcb5c21800c93f3318029e5f19836c32b5c2b4",
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
        "chunk_id": 1756,
        "score": 0.6380270719528198,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1757,
        "score": 0.6060688495635986,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1758,
        "score": 0.6058511137962341,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1777,
        "score": 0.4773692488670349,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1755,
        "score": 0.46972841024398804,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1754,
        "score": 0.4595438241958618,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1753,
        "score": 0.4471765160560608,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1761,
        "score": 0.442929744720459,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1762,
        "score": 0.4386082887649536,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1763,
        "score": 0.43475478887557983,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1736,
        "score": 0.4185059666633606,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1760,
        "score": 0.4109259843826294,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1770,
        "score": 0.4054258465766907,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1767,
        "score": 0.3990286886692047,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1731,
        "score": 0.39590340852737427,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1732,
        "score": 0.394534707069397,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1740,
        "score": 0.3905488848686218,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1759,
        "score": 0.373737633228302,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1764,
        "score": 0.3643377721309662,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1765,
        "score": 0.3608345091342926,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1734,
        "score": 0.35968276858329773,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1735,
        "score": 0.35635748505592346,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1780,
        "score": 0.3515472114086151,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1737,
        "score": 0.3506259620189667,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1752,
        "score": 0.34732264280319214,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1779,
        "score": 0.3443598449230194,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1733,
        "score": 0.33749300241470337,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1741,
        "score": 0.33388233184814453,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1768,
        "score": 0.33323532342910767,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1738,
        "score": 0.3259001076221466,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1771,
        "score": 0.3190385103225708,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1749,
        "score": 0.3136257529258728,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1751,
        "score": 0.30811649560928345,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1773,
        "score": 0.3068224787712097,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1745,
        "score": 0.29876255989074707,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1766,
        "score": 0.29766228795051575,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1748,
        "score": 0.2969576120376587,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1772,
        "score": 0.27959519624710083,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1750,
        "score": 0.27952128648757935,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1774,
        "score": 0.278347373008728,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1775,
        "score": 0.2751007080078125,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1744,
        "score": 0.2708907127380371,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1747,
        "score": 0.27039021253585815,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1778,
        "score": 0.26322150230407715,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1743,
        "score": 0.260103315114975,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1769,
        "score": 0.259732723236084,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1742,
        "score": 0.24458271265029907,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1739,
        "score": 0.24380430579185486,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1746,
        "score": 0.23986023664474487,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1776,
        "score": 0.23981311917304993,
        "score_kind": "cosine"
      }
    ],
    "final_ranking": [
      {
        "chunk_id": 1756,
        "score": 0.6380270719528198,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1757,
        "score": 0.6060688495635986,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1758,
        "score": 0.6058511137962341,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1777,
        "score": 0.4773692488670349,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1755,
        "score": 0.46972841024398804,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1754,
        "score": 0.4595438241958618,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1753,
        "score": 0.4471765160560608,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1761,
        "score": 0.442929744720459,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1762,
        "score": 0.4386082887649536,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1763,
        "score": 0.43475478887557983,
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
          1756
        ]
      ]
    },
    {
      "group_id": "g2",
      "alternatives": [
        [
          1758
        ]
      ]
    }
  ],
  "candidate_ids": [
    1758,
    1756,
    1777,
    1757,
    1768,
    1748,
    1759,
    1760,
    1746,
    1761,
    1754,
    1764,
    1762,
    1774,
    1763,
    1755,
    1753,
    1778,
    1772,
    1773,
    1769,
    1780,
    1739,
    1741,
    1752,
    1743,
    1749,
    1767,
    1765,
    1750,
    1735,
    1771,
    1776,
    1779
  ],
  "final_ids": [
    1758,
    1756,
    1777,
    1757,
    1768,
    1748,
    1759,
    1760,
    1746,
    1761
  ],
  "prompt_citations": [
    {
      "n": 1,
      "chunk_id": "1758",
      "section_path": "商品规格手册/自动饮水机 Pro 不锈钢(型号 MH-W60)",
      "question": "自动饮水机 Pro 不锈钢(型号 MH-W60)",
      "answer": "- 型号:MH-W60\n- 水箱容量:6L,304 不锈钢表面盘\n- 过滤:双滤芯并联,建议每 4 周更换一次滤芯\n- 核心功能:双泵冗余、无线水位提醒推送 App、缺水断电保护\n- 清洗:不锈钢面盘可高温消毒,建议每周清洗一次"
    },
    {
      "n": 3,
      "chunk_id": "1777",
      "section_path": "积分规则/积分怎么用",
      "question": "积分怎么用",
      "answer": "积分可在结算时抵扣商品金额，100 积分抵 1 元现金，单笔订单最多抵 30 元，不用于抵扣偏远地区附加运费，也不支持直接提现。\n\n2000 积分可兑换自动饮水机滤芯 3 片，该兑换套装适用于 MH-W40，普通配送地区包邮；偏远地区附加配送费仍需按页面规则确认。MH-W40 的滤芯更换周期以商品规格手册为准。\n\n800 积分可兑换猫零食小样，普通配送地区另收 6 元运费；该兑换不直接套用普通购物订单的满 99 元包邮规则。兑换商品、可用库存及偏远地区配送规则以兑换页面标注为准。"
    },
    {
      "n": 5,
      "chunk_id": "1768",
      "section_path": "退货退款政策/换货政策/换货运费",
      "question": "换货运费",
      "answer": "非质量问题的换货,往返运费由买家承担;因质量问题或发错货的换货,往返运费由平台承担。"
    },
    {
      "n": 7,
      "chunk_id": "1759",
      "section_path": "商品规格手册/大型猫爬架(型号 MH-CT30)",
      "question": "大型猫爬架(型号 MH-CT30)",
      "answer": "- 型号:MH-CT30\n- 高度:1.6m,共四层带顶层吊床\n- 承重:单层最大 10kg\n- 材质:剑麻柱身、绒布平台\n- 安装:需自行组装,随附六角扳手与图解说明书"
    },
    {
      "n": 9,
      "chunk_id": "1746",
      "section_path": "商品与购物 FAQ/优惠券和满减怎么用",
      "question": "优惠券和满减怎么用",
      "answer": "优惠券在结算页「使用优惠券」中勾选,满减活动自动叠加在商品页标示的门槛上;同一订单一般限用一张店铺券,活动细则以页面为准。"
    },
    {
      "n": 10,
      "chunk_id": "1761",
      "section_path": "商品规格手册/大号三档加热垫(型号 MH-HP20)",
      "question": "大号三档加热垫(型号 MH-HP20)",
      "answer": "- 型号:MH-HP20\n- 尺寸:60cm × 45cm\n- 温控:三档可调 30℃ / 38℃ / 45℃,内置过热保护与定时关机\n- 防护:防水防抓咬电线套管,表面绒布可拆洗\n- 适用:大型猫、多猫窝及冬季保暖"
    },
    {
      "n": 8,
      "chunk_id": "1760",
      "section_path": "商品规格手册/恒温加热垫(型号 MH-HP12)",
      "question": "恒温加热垫(型号 MH-HP12)",
      "answer": "- 型号:MH-HP12\n- 尺寸:40cm × 30cm\n- 温控:恒温 38℃,内置过热保护,连续通电不超过 12 小时为宜\n- 防护:防水防抓咬电线套管\n- 适用:幼猫、老年猫及冬季保暖"
    },
    {
      "n": 6,
      "chunk_id": "1748",
      "section_path": "商品与购物 FAQ/订单可以修改或取消吗",
      "question": "订单可以修改或取消吗",
      "answer": "订单未发货前可在「我的订单」自助取消;已发货订单无法修改收货信息,可拒收后走退款流程。修改商品数量需取消后重新下单。"
    },
    {
      "n": 4,
      "chunk_id": "1757",
      "section_path": "商品规格手册/自动饮水机 Plus(型号 MH-W40)",
      "question": "自动饮水机 Plus(型号 MH-W40)",
      "answer": "- 型号:MH-W40\n- 水箱容量:4L\n- 过滤:五重过滤棉 + 椰壳活性炭,建议每 3 周更换一次滤芯\n- 核心功能:UV 紫外杀菌、静音变频水泵、缺水断电保护\n- 清洗:整机可拆分水洗,建议每周清洗一次"
    },
    {
      "n": 2,
      "chunk_id": "1756",
      "section_path": "商品规格手册/自动饮水机(型号 MH-W20)",
      "question": "自动饮水机(型号 MH-W20)",
      "answer": "- 型号:MH-W20\n- 水箱容量:2L\n- 过滤:三重过滤棉,建议每 2 周更换一次滤芯\n- 核心功能:静音水泵、缺水断电保护、水位窗口\n- 清洗:水泵可拆卸,建议每周清洗一次"
    }
  ],
  "decision": {
    "useful": true,
    "reason": "两个型号滤芯更换周期均有证据",
    "response_kind": "knowledge",
    "source": null
  },
  "answer": "不一样哦，两款饮水机的滤芯更换周期不同：\n\n- **MH-W20（自动饮水机）**：三重过滤棉，建议每 **2 周**更换一次滤芯 [2]\n- **MH-W60（自动饮水机 Pro 不锈钢）**：双滤芯并联，建议每 **4 周**更换一次滤芯 [1]\n\n简单来说，MH-W60 的更换周期更长一些。另外两款都建议每周清洗一次 [1][2]。请问还有什么可以帮您的吗？",
  "point_verdicts": [
    {
      "point_id": "p1",
      "covered": true,
      "reason": "回答明确说明 MH-W20（自动饮水机）三重过滤棉建议每2周更换一次滤芯，型号适用条件已保留"
    },
    {
      "point_id": "p2",
      "covered": true,
      "reason": "回答明确说明 MH-W60（自动饮水机 Pro 不锈钢）双滤芯并联建议每4周更换一次滤芯，并指出两款周期不同且 MH-W60 周期更长，条件已保留"
    }
  ],
  "claim_verdicts": [
    {
      "claim": "MH-W20 和 MH-W60 两款饮水机的滤芯更换周期不同",
      "supported": true,
      "reason": "证据2显示MH-W20建议每2周更换，证据1显示MH-W60建议每4周更换，两者周期确不相同"
    },
    {
      "claim": "MH-W20（自动饮水机）采用三重过滤棉",
      "supported": true,
      "reason": "证据2（商品规格手册/自动饮水机型号MH-W20）记载过滤为三重过滤棉"
    },
    {
      "claim": "MH-W20 建议每 2 周更换一次滤芯",
      "supported": true,
      "reason": "证据2（商品规格手册/自动饮水机型号MH-W20）明确建议每2周更换一次滤芯"
    },
    {
      "claim": "MH-W60（自动饮水机 Pro 不锈钢）采用双滤芯并联",
      "supported": true,
      "reason": "证据1（商品规格手册/自动饮水机Pro不锈钢型号MH-W60）记载过滤为双滤芯并联"
    },
    {
      "claim": "MH-W60 建议每 4 周更换一次滤芯",
      "supported": true,
      "reason": "证据1（商品规格手册/自动饮水机Pro不锈钢型号MH-W60）明确建议每4周更换一次滤芯"
    },
    {
      "claim": "MH-W60 的滤芯更换周期比 MH-W20 更长",
      "supported": true,
      "reason": "由证据1的每4周与证据2的每2周比较，4周长于2周，可支持该断言"
    },
    {
      "claim": "MH-W20 和 MH-W60 都建议每周清洗一次",
      "supported": true,
      "reason": "证据2记载MH-W20建议每周清洗一次，证据1记载MH-W60建议每周清洗一次"
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
  "elapsed_ms": 34027.84809982404,
  "judge_snapshot": {
    "prompt_version": "joint-generation-v2.1",
    "finish_reason": "stop"
  },
  "audit": {
    "audit_version": 1,
    "source_map_id": "378ae65f4ee735c6a8079070fbfcb5c21800c93f3318029e5f19836c32b5c2b4",
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
        "chunk_id": 1758,
        "score": 11.307323455810547,
        "score_kind": "bm25"
      },
      {
        "chunk_id": 1756,
        "score": 11.281126022338867,
        "score_kind": "bm25"
      },
      {
        "chunk_id": 1777,
        "score": 7.956859111785889,
        "score_kind": "bm25"
      },
      {
        "chunk_id": 1757,
        "score": 6.014775276184082,
        "score_kind": "bm25"
      },
      {
        "chunk_id": 1768,
        "score": 5.385351181030273,
        "score_kind": "bm25"
      },
      {
        "chunk_id": 1748,
        "score": 4.653332710266113,
        "score_kind": "bm25"
      },
      {
        "chunk_id": 1759,
        "score": 3.8244388103485107,
        "score_kind": "bm25"
      },
      {
        "chunk_id": 1760,
        "score": 3.8244388103485107,
        "score_kind": "bm25"
      },
      {
        "chunk_id": 1746,
        "score": 3.755237102508545,
        "score_kind": "bm25"
      },
      {
        "chunk_id": 1761,
        "score": 3.6993556022644043,
        "score_kind": "bm25"
      },
      {
        "chunk_id": 1754,
        "score": 3.5821950435638428,
        "score_kind": "bm25"
      },
      {
        "chunk_id": 1764,
        "score": 3.5821950435638428,
        "score_kind": "bm25"
      },
      {
        "chunk_id": 1762,
        "score": 3.5633859634399414,
        "score_kind": "bm25"
      },
      {
        "chunk_id": 1774,
        "score": 3.51131534576416,
        "score_kind": "bm25"
      },
      {
        "chunk_id": 1763,
        "score": 3.5081260204315186,
        "score_kind": "bm25"
      },
      {
        "chunk_id": 1755,
        "score": 3.3193798065185547,
        "score_kind": "bm25"
      },
      {
        "chunk_id": 1753,
        "score": 3.3032233715057373,
        "score_kind": "bm25"
      },
      {
        "chunk_id": 1778,
        "score": 3.088531494140625,
        "score_kind": "bm25"
      },
      {
        "chunk_id": 1772,
        "score": 1.4414697885513306,
        "score_kind": "bm25"
      },
      {
        "chunk_id": 1773,
        "score": 1.2937390804290771,
        "score_kind": "bm25"
      },
      {
        "chunk_id": 1769,
        "score": 1.215309500694275,
        "score_kind": "bm25"
      },
      {
        "chunk_id": 1780,
        "score": 1.1236776113510132,
        "score_kind": "bm25"
      },
      {
        "chunk_id": 1739,
        "score": 1.0660427808761597,
        "score_kind": "bm25"
      },
      {
        "chunk_id": 1741,
        "score": 1.0558345317840576,
        "score_kind": "bm25"
      },
      {
        "chunk_id": 1752,
        "score": 1.0359933376312256,
        "score_kind": "bm25"
      },
      {
        "chunk_id": 1743,
        "score": 1.0168840885162354,
        "score_kind": "bm25"
      },
      {
        "chunk_id": 1749,
        "score": 0.998467206954956,
        "score_kind": "bm25"
      },
      {
        "chunk_id": 1767,
        "score": 0.998467206954956,
        "score_kind": "bm25"
      },
      {
        "chunk_id": 1765,
        "score": 0.9895066618919373,
        "score_kind": "bm25"
      },
      {
        "chunk_id": 1750,
        "score": 0.9807054996490479,
        "score_kind": "bm25"
      },
      {
        "chunk_id": 1735,
        "score": 0.9720594882965088,
        "score_kind": "bm25"
      },
      {
        "chunk_id": 1771,
        "score": 0.9470126032829285,
        "score_kind": "bm25"
      },
      {
        "chunk_id": 1776,
        "score": 0.8389298319816589,
        "score_kind": "bm25"
      },
      {
        "chunk_id": 1779,
        "score": 0.7139831781387329,
        "score_kind": "bm25"
      }
    ],
    "final_ranking": [
      {
        "chunk_id": 1758,
        "score": 11.307323455810547,
        "score_kind": "bm25"
      },
      {
        "chunk_id": 1756,
        "score": 11.281126022338867,
        "score_kind": "bm25"
      },
      {
        "chunk_id": 1777,
        "score": 7.956859111785889,
        "score_kind": "bm25"
      },
      {
        "chunk_id": 1757,
        "score": 6.014775276184082,
        "score_kind": "bm25"
      },
      {
        "chunk_id": 1768,
        "score": 5.385351181030273,
        "score_kind": "bm25"
      },
      {
        "chunk_id": 1748,
        "score": 4.653332710266113,
        "score_kind": "bm25"
      },
      {
        "chunk_id": 1759,
        "score": 3.8244388103485107,
        "score_kind": "bm25"
      },
      {
        "chunk_id": 1760,
        "score": 3.8244388103485107,
        "score_kind": "bm25"
      },
      {
        "chunk_id": 1746,
        "score": 3.755237102508545,
        "score_kind": "bm25"
      },
      {
        "chunk_id": 1761,
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
  "status": "judge_error",
  "stage": "judgment",
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
          1756
        ]
      ]
    },
    {
      "group_id": "g2",
      "alternatives": [
        [
          1758
        ]
      ]
    }
  ],
  "candidate_ids": [
    1756,
    1758,
    1757,
    1777,
    1754,
    1761,
    1760,
    1755,
    1762,
    1753,
    1759,
    1763,
    1768,
    1764,
    1748,
    1767,
    1780,
    1765,
    1746,
    1752,
    1774,
    1741,
    1735,
    1773,
    1772,
    1778,
    1749,
    1779,
    1771,
    1769,
    1739,
    1750,
    1743,
    1776,
    1736,
    1770,
    1731,
    1732,
    1740,
    1734,
    1737,
    1733,
    1738,
    1751,
    1745,
    1766,
    1775,
    1744,
    1747,
    1742
  ],
  "final_ids": [
    1756,
    1758,
    1757,
    1777,
    1754,
    1761,
    1760,
    1755,
    1762,
    1753
  ],
  "prompt_citations": [
    {
      "n": 1,
      "chunk_id": "1756",
      "section_path": "商品规格手册/自动饮水机(型号 MH-W20)",
      "question": "自动饮水机(型号 MH-W20)",
      "answer": "- 型号:MH-W20\n- 水箱容量:2L\n- 过滤:三重过滤棉,建议每 2 周更换一次滤芯\n- 核心功能:静音水泵、缺水断电保护、水位窗口\n- 清洗:水泵可拆卸,建议每周清洗一次"
    },
    {
      "n": 3,
      "chunk_id": "1757",
      "section_path": "商品规格手册/自动饮水机 Plus(型号 MH-W40)",
      "question": "自动饮水机 Plus(型号 MH-W40)",
      "answer": "- 型号:MH-W40\n- 水箱容量:4L\n- 过滤:五重过滤棉 + 椰壳活性炭,建议每 3 周更换一次滤芯\n- 核心功能:UV 紫外杀菌、静音变频水泵、缺水断电保护\n- 清洗:整机可拆分水洗,建议每周清洗一次"
    },
    {
      "n": 5,
      "chunk_id": "1754",
      "section_path": "商品规格手册/智能猫砂盆 Lite(型号 MH-LP50)",
      "question": "智能猫砂盆 Lite(型号 MH-LP50)",
      "answer": "- 型号:MH-LP50\n- 适用猫咪体重:1.5kg 至 6kg\n- 猫砂容量:6L\n- 核心功能:自动感应清理、物理除臭盖板;不含 App 联网功能\n- 与 Pro 差异:Lite 无 App 远程监控与健康记录,价格更低,适合单猫家庭"
    },
    {
      "n": 7,
      "chunk_id": "1760",
      "section_path": "商品规格手册/恒温加热垫(型号 MH-HP12)",
      "question": "恒温加热垫(型号 MH-HP12)",
      "answer": "- 型号:MH-HP12\n- 尺寸:40cm × 30cm\n- 温控:恒温 38℃,内置过热保护,连续通电不超过 12 小时为宜\n- 防护:防水防抓咬电线套管\n- 适用:幼猫、老年猫及冬季保暖"
    },
    {
      "n": 9,
      "chunk_id": "1762",
      "section_path": "商品规格手册/自动喂食器 基础版(型号 MH-FD10)",
      "question": "自动喂食器 基础版(型号 MH-FD10)",
      "answer": "- 型号:MH-FD10\n- 粮桶容量:4L\n- 核心功能:定时定量投喂,每日最多 6 餐,语音呼唤进食\n- 供电:市电供电 + 4 节 5 号电池断电应急\n- 说明:基础版不含摄像头与 App 远程投喂"
    },
    {
      "n": 10,
      "chunk_id": "1753",
      "section_path": "商品规格手册/智能猫砂盆 Pro(型号 MH-LP100)",
      "question": "智能猫砂盆 Pro(型号 MH-LP100)",
      "answer": "- 型号:MH-LP100\n- 适用猫咪体重:1.5kg 至 8kg\n- 猫砂容量:9L,废砂盒容量约 7 天(单猫)\n- 核心功能:自动感应清理、活性炭除臭、App 远程监控与健康记录\n- 供电:220V 市电,断电后配置自动保存\n- 清理提示:废砂盒满时 App 推送提醒,建议每 5 至 7 天倾倒一次"
    },
    {
      "n": 8,
      "chunk_id": "1755",
      "section_path": "商品规格手册/智能猫砂盆 Max(型号 MH-LP200)",
      "question": "智能猫砂盆 Max(型号 MH-LP200)",
      "answer": "- 型号:MH-LP200\n- 适用猫咪体重:2kg 至 12kg,适合大型猫与多猫家庭\n- 猫砂容量:12L,废砂盒容量约 10 天(单猫)\n- 核心功能:超大滚筒、双重称重防夹、活性炭除臭、App 多猫健康档案\n- 供电:220V 市电\n- 清理提示:多猫家庭建议每 3 至 5 天倾倒一次废砂盒"
    },
    {
      "n": 6,
      "chunk_id": "1761",
      "section_path": "商品规格手册/大号三档加热垫(型号 MH-HP20)",
      "question": "大号三档加热垫(型号 MH-HP20)",
      "answer": "- 型号:MH-HP20\n- 尺寸:60cm × 45cm\n- 温控:三档可调 30℃ / 38℃ / 45℃,内置过热保护与定时关机\n- 防护:防水防抓咬电线套管,表面绒布可拆洗\n- 适用:大型猫、多猫窝及冬季保暖"
    },
    {
      "n": 4,
      "chunk_id": "1777",
      "section_path": "积分规则/积分怎么用",
      "question": "积分怎么用",
      "answer": "积分可在结算时抵扣商品金额，100 积分抵 1 元现金，单笔订单最多抵 30 元，不用于抵扣偏远地区附加运费，也不支持直接提现。\n\n2000 积分可兑换自动饮水机滤芯 3 片，该兑换套装适用于 MH-W40，普通配送地区包邮；偏远地区附加配送费仍需按页面规则确认。MH-W40 的滤芯更换周期以商品规格手册为准。\n\n800 积分可兑换猫零食小样，普通配送地区另收 6 元运费；该兑换不直接套用普通购物订单的满 99 元包邮规则。兑换商品、可用库存及偏远地区配送规则以兑换页面标注为准。"
    },
    {
      "n": 2,
      "chunk_id": "1758",
      "section_path": "商品规格手册/自动饮水机 Pro 不锈钢(型号 MH-W60)",
      "question": "自动饮水机 Pro 不锈钢(型号 MH-W60)",
      "answer": "- 型号:MH-W60\n- 水箱容量:6L,304 不锈钢表面盘\n- 过滤:双滤芯并联,建议每 4 周更换一次滤芯\n- 核心功能:双泵冗余、无线水位提醒推送 App、缺水断电保护\n- 清洗:不锈钢面盘可高温消毒,建议每周清洗一次"
    }
  ],
  "decision": {
    "useful": true,
    "reason": "已含MH-W20与MH-W60滤芯周期",
    "response_kind": "knowledge",
    "source": null
  },
  "answer": "您好，两款饮水机的滤芯更换周期不一样哦：\n\n- **MH-W20**：三重过滤棉，建议每 **2 周**更换一次滤芯 [1]\n- **MH-W60**：双滤芯并联，建议每 **4 周**更换一次滤芯 [2]\n\n两款机型都建议每周清洗一次水泵/机身 [1][2]。如需了解滤芯购买或其他问题，欢迎随时告诉我～",
  "point_verdicts": null,
  "claim_verdicts": null,
  "metrics": {
    "recall_at_5": 1.0,
    "recall_at_10": 1.0,
    "mrr_at_10": 1.0,
    "all_groups_hit_at_5": 1.0,
    "all_groups_hit_at_10": 1.0,
    "candidate_group_coverage": 1.0,
    "prompt_group_coverage": 1.0,
    "answer_point_coverage": null,
    "faithfulness": null,
    "absent_refusal_rate": null,
    "answerable_false_refusal_rate": 0.0
  },
  "error": {
    "code": "judgment_error",
    "type": "JudgeError",
    "message": "该阶段执行失败"
  },
  "elapsed_ms": 41945.40029997006,
  "judge_snapshot": {
    "prompt_version": "joint-generation-v2.1",
    "finish_reason": "length"
  },
  "audit": {
    "audit_version": 1,
    "source_map_id": "378ae65f4ee735c6a8079070fbfcb5c21800c93f3318029e5f19836c32b5c2b4",
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
        "chunk_id": 1756,
        "score": 0.032522473484277725,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1758,
        "score": 0.03226646035909653,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1757,
        "score": 0.0317540317773819,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1777,
        "score": 0.0314980149269104,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1754,
        "score": 0.029236022382974625,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1761,
        "score": 0.028991596773266792,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1760,
        "score": 0.028594771400094032,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1755,
        "score": 0.02854251116514206,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1762,
        "score": 0.02819138392806053,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1753,
        "score": 0.027912385761737823,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1759,
        "score": 0.027745885774493217,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1763,
        "score": 0.027619048953056335,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1768,
        "score": 0.026620570570230484,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1764,
        "score": 0.02654711715877056,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1748,
        "score": 0.02546079456806183,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1767,
        "score": 0.024877149611711502,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1780,
        "score": 0.024243313819169998,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1765,
        "score": 0.023735955357551575,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1746,
        "score": 0.023667065426707268,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1752,
        "score": 0.0235294122248888,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1774,
        "score": 0.023513514548540115,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1741,
        "score": 0.02326839789748192,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1735,
        "score": 0.02318413183093071,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1773,
        "score": 0.023138297721743584,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1772,
        "score": 0.022862309589982033,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1778,
        "score": 0.022435897961258888,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1749,
        "score": 0.022363819181919098,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1779,
        "score": 0.0222662054002285,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1771,
        "score": 0.0218585766851902,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1769,
        "score": 0.02177964150905609,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1739,
        "score": 0.021307451650500298,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1750,
        "score": 0.021212121471762657,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1743,
        "score": 0.021151717752218246,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1776,
        "score": 0.01984359696507454,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1736,
        "score": 0.014084506779909134,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1770,
        "score": 0.013698630034923553,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1731,
        "score": 0.013333333656191826,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1732,
        "score": 0.01315789483487606,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1740,
        "score": 0.012987012974917889,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1734,
        "score": 0.012345679104328156,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1737,
        "score": 0.011904762126505375,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1733,
        "score": 0.01149425283074379,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1738,
        "score": 0.011111111380159855,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1751,
        "score": 0.01075268816202879,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1745,
        "score": 0.010526316240429878,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1766,
        "score": 0.010416666977107525,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1775,
        "score": 0.009900989942252636,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1744,
        "score": 0.009803921915590763,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1747,
        "score": 0.009708737954497337,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1742,
        "score": 0.009345794096589088,
        "score_kind": "rrf"
      }
    ],
    "final_ranking": [
      {
        "chunk_id": 1756,
        "score": 0.032522473484277725,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1758,
        "score": 0.03226646035909653,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1757,
        "score": 0.0317540317773819,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1777,
        "score": 0.0314980149269104,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1754,
        "score": 0.029236022382974625,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1761,
        "score": 0.028991596773266792,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1760,
        "score": 0.028594771400094032,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1755,
        "score": 0.02854251116514206,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1762,
        "score": 0.02819138392806053,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1753,
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
  "status": "judge_error",
  "stage": "judgment",
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
          1756
        ]
      ]
    },
    {
      "group_id": "g2",
      "alternatives": [
        [
          1758
        ]
      ]
    }
  ],
  "candidate_ids": [
    1756,
    1758,
    1757,
    1777,
    1754,
    1761,
    1760,
    1755,
    1762,
    1753,
    1759,
    1763,
    1768,
    1764,
    1748,
    1767,
    1780,
    1765,
    1746,
    1752,
    1774,
    1741,
    1735,
    1773,
    1772,
    1778,
    1749,
    1779,
    1771,
    1769,
    1739,
    1750,
    1743,
    1776,
    1736,
    1770,
    1731,
    1732,
    1740,
    1734,
    1737,
    1733,
    1738,
    1751,
    1745,
    1766,
    1775,
    1744,
    1747,
    1742
  ],
  "final_ids": [
    1756,
    1758,
    1777,
    1757,
    1761,
    1770,
    1732,
    1767,
    1736,
    1755
  ],
  "prompt_citations": [
    {
      "n": 1,
      "chunk_id": "1756",
      "section_path": "商品规格手册/自动饮水机(型号 MH-W20)",
      "question": "自动饮水机(型号 MH-W20)",
      "answer": "- 型号:MH-W20\n- 水箱容量:2L\n- 过滤:三重过滤棉,建议每 2 周更换一次滤芯\n- 核心功能:静音水泵、缺水断电保护、水位窗口\n- 清洗:水泵可拆卸,建议每周清洗一次"
    },
    {
      "n": 3,
      "chunk_id": "1777",
      "section_path": "积分规则/积分怎么用",
      "question": "积分怎么用",
      "answer": "积分可在结算时抵扣商品金额，100 积分抵 1 元现金，单笔订单最多抵 30 元，不用于抵扣偏远地区附加运费，也不支持直接提现。\n\n2000 积分可兑换自动饮水机滤芯 3 片，该兑换套装适用于 MH-W40，普通配送地区包邮；偏远地区附加配送费仍需按页面规则确认。MH-W40 的滤芯更换周期以商品规格手册为准。\n\n800 积分可兑换猫零食小样，普通配送地区另收 6 元运费；该兑换不直接套用普通购物订单的满 99 元包邮规则。兑换商品、可用库存及偏远地区配送规则以兑换页面标注为准。"
    },
    {
      "n": 5,
      "chunk_id": "1761",
      "section_path": "商品规格手册/大号三档加热垫(型号 MH-HP20)",
      "question": "大号三档加热垫(型号 MH-HP20)",
      "answer": "- 型号:MH-HP20\n- 尺寸:60cm × 45cm\n- 温控:三档可调 30℃ / 38℃ / 45℃,内置过热保护与定时关机\n- 防护:防水防抓咬电线套管,表面绒布可拆洗\n- 适用:大型猫、多猫窝及冬季保暖"
    },
    {
      "n": 7,
      "chunk_id": "1732",
      "section_path": "售后手册/保修说明",
      "question": "保修说明",
      "answer": "电子类商品保修 12 个月,自签收日起算;人为损坏不在保修范围。"
    },
    {
      "n": 9,
      "chunk_id": "1736",
      "section_path": "售后手册/维修寄修流程",
      "question": "维修寄修流程",
      "answer": "保修期内设备故障,联系客服登记后按指引将设备寄回指定维修点,核验后免费维修并寄回;超保或人为损坏维修可能收取工本费,费用会提前告知。"
    },
    {
      "n": 10,
      "chunk_id": "1755",
      "section_path": "商品规格手册/智能猫砂盆 Max(型号 MH-LP200)",
      "question": "智能猫砂盆 Max(型号 MH-LP200)",
      "answer": "- 型号:MH-LP200\n- 适用猫咪体重:2kg 至 12kg,适合大型猫与多猫家庭\n- 猫砂容量:12L,废砂盒容量约 10 天(单猫)\n- 核心功能:超大滚筒、双重称重防夹、活性炭除臭、App 多猫健康档案\n- 供电:220V 市电\n- 清理提示:多猫家庭建议每 3 至 5 天倾倒一次废砂盒"
    },
    {
      "n": 8,
      "chunk_id": "1767",
      "section_path": "退货退款政策/换货政策/换货条件",
      "question": "换货条件",
      "answer": "收到商品 7 天内,商品完好且配件齐全的,可申请一次同款换货;不同型号或颜色需先退货再重新下单。"
    },
    {
      "n": 6,
      "chunk_id": "1770",
      "section_path": "退货退款政策/质量问题与保修",
      "question": "质量问题与保修",
      "answer": "电子类商品自签收起保修 12 个月,保修期内非人为损坏可申请免费维修或换货;人为损坏、超保商品维修可能收取工本费。"
    },
    {
      "n": 4,
      "chunk_id": "1757",
      "section_path": "商品规格手册/自动饮水机 Plus(型号 MH-W40)",
      "question": "自动饮水机 Plus(型号 MH-W40)",
      "answer": "- 型号:MH-W40\n- 水箱容量:4L\n- 过滤:五重过滤棉 + 椰壳活性炭,建议每 3 周更换一次滤芯\n- 核心功能:UV 紫外杀菌、静音变频水泵、缺水断电保护\n- 清洗:整机可拆分水洗,建议每周清洗一次"
    },
    {
      "n": 2,
      "chunk_id": "1758",
      "section_path": "商品规格手册/自动饮水机 Pro 不锈钢(型号 MH-W60)",
      "question": "自动饮水机 Pro 不锈钢(型号 MH-W60)",
      "answer": "- 型号:MH-W60\n- 水箱容量:6L,304 不锈钢表面盘\n- 过滤:双滤芯并联,建议每 4 周更换一次滤芯\n- 核心功能:双泵冗余、无线水位提醒推送 App、缺水断电保护\n- 清洗:不锈钢面盘可高温消毒,建议每周清洗一次"
    }
  ],
  "decision": {
    "useful": true,
    "reason": "两个型号滤芯周期均有证据：MH-W20每2周，MH-W60每4周，不一样",
    "response_kind": "knowledge",
    "source": null
  },
  "answer": "您好，不一样的哦～\n\n- **MH-W20**（自动饮水机）：三重过滤棉，建议每 2 周更换一次滤芯 [1]\n- **MH-W60**（自动饮水机 Pro 不锈钢）：双滤芯并联，建议每 4 周更换一次滤芯 [2]\n\n简单来说，MH-W60 的滤芯更换周期更长一些。两款机型都建议每周清洗一次机身相关部件 [1][2]。如需了解其他参数，欢迎随时询问～",
  "point_verdicts": null,
  "claim_verdicts": null,
  "metrics": {
    "recall_at_5": 1.0,
    "recall_at_10": 1.0,
    "mrr_at_10": 1.0,
    "all_groups_hit_at_5": 1.0,
    "all_groups_hit_at_10": 1.0,
    "candidate_group_coverage": 1.0,
    "prompt_group_coverage": 1.0,
    "answer_point_coverage": null,
    "faithfulness": null,
    "absent_refusal_rate": null,
    "answerable_false_refusal_rate": 0.0
  },
  "error": {
    "code": "judgment_error",
    "type": "JudgeError",
    "message": "该阶段执行失败"
  },
  "elapsed_ms": 43731.0401997529,
  "judge_snapshot": {
    "prompt_version": "joint-generation-v2.1",
    "finish_reason": "length"
  },
  "audit": {
    "audit_version": 1,
    "source_map_id": "378ae65f4ee735c6a8079070fbfcb5c21800c93f3318029e5f19836c32b5c2b4",
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
        "chunk_id": 1756,
        "score": 0.032522473484277725,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1758,
        "score": 0.03226646035909653,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1757,
        "score": 0.0317540317773819,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1777,
        "score": 0.0314980149269104,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1754,
        "score": 0.029236022382974625,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1761,
        "score": 0.028991596773266792,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1760,
        "score": 0.028594771400094032,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1755,
        "score": 0.02854251116514206,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1762,
        "score": 0.02819138392806053,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1753,
        "score": 0.027912385761737823,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1759,
        "score": 0.027745885774493217,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1763,
        "score": 0.027619048953056335,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1768,
        "score": 0.026620570570230484,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1764,
        "score": 0.02654711715877056,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1748,
        "score": 0.02546079456806183,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1767,
        "score": 0.024877149611711502,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1780,
        "score": 0.024243313819169998,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1765,
        "score": 0.023735955357551575,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1746,
        "score": 0.023667065426707268,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1752,
        "score": 0.0235294122248888,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1774,
        "score": 0.023513514548540115,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1741,
        "score": 0.02326839789748192,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1735,
        "score": 0.02318413183093071,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1773,
        "score": 0.023138297721743584,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1772,
        "score": 0.022862309589982033,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1778,
        "score": 0.022435897961258888,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1749,
        "score": 0.022363819181919098,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1779,
        "score": 0.0222662054002285,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1771,
        "score": 0.0218585766851902,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1769,
        "score": 0.02177964150905609,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1739,
        "score": 0.021307451650500298,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1750,
        "score": 0.021212121471762657,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1743,
        "score": 0.021151717752218246,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1776,
        "score": 0.01984359696507454,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1736,
        "score": 0.014084506779909134,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1770,
        "score": 0.013698630034923553,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1731,
        "score": 0.013333333656191826,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1732,
        "score": 0.01315789483487606,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1740,
        "score": 0.012987012974917889,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1734,
        "score": 0.012345679104328156,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1737,
        "score": 0.011904762126505375,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1733,
        "score": 0.01149425283074379,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1738,
        "score": 0.011111111380159855,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1751,
        "score": 0.01075268816202879,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1745,
        "score": 0.010526316240429878,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1766,
        "score": 0.010416666977107525,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1775,
        "score": 0.009900989942252636,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1744,
        "score": 0.009803921915590763,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1747,
        "score": 0.009708737954497337,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1742,
        "score": 0.009345794096589088,
        "score_kind": "rrf"
      }
    ],
    "final_ranking": [
      {
        "chunk_id": 1756,
        "score": 0.9687467813491821,
        "score_kind": "rerank"
      },
      {
        "chunk_id": 1758,
        "score": 0.8881435990333557,
        "score_kind": "rerank"
      },
      {
        "chunk_id": 1777,
        "score": 0.16230498254299164,
        "score_kind": "rerank"
      },
      {
        "chunk_id": 1757,
        "score": 0.1140696108341217,
        "score_kind": "rerank"
      },
      {
        "chunk_id": 1761,
        "score": 0.005079270806163549,
        "score_kind": "rerank"
      },
      {
        "chunk_id": 1770,
        "score": 0.0016978556523099542,
        "score_kind": "rerank"
      },
      {
        "chunk_id": 1732,
        "score": 0.0013380321906879544,
        "score_kind": "rerank"
      },
      {
        "chunk_id": 1767,
        "score": 0.0012320857495069504,
        "score_kind": "rerank"
      },
      {
        "chunk_id": 1736,
        "score": 0.001129837823100388,
        "score_kind": "rerank"
      },
      {
        "chunk_id": 1755,
        "score": 0.0009845298482105136,
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
  "status": "judge_error",
  "stage": "judgment",
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
          1742
        ]
      ]
    }
  ],
  "candidate_ids": [
    1742,
    1777,
    1751,
    1768,
    1776,
    1769,
    1747,
    1736,
    1745,
    1771,
    1743,
    1774,
    1737,
    1770,
    1778,
    1750,
    1775,
    1731,
    1741,
    1779,
    1773,
    1744,
    1740,
    1767,
    1753,
    1765,
    1754,
    1732,
    1748,
    1746,
    1739,
    1758,
    1738,
    1755,
    1757,
    1762,
    1766,
    1735,
    1749,
    1756,
    1763,
    1761,
    1760,
    1733,
    1759,
    1772,
    1734,
    1752,
    1764,
    1780
  ],
  "final_ids": [
    1742,
    1777,
    1751,
    1768,
    1776,
    1769,
    1747,
    1736,
    1745,
    1771
  ],
  "prompt_citations": [
    {
      "n": 1,
      "chunk_id": "1742",
      "section_path": "商品与购物 FAQ/运费怎么算",
      "question": "运费怎么算",
      "answer": "单笔订单满 99 元包邮,未满收取 10 元运费,偏远地区运费另计。邮费即运费,按此规则收取。"
    },
    {
      "n": 3,
      "chunk_id": "1751",
      "section_path": "商品与购物 FAQ/会员运费权益",
      "question": "会员运费权益",
      "answer": "金卡会员每月享 3 次免运费权益,银卡会员享 1 次;权益不与偏远地区附加运费冲抵,当月未用完不结转。"
    },
    {
      "n": 5,
      "chunk_id": "1776",
      "section_path": "积分规则/积分怎么攒",
      "question": "积分怎么攒",
      "answer": "已完成订单每实际支付 1 元商品金额累计 1 积分，不计配送费；退款后按对应商品金额同步扣回积分。活动期间的双倍积分属于额外积分奖励，不计入会员等级升级；会员等级仍按有效累计消费金额计算。"
    },
    {
      "n": 7,
      "chunk_id": "1747",
      "section_path": "商品与购物 FAQ/配送范围与偏远地区",
      "question": "配送范围与偏远地区",
      "answer": "全国大部分地区支持配送,新疆、西藏、内蒙古等偏远地区运费另计且时效顺延;港澳台及海外暂不支持自营配送。"
    },
    {
      "n": 9,
      "chunk_id": "1745",
      "section_path": "商品与购物 FAQ/会员等级与积分规则",
      "question": "会员等级与积分规则",
      "answer": "会员分为普通、银卡、金卡三档,按累计消费自动升级。每消费 1 元得 1 积分,积分可在结算时抵扣,100 积分抵 1 元。"
    },
    {
      "n": 10,
      "chunk_id": "1771",
      "section_path": "退货退款政策/运输破损处理",
      "question": "运输破损处理",
      "answer": "商品运输途中破损的,请在签收后 48 小时内联系客服并提供开箱视频与照片,核实后可免费补发或退款,相关运费由平台承担。"
    },
    {
      "n": 8,
      "chunk_id": "1736",
      "section_path": "售后手册/维修寄修流程",
      "question": "维修寄修流程",
      "answer": "保修期内设备故障,联系客服登记后按指引将设备寄回指定维修点,核验后免费维修并寄回;超保或人为损坏维修可能收取工本费,费用会提前告知。"
    },
    {
      "n": 6,
      "chunk_id": "1769",
      "section_path": "退货退款政策/退换货运费承担",
      "question": "退换货运费承担",
      "answer": "无理由退货的退回运费由买家承担;因商品质量问题、发错货、少发漏发导致的退换货,运费由平台承担。运费承担以平台售后规则最终判定为准。"
    },
    {
      "n": 4,
      "chunk_id": "1768",
      "section_path": "退货退款政策/换货政策/换货运费",
      "question": "换货运费",
      "answer": "非质量问题的换货,往返运费由买家承担;因质量问题或发错货的换货,往返运费由平台承担。"
    },
    {
      "n": 2,
      "chunk_id": "1777",
      "section_path": "积分规则/积分怎么用",
      "question": "积分怎么用",
      "answer": "积分可在结算时抵扣商品金额，100 积分抵 1 元现金，单笔订单最多抵 30 元，不用于抵扣偏远地区附加运费，也不支持直接提现。\n\n2000 积分可兑换自动饮水机滤芯 3 片，该兑换套装适用于 MH-W40，普通配送地区包邮；偏远地区附加配送费仍需按页面规则确认。MH-W40 的滤芯更换周期以商品规格手册为准。\n\n800 积分可兑换猫零食小样，普通配送地区另收 6 元运费；该兑换不直接套用普通购物订单的满 99 元包邮规则。兑换商品、可用库存及偏远地区配送规则以兑换页面标注为准。"
    }
  ],
  "decision": {
    "useful": true,
    "reason": "有运费规则：满99元包邮，未满收10元，偏远地区另计",
    "response_kind": "knowledge",
    "source": null
  },
  "answer": "您好！根据平台运费规则 [1]：\n\n- **单笔订单满 99 元**：包邮，无需支付邮费\n- **单笔订单未满 99 元**：收取 **10 元** 运费\n- **偏远地区**（如新疆、西藏、内蒙古等）：运费另计 [1]\n\n您可以告诉我订单金额或所在地区，我帮您确认具体邮费～",
  "point_verdicts": null,
  "claim_verdicts": null,
  "metrics": {
    "recall_at_5": 1.0,
    "recall_at_10": 1.0,
    "mrr_at_10": 1.0,
    "all_groups_hit_at_5": 1.0,
    "all_groups_hit_at_10": 1.0,
    "candidate_group_coverage": 1.0,
    "prompt_group_coverage": 1.0,
    "answer_point_coverage": null,
    "faithfulness": null,
    "absent_refusal_rate": null,
    "answerable_false_refusal_rate": 0.0
  },
  "error": {
    "code": "judgment_error",
    "type": "JudgeError",
    "message": "该阶段执行失败"
  },
  "elapsed_ms": 40749.28979994729,
  "judge_snapshot": {
    "prompt_version": "joint-generation-v2.1",
    "finish_reason": "length"
  },
  "audit": {
    "audit_version": 1,
    "source_map_id": "378ae65f4ee735c6a8079070fbfcb5c21800c93f3318029e5f19836c32b5c2b4",
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
        "chunk_id": 1742,
        "score": 0.7382994890213013,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1777,
        "score": 0.5854857563972473,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1751,
        "score": 0.5740665793418884,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1768,
        "score": 0.5732718706130981,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1776,
        "score": 0.5652116537094116,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1769,
        "score": 0.5583927631378174,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1747,
        "score": 0.5497187972068787,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1736,
        "score": 0.5388888716697693,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1745,
        "score": 0.526046097278595,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1771,
        "score": 0.5258296728134155,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1743,
        "score": 0.5228790044784546,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1774,
        "score": 0.5201632976531982,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1737,
        "score": 0.5191847085952759,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1770,
        "score": 0.5091904997825623,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1778,
        "score": 0.49782317876815796,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1750,
        "score": 0.4867149889469147,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1775,
        "score": 0.4850778579711914,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1731,
        "score": 0.48189276456832886,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1741,
        "score": 0.48042619228363037,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1779,
        "score": 0.4783916771411896,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1773,
        "score": 0.4753093123435974,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1744,
        "score": 0.4640308618545532,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1740,
        "score": 0.4589749574661255,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1767,
        "score": 0.44827258586883545,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1753,
        "score": 0.443782776594162,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1765,
        "score": 0.4429931640625,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1754,
        "score": 0.43872278928756714,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1732,
        "score": 0.43656039237976074,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1748,
        "score": 0.4322296977043152,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1746,
        "score": 0.4301239252090454,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1739,
        "score": 0.42482614517211914,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1758,
        "score": 0.4232899844646454,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1738,
        "score": 0.4230842590332031,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1755,
        "score": 0.4222627580165863,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1757,
        "score": 0.4219229221343994,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1762,
        "score": 0.41633695363998413,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1766,
        "score": 0.41621994972229004,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1735,
        "score": 0.4151606261730194,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1749,
        "score": 0.4088750183582306,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1756,
        "score": 0.4074590802192688,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1763,
        "score": 0.4067741632461548,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1761,
        "score": 0.4041818380355835,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1760,
        "score": 0.3981715440750122,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1733,
        "score": 0.3978709578514099,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1759,
        "score": 0.3946291208267212,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1772,
        "score": 0.39055776596069336,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1734,
        "score": 0.38612908124923706,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1752,
        "score": 0.3684488534927368,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1764,
        "score": 0.34877973794937134,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1780,
        "score": 0.332719624042511,
        "score_kind": "cosine"
      }
    ],
    "final_ranking": [
      {
        "chunk_id": 1742,
        "score": 0.7382994890213013,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1777,
        "score": 0.5854857563972473,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1751,
        "score": 0.5740665793418884,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1768,
        "score": 0.5732718706130981,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1776,
        "score": 0.5652116537094116,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1769,
        "score": 0.5583927631378174,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1747,
        "score": 0.5497187972068787,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1736,
        "score": 0.5388888716697693,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1745,
        "score": 0.526046097278595,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1771,
        "score": 0.5258296728134155,
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
  "status": "judge_error",
  "stage": "judgment",
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
          1742
        ]
      ]
    }
  ],
  "candidate_ids": [
    1742
  ],
  "final_ids": [
    1742
  ],
  "prompt_citations": [
    {
      "n": 1,
      "chunk_id": "1742",
      "section_path": "商品与购物 FAQ/运费怎么算",
      "question": "运费怎么算",
      "answer": "单笔订单满 99 元包邮,未满收取 10 元运费,偏远地区运费另计。邮费即运费,按此规则收取。"
    }
  ],
  "decision": {
    "useful": true,
    "reason": "运费规则直接匹配",
    "response_kind": "knowledge",
    "source": null
  },
  "answer": "您好，根据商家运费规则：单笔订单满 99 元包邮；未满 99 元收取 10 元运费；偏远地区运费另计 [1]。\n\n如果您方便提供订单号或订单金额，我可以帮您进一步确认哦。",
  "point_verdicts": null,
  "claim_verdicts": null,
  "metrics": {
    "recall_at_5": 1.0,
    "recall_at_10": 1.0,
    "mrr_at_10": 1.0,
    "all_groups_hit_at_5": 1.0,
    "all_groups_hit_at_10": 1.0,
    "candidate_group_coverage": 1.0,
    "prompt_group_coverage": 1.0,
    "answer_point_coverage": null,
    "faithfulness": null,
    "absent_refusal_rate": null,
    "answerable_false_refusal_rate": 0.0
  },
  "error": {
    "code": "judgment_error",
    "type": "JudgeError",
    "message": "该阶段执行失败"
  },
  "elapsed_ms": 60409.03010009788,
  "judge_snapshot": {
    "prompt_version": "joint-generation-v2.1",
    "finish_reason": "length"
  },
  "audit": {
    "audit_version": 1,
    "source_map_id": "378ae65f4ee735c6a8079070fbfcb5c21800c93f3318029e5f19836c32b5c2b4",
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
        "chunk_id": 1742,
        "score": 4.1900835037231445,
        "score_kind": "bm25"
      }
    ],
    "final_ranking": [
      {
        "chunk_id": 1742,
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
  "status": "judge_error",
  "stage": "judgment",
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
          1742
        ]
      ]
    }
  ],
  "candidate_ids": [
    1742,
    1777,
    1751,
    1768,
    1776,
    1769,
    1747,
    1736,
    1745,
    1771,
    1743,
    1774,
    1737,
    1770,
    1778,
    1750,
    1775,
    1731,
    1741,
    1779,
    1773,
    1744,
    1740,
    1767,
    1753,
    1765,
    1754,
    1732,
    1748,
    1746,
    1739,
    1758,
    1738,
    1755,
    1757,
    1762,
    1766,
    1735,
    1749,
    1756,
    1763,
    1761,
    1760,
    1733,
    1759,
    1772,
    1734,
    1752,
    1764,
    1780
  ],
  "final_ids": [
    1742,
    1777,
    1751,
    1768,
    1776,
    1769,
    1747,
    1736,
    1745,
    1771
  ],
  "prompt_citations": [
    {
      "n": 1,
      "chunk_id": "1742",
      "section_path": "商品与购物 FAQ/运费怎么算",
      "question": "运费怎么算",
      "answer": "单笔订单满 99 元包邮,未满收取 10 元运费,偏远地区运费另计。邮费即运费,按此规则收取。"
    },
    {
      "n": 3,
      "chunk_id": "1751",
      "section_path": "商品与购物 FAQ/会员运费权益",
      "question": "会员运费权益",
      "answer": "金卡会员每月享 3 次免运费权益,银卡会员享 1 次;权益不与偏远地区附加运费冲抵,当月未用完不结转。"
    },
    {
      "n": 5,
      "chunk_id": "1776",
      "section_path": "积分规则/积分怎么攒",
      "question": "积分怎么攒",
      "answer": "已完成订单每实际支付 1 元商品金额累计 1 积分，不计配送费；退款后按对应商品金额同步扣回积分。活动期间的双倍积分属于额外积分奖励，不计入会员等级升级；会员等级仍按有效累计消费金额计算。"
    },
    {
      "n": 7,
      "chunk_id": "1747",
      "section_path": "商品与购物 FAQ/配送范围与偏远地区",
      "question": "配送范围与偏远地区",
      "answer": "全国大部分地区支持配送,新疆、西藏、内蒙古等偏远地区运费另计且时效顺延;港澳台及海外暂不支持自营配送。"
    },
    {
      "n": 9,
      "chunk_id": "1745",
      "section_path": "商品与购物 FAQ/会员等级与积分规则",
      "question": "会员等级与积分规则",
      "answer": "会员分为普通、银卡、金卡三档,按累计消费自动升级。每消费 1 元得 1 积分,积分可在结算时抵扣,100 积分抵 1 元。"
    },
    {
      "n": 10,
      "chunk_id": "1771",
      "section_path": "退货退款政策/运输破损处理",
      "question": "运输破损处理",
      "answer": "商品运输途中破损的,请在签收后 48 小时内联系客服并提供开箱视频与照片,核实后可免费补发或退款,相关运费由平台承担。"
    },
    {
      "n": 8,
      "chunk_id": "1736",
      "section_path": "售后手册/维修寄修流程",
      "question": "维修寄修流程",
      "answer": "保修期内设备故障,联系客服登记后按指引将设备寄回指定维修点,核验后免费维修并寄回;超保或人为损坏维修可能收取工本费,费用会提前告知。"
    },
    {
      "n": 6,
      "chunk_id": "1769",
      "section_path": "退货退款政策/退换货运费承担",
      "question": "退换货运费承担",
      "answer": "无理由退货的退回运费由买家承担;因商品质量问题、发错货、少发漏发导致的退换货,运费由平台承担。运费承担以平台售后规则最终判定为准。"
    },
    {
      "n": 4,
      "chunk_id": "1768",
      "section_path": "退货退款政策/换货政策/换货运费",
      "question": "换货运费",
      "answer": "非质量问题的换货,往返运费由买家承担;因质量问题或发错货的换货,往返运费由平台承担。"
    },
    {
      "n": 2,
      "chunk_id": "1777",
      "section_path": "积分规则/积分怎么用",
      "question": "积分怎么用",
      "answer": "积分可在结算时抵扣商品金额，100 积分抵 1 元现金，单笔订单最多抵 30 元，不用于抵扣偏远地区附加运费，也不支持直接提现。\n\n2000 积分可兑换自动饮水机滤芯 3 片，该兑换套装适用于 MH-W40，普通配送地区包邮；偏远地区附加配送费仍需按页面规则确认。MH-W40 的滤芯更换周期以商品规格手册为准。\n\n800 积分可兑换猫零食小样，普通配送地区另收 6 元运费；该兑换不直接套用普通购物订单的满 99 元包邮规则。兑换商品、可用库存及偏远地区配送规则以兑换页面标注为准。"
    }
  ],
  "decision": {
    "useful": true,
    "reason": "运费规则证据直接覆盖",
    "response_kind": "knowledge",
    "source": null
  },
  "answer": "您好！邮费标准如下[1]：\n\n- **单笔订单满 99 元：免运费**\n- **未满 99 元：收取 10 元运费**\n- **偏远地区**（如新疆、西藏、内蒙古等）：运费另计，时效也会顺延[7]\n\n另外提示：金卡会员每月有 3 次免运费权益，银卡会员每月 1 次[3]。\n\n如果您方便告诉我订单金额或所在地区，我可以帮您进一步确认具体费用哦～",
  "point_verdicts": null,
  "claim_verdicts": null,
  "metrics": {
    "recall_at_5": 1.0,
    "recall_at_10": 1.0,
    "mrr_at_10": 1.0,
    "all_groups_hit_at_5": 1.0,
    "all_groups_hit_at_10": 1.0,
    "candidate_group_coverage": 1.0,
    "prompt_group_coverage": 1.0,
    "answer_point_coverage": null,
    "faithfulness": null,
    "absent_refusal_rate": null,
    "answerable_false_refusal_rate": 0.0
  },
  "error": {
    "code": "judgment_error",
    "type": "JudgeError",
    "message": "该阶段执行失败"
  },
  "elapsed_ms": 55656.65369993076,
  "judge_snapshot": {
    "prompt_version": "joint-generation-v2.1",
    "finish_reason": "length"
  },
  "audit": {
    "audit_version": 1,
    "source_map_id": "378ae65f4ee735c6a8079070fbfcb5c21800c93f3318029e5f19836c32b5c2b4",
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
        "chunk_id": 1742,
        "score": 0.032786883413791656,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1777,
        "score": 0.016129031777381897,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1751,
        "score": 0.01587301678955555,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1768,
        "score": 0.015625,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1776,
        "score": 0.015384615398943424,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1769,
        "score": 0.01515151560306549,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1747,
        "score": 0.014925372786819935,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1736,
        "score": 0.014705882407724857,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1745,
        "score": 0.014492753893136978,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1771,
        "score": 0.014285714365541935,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1743,
        "score": 0.014084506779909134,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1774,
        "score": 0.013888888992369175,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1737,
        "score": 0.013698630034923553,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1770,
        "score": 0.013513513840734959,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1778,
        "score": 0.013333333656191826,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1750,
        "score": 0.01315789483487606,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1775,
        "score": 0.012987012974917889,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1731,
        "score": 0.012820512987673283,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1741,
        "score": 0.012658228166401386,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1779,
        "score": 0.012500000186264515,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1773,
        "score": 0.012345679104328156,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1744,
        "score": 0.012195121496915817,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1740,
        "score": 0.012048192322254181,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1767,
        "score": 0.011904762126505375,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1753,
        "score": 0.0117647061124444,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1765,
        "score": 0.011627906933426857,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1754,
        "score": 0.01149425283074379,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1732,
        "score": 0.011363636702299118,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1748,
        "score": 0.01123595517128706,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1746,
        "score": 0.011111111380159855,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1739,
        "score": 0.010989011265337467,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1758,
        "score": 0.010869565419852734,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1738,
        "score": 0.01075268816202879,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1755,
        "score": 0.010638297535479069,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1757,
        "score": 0.010526316240429878,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1762,
        "score": 0.010416666977107525,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1766,
        "score": 0.010309278033673763,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1735,
        "score": 0.010204081423580647,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1749,
        "score": 0.010101010091602802,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1756,
        "score": 0.009999999776482582,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1763,
        "score": 0.009900989942252636,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1761,
        "score": 0.009803921915590763,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1760,
        "score": 0.009708737954497337,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1733,
        "score": 0.009615384973585606,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1759,
        "score": 0.009523809887468815,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1772,
        "score": 0.009433962404727936,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1734,
        "score": 0.009345794096589088,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1752,
        "score": 0.009259259328246117,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1764,
        "score": 0.00917431153357029,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1780,
        "score": 0.00909090880304575,
        "score_kind": "rrf"
      }
    ],
    "final_ranking": [
      {
        "chunk_id": 1742,
        "score": 0.032786883413791656,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1777,
        "score": 0.016129031777381897,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1751,
        "score": 0.01587301678955555,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1768,
        "score": 0.015625,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1776,
        "score": 0.015384615398943424,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1769,
        "score": 0.01515151560306549,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1747,
        "score": 0.014925372786819935,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1736,
        "score": 0.014705882407724857,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1745,
        "score": 0.014492753893136978,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1771,
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
  "status": "judge_error",
  "stage": "judgment",
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
          1742
        ]
      ]
    }
  ],
  "candidate_ids": [
    1742,
    1777,
    1751,
    1768,
    1776,
    1769,
    1747,
    1736,
    1745,
    1771,
    1743,
    1774,
    1737,
    1770,
    1778,
    1750,
    1775,
    1731,
    1741,
    1779,
    1773,
    1744,
    1740,
    1767,
    1753,
    1765,
    1754,
    1732,
    1748,
    1746,
    1739,
    1758,
    1738,
    1755,
    1757,
    1762,
    1766,
    1735,
    1749,
    1756,
    1763,
    1761,
    1760,
    1733,
    1759,
    1772,
    1734,
    1752,
    1764,
    1780
  ],
  "final_ids": [
    1742,
    1774,
    1776,
    1778,
    1777,
    1769,
    1751,
    1768,
    1737,
    1747
  ],
  "prompt_citations": [
    {
      "n": 1,
      "chunk_id": "1742",
      "section_path": "商品与购物 FAQ/运费怎么算",
      "question": "运费怎么算",
      "answer": "单笔订单满 99 元包邮,未满收取 10 元运费,偏远地区运费另计。邮费即运费,按此规则收取。"
    },
    {
      "n": 3,
      "chunk_id": "1776",
      "section_path": "积分规则/积分怎么攒",
      "question": "积分怎么攒",
      "answer": "已完成订单每实际支付 1 元商品金额累计 1 积分，不计配送费；退款后按对应商品金额同步扣回积分。活动期间的双倍积分属于额外积分奖励，不计入会员等级升级；会员等级仍按有效累计消费金额计算。"
    },
    {
      "n": 5,
      "chunk_id": "1777",
      "section_path": "积分规则/积分怎么用",
      "question": "积分怎么用",
      "answer": "积分可在结算时抵扣商品金额，100 积分抵 1 元现金，单笔订单最多抵 30 元，不用于抵扣偏远地区附加运费，也不支持直接提现。\n\n2000 积分可兑换自动饮水机滤芯 3 片，该兑换套装适用于 MH-W40，普通配送地区包邮；偏远地区附加配送费仍需按页面规则确认。MH-W40 的滤芯更换周期以商品规格手册为准。\n\n800 积分可兑换猫零食小样，普通配送地区另收 6 元运费；该兑换不直接套用普通购物订单的满 99 元包邮规则。兑换商品、可用库存及偏远地区配送规则以兑换页面标注为准。"
    },
    {
      "n": 7,
      "chunk_id": "1751",
      "section_path": "商品与购物 FAQ/会员运费权益",
      "question": "会员运费权益",
      "answer": "金卡会员每月享 3 次免运费权益,银卡会员享 1 次;权益不与偏远地区附加运费冲抵,当月未用完不结转。"
    },
    {
      "n": 9,
      "chunk_id": "1737",
      "section_path": "售后手册/会员专属售后权益",
      "question": "会员专属售后权益",
      "answer": "金卡会员享优先客服接入与上门取件退换货;银卡会员享退换货运费权益 1 次/月。具体权益以会员中心页面标注为准。"
    },
    {
      "n": 10,
      "chunk_id": "1747",
      "section_path": "商品与购物 FAQ/配送范围与偏远地区",
      "question": "配送范围与偏远地区",
      "answer": "全国大部分地区支持配送,新疆、西藏、内蒙古等偏远地区运费另计且时效顺延;港澳台及海外暂不支持自营配送。"
    },
    {
      "n": 8,
      "chunk_id": "1768",
      "section_path": "退货退款政策/换货政策/换货运费",
      "question": "换货运费",
      "answer": "非质量问题的换货,往返运费由买家承担;因质量问题或发错货的换货,往返运费由平台承担。"
    },
    {
      "n": 6,
      "chunk_id": "1769",
      "section_path": "退货退款政策/退换货运费承担",
      "question": "退换货运费承担",
      "answer": "无理由退货的退回运费由买家承担;因商品质量问题、发错货、少发漏发导致的退换货,运费由平台承担。运费承担以平台售后规则最终判定为准。"
    },
    {
      "n": 4,
      "chunk_id": "1778",
      "section_path": "开票细则/可开票类型",
      "question": "可开票类型",
      "answer": "本演示店提供电子普通发票、电子专用发票和纸质专用发票。电子普通发票可按订单申请；电子专票需要企业账户，申请前准备发票抬头及有效纳税人识别号，按申请页面提交资料。\n\n纸质专票仅企业账户可申请，申请时需提供企业开票资料、收件人和邮寄地址，快递费到付。资料审核通过后按开票流程寄出，不承诺快递送达日期。"
    },
    {
      "n": 2,
      "chunk_id": "1774",
      "section_path": "会员权益/会员等级",
      "question": "会员等级",
      "answer": "会员分为普通、银卡和金卡三档，按有效累计消费金额自动升级，不按年度消费金额计算。累计消费未满 1000 元为普通会员，满 1000 元起为银卡，满 5000 元起为金卡。\n\n有效累计消费指已完成订单的商品实际支付金额，不含配送费；退货退款部分从有效累计消费中扣除。退款后根据更新的累计消费重新计算等级，未达到原门槛时可能降级。等级与适用权益在会员中心展示。\n\n银卡在参与会员折扣的商品上享 95 折，金卡享 9 折。折扣适用商品和活动范围以结算页面标注为准。会员折扣、优惠券与满减是否叠加也以当次活动页面为准，不能一概承诺全部优惠同时生效。"
    }
  ],
  "decision": {
    "useful": true,
    "reason": "运费规则已覆盖满99包邮未满10元及偏远地区另计",
    "response_kind": "knowledge",
    "source": null
  },
  "answer": "您好，邮费标准如下：单笔订单满 99 元包邮，未满 99 元收取 10 元运费；新疆、西藏、内蒙古等偏远地区运费另计[1]。\n\n请问您的订单金额是多少？或者您想查询具体订单的运费，可以提供订单号，我帮您确认~",
  "point_verdicts": null,
  "claim_verdicts": null,
  "metrics": {
    "recall_at_5": 1.0,
    "recall_at_10": 1.0,
    "mrr_at_10": 1.0,
    "all_groups_hit_at_5": 1.0,
    "all_groups_hit_at_10": 1.0,
    "candidate_group_coverage": 1.0,
    "prompt_group_coverage": 1.0,
    "answer_point_coverage": null,
    "faithfulness": null,
    "absent_refusal_rate": null,
    "answerable_false_refusal_rate": 0.0
  },
  "error": {
    "code": "judgment_error",
    "type": "JudgeError",
    "message": "该阶段执行失败"
  },
  "elapsed_ms": 44301.22989998199,
  "judge_snapshot": {
    "prompt_version": "joint-generation-v2.1",
    "finish_reason": "length"
  },
  "audit": {
    "audit_version": 1,
    "source_map_id": "378ae65f4ee735c6a8079070fbfcb5c21800c93f3318029e5f19836c32b5c2b4",
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
        "chunk_id": 1742,
        "score": 0.032786883413791656,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1777,
        "score": 0.016129031777381897,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1751,
        "score": 0.01587301678955555,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1768,
        "score": 0.015625,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1776,
        "score": 0.015384615398943424,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1769,
        "score": 0.01515151560306549,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1747,
        "score": 0.014925372786819935,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1736,
        "score": 0.014705882407724857,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1745,
        "score": 0.014492753893136978,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1771,
        "score": 0.014285714365541935,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1743,
        "score": 0.014084506779909134,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1774,
        "score": 0.013888888992369175,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1737,
        "score": 0.013698630034923553,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1770,
        "score": 0.013513513840734959,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1778,
        "score": 0.013333333656191826,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1750,
        "score": 0.01315789483487606,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1775,
        "score": 0.012987012974917889,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1731,
        "score": 0.012820512987673283,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1741,
        "score": 0.012658228166401386,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1779,
        "score": 0.012500000186264515,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1773,
        "score": 0.012345679104328156,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1744,
        "score": 0.012195121496915817,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1740,
        "score": 0.012048192322254181,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1767,
        "score": 0.011904762126505375,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1753,
        "score": 0.0117647061124444,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1765,
        "score": 0.011627906933426857,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1754,
        "score": 0.01149425283074379,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1732,
        "score": 0.011363636702299118,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1748,
        "score": 0.01123595517128706,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1746,
        "score": 0.011111111380159855,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1739,
        "score": 0.010989011265337467,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1758,
        "score": 0.010869565419852734,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1738,
        "score": 0.01075268816202879,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1755,
        "score": 0.010638297535479069,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1757,
        "score": 0.010526316240429878,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1762,
        "score": 0.010416666977107525,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1766,
        "score": 0.010309278033673763,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1735,
        "score": 0.010204081423580647,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1749,
        "score": 0.010101010091602802,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1756,
        "score": 0.009999999776482582,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1763,
        "score": 0.009900989942252636,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1761,
        "score": 0.009803921915590763,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1760,
        "score": 0.009708737954497337,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1733,
        "score": 0.009615384973585606,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1759,
        "score": 0.009523809887468815,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1772,
        "score": 0.009433962404727936,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1734,
        "score": 0.009345794096589088,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1752,
        "score": 0.009259259328246117,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1764,
        "score": 0.00917431153357029,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1780,
        "score": 0.00909090880304575,
        "score_kind": "rrf"
      }
    ],
    "final_ranking": [
      {
        "chunk_id": 1742,
        "score": 0.42253774404525757,
        "score_kind": "rerank"
      },
      {
        "chunk_id": 1774,
        "score": 0.0025972246658056974,
        "score_kind": "rerank"
      },
      {
        "chunk_id": 1776,
        "score": 0.0022758350241929293,
        "score_kind": "rerank"
      },
      {
        "chunk_id": 1778,
        "score": 0.0021258187480270863,
        "score_kind": "rerank"
      },
      {
        "chunk_id": 1777,
        "score": 0.0021101937163621187,
        "score_kind": "rerank"
      },
      {
        "chunk_id": 1769,
        "score": 0.0017548224423080683,
        "score_kind": "rerank"
      },
      {
        "chunk_id": 1751,
        "score": 0.0016951002180576324,
        "score_kind": "rerank"
      },
      {
        "chunk_id": 1768,
        "score": 0.000958225573413074,
        "score_kind": "rerank"
      },
      {
        "chunk_id": 1737,
        "score": 0.0008439415832981467,
        "score_kind": "rerank"
      },
      {
        "chunk_id": 1747,
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
  "status": "judge_error",
  "stage": "judgment",
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
          1734
        ]
      ]
    }
  ],
  "candidate_ids": [
    1734,
    1762,
    1763,
    1760,
    1733,
    1753,
    1761,
    1749,
    1755,
    1736,
    1731,
    1777,
    1771,
    1744,
    1747,
    1772,
    1758,
    1775,
    1754,
    1759,
    1735,
    1780,
    1756,
    1757,
    1776,
    1779,
    1740,
    1773,
    1767,
    1750,
    1746,
    1748,
    1739,
    1768,
    1741,
    1745,
    1752,
    1751,
    1737,
    1765,
    1738,
    1770,
    1778,
    1743,
    1766,
    1764,
    1769,
    1742,
    1774,
    1732
  ],
  "final_ids": [
    1734,
    1762,
    1763,
    1760,
    1733,
    1753,
    1761,
    1749,
    1755,
    1736
  ],
  "prompt_citations": [
    {
      "n": 1,
      "chunk_id": "1734",
      "section_path": "售后手册/常见故障自查",
      "question": "常见故障自查",
      "answer": "- 饮水机不出水:检查水位是否低于最低线、水泵是否卡阻,断电清洗水泵后重试。\n- 猫砂盆报错:清空废砂盒并检查滚筒是否卡砂,重启设备;仍报错联系售后。\n- 喂食器卡粮:检查粮食颗粒直径是否超 12mm、粮桶是否受潮结块,清理出粮口后重试。\n- 摄像头离线:确认 Wi-Fi 为 2.4G 频段、信号良好,重启设备或在 App 内重新配网。"
    },
    {
      "n": 3,
      "chunk_id": "1763",
      "section_path": "商品规格手册/自动喂食器 摄像头版(型号 MH-FD30)",
      "question": "自动喂食器 摄像头版(型号 MH-FD30)",
      "answer": "- 型号:MH-FD30\n- 粮桶容量:6L\n- 核心功能:1080P 摄像头、双向语音、App 远程手动投喂与定时投喂\n- 供电:市电供电 + 内置应急电池\n- 说明:摄像头版支持视频回看,需连接 2.4G Wi-Fi"
    },
    {
      "n": 5,
      "chunk_id": "1733",
      "section_path": "售后手册/设备安装与激活",
      "question": "设备安装与激活",
      "answer": "智能设备首次使用需下载「喵喵优选」App,按说明书扫码添加设备并连接 2.4G Wi-Fi 完成激活;猫爬架等非联网商品按随附图解自行组装。"
    },
    {
      "n": 7,
      "chunk_id": "1761",
      "section_path": "商品规格手册/大号三档加热垫(型号 MH-HP20)",
      "question": "大号三档加热垫(型号 MH-HP20)",
      "answer": "- 型号:MH-HP20\n- 尺寸:60cm × 45cm\n- 温控:三档可调 30℃ / 38℃ / 45℃,内置过热保护与定时关机\n- 防护:防水防抓咬电线套管,表面绒布可拆洗\n- 适用:大型猫、多猫窝及冬季保暖"
    },
    {
      "n": 9,
      "chunk_id": "1755",
      "section_path": "商品规格手册/智能猫砂盆 Max(型号 MH-LP200)",
      "question": "智能猫砂盆 Max(型号 MH-LP200)",
      "answer": "- 型号:MH-LP200\n- 适用猫咪体重:2kg 至 12kg,适合大型猫与多猫家庭\n- 猫砂容量:12L,废砂盒容量约 10 天(单猫)\n- 核心功能:超大滚筒、双重称重防夹、活性炭除臭、App 多猫健康档案\n- 供电:220V 市电\n- 清理提示:多猫家庭建议每 3 至 5 天倾倒一次废砂盒"
    },
    {
      "n": 10,
      "chunk_id": "1736",
      "section_path": "售后手册/维修寄修流程",
      "question": "维修寄修流程",
      "answer": "保修期内设备故障,联系客服登记后按指引将设备寄回指定维修点,核验后免费维修并寄回;超保或人为损坏维修可能收取工本费,费用会提前告知。"
    },
    {
      "n": 8,
      "chunk_id": "1749",
      "section_path": "商品与购物 FAQ/商品缺货多久补货",
      "question": "商品缺货多久补货",
      "answer": "现货售罄的商品通常 3 至 7 天内补货,可在商品页点击「到货通知」,补货后系统会推送提醒。"
    },
    {
      "n": 6,
      "chunk_id": "1753",
      "section_path": "商品规格手册/智能猫砂盆 Pro(型号 MH-LP100)",
      "question": "智能猫砂盆 Pro(型号 MH-LP100)",
      "answer": "- 型号:MH-LP100\n- 适用猫咪体重:1.5kg 至 8kg\n- 猫砂容量:9L,废砂盒容量约 7 天(单猫)\n- 核心功能:自动感应清理、活性炭除臭、App 远程监控与健康记录\n- 供电:220V 市电,断电后配置自动保存\n- 清理提示:废砂盒满时 App 推送提醒,建议每 5 至 7 天倾倒一次"
    },
    {
      "n": 4,
      "chunk_id": "1760",
      "section_path": "商品规格手册/恒温加热垫(型号 MH-HP12)",
      "question": "恒温加热垫(型号 MH-HP12)",
      "answer": "- 型号:MH-HP12\n- 尺寸:40cm × 30cm\n- 温控:恒温 38℃,内置过热保护,连续通电不超过 12 小时为宜\n- 防护:防水防抓咬电线套管\n- 适用:幼猫、老年猫及冬季保暖"
    },
    {
      "n": 2,
      "chunk_id": "1762",
      "section_path": "商品规格手册/自动喂食器 基础版(型号 MH-FD10)",
      "question": "自动喂食器 基础版(型号 MH-FD10)",
      "answer": "- 型号:MH-FD10\n- 粮桶容量:4L\n- 核心功能:定时定量投喂,每日最多 6 餐,语音呼唤进食\n- 供电:市电供电 + 4 节 5 号电池断电应急\n- 说明:基础版不含摄像头与 App 远程投喂"
    }
  ],
  "decision": {
    "useful": true,
    "reason": "有喂食器卡粮排查方案",
    "response_kind": "knowledge",
    "source": null
  },
  "answer": "您好，喂食器卡粮不下粮可以先这样自查[1]：\n\n1. **检查粮粒大小**：确认粮食颗粒直径是否超过 12mm，超了容易卡住出粮口；\n2. **检查粮桶是否受潮结块**：受潮的粮会粘在桶内或出粮口，造成不下粮；\n3. **清理出粮口**：清掉卡住的粮粒或结块后，重新开机试一下。\n\n如果按上面操作后仍然卡粮，麻烦您联系我们，我可以帮您登记人工工单，由售后同事跟进处理（工单为待处理状态，不代表已完成维修或退换）。\n\n请问还需要帮您做其他什么吗？",
  "point_verdicts": null,
  "claim_verdicts": null,
  "metrics": {
    "recall_at_5": 1.0,
    "recall_at_10": 1.0,
    "mrr_at_10": 1.0,
    "all_groups_hit_at_5": 1.0,
    "all_groups_hit_at_10": 1.0,
    "candidate_group_coverage": 1.0,
    "prompt_group_coverage": 1.0,
    "answer_point_coverage": null,
    "faithfulness": null,
    "absent_refusal_rate": null,
    "answerable_false_refusal_rate": 0.0
  },
  "error": {
    "code": "judgment_error",
    "type": "JudgeError",
    "message": "该阶段执行失败"
  },
  "elapsed_ms": 53111.23110004701,
  "judge_snapshot": {
    "prompt_version": "joint-generation-v2.1",
    "finish_reason": "length"
  },
  "audit": {
    "audit_version": 1,
    "source_map_id": "378ae65f4ee735c6a8079070fbfcb5c21800c93f3318029e5f19836c32b5c2b4",
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
        "chunk_id": 1734,
        "score": 0.5772529244422913,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1762,
        "score": 0.5686611533164978,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1763,
        "score": 0.5518475770950317,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1760,
        "score": 0.44198256731033325,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1733,
        "score": 0.4325045645236969,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1753,
        "score": 0.43056777119636536,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1761,
        "score": 0.42521214485168457,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1749,
        "score": 0.42119717597961426,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1755,
        "score": 0.4198179244995117,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1736,
        "score": 0.4171714782714844,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1731,
        "score": 0.41137444972991943,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1777,
        "score": 0.4087750017642975,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1771,
        "score": 0.4039039611816406,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1744,
        "score": 0.40205860137939453,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1747,
        "score": 0.4005569815635681,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1772,
        "score": 0.3999122977256775,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1758,
        "score": 0.39986157417297363,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1775,
        "score": 0.39875853061676025,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1754,
        "score": 0.39636391401290894,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1759,
        "score": 0.39284366369247437,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1735,
        "score": 0.39167726039886475,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1780,
        "score": 0.3914699852466583,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1756,
        "score": 0.3909645080566406,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1757,
        "score": 0.3907371163368225,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1776,
        "score": 0.39067864418029785,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1779,
        "score": 0.380906879901886,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1740,
        "score": 0.3758910298347473,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1773,
        "score": 0.37542933225631714,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1767,
        "score": 0.3736211657524109,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1750,
        "score": 0.37022215127944946,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1746,
        "score": 0.3654598295688629,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1748,
        "score": 0.36215317249298096,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1739,
        "score": 0.3583248555660248,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1768,
        "score": 0.3569454550743103,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1741,
        "score": 0.3557622730731964,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1745,
        "score": 0.3545067012310028,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1752,
        "score": 0.35218995809555054,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1751,
        "score": 0.3514851927757263,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1737,
        "score": 0.34910643100738525,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1765,
        "score": 0.3463781476020813,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1738,
        "score": 0.3463031053543091,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1770,
        "score": 0.34517526626586914,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1778,
        "score": 0.3429110050201416,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1743,
        "score": 0.3407789468765259,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1766,
        "score": 0.33719661831855774,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1764,
        "score": 0.33142441511154175,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1769,
        "score": 0.3235948383808136,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1742,
        "score": 0.3220908045768738,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1774,
        "score": 0.3201596736907959,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1732,
        "score": 0.31397026777267456,
        "score_kind": "cosine"
      }
    ],
    "final_ranking": [
      {
        "chunk_id": 1734,
        "score": 0.5772529244422913,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1762,
        "score": 0.5686611533164978,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1763,
        "score": 0.5518475770950317,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1760,
        "score": 0.44198256731033325,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1733,
        "score": 0.4325045645236969,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1753,
        "score": 0.43056777119636536,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1761,
        "score": 0.42521214485168457,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1749,
        "score": 0.42119717597961426,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1755,
        "score": 0.4198179244995117,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1736,
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
  "status": "judge_error",
  "stage": "judgment",
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
          1734
        ]
      ]
    }
  ],
  "candidate_ids": [
    1762,
    1763,
    1734
  ],
  "final_ids": [
    1762,
    1763,
    1734
  ],
  "prompt_citations": [
    {
      "n": 1,
      "chunk_id": "1762",
      "section_path": "商品规格手册/自动喂食器 基础版(型号 MH-FD10)",
      "question": "自动喂食器 基础版(型号 MH-FD10)",
      "answer": "- 型号:MH-FD10\n- 粮桶容量:4L\n- 核心功能:定时定量投喂,每日最多 6 餐,语音呼唤进食\n- 供电:市电供电 + 4 节 5 号电池断电应急\n- 说明:基础版不含摄像头与 App 远程投喂"
    },
    {
      "n": 3,
      "chunk_id": "1734",
      "section_path": "售后手册/常见故障自查",
      "question": "常见故障自查",
      "answer": "- 饮水机不出水:检查水位是否低于最低线、水泵是否卡阻,断电清洗水泵后重试。\n- 猫砂盆报错:清空废砂盒并检查滚筒是否卡砂,重启设备;仍报错联系售后。\n- 喂食器卡粮:检查粮食颗粒直径是否超 12mm、粮桶是否受潮结块,清理出粮口后重试。\n- 摄像头离线:确认 Wi-Fi 为 2.4G 频段、信号良好,重启设备或在 App 内重新配网。"
    },
    {
      "n": 2,
      "chunk_id": "1763",
      "section_path": "商品规格手册/自动喂食器 摄像头版(型号 MH-FD30)",
      "question": "自动喂食器 摄像头版(型号 MH-FD30)",
      "answer": "- 型号:MH-FD30\n- 粮桶容量:6L\n- 核心功能:1080P 摄像头、双向语音、App 远程手动投喂与定时投喂\n- 供电:市电供电 + 内置应急电池\n- 说明:摄像头版支持视频回看,需连接 2.4G Wi-Fi"
    }
  ],
  "decision": {
    "useful": true,
    "reason": "含喂食器卡粮处理方法",
    "response_kind": "knowledge",
    "source": null
  },
  "answer": "您好~喂食器堵粮可以按这个方法自查[3]：\n\n1. **检查粮粒大小**：确认粮食颗粒直径是否超过 12mm，超了容易卡粮[3]；\n2. **检查粮桶**：看粮食是否受潮结块，结块粮请更换干燥的粮[3]；\n3. **清理出粮口**：清理干净出粮口后重新试机[3]。\n\n如果按以上步骤处理后仍然卡粮，建议联系售后进一步处理哦~",
  "point_verdicts": null,
  "claim_verdicts": null,
  "metrics": {
    "recall_at_5": 1.0,
    "recall_at_10": 1.0,
    "mrr_at_10": 0.3333333333333333,
    "all_groups_hit_at_5": 1.0,
    "all_groups_hit_at_10": 1.0,
    "candidate_group_coverage": 1.0,
    "prompt_group_coverage": 1.0,
    "answer_point_coverage": null,
    "faithfulness": null,
    "absent_refusal_rate": null,
    "answerable_false_refusal_rate": 0.0
  },
  "error": {
    "code": "judgment_error",
    "type": "JudgeError",
    "message": "该阶段执行失败"
  },
  "elapsed_ms": 51707.715100143105,
  "judge_snapshot": {
    "prompt_version": "joint-generation-v2.1",
    "finish_reason": "length"
  },
  "audit": {
    "audit_version": 1,
    "source_map_id": "378ae65f4ee735c6a8079070fbfcb5c21800c93f3318029e5f19836c32b5c2b4",
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
        "chunk_id": 1762,
        "score": 2.582362174987793,
        "score_kind": "bm25"
      },
      {
        "chunk_id": 1763,
        "score": 2.525158166885376,
        "score_kind": "bm25"
      },
      {
        "chunk_id": 1734,
        "score": 2.158566951751709,
        "score_kind": "bm25"
      }
    ],
    "final_ranking": [
      {
        "chunk_id": 1762,
        "score": 2.582362174987793,
        "score_kind": "bm25"
      },
      {
        "chunk_id": 1763,
        "score": 2.525158166885376,
        "score_kind": "bm25"
      },
      {
        "chunk_id": 1734,
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
  "status": "judge_error",
  "stage": "judgment",
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
          1734
        ]
      ]
    }
  ],
  "candidate_ids": [
    1762,
    1734,
    1763,
    1760,
    1733,
    1753,
    1761,
    1749,
    1755,
    1736,
    1731,
    1777,
    1771,
    1744,
    1747,
    1772,
    1758,
    1775,
    1754,
    1759,
    1735,
    1780,
    1756,
    1757,
    1776,
    1779,
    1740,
    1773,
    1767,
    1750,
    1746,
    1748,
    1739,
    1768,
    1741,
    1745,
    1752,
    1751,
    1737,
    1765,
    1738,
    1770,
    1778,
    1743,
    1766,
    1764,
    1769,
    1742,
    1774,
    1732
  ],
  "final_ids": [
    1762,
    1734,
    1763,
    1760,
    1733,
    1753,
    1761,
    1749,
    1755,
    1736
  ],
  "prompt_citations": [
    {
      "n": 1,
      "chunk_id": "1762",
      "section_path": "商品规格手册/自动喂食器 基础版(型号 MH-FD10)",
      "question": "自动喂食器 基础版(型号 MH-FD10)",
      "answer": "- 型号:MH-FD10\n- 粮桶容量:4L\n- 核心功能:定时定量投喂,每日最多 6 餐,语音呼唤进食\n- 供电:市电供电 + 4 节 5 号电池断电应急\n- 说明:基础版不含摄像头与 App 远程投喂"
    },
    {
      "n": 3,
      "chunk_id": "1763",
      "section_path": "商品规格手册/自动喂食器 摄像头版(型号 MH-FD30)",
      "question": "自动喂食器 摄像头版(型号 MH-FD30)",
      "answer": "- 型号:MH-FD30\n- 粮桶容量:6L\n- 核心功能:1080P 摄像头、双向语音、App 远程手动投喂与定时投喂\n- 供电:市电供电 + 内置应急电池\n- 说明:摄像头版支持视频回看,需连接 2.4G Wi-Fi"
    },
    {
      "n": 5,
      "chunk_id": "1733",
      "section_path": "售后手册/设备安装与激活",
      "question": "设备安装与激活",
      "answer": "智能设备首次使用需下载「喵喵优选」App,按说明书扫码添加设备并连接 2.4G Wi-Fi 完成激活;猫爬架等非联网商品按随附图解自行组装。"
    },
    {
      "n": 7,
      "chunk_id": "1761",
      "section_path": "商品规格手册/大号三档加热垫(型号 MH-HP20)",
      "question": "大号三档加热垫(型号 MH-HP20)",
      "answer": "- 型号:MH-HP20\n- 尺寸:60cm × 45cm\n- 温控:三档可调 30℃ / 38℃ / 45℃,内置过热保护与定时关机\n- 防护:防水防抓咬电线套管,表面绒布可拆洗\n- 适用:大型猫、多猫窝及冬季保暖"
    },
    {
      "n": 9,
      "chunk_id": "1755",
      "section_path": "商品规格手册/智能猫砂盆 Max(型号 MH-LP200)",
      "question": "智能猫砂盆 Max(型号 MH-LP200)",
      "answer": "- 型号:MH-LP200\n- 适用猫咪体重:2kg 至 12kg,适合大型猫与多猫家庭\n- 猫砂容量:12L,废砂盒容量约 10 天(单猫)\n- 核心功能:超大滚筒、双重称重防夹、活性炭除臭、App 多猫健康档案\n- 供电:220V 市电\n- 清理提示:多猫家庭建议每 3 至 5 天倾倒一次废砂盒"
    },
    {
      "n": 10,
      "chunk_id": "1736",
      "section_path": "售后手册/维修寄修流程",
      "question": "维修寄修流程",
      "answer": "保修期内设备故障,联系客服登记后按指引将设备寄回指定维修点,核验后免费维修并寄回;超保或人为损坏维修可能收取工本费,费用会提前告知。"
    },
    {
      "n": 8,
      "chunk_id": "1749",
      "section_path": "商品与购物 FAQ/商品缺货多久补货",
      "question": "商品缺货多久补货",
      "answer": "现货售罄的商品通常 3 至 7 天内补货,可在商品页点击「到货通知」,补货后系统会推送提醒。"
    },
    {
      "n": 6,
      "chunk_id": "1753",
      "section_path": "商品规格手册/智能猫砂盆 Pro(型号 MH-LP100)",
      "question": "智能猫砂盆 Pro(型号 MH-LP100)",
      "answer": "- 型号:MH-LP100\n- 适用猫咪体重:1.5kg 至 8kg\n- 猫砂容量:9L,废砂盒容量约 7 天(单猫)\n- 核心功能:自动感应清理、活性炭除臭、App 远程监控与健康记录\n- 供电:220V 市电,断电后配置自动保存\n- 清理提示:废砂盒满时 App 推送提醒,建议每 5 至 7 天倾倒一次"
    },
    {
      "n": 4,
      "chunk_id": "1760",
      "section_path": "商品规格手册/恒温加热垫(型号 MH-HP12)",
      "question": "恒温加热垫(型号 MH-HP12)",
      "answer": "- 型号:MH-HP12\n- 尺寸:40cm × 30cm\n- 温控:恒温 38℃,内置过热保护,连续通电不超过 12 小时为宜\n- 防护:防水防抓咬电线套管\n- 适用:幼猫、老年猫及冬季保暖"
    },
    {
      "n": 2,
      "chunk_id": "1734",
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
  "answer": "您好！关于喂食器卡粮不下粮的问题，可以按以下方法自查[2]：\n\n1. 检查粮食颗粒直径是否超过 12mm，过大的颗粒容易卡住；\n2. 检查粮桶里的粮是否受潮结块，如有请更换干燥的粮食；\n3. 清理出粮口后重试。\n\n如果按上述方法处理后仍无法正常出粮，可能是设备故障，建议联系售后进一步处理[2]。请问还有其他可以帮您的吗？",
  "point_verdicts": null,
  "claim_verdicts": null,
  "metrics": {
    "recall_at_5": 1.0,
    "recall_at_10": 1.0,
    "mrr_at_10": 0.5,
    "all_groups_hit_at_5": 1.0,
    "all_groups_hit_at_10": 1.0,
    "candidate_group_coverage": 1.0,
    "prompt_group_coverage": 1.0,
    "answer_point_coverage": null,
    "faithfulness": null,
    "absent_refusal_rate": null,
    "answerable_false_refusal_rate": 0.0
  },
  "error": {
    "code": "judgment_error",
    "type": "JudgeError",
    "message": "该阶段执行失败"
  },
  "elapsed_ms": 52305.40100019425,
  "judge_snapshot": {
    "prompt_version": "joint-generation-v2.1",
    "finish_reason": "length"
  },
  "audit": {
    "audit_version": 1,
    "source_map_id": "378ae65f4ee735c6a8079070fbfcb5c21800c93f3318029e5f19836c32b5c2b4",
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
        "chunk_id": 1762,
        "score": 0.032522473484277725,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1734,
        "score": 0.03226646035909653,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1763,
        "score": 0.0320020467042923,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1760,
        "score": 0.015625,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1733,
        "score": 0.015384615398943424,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1753,
        "score": 0.01515151560306549,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1761,
        "score": 0.014925372786819935,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1749,
        "score": 0.014705882407724857,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1755,
        "score": 0.014492753893136978,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1736,
        "score": 0.014285714365541935,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1731,
        "score": 0.014084506779909134,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1777,
        "score": 0.013888888992369175,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1771,
        "score": 0.013698630034923553,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1744,
        "score": 0.013513513840734959,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1747,
        "score": 0.013333333656191826,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1772,
        "score": 0.01315789483487606,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1758,
        "score": 0.012987012974917889,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1775,
        "score": 0.012820512987673283,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1754,
        "score": 0.012658228166401386,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1759,
        "score": 0.012500000186264515,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1735,
        "score": 0.012345679104328156,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1780,
        "score": 0.012195121496915817,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1756,
        "score": 0.012048192322254181,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1757,
        "score": 0.011904762126505375,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1776,
        "score": 0.0117647061124444,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1779,
        "score": 0.011627906933426857,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1740,
        "score": 0.01149425283074379,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1773,
        "score": 0.011363636702299118,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1767,
        "score": 0.01123595517128706,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1750,
        "score": 0.011111111380159855,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1746,
        "score": 0.010989011265337467,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1748,
        "score": 0.010869565419852734,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1739,
        "score": 0.01075268816202879,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1768,
        "score": 0.010638297535479069,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1741,
        "score": 0.010526316240429878,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1745,
        "score": 0.010416666977107525,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1752,
        "score": 0.010309278033673763,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1751,
        "score": 0.010204081423580647,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1737,
        "score": 0.010101010091602802,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1765,
        "score": 0.009999999776482582,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1738,
        "score": 0.009900989942252636,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1770,
        "score": 0.009803921915590763,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1778,
        "score": 0.009708737954497337,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1743,
        "score": 0.009615384973585606,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1766,
        "score": 0.009523809887468815,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1764,
        "score": 0.009433962404727936,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1769,
        "score": 0.009345794096589088,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1742,
        "score": 0.009259259328246117,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1774,
        "score": 0.00917431153357029,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1732,
        "score": 0.00909090880304575,
        "score_kind": "rrf"
      }
    ],
    "final_ranking": [
      {
        "chunk_id": 1762,
        "score": 0.032522473484277725,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1734,
        "score": 0.03226646035909653,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1763,
        "score": 0.0320020467042923,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1760,
        "score": 0.015625,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1733,
        "score": 0.015384615398943424,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1753,
        "score": 0.01515151560306549,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1761,
        "score": 0.014925372786819935,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1749,
        "score": 0.014705882407724857,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1755,
        "score": 0.014492753893136978,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1736,
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
  "status": "judge_error",
  "stage": "judgment",
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
          1734
        ]
      ]
    }
  ],
  "candidate_ids": [
    1762,
    1734,
    1763,
    1760,
    1733,
    1753,
    1761,
    1749,
    1755,
    1736,
    1731,
    1777,
    1771,
    1744,
    1747,
    1772,
    1758,
    1775,
    1754,
    1759,
    1735,
    1780,
    1756,
    1757,
    1776,
    1779,
    1740,
    1773,
    1767,
    1750,
    1746,
    1748,
    1739,
    1768,
    1741,
    1745,
    1752,
    1751,
    1737,
    1765,
    1738,
    1770,
    1778,
    1743,
    1766,
    1764,
    1769,
    1742,
    1774,
    1732
  ],
  "final_ids": [
    1734,
    1762,
    1763,
    1753,
    1755,
    1736,
    1754,
    1733,
    1780,
    1775
  ],
  "prompt_citations": [
    {
      "n": 1,
      "chunk_id": "1734",
      "section_path": "售后手册/常见故障自查",
      "question": "常见故障自查",
      "answer": "- 饮水机不出水:检查水位是否低于最低线、水泵是否卡阻,断电清洗水泵后重试。\n- 猫砂盆报错:清空废砂盒并检查滚筒是否卡砂,重启设备;仍报错联系售后。\n- 喂食器卡粮:检查粮食颗粒直径是否超 12mm、粮桶是否受潮结块,清理出粮口后重试。\n- 摄像头离线:确认 Wi-Fi 为 2.4G 频段、信号良好,重启设备或在 App 内重新配网。"
    },
    {
      "n": 3,
      "chunk_id": "1763",
      "section_path": "商品规格手册/自动喂食器 摄像头版(型号 MH-FD30)",
      "question": "自动喂食器 摄像头版(型号 MH-FD30)",
      "answer": "- 型号:MH-FD30\n- 粮桶容量:6L\n- 核心功能:1080P 摄像头、双向语音、App 远程手动投喂与定时投喂\n- 供电:市电供电 + 内置应急电池\n- 说明:摄像头版支持视频回看,需连接 2.4G Wi-Fi"
    },
    {
      "n": 5,
      "chunk_id": "1755",
      "section_path": "商品规格手册/智能猫砂盆 Max(型号 MH-LP200)",
      "question": "智能猫砂盆 Max(型号 MH-LP200)",
      "answer": "- 型号:MH-LP200\n- 适用猫咪体重:2kg 至 12kg,适合大型猫与多猫家庭\n- 猫砂容量:12L,废砂盒容量约 10 天(单猫)\n- 核心功能:超大滚筒、双重称重防夹、活性炭除臭、App 多猫健康档案\n- 供电:220V 市电\n- 清理提示:多猫家庭建议每 3 至 5 天倾倒一次废砂盒"
    },
    {
      "n": 7,
      "chunk_id": "1754",
      "section_path": "商品规格手册/智能猫砂盆 Lite(型号 MH-LP50)",
      "question": "智能猫砂盆 Lite(型号 MH-LP50)",
      "answer": "- 型号:MH-LP50\n- 适用猫咪体重:1.5kg 至 6kg\n- 猫砂容量:6L\n- 核心功能:自动感应清理、物理除臭盖板;不含 App 联网功能\n- 与 Pro 差异:Lite 无 App 远程监控与健康记录,价格更低,适合单猫家庭"
    },
    {
      "n": 9,
      "chunk_id": "1780",
      "section_path": "猫窝清洗说明/猫窝是否可以机洗",
      "question": "猫窝是否可以机洗",
      "answer": "普通布艺猫窝清洗前拆掉内部垫芯，外套放入洗衣袋，使用轻柔模式冷水洗，自然晾干。不可直接将整只猫窝连垫芯一起机洗，商品另有清洗标签时优先遵循标签。\n\n带加热模块的猫窝不可机洗，应先断电，并按说明书局部擦洗；不得将加热模块、电源或线路浸水。未按清洗说明操作导致的损坏不直接认定为商品质量问题，需要客服核验。\n\n退货仍需符合商品完好、不影响二次销售等适用条件。售后手册中的电子类商品 12 个月保修不能直接套用到普通布艺猫窝；本清洗说明未给出布艺猫窝的独立保修期限。"
    },
    {
      "n": 10,
      "chunk_id": "1775",
      "section_path": "会员权益/生日礼",
      "question": "生日礼",
      "answer": "银卡会员生日当月可领取一份猫零食小样，金卡会员生日当月可领取一份猫罐头礼盒。需在会员中心领取，礼品规格与领取期限以页面标注为准，不承诺额外折现或补偿。"
    },
    {
      "n": 8,
      "chunk_id": "1733",
      "section_path": "售后手册/设备安装与激活",
      "question": "设备安装与激活",
      "answer": "智能设备首次使用需下载「喵喵优选」App,按说明书扫码添加设备并连接 2.4G Wi-Fi 完成激活;猫爬架等非联网商品按随附图解自行组装。"
    },
    {
      "n": 6,
      "chunk_id": "1736",
      "section_path": "售后手册/维修寄修流程",
      "question": "维修寄修流程",
      "answer": "保修期内设备故障,联系客服登记后按指引将设备寄回指定维修点,核验后免费维修并寄回;超保或人为损坏维修可能收取工本费,费用会提前告知。"
    },
    {
      "n": 4,
      "chunk_id": "1753",
      "section_path": "商品规格手册/智能猫砂盆 Pro(型号 MH-LP100)",
      "question": "智能猫砂盆 Pro(型号 MH-LP100)",
      "answer": "- 型号:MH-LP100\n- 适用猫咪体重:1.5kg 至 8kg\n- 猫砂容量:9L,废砂盒容量约 7 天(单猫)\n- 核心功能:自动感应清理、活性炭除臭、App 远程监控与健康记录\n- 供电:220V 市电,断电后配置自动保存\n- 清理提示:废砂盒满时 App 推送提醒,建议每 5 至 7 天倾倒一次"
    },
    {
      "n": 2,
      "chunk_id": "1762",
      "section_path": "商品规格手册/自动喂食器 基础版(型号 MH-FD10)",
      "question": "自动喂食器 基础版(型号 MH-FD10)",
      "answer": "- 型号:MH-FD10\n- 粮桶容量:4L\n- 核心功能:定时定量投喂,每日最多 6 餐,语音呼唤进食\n- 供电:市电供电 + 4 节 5 号电池断电应急\n- 说明:基础版不含摄像头与 App 远程投喂"
    }
  ],
  "decision": {
    "useful": true,
    "reason": "故障自查含喂食器卡粮处理",
    "response_kind": "knowledge",
    "source": null
  },
  "answer": "您好~喂食器卡粮可以按以下方法排查处理[1]：\n\n1. 检查粮食颗粒直径是否超过 12mm，过大的颗粒容易卡在出粮口[1]；\n2. 检查粮桶内的粮是否受潮结块，结块粮也会导致下粮不畅[1]；\n3. 清理出粮口后重新试机[1]。\n\n如果按上述步骤处理后仍无法正常出粮，保修期内可联系客服登记后按指引寄回维修点检测[6]。需要我帮您转人工登记吗？",
  "point_verdicts": null,
  "claim_verdicts": null,
  "metrics": {
    "recall_at_5": 1.0,
    "recall_at_10": 1.0,
    "mrr_at_10": 1.0,
    "all_groups_hit_at_5": 1.0,
    "all_groups_hit_at_10": 1.0,
    "candidate_group_coverage": 1.0,
    "prompt_group_coverage": 1.0,
    "answer_point_coverage": null,
    "faithfulness": null,
    "absent_refusal_rate": null,
    "answerable_false_refusal_rate": 0.0
  },
  "error": {
    "code": "judgment_error",
    "type": "JudgeError",
    "message": "该阶段执行失败"
  },
  "elapsed_ms": 40463.381100213155,
  "judge_snapshot": {
    "prompt_version": "joint-generation-v2.1",
    "finish_reason": "length"
  },
  "audit": {
    "audit_version": 1,
    "source_map_id": "378ae65f4ee735c6a8079070fbfcb5c21800c93f3318029e5f19836c32b5c2b4",
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
        "chunk_id": 1762,
        "score": 0.032522473484277725,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1734,
        "score": 0.03226646035909653,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1763,
        "score": 0.0320020467042923,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1760,
        "score": 0.015625,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1733,
        "score": 0.015384615398943424,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1753,
        "score": 0.01515151560306549,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1761,
        "score": 0.014925372786819935,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1749,
        "score": 0.014705882407724857,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1755,
        "score": 0.014492753893136978,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1736,
        "score": 0.014285714365541935,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1731,
        "score": 0.014084506779909134,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1777,
        "score": 0.013888888992369175,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1771,
        "score": 0.013698630034923553,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1744,
        "score": 0.013513513840734959,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1747,
        "score": 0.013333333656191826,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1772,
        "score": 0.01315789483487606,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1758,
        "score": 0.012987012974917889,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1775,
        "score": 0.012820512987673283,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1754,
        "score": 0.012658228166401386,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1759,
        "score": 0.012500000186264515,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1735,
        "score": 0.012345679104328156,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1780,
        "score": 0.012195121496915817,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1756,
        "score": 0.012048192322254181,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1757,
        "score": 0.011904762126505375,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1776,
        "score": 0.0117647061124444,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1779,
        "score": 0.011627906933426857,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1740,
        "score": 0.01149425283074379,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1773,
        "score": 0.011363636702299118,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1767,
        "score": 0.01123595517128706,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1750,
        "score": 0.011111111380159855,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1746,
        "score": 0.010989011265337467,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1748,
        "score": 0.010869565419852734,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1739,
        "score": 0.01075268816202879,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1768,
        "score": 0.010638297535479069,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1741,
        "score": 0.010526316240429878,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1745,
        "score": 0.010416666977107525,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1752,
        "score": 0.010309278033673763,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1751,
        "score": 0.010204081423580647,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1737,
        "score": 0.010101010091602802,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1765,
        "score": 0.009999999776482582,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1738,
        "score": 0.009900989942252636,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1770,
        "score": 0.009803921915590763,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1778,
        "score": 0.009708737954497337,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1743,
        "score": 0.009615384973585606,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1766,
        "score": 0.009523809887468815,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1764,
        "score": 0.009433962404727936,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1769,
        "score": 0.009345794096589088,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1742,
        "score": 0.009259259328246117,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1774,
        "score": 0.00917431153357029,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1732,
        "score": 0.00909090880304575,
        "score_kind": "rrf"
      }
    ],
    "final_ranking": [
      {
        "chunk_id": 1734,
        "score": 0.12182553112506866,
        "score_kind": "rerank"
      },
      {
        "chunk_id": 1762,
        "score": 0.002104800660163164,
        "score_kind": "rerank"
      },
      {
        "chunk_id": 1763,
        "score": 0.001809138571843505,
        "score_kind": "rerank"
      },
      {
        "chunk_id": 1753,
        "score": 0.0006421684520319104,
        "score_kind": "rerank"
      },
      {
        "chunk_id": 1755,
        "score": 0.000590265030041337,
        "score_kind": "rerank"
      },
      {
        "chunk_id": 1736,
        "score": 0.0005042759003117681,
        "score_kind": "rerank"
      },
      {
        "chunk_id": 1754,
        "score": 0.0004009127151221037,
        "score_kind": "rerank"
      },
      {
        "chunk_id": 1733,
        "score": 0.0002827057323884219,
        "score_kind": "rerank"
      },
      {
        "chunk_id": 1780,
        "score": 0.00026314170099794865,
        "score_kind": "rerank"
      },
      {
        "chunk_id": 1775,
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
    1733,
    1775,
    1759,
    1754,
    1780,
    1755,
    1760,
    1744,
    1752,
    1747,
    1753,
    1772,
    1761,
    1777,
    1734,
    1778,
    1740,
    1763,
    1745,
    1735,
    1774,
    1738,
    1737,
    1767,
    1762,
    1768,
    1742,
    1765,
    1770,
    1736,
    1750,
    1741,
    1751,
    1757,
    1739,
    1756,
    1776,
    1771,
    1758,
    1732,
    1748,
    1769,
    1731,
    1773,
    1749,
    1764,
    1746,
    1743,
    1779,
    1766
  ],
  "final_ids": [
    1733,
    1775,
    1759,
    1754,
    1780,
    1755,
    1760,
    1744,
    1752,
    1747
  ],
  "prompt_citations": [
    {
      "n": 1,
      "chunk_id": "1733",
      "section_path": "售后手册/设备安装与激活",
      "question": "设备安装与激活",
      "answer": "智能设备首次使用需下载「喵喵优选」App,按说明书扫码添加设备并连接 2.4G Wi-Fi 完成激活;猫爬架等非联网商品按随附图解自行组装。"
    },
    {
      "n": 3,
      "chunk_id": "1759",
      "section_path": "商品规格手册/大型猫爬架(型号 MH-CT30)",
      "question": "大型猫爬架(型号 MH-CT30)",
      "answer": "- 型号:MH-CT30\n- 高度:1.6m,共四层带顶层吊床\n- 承重:单层最大 10kg\n- 材质:剑麻柱身、绒布平台\n- 安装:需自行组装,随附六角扳手与图解说明书"
    },
    {
      "n": 5,
      "chunk_id": "1780",
      "section_path": "猫窝清洗说明/猫窝是否可以机洗",
      "question": "猫窝是否可以机洗",
      "answer": "普通布艺猫窝清洗前拆掉内部垫芯，外套放入洗衣袋，使用轻柔模式冷水洗，自然晾干。不可直接将整只猫窝连垫芯一起机洗，商品另有清洗标签时优先遵循标签。\n\n带加热模块的猫窝不可机洗，应先断电，并按说明书局部擦洗；不得将加热模块、电源或线路浸水。未按清洗说明操作导致的损坏不直接认定为商品质量问题，需要客服核验。\n\n退货仍需符合商品完好、不影响二次销售等适用条件。售后手册中的电子类商品 12 个月保修不能直接套用到普通布艺猫窝；本清洗说明未给出布艺猫窝的独立保修期限。"
    },
    {
      "n": 7,
      "chunk_id": "1760",
      "section_path": "商品规格手册/恒温加热垫(型号 MH-HP12)",
      "question": "恒温加热垫(型号 MH-HP12)",
      "answer": "- 型号:MH-HP12\n- 尺寸:40cm × 30cm\n- 温控:恒温 38℃,内置过热保护,连续通电不超过 12 小时为宜\n- 防护:防水防抓咬电线套管\n- 适用:幼猫、老年猫及冬季保暖"
    },
    {
      "n": 9,
      "chunk_id": "1752",
      "section_path": "商品规格手册",
      "question": "商品规格手册",
      "answer": "本手册收录喵喵优选自营智能硬件的型号、规格与使用要点,便于按具体型号查询。"
    },
    {
      "n": 10,
      "chunk_id": "1747",
      "section_path": "商品与购物 FAQ/配送范围与偏远地区",
      "question": "配送范围与偏远地区",
      "answer": "全国大部分地区支持配送,新疆、西藏、内蒙古等偏远地区运费另计且时效顺延;港澳台及海外暂不支持自营配送。"
    },
    {
      "n": 8,
      "chunk_id": "1744",
      "section_path": "商品与购物 FAQ/支持哪些支付方式",
      "question": "支持哪些支付方式",
      "answer": "下单支持支付宝、微信支付与主流银行储蓄卡/信用卡在线支付。暂不支持线下汇款,支付遇到问题可重试或更换支付方式。"
    },
    {
      "n": 6,
      "chunk_id": "1755",
      "section_path": "商品规格手册/智能猫砂盆 Max(型号 MH-LP200)",
      "question": "智能猫砂盆 Max(型号 MH-LP200)",
      "answer": "- 型号:MH-LP200\n- 适用猫咪体重:2kg 至 12kg,适合大型猫与多猫家庭\n- 猫砂容量:12L,废砂盒容量约 10 天(单猫)\n- 核心功能:超大滚筒、双重称重防夹、活性炭除臭、App 多猫健康档案\n- 供电:220V 市电\n- 清理提示:多猫家庭建议每 3 至 5 天倾倒一次废砂盒"
    },
    {
      "n": 4,
      "chunk_id": "1754",
      "section_path": "商品规格手册/智能猫砂盆 Lite(型号 MH-LP50)",
      "question": "智能猫砂盆 Lite(型号 MH-LP50)",
      "answer": "- 型号:MH-LP50\n- 适用猫咪体重:1.5kg 至 6kg\n- 猫砂容量:6L\n- 核心功能:自动感应清理、物理除臭盖板;不含 App 联网功能\n- 与 Pro 差异:Lite 无 App 远程监控与健康记录,价格更低,适合单猫家庭"
    },
    {
      "n": 2,
      "chunk_id": "1775",
      "section_path": "会员权益/生日礼",
      "question": "生日礼",
      "answer": "银卡会员生日当月可领取一份猫零食小样，金卡会员生日当月可领取一份猫罐头礼盒。需在会员中心领取，礼品规格与领取期限以页面标注为准，不承诺额外折现或补偿。"
    }
  ],
  "decision": {
    "useful": false,
    "reason": "证据均为宠物用品规格，无售卖活体宠物相关信息",
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
  "elapsed_ms": 45626.969000091776,
  "judge_snapshot": {
    "prompt_version": "joint-generation-v2.1",
    "finish_reason": "stop"
  },
  "audit": {
    "audit_version": 1,
    "source_map_id": "378ae65f4ee735c6a8079070fbfcb5c21800c93f3318029e5f19836c32b5c2b4",
    "gold_groups": [],
    "answer_points": [],
    "candidate_ranking": [
      {
        "chunk_id": 1733,
        "score": 0.5230516195297241,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1775,
        "score": 0.517601728439331,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1759,
        "score": 0.5064369440078735,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1754,
        "score": 0.4854865074157715,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1780,
        "score": 0.48334604501724243,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1755,
        "score": 0.4772193729877472,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1760,
        "score": 0.472115695476532,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1744,
        "score": 0.4711533784866333,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1752,
        "score": 0.4655056595802307,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1747,
        "score": 0.46494314074516296,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1753,
        "score": 0.4633696377277374,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1772,
        "score": 0.46314674615859985,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1761,
        "score": 0.4619412422180176,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1777,
        "score": 0.4520297944545746,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1734,
        "score": 0.41445615887641907,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1778,
        "score": 0.41061165928840637,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1740,
        "score": 0.40904730558395386,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1763,
        "score": 0.39880701899528503,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1745,
        "score": 0.3965839445590973,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1735,
        "score": 0.396505743265152,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1774,
        "score": 0.3948422968387604,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1738,
        "score": 0.3926236033439636,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1737,
        "score": 0.38972947001457214,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1767,
        "score": 0.3883713483810425,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1762,
        "score": 0.3854010999202728,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1768,
        "score": 0.38369667530059814,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1742,
        "score": 0.3832646608352661,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1765,
        "score": 0.38162821531295776,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1770,
        "score": 0.3804421126842499,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1736,
        "score": 0.37865543365478516,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1750,
        "score": 0.37787264585494995,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1741,
        "score": 0.37357136607170105,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1751,
        "score": 0.37291795015335083,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1757,
        "score": 0.37046343088150024,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1739,
        "score": 0.3690685033798218,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1756,
        "score": 0.367192804813385,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1776,
        "score": 0.3657568097114563,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1771,
        "score": 0.3630736172199249,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1758,
        "score": 0.3623853921890259,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1732,
        "score": 0.3607848882675171,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1748,
        "score": 0.3583538830280304,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1769,
        "score": 0.35405170917510986,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1731,
        "score": 0.3537989854812622,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1773,
        "score": 0.3535041809082031,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1749,
        "score": 0.35167378187179565,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1764,
        "score": 0.34829089045524597,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1746,
        "score": 0.34145939350128174,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1743,
        "score": 0.33695530891418457,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1779,
        "score": 0.31677648425102234,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1766,
        "score": 0.31404101848602295,
        "score_kind": "cosine"
      }
    ],
    "final_ranking": [
      {
        "chunk_id": 1733,
        "score": 0.5230516195297241,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1775,
        "score": 0.517601728439331,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1759,
        "score": 0.5064369440078735,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1754,
        "score": 0.4854865074157715,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1780,
        "score": 0.48334604501724243,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1755,
        "score": 0.4772193729877472,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1760,
        "score": 0.472115695476532,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1744,
        "score": 0.4711533784866333,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1752,
        "score": 0.4655056595802307,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1747,
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
    1748,
    1780,
    1734,
    1755,
    1775,
    1746,
    1732,
    1777,
    1739,
    1772,
    1743,
    1749,
    1750,
    1759,
    1760,
    1733,
    1745,
    1771,
    1761,
    1754,
    1774,
    1753,
    1779
  ],
  "final_ids": [
    1748,
    1780,
    1734,
    1755,
    1775,
    1746,
    1732,
    1777,
    1739,
    1772
  ],
  "prompt_citations": [
    {
      "n": 1,
      "chunk_id": "1748",
      "section_path": "商品与购物 FAQ/订单可以修改或取消吗",
      "question": "订单可以修改或取消吗",
      "answer": "订单未发货前可在「我的订单」自助取消;已发货订单无法修改收货信息,可拒收后走退款流程。修改商品数量需取消后重新下单。"
    },
    {
      "n": 3,
      "chunk_id": "1734",
      "section_path": "售后手册/常见故障自查",
      "question": "常见故障自查",
      "answer": "- 饮水机不出水:检查水位是否低于最低线、水泵是否卡阻,断电清洗水泵后重试。\n- 猫砂盆报错:清空废砂盒并检查滚筒是否卡砂,重启设备;仍报错联系售后。\n- 喂食器卡粮:检查粮食颗粒直径是否超 12mm、粮桶是否受潮结块,清理出粮口后重试。\n- 摄像头离线:确认 Wi-Fi 为 2.4G 频段、信号良好,重启设备或在 App 内重新配网。"
    },
    {
      "n": 5,
      "chunk_id": "1775",
      "section_path": "会员权益/生日礼",
      "question": "生日礼",
      "answer": "银卡会员生日当月可领取一份猫零食小样，金卡会员生日当月可领取一份猫罐头礼盒。需在会员中心领取，礼品规格与领取期限以页面标注为准，不承诺额外折现或补偿。"
    },
    {
      "n": 7,
      "chunk_id": "1732",
      "section_path": "售后手册/保修说明",
      "question": "保修说明",
      "answer": "电子类商品保修 12 个月,自签收日起算;人为损坏不在保修范围。"
    },
    {
      "n": 9,
      "chunk_id": "1739",
      "section_path": "商品与购物 FAQ/如何申请退款",
      "question": "如何申请退款",
      "answer": "在「我的订单」找到对应订单点击「申请退款」,按提示提交,审核通过后原路退回。"
    },
    {
      "n": 10,
      "chunk_id": "1772",
      "section_path": "退货退款政策/不支持退货的商品",
      "question": "不支持退货的商品",
      "answer": "定制类、生鲜类、已拆封的猫砂等消耗品,以及标注「不支持无理由退货」的商品,非质量问题不支持退货。"
    },
    {
      "n": 8,
      "chunk_id": "1777",
      "section_path": "积分规则/积分怎么用",
      "question": "积分怎么用",
      "answer": "积分可在结算时抵扣商品金额，100 积分抵 1 元现金，单笔订单最多抵 30 元，不用于抵扣偏远地区附加运费，也不支持直接提现。\n\n2000 积分可兑换自动饮水机滤芯 3 片，该兑换套装适用于 MH-W40，普通配送地区包邮；偏远地区附加配送费仍需按页面规则确认。MH-W40 的滤芯更换周期以商品规格手册为准。\n\n800 积分可兑换猫零食小样，普通配送地区另收 6 元运费；该兑换不直接套用普通购物订单的满 99 元包邮规则。兑换商品、可用库存及偏远地区配送规则以兑换页面标注为准。"
    },
    {
      "n": 6,
      "chunk_id": "1746",
      "section_path": "商品与购物 FAQ/优惠券和满减怎么用",
      "question": "优惠券和满减怎么用",
      "answer": "优惠券在结算页「使用优惠券」中勾选,满减活动自动叠加在商品页标示的门槛上;同一订单一般限用一张店铺券,活动细则以页面为准。"
    },
    {
      "n": 4,
      "chunk_id": "1755",
      "section_path": "商品规格手册/智能猫砂盆 Max(型号 MH-LP200)",
      "question": "智能猫砂盆 Max(型号 MH-LP200)",
      "answer": "- 型号:MH-LP200\n- 适用猫咪体重:2kg 至 12kg,适合大型猫与多猫家庭\n- 猫砂容量:12L,废砂盒容量约 10 天(单猫)\n- 核心功能:超大滚筒、双重称重防夹、活性炭除臭、App 多猫健康档案\n- 供电:220V 市电\n- 清理提示:多猫家庭建议每 3 至 5 天倾倒一次废砂盒"
    },
    {
      "n": 2,
      "chunk_id": "1780",
      "section_path": "猫窝清洗说明/猫窝是否可以机洗",
      "question": "猫窝是否可以机洗",
      "answer": "普通布艺猫窝清洗前拆掉内部垫芯，外套放入洗衣袋，使用轻柔模式冷水洗，自然晾干。不可直接将整只猫窝连垫芯一起机洗，商品另有清洗标签时优先遵循标签。\n\n带加热模块的猫窝不可机洗，应先断电，并按说明书局部擦洗；不得将加热模块、电源或线路浸水。未按清洗说明操作导致的损坏不直接认定为商品质量问题，需要客服核验。\n\n退货仍需符合商品完好、不影响二次销售等适用条件。售后手册中的电子类商品 12 个月保修不能直接套用到普通布艺猫窝；本清洗说明未给出布艺猫窝的独立保修期限。"
    }
  ],
  "decision": {
    "useful": false,
    "reason": "证据均不涉及是否售卖活体宠物",
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
  "elapsed_ms": 21264.291200088337,
  "judge_snapshot": {
    "prompt_version": "joint-generation-v2.1",
    "finish_reason": "stop"
  },
  "audit": {
    "audit_version": 1,
    "source_map_id": "378ae65f4ee735c6a8079070fbfcb5c21800c93f3318029e5f19836c32b5c2b4",
    "gold_groups": [],
    "answer_points": [],
    "candidate_ranking": [
      {
        "chunk_id": 1748,
        "score": 5.146595478057861,
        "score_kind": "bm25"
      },
      {
        "chunk_id": 1780,
        "score": 2.217597484588623,
        "score_kind": "bm25"
      },
      {
        "chunk_id": 1734,
        "score": 2.203824281692505,
        "score_kind": "bm25"
      },
      {
        "chunk_id": 1755,
        "score": 2.051485300064087,
        "score_kind": "bm25"
      },
      {
        "chunk_id": 1775,
        "score": 1.9893113374710083,
        "score_kind": "bm25"
      },
      {
        "chunk_id": 1746,
        "score": 1.9015036821365356,
        "score_kind": "bm25"
      },
      {
        "chunk_id": 1732,
        "score": 1.7063724994659424,
        "score_kind": "bm25"
      },
      {
        "chunk_id": 1777,
        "score": 1.6996121406555176,
        "score_kind": "bm25"
      },
      {
        "chunk_id": 1739,
        "score": 1.6403803825378418,
        "score_kind": "bm25"
      },
      {
        "chunk_id": 1772,
        "score": 1.5823721885681152,
        "score_kind": "bm25"
      },
      {
        "chunk_id": 1743,
        "score": 1.5647372007369995,
        "score_kind": "bm25"
      },
      {
        "chunk_id": 1749,
        "score": 1.536397933959961,
        "score_kind": "bm25"
      },
      {
        "chunk_id": 1750,
        "score": 1.5090670585632324,
        "score_kind": "bm25"
      },
      {
        "chunk_id": 1759,
        "score": 1.5028752088546753,
        "score_kind": "bm25"
      },
      {
        "chunk_id": 1760,
        "score": 1.5028752088546753,
        "score_kind": "bm25"
      },
      {
        "chunk_id": 1733,
        "score": 1.4903959035873413,
        "score_kind": "bm25"
      },
      {
        "chunk_id": 1745,
        "score": 1.469846248626709,
        "score_kind": "bm25"
      },
      {
        "chunk_id": 1771,
        "score": 1.4572218656539917,
        "score_kind": "bm25"
      },
      {
        "chunk_id": 1761,
        "score": 1.4309837818145752,
        "score_kind": "bm25"
      },
      {
        "chunk_id": 1754,
        "score": 1.3656563758850098,
        "score_kind": "bm25"
      },
      {
        "chunk_id": 1774,
        "score": 1.2454544305801392,
        "score_kind": "bm25"
      },
      {
        "chunk_id": 1753,
        "score": 1.217445969581604,
        "score_kind": "bm25"
      },
      {
        "chunk_id": 1779,
        "score": 1.0986462831497192,
        "score_kind": "bm25"
      }
    ],
    "final_ranking": [
      {
        "chunk_id": 1748,
        "score": 5.146595478057861,
        "score_kind": "bm25"
      },
      {
        "chunk_id": 1780,
        "score": 2.217597484588623,
        "score_kind": "bm25"
      },
      {
        "chunk_id": 1734,
        "score": 2.203824281692505,
        "score_kind": "bm25"
      },
      {
        "chunk_id": 1755,
        "score": 2.051485300064087,
        "score_kind": "bm25"
      },
      {
        "chunk_id": 1775,
        "score": 1.9893113374710083,
        "score_kind": "bm25"
      },
      {
        "chunk_id": 1746,
        "score": 1.9015036821365356,
        "score_kind": "bm25"
      },
      {
        "chunk_id": 1732,
        "score": 1.7063724994659424,
        "score_kind": "bm25"
      },
      {
        "chunk_id": 1777,
        "score": 1.6996121406555176,
        "score_kind": "bm25"
      },
      {
        "chunk_id": 1739,
        "score": 1.6403803825378418,
        "score_kind": "bm25"
      },
      {
        "chunk_id": 1772,
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
    1775,
    1780,
    1755,
    1733,
    1759,
    1734,
    1760,
    1777,
    1772,
    1754,
    1761,
    1748,
    1753,
    1745,
    1739,
    1732,
    1774,
    1750,
    1746,
    1749,
    1743,
    1771,
    1779,
    1744,
    1752,
    1747,
    1778,
    1740,
    1763,
    1735,
    1738,
    1737,
    1767,
    1762,
    1768,
    1742,
    1765,
    1770,
    1736,
    1741,
    1751,
    1757,
    1756,
    1776,
    1758,
    1769,
    1731,
    1773,
    1764,
    1766
  ],
  "final_ids": [
    1775,
    1780,
    1755,
    1733,
    1759,
    1734,
    1760,
    1777,
    1772,
    1754
  ],
  "prompt_citations": [
    {
      "n": 1,
      "chunk_id": "1775",
      "section_path": "会员权益/生日礼",
      "question": "生日礼",
      "answer": "银卡会员生日当月可领取一份猫零食小样，金卡会员生日当月可领取一份猫罐头礼盒。需在会员中心领取，礼品规格与领取期限以页面标注为准，不承诺额外折现或补偿。"
    },
    {
      "n": 3,
      "chunk_id": "1755",
      "section_path": "商品规格手册/智能猫砂盆 Max(型号 MH-LP200)",
      "question": "智能猫砂盆 Max(型号 MH-LP200)",
      "answer": "- 型号:MH-LP200\n- 适用猫咪体重:2kg 至 12kg,适合大型猫与多猫家庭\n- 猫砂容量:12L,废砂盒容量约 10 天(单猫)\n- 核心功能:超大滚筒、双重称重防夹、活性炭除臭、App 多猫健康档案\n- 供电:220V 市电\n- 清理提示:多猫家庭建议每 3 至 5 天倾倒一次废砂盒"
    },
    {
      "n": 5,
      "chunk_id": "1759",
      "section_path": "商品规格手册/大型猫爬架(型号 MH-CT30)",
      "question": "大型猫爬架(型号 MH-CT30)",
      "answer": "- 型号:MH-CT30\n- 高度:1.6m,共四层带顶层吊床\n- 承重:单层最大 10kg\n- 材质:剑麻柱身、绒布平台\n- 安装:需自行组装,随附六角扳手与图解说明书"
    },
    {
      "n": 7,
      "chunk_id": "1760",
      "section_path": "商品规格手册/恒温加热垫(型号 MH-HP12)",
      "question": "恒温加热垫(型号 MH-HP12)",
      "answer": "- 型号:MH-HP12\n- 尺寸:40cm × 30cm\n- 温控:恒温 38℃,内置过热保护,连续通电不超过 12 小时为宜\n- 防护:防水防抓咬电线套管\n- 适用:幼猫、老年猫及冬季保暖"
    },
    {
      "n": 9,
      "chunk_id": "1772",
      "section_path": "退货退款政策/不支持退货的商品",
      "question": "不支持退货的商品",
      "answer": "定制类、生鲜类、已拆封的猫砂等消耗品,以及标注「不支持无理由退货」的商品,非质量问题不支持退货。"
    },
    {
      "n": 10,
      "chunk_id": "1754",
      "section_path": "商品规格手册/智能猫砂盆 Lite(型号 MH-LP50)",
      "question": "智能猫砂盆 Lite(型号 MH-LP50)",
      "answer": "- 型号:MH-LP50\n- 适用猫咪体重:1.5kg 至 6kg\n- 猫砂容量:6L\n- 核心功能:自动感应清理、物理除臭盖板;不含 App 联网功能\n- 与 Pro 差异:Lite 无 App 远程监控与健康记录,价格更低,适合单猫家庭"
    },
    {
      "n": 8,
      "chunk_id": "1777",
      "section_path": "积分规则/积分怎么用",
      "question": "积分怎么用",
      "answer": "积分可在结算时抵扣商品金额，100 积分抵 1 元现金，单笔订单最多抵 30 元，不用于抵扣偏远地区附加运费，也不支持直接提现。\n\n2000 积分可兑换自动饮水机滤芯 3 片，该兑换套装适用于 MH-W40，普通配送地区包邮；偏远地区附加配送费仍需按页面规则确认。MH-W40 的滤芯更换周期以商品规格手册为准。\n\n800 积分可兑换猫零食小样，普通配送地区另收 6 元运费；该兑换不直接套用普通购物订单的满 99 元包邮规则。兑换商品、可用库存及偏远地区配送规则以兑换页面标注为准。"
    },
    {
      "n": 6,
      "chunk_id": "1734",
      "section_path": "售后手册/常见故障自查",
      "question": "常见故障自查",
      "answer": "- 饮水机不出水:检查水位是否低于最低线、水泵是否卡阻,断电清洗水泵后重试。\n- 猫砂盆报错:清空废砂盒并检查滚筒是否卡砂,重启设备;仍报错联系售后。\n- 喂食器卡粮:检查粮食颗粒直径是否超 12mm、粮桶是否受潮结块,清理出粮口后重试。\n- 摄像头离线:确认 Wi-Fi 为 2.4G 频段、信号良好,重启设备或在 App 内重新配网。"
    },
    {
      "n": 4,
      "chunk_id": "1733",
      "section_path": "售后手册/设备安装与激活",
      "question": "设备安装与激活",
      "answer": "智能设备首次使用需下载「喵喵优选」App,按说明书扫码添加设备并连接 2.4G Wi-Fi 完成激活;猫爬架等非联网商品按随附图解自行组装。"
    },
    {
      "n": 2,
      "chunk_id": "1780",
      "section_path": "猫窝清洗说明/猫窝是否可以机洗",
      "question": "猫窝是否可以机洗",
      "answer": "普通布艺猫窝清洗前拆掉内部垫芯，外套放入洗衣袋，使用轻柔模式冷水洗，自然晾干。不可直接将整只猫窝连垫芯一起机洗，商品另有清洗标签时优先遵循标签。\n\n带加热模块的猫窝不可机洗，应先断电，并按说明书局部擦洗；不得将加热模块、电源或线路浸水。未按清洗说明操作导致的损坏不直接认定为商品质量问题，需要客服核验。\n\n退货仍需符合商品完好、不影响二次销售等适用条件。售后手册中的电子类商品 12 个月保修不能直接套用到普通布艺猫窝；本清洗说明未给出布艺猫窝的独立保修期限。"
    }
  ],
  "decision": {
    "useful": false,
    "reason": "证据均为猫用品与会员政策，无售卖活体宠物信息",
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
  "elapsed_ms": 24769.383900100365,
  "judge_snapshot": {
    "prompt_version": "joint-generation-v2.1",
    "finish_reason": "stop"
  },
  "audit": {
    "audit_version": 1,
    "source_map_id": "378ae65f4ee735c6a8079070fbfcb5c21800c93f3318029e5f19836c32b5c2b4",
    "gold_groups": [],
    "answer_points": [],
    "candidate_ranking": [
      {
        "chunk_id": 1775,
        "score": 0.03151364624500275,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1780,
        "score": 0.03151364624500275,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1755,
        "score": 0.03077651560306549,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1733,
        "score": 0.02955133654177189,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1759,
        "score": 0.029386531561613083,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1734,
        "score": 0.029206350445747375,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1760,
        "score": 0.028258707374334335,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1777,
        "score": 0.028219396248459816,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1772,
        "score": 0.02817460335791111,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1754,
        "score": 0.02812499925494194,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1761,
        "score": 0.026356857270002365,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1748,
        "score": 0.02629443258047104,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1753,
        "score": 0.02627962827682495,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1745,
        "score": 0.025645241141319275,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1739,
        "score": 0.025019070133566856,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1732,
        "score": 0.02492537349462509,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1774,
        "score": 0.02469135820865631,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1750,
        "score": 0.024687640368938446,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1746,
        "score": 0.02449730969965458,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1749,
        "score": 0.02341269887983799,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1743,
        "score": 0.02334376610815525,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1771,
        "score": 0.02302459441125393,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1779,
        "score": 0.02122250385582447,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1744,
        "score": 0.014705882407724857,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1752,
        "score": 0.014492753893136978,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1747,
        "score": 0.014285714365541935,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1778,
        "score": 0.01315789483487606,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1740,
        "score": 0.012987012974917889,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1763,
        "score": 0.012820512987673283,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1735,
        "score": 0.012500000186264515,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1738,
        "score": 0.012195121496915817,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1737,
        "score": 0.012048192322254181,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1767,
        "score": 0.011904762126505375,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1762,
        "score": 0.0117647061124444,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1768,
        "score": 0.011627906933426857,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1742,
        "score": 0.01149425283074379,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1765,
        "score": 0.011363636702299118,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1770,
        "score": 0.01123595517128706,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1736,
        "score": 0.011111111380159855,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1741,
        "score": 0.010869565419852734,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1751,
        "score": 0.01075268816202879,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1757,
        "score": 0.010638297535479069,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1756,
        "score": 0.010416666977107525,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1776,
        "score": 0.010309278033673763,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1758,
        "score": 0.010101010091602802,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1769,
        "score": 0.009803921915590763,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1731,
        "score": 0.009708737954497337,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1773,
        "score": 0.009615384973585606,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1764,
        "score": 0.009433962404727936,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1766,
        "score": 0.00909090880304575,
        "score_kind": "rrf"
      }
    ],
    "final_ranking": [
      {
        "chunk_id": 1775,
        "score": 0.03151364624500275,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1780,
        "score": 0.03151364624500275,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1755,
        "score": 0.03077651560306549,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1733,
        "score": 0.02955133654177189,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1759,
        "score": 0.029386531561613083,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1734,
        "score": 0.029206350445747375,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1760,
        "score": 0.028258707374334335,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1777,
        "score": 0.028219396248459816,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1772,
        "score": 0.02817460335791111,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1754,
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
    1775,
    1780,
    1755,
    1733,
    1759,
    1734,
    1760,
    1777,
    1772,
    1754,
    1761,
    1748,
    1753,
    1745,
    1739,
    1732,
    1774,
    1750,
    1746,
    1749,
    1743,
    1771,
    1779,
    1744,
    1752,
    1747,
    1778,
    1740,
    1763,
    1735,
    1738,
    1737,
    1767,
    1762,
    1768,
    1742,
    1765,
    1770,
    1736,
    1741,
    1751,
    1757,
    1756,
    1776,
    1758,
    1769,
    1731,
    1773,
    1764,
    1766
  ],
  "final_ids": [
    1775,
    1772,
    1747,
    1738,
    1769,
    1765,
    1774,
    1768,
    1737,
    1745
  ],
  "prompt_citations": [
    {
      "n": 1,
      "chunk_id": "1775",
      "section_path": "会员权益/生日礼",
      "question": "生日礼",
      "answer": "银卡会员生日当月可领取一份猫零食小样，金卡会员生日当月可领取一份猫罐头礼盒。需在会员中心领取，礼品规格与领取期限以页面标注为准，不承诺额外折现或补偿。"
    },
    {
      "n": 3,
      "chunk_id": "1747",
      "section_path": "商品与购物 FAQ/配送范围与偏远地区",
      "question": "配送范围与偏远地区",
      "answer": "全国大部分地区支持配送,新疆、西藏、内蒙古等偏远地区运费另计且时效顺延;港澳台及海外暂不支持自营配送。"
    },
    {
      "n": 5,
      "chunk_id": "1769",
      "section_path": "退货退款政策/退换货运费承担",
      "question": "退换货运费承担",
      "answer": "无理由退货的退回运费由买家承担;因商品质量问题、发错货、少发漏发导致的退换货,运费由平台承担。运费承担以平台售后规则最终判定为准。"
    },
    {
      "n": 7,
      "chunk_id": "1774",
      "section_path": "会员权益/会员等级",
      "question": "会员等级",
      "answer": "会员分为普通、银卡和金卡三档，按有效累计消费金额自动升级，不按年度消费金额计算。累计消费未满 1000 元为普通会员，满 1000 元起为银卡，满 5000 元起为金卡。\n\n有效累计消费指已完成订单的商品实际支付金额，不含配送费；退货退款部分从有效累计消费中扣除。退款后根据更新的累计消费重新计算等级，未达到原门槛时可能降级。等级与适用权益在会员中心展示。\n\n银卡在参与会员折扣的商品上享 95 折，金卡享 9 折。折扣适用商品和活动范围以结算页面标注为准。会员折扣、优惠券与满减是否叠加也以当次活动页面为准，不能一概承诺全部优惠同时生效。"
    },
    {
      "n": 9,
      "chunk_id": "1737",
      "section_path": "售后手册/会员专属售后权益",
      "question": "会员专属售后权益",
      "answer": "金卡会员享优先客服接入与上门取件退换货;银卡会员享退换货运费权益 1 次/月。具体权益以会员中心页面标注为准。"
    },
    {
      "n": 10,
      "chunk_id": "1745",
      "section_path": "商品与购物 FAQ/会员等级与积分规则",
      "question": "会员等级与积分规则",
      "answer": "会员分为普通、银卡、金卡三档,按累计消费自动升级。每消费 1 元得 1 积分,积分可在结算时抵扣,100 积分抵 1 元。"
    },
    {
      "n": 8,
      "chunk_id": "1768",
      "section_path": "退货退款政策/换货政策/换货运费",
      "question": "换货运费",
      "answer": "非质量问题的换货,往返运费由买家承担;因质量问题或发错货的换货,往返运费由平台承担。"
    },
    {
      "n": 6,
      "chunk_id": "1765",
      "section_path": "退货退款政策/无理由退货/适用范围",
      "question": "适用范围",
      "answer": "自签收之日起 7 天内,商品完好、不影响二次销售的,支持无理由退货。定制类、生鲜类商品除外。"
    },
    {
      "n": 4,
      "chunk_id": "1738",
      "section_path": "商品与购物 FAQ/退货政策是什么",
      "question": "退货政策是什么",
      "answer": "支持 7 天无理由退货,商品需保持完好、不影响二次销售,具体以平台售后规则为准。"
    },
    {
      "n": 2,
      "chunk_id": "1772",
      "section_path": "退货退款政策/不支持退货的商品",
      "question": "不支持退货的商品",
      "answer": "定制类、生鲜类、已拆封的猫砂等消耗品,以及标注「不支持无理由退货」的商品,非质量问题不支持退货。"
    }
  ],
  "decision": {
    "useful": false,
    "reason": "证据均与售卖活体宠物无关，缺少商品范围信息",
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
  "elapsed_ms": 28537.37090015784,
  "judge_snapshot": {
    "prompt_version": "joint-generation-v2.1",
    "finish_reason": "stop"
  },
  "audit": {
    "audit_version": 1,
    "source_map_id": "378ae65f4ee735c6a8079070fbfcb5c21800c93f3318029e5f19836c32b5c2b4",
    "gold_groups": [],
    "answer_points": [],
    "candidate_ranking": [
      {
        "chunk_id": 1775,
        "score": 0.03151364624500275,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1780,
        "score": 0.03151364624500275,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1755,
        "score": 0.03077651560306549,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1733,
        "score": 0.02955133654177189,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1759,
        "score": 0.029386531561613083,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1734,
        "score": 0.029206350445747375,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1760,
        "score": 0.028258707374334335,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1777,
        "score": 0.028219396248459816,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1772,
        "score": 0.02817460335791111,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1754,
        "score": 0.02812499925494194,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1761,
        "score": 0.026356857270002365,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1748,
        "score": 0.02629443258047104,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1753,
        "score": 0.02627962827682495,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1745,
        "score": 0.025645241141319275,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1739,
        "score": 0.025019070133566856,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1732,
        "score": 0.02492537349462509,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1774,
        "score": 0.02469135820865631,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1750,
        "score": 0.024687640368938446,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1746,
        "score": 0.02449730969965458,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1749,
        "score": 0.02341269887983799,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1743,
        "score": 0.02334376610815525,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1771,
        "score": 0.02302459441125393,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1779,
        "score": 0.02122250385582447,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1744,
        "score": 0.014705882407724857,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1752,
        "score": 0.014492753893136978,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1747,
        "score": 0.014285714365541935,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1778,
        "score": 0.01315789483487606,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1740,
        "score": 0.012987012974917889,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1763,
        "score": 0.012820512987673283,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1735,
        "score": 0.012500000186264515,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1738,
        "score": 0.012195121496915817,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1737,
        "score": 0.012048192322254181,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1767,
        "score": 0.011904762126505375,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1762,
        "score": 0.0117647061124444,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1768,
        "score": 0.011627906933426857,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1742,
        "score": 0.01149425283074379,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1765,
        "score": 0.011363636702299118,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1770,
        "score": 0.01123595517128706,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1736,
        "score": 0.011111111380159855,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1741,
        "score": 0.010869565419852734,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1751,
        "score": 0.01075268816202879,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1757,
        "score": 0.010638297535479069,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1756,
        "score": 0.010416666977107525,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1776,
        "score": 0.010309278033673763,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1758,
        "score": 0.010101010091602802,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1769,
        "score": 0.009803921915590763,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1731,
        "score": 0.009708737954497337,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1773,
        "score": 0.009615384973585606,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1764,
        "score": 0.009433962404727936,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1766,
        "score": 0.00909090880304575,
        "score_kind": "rrf"
      }
    ],
    "final_ranking": [
      {
        "chunk_id": 1775,
        "score": 0.002305577974766493,
        "score_kind": "rerank"
      },
      {
        "chunk_id": 1772,
        "score": 0.0022089057601988316,
        "score_kind": "rerank"
      },
      {
        "chunk_id": 1747,
        "score": 0.0007817724253982306,
        "score_kind": "rerank"
      },
      {
        "chunk_id": 1738,
        "score": 0.0006711307214573026,
        "score_kind": "rerank"
      },
      {
        "chunk_id": 1769,
        "score": 0.000629141868557781,
        "score_kind": "rerank"
      },
      {
        "chunk_id": 1765,
        "score": 0.0006007851334288716,
        "score_kind": "rerank"
      },
      {
        "chunk_id": 1774,
        "score": 0.0005535759264603257,
        "score_kind": "rerank"
      },
      {
        "chunk_id": 1768,
        "score": 0.0005168296629562974,
        "score_kind": "rerank"
      },
      {
        "chunk_id": 1737,
        "score": 0.00048264750512316823,
        "score_kind": "rerank"
      },
      {
        "chunk_id": 1745,
        "score": 0.0004793392727151513,
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
    1778,
    1743,
    1779,
    1771,
    1739,
    1736,
    1731,
    1732,
    1773,
    1767,
    1770,
    1765,
    1737,
    1748,
    1740,
    1750,
    1768,
    1766,
    1777,
    1769,
    1738,
    1749,
    1772,
    1735,
    1741,
    1744,
    1751,
    1746,
    1734,
    1776,
    1742,
    1747,
    1775,
    1752,
    1774,
    1758,
    1733,
    1745,
    1757,
    1756,
    1762,
    1763,
    1761,
    1780,
    1764,
    1753,
    1755,
    1759,
    1754,
    1760
  ],
  "final_ids": [
    1778,
    1743,
    1779,
    1771,
    1739,
    1736,
    1731,
    1732,
    1773,
    1767
  ],
  "prompt_citations": [
    {
      "n": 1,
      "chunk_id": "1778",
      "section_path": "开票细则/可开票类型",
      "question": "可开票类型",
      "answer": "本演示店提供电子普通发票、电子专用发票和纸质专用发票。电子普通发票可按订单申请；电子专票需要企业账户，申请前准备发票抬头及有效纳税人识别号，按申请页面提交资料。\n\n纸质专票仅企业账户可申请，申请时需提供企业开票资料、收件人和邮寄地址，快递费到付。资料审核通过后按开票流程寄出，不承诺快递送达日期。"
    },
    {
      "n": 3,
      "chunk_id": "1779",
      "section_path": "开票细则/开票时效",
      "question": "开票时效",
      "answer": "订单完成后 30 天内可在「我的订单」申请开票，超过 30 天需联系客服核实补开条件，不能直接承诺一定补开。\n\n有效资料审核通过后 3 个工作日内开出发票，电子发票发送至申请邮箱；纸质专票开出后安排邮寄，邮寄耗时不计入开票时限。发票抬头或税号填错时联系客服核实更正，不保证无需审核即可重开。"
    },
    {
      "n": 5,
      "chunk_id": "1739",
      "section_path": "商品与购物 FAQ/如何申请退款",
      "question": "如何申请退款",
      "answer": "在「我的订单」找到对应订单点击「申请退款」,按提示提交,审核通过后原路退回。"
    },
    {
      "n": 7,
      "chunk_id": "1731",
      "section_path": "售后手册/常见问题处理时限",
      "question": "常见问题处理时限",
      "answer": "| 问题类型 | 首次响应 | 处理时限 |\n| --- | --- | --- |\n| 退款 | 2 小时 | 3 个工作日 |\n| 换货 | 2 小时 | 5 个工作日 |\n| 维修 | 4 小时 | 7 个工作日 |\n| 投诉 | 1 小时 | 3 个工作日 |\n| 发票 | 4 小时 | 3 个工作日 |\n| 物流异常 | 2 小时 | 5 个工作日 |\n| 商品咨询 | 1 小时 | 当日 |\n| 价格保护 | 2 小时 | 3 个工作日 |\n| 账户问题 | 2 小时 | 3 个工作日 |\n| 退换货运费 | 2 小时 | 3 个工作日 |\n| 缺货补发 | 2 小时 | 5 个工作日 |\n| 其他 | 4 小时 | 7 个工作日 |"
    },
    {
      "n": 9,
      "chunk_id": "1773",
      "section_path": "退货退款政策/预售与定金",
      "question": "预售与定金",
      "answer": "预售商品以详情页标注的时间发货;定金支付后不支持无理由退定金,尾款未按时支付的,定金按活动规则处理。"
    },
    {
      "n": 10,
      "chunk_id": "1767",
      "section_path": "退货退款政策/换货政策/换货条件",
      "question": "换货条件",
      "answer": "收到商品 7 天内,商品完好且配件齐全的,可申请一次同款换货;不同型号或颜色需先退货再重新下单。"
    },
    {
      "n": 8,
      "chunk_id": "1732",
      "section_path": "售后手册/保修说明",
      "question": "保修说明",
      "answer": "电子类商品保修 12 个月,自签收日起算;人为损坏不在保修范围。"
    },
    {
      "n": 6,
      "chunk_id": "1736",
      "section_path": "售后手册/维修寄修流程",
      "question": "维修寄修流程",
      "answer": "保修期内设备故障,联系客服登记后按指引将设备寄回指定维修点,核验后免费维修并寄回;超保或人为损坏维修可能收取工本费,费用会提前告知。"
    },
    {
      "n": 4,
      "chunk_id": "1771",
      "section_path": "退货退款政策/运输破损处理",
      "question": "运输破损处理",
      "answer": "商品运输途中破损的,请在签收后 48 小时内联系客服并提供开箱视频与照片,核实后可免费补发或退款,相关运费由平台承担。"
    },
    {
      "n": 2,
      "chunk_id": "1743",
      "section_path": "商品与购物 FAQ/发票如何开具",
      "question": "发票如何开具",
      "answer": "在「我的订单」-「申请开票」提交抬头与税号,电子发票将于 3 个工作日内发送至邮箱。"
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
  "elapsed_ms": 34713.115899823606,
  "judge_snapshot": {
    "prompt_version": "joint-generation-v2.1",
    "finish_reason": "stop"
  },
  "audit": {
    "audit_version": 1,
    "source_map_id": "378ae65f4ee735c6a8079070fbfcb5c21800c93f3318029e5f19836c32b5c2b4",
    "gold_groups": [],
    "answer_points": [],
    "candidate_ranking": [
      {
        "chunk_id": 1778,
        "score": 0.6460713148117065,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1743,
        "score": 0.5758640766143799,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1779,
        "score": 0.5668666362762451,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1771,
        "score": 0.5093562602996826,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1739,
        "score": 0.4919954538345337,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1736,
        "score": 0.47299909591674805,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1731,
        "score": 0.47143441438674927,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1732,
        "score": 0.4683113396167755,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1773,
        "score": 0.46406275033950806,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1767,
        "score": 0.4625740647315979,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1770,
        "score": 0.45951998233795166,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1765,
        "score": 0.45067259669303894,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1737,
        "score": 0.4483277499675751,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1748,
        "score": 0.44779449701309204,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1740,
        "score": 0.4439329504966736,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1750,
        "score": 0.44006818532943726,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1768,
        "score": 0.4366624355316162,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1766,
        "score": 0.4312855899333954,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1777,
        "score": 0.4283146858215332,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1769,
        "score": 0.4222894608974457,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1738,
        "score": 0.4221780300140381,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1749,
        "score": 0.41479384899139404,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1772,
        "score": 0.41299164295196533,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1735,
        "score": 0.4005711078643799,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1741,
        "score": 0.3995623290538788,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1744,
        "score": 0.3971923589706421,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1751,
        "score": 0.3969317078590393,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1746,
        "score": 0.3933674097061157,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1734,
        "score": 0.3871292173862457,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1776,
        "score": 0.386167973279953,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1742,
        "score": 0.3832434415817261,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1747,
        "score": 0.3829110562801361,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1775,
        "score": 0.3758304715156555,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1752,
        "score": 0.36886805295944214,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1774,
        "score": 0.3675192594528198,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1758,
        "score": 0.3672957420349121,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1733,
        "score": 0.3643520474433899,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1745,
        "score": 0.36295390129089355,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1757,
        "score": 0.36274346709251404,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1756,
        "score": 0.3547423481941223,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1762,
        "score": 0.35355210304260254,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1763,
        "score": 0.33501046895980835,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1761,
        "score": 0.32969874143600464,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1780,
        "score": 0.3276887536048889,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1764,
        "score": 0.32578036189079285,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1753,
        "score": 0.31920355558395386,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1755,
        "score": 0.30474111437797546,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1759,
        "score": 0.2920127213001251,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1754,
        "score": 0.2888384759426117,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1760,
        "score": 0.2883756458759308,
        "score_kind": "cosine"
      }
    ],
    "final_ranking": [
      {
        "chunk_id": 1778,
        "score": 0.6460713148117065,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1743,
        "score": 0.5758640766143799,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1779,
        "score": 0.5668666362762451,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1771,
        "score": 0.5093562602996826,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1739,
        "score": 0.4919954538345337,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1736,
        "score": 0.47299909591674805,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1731,
        "score": 0.47143441438674927,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1732,
        "score": 0.4683113396167755,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1773,
        "score": 0.46406275033950806,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1767,
        "score": 0.4625740647315979,
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
    1778,
    1779,
    1743,
    1748,
    1739,
    1750,
    1740,
    1767,
    1770,
    1731
  ],
  "final_ids": [
    1778,
    1779,
    1743,
    1748,
    1739,
    1750,
    1740,
    1767,
    1770,
    1731
  ],
  "prompt_citations": [
    {
      "n": 1,
      "chunk_id": "1778",
      "section_path": "开票细则/可开票类型",
      "question": "可开票类型",
      "answer": "本演示店提供电子普通发票、电子专用发票和纸质专用发票。电子普通发票可按订单申请；电子专票需要企业账户，申请前准备发票抬头及有效纳税人识别号，按申请页面提交资料。\n\n纸质专票仅企业账户可申请，申请时需提供企业开票资料、收件人和邮寄地址，快递费到付。资料审核通过后按开票流程寄出，不承诺快递送达日期。"
    },
    {
      "n": 3,
      "chunk_id": "1743",
      "section_path": "商品与购物 FAQ/发票如何开具",
      "question": "发票如何开具",
      "answer": "在「我的订单」-「申请开票」提交抬头与税号,电子发票将于 3 个工作日内发送至邮箱。"
    },
    {
      "n": 5,
      "chunk_id": "1739",
      "section_path": "商品与购物 FAQ/如何申请退款",
      "question": "如何申请退款",
      "answer": "在「我的订单」找到对应订单点击「申请退款」,按提示提交,审核通过后原路退回。"
    },
    {
      "n": 7,
      "chunk_id": "1740",
      "section_path": "商品与购物 FAQ/换货流程怎么走",
      "question": "换货流程怎么走",
      "answer": "收到商品 7 天内可申请换货,联系客服登记后将商品寄回,平台核验无误后补发新品。"
    },
    {
      "n": 9,
      "chunk_id": "1770",
      "section_path": "退货退款政策/质量问题与保修",
      "question": "质量问题与保修",
      "answer": "电子类商品自签收起保修 12 个月,保修期内非人为损坏可申请免费维修或换货;人为损坏、超保商品维修可能收取工本费。"
    },
    {
      "n": 10,
      "chunk_id": "1731",
      "section_path": "售后手册/常见问题处理时限",
      "question": "常见问题处理时限",
      "answer": "| 问题类型 | 首次响应 | 处理时限 |\n| --- | --- | --- |\n| 退款 | 2 小时 | 3 个工作日 |\n| 换货 | 2 小时 | 5 个工作日 |\n| 维修 | 4 小时 | 7 个工作日 |\n| 投诉 | 1 小时 | 3 个工作日 |\n| 发票 | 4 小时 | 3 个工作日 |\n| 物流异常 | 2 小时 | 5 个工作日 |\n| 商品咨询 | 1 小时 | 当日 |\n| 价格保护 | 2 小时 | 3 个工作日 |\n| 账户问题 | 2 小时 | 3 个工作日 |\n| 退换货运费 | 2 小时 | 3 个工作日 |\n| 缺货补发 | 2 小时 | 5 个工作日 |\n| 其他 | 4 小时 | 7 个工作日 |"
    },
    {
      "n": 8,
      "chunk_id": "1767",
      "section_path": "退货退款政策/换货政策/换货条件",
      "question": "换货条件",
      "answer": "收到商品 7 天内,商品完好且配件齐全的,可申请一次同款换货;不同型号或颜色需先退货再重新下单。"
    },
    {
      "n": 6,
      "chunk_id": "1750",
      "section_path": "商品与购物 FAQ/价格保护怎么申请",
      "question": "价格保护怎么申请",
      "answer": "自营商品支持下单后 7 天内价保,期间若同款降价可在「我的订单」-「申请价保」提交,差价将退回原支付渠道。"
    },
    {
      "n": 4,
      "chunk_id": "1748",
      "section_path": "商品与购物 FAQ/订单可以修改或取消吗",
      "question": "订单可以修改或取消吗",
      "answer": "订单未发货前可在「我的订单」自助取消;已发货订单无法修改收货信息,可拒收后走退款流程。修改商品数量需取消后重新下单。"
    },
    {
      "n": 2,
      "chunk_id": "1779",
      "section_path": "开票细则/开票时效",
      "question": "开票时效",
      "answer": "订单完成后 30 天内可在「我的订单」申请开票，超过 30 天需联系客服核实补开条件，不能直接承诺一定补开。\n\n有效资料审核通过后 3 个工作日内开出发票，电子发票发送至申请邮箱；纸质专票开出后安排邮寄，邮寄耗时不计入开票时限。发票抬头或税号填错时联系客服核实更正，不保证无需审核即可重开。"
    }
  ],
  "decision": {
    "useful": false,
    "reason": "证据只涉及开票类型与时效，无纸质发票遗失挂失证明的规定",
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
  "elapsed_ms": 42336.315699853,
  "judge_snapshot": {
    "prompt_version": "joint-generation-v2.1",
    "finish_reason": "stop"
  },
  "audit": {
    "audit_version": 1,
    "source_map_id": "378ae65f4ee735c6a8079070fbfcb5c21800c93f3318029e5f19836c32b5c2b4",
    "gold_groups": [],
    "answer_points": [],
    "candidate_ranking": [
      {
        "chunk_id": 1778,
        "score": 10.285421371459961,
        "score_kind": "bm25"
      },
      {
        "chunk_id": 1779,
        "score": 8.083020210266113,
        "score_kind": "bm25"
      },
      {
        "chunk_id": 1743,
        "score": 5.832973480224609,
        "score_kind": "bm25"
      },
      {
        "chunk_id": 1748,
        "score": 3.737774610519409,
        "score_kind": "bm25"
      },
      {
        "chunk_id": 1739,
        "score": 2.8332555294036865,
        "score_kind": "bm25"
      },
      {
        "chunk_id": 1750,
        "score": 2.6836564540863037,
        "score_kind": "bm25"
      },
      {
        "chunk_id": 1740,
        "score": 2.1490039825439453,
        "score_kind": "bm25"
      },
      {
        "chunk_id": 1767,
        "score": 2.071161985397339,
        "score_kind": "bm25"
      },
      {
        "chunk_id": 1770,
        "score": 1.9644274711608887,
        "score_kind": "bm25"
      },
      {
        "chunk_id": 1731,
        "score": 1.7175705432891846,
        "score_kind": "bm25"
      }
    ],
    "final_ranking": [
      {
        "chunk_id": 1778,
        "score": 10.285421371459961,
        "score_kind": "bm25"
      },
      {
        "chunk_id": 1779,
        "score": 8.083020210266113,
        "score_kind": "bm25"
      },
      {
        "chunk_id": 1743,
        "score": 5.832973480224609,
        "score_kind": "bm25"
      },
      {
        "chunk_id": 1748,
        "score": 3.737774610519409,
        "score_kind": "bm25"
      },
      {
        "chunk_id": 1739,
        "score": 2.8332555294036865,
        "score_kind": "bm25"
      },
      {
        "chunk_id": 1750,
        "score": 2.6836564540863037,
        "score_kind": "bm25"
      },
      {
        "chunk_id": 1740,
        "score": 2.1490039825439453,
        "score_kind": "bm25"
      },
      {
        "chunk_id": 1767,
        "score": 2.071161985397339,
        "score_kind": "bm25"
      },
      {
        "chunk_id": 1770,
        "score": 1.9644274711608887,
        "score_kind": "bm25"
      },
      {
        "chunk_id": 1731,
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
    1778,
    1743,
    1779,
    1739,
    1731,
    1748,
    1767,
    1770,
    1750,
    1740,
    1771,
    1736,
    1732,
    1773,
    1765,
    1737,
    1768,
    1766,
    1777,
    1769,
    1738,
    1749,
    1772,
    1735,
    1741,
    1744,
    1751,
    1746,
    1734,
    1776,
    1742,
    1747,
    1775,
    1752,
    1774,
    1758,
    1733,
    1745,
    1757,
    1756,
    1762,
    1763,
    1761,
    1780,
    1764,
    1753,
    1755,
    1759,
    1754,
    1760
  ],
  "final_ids": [
    1778,
    1743,
    1779,
    1739,
    1731,
    1748,
    1767,
    1770,
    1750,
    1740
  ],
  "prompt_citations": [
    {
      "n": 1,
      "chunk_id": "1778",
      "section_path": "开票细则/可开票类型",
      "question": "可开票类型",
      "answer": "本演示店提供电子普通发票、电子专用发票和纸质专用发票。电子普通发票可按订单申请；电子专票需要企业账户，申请前准备发票抬头及有效纳税人识别号，按申请页面提交资料。\n\n纸质专票仅企业账户可申请，申请时需提供企业开票资料、收件人和邮寄地址，快递费到付。资料审核通过后按开票流程寄出，不承诺快递送达日期。"
    },
    {
      "n": 3,
      "chunk_id": "1779",
      "section_path": "开票细则/开票时效",
      "question": "开票时效",
      "answer": "订单完成后 30 天内可在「我的订单」申请开票，超过 30 天需联系客服核实补开条件，不能直接承诺一定补开。\n\n有效资料审核通过后 3 个工作日内开出发票，电子发票发送至申请邮箱；纸质专票开出后安排邮寄，邮寄耗时不计入开票时限。发票抬头或税号填错时联系客服核实更正，不保证无需审核即可重开。"
    },
    {
      "n": 5,
      "chunk_id": "1731",
      "section_path": "售后手册/常见问题处理时限",
      "question": "常见问题处理时限",
      "answer": "| 问题类型 | 首次响应 | 处理时限 |\n| --- | --- | --- |\n| 退款 | 2 小时 | 3 个工作日 |\n| 换货 | 2 小时 | 5 个工作日 |\n| 维修 | 4 小时 | 7 个工作日 |\n| 投诉 | 1 小时 | 3 个工作日 |\n| 发票 | 4 小时 | 3 个工作日 |\n| 物流异常 | 2 小时 | 5 个工作日 |\n| 商品咨询 | 1 小时 | 当日 |\n| 价格保护 | 2 小时 | 3 个工作日 |\n| 账户问题 | 2 小时 | 3 个工作日 |\n| 退换货运费 | 2 小时 | 3 个工作日 |\n| 缺货补发 | 2 小时 | 5 个工作日 |\n| 其他 | 4 小时 | 7 个工作日 |"
    },
    {
      "n": 7,
      "chunk_id": "1767",
      "section_path": "退货退款政策/换货政策/换货条件",
      "question": "换货条件",
      "answer": "收到商品 7 天内,商品完好且配件齐全的,可申请一次同款换货;不同型号或颜色需先退货再重新下单。"
    },
    {
      "n": 9,
      "chunk_id": "1750",
      "section_path": "商品与购物 FAQ/价格保护怎么申请",
      "question": "价格保护怎么申请",
      "answer": "自营商品支持下单后 7 天内价保,期间若同款降价可在「我的订单」-「申请价保」提交,差价将退回原支付渠道。"
    },
    {
      "n": 10,
      "chunk_id": "1740",
      "section_path": "商品与购物 FAQ/换货流程怎么走",
      "question": "换货流程怎么走",
      "answer": "收到商品 7 天内可申请换货,联系客服登记后将商品寄回,平台核验无误后补发新品。"
    },
    {
      "n": 8,
      "chunk_id": "1770",
      "section_path": "退货退款政策/质量问题与保修",
      "question": "质量问题与保修",
      "answer": "电子类商品自签收起保修 12 个月,保修期内非人为损坏可申请免费维修或换货;人为损坏、超保商品维修可能收取工本费。"
    },
    {
      "n": 6,
      "chunk_id": "1748",
      "section_path": "商品与购物 FAQ/订单可以修改或取消吗",
      "question": "订单可以修改或取消吗",
      "answer": "订单未发货前可在「我的订单」自助取消;已发货订单无法修改收货信息,可拒收后走退款流程。修改商品数量需取消后重新下单。"
    },
    {
      "n": 4,
      "chunk_id": "1739",
      "section_path": "商品与购物 FAQ/如何申请退款",
      "question": "如何申请退款",
      "answer": "在「我的订单」找到对应订单点击「申请退款」,按提示提交,审核通过后原路退回。"
    },
    {
      "n": 2,
      "chunk_id": "1743",
      "section_path": "商品与购物 FAQ/发票如何开具",
      "question": "发票如何开具",
      "answer": "在「我的订单」-「申请开票」提交抬头与税号,电子发票将于 3 个工作日内发送至邮箱。"
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
  "elapsed_ms": 34893.51440011524,
  "judge_snapshot": {
    "prompt_version": "joint-generation-v2.1",
    "finish_reason": "stop"
  },
  "audit": {
    "audit_version": 1,
    "source_map_id": "378ae65f4ee735c6a8079070fbfcb5c21800c93f3318029e5f19836c32b5c2b4",
    "gold_groups": [],
    "answer_points": [],
    "candidate_ranking": [
      {
        "chunk_id": 1778,
        "score": 0.032786883413791656,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1743,
        "score": 0.0320020467042923,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1779,
        "score": 0.0320020467042923,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1739,
        "score": 0.03076923079788685,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1731,
        "score": 0.02921108715236187,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1748,
        "score": 0.029138512909412384,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1767,
        "score": 0.028991596773266792,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1770,
        "score": 0.028577260673046112,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1750,
        "score": 0.02830941043794155,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1740,
        "score": 0.028258707374334335,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1771,
        "score": 0.015625,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1736,
        "score": 0.01515151560306549,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1732,
        "score": 0.014705882407724857,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1773,
        "score": 0.014492753893136978,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1765,
        "score": 0.013888888992369175,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1737,
        "score": 0.013698630034923553,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1768,
        "score": 0.012987012974917889,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1766,
        "score": 0.012820512987673283,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1777,
        "score": 0.012658228166401386,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1769,
        "score": 0.012500000186264515,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1738,
        "score": 0.012345679104328156,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1749,
        "score": 0.012195121496915817,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1772,
        "score": 0.012048192322254181,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1735,
        "score": 0.011904762126505375,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1741,
        "score": 0.0117647061124444,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1744,
        "score": 0.011627906933426857,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1751,
        "score": 0.01149425283074379,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1746,
        "score": 0.011363636702299118,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1734,
        "score": 0.01123595517128706,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1776,
        "score": 0.011111111380159855,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1742,
        "score": 0.010989011265337467,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1747,
        "score": 0.010869565419852734,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1775,
        "score": 0.01075268816202879,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1752,
        "score": 0.010638297535479069,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1774,
        "score": 0.010526316240429878,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1758,
        "score": 0.010416666977107525,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1733,
        "score": 0.010309278033673763,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1745,
        "score": 0.010204081423580647,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1757,
        "score": 0.010101010091602802,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1756,
        "score": 0.009999999776482582,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1762,
        "score": 0.009900989942252636,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1763,
        "score": 0.009803921915590763,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1761,
        "score": 0.009708737954497337,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1780,
        "score": 0.009615384973585606,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1764,
        "score": 0.009523809887468815,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1753,
        "score": 0.009433962404727936,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1755,
        "score": 0.009345794096589088,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1759,
        "score": 0.009259259328246117,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1754,
        "score": 0.00917431153357029,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1760,
        "score": 0.00909090880304575,
        "score_kind": "rrf"
      }
    ],
    "final_ranking": [
      {
        "chunk_id": 1778,
        "score": 0.032786883413791656,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1743,
        "score": 0.0320020467042923,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1779,
        "score": 0.0320020467042923,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1739,
        "score": 0.03076923079788685,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1731,
        "score": 0.02921108715236187,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1748,
        "score": 0.029138512909412384,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1767,
        "score": 0.028991596773266792,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1770,
        "score": 0.028577260673046112,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1750,
        "score": 0.02830941043794155,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1740,
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
    1778,
    1743,
    1779,
    1739,
    1731,
    1748,
    1767,
    1770,
    1750,
    1740,
    1771,
    1736,
    1732,
    1773,
    1765,
    1737,
    1768,
    1766,
    1777,
    1769,
    1738,
    1749,
    1772,
    1735,
    1741,
    1744,
    1751,
    1746,
    1734,
    1776,
    1742,
    1747,
    1775,
    1752,
    1774,
    1758,
    1733,
    1745,
    1757,
    1756,
    1762,
    1763,
    1761,
    1780,
    1764,
    1753,
    1755,
    1759,
    1754,
    1760
  ],
  "final_ids": [
    1779,
    1778,
    1743,
    1770,
    1771,
    1739,
    1765,
    1766,
    1732,
    1731
  ],
  "prompt_citations": [
    {
      "n": 1,
      "chunk_id": "1779",
      "section_path": "开票细则/开票时效",
      "question": "开票时效",
      "answer": "订单完成后 30 天内可在「我的订单」申请开票，超过 30 天需联系客服核实补开条件，不能直接承诺一定补开。\n\n有效资料审核通过后 3 个工作日内开出发票，电子发票发送至申请邮箱；纸质专票开出后安排邮寄，邮寄耗时不计入开票时限。发票抬头或税号填错时联系客服核实更正，不保证无需审核即可重开。"
    },
    {
      "n": 3,
      "chunk_id": "1743",
      "section_path": "商品与购物 FAQ/发票如何开具",
      "question": "发票如何开具",
      "answer": "在「我的订单」-「申请开票」提交抬头与税号,电子发票将于 3 个工作日内发送至邮箱。"
    },
    {
      "n": 5,
      "chunk_id": "1771",
      "section_path": "退货退款政策/运输破损处理",
      "question": "运输破损处理",
      "answer": "商品运输途中破损的,请在签收后 48 小时内联系客服并提供开箱视频与照片,核实后可免费补发或退款,相关运费由平台承担。"
    },
    {
      "n": 7,
      "chunk_id": "1765",
      "section_path": "退货退款政策/无理由退货/适用范围",
      "question": "适用范围",
      "answer": "自签收之日起 7 天内,商品完好、不影响二次销售的,支持无理由退货。定制类、生鲜类商品除外。"
    },
    {
      "n": 9,
      "chunk_id": "1732",
      "section_path": "售后手册/保修说明",
      "question": "保修说明",
      "answer": "电子类商品保修 12 个月,自签收日起算;人为损坏不在保修范围。"
    },
    {
      "n": 10,
      "chunk_id": "1731",
      "section_path": "售后手册/常见问题处理时限",
      "question": "常见问题处理时限",
      "answer": "| 问题类型 | 首次响应 | 处理时限 |\n| --- | --- | --- |\n| 退款 | 2 小时 | 3 个工作日 |\n| 换货 | 2 小时 | 5 个工作日 |\n| 维修 | 4 小时 | 7 个工作日 |\n| 投诉 | 1 小时 | 3 个工作日 |\n| 发票 | 4 小时 | 3 个工作日 |\n| 物流异常 | 2 小时 | 5 个工作日 |\n| 商品咨询 | 1 小时 | 当日 |\n| 价格保护 | 2 小时 | 3 个工作日 |\n| 账户问题 | 2 小时 | 3 个工作日 |\n| 退换货运费 | 2 小时 | 3 个工作日 |\n| 缺货补发 | 2 小时 | 5 个工作日 |\n| 其他 | 4 小时 | 7 个工作日 |"
    },
    {
      "n": 8,
      "chunk_id": "1766",
      "section_path": "退货退款政策/无理由退货/退款时效",
      "question": "退款时效",
      "answer": "退货商品经平台核验通过后,退款原路退回,到账时效以平台售后规则为准。"
    },
    {
      "n": 6,
      "chunk_id": "1739",
      "section_path": "商品与购物 FAQ/如何申请退款",
      "question": "如何申请退款",
      "answer": "在「我的订单」找到对应订单点击「申请退款」,按提示提交,审核通过后原路退回。"
    },
    {
      "n": 4,
      "chunk_id": "1770",
      "section_path": "退货退款政策/质量问题与保修",
      "question": "质量问题与保修",
      "answer": "电子类商品自签收起保修 12 个月,保修期内非人为损坏可申请免费维修或换货;人为损坏、超保商品维修可能收取工本费。"
    },
    {
      "n": 2,
      "chunk_id": "1778",
      "section_path": "开票细则/可开票类型",
      "question": "可开票类型",
      "answer": "本演示店提供电子普通发票、电子专用发票和纸质专用发票。电子普通发票可按订单申请；电子专票需要企业账户，申请前准备发票抬头及有效纳税人识别号，按申请页面提交资料。\n\n纸质专票仅企业账户可申请，申请时需提供企业开票资料、收件人和邮寄地址，快递费到付。资料审核通过后按开票流程寄出，不承诺快递送达日期。"
    }
  ],
  "decision": {
    "useful": false,
    "reason": "证据无发票挂失证明内容",
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
  "elapsed_ms": 37008.60489998013,
  "judge_snapshot": {
    "prompt_version": "joint-generation-v2.1",
    "finish_reason": "stop"
  },
  "audit": {
    "audit_version": 1,
    "source_map_id": "378ae65f4ee735c6a8079070fbfcb5c21800c93f3318029e5f19836c32b5c2b4",
    "gold_groups": [],
    "answer_points": [],
    "candidate_ranking": [
      {
        "chunk_id": 1778,
        "score": 0.032786883413791656,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1743,
        "score": 0.0320020467042923,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1779,
        "score": 0.0320020467042923,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1739,
        "score": 0.03076923079788685,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1731,
        "score": 0.02921108715236187,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1748,
        "score": 0.029138512909412384,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1767,
        "score": 0.028991596773266792,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1770,
        "score": 0.028577260673046112,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1750,
        "score": 0.02830941043794155,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1740,
        "score": 0.028258707374334335,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1771,
        "score": 0.015625,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1736,
        "score": 0.01515151560306549,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1732,
        "score": 0.014705882407724857,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1773,
        "score": 0.014492753893136978,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1765,
        "score": 0.013888888992369175,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1737,
        "score": 0.013698630034923553,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1768,
        "score": 0.012987012974917889,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1766,
        "score": 0.012820512987673283,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1777,
        "score": 0.012658228166401386,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1769,
        "score": 0.012500000186264515,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1738,
        "score": 0.012345679104328156,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1749,
        "score": 0.012195121496915817,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1772,
        "score": 0.012048192322254181,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1735,
        "score": 0.011904762126505375,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1741,
        "score": 0.0117647061124444,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1744,
        "score": 0.011627906933426857,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1751,
        "score": 0.01149425283074379,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1746,
        "score": 0.011363636702299118,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1734,
        "score": 0.01123595517128706,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1776,
        "score": 0.011111111380159855,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1742,
        "score": 0.010989011265337467,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1747,
        "score": 0.010869565419852734,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1775,
        "score": 0.01075268816202879,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1752,
        "score": 0.010638297535479069,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1774,
        "score": 0.010526316240429878,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1758,
        "score": 0.010416666977107525,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1733,
        "score": 0.010309278033673763,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1745,
        "score": 0.010204081423580647,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1757,
        "score": 0.010101010091602802,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1756,
        "score": 0.009999999776482582,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1762,
        "score": 0.009900989942252636,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1763,
        "score": 0.009803921915590763,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1761,
        "score": 0.009708737954497337,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1780,
        "score": 0.009615384973585606,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1764,
        "score": 0.009523809887468815,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1753,
        "score": 0.009433962404727936,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1755,
        "score": 0.009345794096589088,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1759,
        "score": 0.009259259328246117,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1754,
        "score": 0.00917431153357029,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1760,
        "score": 0.00909090880304575,
        "score_kind": "rrf"
      }
    ],
    "final_ranking": [
      {
        "chunk_id": 1779,
        "score": 0.09022712707519531,
        "score_kind": "rerank"
      },
      {
        "chunk_id": 1778,
        "score": 0.03995951637625694,
        "score_kind": "rerank"
      },
      {
        "chunk_id": 1743,
        "score": 0.0009899823926389217,
        "score_kind": "rerank"
      },
      {
        "chunk_id": 1770,
        "score": 0.0005968508194200695,
        "score_kind": "rerank"
      },
      {
        "chunk_id": 1771,
        "score": 0.000394607603084296,
        "score_kind": "rerank"
      },
      {
        "chunk_id": 1739,
        "score": 0.0002391472371527925,
        "score_kind": "rerank"
      },
      {
        "chunk_id": 1765,
        "score": 0.00023546224110759795,
        "score_kind": "rerank"
      },
      {
        "chunk_id": 1766,
        "score": 0.00021747639402747154,
        "score_kind": "rerank"
      },
      {
        "chunk_id": 1732,
        "score": 0.00021451065549626946,
        "score_kind": "rerank"
      },
      {
        "chunk_id": 1731,
        "score": 0.0001683057489572093,
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
  "status": "judge_error",
  "stage": "judgment",
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
          1765
        ],
        [
          1738
        ]
      ]
    },
    {
      "group_id": "g2",
      "alternatives": [
        [
          1769
        ]
      ]
    },
    {
      "group_id": "g3",
      "alternatives": [
        [
          1766
        ]
      ]
    }
  ],
  "candidate_ids": [
    1769,
    1771,
    1768,
    1765,
    1766,
    1738,
    1740,
    1773,
    1742,
    1770,
    1731,
    1741,
    1767,
    1736,
    1739,
    1737,
    1749,
    1750,
    1747,
    1751,
    1772,
    1779,
    1732,
    1748,
    1776,
    1743,
    1777,
    1735,
    1744,
    1774,
    1745,
    1775,
    1778,
    1746,
    1734,
    1753,
    1755,
    1758,
    1757,
    1756,
    1754,
    1733,
    1762,
    1780,
    1752,
    1760,
    1763,
    1761,
    1764,
    1759
  ],
  "final_ids": [
    1769,
    1771,
    1768,
    1765,
    1766,
    1738,
    1740,
    1773,
    1742,
    1770
  ],
  "prompt_citations": [
    {
      "n": 1,
      "chunk_id": "1769",
      "section_path": "退货退款政策/退换货运费承担",
      "question": "退换货运费承担",
      "answer": "无理由退货的退回运费由买家承担;因商品质量问题、发错货、少发漏发导致的退换货,运费由平台承担。运费承担以平台售后规则最终判定为准。"
    },
    {
      "n": 3,
      "chunk_id": "1768",
      "section_path": "退货退款政策/换货政策/换货运费",
      "question": "换货运费",
      "answer": "非质量问题的换货,往返运费由买家承担;因质量问题或发错货的换货,往返运费由平台承担。"
    },
    {
      "n": 5,
      "chunk_id": "1766",
      "section_path": "退货退款政策/无理由退货/退款时效",
      "question": "退款时效",
      "answer": "退货商品经平台核验通过后,退款原路退回,到账时效以平台售后规则为准。"
    },
    {
      "n": 7,
      "chunk_id": "1740",
      "section_path": "商品与购物 FAQ/换货流程怎么走",
      "question": "换货流程怎么走",
      "answer": "收到商品 7 天内可申请换货,联系客服登记后将商品寄回,平台核验无误后补发新品。"
    },
    {
      "n": 9,
      "chunk_id": "1742",
      "section_path": "商品与购物 FAQ/运费怎么算",
      "question": "运费怎么算",
      "answer": "单笔订单满 99 元包邮,未满收取 10 元运费,偏远地区运费另计。邮费即运费,按此规则收取。"
    },
    {
      "n": 10,
      "chunk_id": "1770",
      "section_path": "退货退款政策/质量问题与保修",
      "question": "质量问题与保修",
      "answer": "电子类商品自签收起保修 12 个月,保修期内非人为损坏可申请免费维修或换货;人为损坏、超保商品维修可能收取工本费。"
    },
    {
      "n": 8,
      "chunk_id": "1773",
      "section_path": "退货退款政策/预售与定金",
      "question": "预售与定金",
      "answer": "预售商品以详情页标注的时间发货;定金支付后不支持无理由退定金,尾款未按时支付的,定金按活动规则处理。"
    },
    {
      "n": 6,
      "chunk_id": "1738",
      "section_path": "商品与购物 FAQ/退货政策是什么",
      "question": "退货政策是什么",
      "answer": "支持 7 天无理由退货,商品需保持完好、不影响二次销售,具体以平台售后规则为准。"
    },
    {
      "n": 4,
      "chunk_id": "1765",
      "section_path": "退货退款政策/无理由退货/适用范围",
      "question": "适用范围",
      "answer": "自签收之日起 7 天内,商品完好、不影响二次销售的,支持无理由退货。定制类、生鲜类商品除外。"
    },
    {
      "n": 2,
      "chunk_id": "1771",
      "section_path": "退货退款政策/运输破损处理",
      "question": "运输破损处理",
      "answer": "商品运输途中破损的,请在签收后 48 小时内联系客服并提供开箱视频与照片,核实后可免费补发或退款,相关运费由平台承担。"
    }
  ],
  "decision": {
    "useful": true,
    "reason": "运费承担与退款时效均有对应证据",
    "response_kind": "knowledge",
    "source": null
  },
  "answer": "您好！关于您的问题：\n\n**运费承担**：由于您是无理由退货（不想要了），寄回的运费需要由买家自行承担；如果是商品质量问题、发错货、少发漏发等情况，运费则由平台承担，最终以平台售后规则判定为准 [1]。\n\n**退款时效**：退货商品经平台核验通过后，退款将原路退回，具体到账时效以平台售后规则为准 [5]，我们无法承诺具体到账日期，请您理解。\n\n另外提醒您：无理由退货需在签收后 7 天内申请，且商品需保持完好、不影响二次销售 [4]。\n\n请问您需要我为您登记退货申请吗？",
  "point_verdicts": null,
  "claim_verdicts": null,
  "metrics": {
    "recall_at_5": 1.0,
    "recall_at_10": 1.0,
    "mrr_at_10": 1.0,
    "all_groups_hit_at_5": 1.0,
    "all_groups_hit_at_10": 1.0,
    "candidate_group_coverage": 1.0,
    "prompt_group_coverage": 1.0,
    "answer_point_coverage": null,
    "faithfulness": null,
    "absent_refusal_rate": null,
    "answerable_false_refusal_rate": 0.0
  },
  "error": {
    "code": "judgment_error",
    "type": "JudgeError",
    "message": "该阶段执行失败"
  },
  "elapsed_ms": 65976.89279983751,
  "judge_snapshot": {
    "prompt_version": "joint-generation-v2.1",
    "finish_reason": "length"
  },
  "audit": {
    "audit_version": 1,
    "source_map_id": "378ae65f4ee735c6a8079070fbfcb5c21800c93f3318029e5f19836c32b5c2b4",
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
        "chunk_id": 1769,
        "score": 0.737133264541626,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1771,
        "score": 0.7230391502380371,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1768,
        "score": 0.7014483213424683,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1765,
        "score": 0.6783180832862854,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1766,
        "score": 0.6764342188835144,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1738,
        "score": 0.6754489541053772,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1740,
        "score": 0.6569998264312744,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1773,
        "score": 0.6457812786102295,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1742,
        "score": 0.6393616795539856,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1770,
        "score": 0.6383430361747742,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1731,
        "score": 0.6368440389633179,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1741,
        "score": 0.6317943930625916,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1767,
        "score": 0.6221569776535034,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1736,
        "score": 0.6189490556716919,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1739,
        "score": 0.6125789284706116,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1737,
        "score": 0.6121077537536621,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1749,
        "score": 0.6097642183303833,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1750,
        "score": 0.6039755344390869,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1747,
        "score": 0.6020753979682922,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1751,
        "score": 0.595412015914917,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1772,
        "score": 0.5927598476409912,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1779,
        "score": 0.5711288452148438,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1732,
        "score": 0.5705702900886536,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1748,
        "score": 0.5658526420593262,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1776,
        "score": 0.5500414371490479,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1743,
        "score": 0.5331028699874878,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1777,
        "score": 0.5211403369903564,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1735,
        "score": 0.4981663227081299,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1744,
        "score": 0.49812501668930054,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1774,
        "score": 0.46587055921554565,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1745,
        "score": 0.4591333270072937,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1775,
        "score": 0.4567941427230835,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1778,
        "score": 0.45207417011260986,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1746,
        "score": 0.44950807094573975,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1734,
        "score": 0.43748342990875244,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1753,
        "score": 0.43041378259658813,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1755,
        "score": 0.4211339056491852,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1758,
        "score": 0.4114055037498474,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1757,
        "score": 0.4039028286933899,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1756,
        "score": 0.39622408151626587,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1754,
        "score": 0.38944557309150696,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1733,
        "score": 0.38788095116615295,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1762,
        "score": 0.36553987860679626,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1780,
        "score": 0.36408042907714844,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1752,
        "score": 0.3582310080528259,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1760,
        "score": 0.3511568009853363,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1763,
        "score": 0.3440558612346649,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1761,
        "score": 0.3353283703327179,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1764,
        "score": 0.33213144540786743,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1759,
        "score": 0.32241925597190857,
        "score_kind": "cosine"
      }
    ],
    "final_ranking": [
      {
        "chunk_id": 1769,
        "score": 0.737133264541626,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1771,
        "score": 0.7230391502380371,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1768,
        "score": 0.7014483213424683,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1765,
        "score": 0.6783180832862854,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1766,
        "score": 0.6764342188835144,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1738,
        "score": 0.6754489541053772,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1740,
        "score": 0.6569998264312744,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1773,
        "score": 0.6457812786102295,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1742,
        "score": 0.6393616795539856,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1770,
        "score": 0.6383430361747742,
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
  "status": "judge_error",
  "stage": "judgment",
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
          1765
        ],
        [
          1738
        ]
      ]
    },
    {
      "group_id": "g2",
      "alternatives": [
        [
          1769
        ]
      ]
    },
    {
      "group_id": "g3",
      "alternatives": [
        [
          1766
        ]
      ]
    }
  ],
  "candidate_ids": [
    1769,
    1768,
    1771,
    1772,
    1741,
    1765,
    1749,
    1751,
    1773,
    1777,
    1738,
    1767,
    1742,
    1747,
    1780,
    1774,
    1766,
    1779,
    1737,
    1776,
    1770,
    1732,
    1731,
    1744,
    1760,
    1739,
    1775,
    1752,
    1743,
    1754,
    1750,
    1735,
    1746,
    1748,
    1734,
    1778
  ],
  "final_ids": [
    1769,
    1768,
    1771,
    1772,
    1741,
    1765,
    1749,
    1751,
    1773,
    1777
  ],
  "prompt_citations": [
    {
      "n": 1,
      "chunk_id": "1769",
      "section_path": "退货退款政策/退换货运费承担",
      "question": "退换货运费承担",
      "answer": "无理由退货的退回运费由买家承担;因商品质量问题、发错货、少发漏发导致的退换货,运费由平台承担。运费承担以平台售后规则最终判定为准。"
    },
    {
      "n": 3,
      "chunk_id": "1771",
      "section_path": "退货退款政策/运输破损处理",
      "question": "运输破损处理",
      "answer": "商品运输途中破损的,请在签收后 48 小时内联系客服并提供开箱视频与照片,核实后可免费补发或退款,相关运费由平台承担。"
    },
    {
      "n": 5,
      "chunk_id": "1741",
      "section_path": "商品与购物 FAQ/发货时效多久",
      "question": "发货时效多久",
      "answer": "现货商品付款后 48 小时内发货,预售商品以商品详情页标注的发货时间为准。"
    },
    {
      "n": 7,
      "chunk_id": "1749",
      "section_path": "商品与购物 FAQ/商品缺货多久补货",
      "question": "商品缺货多久补货",
      "answer": "现货售罄的商品通常 3 至 7 天内补货,可在商品页点击「到货通知」,补货后系统会推送提醒。"
    },
    {
      "n": 9,
      "chunk_id": "1773",
      "section_path": "退货退款政策/预售与定金",
      "question": "预售与定金",
      "answer": "预售商品以详情页标注的时间发货;定金支付后不支持无理由退定金,尾款未按时支付的,定金按活动规则处理。"
    },
    {
      "n": 10,
      "chunk_id": "1777",
      "section_path": "积分规则/积分怎么用",
      "question": "积分怎么用",
      "answer": "积分可在结算时抵扣商品金额，100 积分抵 1 元现金，单笔订单最多抵 30 元，不用于抵扣偏远地区附加运费，也不支持直接提现。\n\n2000 积分可兑换自动饮水机滤芯 3 片，该兑换套装适用于 MH-W40，普通配送地区包邮；偏远地区附加配送费仍需按页面规则确认。MH-W40 的滤芯更换周期以商品规格手册为准。\n\n800 积分可兑换猫零食小样，普通配送地区另收 6 元运费；该兑换不直接套用普通购物订单的满 99 元包邮规则。兑换商品、可用库存及偏远地区配送规则以兑换页面标注为准。"
    },
    {
      "n": 8,
      "chunk_id": "1751",
      "section_path": "商品与购物 FAQ/会员运费权益",
      "question": "会员运费权益",
      "answer": "金卡会员每月享 3 次免运费权益,银卡会员享 1 次;权益不与偏远地区附加运费冲抵,当月未用完不结转。"
    },
    {
      "n": 6,
      "chunk_id": "1765",
      "section_path": "退货退款政策/无理由退货/适用范围",
      "question": "适用范围",
      "answer": "自签收之日起 7 天内,商品完好、不影响二次销售的,支持无理由退货。定制类、生鲜类商品除外。"
    },
    {
      "n": 4,
      "chunk_id": "1772",
      "section_path": "退货退款政策/不支持退货的商品",
      "question": "不支持退货的商品",
      "answer": "定制类、生鲜类、已拆封的猫砂等消耗品,以及标注「不支持无理由退货」的商品,非质量问题不支持退货。"
    },
    {
      "n": 2,
      "chunk_id": "1768",
      "section_path": "退货退款政策/换货政策/换货运费",
      "question": "换货运费",
      "answer": "非质量问题的换货,往返运费由买家承担;因质量问题或发错货的换货,往返运费由平台承担。"
    }
  ],
  "decision": {
    "useful": false,
    "reason": "运费承担有证据,退款到账时效无证据",
    "response_kind": "knowledge",
    "source": "self_check"
  },
  "answer": "目前的知识资料不足以确认这个问题，我无法给出可靠答案。请补充具体商品或适用条件，或联系人工客服确认。",
  "point_verdicts": null,
  "claim_verdicts": null,
  "metrics": {
    "recall_at_5": 0.3333333333333333,
    "recall_at_10": 0.6666666666666666,
    "mrr_at_10": 1.0,
    "all_groups_hit_at_5": 0.0,
    "all_groups_hit_at_10": 0.0,
    "candidate_group_coverage": 1.0,
    "prompt_group_coverage": 0.6666666666666666,
    "answer_point_coverage": null,
    "faithfulness": null,
    "absent_refusal_rate": null,
    "answerable_false_refusal_rate": 1.0
  },
  "error": {
    "code": "judgment_error",
    "type": "JudgeError",
    "message": "该阶段执行失败"
  },
  "elapsed_ms": 60575.65669971518,
  "judge_snapshot": {
    "prompt_version": "joint-generation-v2.1",
    "finish_reason": "length"
  },
  "audit": {
    "audit_version": 1,
    "source_map_id": "378ae65f4ee735c6a8079070fbfcb5c21800c93f3318029e5f19836c32b5c2b4",
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
        "chunk_id": 1769,
        "score": 10.676090240478516,
        "score_kind": "bm25"
      },
      {
        "chunk_id": 1768,
        "score": 9.836376190185547,
        "score_kind": "bm25"
      },
      {
        "chunk_id": 1771,
        "score": 7.268333435058594,
        "score_kind": "bm25"
      },
      {
        "chunk_id": 1772,
        "score": 5.63097620010376,
        "score_kind": "bm25"
      },
      {
        "chunk_id": 1741,
        "score": 4.741880416870117,
        "score_kind": "bm25"
      },
      {
        "chunk_id": 1765,
        "score": 4.518306732177734,
        "score_kind": "bm25"
      },
      {
        "chunk_id": 1749,
        "score": 4.484236717224121,
        "score_kind": "bm25"
      },
      {
        "chunk_id": 1751,
        "score": 4.33558988571167,
        "score_kind": "bm25"
      },
      {
        "chunk_id": 1773,
        "score": 4.041518211364746,
        "score_kind": "bm25"
      },
      {
        "chunk_id": 1777,
        "score": 3.6735312938690186,
        "score_kind": "bm25"
      },
      {
        "chunk_id": 1738,
        "score": 3.423988103866577,
        "score_kind": "bm25"
      },
      {
        "chunk_id": 1767,
        "score": 3.1294915676116943,
        "score_kind": "bm25"
      },
      {
        "chunk_id": 1742,
        "score": 3.048265218734741,
        "score_kind": "bm25"
      },
      {
        "chunk_id": 1747,
        "score": 2.904369831085205,
        "score_kind": "bm25"
      },
      {
        "chunk_id": 1780,
        "score": 2.8818564414978027,
        "score_kind": "bm25"
      },
      {
        "chunk_id": 1774,
        "score": 2.7881808280944824,
        "score_kind": "bm25"
      },
      {
        "chunk_id": 1766,
        "score": 2.4312641620635986,
        "score_kind": "bm25"
      },
      {
        "chunk_id": 1779,
        "score": 1.9325504302978516,
        "score_kind": "bm25"
      },
      {
        "chunk_id": 1737,
        "score": 1.8424832820892334,
        "score_kind": "bm25"
      },
      {
        "chunk_id": 1776,
        "score": 1.823819637298584,
        "score_kind": "bm25"
      },
      {
        "chunk_id": 1770,
        "score": 1.5415995121002197,
        "score_kind": "bm25"
      },
      {
        "chunk_id": 1732,
        "score": 1.3018649816513062,
        "score_kind": "bm25"
      },
      {
        "chunk_id": 1731,
        "score": 1.1889352798461914,
        "score_kind": "bm25"
      },
      {
        "chunk_id": 1744,
        "score": 1.1214089393615723,
        "score_kind": "bm25"
      },
      {
        "chunk_id": 1760,
        "score": 1.0838499069213867,
        "score_kind": "bm25"
      },
      {
        "chunk_id": 1739,
        "score": 1.0660427808761597,
        "score_kind": "bm25"
      },
      {
        "chunk_id": 1775,
        "score": 1.0572911500930786,
        "score_kind": "bm25"
      },
      {
        "chunk_id": 1752,
        "score": 1.0359933376312256,
        "score_kind": "bm25"
      },
      {
        "chunk_id": 1743,
        "score": 1.0168840885162354,
        "score_kind": "bm25"
      },
      {
        "chunk_id": 1754,
        "score": 0.984889805316925,
        "score_kind": "bm25"
      },
      {
        "chunk_id": 1750,
        "score": 0.9807054996490479,
        "score_kind": "bm25"
      },
      {
        "chunk_id": 1735,
        "score": 0.9720594882965088,
        "score_kind": "bm25"
      },
      {
        "chunk_id": 1746,
        "score": 0.9155580401420593,
        "score_kind": "bm25"
      },
      {
        "chunk_id": 1748,
        "score": 0.9155580401420593,
        "score_kind": "bm25"
      },
      {
        "chunk_id": 1734,
        "score": 0.8170415759086609,
        "score_kind": "bm25"
      },
      {
        "chunk_id": 1778,
        "score": 0.7920446395874023,
        "score_kind": "bm25"
      }
    ],
    "final_ranking": [
      {
        "chunk_id": 1769,
        "score": 10.676090240478516,
        "score_kind": "bm25"
      },
      {
        "chunk_id": 1768,
        "score": 9.836376190185547,
        "score_kind": "bm25"
      },
      {
        "chunk_id": 1771,
        "score": 7.268333435058594,
        "score_kind": "bm25"
      },
      {
        "chunk_id": 1772,
        "score": 5.63097620010376,
        "score_kind": "bm25"
      },
      {
        "chunk_id": 1741,
        "score": 4.741880416870117,
        "score_kind": "bm25"
      },
      {
        "chunk_id": 1765,
        "score": 4.518306732177734,
        "score_kind": "bm25"
      },
      {
        "chunk_id": 1749,
        "score": 4.484236717224121,
        "score_kind": "bm25"
      },
      {
        "chunk_id": 1751,
        "score": 4.33558988571167,
        "score_kind": "bm25"
      },
      {
        "chunk_id": 1773,
        "score": 4.041518211364746,
        "score_kind": "bm25"
      },
      {
        "chunk_id": 1777,
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
  "status": "judge_error",
  "stage": "judgment",
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
          1765
        ],
        [
          1738
        ]
      ]
    },
    {
      "group_id": "g2",
      "alternatives": [
        [
          1769
        ]
      ]
    },
    {
      "group_id": "g3",
      "alternatives": [
        [
          1766
        ]
      ]
    }
  ],
  "candidate_ids": [
    1769,
    1768,
    1771,
    1765,
    1741,
    1738,
    1773,
    1766,
    1742,
    1772,
    1749,
    1767,
    1751,
    1770,
    1747,
    1731,
    1737,
    1777,
    1779,
    1739,
    1774,
    1776,
    1732,
    1750,
    1744,
    1780,
    1743,
    1748,
    1775,
    1735,
    1746,
    1760,
    1778,
    1734,
    1754,
    1752,
    1740,
    1736,
    1745,
    1753,
    1755,
    1758,
    1757,
    1756,
    1733,
    1762,
    1763,
    1761,
    1764,
    1759
  ],
  "final_ids": [
    1769,
    1768,
    1771,
    1765,
    1741,
    1738,
    1773,
    1766,
    1742,
    1772
  ],
  "prompt_citations": [
    {
      "n": 1,
      "chunk_id": "1769",
      "section_path": "退货退款政策/退换货运费承担",
      "question": "退换货运费承担",
      "answer": "无理由退货的退回运费由买家承担;因商品质量问题、发错货、少发漏发导致的退换货,运费由平台承担。运费承担以平台售后规则最终判定为准。"
    },
    {
      "n": 3,
      "chunk_id": "1771",
      "section_path": "退货退款政策/运输破损处理",
      "question": "运输破损处理",
      "answer": "商品运输途中破损的,请在签收后 48 小时内联系客服并提供开箱视频与照片,核实后可免费补发或退款,相关运费由平台承担。"
    },
    {
      "n": 5,
      "chunk_id": "1741",
      "section_path": "商品与购物 FAQ/发货时效多久",
      "question": "发货时效多久",
      "answer": "现货商品付款后 48 小时内发货,预售商品以商品详情页标注的发货时间为准。"
    },
    {
      "n": 7,
      "chunk_id": "1773",
      "section_path": "退货退款政策/预售与定金",
      "question": "预售与定金",
      "answer": "预售商品以详情页标注的时间发货;定金支付后不支持无理由退定金,尾款未按时支付的,定金按活动规则处理。"
    },
    {
      "n": 9,
      "chunk_id": "1742",
      "section_path": "商品与购物 FAQ/运费怎么算",
      "question": "运费怎么算",
      "answer": "单笔订单满 99 元包邮,未满收取 10 元运费,偏远地区运费另计。邮费即运费,按此规则收取。"
    },
    {
      "n": 10,
      "chunk_id": "1772",
      "section_path": "退货退款政策/不支持退货的商品",
      "question": "不支持退货的商品",
      "answer": "定制类、生鲜类、已拆封的猫砂等消耗品,以及标注「不支持无理由退货」的商品,非质量问题不支持退货。"
    },
    {
      "n": 8,
      "chunk_id": "1766",
      "section_path": "退货退款政策/无理由退货/退款时效",
      "question": "退款时效",
      "answer": "退货商品经平台核验通过后,退款原路退回,到账时效以平台售后规则为准。"
    },
    {
      "n": 6,
      "chunk_id": "1738",
      "section_path": "商品与购物 FAQ/退货政策是什么",
      "question": "退货政策是什么",
      "answer": "支持 7 天无理由退货,商品需保持完好、不影响二次销售,具体以平台售后规则为准。"
    },
    {
      "n": 4,
      "chunk_id": "1765",
      "section_path": "退货退款政策/无理由退货/适用范围",
      "question": "适用范围",
      "answer": "自签收之日起 7 天内,商品完好、不影响二次销售的,支持无理由退货。定制类、生鲜类商品除外。"
    },
    {
      "n": 2,
      "chunk_id": "1768",
      "section_path": "退货退款政策/换货政策/换货运费",
      "question": "换货运费",
      "answer": "非质量问题的换货,往返运费由买家承担;因质量问题或发错货的换货,往返运费由平台承担。"
    }
  ],
  "decision": {
    "useful": true,
    "reason": "无理由退货运费买家承担且退款原路退回有时效说明",
    "response_kind": "knowledge",
    "source": null
  },
  "answer": "您好！关于您的问题，说明如下：\n\n**1. 退货运费承担** [1]\n- 无理由退货（单纯不想要了）：寄回运费由买家承担；\n- 因商品质量问题、发错货、少发漏发导致的退货：运费由平台承担；\n- 最终以平台售后规则判定为准。\n\n**2. 退款时效** [8]\n- 退货商品经平台核验通过后，退款将原路退回；\n- 具体到账时效以平台售后规则为准，无法向您承诺具体到账日期，还请谅解。\n\n温馨提示：无理由退货需在签收后 7 天内、商品完好且不影响二次销售 [4]。如您能提供订单号，我可以帮您进一步查询订单信息哦～",
  "point_verdicts": null,
  "claim_verdicts": null,
  "metrics": {
    "recall_at_5": 0.6666666666666666,
    "recall_at_10": 1.0,
    "mrr_at_10": 1.0,
    "all_groups_hit_at_5": 0.0,
    "all_groups_hit_at_10": 1.0,
    "candidate_group_coverage": 1.0,
    "prompt_group_coverage": 1.0,
    "answer_point_coverage": null,
    "faithfulness": null,
    "absent_refusal_rate": null,
    "answerable_false_refusal_rate": 0.0
  },
  "error": {
    "code": "judgment_error",
    "type": "TimeoutError",
    "message": "该阶段执行失败"
  },
  "elapsed_ms": 2280022.236999823,
  "judge_snapshot": null,
  "audit": {
    "audit_version": 1,
    "source_map_id": "378ae65f4ee735c6a8079070fbfcb5c21800c93f3318029e5f19836c32b5c2b4",
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
        "chunk_id": 1769,
        "score": 0.032786883413791656,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1768,
        "score": 0.0320020467042923,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1771,
        "score": 0.0320020467042923,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1765,
        "score": 0.03077651560306549,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1741,
        "score": 0.0292735043913126,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1738,
        "score": 0.029236022382974625,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1773,
        "score": 0.02919863536953926,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1766,
        "score": 0.028371628373861313,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1742,
        "score": 0.02819138392806053,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1772,
        "score": 0.027970679104328156,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1749,
        "score": 0.027912385761737823,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1767,
        "score": 0.027587518095970154,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1751,
        "score": 0.027205882593989372,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1770,
        "score": 0.026631392538547516,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1747,
        "score": 0.026171742007136345,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1731,
        "score": 0.026132699102163315,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1737,
        "score": 0.02581612393260002,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1777,
        "score": 0.02577996626496315,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1779,
        "score": 0.025015633553266525,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1739,
        "score": 0.024961240589618683,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1774,
        "score": 0.02426900714635849,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1776,
        "score": 0.024264706298708916,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1732,
        "score": 0.024243313819169998,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1750,
        "score": 0.02380952425301075,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1744,
        "score": 0.023140717297792435,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1780,
        "score": 0.022948719561100006,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1743,
        "score": 0.022863861173391342,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1748,
        "score": 0.022543059661984444,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1775,
        "score": 0.022363819181919098,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1735,
        "score": 0.022233203053474426,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1746,
        "score": 0.02139098569750786,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1760,
        "score": 0.021198667585849762,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1778,
        "score": 0.021169355139136314,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1734,
        "score": 0.021052632480859756,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1754,
        "score": 0.02101210132241249,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1752,
        "score": 0.02088744565844536,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1740,
        "score": 0.014925372786819935,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1736,
        "score": 0.013513513840734959,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1745,
        "score": 0.010989011265337467,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1753,
        "score": 0.010416666977107525,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1755,
        "score": 0.010309278033673763,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1758,
        "score": 0.010204081423580647,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1757,
        "score": 0.010101010091602802,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1756,
        "score": 0.009999999776482582,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1733,
        "score": 0.009803921915590763,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1762,
        "score": 0.009708737954497337,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1763,
        "score": 0.009345794096589088,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1761,
        "score": 0.009259259328246117,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1764,
        "score": 0.00917431153357029,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1759,
        "score": 0.00909090880304575,
        "score_kind": "rrf"
      }
    ],
    "final_ranking": [
      {
        "chunk_id": 1769,
        "score": 0.032786883413791656,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1768,
        "score": 0.0320020467042923,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1771,
        "score": 0.0320020467042923,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1765,
        "score": 0.03077651560306549,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1741,
        "score": 0.0292735043913126,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1738,
        "score": 0.029236022382974625,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1773,
        "score": 0.02919863536953926,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1766,
        "score": 0.028371628373861313,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1742,
        "score": 0.02819138392806053,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1772,
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
  "refused": null,
  "status": "retrieval_error",
  "stage": "retrieval",
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
          1765
        ],
        [
          1738
        ]
      ]
    },
    {
      "group_id": "g2",
      "alternatives": [
        [
          1769
        ]
      ]
    },
    {
      "group_id": "g3",
      "alternatives": [
        [
          1766
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
    "code": "retrieval_error",
    "type": "ConnectError",
    "message": "该阶段执行失败"
  },
  "elapsed_ms": 37130.062399897724,
  "judge_snapshot": null,
  "audit": {
    "audit_version": 1,
    "source_map_id": "378ae65f4ee735c6a8079070fbfcb5c21800c93f3318029e5f19836c32b5c2b4",
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
    "candidate_ranking": null,
    "final_ranking": null
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
  "status": "judge_error",
  "stage": "judgment",
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
          1756
        ]
      ]
    },
    {
      "group_id": "g2",
      "alternatives": [
        [
          1758
        ]
      ]
    }
  ],
  "candidate_ids": [
    1756,
    1758,
    1757,
    1762,
    1755,
    1777,
    1763,
    1754,
    1753,
    1761,
    1734,
    1760,
    1736,
    1731,
    1732,
    1770,
    1759,
    1764,
    1740,
    1735,
    1752,
    1767,
    1737,
    1733,
    1765,
    1741,
    1780,
    1738,
    1768,
    1745,
    1749,
    1775,
    1779,
    1751,
    1771,
    1774,
    1773,
    1750,
    1766,
    1744,
    1748,
    1772,
    1743,
    1742,
    1747,
    1746,
    1776,
    1778,
    1769,
    1739
  ],
  "final_ids": [
    1756,
    1758,
    1757,
    1762,
    1755,
    1777,
    1763,
    1754,
    1753,
    1761
  ],
  "prompt_citations": [
    {
      "n": 1,
      "chunk_id": "1756",
      "section_path": "商品规格手册/自动饮水机(型号 MH-W20)",
      "question": "自动饮水机(型号 MH-W20)",
      "answer": "- 型号:MH-W20\n- 水箱容量:2L\n- 过滤:三重过滤棉,建议每 2 周更换一次滤芯\n- 核心功能:静音水泵、缺水断电保护、水位窗口\n- 清洗:水泵可拆卸,建议每周清洗一次"
    },
    {
      "n": 3,
      "chunk_id": "1757",
      "section_path": "商品规格手册/自动饮水机 Plus(型号 MH-W40)",
      "question": "自动饮水机 Plus(型号 MH-W40)",
      "answer": "- 型号:MH-W40\n- 水箱容量:4L\n- 过滤:五重过滤棉 + 椰壳活性炭,建议每 3 周更换一次滤芯\n- 核心功能:UV 紫外杀菌、静音变频水泵、缺水断电保护\n- 清洗:整机可拆分水洗,建议每周清洗一次"
    },
    {
      "n": 5,
      "chunk_id": "1755",
      "section_path": "商品规格手册/智能猫砂盆 Max(型号 MH-LP200)",
      "question": "智能猫砂盆 Max(型号 MH-LP200)",
      "answer": "- 型号:MH-LP200\n- 适用猫咪体重:2kg 至 12kg,适合大型猫与多猫家庭\n- 猫砂容量:12L,废砂盒容量约 10 天(单猫)\n- 核心功能:超大滚筒、双重称重防夹、活性炭除臭、App 多猫健康档案\n- 供电:220V 市电\n- 清理提示:多猫家庭建议每 3 至 5 天倾倒一次废砂盒"
    },
    {
      "n": 7,
      "chunk_id": "1763",
      "section_path": "商品规格手册/自动喂食器 摄像头版(型号 MH-FD30)",
      "question": "自动喂食器 摄像头版(型号 MH-FD30)",
      "answer": "- 型号:MH-FD30\n- 粮桶容量:6L\n- 核心功能:1080P 摄像头、双向语音、App 远程手动投喂与定时投喂\n- 供电:市电供电 + 内置应急电池\n- 说明:摄像头版支持视频回看,需连接 2.4G Wi-Fi"
    },
    {
      "n": 9,
      "chunk_id": "1753",
      "section_path": "商品规格手册/智能猫砂盆 Pro(型号 MH-LP100)",
      "question": "智能猫砂盆 Pro(型号 MH-LP100)",
      "answer": "- 型号:MH-LP100\n- 适用猫咪体重:1.5kg 至 8kg\n- 猫砂容量:9L,废砂盒容量约 7 天(单猫)\n- 核心功能:自动感应清理、活性炭除臭、App 远程监控与健康记录\n- 供电:220V 市电,断电后配置自动保存\n- 清理提示:废砂盒满时 App 推送提醒,建议每 5 至 7 天倾倒一次"
    },
    {
      "n": 10,
      "chunk_id": "1761",
      "section_path": "商品规格手册/大号三档加热垫(型号 MH-HP20)",
      "question": "大号三档加热垫(型号 MH-HP20)",
      "answer": "- 型号:MH-HP20\n- 尺寸:60cm × 45cm\n- 温控:三档可调 30℃ / 38℃ / 45℃,内置过热保护与定时关机\n- 防护:防水防抓咬电线套管,表面绒布可拆洗\n- 适用:大型猫、多猫窝及冬季保暖"
    },
    {
      "n": 8,
      "chunk_id": "1754",
      "section_path": "商品规格手册/智能猫砂盆 Lite(型号 MH-LP50)",
      "question": "智能猫砂盆 Lite(型号 MH-LP50)",
      "answer": "- 型号:MH-LP50\n- 适用猫咪体重:1.5kg 至 6kg\n- 猫砂容量:6L\n- 核心功能:自动感应清理、物理除臭盖板;不含 App 联网功能\n- 与 Pro 差异:Lite 无 App 远程监控与健康记录,价格更低,适合单猫家庭"
    },
    {
      "n": 6,
      "chunk_id": "1777",
      "section_path": "积分规则/积分怎么用",
      "question": "积分怎么用",
      "answer": "积分可在结算时抵扣商品金额，100 积分抵 1 元现金，单笔订单最多抵 30 元，不用于抵扣偏远地区附加运费，也不支持直接提现。\n\n2000 积分可兑换自动饮水机滤芯 3 片，该兑换套装适用于 MH-W40，普通配送地区包邮；偏远地区附加配送费仍需按页面规则确认。MH-W40 的滤芯更换周期以商品规格手册为准。\n\n800 积分可兑换猫零食小样，普通配送地区另收 6 元运费；该兑换不直接套用普通购物订单的满 99 元包邮规则。兑换商品、可用库存及偏远地区配送规则以兑换页面标注为准。"
    },
    {
      "n": 4,
      "chunk_id": "1762",
      "section_path": "商品规格手册/自动喂食器 基础版(型号 MH-FD10)",
      "question": "自动喂食器 基础版(型号 MH-FD10)",
      "answer": "- 型号:MH-FD10\n- 粮桶容量:4L\n- 核心功能:定时定量投喂,每日最多 6 餐,语音呼唤进食\n- 供电:市电供电 + 4 节 5 号电池断电应急\n- 说明:基础版不含摄像头与 App 远程投喂"
    },
    {
      "n": 2,
      "chunk_id": "1758",
      "section_path": "商品规格手册/自动饮水机 Pro 不锈钢(型号 MH-W60)",
      "question": "自动饮水机 Pro 不锈钢(型号 MH-W60)",
      "answer": "- 型号:MH-W60\n- 水箱容量:6L,304 不锈钢表面盘\n- 过滤:双滤芯并联,建议每 4 周更换一次滤芯\n- 核心功能:双泵冗余、无线水位提醒推送 App、缺水断电保护\n- 清洗:不锈钢面盘可高温消毒,建议每周清洗一次"
    }
  ],
  "decision": {
    "useful": true,
    "reason": "两款型号水箱容量与滤芯周期均有规格证据",
    "response_kind": "knowledge",
    "source": null
  },
  "answer": "您好！根据商品规格手册，两款饮水机的参数如下：\n\n**自动饮水机 MH-W20** [1]\n- 水箱容量：2L\n- 滤芯更换周期：三重过滤棉，建议每 2 周更换一次\n\n**自动饮水机 Pro 不锈钢 MH-W60** [2]\n- 水箱容量：6L（304 不锈钢表面盘）\n- 滤芯更换周期：双滤芯并联，建议每 4 周更换一次\n\n另外，MH-W60 的不锈钢面盘可高温消毒，两款水泵均建议每周清洗一次 [1][2]。请问还有其他需要帮助的吗？",
  "point_verdicts": null,
  "claim_verdicts": null,
  "metrics": {
    "recall_at_5": 1.0,
    "recall_at_10": 1.0,
    "mrr_at_10": 1.0,
    "all_groups_hit_at_5": 1.0,
    "all_groups_hit_at_10": 1.0,
    "candidate_group_coverage": 1.0,
    "prompt_group_coverage": 1.0,
    "answer_point_coverage": null,
    "faithfulness": null,
    "absent_refusal_rate": null,
    "answerable_false_refusal_rate": 0.0
  },
  "error": {
    "code": "judgment_error",
    "type": "JudgeError",
    "message": "该阶段执行失败"
  },
  "elapsed_ms": 57014.40800027922,
  "judge_snapshot": {
    "prompt_version": "joint-generation-v2.1",
    "finish_reason": "length"
  },
  "audit": {
    "audit_version": 1,
    "source_map_id": "378ae65f4ee735c6a8079070fbfcb5c21800c93f3318029e5f19836c32b5c2b4",
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
        "chunk_id": 1756,
        "score": 0.7491767406463623,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1758,
        "score": 0.7155006527900696,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1757,
        "score": 0.7105969786643982,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1762,
        "score": 0.5239151120185852,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1755,
        "score": 0.5213737487792969,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1777,
        "score": 0.5169979333877563,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1763,
        "score": 0.5121591687202454,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1754,
        "score": 0.5058782696723938,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1753,
        "score": 0.5012839436531067,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1761,
        "score": 0.47346651554107666,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1734,
        "score": 0.4690849184989929,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1760,
        "score": 0.4500263035297394,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1736,
        "score": 0.4283367097377777,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1731,
        "score": 0.4235793948173523,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1732,
        "score": 0.42355358600616455,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1770,
        "score": 0.41472920775413513,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1759,
        "score": 0.4141151010990143,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1764,
        "score": 0.4087774157524109,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1740,
        "score": 0.3997528851032257,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1735,
        "score": 0.3912475109100342,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1752,
        "score": 0.3863105773925781,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1767,
        "score": 0.38300246000289917,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1737,
        "score": 0.3733814060688019,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1733,
        "score": 0.36839759349823,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1765,
        "score": 0.36591464281082153,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1741,
        "score": 0.36022883653640747,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1780,
        "score": 0.3573654294013977,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1738,
        "score": 0.3401876389980316,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1768,
        "score": 0.33363038301467896,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1745,
        "score": 0.3331489562988281,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1749,
        "score": 0.3318994641304016,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1775,
        "score": 0.33004024624824524,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1779,
        "score": 0.3231661915779114,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1751,
        "score": 0.32236671447753906,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1771,
        "score": 0.31401360034942627,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1774,
        "score": 0.31361204385757446,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1773,
        "score": 0.2994229793548584,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1750,
        "score": 0.2959010601043701,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1766,
        "score": 0.2954493463039398,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1744,
        "score": 0.2925569415092468,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1748,
        "score": 0.2918779253959656,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1772,
        "score": 0.2886510193347931,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1743,
        "score": 0.2813261151313782,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1742,
        "score": 0.27818983793258667,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1747,
        "score": 0.27697956562042236,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1746,
        "score": 0.2709062099456787,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1776,
        "score": 0.26987195014953613,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1778,
        "score": 0.26727715134620667,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1769,
        "score": 0.2625117301940918,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1739,
        "score": 0.2582545876502991,
        "score_kind": "cosine"
      }
    ],
    "final_ranking": [
      {
        "chunk_id": 1756,
        "score": 0.7491767406463623,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1758,
        "score": 0.7155006527900696,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1757,
        "score": 0.7105969786643982,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1762,
        "score": 0.5239151120185852,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1755,
        "score": 0.5213737487792969,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1777,
        "score": 0.5169979333877563,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1763,
        "score": 0.5121591687202454,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1754,
        "score": 0.5058782696723938,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1753,
        "score": 0.5012839436531067,
        "score_kind": "cosine"
      },
      {
        "chunk_id": 1761,
        "score": 0.47346651554107666,
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
  "status": "judge_error",
  "stage": "judgment",
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
          1756
        ]
      ]
    },
    {
      "group_id": "g2",
      "alternatives": [
        [
          1758
        ]
      ]
    }
  ],
  "candidate_ids": [
    1756,
    1758,
    1757,
    1777,
    1746,
    1778,
    1774,
    1768,
    1734,
    1738,
    1759,
    1760,
    1761,
    1754,
    1764,
    1762,
    1763,
    1755,
    1753,
    1772,
    1773,
    1769,
    1780,
    1739,
    1741,
    1752,
    1743,
    1749,
    1767,
    1765,
    1750,
    1735,
    1771,
    1748,
    1776,
    1779
  ],
  "final_ids": [
    1756,
    1758,
    1757,
    1777,
    1746,
    1778,
    1774,
    1768,
    1734,
    1738
  ],
  "prompt_citations": [
    {
      "n": 1,
      "chunk_id": "1756",
      "section_path": "商品规格手册/自动饮水机(型号 MH-W20)",
      "question": "自动饮水机(型号 MH-W20)",
      "answer": "- 型号:MH-W20\n- 水箱容量:2L\n- 过滤:三重过滤棉,建议每 2 周更换一次滤芯\n- 核心功能:静音水泵、缺水断电保护、水位窗口\n- 清洗:水泵可拆卸,建议每周清洗一次"
    },
    {
      "n": 3,
      "chunk_id": "1757",
      "section_path": "商品规格手册/自动饮水机 Plus(型号 MH-W40)",
      "question": "自动饮水机 Plus(型号 MH-W40)",
      "answer": "- 型号:MH-W40\n- 水箱容量:4L\n- 过滤:五重过滤棉 + 椰壳活性炭,建议每 3 周更换一次滤芯\n- 核心功能:UV 紫外杀菌、静音变频水泵、缺水断电保护\n- 清洗:整机可拆分水洗,建议每周清洗一次"
    },
    {
      "n": 5,
      "chunk_id": "1746",
      "section_path": "商品与购物 FAQ/优惠券和满减怎么用",
      "question": "优惠券和满减怎么用",
      "answer": "优惠券在结算页「使用优惠券」中勾选,满减活动自动叠加在商品页标示的门槛上;同一订单一般限用一张店铺券,活动细则以页面为准。"
    },
    {
      "n": 7,
      "chunk_id": "1774",
      "section_path": "会员权益/会员等级",
      "question": "会员等级",
      "answer": "会员分为普通、银卡和金卡三档，按有效累计消费金额自动升级，不按年度消费金额计算。累计消费未满 1000 元为普通会员，满 1000 元起为银卡，满 5000 元起为金卡。\n\n有效累计消费指已完成订单的商品实际支付金额，不含配送费；退货退款部分从有效累计消费中扣除。退款后根据更新的累计消费重新计算等级，未达到原门槛时可能降级。等级与适用权益在会员中心展示。\n\n银卡在参与会员折扣的商品上享 95 折，金卡享 9 折。折扣适用商品和活动范围以结算页面标注为准。会员折扣、优惠券与满减是否叠加也以当次活动页面为准，不能一概承诺全部优惠同时生效。"
    },
    {
      "n": 9,
      "chunk_id": "1734",
      "section_path": "售后手册/常见故障自查",
      "question": "常见故障自查",
      "answer": "- 饮水机不出水:检查水位是否低于最低线、水泵是否卡阻,断电清洗水泵后重试。\n- 猫砂盆报错:清空废砂盒并检查滚筒是否卡砂,重启设备;仍报错联系售后。\n- 喂食器卡粮:检查粮食颗粒直径是否超 12mm、粮桶是否受潮结块,清理出粮口后重试。\n- 摄像头离线:确认 Wi-Fi 为 2.4G 频段、信号良好,重启设备或在 App 内重新配网。"
    },
    {
      "n": 10,
      "chunk_id": "1738",
      "section_path": "商品与购物 FAQ/退货政策是什么",
      "question": "退货政策是什么",
      "answer": "支持 7 天无理由退货,商品需保持完好、不影响二次销售,具体以平台售后规则为准。"
    },
    {
      "n": 8,
      "chunk_id": "1768",
      "section_path": "退货退款政策/换货政策/换货运费",
      "question": "换货运费",
      "answer": "非质量问题的换货,往返运费由买家承担;因质量问题或发错货的换货,往返运费由平台承担。"
    },
    {
      "n": 6,
      "chunk_id": "1778",
      "section_path": "开票细则/可开票类型",
      "question": "可开票类型",
      "answer": "本演示店提供电子普通发票、电子专用发票和纸质专用发票。电子普通发票可按订单申请；电子专票需要企业账户，申请前准备发票抬头及有效纳税人识别号，按申请页面提交资料。\n\n纸质专票仅企业账户可申请，申请时需提供企业开票资料、收件人和邮寄地址，快递费到付。资料审核通过后按开票流程寄出，不承诺快递送达日期。"
    },
    {
      "n": 4,
      "chunk_id": "1777",
      "section_path": "积分规则/积分怎么用",
      "question": "积分怎么用",
      "answer": "积分可在结算时抵扣商品金额，100 积分抵 1 元现金，单笔订单最多抵 30 元，不用于抵扣偏远地区附加运费，也不支持直接提现。\n\n2000 积分可兑换自动饮水机滤芯 3 片，该兑换套装适用于 MH-W40，普通配送地区包邮；偏远地区附加配送费仍需按页面规则确认。MH-W40 的滤芯更换周期以商品规格手册为准。\n\n800 积分可兑换猫零食小样，普通配送地区另收 6 元运费；该兑换不直接套用普通购物订单的满 99 元包邮规则。兑换商品、可用库存及偏远地区配送规则以兑换页面标注为准。"
    },
    {
      "n": 2,
      "chunk_id": "1758",
      "section_path": "商品规格手册/自动饮水机 Pro 不锈钢(型号 MH-W60)",
      "question": "自动饮水机 Pro 不锈钢(型号 MH-W60)",
      "answer": "- 型号:MH-W60\n- 水箱容量:6L,304 不锈钢表面盘\n- 过滤:双滤芯并联,建议每 4 周更换一次滤芯\n- 核心功能:双泵冗余、无线水位提醒推送 App、缺水断电保护\n- 清洗:不锈钢面盘可高温消毒,建议每周清洗一次"
    }
  ],
  "decision": {
    "useful": true,
    "reason": "两个型号的水箱容量与滤芯周期均有直接证据",
    "response_kind": "knowledge",
    "source": null
  },
  "answer": "您好，很高兴为您解答两款饮水机的参数：\n\n**自动饮水机 MH-W20**[1]\n- 水箱容量：2L\n- 换滤芯周期：三重过滤棉，建议每 2 周更换一次\n\n**自动饮水机 Pro 不锈钢 MH-W60**[2]\n- 水箱容量：6L（304 不锈钢表面盘）\n- 换滤芯周期：双滤芯并联，建议每 4 周更换一次\n\n两款机型均建议每周清洗一次水泵/机身[1][2]。如还有其他问题，欢迎随时咨询～",
  "point_verdicts": null,
  "claim_verdicts": null,
  "metrics": {
    "recall_at_5": 1.0,
    "recall_at_10": 1.0,
    "mrr_at_10": 1.0,
    "all_groups_hit_at_5": 1.0,
    "all_groups_hit_at_10": 1.0,
    "candidate_group_coverage": 1.0,
    "prompt_group_coverage": 1.0,
    "answer_point_coverage": null,
    "faithfulness": null,
    "absent_refusal_rate": null,
    "answerable_false_refusal_rate": 0.0
  },
  "error": {
    "code": "judgment_error",
    "type": "TimeoutError",
    "message": "该阶段执行失败"
  },
  "elapsed_ms": 2271110.8348001726,
  "judge_snapshot": null,
  "audit": {
    "audit_version": 1,
    "source_map_id": "378ae65f4ee735c6a8079070fbfcb5c21800c93f3318029e5f19836c32b5c2b4",
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
        "chunk_id": 1756,
        "score": 21.04051399230957,
        "score_kind": "bm25"
      },
      {
        "chunk_id": 1758,
        "score": 20.065227508544922,
        "score_kind": "bm25"
      },
      {
        "chunk_id": 1757,
        "score": 15.246339797973633,
        "score_kind": "bm25"
      },
      {
        "chunk_id": 1777,
        "score": 12.108427047729492,
        "score_kind": "bm25"
      },
      {
        "chunk_id": 1746,
        "score": 6.594915866851807,
        "score_kind": "bm25"
      },
      {
        "chunk_id": 1778,
        "score": 6.17706298828125,
        "score_kind": "bm25"
      },
      {
        "chunk_id": 1774,
        "score": 6.0217061042785645,
        "score_kind": "bm25"
      },
      {
        "chunk_id": 1768,
        "score": 5.385351181030273,
        "score_kind": "bm25"
      },
      {
        "chunk_id": 1734,
        "score": 5.383184432983398,
        "score_kind": "bm25"
      },
      {
        "chunk_id": 1738,
        "score": 4.2695698738098145,
        "score_kind": "bm25"
      },
      {
        "chunk_id": 1759,
        "score": 3.8244388103485107,
        "score_kind": "bm25"
      },
      {
        "chunk_id": 1760,
        "score": 3.8244388103485107,
        "score_kind": "bm25"
      },
      {
        "chunk_id": 1761,
        "score": 3.6993556022644043,
        "score_kind": "bm25"
      },
      {
        "chunk_id": 1754,
        "score": 3.5821950435638428,
        "score_kind": "bm25"
      },
      {
        "chunk_id": 1764,
        "score": 3.5821950435638428,
        "score_kind": "bm25"
      },
      {
        "chunk_id": 1762,
        "score": 3.5633859634399414,
        "score_kind": "bm25"
      },
      {
        "chunk_id": 1763,
        "score": 3.5081260204315186,
        "score_kind": "bm25"
      },
      {
        "chunk_id": 1755,
        "score": 3.3193798065185547,
        "score_kind": "bm25"
      },
      {
        "chunk_id": 1753,
        "score": 3.3032233715057373,
        "score_kind": "bm25"
      },
      {
        "chunk_id": 1772,
        "score": 1.4414697885513306,
        "score_kind": "bm25"
      },
      {
        "chunk_id": 1773,
        "score": 1.2937390804290771,
        "score_kind": "bm25"
      },
      {
        "chunk_id": 1769,
        "score": 1.215309500694275,
        "score_kind": "bm25"
      },
      {
        "chunk_id": 1780,
        "score": 1.1236776113510132,
        "score_kind": "bm25"
      },
      {
        "chunk_id": 1739,
        "score": 1.0660427808761597,
        "score_kind": "bm25"
      },
      {
        "chunk_id": 1741,
        "score": 1.0558345317840576,
        "score_kind": "bm25"
      },
      {
        "chunk_id": 1752,
        "score": 1.0359933376312256,
        "score_kind": "bm25"
      },
      {
        "chunk_id": 1743,
        "score": 1.0168840885162354,
        "score_kind": "bm25"
      },
      {
        "chunk_id": 1749,
        "score": 0.998467206954956,
        "score_kind": "bm25"
      },
      {
        "chunk_id": 1767,
        "score": 0.998467206954956,
        "score_kind": "bm25"
      },
      {
        "chunk_id": 1765,
        "score": 0.9895066618919373,
        "score_kind": "bm25"
      },
      {
        "chunk_id": 1750,
        "score": 0.9807054996490479,
        "score_kind": "bm25"
      },
      {
        "chunk_id": 1735,
        "score": 0.9720594882965088,
        "score_kind": "bm25"
      },
      {
        "chunk_id": 1771,
        "score": 0.9470126032829285,
        "score_kind": "bm25"
      },
      {
        "chunk_id": 1748,
        "score": 0.9155580401420593,
        "score_kind": "bm25"
      },
      {
        "chunk_id": 1776,
        "score": 0.8389298319816589,
        "score_kind": "bm25"
      },
      {
        "chunk_id": 1779,
        "score": 0.7139831781387329,
        "score_kind": "bm25"
      }
    ],
    "final_ranking": [
      {
        "chunk_id": 1756,
        "score": 21.04051399230957,
        "score_kind": "bm25"
      },
      {
        "chunk_id": 1758,
        "score": 20.065227508544922,
        "score_kind": "bm25"
      },
      {
        "chunk_id": 1757,
        "score": 15.246339797973633,
        "score_kind": "bm25"
      },
      {
        "chunk_id": 1777,
        "score": 12.108427047729492,
        "score_kind": "bm25"
      },
      {
        "chunk_id": 1746,
        "score": 6.594915866851807,
        "score_kind": "bm25"
      },
      {
        "chunk_id": 1778,
        "score": 6.17706298828125,
        "score_kind": "bm25"
      },
      {
        "chunk_id": 1774,
        "score": 6.0217061042785645,
        "score_kind": "bm25"
      },
      {
        "chunk_id": 1768,
        "score": 5.385351181030273,
        "score_kind": "bm25"
      },
      {
        "chunk_id": 1734,
        "score": 5.383184432983398,
        "score_kind": "bm25"
      },
      {
        "chunk_id": 1738,
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
  "refused": null,
  "status": "retrieval_error",
  "stage": "retrieval",
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
          1756
        ]
      ]
    },
    {
      "group_id": "g2",
      "alternatives": [
        [
          1758
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
    "code": "retrieval_error",
    "type": "ConnectError",
    "message": "该阶段执行失败"
  },
  "elapsed_ms": 33373.10940027237,
  "judge_snapshot": null,
  "audit": {
    "audit_version": 1,
    "source_map_id": "378ae65f4ee735c6a8079070fbfcb5c21800c93f3318029e5f19836c32b5c2b4",
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
  "refused": false,
  "status": "judge_error",
  "stage": "judgment",
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
          1756
        ]
      ]
    },
    {
      "group_id": "g2",
      "alternatives": [
        [
          1758
        ]
      ]
    }
  ],
  "candidate_ids": [
    1756,
    1758,
    1757,
    1777,
    1762,
    1734,
    1754,
    1755,
    1761,
    1763,
    1760,
    1759,
    1753,
    1764,
    1768,
    1738,
    1774,
    1746,
    1778,
    1752,
    1780,
    1767,
    1741,
    1735,
    1765,
    1773,
    1749,
    1772,
    1769,
    1743,
    1750,
    1771,
    1779,
    1739,
    1748,
    1776,
    1736,
    1731,
    1732,
    1770,
    1740,
    1737,
    1733,
    1745,
    1775,
    1751,
    1766,
    1744,
    1742,
    1747
  ],
  "final_ids": [
    1756,
    1758,
    1757,
    1777,
    1732,
    1761,
    1770,
    1767,
    1737,
    1734
  ],
  "prompt_citations": [
    {
      "n": 1,
      "chunk_id": "1756",
      "section_path": "商品规格手册/自动饮水机(型号 MH-W20)",
      "question": "自动饮水机(型号 MH-W20)",
      "answer": "- 型号:MH-W20\n- 水箱容量:2L\n- 过滤:三重过滤棉,建议每 2 周更换一次滤芯\n- 核心功能:静音水泵、缺水断电保护、水位窗口\n- 清洗:水泵可拆卸,建议每周清洗一次"
    },
    {
      "n": 3,
      "chunk_id": "1757",
      "section_path": "商品规格手册/自动饮水机 Plus(型号 MH-W40)",
      "question": "自动饮水机 Plus(型号 MH-W40)",
      "answer": "- 型号:MH-W40\n- 水箱容量:4L\n- 过滤:五重过滤棉 + 椰壳活性炭,建议每 3 周更换一次滤芯\n- 核心功能:UV 紫外杀菌、静音变频水泵、缺水断电保护\n- 清洗:整机可拆分水洗,建议每周清洗一次"
    },
    {
      "n": 5,
      "chunk_id": "1732",
      "section_path": "售后手册/保修说明",
      "question": "保修说明",
      "answer": "电子类商品保修 12 个月,自签收日起算;人为损坏不在保修范围。"
    },
    {
      "n": 7,
      "chunk_id": "1770",
      "section_path": "退货退款政策/质量问题与保修",
      "question": "质量问题与保修",
      "answer": "电子类商品自签收起保修 12 个月,保修期内非人为损坏可申请免费维修或换货;人为损坏、超保商品维修可能收取工本费。"
    },
    {
      "n": 9,
      "chunk_id": "1737",
      "section_path": "售后手册/会员专属售后权益",
      "question": "会员专属售后权益",
      "answer": "金卡会员享优先客服接入与上门取件退换货;银卡会员享退换货运费权益 1 次/月。具体权益以会员中心页面标注为准。"
    },
    {
      "n": 10,
      "chunk_id": "1734",
      "section_path": "售后手册/常见故障自查",
      "question": "常见故障自查",
      "answer": "- 饮水机不出水:检查水位是否低于最低线、水泵是否卡阻,断电清洗水泵后重试。\n- 猫砂盆报错:清空废砂盒并检查滚筒是否卡砂,重启设备;仍报错联系售后。\n- 喂食器卡粮:检查粮食颗粒直径是否超 12mm、粮桶是否受潮结块,清理出粮口后重试。\n- 摄像头离线:确认 Wi-Fi 为 2.4G 频段、信号良好,重启设备或在 App 内重新配网。"
    },
    {
      "n": 8,
      "chunk_id": "1767",
      "section_path": "退货退款政策/换货政策/换货条件",
      "question": "换货条件",
      "answer": "收到商品 7 天内,商品完好且配件齐全的,可申请一次同款换货;不同型号或颜色需先退货再重新下单。"
    },
    {
      "n": 6,
      "chunk_id": "1761",
      "section_path": "商品规格手册/大号三档加热垫(型号 MH-HP20)",
      "question": "大号三档加热垫(型号 MH-HP20)",
      "answer": "- 型号:MH-HP20\n- 尺寸:60cm × 45cm\n- 温控:三档可调 30℃ / 38℃ / 45℃,内置过热保护与定时关机\n- 防护:防水防抓咬电线套管,表面绒布可拆洗\n- 适用:大型猫、多猫窝及冬季保暖"
    },
    {
      "n": 4,
      "chunk_id": "1777",
      "section_path": "积分规则/积分怎么用",
      "question": "积分怎么用",
      "answer": "积分可在结算时抵扣商品金额，100 积分抵 1 元现金，单笔订单最多抵 30 元，不用于抵扣偏远地区附加运费，也不支持直接提现。\n\n2000 积分可兑换自动饮水机滤芯 3 片，该兑换套装适用于 MH-W40，普通配送地区包邮；偏远地区附加配送费仍需按页面规则确认。MH-W40 的滤芯更换周期以商品规格手册为准。\n\n800 积分可兑换猫零食小样，普通配送地区另收 6 元运费；该兑换不直接套用普通购物订单的满 99 元包邮规则。兑换商品、可用库存及偏远地区配送规则以兑换页面标注为准。"
    },
    {
      "n": 2,
      "chunk_id": "1758",
      "section_path": "商品规格手册/自动饮水机 Pro 不锈钢(型号 MH-W60)",
      "question": "自动饮水机 Pro 不锈钢(型号 MH-W60)",
      "answer": "- 型号:MH-W60\n- 水箱容量:6L,304 不锈钢表面盘\n- 过滤:双滤芯并联,建议每 4 周更换一次滤芯\n- 核心功能:双泵冗余、无线水位提醒推送 App、缺水断电保护\n- 清洗:不锈钢面盘可高温消毒,建议每周清洗一次"
    }
  ],
  "decision": {
    "useful": true,
    "reason": "两个型号水箱与滤芯周期均有规格证据",
    "response_kind": "knowledge",
    "source": null
  },
  "answer": "您好，根据商品规格手册，两款饮水机的参数如下：\n\n**MH-W20 自动饮水机** [1]\n- 水箱容量：2L\n- 换滤芯周期：建议每 2 周更换一次（三重过滤棉）\n\n**MH-W60 自动饮水机 Pro 不锈钢** [2]\n- 水箱容量：6L（304 不锈钢表面盘）\n- 换滤芯周期：建议每 4 周更换一次（双滤芯并联）\n\n温馨提示：两款机型均建议每周清洗一次 [1][2]。如需了解其他参数或购买滤芯，欢迎随时告诉我～",
  "point_verdicts": null,
  "claim_verdicts": null,
  "metrics": {
    "recall_at_5": 1.0,
    "recall_at_10": 1.0,
    "mrr_at_10": 1.0,
    "all_groups_hit_at_5": 1.0,
    "all_groups_hit_at_10": 1.0,
    "candidate_group_coverage": 1.0,
    "prompt_group_coverage": 1.0,
    "answer_point_coverage": null,
    "faithfulness": null,
    "absent_refusal_rate": null,
    "answerable_false_refusal_rate": 0.0
  },
  "error": {
    "code": "judgment_error",
    "type": "JudgeError",
    "message": "该阶段执行失败"
  },
  "elapsed_ms": 57149.309600004926,
  "judge_snapshot": {
    "prompt_version": "joint-generation-v2.1",
    "finish_reason": "length"
  },
  "audit": {
    "audit_version": 1,
    "source_map_id": "378ae65f4ee735c6a8079070fbfcb5c21800c93f3318029e5f19836c32b5c2b4",
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
        "chunk_id": 1756,
        "score": 0.032786883413791656,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1758,
        "score": 0.032258063554763794,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1757,
        "score": 0.0317460335791111,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1777,
        "score": 0.03077651560306549,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1762,
        "score": 0.02878289483487606,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1734,
        "score": 0.028577260673046112,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1754,
        "score": 0.028219396248459816,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1755,
        "score": 0.028205128386616707,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1761,
        "score": 0.027984343469142914,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1763,
        "score": 0.027912385761737823,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1760,
        "score": 0.02777777798473835,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1759,
        "score": 0.027242401614785194,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1753,
        "score": 0.02715098112821579,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1764,
        "score": 0.026153847575187683,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1768,
        "score": 0.025941837579011917,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1738,
        "score": 0.02564935013651848,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1774,
        "score": 0.025451689958572388,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1746,
        "score": 0.024818576872348785,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1778,
        "score": 0.024410774931311607,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1752,
        "score": 0.023973586037755013,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1780,
        "score": 0.02354244515299797,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1767,
        "score": 0.02343107759952545,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1741,
        "score": 0.023392613977193832,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1735,
        "score": 0.02336956560611725,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1765,
        "score": 0.022875817492604256,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1773,
        "score": 0.022654958069324493,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1749,
        "score": 0.02235264703631401,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1772,
        "score": 0.022303922101855278,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1769,
        "score": 0.021369433030486107,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1743,
        "score": 0.021202990785241127,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1750,
        "score": 0.021193092688918114,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1771,
        "score": 0.021169355139136314,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1779,
        "score": 0.021169355139136314,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1739,
        "score": 0.020995670929551125,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1748,
        "score": 0.020539287477731705,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1776,
        "score": 0.019872110337018967,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1736,
        "score": 0.013698630034923553,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1731,
        "score": 0.013513513840734959,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1732,
        "score": 0.013333333656191826,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1770,
        "score": 0.012987012974917889,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1740,
        "score": 0.012658228166401386,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1737,
        "score": 0.012048192322254181,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1733,
        "score": 0.011904762126505375,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1745,
        "score": 0.011111111380159855,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1775,
        "score": 0.010869565419852734,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1751,
        "score": 0.010638297535479069,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1766,
        "score": 0.010101010091602802,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1744,
        "score": 0.009999999776482582,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1742,
        "score": 0.009615384973585606,
        "score_kind": "rrf"
      },
      {
        "chunk_id": 1747,
        "score": 0.009523809887468815,
        "score_kind": "rrf"
      }
    ],
    "final_ranking": [
      {
        "chunk_id": 1756,
        "score": 0.9935787916183472,
        "score_kind": "rerank"
      },
      {
        "chunk_id": 1758,
        "score": 0.9705812931060791,
        "score_kind": "rerank"
      },
      {
        "chunk_id": 1757,
        "score": 0.3979853689670563,
        "score_kind": "rerank"
      },
      {
        "chunk_id": 1777,
        "score": 0.29511526226997375,
        "score_kind": "rerank"
      },
      {
        "chunk_id": 1732,
        "score": 0.006420794874429703,
        "score_kind": "rerank"
      },
      {
        "chunk_id": 1761,
        "score": 0.005696954671293497,
        "score_kind": "rerank"
      },
      {
        "chunk_id": 1770,
        "score": 0.004989458713680506,
        "score_kind": "rerank"
      },
      {
        "chunk_id": 1767,
        "score": 0.003732342505827546,
        "score_kind": "rerank"
      },
      {
        "chunk_id": 1737,
        "score": 0.003631142433732748,
        "score_kind": "rerank"
      },
      {
        "chunk_id": 1734,
        "score": 0.0031434905249625444,
        "score_kind": "rerank"
      }
    ]
  }
}
````
