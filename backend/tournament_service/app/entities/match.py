"""Partido del torneo.

`phase` es uno de: GROUP, R32, R16, QF, SF, THIRD_PLACE, FINAL.
`status` es uno de: SCHEDULED, LIVE, FINISHED.
"""
from datetime import datetime

from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from tournament_service.app.database import Base


# Fases
PHASE_GROUP = "GROUP"
PHASE_R32 = "R32"
PHASE_R16 = "R16"
PHASE_QF = "QF"
PHASE_SF = "SF"
PHASE_THIRD_PLACE = "THIRD_PLACE"
PHASE_FINAL = "FINAL"

# Estados
STATUS_SCHEDULED = "SCHEDULED"
STATUS_LIVE = "LIVE"
STATUS_FINISHED = "FINISHED"


class Match(Base):
    __tablename__ = "matches"

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    match_number: Mapped[int] = mapped_column(Integer, unique=True, nullable=False)
    phase: Mapped[str] = mapped_column(String(20), nullable=False, index=True)

    # En fase de grupos ambos equipos se conocen de entrada.
    # En eliminatorias pueden ser NULL al inicio y fijarse al avanzar el bracket.
    home_team_id: Mapped[str | None] = mapped_column(String(36), ForeignKey("teams.id"), nullable=True)
    away_team_id: Mapped[str | None] = mapped_column(String(36), ForeignKey("teams.id"), nullable=True)

    # Slot del bracket (ej "1A", "2B", "R32-winner-3") para resolver equipos cuando avanzan.
    home_team_slot: Mapped[str | None] = mapped_column(String(30), nullable=True)
    away_team_slot: Mapped[str | None] = mapped_column(String(30), nullable=True)

    group_id: Mapped[str | None] = mapped_column(String(36), ForeignKey("groups.id"), nullable=True)

    scheduled_at: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    status: Mapped[str] = mapped_column(String(20), nullable=False, default=STATUS_SCHEDULED, index=True)

    # Marcador a los 90 minutos (obligatorio al finalizar).
    home_goals_90: Mapped[int | None] = mapped_column(Integer, nullable=True)
    away_goals_90: Mapped[int | None] = mapped_column(Integer, nullable=True)

    # Solo aplica a eliminatorias que se empatan a 90'.
    went_to_extra_time: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    went_to_penalties: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    home_goals_final: Mapped[int | None] = mapped_column(Integer, nullable=True)
    away_goals_final: Mapped[int | None] = mapped_column(Integer, nullable=True)

    winner_id: Mapped[str | None] = mapped_column(String(36), ForeignKey("teams.id"), nullable=True)
