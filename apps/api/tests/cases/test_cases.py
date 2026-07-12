def test_create_case_starts_waiting_for_upload(client):
    response = client.post(
        "/api/v1/cases",
        json={"customer_name": "测试客户", "company_name": "恒星贸易有限公司"},
    )

    assert response.status_code == 201
    payload = response.json()
    assert payload["status"] == "waiting_upload"
    assert len(payload["customer_token"]) >= 32


def test_created_case_is_available_in_list_and_detail(client):
    created = client.post(
        "/api/v1/cases",
        json={"customer_name": "陈女士", "company_name": "远景顾问有限公司"},
    ).json()

    listing = client.get("/api/v1/cases")
    detail = client.get(f"/api/v1/cases/{created['id']}")

    assert listing.status_code == 200
    assert any(item["id"] == created["id"] for item in listing.json()["items"])
    assert detail.status_code == 200
    assert detail.json()["company_name"] == "远景顾问有限公司"


def test_unknown_case_returns_404(client):
    response = client.get("/api/v1/cases/00000000-0000-0000-0000-000000000000")

    assert response.status_code == 404
