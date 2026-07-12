import uuid
from collections.abc import Iterable

from sqlalchemy import delete, select
from sqlalchemy.orm import Session

from app.audit.models import AuditLog, FieldVersion
from app.cases.models import Case
from app.registration.models import Company, Person, RegistrationProfile, Shareholder
from app.registration.schemas import RegistrationData


def flatten(data: dict, prefix: str = "") -> Iterable[tuple[str, object]]:
    for key, value in data.items():
        path = f"{prefix}.{key}" if prefix else key
        if isinstance(value, dict):
            yield from flatten(value, path)
        elif not isinstance(value, list):
            yield path, value


class RegistrationService:
    def __init__(self, session: Session):
        self.session = session

    def get(self, case_id: uuid.UUID) -> RegistrationData | None:
        company = self.session.scalar(select(Company).where(Company.case_id == case_id))
        profile = self.session.scalar(select(RegistrationProfile).where(RegistrationProfile.case_id == case_id))
        if company is None or profile is None:
            return None
        directors = list(self.session.scalars(select(Person).where(Person.case_id == case_id, Person.role == "director")))
        shareholders = list(self.session.scalars(select(Shareholder).where(Shareholder.case_id == case_id).order_by(Shareholder.position)))
        return RegistrationData.model_validate({
            "company": company,
            "directors": directors,
            "shareholders": shareholders,
            "registered_address": profile.registered_address,
            "contact": {"name": profile.contact_name, "phone": profile.contact_phone},
        }, from_attributes=True)

    def save(self, case_id: uuid.UUID, data: RegistrationData, actor_id: str) -> RegistrationData:
        if self.session.get(Case, case_id) is None:
            raise LookupError("case_not_found")
        previous = self.get(case_id)
        self.session.execute(delete(Person).where(Person.case_id == case_id, Person.role == "director"))
        self.session.execute(delete(Shareholder).where(Shareholder.case_id == case_id))
        company = self.session.scalar(select(Company).where(Company.case_id == case_id)) or Company(case_id=case_id)
        for key, value in data.company.model_dump().items():
            setattr(company, key, value)
        self.session.add(company)
        profile = self.session.scalar(select(RegistrationProfile).where(RegistrationProfile.case_id == case_id)) or RegistrationProfile(case_id=case_id)
        profile.registered_address = data.registered_address
        profile.contact_name = data.contact.name
        profile.contact_phone = data.contact.phone
        self.session.add(profile)
        self.session.add_all([Person(case_id=case_id, role="director", **item.model_dump()) for item in data.directors])
        self.session.add_all([Shareholder(case_id=case_id, position=index, **item.model_dump()) for index, item in enumerate(data.shareholders)])
        old_values = dict(flatten(previous.model_dump(mode="json"))) if previous else {}
        new_values = dict(flatten(data.model_dump(mode="json")))
        for path, value in new_values.items():
            if old_values.get(path) != value:
                self.session.add(FieldVersion(case_id=case_id, field_path=path, value=value, previous_value=old_values.get(path), source="reviewer", actor_id=actor_id))
        changed_paths = [path for path, value in new_values.items() if old_values.get(path) != value]
        self.session.add(AuditLog(case_id=case_id, action="registration.updated", actor_id=actor_id, details={"changed_fields": changed_paths}))
        from app.confirmations.service import ConfirmationService
        from app.documents.storage import get_storage
        ConfirmationService(self.session, get_storage()).invalidate_for_changes(case_id, changed_paths)
        self.session.commit()
        return self.get(case_id)

    def history(self, case_id: uuid.UUID, field_path: str) -> list[FieldVersion]:
        statement = select(FieldVersion).where(FieldVersion.case_id == case_id, FieldVersion.field_path == field_path).order_by(FieldVersion.created_at.desc(), FieldVersion.id.desc())
        return list(self.session.scalars(statement))
