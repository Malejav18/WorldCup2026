"""Consultas de solo lectura sobre el torneo + calculo de los 8 mejores terceros."""
from sqlalchemy.orm import Session

from tournament_service.app.dtos.tournament_dtos import (
    GroupStandings,
    GroupWithTeams,
    StandingRow,
    ThirdPlaceRow,
    TournamentInfo,
)
from tournament_service.app.entities.tournament_state import STATE_PRE_START, TournamentState
from tournament_service.app.repositories.group_repository import GroupRepository
from tournament_service.app.repositories.match_repository import MatchRepository
from tournament_service.app.repositories.standing_repository import StandingRepository
from tournament_service.app.repositories.team_repository import TeamRepository


class TournamentService:
    def __init__(self, db: Session):
        self.db = db
        self.groups = GroupRepository(db)
        self.teams = TeamRepository(db)
        self.matches = MatchRepository(db)
        self.standings = StandingRepository(db)

    def info(self) -> TournamentInfo:
        state = self.db.query(TournamentState).first()
        status = state.status if state else STATE_PRE_START
        next_m = self.matches.next_scheduled()
        return TournamentInfo(
            status=status,
            total_matches=self.matches.count(),
            finished_matches=self.matches.count_finished(),
            next_match=next_m,  # Pydantic model_config from_attributes convierte el ORM
        )

    def list_groups_with_teams(self) -> list[GroupWithTeams]:
        groups = self.groups.list_all()
        result: list[GroupWithTeams] = []
        for g in groups:
            teams = self.teams.list_by_group(g.id)
            result.append(
                GroupWithTeams(
                    id=g.id, letter=g.letter, name=g.name,
                    teams=[t for t in teams],  # pydantic mapea desde ORM por from_attributes
                )
            )
        return result

    def group_standings(self, group_id: str) -> GroupStandings | None:
        group = self.groups.get(group_id)
        if group is None:
            return None
        rows = self.standings.list_by_group(group_id)
        # Enriquecer con el nombre del equipo para el front.
        team_map = {t.id: t.name for t in self.teams.list_by_group(group_id)}
        standing_rows = [
            StandingRow(
                team_id=r.team_id,
                team_name=team_map.get(r.team_id, r.team_id),
                position=r.position,
                played=r.played,
                won=r.won,
                drawn=r.drawn,
                lost=r.lost,
                goals_for=r.goals_for,
                goals_against=r.goals_against,
                goal_difference=r.goal_difference,
                points=r.points,
            )
            for r in rows
        ]
        return GroupStandings(group=group, rows=standing_rows)

    def third_place_standings(self) -> list[ThirdPlaceRow]:
        """Ranking global de los terceros de cada grupo. Los 8 mejores clasifican a R32."""
        groups = self.groups.list_all()
        rows: list[ThirdPlaceRow] = []
        for g in groups:
            group_rows = self.standings.list_by_group(g.id)
            if len(group_rows) < 3:
                continue
            third = group_rows[2]  # lista viene ordenada por position
            team = self.teams.get(third.team_id)
            if team is None:
                continue
            rows.append(
                ThirdPlaceRow(
                    group_id=g.id,
                    group_letter=g.letter,
                    team_id=team.id,
                    team_name=team.name,
                    points=third.points,
                    goal_difference=third.goal_difference,
                    goals_for=third.goals_for,
                    qualifies=False,
                )
            )
        # Mismo criterio que standings: puntos, GD, GF, alfabetico.
        rows.sort(key=lambda r: (-r.points, -r.goal_difference, -r.goals_for, r.team_name))
        for i, r in enumerate(rows):
            r.qualifies = i < 8
        return rows
