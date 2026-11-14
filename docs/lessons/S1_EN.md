# S1 — Follow the data

## Today's goal

Trace a real source response into a saved file, and prove that Python can query PostgreSQL.

## What this solves at work

An analyst needs to know where a price came from and which time interval it describes.
A developer must also prove that the application can reach its database before building
an import process. S1 establishes those facts with saved evidence.

## English explanation

An API is an interface that lets one program request data from another service.
We send a GET request with an area, a range and explicit paging parameters.
The response payload contains price records. We save its original bytes before using them.

The source's request range uses Danish local time. Its `TimeUTC` field means UTC even
though the text has no `Z`. We use that documented meaning, not the computer's local timezone.
The prices are wholesale prices per MWh. They are not household electricity bills.

The database check is a separate path: create an engine, open a connection, execute SQL,
read the answer, and close the connection. `SELECT 1` returning `1` proves a working SQL
connection. It does not prove that energy tables or an import pipeline exist.

## Read the code

Open `scripts/source_probe.py`, starting at `main()`:

1. `argparse` reads `--area`, local range, `--limit`, `--offset` and `--output`.
   It refuses an existing capture path before making a network request.
2. `build_params()` names the area filter and orders records by `TimeUTC asc,PriceArea asc`.
3. `httpx.get()` requests the response. This inspection tool makes one attempt.
4. `save_capture()` opens the file in `xb` mode: write bytes, create exclusively.
   Existing files cannot be overwritten.
5. `decode_payload()` uses `parse_float=Decimal`, so a decimal price is not first converted
   to an approximate binary float. The original file still contains JSON numbers.
6. A metadata file records URL, capture time, HTTP status, SHA-256, row count and attribution.
   An HTTP error is saved and then raised; it is not treated as zero successful rows.

Then open `tests/integration/test_database_ready.py`:

```python
load_dotenv(root / ".env", override=False)
database_url = os.environ["DATABASE_URL"]
engine = create_engine(database_url, connect_args={"connect_timeout": 3})
with engine.connect() as connection:
    assert connection.scalar(text("SELECT 1")) == 1
```

`override=False` keeps an explicitly supplied environment URL, which lets us verify a
bad connection fails. There is no SQLite fallback and no skipped integration test.
`SHOW server_version_num` also checks PostgreSQL major version 17.

## Run and observe

From the repository root in PowerShell:

```powershell
& .\scripts\start-local-db.ps1
& .\.venv\Scripts\python.exe -m pytest tests/integration/test_database_ready.py -v --tb=short
& .\.venv\Scripts\python.exe -m pytest -v --tb=short
Get-Content tests\fixtures\source_probe.json
```

Observed agent result: six tests passed with no skips. A separately supplied unreachable
URL made the readiness test fail, as required. A fresh project environment also passed six tests.

One real saved record contains:

```json
{"TimeUTC":"2026-10-31T23:00:00","TimeDK":"2026-11-01T00:00:00","PriceArea":"DK2","DayAheadPriceEUR":257.450012,"DayAheadPriceDKK":1924.052665}
```

`TimeUTC` and `PriceArea` arrive as JSON strings. `DayAheadPriceEUR` arrives as a JSON
number in EUR/MWh and is decoded to Python Decimal. The UTC timestamp will become an
aware Python datetime in S2. S1 does not yet write these records into database tables.

## Five terms

| English | Example |
| --- | --- |
| source | Energinet is the source of these prices. |
| dependency | httpx is a Python dependency. |
| payload | The payload contains four price records. |
| set up | We set up a local PostgreSQL instance. |
| trace back to | We can trace this value back to a saved response. |

## Change one thing

In `scripts/source_probe.py`, change only the `--area` argument's **default** from
`"DK2"` to `"DK1"`. Keep both allowed choices. Do not change the saved DK2 fixture.
Then personally run:

```powershell
& .\.venv\Scripts\python.exe scripts/source_probe.py --output .local/learning/my-dk1-first.json
& .\.venv\Scripts\python.exe -m pytest -v --tb=short
```

The output path must be new. If it already exists, choose a new filename. If the source
returns 429, inspect the saved metadata's `retry_after`; wait accordingly and use a new
capture path later. Do not repeatedly retry. Offline file inspection and database tests
remain available while the source is rate-limited.

Compare the first DK1 record with the saved DK2 record at the same `TimeUTC`.
Report the area, UTC time, EUR price and units. The two areas may have the same price;
describe the observation instead of assuming they must differ.

## Explain it aloud

Read once, then explain the same ideas without copying:

> This project will provide reliable Danish electricity data for analysis. In the first
> task, we checked the source contract and set up an isolated Python environment with
> a real PostgreSQL database. The source provides day-ahead prices for different bidding
> zones. Our probe sends a small request and saves the original response with its URL,
> capture time and file hash. This lets us trace a value back to its source. One important
> detail is that request boundaries use Danish local time, while TimeUTC represents UTC.
> We also ran SELECT 1 through Python to check the database connection. An invalid URL
> caused a real test failure, so the test does not silently skip connection problems.
> At this stage, we have verified the environment and source behaviour. We have not yet
> built the price tables, import pipeline or query API.

Use “I ran/changed/explained” only for actions you actually performed personally.
The template uses “we” for the assisted project results and is not proof of mastery.

## Three questions

1. What does `SELECT 1` prove, and what does it not prove?
2. Why do we save the original response instead of keeping only processed values?
3. Why must we not interpret the source's `TimeUTC` string as the Windows local timezone?

Send your code change, observed output and a short English explanation. Technical meaning
and English grammar will be corrected separately. Status remains PENDING_LEARNER until then.
