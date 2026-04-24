from datetime import datetime

from sqlalchemy import desc
from sqlalchemy.orm import Session

from notification_service.app.entities.notification import Notification


class NotificationRepository:
    def __init__(self, db: Session):
        self.db = db

    def create(self, notification: Notification) -> Notification:
        self.db.add(notification)
        self.db.flush()
        return notification

    def list_by_user(self, user_id: str, *, limit: int = 50) -> list[Notification]:
        return (
            self.db.query(Notification)
            .filter(Notification.user_id == user_id)
            .order_by(desc(Notification.created_at))
            .limit(limit)
            .all()
        )

    def count_unread_by_user(self, user_id: str) -> int:
        return (
            self.db.query(Notification)
            .filter(Notification.user_id == user_id, Notification.read_at.is_(None))
            .count()
        )

    def mark_read(self, notification_id: int, user_id: str) -> Notification | None:
        notif = (
            self.db.query(Notification)
            .filter(Notification.id == notification_id, Notification.user_id == user_id)
            .first()
        )
        if notif is not None and notif.read_at is None:
            notif.read_at = datetime.utcnow()
        return notif
