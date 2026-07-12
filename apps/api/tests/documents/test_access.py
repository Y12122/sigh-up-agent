from sqlalchemy import select
from sqlalchemy.orm import Session
from uuid import UUID

from app.audit.models import AuditLog
from app.db import engine

from .test_upload import create_case, upload_url


def test_employee_download_records_audit_event(client):
    case = create_case(client)
    uploaded = client.post(
        upload_url(case),
        data={"material_type": "address_proof", "person_role": "company"},
        files={"file": ("proof.pdf", b"%PDF-1.7 synthetic", "application/pdf")},
    ).json()

    response = client.get(
        f"/api/v1/documents/{uploaded['id']}/download",
        headers={"X-Actor-Id": "reviewer-file"},
    )

    assert response.status_code == 200
    assert response.content == b"%PDF-1.7 synthetic"
    assert response.headers["content-disposition"].endswith('filename="proof.pdf"')
    with Session(engine) as session:
        event = session.scalar(
            select(AuditLog)
            .where(AuditLog.case_id == UUID(case["id"]), AuditLog.action == "document.viewed")
            .order_by(AuditLog.created_at.desc())
        )
        assert event is not None
        assert event.actor_id == "reviewer-file"
