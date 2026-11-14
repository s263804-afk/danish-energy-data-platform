"""Bounded public API access and lossless capture of original page bodies."""

import base64
import json
import time
from datetime import UTC, datetime, timedelta
from datetime import time as midnight
from decimal import Decimal
from email.utils import parsedate_to_datetime
from pathlib import Path
from zoneinfo import ZoneInfo

import httpx

from energy_platform.config import SOURCE_URL
from energy_platform.domain import FetchResult


def decode_records(content: bytes) -> list[dict]:
    payload = json.loads(content, parse_float=Decimal)
    if "source_pages_base64" in payload:
        return [
            row
            for page in payload["source_pages_base64"]
            for row in decode_records(base64.b64decode(page, validate=True))
        ]
    if "source_pages" in payload:
        return [
            row
            for page in payload["source_pages"]
            for row in json.loads(page, parse_float=Decimal)["records"]
        ]
    records = payload["records"]
    if not isinstance(records, list):
        raise ValueError("Source records must be a list")
    return records


def capture_failed_pages(pages: list[bytes]) -> bytes:
    if len(pages) == 1:
        return pages[0]
    return json.dumps(
        {
            "source_pages_base64": [base64.b64encode(page).decode("ascii") for page in pages],
            "capture_state": "INCOMPLETE_OR_INVALID_SOURCE",
        }
    ).encode("utf-8")


class FetchError(RuntimeError):
    def __init__(self, code, content=b"", status=0, parameters=None):
        super().__init__(code)
        self.code, self.content, self.status = code, content, status
        self.parameters = parameters or {}


class SnapshotSource:
    def __init__(self, path):
        self.path = Path(path)

    def fetch(self, request):
        return FetchResult(self.path.read_bytes(), {"snapshot_file": self.path.name})


class PriceSource:
    def __init__(
        self,
        client=None,
        page_size=1000,
        sleep=time.sleep,
        max_wait=10,
        now=lambda: datetime.now(UTC),
    ):
        self.client = client
        self.page_size, self.sleep, self.max_wait, self.now = page_size, sleep, max_wait, now

    def _get(self, client, params):
        last = FetchError("SOURCE_UNAVAILABLE", parameters=params)
        for attempt in range(3):
            try:
                response = client.get(SOURCE_URL, params=params, timeout=30)
            except (httpx.TimeoutException, httpx.TransportError):
                last = FetchError("SOURCE_TRANSPORT_ERROR", parameters=params)
                if attempt < 2:
                    self.sleep(min(2**attempt, self.max_wait))
                continue
            if response.status_code < 400:
                return response
            last = FetchError(
                f"HTTP_{response.status_code}", response.content, response.status_code, params
            )
            if response.status_code != 429 and response.status_code < 500:
                raise last
            if attempt == 2:
                break
            delay = min(2**attempt, self.max_wait)
            header = response.headers.get("retry-after")
            if header:
                try:
                    delay = float(header)
                except ValueError:
                    try:
                        delay = (parsedate_to_datetime(header) - self.now()).total_seconds()
                    except (ValueError, TypeError, OverflowError):
                        delay = min(2**attempt, self.max_wait)
                if not 0 <= delay <= self.max_wait:
                    raise last
            self.sleep(delay)
        raise last

    def fetch(self, request):
        local = ZoneInfo("Europe/Copenhagen")
        start_date = request.start_utc.astimezone(local).date()
        end_local = request.end_utc.astimezone(local)
        end_date = end_local.date() + (
            timedelta(0) if end_local.time() == midnight() else timedelta(days=1)
        )
        params = {
            "start": start_date.isoformat(),
            "end": end_date.isoformat(),
            "filter": json.dumps({"PriceArea": [request.area]}),
            "sort": "TimeUTC asc,PriceArea asc",
            "limit": self.page_size,
            "offset": 0,
        }
        pages = []
        owned = self.client is None
        client = self.client or httpx.Client()
        try:
            # A v1 request is at most 366 days. The guard also bounds a malformed upstream loop.
            for _ in range(1000):
                try:
                    response = self._get(client, params)
                except FetchError as exc:
                    received = pages + ([exc.content] if exc.status else [])
                    raise FetchError(
                        exc.code,
                        capture_failed_pages(received),
                        exc.status,
                        {**params, "pages": len(received)},
                    ) from exc
                pages.append(response.content)
                try:
                    rows = decode_records(response.content)
                except (ValueError, TypeError, KeyError) as exc:
                    raise FetchError(
                        "INVALID_SOURCE_RECORD",
                        capture_failed_pages(pages),
                        response.status_code,
                        {**params, "pages": len(pages)},
                    ) from exc
                if len(rows) < self.page_size:
                    break
                params["offset"] += len(rows)
            else:
                raise FetchError("SOURCE_PAGE_LIMIT", capture_failed_pages(pages), 200, params)
            content = (
                pages[0]
                if len(pages) == 1
                else json.dumps(
                    {"source_pages": [page.decode("utf-8") for page in pages]}, ensure_ascii=False
                ).encode("utf-8")
            )
            return FetchResult(content, {**params, "pages": len(pages)})
        finally:
            if owned:
                client.close()
