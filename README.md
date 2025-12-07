# aiNion Orchestration Engine - Build & Deployment Guide

## Architecture Overview

The aiNion Orchestration Engine is a hierarchical AI orchestration system built with:

- **LangGraph**: Stateful graph orchestration with LLM agents
- **LangChain + Google Gemini**: LLM interface for L1 planning and L3 extraction (free tier)
- **FastAPI**: REST API for message processing
- **Redis**: Distributed caching for knowledge retrieval
- **Docker**: Containerization with multi-stage builds

### 3-Layer Architecture

```
L1: Orchestrator (Gemini 2.0 Flash)
    ↓
    Parses message → Creates delegation plan
    ↓
L2: Domain Coordinators
    ├── L2_Tracking (action items, risks, decisions)
    ├── L2_Communication (Q&A, reporting)
    └── Cross_Knowledge (knowledge retrieval with caching)
    ↓
L3: Worker Agents (Gemini 2.0 Flash for efficiency)
    ├── action_item_extractor
    ├── risk_extractor
    └── qna_generator
```

## Prerequisites

- Python 3.11+
- Docker & Docker Compose
- Google Gemini API Key (free tier at https://ai.google.dev)
- Redis (optional - uses in-memory cache if Redis is unavailable)

## Quick Start

### Using Docker Compose (Recommended)

```bash
# Navigate to project directory
cd \aiNions

# Create .env file with your Gemini API key
echo "GOOGLE_API_KEY=your_actual_gemini_api_key_here" > .env

# Build and run containers
docker-compose build --no-cache
docker-compose up -d

# Check health
curl http://localhost:8000/health

# Process a message
curl -X POST http://localhost:8000/process/ainion-map \
  -H "Content-Type: application/json" \
  -d '{
    "message": "The customer demo went great!",
    "sender": "Sarah Chen",
    "project_id": "PRJ-ALPHA"
  }'
```

## Local Development

### 1. Setup Python Environment

```bash
# Navigate to project directory
cd \aiNions

# Create virtual environment
python -m venv venv
.\venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Set Environment Variables

```bash
# PowerShell
$env:GOOGLE_API_KEY = "your_actual_gemini_api_key_here"

# Or create .env file in project root
echo "GOOGLE_API_KEY=your_actual_gemini_api_key_here" > .env
```

### 3. Run FastAPI Server

```bash
# Start Redis (if available) in background
redis-server

# In a new terminal, start FastAPI
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

### 4. Test API Endpoints

```bash
# In another terminal
python test_api.py
```

Or manually:

### 4. Test API Endpoints

```bash
# Health check
curl http://localhost:8000/health

# Process message (returns aiNion Orchestration Map in plaintext)
curl -X POST http://localhost:8000/process/ainion-map \
  -H "Content-Type: application/json" \
  -d '{
    "message": "The customer demo went great!",
    "sender": "Sarah Chen",
    "project_id": "PRJ-ALPHA"
  }'

# Get simple JSON response
curl -X POST http://localhost:8000/process \
  -H "Content-Type: application/json" \
  -d '{
    "message": "The customer demo went great!",
    "sender": "Sarah Chen",
    "project_id": "PRJ-ALPHA"
  }'
```

## Docker Deployment

### Build and Run with Docker Compose

```bash
# Build containers
docker-compose build --no-cache

# Start services (Redis + FastAPI)
docker-compose up -d

# View logs
docker-compose logs -f ainion-orchestrator

# Stop services
docker-compose down
```

### Environment Variables in Docker

Create a `.env` file in the project root:

```bash
GOOGLE_API_KEY=your_actual_gemini_api_key_here
```

This will be automatically loaded by docker-compose.

### Build Docker Image Only

```bash
docker build -t ainion-orchestrator:latest .

# Run container
docker run -e GOOGLE_API_KEY=your_key \
  -p 8000:8000 \
  --name ainion-app \
  ainion-orchestrator:latest
```

## Implementation Details

### Simple Orchestration Mode

The system uses a simplified orchestration approach that bypasses complex LangGraph state machinery:

1. **L1_Orchestrator**: Analyzes message and creates task plan
2. **L2_Tracking**: Extracts action items, risks, and decisions
3. **L2_Communication**: Generates Q&A records
4. **Cross_Knowledge**: Retrieves knowledge context from Redis cache
5. **Evaluator**: Assesses execution results

This sequential execution model provides better reliability and easier debugging compared to state machine approaches.

### Gemini API Integration

- Uses `ChatGoogleGenerativeAI` from `langchain-google-genai`
- Configured with `convert_system_message_to_human=True` for compatibility
- Model: `gemini-2.0-flash` (fast and efficient)
- Free tier quota limits: ~60 requests/minute per user

### API Endpoints

| Endpoint              | Method | Description                        | Response   |
| --------------------- | ------ | ---------------------------------- | ---------- |
| `/health`             | GET    | Service health check               | JSON       |
| `/process`            | POST   | Process message, return stats      | JSON       |
| `/process/ainion-map` | POST   | Process message, return aiNion map | Plain Text |

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
