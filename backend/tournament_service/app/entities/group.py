"""Grupo de fase inicial (12 grupos: A..L con 4 equipos cada uno)."""
from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column

from tournament_service.app.database import Base


class Group(Base):
    __tablename__ = "groups"

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    letter: Mapped[str] = mapped_column(String(1), unique=True, nullable=False)  # A..L
    name: Mapped[str] = mapped_column(String(50), nullable=False)  # "Grupo A"
