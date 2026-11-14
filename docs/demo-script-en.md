# Three-minute demonstration

1. Purpose (30 s): This project makes Danish day-ahead electricity data traceable.
   I can show the original source capture, its hash and the import audit.
2. Import (45 s): Run scripts/demo.ps1. The offline demo uses a real attributed October
   capture, not synthetic prices. Each area has 2,980 records over 31 local days.
   The second import reports unchanged rows rather than duplicates.
3. Reliability (45 s): Show test_ingestion.py, test_recovery.py and test_quality.py.
   A corrected value creates a revision; conflicting same-response values fail.
   A deliberately failed database write rolls back facts while retaining failed-run evidence.
   Explain the 100-interval autumn DST day and the exact missing-interval test.
4. API and SQL (45 s): Start the local API, show /ready and a prices page.
   Explain signed pagination, Decimal strings and a JOIN/window query in sql/analysis.sql.
5. Limits (15 s): This is a local portfolio backend, not a retail-bill predictor.
   The implementation used AI assistance. Personal ownership practice is recorded separately.

Do not claim independent implementation or mastery of unreviewed modules.
