"""Endpoints administrativos: registro y correccion de resultados.

Requieren JWT con rol ADMIN (validado con el secreto compartido via shared).
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from shared.auth_dependency import AuthenticatedUser, build_current_user_dependency, require_admin

from tournament_service.app.config import settings
from tournament_service.app.database import get_db
from tournament_service.app.dtos.tournament_dtos import MatchPublic, RegisterResultRequest
from tournament_service.app.services.match_service import MatchService, TournamentError


router = APIRouter(prefix="/tournament/admin", tags=["tournament-admin"])

_get_current_user = build_current_user_dependency(settings.jwt_secret)


def admin_user(user: AuthenticatedUser = Depends(_get_current_user)) -> AuthenticatedUser:
    require_admin(user)
    return user


def get_match_service(db: Session = Depends(get_db)) -> MatchService:
    return MatchService(db, settings)


@router.post("/matches/{match_id}/result", response_model=MatchPublic, status_code=status.HTTP_200_OK)
def register_result(
    match_id: str,
    req: RegisterResultRequest,
    _: AuthenticatedUser = Depends(admin_user),
    svc: MatchService = Depends(get_match_service),
) -> MatchPublic:
    try:
        match = svc.register_result(match_id, req, is_correction=False)
    except TournamentError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    return MatchPublic.model_validate(match)


@router.put("/matches/{match_id}/result", response_model=MatchPublic)
def correct_result(
    match_id: str,
    req: RegisterResultRequest,
    _: AuthenticatedUser = Depends(admin_user),
    svc: MatchService = Depends(get_match_service),
) -> MatchPublic:
    try:
        match = svc.register_result(match_id, req, is_correction=True)
    except TournamentError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    return MatchPublic.model_validate(match)
