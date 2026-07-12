import uuid

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db import engine
from app.preflight.jobs import PreflightJob, PreflightJobService
from app.preflight.providers.mock import MockOcrProvider


class TimeoutProvider:
    name = "timeout"

    def extract(self, document_id, content):
        raise TimeoutError("provider timeout")


def test_successful_job_persists_candidates(client):
    document_id = uuid.uuid4()
    with Session(engine) as session:
        job = PreflightJobService(session).run(document_id, b"synthetic", MockOcrProvider())
        saved = session.scalar(select(PreflightJob).where(PreflightJob.id == job.id))

        assert saved.status == "succeeded"
        assert saved.candidates[0].field_path == "directors[0].document_number"
        assert saved.candidates[0].provider == "mock-ocr"


def test_timeout_job_is_failed_and_retryable(client):
    with Session(engine) as session:
        job = PreflightJobService(session).run(uuid.uuid4(), b"synthetic", TimeoutProvider())

        assert job.status == "failed"
        assert job.retryable is True
        assert job.error_code == "provider_timeout"
