"""Serviço de aplicação: traduz DTOs ↔ agente e extrai a resposta."""
from langchain_core.messages import AIMessage, HumanMessage

from app.domain.models import ContextoUsuario, MensagemChat, RespostaAgente
from app.services.container import Container


class AydaService:
    def __init__(self, container: Container):
        self._container = container

    def conversar(
        self,
        pergunta: str,
        historico: list[MensagemChat] | None = None,
        contexto: ContextoUsuario | None = None,
    ) -> RespostaAgente:  
        mensagens = self._montar_mensagens(pergunta, historico or [])
        estado = self._container.agent.invoke(mensagens)

        msgs = estado["messages"]
        resposta = msgs[-1].content if msgs else ""
        ferramentas = self._extrair_ferramentas(msgs)

        return RespostaAgente(
    resposta=resposta,
    ferramentas_usadas=ferramentas,
    metadados={
        "papel": contexto.funcao if contexto else "N/A",
        "ferramentas_disponiveis": self.listar_ferramentas()
    },
)

    def ingerir_conhecimento(self) -> int:
        return self._container.retriever.ingerir()  # type: ignore[attr-defined]

    @staticmethod
    def _montar_mensagens(pergunta: str, historico: list[MensagemChat]):
        msgs = []
        for m in historico:
            msgs.append(HumanMessage(m.conteudo) if m.papel == "user" else AIMessage(m.conteudo))
        msgs.append(HumanMessage(pergunta))
        return msgs

    def listar_ferramentas(self):
        return [tool.name for tool in self._container.agent._tools]    

    @staticmethod
    def _extrair_ferramentas(msgs) -> list[str]:
        usadas: list[str] = []
        for m in msgs:
            for tc in getattr(m, "tool_calls", None) or []:
                nome = tc.get("name") if isinstance(tc, dict) else getattr(tc, "name", None)
                if nome:
                    usadas.append(nome)
        return usadas
