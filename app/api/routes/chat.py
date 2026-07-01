from fastapi import APIRouter, Depends, HTTPException

from app.api.schemas import ChatRequest, ChatResponse, IngestResponse
from app.core.exceptions import AydaError
from app.domain.models import ContextoUsuario, MensagemChat
from app.services.ayda_service import AydaService
from app.services.container import Container

router = APIRouter(tags=["ayda"])

# Container único por processo (composition root).
_container = Container()
_service = AydaService(_container)


def get_service() -> AydaService:
    return _service


@router.post("/chat", response_model=ChatResponse)
def chat(req: ChatRequest, service: AydaService = Depends(get_service)):
    try:
        contexto = (
            ContextoUsuario(**req.contexto.model_dump()) if req.contexto else None
        )
        historico = [MensagemChat(m.papel, m.conteudo) for m in req.historico]
        resp = service.conversar(req.pergunta, historico, contexto)
        return ChatResponse(
            resposta=resp.resposta,
            ferramentas_usadas=resp.ferramentas_usadas,
            metadados=resp.metadados,
        )
    except AydaError as exc:
        raise HTTPException(status_code=503, detail=str(exc))
    except Exception as exc:  # noqa: BLE001
        raise HTTPException(status_code=500, detail=f"Erro inesperado: {exc}")


@router.post("/ingest", response_model=IngestResponse)
def ingest(service: AydaService = Depends(get_service)):
    """(Re)constrói o índice RAG a partir dos .md da base de conhecimento."""
    try:
        n = service.ingerir_conhecimento()
        return IngestResponse(fragmentos_indexados=n)
    except AydaError as exc:
        raise HTTPException(status_code=500, detail=str(exc))
