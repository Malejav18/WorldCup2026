"""Recalcula la tabla de posiciones de un grupo a partir de los partidos finalizados.

Criterios de desempate (simplificacion pedagogica del algoritmo FIFA de 7 niveles):
  1) Puntos (3 por victoria, 1 por empate, 0 por derrota)
  2) Diferencia de gol
  3) Goles a favor
  4) Nombre del equipo (alfabetico, fallback determinista)

FIFA oficial incluye ademas head-to-head, fair play y sorteo; se omiten por
simplicidad. La forma del calculo no cambia, solo el tuple de ordenamiento.
"""
from sqlalchemy.orm import Session

from tournament_service.app.entities.group_standing import GroupStanding
from tournament_service.app.entities.match import STATUS_FINISHED, Match
from tournament_service.app.repositories.match_repository import MatchRepository
from tournament_service.app.repositories.standing_repository import StandingRepository
from tournament_service.app.repositories.team_repository import TeamRepository


class StandingsService:
    def __init__(self, db: Session):
        self.db = db
        self.matches = MatchRepository(db)
        self.standings = StandingRepository(db)
        self.teams = TeamRepository(db)

    def recompute_group(self, group_id: str) -> list[GroupStanding]:
        teams = self.teams.list_by_group(group_id)
        finished = self.matches.list_finished_in_group(group_id)

        # Partir de cero para cada equipo del grupo.
        acc: dict[str, dict] = {
            t.id: dict(played=0, won=0, drawn=0, lost=0, gf=0, ga=0, points=0, name=t.name)
            for t in teams
        }

        for m in finished:
            if m.home_team_id not in acc or m.away_team_id not in acc:
                continue
            self._apply_result(acc, m)

        rows = [
            GroupStanding(
                group_id=group_id,
                team_id=team_id,
                played=s["played"],
                won=s["won"],
                drawn=s["drawn"],
                lost=s["lost"],
                goals_for=s["gf"],
                goals_against=s["ga"],
                goal_difference=s["gf"] - s["ga"],
                points=s["points"],
            )
            for team_id, s in acc.items()
        ]

        # Ordenamiento: puntos desc, GD desc, GF desc, nombre asc.
        rows.sort(
            key=lambda r: (
                -r.points,
                -r.goal_difference,
                -r.goals_for,
                acc[r.team_id]["name"],
            )
        )
        for idx, row in enumerate(rows, start=1):
            row.position = idx
            self.standings.upsert(row)

        return rows

    @staticmethod
    def _apply_result(acc: dict[str, dict], m: Match) -> None:
        hg, ag = m.home_goals_90, m.away_goals_90
        if hg is None or ag is None:
            return
        home = acc[m.home_team_id]
        away = acc[m.away_team_id]
        home["played"] += 1
        away["played"] += 1
        home["gf"] += hg
        home["ga"] += ag
        away["gf"] += ag
        away["ga"] += hg
        if hg > ag:
            home["won"] += 1
            home["points"] += 3
            away["lost"] += 1
        elif hg < ag:
            away["won"] += 1
            away["points"] += 3
            home["lost"] += 1
        else:
            home["drawn"] += 1
            away["drawn"] += 1
            home["points"] += 1
            away["points"] += 1
