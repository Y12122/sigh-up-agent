from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from app.cases import models as case_models
from app.cases.router import router as cases_router
from app.config import get_settings
from app.db import Base, engine
from app.documents.router import router as documents_router
from app.preflight import jobs as preflight_jobs
from app.registration.router import router as registration_router


@asynccontextmanager
async def lifespan(_: FastAPI):
    Base.metadata.create_all(engine)
    yield

settings = get_settings()
app = FastAPI(title=settings.app_name, lifespan=lifespan)
app.include_router(cases_router)
app.include_router(registration_router)
app.include_router(documents_router)


@app.exception_handler(RequestValidationError)
async def validation_error_handler(_: Request, error: RequestValidationError) -> JSONResponse:
    details = [
        {
            "code": item["type"],
            "message": item["msg"],
            "location": item["loc"],
        }
        for item in error.errors()
    ]
    return JSONResponse(status_code=422, content={"detail": details})


@app.get("/api/v1/health")
def health() -> dict[str, str]:
    return {"status": "ok"}
