"""创建持久会话后通过两轮聊天和提取完成冒烟验收。"""

import argparse
import asyncio
import codecs
import json
from pathlib import Path
from time import monotonic
from uuid import uuid4

import anyio
import httpx

from evals.evaluate import extract_request, identity, save_report


REQUEST_DEADLINE_SECONDS = 75.0
CHAT_DEADLINE_SECONDS = 150.0
ORDER = "20261005001"
EXTRACT_TEXT = "订单 20261005001 的杯子收到就碎了，我想退货退款。"
EXTRACT_EXPECTED = {"order_id": ORDER, "request_type": "return_refund", "expected_solution": "退货退款"}


# 调用会话创建接口并校验规范十进制字符串身份，返回安全错误分类。
async def create_conversation(client, base_url, user_id) -> dict:
    from app.repositories.conversations import _conversation_id
    result = {"conversation_id": None, "status_code": None, "error_code": None}
    try:
        with anyio.fail_after(REQUEST_DEADLINE_SECONDS):
            response = await client.post(base_url.rstrip('/') + '/api/conversations', json={"user_id": user_id}, timeout=REQUEST_DEADLINE_SECONDS)
            result['status_code'] = response.status_code
            if response.status_code != 200:
                result['error_code'] = 'http_error'
            else:
                data = response.json()
                if not isinstance(data, dict) or set(data) != {'conversation_id'}:
                    raise ValueError
                _conversation_id(data['conversation_id'])
                result['conversation_id'] = data['conversation_id']
    except (TimeoutError, httpx.TimeoutException):
        result['error_code'] = 'timeout'
    except httpx.HTTPError:
        result['error_code'] = 'transport_error'
    except Exception:
        result['error_code'] = 'invalid_conversation'
    return result


# 读取一轮聊天 SSE，统计非空片段、首字延迟及唯一且匹配的 done 帧。
# 网络 EOF 本身不表示成功；帧格式、身份和结束顺序都要通过校验。
async def chat_round(client, base_url, conversation_id, message, *, min_deltas=2) -> dict:
    result = {"status_code": None, "events": [], "deltas": [], "text": "", "nonempty_delta_count": 0,
              "done_count": 0, "first_delta_seconds": None, "error_code": None}
    started = monotonic()
    decoder = codecs.getincrementaldecoder("utf-8")()
    buffer = ""
    frame_lines = []
    protocol_errors = []

    # 解析已收齐的一帧 SSE，累计状态与正文并记录终止后的协议异常。
    def consume_frame():
        event = None
        data_lines = []
        for line in frame_lines:
            if line.startswith(":"):
                continue
            key, _, value = line.partition(":")
            value = value.removeprefix(" ")
            if key == "event":
                if event is not None:
                    raise ValueError
                event = value
            elif key == "data":
                data_lines.append(value)
        if event is None and not data_lines:
            return
        if event not in {"status", "delta", "done", "error"}:
            raise ValueError
        data = json.loads("\n".join(data_lines))
        if not isinstance(data, dict):
            raise ValueError
        result["events"].append(event)
        if result["done_count"]:
            protocol_errors.append('event_after_done')
        if event == 'status':
            if data.get('phase') not in {'selecting', 'tool_running', 'tool_completed', 'answering'}:
                raise ValueError
        elif event == "delta":
            if set(data) != {"delta"} or not isinstance(data["delta"], str):
                raise ValueError
            result["deltas"].append(data["delta"])
            if data["delta"].strip():
                result["nonempty_delta_count"] += 1
                if result["first_delta_seconds"] is None:
                    result["first_delta_seconds"] = monotonic() - started
        elif event == "done":
            result["done_count"] += 1
            if data != {"conversation_id": conversation_id}:
                protocol_errors.append("wrong_identity")
        else:
            # 保留错误事件的证据，丢弃不可信的错误提示内容。
            protocol_errors.append("error_event")
            code = data.get('code')
            result['server_error_code'] = code if code in {'upstream_error', 'upstream_timeout', 'input_too_long', 'database_error'} else 'unknown_error'

    try:
        with anyio.fail_after(CHAT_DEADLINE_SECONDS):
            async with client.stream("POST", base_url.rstrip("/") + "/api/chat",
                                     json={"conversation_id": conversation_id, "message": message}, timeout=CHAT_DEADLINE_SECONDS) as response:
                result["status_code"] = response.status_code
                if response.status_code != 200:
                    result["error_code"] = "http_error"
                elif not response.headers.get("content-type", "").startswith("text/event-stream"):
                    result["error_code"] = "invalid_content_type"
                else:
                    async for chunk in response.aiter_bytes():
                        buffer += decoder.decode(chunk)
                        while "\n" in buffer:
                            line, buffer = buffer.split("\n", 1)
                            line = line.removesuffix("\r")
                            if line:
                                frame_lines.append(line)
                            else:
                                consume_frame()
                                frame_lines.clear()
                    buffer += decoder.decode(b"", final=True)
                    if buffer or frame_lines:
                        raise ValueError
    except (TimeoutError, httpx.TimeoutException):
        result["error_code"] = "timeout"
    except httpx.HTTPError:
        result["error_code"] = "transport_error"
    except (ValueError, UnicodeError):
        result["error_code"] = "invalid_sse"
    result["text"] = "".join(result["deltas"])
    if result["error_code"] is None:
        if protocol_errors:
            result["error_code"] = protocol_errors[0]
        elif result["done_count"] != 1 or not result["events"] or result["events"][-1] != "done":
            result["error_code"] = "invalid_terminal_event"
        elif result["nonempty_delta_count"] < min_deltas:
            result["error_code"] = "insufficient_deltas"
    return result


# 创建独立会话，依次验证首轮回复、订单号上下文和售后结构化提取。
# 前一环节失败就不再发后续验收请求，报告中保留未尝试状态。
async def smoke(base_url: str, output_path: Path, *, http_client: httpx.AsyncClient | None = None) -> dict:
    user_id = "smoke-" + uuid4().hex
    owns_client = http_client is None
    client = http_client if http_client is not None else httpx.AsyncClient(timeout=REQUEST_DEADLINE_SECONDS, trust_env=False)
    try:
        created = await create_conversation(client, base_url, user_id)
        conversation_id = created['conversation_id']
        if created['error_code'] is not None:
            report = {'kind': 'interface_smoke', 'passed': False, 'failures': [{'scenario': 'create_conversation', 'error_code': created['error_code']}], 'identity': identity(), 'http_request_count': 1, 'request_count': 1, 'model_request_count': None, 'conversation_id': None, 'rounds': [], 'extract': None, 'human_role_review': 'pending'}
            save_report(output_path, report)
            return report
        first = await chat_round(client, base_url, conversation_id, f"我的订单号是 {ORDER}，杯子收到就碎了，请给我售后建议。")
        request_count = 2
        second = {'error_code': 'not_attempted'}
        extracted = {'error_code': 'not_attempted', 'response': None}
        if first['error_code'] is None:
            second = await chat_round(client, base_url, conversation_id, "我刚才提供的订单号是什么？请复述并说明下一步。")
            request_count += 1
            if second['error_code'] is None and ORDER not in second['text']:
                second['error_code'] = 'lost_order_continuity'
            if second['error_code'] is None:
                extracted = await extract_request(client, base_url, EXTRACT_TEXT, deadline=REQUEST_DEADLINE_SECONDS)
                request_count += 1
    finally:
        if owns_client:
            await client.aclose()
    if extracted["error_code"] is None and extracted["response"] != EXTRACT_EXPECTED:
        extracted["error_code"] = "unexpected_extraction"
    failures = [{"scenario": name, "error_code": result["error_code"]}
                for name, result in (("chat_round_1", first), ("chat_round_2", second), ("extract", extracted))
                if result["error_code"] is not None]
    report = {"kind": "interface_smoke", "passed": not failures, "failures": failures,
              "identity": identity(), "request_count": request_count, "http_request_count": request_count,
              "model_request_count": None, "model_count_source": "requires_upstream_instrumentation",
              "conversation_id": conversation_id,
              "rounds": [first, second], "extract": extracted,
              "human_role_review": "pending"}
    save_report(output_path, report)
    return report


# 解析服务地址与报告路径，运行冒烟验收并写入明确的配置身份信息。
def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--base-url", default="http://127.0.0.1:8000")
    parser.add_argument("--output", type=Path, default=Path(".cache/tool-smoke.json"))
    parser.add_argument("--configured-upstream")
    parser.add_argument("--configured-model")
    args = parser.parse_args()
    report = asyncio.run(smoke(args.base_url, args.output))
    report["identity"] = identity(configured_upstream=args.configured_upstream, configured_model=args.configured_model)
    save_report(args.output, report)
    print(json.dumps({"passed": report["passed"], "failures": report["failures"]}, ensure_ascii=False))
    return 0 if report["passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
