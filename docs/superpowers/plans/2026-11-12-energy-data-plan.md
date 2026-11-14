# Energy Data Platform Implementation Plan

> **For agentic workers:** Use `superpowers:executing-plans` to implement this plan task by task. Where unavailable, apply the same sequential build/test/evidence workflow. Checkbox steps track implementation; personal learning remains separately tracked. No subagent execution is selected by this work order.

**Goal:** Build an independently runnable, tested public-energy-data backend and teach its engineering concepts in English using clear English.

**Architecture:** A Python ingestion service writes raw snapshots and PostgreSQL records with audit history. FastAPI exposes validated read endpoints; SQL and rule checks reveal gaps and changes.

**Tech Stack:** Python 3.12.x, PostgreSQL 17.x, FastAPI, SQLAlchemy 2, psycopg 3, Alembic, httpx, pytest, Ruff; Docker where available.

**Spec:** `../specs/2026-11-12-energy-data-design.md`.

## Global Constraints

- Read the specification and workbook teaching contract first.
- Independent repository: `projects/danish-energy-data-platform/`; inspect before creating.
- Real PostgreSQL for integration; immutable raw snapshots; UTC-aware internal timestamps.
- Core areas DK1/DK2; natural key `(area, interval_start_utc)`; prices `Decimal`/`numeric(18,6)`.
- Version selection and source contract must be recorded at S1; optional tools do not block the core.
- Keep build evidence and learner evidence separate; no external publication without instruction.

## Review Focus

1. Repeated local clock hours during DST must not overwrite distinct UTC records — S2/S4.
2. Duplicate keys with conflicting source values must not be arbitrarily chosen — S3.
3. Failure after snapshot capture must roll back facts while preserving a failed-run audit — S3/S5.
4. An unreachable database must produce failed readiness and truthful integration status — S1/S6.
5. Cursor tampering and SQL-like area strings must be rejected rather than interpolated — S6.

## S1 — Source and environment

**Files:** Create `docs/environment.md`, `docs/source-contract.md`, `tests/fixtures/source_probe.json`, `pyproject.toml`, lockfile, `.env.example`, `compose.yaml` if supported, `tests/integration/test_database_ready.py`.

**Interfaces:** Produces verified API schema/pagination/timezone contract, installed-version record and `DATABASE_URL` configuration. The source probe in the workbook is reference evidence, not the complete adapter.

- [x] Inspect Python, Git, Docker/PostgreSQL availability and project path; save versions and paths.
- [x] Fetch a small DK2 interval, verify paging/filter semantics, cadence, UTC handling, attribution and date bounds; save request and response. If blocked, label the fixture and blocked live checks explicitly.
- [x] Configure a user-level Python environment and a real PostgreSQL instance; do not change BIOS, enable OS features or use paid services without a separate decision.
- [x] Write and run `test_database_ready_executes_select_one`; an invalid URL must fail rather than silently skip.
- [x] Write `.env.example` without credentials, ignore `.env` and private logs, lock dependencies and rerun the check.
- [x] Save evidence and teach environment, dependency, connection and source contract. Commit only this project if a repository is active.

## S2 — Normalisation and schema

**Files:** Create `src/energy_platform/domain.py`, `normalise.py`, `config.py`, migrations, `tests/unit/test_normalise.py`, `tests/integration/test_constraints.py`.

**Interfaces:** Produces `PriceRecord`, `FetchRequest`, `normalise_record(raw: dict) -> PriceRecord` and the five tables named by the specification.

- [x] First write failing tests for negative `Decimal('-10.250000')`, missing price, non-finite price, unknown area and an explicitly UTC-interpreted source timestamp.
- [x] Test that two autumn records with the same local display hour but different UTC instants remain two rows.
- [x] Implement normalisation and migrations; add the natural primary key and audit/foreign-key rules.
- [x] Run `python -m pytest tests/unit/test_normalise.py tests/integration/test_constraints.py -v` against PostgreSQL. Expected: cases pass with no integration skips.
- [x] Walk through one raw record to one SQL row; learner changes a fixture and predicts acceptance/rejection. Save the short lesson and task evidence, then commit.

## S3 — Idempotent transactional ingestion

**Files:** Create `source.py`, `repository.py`, `ingestion.py`, `cli.py`; tests `test_source.py`, `test_ingestion.py`, `test_transactions.py`.

**Interfaces:** Consumes `PriceRecord` and migrations. Produces `PriceSource.fetch(request) -> FetchResult`, `PriceRepository` transactional methods, `ingest(request, source, repository) -> IngestionResult`, and `energy ingest`.

- [x] Write a failing real-database test: import the same 96-record, single-area synthetic ordinary-day fixture twice; assert 96 current rows, zero revisions, two succeeded runs. Fixtures must be labelled synthetic.
- [x] Add changed-value test: one price changes; assert one current row updated, one revision, unchanged total row count.
- [x] Add conflicting-source-duplicate test: one response has two values for one natural key; assert no facts from that run are committed and its failure is audited.
- [x] Add same-values/different-JSON-format test: no revision; add invalid-row test: no partial facts transaction.
- [x] Implement immutable snapshots, value hashing, PostgreSQL upsert, revision handling, audit status and single-run lock.
- [x] Execute tests and the CLI on a small real interval; save raw response, run ID and counts. Re-run it and demonstrate unchanged current/revision counts.
- [x] Teach ingest, deduplicate, upsert, roll back, trace back. Learner explains why audit runs increase while facts do not. Commit.

## S4 — Quality checks and SQL

**Files:** Create `quality.py`, `queries.py`, `sql/analysis.sql`, `tests/unit/test_quality.py`, `tests/integration/test_analysis_queries.py`.

**Interfaces:** Produces `check_interval_completeness(records, request, cadence_minutes) -> list[QualityIssue]`, daily summary query and `energy quality`.

- [x] Write tests for 96 ordinary-day intervals, 92 on 2026-03-29 and 100 on 2026-10-25 using Europe/Copenhagen boundaries.
- [x] Remove one interior interval: assert one missing issue at that exact UTC instant. Preserve negative prices without a bad-value issue.
- [x] Test requested unpublished future intervals are excluded or explicitly reported as not yet expected according to documented configuration.
- [x] Implement date-boundary generation, issue persistence and parameterised SQL.
- [x] Add SQL examples: current-price/run JOIN, CTE for daily quality, `LAG` for time gaps, moving average with explicit window, and area comparison joined on UTC.
- [x] Check fixture daily values: EUR values `[-10, 10, 20]` have min -10, mean 20/3 and max 20; row/missing counts remain independently checked.
- [x] Run SQL integration tests and teach window frame versus aggregation. Learner writes one variation and explains it. Commit.

## S5 — Operational failure and recovery

**Files:** Modify `source.py`, `ingestion.py`, `repository.py`; create `tests/unit/test_retry.py`, `tests/integration/test_recovery.py`, `docs/incident-example.md`.

**Interfaces:** Produces bounded retry with injected sleep/clock, structured failure codes and safe interval re-run.

- [x] Write timeout/429/503 tests: at most three total attempts; valid bounded `Retry-After` honoured; persistent failure returns an audited failure.
- [x] Test a forced database error after writes begin: facts/revisions/issues roll back; raw snapshot and failed-run audit remain.
- [x] Test concurrent import rejection via database lock; the first run remains intact.
- [x] Implement failure handling and structured logs without leaking credentials.
- [x] Run one offline fault demonstration and one safe re-run; document symptom, hypothesis, evidence, root cause, fix and regression check in English with Chinese notes.
- [x] Teach narrow down, rule out, retry, recover from, reproduce. Learner diagnoses a separately seeded missing-interval case. Commit.

## S6 — Query API

**Files:** Create `api.py`, `tests/integration/test_api.py`, `docs/api-examples.md`.

**Interfaces:** Implements `/health`, `/ready`, `/prices`, `/quality`, `/runs/{run_id}`, `/summary/daily` with the exact parameter contract in the design.

- [x] Write failing tests for ascending pagination without repeats, correct range exclusion, missing run 404 and invalid input 422.
- [x] Test database unavailable → `/ready` 503; unsupported area, SQL-like strings, `start >= end`, limit 1001, naive timestamp and malformed/tampered cursor → 422.
- [x] Implement bound queries, validated models and pagination.
- [x] Run API tests on PostgreSQL, then issue real localhost HTTP requests and record responses.
- [x] Teach request, response, validate, paginate, expose an endpoint. Learner explains why health and readiness differ. Commit.

## S7 — Demonstration, CI and handoff

**Files:** Create `scripts/demo.ps1`, `.github/workflows/ci.yml`, README, `docs/architecture.md`, `docs/AI_ASSISTANCE.md`, `reports/verification.md`, progress/learning/resume files.

**Interfaces:** Produces an independent core demo and portfolio evidence. An unpushed workflow file is not a verified GitHub CI run.

- [x] Execute `python -m pytest tests/unit tests/integration -v` and `ruff check .`; fix relevant failures.
- [x] Load at least 30 complete real historical days for both areas if available; record exact interval, row count and quality findings.
- [x] Build an offline demo with provenance-labelled snapshots/fixtures; prove setup from a clean checkout or separate fresh environment.
- [x] Configure CI with PostgreSQL and no dependency on the live energy API; report workflow as configured until it has actually run remotely.
- [x] Record demo commands, logs and screenshots; measure only named queries with stated data size and environment.
- [x] Prepare English README, three-minute demo script, one incident report and CV bullets conditional on actual verified scope.
- [x] Test learner ownership: run an import, edit a query, diagnose one fault and explain the project in English. Unanswered items remain learning-pending.
- [x] Self-review the design against the acceptance checklist; record gaps and exact next step. Commit locally; publication requires separate instruction.

## Teaching link

Use lessons S1–S7 in `LEARNING_EN_ZH.md`. Every technical task ends with its brief English lesson, exercise and evidence entry. Independent technical work can continue while learner answers are pending.

Technical steps verified; learner-only actions in these combined steps remain pending in docs/LEARNING_PROGRESS.md and are not certified by these checkboxes.
