"""Entrada de ranking-service.

Ejecutar desde `backend/`:
    python -m uvicorn ranking_service.app.main:app --host 127.0.0.1 --port 8006 --reload
"""
import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from ranking_service.app.config import settings
from ranking_service.app.controllers.internal_controller import router as internal_router
from ranking_service.app.controllers.ranking_controller import router as ranking_router
from ranking_service.app.database import Base, engine
from ranking_service.app.entities.user_ranking import UserRanking  # noqa: F401


logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s: %(message)s")


@asynccontextmanager
async def lifespan(_app: FastAPI):
    Base.metadata.create_all(engine)
    yield


app = FastAPI(title=settings.service_name, version="0.1.0", lifespan=lifespan)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(ranking_router)
app.include_router(internal_router)


@app.get("/health", tags=["infra"])
def health() -> dict:
    return {"status": "ok", "service": settings.service_name}
