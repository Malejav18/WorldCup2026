"""DTOs Pydantic para request/response del prediction-service."""
from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


# ---- Predicciones de partidos ----

class PredictionUpsertRequest(BaseModel):
    """Body del POST /predictions. Upsert por (user_id, match_id)."""

    match_id: str
    predicted_home_goals_90: int = Field(ge=0, le=20)
    predicted_away_goals_90: int = Field(ge=0, le=20)
    predicted_winner_id: str | None = None
    predicted_goes_to_penalties: bool = False


class PredictionPublic(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    user_id: str
    match_id: str
    predicted_home_goals_90: int
    predicted_away_goals_90: int
    predicted_winner_id: str | None
    predicted_goes_to_penalties: bool
    match_phase: str
    is_locked: bool
    created_at: datetime
    updated_at: datetime


# ---- Predicciones especiales ----

class SpecialPredictionRequest(BaseModel):
    """Body del POST /predictions/special."""

    prediction_type: str = Field(pattern="^(CHAMPION|RUNNER_UP|THIRD_PLACE)$")
    team_id: str


class SpecialPredictionPublic(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    user_id: str
    prediction_type: str
    team_id: str
    is_locked: bool
    created_at: datetime
    updated_at: datetime


# ---- Eventos consumidos ----

class MatchResultEvent(BaseModel):
    """Payload emitido por tournament-service en match.result.registered y .corrected."""
    match_id: str
    match_number: int | None = None
    phase: str
    group_id: str | None = None
    home_team_id: str | None = None
    away_team_id: str | None = None
    home_goals_90: int | None = None
    away_goals_90: int | None = None
    went_to_extra_time: bool = False
    went_to_penalties: bool = False
    home_goals_final: int | None = None
    away_goals_final: int | None = None
    winner_id: str | None = None
    finished_at: str | None = None
