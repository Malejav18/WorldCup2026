"""Logica de negocio del ranking-service.

Consume `scoring.user.points.updated` para mantener la tabla `user_rankings`.
Expone queries del ranking global y la posicion del usuario autenticado.

Para enriquecer el listado con `display_name` consulta al user-service via HTTP
en batch (una llamada por usuario del top visible). Para el proyecto academico
es aceptable; en produccion lo cachearia o denormalizaria.
"""
import logging

import httpx
from sqlalchemy.orm import Session

from ranking_service.app.config import Settings
from ranking_service.app.dtos.ranking_dtos import (
    GlobalRankingPage,
    MyPosition,
    PointsUpdatedEvent,
    RankingEntry,
)
from ranking_service.app.repositories.user_ranking_repository import UserRankingRepository


logger = logging.getLogger(__name__)


class RankingService:
    def __init__(self, db: Session, settings: Settings):
        self.db = db
        self.settings = settings
        self.rankings = UserRankingRepository(db)

    def handle_points_updated(self, event: PointsUpdatedEvent) -> None:
        """Upsert del total del usuario. Idempotente: el valor es absoluto."""
        self.rankings.upsert(event.user_id, event.new_total_points)
        self.db.commit()

    def global_ranking(self, *, page: int, page_size: int) -> GlobalRankingPage:
        page = max(1, page)
        page_size = max(1, min(page_size, 100))
        offset = (page - 1) * page_size
        rows = self.rankings.list_global(offset=offset, limit=page_size)
        total = self.rankings.count_users()

        names = self._fetch_display_names([r.user_id for r in rows])
        entries = [
            RankingEntry(
                position=offset + i + 1,
                user_id=r.user_id,
                display_name=names.get(r.user_id),
                total_points=r.total_points,
            )
            for i, r in enumerate(rows)
        ]
        return GlobalRankingPage(total_users=total, page=page, page_size=page_size, entries=entries)

    def my_position(self, user_id: str) -> MyPosition:
        row = self.rankings.get(user_id)
        total = self.rankings.count_users()
        if row is None:
            return MyPosition(user_id=user_id, position=None, total_points=0, total_users=total)
        return MyPosition(
            user_id=user_id,
            position=self.rankings.position_of(user_id),
            total_points=row.total_points,
            total_users=total,
        )

    # ---- Helpers ----

    def _fetch_display_names(self, user_ids: list[str]) -> dict[str, str]:
        """Enriquece con display_name consultando al user-service (best-effort).

        Si user-service no responde, sigue sin los nombres (se devuelve None por usuario).
        """
        out: dict[str, str] = {}
        base = self.settings.user_service_url.rstrip("/")
        # Usar un client sync con timeout bajo; el endpoint es liviano.
        with httpx.Client(timeout=3.0) as client:
            for uid in user_ids:
                try:
                    resp = client.get(f"{base}/internal/users/{uid}")
                    if resp.status_code == 200:
                        data = resp.json()
                        if isinstance(data, dict) and "display_name" in data:
                            out[uid] = data["display_name"]
                except httpx.HTTPError as e:
                    logger.warning("Failed to fetch display_name for %s: %s", uid, e)
        return out
