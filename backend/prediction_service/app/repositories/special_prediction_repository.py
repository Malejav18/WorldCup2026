from typing import Optional

from sqlalchemy.orm import Session

from prediction_service.app.entities.special_prediction import SpecialPrediction


class SpecialPredictionRepository:
    def __init__(self, db: Session):
        self.db = db

    def get(self, user_id: str, prediction_type: str) -> Optional[SpecialPrediction]:
        return (
            self.db.query(SpecialPrediction)
            .filter(
                SpecialPrediction.user_id == user_id,
                SpecialPrediction.prediction_type == prediction_type,
            )
            .first()
        )

    def list_by_user(self, user_id: str) -> list[SpecialPrediction]:
        return (
            self.db.query(SpecialPrediction)
            .filter(SpecialPrediction.user_id == user_id)
            .order_by(SpecialPrediction.prediction_type)
            .all()
        )

    def create(self, prediction: SpecialPrediction) -> SpecialPrediction:
        self.db.add(prediction)
        self.db.flush()
        return prediction
