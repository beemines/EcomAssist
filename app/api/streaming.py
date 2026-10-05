import json
import logging

import anyio
from starlette.responses import StreamingResponse
from starlette.types import Receive, Scope, Send

from app.core.chat import ChatService, PreparedChat, StreamEvent


logger = logging.getLogger(__name__)


def encode_sse(event: StreamEvent) -> bytes:
    payload = json.dumps(event.data, ensure_ascii=False, separators=(",", ":"))
    return f"event: {event.event}\ndata: {payload}\n\n".encode("utf-8")


class ManagedChatResponse(StreamingResponse):
    """Own the iterators and lease, including while either generator is paused.

    A successful terminal ASGI send is the commit boundary. It cannot guarantee
    that the remote client actually received those bytes.
    """

    def __init__(self, service: ChatService, prepared: PreparedChat):
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
            terminal = event.event != "delta"
            await send({"type": "http.response.body", "body": encode_sse(event), "more_body": not terminal})
            if event.event == "done":
                # No await may separate successful terminal send and commit.
                self.service.commit(self.prepared)
            if terminal:
                return

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        try:
            version = tuple(map(int, scope.get("asgi", {}).get("spec_version", "2.0").split(".")))
            if version < (2, 4):
                # Starlette owns receive for this branch; never compete for it.
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
                    # Preserve the parent's ordinary ClientDisconnect / cancel
                    # error rather than adding a one-member group wrapper.
                    while isinstance(exc, BaseExceptionGroup) and len(exc.exceptions) == 1:
                        exc = exc.exceptions[0]
                    raise exc
        finally:
            try:
                with anyio.move_on_after(5, shield=True):
                    for iterator in (self.events, self.prepared.upstream):
                        if iterator is not None:
                            try:
                                await iterator.aclose()
                            except Exception:
                                logger.warning("Chat stream cleanup failed.")
            finally:
                self.service.release(self.prepared)
