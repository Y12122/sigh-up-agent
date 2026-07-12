import pytest

from app.preflight.contracts import PreflightResult
from app.preflight.providers.http import HttpOcrProvider
from app.preflight.providers.mock import MockOcrProvider


class FakeTransport:
    def post_json(self, endpoint, payload, headers):
        return {
            "candidates": [
                {
                    "field_path": "directors[0].document_number",
                    "value": "MASKED-A001",
                    "confidence": 0.93,
                    "source": {"document_id": payload["document_id"], "page": 1},
                }
            ],
            "findings": [],
        }


@pytest.mark.parametrize(
    "provider",
    [MockOcrProvider(), HttpOcrProvider("https://ocr.example.test", "test-key", FakeTransport())],
)
def test_ocr_providers_return_the_same_contract(provider):
    result = provider.extract("00000000-0000-0000-0000-000000000001", b"synthetic")

    assert isinstance(result, PreflightResult)
    assert result.candidates[0].field_path == "directors[0].document_number"
    assert 0 <= result.candidates[0].confidence <= 1
    assert result.candidates[0].source.page == 1


def test_contract_rejects_confidence_above_one():
    with pytest.raises(ValueError):
        PreflightResult.model_validate(
            {
                "provider": "bad",
                "candidates": [
                    {
                        "field_path": "company.name_en",
                        "value": "TEST",
                        "confidence": 1.5,
                        "source": {"document_id": "00000000-0000-0000-0000-000000000001", "page": 1},
                    }
                ],
                "findings": [],
            }
        )

