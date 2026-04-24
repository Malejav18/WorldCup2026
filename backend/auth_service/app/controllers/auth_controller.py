"""Capa de controladores: recibe HTTP, delega al servicio, devuelve JSON.

Regla: ningun metodo debe pasar de ~15 lineas. Si crece, la logica se escapo a
donde no corresponde; muevala al servicio.
"""
from fastapi import APIRouter, Body, Depends, HTTPException, status
from sqlalchemy.orm import Session

from auth_service.app.config import settings
from auth_service.app.database import get_db
from auth_service.app.dtos.auth_dtos import (
    LoginRequest,
    RefreshRequest,
    RegisterRequest,
    TokenResponse,
    UserPublic,
    ValidateResponse,
)
from auth_service.app.services.auth_service import AuthError, AuthService


router = APIRouter(prefix="/auth", tags=["auth"])


def get_auth_service(db: Session = Depends(get_db)) -> AuthService:
    return AuthService(db, settings)


@router.post("/register", response_model=UserPublic, status_code=status.HTTP_201_CREATED)
def register(req: RegisterRequest, svc: AuthService = Depends(get_auth_service)) -> UserPublic:
    try:
        user = svc.register(req)
    except AuthError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    return UserPublic.model_validate(user)


@router.post("/login", response_model=TokenResponse)
def login(req: LoginRequest, svc: AuthService = Depends(get_auth_service)) -> TokenResponse:
    try:
        return svc.login(req)
    except AuthError as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(e))


@router.post("/refresh", response_model=TokenResponse)
def refresh(req: RefreshRequest, svc: AuthService = Depends(get_auth_service)) -> TokenResponse:
    try:
        return svc.refresh(req.refresh_token)
    except AuthError as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(e))


@router.post("/logout", status_code=status.HTTP_204_NO_CONTENT)
def logout(req: RefreshRequest, svc: AuthService = Depends(get_auth_service)) -> None:
    svc.logout(req.refresh_token)


@router.post("/validate", response_model=ValidateResponse)
def validate(
    access_token: str = Body(..., embed=True),
    svc: AuthService = Depends(get_auth_service),
) -> ValidateResponse:
    """Usado por el api-gateway (u otros servicios) para validar un access token."""
    try:
        claims = svc.validate_access_token(access_token)
    except AuthError as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(e))
    return ValidateResponse(
        user_id=claims["sub"],
        role=claims.get("role", "USER"),
        email=claims.get("email"),
    )
