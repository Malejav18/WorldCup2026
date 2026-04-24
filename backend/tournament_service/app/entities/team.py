"""Equipo participante (seleccion nacional)."""
from sqlalchemy import String, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column

from tournament_service.app.database import Base


class Team(Base):
    __tablename__ = "teams"

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    name: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    country_code: Mapped[str] = mapped_column(String(3), unique=True, nullable=False)
    confederation: Mapped[str] = mapped_column(String(20), nullable=False)  # UEFA, CONMEBOL, etc.
    group_id: Mapped[str | None] = mapped_column(String(36), ForeignKey("groups.id"), nullable=True, index=True)
