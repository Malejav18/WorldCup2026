"""Emision y validacion de JWT con HS256 (secreto simetrico compartido entre servicios).

Se uso HS256 en lugar del RS256 descrito en el PDF para simplificar el manejo de
claves en un proyecto academico. Todos los servicios comparten el mismo secreto
via variable de entorno JWT_SECRET.
"""
from datetime import datetime, timedelta, timezone
from typing import Any

from jose import JWTError, jwt

ALGORITHM = "HS256"


def create_token(
    *,
    subject: str,
    secret: str,
    expires_in_minutes: int,
    extra_claims: dict[str, Any] | None = None,
) -> str:
    now = datetime.now(tz=timezone.utc)
    payload: dict[str, Any] = {
        "sub": subject,
        "iat": int(now.timestamp()),
        "exp": int((now + timedelta(minutes=expires_in_minutes)).timestamp()),
    }
    if extra_claims:
        payload.update(extra_claims)
    return jwt.encode(payload, secret, algorithm=ALGORITHM)


def decode_token(token: str, secret: str) -> dict[str, Any]:
    try:
        return jwt.decode(token, secret, algorithms=[ALGORITHM])
    except JWTError as e:
        raise ValueError(f"Invalid token: {e}") from e
