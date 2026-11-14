from datetime import date
from decimal import Decimal

from sqlalchemy import text

from energy_platform.ingestion import ingest
from energy_platform.queries import daily_summary, gap_rows, moving_average_rows
from energy_platform.repository import PriceRepository
from tests.integration.test_ingestion import fixture_rows, request, source


def test_join_cte_aggregate_and_window_have_checked_answers(db, tmp_path):
    rows = fixture_rows(3)
    for row, value in zip(rows, ["-10", "10", "20"], strict=True):
        row["DayAheadPriceEUR"] = value
    repo = PriceRepository(db, tmp_path / "raw")
    ingest(request(), source(tmp_path, rows), repo)
    summary = daily_summary(db, "DK2", date(2026, 2, 1), date(2026, 2, 2))[0]
    assert summary["count"] == 3
    assert summary["min_eur"] == -10
    assert summary["max_eur"] == 20
    assert abs(summary["mean_eur"] - Decimal(20) / 3) < Decimal("1e-12")
    assert summary["missing"] == 93
    averages = moving_average_rows(db, request())
    assert [r["moving_mean"] for r in averages[:2]] == [-10, 0]
    assert abs(averages[2]["moving_mean"] - Decimal(20) / 3) < Decimal("1e-12")
    with db.connect() as conn:
        assert (
            conn.scalar(
                text("""
            SELECT count(*) FROM prices p JOIN ingestion_runs r ON r.id=p.latest_run_id
            WHERE r.status='SUCCEEDED'
        """)
            )
            == 3
        )


def test_lag_finds_real_gap(db, tmp_path):
    rows = fixture_rows(4)
    del rows[1]
    ingest(request(), source(tmp_path, rows), PriceRepository(db, tmp_path / "raw"))
    gaps = gap_rows(db, request())
    assert len(gaps) == 1
    assert gaps[0]["gap_minutes"] == 30
