# 仅启动/重启本工作树拥有的8004；旧PID文件不能授权停止服务。
param(
    [Parameter(Mandatory)][ValidateSet('default','demo')][string]$Profile,
    [string]$RunId,
    [Nullable[int]]$MaxGlmCalls,
    [Nullable[int]]$MaxEmbeddingCalls,
    [Nullable[int]]$MaxRerankCalls
)
$ErrorActionPreference='Stop'
$capKeys=@('RunId','MaxGlmCalls','MaxEmbeddingCalls','MaxRerankCalls')
$provided=@($capKeys | Where-Object { $PSBoundParameters.ContainsKey($_) })
if($provided.Count -ne 0 -and $provided.Count -ne 4) { throw 'RunId and all three caps must appear together' }
if($provided.Count -eq 4 -and ($RunId -cnotmatch '^[A-Za-z0-9][A-Za-z0-9_-]{0,79}$' -or $MaxGlmCalls -lt 0 -or $MaxEmbeddingCalls -lt 0 -or $MaxRerankCalls -lt 0)) { throw 'Invalid run id or nonnegative caps' }
$taskRoot=Split-Path -Parent $PSScriptRoot
. (Join-Path $PSScriptRoot 'context-process-ownership.ps1')
$cache=Join-Path $taskRoot '.cache/context'
New-Item -ItemType Directory -Force $cache | Out-Null
$ownerFile=Join-Path $cache 'server8004-owner.json'
$listener=@(Get-NetTCPConnection -LocalPort 8004 -State Listen -ErrorAction SilentlyContinue)
$owner=if(Test-Path -LiteralPath $ownerFile) { Get-Content -LiteralPath $ownerFile -Raw | ConvertFrom-Json } else { $null }
# 在任何启动/停止前拒绝没有创建身份元数据的占用者。
if($listener.Count -gt 0 -and $null -eq $owner) { throw 'Pre-existing unowned 8004 listener; refused to launch or stop' }
$pythonHome=(Get-Content -LiteralPath (Join-Path $taskRoot '.venv/pyvenv.cfg') | Where-Object { $_ -match '^home = ' }) -replace '^home = ',''
$interpreter=Join-Path $pythonHome 'python.exe'
if($null -ne $owner) {
    $ownedProcess=Get-CimInstance Win32_Process -Filter "ProcessId=$($owner.listener.pid)"
    if($null -ne $ownedProcess) {
        if(!(Test-ContextOwnedProcess $ownedProcess $owner $taskRoot $interpreter)) { throw 'PID ownership mismatch; refused to stop' }
        $processes=@(Get-CimInstance Win32_Process)
        $originalLaunch=$processes | Where-Object { Test-ContextIdentity $_ $owner.launch }
        if($null -eq $originalLaunch -or !(Test-ContextLaunchAncestry $ownedProcess $originalLaunch $processes)) { throw 'Launch ancestry mismatch; refused to stop' }
        if($listener.Count -ne 1 -or $listener[0].OwningProcess -ne $ownedProcess.ProcessId) { throw 'Listener ownership mismatch; refused to stop' }
        # 停止前再取创建身份，避免检查与操作之间PID被重用。
        $rechecked=Get-CimInstance Win32_Process -Filter "ProcessId=$($ownedProcess.ProcessId)"
        if(!(Test-ContextOwnedProcess $rechecked $owner $taskRoot $interpreter)) { throw 'Process identity changed; refused to stop' }
        Stop-Process -Id $rechecked.ProcessId
        Start-Sleep -Seconds 2
    } elseif($listener.Count -gt 0) { throw 'Pre-existing unowned 8004 listener; refused to launch' }
}
if(@(Get-NetTCPConnection -LocalPort 8004 -State Listen -ErrorAction SilentlyContinue).Count -gt 0) { throw '8004 is still occupied; refused to launch' }
$env:PYTHONUTF8='1'
$env:PYTHONUNBUFFERED='1'
$env:PYTHONPATH=$taskRoot
$env:CONTEXT_DEMO_PROFILE=$Profile
$env:WORKFLOW_CHECKPOINT_PATH=Join-Path $taskRoot "runtime/workflow/context-$Profile-8004.sqlite"
foreach($key in @('CONTEXT_RUN_ID','CONTEXT_MAX_GLM_CALLS','CONTEXT_MAX_EMBEDDING_CALLS','CONTEXT_MAX_RERANK_CALLS')) { Remove-Item -LiteralPath "Env:$key" -ErrorAction SilentlyContinue }
if($provided.Count -eq 4) {
    $env:CONTEXT_RUN_ID=$RunId
    $env:CONTEXT_MAX_GLM_CALLS=[string]$MaxGlmCalls
    $env:CONTEXT_MAX_EMBEDDING_CALLS=[string]$MaxEmbeddingCalls
    $env:CONTEXT_MAX_RERANK_CALLS=[string]$MaxRerankCalls
}
$stamp=Get-Date -Format 'yyyyMMdd-HHmmss-fff'
$process=Start-Process -FilePath (Join-Path $taskRoot '.venv/Scripts/python.exe') -ArgumentList @('-m','uvicorn','app.context.acceptance:create_demo_app','--factory','--host','127.0.0.1','--port','8004','--workers','1','--app-dir',('"'+$taskRoot+'"')) -WorkingDirectory $taskRoot -WindowStyle Hidden -PassThru -RedirectStandardOutput (Join-Path $cache "server8004-stdout-$stamp.log") -RedirectStandardError (Join-Path $cache "server8004-stderr-$stamp.log")
$launch=Get-CimInstance Win32_Process -Filter "ProcessId=$($process.Id)"
if($null -eq $launch) { throw 'Launched process disappeared before ownership could be established' }
for($attempt=0; $attempt -lt 30; $attempt++) {
    Start-Sleep -Seconds 1
    $listeners=@(Get-NetTCPConnection -LocalPort 8004 -State Listen -ErrorAction SilentlyContinue)
    if($listeners.Count -eq 0) { continue }
    if($listeners.Count -ne 1) { throw 'Ambiguous listener; refused adoption' }
    $candidate=Get-CimInstance Win32_Process -Filter "ProcessId=$($listeners[0].OwningProcess)"
    if(!(Test-ContextCommand $candidate $taskRoot $interpreter) -or !(Test-ContextLaunchAncestry $candidate $launch @(Get-CimInstance Win32_Process))) { throw 'Listener is not the exact launched worktree process; refused adoption' }
    try { $response=Invoke-WebRequest http://127.0.0.1:8004/health -UseBasicParsing } catch { continue }
    if($response.StatusCode -eq 200) {
        $health=$response.Content | ConvertFrom-Json
        if($health.context_profile -cne $Profile) { throw 'Unexpected server profile; refused adoption' }
        if($provided.Count -eq 4 -and ($health.acceptance.run_id -cne $RunId -or $health.acceptance.limits.glm -ne $MaxGlmCalls -or $health.acceptance.limits.embedding -ne $MaxEmbeddingCalls -or $health.acceptance.limits.rerank -ne $MaxRerankCalls)) { throw 'Unexpected server run or limits; refused adoption' }
        $identity=New-ContextProcessIdentity $candidate
        $rechecked=Get-CimInstance Win32_Process -Filter "ProcessId=$($candidate.ProcessId)"
        if(!(Test-ContextIdentity $rechecked $identity)) { throw 'Listener identity changed during health check' }
        @{root=$taskRoot;interpreter=$interpreter;listener=$identity;launch=(New-ContextProcessIdentity $launch);stamp=$stamp} | ConvertTo-Json -Depth 4 | Set-Content -LiteralPath $ownerFile
        $candidate.ProcessId | Set-Content -LiteralPath (Join-Path $cache 'server8004.pid')
        Write-Output "READY8004 PID=$($candidate.ProcessId)"
        exit 0
    }
}
throw '8004 did not become healthy; inspect saved stderr'
