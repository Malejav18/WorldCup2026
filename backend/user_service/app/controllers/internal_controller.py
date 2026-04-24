"""Endpoints internos para consumo de eventos publicados por otros servicios.

Estas rutas NO se exponen en el api-gateway; solo son llamadas por los
dispatcher de outbox de auth-service y (en el futuro) scoring-service.

Los handlers DEBEN ser idempotentes: el outbox es at-least-once y un mismo
evento puede llegar varias veces.
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from user_service.app.database import get_db
from user_service.app.dtos.user_dtos import (
    PointsUpdatedEvent,
    UserProfilePublic,
    UserProfileSelf,
    UserRegisteredEvent,
)
from user_service.app.services.user_service import UserError, UserService


router = APIRouter(prefix="/internal", tags=["internal"])


def get_user_service(db: Session = Depends(get_db)) -> UserService:
    return UserService(db)


@router.post("/events/user-registered", response_model=UserProfileSelf, status_code=status.HTTP_200_OK)
def on_user_registered(
    event: UserRegisteredEvent,
    svc: UserService = Depends(get_user_service),
) -> UserProfileSelf:
    """Consumidor de `auth.user.registered` (desde auth-service)."""
    profile = svc.handle_user_registered(event)
    return UserProfileSelf.model_validate(profile)


@router.post("/events/points-updated", status_code=status.HTTP_204_NO_CONTENT)
def on_points_updated(
    event: PointsUpdatedEvent,
    svc: UserService = Depends(get_user_service),
) -> None:
    """Consumidor de `scoring.user.points.updated` (desde scoring-service)."""
    svc.handle_points_updated(event)


@router.get("/users/{user_id}", response_model=UserProfilePublic)
def get_public_internal(
    user_id: str,
    svc: UserService = Depends(get_user_service),
) -> UserProfilePublic:
    """Consulta server-to-server (sin JWT). Usado por ranking-service para enriquecer
    el ranking con display_name. Expuesto solo en red interna (127.0.0.1)."""
    try:
        profile = svc.get_public(user_id)
    except UserError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    return UserProfilePublic.model_validate(profile)
