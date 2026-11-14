param(
    [string]$PgBin = "$env:LOCALAPPDATA\PortfolioTools\postgresql-17.12\pgsql\bin"
)
$ErrorActionPreference = 'Stop'
$taskData = Join-Path (Split-Path -Parent $PSScriptRoot) '.local\postgres-data'
$taskPgCtl = Join-Path $PgBin 'pg_ctl.exe'
if (-not (Test-Path -LiteralPath (Join-Path $taskData 'PG_VERSION'))) {
    throw 'No project database cluster exists.'
}
& $taskPgCtl status -D $taskData *> $null
if ($LASTEXITCODE -ne 0) {
    Write-Output 'The project PostgreSQL process is already stopped.'
    exit 0
}
& $taskPgCtl stop -D $taskData -m fast -w -t 30
if ($LASTEXITCODE -ne 0) { throw 'Project PostgreSQL stop failed.' }
