from typing import Optional

from sqlalchemy.orm import Session

from league_service.app.entities.league import League


class LeagueRepository:
    def __init__(self, db: Session):
        self.db = db

    def create(self, league: League) -> League:
        self.db.add(league)
        self.db.flush()
        return league

    def get(self, league_id: str) -> Optional[League]:
        return self.db.query(League).filter(League.id == league_id).first()

    def get_by_invite_code(self, invite_code: str) -> Optional[League]:
        return self.db.query(League).filter(League.invite_code == invite_code).first()

    def update_invite_code(self, league_id: str, new_code: str) -> Optional[League]:
        league = self.get(league_id)
        if league is not None:
            league.invite_code = new_code
        return league
