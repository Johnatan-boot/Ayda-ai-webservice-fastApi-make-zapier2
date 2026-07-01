"""Entrypoint do microserviço AYDA."""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes import chat, health
from app.core.config import get_settings
from app.core.logging import setup_logging

setup_logging()
settings = get_settings()

app = FastAPI(
    title="AYDA - AI Service (Logística & Compras)",
    version="0.1.0",
    description="Agente de IA (LangGraph + RAG + Groq) para a operação KingStar.",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_list,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(health.router)
app.include_router(chat.router, prefix="/api/v1")


@app.get("/")
def root():
    return {"service": "ayda-ai-service", "docs": "/docs"}
