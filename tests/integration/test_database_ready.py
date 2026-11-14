"""S1 requires an actual PostgreSQL connection; unavailable configuration must fail."""

import os
from pathlib import Path

from dotenv import load_dotenv
from sqlalchemy import create_engine, text


def test_database_ready_executes_select_one():
    """Catch an absent/unreachable database or an incorrect PostgreSQL major version."""
    root = Path(__file__).resolve().parents[2]
    load_dotenv(root / ".env", override=False)
    # No default SQLite URL and no pytest.skip: a missing prerequisite is a real failure.
    database_url = os.environ["DATABASE_URL"]
    engine = create_engine(database_url, connect_args={"connect_timeout": 3})
    try:
        with engine.connect() as connection:
            assert connection.scalar(text("SELECT 1")) == 1
            version = int(connection.scalar(text("SHOW server_version_num")))
            assert 170000 <= version < 180000
    finally:
        engine.dispose()
