# Danish Energy Data Reliability Platform

Independent personal portfolio project by **Weitong Liu**, developed with **AI assistance**.

A local Python/PostgreSQL project for traceable DK1/DK2 day-ahead electricity analysis.
The backend implements immutable raw captures, Decimal/UTC validation, PostgreSQL migrations,
transactional imports, revision history, completeness checks and a validated FastAPI read API.
An offline demo uses 5,960 real DK1/DK2 records covering 31 Copenhagen local days.

中文：已实现数据导入、修订、质量检查、SQL 分析与查询接口；本地真实数据库和 HTTP 已验证。

## Run the project

Use PowerShell in this repository. Initial installation and binary provenance are in
[environment.md](docs/environment.md). If the project environment is already configured:

```powershell
& .\scripts\start-local-db.ps1
& .\.venv\Scripts\python.exe -m pytest -v --tb=short
& .\.venv\Scripts\python.exe -m ruff check .
Get-Content tests\fixtures\source_probe.json
& .\.venv\Scripts\python.exe -m energy_platform.cli init-db
& .\.venv\Scripts\python.exe -m energy_platform.cli demo --offline
& .\.venv\Scripts\python.exe -m energy_platform.cli serve --port 8000
```

The current suite has 62 passing tests with real PostgreSQL 17.12 and no integration skips.
It covers normalisation, idempotency, revisions, conflicting duplicates, DST, SQL answers,
rollback, single-run locking, bounded retry, API validation and signed pagination.
See the completion verification report for fresh-environment reproduction and exact CI status.

Optional live inspection, choosing a **new** output path:

```powershell
& .\.venv\Scripts\python.exe scripts/source_probe.py --area DK2 --limit 4 --output .local/my-new-probe.json
```

Read [source-contract.md](docs/source-contract.md) first. Respect source rate limits; use saved
fixtures for routine tests. Requests use Danish local boundaries; returned TimeUTC means UTC.
The probe saves bytes and metadata, and does not load price rows into PostgreSQL.

## Evidence and learning

- [Verification results](reports/verification.md)
- [Technical progress](docs/PROGRESS.md) and [personal learning](docs/LEARNING_PROGRESS.md)
- [S1 bilingual lesson, code walkthrough and exercise](docs/lessons/S1_EN_ZH.md)
- [Execution ledger](docs/EXECUTION_LEDGER.md), [decisions](docs/DECISIONS.md)
- [AI assistance and ownership](docs/AI_ASSISTANCE.md), [resume instructions](docs/RESUME_STATE.md)

Architecture: Energinet API/captured source → immutable snapshot → validation →
PostgreSQL transaction → quality checks and SQL analysis → FastAPI.
Current prices, revisions and quality findings commit atomically; failed-run audits survive
facts rollback. Import the same interval again to recover safely.

## Verified data and API

The captured interval is [2026-10-01,2026-11-01) in Europe/Copenhagen: 2,980 records per area,
including 100 quarter-hours on the autumn DST day. Both areas have zero missing intervals
in this capture. Reimports do not duplicate current records or create false revisions.
This verifies the stated capture, not guaranteed future upstream completeness.

Local endpoints: /health, /ready, /prices, /quality, /runs/{run_id}, /summary/daily.
Prices are returned as decimal strings. UTC ranges are half-open; daily reports use
Europe/Copenhagen. Cursor signatures are process-scoped, so restart invalidates old cursors.
Missing-data checks use elapsed intervals only; unpublished future intervals are excluded.

- [Full verification and limitations](reports/completion-verification.md)
- [Architecture and transactions](docs/architecture.md)
- [API examples](docs/api-examples.md)
- [English demo script](docs/demo-script-en-zh.md)
- [CV project entry](docs/CV_PROJECT_ENTRY_EN_ZH.md)

GitHub Actions is configured with a real PostgreSQL service and no live Energinet dependency.
Remote execution status must be taken from the actual workflow runs, not the YAML file alone.

## Attribution and limits

Small source captures are from Energinet (www.energidataservice.dk), under
[CC BY 4.0 data terms](https://www.energidataservice.dk/terms-and-conditions).
Captured JSON is unmodified; generated metadata and verification summaries are project artifacts.
The data represents wholesale prices per MWh, not a retail-bill prediction.
Technical verification and personal learning evidence are recorded separately in docs/.

The initial published implementation passed [GitHub PostgreSQL verification](https://github.com/s263804-afk/danish-energy-data-platform/actions/runs/43603601599).
