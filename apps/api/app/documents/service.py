import uuid

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.audit.models import AuditLog
from app.cases.models import Case
from app.documents.models import Document
from app.documents.storage import PrivateStorage


class DocumentService:
    def __init__(self, session: Session, storage: PrivateStorage):
        self.session = session
        self.storage = storage

    def create(self, token: str, filename: str, content_type: str, content: bytes, material_type: str, person_role: str) -> Document:
        case = self.session.scalar(select(Case).where(Case.customer_token == token))
        if case is None:
            raise LookupError("case_not_found")
        document_id = uuid.uuid4()
        storage_key = f"cases/{case.id}/{document_id}"
        self.storage.put(storage_key, content, content_type)
        document = Document(id=document_id, case_id=case.id, material_type=material_type, person_role=person_role, original_name=filename, content_type=content_type, size_bytes=len(content), storage_key=storage_key)
        self.session.add(document)
        self.session.add(AuditLog(case_id=case.id, action="document.uploaded", actor_id="customer", details={"document_id": str(document_id), "material_type": material_type}))
        self.session.commit()
        self.session.refresh(document)
        return document

    def open(self, document_id: uuid.UUID, actor_id: str) -> tuple[Document, bytes]:
        document = self.session.get(Document, document_id)
        if document is None:
            raise LookupError("document_not_found")
        content = self.storage.get(document.storage_key)
        self.session.add(AuditLog(case_id=document.case_id, action="document.viewed", actor_id=actor_id, details={"document_id": str(document.id)}))
        self.session.commit()
        return document, content

