"""Entrada de tournament-service.

Ejecutar desde `backend/`:
    python -m uvicorn tournament_service.app.main:app --host 127.0.0.1 --port 8003 --reload
"""
import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from shared.outbox import OutboxDispatcher

from tournament_service.app.config import settings
from tournament_service.app.controllers.admin_controller import router as admin_router
from tournament_service.app.controllers.tournament_controller import router as tournament_router
from tournament_service.app.database import Base, SessionLocal, engine

# Importar las entidades para que queden registradas antes de create_all.
from tournament_service.app.entities.group import Group  # noqa: F401
from tournament_service.app.entities.group_standing import GroupStanding  # noqa: F401
from tournament_service.app.entities.match import Match  # noqa: F401
from tournament_service.app.entities.outbox_event import OutboxEvent
from tournament_service.app.entities.team import Team  # noqa: F401
from tournament_service.app.entities.tournament_state import TournamentState  # noqa: F401


logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s: %(message)s")


@asynccontextmanager
async def lifespan(_app: FastAPI):
    Base.metadata.create_all(engine)

    dispatcher = OutboxDispatcher(
        session_factory=SessionLocal,
        outbox_model=OutboxEvent,
        service_urls={
            "scoring-service": settings.scoring_service_url,
            "prediction-service": settings.prediction_service_url,
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

app.include_router(tournament_router)
app.include_router(admin_router)


@app.get("/health", tags=["infra"])
def health() -> dict:
    return {"status": "ok", "service": settings.service_name}
