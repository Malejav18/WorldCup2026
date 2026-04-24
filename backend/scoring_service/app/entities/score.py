"""Fila de puntuacion persistida.

Clave compuesta unica (user_id, match_id): garantiza idempotencia ante
reentregas del evento `match.result.registered` o correcciones.

`prediction_snapshot` y `result_snapshot` son JSON string con copia del estado
al momento del calculo (util para auditoria y explicacion de puntos).
"""
from datetime import datetime

from sqlalchemy import Boolean, DateTime, Integer, String, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from scoring_service.app.database import Base


class Score(Base):
    __tablename__ = "scores"
    __table_args__ = (UniqueConstraint("user_id", "match_id", name="uq_user_match_score"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[str] = mapped_column(String(36), nullable=False, index=True)
    match_id: Mapped[str] = mapped_column(String(36), nullable=False, index=True)

    phase: Mapped[str] = mapped_column(String(20), nullable=False)  # GROUP, R32, R16, QF, SF, FINAL...
    reason: Mapped[str] = mapped_column(String(40), nullable=False)  # "exact_score", "correct_result", "wrong"

    prediction_snapshot: Mapped[str] = mapped_column(Text, nullable=False)
    result_snapshot: Mapped[str] = mapped_column(Text, nullable=False)

    points_base: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    points_bonus: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    points_total: Mapped[int] = mapped_column(Integer, nullable=False, default=0)

    is_from_correction: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow
    )
