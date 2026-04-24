"""Configuracion del auth-service (se lee del .env del root backend/)."""
from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict


# __file__ = backend/auth_service/app/config.py
# parents[1] = backend/auth_service/ (raiz del servicio)
# parents[2] = backend/                (donde vive .env)
_SERVICE_DIR = Path(__file__).resolve().parents[1]
_BACKEND_DIR = Path(__file__).resolve().parents[2]


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=_BACKEND_DIR / ".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    service_name: str = "auth-service"
    host: str = "127.0.0.1"
    port: int = 8001

    database_path: Path = _SERVICE_DIR / "data" / "auth.db"

    jwt_secret: str = "dev-secret-change-me-please-make-this-long-and-random"
    access_token_minutes: int = 15
    refresh_token_days: int = 30

    user_service_url: str = "http://127.0.0.1:8002"
    notification_service_url: str = "http://127.0.0.1:8008"


settings = Settings()
