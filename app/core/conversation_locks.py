# 限制同一会话同时进行一轮聊天，通过占用凭证避免旧请求释放新请求的锁。
from dataclasses import dataclass, field

from app.core.errors import SessionBusy


@dataclass(frozen=True)
class Lease:
    conversation_id: str
    _locks: "ConversationLocks" = field(repr=False, compare=False)
    _identity: object = field(default_factory=object, repr=False, compare=False)

    # 仅释放自身仍持有的会话占用，允许安全地重复调用。
    def release(self) -> None:
        # 身份校验防止旧凭证的重复释放影响后来取得的占用。
        if self._locks._occupied.get(self.conversation_id) is self._identity:
            del self._locks._occupied[self.conversation_id]


class ConversationLocks:
    """单 worker、单事件循环内的同步占用检查，无 await 竞争窗口。"""

    # 初始化当前进程内的会话占用表。
    def __init__(self):
        self._occupied: dict[str, object] = {}

    # 同步检查并占用会话，重复请求抛出忙碌错误。
    def acquire(self, conversation_id: str) -> Lease:
        if conversation_id in self._occupied:
            raise SessionBusy()
        lease = Lease(conversation_id, self)
        self._occupied[conversation_id] = lease._identity
        return lease
