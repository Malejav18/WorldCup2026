"""Endpoints publicos del scoring-service."""
from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from shared.auth_dependency import AuthenticatedUser, build_current_user_dependency

from scoring_service.app.config import settings
from scoring_service.app.database import get_db
from scoring_service.app.dtos.scoring_dtos import ScorePublic, ScoreSummary
from scoring_service.app.services.scoring_service import ScoringService


router = APIRouter(prefix="/scoring", tags=["scoring"])

_get_current_user = build_current_user_dependency(settings.jwt_secret)


def get_scoring_service(db: Session = Depends(get_db)) -> ScoringService:
    return ScoringService(db, settings)


@router.get("/me", response_model=list[ScorePublic])
def list_mine(
    current: AuthenticatedUser = Depends(_get_current_user),
    svc: ScoringService = Depends(get_scoring_service),
) -> list[ScorePublic]:
    return [ScorePublic.model_validate(s) for s in svc.list_scores_for_user(current.user_id)]


@router.get("/me/summary", response_model=ScoreSummary, status_code=status.HTTP_200_OK)
def my_summary(
    current: AuthenticatedUser = Depends(_get_current_user),
    svc: ScoringService = Depends(get_scoring_service),
) -> ScoreSummary:
    total, count = svc.summary_for_user(current.user_id)
    return ScoreSummary(user_id=current.user_id, total_points=total, scored_matches=count)
