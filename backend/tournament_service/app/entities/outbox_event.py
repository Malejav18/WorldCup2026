from shared.outbox import OutboxEventMixin

from tournament_service.app.database import Base


class OutboxEvent(Base, OutboxEventMixin):
    __tablename__ = "outbox_events"
