"""Estado global del torneo (unica fila).

Estados:
  PRE_START       - antes del 11 jun 2026 (predicciones abiertas)
  GROUP_STAGE     - fase de grupos en curso
  BRACKET_LOCKING - entre fin de grupos y Ronda de 32 (corto periodo de prediccion)
  R32, R16, QF, SF, THIRD_PLACE, FINAL - rondas eliminatorias
  FINISHED        - torneo terminado
"""
from datetime import datetime

from sqlalchemy import DateTime, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from tournament_service.app.database import Base


STATE_PRE_START = "PRE_START"
STATE_GROUP_STAGE = "GROUP_STAGE"
STATE_BRACKET_LOCKING = "BRACKET_LOCKING"
STATE_R32 = "R32"
STATE_R16 = "R16"
STATE_QF = "QF"
STATE_SF = "SF"
STATE_THIRD_PLACE = "THIRD_PLACE"
STATE_FINAL = "FINAL"
STATE_FINISHED = "FINISHED"


class TournamentState(Base):
    __tablename__ = "tournament_state"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, default=1)
    status: Mapped[str] = mapped_column(String(30), nullable=False, default=STATE_PRE_START)
    updated_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.utcnow)
