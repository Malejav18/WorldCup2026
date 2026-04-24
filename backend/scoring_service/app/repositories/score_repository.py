from typing import Optional

from sqlalchemy import func
from sqlalchemy.orm import Session

from scoring_service.app.entities.score import Score


class ScoreRepository:
    def __init__(self, db: Session):
        self.db = db

    def get(self, user_id: str, match_id: str) -> Optional[Score]:
        return (
            self.db.query(Score)
            .filter(Score.user_id == user_id, Score.match_id == match_id)
            .first()
        )

    def list_by_user(self, user_id: str) -> list[Score]:
        return (
            self.db.query(Score)
            .filter(Score.user_id == user_id)
            .order_by(Score.created_at)
            .all()
        )

    def list_by_match(self, match_id: str) -> list[Score]:
        return self.db.query(Score).filter(Score.match_id == match_id).all()

    def upsert(self, score: Score) -> Score:
        """Crea o actualiza la fila (user_id, match_id). Devuelve la fila persistida."""
        existing = self.get(score.user_id, score.match_id)
        if existing is None:
            self.db.add(score)
            self.db.flush()
            return score
        existing.phase = score.phase
        existing.reason = score.reason
        existing.prediction_snapshot = score.prediction_snapshot
        existing.result_snapshot = score.result_snapshot
        existing.points_base = score.points_base
        existing.points_bonus = score.points_bonus
        existing.points_total = score.points_total
        existing.is_from_correction = score.is_from_correction
        return existing

    def total_points_for_user(self, user_id: str) -> int:
        total = (
            self.db.query(func.coalesce(func.sum(Score.points_total), 0))
            .filter(Score.user_id == user_id)
            .scalar()
        )
        return int(total or 0)

    def count_for_user(self, user_id: str) -> int:
        return self.db.query(Score).filter(Score.user_id == user_id).count()
