import uuid
from datetime import UTC, datetime

from sqlalchemy import Boolean, DateTime, ForeignKey, String, Text
from sqlalchemy.orm import Mapped, Session, mapped_column, relationship

from app.db import Base
from app.preflight.providers.base import DocumentProvider


class PreflightJob(Base):
    __tablename__ = "preflight_jobs"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    document_id: Mapped[uuid.UUID] = mapped_column(index=True)
    provider: Mapped[str] = mapped_column(String(80))
    status: Mapped[str] = mapped_column(String(30), default="queued", index=True)
    retryable: Mapped[bool] = mapped_column(Boolean, default=False)
    error_code: Mapped[str | None] = mapped_column(String(80), nullable=True)
    error_message: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(UTC))
    completed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    candidates: Mapped[list["CandidateRecord"]] = relationship(cascade="all, delete-orphan", lazy="selectin")
    findings: Mapped[list["FindingRecord"]] = relationship(cascade="all, delete-orphan", lazy="selectin")


class CandidateRecord(Base):
    __tablename__ = "field_candidates"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    job_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("preflight_jobs.id", ondelete="CASCADE"), index=True)
    provider: Mapped[str] = mapped_column(String(80))
    field_path: Mapped[str] = mapped_column(String(240), index=True)
    value: Mapped[str] = mapped_column(Text)
    confidence: Mapped[float]
    document_id: Mapped[uuid.UUID]
    page: Mapped[int]


class FindingRecord(Base):
    __tablename__ = "review_findings"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    job_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("preflight_jobs.id", ondelete="CASCADE"), index=True)
    code: Mapped[str] = mapped_column(String(100), index=True)
    severity: Mapped[str] = mapped_column(String(20))
    message: Mapped[str] = mapped_column(Text)


class PreflightJobService:
    def __init__(self, session: Session):
        self.session = session

    def run(self, document_id: uuid.UUID, content: bytes, provider: DocumentProvider) -> PreflightJob:
        job = PreflightJob(document_id=document_id, provider=provider.name, status="running")
        self.session.add(job)
        self.session.flush()
        try:
            result = provider.extract(str(document_id), content)
            job.candidates = [
                CandidateRecord(
                    provider=result.provider,
                    field_path=item.field_path,
                    value=item.value,
                    confidence=item.confidence,
                    document_id=item.source.document_id,
                    page=item.source.page,
                )
                for item in result.candidates
            ]
            job.findings = [
                FindingRecord(code=item.code, severity=item.severity, message=item.message)
                for item in result.findings
            ]
            job.status = "succeeded"
        except TimeoutError as error:
            job.status = "failed"
            job.retryable = True
            job.error_code = "provider_timeout"
            job.error_message = str(error)
        except Exception as error:
            job.status = "failed"
            job.retryable = False
            job.error_code = "invalid_provider_response"
            job.error_message = type(error).__name__
        job.completed_at = datetime.now(UTC)
        self.session.commit()
        self.session.refresh(job)
        return job

