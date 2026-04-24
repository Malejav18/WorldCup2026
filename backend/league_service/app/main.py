"""Entrada de league-service.

Ejecutar desde `backend/`:
    python -m uvicorn league_service.app.main:app --host 127.0.0.1 --port 8007 --reload
"""
import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from shared.outbox import OutboxDispatcher

from league_service.app.config import settings
from league_service.app.controllers.league_controller import router as league_router
from league_service.app.database import Base, SessionLocal, engine
from league_service.app.entities.league import League  # noqa: F401
from league_service.app.entities.league_membership import LeagueMembership  # noqa: F401
from league_service.app.entities.outbox_event import OutboxEvent


logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s: %(message)s")


@asynccontextmanager
async def lifespan(_app: FastAPI):
    Base.metadata.create_all(engine)
    dispatcher = OutboxDispatcher(
        session_factory=SessionLocal,
        outbox_model=OutboxEvent,
        service_urls={
            "ranking-service": "http://127.0.0.1:8006",
            "notification-service": settings.notification_service_url,
        },
    )
    dispatcher.start()
    try:
        yield
    finally:
        await dispatcher.stop()


app = FastAPI(title=settings.service_name, version="0.1.0", lifespan=lifespan)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(league_router)


@app.get("/health", tags=["infra"])
def health() -> dict:
    return {"status": "ok", "service": settings.service_name}
