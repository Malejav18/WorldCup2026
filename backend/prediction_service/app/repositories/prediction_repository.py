from typing import Optional

from sqlalchemy.orm import Session

from prediction_service.app.entities.prediction import Prediction


class PredictionRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_by_user_and_match(self, user_id: str, match_id: str) -> Optional[Prediction]:
        return (
            self.db.query(Prediction)
            .filter(Prediction.user_id == user_id, Prediction.match_id == match_id)
            .first()
        )

    def list_by_user(self, user_id: str) -> list[Prediction]:
        return (
            self.db.query(Prediction)
            .filter(Prediction.user_id == user_id)
            .order_by(Prediction.match_id)
            .all()
        )

    def list_by_user_and_phase(self, user_id: str, phase: str) -> list[Prediction]:
        return (
            self.db.query(Prediction)
            .filter(Prediction.user_id == user_id, Prediction.match_phase == phase)
            .order_by(Prediction.match_id)
            .all()
        )

    def list_by_match(self, match_id: str) -> list[Prediction]:
        """Usado por scoring-service via /internal para puntuar todas las predicciones."""
        return self.db.query(Prediction).filter(Prediction.match_id == match_id).all()

    def create(self, prediction: Prediction) -> Prediction:
        self.db.add(prediction)
        self.db.flush()
        return prediction

    def lock_for_match(self, match_id: str) -> int:
        """Marca como bloqueadas todas las predicciones de un partido. Devuelve cuantas actualizo."""
        rows = (
            self.db.query(Prediction)
            .filter(Prediction.match_id == match_id, Prediction.is_locked.is_(False))
            .update({Prediction.is_locked: True}, synchronize_session=False)
        )
        return rows
