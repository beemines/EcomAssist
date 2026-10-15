# 所有函数只核验传入的进程事实；不启动、停止或枚举真实进程。
function New-IntentProcessIdentity($Process) {
    # PID与UTC创建时间共同防止PID重用。
    [pscustomobject]@{pid=[int]$Process.ProcessId;created=$Process.CreationDate.ToUniversalTime().ToString('o')}
}
function Test-IntentIdentity($Process,$Identity) {
    # 创建身份必须完整且完全相同。
    if($null -eq $Process -or $null -eq $Identity -or $null -eq $Identity.created) { return $false }
    try { $created=([datetime]$Identity.created).ToUniversalTime().ToString('o') } catch { return $false }
    return [int]$Process.ProcessId -eq [int]$Identity.pid -and (New-IntentProcessIdentity $Process).created -ceq $created
}
function Test-IntentCommand($Process,$Root,$Interpreter) {
    # 绝对app-dir明确工作树，精确解释器与固定端口/worker防止认领其他uvicorn。
    if($null -eq $Process -or $Process.ExecutablePath -ine $Interpreter) { return $false }
    $launcher=Join-Path $Root '.venv\Scripts\python.exe'
    $expected='"'+$launcher+'" -m uvicorn app.main:create_app --factory --host 127.0.0.1 --port 8003 --workers 1 --app-dir "'+$Root+'"'
    return $Process.CommandLine -ieq $expected
}
function Test-IntentOwnedProcess($Process,$Owner,$Root,$Interpreter) {
    # 重启前同时核对保存的工作树、解释器与监听进程创建身份。
    return $null -ne $Owner -and $Owner.root -ieq $Root -and $Owner.interpreter -ieq $Interpreter -and (Test-IntentIdentity $Process $Owner.listener) -and (Test-IntentCommand $Process $Root $Interpreter)
}
function Test-IntentLaunchAncestry($Process,$Launch,$Processes) {
    # 有界父链仅接受本次启动身份；旧父PID及创建时间倒置不能成为祖先。
    $current=$Process
    for($depth=0; $depth -lt 8 -and $null -ne $current; $depth++) {
        if(Test-IntentIdentity $current (New-IntentProcessIdentity $Launch)) { return $true }
        $parent=@($Processes | Where-Object ProcessId -eq $current.ParentProcessId)
        if($parent.Count -ne 1 -or $parent[0].CreationDate -gt $current.CreationDate) { return $false }
        $current=$parent[0]
    }
    return $false
}
