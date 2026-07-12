import argparse

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.audit import models as audit_models
from app.cases.models import Case
from app.confirmations import models as confirmation_models
from app.config import get_settings
from app.db import Base, engine
from app.documents import models as document_models
from app.preflight import jobs as preflight_models
from app.registration import models as registration_models


def reset_demo(session: Session, *, environment: str) -> int:
    if environment == "production":
        raise RuntimeError("demo_reset_disabled_in_production")
    removed = session.scalar(select(func.count()).select_from(Case)) or 0
    session.close()
    Base.metadata.drop_all(engine)
    Base.metadata.create_all(engine)
    return removed


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--confirm", action="store_true")
    arguments = parser.parse_args()
    if not arguments.confirm:
        raise SystemExit("Pass --confirm to reset all Demo data")
    settings = get_settings()
    with Session(engine) as session:
        removed = reset_demo(session, environment=settings.environment)
    print(f"removed_cases={removed}")


if __name__ == "__main__":
    main()
