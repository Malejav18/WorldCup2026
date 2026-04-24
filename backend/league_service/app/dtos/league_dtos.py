"""DTOs del league-service."""
from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class LeagueCreateRequest(BaseModel):
    name: str = Field(min_length=3, max_length=100)
    description: str | None = Field(default=None, max_length=500)


class LeagueJoinRequest(BaseModel):
    invite_code: str = Field(min_length=4, max_length=16)


class LeaguePublic(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    name: str
    description: str | None
    created_by_user_id: str
    created_at: datetime
    # El invite_code NO se expone en las vistas publicas; solo via endpoint dedicado.


class LeagueDetail(LeaguePublic):
    member_count: int
    my_role: str | None = None  # ADMIN / MEMBER / None (no es miembro)


class LeagueMemberEntry(BaseModel):
    user_id: str
    display_name: str | None = None
    role: str
    joined_at: datetime


class LeagueMembers(BaseModel):
    league_id: str
    members: list[LeagueMemberEntry]


class LeagueInviteCode(BaseModel):
    league_id: str
    invite_code: str


class LeagueRankingEntry(BaseModel):
    position: int
    user_id: str
    display_name: str | None = None
    total_points: int


class LeagueRanking(BaseModel):
    league_id: str
    league_name: str
    total_members: int
    entries: list[LeagueRankingEntry]
