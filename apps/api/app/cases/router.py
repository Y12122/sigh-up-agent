import uuid

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.cases.schemas import CaseList, CaseRead, CreateCase
from app.cases.service import CaseService
from app.db import get_session

router = APIRouter(prefix="/api/v1/cases", tags=["cases"])


@router.post("", response_model=CaseRead, status_code=status.HTTP_201_CREATED)
def create_case(data: CreateCase, session: Session = Depends(get_session)) -> CaseRead:
    return CaseRead.model_validate(CaseService(session).create(data))


@router.get("", response_model=CaseList)
def list_cases(session: Session = Depends(get_session)) -> CaseList:
    return CaseList(items=[CaseRead.model_validate(item) for item in CaseService(session).list()])


@router.get("/{case_id}", response_model=CaseRead)
def get_case(case_id: uuid.UUID, session: Session = Depends(get_session)) -> CaseRead:
    case = CaseService(session).get(case_id)
    if case is None:
        raise HTTPException(status_code=404, detail="Case not found")
    return CaseRead.model_validate(case)

