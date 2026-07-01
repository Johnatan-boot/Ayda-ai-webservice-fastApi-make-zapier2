"""Configuração central via variáveis de ambiente (12-factor)."""
from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    # Servidor
    app_env: str = "development"
    app_port: int = 8000
    log_level: str = "INFO"
    cors_origins: str = "http://localhost:3000"

    # LLM principal
    llm_provider: str = "groq"
    groq_api_key: str = ""
    groq_model: str = "llama-3.3-70b-versatile"

    # Fallbacks
    openai_api_key: str = ""
    anthropic_api_key: str = ""
    google_api_key: str = ""

    # Automacao (Make / n8n)
    make_webhook_url: str = ""

    # RAG
    embedding_model: str = "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"
    vector_dir: str = "./data/chroma"
    knowledge_dir: str = "./data/knowledge"

    # Banco da operação
    db_host: str = ""
    db_port: int = 3306
    db_user: str = ""
    db_password: str = ""
    db_name: str = ""

    @property
    def cors_list(self) -> list[str]:
        return [o.strip() for o in self.cors_origins.split(",") if o.strip()]

    @property
    def database_url(self) -> str:
        return (
            f"mysql+pymysql://{self.db_user}:{self.db_password}"
            f"@{self.db_host}:{self.db_port}/{self.db_name}"
        )

    @property
    def db_configured(self) -> bool:
        return all([self.db_host, self.db_user, self.db_name])


@lru_cache
def get_settings() -> Settings:
    return Settings()
