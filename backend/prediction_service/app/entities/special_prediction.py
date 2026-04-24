"""Predicciones especiales con bonus:
  - CHAMPION     (campeon del torneo) -> 10 pts si acierta
  - RUNNER_UP    (subcampeon)          -> 5 pts
  - THIRD_PLACE  (tercer puesto)       -> 3 pts

Un usuario tiene a lo sumo una prediccion por cada tipo (unica por user+type).
"""
from datetime import datetime

from sqlalchemy import Boolean, DateTime, Integer, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from prediction_service.app.database import Base


TYPE_CHAMPION = "CHAMPION"
TYPE_RUNNER_UP = "RUNNER_UP"
TYPE_THIRD_PLACE = "THIRD_PLACE"
VALID_SPECIAL_TYPES = {TYPE_CHAMPION, TYPE_RUNNER_UP, TYPE_THIRD_PLACE}


class SpecialPrediction(Base):
    __tablename__ = "special_predictions"
    __table_args__ = (UniqueConstraint("user_id", "prediction_type", name="uq_user_specialtype"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[str] = mapped_column(String(36), nullable=False, index=True)
    prediction_type: Mapped[str] = mapped_column(String(30), nullable=False)
    team_id: Mapped[str] = mapped_column(String(36), nullable=False)
    is_locked: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow
    )
