# 仅启动/重启本工作树拥有的8003；旧PID文件不能授权停止服务。
$ErrorActionPreference='Stop'
$taskRoot=Split-Path -Parent $PSScriptRoot
. (Join-Path $PSScriptRoot 'intent-routing-process-ownership.ps1')
$cache=Join-Path $taskRoot '.cache/intent-routing'
New-Item -ItemType Directory -Force $cache | Out-Null
$ownerFile=Join-Path $cache 'server8003-owner.json'
$listener=@(Get-NetTCPConnection -LocalAddress 127.0.0.1 -LocalPort 8003 -State Listen -ErrorAction SilentlyContinue)
$owner=if(Test-Path -LiteralPath $ownerFile) { Get-Content -LiteralPath $ownerFile -Raw | ConvertFrom-Json } else { $null }
# 在任何启动/停止前拒绝没有创建身份元数据的占用者。
if($listener.Count -gt 0 -and $null -eq $owner) { throw 'Pre-existing unowned 8003 listener; refused to launch or stop' }
$pythonHome=(Get-Content -LiteralPath (Join-Path $taskRoot '.venv/pyvenv.cfg') | Where-Object { $_ -match '^home = ' }) -replace '^home = ',''
$interpreter=Join-Path $pythonHome 'python.exe'
if($null -ne $owner) {
    $ownedProcess=Get-CimInstance Win32_Process -Filter "ProcessId=$($owner.listener.pid)"
    if($null -ne $ownedProcess) {
        if(!(Test-IntentOwnedProcess $ownedProcess $owner $taskRoot $interpreter)) { throw 'PID ownership mismatch; refused to stop' }
        $processes=@(Get-CimInstance Win32_Process)
        $originalLaunch=$processes | Where-Object { Test-IntentIdentity $_ $owner.launch }
        if($null -eq $originalLaunch -or !(Test-IntentLaunchAncestry $ownedProcess $originalLaunch $processes)) { throw 'Launch ancestry mismatch; refused to stop' }
        if($listener.Count -ne 1 -or $listener[0].OwningProcess -ne $ownedProcess.ProcessId) { throw 'Listener ownership mismatch; refused to stop' }
        # 停止前再取创建身份，避免检查与操作之间PID被重用。
        $rechecked=Get-CimInstance Win32_Process -Filter "ProcessId=$($ownedProcess.ProcessId)"
        if(!(Test-IntentOwnedProcess $rechecked $owner $taskRoot $interpreter)) { throw 'Process identity changed; refused to stop' }
        Stop-Process -Id $rechecked.ProcessId
        Start-Sleep -Seconds 2
    } elseif($listener.Count -gt 0) { throw 'Pre-existing unowned 8003 listener; refused to launch' }
}
if(@(Get-NetTCPConnection -LocalAddress 127.0.0.1 -LocalPort 8003 -State Listen -ErrorAction SilentlyContinue).Count -gt 0) { throw '8003 is still occupied; refused to launch' }
$env:PYTHONUTF8='1'
$env:PYTHONPATH=$taskRoot
$env:WORKFLOW_CHECKPOINT_PATH=Join-Path $taskRoot 'runtime/workflow/intent-routing-8003.sqlite'
$stamp=Get-Date -Format 'yyyyMMdd-HHmmss-fff'
$process=Start-Process -FilePath (Join-Path $taskRoot '.venv/Scripts/python.exe') -ArgumentList @('-m','uvicorn','app.main:create_app','--factory','--host','127.0.0.1','--port','8003','--workers','1','--app-dir',('"'+$taskRoot+'"')) -WorkingDirectory $taskRoot -WindowStyle Hidden -PassThru -RedirectStandardOutput (Join-Path $cache "server8003-stdout-$stamp.log") -RedirectStandardError (Join-Path $cache "server8003-stderr-$stamp.log")
$launch=Get-CimInstance Win32_Process -Filter "ProcessId=$($process.Id)"
if($null -eq $launch) { throw 'Launched process disappeared before ownership could be established' }
for($attempt=0; $attempt -lt 30; $attempt++) {
    Start-Sleep -Seconds 1
    $listeners=@(Get-NetTCPConnection -LocalAddress 127.0.0.1 -LocalPort 8003 -State Listen -ErrorAction SilentlyContinue)
    if($listeners.Count -eq 0) { continue }
    if($listeners.Count -ne 1) { throw 'Ambiguous listener; refused adoption' }
    $candidate=Get-CimInstance Win32_Process -Filter "ProcessId=$($listeners[0].OwningProcess)"
    if(!(Test-IntentCommand $candidate $taskRoot $interpreter) -or !(Test-IntentLaunchAncestry $candidate $launch @(Get-CimInstance Win32_Process))) { throw 'Listener is not the exact launched worktree process; refused adoption' }
    try { $response=Invoke-WebRequest http://127.0.0.1:8003/health -UseBasicParsing } catch { continue }
    if($response.StatusCode -eq 200) {
        $identity=New-IntentProcessIdentity $candidate
        $rechecked=Get-CimInstance Win32_Process -Filter "ProcessId=$($candidate.ProcessId)"
        if(!(Test-IntentIdentity $rechecked $identity)) { throw 'Listener identity changed during health check' }
        @{root=$taskRoot;interpreter=$interpreter;listener=$identity;launch=(New-IntentProcessIdentity $launch);stamp=$stamp} | ConvertTo-Json -Depth 4 | Set-Content -LiteralPath $ownerFile
        $candidate.ProcessId | Set-Content -LiteralPath (Join-Path $cache 'server8003.pid')
        Write-Output "READY8003 PID=$($candidate.ProcessId)"
        exit 0
    }
}
throw '8003 did not become healthy; inspect saved stderr'
