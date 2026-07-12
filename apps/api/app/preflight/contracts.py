import uuid
from typing import Literal

from pydantic import BaseModel, Field


class SourceReference(BaseModel):
    document_id: uuid.UUID
    page: int = Field(ge=1)


class FieldCandidate(BaseModel):
    field_path: str = Field(min_length=1)
    value: str
    confidence: float = Field(ge=0, le=1)
    source: SourceReference


class Finding(BaseModel):
    code: str
    severity: Literal["info", "warning", "blocking"]
    message: str
    source: SourceReference | None = None


class PreflightResult(BaseModel):
    provider: str
    candidates: list[FieldCandidate]
    findings: list[Finding]

