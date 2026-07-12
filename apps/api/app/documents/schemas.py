import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict


class DocumentRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    case_id: uuid.UUID
    material_type: str
    person_role: str
    original_name: str
    content_type: str
    size_bytes: int
    created_at: datetime

