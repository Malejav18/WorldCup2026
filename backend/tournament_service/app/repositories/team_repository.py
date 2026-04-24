from typing import Optional

from sqlalchemy.orm import Session

from tournament_service.app.entities.team import Team


class TeamRepository:
    def __init__(self, db: Session):
        self.db = db

    def list_all(self) -> list[Team]:
        return self.db.query(Team).order_by(Team.name).all()

    def list_by_group(self, group_id: str) -> list[Team]:
        return self.db.query(Team).filter(Team.group_id == group_id).order_by(Team.name).all()

    def get(self, team_id: str) -> Optional[Team]:
        return self.db.query(Team).filter(Team.id == team_id).first()

    def get_by_country_code(self, code: str) -> Optional[Team]:
        return self.db.query(Team).filter(Team.country_code == code).first()
