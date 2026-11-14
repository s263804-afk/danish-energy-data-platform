from uuid import uuid4

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine

from energy_platform.api import create_app
from energy_platform.ingestion import ingest
from energy_platform.repository import PriceRepository
from tests.integration.test_ingestion import fixture_rows, request, source

PARAMS = {"area": "DK2", "start": "2026-02-01T00:00:00Z", "end": "2026-02-01T01:00:00Z"}


def test_prices_have_stable_signed_pagination_and_exact_decimal_values(db, tmp_path):
    result = ingest(
        request(), source(tmp_path, fixture_rows(4)), PriceRepository(db, tmp_path / "raw")
    )
    with TestClient(create_app(db)) as client:
        assert client.get("/health").status_code == 200
        assert client.get("/ready").status_code == 200
        first = client.get("/prices", params={**PARAMS, "limit": 2}).json()
        second = client.get(
            "/prices", params={**PARAMS, "limit": 2, "cursor": first["next_cursor"]}
        ).json()
        assert len(first["items"]) == len(second["items"]) == 2
        all_items = first["items"] + second["items"]
        assert len({r["interval_start_utc"] for r in all_items}) == 4
        assert all_items[0]["price_eur"] == "-10.250000"
        assert second["next_cursor"] is None
        assert client.get("/runs/" + result.run_id).json()["status"] == "SUCCEEDED"
        assert client.get("/runs/" + str(uuid4())).status_code == 404
        assert (
            client.get("/prices", params={**PARAMS, "end": "2026-02-01T00:30Z"}).json()["count"]
            == 2
        )
        assert (
            client.get(
                "/prices", params={**PARAMS, "cursor": first["next_cursor"] + "x"}
            ).status_code
            == 422
        )
        assert (
            client.get(
                "/prices", params={**PARAMS, "area": "DK1", "cursor": first["next_cursor"]}
            ).status_code
            == 422
        )


@pytest.mark.parametrize(
    "changes",
    [
        {"area": "DK3"},
        {"area": "DK2'; DROP TABLE prices;--"},
        {"limit": 1001},
        {"limit": 0},
        {"start": "2026-02-01T00:00:00"},
        {"end": "2026-01-01T00:00Z"},
        {"end": "2028-01-01T00:00Z"},
        {"cursor": "malformed"},
        {"cursor": ""},
    ],
)
def test_invalid_query_returns_422(db, changes):
    with TestClient(create_app(db)) as client:
        assert client.get("/prices", params={**PARAMS, **changes}).status_code == 422


def test_database_unavailable_is_503_while_health_is_200():
    engine = create_engine(
        "postgresql+psycopg://invalid@127.0.0.1:1/no_db", connect_args={"connect_timeout": 2}
    )
    try:
        with TestClient(create_app(engine)) as client:
            assert client.get("/health").status_code == 200
            response = client.get("/ready")
            assert response.status_code == 503
            assert "password" not in response.text
    finally:
        engine.dispose()


def test_quality_and_summary_preserve_missing_counts_and_exclude_future(db, tmp_path):
    ingest(request(), source(tmp_path, fixture_rows(3)), PriceRepository(db, tmp_path / "raw"))
    with TestClient(create_app(db)) as client:
        quality = client.get("/quality", params={**PARAMS}).json()
        assert quality["count"] == 1
        daily = client.get(
            "/summary/daily",
            params={"area": "DK2", "start_date": "2026-02-01", "end_date": "2026-02-02"},
        ).json()
        assert daily["items"][0]["missing"] == 93
        future = client.get(
            "/summary/daily",
            params={"area": "DK2", "start_date": "2100-01-01", "end_date": "2100-01-02"},
        ).json()
        assert future["items"][0]["missing"] == 0
