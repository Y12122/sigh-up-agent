import pytest


@pytest.fixture
def case_id(client):
    response = client.post(
        "/api/v1/cases",
        json={"customer_name": "测试联系人", "company_name": "星河贸易有限公司"},
    )
    return response.json()["id"]


def registration_payload(*, second_share: str = "40.00"):
    return {
        "company": {
            "name_zh": "星河贸易有限公司",
            "name_en": "GALAXY TRADING LIMITED",
            "business_scope": "国际贸易",
            "registered_capital": "10000.00",
            "currency": "HKD",
        },
        "directors": [
            {
                "name": "测试董事甲",
                "document_type": "passport",
                "document_number": "MASKED-A001",
                "phone": "+852 5555 0001",
                "email": "director-a@example.test",
            }
        ],
        "shareholders": [
            {"name": "测试股东甲", "share_percentage": "60.00"},
            {"name": "测试股东乙", "share_percentage": second_share},
        ],
        "registered_address": "香港测试区示例道 1 号",
        "contact": {"name": "测试联系人", "phone": "+86 13800000000"},
    }


def test_save_and_read_registration_data(client, case_id):
    response = client.patch(
        f"/api/v1/cases/{case_id}/registration",
        json=registration_payload(),
        headers={"X-Actor-Id": "reviewer-1"},
    )

    assert response.status_code == 200
    assert response.json()["company"]["name_en"] == "GALAXY TRADING LIMITED"
    assert response.json()["shareholders"][1]["share_percentage"] == "40.00"
    assert client.get(f"/api/v1/cases/{case_id}/registration").json() == response.json()


def test_shareholding_must_total_100(client, case_id):
    response = client.patch(
        f"/api/v1/cases/{case_id}/registration",
        json=registration_payload(second_share="30.00"),
        headers={"X-Actor-Id": "reviewer-1"},
    )

    assert response.status_code == 422
    assert response.json()["detail"][0]["code"] == "shareholding_total"


def test_manual_change_creates_field_version(client, case_id):
    first = registration_payload()
    client.patch(
        f"/api/v1/cases/{case_id}/registration",
        json=first,
        headers={"X-Actor-Id": "reviewer-1"},
    )
    first["company"]["name_en"] = "GALAXY CONSULTING LIMITED"
    client.patch(
        f"/api/v1/cases/{case_id}/registration",
        json=first,
        headers={"X-Actor-Id": "reviewer-2"},
    )

    history = client.get(
        f"/api/v1/cases/{case_id}/field-history",
        params={"field_path": "company.name_en"},
    )

    assert history.status_code == 200
    assert history.json()["items"][0]["value"] == "GALAXY CONSULTING LIMITED"
    assert history.json()["items"][0]["actor_id"] == "reviewer-2"
    assert history.json()["items"][0]["source"] == "reviewer"
