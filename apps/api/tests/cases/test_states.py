import pytest

from app.cases.states import CaseStatus, InvalidTransition, transition


def test_waiting_upload_can_start_preflight():
    assert transition(CaseStatus.WAITING_UPLOAD, CaseStatus.PREFLIGHT) == CaseStatus.PREFLIGHT


def test_invalid_transition_is_rejected():
    with pytest.raises(InvalidTransition):
        transition(CaseStatus.WAITING_UPLOAD, CaseStatus.WAITING_CONFIRMATION)


def test_complete_case_has_no_outgoing_transition():
    with pytest.raises(InvalidTransition):
        transition(CaseStatus.COMPLETE, CaseStatus.HUMAN_REVIEW)

