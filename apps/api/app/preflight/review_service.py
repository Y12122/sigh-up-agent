from enum import StrEnum

from app.preflight.contracts import Finding


class CandidateDecision(StrEnum):
    ACCEPTED = "accepted"
    UNCHANGED = "unchanged"
    REQUIRES_EXPLICIT_OVERRIDE = "requires_explicit_override"


class BlockingFindings(ValueError):
    def __init__(self, codes: list[str]):
        super().__init__("Blocking findings prevent approval")
        self.codes = codes


def decide_candidate(
    *,
    current_value: str | None,
    candidate_value: str,
    current_source: str,
    explicit_override: bool,
) -> CandidateDecision:
    if current_value == candidate_value:
        return CandidateDecision.UNCHANGED
    if current_value is not None and current_source in {"customer", "reviewer"}:
        if not explicit_override:
            return CandidateDecision.REQUIRES_EXPLICIT_OVERRIDE
    return CandidateDecision.ACCEPTED


def approve_review(findings: list[Finding], *, llm_recommendation: str | None = None) -> bool:
    blocking_codes = [item.code for item in findings if item.severity == "blocking"]
    if blocking_codes:
        raise BlockingFindings(blocking_codes)
    return True
