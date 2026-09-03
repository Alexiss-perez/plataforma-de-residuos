from __future__ import annotations

from functools import lru_cache
from typing import List

from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    APP_NAME: str = "ReVinculo"
    ENVIRONMENT: str = "development"

    DATABASE_URL: str = "sqlite:///./revinculo.db"

    JWT_SECRET: str = "change-me"
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 1440

    CORS_ORIGINS: str = "http://localhost:5173,http://localhost:3000"

    AI_BASE_URL: str = "https://ai.kostra.cloud/v1"
    AI_API_KEY: str = ""
    AI_MODEL: str = "glm-5.2"

    STORAGE_PROVIDER: str = "local"
    STORAGE_LOCAL_PATH: str = "./uploads"

    OBS_ACCESS_KEY: str = ""
    OBS_SECRET_KEY: str = ""
    OBS_BUCKET: str = ""
    OBS_ENDPOINT: str = ""

    @field_validator("DATABASE_URL", mode="before")
    @classmethod
    def _normalize_db_url(cls, v: str) -> str:
        if isinstance(v, str) and v.startswith("postgres://"):
            return v.replace("postgres://", "postgresql://", 1)
        return v

    @property
    def cors_origins_list(self) -> List[str]:
        return [o.strip() for o in self.CORS_ORIGINS.split(",") if o.strip()]


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
