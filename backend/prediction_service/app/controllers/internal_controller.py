"""Endpoints internos del prediction-service.

  - /internal/events/match-result: recibe match.result.registered/corrected
    desde tournament-service y bloquea todas las predicciones del partido.
  - /internal/predictions/match/{match_id}: consultado por scoring-service
    para puntuar todas las predicciones de un partido.
"""
from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from prediction_service.app.database import get_db
from prediction_service.app.dtos.prediction_dtos import MatchResultEvent, PredictionPublic
from prediction_service.app.config import settings
from prediction_service.app.repositories.prediction_repository import PredictionRepository
from prediction_service.app.services.prediction_service import PredictionService


router = APIRouter(prefix="/internal", tags=["internal"])


def get_prediction_service(db: Session = Depends(get_db)) -> PredictionService:
    return PredictionService(db, settings)


@router.post("/events/match-result", status_code=status.HTTP_200_OK)
def on_match_result(
    event: MatchResultEvent,
    svc: PredictionService = Depends(get_prediction_service),
) -> dict:
    """Consumidor de match.result.registered / match.result.corrected."""
    locked = svc.handle_match_result(event)
    return {"match_id": event.match_id, "predictions_locked": locked}


@router.get("/predictions/match/{match_id}", response_model=list[PredictionPublic])
def list_predictions_for_match(match_id: str, db: Session = Depends(get_db)) -> list[PredictionPublic]:
    """Endpoint para scoring-service: todas las predicciones de un partido."""
    items = PredictionRepository(db).list_by_match(match_id)
    return [PredictionPublic.model_validate(p) for p in items]
