from uuid import uuid4

import pytest
from sqlalchemy import text
from sqlalchemy.exc import IntegrityError


def test_five_tables_are_migrated(db):
    with db.connect() as conn:
        names = set(
            conn.scalars(text("SELECT tablename FROM pg_tables WHERE schemaname=current_schema()"))
        )
        assert {
            "prices",
            "price_versions",
            "raw_snapshots",
            "ingestion_runs",
            "quality_issues",
        } <= names


def test_test_schema_has_its_own_prices_table_even_when_public_is_migrated(db):
    with db.connect() as conn:
        assert (
            conn.scalar(
                text("""
            SELECT count(*) FROM information_schema.tables
            WHERE table_schema=current_schema() AND table_name='prices'
        """)
            )
            == 1
        )


def seed_run(conn):
    run = uuid4()
    conn.execute(
        text("""
        INSERT INTO ingestion_runs(id,area,start_utc,end_utc,status)
        VALUES(:id,'DK2','2026-10-25T00:00Z','2026-10-25T02:00Z','RUNNING')
    """),
        {"id": run},
    )
    return run


def test_dst_repeated_local_hour_keeps_distinct_utc_keys(db):
    with db.begin() as conn:
        run = seed_run(conn)
        for timestamp in ["2026-10-25T00:15Z", "2026-10-25T01:15Z"]:
            conn.execute(
                text("""
                INSERT INTO prices(area,interval_start_utc,price_eur,price_dkk,
                                   value_hash,latest_run_id)
                VALUES('DK2',:ts,-10.25,-76.5,'hash',:run)
            """),
                {"ts": timestamp, "run": run},
            )
        assert conn.scalar(text("SELECT count(*) FROM prices")) == 2
        local = conn.scalars(
            text("SELECT interval_start_utc AT TIME ZONE 'Europe/Copenhagen' FROM prices")
        ).all()
        assert local[0] == local[1]


def test_duplicate_key_and_unknown_area_are_database_errors(db):
    with db.begin() as conn:
        run = seed_run(conn)
        conn.execute(
            text("""
            INSERT INTO prices VALUES ('DK2','2026-10-25T00:15Z',1,2,'h',:run)
        """),
            {"run": run},
        )
    with pytest.raises(IntegrityError), db.begin() as conn:
        conn.execute(
            text("""
            INSERT INTO prices VALUES ('DK2','2026-10-25T00:15Z',2,3,'h',:run)
        """),
            {"run": run},
        )
    with pytest.raises(IntegrityError), db.begin() as conn:
        conn.execute(
            text("""
            INSERT INTO prices VALUES ('DK3','2026-10-25T00:15Z',2,3,'h',:run)
        """),
            {"run": run},
        )
