# VeriScope

AI-powered backend research engine with LLM-driven synthesis, intelligent query planning, modular search providers, and structured citation generation.

## Overview

VeriScope is a modular backend research engine that takes a user query, analyzes it with a local LLM, searches the web using pluggable providers, synthesizes sources into a coherent narrative, and returns a structured response with inline citations.

The system uses a clean separation between search providers, LLM providers, prompt templates, data models, agent logic, and API routing. The current implementation delivers an end-to-end LLM-powered research pipeline running entirely on local hardware, with an active roadmap toward source quality scoring, ambiguity resolution, and ReAct-based agentic reasoning.

## Current Capabilities

- LLM-powered narrative synthesis via Ollama (Mistral 7B) with graceful fallback to rule-based concatenation
- LLM-powered query analysis with intent classification, domain detection, and dynamic search query generation
- Pluggable LLM provider architecture mirroring the search provider pattern (abstract interface, Ollama provider, mock provider)
- Pluggable search provider architecture with abstract interface
- Brave Search API integration with structured JSON parsing, TTL caching, and HTML snippet cleaning
- DuckDuckGo fallback provider with HTML parsing, URL canonicalization, and domain filtering
- Prompt template system for synthesis and query analysis with structured JSON output parsing
- Citation filtering — only sources referenced in the LLM answer are included in the response
- Source limiting — top 10 sources sent to synthesis for faster generation on consumer GPUs
- Environment-based provider switching for both search and LLM (no code changes required)
- Structured Pydantic models for sources, citations, research plans, LLM responses, and API responses
- End-to-end research pipeline: Query → LLM Analysis → Search → Analyze → LLM Synthesis → Cite → Respond
- Source deduplication by URL across multiple search queries
- HTML tag stripping and entity decoding in search snippets
- Input validation with length and empty-check guards
- RESTful API with health check (includes LLM status) and research endpoints
- JSON parsing utility for safely extracting structured data from LLM responses

## Core Architecture

```text
VeriScope/
├── app/
│   ├── api/
│   │   └── routes.py              # FastAPI endpoint definitions
│   ├── agents/
│   │   └── research_agent.py      # Core research pipeline logic
│   ├── config/
│   │   └── settings.py            # Environment-based configuration
│   ├── models/
│   │   └── research_models.py     # Pydantic schemas (Source, Citation, LLMResponse, etc.)
│   ├── prompts/
│   │   ├── synthesis.py           # Prompt templates for narrative synthesis
│   │   └── query_analysis.py      # Prompt templates for query understanding
│   ├── providers/
│   │   ├── search_provider.py     # Abstract SearchProvider interface
│   │   ├── llm_provider.py        # Abstract LLMProvider interface
│   │   ├── brave_search_provider.py   # Brave Search API provider
│   │   ├── web_search_provider.py     # DuckDuckGo fallback provider
│   │   ├── ollama_provider.py     # Ollama local LLM provider
│   │   ├── mock_search_provider.py    # Mock search provider for testing
│   │   └── mock_llm_provider.py   # Mock LLM provider for testing
│   ├── services/
│   │   └── research_services.py   # Provider wiring and agent orchestration
│   └── utils/
│       └── json_parser.py         # Safe JSON extraction from LLM responses
├── main.py                        # FastAPI application entry point
├── requirements.txt
└── .env                           # Environment variables (not committed)
```

The architecture separates concerns so that search providers, LLM providers, prompt templates, agent logic, data models, and API routing can evolve independently.

## How the Pipeline Works

1. **Query Analysis (LLM-powered)**
   - Accept a user query via the API.
   - Send the query to the LLM for intent classification, domain detection, and ambiguity flagging.
   - LLM generates tailored search queries based on understanding the query's meaning.
   - Falls back to static templates if the LLM is unavailable.

2. **Web Search**
   - Execute the LLM-generated search queries through the active provider (Brave or DuckDuckGo).
   - Collect and deduplicate results by URL.
   - Strip HTML tags and decode entities from snippets.

3. **Source Analysis**
   - Extract snippets from collected sources.
   - Remove duplicate content across results.
   - Limit to top 10 sources for synthesis.

4. **Narrative Synthesis (LLM-powered)**
   - Send the query and numbered sources to the LLM with a synthesis prompt.
   - LLM writes a coherent answer citing sources with inline references like [1], [2].
   - Falls back to concatenation-based synthesis if the LLM is unavailable.

5. **Citation Filtering**
   - Parse which source numbers the LLM referenced in its answer.
   - Include only those sources in the citations array.
   - Return a structured JSON response.

```json
{
  "status": "success",
  "prompt": "What is retrieval augmented generation?",
  "answer": "Retrieval-Augmented Generation (RAG) is a technique that optimizes the output of large language models by referencing authoritative knowledge bases outside of their training data [1][2]. The approach combines retrieval-based methods with generative AI to produce more accurate and contextually relevant responses [3]...",
  "citations": [
    {
      "source_id": "28839f5dd7",
      "url": "https://aws.amazon.com/what-is/retrieval-augmented-generation/",
      "title": "What is RAG? - Retrieval-Augmented Generation AI Explained - AWS",
      "quotes": "...",
      "evidence": "...",
      "confidence": 0.5
    }
  ],
  "confidence": 0.75
}
```

## Provider Systems

### Search Providers

VeriScope uses an abstract `SearchProvider` interface that decouples agent logic from any specific search engine.

- **BraveSearchProvider** — Primary provider. Uses the Brave Search API for structured JSON results. Supports API key authentication, configurable result count, TTL-based caching, and HTML snippet cleaning.
- **WebSearchProvider (DuckDuckGo)** — Fallback provider. Parses DuckDuckGo HTML results with URL canonicalization, tracking parameter removal, domain allow/block filtering, and HTML cleaning.
- **MockSearchProvider** — Testing provider. Returns deterministic results for unit and integration tests.

The active search provider is selected via the `WEB_SEARCH_PROVIDER` environment variable.

### LLM Providers

VeriScope uses an abstract `LLMProvider` interface that mirrors the search provider pattern.

- **OllamaProvider** — Primary provider. Calls Ollama's OpenAI-compatible chat completions API at `localhost:11434`. Supports system prompts, configurable temperature and token limits, and health checking via `/api/tags`.
- **MockLLMProvider** — Testing provider. Returns deterministic responses for testing the pipeline without a running LLM.

The active LLM provider is selected via the `LLM_PROVIDER` environment variable. The LLM provider includes an `is_available()` health check because local models may not always be running — unlike cloud search APIs, a local Ollama instance can be stopped, out of VRAM, or not yet loaded.

## Technology Stack

- **Backend:** Python 3.10+, FastAPI, Uvicorn
- **LLM Backend:** Ollama (local), via OpenAI-compatible chat completions API
- **LLM Model:** Mistral 7B (configurable — supports any Ollama-compatible model)
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

4. **Install and start Ollama**
   ```bash
   # Download from https://ollama.com and install
   ollama serve                     # Start the Ollama server
   ollama pull mistral              # Download Mistral 7B (~4GB)
   ```

5. **Configure environment variables** — create a `.env` file:
   ```env
   app_name=VeriScope
   env=development
   WEB_SEARCH_PROVIDER=brave
   BRAVE_API_KEY=your_brave_api_key
   WEB_SEARCH_MAX_RESULTS=8
   LLM_PROVIDER=ollama
   OLLAMA_BASE_URL=http://localhost:11434
   OLLAMA_MODEL=mistral
   LLM_TEMPERATURE=0.3
   LLM_MAX_TOKENS=2048
   LLM_TIMEOUT_S=120
   ```

## Running the Application

```bash
# Terminal 1: Start Ollama
ollama serve

# Terminal 2: Start VeriScope
uvicorn app.main:app --reload
```

## API Documentation

Interactive docs available at: `http://127.0.0.1:8000/docs`

## API Endpoints

| Method | Path        | Description                                      |
|--------|-------------|--------------------------------------------------|
| GET    | `/`         | Hello endpoint                                   |
| GET    | `/health`   | Service health check with app name, env, and LLM status |
| POST   | `/research` | Submit a query and receive a research response    |

### GET /health

**Response:**
```json
{
  "status": "ok",
  "app_name": "VeriScope",
  "env": "development",
  "llm_provider": "ollama",
  "llm_model": "mistral",
  "llm_status": "connected"
}
```

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
  "answer": "Retrieval-Augmented Generation (RAG) is a technique...",
  "citations": [
    {
      "source_id": "28839f5dd7",
      "url": "https://aws.amazon.com/what-is/retrieval-augmented-generation/",
      "title": "What is RAG? - Retrieval-Augmented Generation AI Explained - AWS",
      "quotes": "...",
      "evidence": "...",
      "confidence": 0.5
    }
  ],
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
| `WEB_SEARCH_CACHE_TTL_S`  | `300`                                            | Cache time-to-live (seconds)         |
| `WEB_SEARCH_BLOCK_DOMAINS`| `[]`                                             | Domains to exclude from results      |
| `WEB_SEARCH_ALLOW_DOMAINS`| `null`                                           | If set, only allow these domains     |
| `LLM_PROVIDER`            | `ollama`                                         | Active LLM provider (ollama / mock)  |
| `OLLAMA_BASE_URL`         | `http://localhost:11434`                         | Ollama server address                |
| `OLLAMA_MODEL`            | `mistral`                                        | Model name (mistral, llama3, phi3)   |
| `LLM_TEMPERATURE`         | `0.3`                                            | Generation randomness (0.0–1.0)      |
| `LLM_MAX_TOKENS`          | `2048`                                           | Max response length in tokens        |
| `LLM_TIMEOUT_S`           | `120.0`                                          | LLM request timeout (seconds)        |

## Design Principles

- **Modularity over monolith** — every component has a clear interface and responsibility
- **Structured data everywhere** — Pydantic models enforce validation at every stage
- **Provider agnostic** — both search and LLM backends are swappable without changing agent logic
- **Evidence over hallucination** — synthesis prompt instructs the LLM to only use provided sources
- **Graceful degradation** — if the LLM is unavailable, the pipeline falls back to rule-based logic
- **Honest documentation** — capabilities and limitations reflect the actual implementation

## Known Limitations

The current implementation is a working LLM-powered pipeline with known areas for improvement:

- **No ambiguity resolution** — ambiguous terms (e.g., "RAG", "Python", "Java") are not disambiguated before search; the "What is rag?" query returns both dictionary definitions and AI framework results
- **Snippet-based analysis** — the analysis step deduplicates snippets but does not extract key claims or assess source agreement
- **Source quality not scored** — all sources are treated equally regardless of domain authority or relevance
- **Confidence is source-count-based** — the score does not factor in source quality, agreement, or the LLM's assessment
- **Citation confidence is static** — individual citation confidence is hardcoded at 0.5 rather than reflecting actual relevance
- **Local model speed** — synthesis on consumer GPUs (e.g., RTX 3050) takes 2–5 minutes per query; faster with smaller models like phi3
- **JSON parsing from LLM is best-effort** — query analysis falls back to static templates if the LLM returns unparseable JSON

## Roadmap

The following features are planned, in implementation order:

### Phase 1: Query Intelligence
- [x] LLM-powered query analysis with intent classification and domain detection
- [x] Dynamic query expansion based on detected intent
- [ ] Ambiguity Resolver for multi-meaning terms (RAG, Python, Java, Apple, etc.)
- [ ] User-facing disambiguation when ambiguity is detected

### Phase 2: Source Quality
- [ ] Domain authority scoring (tiered ranking of source domains)
- [ ] Relevance scoring per source against the resolved query
- [ ] Low-quality source filtering before synthesis

### Phase 3: Intelligent Synthesis
- [x] LLM integration for narrative synthesis via Ollama (Mistral 7B)
- [x] Inline citation mapping (LLM references sources by number, citations filtered to match)
- [x] Graceful fallback to rule-based synthesis when LLM is unavailable
- [ ] Claim extraction and cross-source agreement detection
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