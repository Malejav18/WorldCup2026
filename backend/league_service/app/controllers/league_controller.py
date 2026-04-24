"""Endpoints publicos del league-service."""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from shared.auth_dependency import AuthenticatedUser, build_current_user_dependency

from league_service.app.config import settings
from league_service.app.database import get_db
from league_service.app.dtos.league_dtos import (
    LeagueCreateRequest,
    LeagueDetail,
    LeagueInviteCode,
    LeagueJoinRequest,
    LeagueMembers,
    LeaguePublic,
    LeagueRanking,
)
from league_service.app.services.league_service import LeagueError, LeagueService


router = APIRouter(prefix="/leagues", tags=["leagues"])

_get_current_user = build_current_user_dependency(settings.jwt_secret)


def get_league_service(db: Session = Depends(get_db)) -> LeagueService:
    return LeagueService(db, settings)


@router.post("", response_model=LeaguePublic, status_code=status.HTTP_201_CREATED)
def create_league(
    req: LeagueCreateRequest,
    current: AuthenticatedUser = Depends(_get_current_user),
    svc: LeagueService = Depends(get_league_service),
) -> LeaguePublic:
    try:
        league = svc.create(current.user_id, req)
    except LeagueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    return LeaguePublic.model_validate(league)


@router.get("/me", response_model=list[LeaguePublic])
def list_my_leagues(
    current: AuthenticatedUser = Depends(_get_current_user),
    svc: LeagueService = Depends(get_league_service),
) -> list[LeaguePublic]:
    leagues = svc.list_my_leagues(current.user_id)
    return [LeaguePublic.model_validate(l) for l in leagues]


@router.get("/{league_id}", response_model=LeagueDetail)
def get_league(
    league_id: str,
    current: AuthenticatedUser = Depends(_get_current_user),
    svc: LeagueService = Depends(get_league_service),
) -> LeagueDetail:
    try:
        league, member_count, my_role = svc.get_league(league_id, current.user_id)
    except LeagueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    return LeagueDetail(
        id=league.id,
        name=league.name,
        description=league.description,
        created_by_user_id=league.created_by_user_id,
        created_at=league.created_at,
        member_count=member_count,
        my_role=my_role,
    )


@router.get("/{league_id}/members", response_model=LeagueMembers)
def get_members(
    league_id: str,
    _: AuthenticatedUser = Depends(_get_current_user),
    svc: LeagueService = Depends(get_league_service),
) -> LeagueMembers:
    try:
        return svc.members(league_id)
    except LeagueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@router.get("/{league_id}/ranking", response_model=LeagueRanking)
def get_ranking(
    league_id: str,
    _: AuthenticatedUser = Depends(_get_current_user),
    svc: LeagueService = Depends(get_league_service),
) -> LeagueRanking:
    try:
        return svc.ranking(league_id)
    except LeagueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@router.post("/{league_id}/join", response_model=LeaguePublic)
def join_league_by_id(
    league_id: str,
    req: LeagueJoinRequest,
    current: AuthenticatedUser = Depends(_get_current_user),
    svc: LeagueService = Depends(get_league_service),
) -> LeaguePublic:
    """Se pide `invite_code` en el body (doble verificacion: id + codigo)."""
    try:
        league = svc.join(current.user_id, req.invite_code)
    except LeagueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    if league.id != league_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="invite_code does not match the provided league_id",
        )
    return LeaguePublic.model_validate(league)


@router.post("/join", response_model=LeaguePublic)
def join_by_code(
    req: LeagueJoinRequest,
    current: AuthenticatedUser = Depends(_get_current_user),
    svc: LeagueService = Depends(get_league_service),
) -> LeaguePublic:
    """Union solo con el invite_code (sin conocer la liga id)."""
    try:
        league = svc.join(current.user_id, req.invite_code)
    except LeagueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    return LeaguePublic.model_validate(league)


@router.delete("/{league_id}/leave", status_code=status.HTTP_204_NO_CONTENT)
def leave_league(
    league_id: str,
    current: AuthenticatedUser = Depends(_get_current_user),
    svc: LeagueService = Depends(get_league_service),
) -> None:
    try:
        svc.leave(current.user_id, league_id)
    except LeagueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.get("/{league_id}/invite-code", response_model=LeagueInviteCode)
def get_invite_code(
    league_id: str,
    current: AuthenticatedUser = Depends(_get_current_user),
    svc: LeagueService = Depends(get_league_service),
) -> LeagueInviteCode:
    try:
        code = svc.get_invite_code(current.user_id, league_id)
    except LeagueError as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))
    return LeagueInviteCode(league_id=league_id, invite_code=code)


@router.post("/{league_id}/invite-code/regenerate", response_model=LeagueInviteCode)
def regenerate_invite_code(
    league_id: str,
    current: AuthenticatedUser = Depends(_get_current_user),
    svc: LeagueService = Depends(get_league_service),
) -> LeagueInviteCode:
    try:
        code = svc.regenerate_invite_code(current.user_id, league_id)
    except LeagueError as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))
    return LeagueInviteCode(league_id=league_id, invite_code=code)
