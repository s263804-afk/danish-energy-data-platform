"""Capture a small real source response for S1 inspection, not a production importer.

Energinet interprets start/end as Danish local time. Returned TimeUTC is UTC,
even though the source omits Z. See docs/source-contract.md before reusing this.
"""

import argparse
import hashlib
import json
from datetime import UTC, datetime
from decimal import Decimal
from pathlib import Path

import httpx

SOURCE_URL = "https://api.energidataservice.dk/dataset/DayAheadPrices"


def build_params(area: str, start_local: str, end_local: str, limit: int, offset: int) -> dict:
    """Keep filter, order and offset explicit so different pages are comparable."""
    return {
        "start": start_local,
        "end": end_local,
        "filter": json.dumps({"PriceArea": [area]}, separators=(",", ":")),
        "sort": "TimeUTC asc,PriceArea asc",
        "limit": limit,
        "offset": offset,
    }


def decode_payload(content: bytes) -> dict:
    """Decode JSON decimal literals directly to Decimal, without binary floating point."""
    return json.loads(content, parse_float=Decimal)


def save_capture(path: Path, content: bytes) -> None:
    """Save original response bytes; exclusive creation refuses accidental overwrite."""
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("xb") as snapshot:
        snapshot.write(content)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--area", choices=("DK1", "DK2"), default="DK2")
    parser.add_argument("--start-local", default="2026-11-01T00:00")
    parser.add_argument("--end-local", default="2026-11-01T01:00")
    parser.add_argument("--limit", type=int, default=4)
    parser.add_argument("--offset", type=int, default=0)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    if not 1 <= args.limit <= 100 or args.offset < 0:
        parser.error("S1 probes require limit 1..100 and a nonnegative offset")
    if args.output.exists() or args.output.with_suffix(".metadata.json").exists():
        raise FileExistsError(
            f"Choose a new capture path; existing evidence is preserved: {args.output}"
        )
    params = build_params(args.area, args.start_local, args.end_local, args.limit, args.offset)
    # Source failures stay visible. Bounded ingestion retries are implemented in S5.
    response = httpx.get(SOURCE_URL, params=params, timeout=30)
    save_capture(args.output, response.content)
    payload = decode_payload(response.content) if response.is_success else None
    metadata = {
        "provenance": "LIVE_CAPTURE",
        "source": "Energinet / Energi Data Service, DayAheadPrices",
        "attribution": "Source: Energinet (www.energidataservice.dk).",
        "license": "CC-BY-4.0",
        "requested_url": str(response.request.url),
        "request_parameters": params,
        "retrieved_at_utc": datetime.now(UTC).isoformat(),
        "http_status": response.status_code,
        "response_date_header": response.headers.get("date"),
        "retry_after": response.headers.get("retry-after"),
        "sha256": hashlib.sha256(response.content).hexdigest(),
        "row_count": len(payload["records"]) if payload is not None else None,
        "scope": "S1 source inspection only; not an ingestion/database/API integration result",
        "modified": False,
    }
    save_capture(
        args.output.with_suffix(".metadata.json"),
        json.dumps(metadata, indent=2).encode("utf-8") + b"\n",
    )
    response.raise_for_status()
    print(f"Saved {len(payload['records'])} real {args.area} records to {args.output}")
    if payload["records"]:
        print(json.dumps(payload["records"][0], default=str, indent=2))
    print("No price rows have been imported into PostgreSQL by this source probe.")


if __name__ == "__main__":
    main()
