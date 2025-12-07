# Execution Guide - Step-by-Step Instructions

## Overview

This guide provides detailed instructions for running the aiNions Orchestration Engine in different environments: local development, FastAPI server mode, Docker Compose, and Kubernetes production deployment.

## Prerequisites

- Python 3.11 or higher
- pip package manager
- (Optional) Docker and Docker Compose for containerized environments
- (Optional) kubectl for Kubernetes deployment
- OpenAI API key from https://platform.openai.com/api-keys

## Environment Setup

### 1. Set API Key

Choose one of these methods:

**Method A: Environment Variable (PowerShell)**

```powershell
$env:OPENAI_API_KEY = "sk-your-actual-api-key-here"
```

**Method B: Create .env File**

```powershell
@"
OPENAI_API_KEY=sk-your-actual-api-key-here
REDIS_HOST=localhost
REDIS_PORT=6379
"@ | Out-File -FilePath .env -Encoding UTF8
```

**Method C: Export File (.env.template)**
Copy `.env.template` to `.env` and fill in your API key.

### 2. Verify Python Version

```powershell
python --version
# Output should be Python 3.11.x or higher
```

## Option 1: Local Integration Test (Fastest)

Use this for quick validation without running a server.

### Steps

```powershell
# 1. Navigate to project directory
cd c:\Users\jainp\OneDrive\Desktop\aiNions

# 2. Create virtual environment
python -m venv venv

# 3. Activate virtual environment
.\venv\Scripts\activate

# 4. Install dependencies
pip install -r requirements.txt

# 5. Set API key
$env:OPENAI_API_KEY = "sk-your-actual-api-key-here"

# 6. Run local test
python test_local.py
```

### Expected Output

```
Initializing NionGraph...
Processing message: [Your message content]
═══════════════════════════════════════════════
NION ORCHESTRATION MAP
═══════════════════════════════════════════════
[Plaintext orchestration results]
[Action items, risks, Q&A pairs]
═══════════════════════════════════════════════
Test completed successfully!
```

### Troubleshooting Local Test

| Issue                                              | Solution                                        |
| -------------------------------------------------- | ----------------------------------------------- |
| `ModuleNotFoundError: No module named 'langchain'` | Run `pip install -r requirements.txt`           |
| `OPENAI_API_KEY not found`                         | Set environment variable before running         |
| `Connection timeout`                               | Check OpenAI API key validity and network       |
| `RateLimitError`                                   | Wait a moment and retry, or upgrade OpenAI plan |

## Option 2: FastAPI Server Mode

Run the system as a REST API server for endpoint testing and integration.

### Steps

**Terminal 1: Start Server**

```powershell
cd c:\Users\jainp\OneDrive\Desktop\aiNions
.\venv\Scripts\activate
$env:OPENAI_API_KEY = "sk-your-actual-api-key-here"

python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

**Expected output:**

```
INFO:     Uvicorn running on http://0.0.0.0:8000 (Press CTRL+C to quit)
INFO:     Nion Orchestration Engine starting...
INFO:     Graph initialized and ready for requests
```

**Terminal 2: Test API**

```powershell
# In another terminal, run the test suite
python test_api.py
```

### Manual API Testing

```powershell
# Health check
curl http://localhost:8000/health

# Process message (JSON response)
$body = @{
    message = "The customer demo went great!"
    sender = "Sarah Chen"
    project_id = "PRJ-ALPHA"
} | ConvertTo-Json

curl -X POST http://localhost:8000/process `
  -H "Content-Type: application/json" `
  -d $body

# Get NION Map (plaintext)
curl -X POST http://localhost:8000/process/nion-map `
  -H "Content-Type: application/json" `
  -d $body

# Get detailed JSON
curl -X POST http://localhost:8000/process/json `
  -H "Content-Type: application/json" `
  -d $body
```

### Server Troubleshooting

| Issue                       | Solution                                     |
| --------------------------- | -------------------------------------------- |
| `Port 8000 already in use`  | Use `--port 8001` flag or stop other service |
| `ModuleNotFoundError`       | Ensure virtual environment is activated      |
| `Connection refused`        | Verify server is running (check Terminal 1)  |
| `400 Bad Request`           | Validate JSON payload format                 |
| `500 Internal Server Error` | Check server logs in Terminal 1              |

### Viewing Server Logs

```powershell
# Logs appear in Terminal 1 where server started
# Look for ERROR, WARNING levels for issues
# INFO lines show request processing
```

## Option 3: Docker Compose (Recommended for Production Testing)

Deploy with Redis cache in containerized environment.

### Prerequisites

- Docker Desktop installed
- No services running on ports 6379 (Redis) or 8000 (App)

### Steps

```powershell
# 1. Navigate to project
cd c:\Users\jainp\OneDrive\Desktop\aiNions

# 2. Create .env file
@"
OPENAI_API_KEY=sk-your-actual-api-key-here
REDIS_HOST=redis
REDIS_PORT=6379
HOST=0.0.0.0
PORT=8000
"@ | Out-File -FilePath .env -Encoding UTF8

# 3. Build images
docker-compose build --no-cache

# 4. Start services
docker-compose up -d

# 5. Verify services are running
docker-compose ps
```

### Testing Docker Compose

```powershell
# Check health
curl http://localhost:8000/health

# View logs
docker-compose logs -f nion-app

# Test API (same as FastAPI mode)
$body = @{
    message = "The customer demo went great!"
    sender = "Sarah Chen"
    project_id = "PRJ-ALPHA"
} | ConvertTo-Json

curl -X POST http://localhost:8000/process/nion-map `
  -H "Content-Type: application/json" `
  -d $body
```

### Stopping Docker Compose

```powershell
# Stop all services
docker-compose down

# Stop and remove volumes
docker-compose down -v

# View exit logs before cleanup
docker-compose logs
```

### Docker Compose Troubleshooting

| Issue                    | Solution                                                            |
| ------------------------ | ------------------------------------------------------------------- |
| `Port 8000 in use`       | Run `docker-compose down` first                                     |
| `Connection refused`     | Wait 10-15 seconds for services to start, check `docker-compose ps` |
| `Redis connection error` | Normal - Redis may not be ready yet, server uses in-memory fallback |
| `Image build fails`      | Run `docker-compose build --no-cache` and check Docker logs         |
| `Permission denied`      | Run PowerShell as Administrator                                     |

## Option 4: Kubernetes Deployment (Production)

Deploy to Kubernetes cluster for production-scale testing.

### Prerequisites

- Kubernetes cluster (local k3d, cloud provider, etc.)
- kubectl CLI installed and configured
- Docker image pushed to registry (or local Docker available)

### Steps

```powershell
# 1. Navigate to project
cd c:\Users\jainp\OneDrive\Desktop\aiNions

# 2. Create namespace and secret
kubectl create namespace nion-system

# Create secret with API key (base64 encoded)
$apiKey = [Convert]::ToBase64String([Text.Encoding]::UTF8.GetBytes("sk-your-actual-api-key-here"))
$secretManifest = @"
apiVersion: v1
kind: Secret
metadata:
  name: openai-secret
  namespace: nion-system
type: Opaque
data:
  api-key: $apiKey
"@
$secretManifest | kubectl apply -f -

# 3. Apply deployment manifests
kubectl apply -f k8s-deployment.yaml

# 4. Monitor deployment
kubectl get pods -n nion-system -w

# 5. Wait for pods to be ready (Ready: 1/1)
```

### Testing Kubernetes Deployment

```powershell
# Port forward to local machine
kubectl port-forward -n nion-system svc/nion-app 8000:8000

# In another terminal, test API
curl http://localhost:8000/health

# View logs
kubectl logs -n nion-system -l app=nion-orchestrator

# View all resources
kubectl get all -n nion-system
```

### Scaling in Kubernetes

```powershell
# Manual scaling (overrides HPA)
kubectl scale deployment nion-orchestrator -n nion-system --replicas=3

# Monitor replica status
kubectl get pods -n nion-system

# Check HorizontalPodAutoscaler status
kubectl get hpa -n nion-system
```

### Kubernetes Troubleshooting

| Issue                | Solution                                                  |
| -------------------- | --------------------------------------------------------- |
| `ImagePullBackOff`   | Image not found in registry; check image name in manifest |
| `CrashLoopBackOff`   | Pod crashed; check logs with `kubectl logs`               |
| `Pending` state      | Insufficient resources; check `kubectl describe pod`      |
| `Connection refused` | Port-forward may not be active; run command again         |
| `Secret not found`   | Create secret first with proper base64 encoding           |

### Cleanup Kubernetes

```powershell
# Delete entire deployment
kubectl delete namespace nion-system

# Or delete specific resources
kubectl delete -f k8s-deployment.yaml -n nion-system
```

## Monitoring and Logs

### Local Logs

Check console output where process is running (test_local.py or uvicorn server).

### Docker Logs

```powershell
# Real-time logs from application
docker-compose logs -f nion-app

# Last 100 lines
docker-compose logs --tail=100 nion-app

# Logs from Redis
docker-compose logs -f redis
```

### Kubernetes Logs

```powershell
# Current pod logs
kubectl logs -n nion-system pod-name

# Follow logs (tail -f)
kubectl logs -n nion-system -f pod-name

# All pod logs for app
kubectl logs -n nion-system -l app=nion-orchestrator

# Previous pod logs (after crash)
kubectl logs -n nion-system pod-name --previous
```

## Performance Monitoring

### Measure Execution Time

```powershell
# Using test_api.py output
# Look for timing_ms field in response

# Manual timing
Measure-Command { python test_local.py }

# Docker timing
time docker-compose run nion-app python test_local.py
```

### Resource Usage

```powershell
# Docker resource stats
docker stats

# Kubernetes resource usage
kubectl top node -n nion-system
kubectl top pod -n nion-system
```

## Common Configuration

### Adjust Timeout Values

Edit `app/agents.py`:

```python
DEFAULT_TIMEOUT = 30  # seconds
RETRY_ATTEMPTS = 3
RETRY_DELAY = 1  # seconds
```

### Change Redis Configuration

In `.env`:

```
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_TTL=60
```

### Adjust Model Parameters

Edit `app/agents.py`:

```python
# L1 Model parameters
temperature=0.7  # 0-2, higher = more creative
max_tokens=2000

# L3 Model parameters
temperature=0.5
max_tokens=1500
```

## Best Practices

1. **Always test locally first** before Docker or Kubernetes
2. **Use .env files** for sensitive data, never commit API keys
3. **Monitor logs** for errors and warnings during testing
4. **Validate output** against expected NION Map format
5. **Test error cases** like invalid API keys or network failures
6. **Use health checks** to verify service readiness
7. **Implement retries** for transient failures
8. **Document custom changes** for team reference

## Next Steps

After successful execution:

1. Read **API_EXAMPLES.md** for integration patterns
2. Explore **PROJECT_INDEX.md** for code organization
3. Review **README.md** for deployment options
4. Check **IMPLEMENTATION_SUMMARY.md** for technical details

---

For additional help, see the troubleshooting sections in each execution option or contact your team lead.
