"""Repositorio RefreshToken: persistencia de refresh tokens emitidos (blacklist en SQL)."""
from datetime import datetime
from typing import Optional

from sqlalchemy.orm import Session

from auth_service.app.entities.refresh_token import RefreshToken


class RefreshTokenRepository:
    def __init__(self, db: Session):
        self.db = db

    def create(self, token: RefreshToken) -> RefreshToken:
        self.db.add(token)
        self.db.flush()
        return token

    def get(self, jti: str) -> Optional[RefreshToken]:
        return self.db.query(RefreshToken).filter(RefreshToken.id == jti).first()

    def revoke(self, jti: str) -> None:
        token = self.get(jti)
        if token is not None:
            token.revoked = True

    def is_valid(self, jti: str) -> bool:
        token = self.get(jti)
        return (
            token is not None
            and not token.revoked
            and token.expires_at > datetime.utcnow()
        )
