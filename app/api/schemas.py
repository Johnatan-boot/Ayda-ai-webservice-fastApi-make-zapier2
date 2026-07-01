"""DTOs da API (Pydantic)."""
from pydantic import BaseModel, Field


class MensagemDTO(BaseModel):
    papel: str = Field(..., description="'user' ou 'assistant'")
    conteudo: str


class ContextoDTO(BaseModel):
    user_id: str = ""
    nome: str = ""
    funcao: str = "RECEBIMENTO"


class ChatRequest(BaseModel):
    pergunta: str = Field(..., min_length=1)
    historico: list[MensagemDTO] = Field(default_factory=list)
    contexto: ContextoDTO | None = None


class ChatResponse(BaseModel):
    resposta: str
    ferramentas_usadas: list[str] = []
    metadados: dict = {}


class IngestResponse(BaseModel):
    fragmentos_indexados: int
