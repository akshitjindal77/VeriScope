<p align="center">
  <h1 align="center">🔍 VeriScope</h1>
  <p align="center">
    <strong>AI-Powered Research Engine with Deep Reasoning</strong>
  </p>
  <p align="center">
    Intelligent query analysis · Source quality scoring · LLM synthesis with citations · ReAct agent reasoning
  </p>
  <p align="center">
    <a href="#live-features">Features</a> ·
    <a href="#how-the-pipeline-works">How It Works</a> ·
    <a href="#installation">Installation</a> ·
    <a href="#api-endpoints">API Docs</a> ·
    <a href="#roadmap">Roadmap</a>
  </p>
</p>

---

## What is VeriScope?

VeriScope is a full-stack research application that transforms a simple question into a comprehensive, cited answer. It analyzes your query with a local LLM, resolves ambiguity, searches the web through pluggable providers, scores every source by domain authority and relevance, synthesizes a coherent narrative with inline citations, and streams the entire process to you in real-time.

**Two research modes:**

| Mode | Speed | How it works |
|------|-------|-------------|
| ⚡ **Fast** | ~3–5 min | Linear pipeline — single-pass analysis, search, and synthesis |
| 🧠 **Deep** | ~8–15 min | ReAct agent — reasons step-by-step, searches multiple angles, self-corrects |

All results are persisted with user accounts, session history, semantic caching, and email verification.

---

## Live Features

### 🧠 Intelligence Layer
| Feature | Description |
|---------|-------------|
| **Query Analysis** | LLM classifies intent, detects domain, and generates targeted search queries |
| **Ambiguity Resolution** | Detects multi-meaning terms (RAG, Python, Rust, Java) and resolves to the correct meaning |
| **Source Quality Scoring** | Tiered domain authority (government → tech → blogs) combined with keyword relevance scoring |
| **Confidence Calibration** | Multi-factor score based on source quality, count, diversity, and ambiguity |
| **Post-Processing** | Code-level cleanup removes LLM artifacts (trailing source lists, summary paragraphs) |

### 🔍 Research Pipeline
| Feature | Description |
|---------|-------------|
| **LLM Synthesis** | Mistral 7B writes coherent 5–6 paragraph answers with inline [1][2] citations |
| **ReAct Agent Loop** | Iterative Thought → Action → Observation cycles with tool access |
| **Citation Filtering** | Only sources actually referenced in the answer appear in the response |
| **Graceful Fallback** | Pipeline falls back to rule-based logic when the LLM is unavailable |

### 🛡️ Backend Infrastructure
| Feature | Description |
|---------|-------------|
| **User Authentication** | Signup, login, JWT tokens with bcrypt password hashing |
| **Email Verification** | Secure token-based verification via itsdangerous |
| **Session History** | Research conversations persisted in SQLite, grouped by date |
| **Result Caching** | Exact-match + semantic embedding cache (sentence-transformers) |
| **Rate Limiting** | SlowAPI-powered per-IP rate limits (10/hr research, 5/hr signup, 20/hr login) |
| **Real-Time Streaming** | Server-Sent Events stream pipeline progress as it happens |

### 🎨 Frontend
| Feature | Description |
|---------|-------------|
| **Landing Page** | "See Through the Noise" — animated hero with interactive claim checker and Truth Lens visualization |
| **Radiant Search Bar** | Rotating conic gradient border — blue (Fast), purple (Deep), accelerated glow during research |
| **CardSwap Showcase** | GSAP-animated feature cards with elastic depth transitions |
| **Streaming Status** | Live progress indicators with stage-by-stage checkmarks |
| **ReAct Thought Viewer** | Displays agent reasoning steps in real-time during deep mode |
| **Citation Cards** | Expandable source cards with confidence badges (green / yellow / red) |
| **Session Sidebar** | Past conversations grouped by date — reload, delete, or start new |
| **Stop Button** | Cancel in-progress research via AbortController |

### 🔌 Pluggable Architecture
| Feature | Description |
|---------|-------------|
| **Search Providers** | Brave Search API (primary) + DuckDuckGo HTML fallback + Mock for testing |
| **LLM Providers** | Ollama / Mistral (primary) + Mock for testing — swap via environment variable |

---

## Architecture

```text
VeriScope/
├── app/                              # Python backend (FastAPI)
│   ├── api/
│   │   ├── routes.py                 # REST endpoints + rate limiting
│   │   ├── stream_routes.py          # SSE streaming endpoint
│   │   └── rate_limiter.py           # SlowAPI configuration
│   ├── agents/
│   │   ├── research_agent.py         # Linear research pipeline
│   │   ├── react_agent.py            # ReAct deep reasoning agent
│   │   └── tools.py                  # ReAct tool definitions
│   ├── auth/
│   │   ├── routes.py                 # Signup, login, verify, me
│   │   ├── dependencies.py           # JWT authentication dependency
│   │   ├── security.py               # Hashing, JWT, verification tokens
│   │   └── schemas.py                # Auth request/response models
│   ├── config/
│   │   └── settings.py               # Environment-based configuration
│   ├── database/
│   │   ├── connection.py             # SQLAlchemy async engine + session
│   │   └── models.py                 # User, Session, Query, Cache tables
│   ├── models/
│   │   └── research_models.py        # Pydantic schemas
│   ├── prompts/
│   │   ├── synthesis.py              # Narrative synthesis templates
│   │   ├── query_analysis.py         # Query understanding templates
│   │   ├── disambiguation.py         # Ambiguity resolution templates
│   │   └── react_prompt.py           # ReAct reasoning templates
│   ├── providers/
│   │   ├── search_provider.py        # Abstract SearchProvider
│   │   ├── llm_provider.py           # Abstract LLMProvider
│   │   ├── brave_search_provider.py  # Brave Search API
│   │   ├── web_search_provider.py    # DuckDuckGo fallback
│   │   ├── ollama_provider.py        # Ollama local LLM
│   │   ├── mock_search_provider.py   # Mock search (testing)
│   │   └── mock_llm_provider.py      # Mock LLM (testing)
│   ├── services/
│   │   └── research_services.py      # Orchestration + caching
│   ├── sessions/
│   │   ├── routes.py                 # Session CRUD
│   │   └── schemas.py                # Session models
│   └── utils/
│       ├── json_parser.py            # Safe JSON extraction
│       ├── react_parser.py           # ReAct action parser
│       ├── source_scoring.py         # Domain authority + relevance
│       └── embeddings.py             # Sentence-transformer embeddings
├── frontend/                          # React application
│   ├── src/
│   │   ├── components/
│   │   │   ├── RadiantPromptInput.jsx # Gradient search bar
│   │   │   ├── CardSwap.jsx           # Animated card showcase
│   │   │   ├── StreamingStatus.jsx    # Pipeline progress
│   │   │   ├── AnswerCard.jsx         # Result + citations
│   │   │   ├── CitationCard.jsx       # Expandable source card
│   │   │   └── ConfidenceMeter.jsx    # Confidence bar
│   │   ├── pages/
│   │   │   ├── LandingPage.jsx        # Landing page
│   │   │   ├── LoginPage.jsx          # Login
│   │   │   ├── SignupPage.jsx         # Signup
│   │   │   └── DashboardPage.jsx      # Research dashboard
│   │   ├── services/api.js            # API client + interceptors
│   │   ├── context/AuthContext.jsx     # Auth state
│   │   └── App.jsx                    # Root + routing
│   ├── package.json
│   └── vite.config.js
├── tests/                             # Test suite (pytest)
│   ├── test_api.py                    # API endpoint tests
│   ├── test_auth.py                   # Authentication tests
│   ├── test_cache.py                  # Cache normalization tests
│   ├── test_json_parser.py            # JSON parser tests
│   ├── test_research_agent.py         # Pipeline tests
│   ├── test_source_scoring.py         # Scoring tests
│   └── conftest.py                    # Shared fixtures
├── main.py
├── requirements.txt
├── veriscope.db                       # Auto-created, gitignored
└── .env                               # Not committed
```

---

## How the Pipeline Works

### ⚡ Linear Mode

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
│  Authority +     │     │  Mistral writes  │     │  Clean artifacts│
│  relevance rank  │     │  cited narrative  │     │  Filter cites   │
└─────────────────┘     └──────────────────┘     └────────┬────────┘
                                                          │
                                                          ▼
                                                   JSON Response
                                                   + Confidence
```

### 🧠 ReAct Mode

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

---

## Technology Stack

| Layer | Technology |
|-------|-----------|
| **Backend** | Python 3.10+, FastAPI, Uvicorn |
| **LLM** | Ollama, Mistral 7B (OpenAI-compatible API) |
| **Search** | Brave Search API, DuckDuckGo (fallback) |
| **Database** | SQLite, SQLAlchemy (async), aiosqlite |
| **Auth** | JWT (python-jose), bcrypt (passlib), itsdangerous |
| **Embeddings** | sentence-transformers (all-MiniLM-L6-v2) |
| **Rate Limiting** | SlowAPI |
| **Streaming** | Server-Sent Events (StreamingResponse) |
| **Frontend** | React 18, Vite, Tailwind CSS |
| **Animations** | Framer Motion, GSAP |
| **HTTP** | httpx (backend), axios (frontend) |
| **Validation** | Pydantic v2 |
| **Testing** | pytest, pytest-asyncio |

---

## Installation

### 1. Backend

```bash
git clone https://github.com/akshitjindal77/VeriScope.git
cd VeriScope

python -m venv venv
source venv/bin/activate        # Linux/macOS
venv\Scripts\activate           # Windows

pip install -r requirements.txt
```

### 2. Ollama

```bash
# Download from https://ollama.com
ollama serve
ollama pull mistral
```

### 3. Frontend

```bash
cd frontend
npm install
```

### 4. Environment

Create `.env` in project root:

```env
app_name=VeriScope
env=development

# Search
WEB_SEARCH_PROVIDER=brave
BRAVE_API_KEY=your_brave_api_key
WEB_SEARCH_MAX_RESULTS=8

# LLM
LLM_PROVIDER=ollama
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=mistral
LLM_TEMPERATURE=0.3
LLM_MAX_TOKENS=2048
LLM_TIMEOUT_S=120

# Auth
JWT_SECRET_KEY=change-this-to-a-random-secret-in-production

# Database
DATABASE_URL=sqlite+aiosqlite:///./veriscope.db

# ReAct
REACT_MAX_STEPS=7
```

---

## Running

```bash
ollama serve                          # Terminal 1
uvicorn app.main:app --reload         # Terminal 2
cd frontend && npm run dev            # Terminal 3
```

| Service | URL |
|---------|-----|
| Frontend | http://localhost:5173 |
| Backend | http://localhost:8000 |
| API Docs | http://localhost:8000/docs |

---

## Tests

```bash
pytest tests/ -v
```

59+ tests covering scoring, parsing, caching, pipeline, auth, and API endpoints — all using mock providers.

---

## API Endpoints

### Authentication

| Method | Path | Rate Limit | Description |
|--------|------|-----------|-------------|
| `POST` | `/auth/signup` | 5/hr | Create account → JWT + verification URL |
| `POST` | `/auth/login` | 20/hr | Authenticate → JWT |
| `GET` | `/auth/me` | — | Current user info |
| `GET` | `/auth/verify` | — | Verify email via token |

### Research (JWT required)

| Method | Path | Rate Limit | Description |
|--------|------|-----------|-------------|
| `POST` | `/research` | 10/hr | Full response |
| `POST` | `/research/stream` | 10/hr | SSE event stream |

### Sessions (JWT required)

| Method | Path | Description |
|--------|------|-------------|
| `GET` | `/sessions` | List sessions |
| `POST` | `/sessions` | Create session |
| `GET` | `/sessions/{id}` | Load session + queries |
| `DELETE` | `/sessions/{id}` | Delete session |

### System

| Method | Path | Description |
|--------|------|-------------|
| `GET` | `/health` | Health + LLM status + rate limits |
| `DELETE` | `/cache` | Clear expired cache |

<details>
<summary><strong>Example: POST /research</strong></summary>

**Request:**
```json
{
  "prompt": "What is RAG?",
  "mode": "linear",
  "session_id": null
}
```

**Response:**
```json
{
  "status": "success",
  "prompt": "What is RAG?",
  "answer": "Retrieval-Augmented Generation (RAG) is a technique that optimizes LLM output by referencing external knowledge bases [1][2]...",
  "citations": [
    {
      "source_id": "28839f5dd7",
      "url": "https://aws.amazon.com/what-is/retrieval-augmented-generation/",
      "title": "What is RAG? — AWS",
      "confidence": 0.84
    }
  ],
  "confidence": 0.77,
  "query_type": "factual",
  "resolved_meaning": "Retrieval-Augmented Generation (AI)",
  "react_steps": null,
  "session_id": "e4dd1f77-3b9c-4961-82cf-7e71777fea14"
}
```
</details>

<details>
<summary><strong>Example: POST /research/stream</strong></summary>

```
data: {"event": "status", "stage": "analyzing", "message": "Analyzing your query..."}
data: {"event": "status", "stage": "disambiguating", "message": "Resolving ambiguous term..."}
data: {"event": "status", "stage": "searching", "message": "Searching 4 queries..."}
data: {"event": "status", "stage": "scoring", "message": "Scoring 32 sources..."}
data: {"event": "status", "stage": "synthesizing", "message": "Writing answer..."}
data: {"event": "result", "data": { ...full response... }}
```
</details>

---

## Configuration

<details>
<summary><strong>All environment variables</strong></summary>

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
| `OLLAMA_BASE_URL` | `http://localhost:11434` | Ollama server |
| `OLLAMA_MODEL` | `mistral` | Model name |
| `LLM_TEMPERATURE` | `0.3` | Randomness |
| `LLM_MAX_TOKENS` | `2048` | Max tokens |
| `LLM_TIMEOUT_S` | `120.0` | LLM timeout |
| `JWT_SECRET_KEY` | — | JWT secret |
| `JWT_EXPIRE_MINUTES` | `1440` | Token expiry |
| `DATABASE_URL` | `sqlite+aiosqlite:///./veriscope.db` | Database |
| `REACT_MAX_STEPS` | `7` | Max ReAct steps |
| `SOURCE_MIN_QUALITY` | `0.3` | Min source quality |

</details>

---

## Design Principles

- **Modularity** — every component has a clear interface; providers, agents, and models evolve independently
- **Provider Agnostic** — swap search engines or LLMs via environment variables
- **Evidence-First** — LLM uses only provided sources; post-processing enforces citation integrity
- **Graceful Degradation** — LLM down? Rule-based fallback. Cache miss? Full pipeline runs.
- **Defense in Depth** — prompt engineering + code-level cleanup + Pydantic validation at every boundary
- **Honest Documentation** — limitations documented alongside capabilities

---

## Known Limitations

| Area | Details |
|------|---------|
| Speed | 2–5 min/query on RTX 3050. Faster with phi3 or cloud LLMs (Groq). |
| ReAct Parsing | Mistral 7B occasionally hallucinates future steps. Parser strips them. |
| Confidence | Improved multi-factor formula; still doesn't assess factual accuracy. |
| Deduplication | String-exact only. Semantic source grouping planned. |
| Concurrency | SQLite is single-user. PostgreSQL needed for production. |
| Semantic Cache | 0.85 cosine threshold. Borderline queries may miss or false-positive. |

---

## Roadmap

### ✅ Completed

- [x] Pluggable search providers (Brave + DuckDuckGo + Mock)
- [x] Pluggable LLM providers (Ollama + Mock)
- [x] LLM-powered query analysis
- [x] Ambiguity detection and resolution
- [x] Dynamic query expansion
- [x] Domain authority + relevance scoring
- [x] Low-quality source filtering
- [x] LLM narrative synthesis
- [x] Citation mapping and filtering
- [x] Calibrated confidence scoring
- [x] ReAct agent loop
- [x] Real-time SSE streaming
- [x] JWT authentication + bcrypt
- [x] Email verification
- [x] Session persistence (SQLite)
- [x] Exact + semantic caching
- [x] Rate limiting (SlowAPI)
- [x] Test suite (pytest)
- [x] React frontend + landing page
- [x] Dashboard + streaming UI
- [x] Radiant gradient search bar
- [x] Post-processing cleanup

### 🔜 Planned

- [ ] Embedding-based source deduplication
- [ ] PostgreSQL for production
- [ ] Docker containerization
- [ ] Cloud deployment (Render / Railway)
- [ ] Groq API integration (cloud LLM)
- [ ] Word-by-word response streaming

---

## Research Foundation

| Paper / Concept | Relevance |
|----------------|-----------|
| **ReAct** (Yao et al., 2023) | Foundation for VeriScope's deep reasoning mode |
| **RAG** (Lewis et al., 2020) | Core retrieval-augmented generation pipeline |
| **Tool-Augmented LLMs** | Agent tool access: search, disambiguate, synthesize |
| **Structured Output Validation** | Pydantic schemas at every pipeline boundary |

---

<p align="center">
  <strong>Built by <a href="https://github.com/akshitjindal77">Akshit Jindal</a></strong><br>
  Bachelor of Computer Information Systems · University of the Fraser Valley
</p>