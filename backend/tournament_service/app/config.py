"""Configuracion del tournament-service."""
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

    service_name: str = "tournament-service"
    host: str = "127.0.0.1"
    port: int = 8003

    database_path: Path = _SERVICE_DIR / "data" / "tournament.db"

    jwt_secret: str = "dev-secret-change-me-please-make-this-long-and-random"

    # Destinos de eventos (consumidores de los events publicados por tournament)
    scoring_service_url: str = "http://127.0.0.1:8005"
    prediction_service_url: str = "http://127.0.0.1:8004"
    notification_service_url: str = "http://127.0.0.1:8008"


settings = Settings()
