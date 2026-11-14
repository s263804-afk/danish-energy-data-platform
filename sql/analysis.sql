-- 1. JOIN: trace a current price back to the run that last changed it.
SELECT p.area,p.interval_start_utc,p.price_eur,r.id,r.status,r.snapshot_id
FROM prices p JOIN ingestion_runs r ON r.id=p.latest_run_id
ORDER BY p.interval_start_utc,p.area LIMIT 20;

-- 2. CTE/aggregate: current prices grouped by Copenhagen local date.
WITH local_prices AS (
 SELECT *, (interval_start_utc AT TIME ZONE 'Europe/Copenhagen')::date AS local_date
 FROM prices
)
SELECT area,local_date,count(*),min(price_eur),avg(price_eur),max(price_eur)
FROM local_prices GROUP BY area,local_date ORDER BY local_date,area;

-- 3. LAG locates interior time gaps (boundary gaps need generated expected intervals).
WITH prior AS (
 SELECT area,interval_start_utc,
  lag(interval_start_utc) OVER (PARTITION BY area ORDER BY interval_start_utc) previous_utc
 FROM prices
)
SELECT * FROM prior WHERE interval_start_utc-previous_utc>interval '15 minutes';

-- 4. Window calculation retains individual rows; the frame is explicitly three samples.
SELECT area,interval_start_utc,price_eur,
 avg(price_eur) OVER (PARTITION BY area ORDER BY interval_start_utc
                     ROWS BETWEEN 2 PRECEDING AND CURRENT ROW) AS moving_mean
FROM prices ORDER BY interval_start_utc,area;

-- 5. Area comparison joins on UTC, not an ambiguous local wall-clock string.
SELECT a.interval_start_utc,a.price_eur AS dk1,b.price_eur AS dk2,
 b.price_eur-a.price_eur AS spread_eur
FROM prices a JOIN prices b USING(interval_start_utc)
WHERE a.area='DK1' AND b.area='DK2' ORDER BY a.interval_start_utc;
