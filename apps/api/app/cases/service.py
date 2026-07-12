import secrets
import uuid

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.cases.models import Case
from app.cases.schemas import CreateCase


class CaseService:
    def __init__(self, session: Session):
        self.session = session

    def create(self, data: CreateCase) -> Case:
        case = Case(
            customer_name=data.customer_name,
            company_name=data.company_name,
            customer_token=secrets.token_urlsafe(32),
        )
        self.session.add(case)
        self.session.commit()
        self.session.refresh(case)
        return case

    def list(self) -> list[Case]:
        return list(self.session.scalars(select(Case).order_by(Case.created_at.desc())))

    def get(self, case_id: uuid.UUID) -> Case | None:
        return self.session.get(Case, case_id)

