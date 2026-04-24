"""Configuracion del api-gateway."""
from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict


_BACKEND_DIR = Path(__file__).resolve().parents[1]


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=_BACKEND_DIR / ".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    service_name: str = "api-gateway"
    host: str = "127.0.0.1"
    port: int = 8000

    # URLs downstream
    auth_service_url: str = "http://127.0.0.1:8001"
    user_service_url: str = "http://127.0.0.1:8002"
    tournament_service_url: str = "http://127.0.0.1:8003"
    prediction_service_url: str = "http://127.0.0.1:8004"
    scoring_service_url: str = "http://127.0.0.1:8005"
    ranking_service_url: str = "http://127.0.0.1:8006"
    league_service_url: str = "http://127.0.0.1:8007"
    notification_service_url: str = "http://127.0.0.1:8008"


settings = Settings()
