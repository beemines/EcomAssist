"""Manage only this checkout's local Langfuse project, retaining persistent data."""
from __future__ import annotations

import argparse
import json
import secrets
import socket
import subprocess
from pathlib import Path

from dotenv import dotenv_values

ROOT = Path(__file__).resolve().parents[2]
PROJECT = 'ecs-ch09-langfuse'
SERVER_VERSION = '4.63.0'
REQUIRED = {'LANGFUSE_PORT', 'NEXTAUTH_URL', 'POSTGRES_PASSWORD', 'REDIS_AUTH',
            'CLICKHOUSE_PASSWORD', 'MINIO_ROOT_PASSWORD', 'SALT', 'ENCRYPTION_KEY',
            'NEXTAUTH_SECRET', 'LANGFUSE_INIT_PROJECT_PUBLIC_KEY',
            'LANGFUSE_INIT_PROJECT_SECRET_KEY', 'LANGFUSE_INIT_USER_PASSWORD'}


def _write_new(path: Path, values: dict[str, str]) -> None:
    # Exclusive creation preserves passwords if two launchers race.
    with path.open('x', encoding='utf-8', newline='\n') as stream:
        stream.write(''.join(f'{key}={value}\n' for key, value in values.items()))
    path.chmod(0o600)


def prepare(directory: Path, *, port: int = 3000) -> dict[str, str]:
    if isinstance(port, bool) or not 1 <= port <= 65535:
        raise ValueError('Invalid local Langfuse port')
    directory.mkdir(parents=True, exist_ok=True)
    env_file = directory / 'local.env'
    origin = f'http://127.0.0.1:{port}'
    if not env_file.exists():
        token = lambda: secrets.token_hex(24)
        try:
            _write_new(env_file, {
                'LANGFUSE_PORT': str(port), 'NEXTAUTH_URL': origin,
                'POSTGRES_PASSWORD': token(), 'REDIS_AUTH': token(),
                'CLICKHOUSE_PASSWORD': token(), 'MINIO_ROOT_USER': 'langfuse',
                'MINIO_ROOT_PASSWORD': token(), 'SALT': token(),
                'ENCRYPTION_KEY': secrets.token_hex(32), 'NEXTAUTH_SECRET': token(),
                'LANGFUSE_INIT_ORG_ID': 'ch09-local-org',
                'LANGFUSE_INIT_ORG_NAME': 'EcomAssist Local',
                'LANGFUSE_INIT_PROJECT_ID': 'ch09-local-project',
                'LANGFUSE_INIT_PROJECT_NAME': 'EcomAssist CH09',
                'LANGFUSE_INIT_PROJECT_PUBLIC_KEY': 'pk-lf-' + token(),
                'LANGFUSE_INIT_PROJECT_SECRET_KEY': 'sk-lf-' + token(),
                'LANGFUSE_INIT_USER_EMAIL': 'admin@ch09.local',
                'LANGFUSE_INIT_USER_NAME': 'Local Admin',
                'LANGFUSE_INIT_USER_PASSWORD': token(),
            })
        except FileExistsError:
            pass
    values = dict(dotenv_values(env_file))
    if (not REQUIRED <= values.keys() or any(not values[k] for k in REQUIRED)
            or values['LANGFUSE_PORT'] != str(port) or values['NEXTAUTH_URL'] != origin):
        raise ValueError('Existing local.env is incomplete or uses another port; preserve credentials and inspect it')
    sdk = {'LANGFUSE_ENABLED': 'true', 'LANGFUSE_BASE_URL': origin,
           'LANGFUSE_PUBLIC_KEY': values['LANGFUSE_INIT_PROJECT_PUBLIC_KEY'],
           'LANGFUSE_SECRET_KEY': values['LANGFUSE_INIT_PROJECT_SECRET_KEY']}
    sdk_file = directory / 'sdk.env'
    if not sdk_file.exists():
        try:
            _write_new(sdk_file, sdk)
        except FileExistsError:
            pass
    if dict(dotenv_values(sdk_file)) != sdk:
        raise ValueError('Local SDK settings differ from server initialization; no credentials overwritten')
    return {'url': origin, 'server_env': str(env_file), 'sdk_env': str(sdk_file),
            'login_email': values.get('LANGFUSE_INIT_USER_EMAIL', 'admin@ch09.local')}


def _docker(*args: str, timeout: int = 60) -> str:
    # Never echo the expanded environment or provider error output containing secrets.
    result = subprocess.run(['docker', *args], cwd=ROOT, capture_output=True,
                            text=True, encoding='utf-8', errors='replace', timeout=timeout)
    if result.returncode:
        directory = ROOT / 'runtime/langfuse'
        diagnostic = result.stderr[-16000:]
        try:
            for key, value in dotenv_values(directory / 'local.env').items():
                if value and any(word in key for word in ('PASSWORD', 'SECRET', 'KEY', 'SALT', 'REDIS_AUTH')):
                    diagnostic = diagnostic.replace(value, '[redacted]')
            directory.mkdir(parents=True, exist_ok=True)
            (directory / 'docker-error.log').write_text(diagnostic, encoding='utf-8')
        except OSError:
            pass
        raise RuntimeError(f'Docker command failed (exit {result.returncode}); see runtime/langfuse/docker-error.log')
    return result.stdout


def _owned_containers() -> bool:
    ids = _docker('ps', '-aq', '--filter', f'label=com.docker.compose.project={PROJECT}').split()
    for container_id in ids:
        labels = json.loads(_docker('inspect', container_id, '--format', '{{json .Config.Labels}}'))
        working_dir = labels.get('com.docker.compose.project.working_dir', '')
        if not working_dir or Path(working_dir).resolve() != ROOT:
            raise RuntimeError('Compose project belongs to another checkout; refusing to manage it')
    return bool(ids)


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('action', choices=('prepare', 'up', 'status', 'stop'))
    parser.add_argument('--port', type=int, default=3000)
    args = parser.parse_args(argv)
    try:
        data = prepare(ROOT / 'runtime/langfuse', port=args.port)
        if args.action == 'prepare':
            print(json.dumps(data, ensure_ascii=False))
            return 0
        owned = _owned_containers()
        compose = ['compose', '--env-file', data['server_env'], '-f',
                   str(ROOT / 'compose.langfuse.yaml'), '-p', PROJECT]
        if args.action == 'up':
            with socket.socket() as probe:
                probe.settimeout(1)
                occupied = probe.connect_ex(('127.0.0.1', args.port)) == 0
            if occupied and not owned:
                raise RuntimeError('Local UI port is occupied by an unowned service')
            _docker(*compose, 'config', '--quiet')
            _docker(*compose, 'up', '-d', '--wait', '--wait-timeout', '240', timeout=1200)
            print(json.dumps({**data, 'status': 'ready'}, ensure_ascii=False))
        elif args.action == 'stop':
            if owned:
                _docker(*compose, 'stop', timeout=90)
            print('Local Langfuse stopped; persistent data retained.')
        else:
            print(_docker(*compose, 'ps', '--format', 'json'))
        return 0
    except (ValueError, RuntimeError, OSError, subprocess.TimeoutExpired) as exc:
        # Never stringify subprocess/provider exceptions containing environment values.
        if isinstance(exc, (ValueError, RuntimeError)):
            print(str(exc))
        else:
            print(f'Local Langfuse operation failed: {type(exc).__name__}')
        return 1


if __name__ == '__main__':
    raise SystemExit(main())
