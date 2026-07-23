"""Agente AYDA orquestrado com LangGraph.

Padrão ReAct: o nó 'agente' decide; se pedir ferramenta, vai ao nó 'tools'
e retorna ao 'agente'; quando não houver mais chamadas, finaliza.

   START → agente → (tools? ) → agente → ... → END
"""
from langchain_core.messages import SystemMessage
from langgraph.graph import START, END, StateGraph
from langgraph.prebuilt import ToolNode, tools_condition

from app.agent.prompts import SYSTEM_PROMPT
from app.agent.state import EstadoAgente
from app.core.logging import get_logger

logger = get_logger(__name__)


class AydaAgent:
    def __init__(self, chat_model, tools):
        self._tools = tools
        self._llm = chat_model.bind_tools(tools)
        self._app = self._build_graph()

    @property
    def tools(self):
        """Lista de ferramentas (tools) disponiveis para o agente."""
        return self._tools

    def _build_graph(self):
        graph = StateGraph(EstadoAgente)

        def no_agente(state: EstadoAgente):
            mensagens = [SystemMessage(content=SYSTEM_PROMPT), *state["messages"]]
            resposta = self._llm.invoke(mensagens)
            return {"messages": [resposta]}

        graph.add_node("agente", no_agente)
        graph.add_node("tools", ToolNode(self._tools))

        graph.add_edge(START, "agente")
        # tools_condition: se a última mensagem pediu tool → "tools", senão → END
        graph.add_conditional_edges("agente", tools_condition, {"tools": "tools", END: END})
        graph.add_edge("tools", "agente")

        return graph.compile()

    def invoke(self, messages: list) -> dict:
        """Recebe mensagens LangChain e devolve o estado final (modo síncrono, sem streaming)."""
        return self._app.invoke(
            {"messages": messages},
            config={"recursion_limit": 50}
        )

    def stream_eventos(self, messages: list):
        """Gera atualizações incrementais do grafo, nó a nó (modo streaming).

        A cada passo do LangGraph (nó 'agente' decidindo, nó 'tools' executando
        uma automação), este generator emite o update correspondente. É isso que
        permite ao frontend "ver" a automação acontecendo em tempo real, em vez
        de esperar em silêncio pela resposta final.
        """
        yield from self._app.stream(
            {"messages": messages},
            config={"recursion_limit": 50},
            stream_mode="updates",
        )