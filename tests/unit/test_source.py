import json
from datetime import UTC, datetime
from decimal import Decimal

import httpx

from energy_platform.domain import FetchRequest
from energy_platform.source import PriceSource, decode_records


def test_paging_does_not_use_page_sized_total_as_available_count():
    offsets = []

    def response(request):
        offset = int(request.url.params["offset"])
        offsets.append(offset)
        records = [
            {
                "TimeUTC": f"2026-11-01T00:{minute}:00",
                "PriceArea": "DK2",
                "DayAheadPriceEUR": -10.25,
                "DayAheadPriceDKK": -76.5,
            }
            for minute in (["00", "15"] if offset == 0 else ["30", "45"] if offset == 2 else [])
        ]
        return httpx.Response(200, content=json.dumps({"total": len(records), "records": records}))

    client = httpx.Client(transport=httpx.MockTransport(response))
    req = FetchRequest(
        "DK2", datetime(2026, 11, 1, tzinfo=UTC), datetime(2026, 11, 1, 1, tzinfo=UTC)
    )
    result = PriceSource(client=client, page_size=2).fetch(req)
    rows = decode_records(result.content)
    assert offsets == [0, 2, 4]
    assert len(rows) == 4
    assert rows[0]["DayAheadPriceEUR"] == Decimal("-10.25")
    assert len(json.loads(result.content)["source_pages"]) == 3
