"""Readable bound SQL for reporting. UTC instants remain the join identity."""

from sqlalchemy import text

DAILY_SQL = """
WITH days AS (
    SELECT generate_series(CAST(:start AS date), CAST(:end AS date)-1, interval '1 day')::date d
), bounds AS (
    SELECT d,least((d+1)::timestamp AT TIME ZONE 'Europe/Copenhagen',
      to_timestamp(floor(extract(epoch FROM
        coalesce(CAST(:asof AS timestamptz),CURRENT_TIMESTAMP))/900)*900)) AS expected_end
    FROM days
), expected AS (
    SELECT d,expected_end,
      greatest(0,floor(extract(epoch FROM
        (expected_end
         - d::timestamp AT TIME ZONE 'Europe/Copenhagen'))/900))::integer AS expected
    FROM bounds
)
SELECT e.d AS date, e.expected, count(p.interval_start_utc)::integer AS count,
       min(p.price_eur) AS min_eur, avg(p.price_eur) AS mean_eur,
       max(p.price_eur) AS max_eur,
       count(p.interval_start_utc) FILTER (
         WHERE p.interval_start_utc<e.expected_end)::integer AS elapsed_count,
       greatest(0,e.expected-count(p.interval_start_utc) FILTER (
         WHERE p.interval_start_utc<e.expected_end)::integer) AS missing
FROM expected e LEFT JOIN prices p
  ON p.area=:area
 AND p.interval_start_utc >= e.d::timestamp AT TIME ZONE 'Europe/Copenhagen'
 AND p.interval_start_utc < (e.d+1)::timestamp AT TIME ZONE 'Europe/Copenhagen'
GROUP BY e.d,e.expected,e.expected_end ORDER BY e.d
"""


def daily_summary(engine, area, start, end, expected_until=None):
    with engine.connect() as conn:
        return list(
            conn.execute(
                text(DAILY_SQL),
                {
                    "area": area,
                    "start": start,
                    "end": end,
                    "asof": expected_until,
                },
            ).mappings()
        )


def moving_average_rows(engine, request):
    with engine.connect() as conn:
        return list(
            conn.execute(
                text("""
            SELECT interval_start_utc,price_eur,
              avg(price_eur) OVER (ORDER BY interval_start_utc
                                  ROWS BETWEEN 2 PRECEDING AND CURRENT ROW) AS moving_mean
            FROM prices WHERE area=:area AND interval_start_utc>=:start
            AND interval_start_utc<:end ORDER BY interval_start_utc
        """),
                {"area": request.area, "start": request.start_utc, "end": request.end_utc},
            ).mappings()
        )


def gap_rows(engine, request):
    with engine.connect() as conn:
        return list(
            conn.execute(
                text("""
            WITH previous AS (
              SELECT interval_start_utc,
                lag(interval_start_utc) OVER (ORDER BY interval_start_utc) AS previous_utc
              FROM prices WHERE area=:area AND interval_start_utc>=:start
              AND interval_start_utc<:end
            )
            SELECT *,extract(epoch FROM interval_start_utc-previous_utc)/60 AS gap_minutes
            FROM previous WHERE interval_start_utc-previous_utc>interval '15 minutes'
            ORDER BY interval_start_utc
        """),
                {"area": request.area, "start": request.start_utc, "end": request.end_utc},
            ).mappings()
        )
