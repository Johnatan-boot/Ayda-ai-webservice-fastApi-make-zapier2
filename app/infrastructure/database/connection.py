"""Engine SQLAlchemy (somente leitura) para o banco da operacao KingStar."""
from sqlalchemy import create_engine
from sqlalchemy.engine import Engine

from app.core.config import Settings
from app.core.logging import get_logger

logger = get_logger(__name__)


def _validar_senha_latin1(settings: Settings) -> None:
    """O driver pymysql codifica a SENHA em latin-1. Caracteres como travessao
    longo ou espacos invisiveis quebram a conexao com erro criptico. Detectamos
    cedo e damos uma mensagem clara."""
    try:
        settings.db_password.encode("latin1")
    except UnicodeEncodeError as exc:
        ch = settings.db_password[exc.start]
        raise RuntimeError(
            "DB_PASSWORD contem um caractere invalido para a conexao MySQL "
            f"(caractere {ch!r} na posicao {exc.start}). Abra o .env e redigite "
            "a senha na mao (ou deixe vazia se for XAMPP local)."
        ) from None


def criar_engine(settings: Settings) -> Engine | None:
    if not settings.db_configured:
        logger.warning("Banco nao configurado - ferramentas de dados em tempo real inativas.")
        return None

    _validar_senha_latin1(settings)

    engine = create_engine(
        settings.database_url,
        connect_args={"charset": "utf8mb4"},
        pool_pre_ping=True,
        pool_recycle=1800,
        pool_size=5,
        max_overflow=5,
    )
    logger.info("Engine MySQL criado para %s (utf8mb4).", settings.db_name)
    return engine
