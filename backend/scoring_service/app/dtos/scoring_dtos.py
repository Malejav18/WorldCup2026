"""DTOs del scoring-service."""
from datetime import datetime

from pydantic import BaseModel, ConfigDict


class ScorePublic(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    user_id: str
    match_id: str
    phase: str
    reason: str
    points_base: int
    points_bonus: int
    points_total: int
    is_from_correction: bool
    created_at: datetime
    updated_at: datetime


class ScoreSummary(BaseModel):
    user_id: str
    total_points: int
    scored_matches: int


# ---- Eventos consumidos ----

class MatchResultEvent(BaseModel):
    """Mismo payload que tournament-service emite. Campos opcionales para tolerar variaciones."""
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
