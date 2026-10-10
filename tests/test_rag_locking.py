"""真实 OS 锁验收，验证跨进程排他和进程死亡释放。"""

import importlib
from pathlib import Path
import subprocess
import sys
import time

import pytest


def api():
    """缺少 OS 锁功能时用明确断言产生 RED。"""
    assert importlib.util.find_spec("app.rag_evaluation.locking"), "尚未实现跨进程运行锁"
    return importlib.import_module("app.rag_evaluation.locking")


def test_process_local_alias_is_busy_and_close_is_idempotent(tmp_path):
    """同根路径别名不得重复获取；重复关闭不误释后继租约。"""
    module = api()
    lease = module.RunLock(tmp_path).acquire()
    with pytest.raises(module.RunBusy):
        module.RunLock(tmp_path / ".").acquire()
    lease.close()
    next_lease = module.RunLock(tmp_path).acquire()
    lease.close()
    with pytest.raises(module.RunBusy):
        module.RunLock(tmp_path).acquire()
    next_lease.close()
    assert (tmp_path / "evaluation.lock").read_bytes() == b"\0"


def test_two_processes_cannot_acquire_same_lock_and_death_releases(tmp_path):
    """子进程持锁时即刻拒绝父进程；强制终止后原锁文件可重新获取。"""
    module = api()
    ready = tmp_path / "ready"
    script = """
import sys, time
from pathlib import Path
from app.rag_evaluation.locking import RunLock
lease = RunLock(Path(sys.argv[1])).acquire()
Path(sys.argv[2]).write_text('ready', encoding='utf-8')
time.sleep(60)
"""
    process = subprocess.Popen([sys.executable, "-c", script, str(tmp_path), str(ready)],
        cwd=Path(__file__).resolve().parents[1], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    try:
        deadline = time.monotonic() + 10
        while not ready.exists() and process.poll() is None and time.monotonic() < deadline:
            time.sleep(.02)
        if not ready.exists():
            process.kill()
            stdout, stderr = process.communicate(timeout=5)
            pytest.fail(f"子进程未就绪: {stdout!r} {stderr!r}")
        start = time.monotonic()
        with pytest.raises(module.RunBusy):
            module.RunLock(tmp_path / ".").acquire()
        assert time.monotonic() - start < 1
        process.kill()
        process.communicate(timeout=5)
        lease = module.RunLock(tmp_path).acquire()
        lease.close()
        assert (tmp_path / "evaluation.lock").read_bytes() == b"\0"
    finally:
        if process.poll() is None:
            process.kill()
        process.communicate(timeout=5)


def test_symlink_lock_file_is_rejected(tmp_path):
    """锁文件符号链接不能把 OS 锁转移到根目录外。"""
    module = api()
    outside = tmp_path / "outside"
    outside.write_bytes(b"x")
    root = tmp_path / "runs"
    root.mkdir()
    try:
        (root / "evaluation.lock").symlink_to(outside)
    except OSError:
        pytest.skip("本机没有创建文件符号链接权限")
    with pytest.raises(module.StoreError):
        module.RunLock(root).acquire()
    assert outside.read_bytes() == b"x"
