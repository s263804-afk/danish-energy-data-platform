# Incident: PostgreSQL was running but setup did not finish

Date: 2026-11-12. Actual development incident, not a deliberately injected fault.

## Environment and reproduction

Windows 11 Home 10.0.26200; PostgreSQL 17.12 EDB Windows binaries; PowerShell task runner
capturing native command output. The initial wrapper executed `pg_ctl start` directly
while its caller redirected the setup output to a file.

## Expected and observed

Expected: initialise a private cluster, start PostgreSQL, create the application role and
database, write private `.env`, then return control.

Observed: PostgreSQL logged a loopback listener on 55432 and readiness. The setup log
printed `server started`, but setup did not reach role creation or `.env` writing.
Process inspection showed PostgreSQL processes and no psql/createdb process. Interrupting
the stalled execution also ended that initial server tree. Its cluster was preserved
under the project's ignored `.local/` directory, rather than deleting data blindly.

## Diagnosis and fix

The evidence is consistent with captured native-process pipes remaining open across
the Windows daemon lifecycle. The precise inherited OS handle was not instrumented,
so that low-level explanation remains a hypothesis, not a proven OS defect.

The wrapper now launches pg_ctl with hidden `Start-Process`, separate stdout/stderr files
and process-only `WaitForExit(35000)`. It does not use `Start-Process -Wait`, which can
wait for the descendant server tree. PostgreSQL retains its own private log.

A second observed failure exposed an independent, confirmed wrapper error: after
successful Start-Process, `$LASTEXITCODE` still held the earlier pg_ctl status result 3.
The parent interpreted this stale status as startup failure. The successful start script
now explicitly exits with 0. The admin password is retained locally before initialisation
so an interrupted setup does not lose its generated maintenance credential.

## Regression evidence

- `reports/evidence/s1-database-stop.log`
- `reports/evidence/s1-database-restart.log`
- `reports/evidence/s1-database-restart-green.log`: real SELECT 1 test passed after restart.
- `reports/evidence/s1-fresh-db-setup.log`: a new cluster on 55433 completed full setup,
  including role/database creation and `.env` writing.
- `reports/evidence/s1-fresh-suite.log`: six tests passed, no skips; extra cluster then stopped.

No Windows service or global configuration was needed. The workaround is verified on
this environment, not on every Windows/PowerShell version.

中文：先区分“数据库已启动”和“配置脚本已完成”。日志和进程证明卡在配置流程，
不能据此声称数据库本身启动失败。底层句柄原因仍为假设；陈旧退出码误判则已确认。
