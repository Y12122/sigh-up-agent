import uuid
from urllib.parse import quote

from fastapi import APIRouter, Depends, File, Form, Header, HTTPException, UploadFile, status
from fastapi.responses import Response
from sqlalchemy.orm import Session

from app.db import get_session
from app.documents.schemas import DocumentRead
from app.documents.service import DocumentService
from app.documents.storage import PrivateStorage, get_storage
from app.documents.validation import InvalidDocument, validate_document

router = APIRouter(tags=["documents"])


@router.post("/api/v1/customer/cases/{token}/documents", response_model=DocumentRead, status_code=status.HTTP_201_CREATED)
async def upload_document(token: str, material_type: str = Form(min_length=1), person_role: str = Form(min_length=1), file: UploadFile = File(), session: Session = Depends(get_session), storage: PrivateStorage = Depends(get_storage)):
    content = await file.read()
    try:
        validate_document(file.filename or "", file.content_type or "", content)
        document = DocumentService(session, storage).create(token, file.filename or "file", file.content_type or "application/octet-stream", content, material_type, person_role)
    except InvalidDocument as error:
        raise HTTPException(status_code=422, detail=[{"code": error.code, "message": str(error)}]) from error
    except LookupError as error:
        raise HTTPException(status_code=404, detail="Case not found") from error
    return DocumentRead.model_validate(document)


@router.get("/api/v1/documents/{document_id}/download")
def download_document(document_id: uuid.UUID, x_actor_id: str = Header(min_length=1), session: Session = Depends(get_session), storage: PrivateStorage = Depends(get_storage)) -> Response:
    try:
        document, content = DocumentService(session, storage).open(document_id, x_actor_id)
    except (LookupError, KeyError) as error:
        raise HTTPException(status_code=404, detail="Document not found") from error
    filename = quote(document.original_name)
    return Response(content=content, media_type=document.content_type, headers={"Content-Disposition": f'attachment; filename="{filename}"'})

