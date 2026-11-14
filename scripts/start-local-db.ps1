param(
    [string]$PgBin = "$env:LOCALAPPDATA\PortfolioTools\postgresql-17.12\pgsql\bin"
)
$ErrorActionPreference = 'Stop'
$taskProjectRoot = Split-Path -Parent $PSScriptRoot
$taskData = Join-Path $taskProjectRoot '.local\postgres-data'
$taskLog = Join-Path $taskProjectRoot '.local\postgres.log'
$taskPgCtl = Join-Path $PgBin 'pg_ctl.exe'
if (-not (Test-Path -LiteralPath (Join-Path $taskData 'PG_VERSION'))) {
    throw 'No project database cluster. Run scripts/setup-local-db.ps1 first.'
}
& $taskPgCtl status -D $taskData *> $null
if ($LASTEXITCODE -eq 0) {
    Write-Output 'The project PostgreSQL process is already running.'
    exit 0
}
# A daemon launched through a captured native pipeline can retain its pipe handles
# on Windows. Start pg_ctl with separate files and wait for pg_ctl, not its server tree.
$taskStdout = Join-Path $taskProjectRoot '.local\pgctl-start.stdout.log'
$taskStderr = Join-Path $taskProjectRoot '.local\pgctl-start.stderr.log'
$taskArguments = @('start', '-D', "`"$taskData`"", '-l', "`"$taskLog`"", '-w', '-t', '30')
$taskStartProcess = Start-Process -FilePath $taskPgCtl -ArgumentList $taskArguments -WindowStyle Hidden -PassThru -RedirectStandardOutput $taskStdout -RedirectStandardError $taskStderr
if (-not $taskStartProcess.WaitForExit(35000)) { throw "pg_ctl did not finish; inspect $taskLog" }
Get-Content -LiteralPath $taskStdout
if ($taskStartProcess.ExitCode -ne 0) {
    Get-Content -LiteralPath $taskStderr
    throw "PostgreSQL start failed. Inspect $taskLog"
}
exit 0
