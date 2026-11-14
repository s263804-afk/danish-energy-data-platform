"""Offline contract checks for the S1 probe, independent of the live source."""

import json
import sys
from decimal import Decimal

import httpx
import pytest

from scripts.source_probe import build_params, decode_payload, main, save_capture


def test_probe_builds_explicit_area_order_and_offset():
    params = build_params("DK2", "2026-11-01T00:00", "2026-11-01T01:00", 2, 2)
    assert json.loads(params["filter"]) == {"PriceArea": ["DK2"]}
    assert params["sort"] == "TimeUTC asc,PriceArea asc"
    assert params["offset"] == 2
    assert params["limit"] == 2
    assert params["start"] == "2026-11-01T00:00"
    assert params["end"] == "2026-11-01T01:00"


def test_probe_keeps_original_decimal_number_without_float_roundtrip():
    payload = decode_payload(b'{"records":[{"DayAheadPriceEUR":-10.123456}]}')
    assert payload["records"][0]["DayAheadPriceEUR"] == Decimal("-10.123456")
    assert isinstance(payload["records"][0]["DayAheadPriceEUR"], Decimal)


def test_capture_preserves_raw_bytes_and_cannot_overwrite(tmp_path):
    raw = b'{ "records": [], "dataset": "DayAheadPrices" }\n'
    path = tmp_path / "probe.json"
    save_capture(path, raw)
    assert path.read_bytes() == raw
    with pytest.raises(FileExistsError):
        save_capture(path, b"changed")
    assert path.read_bytes() == raw


def test_failed_http_probe_preserves_response_and_status_without_retry(tmp_path, monkeypatch):
    """Catch discarded 429 evidence or a probe that retries against source rate limits."""
    output = tmp_path / "rate-limit.json"
    calls = []

    def rate_limited_get(url, **kwargs):
        calls.append(url)
        return httpx.Response(
            429,
            request=httpx.Request("GET", url, params=kwargs["params"]),
            headers={"Retry-After": "60"},
            content=b'{"message":"rate limit"}',
        )

    monkeypatch.setattr(httpx, "get", rate_limited_get)
    monkeypatch.setattr(sys, "argv", ["source_probe.py", "--output", str(output)])
    with pytest.raises(httpx.HTTPStatusError):
        main()
    assert output.read_bytes() == b'{"message":"rate limit"}'
    metadata = json.loads(output.with_suffix(".metadata.json").read_text())
    assert metadata["http_status"] == 429
    assert metadata["retry_after"] == "60"
    assert metadata["row_count"] is None
    assert len(calls) == 1


def test_existing_capture_is_rejected_before_any_network_request(tmp_path, monkeypatch):
    """Catch a repeated probe that needlessly contacts the source before refusing overwrite."""
    output = tmp_path / "existing.json"
    output.write_bytes(b"original bytes")

    def unexpected_request(*args, **kwargs):
        raise AssertionError("The source must not be called for an existing output path")

    monkeypatch.setattr(httpx, "get", unexpected_request)
    monkeypatch.setattr(sys, "argv", ["source_probe.py", "--output", str(output)])
    with pytest.raises(FileExistsError):
        main()
    assert output.read_bytes() == b"original bytes"
