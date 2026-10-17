"""Execute process guards with injected facts, never touch existing listeners."""
import json
from pathlib import Path
import shutil
import subprocess

from tests.test_demo_server_ownership import powershell

ROOT = Path(__file__).parents[1]


def test_context_unowned_8004_and_partial_cap_are_rejected(tmp_path):
    scripts = tmp_path/'scripts'
    scripts.mkdir()
    for name in ('start-context-demo.ps1', 'context-process-ownership.ps1'):
        assert (ROOT/'scripts'/name).exists(), 'Context launch tooling missing'
        shutil.copy(ROOT/'scripts'/name, scripts/name)
    for args, expected in [('-Profile demo', 'unowned'), ('-Profile demo -RunId partial', 'together')]:
        result = powershell(tmp_path, f"""
function Get-NetTCPConnection {{ [pscustomobject]@{{OwningProcess=999}} }}
function Start-Process {{ throw 'FORBIDDEN_LAUNCH' }}
function Stop-Process {{ throw 'FORBIDDEN_STOP' }}
try {{ & '{scripts/'start-context-demo.ps1'}' {args} }} catch {{ Write-Output $_.Exception.Message; exit 3 }}
""")
        assert result.returncode == 3 and expected in result.stdout.lower(), result.stdout+result.stderr
        assert 'FORBIDDEN' not in result.stdout


def test_context_identity_requires_creation_command_workspace_and_listener(tmp_path):
    helper = ROOT/'scripts/context-process-ownership.ps1'
    assert helper.exists(), 'Context process guard missing'
    result = powershell(tmp_path, f"""
. '{helper}'
$root='D:\\feature'
$interpreter='C:\\locked\\python.exe'
$cmd='"D:\\feature\\.venv\\Scripts\\python.exe" -m uvicorn app.context.acceptance:create_demo_app --factory --host 127.0.0.1 --port 8004 --workers 1 --app-dir "D:\\feature"'
$proc=[pscustomobject]@{{ProcessId=10;ParentProcessId=9;CreationDate=[datetime]'2026-10-17T10:00:01Z';ExecutablePath=$interpreter;CommandLine=$cmd}}
$owner=[pscustomobject]@{{root=$root;interpreter=$interpreter;listener=(New-ContextProcessIdentity $proc)}}
$values=@()
$values+=Test-ContextOwnedProcess $proc $owner $root $interpreter
$proc.CreationDate=$proc.CreationDate.AddSeconds(1)
$values+=Test-ContextOwnedProcess $proc $owner $root $interpreter
$proc.CreationDate=$proc.CreationDate.AddSeconds(-1)
$proc.CommandLine=$cmd.Replace('8004','8003')
$values+=Test-ContextOwnedProcess $proc $owner $root $interpreter
$proc.CommandLine=$cmd.Replace('D:\\feature','D:\\foreign')
$values+=Test-ContextOwnedProcess $proc $owner $root $interpreter
$values+=Test-ContextOwnedProcess $proc ([pscustomobject]@{{pid=10}}) $root $interpreter
ConvertTo-Json -InputObject $values -Compress
""")
    assert result.returncode == 0, result.stderr
    assert json.loads(result.stdout) == [True, False, False, False, False]


async def test_evidence_missing_checkpoint_does_not_create_database(tmp_path):
    import importlib.util
    script = ROOT/'scripts/context-storage-evidence.py'
    assert script.exists(), 'Read-only evidence script missing'
    spec = importlib.util.spec_from_file_location('context_evidence', script)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    missing = tmp_path/'not-created.sqlite'
    assert module.read_checkpoint(missing, '1') is None
    assert not missing.exists()
