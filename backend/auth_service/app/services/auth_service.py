"""Capa de servicios: toda la logica de negocio de autenticacion.

Responsabilidades:
  - Registrar usuarios (email + password bcrypt).
  - Emitir access + refresh tokens en login.
  - Rotar refresh tokens (revoca el anterior, emite uno nuevo).
  - Revocar refresh tokens al hacer logout.
  - Publicar eventos (outbox) cuando un usuario se registra, para que user-service
    cree el perfil y notification-service envie el email de bienvenida.

Esta capa NO toca HTTP ni sabe de FastAPI. Solo recibe DTOs, habla con repositorios
y devuelve DTOs/entidades.
"""
import json
import uuid
from datetime import datetime, timedelta

from sqlalchemy.orm import Session

from shared.jwt_utils import create_token, decode_token
from shared.security import hash_password, verify_password

from auth_service.app.config import Settings
from auth_service.app.dtos.auth_dtos import LoginRequest, RegisterRequest, TokenResponse
from auth_service.app.entities.outbox_event import OutboxEvent
from auth_service.app.entities.refresh_token import RefreshToken
from auth_service.app.entities.user import User
from auth_service.app.repositories.refresh_token_repository import RefreshTokenRepository
from auth_service.app.repositories.user_repository import UserRepository


class AuthError(ValueError):
    """Error de dominio: credenciales invalidas, email duplicado, token invalido, etc."""


class AuthService:
    def __init__(self, db: Session, settings: Settings):
        self.db = db
        self.settings = settings
        self.users = UserRepository(db)
        self.refresh_tokens = RefreshTokenRepository(db)

    def register(self, req: RegisterRequest) -> User:
        if self.users.get_by_email(req.email) is not None:
            raise AuthError("Email already registered")

        user = User(
            email=req.email,
            password_hash=hash_password(req.password),
            role="USER",
        )
        self.users.create(user)

        # Eventos outbox (se despachan en background tras el commit)
        self._emit_event(
            event_type="auth.user.registered",
            target_service="user-service",
            target_endpoint="/internal/events/user-registered",
            payload={
                "user_id": user.id,
                "email": user.email,
                "display_name": req.display_name,
            },
        )
        self._emit_event(
            event_type="auth.user.registered",
            target_service="notification-service",
            target_endpoint="/internal/events/user-registered",
            payload={
                "user_id": user.id,
                "email": user.email,
                "display_name": req.display_name,
            },
        )

        self.db.commit()
        self.db.refresh(user)
        return user

    def login(self, req: LoginRequest) -> TokenResponse:
        user = self.users.get_by_email(req.email)
        if user is None or not verify_password(req.password, user.password_hash):
            raise AuthError("Invalid credentials")
        if not user.is_active:
            raise AuthError("User is inactive")
        tokens = self._build_tokens(user)
        self.db.commit()
        return tokens

    def refresh(self, refresh_token: str) -> TokenResponse:
        claims = self._decode(refresh_token)
        if claims.get("type") != "refresh":
            raise AuthError("Not a refresh token")
        jti = claims.get("jti")
        if not jti or not self.refresh_tokens.is_valid(jti):
            raise AuthError("Refresh token revoked or expired")

        self.refresh_tokens.revoke(jti)
        user = self.users.get_by_id(claims["sub"])
        if user is None:
            raise AuthError("User not found")

        tokens = self._build_tokens(user)
        self.db.commit()
        return tokens

    def logout(self, refresh_token: str) -> None:
        try:
            claims = self._decode(refresh_token)
        except AuthError:
            return
        jti = claims.get("jti")
        if jti:
            self.refresh_tokens.revoke(jti)
            self.db.commit()

    def validate_access_token(self, access_token: str) -> dict:
        claims = self._decode(access_token)
        if claims.get("type") != "access":
            raise AuthError("Not an access token")
        return claims

    def _build_tokens(self, user: User) -> TokenResponse:
        """Emite par access+refresh. Persiste el refresh token (sin commit)."""
        access = create_token(
            subject=user.id,
            secret=self.settings.jwt_secret,
            expires_in_minutes=self.settings.access_token_minutes,
            extra_claims={"role": user.role, "email": user.email, "type": "access"},
        )
        jti = str(uuid.uuid4())
        refresh = create_token(
            subject=user.id,
            secret=self.settings.jwt_secret,
            expires_in_minutes=self.settings.refresh_token_days * 24 * 60,
            extra_claims={"jti": jti, "type": "refresh"},
        )
        self.refresh_tokens.create(
            RefreshToken(
                id=jti,
                user_id=user.id,
                expires_at=datetime.utcnow() + timedelta(days=self.settings.refresh_token_days),
            )
        )
        return TokenResponse(
            access_token=access,
            refresh_token=refresh,
            expires_in=self.settings.access_token_minutes * 60,
        )

    def _decode(self, token: str) -> dict:
        try:
            return decode_token(token, self.settings.jwt_secret)
        except ValueError as e:
            raise AuthError(str(e)) from e

    def _emit_event(
        self,
        *,
        event_type: str,
        target_service: str,
        target_endpoint: str,
        payload: dict,
    ) -> None:
        self.db.add(
            OutboxEvent(
                aggregate_type="user",
                event_type=event_type,
                payload=json.dumps(payload),
                target_service=target_service,
                target_endpoint=target_endpoint,
            )
        )
