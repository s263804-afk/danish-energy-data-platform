"""Completeness checks use UTC instants and Copenhagen civil-day boundaries."""

from datetime import UTC, date, datetime, time, timedelta
from zoneinfo import ZoneInfo

from energy_platform.domain import QualityIssue


def local_day_bounds(day: date):
    zone = ZoneInfo("Europe/Copenhagen")
    return (
        datetime.combine(day, time(), zone).astimezone(UTC),
        datetime.combine(day + timedelta(days=1), time(), zone).astimezone(UTC),
    )


def expected_intervals(request, cadence_minutes=15, expected_until=None):
    if cadence_minutes <= 0:
        raise ValueError("Cadence must be positive")
    step = cadence_minutes * 60
    now = expected_until or datetime.now(UTC)
    if now.tzinfo is None:
        raise ValueError("Expected-until must be aware")
    # Default policy: only elapsed intervals. Future published data may be loaded,
    # but is not diagnosed as missing unless a verified cutoff is explicitly supplied.
    cutoff = datetime.fromtimestamp((now.timestamp() // step) * step, UTC)
    end = min(request.end_utc, cutoff)
    epoch = request.start_utc.timestamp()
    first = datetime.fromtimestamp(-(-epoch // step) * step, UTC)
    values = []
    while first < end:
        values.append(first)
        first += timedelta(seconds=step)
    return values


def check_interval_completeness(records, request, cadence_minutes=15, expected_until=None):
    found = {r.interval_start_utc for r in records if r.area == request.area}
    return [
        QualityIssue(
            request.area,
            instant,
            "MISSING_INTERVAL",
            "WARNING",
            "No source record for an expected elapsed UTC interval",
        )
        for instant in expected_intervals(request, cadence_minutes, expected_until)
        if instant not in found
    ]
