"""Endpoints publicos del ranking-service."""
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from shared.auth_dependency import AuthenticatedUser, build_current_user_dependency

from ranking_service.app.config import settings
from ranking_service.app.database import get_db
from ranking_service.app.dtos.ranking_dtos import GlobalRankingPage, MyPosition
from ranking_service.app.services.ranking_service import RankingService


router = APIRouter(prefix="/rankings", tags=["rankings"])

_get_current_user = build_current_user_dependency(settings.jwt_secret)


def get_ranking_service(db: Session = Depends(get_db)) -> RankingService:
    return RankingService(db, settings)


@router.get("/global", response_model=GlobalRankingPage)
def global_ranking(
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
    svc: RankingService = Depends(get_ranking_service),
) -> GlobalRankingPage:
    return svc.global_ranking(page=page, page_size=page_size)


@router.get("/global/me", response_model=MyPosition)
def my_position(
    current: AuthenticatedUser = Depends(_get_current_user),
    svc: RankingService = Depends(get_ranking_service),
) -> MyPosition:
    return svc.my_position(current.user_id)
