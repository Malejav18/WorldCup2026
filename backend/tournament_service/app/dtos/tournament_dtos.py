"""DTOs Pydantic para request/response del tournament-service."""
from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class TeamPublic(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: str
    name: str
    country_code: str
    confederation: str
    group_id: str | None = None


class GroupPublic(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: str
    letter: str
    name: str


class GroupWithTeams(GroupPublic):
    teams: list[TeamPublic] = Field(default_factory=list)


class StandingRow(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    team_id: str
    team_name: str
    position: int
    played: int
    won: int
    drawn: int
    lost: int
    goals_for: int
    goals_against: int
    goal_difference: int
    points: int


class GroupStandings(BaseModel):
    group: GroupPublic
    rows: list[StandingRow]


class MatchPublic(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: str
    match_number: int
    phase: str
    group_id: str | None
    home_team_id: str | None
    away_team_id: str | None
    home_team_slot: str | None
    away_team_slot: str | None
    scheduled_at: datetime
    status: str
    home_goals_90: int | None
    away_goals_90: int | None
    went_to_extra_time: bool
    went_to_penalties: bool
    home_goals_final: int | None
    away_goals_final: int | None
    winner_id: str | None


class RegisterResultRequest(BaseModel):
    """Payload para POST /tournament/admin/matches/{id}/result."""

    home_goals_90: int = Field(ge=0, le=20)
    away_goals_90: int = Field(ge=0, le=20)

    # Para partidos de R32 sin equipos asignados
    home_team_id: str | None = None
    away_team_id: str | None = None

    # Para simplificar: winner_id directo (opcional, para determinar automaticamente extra time/penalties)
    winner_id: str | None = None

    # Solo eliminatorias: si hubo tiempo extra y/o penales
    went_to_extra_time: bool = False
    went_to_penalties: bool = False
    home_goals_final: int | None = Field(default=None, ge=0, le=20)
    away_goals_final: int | None = Field(default=None, ge=0, le=20)

    # En penales, quien gano (home/away). Requerido solo si went_to_penalties=True.
    penalties_winner: str | None = Field(default=None, pattern="^(home|away)$")


class TournamentInfo(BaseModel):
    status: str
    total_matches: int
    finished_matches: int
    next_match: MatchPublic | None = None


class ThirdPlaceRow(BaseModel):
    group_id: str
    group_letter: str
    team_id: str
    team_name: str
    points: int
    goal_difference: int
    goals_for: int
    qualifies: bool  # True para los 8 mejores terceros
