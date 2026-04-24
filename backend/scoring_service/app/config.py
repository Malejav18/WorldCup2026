"""Configuracion del scoring-service.

La tabla de puntuacion es configurable; los valores por defecto corresponden al
PDF del proyecto.
"""
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

    service_name: str = "scoring-service"
    host: str = "127.0.0.1"
    port: int = 8005
    database_path: Path = _SERVICE_DIR / "data" / "scoring.db"

    jwt_secret: str = "dev-secret-change-me-please-make-this-long-and-random"

    # Puntos por fase (externalizados - el admin podria modificarlos sin recompilar).
    points_group_exact: int = 3
    points_group_result: int = 1
    points_knockout_exact: int = 4
    points_knockout_winner: int = 2

    # URLs downstream.
    prediction_service_url: str = "http://127.0.0.1:8004"
    user_service_url: str = "http://127.0.0.1:8002"
    ranking_service_url: str = "http://127.0.0.1:8006"
    notification_service_url: str = "http://127.0.0.1:8008"


settings = Settings()
