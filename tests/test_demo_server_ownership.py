"""离线执行PowerShell启动边界；所有进程事实注入，不接触真实监听器。"""
import json
from pathlib import Path
import shutil
import subprocess


def powershell(tmp_path, body):
    """单独脚本执行实际函数，不读取或停止本机服务。"""
    script = tmp_path / 'probe.ps1'
    script.write_text(body, encoding='utf-8')
    return subprocess.run(['pwsh', '-NoProfile', '-File', str(script)], capture_output=True, text=True, encoding='utf-8')


def test_unowned_listener_rejected_before_launch(tmp_path):
    """旧脚本会先启动再认领任意health；新脚本必须在进程边界前拒绝。"""
    root = Path(__file__).parents[1]
    scripts = tmp_path / 'scripts'
    scripts.mkdir()
    for source in root.joinpath('scripts').glob('*intent-routing*.ps1'):
        shutil.copy(source, scripts / source.name)
    (tmp_path / '.venv').mkdir()
    (tmp_path / '.venv/pyvenv.cfg').write_text('home = C:\\locked-python\n')
    result = powershell(tmp_path, f"""
$ErrorActionPreference='Stop'
function Get-NetTCPConnection {{ [pscustomobject]@{{OwningProcess=999}} }}
function Start-Process {{ throw 'FORBIDDEN_LAUNCH' }}
function Stop-Process {{ throw 'FORBIDDEN_STOP' }}
try {{ & '{scripts / 'start-intent-routing-demo.ps1'}' }} catch {{ Write-Output $_.Exception.Message; exit 3 }}
""")
    assert result.returncode == 3 and 'unowned' in result.stdout.lower()
    assert 'FORBIDDEN' not in result.stdout


def test_identity_and_ancestry_reject_reused_or_foreign_process(tmp_path):
    """实际权限判断要求PID创建身份、精确工作树/解释器、启动祖先全匹配。"""
    helper = Path(__file__).parents[1] / 'scripts/intent-routing-process-ownership.ps1'
    assert helper.exists(), 'process ownership verification missing'
    result = powershell(tmp_path, f"""
. '{helper}'
$cmd='"D:\\feature\\.venv\\Scripts\\python.exe" -m uvicorn app.main:create_app --factory --host 127.0.0.1 --port 8003 --workers 1 --app-dir "D:\\feature"'
$process=[pscustomobject]@{{ProcessId=10;ParentProcessId=9;CreationDate=[datetime]'2026-10-15T10:00:01Z';ExecutablePath='C:\\locked-python\\python.exe';CommandLine=$cmd}}
$launch=[pscustomobject]@{{ProcessId=9;ParentProcessId=8;CreationDate=[datetime]'2026-10-15T10:00:00Z'}}
$identity=New-IntentProcessIdentity $process
$owner=[pscustomobject]@{{root='D:\\feature';interpreter='C:\\locked-python\\python.exe';listener=$identity;launch=(New-IntentProcessIdentity $launch)}}
$owner=$owner | ConvertTo-Json -Depth 4 | ConvertFrom-Json
$results=@()
$results+=Test-IntentOwnedProcess $process $owner 'D:\\feature' 'C:\\locked-python\\python.exe'
$results+=Test-IntentLaunchAncestry $process $launch @($launch,$process)
$process.CreationDate=[datetime]'2026-10-15T10:05:00Z'
$results+=Test-IntentOwnedProcess $process $owner 'D:\\feature' 'C:\\locked-python\\python.exe'
$process.CreationDate=[datetime]'2026-10-15T10:00:01Z'
$process.CommandLine=$cmd.Replace('D:\\feature','D:\\other')
$results+=Test-IntentOwnedProcess $process $owner 'D:\\feature' 'C:\\locked-python\\python.exe'
$process.CommandLine=$cmd
$process.ExecutablePath='C:\\other\\python.exe'
$results+=Test-IntentOwnedProcess $process $owner 'D:\\feature' 'C:\\locked-python\\python.exe'
$process.ExecutablePath='C:\\locked-python\\python.exe'
$process.ParentProcessId=77
$results+=Test-IntentLaunchAncestry $process $launch @($launch,$process)
ConvertTo-Json -InputObject $results -Compress
""")
    assert result.returncode == 0, result.stderr
    assert json.loads(result.stdout) == [True, True, False, False, False, False]
