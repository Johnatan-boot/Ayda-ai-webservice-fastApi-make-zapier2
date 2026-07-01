from fastapi import APIRouter

from app.core.config import get_settings

router = APIRouter(tags=["health"])


@router.get("/health")
def health():
    s = get_settings()
    return {
        "status": "online",
        "service": "ayda-ai-service",
        "llm_provider": s.llm_provider,
        "banco_configurado": s.db_configured,
    }
