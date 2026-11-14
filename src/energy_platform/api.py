"""Local read API with bound SQL, strict time ranges and signed cursors."""

import base64
import binascii
import hashlib
import hmac
import json
import secrets
from collections.abc import Mapping
from datetime import UTC, date, datetime
from decimal import Decimal
from typing import Literal
from uuid import UUID

from fastapi import FastAPI, HTTPException, Query
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError

from energy_platform.config import make_engine
from energy_platform.domain import FetchRequest, PriceRecord
from energy_platform.quality import check_interval_completeness
from energy_platform.queries import daily_summary


def serialise(value):
    if isinstance(value, Mapping):
        return {k: serialise(v) for k, v in value.items()}
    if isinstance(value, (list, tuple)):
        return [serialise(v) for v in value]
    if isinstance(value, (Decimal, UUID)):
        return str(value)
    if isinstance(value, (date, datetime)):
        return value.isoformat()
    return value


def checked_request(area, start, end):
    try:
        return FetchRequest(area, start, end)
    except ValueError as exc:
        raise HTTPException(422, str(exc)) from None


def create_app(engine=None, now=lambda: datetime.now(UTC)):
    engine = engine if engine is not None else make_engine()
    app = FastAPI(title="Danish Energy Data Reliability Platform", version="1.0.0")
    signing_key = secrets.token_bytes(32)

    def encode_cursor(request, instant):
        payload = json.dumps(
            [
                request.area,
                request.start_utc.isoformat(),
                request.end_utc.isoformat(),
                instant.isoformat(),
            ],
            separators=(",", ":"),
        ).encode()
        signature = hmac.new(signing_key, payload, hashlib.sha256).digest()
        return base64.urlsafe_b64encode(payload + signature).decode()

    def decode_cursor(cursor, request):
        try:
            if len(cursor) > 2048:
                raise ValueError
            decoded = base64.b64decode(cursor, altchars=b"-_", validate=True)
            payload, signature = decoded[:-32], decoded[-32:]
            if not hmac.compare_digest(
                hmac.new(signing_key, payload, hashlib.sha256).digest(), signature
            ):
                raise ValueError
            parts = json.loads(payload)
            if (
                parts[:3]
                != [request.area, request.start_utc.isoformat(), request.end_utc.isoformat()]
                or len(parts) != 4
            ):
                raise ValueError
            instant = datetime.fromisoformat(parts[3])
            if instant.tzinfo is None or not request.start_utc <= instant < request.end_utc:
                raise ValueError
            return instant
        except (ValueError, TypeError, IndexError, binascii.Error):
            raise HTTPException(422, "Invalid or mismatched cursor") from None

    @app.get("/health")
    def health():
        return {"status": "ok"}

    @app.get("/ready")
    def ready():
        try:
            with engine.connect() as conn:
                if conn.scalar(text("SELECT 1")) != 1:
                    raise ValueError
                revision = conn.scalar(text("SELECT version_num FROM alembic_version"))
                if revision != "0001_core":
                    raise ValueError
                conn.execute(
                    text("""
                    SELECT p.area,r.id,s.id,v.id,q.id FROM prices p
                    LEFT JOIN ingestion_runs r ON false LEFT JOIN raw_snapshots s ON false
                    LEFT JOIN price_versions v ON false LEFT JOIN quality_issues q ON false LIMIT 0
                """)
                )
            return {"ready": True, "revision": revision}
        except (SQLAlchemyError, ValueError):
            raise HTTPException(503, "Database or migrations not ready") from None

    @app.get("/prices")
    def prices(
        area: Literal["DK1", "DK2"],
        start: datetime,
        end: datetime,
        limit: int = Query(100, ge=1, le=1000),
        cursor: str | None = None,
    ):
        request = checked_request(area, start, end)
        after = decode_cursor(cursor, request) if cursor is not None else None
        clause = "AND interval_start_utc>:after" if after else ""
        try:
            with engine.connect() as conn:
                rows = list(
                    conn.execute(
                        text(f"""
                    SELECT area,interval_start_utc,price_eur,price_dkk,latest_run_id
                    FROM prices WHERE area=:area AND interval_start_utc>=:start
                    AND interval_start_utc<:end {clause}
                    ORDER BY interval_start_utc ASC LIMIT :limit
                """),
                        {
                            "area": area,
                            "start": request.start_utc,
                            "end": request.end_utc,
                            "after": after,
                            "limit": limit + 1,
                        },
                    ).mappings()
                )
        except SQLAlchemyError:
            raise HTTPException(503, "Database unavailable") from None
        next_cursor = (
            encode_cursor(request, rows[limit - 1]["interval_start_utc"])
            if (len(rows) > limit)
            else None
        )
        items = serialise(rows[:limit])
        return {"items": items, "count": len(items), "next_cursor": next_cursor}

    @app.get("/runs/{run_id}")
    def run_status(run_id: UUID):
        try:
            with engine.connect() as conn:
                row = (
                    conn.execute(
                        text("""
                    SELECT r.*,s.sha256 AS snapshot_sha256,s.http_status
                    FROM ingestion_runs r LEFT JOIN raw_snapshots s ON s.id=r.snapshot_id
                    WHERE r.id=:id
                """),
                        {"id": run_id},
                    )
                    .mappings()
                    .first()
                )
        except SQLAlchemyError:
            raise HTTPException(503, "Database unavailable") from None
        if row is None:
            raise HTTPException(404, "Run not found")
        return serialise(row)

    @app.get("/quality")
    def quality(area: Literal["DK1", "DK2"], start: datetime, end: datetime):
        request = checked_request(area, start, end)
        try:
            with engine.connect() as conn:
                rows = conn.execute(
                    text("""
                    SELECT area,interval_start_utc,price_eur,price_dkk FROM prices
                    WHERE area=:area AND interval_start_utc>=:start AND interval_start_utc<:end
                """),
                    {"area": area, "start": request.start_utc, "end": request.end_utc},
                ).all()
        except SQLAlchemyError:
            raise HTTPException(503, "Database unavailable") from None
        from dataclasses import asdict

        issues = check_interval_completeness(
            [PriceRecord(*row) for row in rows], request, expected_until=now()
        )
        return {
            "items": serialise([asdict(issue) for issue in issues]),
            "count": len(issues),
            "policy": "elapsed_intervals_only",
        }

    @app.get("/summary/daily")
    def summary(area: Literal["DK1", "DK2"], start_date: date, end_date: date):
        if not 0 < (end_date - start_date).days <= 366:
            raise HTTPException(422, "Date range must be positive and at most 366 days")
        try:
            items = daily_summary(engine, area, start_date, end_date, expected_until=now())
        except SQLAlchemyError:
            raise HTTPException(503, "Database unavailable") from None
        return {"items": serialise(items), "timezone": "Europe/Copenhagen"}

    return app


app = create_app()
