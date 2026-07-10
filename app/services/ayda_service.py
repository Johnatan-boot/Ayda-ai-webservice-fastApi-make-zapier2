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

    def conversar_stream(
        self,
        pergunta: str,
        historico: list[MensagemChat] | None = None,
        contexto: ContextoUsuario | None = None,
    ):
        """Versão streaming de `conversar`: emite eventos incrementais conforme
        o agente decide usar ferramentas (automações) e conforme cada uma
        termina, além do evento final com a resposta completa.

        Cada evento é um dict com `tipo` e `dados`, pronto para ser serializado
        como SSE pela rota HTTP.
        """
        mensagens = self._montar_mensagens(pergunta, historico or [])

        yield {
            "tipo": "inicio",
            "dados": {"mensagem": "Ayda recebeu a pergunta e está analisando..."},
        }

        ferramentas_usadas: list[str] = []
        resposta_final = ""

        for update in self._container.agent.stream_eventos(mensagens):
            for node_name, node_output in update.items():
                msgs = (node_output or {}).get("messages", [])

                if node_name == "agente":
                    for m in msgs:
                        tool_calls = getattr(m, "tool_calls", None) or []
                        if tool_calls:
                            for tc in tool_calls:
                                nome = tc.get("name") if isinstance(tc, dict) else getattr(tc, "name", None)
                                args = tc.get("args") if isinstance(tc, dict) else getattr(tc, "args", None)
                                if nome:
                                    ferramentas_usadas.append(nome)
                                yield {
                                    "tipo": "ferramenta_iniciada",
                                    "dados": {"ferramenta": nome, "argumentos": args},
                                }
                        elif getattr(m, "content", None):
                            resposta_final = m.content

                elif node_name == "tools":
                    for m in msgs:
                        nome = getattr(m, "name", None)
                        conteudo = getattr(m, "content", "")
                        preview = conteudo if isinstance(conteudo, str) else str(conteudo)
                        if len(preview) > 400:
                            preview = preview[:400] + "…"
                        yield {
                            "tipo": "ferramenta_concluida",
                            "dados": {"ferramenta": nome, "resultado_preview": preview},
                        }

        yield {
            "tipo": "resposta_final",
            "dados": {
                "resposta": resposta_final,
                "ferramentas_usadas": ferramentas_usadas,
                "metadados": {
                    "papel": contexto.funcao if contexto else "N/A",
                },
            },
        }

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
