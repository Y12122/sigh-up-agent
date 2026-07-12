import uuid

from fastapi import APIRouter, Depends, Header, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.cases.models import Case
from app.confirmations.schemas import ConfirmationRead
from app.confirmations.service import ConfirmationConflict, ConfirmationService
from app.db import get_session
from app.documents.storage import PrivateStorage, get_storage

router = APIRouter(tags=["confirmations"])


@router.post("/api/v1/cases/{case_id}/confirmations", response_model=ConfirmationRead, status_code=status.HTTP_201_CREATED)
def generate_confirmation(case_id: uuid.UUID, x_actor_id: str = Header(min_length=1), session: Session = Depends(get_session), storage: PrivateStorage = Depends(get_storage)):
    try:
        return ConfirmationService(session, storage).generate(case_id, x_actor_id)
    except ConfirmationConflict as error:
        raise HTTPException(status_code=409, detail={"code": str(error)}) from error


def case_by_token(session: Session, token: str) -> Case:
    case = session.scalar(select(Case).where(Case.customer_token == token))
    if case is None:
        raise HTTPException(status_code=404, detail="Case not found")
    return case


@router.get("/api/v1/customer/cases/{token}/confirmation", response_model=ConfirmationRead)
def current_confirmation(token: str, session: Session = Depends(get_session), storage: PrivateStorage = Depends(get_storage)):
    case = case_by_token(session, token)
    current = ConfirmationService(session, storage).current(case.id)
    if current is None:
        raise HTTPException(status_code=404, detail="Confirmation not found")
    return current


@router.post("/api/v1/customer/cases/{token}/confirmations/{confirmation_id}/confirm", response_model=ConfirmationRead)
def confirm(token: str, confirmation_id: uuid.UUID, session: Session = Depends(get_session), storage: PrivateStorage = Depends(get_storage)):
    case = case_by_token(session, token)
    try:
        return ConfirmationService(session, storage).confirm(case, confirmation_id)
    except ConfirmationConflict as error:
        raise HTTPException(status_code=409, detail={"code": str(error)}) from error

