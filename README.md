# aiNions Orchestration Engine - Setup & Deployment Guide

## Overview

The aiNions Orchestration Engine is a hierarchical AI orchestration system that processes messages through a 3-layer LLM architecture. It provides intelligent task planning, domain-specific coordination, and specialized extraction capabilities with production-ready deployment options.

## Technology Stack

- **LangGraph**: Stateful graph orchestration with conditional routing
- **LangChain + OpenAI**: LLM integration for strategic planning and semantic extraction
- **FastAPI**: RESTful API server with health checks and validation
- **Redis**: Distributed caching layer with in-memory fallback
- **Docker**: Multi-stage containerization with optimized image size (~400MB)

## Architecture

### 3-Layer Hierarchy

```
┌─────────────────────────────────────────────────────────────────┐
│ INPUT: Message + Metadata                                       │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│ L1: Orchestrator (Strategic Planning)                          │
│ • Analyzes message intent and context                          │
│ • Creates delegation plan for L2 domains                       │
│ • Enforced isolation: Cannot see or access L3 directly        │
└─────────────────────────────────────────────────────────────────┘
          ↓                    ↓                    ↓
┌──────────────────┐ ┌──────────────────┐ ┌──────────────────────┐
│ L2: Tracking     │ │ L2: Communication│ │ Cross-Cutting Layer │
│ • Action Items   │ │ • Q&A Generation │ │ • Knowledge Retrieval│
│ • Risk Assessment│ │ • Issue Tracking │ │ • Quality Evaluation │
└──────────────────┘ └──────────────────┘ └──────────────────────┘
          ↓                    ↓                    ↓
┌─────────────────────────────────────────────────────────────────┐
│ L3: Worker Agents (Semantic Extraction - Optimized for Cost)   │
│ • extract_action_items()  • extract_risks()  • generate_qna()  │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│ EVALUATOR: Quality Assessment & Output Formatting              │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│ OUTPUT: NION Orchestration Map (Plaintext or JSON)             │
└─────────────────────────────────────────────────────────────────┘
```

## Requirements

- **Python**: 3.11 or higher
- **Docker**: Latest version (optional, for containerized deployment)
- **Docker Compose**: Latest version (optional, for development)
- **OpenAI API Key**: For LLM integration (https://platform.openai.com/api-keys)
- **Redis**: Optional (system provides in-memory fallback if unavailable)

## Quick Start

### Option 1: Local Development (Fastest)

```powershell
# Navigate to project directory
cd c:\Users\jainp\OneDrive\Desktop\aiNions

# Create virtual environment
python -m venv venv
.\venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Set your OpenAI API key (PowerShell)
$env:OPENAI_API_KEY = "sk-your-actual-api-key-here"

# Run integration test
python test_local.py
```

### Option 2: With FastAPI Server

```powershell
# In terminal 1: Start the FastAPI server
$env:OPENAI_API_KEY = "sk-your-actual-api-key-here"
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload

# In terminal 2: Test the API
python test_api.py
```

### Option 3: Using Docker Compose (Recommended for Production Testing)

```powershell
# Navigate to project directory
cd c:\Users\jainp\OneDrive\Desktop\aiNions

# Create .env file with your OpenAI API key
@"
OPENAI_API_KEY=sk-your-actual-api-key-here
"@ | Out-File -FilePath .env -Encoding UTF8

# Build and run containers
docker-compose build --no-cache
docker-compose up -d

# Check service health
curl http://localhost:8000/health

# Process a message
$message = @{
    message = "The customer demo went great!"
    sender = "Sarah Chen"
    project_id = "PRJ-ALPHA"
} | ConvertTo-Json

curl -X POST http://localhost:8000/process/nion-map `
  -H "Content-Type: application/json" `
  -d $message
```

## API Endpoints

| Endpoint            | Method | Description                          | Response Format |
| ------------------- | ------ | ------------------------------------ | --------------- |
| `/health`           | GET    | Health check                         | JSON            |
| `/process`          | POST   | Process message with standard output | JSON            |
| `/process/nion-map` | POST   | Process message with NION Map format | Plaintext       |
| `/process/json`     | POST   | Process message with detailed JSON   | JSON            |

## Docker Deployment

### Build with Docker Compose

```powershell
# Build containers
docker-compose build --no-cache

# Start services (Redis + FastAPI)
docker-compose up -d

# View logs
docker-compose logs -f nion-app

# Stop services
docker-compose down
```

### Environment Configuration

Create a `.env` file in the project root:

```env
OPENAI_API_KEY=sk-your-actual-api-key-here
REDIS_HOST=redis
REDIS_PORT=6379
HOST=0.0.0.0
PORT=8000
```

### Build Docker Image

```powershell
docker build -t nion-orchestrator:latest .

# Run container
docker run -e OPENAI_API_KEY="sk-your-key" `
  -p 8000:8000 `
  --name nion-app `
  nion-orchestrator:latest
```

## Implementation Details

### Orchestration Flow

1. **L1 Orchestrator**: Receives message and creates a strategic plan

   - Analyzes message intent and context
   - Determines which L2 domains require execution
   - Creates task list with execution routing

2. **L2 Domain Layers**: Execute specialized coordination tasks

   - **L2 Tracking**: Extracts action items, risks, and key decisions
   - **L2 Communication**: Generates Q&A pairs and issue tracking data
   - **Cross-Cutting**: Retrieves contextual knowledge and evaluates output quality

3. **L3 Worker Agents**: Perform fine-grained semantic extraction

   - `extract_action_items()`: Identifies actionable tasks
   - `extract_risks()`: Detects potential risks and mitigation strategies
   - `generate_qna()`: Creates question-answer pairs for documentation

4. **Evaluator**: Assesses execution results
   - Validates output quality
   - Computes confidence scores
   - Generates audit logs

### Caching Strategy

- **Redis Primary**: 60-second TTL for knowledge retrieval
- **In-Memory Fallback**: Automatic fallback if Redis unavailable
- **Transparent Integration**: Via `@cache_result` decorator in `agents.py`

### LLM Models

- **L1 Orchestrator**: `gpt-4o` (strategic planning)
- **L3 Workers**: `gpt-3.5-turbo` (cost-optimized extraction)
- **Response Format**: Structured JSON with validation via Pydantic

### Response Format

#### NION Orchestration Map (Plaintext)

```
═══════════════════════════════════════════════════════════════
NION ORCHESTRATION MAP
═══════════════════════════════════════════════════════════════

MESSAGE METADATA
────────────────────────────────────────────────────────────────
Sender: Sarah Chen
Project: PRJ-ALPHA
Timestamp: 2024-01-15T10:30:45Z
Request ID: a1b2c3d4-e5f6-7890-abcd-ef1234567890

L1 PLAN (Strategic Direction)
────────────────────────────────────────────────────────────────
Task 1: [HIGH] Extract action items from customer feedback
Task 2: [MEDIUM] Assess project risks
Task 3: [MEDIUM] Generate Q&A for documentation

L2/L3 EXECUTION RESULTS
────────────────────────────────────────────────────────────────
ACTION ITEMS:
  • Follow up with customer on timeline
  • Update project roadmap based on feedback
  • Schedule team retrospective

RISKS:
  • Resource allocation may be tight
  • External dependency on vendor response

Q&A PAIRS:
  Q: What was the customer feedback?
  A: The customer demo went great! Team is excited.

EXECUTION SUMMARY
────────────────────────────────────────────────────────────────
Total Tasks: 3
Successful: 3
Failed: 0
Duration: 8.5 seconds
```

#### JSON Response

```json
{
  "status": "success",
  "request_id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
  "timestamp": "2024-01-15T10:30:45Z",
  "results": {
    "action_items": [
      {
        "item": "Follow up with customer on timeline",
        "priority": "HIGH",
        "assignee": "Sarah Chen"
      }
    ],
    "risks": [
      {
        "risk": "Resource allocation may be tight",
        "severity": "MEDIUM",
        "mitigation": "Plan resource allocation review"
      }
    ],
    "qna_pairs": [
      {
        "question": "What was the customer feedback?",
        "answer": "The customer demo went great! Team is excited."
      }
    ]
  },
  "execution_metrics": {
    "total_tasks": 3,
    "successful": 3,
    "failed": 0,
    "duration_ms": 8500
  }
}
```

## Troubleshooting

| Issue                      | Cause                        | Solution                                                  |
| -------------------------- | ---------------------------- | --------------------------------------------------------- |
| `OPENAI_API_KEY not found` | Missing environment variable | Set `$env:OPENAI_API_KEY` or create `.env` file           |
| Redis connection error     | Redis not running            | Run `redis-server` or remove Redis dependency             |
| API rate limit exceeded    | Too many requests            | Implement request throttling or wait for rate limit reset |
| Module not found           | Dependencies not installed   | Run `pip install -r requirements.txt`                     |
| Port 8000 in use           | Another service on same port | Change port with `--port 8001` flag                       |

## Docker Compose Logs

```powershell
# View all logs
docker-compose logs -f

# View specific service logs
docker-compose logs -f nion-app
docker-compose logs -f redis

# View last 50 lines
docker-compose logs --tail=50
```

## File Structure

```
aiNions/
├── app/                      # Core application code
│   ├── __init__.py
│   ├── main.py              # FastAPI server
│   ├── graph.py             # LangGraph orchestration
│   ├── agents.py            # L3 worker agents
│   ├── schemas.py           # Pydantic models
│   └── formatter.py         # Output formatting
├── requirements.txt         # Python dependencies
├── Dockerfile               # Docker image definition
├── docker-compose.yml       # Docker Compose configuration
├── k8s-deployment.yaml      # Kubernetes manifests
├── test_local.py            # Local integration tests
├── test_api.py              # API endpoint tests
├── setup.py                 # Setup wizard
└── README.md                # This file
```

## Project Documentation

- **START_HERE.md**: Quick overview and key features
- **API_EXAMPLES.md**: Complete API reference with examples
- **EXECUTION_GUIDE.md**: Detailed execution and configuration
- **IMPLEMENTATION_SUMMARY.md**: Technical architecture details
- **PROJECT_INDEX.md**: Complete file guide
- **.env.template**: Environment variable template

## Support & Resources

- **LangGraph Documentation**: https://langchain-ai.github.io/langgraph/
- **LangChain Documentation**: https://docs.langchain.com/
- **FastAPI Documentation**: https://fastapi.tiangolo.com/
- **OpenAI API Documentation**: https://platform.openai.com/docs/
  | `/health` | GET | Service health check | JSON |
  | `/process` | POST | Process message, return stats | JSON |
  | `/process/ainion-map` | POST | Process message, return aiNion map | Plain Text |

## File Structure

```
\aiNions\
├── app/
│   ├── __init__.py
│   ├── main.py                 # FastAPI application with endpoints
│   ├── schemas.py              # Pydantic models and data structures
│   ├── agents.py               # L3 workers + Cross-cutting agents (Gemini integration)
│   ├── graph.py                # LangGraph + simple orchestration
│   └── formatter.py            # aiNion output formatting
├── requirements.txt            # Python dependencies (Gemini, LangGraph, FastAPI, etc.)
├── Dockerfile                  # Multi-stage Docker build
├── docker-compose.yml          # Docker Compose configuration (Redis + FastAPI)
├── .gitignore                  # Git ignore file (excludes .env and secrets)
├── test_local.py               # Local testing script
├── test_api.py                 # API testing script
├── .env                        # Environment variables (GOOGLE_API_KEY) - NOT TRACKED
├── .env.template               # Template for .env file
├── README.md                   # This file
└── logs/                       # Application logs directory
```

## Dependencies

```
fastapi==0.104.1
uvicorn==0.24.0
pydantic==2.5.0
langchain==0.1.20
langchain-google-genai==0.0.11
langgraph==0.0.50
redis==5.0.1
```

Key changes from OpenAI version:

- Replaced `langchain-openai` with `langchain-google-genai`
- Uses Gemini 2.0 Flash model instead of GPT-4o
- Simplified orchestration bypasses complex LangGraph state machinery

## aiNion Orchestration Map Format

The formatter generates output like:

```
================================================================================
aiNION ORCHESTRATION MAP
================================================================================

MESSAGE METADATA
────────────────────────────────────────────────────────────────────────────
  Message ID: MSG-001
  Sender: Sarah Chen
  Project: PRJ-ALPHA
  Timestamp: 2024-12-06T10:30:00Z
  State ID: abc123
  Message: The customer demo went great!...

=== L1 PLAN ===
────────────────────────────────────────────────────────────────────────────
  [TASK-001] Domain: L2_Tracking
    Task ID: PLAN-001
    Description: Extract and track action items, risks, decisions...
    Priority: P1
    Status: IN_PROGRESS

=== L2/L3 EXECUTION ===
────────────────────────────────────────────────────────────────────────────
  [L2_TRACKING_001] L2_Tracking
    Status: SUCCESS
    Duration: 2345.67ms
    ACTION ITEMS (2):
      • ACT-001: Implement real-time notifications feature
        Owner: Engineering Team, Priority: HIGH, Status: OPEN
        Due: 2025-01-15

=== EXECUTION SUMMARY ===
────────────────────────────────────────────────────────────────────────────
  Total Tasks Executed: 3
  Successful: 3
  Failed: 0
  Overall Status: COMPLETED

================================================================================
```

## Environment Variables

| Variable       | Required | Default   | Description                                            |
| -------------- | -------- | --------- | ------------------------------------------------------ |
| GOOGLE_API_KEY | Yes      | -         | Google Gemini API key (get from https://ai.google.dev) |
| REDIS_HOST     | No       | localhost | Redis server hostname                                  |
| REDIS_PORT     | No       | 6379      | Redis server port                                      |

### Getting a Gemini API Key

1. Go to https://ai.google.dev
2. Click "Get API Key"
3. Create a new API key (free tier available)
4. Set as environment variable: `GOOGLE_API_KEY=your_key_here`

### Free Tier Limits

- 60 requests per minute per user
- 1 request per second per IP
- Monthly quota resets

If you exceed the quota, the system will retry automatically after the rate limit window.

## Troubleshooting

### Redis Connection Error

The system gracefully falls back to in-memory caching if Redis is unavailable. This is expected behavior in development.

### Gemini API Rate Limiting (429 Error)

If you see "429 You exceeded your current quota":

- **Free tier limit**: 60 requests/minute
- **Resolution**: Wait for the retry delay (typically 30-60 seconds) or upgrade to a paid plan
- The system will automatically retry after the specified delay

### Gemini API Errors

Check that:

- `GOOGLE_API_KEY` is correctly set: `echo $env:GOOGLE_API_KEY` (PowerShell)
- API key is valid and hasn't been revoked
- Network connectivity to Google APIs
- Sufficient quota available (monitor at https://ai.dev/usage)

### LangGraph/State Issues

If you encounter LangGraph state errors:

- The system automatically falls back to simple orchestration mode
- This bypasses the state machine and executes nodes sequentially
- All functionality is preserved with better reliability

### Docker Container Won't Start

```bash
# Check logs
docker-compose logs ainion-orchestrator

# Common issues:
# 1. Missing .env file with GOOGLE_API_KEY
# 2. Port 8000 already in use
# 3. Docker daemon not running

# Solution: Create .env file
echo "GOOGLE_API_KEY=your_key_here" > .env

# Then rebuild
docker-compose build --no-cache
docker-compose up -d
```

### Health Check Failing

```bash
# Verify endpoint is responding
curl http://localhost:8000/health

# If failing, check logs:
docker logs ainion-orchestrator

# Common causes:
# 1. GOOGLE_API_KEY not set
# 2. Gemini API quota exceeded
# 3. Network connectivity issues
```

## Performance Considerations

- **L1 (Orchestrator)**: Gemini 2.0 Flash (~1-3s with rate limiting)
- **L2 Tracking**: Extracts action items, risks, decisions
- **L2 Communication**: Generates Q&A records
- **L3 Workers**: Use Gemini for cost efficiency
- **Redis Caching**: Knowledge retrieval cached for 60 seconds
- **Sequential Execution**: Simple orchestration mode executes tasks sequentially for better reliability

### Optimization Tips

1. **Cache Warmer**: Pre-populate Redis with common project contexts
2. **Batch Processing**: Send multiple messages in parallel requests
3. **Timeout Tuning**: Adjust Gemini API timeout based on your network
4. **Rate Limit Management**: Upgrade to paid Gemini tier for higher limits

## Architecture Benefits

### Simple Orchestration Mode

- ✅ **Reliable**: No complex state machine issues
- ✅ **Debuggable**: Linear execution flow easy to trace
- ✅ **Fast**: Sequential execution with no network overhead
- ✅ **Scalable**: Can be parallelized with multiple containers
- ✅ **Flexible**: Easy to add/modify orchestration steps

### Gemini API Integration

- ✅ **Free Tier**: Available at https://ai.google.dev
- ✅ **Fast Model**: Gemini 2.0 Flash optimized for speed
- ✅ **Well Integrated**: LangChain support via langchain-google-genai
- ✅ **Cost Effective**: 0 cost for development/testing

## Security

- API Keys stored only in `.env` file (excluded via .gitignore)
- No credentials in code or Docker images
- Environment variables injected at runtime
- Support for Kubernetes Secrets for production deployment

## Monitoring & Logging

All components log to stdout/stderr:

```bash
# View logs in Docker
docker-compose logs -f ainion-orchestrator

# View specific log entries
docker-compose logs ainion-orchestrator | grep "\[L1\]"
docker-compose logs ainion-orchestrator | grep "ERROR"
```

### Log Levels

- `INFO`: Standard operational messages (L1 execution, API requests)
- `WARNING`: Rate limiting, fallback operations
- `ERROR`: API errors, orchestration failures
- `DEBUG`: Detailed LLM interactions (enable in development)

## API Request/Response Examples

### Health Check

```bash
curl http://localhost:8000/health
```

Response:

```json
{
  "status": "healthy",
  "timestamp": "2025-12-07T07:07:15.822255",
  "service": "Nion Orchestration Engine"
}
```

### Process Message - JSON Response

```bash
curl -X POST http://localhost:8000/process \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Customer demo went great!",
    "sender": "Sarah Chen",
    "project_id": "PRJ-ALPHA"
  }'
```

Response:

```json
{
  "state_id": "abc123-def456",
  "status": "COMPLETED",
  "message": "Orchestration completed successfully",
  "execution_time_ms": 2345.67,
  "execution_results_count": 5
}
```

### Process Message - NION Map (Plaintext)

```bash
curl -X POST http://localhost:8000/process/nion-map \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Customer demo went great!",
    "sender": "Sarah Chen",
    "project_id": "PRJ-ALPHA"
  }'
```

Returns formatted orchestration map (see NION Orchestration Map Format section above)

## Deployment Checklist

- [ ] Python 3.11+ installed
- [ ] Docker and Docker Compose installed
- [ ] Google Gemini API key obtained
- [ ] `.env` file created with `GOOGLE_API_KEY`
- [ ] Docker image builds successfully
- [ ] Redis container starts
- [ ] FastAPI health endpoint responds
- [ ] Sample API request processed successfully
- [ ] Logs show L1 orchestrator executing
- [ ] Changes committed and pushed to git

## Support & Issues

For issues or questions:

1. Check the troubleshooting section above
2. Review logs: `docker-compose logs -f`
3. Verify `.env` file has correct `GOOGLE_API_KEY`
4. Test health endpoint: `curl http://localhost:8000/health`
5. Check Gemini API status: https://status.cloud.google.com/

## Recent Changes (v1.1)

- ✅ Migrated from OpenAI to Google Gemini API
- ✅ Implemented simple orchestration (bypasses complex LangGraph state)
- ✅ Fixed state management issues with LangGraph 0.0.50
- ✅ Added `convert_system_message_to_human=True` for Gemini compatibility
- ✅ Implemented rate limit retry logic
- ✅ Added Docker Compose orchestration
- ✅ Improved logging and debugging

## License

[Add your license here]

## Contributing

[Add contribution guidelines here]
