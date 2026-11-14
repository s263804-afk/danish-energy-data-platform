from datetime import UTC, date, datetime
from decimal import Decimal

import pytest

from energy_platform.domain import FetchRequest, PriceRecord
from energy_platform.quality import (
    check_interval_completeness,
    expected_intervals,
    local_day_bounds,
)


@pytest.mark.parametrize(
    "day,count",
    [
        (date(2026, 2, 1), 96),
        (date(2026, 3, 29), 92),
        (date(2026, 10, 25), 100),
    ],
)
def test_local_civil_day_counts_match_dst(day, count):
    start, end = local_day_bounds(day)
    assert len(expected_intervals(FetchRequest("DK2", start, end), 15)) == count


def test_exact_missing_interval_and_negative_price_accepted():
    start, end = local_day_bounds(date(2026, 2, 1))
    request = FetchRequest("DK2", start, end)
    times = expected_intervals(request, 15)
    rows = [PriceRecord("DK2", t, Decimal("-10"), Decimal("-75")) for t in times if t != times[27]]
    issues = check_interval_completeness(rows, request, 15)
    assert len(issues) == 1
    assert issues[0].interval_start_utc == times[27]
    assert issues[0].rule_code == "MISSING_INTERVAL"


def test_unpublished_future_is_not_reported_as_missing():
    request = FetchRequest(
        "DK2", datetime(2027, 1, 1, tzinfo=UTC), datetime(2027, 1, 2, tzinfo=UTC)
    )
    assert (
        check_interval_completeness(
            [], request, 15, expected_until=datetime(2026, 11, 13, tzinfo=UTC)
        )
        == []
    )
