# Verified source contract — S1

Checked 2026-11-12 against official documentation, dataset metadata and small live captures.
Data source: Energinet / Energi Data Service, `DayAheadPrices`.

- [Dataset](https://www.energidataservice.dk/tso-electricity/DayAheadPrices)
- [Metadata API](https://api.energidataservice.dk/meta/dataset/DayAheadPrices)
- [Official API guide](https://www.energidataservice.dk/guides/api-guides)
- [Data terms](https://www.energidataservice.dk/terms-and-conditions)

## Fields, units and coverage

| Field | Source meaning | Planned internal use |
| --- | --- | --- |
| `TimeUTC` | UTC interval-start string; source omits `Z` | Aware UTC datetime and PostgreSQL `timestamptz` in S2 |
| `TimeDK` | Danish local interval-start string | Display/comparison, never a unique key |
| `PriceArea` | Bidding zone; metadata includes DK1/DK2 and other countries | Core project accepts DK1/DK2 |
| `DayAheadPriceEUR` | EUR/MWh JSON number | Decimal; six places, ROUND_HALF_EVEN in S2 |
| `DayAheadPriceDKK` | DKK/MWh JSON number | Same Decimal policy; source-calculated DKK value |

Metadata reports `resolution="15 minutes (PT15M)"`, update frequency `P1D`,
`dataFrom="2025-10-01T00:00:00"` and, when captured,
`dataTo="2026-11-13T23:45:00"`. These last two strings are recorded exactly as source
metadata reports them; they are not a guarantee that every interval/area is complete.
Version 1 will support modern 15-minute data from the Danish local date 2025-10-01.
Earlier hourly `Elspotprices` data requires a different adapter and is outside this contract.
The newest available boundary is dynamic, not a hard-coded permanent end date.

The metadata describes a daily update and publication guidance, not a guaranteed exact
release instant. S4 must document a configurable policy for unpublished future intervals.

## Request range and timezone

`start` is included; `end` is excluded. The guide interprets request dates/times in Danish
local time. An ISO-looking request value must not simply be assumed to mean UTC.
Returned `TimeUTC` is explicitly documented as UTC despite having no suffix.
Attaching UTC is therefore a source-contract decision, not a Windows timezone guess.

Live winter example:

```text
start=2026-11-01T00:00, end=2026-11-01T01:00  (Danish local)
TimeUTC = 2026-10-31 23:00, 23:15, 23:30, 23:45
TimeDK  = 2026-11-01 00:00, 00:15, 00:30, 00:45
```

Live summer example:

```text
start=2026-07-01T00:00, end=2026-07-01T01:00  (Danish local)
TimeUTC = 2026-06-30 22:00, 22:15, 22:30, 22:45
```

The UTC spacing is 15 minutes in both four-record samples. These checks do not validate
the production DST gap/overlap logic; that work is still S2/S4. Internal fetch requests
will use half-open aware UTC bounds. The S3 adapter must safely enclose them with local-day
source requests and filter back to exact UTC bounds, avoiding ambiguous local-hour limits.

## Filter, order and pagination

Verified request parameters:

```text
filter={"PriceArea":["DK2"]}
sort=TimeUTC asc,PriceArea asc
limit=2
offset=0, then 2, then 4
```

The first two pages contain two rows each. Their concatenation equals a separately
captured four-row response; offset 4 returns zero rows for that same one-hour range.
All sampled records are DK2, ordered by UTC, with no repeated interval across the pages.
The guide documents offset as a row offset, not a page number.

Observed outer `total` values are 2, 2, 4 and 0 for those requests. In these responses it
tracks returned rows, not the total rows available before limiting. The S3 adapter must
not stop at `offset >= total` after the first full page. Use returned page length/exhaustion,
explicit ordering, bounds and duplicate/conflict checks. Source revisions can still change
a dataset between offset-based requests; S1 does not promise an atomic upstream snapshot.

## Captures and provenance

`reports/evidence/source-s1/` contains original response bytes, request metadata and
`checks.json` with fourteen successful comparisons/hash checks. The captures cover eight
distinct DK2 intervals in two one-hour windows. Pagination captures repeat some of those
intervals; they are not additional unique data. `tests/fixtures/source_probe.json` is an
unmodified copy of the real four-record winter response, with adjacent metadata.

All are labelled real source captures. Unit-test byte literals and constructed HTTP
responses are controlled test inputs, not live source evidence. The workbook's older
two-record sample remains separate reference evidence.

## Access, rate limits and attribution

The public requests used no token. Access is not a permanent availability guarantee.
Initial rapid follow-up probes received HTTP 429. Later deliberately spaced requests
succeeded; no particular sustainable request rate has been established. The inspection
CLI sends only one request, records error responses and exposes failure. Respect valid
`Retry-After` and current dataset guidance. Do not run a rapid batch of probes.
The production bounded-retry policy remains S5.

Data is published under CC BY 4.0. Attribute Energinet and identify any transformation;
do not imply endorsement. These captured JSON responses are unmodified. Any later
normalisation or aggregation must be labelled as a transformation. Attribution:

> Source: Energinet (www.energidataservice.dk).

Only small local snapshots are prepared here. No public repository or larger public
data redistribution has been performed.
