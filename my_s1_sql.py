import os
from pathlib import Path

from dotenv import load_dotenv
from sqlalchemy import create_engine, text

# Read the database configuration from the project's .env file.
root = Path(__file__).resolve().parent
load_dotenv(root / ".env")

# Configure the database connection.
engine = create_engine(
    os.environ["DATABASE_URL"],
    connect_args={"connect_timeout": 3},
)

# Send SQL to PostgreSQL and read the returned value.
with engine.connect() as connection:
    result = connection.scalar(text("SELECT 2"))
    print("Database returned:", result)

engine.dispose()
