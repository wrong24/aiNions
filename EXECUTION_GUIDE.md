╔════════════════════════════════════════════════════════════════════════════════╗
║ NION ORCHESTRATION ENGINE - EXECUTION GUIDE ║
║ Everything You Need to Know to Run It ║
╚════════════════════════════════════════════════════════════════════════════════╝

📋 PRE-EXECUTION CHECKLIST
══════════════════════════════════════════════════════════════════════════════════

System Requirements:
☑ Windows/Linux/macOS with Python 3.11+
☑ OpenAI API Key (set OPENAI_API_KEY environment variable)
☑ 2GB RAM minimum (4GB+ recommended)
☑ 500MB disk space minimum
☑ Internet connection (for OpenAI API and pip packages)

Optional (for container/K8s):
☑ Docker Desktop installed (for docker-compose)
☑ kubectl + minikube/AKS/EKS (for Kubernetes)
☑ Redis (optional - system uses in-memory cache if unavailable)

🚀 QUICKEST START (60 seconds)
══════════════════════════════════════════════════════════════════════════════════

Windows PowerShell:
──────────────────

1. Set API Key:
   $env:OPENAI_API_KEY = "sk-your-api-key-here"

2. Install dependencies:
   pip install -r requirements.txt

3. Run test:
   python test_local.py

Expected output: NION ORCHESTRATION MAP + orchestration_result.json

🐍 DETAILED: LOCAL PYTHON EXECUTION (Recommended for Development)
══════════════════════════════════════════════════════════════════════════════════

Step 1: Navigate to Project Directory
────────────────────────────────────────
cd \aiNions

Step 2: Create Virtual Environment (Optional but Recommended)
────────────────────────────────────────────────────────────

Windows:
python -m venv venv
.\venv\Scripts\activate

Linux/macOS:
python3 -m venv venv
source venv/bin/activate

Step 3: Install Dependencies
────────────────────────────────────────

pip install -r requirements.txt

Expected packages:
✓ fastapi==0.104.1
✓ uvicorn==0.24.0
✓ pydantic==2.5.0
✓ langchain==0.1.10
✓ langchain-openai==0.0.8
✓ langgraph==0.0.40
✓ redis==5.0.1

Step 4: Set Environment Variables
────────────────────────────────────────

Option A: Command line
Windows:
$env:OPENAI_API_KEY = "sk-your-api-key-here"

Linux/macOS:
export OPENAI_API_KEY="sk-your-api-key-here"

Option B: Create .env file
Copy .env.template to .env
Edit .env and add your API key
(Note: Python will read .env via python-dotenv if installed)

Option C: Load from secrets manager
(Implement as needed for your infrastructure)

Step 5: Run Test (Local - No Server)
────────────────────────────────────────

python test_local.py

Expected output:
[INFO] Starting orchestration...
[L1] Created plan with 3 tasks
[L2_Tracking] Completed: 3 actions, 3 risks
[L2_Communication] Completed: 2 Q&A records
[Cross_Knowledge] Retrieved context for PRJ-ALPHA
[Evaluator] COMPLETED: 3/3 tasks successful

==================================================================================
NION ORCHESTRATION MAP
==================================================================================

MESSAGE METADATA
...

=== L1 PLAN ===
...

=== L2/L3 EXECUTION ===
...

Output file: orchestration_result.json

Step 6: Start FastAPI Server (Optional)
────────────────────────────────────────

python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload

Expected output:
INFO: Uvicorn running on http://0.0.0.0:8000
INFO: Application startup complete

Step 7: Test API Endpoints (In New Terminal)
────────────────────────────────────────────────

# Health check

curl http://localhost:8000/health

# Process message with NION MAP

curl -X POST http://localhost:8000/process/nion-map \
 -H "Content-Type: application/json" \
 -d '{
"message": "The customer demo went great! Add real-time notifications.",
"sender": "Sarah Chen",
"project_id": "PRJ-ALPHA"
}'

# Run API tests

python test_api.py

🐳 DOCKER EXECUTION (Recommended for Testing Full Stack)
══════════════════════════════════════════════════════════════════════════════════

Step 1: Build Docker Image
────────────────────────────

docker build -t nion-orchestrator:latest .

Output: Successfully tagged nion-orchestrator:latest

Step 2: Set Environment Variable
────────────────────────────────

Windows PowerShell:
$env:OPENAI_API_KEY = "sk-your-api-key-here"

Linux/macOS:
export OPENAI_API_KEY="sk-your-api-key-here"

Step 3: Run with Docker Compose
────────────────────────────────

docker-compose up --build

Expected output:
nion-redis-1 is healthy
nion-orchestrator-1 | INFO: Uvicorn running on http://0.0.0.0:8000
nion-orchestrator-1 | INFO: Application startup complete

Step 4: Test in New Terminal
────────────────────────────

docker-compose exec nion-app curl http://localhost:8000/health

Or from host (after port forwarding):
curl http://localhost:8000/health

Step 5: View Logs
─────────────────

docker-compose logs -f nion-app
docker-compose logs -f nion-redis

Step 6: Stop Services
─────────────────────

docker-compose down

To also remove volumes:
docker-compose down -v

☸️ KUBERNETES EXECUTION (Recommended for Production)
══════════════════════════════════════════════════════════════════════════════════

Prerequisites:

- kubectl installed and configured
- Access to Kubernetes cluster (minikube/AKS/EKS/GKE)
- Docker image built: docker build -t nion-orchestrator:latest .

Step 1: Set OpenAI API Key (Base64 Encoded)
─────────────────────────────────────────────

Windows PowerShell:
$apiKey = "sk-your-api-key-here"
  $bytes = [System.Text.Encoding]::UTF8.GetBytes($apiKey)
$encoded = [Convert]::ToBase64String($bytes)
Write-Host $encoded

Linux/macOS:
echo -n "sk-your-api-key-here" | base64

Copy the encoded key.

Step 2: Update k8s-deployment.yaml
──────────────────────────────────

Find the line:
api-key: c2stcHJvai1YWFhYWFhY... # PLACEHOLDER

Replace with:
api-key: <YOUR-ENCODED-KEY>

Step 3: Load Image into Minikube (if using minikube)
──────────────────────────────────────────────────────

minikube image load nion-orchestrator:latest

Or configure image pull from Docker Hub/ACR (production)

Step 4: Create Namespace & Deploy
──────────────────────────────────

kubectl create namespace nion-system # Usually created by manifest
kubectl apply -f k8s-deployment.yaml

Step 5: Verify Deployment
──────────────────────────

# Check pods

kubectl get pods -n nion-system
Expected:
nion-orchestrator-xxx 1/1 Running
redis-xxx 1/1 Running

# Check services

kubectl get svc -n nion-system
Expected:
nion-service LoadBalancer 10.x.x.x <EXTERNAL-IP> 80:30080/TCP
redis-service ClusterIP 10.x.x.x <none> 6379/TCP

# Check deployment

kubectl get deployment -n nion-system

# Check pod logs

kubectl logs -n nion-system -l app=nion -f

Step 6: Port Forward for Testing
────────────────────────────────

kubectl port-forward -n nion-system svc/nion-service 8000:80

In another terminal:
curl http://localhost:8000/health

Step 7: Test API
────────────────

curl -X POST http://localhost:8000/process/nion-map \
 -H "Content-Type: application/json" \
 -d '{
"message": "Feature request",
"sender": "User",
"project_id": "PRJ-ALPHA"
}'

Step 8: Monitor & Scale
───────────────────────

# View HPA status

kubectl get hpa -n nion-system

# Manual scaling

kubectl scale deployment nion-orchestrator -n nion-system --replicas=3

# Watch pods

kubectl get pods -n nion-system -w

# Check resource usage

kubectl top pods -n nion-system

Step 9: Cleanup
───────────────

# Delete deployment

kubectl delete namespace nion-system

# Or just individual resources

kubectl delete -f k8s-deployment.yaml

🧪 AUTOMATED SETUP (All-in-One)
══════════════════════════════════════════════════════════════════════════════════

Interactive Setup Script:
python setup.py

This will:

1. Check Python version (3.11+)
2. Check dependencies (pip, git)
3. Create virtual environment
4. Install all dependencies
5. Configure environment
6. Run local test
7. Optionally start FastAPI server

📊 EXPECTED OUTPUT EXAMPLES
══════════════════════════════════════════════════════════════════════════════════

NION ORCHESTRATION MAP Format:
──────────────────────────────

==================================================================================
NION ORCHESTRATION MAP
==================================================================================

MESSAGE METADATA
────────────────────────────────────────────────────────────────────────────────
Message ID: MSG-20241206-001
Sender: Sarah Chen
Project: PRJ-ALPHA
Timestamp: 2024-12-06T10:30:00Z
State ID: abc-123-xyz
Message: The customer demo went great! They loved it...

=== L1 PLAN ===
────────────────────────────────────────────────────────────────────────────────
[TASK-001] Domain: L2_Tracking
Task ID: PLAN-001
Description: Extract and track action items, risks, decisions
Priority: P1
Status: IN_PROGRESS

=== L2/L3 EXECUTION ===
────────────────────────────────────────────────────────────────────────────────
[L2_TRACKING_001] L2_Tracking
Status: SUCCESS
Duration: 2345.67ms
ACTION ITEMS (3):
• ACT-001: Implement real-time notifications
Owner: Engineering Team, Priority: HIGH
Due: 2025-01-15

=== EXECUTION SUMMARY ===
────────────────────────────────────────────────────────────────────────────────
Total Tasks Executed: 3
Successful: 3
Failed: 0
Overall Status: COMPLETED

==================================================================================

JSON Output Example:
──────────────────

{
"state_id": "abc-123-xyz",
"message_metadata": {
"message_id": "MSG-001",
"sender": "Sarah Chen",
"project_id": "PRJ-ALPHA"
},
"plan": [
{
"task_id": "PLAN-001",
"domain": "L2_Tracking",
"description": "Extract and track...",
"priority": 1,
"status": "IN_PROGRESS"
}
],
"execution_results": {
"L2_TRACKING_001": {
"task_id": "L2_TRACKING_001",
"task_type": "L2_Tracking",
"status": "SUCCESS",
"duration_ms": 2345.67,
"output": {
"action_items": [...],
"risks": [...],
"decisions": [...]
}
}
},
"logs": [...]
}

🛠️ TROUBLESHOOTING
══════════════════════════════════════════════════════════════════════════════════

Problem: "OPENAI_API_KEY not set" Error
─────────────────────────────────────────
Solution:

1. Verify API key is set: echo $env:OPENAI_API_KEY (Windows)
2. Check if using virtual environment: activate it first
3. Restart terminal/shell after setting env var
4. Use .env file approach if command-line fails

Problem: ModuleNotFoundError (langgraph, langchain, etc.)
──────────────────────────────────────────────────────────
Solution:

1. Verify installation: pip list | grep langchain
2. Reinstall: pip install -r requirements.txt --force-reinstall
3. Check Python version: python --version (must be 3.11+)
4. Use virtual environment: venv/Scripts/pip install -r requirements.txt

Problem: Port 8000 Already in Use
──────────────────────────────────
Solution:

1. Kill existing process on port 8000
2. Use different port: uvicorn app.main:app --port 8001
3. List processes: netstat -ano | findstr :8000 (Windows)

Problem: Redis Connection Error
────────────────────────────────
Solution:

1. System gracefully falls back to in-memory cache
2. No action required - application will work
3. Optional: Start Redis separately for caching
4. Docker Compose starts Redis automatically

Problem: Kubernetes Pod CrashLoopBackOff
──────────────────────────────────────────
Solution:

1. Check logs: kubectl logs pod-name -n nion-system
2. Verify secrets: kubectl get secrets -n nion-system
3. Check API key encoding: base64 -d <<< "your-encoded-key"
4. Verify image exists: kubectl describe pod pod-name -n nion-system

Problem: Docker Build Fails
────────────────────────────
Solution:

1. Check Docker daemon: docker --version
2. Build with detailed output: docker build --progress=plain -t nion:latest .
3. Ensure Python 3.11 base image is available
4. Check internet connection (pip install stage)

Problem: API Returns 500 Error
──────────────────────────────
Solution:

1. Check logs: kubectl logs or docker logs
2. Verify OPENAI_API_KEY is set
3. Check OpenAI API quota: https://platform.openai.com/account/billing/overview
4. Verify network connectivity to api.openai.com

⏱️ EXECUTION TIMING
══════════════════════════════════════════════════════════════════════════════════

First Run (with API calls):
L1 Planning: 2-5 seconds
L3 Extractors: 3-7 seconds
Cross-Knowledge: 0.1-0.5 seconds
─────────────────────────
Total: 5-12 seconds

Cached Run (Redis hit):
Everything: 0.5-2 seconds

Local Test:
Start to finish: 5-15 seconds (depends on API response time)

✅ VALIDATION CHECKLIST (After Execution)
══════════════════════════════════════════════════════════════════════════════════

✓ test_local.py produces NION MAP output
✓ orchestration_result.json is created with valid JSON
✓ FastAPI server starts without errors
✓ Health endpoint returns 200 OK
✓ /process endpoints accept POST requests
✓ All responses contain state_id and execution results
✓ Docker container builds successfully
✓ Docker Compose brings up Redis + App
✓ Kubernetes manifests apply without errors
✓ Pods reach Running state
✓ Services get proper IP addresses
✓ No CrashLoopBackOff or pending pods

🎯 SUCCESS CRITERIA
══════════════════════════════════════════════════════════════════════════════════

✅ NION ORCHESTRATION MAP displays:

- Message metadata with sender, project, timestamp
- L1 Plan with 2-3 tasks delegated to L2 domains
- L2/L3 Execution results with:
  • 2-3 action items extracted
  • 2-3 risks identified
  • 1+ decisions made
  • Q&A records generated
- Execution summary showing success

✅ All endpoints respond correctly:

- /health returns healthy status
- /process returns standard JSON response
- /process/nion-map returns NION MAP text
- /process/json returns detailed JSON

✅ Performance is acceptable:

- Total execution: < 15 seconds
- L1 planning: < 5 seconds
- L3 extraction: < 3 seconds each

✅ Logging is comprehensive:

- Shows L1 planning process
- Shows L2 domain execution
- Shows L3 worker results
- Shows cross-cutting operations

📚 DOCUMENTATION REFERENCE
══════════════════════════════════════════════════════════════════════════════════

For More Info, See:
README.md - Comprehensive setup & deployment guide
API_EXAMPLES.md - Complete API reference with examples
IMPLEMENTATION_SUMMARY.md - Technical architecture details
DELIVERY_SUMMARY.txt - Project deliverables overview

🎬 NEXT STEPS (After Successful Execution)
══════════════════════════════════════════════════════════════════════════════════

1. Test with different messages:

   - Try PRJ-BETA project
   - Test with different senders
   - Use different message types

2. Integrate with your systems:

   - Call /process/json from your application
   - Parse NION MAP for reporting
   - Hook into your deployment pipeline

3. Configure monitoring:

   - Set up log aggregation
   - Add metrics collection
   - Create alerts for failures

4. Deploy to production:

   - Use Kubernetes manifests
   - Configure RBAC and network policies
   - Set up GitOps for updates

5. Enhance functionality:
   - Add authentication (OAuth2)
   - Implement rate limiting
   - Add more L3 workers
   - Extend knowledge base

════════════════════════════════════════════════════════════════════════════════
Ready to execute? Start with: python test_local.py
════════════════════════════════════════════════════════════════════════════════
