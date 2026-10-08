# Register from a Windows host set to China Standard Time:
# schtasks /Create /TN "ECS Knowledge Daily" /SC DAILY /ST 02:00 /TR 'powershell.exe -NoProfile -ExecutionPolicy Bypass -File "D:\shixi\ecommerce-customer-service\scripts\run-knowledge-daily.ps1"' /F
# This file does not register a task. Deploy the reviewed branch to the fixed
# checkout first. A concurrent job is rejected by MySQL GET_LOCK and exits 1.
$ErrorActionPreference = 'Stop'
$projectRoot = 'D:\shixi\ecommerce-customer-service'
$env:UV_CACHE_DIR = 'D:\shixi\ecommerce-customer-service\.cache\uv'
try {
    Push-Location -LiteralPath $projectRoot
    try {
        $logDirectory = Join-Path $projectRoot '.cache'
        New-Item -ItemType Directory -Path $logDirectory -Force | Out-Null
        $logPath = Join-Path $logDirectory 'knowledge-daily.log'
        # Windows PowerShell 5.1 treats native stderr as ErrorRecord. Continue
        # during capture so stderr cannot stop the pipeline before exit capture.
        $ErrorActionPreference = 'Continue'
        try {
            & uv --directory $projectRoot run python -m app.knowledge.cli run-daily 2>&1 |
                Tee-Object -FilePath $logPath -Append -ErrorAction Stop
            $jobExitCode = $LASTEXITCODE
        }
        finally {
            $ErrorActionPreference = 'Stop'
        }
    }
    finally {
        Pop-Location
    }
    exit $jobExitCode
}
catch {
    [Console]::Error.WriteLine('Knowledge daily launcher failed; check project path and uv availability')
    exit 1
}
