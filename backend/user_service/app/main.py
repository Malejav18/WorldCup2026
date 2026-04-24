"""Entrada de user-service.

Ejecutar desde `backend/`:
    python -m uvicorn user_service.app.main:app --host 127.0.0.1 --port 8002 --reload

user-service solo consume eventos (no publica), asi que no corre el dispatcher
de outbox; solo expone endpoints /internal/events/* como entrada.
"""
import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from user_service.app.config import settings
from user_service.app.controllers.internal_controller import router as internal_router
from user_service.app.controllers.user_controller import router as user_router
from user_service.app.database import Base, engine
from user_service.app.entities.user_profile import UserProfile  # noqa: F401


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

app.include_router(user_router)
app.include_router(internal_router)


@app.get("/health", tags=["infra"])
def health() -> dict:
    return {"status": "ok", "service": settings.service_name}
