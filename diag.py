from app.core.config import get_settings
from app.infrastructure.database.connection import criar_engine
from sqlalchemy import text

s = get_settings()
print("DB_HOST:", s.db_host, "| DB_NAME:", s.db_name, "| configurado:", s.db_configured)

engine = criar_engine(s)
print("engine:", engine)

try:
    with engine.connect() as c:
        total = c.execute(text("SELECT COUNT(*) FROM pedidos_compra")).scalar()
        print("TOTAL pedidos:", total)
except Exception as e:
    print("ERRO REAL:", type(e).__name__, "->", e)