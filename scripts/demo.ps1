$ErrorActionPreference = 'Stop'
$taskRoot = Split-Path -Parent $PSScriptRoot
Push-Location $taskRoot
try {
    & "$PSScriptRoot\start-local-db.ps1"
    if ($LASTEXITCODE -ne 0) { throw 'Database not started.' }
    & '.\.venv\Scripts\python.exe' -m energy_platform.cli demo --offline
    if ($LASTEXITCODE -ne 0) { throw 'Demo failed.' }
} finally {
    Pop-Location
}
