# S1 verification / S1 技术验证

Date: 2026-11-12. Scope: source/environment only. Agent-run evidence, not personal mastery.
Commands below run from this repository in PowerShell. Private URLs/passwords are not printed.

| Check | Command / action | Observed result | Evidence |
|---|---|---|---|
| Runtime versions | Explicit Python/Git/PostgreSQL versions; installed package metadata | Python 3.12.7, Git 2.55.0, PostgreSQL 17.12; exact package record | `evidence/environment-versions.json`, `../docs/environment.md` |
| Initial packaging failure | `python -m pip install -e '.[dev]' pip-tools` | Failed: declared src directory absent; created package directory and installation succeeded | `evidence/s1-install-initial-failure.log`; corrected private install log |
| Probe RED → GREEN | `python -m pytest tests/unit/test_source_probe.py -v` | Three initial behavior tests failed before implementation, then passed | `evidence/s1-probe-red.log`, `evidence/s1-probe-green.log` |
| Missing database configuration | Real readiness test before `.env` existed | Failed with missing DATABASE_URL; did not skip | `evidence/s1-database-missing-red.log` (environment representation omitted; original private) |
| Invalid URL | Set DATABASE_URL to an unreachable loopback port; run readiness test | Exit 1, one failed test, connection timeout; no skip | `evidence/s1-database-invalid-url.log` |
| Actual database connection | `python -m pytest tests/integration/test_database_ready.py -v --tb=short` | SELECT 1 returned 1; PostgreSQL major 17 | `evidence/database-ready.json`, `evidence/s1-database-restart-green.log` |
| Role/listener/tables | SQL server/role settings and public table count | Non-superuser energy_app; loopback port 55432; UTC; zero business tables | `evidence/database-ready.json` |
| Lifecycle | `scripts/stop-local-db.ps1`, `scripts/start-local-db.ps1`, then SQL test | Stop/start returned and readiness test passed | `evidence/s1-database-stop.log`, `evidence/s1-database-restart.log` |
| HTTP-error evidence | Test before/after saving error bytes/status | RED before fix; final GREEN; one controlled request, no retry | `evidence/s1-http-failure-red.log`, final suite |
| Existing output | Test before/after preflight refusal | RED before fix; final GREEN; original bytes preserved with no request | `evidence/s1-existing-output-red.log`, final suite |
| Full current S1 suite | `& .\.venv\Scripts\python.exe -m pytest -v --tb=short` | 6 passed, 0 skipped | `evidence/s1-suite-final.log` |
| Lint | `& .\.venv\Scripts\python.exe -m ruff check .` | All checks passed after correcting one long line | `evidence/s1-lint-final.log` |
| Dependency consistency | `& .\.venv\Scripts\python.exe -m pip check` | No broken requirements | `evidence/s1-pip-check-final.log` |
| Fresh project environment | New venv, `pip install --require-hashes -r requirements.lock`, install package, new cluster on 55433, same pytest command | 6 passed, 0 skipped; full setup succeeded; extra cluster stopped | `evidence/s1-fresh-db-setup.log`, `evidence/s1-fresh-suite.log`, `evidence/s1-fresh-db-stop.log` |
| Fresh dependencies | Fresh interpreter `-m pip check` | No broken requirements | `evidence/s1-fresh-pip-check.log` |
| Live schema/filter/pages/time | Source probe commands below, then compare saved JSON/UTC intervals/hashes | 14 comparisons passed; 8 distinct DK2 intervals | `evidence/source-s1/checks.json` and adjacent raw/metadata files |

## Live commands and observations

Each request was separate. After an initial rapid batch produced 429, later requests
were deliberately spaced; this is not a measured throughput claim.

```powershell
& .\.venv\Scripts\python.exe scripts/source_probe.py --area DK2 --limit 2 --offset 0 --output reports/evidence/source-s1/winter-page-1.json
& .\.venv\Scripts\python.exe scripts/source_probe.py --area DK2 --limit 2 --offset 2 --output reports/evidence/source-s1/winter-page-2.json
& .\.venv\Scripts\python.exe scripts/source_probe.py --area DK2 --limit 4 --offset 0 --output reports/evidence/source-s1/winter-full.json
& .\.venv\Scripts\python.exe scripts/source_probe.py --area DK2 --start-local 2026-07-01T00:00 --end-local 2026-07-01T01:00 --limit 4 --output reports/evidence/source-s1/summer-full.json
& .\.venv\Scripts\python.exe scripts/source_probe.py --area DK2 --limit 2 --offset 4 --output reports/evidence/source-s1/winter-exhausted.json
```

These filenames now exist and must not be reused. For a new probe choose a new path.
Initial rapid attempts for page 2, full, exhausted, summer and two coverage-boundary
probes received HTTP 429. That batch did not abort on its first failed request. The
failed HTTP bodies/Retry-After headers were not preserved at that point; no exact
rate-limit period is claimed. The corrected inspection tool now saves those if received.
Coverage bounds are taken from captured official metadata, not successful boundary probes.

Saved pages compare as 2 + 2 = 4 rows, followed by an empty page. Winter UTC times are
2026-10-31 23:00–23:45, summer UTC times 2026-06-30 22:00–22:45; both at 15-minute spacing.
Official semantics and the observed local/UTC relationship agree. `total` is page-sized
in these samples. Request URLs, timestamps and SHA-256 hashes are in adjacent metadata.

## Reproduction limits and remaining work

- Fresh project reproduction reused this machine, base Python and downloaded database
  binaries; it was not a fresh Windows installation. Exact dependency hashes were checked.
- Unit fixtures/constructed responses are not counted as live API integration.
- S1 only: no migrated business tables, ingestion, revision handling, DST quality engine,
  query API, 30-day dataset, production retry/concurrency handling or remote CI yet.
- Source sampling is not exhaustive completeness verification. No public upload occurred.
- S1 learner code change, personal run and English explanation remain PENDING_LEARNER.
- Author follow-up: configured learner-supplied Git identity locally, reran the six tests
  and Ruff successfully, and recorded S1 in the initial local commit. Follow-up test log:
  `evidence/s1-author-followup-tests.log`. No remote or public publication was configured.

Incident explanation: `../docs/incident-s1-startup.md`. Next technical task: S2.
