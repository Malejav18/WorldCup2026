"""Dependencia reutilizable para validar JWT y extraer el usuario autenticado.

Cualquier servicio que necesite proteger endpoints importa `get_current_user`
(pasandole el mismo JWT_SECRET compartido).
"""
from dataclasses import dataclass

from fastapi import Header, HTTPException, status

from shared.jwt_utils import decode_token


@dataclass(frozen=True)
class AuthenticatedUser:
    user_id: str
    role: str
    email: str | None = None


def build_current_user_dependency(jwt_secret: str):
    def get_current_user(authorization: str | None = Header(default=None)) -> AuthenticatedUser:
        if not authorization or not authorization.lower().startswith("bearer "):
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Missing bearer token")
        token = authorization.split(" ", 1)[1].strip()
        try:
            claims = decode_token(token, jwt_secret)
        except ValueError as e:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(e))
        if claims.get("type") != "access":
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Not an access token")
        return AuthenticatedUser(
            user_id=claims["sub"],
            role=claims.get("role", "USER"),
            email=claims.get("email"),
        )

    return get_current_user


def require_admin(user: AuthenticatedUser) -> None:
    if user.role != "ADMIN":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Admin role required")
