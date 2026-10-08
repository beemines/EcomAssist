# 冒烟脚本离线测试，使用碎片化 UTF-8/SSE 响应核验终止帧、连续轮次和抽取结果。
import importlib
import json

import anyio
import httpx
import pytest


ORDER = "20261005001"
EXTRACT = {"order_id": ORDER, "request_type": "return_refund", "expected_solution": "退货退款"}


# 加载在线接口冒烟评测模块，缺失实现时明确失败。
def implementation():
    try:
        return importlib.import_module("evals.smoke")
    except ModuleNotFoundError:
        pytest.fail("smoke implementation is missing")


class Fragments(httpx.AsyncByteStream):
    # 配置按字节分片的响应数据、故障与延迟，并记录关闭状态。
    def __init__(self, data, *, failure=None, delay=0):
        self.data, self.failure, self.delay = data, failure, delay
        self.closed = False

    # 逐字节发送响应，可模拟持续慢流或发送后断连以检验 UTF-8 解码与截止时间。
    async def __aiter__(self):
        for byte in self.data:
            if self.delay:
                await anyio.sleep(self.delay)
            yield bytes([byte])
        if self.failure:
            raise self.failure

    # 记录响应流已关闭，供所有成功和故障路径核对。
    async def aclose(self):
        self.closed = True


# 生成带 CRLF 边界和中文 JSON 数据的 SSE 字节帧。
def frame(event, data):
    return f"event: {event}\r\ndata: {json.dumps(data, ensure_ascii=False)}\r\n\r\n".encode()


# 运行真实冒烟评测并注入各类协议故障，核对请求数量、会话复用、流关闭与报告脱敏。
async def run_smoke(tmp_path, *, mode="good", extraction=EXTRACT, monkeypatch=None):
    module = implementation()
    requests, streams = [], []

    # 模拟创建、抽取和聊天路由，并按场景制造 SSE 缺失、重复、错序、断连或连续性错误。
    def handler(request):
        payload = json.loads(request.content)
        requests.append((request.url.path, payload))
        if request.url.path == "/api/conversations":
            return httpx.Response(200, json={"conversation_id": "9007199254741099"})
        if request.url.path == "/api/extract":
            return httpx.Response(200, json=extraction)
        session = payload["conversation_id"]
        data = frame("delta", {"delta": "您好"}) + frame("delta", {"delta": ORDER}) + frame("done", {"conversation_id": session})
        if mode == "non200":
            return httpx.Response(502, content=b"SECRET")
        if mode == "missing_done":
            data = data[:data.rfind(b"event: done")]
        if mode == "error_done":
            data = frame("error", {"code": "upstream_error", "message": "SECRET"}) + data
        if mode == "duplicate_done":
            data += frame("done", {"conversation_id": session})
        if mode == "after_done":
            data += frame("delta", {"delta": "later"})
        if mode == "one_delta":
            data = frame("delta", {"delta": ORDER}) + frame("done", {"conversation_id": session})
        if mode == "wrong_identity":
            data = data[:data.rfind(b"event: done")] + frame("done", {"conversation_id": "wrong"})
        if mode == "continuity" and len(requests) == 3:
            data = frame("delta", {"delta": "不记得"}) + frame("delta", {"delta": "订单"}) + frame("done", {"conversation_id": session})
        stream = Fragments(data, failure=httpx.ReadError("SECRET") if mode == "disconnect" else None,
                           delay=.005 if mode == "timeout" else 0)
        streams.append(stream)
        return httpx.Response(200, headers={"content-type": "text/event-stream"}, stream=stream)

    if monkeypatch:
        monkeypatch.setattr(module, "CHAT_DEADLINE_SECONDS", .02)
    output = tmp_path / f"{mode}.json"
    async with httpx.AsyncClient(transport=httpx.MockTransport(handler)) as client:
        report = await module.smoke("http://app.invalid", output, http_client=client)
        assert not client.is_closed
    expected_requests = 4 if mode == 'good' else 3 if mode == 'continuity' else 2
    assert len(requests) == report["request_count"] == expected_requests
    if len(requests) >= 3:
        assert requests[1][1]["conversation_id"] == requests[2][1]["conversation_id"]
    assert ORDER in requests[1][1]["message"]
    if len(requests) >= 3:
        assert ORDER not in requests[2][1]["message"]
    assert all(s.closed for s in streams)
    assert "SECRET" not in output.read_text(encoding="utf-8")
    assert json.loads(output.read_text(encoding="utf-8")) == report
    return report, requests


# 验证字节分片中文 SSE、两轮订单连续性与抽取通过，且每次冒烟使用独立用户。
async def test_fragmented_utf8_sse_and_round_continuity(tmp_path):
    report, first = await run_smoke(tmp_path)
    assert report["passed"] is True
    assert report["failures"] == []
    assert report["extract"]["response"] == EXTRACT
    for round in report["rounds"]:
        assert round["nonempty_delta_count"] == 2
        assert round["done_count"] == 1
        assert round["events"] == ["delta", "delta", "done"]
        assert round["first_delta_seconds"] is not None
        assert round["text"] == "您好20261005001"
    assert report["identity"]["provider_verified"] is False
    _, second = await run_smoke(tmp_path)
    assert first[0][1]["user_id"] != second[0][1]["user_id"]


# 验证错误状态、缺失或重复完成、错序增量、编号不符、连续性丢失与断连均不能通过。
@pytest.mark.parametrize("mode", ["non200", "missing_done", "error_done", "duplicate_done", "after_done", "one_delta", "wrong_identity", "continuity", "disconnect"])
async def test_invalid_streams_cannot_pass(tmp_path, mode):
    report, _ = await run_smoke(tmp_path, mode=mode)
    assert report["passed"] is False
    assert report["failures"]


# 验证冒烟抽取必须精确匹配三个预期字段，结构或内容偏差均判失败。
@pytest.mark.parametrize("extraction", [{}, {**EXTRACT, "extra": 1}, {**EXTRACT, "expected_solution": "退款"}])
async def test_extraction_must_match_exact_expected_three_fields(tmp_path, extraction):
    report, _ = await run_smoke(tmp_path, extraction=extraction)
    assert report["passed"] is False
    assert report["extract"]["error_code"] is not None


# 验证持续收到片段也不能突破整体截止时间，首轮超时后后续轮次标记未执行。
async def test_stream_wall_clock_deadline_even_when_chunks_keep_arriving(tmp_path, monkeypatch):
    report, _ = await run_smoke(tmp_path, mode="timeout", monkeypatch=monkeypatch)
    assert report["passed"] is False
    assert report['rounds'][0]['error_code'] == 'timeout'
    assert report['rounds'][1]['error_code'] == 'not_attempted'


# 验证会话创建返回数值编号等非法结构时停止，不能继续调用模型路由。
async def test_creation_failure_never_calls_model_routes(tmp_path):
    requests = []
    # 返回非法数值会话编号并记录请求路径，证明创建失败后的提前终止。
    def handler(request):
        requests.append(request.url.path)
        return httpx.Response(200, json={'conversation_id': 9007199254741099})
    async with httpx.AsyncClient(transport=httpx.MockTransport(handler)) as client:
        report = await implementation().smoke('http://test', tmp_path / 'creation.json', http_client=client)
    assert report['passed'] is False
    assert report['http_request_count'] == 1
    assert requests == ['/api/conversations']
