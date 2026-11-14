# Architecture

Source bytes are immutable UUID-named captures with SHA-256 and request metadata.
Paged HTTP bodies are stored losslessly inside a source_pages envelope; decode_records
reconstructs source numbers directly as Decimal. The official API takes local Danish
date boundaries; the adapter requests enclosing local days and filters exact UTC instants.

FetchRequest validates aware UTC bounds. Normalisation rejects floats, unknown areas,
invalid/non-finite prices and off-grid timestamps. Canonical six-place values use HALF_EVEN.
The natural current-price key is (area, UTC interval start). Negative prices are legitimate.

An import holds a PostgreSQL session advisory lock. A concurrent importer is rejected.
Run creation and raw snapshot metadata are independently committed. The facts transaction
updates current values, appends actual revisions, inserts quality findings and records success
atomically. A failure rolls those changes back and updates the run to FAILED separately.
No database can preserve a fresh audit while that database itself is completely unreachable;
the surviving-audit guarantee covers a failed facts transaction on a reachable database.

Current-price writes use explicit SELECT FOR UPDATE followed by INSERT/UPDATE, under the
single-import lock. This makes revision decisions visible. They provide transactional
upsert semantics; PostgreSQL ON CONFLICT syntax is not required for this implementation.

Five business tables are migrated by Alembic. Tests use UUID-named schemas with no public
fallback and a schema-qualified migration marker. The isolation regression is retained.
Daily SQL uses local midnight boundaries; DST days therefore have 92/96/100 intervals.
Quality defaults to completed elapsed intervals; a configurable cutoff supports tested policies.

FastAPI uses bound parameters and literal sort clauses. Signed cursors bind area/range/last
UTC instant; signatures prevent modification, but are not authentication. The local API
has no accounts and binds only to loopback. Deployment/authentication are outside this demo.
