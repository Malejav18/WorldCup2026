"""DTOs Pydantic para request/response del user-service."""
from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class UserProfilePublic(BaseModel):
    """Vista publica del perfil (lo que ven otros usuarios)."""
    model_config = ConfigDict(from_attributes=True)

    id: str
    display_name: str
    avatar_url: str | None = None
    total_points: int
    global_rank: int | None = None


class UserProfileSelf(UserProfilePublic):
    """Vista propia: incluye email, preferencias, timestamps."""
    email: str
    timezone: str
    language: str
    created_at: datetime
    updated_at: datetime


class UserProfileUpdate(BaseModel):
    display_name: str | None = Field(default=None, min_length=2, max_length=100)
    avatar_url: str | None = None
    timezone: str | None = Field(default=None, max_length=50)
    language: str | None = Field(default=None, max_length=10)


class UserStats(BaseModel):
    """Stats acumuladas del usuario (se completan cuando haya scoring-service)."""
    user_id: str
    total_points: int
    global_rank: int | None = None
    predictions_count: int = 0  # placeholder hasta que prediction-service lo reporte
    correct_predictions: int = 0


# ---- Internos (para eventos entre servicios) ----

class UserRegisteredEvent(BaseModel):
    user_id: str
    email: str
    display_name: str


class PointsUpdatedEvent(BaseModel):
    user_id: str
    new_total_points: int
    points_delta: int | None = None
