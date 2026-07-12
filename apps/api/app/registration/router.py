import uuid

from fastapi import APIRouter, Depends, Header, HTTPException, Query
from sqlalchemy.orm import Session

from app.db import get_session
from app.registration.schemas import FieldVersionList, FieldVersionRead, RegistrationData
from app.registration.service import RegistrationService

router = APIRouter(prefix="/api/v1/cases/{case_id}", tags=["registration"])


@router.get("/registration", response_model=RegistrationData)
def get_registration(case_id: uuid.UUID, session: Session = Depends(get_session)):
    result = RegistrationService(session).get(case_id)
    if result is None:
        raise HTTPException(status_code=404, detail="Registration data not found")
    return result


@router.patch("/registration", response_model=RegistrationData)
def save_registration(case_id: uuid.UUID, data: RegistrationData, x_actor_id: str = Header(min_length=1), session: Session = Depends(get_session)):
    try:
        return RegistrationService(session).save(case_id, data, x_actor_id)
    except LookupError as error:
        raise HTTPException(status_code=404, detail="Case not found") from error


@router.get("/field-history", response_model=FieldVersionList)
def get_field_history(case_id: uuid.UUID, field_path: str = Query(min_length=1), session: Session = Depends(get_session)):
    items = RegistrationService(session).history(case_id, field_path)
    return FieldVersionList(items=[FieldVersionRead.model_validate(item, from_attributes=True) for item in items])

