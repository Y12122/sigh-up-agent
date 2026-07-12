from uuid import UUID

from sqlalchemy.orm import Session

from app.cases.models import Case
from app.db import engine


def create_ready_case(client):
    case = client.post("/api/v1/cases", json={"customer_name": "确认测试", "company_name": "确认测试有限公司"}).json()
    registration = {
        "company": {"name_zh": "确认测试有限公司", "name_en": "CONFIRMATION TEST LIMITED", "business_scope": "咨询", "registered_capital": "10000", "currency": "HKD"},
        "directors": [{"name": "测试董事", "document_type": "passport", "document_number": "MASKED-C001"}],
        "shareholders": [{"name": "测试股东", "share_percentage": "100"}],
        "registered_address": "香港测试地址",
        "contact": {"name": "确认测试", "phone": "13800000000"},
    }
    client.patch(f"/api/v1/cases/{case['id']}/registration", json=registration, headers={"X-Actor-Id": "reviewer-1"})
    with Session(engine) as session:
        model = session.get(Case, UUID(case["id"]))
        model.status = "waiting_confirmation"
        session.commit()
    return case, registration


def test_generate_and_confirm_current_version(client):
    case, _ = create_ready_case(client)
    generated = client.post(f"/api/v1/cases/{case['id']}/confirmations", headers={"X-Actor-Id": "reviewer-1"})
    confirmed = client.post(f"/api/v1/customer/cases/{case['customer_token']}/confirmations/{generated.json()['id']}/confirm")

    assert generated.status_code == 201
    assert len(generated.json()["snapshot_hash"]) == 64
    assert generated.json()["version"] == 1
    assert confirmed.status_code == 200
    assert confirmed.json()["status"] == "confirmed"
    assert client.get(f"/api/v1/cases/{case['id']}").json()["status"] == "complete"


def test_key_field_change_invalidates_confirmation(client):
    case, registration = create_ready_case(client)
    generated = client.post(f"/api/v1/cases/{case['id']}/confirmations", headers={"X-Actor-Id": "reviewer-1"}).json()
    client.post(f"/api/v1/customer/cases/{case['customer_token']}/confirmations/{generated['id']}/confirm")
    registration["company"]["name_en"] = "CHANGED LIMITED"

    response = client.patch(f"/api/v1/cases/{case['id']}/registration", json=registration, headers={"X-Actor-Id": "reviewer-2"})
    current = client.get(f"/api/v1/customer/cases/{case['customer_token']}/confirmation").json()

    assert response.status_code == 200
    assert current["status"] == "invalidated"
    assert client.get(f"/api/v1/cases/{case['id']}").json()["status"] == "human_review"


def test_only_current_version_can_be_confirmed(client):
    case, _ = create_ready_case(client)
    first = client.post(f"/api/v1/cases/{case['id']}/confirmations", headers={"X-Actor-Id": "reviewer-1"}).json()
    second = client.post(f"/api/v1/cases/{case['id']}/confirmations", headers={"X-Actor-Id": "reviewer-1"}).json()

    response = client.post(f"/api/v1/customer/cases/{case['customer_token']}/confirmations/{first['id']}/confirm")

    assert second["version"] == 2
    assert response.status_code == 409

