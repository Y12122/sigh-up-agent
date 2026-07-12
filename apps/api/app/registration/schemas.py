import uuid
from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, Field, field_serializer, model_validator
from pydantic_core import PydanticCustomError


class CompanyData(BaseModel):
    name_zh: str = Field(min_length=1, max_length=200)
    name_en: str = Field(min_length=1, max_length=200)
    business_scope: str = Field(min_length=1, max_length=30)
    registered_capital: Decimal = Field(gt=0)
    currency: str = Field(default="HKD", min_length=3, max_length=3)

    @field_serializer("registered_capital")
    def serialize_capital(self, value: Decimal) -> str:
        return f"{value:.2f}"


class DirectorData(BaseModel):
    name: str = Field(min_length=1, max_length=120)
    document_type: str
    document_number: str
    phone: str | None = None
    email: str | None = None


class ShareholderData(BaseModel):
    name: str = Field(min_length=1, max_length=200)
    share_percentage: Decimal = Field(gt=0, le=100)

    @field_serializer("share_percentage")
    def serialize_share(self, value: Decimal) -> str:
        return f"{value:.2f}"


class ContactData(BaseModel):
    name: str
    phone: str


class RegistrationData(BaseModel):
    company: CompanyData
    directors: list[DirectorData] = Field(min_length=1)
    shareholders: list[ShareholderData] = Field(min_length=1)
    registered_address: str = Field(min_length=1)
    contact: ContactData

    @model_validator(mode="after")
    def validate_shareholding(self):
        if sum(item.share_percentage for item in self.shareholders) != Decimal("100"):
            raise PydanticCustomError(
                "shareholding_total",
                "Shareholding percentages must total 100",
            )
        return self


class FieldVersionRead(BaseModel):
    id: uuid.UUID
    field_path: str
    value: object
    previous_value: object | None
    source: str
    actor_id: str
    created_at: datetime


class FieldVersionList(BaseModel):
    items: list[FieldVersionRead]
