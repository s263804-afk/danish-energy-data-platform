"""Core traceability schema; SQL stays visible for learning."""

from alembic import op

revision = "0001_core"
down_revision = None


def upgrade():
    op.execute("""
    CREATE TABLE raw_snapshots (
        id uuid PRIMARY KEY, fetched_at timestamptz NOT NULL DEFAULT now(),
        parameters jsonb NOT NULL, sha256 text NOT NULL, path text NOT NULL,
        http_status integer NOT NULL
    )""")
    op.execute("""
    CREATE TABLE ingestion_runs (
        id uuid PRIMARY KEY, area text NOT NULL CHECK (area IN ('DK1','DK2')),
        start_utc timestamptz NOT NULL, end_utc timestamptz NOT NULL,
        started_at timestamptz NOT NULL DEFAULT now(), finished_at timestamptz,
        status text NOT NULL CHECK (status IN ('RUNNING','SUCCEEDED','FAILED')),
        inserted integer NOT NULL DEFAULT 0, updated integer NOT NULL DEFAULT 0,
        unchanged integer NOT NULL DEFAULT 0, duplicates integer NOT NULL DEFAULT 0,
        error_code text, snapshot_id uuid REFERENCES raw_snapshots(id),
        CHECK (end_utc > start_utc)
    )""")
    op.execute("""
    CREATE TABLE prices (
        area text NOT NULL CHECK (area IN ('DK1','DK2')),
        interval_start_utc timestamptz NOT NULL,
        price_eur numeric(18,6) NOT NULL CHECK (price_eur <> 'NaN'::numeric),
        price_dkk numeric(18,6) NOT NULL CHECK (price_dkk <> 'NaN'::numeric),
        value_hash text NOT NULL, latest_run_id uuid NOT NULL REFERENCES ingestion_runs(id),
        PRIMARY KEY(area,interval_start_utc)
    )""")
    op.execute("""
    CREATE TABLE price_versions (
        id bigserial PRIMARY KEY, area text NOT NULL, interval_start_utc timestamptz NOT NULL,
        old_eur numeric(18,6) NOT NULL, old_dkk numeric(18,6) NOT NULL,
        new_eur numeric(18,6) NOT NULL, new_dkk numeric(18,6) NOT NULL,
        run_id uuid NOT NULL REFERENCES ingestion_runs(id),
        observed_at timestamptz NOT NULL DEFAULT now(),
        FOREIGN KEY(area,interval_start_utc) REFERENCES prices(area,interval_start_utc)
    )""")
    op.execute("""
    CREATE TABLE quality_issues (
        id bigserial PRIMARY KEY, run_id uuid NOT NULL REFERENCES ingestion_runs(id),
        area text NOT NULL, interval_start_utc timestamptz NOT NULL,
        rule_code text NOT NULL, severity text NOT NULL, details text NOT NULL,
        UNIQUE(run_id,area,interval_start_utc,rule_code)
    )""")


def downgrade():
    for table in ["quality_issues", "price_versions", "prices", "ingestion_runs", "raw_snapshots"]:
        op.execute(f"DROP TABLE {table}")
