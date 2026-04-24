from typing import Optional

from sqlalchemy.orm import Session

from league_service.app.entities.league_membership import LeagueMembership


class MembershipRepository:
    def __init__(self, db: Session):
        self.db = db

    def get(self, league_id: str, user_id: str) -> Optional[LeagueMembership]:
        return (
            self.db.query(LeagueMembership)
            .filter(LeagueMembership.league_id == league_id, LeagueMembership.user_id == user_id)
            .first()
        )

    def create(self, membership: LeagueMembership) -> LeagueMembership:
        self.db.add(membership)
        self.db.flush()
        return membership

    def delete(self, league_id: str, user_id: str) -> bool:
        m = self.get(league_id, user_id)
        if m is None:
            return False
        self.db.delete(m)
        return True

    def list_by_user(self, user_id: str) -> list[LeagueMembership]:
        return (
            self.db.query(LeagueMembership)
            .filter(LeagueMembership.user_id == user_id)
            .order_by(LeagueMembership.joined_at)
            .all()
        )

    def list_by_league(self, league_id: str) -> list[LeagueMembership]:
        return (
            self.db.query(LeagueMembership)
            .filter(LeagueMembership.league_id == league_id)
            .order_by(LeagueMembership.joined_at)
            .all()
        )

    def count_by_league(self, league_id: str) -> int:
        return (
            self.db.query(LeagueMembership)
            .filter(LeagueMembership.league_id == league_id)
            .count()
        )
