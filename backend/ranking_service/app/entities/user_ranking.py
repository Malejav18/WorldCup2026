"""Ranking del usuario en el torneo global.

Version SQL del Sorted Set de Redis que proponia el PDF: usamos un indice sobre
`total_points DESC` para consultas O(log N) de posicion. Para 100k usuarios
con SQLite es subideal pero funcional para proyecto academico.
"""
from datetime import datetime

from sqlalchemy import DateTime, Index, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from ranking_service.app.database import Base


class UserRanking(Base):
    __tablename__ = "user_rankings"
    __table_args__ = (
        Index("ix_ranking_points_desc", "total_points"),
    )

    user_id: Mapped[str] = mapped_column(String(36), primary_key=True)
    total_points: Mapped[int] = mapped_column(Integer, nullable=False, default=0, index=True)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow
    )
