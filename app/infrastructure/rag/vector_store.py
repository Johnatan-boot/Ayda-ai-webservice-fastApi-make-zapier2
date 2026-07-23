"""Pipeline de RAG: indexa a base de conhecimento e recupera trechos.

- Embeddings locais (HuggingFace multilíngue) → sem custo de API, funciona offline.
- Vector store Chroma persistido em disco.
- Implementa a porta KnowledgeRetriever (DIP).
"""
import os
from pathlib import Path

from app.core.config import Settings
from app.core.exceptions import KnowledgeBaseError
from app.core.logging import get_logger
from app.domain.interfaces import KnowledgeRetriever

logger = get_logger(__name__)


class ChromaKnowledgeRetriever(KnowledgeRetriever):
    def __init__(self, settings: Settings):
        self._settings = settings
        self._store = None  # carregamento preguiçoso

    # ── construção do índice ──────────────────────────────────────
    def ingerir(self) -> int:
        """Lê os .md da base, fragmenta e (re)constrói o índice vetorial."""
        from langchain_text_splitters import RecursiveCharacterTextSplitter
        from langchain_community.document_loaders import TextLoader

        docs = []
        knowledge_dir = Path(self._settings.knowledge_dir)
        arquivos = sorted(knowledge_dir.glob("*.md"))
        if not arquivos:
            raise KnowledgeBaseError(f"Nenhum .md encontrado em {knowledge_dir}")

        for arq in arquivos:
            docs.extend(TextLoader(str(arq), encoding="utf-8").load())

        splitter = RecursiveCharacterTextSplitter(chunk_size=800, chunk_overlap=120)
        chunks = splitter.split_documents(docs)

        store = self._get_store()
        ids_existentes = store.get().get("ids", [])
        if ids_existentes:
            store.delete(ids=ids_existentes)
            logger.info("RAG: %d fragmentos antigos removidos antes de reindexar.", len(ids_existentes))
        store.add_documents(chunks)
        logger.info("RAG indexado: %d arquivos, %d fragmentos.", len(arquivos), len(chunks))
        return len(chunks)

    # ── consulta ──────────────────────────────────────────────────
    def buscar(self, consulta: str, k: int = 4) -> list[str]:
        try:
            store = self._get_store()
            achados = store.similarity_search(consulta, k=k)
            return [d.page_content for d in achados]
        except Exception as exc:  # noqa: BLE001
            logger.error("Falha na busca RAG: %s", exc)
            return []

    # ── infra interna ─────────────────────────────────────────────
    def _get_store(self):
        if self._store is None:
            from langchain_chroma import Chroma
            from langchain_huggingface import HuggingFaceEmbeddings

            os.makedirs(self._settings.vector_dir, exist_ok=True)
            embeddings = HuggingFaceEmbeddings(model_name=self._settings.embedding_model)
            self._store = Chroma(
                collection_name="ayda_logistica",
                embedding_function=embeddings,
                persist_directory=self._settings.vector_dir,
            )
        return self._store
