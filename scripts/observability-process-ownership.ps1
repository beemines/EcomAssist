. (Join-Path $PSScriptRoot 'tool-system-process-ownership.ps1')
function Get-ObservabilityCommand($Root) {
    return '"'+(Join-Path $Root '.venv\Scripts\python.exe')+'" -m uvicorn app.observability.demo:create_observability_app --factory --host 127.0.0.1 --port 8006 --workers 1 --app-dir "'+$Root+'"'
}
function Test-ObservabilityOwner($Process,$Owner,$Root,$Interpreter,$Processes) {
    return Test-ToolSystemOwner $Process $Owner $Root $Interpreter (Get-ObservabilityCommand $Root) $Processes
}
