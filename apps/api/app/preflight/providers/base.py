from typing import Protocol

from app.preflight.contracts import PreflightResult


class DocumentProvider(Protocol):
    name: str

    def extract(self, document_id: str, content: bytes) -> PreflightResult: ...

