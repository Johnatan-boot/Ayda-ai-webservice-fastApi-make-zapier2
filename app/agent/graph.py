"""Agente AYDA orquestrado com LangGraph.

Padrão ReAct: o nó 'agente' decide; se pedir ferramenta, vai ao nó 'tools'
e retorna ao 'agente'; quando não houver mais chamadas, finaliza.

   START → agente → (tools? ) → agente → ... → END
"""
from pyexpat.errors import messages

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
     """Recebe mensagens oLangChain e devolve o estado final."""
     return self._app.invoke(
        {"messages": messages},
        config={"recursion_limit": 50}
    )