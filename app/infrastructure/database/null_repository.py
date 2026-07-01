"""Implementacao nula (Null Object) - usada quando o banco nao esta configurado."""
from typing import Any

from app.domain.interfaces import PurchasingDataRepository

_INDISPONIVEL = {"erro": "Banco da operacao nao configurado neste ambiente."}


class NullPurchasingRepository(PurchasingDataRepository):
    def resumo_pedidos(self, dias: int = 30) -> dict[str, Any]:
        return dict(_INDISPONIVEL)

    def pedidos_por_status(self, status: str, limite: int = 20) -> list[dict[str, Any]]:
        return []

    def kpis_compras(self, dias: int = 30) -> dict[str, Any]:
        return dict(_INDISPONIVEL)

    def itens_em_atraso(self, limite: int = 20) -> list[dict[str, Any]]:
        return []

    def volume_por_categoria(self, dias: int = 30) -> list[dict[str, Any]]:
        return []

    def pecas_a_chegar(self) -> list[dict[str, Any]]:
        return []

    def ranking_fornecedores(self, dias: int = 90) -> list[dict[str, Any]]:
        return []

    def agenda_de_chegada(self, dias: int = 7) -> list[dict[str, Any]]:
        return []
