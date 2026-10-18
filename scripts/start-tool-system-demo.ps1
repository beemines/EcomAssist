param(
    [ValidateSet('all','customer','logistics','aftersales')][string]$Service='all',
    [string]$LogisticsPlugin='',
    [switch]$Acceptance
)
$ErrorActionPreference='Stop'
$taskRoot=Split-Path -Parent $PSScriptRoot
. (Join-Path $PSScriptRoot 'tool-system-process-ownership.ps1')
$cache=Join-Path $taskRoot '.cache/tool-system'
New-Item -ItemType Directory -Force $cache | Out-Null
$services=if($Service -eq 'all') {@('logistics','aftersales','customer')} else {@($Service)}
foreach($name in $services) {
    $port=@{customer=8005;logistics=8101;aftersales=8102}[$name]
    $ownerFile=Join-Path $cache "$name-owner.json"
    $listeners=@(Get-NetTCPConnection -LocalPort $port -State Listen -ErrorAction SilentlyContinue)
    $owner=if(Test-Path -LiteralPath $ownerFile) {Get-Content -LiteralPath $ownerFile -Raw | ConvertFrom-Json} else {$null}
    if($listeners.Count -gt 0 -and $null -eq $owner) {throw "Pre-existing unowned $port listener; refused to launch or stop"}
    $pythonHome=(Get-Content -LiteralPath (Join-Path $taskRoot '.venv/pyvenv.cfg') | Where-Object {$_ -match '^home = '}) -replace '^home = ',''
    $interpreter=Join-Path $pythonHome 'python.exe'
    $plugin=if($name -eq 'logistics') {$LogisticsPlugin} else {''}
    $command=Get-ToolSystemCommand $taskRoot $name $plugin
    if($null -ne $owner) {
        $process=Get-CimInstance Win32_Process -Filter "ProcessId=$($owner.listener.pid)"
        if($null -ne $process) {
            # Validate the previously launched command as well as the new command.
            # A local plugin switch is an intentional restart, not permission to adopt a PID.
            $oldCommand=Get-ToolSystemCommand $taskRoot $name $(if($owner.plugin) {$owner.plugin} else {''})
            if(!(Test-ToolSystemOwner $process $owner $taskRoot $interpreter $oldCommand @(Get-CimInstance Win32_Process)) -or
                $listeners.Count -ne 1 -or $listeners[0].OwningProcess -ne $process.ProcessId) {throw "PID ownership mismatch on $port; refused to stop"}
            $again=Get-CimInstance Win32_Process -Filter "ProcessId=$($process.ProcessId)"
            if(!(Test-ToolSystemOwner $again $owner $taskRoot $interpreter $oldCommand @(Get-CimInstance Win32_Process))) {throw 'Process identity changed before stop'}
            Stop-Process -Id $again.ProcessId
            Start-Sleep -Milliseconds 500
        } elseif($listeners.Count -gt 0) {throw "Pre-existing unowned $port listener"}
    }
    if(@(Get-NetTCPConnection -LocalPort $port -State Listen -ErrorAction SilentlyContinue).Count -gt 0) {throw "$port still occupied"}
    $env:PYTHONUTF8='1'
    $env:PYTHONUNBUFFERED='1'
    $env:PYTHONPATH=$taskRoot
    $env:WORKFLOW_CHECKPOINT_PATH=Join-Path $taskRoot 'runtime/workflow/tool-system-8005.sqlite'
    Remove-Item -LiteralPath Env:TOOL_SYSTEM_ACCEPTANCE -ErrorAction SilentlyContinue
    if($Acceptance -and $name -eq 'customer') {$env:TOOL_SYSTEM_ACCEPTANCE='ch08-page-20261018'}
    $arguments=if($name -eq 'customer') {@('-m','uvicorn','app.tools.demo:create_tool_system_app','--factory','--host','127.0.0.1','--port','8005','--workers','1','--app-dir',('"'+$taskRoot+'"'))}
        else {@('-m',('business_mcp.'+$name),'--port',[string]$port)}
    if($plugin) {$arguments+=@('--plugin-module',$plugin)}
    $stamp=Get-Date -Format 'yyyyMMdd-HHmmss-fff'
    $launched=Start-Process -FilePath (Join-Path $taskRoot '.venv/Scripts/python.exe') -ArgumentList $arguments -WorkingDirectory $taskRoot -WindowStyle Hidden -PassThru -RedirectStandardOutput (Join-Path $cache "$name-$stamp.out.log") -RedirectStandardError (Join-Path $cache "$name-$stamp.err.log")
    $launch=Get-CimInstance Win32_Process -Filter "ProcessId=$($launched.Id)"
    if($null -eq $launch) {throw 'New launch disappeared before identity capture'}
    $ready=$false
    for($attempt=0;$attempt -lt 45;$attempt++) {
        Start-Sleep -Milliseconds 700
        $listeners=@(Get-NetTCPConnection -LocalPort $port -State Listen -ErrorAction SilentlyContinue)
        if($listeners.Count -eq 0) {continue}
        if($listeners.Count -ne 1) {throw 'Ambiguous listener'}
        $candidate=Get-CimInstance Win32_Process -Filter "ProcessId=$($listeners[0].OwningProcess)"
        $newOwner=[pscustomobject]@{root=$taskRoot;interpreter=$interpreter;command=$command;plugin=$plugin;listener=(New-ContextProcessIdentity $candidate);launch=(New-ContextProcessIdentity $launch)}
        if(!(Test-ToolSystemOwner $candidate $newOwner $taskRoot $interpreter $command @(Get-CimInstance Win32_Process))) {throw 'Listener does not belong to launched child'}
        if($name -eq 'customer') {
            try {$health=Invoke-RestMethod "http://127.0.0.1:$port/health" -TimeoutSec 3} catch {continue}
            if($health.status -ne 'ok') {continue}
            if($Acceptance -and $health.acceptance.run_id -cne 'ch08-page-20261018') {throw 'Unexpected acceptance run'}
            if(!$Acceptance -and $null -ne $health.acceptance) {throw 'Ordinary demo must not retain a call cap'}
        }
        $newOwner | ConvertTo-Json -Depth 4 | Set-Content -LiteralPath $ownerFile
        Write-Output "READY $name port=$port PID=$($candidate.ProcessId)"
        $ready=$true
        break
    }
    if(!$ready) {throw "$name did not start; inspect saved stderr"}
}
