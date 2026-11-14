from alembic import context
from sqlalchemy import text

from energy_platform.config import make_engine


def run():
    supplied = context.config.attributes.get("connection")
    if supplied is not None:
        schema = supplied.scalar(text("SELECT current_schema()"))
        context.configure(connection=supplied, target_metadata=None, version_table_schema=schema)
        with context.begin_transaction():
            context.run_migrations()
        return
    engine = make_engine()
    try:
        with engine.connect() as connection:
            context.configure(connection=connection, target_metadata=None)
            with context.begin_transaction():
                context.run_migrations()
    finally:
        engine.dispose()


run()
