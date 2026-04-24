"""Orquestacion: consume match.result.registered/corrected, calcula puntos
y publica scoring.user.points.updated.

Flujo:
  1) Llega evento via /internal/events/match-result con payload del partido
     (incluye winner_id, marcador, fase).
  2) Se consulta prediction-service (HTTP) por todas las predicciones para ese
     match_id.
  3) Para cada prediccion se calcula puntos con `points_calculator`.
  4) Se upserts en la tabla `scores` (idempotente por user_id+match_id).
  5) Se publica via outbox `scoring.user.points.updated` con el nuevo total del
     usuario (suma de todas sus scores) a user-service y ranking-service.

Idempotencia: si el evento reentrega, el upsert deja la fila en el mismo estado
y las publicaciones repetidas no rompen a los consumidores (son absolutas).
"""
import json
import logging

import httpx
from sqlalchemy.orm import Session

from scoring_service.app.config import Settings
from scoring_service.app.dtos.scoring_dtos import MatchResultEvent
from scoring_service.app.entities.outbox_event import OutboxEvent
from scoring_service.app.entities.score import Score
from scoring_service.app.repositories.score_repository import ScoreRepository
from scoring_service.app.services.points_calculator import calculate_points


logger = logging.getLogger(__name__)


class ScoringError(ValueError):
    pass


class ScoringService:
    def __init__(self, db: Session, settings: Settings):
        self.db = db
        self.settings = settings
        self.scores = ScoreRepository(db)

    def handle_match_result(self, event: MatchResultEvent, *, is_correction: bool = False) -> dict:
        if event.home_goals_90 is None or event.away_goals_90 is None:
            raise ScoringError("Match event missing goals")

        predictions = self._fetch_predictions(event.match_id)
        affected_user_ids: set[str] = set()

        for pred in predictions:
            points = calculate_points(
                settings=self.settings,
                phase=event.phase,
                actual_home_goals_90=event.home_goals_90,
                actual_away_goals_90=event.away_goals_90,
                actual_winner_id=event.winner_id,
                predicted_home_goals_90=pred["predicted_home_goals_90"],
                predicted_away_goals_90=pred["predicted_away_goals_90"],
                predicted_winner_id=pred.get("predicted_winner_id"),
                home_team_id=event.home_team_id,
                away_team_id=event.away_team_id,
            )
            score_row = Score(
                user_id=pred["user_id"],
                match_id=event.match_id,
                phase=event.phase,
                reason=points.reason,
                prediction_snapshot=json.dumps(pred, default=str),
                result_snapshot=json.dumps(event.model_dump(), default=str),
                points_base=points.base,
                points_bonus=points.bonus,
                points_total=points.total,
                is_from_correction=is_correction,
            )
            self.scores.upsert(score_row)
            affected_user_ids.add(pred["user_id"])

        # Flush para que total_points_for_user vea las filas recien upserteadas.
        self.db.flush()

        for user_id in affected_user_ids:
            new_total = self.scores.total_points_for_user(user_id)
            self._emit_points_updated(user_id=user_id, new_total_points=new_total, match_id=event.match_id)

        self._emit_match_calculated(event, scores_count=len(predictions), is_correction=is_correction)

        self.db.commit()
        return {
            "match_id": event.match_id,
            "phase": event.phase,
            "scored_predictions": len(predictions),
            "affected_users": len(affected_user_ids),
        }

    # ---- Queries publicas ----

    def list_scores_for_user(self, user_id: str) -> list[Score]:
        return self.scores.list_by_user(user_id)

    def summary_for_user(self, user_id: str) -> tuple[int, int]:
        total = self.scores.total_points_for_user(user_id)
        count = self.scores.count_for_user(user_id)
        return total, count

    # ---- Helpers ----

    def _fetch_predictions(self, match_id: str) -> list[dict]:
        url = f"{self.settings.prediction_service_url.rstrip('/')}/internal/predictions/match/{match_id}"
        try:
            response = httpx.get(url, timeout=5.0)
            response.raise_for_status()
        except httpx.HTTPError as e:
            raise ScoringError(f"Failed to fetch predictions: {e}") from e
        return response.json()

    def _emit_points_updated(self, *, user_id: str, new_total_points: int, match_id: str) -> None:
        payload = {
            "user_id": user_id,
            "new_total_points": new_total_points,
            "match_id": match_id,
        }
        for target_service, target_endpoint in (
            ("user-service", "/internal/events/points-updated"),
            ("ranking-service", "/internal/events/points-updated"),
            ("notification-service", "/internal/events/points-updated"),
        ):
            self.db.add(
                OutboxEvent(
                    aggregate_type="user_points",
                    event_type="scoring.user.points.updated",
                    payload=json.dumps(payload),
                    target_service=target_service,
                    target_endpoint=target_endpoint,
                )
            )

    def _emit_match_calculated(self, event: MatchResultEvent, *, scores_count: int, is_correction: bool) -> None:
        payload = {
            "match_id": event.match_id,
            "phase": event.phase,
            "scores_count": scores_count,
            "is_correction": is_correction,
        }
        self.db.add(
            OutboxEvent(
                aggregate_type="match_scoring",
                event_type="scoring.recalculated" if is_correction else "scoring.match.calculated",
                payload=json.dumps(payload),
                target_service="notification-service",
                target_endpoint="/internal/events/match-calculated",
            )
        )
