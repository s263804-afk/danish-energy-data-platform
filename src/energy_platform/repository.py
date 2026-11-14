"""Explicit PostgreSQL statements and a session-level single-import lock."""

import hashlib
import json
from contextlib import contextmanager
from pathlib import Path
from uuid import uuid4

from sqlalchemy import text

from energy_platform.domain import IngestionResult

LOCK_KEY = 2026111201


class ConcurrentRunError(RuntimeError):
    pass


class PriceRepository:
    def __init__(self, engine, snapshot_dir):
        self.engine, self.snapshot_dir = engine, Path(snapshot_dir)

    @contextmanager
    def single_run(self):
        with self.engine.connect() as conn:
            locked = conn.scalar(text("SELECT pg_try_advisory_lock(:key)"), {"key": LOCK_KEY})
            conn.commit()
            if not locked:
                raise ConcurrentRunError("CONCURRENT_RUN")
            try:
                yield
            finally:
                conn.execute(text("SELECT pg_advisory_unlock(:key)"), {"key": LOCK_KEY})
                conn.commit()

    def start(self, request):
        run = uuid4()
        with self.engine.begin() as conn:
            conn.execute(
                text("""
                INSERT INTO ingestion_runs(id,area,start_utc,end_utc,status)
                VALUES(:id,:area,:start,:end,'RUNNING')
            """),
                {
                    "id": run,
                    "area": request.area,
                    "start": request.start_utc,
                    "end": request.end_utc,
                },
            )
        return run

    def capture(self, run, result):
        snapshot = uuid4()
        self.snapshot_dir.mkdir(parents=True, exist_ok=True)
        path = self.snapshot_dir / f"{snapshot}.json"
        with path.open("xb") as stream:
            stream.write(result.content)
        with self.engine.begin() as conn:
            conn.execute(
                text("""
                INSERT INTO raw_snapshots(id,parameters,sha256,path,http_status)
                VALUES(:id,CAST(:parameters AS jsonb),:sha,:path,:status)
            """),
                {
                    "id": snapshot,
                    "parameters": json.dumps(result.parameters),
                    "sha": hashlib.sha256(result.content).hexdigest(),
                    "path": str(path.resolve()),
                    "status": result.status,
                },
            )
            conn.execute(
                text("UPDATE ingestion_runs SET snapshot_id=:sid WHERE id=:id"),
                {"sid": snapshot, "id": run},
            )

    def fail(self, run, code):
        with self.engine.begin() as conn:
            conn.execute(
                text("""
                UPDATE ingestion_runs SET status='FAILED',error_code=:code,finished_at=now()
                WHERE id=:id
            """),
                {"id": run, "code": code},
            )

    def persist(self, run, records, duplicates, issues=()):
        inserted = updated = unchanged = 0
        with self.engine.begin() as conn:
            for record in records:
                params = {
                    "area": record.area,
                    "ts": record.interval_start_utc,
                    "eur": record.price_eur,
                    "dkk": record.price_dkk,
                    "hash": record.value_hash,
                    "run": run,
                }
                old = (
                    conn.execute(
                        text("""
                    SELECT price_eur,price_dkk,value_hash FROM prices
                    WHERE area=:area AND interval_start_utc=:ts FOR UPDATE
                """),
                        params,
                    )
                    .mappings()
                    .first()
                )
                if old is None:
                    conn.execute(
                        text("""
                        INSERT INTO prices(area,interval_start_utc,price_eur,price_dkk,
                                           value_hash,latest_run_id)
                        VALUES(:area,:ts,:eur,:dkk,:hash,:run)
                    """),
                        params,
                    )
                    inserted += 1
                elif old["value_hash"] == record.value_hash:
                    unchanged += 1
                else:
                    conn.execute(
                        text("""
                        UPDATE prices SET price_eur=:eur,price_dkk=:dkk,value_hash=:hash,
                                          latest_run_id=:run
                        WHERE area=:area AND interval_start_utc=:ts
                    """),
                        params,
                    )
                    conn.execute(
                        text("""
                        INSERT INTO price_versions(area,interval_start_utc,old_eur,old_dkk,
                                                   new_eur,new_dkk,run_id)
                        VALUES(:area,:ts,:old_eur,:old_dkk,:eur,:dkk,:run)
                    """),
                        {**params, "old_eur": old["price_eur"], "old_dkk": old["price_dkk"]},
                    )
                    updated += 1
            for issue in issues:
                conn.execute(
                    text("""
                    INSERT INTO quality_issues(run_id,area,interval_start_utc,rule_code,
                                               severity,details)
                    VALUES(:run,:area,:ts,:rule,:severity,:details)
                """),
                    {
                        "run": run,
                        "area": issue.area,
                        "ts": issue.interval_start_utc,
                        "rule": issue.rule_code,
                        "severity": issue.severity,
                        "details": issue.details,
                    },
                )
            conn.execute(
                text("""
                UPDATE ingestion_runs SET status='SUCCEEDED',finished_at=now(),
                    inserted=:inserted,updated=:updated,unchanged=:unchanged,duplicates=:duplicates
                WHERE id=:id
            """),
                {
                    "id": run,
                    "inserted": inserted,
                    "updated": updated,
                    "unchanged": unchanged,
                    "duplicates": duplicates,
                },
            )
        return IngestionResult(
            str(run), "SUCCEEDED", inserted, updated, unchanged, duplicates, len(issues)
        )
