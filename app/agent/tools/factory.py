"""Monta as ferramentas (tools) do agente a partir das dependencias injetadas.

Cada tool e uma capacidade que o LLM pode decidir chamar. Recebemos as
abstracoes (retriever, repositorio, alertador) por injecao - as tools nao
conhecem Chroma, MySQL ou Make diretamente (separacao de responsabilidades).
"""
import json

from langchain_core.tools import StructuredTool

from app.domain.interfaces import AlertSender, KnowledgeRetriever, PurchasingDataRepository


def _json(obj) -> str:
    return json.dumps(obj, ensure_ascii=False, default=str)


def construir_tools(
    retriever: KnowledgeRetriever,
    repo: PurchasingDataRepository,
    alertador: AlertSender,
) -> list[StructuredTool]:

    # ---- Conhecimento (RAG) ----
    def buscar_conhecimento_logistica(pergunta: str) -> str:
        """Busca conhecimento conceitual sobre logistica, planejamento e compras
        (definicoes, formulas, KPIs, boas praticas). Use para perguntas teoricas."""
        trechos = retriever.buscar(pergunta, k=4)
        return "\n\n---\n\n".join(trechos) if trechos else "Nada encontrado na base."

    # ---- Dados em tempo real: visao geral ----
    def resumo_de_compras(dias: int = 30) -> str:
        """Resumo em tempo real dos pedidos de compra dos ultimos N dias
        (totais por status, numero de fornecedores)."""
        return _json(repo.resumo_pedidos(dias))

    def kpis_de_compras(dias: int = 30) -> str:
        """KPIs de compras dos ultimos N dias: volume, tempo medio de ciclo,
        taxa de cancelamento e de conclusao."""
        return _json(repo.kpis_compras(dias))

    def pedidos_por_status(status: str, limite: int = 20) -> str:
        """Lista pedidos por status. Valores validos: PENDING, RECEIVING,
        CONFERENCE, COMPLETED, CANCELLED."""
        return _json(repo.pedidos_por_status(status.upper(), limite))

    def pedidos_em_atraso(limite: int = 20) -> str:
        """Pedidos ainda em aberto ha mais tempo - risco de ruptura. Use para
        priorizacao e follow-up de compras."""
        return _json(repo.itens_em_atraso(limite))

    # ---- Novas capacidades ----
    def volume_por_categoria(dias: int = 30) -> str:
        """Quantidade de PECAS por categoria de produto (Cama Box, Cama Box Bau,
        Colchao, Acessorios) nos ultimos N dias. Use quando perguntarem sobre
        volume fisico, quantas pecas, ou comparacao entre categorias."""
        return _json(repo.volume_por_categoria(dias))

    def pecas_a_chegar() -> str:
        """Pecas que ainda vao chegar (pedidos em aberto), agrupadas por categoria.
        Use para perguntas como 'quantas pecas de cama box bau estao para chegar'."""
        return _json(repo.pecas_a_chegar())

    def ranking_de_fornecedores(dias: int = 90) -> str:
        """Desempenho por fornecedor: total de pedidos, cancelamentos, pedidos em
        aberto e maior atraso em dias. Use para 'qual fornecedor mais atrasa'."""
        return _json(repo.ranking_fornecedores(dias))

    def agenda_de_chegada(dias: int = 7) -> str:
        """Entregas agendadas para os proximos N dias (fornecedor, NF, data, doca).
        Use para 'o que chega hoje/amanha/esta semana'."""
        return _json(repo.agenda_de_chegada(dias))

    # ---- Acao no mundo real (Make) ----
    def alertar_equipe(assunto: str, mensagem: str, departamento: str = "Compras") -> str:
        """Dispara um alerta para a equipe via automacao (Make/n8n). Use SOMENTE
        quando o usuario pedir explicitamente para avisar/notificar a equipe sobre
        algo critico (ex.: um pedido muito atrasado). Informe assunto e mensagem."""
        ok = alertador.enviar(departamento=departamento, assunto=assunto, mensagem=mensagem)
        if ok:
            return "Alerta enviado para a equipe com sucesso via Make."
        return ("Nao foi possivel enviar o alerta (automacao Make nao configurada "
                "ou indisponivel). Configure MAKE_WEBHOOK_URL no .env.")

    return [
        StructuredTool.from_function(buscar_conhecimento_logistica),
        StructuredTool.from_function(resumo_de_compras),
        StructuredTool.from_function(kpis_de_compras),
        StructuredTool.from_function(pedidos_por_status),
        StructuredTool.from_function(pedidos_em_atraso),
        StructuredTool.from_function(volume_por_categoria),
        StructuredTool.from_function(pecas_a_chegar),
        StructuredTool.from_function(ranking_de_fornecedores),
        StructuredTool.from_function(agenda_de_chegada),
        StructuredTool.from_function(alertar_equipe),
    ]
