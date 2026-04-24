"""Consumidores de eventos publicados por otros microservicios.

Todos los handlers son idempotentes en la practica: reentregar el mismo evento
simplemente agrega una nueva fila en la tabla notifications (es un log). Si se
quisiera deduplicar, se podria usar una tabla processed_events con el id del
outbox como clave unica, pero para un sistema de notificaciones academico
duplicar un mensaje no corrompe el estado.
"""
from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from notification_service.app.database import get_db
from notification_service.app.dtos.notification_dtos import (
    LeagueMemberAddedEvent,
    MatchCalculatedEvent,
    MatchResultEvent,
    PointsUpdatedEvent,
    StandingsUpdatedEvent,
    UserRegisteredEvent,
)
from notification_service.app.services.notification_service import NotificationService


router = APIRouter(prefix="/internal/events", tags=["internal"])


def get_notification_service(db: Session = Depends(get_db)) -> NotificationService:
    return NotificationService(db)


@router.post("/user-registered", status_code=status.HTTP_200_OK)
def on_user_registered(
    event: UserRegisteredEvent,
    svc: NotificationService = Depends(get_notification_service),
) -> dict:
    notif = svc.on_user_registered(event)
    return {"notification_id": notif.id, "channel": notif.channel}


@router.post("/match-result", status_code=status.HTTP_200_OK)
def on_match_result(
    event: MatchResultEvent,
    svc: NotificationService = Depends(get_notification_service),
) -> dict:
    svc.on_match_result(event)
    return {"ok": True}


@router.post("/match-calculated", status_code=status.HTTP_200_OK)
def on_match_calculated(
    event: MatchCalculatedEvent,
    svc: NotificationService = Depends(get_notification_service),
) -> dict:
    notif = svc.on_match_calculated(event)
    return {"notification_id": notif.id}


@router.post("/points-updated", status_code=status.HTTP_200_OK)
def on_points_updated(
    event: PointsUpdatedEvent,
    svc: NotificationService = Depends(get_notification_service),
) -> dict:
    notif = svc.on_points_updated(event)
    return {"notification_id": notif.id}


@router.post("/standings-updated", status_code=status.HTTP_200_OK)
def on_standings_updated(
    event: StandingsUpdatedEvent,
    svc: NotificationService = Depends(get_notification_service),
) -> dict:
    notif = svc.on_standings_updated(event)
    return {"notification_id": notif.id}


@router.post("/league-member-added", status_code=status.HTTP_200_OK)
def on_league_member_added(
    event: LeagueMemberAddedEvent,
    svc: NotificationService = Depends(get_notification_service),
) -> dict:
    notif = svc.on_league_member_added(event)
    return {"notification_id": notif.id}
