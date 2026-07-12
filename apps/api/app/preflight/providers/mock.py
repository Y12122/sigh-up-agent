from app.preflight.contracts import FieldCandidate, PreflightResult, SourceReference


class MockOcrProvider:
    name = "mock-ocr"

    def extract(self, document_id: str, content: bytes) -> PreflightResult:
        return PreflightResult(
            provider=self.name,
            candidates=[
                FieldCandidate(
                    field_path="directors[0].document_number",
                    value="MASKED-A001",
                    confidence=0.93,
                    source=SourceReference(document_id=document_id, page=1),
                )
            ],
            findings=[],
        )


class MockLlmProvider:
    name = "mock-llm"

    def extract(self, document_id: str, content: bytes) -> PreflightResult:
        return PreflightResult(provider=self.name, candidates=[], findings=[])

