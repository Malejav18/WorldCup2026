from typing import Optional

from sqlalchemy import desc
from sqlalchemy.orm import Session

from ranking_service.app.entities.user_ranking import UserRanking


class UserRankingRepository:
    def __init__(self, db: Session):
        self.db = db

    def get(self, user_id: str) -> Optional[UserRanking]:
        return self.db.query(UserRanking).filter(UserRanking.user_id == user_id).first()

    def upsert(self, user_id: str, total_points: int) -> UserRanking:
        existing = self.get(user_id)
        if existing is None:
            row = UserRanking(user_id=user_id, total_points=total_points)
            self.db.add(row)
            self.db.flush()
            return row
        existing.total_points = total_points
        return existing

    def list_global(self, *, offset: int, limit: int) -> list[UserRanking]:
        return (
            self.db.query(UserRanking)
            .order_by(desc(UserRanking.total_points), UserRanking.user_id)
            .offset(offset)
            .limit(limit)
            .all()
        )

    def count_users(self) -> int:
        return self.db.query(UserRanking).count()

    def position_of(self, user_id: str) -> int | None:
        """Retorna la posicion 1-based del usuario. None si no existe en la tabla."""
        row = self.get(user_id)
        if row is None:
            return None
        # Posicion = cuantos usuarios tienen mas puntos + 1.
        # Desempate determinista por user_id asc si hay empate en puntos.
        higher = (
            self.db.query(UserRanking)
            .filter(
                (UserRanking.total_points > row.total_points)
                | (
                    (UserRanking.total_points == row.total_points)
                    & (UserRanking.user_id < row.user_id)
                )
            )
            .count()
        )
        return higher + 1
