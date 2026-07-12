from enum import StrEnum


class CaseStatus(StrEnum):
    WAITING_UPLOAD = "waiting_upload"
    PREFLIGHT = "preflight"
    NEEDS_DOCUMENTS = "needs_documents"
    HUMAN_REVIEW = "human_review"
    WAITING_CONFIRMATION = "waiting_confirmation"
    COMPLETE = "complete"


class InvalidTransition(ValueError):
    pass


ALLOWED_TRANSITIONS: dict[CaseStatus, set[CaseStatus]] = {
    CaseStatus.WAITING_UPLOAD: {CaseStatus.PREFLIGHT},
    CaseStatus.PREFLIGHT: {CaseStatus.NEEDS_DOCUMENTS, CaseStatus.HUMAN_REVIEW},
    CaseStatus.NEEDS_DOCUMENTS: {CaseStatus.PREFLIGHT},
    CaseStatus.HUMAN_REVIEW: {
        CaseStatus.NEEDS_DOCUMENTS,
        CaseStatus.WAITING_CONFIRMATION,
    },
    CaseStatus.WAITING_CONFIRMATION: {
        CaseStatus.COMPLETE,
        CaseStatus.HUMAN_REVIEW,
    },
    CaseStatus.COMPLETE: set(),
}


def transition(current: CaseStatus, target: CaseStatus) -> CaseStatus:
    if target not in ALLOWED_TRANSITIONS[current]:
        raise InvalidTransition(f"Cannot transition from {current} to {target}")
    return target

