# Pure identity predicates reused by the launcher and fixture-driven tests.
. (Join-Path $PSScriptRoot 'context-process-ownership.ps1')

function Get-ToolSystemCommand($Root,$Service,$Plugin) {
    $python=Join-Path $Root '.venv\Scripts\python.exe'
    if($Service -eq 'customer') {
        return '"'+$python+'" -m uvicorn app.tools.demo:create_tool_system_app --factory --host 127.0.0.1 --port 8005 --workers 1 --app-dir "'+$Root+'"'
    }
    $port=if($Service -eq 'logistics') {8101} elseif($Service -eq 'aftersales') {8102} else {throw 'Unknown service'}
    $command='"'+$python+'" -m business_mcp.'+$Service+' --port '+$port
    if($Plugin) {
        if($Service -ne 'logistics' -or $Plugin -cnotmatch '^[A-Za-z_][A-Za-z0-9_.]*$') { throw 'Invalid local MCP plugin' }
        $command+=' --plugin-module '+$Plugin
    }
    return $command
}

function Test-ToolSystemOwner($Process,$Owner,$Root,$Interpreter,$Command,$Processes) {
    if($null -eq $Process -or $null -eq $Owner -or $Owner.root -ine $Root -or $Owner.interpreter -ine $Interpreter -or $Owner.command -cne $Command) { return $false }
    $suffix=$Command.Substring($Command.IndexOf('" ')+2)
    $childCommand='"'+$Interpreter+'"  '+$suffix
    $singleSpaceChild='"'+$Interpreter+'" '+$suffix
    if($Process.ExecutablePath -ine $Interpreter -or $Process.CommandLine -cnotin @($Command,$childCommand,$singleSpaceChild) -or !(Test-ContextIdentity $Process $Owner.listener)) { return $false }
    $launch=@($Processes | Where-Object { Test-ContextIdentity $_ $Owner.launch })
    $launcher=Join-Path $Root '.venv\Scripts\python.exe'
    return $launch.Count -eq 1 -and $launch[0].ExecutablePath -ieq $launcher -and $launch[0].CommandLine -ceq $Command -and (Test-ContextLaunchAncestry $Process $launch[0] $Processes)
}
