"""Registro de una notificacion enviada (o simulada) a un usuario.

En produccion, `status` distingue PENDING/SENT/FAILED segun la respuesta del
proveedor externo. En el mock siempre se persiste como SENT inmediatamente,
con el `external_reference` como id simulado del proveedor.
"""
from datetime import datetime

from sqlalchemy import DateTime, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from notification_service.app.database import Base


# Canales
CHANNEL_EMAIL = "EMAIL"
CHANNEL_PUSH = "PUSH"

# Estados
STATUS_PENDING = "PENDING"
STATUS_SENT = "SENT"
STATUS_FAILED = "FAILED"


class Notification(Base):
    __tablename__ = "notifications"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[str] = mapped_column(String(36), nullable=False, index=True)

    event_type: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    channel: Mapped[str] = mapped_column(String(20), nullable=False)

    subject: Mapped[str] = mapped_column(String(200), nullable=False)
    body: Mapped[str] = mapped_column(Text, nullable=False)

    status: Mapped[str] = mapped_column(String(20), nullable=False, default=STATUS_SENT)
    external_reference: Mapped[str | None] = mapped_column(String(100), nullable=True)

    read_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.utcnow)
    sent_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True, default=datetime.utcnow)
