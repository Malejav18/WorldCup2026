"""Logica de negocio del notification-service.

Para cada tipo de evento que llega, construye un mensaje, lo envia por el canal
correspondiente (mock), y persiste el registro en la BD. Los usuarios pueden
consultar su historial via /notifications/me.
"""
from datetime import datetime

from sqlalchemy.orm import Session

from notification_service.app.dtos.notification_dtos import (
    LeagueMemberAddedEvent,
    MatchCalculatedEvent,
    MatchResultEvent,
    PointsUpdatedEvent,
    StandingsUpdatedEvent,
    UserRegisteredEvent,
)
from notification_service.app.entities.notification import (
    CHANNEL_EMAIL,
    CHANNEL_PUSH,
    STATUS_SENT,
    Notification,
)
from notification_service.app.repositories.notification_repository import NotificationRepository
from notification_service.app.services.mock_sender import MockSender


class NotificationService:
    def __init__(self, db: Session, sender: MockSender | None = None):
        self.db = db
        self.repo = NotificationRepository(db)
        self.sender = sender or MockSender()

    # ---- Handlers de eventos ----

    def on_user_registered(self, event: UserRegisteredEvent) -> Notification:
        subject = "Bienvenido al Mundial 2026"
        body = (
            f"Hola {event.display_name},\n\n"
            "Te registraste con exito en el Sistema de Predicciones del Mundial FIFA 2026.\n"
            "Ingresa tus predicciones antes del 11 de junio de 2026.\n\n"
            "Exitos!"
        )
        ref = self.sender.send_email(to=event.email, subject=subject, body=body)
        return self._persist(event.user_id, "auth.user.registered", CHANNEL_EMAIL, subject, body, ref)

    def on_match_result(self, event: MatchResultEvent) -> int:
        """Emite notificacion push a todos los usuarios que predijeron este partido.

        Como notification-service no tiene acceso directo a las predicciones, en
        esta implementacion registra una unica notificacion "sistema" por match.
        En produccion, se resolveria con un fanout consultando prediction-service.
        """
        subject = "Resultado registrado"
        score = (
            f"{event.home_goals_90}-{event.away_goals_90}"
            if event.home_goals_90 is not None and event.away_goals_90 is not None
            else "N/A"
        )
        body = f"Resultado del partido #{event.match_number} ({event.phase}): {score}. Revisa tus puntos."
        ref = self.sender.send_push(to_user_id="__broadcast__", subject=subject, body=body)
        self._persist("__broadcast__", "match.result.registered", CHANNEL_PUSH, subject, body, ref)
        return 1

    def on_match_calculated(self, event: MatchCalculatedEvent) -> Notification:
        subject = "Puntuacion recalculada" if event.is_correction else "Partido puntuado"
        body = (
            f"Se procesaron los puntajes del partido {event.match_id} (fase {event.phase}). "
            f"Afectadas {event.scores_count} predicciones."
        )
        ref = self.sender.send_push(to_user_id="__system__", subject=subject, body=body)
        return self._persist("__system__", "scoring.match.calculated", CHANNEL_PUSH, subject, body, ref)

    def on_points_updated(self, event: PointsUpdatedEvent) -> Notification:
        subject = "Puntos actualizados"
        body = f"Tu total ahora es {event.new_total_points} pts. Revisa tu posicion en el ranking!"
        ref = self.sender.send_push(to_user_id=event.user_id, subject=subject, body=body)
        return self._persist(event.user_id, "scoring.user.points.updated", CHANNEL_PUSH, subject, body, ref)

    def on_standings_updated(self, event: StandingsUpdatedEvent) -> Notification:
        subject = "Standings actualizadas"
        body = f"Tabla de posiciones del grupo {event.group_id} actualizada."
        ref = self.sender.send_push(to_user_id="__system__", subject=subject, body=body)
        return self._persist("__system__", "group.standings.updated", CHANNEL_PUSH, subject, body, ref)

    def on_league_member_added(self, event: LeagueMemberAddedEvent) -> Notification:
        subject = f"Te uniste a la liga {event.league_name}"
        body = f"Ya formas parte de la liga privada '{event.league_name}'. Exitos!"
        ref = self.sender.send_push(to_user_id=event.user_id, subject=subject, body=body)
        return self._persist(event.user_id, "league.member.added", CHANNEL_PUSH, subject, body, ref)

    # ---- Queries publicas ----

    def list_for_user(self, user_id: str, *, limit: int = 50) -> list[Notification]:
        """Incluye tambien las notificaciones de sistema/broadcast relacionadas a este usuario."""
        return self.repo.list_by_user(user_id, limit=limit)

    def unread_count(self, user_id: str) -> int:
        return self.repo.count_unread_by_user(user_id)

    def mark_read(self, notification_id: int, user_id: str) -> Notification | None:
        notif = self.repo.mark_read(notification_id, user_id)
        if notif is not None:
            self.db.commit()
        return notif

    # ---- Helper ----

    def _persist(
        self,
        user_id: str,
        event_type: str,
        channel: str,
        subject: str,
        body: str,
        external_reference: str,
    ) -> Notification:
        notif = Notification(
            user_id=user_id,
            event_type=event_type,
            channel=channel,
            subject=subject,
            body=body,
            status=STATUS_SENT,
            external_reference=external_reference,
            sent_at=datetime.utcnow(),
        )
        self.repo.create(notif)
        self.db.commit()
        self.db.refresh(notif)
        return notif
