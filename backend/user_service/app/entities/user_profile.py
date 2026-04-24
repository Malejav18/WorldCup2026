"""Perfil publico del usuario.

El `id` es el mismo UUID que user_service recibe de auth-service via el evento
`auth.user.registered`. Es el mismo `sub` del JWT, asi que userId es unico
entre ambos servicios aunque vivan en BDs distintas.
"""
from datetime import datetime

from sqlalchemy import DateTime, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from user_service.app.database import Base


class UserProfile(Base):
    __tablename__ = "user_profiles"

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    display_name: Mapped[str] = mapped_column(String(100), nullable=False)
    avatar_url: Mapped[str | None] = mapped_column(Text, nullable=True)
    timezone: Mapped[str] = mapped_column(String(50), nullable=False, default="America/Bogota")
    language: Mapped[str] = mapped_column(String(10), nullable=False, default="es")
    total_points: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    global_rank: Mapped[int | None] = mapped_column(Integer, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow
    )
