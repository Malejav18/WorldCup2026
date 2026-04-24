"""Entrada de scoring-service.

Ejecutar desde `backend/`:
    python -m uvicorn scoring_service.app.main:app --host 127.0.0.1 --port 8005 --reload
"""
import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from shared.outbox import OutboxDispatcher

from scoring_service.app.config import settings
from scoring_service.app.controllers.internal_controller import router as internal_router
from scoring_service.app.controllers.scoring_controller import router as scoring_router
from scoring_service.app.database import Base, SessionLocal, engine
from scoring_service.app.entities.outbox_event import OutboxEvent
from scoring_service.app.entities.score import Score  # noqa: F401


logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s: %(message)s")


@asynccontextmanager
async def lifespan(_app: FastAPI):
    Base.metadata.create_all(engine)
    dispatcher = OutboxDispatcher(
        session_factory=SessionLocal,
        outbox_model=OutboxEvent,
        service_urls={
            "user-service": "http://127.0.0.1:8002",
            "ranking-service": settings.ranking_service_url,
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

app.include_router(scoring_router)
app.include_router(internal_router)


@app.get("/health", tags=["infra"])
def health() -> dict:
    return {"status": "ok", "service": settings.service_name}
