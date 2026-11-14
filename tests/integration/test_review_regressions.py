import base64
import json
from datetime import UTC, date, datetime, timedelta

import httpx
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import text

from energy_platform.api import create_app
from energy_platform.domain import FetchRequest
from energy_platform.ingestion import IngestionError, ingest
from energy_platform.quality import local_day_bounds
from energy_platform.repository import PriceRepository
from energy_platform.source import PriceSource
from tests.integration.test_ingestion import fixture_rows, request, source


@pytest.mark.parametrize("failure", ["first", "later", "later503"])
def test_every_received_page_is_retained_when_a_fetch_fails(db, tmp_path, failure):
    valid = json.dumps({"records": fixture_rows(1)}).encode()
    broken = b"{broken-json"
    calls = []

    def response(req):
        calls.append(req)
        if failure != "first" and len(calls) == 1:
            return httpx.Response(200, content=valid)
        if failure == "later503":
            return httpx.Response(503, content=b"source down")
        return httpx.Response(200, content=broken)

    fetcher = PriceSource(
        client=httpx.Client(transport=httpx.MockTransport(response)),
        page_size=1,
        sleep=lambda _: None,
    )
    with pytest.raises(IngestionError):
        ingest(request(), fetcher, PriceRepository(db, tmp_path / "raw"))
    with db.connect() as conn:
        audit = conn.execute(text("SELECT status,snapshot_id FROM ingestion_runs")).one()
        assert audit.status == "FAILED"
        assert audit.snapshot_id is not None
        assert conn.scalar(text("SELECT count(*) FROM prices")) == 0
        path = conn.scalar(text("SELECT path FROM raw_snapshots"))
    from pathlib import Path

    raw = Path(path).read_bytes()
    if failure == "first":
        assert raw == broken
    else:
        envelope = json.loads(raw)
        pages = [base64.b64decode(p) for p in envelope["source_pages_base64"]]
        assert pages == [valid, b"source down" if failure == "later503" else broken]


def test_future_rows_cannot_compensate_for_a_missing_elapsed_interval(db, tmp_path):
    start, end = local_day_bounds(date(2026, 2, 1))
    cutoff = datetime(2026, 2, 1, 11, tzinfo=UTC)
    rows = [
        {
            "TimeUTC": (start + timedelta(minutes=15 * i)).isoformat(),
            "PriceArea": "DK2",
            "DayAheadPriceEUR": "10",
            "DayAheadPriceDKK": "75",
        }
        for i in range(96)
        if i != 10
    ]
    ingest(
        FetchRequest("DK2", start, end),
        source(tmp_path, rows),
        PriceRepository(db, tmp_path / "raw"),
    )
    with TestClient(create_app(db, now=lambda: cutoff)) as client:
        daily = client.get(
            "/summary/daily",
            params={
                "area": "DK2",
                "start_date": "2026-02-01",
                "end_date": "2026-02-02",
            },
        ).json()["items"][0]
        quality = client.get(
            "/quality",
            params={
                "area": "DK2",
                "start": start.isoformat(),
                "end": end.isoformat(),
            },
        ).json()
        assert daily["count"] == 95
        assert daily["expected"] == 48
        assert daily["elapsed_count"] == 47
        assert daily["missing"] == quality["count"] == 1
