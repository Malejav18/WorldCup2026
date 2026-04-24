"""Logica de negocio del league-service.

Responsabilidades:
  - Crear liga: genera invite_code unico, registra al creador como ADMIN.
  - Unirse: busca la liga por invite_code y agrega al usuario como MEMBER.
  - Salir: elimina la membresia (el creador no puede salir; debe eliminar la liga).
  - Regenerar invite_code: solo el ADMIN de la liga puede hacerlo.
  - Ranking de liga: consulta user-service por cada miembro para obtener
    total_points y ordena descendente.

Publica (via outbox):
  - league.member.added -> ranking-service, notification-service
  - league.member.removed -> ranking-service
"""
import json
import logging
import secrets
import string
import uuid

import httpx
from sqlalchemy.orm import Session

from league_service.app.config import Settings
from league_service.app.dtos.league_dtos import (
    LeagueCreateRequest,
    LeagueMemberEntry,
    LeagueMembers,
    LeagueRanking,
    LeagueRankingEntry,
)
from league_service.app.entities.league import League
from league_service.app.entities.league_membership import ROLE_ADMIN, ROLE_MEMBER, LeagueMembership
from league_service.app.entities.outbox_event import OutboxEvent
from league_service.app.repositories.league_repository import LeagueRepository
from league_service.app.repositories.membership_repository import MembershipRepository


logger = logging.getLogger(__name__)


class LeagueError(ValueError):
    pass


_INVITE_ALPHABET = string.ascii_uppercase + string.digits
_INVITE_LENGTH = 8


def _generate_invite_code() -> str:
    return "".join(secrets.choice(_INVITE_ALPHABET) for _ in range(_INVITE_LENGTH))


class LeagueService:
    def __init__(self, db: Session, settings: Settings):
        self.db = db
        self.settings = settings
        self.leagues = LeagueRepository(db)
        self.memberships = MembershipRepository(db)

    # ---- Comandos ----

    def create(self, creator_user_id: str, req: LeagueCreateRequest) -> League:
        invite_code = self._fresh_invite_code()
        league = League(
            id=str(uuid.uuid4()),
            name=req.name,
            description=req.description,
            created_by_user_id=creator_user_id,
            invite_code=invite_code,
        )
        self.leagues.create(league)
        self.memberships.create(
            LeagueMembership(league_id=league.id, user_id=creator_user_id, role=ROLE_ADMIN)
        )
        self._emit_member_added(league, creator_user_id)
        self.db.commit()
        self.db.refresh(league)
        return league

    def join(self, user_id: str, invite_code: str) -> League:
        league = self.leagues.get_by_invite_code(invite_code)
        if league is None:
            raise LeagueError("Invalid invite code")
        if self.memberships.get(league.id, user_id) is not None:
            raise LeagueError("User is already a member of this league")
        self.memberships.create(
            LeagueMembership(league_id=league.id, user_id=user_id, role=ROLE_MEMBER)
        )
        self._emit_member_added(league, user_id)
        self.db.commit()
        self.db.refresh(league)
        return league

    def leave(self, user_id: str, league_id: str) -> None:
        league = self.leagues.get(league_id)
        if league is None:
            raise LeagueError("League not found")
        if league.created_by_user_id == user_id:
            raise LeagueError("The creator cannot leave the league (must delete it instead)")
        removed = self.memberships.delete(league_id, user_id)
        if not removed:
            raise LeagueError("User is not a member of this league")
        self._emit_member_removed(league, user_id)
        self.db.commit()

    def regenerate_invite_code(self, user_id: str, league_id: str) -> str:
        league = self.leagues.get(league_id)
        if league is None:
            raise LeagueError("League not found")
        if league.created_by_user_id != user_id:
            raise LeagueError("Only the league creator can regenerate the invite code")
        new_code = self._fresh_invite_code()
        self.leagues.update_invite_code(league_id, new_code)
        self.db.commit()
        return new_code

    def get_invite_code(self, user_id: str, league_id: str) -> str:
        league = self.leagues.get(league_id)
        if league is None:
            raise LeagueError("League not found")
        if self.memberships.get(league_id, user_id) is None:
            raise LeagueError("Only members can view the invite code")
        return league.invite_code

    # ---- Queries ----

    def list_my_leagues(self, user_id: str) -> list[League]:
        memberships = self.memberships.list_by_user(user_id)
        out: list[League] = []
        for m in memberships:
            league = self.leagues.get(m.league_id)
            if league is not None:
                out.append(league)
        return out

    def get_league(self, league_id: str, viewer_user_id: str | None = None) -> tuple[League, int, str | None]:
        league = self.leagues.get(league_id)
        if league is None:
            raise LeagueError("League not found")
        member_count = self.memberships.count_by_league(league_id)
        my_role: str | None = None
        if viewer_user_id is not None:
            m = self.memberships.get(league_id, viewer_user_id)
            if m is not None:
                my_role = m.role
        return league, member_count, my_role

    def members(self, league_id: str) -> LeagueMembers:
        league = self.leagues.get(league_id)
        if league is None:
            raise LeagueError("League not found")
        members = self.memberships.list_by_league(league_id)
        names = self._fetch_display_names([m.user_id for m in members])
        return LeagueMembers(
            league_id=league_id,
            members=[
                LeagueMemberEntry(
                    user_id=m.user_id,
                    display_name=names.get(m.user_id),
                    role=m.role,
                    joined_at=m.joined_at,
                )
                for m in members
            ],
        )

    def ranking(self, league_id: str) -> LeagueRanking:
        league = self.leagues.get(league_id)
        if league is None:
            raise LeagueError("League not found")
        members = self.memberships.list_by_league(league_id)
        profiles = self._fetch_profiles([m.user_id for m in members])
        entries = [
            LeagueRankingEntry(
                position=0,
                user_id=m.user_id,
                display_name=profiles.get(m.user_id, {}).get("display_name"),
                total_points=int(profiles.get(m.user_id, {}).get("total_points", 0)),
            )
            for m in members
        ]
        entries.sort(key=lambda e: (-e.total_points, e.user_id))
        for i, e in enumerate(entries, start=1):
            e.position = i
        return LeagueRanking(
            league_id=league_id,
            league_name=league.name,
            total_members=len(entries),
            entries=entries,
        )

    # ---- Helpers ----

    def _fresh_invite_code(self) -> str:
        for _ in range(20):
            code = _generate_invite_code()
            if self.leagues.get_by_invite_code(code) is None:
                return code
        raise LeagueError("Could not generate a unique invite code; try again")

    def _emit_member_added(self, league: League, user_id: str) -> None:
        payload = {"league_id": league.id, "league_name": league.name, "user_id": user_id}
        for target_service, target_endpoint in (
            ("ranking-service", "/internal/events/league-member-added"),
            ("notification-service", "/internal/events/league-member-added"),
        ):
            self.db.add(
                OutboxEvent(
                    aggregate_type="league_member",
                    event_type="league.member.added",
                    payload=json.dumps(payload),
                    target_service=target_service,
                    target_endpoint=target_endpoint,
                )
            )

    def _emit_member_removed(self, league: League, user_id: str) -> None:
        payload = {"league_id": league.id, "league_name": league.name, "user_id": user_id}
        self.db.add(
            OutboxEvent(
                aggregate_type="league_member",
                event_type="league.member.removed",
                payload=json.dumps(payload),
                target_service="ranking-service",
                target_endpoint="/internal/events/league-member-removed",
            )
        )

    def _fetch_display_names(self, user_ids: list[str]) -> dict[str, str]:
        base = self.settings.user_service_url.rstrip("/")
        out: dict[str, str] = {}
        with httpx.Client(timeout=3.0) as client:
            for uid in user_ids:
                try:
                    resp = client.get(f"{base}/internal/users/{uid}")
                    if resp.status_code == 200:
                        data = resp.json()
                        if isinstance(data, dict) and "display_name" in data:
                            out[uid] = data["display_name"]
                except httpx.HTTPError as e:
                    logger.warning("display_name lookup failed for %s: %s", uid, e)
        return out

    def _fetch_profiles(self, user_ids: list[str]) -> dict[str, dict]:
        base = self.settings.user_service_url.rstrip("/")
        out: dict[str, dict] = {}
        with httpx.Client(timeout=3.0) as client:
            for uid in user_ids:
                try:
                    resp = client.get(f"{base}/internal/users/{uid}")
                    if resp.status_code == 200 and isinstance(resp.json(), dict):
                        out[uid] = resp.json()
                except httpx.HTTPError as e:
                    logger.warning("profile lookup failed for %s: %s", uid, e)
        return out
