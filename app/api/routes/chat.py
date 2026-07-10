import json

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse

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


@router.post("/chat/stream")
def chat_stream(req: ChatRequest, service: AydaService = Depends(get_service)):
    """Versão em streaming (Server-Sent Events) do /chat.

    Emite um evento por passo do agente (ferramenta iniciada, ferramenta
    concluída) e um evento final com a resposta completa. É este endpoint
    que o backend Node.js consome e repassa ao frontend para que a janela
    da Ayda mostre a automação acontecendo em tempo real.
    """
    contexto = ContextoUsuario(**req.contexto.model_dump()) if req.contexto else None
    historico = [MensagemChat(m.papel, m.conteudo) for m in req.historico]

    def gerar():
        try:
            for evento in service.conversar_stream(req.pergunta, historico, contexto):
                yield f"data: {json.dumps(evento, ensure_ascii=False)}\n\n"
        except AydaError as exc:
            erro = {"tipo": "erro", "dados": {"mensagem": str(exc)}}
            yield f"data: {json.dumps(erro, ensure_ascii=False)}\n\n"
        except Exception as exc:  # noqa: BLE001
            erro = {"tipo": "erro", "dados": {"mensagem": f"Erro inesperado: {exc}"}}
            yield f"data: {json.dumps(erro, ensure_ascii=False)}\n\n"
        yield "event: end\ndata: {}\n\n"

    return StreamingResponse(
        gerar(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            # Evita que proxies (nginx/render) façam buffer da resposta em chunks.
            "X-Accel-Buffering": "no",
        },
    )


@router.post("/ingest", response_model=IngestResponse)
def ingest(service: AydaService = Depends(get_service)):
    """(Re)constrói o índice RAG a partir dos .md da base de conhecimento."""
    try:
        n = service.ingerir_conhecimento()
        return IngestResponse(fragmentos_indexados=n)
    except AydaError as exc:
        raise HTTPException(status_code=500, detail=str(exc))
