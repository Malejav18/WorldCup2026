"""Endpoints internos del scoring-service.

/internal/events/match-result: consumidor de match.result.registered.
/internal/events/match-corrected: consumidor de match.result.corrected.
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from scoring_service.app.config import settings
from scoring_service.app.database import get_db
from scoring_service.app.dtos.scoring_dtos import MatchResultEvent
from scoring_service.app.services.scoring_service import ScoringError, ScoringService


router = APIRouter(prefix="/internal/events", tags=["internal"])


def get_scoring_service(db: Session = Depends(get_db)) -> ScoringService:
    return ScoringService(db, settings)


@router.post("/match-result", status_code=status.HTTP_200_OK)
def on_match_result(
    event: MatchResultEvent,
    svc: ScoringService = Depends(get_scoring_service),
) -> dict:
    try:
        return svc.handle_match_result(event, is_correction=False)
    except ScoringError as e:
        raise HTTPException(status_code=status.HTTP_502_BAD_GATEWAY, detail=str(e))


@router.post("/match-corrected", status_code=status.HTTP_200_OK)
def on_match_corrected(
    event: MatchResultEvent,
    svc: ScoringService = Depends(get_scoring_service),
) -> dict:
    try:
        return svc.handle_match_result(event, is_correction=True)
    except ScoringError as e:
        raise HTTPException(status_code=status.HTTP_502_BAD_GATEWAY, detail=str(e))
