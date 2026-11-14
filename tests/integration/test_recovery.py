import pytest
from sqlalchemy import text

from energy_platform.ingestion import IngestionError, ingest
from energy_platform.repository import ConcurrentRunError, PriceRepository
from energy_platform.source import FetchError
from tests.integration.test_ingestion import counts, fixture_rows, request, source


def test_database_failure_rolls_back_facts_but_failed_audit_survives(db, tmp_path):
    with db.begin() as conn:
        conn.execute(
            text("""
          CREATE FUNCTION reject_second() RETURNS trigger LANGUAGE plpgsql AS $$
          BEGIN
            IF NEW.interval_start_utc='2026-02-01T00:15Z'::timestamptz THEN
              RAISE EXCEPTION 'deliberate integration-test failure';
            END IF;
            RETURN NEW;
          END $$;
          CREATE TRIGGER fail_one BEFORE INSERT ON prices
            FOR EACH ROW EXECUTE FUNCTION reject_second();
        """)
        )
    with pytest.raises(IngestionError) as failure:
        ingest(request(), source(tmp_path, fixture_rows()), PriceRepository(db, tmp_path / "raw"))
    assert failure.value.code == "DATABASE_ERROR"
    assert counts(db) == (0, 0, 1)
    with db.connect() as conn:
        assert conn.scalar(text("SELECT status FROM ingestion_runs")) == "FAILED"
        assert conn.scalar(text("SELECT count(*) FROM raw_snapshots")) == 1
        assert conn.scalar(text("SELECT count(*) FROM quality_issues")) == 0
    assert len(list((tmp_path / "raw").glob("*.json"))) == 1


def test_concurrent_import_is_rejected_without_harming_first_run(db, tmp_path):
    repo = PriceRepository(db, tmp_path / "raw")
    with repo.single_run(), pytest.raises(ConcurrentRunError):
        ingest(request(), source(tmp_path, fixture_rows()), repo)
    result = ingest(request(), source(tmp_path, fixture_rows()), repo)
    assert result.inserted == 96
    assert counts(db) == (96, 0, 1)


def test_fetch_failure_is_audited_and_error_body_retained(db, tmp_path):
    class FailedSource:
        def fetch(self, request):
            raise FetchError("HTTP_503", b"source down", 503, {"test": "synthetic"})

    with pytest.raises(IngestionError):
        ingest(request(), FailedSource(), PriceRepository(db, tmp_path / "raw"))
    assert counts(db) == (0, 0, 1)
    with db.connect() as conn:
        assert conn.scalar(text("SELECT http_status FROM raw_snapshots")) == 503
