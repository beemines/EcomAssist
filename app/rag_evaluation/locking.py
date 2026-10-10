"""固定首字节与打开句柄实现跨进程排他；锁文件永不按 PID 重建。"""

import errno
import os
from pathlib import Path
import threading

from app.rag_evaluation.store import StoreError, canonical_root, guarded_path

if os.name == "nt":
    import msvcrt
else:
    import fcntl

_HELD_ROOTS = set()
_PROCESS_GUARD = threading.Lock()


class RunBusy(RuntimeError):
    """相同规范化根已有运行持锁，调用方不得启动第二个评估。"""


def _os_lock(stream, *, release: bool = False) -> None:
    """Windows 从首字节非阻塞锁定；Unix 使用等价排他 flock。"""
    stream.seek(0)
    if os.name == "nt":
        msvcrt.locking(stream.fileno(), msvcrt.LK_UNLCK if release else msvcrt.LK_NBLCK, 1)
    else:
        fcntl.flock(stream.fileno(), fcntl.LOCK_UN if release else fcntl.LOCK_EX | fcntl.LOCK_NB)


class RunLease:
    """持有 OS 句柄和进程内占位；close 只释放自己的租约一次。"""

    def __init__(self, stream, key: str):
        """租约只能由成功 acquire 创建，打开句柄生命周期涵盖整个运行。"""
        self._stream = stream
        self._key = key

    def close(self) -> None:
        """幂等关闭，任何解锁异常仍关闭句柄并撤销进程占位。"""
        with _PROCESS_GUARD:
            if self._stream is None:
                return
            stream, self._stream = self._stream, None
            try:
                _os_lock(stream, release=True)
            finally:
                stream.close()
                _HELD_ROOTS.discard(self._key)


class RunLock:
    """HTTP 与 CLI 共用的规范根 OS 锁，忙时立即抛 RunBusy。"""

    def __init__(self, root: Path):
        """拒绝根目录链接并规范化路径大小写别名。"""
        self.root = canonical_root(root)
        self._key = os.path.normcase(str(self.root))

    def acquire(self) -> RunLease:
        """固定 evaluation.lock 首字节，持锁文件不能删除或截断。"""
        with _PROCESS_GUARD:
            if self._key in _HELD_ROOTS:
                raise RunBusy("已有评估运行")
            stream = None
            try:
                path = guarded_path(self.root, "evaluation.lock")
                self.root.mkdir(parents=True, exist_ok=True)
                descriptor = os.open(path, os.O_RDWR | os.O_CREAT, 0o600)
                stream = os.fdopen(descriptor, "r+b", buffering=0)
                _os_lock(stream)
                if os.fstat(stream.fileno()).st_size == 0:
                    stream.write(b"\0")
                    stream.flush()
                _HELD_ROOTS.add(self._key)
                return RunLease(stream, self._key)
            except OSError as exc:
                if stream is not None:
                    stream.close()
                if exc.errno in (errno.EACCES, errno.EAGAIN, errno.EDEADLK):
                    raise RunBusy("已有评估运行") from exc
                raise StoreError("运行锁文件无法打开") from exc
