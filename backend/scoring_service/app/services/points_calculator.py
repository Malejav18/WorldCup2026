"""Calculadora de puntos - funciones puras (sin IO).

Implementa la tabla de puntuacion del PDF, seccion 3.3:

Fase de grupos (por partido):
    Marcador exacto  -> points_group_exact (default 3)
    Resultado correcto pero marcador erroneo -> points_group_result (default 1)
    Prediccion incorrecta -> 0

Eliminatorias (por partido):
    Ganador + marcador exacto a 90' -> points_knockout_exact (default 4)
    Solo ganador correcto -> points_knockout_winner (default 2)
    Ganador incorrecto -> 0

Se usan los valores actuales del `Settings` para permitir que el admin los
modifique sin recompilar.
"""
from dataclasses import dataclass

from scoring_service.app.config import Settings


PHASE_GROUP = "GROUP"


@dataclass(frozen=True)
class PointsResult:
    base: int
    bonus: int
    reason: str

    @property
    def total(self) -> int:
        return self.base + self.bonus


def _compare(home: int, away: int) -> str:
    if home > away:
        return "home"
    if home < away:
        return "away"
    return "draw"


def calculate_points(
    *,
    settings: Settings,
    phase: str,
    actual_home_goals_90: int,
    actual_away_goals_90: int,
    actual_winner_id: str | None,
    predicted_home_goals_90: int,
    predicted_away_goals_90: int,
    predicted_winner_id: str | None,
    home_team_id: str | None,
    away_team_id: str | None,
) -> PointsResult:
    if phase == PHASE_GROUP:
        return _calculate_group(
            settings=settings,
            actual_home=actual_home_goals_90,
            actual_away=actual_away_goals_90,
            pred_home=predicted_home_goals_90,
            pred_away=predicted_away_goals_90,
        )
    return _calculate_knockout(
        settings=settings,
        actual_home=actual_home_goals_90,
        actual_away=actual_away_goals_90,
        actual_winner_id=actual_winner_id,
        pred_home=predicted_home_goals_90,
        pred_away=predicted_away_goals_90,
        pred_winner_id=predicted_winner_id,
        home_team_id=home_team_id,
        away_team_id=away_team_id,
    )


def _calculate_group(*, settings, actual_home, actual_away, pred_home, pred_away) -> PointsResult:
    if pred_home == actual_home and pred_away == actual_away:
        return PointsResult(base=settings.points_group_exact, bonus=0, reason="exact_score")
    if _compare(pred_home, pred_away) == _compare(actual_home, actual_away):
        return PointsResult(base=settings.points_group_result, bonus=0, reason="correct_result")
    return PointsResult(base=0, bonus=0, reason="wrong")


def _calculate_knockout(
    *,
    settings,
    actual_home,
    actual_away,
    actual_winner_id,
    pred_home,
    pred_away,
    pred_winner_id,
    home_team_id,
    away_team_id,
) -> PointsResult:
    # En eliminatoria siempre hay ganador. Si la prediccion no tiene winner_id,
    # lo inferimos del marcador predicho a 90' (tolerante con predicciones viejas).
    if pred_winner_id is None:
        if pred_home > pred_away:
            pred_winner_id = home_team_id
        elif pred_home < pred_away:
            pred_winner_id = away_team_id
        else:
            # Empate predicho sin especificar ganador -> se considera incorrecta
            # (la regla del PDF exige predicted_winner_id en eliminatoria).
            return PointsResult(base=0, bonus=0, reason="wrong")

    if pred_winner_id != actual_winner_id:
        return PointsResult(base=0, bonus=0, reason="wrong")

    # Acertó ganador. Ver si ademas acerto marcador a 90'.
    if pred_home == actual_home and pred_away == actual_away:
        return PointsResult(base=settings.points_knockout_exact, bonus=0, reason="winner_exact_score")
    return PointsResult(base=settings.points_knockout_winner, bonus=0, reason="correct_winner")
