import json
import logging

import anyio
from starlette.responses import StreamingResponse
from starlette.types import Receive, Scope, Send

from app.core.chat import StreamEvent
from app.core.tool_chat import ToolChatService, PreparedToolChat


logger = logging.getLogger(__name__)


def encode_sse(event: StreamEvent) -> bytes:
    payload = json.dumps(event.data, ensure_ascii=False, separators=(",", ":"))
    return f"event: {event.event}\ndata: {payload}\n\n".encode("utf-8")


class ManagedChatResponse(StreamingResponse):
    """负责迭代器和会话占用凭证的生命周期，包括生成器暂停期间。

    服务先提交完整回答，响应层再发送 done；发送失败不回滚已提交结果。
    """

    def __init__(self, service: ToolChatService, prepared: PreparedToolChat):
        self.service = service
        self.prepared = prepared
        self.events = service.stream(prepared)
        super().__init__(
            self.events,
            media_type="text/event-stream",
            headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"},
        )

    async def stream_response(self, send: Send) -> None:
        await send({"type": "http.response.start", "status": self.status_code, "headers": self.raw_headers})
        async for event in self.events:
            terminal = event.event in {"done", "error"}
            await send({"type": "http.response.body", "body": encode_sse(event), "more_body": not terminal})
            if terminal:
                return

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        try:
            version = tuple(map(int, scope.get("asgi", {}).get("spec_version", "2.0").split(".")))
            if version < (2, 4):
                # 此分支由 Starlette 负责 receive，不能与它竞争读取。
                await super().__call__(scope, receive, send)
            else:
                try:
                    async with anyio.create_task_group() as tasks:
                        async def disconnect():
                            await self.listen_for_disconnect(receive)
                            tasks.cancel_scope.cancel()

                        tasks.start_soon(disconnect)
                        await super().__call__(scope, receive, send)
                        tasks.cancel_scope.cancel()
                except BaseExceptionGroup as exc:
                    # 保留父类原有的 ClientDisconnect 或取消异常，
                    # 避免额外包裹一层只含单个异常的异常组。
                    while isinstance(exc, BaseExceptionGroup) and len(exc.exceptions) == 1:
                        exc = exc.exceptions[0]
                    raise exc
        finally:
            try:
                with anyio.move_on_after(5, shield=True):
                    try:
                        await self.events.aclose()
                    except Exception:
                        logger.warning("Chat stream cleanup failed.")
            finally:
                self.service.release(self.prepared)
