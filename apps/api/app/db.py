from collections.abc import Generator

from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, Session
from sqlalchemy.pool import StaticPool

from app.config import get_settings


class Base(DeclarativeBase):
    pass


database_url = get_settings().database_url
engine_options = {"pool_pre_ping": True}
if database_url.startswith("sqlite"):
    engine_options.update(
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )

engine = create_engine(database_url, **engine_options)


def get_session() -> Generator[Session, None, None]:
    with Session(engine) as session:
        yield session

