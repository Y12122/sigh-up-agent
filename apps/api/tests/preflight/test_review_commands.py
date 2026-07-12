import pytest
from sqlalchemy.orm import Session
from uuid import UUID

from app.cases.models import Case
from app.db import engine
from app.preflight.contracts import Finding
from app.preflight.review_service import (
    BlockingFindings,
    CandidateDecision,
    approve_review,
    decide_candidate,
)


def test_ai_candidate_does_not_overwrite_customer_value_implicitly():
    decision = decide_candidate(
        current_value="CUSTOMER-A001",
        candidate_value="OCR-A001",
        current_source="customer",
        explicit_override=False,
    )

    assert decision == CandidateDecision.REQUIRES_EXPLICIT_OVERRIDE


def test_explicit_reviewer_override_can_accept_candidate():
    decision = decide_candidate(
        current_value="CUSTOMER-A001",
        candidate_value="OCR-A001",
        current_source="customer",
        explicit_override=True,
    )

    assert decision == CandidateDecision.ACCEPTED


def test_blocking_rule_overrides_llm_recommendation():
    findings = [
        Finding(code="shareholding_total", severity="blocking", message="Must total 100")
    ]

    with pytest.raises(BlockingFindings):
        approve_review(findings, llm_recommendation="approve")


def create_review_case(client):
    created = client.post(
        "/api/v1/cases",
        json={"customer_name": "审核测试", "company_name": "审核测试有限公司"},
    ).json()
    with Session(engine) as session:
        case = session.get(Case, UUID(created["id"]))
        case.status = "human_review"
        session.commit()
    return created


def test_approve_command_rejects_blocking_findings(client):
    case = create_review_case(client)
    response = client.post(
        f"/api/v1/cases/{case['id']}/review/approve",
        json={"findings": [{"code": "shareholding_total", "severity": "blocking", "message": "Must total 100"}]},
        headers={"X-Actor-Id": "reviewer-1"},
    )

    assert response.status_code == 409
    assert response.json()["detail"]["codes"] == ["shareholding_total"]


def test_approve_and_request_documents_commands_change_status(client):
    approved_case = create_review_case(client)
    approved = client.post(
        f"/api/v1/cases/{approved_case['id']}/review/approve",
        json={"findings": []},
        headers={"X-Actor-Id": "reviewer-1"},
    )
    supplement_case = create_review_case(client)
    supplement = client.post(
        f"/api/v1/cases/{supplement_case['id']}/review/request-documents",
        json={"reason_codes": ["address_proof_expired"]},
        headers={"X-Actor-Id": "reviewer-2"},
    )

    assert approved.status_code == 200
    assert approved.json()["status"] == "waiting_confirmation"
    assert supplement.status_code == 200
    assert supplement.json()["status"] == "needs_documents"
