"""Repositorio de Planejamento e Compras - consultas SOMENTE LEITURA.

Schema real: pedidos_compra (id, fornecedor_nome, numero_nf, status, data_pedido,
atualizado_em, tipo_veiculo, placa_veiculo, data_agendamento) + itens_pedido
(pedido_compra_id, sku, descricao, quantidade_esperada) + agendamentos.

A categoria do produto e derivada da descricao do item (LIKE accent-insensitive
por causa da collation utf8mb4_unicode_ci). Mantemos o SQL em ASCII puro.
"""
from typing import Any

from sqlalchemy import text
from sqlalchemy.engine import Engine

from app.core.logging import get_logger
from app.domain.interfaces import PurchasingDataRepository

logger = get_logger(__name__)

# Expressao SQL reutilizavel que classifica o item em uma categoria.
_CATEGORIA_CASE = (
    "CASE "
    "WHEN i.descricao LIKE '%bau%' THEN 'Cama Box Bau' "
    "WHEN i.descricao LIKE '%cama box%' OR i.descricao LIKE '%box%' THEN 'Cama Box' "
    "WHEN i.descricao LIKE '%colch%' THEN 'Colchao' "
    "WHEN i.descricao LIKE '%acess%' THEN 'Acessorios' "
    "ELSE 'Outros' END"
)


class MySQLPurchasingRepository(PurchasingDataRepository):
    def __init__(self, engine: Engine):
        self._engine = engine

    def _rows(self, sql: str, params: dict[str, Any] | None = None) -> list[dict[str, Any]]:
        try:
            with self._engine.connect() as conn:
                result = conn.execute(text(sql), params or {})
                return [dict(r._mapping) for r in result]
        except Exception as exc:
            logger.error("ERRO SQL: %s -> %s", type(exc).__name__, exc)
            raise

    # ---- capacidades originais ----
    def resumo_pedidos(self, dias: int = 30) -> dict[str, Any]:
        sql = (
            "SELECT COUNT(*) AS total_pedidos, "
            "SUM(status = 'PENDING') AS pendentes, "
            "SUM(status = 'RECEIVING') AS em_recebimento, "
            "SUM(status = 'CONFERENCE') AS em_conferencia, "
            "SUM(status = 'COMPLETED') AS concluidos, "
            "SUM(status = 'CANCELLED') AS cancelados, "
            "COUNT(DISTINCT fornecedor_nome) AS fornecedores "
            "FROM pedidos_compra "
            "WHERE data_pedido >= (NOW() - INTERVAL :dias DAY)"
        )
        rows = self._rows(sql, {"dias": dias})
        return rows[0] if rows else {}

    def pedidos_por_status(self, status: str, limite: int = 20) -> list[dict[str, Any]]:
        sql = (
            "SELECT id, numero_nf, fornecedor_nome, status, data_pedido "
            "FROM pedidos_compra WHERE status = :status "
            "ORDER BY data_pedido DESC LIMIT :limite"
        )
        return self._rows(sql, {"status": status, "limite": limite})

    def kpis_compras(self, dias: int = 30) -> dict[str, Any]:
        sql = (
            "SELECT COUNT(*) AS pedidos_periodo, "
            "ROUND(AVG(TIMESTAMPDIFF(HOUR, data_pedido, atualizado_em)), 1) AS horas_medias_ciclo, "
            "ROUND(100 * SUM(status = 'CANCELLED') / NULLIF(COUNT(*), 0), 1) AS taxa_cancelamento_pct, "
            "ROUND(100 * SUM(status = 'COMPLETED') / NULLIF(COUNT(*), 0), 1) AS taxa_conclusao_pct "
            "FROM pedidos_compra "
            "WHERE data_pedido >= (NOW() - INTERVAL :dias DAY)"
        )
        rows = self._rows(sql, {"dias": dias})
        return rows[0] if rows else {}

    def itens_em_atraso(self, limite: int = 20) -> list[dict[str, Any]]:
        sql = (
            "SELECT id, numero_nf, fornecedor_nome, status, "
            "DATEDIFF(NOW(), data_pedido) AS dias_em_aberto "
            "FROM pedidos_compra "
            "WHERE status IN ('PENDING', 'RECEIVING', 'CONFERENCE') "
            "ORDER BY data_pedido ASC LIMIT :limite"
        )
        return self._rows(sql, {"limite": limite})

    # ---- novas capacidades ----
    def volume_por_categoria(self, dias: int = 30) -> list[dict[str, Any]]:
        sql = (
            "SELECT " + _CATEGORIA_CASE + " AS categoria, "
            "COUNT(DISTINCT p.id) AS pedidos, "
            "SUM(i.quantidade_esperada) AS total_pecas "
            "FROM pedidos_compra p "
            "JOIN itens_pedido i ON i.pedido_compra_id = p.id "
            "WHERE p.data_pedido >= (NOW() - INTERVAL :dias DAY) "
            "GROUP BY categoria ORDER BY total_pecas DESC"
        )
        return self._rows(sql, {"dias": dias})

    def pecas_a_chegar(self) -> list[dict[str, Any]]:
        # Pecas de pedidos ainda nao concluidos = volume previsto de entrada.
        sql = (
            "SELECT " + _CATEGORIA_CASE + " AS categoria, "
            "COUNT(DISTINCT p.id) AS pedidos_em_aberto, "
            "SUM(i.quantidade_esperada) AS pecas_a_chegar "
            "FROM pedidos_compra p "
            "JOIN itens_pedido i ON i.pedido_compra_id = p.id "
            "WHERE p.status IN ('PENDING', 'RECEIVING', 'CONFERENCE') "
            "GROUP BY categoria ORDER BY pecas_a_chegar DESC"
        )
        return self._rows(sql)

    def ranking_fornecedores(self, dias: int = 90) -> list[dict[str, Any]]:
        sql = (
            "SELECT fornecedor_nome, "
            "COUNT(*) AS total_pedidos, "
            "SUM(status = 'CANCELLED') AS cancelados, "
            "SUM(status IN ('PENDING','RECEIVING','CONFERENCE')) AS em_aberto, "
            "MAX(CASE WHEN status IN ('PENDING','RECEIVING','CONFERENCE') "
            "THEN DATEDIFF(NOW(), data_pedido) ELSE 0 END) AS maior_atraso_dias "
            "FROM pedidos_compra "
            "WHERE data_pedido >= (NOW() - INTERVAL :dias DAY) "
            "GROUP BY fornecedor_nome "
            "ORDER BY maior_atraso_dias DESC, cancelados DESC"
        )
        return self._rows(sql, {"dias": dias})

    def agenda_de_chegada(self, dias: int = 7) -> list[dict[str, Any]]:
        # Le a tabela dedicada de agendamentos (data, doca, fornecedor, NF).
        sql = (
            "SELECT fornecedor_nome, numero_nf, data_agendada, doca, status "
            "FROM agendamentos "
            "WHERE status <> 'CANCELADO' "
            "AND data_agendada BETWEEN NOW() AND (NOW() + INTERVAL :dias DAY) "
            "ORDER BY data_agendada ASC"
        )
        return self._rows(sql, {"dias": dias})
