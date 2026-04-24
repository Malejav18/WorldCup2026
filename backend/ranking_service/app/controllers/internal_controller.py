"""Consumidores de eventos para el ranking-service."""
import logging

from fastapi import APIRouter, Body, Depends, status
from sqlalchemy.orm import Session

from ranking_service.app.config import settings
from ranking_service.app.database import get_db
from ranking_service.app.dtos.ranking_dtos import PointsUpdatedEvent
from ranking_service.app.services.ranking_service import RankingService


logger = logging.getLogger(__name__)
router = APIRouter(prefix="/internal/events", tags=["internal"])


def get_ranking_service(db: Session = Depends(get_db)) -> RankingService:
    return RankingService(db, settings)


@router.post("/points-updated", status_code=status.HTTP_204_NO_CONTENT)
def on_points_updated(
    event: PointsUpdatedEvent,
    svc: RankingService = Depends(get_ranking_service),
) -> None:
    svc.handle_points_updated(event)


@router.post("/league-member-added", status_code=status.HTTP_204_NO_CONTENT)
def on_league_member_added(payload: dict = Body(default_factory=dict)) -> None:
    """Placeholder: cuando se implemente ranking por liga, aca se agregaria el
    usuario al sorted set de la liga. Por ahora solo se loguea y retorna 204.
    """
    logger.info("ranking: league.member.added -> %s", payload)


@router.post("/league-member-removed", status_code=status.HTTP_204_NO_CONTENT)
def on_league_member_removed(payload: dict = Body(default_factory=dict)) -> None:
    logger.info("ranking: league.member.removed -> %s", payload)
