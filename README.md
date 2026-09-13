# 📊 GenAI Market Research & Intelligence Platform

[![Python](https://img.shields.io/badge/Python-3.11.9-blue.svg?logo=python&logoColor=white)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-1.0.0-009688.svg?logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com/)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.58.0-FF4B4B.svg?logo=streamlit&logoColor=white)](https://streamlit.io/)
[![CrewAI](https://img.shields.io/badge/CrewAI-1.14.7-red.svg)](https://www.crewai.com/)
[![uv](https://img.shields.io/badge/Package_Manager-uv-purple.svg)](https://github.com/astral-sh/uv)

An autonomous multi-agent market research and competitive intelligence engine built with **CrewAI**, **FastAPI**, and **Streamlit**. The platform synthesizes real-time web research, competitive mapping, customer demand signals, and research quality audits into validated business strategy recommendations.

---

## 📌 Problem Statement

Conducting thorough market research and competitive intelligence for new product ideas is complex, time-consuming, and prone to subjective bias. Strategists and entrepreneurs struggle to:
- Estimate TAM/SAM/SOM with objective confidence levels.
- Track real-time competitor positioning, feature overlap, and defensibility risks.
- Separate stated customer interest from true willingness-to-pay.
- Validate research quality and flag hallucinated or unsupported claims.

**Solution**: This platform deploys a sequential team of specialized AI agents that gather real-time market data, map competitive landscapes, audit evidence reliability, and generate executive-level product strategy reports with confidence scores.

---

## 🏗️ Methodology & Architecture

The application executes a 5-stage sequential workflow using **CrewAI**. Each agent operates with specific goals, evidence guidelines, and output schemas:

```mermaid
graph TD
    A[Product Idea Input] --> B[1. Market Research Specialist]
    B -->|Market Size and Signals| C[2. Competitive Intelligence Analyst]
    B -->|Market Data| D[3. Customer Insights Researcher]
    C -->|Competitor Data| D
    B -->|Market Findings| E[4. Research Review Manager]
    C -->|Competitive Findings| E
    D -->|Customer Findings| E
    E -->|Validated Audit Report| F[5. Product Strategy Lead]
    F --> G[Final Strategy Synthesis and Score]

    subgraph External Tools and Memory
        T1[Tavily Search API]
    end

    B --- T1
    C --- T1
    D --- T1
```

### Multi-Agent Pipeline Roles

1. **Market Research Specialist**: Analyzes market size (TAM/SAM/SOM), growth drivers, regulatory constraints, and technology readiness.
2. **Competitive Intelligence Analyst**: Maps direct, indirect, and substitute competitors, positioning, pricing models, and differentiation paths.
3. **Customer Insights Researcher**: Identifies target segments, jobs-to-be-done, adoption barriers, and willingness-to-pay signals.
4. **Research Review & Validation Manager**: Audits research for consistency, evidence recency, and overconfident claims.
5. **Product Strategy Lead**: Reconciles validated findings into an MVP scope, GTM plan, risk analysis, and business viability score (0.0 to 10.0).

---

## 🧠 Model Details & Provider Fallback

The LLM architecture implements a robust multi-provider fallback and priority system:

| Provider | Supported Config / Models | Primary Role |
| :--- | :--- | :--- |
| **Google Gemini** | `gemini-2.5-flash` / `gemini-2.5-pro` | Primary LLM Provider |
| **OpenRouter** | Multi-vendor models via OpenRouter API | Secondary / Fallback LLM |
| **Ollama Cloud / Local** | `deepseek-v3.1:671b-cloud`, `gpt-oss:120b-cloud`, `qwen3-coder:480b-cloud`, `kimi-k2:1t-cloud` | Critic LLM / Local Execution |

- **Hyperparameters & Resilience**:
  - `Temperature`: `0.6`
  - `Max Tokens`: `1024`
  - `Circuit Breaker Threshold`: `3 failures`
  - `Cooldown Period`: `30s`

---

## 📦 Project Structure

```text
market_research/
├── app/                        # FastAPI Backend Application
│   ├── api/                    # API endpoints & routing (auth, research)
│   ├── db/                     # Database connection & management (PostgreSQL / AsyncPG)
│   └── main.py                 # FastAPI application entry point & lifecycle
├── configs/                    # YAML agent definitions & configuration schemas
│   ├── agents.yaml             # Agent role descriptions, goals, and backstories
│   ├── core_config.py          # Pydantic settings & env variable parsing
│   └── tasks.yaml              # Task descriptions, expected outputs & evaluation
├── pages/                      # Streamlit UI Navigation Pages
│   ├── home.py                 # Landing page
│   ├── login.py                # User login page
│   ├── signup.py               # User registration page
│   ├── research.py             # Interactive research workspace
│   └── settings.py             # User account settings
├── personal/                   # Project helper documentation & run scripts
│   └── helper.md               # Quick execution reference & sample inputs
├── reports/                    # Generated market research reports
├── schemas/                    # Pydantic data contracts
├── src/                        # Core Application & AI Logic
│   ├── llm/                    # LLM provider factories & fallbacks
│   ├── utils/                  # Logging & custom exception handling
│   └── workflow/               # CrewAI agents, tasks, guardrails & tools
├── ui/                         # Streamlit UI utilities, styling & API client
│   ├── api_client.py           # Streamlit-to-FastAPI client wrapper
│   ├── auth.py                 # Frontend session management
│   └── styles.py               # Custom UI styles & layout
├── Dockerfile                  # Container definition
├── docker-compose.yml          # Multi-container service setup
├── pyproject.toml              # Dependencies & project metadata
├── streamlit_app.py            # Streamlit application entry point
└── uv.lock                     # UV lockfile for deterministic builds
```

---

## 🔑 Required API Keys & Environment Setup

Create a `.env` file in the root directory. **Do NOT commit real credentials or keys to source control.** Configure the following required environment variables:

```env
# App Configuration
APP_NAME="Market Research Platform"
APP_VERSION="1.0.0"
SECRET_KEY=your_jwt_secret_key_here

# Database Configurations
DB_DSN=postgresql://username:password@localhost:5432/market_research_db
DB_PATH=data/raw.db
VECTOR_DB_PATH=data/vectordb

# Agent & Task YAML Config Paths
AGENTS_CONFIG_PATH=configs/agents.yaml
TASKS_CONFIG_PATH=configs/tasks.yaml
LANGCHAIN_PROJECT=market-research

# LLM Providers (Configure at least one valid provider)
# 1. Google Gemini
GEMINI_PROVIDER_NAME=gemini
GEMINI_MODEL_NAME=gemini-2.5-flash
GOOGLE_API_KEY=your_google_api_key_here
GEMINI_PRIORITY=1

# 2. OpenRouter (Optional)
OPENROUTER_PROVIDER_NAME=openrouter
OPENROUTER_MODEL_NAME=anthropic/claude-3.5-sonnet
OPENROUTER_API_KEY=your_openrouter_api_key_here
OPENROUTER_PRIORITY=2

# 3. Ollama (Optional / Critic LLM)
OLLAMA_PROVIDER_NAME=ollama
OLLAMA_MODEL_NAME=deepseek-v3.1:671b-cloud
OLLAMA_API_KEY=your_ollama_api_key_here
OLLAMA_PRIORITY=3

# Embedding Settings
HUGGINGFACEHUB_API_TOKEN=your_huggingface_token_here
EMBEDDING_MODEL=sentence-transformers/all-MiniLM-L6-v2
EMBEDDING_DIMENSION=384
EMBEDDINGS_TABLE_NAME=market_embeddings
CHUNK_SIZE=500
CHUNK_OVERLAP=50

# Research & External Tools
TAVILY_API_KEY=your_tavily_api_key_here
ALPHAVANTAGE_STOCK_API_KEY=your_alphavantage_key_here
CURRENCY_EXCHANGE_URL=https://v6.exchangerate-api.com/v6
CURRENCY_EXCHANGE_API_KEY=your_currency_api_key_here
```

---

## 🚀 Installation & Execution

### 1. Prerequisites
- **Python**: `3.11.9`
- **uv**: Fast Python package installer (`pip install uv` or `curl -LsSf https://astral.sh/uv/install.sh | sh`)

### 2. Install Dependencies
```bash
# Clone the repository
git clone https://github.com/your-username/market_research.git
cd market_research

# Sync project dependencies using uv
uv sync
```

### 3. Run Commands

#### Start the FastAPI Backend Server
```bash
uv run uvicorn app.main:app --port 8000
```
- API Documentation available at `http://localhost:8000/docs`

#### Start the Streamlit Frontend Web App
```bash
uv run streamlit run streamlit_app.py --server.port 8500
```
- Frontend UI accessible at `http://localhost:8500`

---

## 💡 Usage Examples & Sample Inputs

Once the application is running, enter a product idea in the Streamlit workspace or send a POST request to `/api/v1/research`.

### Sample Input 1: YouTube Content Distribution Automation
> *"An AI-powered tool that summarizes YouTube videos on my channel and posts them to LinkedIn, X, and WhatsApp."*

### Sample Input 2: AI Interview Simulator Platform
> *"An AI-powered interview simulator designed specifically for engineering students and job seekers. Users upload their resume, select a target role or company, and participate in realistic mock interviews conducted by an AI interviewer through voice or chat. The system evaluates technical answers, communication skills, confidence, and resume explanations, then generates detailed feedback and improvement suggestions."*

---

## 🔮 Future Work

- [ ] **Dynamic Tool Selection**: Expand integrations with Google Trends and real-time financial APIs.
- [ ] **Prompt Optimization**: Continuous refinement of agent prompts for stricter JSON output compliance.
- [ ] **Multi-Modal Research**: Support automated ingestion and parsing of PDF pitch decks and market slide decks.
- [ ] **Report PDF Export**: Allow users to download styled PDF reports directly from the Streamlit UI.

---

## 🛠️ Tech Stack

- **Framework**: FastAPI, Streamlit
- **Agentic Workflow**: CrewAI, LiteLLM
- **Database & Storage**: AsyncPG (PostgreSQL)
- **Web Research**: Tavily Python SDK, DuckDuckGo Search, Selenium
- **Package Manager**: `uv`
