"""Estado de tournament.db (equipos, grupos, partidos, standings, outbox)."""
import sqlite3
from pathlib import Path

db = Path(__file__).resolve().parents[1] / "backend" / "tournament_service" / "data" / "tournament.db"
c = sqlite3.connect(str(db))

print("--- Conteos ---")
for tbl in ("teams", "groups", "matches", "group_standings", "outbox_events"):
    n = c.execute(f"SELECT COUNT(*) FROM {tbl}").fetchone()[0]
    print(f"  {tbl:20}: {n}")

print("\n--- Matches por fase y status ---")
for row in c.execute("SELECT phase, status, COUNT(*) FROM matches GROUP BY phase, status"):
    print(f"  phase={row[0]:10} status={row[1]:10} count={row[2]}")

print("\n--- Outbox events por tipo y estado ---")
for row in c.execute(
    "SELECT event_type, target_service, status, COUNT(*), MAX(attempts) "
    "FROM outbox_events GROUP BY event_type, target_service, status "
    "ORDER BY event_type, target_service"
):
    print(f"  {row[0]:30} -> {row[1]:22} status={row[2]:8} count={row[3]}  max_attempts={row[4]}")

print("\n--- Tournament state ---")
for row in c.execute("SELECT id, status, updated_at FROM tournament_state"):
    print(f"  {row}")

c.close()
