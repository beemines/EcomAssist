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
        & uv --directory $projectRoot run python -m app.knowledge.cli run-daily
        $jobExitCode = $LASTEXITCODE
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
