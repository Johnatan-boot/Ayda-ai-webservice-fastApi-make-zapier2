"""Entidades e DTOs de domínio (independentes de framework)."""
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any


class Papel(str, Enum):
    """Papéis RBAC - espelham o backend KingStar."""
    SUPER_ADMIN = "SUPER_ADMIN"
    ADMIN = "ADMIN"
    GESTOR = "GESTOR"
    COMPRAS = "COMPRAS"
    PCL = "PCL"
    ANALITICA = "ANALITICA"
    RECEBIMENTO = "RECEBIMENTO"
    CONFERENCIA = "CONFERENCIA"
    ESTOQUE = "ESTOQUE"


ACESSO_TOTAL = {Papel.SUPER_ADMIN, Papel.ADMIN, Papel.GESTOR, Papel.COMPRAS, Papel.PCL, Papel.ANALITICA}


@dataclass
class ContextoUsuario:
    """Quem está perguntando - usado para autorizar dados sigilosos."""
    user_id: str = ""
    nome: str = ""
    funcao: str = "RECEBIMENTO"

    @property
    def pode_ver_sigiloso(self) -> bool:
        try:
            return Papel(self.funcao) in ACESSO_TOTAL
        except ValueError:
            return False


@dataclass
class MensagemChat:
    papel: str  # "user" | "assistant"
    conteudo: str


@dataclass
class RespostaAgente:
    resposta: str
    ferramentas_usadas: list[str] = field(default_factory=list)
    metadados: dict[str, Any] = field(default_factory=dict)
    gerado_em: datetime = field(default_factory=datetime.utcnow)
