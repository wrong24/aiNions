# aiNions Orchestration Engine - Quick Start Guide

## Project Overview

The aiNions Orchestration Engine is a production-ready AI orchestration system that processes messages through a hierarchical 3-layer LLM architecture. It intelligently delegates tasks, extracts actionable insights, and generates comprehensive orchestration maps.

## Key Features

**Hierarchical Architecture**

- L1 Orchestrator: Strategic planning with GPT-4o
- L2 Coordinators: Domain-specific task execution
- L3 Workers: Semantic extraction with GPT-3.5-turbo
- Strict architectural constraint: L1 cannot access L3 directly

**Real LLM Integration**

- GPT-4o for strategic planning (L1)
- GPT-3.5-turbo for cost-optimized extraction (L3)
- Structured output validation via Pydantic
- Full error handling and retry logic

**Production Infrastructure**

- Docker: Multi-stage build (~400MB optimized image)
- Kubernetes: 11 resources with auto-scaling (2-5 replicas)
- FastAPI: 4 endpoints with health checks
- Redis: Distributed caching with automatic in-memory fallback

**Intelligent Caching**

- Redis-backed knowledge retrieval with 60-second TTL
- Automatic in-memory fallback if Redis unavailable
- Transparent `@cache_result` decorator
- Cost-optimized extraction strategies

**Multiple Output Formats**

- NION Orchestration Map (plaintext for readability)
- Structured JSON (for programmatic access)
- Detailed JSON with execution metadata

## Getting Started (5 Minutes)

### Prerequisites

- Python 3.11+ or Docker
- OpenAI API key (https://platform.openai.com/api-keys)
- ~5 minutes for setup

### Option 1: Local Python (Recommended for Quick Testing)

```powershell
# Navigate to project
cd c:\Users\jainp\OneDrive\Desktop\aiNions

# Create and activate virtual environment
python -m venv venv
.\venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Set API key
$env:OPENAI_API_KEY = "sk-your-actual-api-key-here"

# Run local integration test
python test_local.py
```

### Option 2: With FastAPI Server

```powershell
# From project directory with venv activated
$env:OPENAI_API_KEY = "sk-your-actual-api-key-here"

# Terminal 1: Start server
python -m uvicorn app.main:app --port 8000

# Terminal 2: Test API
python test_api.py
```

### Option 3: Using Docker Compose

```powershell
cd c:\Users\jainp\OneDrive\Desktop\aiNions

# Create .env file
@"
OPENAI_API_KEY=sk-your-actual-api-key-here
"@ | Out-File .env -Encoding UTF8

# Start services
docker-compose up --build

# Verify health
curl http://localhost:8000/health
```

## API Endpoints

| Endpoint            | Method | Purpose                              |
| ------------------- | ------ | ------------------------------------ |
| `/health`           | GET    | Service health check                 |
| `/process`          | POST   | Process message (JSON response)      |
| `/process/nion-map` | POST   | Process message (plaintext NION Map) |
| `/process/json`     | POST   | Process message (detailed JSON)      |

## Example API Call

```powershell
$body = @{
    message = "The customer demo went great!"
    sender = "Sarah Chen"
    project_id = "PRJ-ALPHA"
} | ConvertTo-Json

curl -X POST http://localhost:8000/process/nion-map `
  -H "Content-Type: application/json" `
  -d $body
```

## Project Structure

```
aiNions/
├── app/                         # Application code (5 modules, 2,050+ LOC)
│   ├── main.py                  # FastAPI server (320 LOC)
│   ├── graph.py                 # LangGraph orchestration (380 LOC)
│   ├── agents.py                # L3 workers + caching (450 LOC)
│   ├── schemas.py               # Pydantic models (650 LOC)
│   └── formatter.py             # Output formatting (250 LOC)
├── test_local.py                # Integration test
├── test_api.py                  # Endpoint tests
├── setup.py                     # Setup wizard
├── docker-compose.yml           # Local development
├── Dockerfile                   # Production image
├── k8s-deployment.yaml          # Kubernetes manifests
└── Documentation/
    ├── README.md                # Complete setup guide
    ├── EXECUTION_GUIDE.md       # Execution steps
    ├── API_EXAMPLES.md          # API reference
    ├── IMPLEMENTATION_SUMMARY.md # Technical details
    ├── PROJECT_INDEX.md         # File-by-file guide
    └── .env.template            # Config template
```

## Performance Characteristics

| Metric                      | Value        |
| --------------------------- | ------------ |
| L1 Planning Time            | 2-5 seconds  |
| L3 Extraction Time          | 3-7 seconds  |
| Knowledge Retrieval (Redis) | 50-150ms     |
| Total End-to-End            | 5-12 seconds |
| Docker Image Size           | ~400MB       |
| Per-Request Memory          | ~100-200MB   |

## Common Tasks

**Add a New L3 Worker:**

1. Create method in `L3Agents` class (agents.py)
2. Add Pydantic model in schemas.py
3. Update L2 coordinator to call it
4. Update formatter for output

**Change LLM Models:**

1. Edit model initialization in agents.py
2. Update L1 and/or L3 model selection
3. Adjust temperature/token parameters
4. Test with test_local.py

**Deploy to Production:**

1. Set `OPENAI_API_KEY` in Kubernetes Secret
2. Apply manifests: `kubectl apply -f k8s-deployment.yaml`
3. Verify: `kubectl get pods -n nion-system`
4. Monitor with `kubectl logs -f`

## Troubleshooting

| Issue                    | Solution                                        |
| ------------------------ | ----------------------------------------------- |
| `ModuleNotFoundError`    | Run `pip install -r requirements.txt`           |
| `OPENAI_API_KEY not set` | Set environment variable or create `.env`       |
| Redis connection error   | System uses in-memory fallback automatically    |
| Port 8000 in use         | Use `--port 8001` flag or stop other service    |
| API rate limit           | Reduce request frequency or upgrade OpenAI plan |

## Documentation Roadmap

1. **START_HERE.md** ← You are here (Quick overview)
2. **README.md** - Full setup and deployment guide
3. **EXECUTION_GUIDE.md** - Step-by-step execution
4. **API_EXAMPLES.md** - API reference with examples
5. **IMPLEMENTATION_SUMMARY.md** - Technical architecture
6. **PROJECT_INDEX.md** - File-by-file guide

## Next Steps

1. **Run test**: `python test_local.py`
2. **Start server**: `python -m uvicorn app.main:app --port 8000`
3. **Test API**: `python test_api.py`
4. **Read guide**: Open `README.md` for comprehensive setup
5. **Deploy**: Use `docker-compose up` or Kubernetes

---

**Ready to start?**

```powershell
python test_local.py
```
