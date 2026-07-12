from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "Business Registration AI"
    environment: str = "development"
    database_url: str = "sqlite+pysqlite:///:memory:"
    minio_endpoint: str = "minio:9000"
    minio_access_key: str = "registration"
    minio_secret_key: str = "registration_dev_only"
    minio_bucket: str = "registration-documents"
    storage_provider: str = "memory"
    ocr_provider: str = "mock"
    ocr_endpoint: str = ""
    ocr_api_key: str = ""
    llm_provider: str = "mock"
    llm_endpoint: str = ""
    llm_api_key: str = ""

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


@lru_cache
def get_settings() -> Settings:
    return Settings()
