"""Tabla outbox_events local a auth-service (ver shared.outbox para detalles del patron)."""
from shared.outbox import OutboxEventMixin

from auth_service.app.database import Base


class OutboxEvent(Base, OutboxEventMixin):
    __tablename__ = "outbox_events"
