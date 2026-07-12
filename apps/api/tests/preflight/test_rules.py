from datetime import date
from decimal import Decimal

from app.preflight.rules import (
    check_address_proof,
    check_business_scope,
    check_confidence,
    check_phone,
    check_shareholding,
)


def test_address_proof_older_than_three_calendar_months_is_blocking():
    finding = check_address_proof(date(2026, 3, 31), today=date(2026, 7, 11))

    assert finding.code == "address_proof_expired"
    assert finding.severity == "blocking"


def test_address_proof_on_calendar_boundary_is_valid():
    assert check_address_proof(date(2026, 4, 11), today=date(2026, 7, 11)) is None


def test_business_scope_above_30_characters_is_blocking():
    finding = check_business_scope("测" * 31)
    assert finding.code == "business_scope_too_long"


def test_shareholding_must_total_100():
    finding = check_shareholding([Decimal("60"), Decimal("30")])
    assert finding.code == "shareholding_total"


def test_phone_format_requires_manual_confirmation():
    finding = check_phone("abc-not-phone")
    assert finding.code == "phone_format"
    assert finding.severity == "warning"


def test_low_confidence_requires_human_review():
    finding = check_confidence(0.74, threshold=0.80)
    assert finding.code == "low_confidence"

