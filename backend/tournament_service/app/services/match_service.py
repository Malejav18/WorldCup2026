"""Logica de registro/correccion de resultados.

Responsabilidades:
  - Validar el payload del admin (marcador final, penales, etc).
  - Actualizar la entidad Match.
  - Recalcular standings del grupo si aplica.
  - Publicar eventos via outbox a scoring-service, prediction-service y
    notification-service.
"""
import json
from datetime import datetime
from typing import Any

from sqlalchemy.orm import Session

from tournament_service.app.config import Settings
from tournament_service.app.dtos.tournament_dtos import RegisterResultRequest
from tournament_service.app.entities.match import (
    PHASE_GROUP,
    STATUS_FINISHED,
    Match,
)
from tournament_service.app.entities.outbox_event import OutboxEvent
from tournament_service.app.repositories.match_repository import MatchRepository
from tournament_service.app.services.standings_service import StandingsService


class TournamentError(ValueError):
    """Error de dominio para el tournament-service."""


class MatchService:
    def __init__(self, db: Session, settings: Settings):
        self.db = db
        self.settings = settings
        self.matches = MatchRepository(db)
        self.standings_service = StandingsService(db)

    def register_result(self, match_id: str, req: RegisterResultRequest, *, is_correction: bool = False) -> Match:
        match = self.matches.get(match_id)
        if match is None:
            raise TournamentError(f"Match not found: {match_id}")

        if match.phase != PHASE_GROUP:
            self._validate_knockout_payload(req)

        # Asignar equipos si se proporcionaron (para partidos de R32 sin equipos asignados)
        if req.home_team_id:
            match.home_team_id = req.home_team_id
        if req.away_team_id:
            match.away_team_id = req.away_team_id

        was_finished = match.status == STATUS_FINISHED
        if was_finished and not is_correction:
            raise TournamentError("Match already has a result. Use PUT to correct it.")

        match.home_goals_90 = req.home_goals_90
        match.away_goals_90 = req.away_goals_90
        match.status = STATUS_FINISHED

        if match.phase == PHASE_GROUP:
            match.went_to_extra_time = False
            match.went_to_penalties = False
            match.home_goals_final = None
            match.away_goals_final = None
            match.winner_id = self._winner_for_group(match)
        else:
            # Si se proporciona winner_id directamente, determinar automaticamente extra time/penalties
            if req.winner_id:
                match.winner_id = req.winner_id
                is_draw = req.home_goals_90 == req.away_goals_90
                match.went_to_extra_time = is_draw
                match.went_to_penalties = is_draw  # Si hay empate y winner, fueron penaltis
                match.home_goals_final = req.home_goals_90 if not is_draw else req.home_goals_90  # Mantener mismo marcador
                match.away_goals_final = req.away_goals_90 if not is_draw else req.away_goals_90
            else:
                # Lógica original
                match.went_to_extra_time = req.went_to_extra_time
                match.went_to_penalties = req.went_to_penalties
                match.home_goals_final = req.home_goals_final if req.went_to_extra_time else req.home_goals_90
                match.away_goals_final = req.away_goals_final if req.went_to_extra_time else req.away_goals_90
                match.winner_id = self._winner_for_knockout(match, req)

        # Recalcular standings solo si es partido de grupo.
        if match.phase == PHASE_GROUP and match.group_id:
            # Flush para que la query del recompute vea el match como FINISHED
            # (la sesion esta configurada con autoflush=False a proposito).
            self.db.flush()
            self.standings_service.recompute_group(match.group_id)
            self._emit(
                event_type="group.standings.updated",
                target_service="notification-service",
                target_endpoint="/internal/events/standings-updated",
                payload={"group_id": match.group_id, "match_id": match.id},
            )

        event_name = "match.result.corrected" if (was_finished and is_correction) else "match.result.registered"
        self._emit_match_event(match, event_name)

        self.db.commit()
        self.db.refresh(match)
        return match

    # ---- Helpers ----

    @staticmethod
    def _validate_knockout_payload(req: RegisterResultRequest) -> None:
        if req.went_to_penalties and not req.penalties_winner:
            raise TournamentError("penalties_winner is required when went_to_penalties=True")
        if req.went_to_extra_time and (req.home_goals_final is None or req.away_goals_final is None):
            raise TournamentError("home_goals_final and away_goals_final required when went_to_extra_time=True")

    @staticmethod
    def _winner_for_group(match: Match) -> str | None:
        hg, ag = match.home_goals_90, match.away_goals_90
        if hg is None or ag is None:
            return None
        if hg > ag:
            return match.home_team_id
        if hg < ag:
            return match.away_team_id
        return None  # empate permitido en grupos

    @staticmethod
    def _winner_for_knockout(match: Match, req: RegisterResultRequest) -> str | None:
        if req.went_to_penalties:
            return match.home_team_id if req.penalties_winner == "home" else match.away_team_id
        final_home = req.home_goals_final if req.went_to_extra_time else req.home_goals_90
        final_away = req.away_goals_final if req.went_to_extra_time else req.away_goals_90
        if final_home is None or final_away is None:
            return None
        if final_home > final_away:
            return match.home_team_id
        if final_home < final_away:
            return match.away_team_id
        raise TournamentError("Knockout match cannot end in a draw at 90' or ET without penalties")

    def _emit_match_event(self, match: Match, event_type: str) -> None:
        payload: dict[str, Any] = {
            "match_id": match.id,
            "match_number": match.match_number,
            "phase": match.phase,
            "group_id": match.group_id,
            "home_team_id": match.home_team_id,
            "away_team_id": match.away_team_id,
            "home_goals_90": match.home_goals_90,
            "away_goals_90": match.away_goals_90,
            "went_to_extra_time": match.went_to_extra_time,
            "went_to_penalties": match.went_to_penalties,
            "home_goals_final": match.home_goals_final,
            "away_goals_final": match.away_goals_final,
            "winner_id": match.winner_id,
            "finished_at": datetime.utcnow().isoformat(),
        }
        for target_service, target_endpoint in (
            ("scoring-service", "/internal/events/match-result"),
            ("prediction-service", "/internal/events/match-result"),
            ("notification-service", "/internal/events/match-result"),
        ):
            self._emit(
                event_type=event_type,
                target_service=target_service,
                target_endpoint=target_endpoint,
                payload=payload,
            )

    def _emit(self, *, event_type: str, target_service: str, target_endpoint: str, payload: dict) -> None:
        self.db.add(
            OutboxEvent(
                aggregate_type="match",
                event_type=event_type,
                payload=json.dumps(payload),
                target_service=target_service,
                target_endpoint=target_endpoint,
            )
        )
