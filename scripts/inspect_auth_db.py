"""Script auxiliar: imprime el estado de la BD de auth-service."""
import sqlite3
import sys
from pathlib import Path

db_path = Path(__file__).resolve().parents[1] / "backend" / "auth_service" / "data" / "auth.db"
if not db_path.exists():
    print(f"BD no existe: {db_path}")
    sys.exit(1)

c = sqlite3.connect(str(db_path))

print("--- Tablas ---")
for row in c.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name"):
    print(f"  {row[0]}")

print("\n--- Usuarios ---")
for row in c.execute("SELECT id, email, role, created_at FROM users ORDER BY created_at"):
    print(f"  {row}")

print("\n--- Refresh tokens ---")
print(f"  total:   {c.execute('SELECT COUNT(*) FROM refresh_tokens').fetchone()[0]}")
print(f"  revoked: {c.execute('SELECT COUNT(*) FROM refresh_tokens WHERE revoked=1').fetchone()[0]}")

print("\n--- Outbox events (por estado / target / attempts) ---")
rows = c.execute(
    "SELECT status, target_service, target_endpoint, attempts, COUNT(*) "
    "FROM outbox_events GROUP BY status, target_service, target_endpoint, attempts "
    "ORDER BY status, target_service"
).fetchall()
for row in rows:
    print(f"  status={row[0]:8} service={row[1]:22} endpoint={row[2]:40} attempts={row[3]}  count={row[4]}")

print("\n--- Ultimo error del outbox (si hay) ---")
row = c.execute(
    "SELECT id, target_service, attempts, last_error FROM outbox_events "
    "WHERE last_error IS NOT NULL ORDER BY id DESC LIMIT 1"
).fetchone()
if row:
    print(f"  event {row[0]} target={row[1]} attempts={row[2]}")
    print(f"  error: {row[3]}")
else:
    print("  (ninguno)")

c.close()
