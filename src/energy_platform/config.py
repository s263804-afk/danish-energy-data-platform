import os
from datetime import UTC, datetime
from pathlib import Path

from dotenv import load_dotenv
from sqlalchemy import create_engine

ROOT = Path(__file__).resolve().parents[2]
SOURCE_URL = "https://api.energidataservice.dk/dataset/DayAheadPrices"
CADENCE_MINUTES = 15
MODERN_DATA_START_UTC = datetime(2025, 9, 30, 22, tzinfo=UTC)


def make_engine(url: str | None = None):
    load_dotenv(ROOT / ".env")
    selected = url or os.environ["DATABASE_URL"]
    return create_engine(selected, connect_args={"connect_timeout": 3}, pool_pre_ping=True)
