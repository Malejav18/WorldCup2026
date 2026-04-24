"""Endpoints publicos del notification-service."""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from shared.auth_dependency import AuthenticatedUser, build_current_user_dependency

from notification_service.app.config import settings
from notification_service.app.database import get_db
from notification_service.app.dtos.notification_dtos import NotificationPublic
from notification_service.app.services.notification_service import NotificationService


router = APIRouter(prefix="/notifications", tags=["notifications"])

_get_current_user = build_current_user_dependency(settings.jwt_secret)


def get_notification_service(db: Session = Depends(get_db)) -> NotificationService:
    return NotificationService(db)


@router.get("/me", response_model=list[NotificationPublic])
def list_mine(
    current: AuthenticatedUser = Depends(_get_current_user),
    svc: NotificationService = Depends(get_notification_service),
) -> list[NotificationPublic]:
    items = svc.list_for_user(current.user_id)
    return [NotificationPublic.model_validate(n) for n in items]


@router.get("/me/unread-count")
def unread_count(
    current: AuthenticatedUser = Depends(_get_current_user),
    svc: NotificationService = Depends(get_notification_service),
) -> dict:
    return {"unread": svc.unread_count(current.user_id)}


@router.put("/me/{notification_id}/read", response_model=NotificationPublic)
def mark_read(
    notification_id: int,
    current: AuthenticatedUser = Depends(_get_current_user),
    svc: NotificationService = Depends(get_notification_service),
) -> NotificationPublic:
    notif = svc.mark_read(notification_id, current.user_id)
    if notif is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Notification not found")
    return NotificationPublic.model_validate(notif)
