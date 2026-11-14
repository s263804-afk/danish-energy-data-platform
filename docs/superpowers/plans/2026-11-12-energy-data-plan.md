# Energy Data Platform Implementation Plan / 软件实施计划

> **For agentic workers:** Use `superpowers:executing-plans` to implement this plan task by task. Where unavailable, apply the same sequential build/test/evidence workflow. Checkbox steps track implementation; personal learning remains separately tracked. No subagent execution is selected by this work order.

**Goal:** Build an independently runnable, tested public-energy-data backend and teach its engineering concepts in English with Chinese support.

**Architecture:** A Python ingestion service writes raw snapshots and PostgreSQL records with audit history. FastAPI exposes validated read endpoints; SQL and rule checks reveal gaps and changes.

**Tech Stack:** Python 3.12.x, PostgreSQL 17.x, FastAPI, SQLAlchemy 2, psycopg 3, Alembic, httpx, pytest, Ruff; Docker where available.

**Spec:** `../specs/2026-11-12-energy-data-design.md`.

## Global Constraints / 全局要求

- Read the specification and workbook teaching contract first. / 先读设计与教学约定。
- Independent repository: `projects/danish-energy-data-platform/`; inspect before creating. / 独立目录，先检查。
- Real PostgreSQL for integration; immutable raw snapshots; UTC-aware internal timestamps. / 真实数据库、原文不可变、内部 UTC。
- Core areas DK1/DK2; natural key `(area, interval_start_utc)`; prices `Decimal`/`numeric(18,6)`.
- Version selection and source contract must be recorded at S1; optional tools do not block the core. / S1 记录版本和来源约定。
- Keep build evidence and learner evidence separate; no external publication without instruction. / 区分实现与本人学习证据。

## Review Focus / 重点审查

1. Repeated local clock hours during DST must not overwrite distinct UTC records — S2/S4. / 夏令时重复时刻不能覆盖。
2. Duplicate keys with conflicting source values must not be arbitrarily chosen — S3. / 同键冲突不能任意取值。
3. Failure after snapshot capture must roll back facts while preserving a failed-run audit — S3/S5. / 失败仍有审计。
4. An unreachable database must produce failed readiness and truthful integration status — S1/S6. / 数据库不可用不能假装通过。
5. Cursor tampering and SQL-like area strings must be rejected rather than interpolated — S6. / 参数与分页游标需验证。

## S1 — Source and environment / 来源与环境

**Files:** Create `docs/environment.md`, `docs/source-contract.md`, `tests/fixtures/source_probe.json`, `pyproject.toml`, lockfile, `.env.example`, `compose.yaml` if supported, `tests/integration/test_database_ready.py`.

**Interfaces:** Produces verified API schema/pagination/timezone contract, installed-version record and `DATABASE_URL` configuration. The source probe in the workbook is reference evidence, not the complete adapter.

- [x] Inspect Python, Git, Docker/PostgreSQL availability and project path; save versions and paths. / 只读检查并记录。
- [x] Fetch a small DK2 interval, verify paging/filter semantics, cadence, UTC handling, attribution and date bounds; save request and response. If blocked, label the fixture and blocked live checks explicitly. / 核对真实接口。
- [x] Configure a user-level Python environment and a real PostgreSQL instance; do not change BIOS, enable OS features or use paid services without a separate decision. / 配置可复现环境。
- [x] Write and run `test_database_ready_executes_select_one`; an invalid URL must fail rather than silently skip. / 数据库探测。
- [x] Write `.env.example` without credentials, ignore `.env` and private logs, lock dependencies and rerun the check. / 配置与版本锁定。
- [x] Save evidence and teach environment, dependency, connection and source contract. Commit only this project if a repository is active. / 留证、讲解、局部提交。 Evidence and teaching complete; initial local commit uses the learner-supplied author identity.

## S2 — Normalisation and schema / 数据规范化与结构

**Files:** Create `src/energy_platform/domain.py`, `normalise.py`, `config.py`, migrations, `tests/unit/test_normalise.py`, `tests/integration/test_constraints.py`.

**Interfaces:** Produces `PriceRecord`, `FetchRequest`, `normalise_record(raw: dict) -> PriceRecord` and the five tables named by the specification.

- [x] First write failing tests for negative `Decimal('-10.250000')`, missing price, non-finite price, unknown area and an explicitly UTC-interpreted source timestamp. / 先写边界测试。
- [x] Test that two autumn records with the same local display hour but different UTC instants remain two rows. / 重复当地小时仍保留两条。
- [x] Implement normalisation and migrations; add the natural primary key and audit/foreign-key rules. / 实现规范化与迁移。
- [x] Run `python -m pytest tests/unit/test_normalise.py tests/integration/test_constraints.py -v` against PostgreSQL. Expected: cases pass with no integration skips. / 真实运行验证。
- [x] Walk through one raw record to one SQL row; learner changes a fixture and predicts acceptance/rejection. Save the short lesson and task evidence, then commit. / 讲解与本人预测练习。

## S3 — Idempotent transactional ingestion / 幂等导入与事务

**Files:** Create `source.py`, `repository.py`, `ingestion.py`, `cli.py`; tests `test_source.py`, `test_ingestion.py`, `test_transactions.py`.

**Interfaces:** Consumes `PriceRecord` and migrations. Produces `PriceSource.fetch(request) -> FetchResult`, `PriceRepository` transactional methods, `ingest(request, source, repository) -> IngestionResult`, and `energy ingest`.

- [x] Write a failing real-database test: import the same 96-record, single-area synthetic ordinary-day fixture twice; assert 96 current rows, zero revisions, two succeeded runs. Fixtures must be labelled synthetic. / 验证单区域同值重跑。
- [x] Add changed-value test: one price changes; assert one current row updated, one revision, unchanged total row count. / 验证修订。
- [x] Add conflicting-source-duplicate test: one response has two values for one natural key; assert no facts from that run are committed and its failure is audited. / 验证同次冲突。
- [x] Add same-values/different-JSON-format test: no revision; add invalid-row test: no partial facts transaction. / 规范化哈希与原子性。
- [x] Implement immutable snapshots, value hashing, PostgreSQL upsert, revision handling, audit status and single-run lock. / 实现数据与审计流程。
- [x] Execute tests and the CLI on a small real interval; save raw response, run ID and counts. Re-run it and demonstrate unchanged current/revision counts. / 实际重跑展示。
- [x] Teach ingest, deduplicate, upsert, roll back, trace back. Learner explains why audit runs increase while facts do not. Commit. / 术语与解释练习。

## S4 — Quality checks and SQL / 质量检查与 SQL

**Files:** Create `quality.py`, `queries.py`, `sql/analysis.sql`, `tests/unit/test_quality.py`, `tests/integration/test_analysis_queries.py`.

**Interfaces:** Produces `check_interval_completeness(records, request, cadence_minutes) -> list[QualityIssue]`, daily summary query and `energy quality`.

- [x] Write tests for 96 ordinary-day intervals, 92 on 2026-03-29 and 100 on 2026-10-25 using Europe/Copenhagen boundaries. / 夏令时精确数量。
- [x] Remove one interior interval: assert one missing issue at that exact UTC instant. Preserve negative prices without a bad-value issue. / 缺口位置与负数合法性。
- [x] Test requested unpublished future intervals are excluded or explicitly reported as not yet expected according to documented configuration. / 已发布边界。
- [x] Implement date-boundary generation, issue persistence and parameterised SQL. / 实现规则与查询。
- [x] Add SQL examples: current-price/run JOIN, CTE for daily quality, `LAG` for time gaps, moving average with explicit window, and area comparison joined on UTC. / JOIN、CTE、窗口函数。
- [x] Check fixture daily values: EUR values `[-10, 10, 20]` have min -10, mean 20/3 and max 20; row/missing counts remain independently checked. / 已知答案校验。
- [x] Run SQL integration tests and teach window frame versus aggregation. Learner writes one variation and explains it. Commit. / 本人查询练习。

## S5 — Operational failure and recovery / 运行故障与恢复

**Files:** Modify `source.py`, `ingestion.py`, `repository.py`; create `tests/unit/test_retry.py`, `tests/integration/test_recovery.py`, `docs/incident-example.md`.

**Interfaces:** Produces bounded retry with injected sleep/clock, structured failure codes and safe interval re-run.

- [x] Write timeout/429/503 tests: at most three total attempts; valid bounded `Retry-After` honoured; persistent failure returns an audited failure. / 重试次数有界。
- [x] Test a forced database error after writes begin: facts/revisions/issues roll back; raw snapshot and failed-run audit remain. / 数据回滚与原文留存。
- [x] Test concurrent import rejection via database lock; the first run remains intact. / 并发拒绝。
- [x] Implement failure handling and structured logs without leaking credentials. / 实现故障处理。
- [x] Run one offline fault demonstration and one safe re-run; document symptom, hypothesis, evidence, root cause, fix and regression check in English with Chinese notes. / 故障复盘。
- [x] Teach narrow down, rule out, retry, recover from, reproduce. Learner diagnoses a separately seeded missing-interval case. Commit. / 排查与动词表达。

## S6 — Query API / 查询接口

**Files:** Create `api.py`, `tests/integration/test_api.py`, `docs/api-examples.md`.

**Interfaces:** Implements `/health`, `/ready`, `/prices`, `/quality`, `/runs/{run_id}`, `/summary/daily` with the exact parameter contract in the design.

- [x] Write failing tests for ascending pagination without repeats, correct range exclusion, missing run 404 and invalid input 422. / 正常与错误请求。
- [x] Test database unavailable → `/ready` 503; unsupported area, SQL-like strings, `start >= end`, limit 1001, naive timestamp and malformed/tampered cursor → 422. / 可用性与边界。
- [x] Implement bound queries, validated models and pagination. / 实现安全参数绑定与分页。
- [x] Run API tests on PostgreSQL, then issue real localhost HTTP requests and record responses. / 测试与实际 HTTP。
- [x] Teach request, response, validate, paginate, expose an endpoint. Learner explains why health and readiness differ. Commit. / 接口英文。

## S7 — Demonstration, CI and handoff / 演示、CI 与交付

**Files:** Create `scripts/demo.ps1`, `.github/workflows/ci.yml`, README, `docs/architecture.md`, `docs/AI_ASSISTANCE.md`, `reports/verification.md`, progress/learning/resume files.

**Interfaces:** Produces an independent core demo and portfolio evidence. An unpushed workflow file is not a verified GitHub CI run.

- [x] Execute `python -m pytest tests/unit tests/integration -v` and `ruff check .`; fix relevant failures. / 全部必要检查。
- [x] Load at least 30 complete real historical days for both areas if available; record exact interval, row count and quality findings. / 真实数据范围。
- [x] Build an offline demo with provenance-labelled snapshots/fixtures; prove setup from a clean checkout or separate fresh environment. / 离线与干净环境复现。
- [x] Configure CI with PostgreSQL and no dependency on the live energy API; report workflow as configured until it has actually run remotely. / CI 证据区分。
- [x] Record demo commands, logs and screenshots; measure only named queries with stated data size and environment. / 可核实演示。
- [x] Prepare English README, three-minute demo script, one incident report and CV bullets conditional on actual verified scope. / 英文求职材料。
- [x] Test learner ownership: run an import, edit a query, diagnose one fault and explain the project in English. Unanswered items remain learning-pending. / 本人验收。
- [x] Self-review the design against the acceptance checklist; record gaps and exact next step. Commit locally; publication requires separate instruction. / 对照验收并交付。

## Teaching link / 教学对应

Use lessons S1–S7 in `LEARNING_EN_ZH.md`. Every technical task ends with its brief bilingual lesson, exercise and evidence entry. Independent technical work can continue while learner answers are pending.
按对应课程教学；个人练习待答时可继续独立技术任务。

Technical steps verified; learner-only actions in these combined steps remain pending in docs/LEARNING_PROGRESS.md and are not certified by these checkboxes.
