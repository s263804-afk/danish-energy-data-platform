"""Explicit local commands; credentials and database exception strings are never printed."""

import argparse
import json
from dataclasses import asdict
from datetime import UTC, date, datetime
from pathlib import Path

from alembic import command
from alembic.config import Config

from energy_platform.config import ROOT, make_engine
from energy_platform.domain import FetchRequest
from energy_platform.ingestion import IngestionError, ingest
from energy_platform.repository import ConcurrentRunError, PriceRepository
from energy_platform.source import PriceSource, SnapshotSource


def migrate(engine):
    cfg = Config(str(ROOT / "alembic.ini"))
    with engine.begin() as conn:
        cfg.attributes["connection"] = conn
        command.upgrade(cfg, "head")


def main():
    parser = argparse.ArgumentParser(prog="energy")
    sub = parser.add_subparsers(dest="command", required=True)
    sub.add_parser("init-db")
    load = sub.add_parser("ingest")
    load.add_argument("--area", choices=["DK1", "DK2"], required=True)
    load.add_argument("--start", required=True)
    load.add_argument("--end", required=True)
    load.add_argument("--snapshot", type=Path)
    quality = sub.add_parser("quality")
    quality.add_argument("--area", choices=["DK1", "DK2"], required=True)
    quality.add_argument("--start", required=True)
    quality.add_argument("--end", required=True)
    serve = sub.add_parser("serve")
    serve.add_argument("--port", type=int, default=8000)
    demo = sub.add_parser("demo")
    demo.add_argument("--offline", action="store_true", required=True)
    args = parser.parse_args()
    engine = make_engine()
    try:
        if args.command == "init-db":
            migrate(engine)
            print(json.dumps({"migrations": "head"}))
        elif args.command == "ingest":
            try:
                request = FetchRequest(
                    args.area,
                    datetime.fromisoformat(args.start.replace("Z", "+00:00")),
                    datetime.fromisoformat(args.end.replace("Z", "+00:00")),
                )
            except ValueError as exc:
                parser.error(str(exc))
            source = SnapshotSource(args.snapshot) if args.snapshot else PriceSource()
            result = ingest(request, source, PriceRepository(engine, ROOT / "data/raw"))
            print(json.dumps(asdict(result)))
        elif args.command == "quality":
            from sqlalchemy import text

            from energy_platform.domain import PriceRecord
            from energy_platform.quality import check_interval_completeness

            request = FetchRequest(
                args.area,
                datetime.fromisoformat(args.start.replace("Z", "+00:00")),
                datetime.fromisoformat(args.end.replace("Z", "+00:00")),
            )
            with engine.connect() as conn:
                rows = conn.execute(
                    text("""
                    SELECT area,interval_start_utc,price_eur,price_dkk FROM prices
                    WHERE area=:area AND interval_start_utc>=:start AND interval_start_utc<:end
                """),
                    {"area": request.area, "start": request.start_utc, "end": request.end_utc},
                )
                issues = check_interval_completeness([PriceRecord(*r) for r in rows], request)
            print(
                json.dumps(
                    {"count": len(issues), "items": [asdict(i) for i in issues]}, default=str
                )
            )
        elif args.command == "serve":
            import uvicorn

            uvicorn.run("energy_platform.api:app", host="127.0.0.1", port=args.port)
        elif args.command == "demo":
            import hashlib

            from energy_platform.quality import local_day_bounds
            from energy_platform.queries import daily_summary

            migrate(engine)
            snapshot = ROOT / "tests/fixtures/energinet_october_2026.json"
            summary = {
                "mode": "offline_real_capture",
                "executed_at_utc": datetime.now(UTC).isoformat(),
                "source": "Energinet (www.energidataservice.dk), CC BY 4.0",
                "source_sha256": hashlib.sha256(snapshot.read_bytes()).hexdigest(),
                "local_range": "[2026-10-01,2026-11-01)",
                "areas": {},
            }
            for area in ("DK1", "DK2"):
                request = FetchRequest(
                    area,
                    local_day_bounds(date(2026, 10, 1))[0],
                    local_day_bounds(date(2026, 11, 1))[0],
                )
                repo = PriceRepository(engine, ROOT / "data/raw")
                first = ingest(request, SnapshotSource(snapshot), repo)
                repeat = ingest(request, SnapshotSource(snapshot), repo)
                days = daily_summary(engine, area, date(2026, 10, 1), date(2026, 11, 1))
                count = sum(day["count"] for day in days)
                missing = sum(day["missing"] for day in days)
                if count != 2980 or missing or repeat.inserted or repeat.updated:
                    raise RuntimeError("Offline demo invariants failed")
                summary["areas"][area] = {
                    "first": asdict(first),
                    "repeat": asdict(repeat),
                    "historical_days": 31,
                    "rows": count,
                    "missing": missing,
                }
            summary["verdict"] = "PASS"
            output = ROOT / "reports/demo/software-demo.json"
            output.parent.mkdir(parents=True, exist_ok=True)
            output.write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
            print(json.dumps(summary, indent=2))
    except IngestionError as exc:
        print(json.dumps({"status": "FAILED", "error_code": exc.code, "run_id": exc.run_id}))
        raise SystemExit(1) from None
    except ConcurrentRunError:
        print(json.dumps({"status": "REJECTED", "error_code": "CONCURRENT_RUN"}))
        raise SystemExit(2) from None
    finally:
        engine.dispose()


if __name__ == "__main__":
    main()
