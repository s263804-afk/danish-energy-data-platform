"""Immutable contracts shared by source, persistence and HTTP boundaries."""

import hashlib
from dataclasses import dataclass
from datetime import UTC, datetime, timedelta
from decimal import Decimal


@dataclass(frozen=True)
class FetchRequest:
    area: str
    start_utc: datetime
    end_utc: datetime

    def __post_init__(self):
        if self.area not in ("DK1", "DK2"):
            raise ValueError("Unsupported price area")
        if any(t.tzinfo is None or t.utcoffset() is None for t in (self.start_utc, self.end_utc)):
            raise ValueError("Aware timestamps are required")
        object.__setattr__(self, "start_utc", self.start_utc.astimezone(UTC))
        object.__setattr__(self, "end_utc", self.end_utc.astimezone(UTC))
        if not timedelta(0) < self.end_utc - self.start_utc <= timedelta(days=366):
            raise ValueError("Range must be positive and at most 366 days")


@dataclass(frozen=True)
class PriceRecord:
    area: str
    interval_start_utc: datetime
    price_eur: Decimal
    price_dkk: Decimal

    @property
    def value_hash(self) -> str:
        canonical = "|".join(
            [
                self.area,
                self.interval_start_utc.astimezone(UTC).isoformat(),
                format(self.price_eur, ".6f"),
                format(self.price_dkk, ".6f"),
            ]
        )
        return hashlib.sha256(canonical.encode("ascii")).hexdigest()


@dataclass(frozen=True)
class FetchResult:
    content: bytes
    parameters: dict
    status: int = 200


@dataclass(frozen=True)
class QualityIssue:
    area: str
    interval_start_utc: datetime
    rule_code: str
    severity: str
    details: str


@dataclass(frozen=True)
class IngestionResult:
    run_id: str
    status: str
    inserted: int = 0
    updated: int = 0
    unchanged: int = 0
    duplicates: int = 0
    issues: int = 0
