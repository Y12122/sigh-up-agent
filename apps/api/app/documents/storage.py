import io
from typing import Protocol

from minio import Minio

from app.config import get_settings


class PrivateStorage(Protocol):
    def put(self, key: str, content: bytes, content_type: str) -> None: ...
    def get(self, key: str) -> bytes: ...


class MemoryStorage:
    def __init__(self):
        self.objects: dict[str, bytes] = {}

    def put(self, key: str, content: bytes, content_type: str) -> None:
        self.objects[key] = content

    def get(self, key: str) -> bytes:
        return self.objects[key]


class MinioStorage:
    def __init__(self):
        settings = get_settings()
        self.bucket = settings.minio_bucket
        self.client = Minio(
            settings.minio_endpoint,
            access_key=settings.minio_access_key,
            secret_key=settings.minio_secret_key,
            secure=False,
        )
        if not self.client.bucket_exists(self.bucket):
            self.client.make_bucket(self.bucket)

    def put(self, key: str, content: bytes, content_type: str) -> None:
        self.client.put_object(self.bucket, key, io.BytesIO(content), len(content), content_type=content_type)

    def get(self, key: str) -> bytes:
        response = self.client.get_object(self.bucket, key)
        try:
            return response.read()
        finally:
            response.close()
            response.release_conn()


_memory_storage = MemoryStorage()


def get_storage() -> PrivateStorage:
    return MinioStorage() if get_settings().storage_provider == "minio" else _memory_storage

