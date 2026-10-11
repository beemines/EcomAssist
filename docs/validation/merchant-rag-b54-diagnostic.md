# B54 单次实际改写诊断

2026-10-11 用户另行批准 B54 改写一次，root 完整读取 helper 并明确放行后仅执行一次。诊断合法，实际 HTTP 出站 1、rewrite 1，其余六阶段（self_check、answer、judge、embedding、rerank、milvus）均 0，客户端清理成功。诊断结束即停止收费；本范围没有试跑、全量或后续探针。

Probe `59e4d535ec0c4471bbe2538e2c18a39d`，来源为失败 pilot `b1af9aadc0094141aa5df5ae0ec91bd1` 的 B54。开始 `2026-10-11T04:31:51.020566Z`，结束 `04:31:53.909754Z`，耗时 2.889186199987307 秒。GLM-5.3-Flash、评估专用 low、输出 2048、输入 847/8000、SDK/改写期限各 60 秒、重试 0，完整配置指纹 `191d53c027323fa8005327336e6ec0e737f7d196eebd6ad05f2dea7258f60913` 均保持。

HTTP 200、HTTP/1.1、响应 601 字节、choice finish=stop。LangChain 返回原 AIMessage 108 字符、finish=stop、parsed=QueryPlan、parsing_error=null；未改动的原 JSON 为合法对象，无额外字段，standard 为字符串、expansions 为含 3 条的列表。生产严格 JSON/Pydantic/parsed 一致性校验通过后，现有 safe-plan 锚点保护保守返回原问句和 0 条 expansions。原有校验、保护规则和期限均未弱化。

调用前离线重建使用生产消息构造器，消息摘要与准备证明一致，无 gold，模型/客户端构造与上游请求均 0。原失败调用未保存完整消息字节，所以这是同构造器与离线证明的一致性，而不是原请求字节相等证明。返回捕获位于生产校验之前，完整输入、HTTP 正文、结构化输出和最终 plan 只私存；公开报告仅白名单状态、类型、长度、摘要和计数。独占执行标记已经存在，禁止重跑。root 又独立离线重跑生产严格校验和 safe-plan，并核对计数、清理与六个旧公开文件摘要，额外上游请求 0。

旧三轮 pilot 六个公开文件字节摘要保持，旧错误不补行或覆盖。本次成功不能确定旧 B54 的具体失败原因；旧记录缺失 raw/finish/ServiceError.code，不能作根因猜测或修复声明。最新真实 pilot 仍为 40 尝试、32 完整完成、8 改写错误，matching_pilot=false；full 300 题/1200 条未运行，Task10 保持开放。该单次诊断不进入运行资格或质量分母。

API 捕获边界依据已保存的官方文档：[LangChain include_raw](https://reference.langchain.com/python/langchain-openai/chat_models/base/ChatOpenAI/with_structured_output)、[ChatOpenAI 元数据](https://reference.langchain.com/python/langchain-openai/ChatOpenAI)、[HTTPX hooks](https://github.com/encode/httpx/blob/master/docs/advanced/event-hooks.md)。无新增工程测试、源码修改、数据库/Milvus操作或8000/8001操作。

以下元数据与独立 [JSON](merchant-rag-b54-diagnostic.json) 逐值相同：

```json
{
  "kind": "actual-bounded-single-rewrite-diagnostic-not-pilot",
  "authorization_scope": "B54 rewrite once only; success does not authorize pilot/full or another probe",
  "reviewed_source_commit": "cfc65fdb99e44de68c2727e05743a384bba6e89e",
  "execution_checkout_commit": "77a541153f50e4b66d793eb7e9a1596edc932b47",
  "offline_preparation": {
    "kind": "offline-single-rewrite-diagnostic-ready-not-executed",
    "source_run_id": "b1af9aadc0094141aa5df5ae0ec91bd1",
    "case": "B54",
    "prepared_at": "2026-10-11T04:31:50.969401+00:00",
    "config_equal_captured": true,
    "config_fingerprint": "191d53c027323fa8005327336e6ec0e737f7d196eebd6ad05f2dea7258f60913",
    "model": "glm-5.3-flash",
    "reasoning_effort": "low",
    "rewrite_output_tokens": 2048,
    "rewrite_timeout_s": 60,
    "sdk_timeout_s": 60,
    "input_tokens_estimate": 847,
    "input_budget": 8000,
    "messages_sha256": "55ae7e897ce1ff76c387325ce61f41394263af55487f90905a2d1fab02a75538",
    "original_message_bytes_saved": false,
    "gold_in_request": false,
    "models_constructed": 0,
    "clients_constructed": 0,
    "upstream_requests": 0,
    "retries": 0,
    "original_six_public_hashes_unchanged": true,
    "execution_marker_exists": false,
    "versions": {
      "langchain-openai": "1.6.7",
      "langchain-core": "1.6.6",
      "httpx": "0.28.1"
    },
    "capture_boundary": "Transparent structured_model.ainvoke return before production QueryPlanner finish/strict raw JSON/safe-plan validation",
    "scope": "Only B54 rewrite once; successful diagnosis never authorizes pilot/full"
  },
  "actual_result": {
    "kind": "actual-bounded-single-rewrite-diagnostic-not-pilot",
    "probe_id": "59e4d535ec0c4471bbe2538e2c18a39d",
    "source_run_id": "b1af9aadc0094141aa5df5ae0ec91bd1",
    "case": "B54",
    "started_at": "2026-10-11T04:31:51.020566+00:00",
    "config_fingerprint": "191d53c027323fa8005327336e6ec0e737f7d196eebd6ad05f2dea7258f60913",
    "legal": true,
    "production_plan_validated": true,
    "standard_equals_question": true,
    "expansions_count": 0,
    "finished_at": "2026-10-11T04:31:53.909754+00:00",
    "elapsed_s": 2.889186199987307,
    "capture": {
      "structured_returned": true,
      "raw_ai_message": true,
      "finish_reason": "stop",
      "body_characters": 108,
      "parsed_type": "QueryPlan",
      "parsing_error_type": null,
      "raw_json_valid": true,
      "raw_json_object": true,
      "unexpected_field_count": 0,
      "standard_type": "str",
      "expansions_type": "list",
      "expansions_count": 3
    },
    "http": [
      {
        "status_code": 200,
        "http_version": "HTTP/1.1",
        "body_bytes": 601,
        "json_parseable": true,
        "choice_finish_reasons": [
          "stop"
        ]
      }
    ],
    "actual_outgoing_count": 1,
    "request_counts": {
      "rewrite": 1,
      "self_check": 0,
      "answer": 0,
      "judge": 0,
      "embedding": 0,
      "rerank": 0,
      "milvus": 0
    },
    "cleanup": {
      "ok": true,
      "errors": [],
      "unverified": []
    },
    "original_six_public_hashes_unchanged": true
  },
  "actual_outgoing": [
    {
      "stage": "rewrite",
      "sent_at": "2026-10-11T04:31:52.667364+00:00",
      "model": "glm-5.3-flash",
      "reasoning_effort": "low",
      "output_tokens": 2048,
      "json_mode": true,
      "stream": false
    }
  ],
  "original_public_sha256": {
    "merchant-rag-pilot.json": "b2865bbd127305bf2436b28c69fc1bdd35ac14a39f065f42bb5a9b9028725501",
    "merchant-rag-pilot.md": "48e5eeee19f0a20c0470fa90da92c28b3e12b96e66ef3ef84d20742bf72bc352",
    "merchant-rag-low-effort-pilot.json": "d0c97061a1b62c85378a44e3f8ed95b693ed3dcd4e5242ef846a23facfd9e8ee",
    "merchant-rag-low-effort-pilot.md": "c0bf7930537e0c78a469c8f9d3176f00cbce96d02df304b80e764b31e17c9b9e",
    "merchant-rag-c5-followup-pilot.json": "37020a3058913b3e7454023aab58603c27393654f1e6ee8a76337c941dc1b47a",
    "merchant-rag-c5-followup-pilot.md": "84da91d9adbc19250a5c24f0119d318d9163649dd6cfdb9a7397bb7bf5ea0167"
  },
  "independent_offline_verification": {
    "production_strict_output_and_safe_plan": true,
    "requests": 0
  },
  "limitations": [
    "Original failing request message bytes and raw/finish/ServiceError.code were not saved; reconstruction matches production builders and the offline proof, not original captured bytes.",
    "Three raw expansions passed strict JSON validation; existing safe-plan protection conservatively returned the original question with zero expansions.",
    "This new legal diagnostic cannot establish the cause of the original B54 failure, repair that record, or qualify a pilot.",
    "Latest actual pilot remains 32 completed/8 rewrite_error out of 40; full 300/1200 remains not run and Task10 open."
  ]
}
```
