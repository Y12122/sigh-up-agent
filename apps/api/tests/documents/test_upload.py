import io


def create_case(client):
    return client.post(
        "/api/v1/cases",
        json={"customer_name": "文件测试", "company_name": "文件测试有限公司"},
    ).json()


def upload_url(case):
    return f"/api/v1/customer/cases/{case['customer_token']}/documents"


def test_rejects_extension_mime_and_signature_mismatch(client):
    case = create_case(client)

    response = client.post(
        upload_url(case),
        data={"material_type": "director_id_front", "person_role": "director"},
        files={"file": ("identity.pdf", b"MZ\x90\x00fake executable", "application/pdf")},
    )

    assert response.status_code == 422
    assert response.json()["detail"][0]["code"] == "invalid_file_signature"


def test_valid_png_is_bound_to_case_and_material_type(client):
    case = create_case(client)
    png = b"\x89PNG\r\n\x1a\n" + b"synthetic-image-data"

    response = client.post(
        upload_url(case),
        data={"material_type": "director_id_front", "person_role": "director"},
        files={"file": ("identity.png", io.BytesIO(png), "image/png")},
    )

    assert response.status_code == 201
    payload = response.json()
    assert payload["case_id"] == case["id"]
    assert payload["material_type"] == "director_id_front"
    assert payload["original_name"] == "identity.png"
    assert "storage_key" not in payload


def test_unknown_customer_token_is_rejected(client):
    response = client.post(
        "/api/v1/customer/cases/not-a-valid-token/documents",
        data={"material_type": "address_proof", "person_role": "company"},
        files={"file": ("proof.pdf", b"%PDF-1.7 synthetic", "application/pdf")},
    )

    assert response.status_code == 404

