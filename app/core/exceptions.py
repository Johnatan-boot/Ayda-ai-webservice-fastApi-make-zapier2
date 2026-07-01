"""Exceções de domínio."""


class AydaError(Exception):
    """Erro base do serviço."""


class LLMUnavailableError(AydaError):
    """Nenhum provedor de LLM pôde ser inicializado."""


class KnowledgeBaseError(AydaError):
    """Falha ao construir/consultar a base de conhecimento (RAG)."""
