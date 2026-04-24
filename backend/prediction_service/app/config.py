"""Configuracion del prediction-service."""
from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict


_SERVICE_DIR = Path(__file__).resolve().parents[1]
_BACKEND_DIR = Path(__file__).resolve().parents[2]


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=_BACKEND_DIR / ".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    service_name: str = "prediction-service"
    host: str = "127.0.0.1"
    port: int = 8004
    database_path: Path = _SERVICE_DIR / "data" / "prediction.db"

    jwt_secret: str = "dev-secret-change-me-please-make-this-long-and-random"

    # Para validar que el match existe al crear una prediccion.
    tournament_service_url: str = "http://127.0.0.1:8003"


settings = Settings()
