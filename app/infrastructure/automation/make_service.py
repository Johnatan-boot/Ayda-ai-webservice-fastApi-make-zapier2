"""Integracao com o Make (e/ou n8n) via Webhook.

Implementa a porta AlertSender. A AYDA usa isto como uma "ferramenta de acao":
quando identifica algo critico (ex.: pedido muito atrasado), dispara um POST
para o webhook do Make, que por sua vez notifica a equipe (WhatsApp, Telegram,
e-mail, etc.) ou registra o evento. Provedor-agnostico: o cenario no Make decide
o que fazer com o payload.
"""
from typing import Any

import requests

from app.core.logging import get_logger
from app.domain.interfaces import AlertSender

logger = get_logger(__name__)


class MakeAlertSender(AlertSender):
    def __init__(self, webhook_url: str | None, timeout: int = 10):
        self._url = (webhook_url or "").strip()
        self._timeout = timeout

    @property
    def configurado(self) -> bool:
        return self._url.startswith("http")

    def enviar(self, departamento: str, assunto: str, mensagem: str,
               dados: dict[str, Any] | None = None) -> bool:
        if not self.configurado:
            logger.warning("MAKE_WEBHOOK_URL nao configurada - alerta nao enviado.")
            return False

        payload = {
            "origem": "AYDA",
            "departamento": departamento,
            "assunto": assunto,
            "mensagem": mensagem,
            "dados": dados or {},
        }
        try:
            resp = requests.post(self._url, json=payload, timeout=self._timeout)
            ok = 200 <= resp.status_code < 300
            if ok:
                logger.info("Alerta enviado ao Make (%s).", assunto)
            else:
                logger.error("Make respondeu %s.", resp.status_code)
            return ok
        except Exception as exc:  # noqa: BLE001
            logger.error("Falha ao enviar alerta ao Make: %s", exc)
            return False


class NullAlertSender(AlertSender):
    """Usado quando nenhum webhook esta configurado."""

    def enviar(self, departamento: str, assunto: str, mensagem: str,
               dados: dict[str, Any] | None = None) -> bool:
        return False
