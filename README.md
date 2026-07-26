# VeriScope

Research engine for evidence-based answers, source scoring, and step-by-step reasoning.

## What is VeriScope?

VeriScope turns a question into an evidence-backed answer. The backend analyzes intent, resolves ambiguous terms, searches the web with pluggable providers, ranks sources by authority and relevance, and writes a cited narrative with a modern LLM.

The system supports two research modes: a faster linear pipeline and a deeper ReAct agent loop. It works with local inference via Ollama or cloud inference via Groq, and it keeps the frontend and backend configurable for both development and deployment.

## Demo

A short walkthrough of VeriScope in action:

[<video src="main post.mp4" controls width="100%"></video>](https://github.com/user-attachments/assets/3c34db82-9f07-4fae-8ee6-2274e89f3111)

## Research modes

| Mode | Speed | How it works |
|------|-------|-------------|
| Fast | 3–5 min | Single-pass analysis, disambiguation, web search, source scoring, synthesis |
| Deep | 8–15 min | ReAct agent loop with thought/action/observation cycles and multiple searches |

## Features

### Intelligence layer
| Feature | Description |
|---------|-------------|
| Query analysis | Classifies intent, detects domain, and generates targeted search queries |
| Ambiguity resolution | Finds and resolves multi-meaning terms before search starts |
| Source scoring | Combines domain authority and relevance to rank results |
| Confidence calibration | Scores answer confidence based on sources, diversity, and ambiguity |
| Post-processing | Removes LLM artifacts and keeps citations aligned with the answer |

### Research pipeline
| Feature | Description |
|---------|-------------|
| LLM synthesis | LLM writes coherent 5-6 paragraph answers with inline citations |
| ReAct agent loop | Iterative reasoning with tool actions and observations in deep mode |
| Citation filtering | Only sources actually referenced in the final answer are returned |
| Graceful fallback | The pipeline can fall back to non-LLM logic when needed |

### Backend infrastructure
| Feature | Description |
|---------|-------------|
| User authentication | Signup, login, JWT tokens, bcrypt password hashing |
| Email verification | Secure token-based verification with itsdangerous |
| Session history | Research conversations persisted in SQLite and grouped by date |
| Result caching | Exact-match caching, optional semantic caching with sentence-transformers |
| Rate limiting | SlowAPI per-IP rate limits for research and auth endpoints |
| Real-time streaming | SSE endpoint streams pipeline progress to the frontend |

### Frontend
| Feature | Description |
|---------|-------------|
| Landing page | React landing page with direct routing to the dashboard |
| Search input | Configurable prompt input with live mode selection |
| Streaming status | Live progress updates for the research pipeline |
| ReAct thought viewer | Shows reasoning steps during deep mode searches |
| Citation cards | Expandable source cards with confidence indicators |
| Session sidebar | Load, create, and delete past research sessions |
| Stop button | Abort ongoing research with AbortController |

### Pluggable architecture
| Feature | Description |
|---------|-------------|
| Search providers | Brave Search API primary, DuckDuckGo fallback, Mock provider for tests |
| LLM providers | Ollama (local), Groq (cloud), Mock (testing) |
| Deployment config | API URL switching and CORS origins driven by environment variables |

## How the pipeline works

### Linear mode

```
User Query
  │
  ▼
┌─────────────────┐     ┌──────────────────┐     ┌─────────────────┐
│  Query Analysis  │────▶│  Disambiguation  │────▶│   Web Search    │
│  Intent, domain, │     │  Resolve multi-  │     │  Brave / DDG    │
│  ambiguity check │     │  meaning terms   │     │  Deduplicate    │
└─────────────────┘     └──────────────────┘     └────────┬────────┘
                                                          │
  ┌───────────────────────────────────────────────────────┘
  ▼
┌─────────────────┐     ┌──────────────────┐     ┌─────────────────┐
│  Source Scoring  │────▶│  LLM Synthesis   │────▶│  Post-Process   │
│  Authority +     │     │  LLM writes      │     │  Clean artifacts│
│  relevance rank  │     │  cited narrative │     │  Filter cites   │
└─────────────────┘     └──────────────────┘     └────────┬────────┘
                                                          │
                                                          ▼
                                                   JSON Response
                                                   + Confidence
```

### ReAct mode

```
Thought: "The query asks about RAG, which could be ambiguous..."
Action:  disambiguate("RAG", ["AI technique", "piece of cloth"])
Observation: Resolved to "Retrieval-Augmented Generation"

Thought: "Now I need specific technical information..."
Action:  web_search("Retrieval-Augmented Generation explained")
Observation: Found 8 results from AWS, IBM, NVIDIA...

Thought: "Good overview sources. Need more depth on architecture..."
Action:  web_search("RAG pipeline architecture components")
Observation: Found 10 more results including arxiv papers...

Thought: "15 high-quality sources collected. Ready to synthesize."
Action:  synthesize()
Action:  finish()
```

## Technology Stack

| Layer | Technology |
|-------|-----------|
| Backend | Python 3.10+, FastAPI, Uvicorn |
| LLM | Ollama (local) |
| LLM | Groq, Llama 3.3 70B (OpenAI-compatible API) |
| Search | Brave Search API, DuckDuckGo fallback |
| Database | SQLite, SQLAlchemy (async), aiosqlite |
| Auth | JWT (python-jose), bcrypt (passlib), itsdangerous |
| Embeddings | sentence-transformers (optional) |
| Rate limiting | SlowAPI |
| Streaming | Server-Sent Events (StreamingResponse) |
| Frontend | React 18, Vite, Tailwind CSS |
| Animations | Framer Motion, GSAP |
| HTTP | httpx (backend), axios (frontend) |
| Validation | Pydantic v2 |
| Testing | pytest, pytest-asyncio |

## Architecture

```text
VeriScope/
├── app/
│   ├── api/
│   │   ├── routes.py
│   │   ├── stream_routes.py
│   │   └── rate_limiter.py
│   ├── agents/
│   │   ├── research_agent.py
│   │   ├── react_agent.py
│   │   └── tools.py
│   ├── auth/
│   │   ├── routes.py
│   │   ├── dependencies.py
│   │   ├── security.py
│   │   └── schemas.py
│   ├── config/
│   │   └── settings.py
│   ├── database/
│   │   ├── connection.py
│   │   └── models.py
│   ├── models/
│   │   └── research_models.py
│   ├── prompts/
│   │   ├── synthesis.py
│   │   ├── query_analysis.py
│   │   ├── disambiguation.py
│   │   └── react_prompt.py
│   ├── providers/
│   │   ├── search_provider.py
│   │   ├── llm_provider.py
│   │   ├── brave_search_provider.py
│   │   ├── web_search_provider.py
│   │   ├── ollama_provider.py
│   │   ├── groq_provider.py
│   │   ├── mock_search_provider.py
│   │   └── mock_llm_provider.py
│   ├── services/
│   │   └── research_services.py
│   ├── sessions/
│   │   ├── routes.py
│   │   └── schemas.py
│   └── utils/
│       ├── json_parser.py
│       ├── react_parser.py
│       ├── source_scoring.py
│       └── embeddings.py
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   ├── context/
│   │   ├── pages/
│   │   ├── services/api.js
│   │   └── App.jsx
│   ├── package.json
│   └── vite.config.js
├── tests/
├── main.py
├── requirements.txt
├── veriscope.db
└── .env
```

## Installation

### 1. Backend

```bash
git clone https://github.com/akshitjindal77/VeriScope.git
cd VeriScope

python -m venv venv
source venv/bin/activate        # Linux/macOS
venv\Scripts\activate         # Windows

pip install -r requirements.txt
```

### 2. Ollama (optional for local inference)

```bash
ollama serve
ollama pull mistral
```

### 3. Frontend

```bash
cd frontend
npm install
```

### 4. Environment

Create `.env` in the project root:

```env
app_name=VeriScope
env=development

# Search
WEB_SEARCH_PROVIDER=brave
BRAVE_API_KEY=your_brave_api_key
WEB_SEARCH_MAX_RESULTS=8
WEB_SEARCH_TIMEOUT_S=10.0
WEB_SEARCH_CACHE_TTL_S=300
WEB_SEARCH_BLOCK_DOMAINS=[]
WEB_SEARCH_ALLOW_DOMAINS=null

# LLM provider: choose one
LLM_PROVIDER=ollama
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=mistral
# LLM_PROVIDER=groq
# GROQ_API_KEY=your_groq_api_key
# GROQ_MODEL=llama-3.3-70b-versatile
LLM_TEMPERATURE=0.3
LLM_MAX_TOKENS=2048
LLM_TIMEOUT_S=120.0

# Auth
JWT_SECRET_KEY=change-this-to-a-random-secret-in-production
JWT_EXPIRE_MINUTES=1440

# Database
DATABASE_URL=sqlite+aiosqlite:///./veriscope.db

# Deployment / CORS
ALLOWED_ORIGINS=http://localhost:5173,http://localhost:3000

# ReAct
REACT_MAX_STEPS=7
REACT_STEP_TIMEOUT_S=60.0
```

For cloud deployment you do not need Ollama. A Groq API key is enough when `LLM_PROVIDER=groq`.

## Running

### Local Development

Terminal 1:

```bash
ollama serve
```

Terminal 2:

```bash
uvicorn app.main:app --reload
```

Terminal 3:

```bash
cd frontend
npm run dev
```

Frontend defaults to `http://localhost:5173`. Backend defaults to `http://localhost:8000`.

### Deployment

The app is ready to deploy with a split frontend and backend setup. Host the Python backend on Render or another service that supports FastAPI, and host the React frontend on Vercel or a static frontend host.

For a deployed frontend, set `VITE_API_URL` to the backend base URL and add that frontend URL to `ALLOWED_ORIGINS`. The backend CORS policy is controlled by `ALLOWED_ORIGINS`.

Render free tier memory is usually not enough for the full stack. Use a paid Render plan or an alternative host for production.

## Tests

```bash
pytest tests/ -v
```

The test suite covers API behavior, authentication, cache handling, parsing, scoring, and research pipeline flow with mock providers.

## API Endpoints

All routes are mounted under `/api`.

### Authentication

| Method | Path | Rate Limit | Description |
|--------|------|-----------|-------------|
| POST | `/api/auth/signup` | 5/hr | Create account and return JWT + verification token |
| POST | `/api/auth/login` | 20/hr | Authenticate and return JWT |
| GET | `/api/auth/me` | — | Return current user info |
| GET | `/api/auth/verify` | — | Verify email token |

### Research (JWT required)

| Method | Path | Rate Limit | Description |
|--------|------|-----------|-------------|
| POST | `/api/research` | 10/hr | Run full research pipeline and return answer |
| POST | `/api/research/stream` | 10/hr | Stream pipeline progress over SSE |

### Sessions (JWT required)

| Method | Path | Description |
|--------|-------------|-------------|
| GET | `/api/sessions` | List sessions |
| POST | `/api/sessions` | Create a new session |
| GET | `/api/sessions/{id}` | Load a session and its queries |
| DELETE | `/api/sessions/{id}` | Delete a session |

### System

| Method | Path | Description |
|--------|------|-------------|
| GET | `/api/health` | Health status, LLM availability, and rate limits |
| DELETE | `/api/cache` | Clear expired cache entries |

## Configuration

| Variable | Default | Description |
|----------|---------|-------------|
| `app_name` | — | Application name |
| `env` | `development` | Environment mode |
| `WEB_SEARCH_PROVIDER` | `brave` | Search provider |
| `BRAVE_API_KEY` | — | Brave API key |
| `WEB_SEARCH_MAX_RESULTS` | `8` | Results per query |
| `WEB_SEARCH_TIMEOUT_S` | `10.0` | Search timeout |
| `WEB_SEARCH_CACHE_TTL_S` | `300` | In-memory cache TTL |
| `WEB_SEARCH_BLOCK_DOMAINS` | `[]` | Blocked domains |
| `WEB_SEARCH_ALLOW_DOMAINS` | `null` | Allowed domains |
| `LLM_PROVIDER` | `ollama` | LLM provider |
| `OLLAMA_BASE_URL` | `http://localhost:11434` | Ollama server URL |
| `OLLAMA_MODEL` | `mistral` | Ollama model |
| `GROQ_API_KEY` | — | Groq API key (required if `LLM_PROVIDER=groq`) |
| `GROQ_MODEL` | `llama-3.3-70b-versatile` | Groq model |
| `LLM_TEMPERATURE` | `0.3` | Model randomness |
| `LLM_MAX_TOKENS` | `2048` | Max token limit |
| `LLM_TIMEOUT_S` | `120.0` | LLM request timeout |
| `JWT_SECRET_KEY` | — | JWT signing secret |
| `JWT_EXPIRE_MINUTES` | `1440` | Token expiry in minutes |
| `DATABASE_URL` | `sqlite+aiosqlite:///./veriscope.db` | Database connection URL |
| `REACT_MAX_STEPS` | `7` | Max ReAct steps |
| `REACT_STEP_TIMEOUT_S` | `60.0` | Max seconds per ReAct step |
| `ALLOWED_ORIGINS` | `http://localhost:5173,http://localhost:3000` | Allowed CORS origins |

## Deployment

The codebase is deployment-ready. It supports a split frontend/backend workflow with environment-controlled API routing and CORS.

- Backend: deploy the FastAPI app from `app.main` on Render or another Python host.
- Frontend: build the React app and deploy it on Vercel, or any static host.
- Set `VITE_API_URL` in the frontend deployment to the backend URL.
- Set `ALLOWED_ORIGINS` in the backend deployment to include the frontend URL.
- If you use Groq, local Ollama is not required.

Render free tier usually does not provide enough memory for the full stack. For production use, choose a paid Render plan or a host with more memory.

## Design principles

- Modularity: providers, agents, and schemas are separated so components can change independently.
- Provider agnostic: search and LLM providers are selected with environment variables.
- Evidence first: the system only returns sources that are actually referenced in the answer.
- Graceful degradation: missing providers or unavailable models fall back to safe behavior.
- Validation at every boundary: Pydantic schemas validate input and output across the pipeline.
- Honest documentation: the README reflects current project state, missing pieces, and known tradeoffs.

## Known limitations

| Area | Details |
|------|---------|
| Speed | Local Ollama on an RTX 3050 is 2–5 min per query. Groq cloud inference is noticeably faster. |
| Semantic cache | sentence-transformers and semantic caching are optional. If unavailable, the system falls back to exact-match cache. |
| ReAct parsing | The deep agent may attempt future actions. The parser strips invalid steps. |
| Confidence | Confidence is calibrated from source quality, count, diversity, and ambiguity, but it does not guarantee factual correctness. |
| Deduplication | Duplicate sources are detected by exact string matching only; semantic grouping is not implemented yet. |
| Hosting | Render free tier memory may not be sufficient for a production-grade backend. |

## Roadmap

### Completed

- Pluggable search providers (Brave, DuckDuckGo, Mock)
- Pluggable LLM providers (Ollama, Groq, Mock)
- LLM-powered query analysis
- Ambiguity detection and resolution
- Dynamic query expansion
- Domain authority and relevance scoring
- Low-quality source filtering
- LLM narrative synthesis
- Citation mapping and filtering
- Calibrated confidence scoring
- ReAct agent loop
- Real-time SSE streaming
- JWT authentication and bcrypt
- Email verification
- Session persistence with SQLite
- Exact-match and optional semantic caching
- Rate limiting with SlowAPI
- Test suite with pytest
- React frontend and dashboard
- Streaming status UI and ReAct thought viewer
- Post-processing cleanup

### Planned

- Embedding-based source deduplication
- PostgreSQL for production deployments
- Docker containerization
- Cloud deployment (Render / Railway) — codebase is ready and tested with Render and Vercel
- Word-by-word response streaming

## Research foundation

| Paper / concept | Relevance |
|----------------|-----------|
| ReAct (Yao et al., 2023) | Basis for the deep reasoning mode |
| RAG (Lewis et al., 2020) | Foundation for retrieval-augmented generation |
| Tool-augmented LLMs | Agent actions use search, disambiguation, and synthesis tools |
| Structured output validation | Pydantic schemas validate data across the pipeline |

## Author

Built by Akshit Jindal
