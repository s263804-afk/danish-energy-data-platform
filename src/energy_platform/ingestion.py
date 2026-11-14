import logging

from sqlalchemy.exc import SQLAlchemyError

from energy_platform.domain import FetchResult
from energy_platform.normalise import normalise_record
from energy_platform.quality import check_interval_completeness
from energy_platform.source import FetchError, decode_records

logger = logging.getLogger(__name__)


class IngestionError(RuntimeError):
    def __init__(self, code, run_id):
        super().__init__(code)
        self.code, self.run_id = code, str(run_id)


def ingest(request, source, repository):
    with repository.single_run():
        run = repository.start(request)
        try:
            try:
                fetched = source.fetch(request)
            except FetchError as exc:
                repository.capture(run, FetchResult(exc.content, exc.parameters, exc.status))
                raise
            repository.capture(run, fetched)
            unique = {}
            duplicates = 0
            for raw in decode_records(fetched.content):
                record = normalise_record(raw)
                if record.area != request.area or not (
                    request.start_utc <= record.interval_start_utc < request.end_utc
                ):
                    continue
                key = (record.area, record.interval_start_utc)
                if key in unique:
                    if unique[key].value_hash != record.value_hash:
                        raise IngestionError("CONFLICTING_SOURCE_DUPLICATE", run)
                    duplicates += 1
                unique[key] = record
            records = list(unique.values())
            issues = check_interval_completeness(records, request, 15)
            return repository.persist(run, records, duplicates, issues)
        except Exception as exc:
            code = (
                exc.code
                if isinstance(exc, (IngestionError, FetchError))
                else "DATABASE_ERROR"
                if isinstance(exc, SQLAlchemyError)
                else "INVALID_SOURCE_RECORD"
            )
            repository.fail(run, code)
            logger.warning("ingestion_failed run_id=%s error_code=%s", run, code)
            raise IngestionError(code, run) from exc
