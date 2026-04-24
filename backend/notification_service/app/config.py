"""Configuracion del notification-service.

Los "proveedores externos" (SendGrid, FCM, APNs) estan moqueados: las
notificaciones se persisten en SQL y se loguean a consola. En produccion se
reemplaza el MockSender por clientes reales de cada proveedor.
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

    service_name: str = "notification-service"
    host: str = "127.0.0.1"
    port: int = 8008
    database_path: Path = _SERVICE_DIR / "data" / "notification.db"

    jwt_secret: str = "dev-secret-change-me-please-make-this-long-and-random"


settings = Settings()
