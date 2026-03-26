# VeriScope

AI-powered research engine with LLM-driven synthesis, intelligent query disambiguation, source quality scoring, ReAct deep reasoning, real-time streaming, user authentication, and a modern React frontend.

## Overview

VeriScope is a full-stack research application that takes a user query, analyzes it with a local LLM, resolves ambiguity, searches the web using pluggable providers, scores sources by quality, synthesizes a coherent narrative answer with inline citations, and streams the entire process to the user in real-time.

The system features two research modes: a fast linear pipeline (~3-5 minutes) and an optional ReAct deep reasoning mode (~8-15 minutes) where the LLM agent reasons step-by-step, searches multiple angles, and self-corrects. All results are persisted in a database with user accounts, session history, and intelligent caching.

## Live Features

- **LLM-powered narrative synthesis** via Ollama (Mistral 7B) with graceful fallback to rule-based logic
- **LLM-powered query analysis** with intent classification, domain detection, and dynamic search query generation
- **Ambiguity resolution** — detects multi-meaning terms (RAG, Python, Rust, Java, etc.) and resolves to the most likely meaning
- **Source quality scoring** — tiered domain authority ranking + relevance scoring, with low-quality source filtering
- **Calibrated confidence** — multi-factor scoring based on source quality, count, domain diversity, and ambiguity
- **ReAct agent loop** — optional deep reasoning mode with iterative Thought → Action → Observation cycles
- **Real-time streaming** — Server-Sent Events (SSE) endpoint streams pipeline progress as it happens
- **User authentication** — signup, login, JWT tokens, protected API routes
- **Session history** — research conversations persisted in SQLite, loadable from the sidebar
- **Result caching** — repeated queries return instantly from cache with case and punctuation normalization
- **Citation filtering** — only sources referenced in the answer appear in the response
- **HTML cleanup** — strips tags and decodes entities from search snippets
- **Post-processing** — removes LLM artifacts like trailing source lists and summary paragraphs
- **Modern React frontend** — animated landing page, auth flow, dashboard with streaming status, citation cards
- **Radiant gradient search bar** — rotating conic gradient border with mode-aware color states
- **CardSwap feature showcase** — animated card cycling with GSAP-powered depth animations
- **Pluggable provider architecture** — abstract interfaces for both search and LLM backends
- **Brave Search API** integration with TTL caching and HTML snippet cleaning
- **DuckDuckGo fallback** provider with URL canonicalization and domain filtering

## Architecture

```text
VeriScope/
├── app/                              # Python backend
│   ├── api/
│   │   ├── routes.py                 # REST API endpoints
│   │   └── stream_routes.py          # SSE streaming endpoint
│   ├── agents/
│   │   ├── research_agent.py         # Linear research pipeline
│   │   ├── react_agent.py            # ReAct deep reasoning agent
│   │   └── tools.py                  # ReAct tool definitions
│   ├── auth/
│   │   ├── routes.py                 # Signup, login, me endpoints
│   │   ├── dependencies.py           # JWT authentication dependency
│   │   ├── security.py               # Password hashing, token management
│   │   └── schemas.py                # Auth request/response models
│   ├── config/
│   │   └── settings.py               # Environment-based configuration
│   ├── database/
│   │   ├── connection.py             # SQLAlchemy async engine setup
│   │   └── models.py                 # User, Session, Query, Cache tables
│   ├── models/
│   │   └── research_models.py        # Pydantic schemas (Source, Citation, LLMResponse, etc.)
│   ├── prompts/
│   │   ├── synthesis.py              # Prompt templates for narrative synthesis
│   │   ├── query_analysis.py         # Prompt templates for query understanding
│   │   ├── disambiguation.py         # Prompt templates for ambiguity resolution
│   │   └── react_prompt.py           # Prompt templates for ReAct reasoning
│   ├── providers/
│   │   ├── search_provider.py        # Abstract SearchProvider interface
│   │   ├── llm_provider.py           # Abstract LLMProvider interface
│   │   ├── brave_search_provider.py  # Brave Search API provider
│   │   ├── web_search_provider.py    # DuckDuckGo fallback provider
│   │   ├── ollama_provider.py        # Ollama local LLM provider
│   │   ├── mock_search_provider.py   # Mock search provider for testing
│   │   └── mock_llm_provider.py      # Mock LLM provider for testing
│   ├── services/
│   │   └── research_services.py      # Provider wiring, caching, orchestration
│   ├── sessions/
│   │   ├── routes.py                 # Session CRUD endpoints
│   │   └── schemas.py                # Session request/response models
│   └── utils/
│       ├── json_parser.py            # Safe JSON extraction from LLM responses
│       ├── react_parser.py           # ReAct action/thought parser
│       └── source_scoring.py         # Domain authority and relevance scoring
├── frontend/                          # React application
│   ├── src/
│   │   ├── components/
│   │   │   ├── RadiantPromptInput.jsx # Gradient search bar with mode toggle
│   │   │   ├── CardSwap.jsx           # Animated card showcase component
│   │   │   ├── StreamingStatus.jsx    # Real-time pipeline progress display
│   │   │   ├── AnswerCard.jsx         # Research result with citations
│   │   │   ├── CitationCard.jsx       # Expandable source card
│   │   │   └── ConfidenceMeter.jsx    # Animated confidence bar
│   │   ├── pages/
│   │   │   ├── LandingPage.jsx        # Animated landing with Truth Lens demo
│   │   │   ├── LoginPage.jsx          # Authentication - login
│   │   │   ├── SignupPage.jsx         # Authentication - signup
│   │   │   └── DashboardPage.jsx      # Main research interface
│   │   ├── services/
│   │   │   └── api.js                 # API client with JWT interceptors
│   │   ├── context/
│   │   │   └── AuthContext.jsx        # Global authentication state
│   │   └── App.jsx                    # Root component with routing
│   ├── package.json
│   └── vite.config.js
├── main.py                            # FastAPI application entry point
├── requirements.txt                   # Python dependencies
├── veriscope.db                       # SQLite database (auto-created, gitignored)
└── .env                               # Environment variables (not committed)
```

## How the Pipeline Works

### Linear Mode (Fast, ~3-5 minutes)

1. **Query Analysis** — LLM analyzes the query for intent, domain, and ambiguity. Generates tailored search queries instead of generic templates.
2. **Disambiguation** — If the query is ambiguous (e.g., "What is Rust?"), a second LLM call resolves it to the most likely meaning based on context.
3. **Web Search** — Executes LLM-generated search queries through the active provider (Brave or DuckDuckGo). Deduplicates by URL.
4. **Source Scoring** — Each source is scored by domain authority (tiered ranking) and relevance (keyword overlap). Sources are sorted by quality.
5. **Source Filtering** — Sources below the quality threshold are removed. Top 10 by quality are sent to synthesis.
6. **LLM Synthesis** — Mistral writes a coherent 5-6 paragraph answer citing sources with [1], [2] references. Post-processing removes artifacts.
7. **Citation Filtering** — Only sources the LLM actually referenced appear in the response.
8. **Confidence Calibration** — Multi-factor score based on average source quality, source count (diminishing returns), domain diversity, and ambiguity penalty.

### ReAct Mode (Deep, ~8-15 minutes)

The LLM operates in a reasoning loop with access to tools:

```
Thought: "The query asks about RAG, which is ambiguous..."
Action:  disambiguate("RAG", ["AI technique", "piece of cloth", "project management"])
Observation: Resolved to "Retrieval-Augmented Generation (AI)"

Thought: "Let me search for specific information..."
Action:  web_search("Retrieval-Augmented Generation explained")
Observation: Found 8 results from AWS, IBM, NVIDIA...

Thought: "Good sources but need more depth. Searching again..."
Action:  web_search("RAG architecture pipeline components")
Observation: Found 10 more results including arxiv papers...

Thought: "Ready to synthesize from 15 high-quality sources."
Action:  synthesize()
Observation: Generated comprehensive answer with citations.

Action:  finish()
```

The agent decides when to search again, disambiguate, analyze sources, or finalize — adapting its strategy per query.

## The Frontend

### Landing Page
- **"See Through the Noise"** headline with gradient text animation
- **Interactive claim checker** — auto-typing demo with scanning animation showing VeriScope's verification flow
- **Truth Lens visualization** — three-column display showing Raw Input → Analysis → Verified Output with scan-line animation
- **CardSwap feature showcase** — GSAP-animated cards cycling through VeriScope's capabilities
- **Trust indicators** — Research Papers, News Sources, AI Models, Data Analysis

### Dashboard
- **Radiant search bar** — rotating conic gradient border that changes color per mode (blue for Fast, purple for Deep) and spins faster during research
- **Real-time streaming** — SSE events display pipeline progress as it happens
- **ReAct thought viewer** — shows agent reasoning steps in deep mode
- **Answer cards** — formatted answers with inline citation badges, confidence meter, query type, disambiguation info
- **Citation cards** — expandable source cards with domain, title, confidence badge (green/yellow/red)
- **Session sidebar** — past conversations grouped by date, click to reload, delete, or create new
- **Stop button** — cancel in-progress research with AbortController

## Technology Stack

| Layer | Technology |
|-------|-----------|
| **Backend** | Python 3.10+, FastAPI, Uvicorn |
| **LLM** | Ollama (local), Mistral 7B via OpenAI-compatible API |
| **Search** | Brave Search API (primary), DuckDuckGo (fallback) |
| **Database** | SQLite via SQLAlchemy (async), aiosqlite |
| **Auth** | JWT (python-jose), bcrypt (passlib) |
| **Streaming** | Server-Sent Events (SSE) via StreamingResponse |
| **Frontend** | React 18, Vite, Tailwind CSS |
| **Animations** | Framer Motion, GSAP |
| **HTTP Client** | httpx (async), axios (frontend) |
| **Data Validation** | Pydantic v2, Pydantic Settings |
| **Caching** | SQLite (database cache) + cachetools (in-memory TTL) |

## Installation

### Backend

```bash
git clone https://github.com/akshitjindal77/VeriScope.git
cd VeriScope

python -m venv venv
source venv/bin/activate        # Linux/macOS
venv\Scripts\activate           # Windows

pip install -r requirements.txt
```

### Ollama (Local LLM)

```bash
# Download from https://ollama.com and install
ollama serve                     # Start the Ollama server (keep running)
ollama pull mistral              # Download Mistral 7B (~4GB)
```

### Frontend

```bash
cd frontend
npm install
```

### Configuration

Create a `.env` file in the project root:

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

## Running the Application

```bash
# Terminal 1: Start Ollama
ollama serve

# Terminal 2: Start the backend
uvicorn app.main:app --reload

# Terminal 3: Start the frontend
cd frontend && npm run dev
```

- Backend API: `http://localhost:8000`
- Frontend: `http://localhost:5173`
- API docs: `http://localhost:8000/docs`

## API Endpoints

### Auth

| Method | Path | Description |
|--------|------|-------------|
| POST | `/auth/signup` | Create account |
| POST | `/auth/login` | Get JWT token |
| GET | `/auth/me` | Current user info |

### Research (requires JWT)

| Method | Path | Description |
|--------|------|-------------|
| POST | `/research` | Submit query, get full response |
| POST | `/research/stream` | Submit query, receive SSE events |

### Sessions (requires JWT)

| Method | Path | Description |
|--------|------|-------------|
| GET | `/sessions` | List user's sessions |
| POST | `/sessions` | Create new session |
| GET | `/sessions/{id}` | Get session with queries |
| DELETE | `/sessions/{id}` | Delete session |

### System

| Method | Path | Description |
|--------|------|-------------|
| GET | `/` | Hello endpoint |
| GET | `/health` | Health check with LLM status |
| DELETE | `/cache` | Clear expired cache entries |

### POST /research

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
  "answer": "Retrieval-Augmented Generation (RAG) is a technique that optimizes the output of large language models by referencing authoritative knowledge bases outside of their training data [1][2]...",
  "citations": [
    {
      "source_id": "28839f5dd7",
      "url": "https://aws.amazon.com/what-is/retrieval-augmented-generation/",
      "title": "What is RAG? - AWS",
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

### POST /research/stream

Returns Server-Sent Events:

```
data: {"event": "status", "stage": "analyzing", "message": "Analyzing your query..."}
data: {"event": "status", "stage": "searching", "message": "Searching 4 queries..."}
data: {"event": "status", "stage": "scoring", "message": "Scoring 32 sources by quality..."}
data: {"event": "status", "stage": "synthesizing", "message": "Writing answer from sources..."}
data: {"event": "result", "data": {full research response}}
```

## Configuration Options

| Variable | Default | Description |
|----------|---------|-------------|
| `app_name` | — | Application name |
| `env` | `development` | Environment mode |
| `WEB_SEARCH_PROVIDER` | `brave` | Active search provider |
| `BRAVE_API_KEY` | — | Brave Search API key |
| `BRAVE_ENDPOINT` | `https://api.search.brave.com/res/v1/web/search` | Brave API endpoint |
| `WEB_SEARCH_MAX_RESULTS` | `8` | Max results per search query |
| `WEB_SEARCH_TIMEOUT_S` | `10.0` | Search request timeout (seconds) |
| `WEB_SEARCH_CACHE_TTL_S` | `300` | In-memory cache TTL (seconds) |
| `WEB_SEARCH_BLOCK_DOMAINS` | `[]` | Domains to exclude |
| `WEB_SEARCH_ALLOW_DOMAINS` | `null` | If set, only allow these domains |
| `LLM_PROVIDER` | `ollama` | Active LLM provider |
| `OLLAMA_BASE_URL` | `http://localhost:11434` | Ollama server address |
| `OLLAMA_MODEL` | `mistral` | Model name |
| `LLM_TEMPERATURE` | `0.3` | Generation randomness |
| `LLM_MAX_TOKENS` | `2048` | Max response tokens |
| `LLM_TIMEOUT_S` | `120.0` | LLM request timeout |
| `JWT_SECRET_KEY` | — | Secret for JWT signing |
| `JWT_EXPIRE_MINUTES` | `1440` | Token expiry (24 hours) |
| `DATABASE_URL` | `sqlite+aiosqlite:///./veriscope.db` | Database connection |
| `REACT_MAX_STEPS` | `7` | Max ReAct reasoning steps |
| `SOURCE_MIN_QUALITY` | `0.3` | Minimum source quality threshold |

## Design Principles

- **Modularity over monolith** — every component has a clear interface and responsibility
- **Structured data everywhere** — Pydantic models enforce validation at every stage
- **Provider agnostic** — both search and LLM backends are swappable without changing agent logic
- **Evidence over hallucination** — synthesis prompt instructs the LLM to only use provided sources
- **Graceful degradation** — if the LLM is unavailable, the pipeline falls back to rule-based logic
- **Honest documentation** — capabilities and limitations reflect the actual implementation
- **Code-level safety nets** — post-processing catches LLM formatting issues that prompt engineering alone can't fix

## Known Limitations

- **Local model speed** — synthesis on consumer GPUs (e.g., RTX 3050) takes 2-5 minutes per query; faster with smaller models like phi3
- **ReAct parsing reliability** — Mistral 7B sometimes hallucinates future conversation steps in its action output; the parser strips these but edge cases remain
- **Confidence is approximate** — the multi-factor formula is better than source-count-based but still doesn't assess actual factual accuracy
- **No embedding-based deduplication** — semantic similarity for source grouping is planned but not implemented
- **Single-user optimized** — SQLite handles development well but would need PostgreSQL for concurrent production use
- **No email verification** — signup doesn't verify email addresses
- **Cache is prompt-exact** — "What is RAG" and "explain RAG to me" are cached separately even though they ask the same thing

## Roadmap

### Completed

- [x] Pluggable search provider architecture (Brave + DuckDuckGo + Mock)
- [x] Pluggable LLM provider architecture (Ollama + Mock)
- [x] LLM-powered query analysis with intent classification
- [x] Ambiguity detection and resolution
- [x] Dynamic query expansion
- [x] Domain authority scoring (tiered ranking)
- [x] Relevance scoring per source
- [x] Low-quality source filtering
- [x] LLM-powered narrative synthesis
- [x] Inline citation mapping with filtering
- [x] Calibrated confidence scoring
- [x] ReAct agent loop with tool-based architecture
- [x] Real-time SSE streaming
- [x] User authentication (JWT)
- [x] Session and query persistence (SQLite)
- [x] Result caching with TTL
- [x] React frontend with animated landing page
- [x] Dashboard with streaming status and citation cards
- [x] Post-processing cleanup for LLM output artifacts

### Planned

- [ ] Embedding-based semantic deduplication and source clustering
- [ ] Semantic cache matching (similar queries hit cache, not just exact matches)
- [ ] Email verification on signup
- [ ] PostgreSQL support for production deployment
- [ ] Unit and integration test suite
- [ ] Deployment configuration (Docker, Railway, or Render)
- [ ] Rate limiting on API endpoints
- [ ] Response streaming for answer text (word-by-word appearance)

## Research Foundation

VeriScope is conceptually grounded in:

- ReAct: Synergizing Reasoning and Acting in Language Models (Yao et al., 2023)
- Retrieval-Augmented Generation (Lewis et al., 2020)
- Tool-augmented LLM architectures
- Structured output validation techniques

## Author

Akshit Jindal
Bachelor of Computer Information Systems
University of the Fraser Valley