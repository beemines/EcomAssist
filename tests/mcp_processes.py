"""Owned child processes only; no port-based killing."""
import asyncio
from contextlib import asynccontextmanager
import socket
import re
import subprocess
import sys
from uuid import uuid4

import httpx


def free_port():
    with socket.socket() as sock:
        sock.bind(('127.0.0.1', 0))
        return sock.getsockname()[1]


@asynccontextmanager
async def server_process(module, tmp_path, *, plugin=None):
    # Let the child bind port0 itself; closing a probe socket leaves a race and
    # can hit transient Windows/Docker port reservations before uvicorn binds.
    command = [sys.executable, '-m', module, '--port', '0']
    if plugin:
        command += ['--plugin-module', plugin]
    log_path=tmp_path/f'mcp-{uuid4().hex}.log'
    with log_path.open('w', encoding='utf-8') as log:
        process = subprocess.Popen(command, stdout=log, stderr=log,
            creationflags=subprocess.CREATE_NO_WINDOW if sys.platform == 'win32' else 0)
        url=None
        try:
            async with httpx.AsyncClient(timeout=.5, trust_env=False) as client:
                for _ in range(200):
                    if process.poll() is not None:
                        raise RuntimeError(f'MCP child exited ({process.returncode}): {log_path}')
                    if url is None:
                        bound=re.search(r'Uvicorn running on http://127\.0\.0\.1:(\d+)',
                            log_path.read_text(encoding='utf-8',errors='replace'))
                        if bound is None:
                            await asyncio.sleep(.05)
                            continue
                        url=f'http://127.0.0.1:{int(bound.group(1))}/mcp'
                    try:
                        response = await client.get(url)
                        if response.status_code in (400, 405, 406):
                            break
                    except httpx.TransportError:
                        pass
                    await asyncio.sleep(.05)
                else:
                    raise TimeoutError('Owned MCP child did not start')
            yield process, {'transport': 'streamable_http', 'url': url, 'timeout': 2, 'sse_read_timeout': 3}
        finally:
            if process.poll() is None:
                process.terminate()
                await asyncio.to_thread(process.wait, timeout=5)
