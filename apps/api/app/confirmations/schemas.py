import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict


class ConfirmationRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    case_id: uuid.UUID
    version: int
    snapshot: dict
    snapshot_hash: str
    status: str
    created_at: datetime
    confirmed_at: datetime | None
    invalidated_at: datetime | None

