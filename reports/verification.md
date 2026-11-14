# Release verification —14 November2026

Current scope: S1–S7, technically verified. Personal mastery remains separately tracked.

- Main and fresh hash-locked environments:62 tests passed,0 failed,0 skipped.
- PostgreSQL17.12 with real schema/migration/import/rollback/concurrency checks.
- Offline demo:5960 attributed genuine Energinet rows, DK1/DK2,31 Copenhagen days;
  repeat ingestion inserts/updates zero unchanged rows and reports zero missing.
- Actual loopback HTTP: health/readiness, prices/pagination, quality, daily summary
  and invalid-request422 checks observed. Ruff and dependency checks passed.
- Independent review: two important findings fixed with four RED→GREEN regressions.
  Raw HTTP evidence now survives invalid pages and later-page failures; daily
  missing counts use the elapsed expected set, so future rows cannot hide gaps.
- Remote GitHub CI: CONFIGURED_NOT_YET_OBSERVED. Publication status is recorded separately in the delivery manifest.

[Detailed completion evidence](completion-verification.md) records commands, exact
outputs, source provenance, hashes, incidents and reproduction limitations.
[Historical S1-only evidence](verification-s1.md) is retained under its original date;
its six-test total and then-pending implementation do not describe the final release.

Fresh reproduction reused the Windows OS, Python base and installed PostgreSQL
binaries. It was a new project environment and database cluster, not a new OS.
The performance sample is small/local; no production scale claim is made.

Deferred minor: API accepts pre-2025-10-01 requests rather than enforcing the
source coverage bound. Completeness claims are restricted to the documented
supported interval and the verified modern-data dataset.

Learning: partial S1 practice observed (venv/database check and SELECT1→2);
independent explanation and later exercises remain pending. AI-assisted technical
verification is not substituted for personal learning evidence.

## English publication copy

Documentation is published in English. Localized diagnostic labels in selected
archived transcripts/reports were translated or excerpted for publication; these
files are labelled and are not presented as verbatim raw console output. Original
transcripts and bilingual learning materials remain in a separate local backup.
See english-publication.json for original hashes and the affected-file list.
The original English GitHub execution log is evidence/github-ci-verified.log.
Numeric measurements, test outcomes, algorithms and source-data captures are unchanged.
