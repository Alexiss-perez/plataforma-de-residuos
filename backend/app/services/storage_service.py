from __future__ import annotations

import os
import uuid
from abc import ABC, abstractmethod

from app.core.config import settings


class StorageService(ABC):
    @abstractmethod
    def upload(self, data: bytes, filename: str, content_type: str = "application/octet-stream") -> str:
        ...


class LocalStorage(StorageService):
    def __init__(self, base_path: str | None = None) -> None:
        self.base_path = base_path or settings.STORAGE_LOCAL_PATH
        os.makedirs(self.base_path, exist_ok=True)

    def upload(self, data: bytes, filename: str, content_type: str = "application/octet-stream") -> str:
        ext = os.path.splitext(filename)[1]
        safe_name = f"{uuid.uuid4().hex}{ext}"
        path = os.path.join(self.base_path, safe_name)
        with open(path, "wb") as f:
            f.write(data)
        return f"/uploads/{safe_name}"


class HuaweiOBSStorage(StorageService):
    """Adapter for Huawei Object Storage Service.

    Prepared for production. Requires OBS_ACCESS_KEY / OBS_SECRET_KEY.
    Falls back gracefully if esdk is not installed (not a hard dependency for dev/tests).
    """

    def __init__(self) -> None:
        self.access_key = settings.OBS_ACCESS_KEY
        self.secret_key = settings.OBS_SECRET_KEY
        self.bucket = settings.OBS_BUCKET
        self.endpoint = settings.OBS_ENDPOINT
        self._client = None
        try:
            from obs import ObsClient  # type: ignore

            if self.access_key and self.secret_key and self.endpoint:
                self._client = ObsClient(
                    access_key_id=self.access_key,
                    secret_access_key=self.secret_key,
                    server=self.endpoint,
                )
        except ImportError:
            pass

    def upload(self, data: bytes, filename: str, content_type: str = "application/octet-stream") -> str:
        if self._client is None:
            raise RuntimeError("Huawei OBS client is not configured. Set OBS credentials and install esdk-obs-python.")
        ext = os.path.splitext(filename)[1]
        key = f"uploads/{uuid.uuid4().hex}{ext}"
        self._client.putContent(self.bucket, key, content=data, contentType=content_type)
        return f"https://{self.bucket}.{self.endpoint}/{key}"


def get_storage_service() -> StorageService:
    provider = settings.STORAGE_PROVIDER.lower()
    if provider == "huawei_obs":
        return HuaweiOBSStorage()
    return LocalStorage()
