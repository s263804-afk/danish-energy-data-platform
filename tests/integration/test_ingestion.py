"""Synthetic data exercises PostgreSQL idempotency and audit invariants."""

import json
from datetime import UTC, datetime, timedelta

import pytest
from sqlalchemy import text

from energy_platform.domain import FetchRequest
from energy_platform.ingestion import IngestionError, ingest
from energy_platform.repository import PriceRepository
from energy_platform.source import SnapshotSource


def fixture_rows(count=96):
    start = datetime(2026, 2, 1, tzinfo=UTC)
    return [
        {
            "TimeUTC": (start + timedelta(minutes=15 * i)).isoformat(),
            "PriceArea": "DK2",
            "DayAheadPriceEUR": "-10.25",
            "DayAheadPriceDKK": "-76.5",
        }
        for i in range(count)
    ]


def request():
    return FetchRequest("DK2", datetime(2026, 2, 1, tzinfo=UTC), datetime(2026, 2, 2, tzinfo=UTC))


def source(tmp_path, rows, filename="synthetic.json"):
    path = tmp_path / filename
    path.write_text(json.dumps({"provenance": "SYNTHETIC_TEST_FIXTURE", "records": rows}))
    return SnapshotSource(path)


def counts(db):
    with db.connect() as conn:
        return tuple(
            conn.scalar(text(f"SELECT count(*) FROM {table}"))
            for table in ["prices", "price_versions", "ingestion_runs"]
        )


def test_repeat_import_is_idempotent_and_changed_value_adds_one_revision(db, tmp_path):
    repo = PriceRepository(db, tmp_path / "raw")
    rows = fixture_rows()
    first = ingest(request(), source(tmp_path, rows), repo)
    assert first.inserted == 96
    second = ingest(request(), source(tmp_path, rows), repo)
    assert second.unchanged == 96
    assert counts(db) == (96, 0, 2)
    rows[5]["DayAheadPriceEUR"] = "20.5"
    third = ingest(request(), source(tmp_path, rows), repo)
    assert third.updated == 1
    assert counts(db) == (96, 1, 3)


def test_json_whitespace_and_identical_duplicates_do_not_create_revisions(db, tmp_path):
    repo = PriceRepository(db, tmp_path / "raw")
    rows = fixture_rows()
    ingest(request(), source(tmp_path, rows), repo)
    rows.append(dict(rows[0]))
    result = ingest(request(), source(tmp_path, rows), repo)
    assert result.duplicates == 1
    assert counts(db) == (96, 0, 2)


@pytest.mark.parametrize("invalid", ["conflict", "missing", "nan"])
def test_invalid_response_has_no_partial_facts_and_keeps_failed_audit(db, tmp_path, invalid):
    rows = fixture_rows()
    if invalid == "conflict":
        rows.append({**rows[0], "DayAheadPriceEUR": "99"})
    elif invalid == "missing":
        del rows[-1]["DayAheadPriceEUR"]
    else:
        rows[-1]["DayAheadPriceEUR"] = "NaN"
    with pytest.raises(IngestionError) as failure:
        ingest(request(), source(tmp_path, rows), PriceRepository(db, tmp_path / "raw"))
    assert counts(db) == (0, 0, 1)
    with db.connect() as conn:
        audit = conn.execute(text("SELECT status,error_code,snapshot_id FROM ingestion_runs")).one()
        assert audit.status == "FAILED"
        assert audit.snapshot_id is not None
        if invalid == "conflict":
            assert failure.value.code == "CONFLICTING_SOURCE_DUPLICATE"
    assert len(list((tmp_path / "raw").glob("*.json"))) == 1
