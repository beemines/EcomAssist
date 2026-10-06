from dataclasses import dataclass, field

from app.core.errors import SessionBusy


@dataclass(frozen=True)
class Lease:
    conversation_id: str
    _locks: "ConversationLocks" = field(repr=False, compare=False)
    _identity: object = field(default_factory=object, repr=False, compare=False)

    def release(self) -> None:
        # 身份校验防止旧凭证的重复释放影响后来取得的占用。
        if self._locks._occupied.get(self.conversation_id) is self._identity:
            del self._locks._occupied[self.conversation_id]


class ConversationLocks:
    """单 worker、单事件循环内的同步占用检查，无 await 竞争窗口。"""

    def __init__(self):
        self._occupied: dict[str, object] = {}

    def acquire(self, conversation_id: str) -> Lease:
        if conversation_id in self._occupied:
            raise SessionBusy()
        lease = Lease(conversation_id, self)
        self._occupied[conversation_id] = lease._identity
        return lease
