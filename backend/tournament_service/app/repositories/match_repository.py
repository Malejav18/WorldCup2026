from typing import Optional

from sqlalchemy.orm import Session

from tournament_service.app.entities.match import Match


class MatchRepository:
    def __init__(self, db: Session):
        self.db = db

    def get(self, match_id: str) -> Optional[Match]:
        return self.db.query(Match).filter(Match.id == match_id).first()

    def list_all(
        self,
        *,
        phase: Optional[str] = None,
        status: Optional[str] = None,
        group_id: Optional[str] = None,
    ) -> list[Match]:
        q = self.db.query(Match)
        if phase is not None:
            q = q.filter(Match.phase == phase)
        if status is not None:
            q = q.filter(Match.status == status)
        if group_id is not None:
            q = q.filter(Match.group_id == group_id)
        return q.order_by(Match.scheduled_at, Match.match_number).all()

    def list_finished_in_group(self, group_id: str) -> list[Match]:
        from tournament_service.app.entities.match import STATUS_FINISHED

        return (
            self.db.query(Match)
            .filter(Match.group_id == group_id, Match.status == STATUS_FINISHED)
            .all()
        )

    def next_scheduled(self) -> Optional[Match]:
        from tournament_service.app.entities.match import STATUS_SCHEDULED

        return (
            self.db.query(Match)
            .filter(Match.status == STATUS_SCHEDULED)
            .order_by(Match.scheduled_at, Match.match_number)
            .first()
        )

    def count(self) -> int:
        return self.db.query(Match).count()

    def count_finished(self) -> int:
        from tournament_service.app.entities.match import STATUS_FINISHED

        return self.db.query(Match).filter(Match.status == STATUS_FINISHED).count()
