"""Estado do grafo LangGraph."""
from typing import Annotated, TypedDict

from langgraph.graph.message import add_messages


class EstadoAgente(TypedDict):
    # add_messages acumula o histórico de mensagens entre os nós.
    messages: Annotated[list, add_messages]
