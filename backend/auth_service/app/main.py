"""Entrada de auth-service: FastAPI + lifespan que arranca el outbox dispatcher.

Ejecutar desde `backend/`:
    python -m uvicorn auth_service.app.main:app --host 127.0.0.1 --port 8001 --reload
"""
import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from shared.outbox import OutboxDispatcher

from auth_service.app.config import settings
from auth_service.app.controllers.auth_controller import router as auth_router
from auth_service.app.database import Base, SessionLocal, engine

# Importar las entidades para que SQLAlchemy las registre antes de create_all.
from auth_service.app.entities.outbox_event import OutboxEvent
from auth_service.app.entities.refresh_token import RefreshToken  # noqa: F401
from auth_service.app.entities.user import User  # noqa: F401


logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s: %(message)s")


@asynccontextmanager
async def lifespan(_app: FastAPI):
    # Crea tablas si no existen (para proyecto academico; en produccion usar Alembic).
    Base.metadata.create_all(engine)

    dispatcher = OutboxDispatcher(
        session_factory=SessionLocal,
        outbox_model=OutboxEvent,
        service_urls={
            "user-service": settings.user_service_url,
            "notification-service": settings.notification_service_url,
        },
    )
    dispatcher.start()
    try:
        yield
    finally:
        await dispatcher.stop()


app = FastAPI(title=settings.service_name, version="0.1.0", lifespan=lifespan)

# CORS abierto en dev; en prod restringir a los origenes del frontend.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router)


@app.get("/health", tags=["infra"])
def health() -> dict:
    return {"status": "ok", "service": settings.service_name}
