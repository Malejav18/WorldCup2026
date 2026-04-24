"""Logica de negocio del prediction-service.

Responsabilidades:
  - Upsert de la prediccion por (user_id, match_id).
  - Validar que el partido existe (HTTP GET a tournament-service).
  - Rechazar ediciones cuando la prediccion esta bloqueada (match ya empezo).
  - Validar reglas por fase:
      * Grupos: empates permitidos, predicted_winner_id opcional.
      * Eliminatorias: predicted_winner_id OBLIGATORIO; si 90' empata, obliga
        predicted_goes_to_penalties=True.
  - Consumir match.result.registered para bloquear predicciones del partido.

No publica eventos en esta fase (el PDF menciona prediction.events para
analiticas futuras; se omite por simplicidad).
"""
import httpx
from sqlalchemy.orm import Session

from prediction_service.app.config import Settings
from prediction_service.app.dtos.prediction_dtos import (
    MatchResultEvent,
    PredictionUpsertRequest,
    SpecialPredictionRequest,
)
from prediction_service.app.entities.prediction import Prediction
from prediction_service.app.entities.special_prediction import (
    VALID_SPECIAL_TYPES,
    SpecialPrediction,
)
from prediction_service.app.repositories.prediction_repository import PredictionRepository
from prediction_service.app.repositories.special_prediction_repository import SpecialPredictionRepository


class PredictionError(ValueError):
    pass


KNOCKOUT_PHASES = {"R32", "R16", "QF", "SF", "THIRD_PLACE", "FINAL"}


class PredictionService:
    def __init__(self, db: Session, settings: Settings):
        self.db = db
        self.settings = settings
        self.predictions = PredictionRepository(db)
        self.specials = SpecialPredictionRepository(db)

    # ---- Predicciones de partidos ----

    def upsert(self, user_id: str, req: PredictionUpsertRequest) -> Prediction:
        match = self._fetch_match(req.match_id)  # valida existencia

        if match.get("status") != "SCHEDULED":
            raise PredictionError("Match is not open for predictions (already locked/finished)")

        phase = match.get("phase", "GROUP")
        self._validate_rules(phase, req)

        existing = self.predictions.get_by_user_and_match(user_id, req.match_id)
        if existing is not None:
            if existing.is_locked:
                raise PredictionError("Prediction is locked and cannot be edited")
            existing.predicted_home_goals_90 = req.predicted_home_goals_90
            existing.predicted_away_goals_90 = req.predicted_away_goals_90
            existing.predicted_winner_id = req.predicted_winner_id
            existing.predicted_goes_to_penalties = req.predicted_goes_to_penalties
            existing.match_phase = phase
            self.db.commit()
            self.db.refresh(existing)
            return existing

        new = Prediction(
            user_id=user_id,
            match_id=req.match_id,
            predicted_home_goals_90=req.predicted_home_goals_90,
            predicted_away_goals_90=req.predicted_away_goals_90,
            predicted_winner_id=req.predicted_winner_id,
            predicted_goes_to_penalties=req.predicted_goes_to_penalties,
            match_phase=phase,
        )
        self.predictions.create(new)
        self.db.commit()
        self.db.refresh(new)
        return new

    def list_for_user(self, user_id: str) -> list[Prediction]:
        return self.predictions.list_by_user(user_id)

    def list_for_user_by_phase(self, user_id: str, phase: str) -> list[Prediction]:
        return self.predictions.list_by_user_and_phase(user_id, phase)

    def get_for_user_and_match(self, user_id: str, match_id: str) -> Prediction | None:
        return self.predictions.get_by_user_and_match(user_id, match_id)

    # ---- Predicciones especiales ----

    def upsert_special(self, user_id: str, req: SpecialPredictionRequest) -> SpecialPrediction:
        if req.prediction_type not in VALID_SPECIAL_TYPES:
            raise PredictionError(f"Invalid prediction type: {req.prediction_type}")
        existing = self.specials.get(user_id, req.prediction_type)
        if existing is not None:
            if existing.is_locked:
                raise PredictionError("Special prediction is locked")
            existing.team_id = req.team_id
            self.db.commit()
            self.db.refresh(existing)
            return existing
        new = SpecialPrediction(
            user_id=user_id,
            prediction_type=req.prediction_type,
            team_id=req.team_id,
        )
        self.specials.create(new)
        self.db.commit()
        self.db.refresh(new)
        return new

    def list_specials_for_user(self, user_id: str) -> list[SpecialPrediction]:
        return self.specials.list_by_user(user_id)

    # ---- Handler de eventos ----

    def handle_match_result(self, event: MatchResultEvent) -> int:
        """Bloquea todas las predicciones del partido. Idempotente."""
        locked_count = self.predictions.lock_for_match(event.match_id)
        self.db.commit()
        return locked_count

    # ---- Helpers ----

    def _fetch_match(self, match_id: str) -> dict:
        url = f"{self.settings.tournament_service_url.rstrip('/')}/tournament/matches/{match_id}"
        try:
            response = httpx.get(url, timeout=5.0)
        except httpx.HTTPError as e:
            raise PredictionError(f"Tournament service unreachable: {e}") from e
        if response.status_code == 404:
            raise PredictionError(f"Match not found: {match_id}")
        if response.status_code >= 400:
            raise PredictionError(f"Tournament service error: {response.status_code}")
        return response.json()

    @staticmethod
    def _validate_rules(phase: str, req: PredictionUpsertRequest) -> None:
        if phase in KNOCKOUT_PHASES:
            if req.predicted_winner_id is None:
                raise PredictionError(f"predicted_winner_id is required in phase {phase}")
            # Si 90' empata y no declaro penales -> rechazo. No hay empates en eliminatoria.
            if (
                req.predicted_home_goals_90 == req.predicted_away_goals_90
                and not req.predicted_goes_to_penalties
            ):
                raise PredictionError(
                    "Knockout 90' cannot be a draw without predicted_goes_to_penalties=True"
                )
