param([switch]$Acceptance)
$ErrorActionPreference='Stop'
$taskRoot=Split-Path -Parent $PSScriptRoot
. (Join-Path $PSScriptRoot 'observability-process-ownership.ps1')
$cache=Join-Path $taskRoot '.cache/observability'
New-Item -ItemType Directory -Force $cache | Out-Null
$ownerFile=Join-Path $cache 'customer-owner.json'
$listeners=@(Get-NetTCPConnection -LocalPort 8006 -State Listen -ErrorAction SilentlyContinue)
$owner=if(Test-Path -LiteralPath $ownerFile) {Get-Content -LiteralPath $ownerFile -Raw|ConvertFrom-Json} else {$null}
if($listeners.Count -gt 0 -and $null -eq $owner) {throw 'Pre-existing unowned 8006 listener; refused to stop or launch'}
$jobFile=Join-Path $taskRoot 'runtime/ch09-evidence/acceptance-owned-jobs.json'
if(!$Acceptance -and (Test-Path -LiteralPath $jobFile)) {
    $jobs=Get-Content -LiteralPath $jobFile -Raw|ConvertFrom-Json
    if($jobs.closed -ne $true) {throw 'Acceptance has unfinished owned jobs; ordinary mode refused'}
}
$pythonHome=(Get-Content -LiteralPath (Join-Path $taskRoot '.venv/pyvenv.cfg')|Where-Object {$_ -match '^home = '}) -replace '^home = ',''
$interpreter=Join-Path $pythonHome 'python.exe'
$command=Get-ObservabilityCommand $taskRoot
if($null -ne $owner) {
    $process=Get-CimInstance Win32_Process -Filter "ProcessId=$($owner.listener.pid)"
    if($null -ne $process) {
        if(!(Test-ObservabilityOwner $process $owner $taskRoot $interpreter @(Get-CimInstance Win32_Process)) -or $listeners.Count -ne 1 -or $listeners[0].OwningProcess -ne $process.ProcessId) {throw 'PID ownership mismatch; refused to stop'}
        $again=Get-CimInstance Win32_Process -Filter "ProcessId=$($process.ProcessId)"
        if(!(Test-ObservabilityOwner $again $owner $taskRoot $interpreter @(Get-CimInstance Win32_Process))) {throw 'Process identity changed before stop'}
        Stop-Process -Id $again.ProcessId
        Start-Sleep -Milliseconds 500
    } elseif($listeners.Count -gt 0) {throw 'Pre-existing unowned listener'}
}
if(@(Get-NetTCPConnection -LocalPort 8006 -State Listen -ErrorAction SilentlyContinue).Count -gt 0) {throw '8006 still occupied'}
# Existing MCP processes are only inspected, never stopped or adopted here.
foreach($port in @(8101,8102)) {
    $mcp=@(Get-NetTCPConnection -LocalPort $port -State Listen -ErrorAction SilentlyContinue)
    if($mcp.Count -gt 0) {
        $expected=if($port -eq 8101) {'business_mcp.logistics'} else {'business_mcp.aftersales'}
        foreach($item in $mcp) {
            $actual=Get-CimInstance Win32_Process -Filter "ProcessId=$($item.OwningProcess)"
            if($null -eq $actual -or $actual.CommandLine -notmatch ([regex]::Escape($expected)) -or $actual.CommandLine -notmatch "--port $port(\s|$)") {throw "Unrecognized MCP listener on $port; no process changed"}
        }
        Write-Output "Verified existing MCP $port; ownership retained by its launcher"
    } else {Write-Output "MCP $port is absent; start the CH08 run configuration when needed"}
}
$env:PYTHONUTF8='1';$env:PYTHONUNBUFFERED='1';$env:PYTHONPATH=$taskRoot
$env:CH09_SETTINGS_FILE=Join-Path $taskRoot '.env'
Remove-Item -LiteralPath Env:CH09_ACCEPTANCE -ErrorAction SilentlyContinue
if($Acceptance) {$env:CH09_ACCEPTANCE='ch09-local-20261019'}
$arguments=@('-m','uvicorn','app.observability.demo:create_observability_app','--factory','--host','127.0.0.1','--port','8006','--workers','1','--app-dir',('"'+$taskRoot+'"'))
$stamp=Get-Date -Format 'yyyyMMdd-HHmmss-fff'
$launched=Start-Process -FilePath (Join-Path $taskRoot '.venv/Scripts/python.exe') -ArgumentList $arguments -WorkingDirectory $taskRoot -WindowStyle Hidden -PassThru -RedirectStandardOutput (Join-Path $cache "$stamp.out.log") -RedirectStandardError (Join-Path $cache "$stamp.err.log")
$launch=Get-CimInstance Win32_Process -Filter "ProcessId=$($launched.Id)"
if($null -eq $launch) {throw 'Launch disappeared before identity capture'}
for($attempt=0;$attempt -lt 65;$attempt++) {
    Start-Sleep -Milliseconds 700
    $listeners=@(Get-NetTCPConnection -LocalPort 8006 -State Listen -ErrorAction SilentlyContinue)
    if($listeners.Count -eq 0) {continue}
    if($listeners.Count -ne 1) {throw 'Ambiguous listener'}
    $candidate=Get-CimInstance Win32_Process -Filter "ProcessId=$($listeners[0].OwningProcess)"
    $newOwner=[pscustomobject]@{root=$taskRoot;interpreter=$interpreter;command=$command;listener=(New-ContextProcessIdentity $candidate);launch=(New-ContextProcessIdentity $launch)}
    if(!(Test-ObservabilityOwner $candidate $newOwner $taskRoot $interpreter @(Get-CimInstance Win32_Process))) {throw 'Listener does not belong to launched process'}
    try {$health=Invoke-RestMethod 'http://127.0.0.1:8006/health' -TimeoutSec 3} catch {continue}
    if($health.status -ne 'ok') {continue}
    if($Acceptance -and $health.acceptance.run_id -cne 'ch09-local-20261019') {throw 'Unexpected acceptance run'}
    if(!$Acceptance -and $null -ne $health.acceptance) {throw 'Ordinary mode must have no acceptance cap'}
    $newOwner|ConvertTo-Json -Depth 4|Set-Content -LiteralPath $ownerFile -Encoding utf8
    Write-Output "READY customer port=8006 PID=$($candidate.ProcessId) acceptance=$Acceptance"
    exit 0
}
throw '8006 did not start; inspect this checkout .cache/observability/*.err.log'
