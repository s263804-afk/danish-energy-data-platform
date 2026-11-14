# Danish Energy Data Reliability Platform — Design

Status: proposed implementation specification, 12 November 2026. The topic and independent-project approach have been selected by the learner. Detailed defaults below are the author's implementation proposal and may be adjusted transparently when compatibility evidence requires it.

## Purpose and users

An energy analyst needs reliable DK1/DK2 day-ahead prices for internal analysis. A developer needs a query API and an operator needs to know whether a load succeeded, failed or introduced a data-quality issue.

This is a local portfolio system using public data, not a trading product or retail electricity-bill calculator.

## Approaches

- Selected: independent public-energy-data project, giving backend/data-engineering evidence without depending on the embedded project.
- Alternative: device-test-results backend shared with the embedded project, offering a coherent test-engineering story but narrower data-domain exposure.
- Within the selected route: one service and a relational database; streaming infrastructure is deferred until a demonstrated need exists.

## Required stack and scope

- Python 3.12.x, PostgreSQL 17.x, FastAPI, SQLAlchemy 2, psycopg 3, Alembic, httpx, pytest, Ruff. Resolve and lock compatible package versions at S1.
- PostgreSQL is mandatory for integration evidence. SQLite or mocked database tests cannot substitute for it.
- Docker Compose is the preferred local packaging if Docker is available. A documented native PostgreSQL path is acceptable.
- Bind the demo API to localhost. A public server, paid cloud subscription, user accounts and a complex frontend are not required.
- Keep raw snapshots, curated records, revisions and ingestion audit history.
- Provide one documented CLI entry point `energy` and one HTTP application.

## Flow

```text
Energinet API → immutable raw snapshot → validation → PostgreSQL transaction
                                                  ↓
                              quality checks + SQL analysis → FastAPI
```

Run one ingestion at a time in v1. A second concurrent run must be rejected cleanly using a database lock rather than racing the first.

## Source contract

Observed API: `https://api.energidataservice.dk/dataset/DayAheadPrices`.
Observed fields: `TimeUTC`, `TimeDK`, `PriceArea`, `DayAheadPriceEUR`, `DayAheadPriceDKK`.
The workbook includes a two-record live schema probe. S1 must verify filtering, paging, ordering, cadence and source timezone semantics before loading a larger interval.

- Core areas: DK1 and DK2.
- Internal intervals: half-open `[start_utc, end_utc)`.
- Internal timestamps: timezone-aware UTC; store as `timestamptz`. Derive local display with `Europe/Copenhagen`.
- If an official field contains a naive UTC string, attach UTC only after confirming the field contract; never interpret it as Windows local time.
- Default expected cadence for checked modern records: 15 minutes, subject to S1 metadata verification. Configuration must record effective cadence and any supported date bounds.
- Source-provided `TimeDK` is for comparison/display, never the unique key.
- Prices use `Decimal` and SQL `numeric(18,6)`; negative prices are valid. Parse JSON numbers without a binary-float round trip, and normalise finite prices to six decimal places with `ROUND_HALF_EVEN` before hashing or persistence.
- No API token is assumed; respect current public usage rules and document attribution.

## Data model

Create migrations for:

| Table | Important fields | Rule |
| --- | --- | --- |
| `ingestion_runs` | UUID, area/range, start/end times, status, counts, error code, snapshot ID | Audit status survives a failed facts transaction |
| `raw_snapshots` | UUID, request parameters, fetch time, SHA-256, path, HTTP status | Immutable files; no secrets in URLs |
| `prices` | area, interval_start_utc, price_eur, price_dkk, value_hash, latest_run_id | Primary key `(area, interval_start_utc)` |
| `price_versions` | area/time, old/new values, run ID, observed_at | Record actual value changes, not every unchanged import |
| `quality_issues` | run ID, area/time or range, rule_code, severity, details | Findings reference data and rule |

Canonical hashes use normalised timestamp, area and Decimal values. JSON whitespace or field order must not create a revision.

Idempotency: loading the same content twice leaves the same curated rows and versions, with two audit runs. A corrected price updates one current row and appends one revision.

Do not silently choose between conflicting values for the same natural key within one response. Fail that facts load, save the raw response and report `CONFLICTING_SOURCE_DUPLICATE`.

## Validation and recovery

- Missing required fields, unknown areas and non-finite prices produce explicit schema/value errors.
- Identical source duplicates can be deduplicated and counted. Missing intervals become quality issues within the requested complete historical range.
- A local civil day is defined by its local midnight boundaries converted to UTC. For 15-minute data: 92 intervals on 2026-03-29, 100 on 2026-10-25, 96 on an ordinary day.
- Missing-data checks apply to requested intervals that should already exist; do not flag tomorrow's unpublished prices just because they are not present. Keep release-time rules configurable and labelled.
- Network timeouts, HTTP 429 and HTTP 5xx have bounded retry: at most three total attempts. Honour a valid `Retry-After` within the configured maximum wait; otherwise report a recoverable failure. Inject the sleeper in tests.
- Validation precedes facts writes. Current rows, revisions and quality findings for one run commit atomically; a failure rolls them back. Record the failed run separately.
- Resume via rerunning the same interval safely.

## Public interfaces

Python domain contracts:
```text
PriceRecord(area: str, interval_start_utc: datetime, price_eur: Decimal, price_dkk: Decimal)
FetchRequest(area: str, start_utc: datetime, end_utc: datetime)
fetch_prices(request: FetchRequest) -> FetchResult
normalise_record(raw: dict) -> PriceRecord
ingest(request: FetchRequest, source: PriceSource, repository: PriceRepository) -> IngestionResult
check_interval_completeness(records, request, cadence_minutes: int) -> list[QualityIssue]
```

CLI examples are target interfaces, not commands already implemented:
```text
energy ingest --area DK2 --start 2026-10-01T00:00:00Z --end 2026-10-02T00:00:00Z
energy quality --area DK2 --start 2026-10-01T00:00:00Z --end 2026-10-02T00:00:00Z
energy demo --offline
```

HTTP:
- `GET /health`: process health; `GET /ready`: database/migration readiness.
- `GET /prices?area=DK2&start=...&end=...&limit=100&cursor=...`: ascending UTC order, maximum limit 1000, opaque cursor, no duplicates across pages.
- `GET /quality?area=DK2&start=...&end=...`: documented rule results.
- `GET /runs/{run_id}`: ingestion status and counts.
- `GET /summary/daily?area=DK2&start_date=...&end_date=...`: local-day count, min/mean/max and missing count. Date range is also half-open.

Use bound SQL parameters. Reject unsupported area, naive query timestamps, `start >= end`, limit outside 1–1000, malformed cursor and excessive v1 range over 366 days with HTTP 422. Return 503 when readiness fails; do not expose raw database exceptions to callers.

## File responsibilities

```text
pyproject.toml, lockfile, compose.yaml, .env.example
src/energy_platform/
  config.py                 environment and verified dataset bounds
  domain.py                 typed records and result types
  source.py                 source adapter, paging and bounded retry
  normalise.py              schema, Decimal and UTC normalisation
  repository.py             transactional persistence and locks
  ingestion.py              orchestration and run audit
  quality.py                interval and value rules
  queries.py                parameterised reporting SQL
  api.py                    HTTP validation and routing
  cli.py                    documented entry point
migrations/                 Alembic revisions
sql/analysis.sql            readable joins, CTEs and window queries
tests/unit/, tests/integration/, tests/fixtures/
docs/, reports/, scripts/demo.ps1, .github/workflows/ci.yml
```

Keep SQL visible for learning; do not hide every query behind ORM calls. Tests must cover PostgreSQL behaviour on PostgreSQL.

## Acceptance and evidence

1. Load at least 30 complete historical days for DK1/DK2 if source access permits; save exact range and counts, not a fabricated row target.
2. Prove repeat-import idempotency, one changed-price revision and source-conflict rejection.
3. Demonstrate DST days, negative prices, partial failure, timeout and database rollback.
4. Query API and SQL return checked fixture results.
5. Offline demo uses licensed/correctly attributed captured data or clearly labelled synthetic fixtures; never call synthetic records real.
6. `pytest` unit and integration suites actually run; CI uses a PostgreSQL service. Save failures and final results.
7. Measure query runtime only with row count, environment and command recorded. No unsupported scale claims.
8. README, architecture, schema, English bug report, decisions, AI disclosure, evidence and learning progress are complete.

## Deferred extensions

Azure deployment, Kafka/Spark, an LLM assistant, authentication and a complex dashboard are optional after the core is verified. Add one only when its workplace value can be explained and its cost is approved.

## Ownership and language

The learner must personally run an import, write one join and one window query, reproduce a missing-interval bug, and explain UTC/idempotency/rollback in English. Technical completion alone does not prove these learning outcomes.
