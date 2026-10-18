from pathlib import Path
import json
import subprocess


def powershell(tmp_path, body):
    script = tmp_path / 'ownership.ps1'
    script.write_text(body, encoding='utf-8-sig')
    return subprocess.run(['pwsh', '-NoProfile', '-File', str(script)], capture_output=True, text=True, encoding='utf-8', timeout=30)


def test_process_identity_root_interpreter_command_and_ancestry_are_all_required(tmp_path):
    helper = (Path('scripts/tool-system-process-ownership.ps1').resolve()).as_posix()
    body = r"""
$ErrorActionPreference='Stop'
. 'HELPER'
$root='D:\project'
$interpreter='C:\Python\python.exe'
$command=Get-ToolSystemCommand $root 'logistics' ''
$launch=[pscustomobject]@{ProcessId=10;ParentProcessId=1;CreationDate=[datetime]'2026-10-18T10:00:00Z';ExecutablePath=$interpreter;CommandLine=$command}
$launch.ExecutablePath=Join-Path $root '.venv\Scripts\python.exe'
$childCommand='"'+$interpreter+'"  '+$command.Substring($command.IndexOf('" ')+2)
$process=[pscustomobject]@{ProcessId=11;ParentProcessId=10;CreationDate=[datetime]'2026-10-18T10:00:01Z';ExecutablePath=$interpreter;CommandLine=$childCommand}
$owner=[pscustomobject]@{root=$root;interpreter=$interpreter;command=$command;listener=(New-ContextProcessIdentity $process);launch=(New-ContextProcessIdentity $launch)}
$valid=Test-ToolSystemOwner $process $owner $root $interpreter $command @($launch,$process)
$process.CreationDate=$process.CreationDate.AddSeconds(1)
$reuse=Test-ToolSystemOwner $process $owner $root $interpreter $command @($launch,$process)
$process.CreationDate=$process.CreationDate.AddSeconds(-1)
$rootMismatch=Test-ToolSystemOwner $process $owner 'D:\other' $interpreter $command @($launch,$process)
$exeMismatch=Test-ToolSystemOwner $process $owner $root 'C:\other\python.exe' $command @($launch,$process)
$cmdMismatch=Test-ToolSystemOwner $process $owner $root $interpreter ($command+' --unexpected') @($launch,$process)
$parentMismatch=Test-ToolSystemOwner $process $owner $root $interpreter $command @($process)
@($valid,$reuse,$rootMismatch,$exeMismatch,$cmdMismatch,$parentMismatch) | ConvertTo-Json -Compress
""".replace('HELPER', helper)
    result = powershell(tmp_path, body)
    assert result.returncode == 0, result.stderr
    assert json.loads(result.stdout) == [True, False, False, False, False, False]


def test_launcher_refuses_unknown_listener_without_starting_or_stopping(tmp_path):
    launcher = Path('scripts/start-tool-system-demo.ps1').resolve().as_posix()
    result = powershell(tmp_path, """
$ErrorActionPreference='Stop'
function Get-NetTCPConnection { [pscustomobject]@{OwningProcess=987654} }
function Stop-Process { throw 'UNSAFE_STOP' }
function Start-Process { throw 'UNSAFE_START' }
try { & 'LAUNCHER' -Service customer; throw 'Unexpected success' }
catch { if($_.Exception.Message -match 'unowned|ownership mismatch') { 'REFUSED_UNOWNED'; exit 0 }; throw }
""".replace('LAUNCHER', launcher))
    assert result.returncode == 0, result.stderr
    assert result.stdout.strip() == 'REFUSED_UNOWNED'
