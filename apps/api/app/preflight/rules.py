import calendar
import re
from datetime import date
from decimal import Decimal

from app.preflight.contracts import Finding


def subtract_months(value: date, months: int) -> date:
    month_index = value.year * 12 + value.month - 1 - months
    year, zero_based_month = divmod(month_index, 12)
    month = zero_based_month + 1
    day = min(value.day, calendar.monthrange(year, month)[1])
    return date(year, month, day)


def check_address_proof(proof_date: date, *, today: date | None = None) -> Finding | None:
    current = today or date.today()
    if proof_date < subtract_months(current, 3):
        return Finding(
            code="address_proof_expired",
            severity="blocking",
            message="Address proof must be dated within three calendar months",
        )
    return None


def check_business_scope(value: str) -> Finding | None:
    if len(value) > 30:
        return Finding(
            code="business_scope_too_long",
            severity="blocking",
            message="Business scope must not exceed 30 characters",
        )
    return None


def check_shareholding(percentages: list[Decimal]) -> Finding | None:
    if sum(percentages) != Decimal("100"):
        return Finding(
            code="shareholding_total",
            severity="blocking",
            message="Shareholding percentages must total 100",
        )
    return None


def check_phone(value: str) -> Finding | None:
    normalized = re.sub(r"[\s()-]", "", value)
    if not re.fullmatch(r"\+?\d{8,15}", normalized):
        return Finding(
            code="phone_format",
            severity="warning",
            message="Phone number format requires manual confirmation",
        )
    return None


def check_confidence(confidence: float, *, threshold: float = 0.8) -> Finding | None:
    if confidence < threshold:
        return Finding(
            code="low_confidence",
            severity="warning",
            message="Extracted value requires human review",
        )
    return None

