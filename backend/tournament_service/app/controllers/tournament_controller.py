"""Endpoints publicos del torneo (no requieren JWT)."""
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from tournament_service.app.database import get_db
from tournament_service.app.dtos.tournament_dtos import (
    GroupStandings,
    GroupWithTeams,
    MatchPublic,
    TeamPublic,
    ThirdPlaceRow,
    TournamentInfo,
)
from tournament_service.app.repositories.match_repository import MatchRepository
from tournament_service.app.repositories.team_repository import TeamRepository
from tournament_service.app.services.tournament_service import TournamentService


router = APIRouter(prefix="/tournament", tags=["tournament"])


def get_tournament_service(db: Session = Depends(get_db)) -> TournamentService:
    return TournamentService(db)


@router.get("/info", response_model=TournamentInfo)
def get_info(svc: TournamentService = Depends(get_tournament_service)) -> TournamentInfo:
    return svc.info()


@router.get("/teams", response_model=list[TeamPublic])
def list_teams(db: Session = Depends(get_db)) -> list[TeamPublic]:
    teams = TeamRepository(db).list_all()
    return [TeamPublic.model_validate(t) for t in teams]


@router.get("/groups", response_model=list[GroupWithTeams])
def list_groups(svc: TournamentService = Depends(get_tournament_service)) -> list[GroupWithTeams]:
    return svc.list_groups_with_teams()


@router.get("/groups/{group_id}/standings", response_model=GroupStandings)
def get_standings(group_id: str, svc: TournamentService = Depends(get_tournament_service)) -> GroupStandings:
    result = svc.group_standings(group_id)
    if result is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Group not found")
    return result


@router.get("/third-place-standings", response_model=list[ThirdPlaceRow])
def third_place_standings(svc: TournamentService = Depends(get_tournament_service)) -> list[ThirdPlaceRow]:
    return svc.third_place_standings()


@router.get("/matches", response_model=list[MatchPublic])
def list_matches(
    phase: str | None = Query(default=None),
    status_filter: str | None = Query(default=None, alias="status"),
    group_id: str | None = Query(default=None),
    db: Session = Depends(get_db),
) -> list[MatchPublic]:
    matches = MatchRepository(db).list_all(phase=phase, status=status_filter, group_id=group_id)
    return [MatchPublic.model_validate(m) for m in matches]


@router.get("/matches/{match_id}", response_model=MatchPublic)
def get_match(match_id: str, db: Session = Depends(get_db)) -> MatchPublic:
    match = MatchRepository(db).get(match_id)
    if match is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Match not found")
    return MatchPublic.model_validate(match)
