"""Composition Root - monta o grafo de dependencias uma unica vez."""
from app.agent.graph import AydaAgent
from app.agent.tools.factory import construir_tools
from app.core.config import Settings, get_settings
from app.core.logging import get_logger
from app.domain.interfaces import AlertSender, KnowledgeRetriever, PurchasingDataRepository
from app.infrastructure.automation.make_service import MakeAlertSender
from app.infrastructure.database.connection import criar_engine
from app.infrastructure.database.null_repository import NullPurchasingRepository
from app.infrastructure.database.purchasing_repository import MySQLPurchasingRepository
from app.infrastructure.llm.provider_factory import MultiLLMProvider
from app.infrastructure.rag.vector_store import ChromaKnowledgeRetriever

logger = get_logger(__name__)


class Container:
    def __init__(self, settings: Settings | None = None):
        self.settings = settings or get_settings()
        self.retriever: KnowledgeRetriever = ChromaKnowledgeRetriever(self.settings)
        self.repo: PurchasingDataRepository = self._build_repo()
        self.alertador: AlertSender = MakeAlertSender(self.settings.make_webhook_url)
        self._agent: AydaAgent | None = None

    def _build_repo(self) -> PurchasingDataRepository:
        engine = criar_engine(self.settings)
        if engine is None:
            return NullPurchasingRepository()
        return MySQLPurchasingRepository(engine)

    @property
    def agent(self) -> AydaAgent:
        if self._agent is None:
            chat_model = MultiLLMProvider(self.settings).get_chat_model()
            tools = construir_tools(self.retriever, self.repo, self.alertador)
            self._agent = AydaAgent(chat_model, tools)
            logger.info("Agente AYDA inicializado com %d ferramentas.", len(tools))
        return self._agent
