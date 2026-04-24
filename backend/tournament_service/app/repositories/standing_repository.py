from typing import Optional

from sqlalchemy.orm import Session

from tournament_service.app.entities.group_standing import GroupStanding


class StandingRepository:
    def __init__(self, db: Session):
        self.db = db

    def get(self, group_id: str, team_id: str) -> Optional[GroupStanding]:
        return (
            self.db.query(GroupStanding)
            .filter(GroupStanding.group_id == group_id, GroupStanding.team_id == team_id)
            .first()
        )

    def list_by_group(self, group_id: str) -> list[GroupStanding]:
        return (
            self.db.query(GroupStanding)
            .filter(GroupStanding.group_id == group_id)
            .order_by(GroupStanding.position, GroupStanding.id)
            .all()
        )

    def list_all(self) -> list[GroupStanding]:
        return self.db.query(GroupStanding).all()

    def upsert(self, standing: GroupStanding) -> GroupStanding:
        existing = self.get(standing.group_id, standing.team_id)
        if existing is None:
            self.db.add(standing)
            self.db.flush()
            return standing
        existing.position = standing.position
        existing.played = standing.played
        existing.won = standing.won
        existing.drawn = standing.drawn
        existing.lost = standing.lost
        existing.goals_for = standing.goals_for
        existing.goals_against = standing.goals_against
        existing.goal_difference = standing.goal_difference
        existing.points = standing.points
        return existing
