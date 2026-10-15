# 启动或重启本工作树专属8003；只停止PID文件确认且命令匹配的自有进程，保留每次日志和SQLite。
$ErrorActionPreference='Stop'
$taskRoot=Split-Path -Parent $PSScriptRoot
New-Item -ItemType Directory -Force (Join-Path $taskRoot '.cache/intent-routing') | Out-Null
$pidFile=Join-Path $taskRoot '.cache/intent-routing/server8003.pid'
if(Test-Path $pidFile) {
  $ownedPid=[int](Get-Content $pidFile)
  $ownedProcess=Get-CimInstance Win32_Process -Filter "ProcessId=$ownedPid"
  if($ownedProcess -and $ownedProcess.CommandLine.Contains('uvicorn app.main:create_app') -and $ownedProcess.CommandLine.Contains('--port 8003')) {
    Stop-Process -Id $ownedPid
    Start-Sleep -Seconds 2
  } elseif($ownedProcess) { throw 'PID ownership mismatch; refused to stop' }
}
$env:PYTHONUTF8='1'
$env:PYTHONPATH=$taskRoot
$env:WORKFLOW_CHECKPOINT_PATH=Join-Path $taskRoot 'runtime/workflow/intent-routing-8003.sqlite'
$stamp=Get-Date -Format 'yyyyMMdd-HHmmss-fff'
$process=Start-Process -FilePath (Join-Path $taskRoot '.venv/Scripts/python.exe') -ArgumentList @('-m','uvicorn','app.main:create_app','--factory','--host','127.0.0.1','--port','8003','--workers','1') -WorkingDirectory $taskRoot -WindowStyle Hidden -PassThru -RedirectStandardOutput (Join-Path $taskRoot (".cache/intent-routing/server8003-stdout-$stamp.log")) -RedirectStandardError (Join-Path $taskRoot (".cache/intent-routing/server8003-stderr-$stamp.log"))
$process.Id | Set-Content $pidFile
for($attempt=0; $attempt -lt 30; $attempt++) {
  Start-Sleep -Seconds 1
  try { $r=Invoke-WebRequest http://127.0.0.1:8003/health -UseBasicParsing; if($r.StatusCode -eq 200) { $listener=Get-NetTCPConnection -LocalAddress 127.0.0.1 -LocalPort 8003 -State Listen; $listener.OwningProcess | Set-Content $pidFile; Write-Output "READY8003 PID=$($listener.OwningProcess)"; exit 0 } } catch { }
}
throw '8003 did not become healthy; inspect saved stderr'

