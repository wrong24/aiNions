# Nion Orchestration Engine - Build & Deployment Guide

## Architecture Overview

The Nion Orchestration Engine is a hierarchical AI orchestration system built with:

- **LangGraph**: Stateful graph orchestration with LLM agents
- **LangChain + OpenAI**: LLM interface for L1 planning and L3 extraction
- **FastAPI**: REST API for message processing
- **Redis**: Distributed caching for knowledge retrieval
- **Kubernetes**: Container orchestration and scaling

### 3-Layer Architecture

```
L1: Orchestrator (gpt-4o)
    ↓
    Parses message → Creates delegation plan
    ↓
L2: Domain Coordinators
    ├── L2_Tracking (action items, risks, decisions)
    ├── L2_Communication (Q&A, reporting)
    └── Cross_Knowledge (knowledge retrieval with caching)
    ↓
L3: Worker Agents (gpt-3.5-turbo for cost)
    ├── action_item_extractor
    ├── risk_extractor
    └── qna_generator
```

## Prerequisites

- Python 3.11+
- Docker & Docker Compose
- Kubernetes cluster (or minikube for testing)
- OpenAI API Key (set `OPENAI_API_KEY` environment variable)
- Redis (optional - uses in-memory cache if Redis is unavailable)

## Local Development

### 1. Setup Python Environment

```bash
# Navigate to project directory
cd c:\Users\jainp\OneDrive\Desktop\aiNions

# Create virtual environment
python -m venv venv
.\venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Set Environment Variables

```bash
# PowerShell
$env:OPENAI_API_KEY = "sk-your-api-key-here"

# Or create .env file in project root
echo "OPENAI_API_KEY=sk-your-api-key-here" > .env
```

### 3. Run Local Test (Without Server)

```bash
python test_local.py
```

This will:

- Initialize the LangGraph
- Process the test message through all layers
- Generate the NION ORCHESTRATION MAP
- Save results to `orchestration_result.json`

### 4. Run FastAPI Server

```bash
# Start Redis (if available) in background
redis-server

# In a new terminal, start FastAPI
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

### 5. Test API Endpoints

```bash
# In another terminal
python test_api.py
```

Or manually:

```bash
# Health check
curl http://localhost:8000/health

# Process message (JSON response)
curl -X POST http://localhost:8000/process \
  -H "Content-Type: application/json" \
  -d '{
    "message": "The customer demo went great!",
    "sender": "Sarah Chen",
    "project_id": "PRJ-ALPHA"
  }'

# Get NION MAP (plaintext)
curl -X POST http://localhost:8000/process/nion-map \
  -H "Content-Type: application/json" \
  -d '{
    "message": "The customer demo went great!",
    "sender": "Sarah Chen",
    "project_id": "PRJ-ALPHA"
  }'

# Get detailed JSON
curl -X POST http://localhost:8000/process/json \
  -H "Content-Type: application/json" \
  -d '{
    "message": "The customer demo went great!",
    "sender": "Sarah Chen",
    "project_id": "PRJ-ALPHA"
  }'
```

## Docker Deployment

### Build Docker Image

```bash
docker build -t nion-orchestrator:latest .
```

### Run Container

```bash
# Set API key
set OPENAI_API_KEY=sk-your-api-key-here

# Run with Redis
docker run -e OPENAI_API_KEY=%OPENAI_API_KEY% \
  -p 8000:8000 \
  --name nion-app \
  nion-orchestrator:latest

# Or with Docker Compose
docker-compose up
```

Create `docker-compose.yml`:

```yaml
version: "3.8"

services:
  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"
    healthcheck:
      test: ["CMD", "redis-cli", "ping"]
      interval: 5s
      timeout: 3s
      retries: 5

  nion:
    build: .
    ports:
      - "8000:8000"
    environment:
      - OPENAI_API_KEY=${OPENAI_API_KEY}
      - REDIS_HOST=redis
      - REDIS_PORT=6379
    depends_on:
      redis:
        condition: service_healthy
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
      interval: 30s
      timeout: 10s
      retries: 3
```

## Kubernetes Deployment

### Prerequisites

```bash
# Create namespace
kubectl create namespace nion-system

# Set OpenAI API Key
$env:OPENAI_API_KEY = "sk-your-api-key-here"
$encodedKey = [System.Convert]::ToBase64String([System.Text.Encoding]::UTF8.GetBytes($env:OPENAI_API_KEY))
Write-Host $encodedKey  # Copy this value
```

### Update Secret in k8s-deployment.yaml

Replace the placeholder in the `openai-secrets` Secret:

```yaml
apiVersion: v1
kind: Secret
metadata:
  name: openai-secrets
  namespace: nion-system
type: Opaque
data:
  api-key: <BASE64_ENCODED_KEY> # Replace with your encoded key
```

### Deploy to Kubernetes

```bash
# Load image into minikube (if using minikube)
minikube image load nion-orchestrator:latest

# Apply deployment
kubectl apply -f k8s-deployment.yaml

# Verify deployment
kubectl get pods -n nion-system
kubectl get svc -n nion-system

# Check logs
kubectl logs -n nion-system -l app=nion -f

# Port forward for testing
kubectl port-forward -n nion-system svc/nion-service 8000:80
```

### Scale Deployment

```bash
# Manually scale
kubectl scale deployment nion-orchestrator -n nion-system --replicas=3

# Or let HPA auto-scale based on CPU/Memory
kubectl get hpa -n nion-system
```

## File Structure

```
c:\Users\jainp\OneDrive\Desktop\aiNions\
├── app/
│   ├── __init__.py
│   ├── main.py                 # FastAPI application
│   ├── schemas.py              # Pydantic models
│   ├── agents.py               # L3 workers + Cross-cutting agents
│   ├── graph.py                # LangGraph orchestration
│   └── formatter.py            # Output formatting
├── requirements.txt            # Python dependencies
├── Dockerfile                  # Multi-stage Docker build
├── docker-compose.yml          # Docker Compose (create if needed)
├── k8s-deployment.yaml         # Kubernetes manifests
├── test_local.py               # Local testing script
├── test_api.py                 # API testing script
├── README.md                   # This file
└── orchestration_result.json   # Sample output (generated)
```

## NION Orchestration Map Format

The formatter generates output like:

```
================================================================================
NION ORCHESTRATION MAP
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

| Variable       | Default   | Description                   |
| -------------- | --------- | ----------------------------- |
| OPENAI_API_KEY | Required  | OpenAI API key for LLM access |
| REDIS_HOST     | localhost | Redis server hostname         |
| REDIS_PORT     | 6379      | Redis server port             |
| HOST           | 0.0.0.0   | FastAPI host binding          |
| PORT           | 8000      | FastAPI port                  |

## Troubleshooting

### Redis Connection Error

The system gracefully falls back to in-memory caching if Redis is unavailable.

### OpenAI API Errors

Check that:

- `OPENAI_API_KEY` is correctly set
- API key has sufficient quota
- Network connectivity to OpenAI API

### LangGraph Issues

Enable debug logging:

```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

### Kubernetes Pod Issues

```bash
# Check pod status
kubectl describe pod nion-orchestrator-xxx -n nion-system

# View logs
kubectl logs pod nion-orchestrator-xxx -n nion-system

# Exec into pod
kubectl exec -it nion-orchestrator-xxx -n nion-system -- /bin/bash
```

## Performance Considerations

- **L1 (Orchestrator)**: Uses gpt-4o for planning (~2-5s)
- **L3 Workers**: Use gpt-3.5-turbo for cost efficiency
- **Redis Caching**: Knowledge retrieval cached for 60 seconds
- **Auto-scaling**: HPA configured to scale 2-5 replicas based on CPU/Memory

## Security

- API Key injected via Kubernetes Secrets
- No credentials in code or Docker images
- Service Account with minimal RBAC
- Network policies should be configured per environment

## Monitoring & Logging

All components log to stdout/stderr:

```bash
# View real-time logs
kubectl logs -n nion-system -l app=nion -f --all-containers=true

# Aggregate logs (requires logging stack like ELK)
# See Kubernetes logging documentation
```

## Support

For issues or questions, please check:

1. Logs with `kubectl logs` or local terminal
2. Health endpoint: `curl http://localhost:8000/health`
3. Verify environment variables are set
4. Check OpenAI API quota and status
