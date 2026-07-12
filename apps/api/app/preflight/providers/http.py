import base64
from typing import Protocol

import httpx

from app.preflight.contracts import PreflightResult


class JsonTransport(Protocol):
    def post_json(self, endpoint: str, payload: dict, headers: dict) -> dict: ...


class HttpxTransport:
    def post_json(self, endpoint: str, payload: dict, headers: dict) -> dict:
        response = httpx.post(endpoint, json=payload, headers=headers, timeout=30)
        response.raise_for_status()
        return response.json()


class HttpDocumentProvider:
    def __init__(self, name: str, endpoint: str, api_key: str, transport: JsonTransport | None = None):
        self.name = name
        self.endpoint = endpoint
        self.api_key = api_key
        self.transport = transport or HttpxTransport()

    def extract(self, document_id: str, content: bytes) -> PreflightResult:
        payload = {
            "document_id": str(document_id),
            "content_base64": base64.b64encode(content).decode("ascii"),
        }
        raw = self.transport.post_json(
            self.endpoint,
            payload,
            {"Authorization": f"Bearer {self.api_key}"},
        )
        return PreflightResult.model_validate({"provider": self.name, **raw})


class HttpOcrProvider(HttpDocumentProvider):
    def __init__(self, endpoint: str, api_key: str, transport: JsonTransport | None = None):
        super().__init__("http-ocr", endpoint, api_key, transport)


class HttpLlmProvider(HttpDocumentProvider):
    def __init__(self, endpoint: str, api_key: str, transport: JsonTransport | None = None):
        super().__init__("http-llm", endpoint, api_key, transport)

