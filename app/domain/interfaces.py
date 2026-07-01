"""Portas (interfaces abstratas) - Dependency Inversion Principle.

As camadas de aplicacao/agente dependem destas abstracoes, nunca das
implementacoes concretas (Groq, Chroma, MySQL, Make).
"""
from abc import ABC, abstractmethod
from typing import Any


class LLMProvider(ABC):
    """Fornece um chat model compativel com LangChain, com fallback."""

    @abstractmethod
    def get_chat_model(self) -> Any:
        ...


class KnowledgeRetriever(ABC):
    """Recupera trechos relevantes da base de conhecimento (RAG)."""

    @abstractmethod
    def buscar(self, consulta: str, k: int = 4) -> list[str]:
        ...


class PurchasingDataRepository(ABC):
    """Acesso somente-leitura aos dados de planejamento e compras."""

    @abstractmethod
    def resumo_pedidos(self, dias: int = 30) -> dict[str, Any]:
        ...

    @abstractmethod
    def pedidos_por_status(self, status: str, limite: int = 20) -> list[dict[str, Any]]:
        ...

    @abstractmethod
    def kpis_compras(self, dias: int = 30) -> dict[str, Any]:
        ...

    @abstractmethod
    def itens_em_atraso(self, limite: int = 20) -> list[dict[str, Any]]:
        ...

    # ---- Novas capacidades do modulo de Compras ----
    @abstractmethod
    def volume_por_categoria(self, dias: int = 30) -> list[dict[str, Any]]:
        """Soma de pecas por categoria de produto (cama box, bau, acessorios...)."""
        ...

    @abstractmethod
    def pecas_a_chegar(self) -> list[dict[str, Any]]:
        """Pecas ainda nao recebidas (pedidos em aberto), agrupadas por categoria."""
        ...

    @abstractmethod
    def ranking_fornecedores(self, dias: int = 90) -> list[dict[str, Any]]:
        """Desempenho por fornecedor: volume, cancelamentos e dias em aberto."""
        ...

    @abstractmethod
    def agenda_de_chegada(self, dias: int = 7) -> list[dict[str, Any]]:
        """Entregas agendadas para os proximos N dias (data, doca, veiculo)."""
        ...


class AlertSender(ABC):
    """Dispara alertas/acoes para o mundo real (ex.: Make/n8n via webhook)."""

    @abstractmethod
    def enviar(self, departamento: str, assunto: str, mensagem: str,
               dados: dict[str, Any] | None = None) -> bool:
        ...
