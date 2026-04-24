"""Endpoints publicos del user-service (expuestos por el gateway)."""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from shared.auth_dependency import AuthenticatedUser, build_current_user_dependency

from user_service.app.config import settings
from user_service.app.database import get_db
from user_service.app.dtos.user_dtos import UserProfilePublic, UserProfileSelf, UserProfileUpdate, UserStats
from user_service.app.services.user_service import UserError, UserService


router = APIRouter(prefix="/users", tags=["users"])

_get_current_user = build_current_user_dependency(settings.jwt_secret)


def get_user_service(db: Session = Depends(get_db)) -> UserService:
    return UserService(db)


@router.get("/me", response_model=UserProfileSelf)
def get_me(
    current: AuthenticatedUser = Depends(_get_current_user),
    svc: UserService = Depends(get_user_service),
) -> UserProfileSelf:
    try:
        profile = svc.get_self(current.user_id)
    except UserError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    return UserProfileSelf.model_validate(profile)


@router.put("/me", response_model=UserProfileSelf)
def update_me(
    update: UserProfileUpdate,
    current: AuthenticatedUser = Depends(_get_current_user),
    svc: UserService = Depends(get_user_service),
) -> UserProfileSelf:
    try:
        profile = svc.update_self(current.user_id, update)
    except UserError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    return UserProfileSelf.model_validate(profile)


@router.get("/me/stats", response_model=UserStats)
def get_my_stats(
    current: AuthenticatedUser = Depends(_get_current_user),
    svc: UserService = Depends(get_user_service),
) -> UserStats:
    try:
        profile = svc.get_self(current.user_id)
    except UserError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    return UserStats(
        user_id=profile.id,
        total_points=profile.total_points,
        global_rank=profile.global_rank,
    )


@router.get("/{user_id}", response_model=UserProfilePublic)
def get_public(
    user_id: str,
    _: AuthenticatedUser = Depends(_get_current_user),
    svc: UserService = Depends(get_user_service),
) -> UserProfilePublic:
    try:
        profile = svc.get_public(user_id)
    except UserError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    return UserProfilePublic.model_validate(profile)
