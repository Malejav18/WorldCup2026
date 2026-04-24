"""Implementacion del patron Outbox como reemplazo de Kafka.

Flujo:
  1) El servicio escribe un registro en su tabla local `outbox_events` dentro de
     la misma transaccion de negocio (ej: al crear un usuario tambien inserta el
     evento `auth.user.registered`).
  2) Un asyncio.Task de background (OutboxDispatcher) consulta periodicamente los
     eventos PENDING y los despacha via HTTP al endpoint interno del servicio
     consumidor.
  3) Si la llamada HTTP es exitosa marca el evento como SENT. Si falla, incrementa
     `attempts` y reintenta; tras `max_attempts` lo marca como FAILED.

Esto garantiza entrega at-least-once sin broker de mensajeria.
"""
from __future__ import annotations

import asyncio
import json
import logging
from datetime import datetime
from typing import Type

import httpx
from sqlalchemy import DateTime, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, sessionmaker

logger = logging.getLogger(__name__)


STATUS_PENDING = "PENDING"
STATUS_SENT = "SENT"
STATUS_FAILED = "FAILED"


class OutboxEventMixin:
    """Mixin con las columnas del outbox. Cada servicio crea su propia clase
    combinando este mixin con su `Base` local, de modo que la tabla vive en el
    archivo SQLite de ese servicio.
    """

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    aggregate_type: Mapped[str] = mapped_column(String(50), nullable=False)
    event_type: Mapped[str] = mapped_column(String(100), nullable=False)
    payload: Mapped[str] = mapped_column(Text, nullable=False)  # JSON serializado
    target_service: Mapped[str] = mapped_column(String(50), nullable=False)
    target_endpoint: Mapped[str] = mapped_column(String(200), nullable=False)
    status: Mapped[str] = mapped_column(String(20), nullable=False, default=STATUS_PENDING, index=True)
    attempts: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    last_error: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.utcnow)
    sent_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)


class OutboxDispatcher:
    """Poll-based dispatcher. Corre como un asyncio.Task dentro del lifespan de FastAPI."""

    def __init__(
        self,
        *,
        session_factory: sessionmaker,
        outbox_model: Type,
        service_urls: dict[str, str],
        poll_interval_seconds: float = 2.0,
        max_attempts: int = 5,
        batch_size: int = 20,
        request_timeout_seconds: float = 10.0,
    ) -> None:
        self.session_factory = session_factory
        self.outbox_model = outbox_model
        self.service_urls = service_urls
        self.poll_interval = poll_interval_seconds
        self.max_attempts = max_attempts
        self.batch_size = batch_size
        self.request_timeout = request_timeout_seconds
        self._task: asyncio.Task | None = None
        self._stop = asyncio.Event()

    def start(self) -> None:
        self._stop.clear()
        self._task = asyncio.create_task(self._run(), name="outbox-dispatcher")

    async def stop(self) -> None:
        self._stop.set()
        if self._task is not None:
            try:
                await self._task
            except asyncio.CancelledError:
                pass

    async def _run(self) -> None:
        async with httpx.AsyncClient(timeout=self.request_timeout) as client:
            while not self._stop.is_set():
                try:
                    await self._process_batch(client)
                except Exception:
                    logger.exception("Outbox dispatcher iteration failed")
                try:
                    await asyncio.wait_for(self._stop.wait(), timeout=self.poll_interval)
                except asyncio.TimeoutError:
                    pass

    async def _process_batch(self, client: httpx.AsyncClient) -> None:
        pending = await asyncio.to_thread(self._fetch_pending)
        for event_id, target_service, target_endpoint, payload in pending:
            await self._dispatch_one(client, event_id, target_service, target_endpoint, payload)

    def _fetch_pending(self) -> list[tuple[int, str, str, str]]:
        with self.session_factory() as db:
            rows = (
                db.query(self.outbox_model)
                .filter(self.outbox_model.status == STATUS_PENDING)
                .filter(self.outbox_model.attempts < self.max_attempts)
                .order_by(self.outbox_model.id)
                .limit(self.batch_size)
                .all()
            )
            return [(r.id, r.target_service, r.target_endpoint, r.payload) for r in rows]

    async def _dispatch_one(
        self,
        client: httpx.AsyncClient,
        event_id: int,
        target_service: str,
        target_endpoint: str,
        payload_json: str,
    ) -> None:
        base_url = self.service_urls.get(target_service)
        if not base_url:
            logger.error("Outbox event %s has unknown target_service=%s", event_id, target_service)
            await asyncio.to_thread(self._mark_failed, event_id, f"Unknown service: {target_service}")
            return
        url = f"{base_url.rstrip('/')}{target_endpoint}"
        try:
            payload = json.loads(payload_json)
            response = await client.post(url, json=payload)
            response.raise_for_status()
            await asyncio.to_thread(self._mark_sent, event_id)
            logger.info("Outbox event %s -> %s %s OK", event_id, target_service, target_endpoint)
        except Exception as e:
            logger.warning("Outbox event %s dispatch failed: %s", event_id, e)
            await asyncio.to_thread(self._mark_failed, event_id, str(e))

    def _mark_sent(self, event_id: int) -> None:
        with self.session_factory() as db:
            event = db.get(self.outbox_model, event_id)
            if event is None:
                return
            event.status = STATUS_SENT
            event.sent_at = datetime.utcnow()
            db.commit()

    def _mark_failed(self, event_id: int, error: str) -> None:
        with self.session_factory() as db:
            event = db.get(self.outbox_model, event_id)
            if event is None:
                return
            event.attempts += 1
            event.last_error = error[:500]
            if event.attempts >= self.max_attempts:
                event.status = STATUS_FAILED
            db.commit()
