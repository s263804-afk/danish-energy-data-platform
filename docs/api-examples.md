# API examples

Start: python -m energy_platform.cli serve --port 8000 (project environment).
Open http://127.0.0.1:8000/docs for the generated contract.

- GET /health checks the process.
- GET /ready checks PostgreSQL, the migration revision and the five tables.
- GET /prices?area=DK2&start=2026-09-30T22:00:00Z&end=2026-10-31T23:00:00Z&limit=10
  returns items/count/next_cursor. Copy the opaque next_cursor into the next request.
- GET /quality with the same area/start/end recomputes current completeness.
- GET /runs/{UUID} returns the audit and captured-source hash, without local secret paths.
- GET /summary/daily?area=DK2&start_date=2026-10-01&end_date=2026-11-01
  returns Copenhagen local-day counts, prices and missing counts.

All ranges are half-open. Supported areas: DK1/DK2; limit: 1..1000; range: at most 366 days.
Naive timestamps, unsupported areas, reversed ranges and malformed/mismatched/tampered
cursors return 422. Unknown run UUID returns 404. Database readiness failure returns 503.
Decimal values are JSON strings to preserve precision. Cursor validity ends at process restart.
Clients should read large intervals from this backend rather than repeatedly polling Energinet.

Real loopback HTTP evidence is in reports/evidence/completion/actual-http.json.
