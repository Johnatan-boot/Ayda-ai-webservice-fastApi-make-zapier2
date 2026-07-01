# AYDA — AI Service (Logística & Compras)

Microserviço de IA da KingStar: agente autônomo que responde sobre a cadeia
logística e consulta dados reais da operação (módulo de Planejamento e Compras).

## Stack
- **Python 3.12 + FastAPI** (API)
- **LangChain + LangGraph** (orquestração do agente, padrão ReAct)
- **Groq** como LLM principal, com **fallback** automático (OpenAI / Anthropic / Google)
- **RAG** com Chroma + embeddings locais (HuggingFace multilíngue)
- **SQLAlchemy + PyMySQL** (consultas somente-leitura ao MySQL da operação)

## Arquitetura (camadas + SOLID)
- `app/domain` — entidades e **interfaces** (portas). Regras independentes de framework.
- `app/infrastructure` — implementações (Groq, Chroma, MySQL). Trocáveis.
- `app/agent` — grafo LangGraph, ferramentas e prompts.
- `app/services` — **composition root** (injeção de dependências) + serviço de aplicação.
- `app/api` — rotas FastAPI e DTOs.

O agente depende só das abstrações (DIP); a escolha das implementações fica
isolada no `Container`. Quando o banco não está configurado, um `NullRepository`
mantém o agente funcional via RAG (Liskov).

## Como rodar
```bash
cp .env.example .env        # preencha GROQ_API_KEY e (opcional) DB_*
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
# indexar a base de conhecimento (RAG) uma vez:
curl -X POST http://localhost:8000/api/v1/ingest
```

## Endpoints
- `GET  /health` — status do serviço.
- `POST /api/v1/chat` — conversa com a AYDA (`{ "pergunta": "...", "historico": [], "contexto": {...} }`).
- `POST /api/v1/ingest` — (re)constrói o índice RAG.

## Ferramentas do agente (módulo Compras)
- `buscar_conhecimento_logistica` (RAG conceitual)
- `resumo_de_compras`, `kpis_de_compras`, `pedidos_por_status`, `pedidos_em_atraso` (dados em tempo real)

## Automação (N8N / Make / Zapier)
O endpoint `/api/v1/chat` é stateless e webhook-friendly: um fluxo no N8N pode
chamar a AYDA periodicamente (ex.: alertar gestores sobre pedidos em atraso).
