"""DTOs del ranking-service."""
from pydantic import BaseModel


class RankingEntry(BaseModel):
    position: int
    user_id: str
    display_name: str | None = None  # enriquecido via user-service si es posible
    total_points: int


class GlobalRankingPage(BaseModel):
    total_users: int
    page: int
    page_size: int
    entries: list[RankingEntry]


class MyPosition(BaseModel):
    user_id: str
    position: int | None  # null si el usuario aun no tiene puntos registrados
    total_points: int
    total_users: int


# ---- Eventos consumidos ----

class PointsUpdatedEvent(BaseModel):
    user_id: str
    new_total_points: int
    match_id: str | None = None
