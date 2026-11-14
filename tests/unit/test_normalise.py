from datetime import UTC, datetime
from decimal import Decimal
from zoneinfo import ZoneInfo

import pytest

from energy_platform.domain import FetchRequest
from energy_platform.normalise import normalise_record


def row(**changes):
    return {
        "TimeUTC": "2026-10-25T00:15:00",
        "TimeDK": "2026-10-25T02:15:00",
        "PriceArea": "DK2",
        "DayAheadPriceEUR": Decimal("-10.25"),
        "DayAheadPriceDKK": Decimal("-76.5"),
        **changes,
    }


def test_negative_price_and_source_timestamp_are_normalised_without_float():
    record = normalise_record(row())
    assert record.price_eur == Decimal("-10.250000")
    assert str(record.price_eur) == "-10.250000"
    assert record.interval_start_utc == datetime(2026, 10, 25, 0, 15, tzinfo=UTC)


@pytest.mark.parametrize(
    "changes",
    [
        {"DayAheadPriceEUR": None},
        {"DayAheadPriceEUR": Decimal("NaN")},
        {"DayAheadPriceEUR": Decimal("Infinity")},
        {"PriceArea": "DK3"},
        {"DayAheadPriceEUR": 0.1},
        {"TimeUTC": "not-a-date"},
        {"TimeUTC": "2026-10-25T00:15:01"},
        {"DayAheadPriceEUR": Decimal("1e20")},
    ],
)
def test_invalid_records_fail_explicitly(changes):
    with pytest.raises(ValueError):
        normalise_record(row(**changes))


def test_missing_field_is_rejected():
    raw = row()
    del raw["DayAheadPriceEUR"]
    with pytest.raises(ValueError):
        normalise_record(raw)


def test_request_normalises_ambiguous_local_bounds_before_comparing_them():
    zone = ZoneInfo("Europe/Copenhagen")
    request = FetchRequest(
        "DK2",
        datetime(2026, 10, 25, 2, 15, tzinfo=zone, fold=0),
        datetime(2026, 10, 25, 2, 15, tzinfo=zone, fold=1),
    )
    assert (request.end_utc - request.start_utc).total_seconds() == 3600


def test_round_half_even_and_value_hash_ignore_formatting():
    a = normalise_record(row(DayAheadPriceEUR=Decimal("1.2345665")))
    b = normalise_record(row(DayAheadPriceEUR="1.234566"))
    assert a.price_eur == Decimal("1.234566")
    assert a.value_hash == b.value_hash
    assert a.value_hash != normalise_record(row(DayAheadPriceEUR="1.234567")).value_hash


@pytest.mark.parametrize(
    "start,end",
    [
        (datetime(2026, 1, 1), datetime(2026, 1, 2, tzinfo=UTC)),
        (datetime(2026, 1, 2, tzinfo=UTC), datetime(2026, 1, 1, tzinfo=UTC)),
        (datetime(2025, 1, 1, tzinfo=UTC), datetime(2026, 2, 1, tzinfo=UTC)),
    ],
)
def test_request_rejects_naive_reversed_and_excessive_ranges(start, end):
    with pytest.raises(ValueError):
        FetchRequest("DK2", start, end)
