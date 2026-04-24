from sqlalchemy.orm import DeclarativeBase

from shared.database import build_engine, build_session_factory

from notification_service.app.config import settings


class Base(DeclarativeBase):
    pass


engine = build_engine(settings.database_path)
SessionLocal = build_session_factory(engine)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
