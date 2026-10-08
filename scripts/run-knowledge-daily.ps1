# 在使用北京时间（China Standard Time）的 Windows 主机上执行下面的命令注册任务：
# schtasks /Create /TN "ECS Knowledge Daily" /SC DAILY /ST 02:00 /TR 'powershell.exe -NoProfile -ExecutionPolicy Bypass -File "D:\shixi\ecommerce-customer-service\scripts\run-knowledge-daily.ps1"' /F
# 本脚本负责运行每日任务；上面的注册命令需要单独执行。
# 先把已核验代码部署到固定目录；并发运行时 MySQL GET_LOCK 会拒绝第二个任务。
$ErrorActionPreference = 'Stop'
$projectRoot = 'D:\shixi\ecommerce-customer-service'
$env:UV_CACHE_DIR = 'D:\shixi\ecommerce-customer-service\.cache\uv'
try {
    # 固定工作目录确保 .env、知识文件和 Python 模块都按项目目录解析。
    Push-Location -LiteralPath $projectRoot
    try {
        $logDirectory = Join-Path $projectRoot '.cache'
        New-Item -ItemType Directory -Path $logDirectory -Force | Out-Null
        $logPath = Join-Path $logDirectory 'knowledge-daily.log'
        # PowerShell 5.1 会把原生命令的 stderr 包装为 ErrorRecord。
        # 捕获期间允许继续，保证 uv 退出码能被保存，而不是提前中断管道。
        $ErrorActionPreference = 'Continue'
        try {
            & uv --directory $projectRoot run python -m app.knowledge.cli run-daily 2>&1 |
                Tee-Object -FilePath $logPath -Append -ErrorAction Stop
            $jobExitCode = $LASTEXITCODE
        }
        finally {
            # 日志捕获结束后恢复严格错误处理，避免后续错误被静默忽略。
            $ErrorActionPreference = 'Stop'
        }
    }
    finally {
        # 任务失败时也恢复调用方的原工作目录。
        Pop-Location
    }
    exit $jobExitCode
}
catch {
    [Console]::Error.WriteLine('Knowledge daily launcher failed; check project path and uv availability')
    exit 1
}
