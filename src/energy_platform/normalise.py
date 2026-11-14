"""Source JSON numbers must be parsed as Decimal before this boundary."""

from datetime import UTC, datetime
from decimal import ROUND_HALF_EVEN, Decimal, InvalidOperation

from energy_platform.domain import PriceRecord


def price_decimal(value) -> Decimal:
    if isinstance(value, (bool, float)) or value is None:
        raise ValueError("Price must be a finite Decimal/string, not a binary float")
    try:
        number = Decimal(value)
        if not number.is_finite() or abs(number) >= Decimal("1e12"):
            raise ValueError("Price outside numeric(18,6)")
        result = number.quantize(Decimal("0.000001"), rounding=ROUND_HALF_EVEN)
        if abs(result) >= Decimal("1e12"):
            raise ValueError("Rounded price outside numeric(18,6)")
        # Canonicalise signed zero so equivalent business values have the same hash.
        return abs(result) if result == 0 else result
    except (InvalidOperation, TypeError) as exc:
        raise ValueError("Invalid decimal price") from exc


def normalise_record(raw: dict) -> PriceRecord:
    try:
        area = raw["PriceArea"]
        if area not in ("DK1", "DK2"):
            raise ValueError("Unsupported price area")
        timestamp = datetime.fromisoformat(raw["TimeUTC"].replace("Z", "+00:00"))
        # Official S1 metadata defines a suffix-free TimeUTC as UTC.
        timestamp = timestamp.replace(tzinfo=UTC) if timestamp.tzinfo is None else timestamp
        timestamp = timestamp.astimezone(UTC)
        if timestamp.minute % 15 or timestamp.second or timestamp.microsecond:
            raise ValueError("Timestamp is not on a 15-minute interval boundary")
        return PriceRecord(
            area,
            timestamp,
            price_decimal(raw["DayAheadPriceEUR"]),
            price_decimal(raw["DayAheadPriceDKK"]),
        )
    except (KeyError, AttributeError, TypeError) as exc:
        raise ValueError("Missing or malformed source field") from exc
