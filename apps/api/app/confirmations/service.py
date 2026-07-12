import hashlib
import json
import uuid
from datetime import UTC, datetime

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.audit.models import AuditLog
from app.cases.models import Case
from app.confirmations.models import Confirmation
from app.confirmations.renderer import render_docx, render_pdf
from app.documents.storage import PrivateStorage
from app.registration.service import RegistrationService


KEY_PREFIXES = ("company.", "directors", "shareholders", "registered_address")


class ConfirmationConflict(ValueError):
    pass


class ConfirmationService:
    def __init__(self, session: Session, storage: PrivateStorage):
        self.session = session
        self.storage = storage

    def generate(self, case_id: uuid.UUID, actor_id: str) -> Confirmation:
        case = self.session.get(Case, case_id)
        if case is None or case.status != "waiting_confirmation":
            raise ConfirmationConflict("case_not_ready")
        registration = RegistrationService(self.session).get(case_id)
        if registration is None:
            raise ConfirmationConflict("registration_missing")
        snapshot = registration.model_dump(mode="json")
        canonical = json.dumps(snapshot, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")
        digest = hashlib.sha256(canonical).hexdigest()
        version = (self.session.scalar(select(func.max(Confirmation.version)).where(Confirmation.case_id == case_id)) or 0) + 1
        confirmation = Confirmation(case_id=case_id, version=version, snapshot=snapshot, snapshot_hash=digest, status="pending", docx_storage_key=f"cases/{case_id}/confirmations/{version}.docx", pdf_storage_key=f"cases/{case_id}/confirmations/{version}.pdf", created_by=actor_id)
        self.storage.put(confirmation.docx_storage_key, render_docx(snapshot), "application/vnd.openxmlformats-officedocument.wordprocessingml.document")
        self.storage.put(confirmation.pdf_storage_key, render_pdf(snapshot), "application/pdf")
        self.session.add(confirmation)
        self.session.add(AuditLog(case_id=case_id, action="confirmation.generated", actor_id=actor_id, details={"version": version, "snapshot_hash": digest}))
        self.session.commit()
        self.session.refresh(confirmation)
        return confirmation

    def current(self, case_id: uuid.UUID) -> Confirmation | None:
        return self.session.scalar(select(Confirmation).where(Confirmation.case_id == case_id).order_by(Confirmation.version.desc()))

    def confirm(self, case: Case, confirmation_id: uuid.UUID) -> Confirmation:
        current = self.current(case.id)
        if current is None or current.id != confirmation_id or current.status != "pending":
            raise ConfirmationConflict("not_current_confirmation")
        current.status = "confirmed"
        current.confirmed_at = datetime.now(UTC)
        case.status = "complete"
        self.session.add(AuditLog(case_id=case.id, action="confirmation.confirmed", actor_id="customer", details={"version": current.version}))
        self.session.commit()
        self.session.refresh(current)
        return current

    def invalidate_for_changes(self, case_id: uuid.UUID, changed_paths: list[str]) -> None:
        if not any(path.startswith(KEY_PREFIXES) for path in changed_paths):
            return
        current = self.current(case_id)
        if current is None or current.status == "invalidated":
            return
        current.status = "invalidated"
        current.invalidated_at = datetime.now(UTC)
        case = self.session.get(Case, case_id)
        case.status = "human_review"
        self.session.add(AuditLog(case_id=case_id, action="confirmation.invalidated", actor_id="system", details={"changed_fields": changed_paths}))

