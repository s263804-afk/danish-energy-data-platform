# Publication check precondition

A final test run was attempted after the computer/browser session had changed.
The local PostgreSQL process was not listening. The readiness test failed and
29 integration fixtures errored (32 tests passed;96.72s). No skip/fallback was used.
The full first log was overwritten during rerun; this note records that limitation.
The project-owned database was started using scripts/start-local-db.ps1, then the
same suite passed62/62 in7.75s and Ruff passed. No source-code fix was required.
The saved publication-final-tests.log is the successful run, not the initial failure.
