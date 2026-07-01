"""Fábrica de LLM multi-provedor.

Groq é o principal (rápido/barato). Se outras chaves estiverem
configuradas, são adicionadas como FALLBACK automático via LangChain -
se o Groq falhar (rate limit, indisponibilidade), cai pro próximo.
"""
from typing import Any

from app.core.config import Settings
from app.core.exceptions import LLMUnavailableError
from app.core.logging import get_logger
from app.domain.interfaces import LLMProvider

logger = get_logger(__name__)


class MultiLLMProvider(LLMProvider):
    def __init__(self, settings: Settings, temperature: float = 0.2):
        self._settings = settings
        self._temperature = temperature

    def get_chat_model(self) -> Any:
        primary = self._build_primary()
        fallbacks = self._build_fallbacks()
        if primary is None:
            if not fallbacks:
                raise LLMUnavailableError(
                    "Nenhum provedor de LLM configurado. Defina GROQ_API_KEY (ou outra)."
                )
            primary, fallbacks = fallbacks[0], fallbacks[1:]
        return primary.with_fallbacks(fallbacks) if fallbacks else primary

    def _build_primary(self) -> Any | None:
        if not self._settings.groq_api_key:
            logger.warning("GROQ_API_KEY ausente - usando fallback como principal.")
            return None
        from langchain_groq import ChatGroq
        return ChatGroq(
            api_key=self._settings.groq_api_key,
            model=self._settings.groq_model,
            temperature=self._temperature,
        )

    def _build_fallbacks(self) -> list[Any]:
        fallbacks: list[Any] = []
        s = self._settings

        if s.openai_api_key:
            try:
                from langchain_openai import ChatOpenAI
                fallbacks.append(ChatOpenAI(api_key=s.openai_api_key, model="gpt-4o-mini",
                                            temperature=self._temperature))
            except ImportError:
                logger.warning("langchain-openai não instalado; fallback OpenAI ignorado.")

        if s.anthropic_api_key:
            try:
                from langchain_anthropic import ChatAnthropic
                fallbacks.append(ChatAnthropic(api_key=s.anthropic_api_key,
                                               model="claude-3-5-haiku-latest",
                                               temperature=self._temperature))
            except ImportError:
                logger.warning("langchain-anthropic não instalado; fallback Anthropic ignorado.")

        if s.google_api_key:
            try:
                from langchain_google_genai import ChatGoogleGenerativeAI
                fallbacks.append(ChatGoogleGenerativeAI(google_api_key=s.google_api_key,
                                                        model="gemini-1.5-flash",
                                                        temperature=self._temperature))
            except ImportError:
                logger.warning("langchain-google-genai não instalado; fallback Google ignorado.")

        if fallbacks:
            logger.info("Fallbacks de LLM ativos: %d provedor(es).", len(fallbacks))
        return fallbacks
