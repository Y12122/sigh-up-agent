from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.cases import models as case_models
from app.cases.router import router as cases_router
from app.config import get_settings
from app.db import Base, engine


@asynccontextmanager
async def lifespan(_: FastAPI):
    Base.metadata.create_all(engine)
    yield

settings = get_settings()
app = FastAPI(title=settings.app_name, lifespan=lifespan)
app.include_router(cases_router)


@app.get("/api/v1/health")
def health() -> dict[str, str]:
    return {"status": "ok"}
