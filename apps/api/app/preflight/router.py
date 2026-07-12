import uuid

from fastapi import APIRouter, Depends, Header, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from app.audit.models import AuditLog
from app.cases.models import Case
from app.cases.schemas import CaseRead
from app.cases.states import CaseStatus, InvalidTransition, transition
from app.db import get_session
from app.preflight.contracts import Finding
from app.preflight.review_service import BlockingFindings, approve_review

router = APIRouter(prefix="/api/v1/cases/{case_id}/review", tags=["review"])


class ApprovalRequest(BaseModel):
    findings: list[Finding]
    llm_recommendation: str | None = None


class RequestDocumentsRequest(BaseModel):
    reason_codes: list[str] = Field(min_length=1)


def load_case(session: Session, case_id: uuid.UUID) -> Case:
    case = session.get(Case, case_id)
    if case is None:
        raise HTTPException(status_code=404, detail="Case not found")
    return case


@router.post("/approve", response_model=CaseRead)
def approve_case(case_id: uuid.UUID, request: ApprovalRequest, x_actor_id: str = Header(min_length=1), session: Session = Depends(get_session)):
    case = load_case(session, case_id)
    try:
        approve_review(request.findings, llm_recommendation=request.llm_recommendation)
        case.status = transition(CaseStatus(case.status), CaseStatus.WAITING_CONFIRMATION).value
    except BlockingFindings as error:
        raise HTTPException(status_code=409, detail={"code": "blocking_findings", "codes": error.codes}) from error
    except InvalidTransition as error:
        raise HTTPException(status_code=409, detail={"code": "invalid_transition"}) from error
    session.add(AuditLog(case_id=case.id, action="review.approved", actor_id=x_actor_id, details={}))
    session.commit()
    session.refresh(case)
    return CaseRead.model_validate(case)


@router.post("/request-documents", response_model=CaseRead)
def request_documents(case_id: uuid.UUID, request: RequestDocumentsRequest, x_actor_id: str = Header(min_length=1), session: Session = Depends(get_session)):
    case = load_case(session, case_id)
    try:
        case.status = transition(CaseStatus(case.status), CaseStatus.NEEDS_DOCUMENTS).value
    except InvalidTransition as error:
        raise HTTPException(status_code=409, detail={"code": "invalid_transition"}) from error
    session.add(AuditLog(case_id=case.id, action="review.documents_requested", actor_id=x_actor_id, details={"reason_codes": request.reason_codes}))
    session.commit()
    session.refresh(case)
    return CaseRead.model_validate(case)

