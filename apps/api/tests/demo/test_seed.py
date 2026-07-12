from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.cases.models import Case
from app.db import engine
from app.demo.reset import main as reset_main, reset_demo
from app.demo.seed import DEMO_COMPANY_NAME, seed_demo


def test_seed_is_idempotent(client):
    with Session(engine) as session:
        first = seed_demo(session)
        second = seed_demo(session)
        count = session.scalar(select(func.count()).select_from(Case).where(Case.company_name == DEMO_COMPANY_NAME))

    assert first.id == second.id
    assert count == 1
    assert first.status == "human_review"


def test_reset_removes_demo_cases(client):
    with Session(engine) as session:
        seed_demo(session)
        removed = reset_demo(session, environment="development")
        count = session.scalar(select(func.count()).select_from(Case))

    assert removed >= 1
    assert count == 0


def test_reset_is_blocked_in_production(client):
    with Session(engine) as session:
        try:
            reset_demo(session, environment="production")
        except RuntimeError as error:
            assert str(error) == "demo_reset_disabled_in_production"
        else:
            raise AssertionError("Production reset must be blocked")


def test_reset_cli_requires_explicit_confirmation(monkeypatch):
    monkeypatch.setattr(sys, "argv", ["reset"])
    with pytest.raises(SystemExit, match="Pass --confirm"):
        reset_main()
import sys

import pytest
