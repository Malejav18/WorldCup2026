"""MockSender: simula el envio a SendGrid / FCM / APNs.

En vez de llamar a los proveedores reales, persiste la notificacion en la BD y
la escribe a consola con un prefijo identificable. El "external_reference" es
un uuid ficticio para simular el id del proveedor.

En produccion, sustituir por clientes reales:
  - EmailSender (SendGrid / AWS SES)
  - PushSender (FCM para Android/Web, APNs para iOS)
"""
import logging
import uuid

logger = logging.getLogger("notification.mock")


class MockSender:
    def send_email(self, *, to: str, subject: str, body: str) -> str:
        ref = f"mock-email-{uuid.uuid4()}"
        logger.info("[MOCK-EMAIL] to=%s subject=%s\n%s\n--- ref=%s ---", to, subject, body, ref)
        return ref

    def send_push(self, *, to_user_id: str, subject: str, body: str) -> str:
        ref = f"mock-push-{uuid.uuid4()}"
        logger.info("[MOCK-PUSH] user=%s subject=%s body=%s (ref=%s)", to_user_id, subject, body, ref)
        return ref
