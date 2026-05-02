"""Seed inicial del torneo: 12 grupos, 48 equipos, 72 partidos de fase de grupos.

Ejecutar desde `backend/`:
    python -m tournament_service.app.seed.seed_tournament

Es idempotente: si ya hay datos, no duplica; se puede correr varias veces.

Nota: los grupos y el calendario son una asignacion representativa para el
proyecto academico (la rifa oficial de FIFA es en dic 2025). No pretende ser
el sorteo real.
"""
import uuid
from datetime import datetime, timedelta

from tournament_service.app.database import Base, SessionLocal, engine
from tournament_service.app.entities.group import Group
from tournament_service.app.entities.match import (
    PHASE_GROUP,
    PHASE_R32,
    PHASE_R16,
    PHASE_QF,
    PHASE_SF,
    PHASE_THIRD_PLACE,
    PHASE_FINAL,
    STATUS_SCHEDULED,
    Match,
)
from tournament_service.app.entities.team import Team
from tournament_service.app.entities.tournament_state import STATE_PRE_START, TournamentState


# 48 equipos distribuidos en 12 grupos (A..L), 4 equipos por grupo.
# Composicion representativa para fines academicos.
GROUPS_DATA: list[tuple[str, list[tuple[str, str, str]]]] = [
    ("A", [("Mexico", "MEX", "CONCACAF"), ("Sudafrica", "RSA", "CAF"), ("Corea del Sur", "KOR", "AFC"), ("Chequia", "CZE", "UEFA")]),
    ("B", [("Canada", "CAN", "CONCACAF"), ("Bosnia", "BIH", "UEFA"), ("Qatar", "QAT", "AFC"), ("Suiza", "SUI", "UEFA")]),
    ("C", [("Brasil", "BRA", "CONMEBOL"), ("Marruecos", "MAR", "CAF"), ("Haiti", "HAI", "CONCACAF"), ("Escocia", "SCO", "UEFA")]),
    ("D", [("Estados Unidos", "USA", "CONCACAF"), ("Paraguay", "PAR", "CONMEBOL"), ("Australia", "AUS", "AFC"), ("Turquia", "TUR", "UEFA")]),
    ("E", [("Alemania", "GER", "UEFA"), ("Curazao", "CUW", "CONCACAF"), ("Costa de Marfil", "CIV", "CAF"), ("Ecuador", "ECU", "CONMEBOL")]),
    ("F", [("Paises Bajos", "NED", "UEFA"), ("Japon", "JPN", "AFC"), ("Suecia", "SWE", "UEFA"), ("Tunez", "TUN", "CAF")]),
    ("G", [("Belgica", "BEL", "UEFA"), ("Egipto", "EGY", "CAF"), ("Iran", "IRN", "AFC"), ("Nueva Zelanda", "NZL", "OFC")]),
    ("H", [("Espana", "ESP", "UEFA"), ("Cabo Verde", "CPV", "CAF"), ("Arabia Saudita", "KSA", "AFC"), ("Uruguay", "URU", "CONMEBOL")]),
    ("I", [("Francia", "FRA", "UEFA"), ("Senegal", "SEN", "CAF"), ("Irak", "IRQ", "AFC"), ("Noruega", "NOR", "UEFA")]),
    ("J", [("Argentina", "ARG", "CONMEBOL"), ("Argelia", "ALG", "CAF"), ("Austria", "AUT", "UEFA"), ("Jordania", "JOR", "AFC")]),
    ("K", [("Portugal", "POR", "UEFA"), ("RD Congo", "COD", "CAF"), ("Uzbekistan", "UZB", "AFC"), ("Colombia", "COL", "CONMEBOL")]),
    ("L", [("Inglaterra", "ENG", "UEFA"), ("Croacia", "CRO", "UEFA"), ("Ghana", "GHA", "CAF"), ("Panama", "PAN", "CONCACAF")]),
]


def _new_uuid() -> str:
    return str(uuid.uuid4())


def seed() -> None:
    Base.metadata.create_all(engine)
    with SessionLocal() as db:
        if db.query(Team).count() > 0:
            print("Datos ya existen; seed omitido (idempotente).")
            return

        # Estado inicial del torneo.
        db.add(TournamentState(id=1, status=STATE_PRE_START, updated_at=datetime.utcnow()))

        # Grupos + equipos.
        groups_by_letter: dict[str, Group] = {}
        teams_by_group: dict[str, list[Team]] = {}
        for letter, teams in GROUPS_DATA:
            g = Group(id=_new_uuid(), letter=letter, name=f"Grupo {letter}")
            db.add(g)
            groups_by_letter[letter] = g
            teams_by_group[letter] = []
            for name, code, confed in teams:
                t = Team(
                    id=_new_uuid(),
                    name=name,
                    country_code=code,
                    confederation=confed,
                    group_id=g.id,
                )
                db.add(t)
                teams_by_group[letter].append(t)

        db.flush()  # asegurar IDs antes de referenciarlos en Match

        # Partidos de fase de grupos: 6 partidos por grupo (todos contra todos).
        # 12 grupos x 6 = 72 partidos.
        base_date = datetime(2026, 6, 11, 15, 0, 0)  # 11 jun 2026, primer partido
        match_number = 1
        for letter, _ in GROUPS_DATA:
            group = groups_by_letter[letter]
            teams = teams_by_group[letter]
            pairings = [
                (teams[0], teams[1]),
                (teams[2], teams[3]),
                (teams[0], teams[2]),
                (teams[1], teams[3]),
                (teams[0], teams[3]),
                (teams[1], teams[2]),
            ]
            for i, (home, away) in enumerate(pairings):
                scheduled = base_date + timedelta(days=(match_number // 4), hours=(i % 3) * 3)
                db.add(
                    Match(
                        id=_new_uuid(),
                        match_number=match_number,
                        phase=PHASE_GROUP,
                        group_id=group.id,
                        home_team_id=home.id,
                        away_team_id=away.id,
                        home_team_slot=None,
                        away_team_slot=None,
                        scheduled_at=scheduled,
                        status=STATUS_SCHEDULED,
                    )
                )
                match_number += 1

        elimination_phases = [
            (PHASE_R32, 16),
            (PHASE_R16, 8),
            (PHASE_QF, 4),
            (PHASE_SF, 2),
            (PHASE_THIRD_PLACE, 1),
            (PHASE_FINAL, 1),
        ]

        for phase, count in elimination_phases:
            for i in range(count):
                scheduled = base_date + timedelta(days=(match_number // 4), hours=(i % 3) * 3)
                db.add(
                    Match(
                        id=_new_uuid(),
                        match_number=match_number,
                        phase=phase,
                        group_id=None,
                        home_team_id=None,
                        away_team_id=None,
                        home_team_slot=None,
                        away_team_slot=None,
                        scheduled_at=scheduled,
                        status=STATUS_SCHEDULED,
                    )
                )
                match_number += 1

        db.commit()
        total_matches = match_number - 1
        print(
            f"Seed completo: {len(GROUPS_DATA)} grupos, "
            f"{sum(len(t) for _, t in GROUPS_DATA)} equipos, "
            f"{total_matches} partidos (72 fase de grupos + 32 segunda fase)."
        )


if __name__ == "__main__":
    seed()
