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
from tournament_service.app.entities.match import PHASE_GROUP, STATUS_SCHEDULED, Match
from tournament_service.app.entities.team import Team
from tournament_service.app.entities.tournament_state import STATE_PRE_START, TournamentState


# 48 equipos distribuidos en 12 grupos (A..L), 4 equipos por grupo.
# Composicion representativa para fines academicos.
GROUPS_DATA: list[tuple[str, list[tuple[str, str, str]]]] = [
    # (letra_grupo, [(nombre, country_code, confederacion), ...])
    ("A", [("Canada", "CAN", "CONCACAF"), ("Belgica", "BEL", "UEFA"), ("Marruecos", "MAR", "CAF"), ("Corea del Sur", "KOR", "AFC")]),
    ("B", [("Estados Unidos", "USA", "CONCACAF"), ("Paises Bajos", "NED", "UEFA"), ("Japon", "JPN", "AFC"), ("Ghana", "GHA", "CAF")]),
    ("C", [("Mexico", "MEX", "CONCACAF"), ("Croacia", "CRO", "UEFA"), ("Australia", "AUS", "AFC"), ("Nigeria", "NGA", "CAF")]),
    ("D", [("Argentina", "ARG", "CONMEBOL"), ("Polonia", "POL", "UEFA"), ("Senegal", "SEN", "CAF"), ("Costa Rica", "CRC", "CONCACAF")]),
    ("E", [("Francia", "FRA", "UEFA"), ("Dinamarca", "DEN", "UEFA"), ("Tunez", "TUN", "CAF"), ("Iran", "IRN", "AFC")]),
    ("F", [("Brasil", "BRA", "CONMEBOL"), ("Suiza", "SUI", "UEFA"), ("Camerun", "CMR", "CAF"), ("Arabia Saudita", "KSA", "AFC")]),
    ("G", [("Inglaterra", "ENG", "UEFA"), ("Uruguay", "URU", "CONMEBOL"), ("Egipto", "EGY", "CAF"), ("Qatar", "QAT", "AFC")]),
    ("H", [("Espana", "ESP", "UEFA"), ("Colombia", "COL", "CONMEBOL"), ("Costa de Marfil", "CIV", "CAF"), ("Nueva Zelanda", "NZL", "OFC")]),
    ("I", [("Portugal", "POR", "UEFA"), ("Ecuador", "ECU", "CONMEBOL"), ("Argelia", "ALG", "CAF"), ("Jamaica", "JAM", "CONCACAF")]),
    ("J", [("Alemania", "GER", "UEFA"), ("Serbia", "SRB", "UEFA"), ("Panama", "PAN", "CONCACAF"), ("Paraguay", "PAR", "CONMEBOL")]),
    ("K", [("Italia", "ITA", "UEFA"), ("Turquia", "TUR", "UEFA"), ("Venezuela", "VEN", "CONMEBOL"), ("Haiti", "HAI", "CONCACAF")]),
    ("L", [("Paises Bajos B", "PB2", "UEFA"), ("Peru", "PER", "CONMEBOL"), ("Sudafrica", "RSA", "CAF"), ("Jordania", "JOR", "AFC")]),
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

        db.commit()
        print(f"Seed completo: {len(GROUPS_DATA)} grupos, "
              f"{sum(len(t) for _, t in GROUPS_DATA)} equipos, "
              f"{match_number - 1} partidos de fase de grupos.")


if __name__ == "__main__":
    seed()
