# Software completion verification

Date: 2026-11-13. Scope: technical S1–S7; personal learning separately tracked.

- python -m pytest -q --tb=short: 62 passed, no skips or warnings.
  Evidence: evidence/completion/review-green-full-suite.log.
- Ruff check/format: clean after import/format corrections.
- Real PostgreSQL 17.12: Alembic five-table schema, separate test schemas and regression
  for migration-marker isolation.
- Offline demo: two independent areas, 31 local days each, 2,980 rows each, zero missing;
  repeat imports insert/update zero facts. Evidence: ../reports/demo/software-demo.json.
- Real source provenance: tests/fixtures/energinet_october_2026.metadata.json.
- Real localhost HTTP: health, ready, prices, non-overlapping next page, quality, daily
  summary and invalid-limit 422; evidence/completion/actual-http.json.
- Named SQL measurement: five local daily-summary invocations, 31 result rows over a
  5,960-row dataset. Full timings/environment: evidence/completion/runtime-and-query.json.
  The first includes connection setup; these are not large-scale benchmark claims.
- Retry 429/503/timeout tests use injected transport/sleep; they are controlled fault tests.
- Database rollback uses an actual PostgreSQL trigger that deliberately fails the second
  write. The failure audit and raw snapshot survive; no facts/revisions/issues commit.
- CI: PostgreSQL workflow configured; remote status is recorded separately when observed.

Actual incident: an early test-schema search_path included public, and Alembic incorrectly
found the public revision marker. The regression failed (0 own tables), then passed after
removing the public fallback and qualifying the version table. Exactly two identified
synthetic runs were marked FAILED/TEST_ISOLATION_INCIDENT and their facts removed.
Their audit/snapshot records remain. The four genuine source rows were preserved.

Additional RED→GREEN boundaries: compare DST fold times after UTC conversion; reject an
empty cursor rather than treating it as absent. All covering tests are in the final suite.

Fresh reproduction and review status: see the adjacent final-release record generated
after those checks. Neither configured CI nor prepared learning notes imply observed mastery.

Independent review: two Important findings fixed in one regression pass.
Malformed first/later page and later persistent 503 preserve received raw bytes; a fixed
midday test proves future rows cannot conceal an elapsed gap. Four new tests failed before
the fixes, then passed; full suite 62/62 passed in main and fresh environments. New real
HTTP checks passed. Evidence: review-red.log, review-green-full-suite.log,
fresh-review-tests.log, actual-http-after-review.json.
Deferred minor: pre-2025-10-01 unsupported requests are not enforced at the API boundary.
Restrict this version to the documented modern dataset; earlier-period completeness
findings may be misleading. The verified capture is entirely inside supported coverage.
