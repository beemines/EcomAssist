param([switch]$PrepareOnly, [int]$Port = 3000)
$ErrorActionPreference = 'Stop'
$ch09Root = Split-Path -Parent $PSScriptRoot
$ch09Python = Join-Path $ch09Root '.venv/Scripts/python.exe'
if (-not (Test-Path -LiteralPath $ch09Python)) { throw 'Run uv sync --frozen in this checkout first.' }
Push-Location -LiteralPath $ch09Root
try {
    $ch09Action = if ($PrepareOnly) { 'prepare' } else { 'up' }
    & $ch09Python -m app.observability.local_stack $ch09Action --port $Port
    if ($LASTEXITCODE -ne 0) { throw 'Local Langfuse operation failed; inspect local status.' }
} finally { Pop-Location }
