from datetime import UTC, datetime

import httpx
import pytest

from energy_platform.domain import FetchRequest
from energy_platform.source import FetchError, PriceSource


def req():
    return FetchRequest("DK2", datetime(2026, 2, 1, tzinfo=UTC), datetime(2026, 2, 2, tzinfo=UTC))


@pytest.mark.parametrize("failure", ["timeout", 429, 503])
def test_persistent_failure_has_three_total_attempts(failure):
    calls, waits = [], []

    def response(request):
        calls.append(request)
        if failure == "timeout":
            raise httpx.ReadTimeout("deliberate test timeout", request=request)
        return httpx.Response(failure, headers={"Retry-After": "2"}, content=b"unavailable")

    source = PriceSource(
        client=httpx.Client(transport=httpx.MockTransport(response)), sleep=waits.append
    )
    with pytest.raises(FetchError):
        source.fetch(req())
    assert len(calls) == 3
    assert waits == ([1, 2] if failure == "timeout" else [2, 2])


def test_success_after_transient_error_and_retry_after_is_honoured():
    calls, waits = [], []

    def response(request):
        calls.append(request)
        return (
            httpx.Response(429, headers={"Retry-After": "3"})
            if len(calls) == 1
            else httpx.Response(200, json={"records": []})
        )

    source = PriceSource(
        client=httpx.Client(transport=httpx.MockTransport(response)), sleep=waits.append
    )
    source.fetch(req())
    assert len(calls) == 2
    assert waits == [3]


def test_retry_after_exceeding_wait_budget_is_reported_without_long_sleep():
    waits = []
    source = PriceSource(
        client=httpx.Client(
            transport=httpx.MockTransport(
                lambda r: httpx.Response(429, headers={"Retry-After": "99999"})
            )
        ),
        sleep=waits.append,
        max_wait=10,
    )
    with pytest.raises(FetchError):
        source.fetch(req())
    assert waits == []
