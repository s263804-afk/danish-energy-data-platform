# Danish Energy Data Reliability Platform — Design / 软件设计

Status: proposed implementation specification, 12 November 2026. The topic and independent-project approach have been selected by the learner. Detailed defaults below are the author's implementation proposal and may be adjusted transparently when compatibility evidence requires it.
选题及独立项目路线已确定；以下细节是工作单建议，兼容性需要调整时记录原因，不伪装成用户既有决定。

## Purpose and users / 用途与使用者

An energy analyst needs reliable DK1/DK2 day-ahead prices for internal analysis. A developer needs a query API and an operator needs to know whether a load succeeded, failed or introduced a data-quality issue.
面向能源分析人员、内部应用开发者和数据流程维护者：数据可查询，导入可追溯，故障可定位。

This is a local portfolio system using public data, not a trading product or retail electricity-bill calculator.
这是使用公开数据的本地作品，不作为交易系统或居民电费计算器。

## Approaches / 已比较路线

- Selected: independent public-energy-data project, giving backend/data-engineering evidence without depending on the embedded project. / 已选：独立能源数据项目，覆盖更广岗位。
- Alternative: device-test-results backend shared with the embedded project, offering a coherent test-engineering story but narrower data-domain exposure. / 备选：统一设备测试后台，工程叙事集中但数据场景较窄。
- Within the selected route: one service and a relational database; streaming infrastructure is deferred until a demonstrated need exists. / 实现采用单服务与关系数据库；流式平台留到确有需求时。

## Required stack and scope / 技术与范围

- Python 3.12.x, PostgreSQL 17.x, FastAPI, SQLAlchemy 2, psycopg 3, Alembic, httpx, pytest, Ruff. Resolve and lock compatible package versions at S1. / S1 锁定可用版本。
- PostgreSQL is mandatory for integration evidence. SQLite or mocked database tests cannot substitute for it. / 集成证据必须使用 PostgreSQL。
- Docker Compose is the preferred local packaging if Docker is available. A documented native PostgreSQL path is acceptable. / Docker 可用则采用；否则允许有说明的本地 PostgreSQL。
- Bind the demo API to localhost. A public server, paid cloud subscription, user accounts and a complex frontend are not required. / 本地接口即可，不要求公网、付费云和复杂前端。
- Keep raw snapshots, curated records, revisions and ingestion audit history. / 保留原始快照、规范数据、版本与导入记录。
- Provide one documented CLI entry point `energy` and one HTTP application. / 统一命令行入口与一个接口服务。

## Flow / 流程

```text
Energinet API → immutable raw snapshot → validation → PostgreSQL transaction
                                                  ↓
                              quality checks + SQL analysis → FastAPI
```

Run one ingestion at a time in v1. A second concurrent run must be rejected cleanly using a database lock rather than racing the first.
第一版单任务导入；并发任务通过数据库锁明确拒绝。

## Source contract / 来源约定

Observed API: `https://api.energidataservice.dk/dataset/DayAheadPrices`.
Observed fields: `TimeUTC`, `TimeDK`, `PriceArea`, `DayAheadPriceEUR`, `DayAheadPriceDKK`.
The workbook includes a two-record live schema probe. S1 must verify filtering, paging, ordering, cadence and source timezone semantics before loading a larger interval.
工作单已保存两条真实响应；S1 还要验证筛选、分页、顺序、时间粒度与时区含义。

- Core areas: DK1 and DK2. / 核心区域。
- Internal intervals: half-open `[start_utc, end_utc)`. / 开始包含，结束不包含。
- Internal timestamps: timezone-aware UTC; store as `timestamptz`. Derive local display with `Europe/Copenhagen`. / UTC 入库，哥本哈根时区显示。
- If an official field contains a naive UTC string, attach UTC only after confirming the field contract; never interpret it as Windows local time. / 不能按本机时区猜测。
- Default expected cadence for checked modern records: 15 minutes, subject to S1 metadata verification. Configuration must record effective cadence and any supported date bounds. / 先按待核实的现代 15 分钟数据设计，并记录支持日期范围。
- Source-provided `TimeDK` is for comparison/display, never the unique key. / 本地时间不能作为唯一键。
- Prices use `Decimal` and SQL `numeric(18,6)`; negative prices are valid. Parse JSON numbers without a binary-float round trip, and normalise finite prices to six decimal places with `ROUND_HALF_EVEN` before hashing or persistence. / 使用定点数，负电价合法；避免先转二进制浮点；哈希和存储前统一六位小数与舍入规则。
- No API token is assumed; respect current public usage rules and document attribution. / 不假设需要令牌；核实使用规则与归属。

## Data model / 数据模型

Create migrations for:

| Table / 表 | Important fields / 关键字段 | Rule / 规则 |
|---|---|---|
| `ingestion_runs` | UUID, area/range, start/end times, status, counts, error code, snapshot ID | Audit status survives a failed facts transaction / 数据事务失败后仍保留审计结果 |
| `raw_snapshots` | UUID, request parameters, fetch time, SHA-256, path, HTTP status | Immutable files; no secrets in URLs / 原始文件不可覆盖 |
| `prices` | area, interval_start_utc, price_eur, price_dkk, value_hash, latest_run_id | Primary key `(area, interval_start_utc)` / 自然唯一键 |
| `price_versions` | area/time, old/new values, run ID, observed_at | Record actual value changes, not every unchanged import / 只记录真实数值修订 |
| `quality_issues` | run ID, area/time or range, rule_code, severity, details | Findings reference data and rule / 可定位到数据与规则 |

Canonical hashes use normalised timestamp, area and Decimal values. JSON whitespace or field order must not create a revision.
哈希基于规范化业务字段；JSON 空白和字段顺序变化不能制造版本修订。

Idempotency: loading the same content twice leaves the same curated rows and versions, with two audit runs. A corrected price updates one current row and appends one revision.
重复导入仅增加运行审计；修订价格更新当前值并增加一条版本记录。

Do not silently choose between conflicting values for the same natural key within one response. Fail that facts load, save the raw response and report `CONFLICTING_SOURCE_DUPLICATE`.
同次来源响应若同键不同值，不能静默选一个；保存原文、回滚数据写入并记录错误。

## Validation and recovery / 校验与恢复

- Missing required fields, unknown areas and non-finite prices produce explicit schema/value errors. / 字段、区域、非法数值明确报错。
- Identical source duplicates can be deduplicated and counted. Missing intervals become quality issues within the requested complete historical range. / 同值重复可去重并计数，历史完整范围缺口要报告。
- A local civil day is defined by its local midnight boundaries converted to UTC. For 15-minute data: 92 intervals on 2026-03-29, 100 on 2026-10-25, 96 on an ordinary day. / 夏令时切换日不是固定 96 条。
- Missing-data checks apply to requested intervals that should already exist; do not flag tomorrow's unpublished prices just because they are not present. Keep release-time rules configurable and labelled. / 不将尚未发布的未来价格当成缺失。
- Network timeouts, HTTP 429 and HTTP 5xx have bounded retry: at most three total attempts. Honour a valid `Retry-After` within the configured maximum wait; otherwise report a recoverable failure. Inject the sleeper in tests. / 重试有上限，测试不真实长时间等待。
- Validation precedes facts writes. Current rows, revisions and quality findings for one run commit atomically; a failure rolls them back. Record the failed run separately. / 一次数据事务整体提交或回滚，失败状态独立留存。
- Resume via rerunning the same interval safely. / 同一区间可以安全重跑。

## Public interfaces / 对外接口

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
- `GET /health`: process health; `GET /ready`: database/migration readiness. / 分开进程健康与数据就绪。
- `GET /prices?area=DK2&start=...&end=...&limit=100&cursor=...`: ascending UTC order, maximum limit 1000, opaque cursor, no duplicates across pages. / 稳定排序与分页。
- `GET /quality?area=DK2&start=...&end=...`: documented rule results. / 规则结果。
- `GET /runs/{run_id}`: ingestion status and counts. / 导入记录。
- `GET /summary/daily?area=DK2&start_date=...&end_date=...`: local-day count, min/mean/max and missing count. Date range is also half-open. / 按当地自然日汇总。

Use bound SQL parameters. Reject unsupported area, naive query timestamps, `start >= end`, limit outside 1–1000, malformed cursor and excessive v1 range over 366 days with HTTP 422. Return 503 when readiness fails; do not expose raw database exceptions to callers.
绑定 SQL 参数，校验查询边界；数据库不可用返回明确状态，不泄露内部异常。

## File responsibilities / 文件职责

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
保留可阅读 SQL；数据库行为用真实 PostgreSQL 验证。

## Acceptance and evidence / 验收与证据

1. Load at least 30 complete historical days for DK1/DK2 if source access permits; save exact range and counts, not a fabricated row target. / 记录真实范围与数量。
2. Prove repeat-import idempotency, one changed-price revision and source-conflict rejection. / 证明重复、修订与冲突处理。
3. Demonstrate DST days, negative prices, partial failure, timeout and database rollback. / 边界与失败演示。
4. Query API and SQL return checked fixture results. / 接口与查询有已知答案。
5. Offline demo uses licensed/correctly attributed captured data or clearly labelled synthetic fixtures; never call synthetic records real. / 离线来源明确。
6. `pytest` unit and integration suites actually run; CI uses a PostgreSQL service. Save failures and final results. / 保存真实测试与 CI 结果。
7. Measure query runtime only with row count, environment and command recorded. No unsupported scale claims. / 性能结果有条件与命令。
8. README, architecture, schema, English bug report, decisions, AI disclosure, evidence and learning progress are complete. / 完整说明与学习记录。

## Deferred extensions / 选做扩展

Azure deployment, Kafka/Spark, an LLM assistant, authentication and a complex dashboard are optional after the core is verified. Add one only when its workplace value can be explained and its cost is approved.
核心通过后再选扩展，须讲清价值与费用。

## Ownership and language / 本人能力与语言

The learner must personally run an import, write one join and one window query, reproduce a missing-interval bug, and explain UTC/idempotency/rollback in English. Technical completion alone does not prove these learning outcomes.
本人需运行导入、写 JOIN 与窗口查询、复现缺口问题，并用英语解释 UTC、幂等与回滚。
