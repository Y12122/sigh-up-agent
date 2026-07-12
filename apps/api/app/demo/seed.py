from sqlalchemy import select
from sqlalchemy.orm import Session

from app.cases.models import Case
from app.cases.schemas import CreateCase
from app.cases.service import CaseService
from app.db import engine
from app.registration.schemas import RegistrationData
from app.registration.service import RegistrationService

DEMO_COMPANY_NAME = "恒星贸易有限公司"


def seed_demo(session: Session) -> Case:
    existing = session.scalar(select(Case).where(Case.company_name == DEMO_COMPANY_NAME))
    case = existing or CaseService(session).create(
        CreateCase(customer_name="陈女士（演示）", company_name=DEMO_COMPANY_NAME)
    )
    registration = RegistrationData.model_validate({
        "company": {"name_zh": DEMO_COMPANY_NAME, "name_en": "GALAXY TRADING LIMITED", "business_scope": "国际贸易", "registered_capital": "10000", "currency": "HKD"},
        "directors": [{"name": "测试董事甲", "document_type": "passport", "document_number": "MASKED-A001", "phone": "+852 5555 0001", "email": "director@example.test"}],
        "shareholders": [{"name": "测试股东甲", "share_percentage": "100"}],
        "registered_address": "香港测试区示例道 1 号",
        "contact": {"name": "陈女士（演示）", "phone": "+86 13800000000"},
    })
    RegistrationService(session).save(case.id, registration, "demo-seed")
    case.status = "human_review"
    session.commit()
    session.refresh(case)
    return case


def main() -> None:
    with Session(engine) as session:
        case = seed_demo(session)
        print(f"case_id={case.id}")
        print(f"customer_path=/customer/{case.customer_token}")


if __name__ == "__main__":
    main()
