"""Logica de negocio del user-service.

Reacciona a eventos de dominio (auth.user.registered, scoring.user.points.updated)
y expone operaciones CRUD sobre el perfil publico.

La idempotencia en el consumo de eventos es critica porque el outbox es at-least-once:
un mismo evento puede llegar dos o mas veces si hubo reintentos.
"""
from sqlalchemy.orm import Session

from user_service.app.dtos.user_dtos import (
    PointsUpdatedEvent,
    UserProfileUpdate,
    UserRegisteredEvent,
)
from user_service.app.entities.user_profile import UserProfile
from user_service.app.repositories.user_profile_repository import UserProfileRepository


class UserError(ValueError):
    pass


class UserService:
    def __init__(self, db: Session):
        self.db = db
        self.profiles = UserProfileRepository(db)

    # ---- Comandos del dominio (invocados desde controllers publicos) ----

    def get_self(self, user_id: str) -> UserProfile:
        profile = self.profiles.get(user_id)
        if profile is None:
            raise UserError("User profile not found")
        return profile

    def get_public(self, user_id: str) -> UserProfile:
        profile = self.profiles.get(user_id)
        if profile is None:
            raise UserError("User not found")
        return profile

    def update_self(self, user_id: str, update: UserProfileUpdate) -> UserProfile:
        profile = self.profiles.get(user_id)
        if profile is None:
            raise UserError("User profile not found")
        if update.display_name is not None:
            profile.display_name = update.display_name
        if update.avatar_url is not None:
            profile.avatar_url = update.avatar_url
        if update.timezone is not None:
            profile.timezone = update.timezone
        if update.language is not None:
            profile.language = update.language
        self.db.commit()
        self.db.refresh(profile)
        return profile

    # ---- Handlers de eventos (invocados desde /internal/events/*) ----

    def handle_user_registered(self, event: UserRegisteredEvent) -> UserProfile:
        """Crea el perfil inicial. Idempotente: si ya existe, devuelve el existente."""
        existing = self.profiles.get(event.user_id)
        if existing is not None:
            return existing
        profile = UserProfile(
            id=event.user_id,
            email=event.email,
            display_name=event.display_name,
        )
        self.profiles.create(profile)
        self.db.commit()
        self.db.refresh(profile)
        return profile

    def handle_points_updated(self, event: PointsUpdatedEvent) -> UserProfile | None:
        """Actualiza totalPoints. Idempotente: el nuevo total es absoluto."""
        profile = self.profiles.update_total_points(event.user_id, event.new_total_points)
        if profile is not None:
            self.db.commit()
            self.db.refresh(profile)
        return profile
