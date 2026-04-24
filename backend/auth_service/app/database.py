"""Setup del engine y session factory local de auth-service."""
from sqlalchemy.orm import DeclarativeBase

from shared.database import build_engine, build_session_factory

from auth_service.app.config import settings


class Base(DeclarativeBase):
    """Base declarativa aislada para este servicio."""


engine = build_engine(settings.database_path)
SessionLocal = build_session_factory(engine)


def get_db():
    """Dependencia FastAPI: abre una sesion por request."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
