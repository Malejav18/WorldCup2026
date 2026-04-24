"""Liga privada creada por un usuario (creator).

`invite_code` es un token corto, unico, que cualquiera con el puede unirse
a la liga. El creador puede regenerarlo.
"""
from datetime import datetime

from sqlalchemy import DateTime, String
from sqlalchemy.orm import Mapped, mapped_column

from league_service.app.database import Base


class League(Base):
    __tablename__ = "leagues"

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    description: Mapped[str | None] = mapped_column(String(500), nullable=True)
    created_by_user_id: Mapped[str] = mapped_column(String(36), nullable=False, index=True)
    invite_code: Mapped[str] = mapped_column(String(16), unique=True, nullable=False, index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.utcnow)
