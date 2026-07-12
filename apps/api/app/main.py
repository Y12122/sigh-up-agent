from fastapi import FastAPI

from app.config import get_settings

settings = get_settings()
app = FastAPI(title=settings.app_name)


@app.get("/api/v1/health")
def health() -> dict[str, str]:
    return {"status": "ok"}

