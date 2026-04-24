"""Pertenencia de un usuario a una liga.

Un usuario puede pertenecer a varias ligas; la UNIQUE sobre (league_id, user_id)
impide duplicados. `role` distingue al creador (ADMIN) del resto (MEMBER).
"""
from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Integer, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from league_service.app.database import Base


ROLE_ADMIN = "ADMIN"
ROLE_MEMBER = "MEMBER"


class LeagueMembership(Base):
    __tablename__ = "league_memberships"
    __table_args__ = (UniqueConstraint("league_id", "user_id", name="uq_league_user"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    league_id: Mapped[str] = mapped_column(String(36), ForeignKey("leagues.id"), nullable=False, index=True)
    user_id: Mapped[str] = mapped_column(String(36), nullable=False, index=True)
    role: Mapped[str] = mapped_column(String(20), nullable=False, default=ROLE_MEMBER)
    joined_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.utcnow)
