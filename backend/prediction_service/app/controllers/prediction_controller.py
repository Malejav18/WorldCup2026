"""Endpoints publicos del prediction-service (expuestos via api-gateway)."""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from shared.auth_dependency import AuthenticatedUser, build_current_user_dependency

from prediction_service.app.config import settings
from prediction_service.app.database import get_db
from prediction_service.app.dtos.prediction_dtos import (
    PredictionPublic,
    PredictionUpsertRequest,
    SpecialPredictionPublic,
    SpecialPredictionRequest,
)
from prediction_service.app.services.prediction_service import PredictionError, PredictionService


router = APIRouter(prefix="/predictions", tags=["predictions"])

_get_current_user = build_current_user_dependency(settings.jwt_secret)


def get_prediction_service(db: Session = Depends(get_db)) -> PredictionService:
    return PredictionService(db, settings)


@router.post("", response_model=PredictionPublic, status_code=status.HTTP_200_OK)
def upsert(
    req: PredictionUpsertRequest,
    current: AuthenticatedUser = Depends(_get_current_user),
    svc: PredictionService = Depends(get_prediction_service),
) -> PredictionPublic:
    try:
        pred = svc.upsert(current.user_id, req)
    except PredictionError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    return PredictionPublic.model_validate(pred)


@router.get("/me", response_model=list[PredictionPublic])
def list_mine(
    current: AuthenticatedUser = Depends(_get_current_user),
    svc: PredictionService = Depends(get_prediction_service),
) -> list[PredictionPublic]:
    items = svc.list_for_user(current.user_id)
    return [PredictionPublic.model_validate(p) for p in items]


@router.get("/me/match/{match_id}", response_model=PredictionPublic)
def get_mine_for_match(
    match_id: str,
    current: AuthenticatedUser = Depends(_get_current_user),
    svc: PredictionService = Depends(get_prediction_service),
) -> PredictionPublic:
    pred = svc.get_for_user_and_match(current.user_id, match_id)
    if pred is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Prediction not found")
    return PredictionPublic.model_validate(pred)


@router.get("/me/phase/{phase}", response_model=list[PredictionPublic])
def list_mine_by_phase(
    phase: str,
    current: AuthenticatedUser = Depends(_get_current_user),
    svc: PredictionService = Depends(get_prediction_service),
) -> list[PredictionPublic]:
    items = svc.list_for_user_by_phase(current.user_id, phase)
    return [PredictionPublic.model_validate(p) for p in items]


# ---- Predicciones especiales (campeon, subcampeon, tercero) ----

@router.post("/special", response_model=SpecialPredictionPublic)
def upsert_special(
    req: SpecialPredictionRequest,
    current: AuthenticatedUser = Depends(_get_current_user),
    svc: PredictionService = Depends(get_prediction_service),
) -> SpecialPredictionPublic:
    try:
        pred = svc.upsert_special(current.user_id, req)
    except PredictionError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    return SpecialPredictionPublic.model_validate(pred)


@router.get("/special/me", response_model=list[SpecialPredictionPublic])
def list_my_specials(
    current: AuthenticatedUser = Depends(_get_current_user),
    svc: PredictionService = Depends(get_prediction_service),
) -> list[SpecialPredictionPublic]:
    items = svc.list_specials_for_user(current.user_id)
    return [SpecialPredictionPublic.model_validate(p) for p in items]
