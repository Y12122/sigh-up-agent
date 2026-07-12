import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from app.cases.states import CaseStatus


class CreateCase(BaseModel):
    customer_name: str = Field(min_length=1, max_length=120)
    company_name: str = Field(min_length=1, max_length=200)


class CaseRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    customer_name: str
    company_name: str
    customer_token: str
    status: CaseStatus
    created_at: datetime


class CaseList(BaseModel):
    items: list[CaseRead]

