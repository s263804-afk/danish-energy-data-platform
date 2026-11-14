param(
    [string]$PgBin = "$env:LOCALAPPDATA\PortfolioTools\postgresql-17.12\pgsql\bin",
    [int]$Port = 55432
)
$ErrorActionPreference = 'Stop'
$taskRoot = Split-Path -Parent $PSScriptRoot
$taskPrivate = Join-Path $taskRoot '.local'
$taskData = Join-Path $taskPrivate 'postgres-data'
$taskEnvFile = Join-Path $taskRoot '.env'
if (-not (Test-Path -LiteralPath (Join-Path $PgBin 'initdb.exe'))) {
    throw "Install the documented PostgreSQL 17.12 binaries first: $PgBin"
}
if ((Test-Path -LiteralPath $taskEnvFile) -or (Test-Path -LiteralPath $taskData)) {
    throw 'Existing configuration preserved. Use start-local-db.ps1; do not reinitialise it.'
}
if (Get-NetTCPConnection -State Listen -LocalPort $Port -ErrorAction SilentlyContinue) {
    throw "Port $Port is already in use. Choose a free local port."
}
New-Item -ItemType Directory -Path $taskPrivate -Force | Out-Null
# Random hex secrets need no URL escaping and never appear in command output.
$taskAdminPassword = [Convert]::ToHexString([System.Security.Cryptography.RandomNumberGenerator]::GetBytes(24))
$taskAppPassword = [Convert]::ToHexString([System.Security.Cryptography.RandomNumberGenerator]::GetBytes(24))
$taskAdminFile = Join-Path $taskPrivate 'admin-password.txt'
if (Test-Path -LiteralPath $taskAdminFile) { throw 'An existing admin credential is preserved.' }
[System.IO.File]::WriteAllText($taskAdminFile, $taskAdminPassword)
$taskPasswordFile = Join-Path $taskPrivate 'initdb-password.txt'
[System.IO.File]::WriteAllText($taskPasswordFile, $taskAdminPassword + "`n")
try {
    & (Join-Path $PgBin 'initdb.exe') -D $taskData -U portfolio_admin --pwfile=$taskPasswordFile --auth=scram-sha-256 --encoding=UTF8 --locale=C
    if ($LASTEXITCODE -ne 0) { throw 'initdb failed; inspect the output before retrying.' }
} finally {
    Remove-Item -LiteralPath $taskPasswordFile -Force
}
@"

# Project-only development settings; no Windows service or external listener.
listen_addresses = '127.0.0.1'
port = $Port
timezone = 'UTC'
log_timezone = 'UTC'
"@ | Add-Content -LiteralPath (Join-Path $taskData 'postgresql.conf') -Encoding UTF8
& "$PSScriptRoot\start-local-db.ps1" -PgBin $PgBin
if ($LASTEXITCODE -ne 0) { throw 'Could not start the project PostgreSQL instance.' }
$taskPriorPassword = $env:PGPASSWORD
try {
    $env:PGPASSWORD = $taskAdminPassword
    # Feed SQL through stdin rather than putting the role password on a process command line.
    "CREATE ROLE energy_app WITH LOGIN PASSWORD '$taskAppPassword';" |
        & (Join-Path $PgBin 'psql.exe') -h 127.0.0.1 -p $Port -U portfolio_admin -d postgres -v ON_ERROR_STOP=1
    if ($LASTEXITCODE -ne 0) { throw 'Creating the application role failed.' }
    & (Join-Path $PgBin 'createdb.exe') -h 127.0.0.1 -p $Port -U portfolio_admin -O energy_app energy
    if ($LASTEXITCODE -ne 0) { throw 'Creating the application database failed.' }
} finally {
    $env:PGPASSWORD = $taskPriorPassword
}
$taskConfig = "DATABASE_URL=postgresql+psycopg://energy_app:${taskAppPassword}@127.0.0.1:${Port}/energy`n"
$taskConfig += "SOURCE_BASE_URL=https://api.energidataservice.dk/dataset/DayAheadPrices`n"
[System.IO.File]::WriteAllText($taskEnvFile, $taskConfig)
# The admin secret remains local for maintenance; application tests use a non-superuser role.
Write-Output "Created project-only PostgreSQL on 127.0.0.1:$Port; private .env written."
