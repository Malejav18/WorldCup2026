"""Prediccion de un usuario para un partido.

Unica por (user_id, match_id) - el upsert usa esa combinacion.

`is_locked=True` significa que el partido ya comenzo o finalizo y la
prediccion no puede editarse. Se activa via evento match.result.registered
(y en el futuro, match.started).
"""
from datetime import datetime

from sqlalchemy import Boolean, DateTime, Integer, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from prediction_service.app.database import Base


class Prediction(Base):
    __tablename__ = "predictions"
    __table_args__ = (UniqueConstraint("user_id", "match_id", name="uq_user_match"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[str] = mapped_column(String(36), nullable=False, index=True)
    match_id: Mapped[str] = mapped_column(String(36), nullable=False, index=True)

    predicted_home_goals_90: Mapped[int] = mapped_column(Integer, nullable=False)
    predicted_away_goals_90: Mapped[int] = mapped_column(Integer, nullable=False)

    # Para partidos donde los equipos no están definidos (ej R32), el usuario predice qué equipos juegan.
    predicted_home_team_id: Mapped[str | None] = mapped_column(String(36), nullable=True)
    predicted_away_team_id: Mapped[str | None] = mapped_column(String(36), nullable=True)

    # Requerido en eliminatorias; opcional en fase de grupos (puede haber empate).
    predicted_winner_id: Mapped[str | None] = mapped_column(String(36), nullable=True)
    predicted_goes_to_penalties: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)

    # Snapshot de la fase del partido al momento de la prediccion, para queries por fase.
    match_phase: Mapped[str] = mapped_column(String(20), nullable=False, default="GROUP")

    is_locked: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False, index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow
    )
