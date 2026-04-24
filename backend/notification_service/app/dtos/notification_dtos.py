"""DTOs del notification-service."""
from datetime import datetime

from pydantic import BaseModel, ConfigDict


class NotificationPublic(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    user_id: str
    event_type: str
    channel: str
    subject: str
    body: str
    status: str
    read_at: datetime | None = None
    created_at: datetime
    sent_at: datetime | None = None


# ---- Eventos consumidos ----

class UserRegisteredEvent(BaseModel):
    user_id: str
    email: str
    display_name: str


class MatchResultEvent(BaseModel):
    match_id: str
    match_number: int | None = None
    phase: str
    home_team_id: str | None = None
    away_team_id: str | None = None
    home_goals_90: int | None = None
    away_goals_90: int | None = None
    winner_id: str | None = None


class PointsUpdatedEvent(BaseModel):
    user_id: str
    new_total_points: int
    match_id: str | None = None


class MatchCalculatedEvent(BaseModel):
    match_id: str
    phase: str
    scores_count: int
    is_correction: bool = False


class StandingsUpdatedEvent(BaseModel):
    group_id: str
    match_id: str | None = None


class LeagueMemberAddedEvent(BaseModel):
    league_id: str
    league_name: str
    user_id: str
