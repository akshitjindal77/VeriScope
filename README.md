# VeriScope

AI-powered backend research engine with modular search providers, structured citation generation, and a clear path toward ReAct-based agentic reasoning.

## Overview

VeriScope is a modular backend research engine designed to take a user query, search the web using pluggable providers, collect and analyze sources, extract knowledge, and produce a synthesized research response with citations.

The system is architected with a clean separation between search providers, data models, agent logic, and API routing. The current implementation delivers a working end-to-end research pipeline, with an active roadmap toward intelligent query understanding, source quality scoring, and ReAct-based reasoning.

## Current Capabilities

- Pluggable search provider architecture with abstract interface
- Brave Search API integration with structured JSON parsing and TTL caching
- DuckDuckGo fallback provider with HTML parsing, URL canonicalization, and domain filtering
- Environment-based provider switching (no code changes required)
- Structured Pydantic models for sources, citations, research plans, and responses
- End-to-end research pipeline: Query → Plan → Search → Analyze → Write → Cite → Respond
- Source deduplication by URL across multiple search queries
- Input validation with length and empty-check guards
- RESTful API with health check and research endpoints

## Core Architecture

```text
VeriScope/
├── app/
│   ├── api/
│   │   └── routes.py            # FastAPI endpoint definitions
│   ├── agents/
│   │   └── research_agent.py    # Core research pipeline logic
│   ├── config/
│   │   └── settings.py          # Environment-based configuration
│   ├── models/
│   │   └── research_models.py   # Pydantic schemas (Source, Citation, etc.)
│   ├── providers/
│   │   ├── search_provider.py   # Abstract SearchProvider interface
│   │   ├── brave_search_provider.py   # Brave Search API provider
│   │   ├── web_search_provider.py     # DuckDuckGo fallback provider
│   │   └── mock_search_provider.py    # Mock provider for testing
│   └── services/
│       └── research_services.py # Provider wiring and agent orchestration
├── main.py                      # FastAPI application entry point
├── requirements.txt
└── .env                         # Environment variables (not committed)
```

The architecture separates concerns so that search providers, agent logic, data models, and API routing can evolve independently.

## How the Pipeline Works

1. **Query Planning**
   - Accept a user query via the API.
   - Generate sub-questions and search queries based on the prompt.

2. **Web Search**
   - Execute search queries through the active provider (Brave or DuckDuckGo).
   - Collect and deduplicate results by URL.

3. **Source Analysis**
   - Extract snippets from collected sources.
   - Remove duplicate content across results.

4. **Response Generation**
   - Assemble a structured answer from analyzed notes.
   - Generate a confidence score based on source count and coverage.

5. **Citation Attachment**
   - Map each source to a citation with URL, title, and supporting evidence.
   - Return a structured JSON response.

```json
{
  "status": "success",
  "prompt": "What is retrieval augmented generation?",
  "answer": "Based on the collected research...",
  "citations": [
    {
      "source_id": "a3f8c1b2e9",
      "url": "https://example.com/rag-explained",
      "title": "RAG Explained",
      "quotes": "...",
      "evidence": "...",
      "confidence": 0.5
    }
  ],
  "confidence": 0.75
}
```

## Search Provider System

VeriScope uses an abstract `SearchProvider` interface that decouples agent logic from any specific search engine.

- **BraveSearchProvider** — Primary provider. Uses the Brave Search API for structured JSON results. Supports API key authentication, configurable result count, and TTL-based caching.
- **WebSearchProvider (DuckDuckGo)** — Fallback provider. Parses DuckDuckGo HTML results with URL canonicalization, tracking parameter removal, and domain allow/block filtering.
- **MockSearchProvider** — Testing provider. Returns deterministic results for unit and integration tests.

The active provider is selected via the `WEB_SEARCH_PROVIDER` environment variable.

## Technology Stack

- **Backend:** Python 3.10+, FastAPI, Uvicorn
- **Data Validation:** Pydantic v2, Pydantic Settings
- **HTTP Client:** httpx (async)
- **HTML Parsing:** BeautifulSoup4 (DuckDuckGo provider)
- **Caching:** cachetools (TTLCache)
- **Configuration:** python-dotenv, environment variables
- **Testing:** Pytest

## Installation

1. **Clone repository**
   ```bash
   git clone https://github.com/akshitjindal77/VeriScope.git
   cd VeriScope
   ```

2. **Create virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate        # Linux/macOS
   venv\Scripts\activate           # Windows
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure environment variables** — create a `.env` file:
   ```env
   app_name=VeriScope
   env=development
   WEB_SEARCH_PROVIDER=brave
   BRAVE_API_KEY=your_brave_api_key
   WEB_SEARCH_MAX_RESULTS=8
   ```

## Running the Application

```bash
uvicorn app.main:app --reload
```

## API Documentation

Interactive docs available at: `http://127.0.0.1:8000/docs`

## API Endpoints

| Method | Path        | Description                                      |
|--------|-------------|--------------------------------------------------|
| GET    | `/`         | Hello endpoint                                   |
| GET    | `/health`   | Service health check with app name and env        |
| POST   | `/research` | Submit a query and receive a research response    |

### POST /research

**Request:**
```json
{
  "prompt": "What is retrieval augmented generation?"
}
```

**Response:**
```json
{
  "status": "success",
  "prompt": "What is retrieval augmented generation?",
  "answer": "...",
  "citations": [...],
  "confidence": 0.75
}
```

## Configuration Options

| Variable                  | Default                                          | Description                          |
|---------------------------|--------------------------------------------------|--------------------------------------|
| `app_name`                | —                                                | Application name                     |
| `env`                     | `development`                                    | Environment mode                     |
| `WEB_SEARCH_PROVIDER`     | `brave`                                          | Active search provider               |
| `BRAVE_API_KEY`           | —                                                | Brave Search API key                 |
| `BRAVE_ENDPOINT`          | `https://api.search.brave.com/res/v1/web/search` | Brave API endpoint                   |
| `WEB_SEARCH_MAX_RESULTS`  | `8`                                              | Max results per search query         |
| `WEB_SEARCH_TIMEOUT_S`    | `10.0`                                           | Search request timeout (seconds)     |
| `WEB_SEARCH_CACHE_TTL_S`  | `300`                                             | Cache time-to-live (seconds)         |
| `WEB_SEARCH_BLOCK_DOMAINS`| `[]`                                             | Domains to exclude from results      |
| `WEB_SEARCH_ALLOW_DOMAINS`| `null`                                           | If set, only allow these domains     |

## Design Principles

- **Modularity over monolith** — every component has a clear interface and responsibility
- **Structured data everywhere** — Pydantic models enforce validation at every stage
- **Provider agnostic** — search backends are swappable without changing agent logic
- **Evidence over hallucination** — responses are grounded in retrieved sources with citations
- **Honest confidence** — confidence scores reflect actual evidence quality

## Known Limitations

The current implementation is a working pipeline with known areas for improvement:

- **Query planning is static** — sub-questions and search queries follow a fixed template regardless of query type or intent
- **No ambiguity resolution** — ambiguous terms (e.g., "RAG", "Python", "Java") are not disambiguated before search
- **Snippet-based analysis** — the analysis step deduplicates snippets but does not extract key claims or assess source agreement
- **Concatenation-based synthesis** — the response is assembled from joined snippets rather than LLM-synthesized narrative
- **Source quality not scored** — all sources are treated equally regardless of domain authority or relevance
- **Confidence is source-count-based** — the score does not factor in source quality, agreement, or ambiguity
- **No LLM integration yet** — the pipeline is entirely rule-based and template-driven

## Roadmap

The following features are planned, in implementation order:

### Phase 1: Query Intelligence
- [ ] Query Analysis module with intent classification, domain detection, and ambiguity flagging
- [ ] Ambiguity Resolver for multi-meaning terms (RAG, Python, Java, Apple, etc.)
- [ ] Dynamic query expansion based on detected intent and domain

### Phase 2: Source Quality
- [ ] Domain authority scoring (tiered ranking of source domains)
- [ ] Relevance scoring per source against the resolved query
- [ ] Low-quality source filtering before synthesis

### Phase 3: Intelligent Synthesis
- [ ] LLM integration for narrative synthesis (OpenAI / Anthropic / local models)
- [ ] Claim extraction and cross-source agreement detection
- [ ] Inline citation mapping (claims linked to specific sources)
- [ ] Calibrated confidence scoring based on evidence quality and agreement

### Phase 4: Deduplication and Clustering
- [ ] Embedding-based semantic similarity for source grouping
- [ ] Redundancy removal across overlapping sources

### Phase 5: ReAct Agent Loop
- [ ] Iterative Thought → Action → Observation reasoning loop
- [ ] Tool-based architecture (web_search, resolve_ambiguity, filter_sources, synthesize)
- [ ] Agent decides when to search again, disambiguate, or finalize
- [ ] Session and conversation context support

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