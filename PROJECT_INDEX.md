# aiNions Project Index - Complete File Guide

## Project Location

```
.
```

## Directory Structure

```
aiNions/
├── app/                          # Core application (2,050+ LOC)
│   ├── __init__.py              # Package initialization
│   ├── main.py                  # FastAPI REST API server
│   ├── graph.py                 # LangGraph orchestration engine
│   ├── agents.py                # L3 worker agents + caching
│   ├── schemas.py               # Pydantic data models
│   └── formatter.py             # Output formatting logic
│
├── test_local.py                # Local integration test
├── test_api.py                  # API endpoint tests
├── setup.py                     # Interactive setup wizard
│
├── requirements.txt             # Python dependencies
├── Dockerfile                   # Docker image definition
├── docker-compose.yml           # Docker Compose configuration
├── k8s-deployment.yaml          # Kubernetes manifests
├── .env.template                # Environment variables template
│
├── README.md                    # Setup & deployment guide
├── START_HERE.md                # Quick start guide
├── EXECUTION_GUIDE.md           # Step-by-step execution
├── API_EXAMPLES.md              # API reference with examples
├── IMPLEMENTATION_SUMMARY.md    # Technical architecture
├── PROJECT_INDEX.md             # This file
│
└── logs/                        # Application logs directory
    └── (log files created at runtime)
```

## Core Application Files

### app/main.py (320 LOC)

**Purpose**: FastAPI REST API server

**Key Components**:

- Application initialization with lifespan management
- Health check endpoint (`/health`)
- Message processing endpoints (`/process`, `/process/nion-map`, `/process/json`)
- Input validation using Pydantic models
- Error handling and HTTP exception management
- CORS configuration
- Request logging

**Key Functions**:

- `get_graph()` - Lazy initialization of NionGraph
- `lifespan()` - Application startup/shutdown lifecycle
- `process_message()` - Main message processing endpoint
- `health_check()` - Service health verification

**When to Modify**:

- Add new endpoints
- Change response formats
- Modify timeout values
- Add authentication/authorization
- Update CORS settings

**Dependencies**: FastAPI, Uvicorn, Pydantic, LangChain

### app/graph.py (380 LOC)

**Purpose**: LangGraph orchestration engine with state management

**Key Classes**:

- `NionGraph` - Main orchestration engine

**Key Methods**:

- `_build_graph()` - Constructs StateGraph with conditional routing
- `_node_l1_orchestrator()` - L1 strategic planning (GPT-4o)
- `_node_l2_tracking()` - L2 tracking domain coordination
- `_node_l2_communication()` - L2 communication domain coordination
- `_node_cross_knowledge()` - Cross-cutting knowledge retrieval
- `_node_evaluator()` - Quality assessment and evaluation
- `_router_l1_to_l2()` - Conditional routing based on L1 plan
- `invoke()` - Synchronous graph execution
- `ainvoke()` - Asynchronous graph execution

**Graph Flow**:

1. Input → L1 Orchestrator (creates plan)
2. Router → Selects L2 domains based on L1 plan
3. Parallel execution → L2 Tracking, L2 Communication, Cross-Knowledge
4. L3 Workers → Called from L2 coordinators (isolated from L1)
5. Evaluator → Quality assessment
6. Formatter → Output generation

**When to Modify**:

- Add new L2 coordinator nodes
- Change routing logic
- Modify LLM models for L1
- Add new cross-cutting concerns
- Change execution order

**Architecture Constraint**: L1 cannot directly access or call L3 agents (enforced in code)

**Dependencies**: LangGraph, LangChain

### app/agents.py (450 LOC)

**Purpose**: L3 worker agents and cross-cutting concerns with caching

**Key Classes**:

- `L3Agents` - Worker agents for semantic extraction
- `CrossCuttingAgents` - Knowledge retrieval and evaluation
- `LLMConfig` - LLM model configuration

**L3 Agent Methods** (Called from L2 only):

- `extract_action_items(context: str) -> List[ActionItem]`
- `extract_risks(context: str) -> List[Risk]`
- `generate_qna(context: str) -> List[QnAPair]`

**Cross-Cutting Methods**:

- `retrieve_knowledge(project_id: str, context: str) -> Dict`
- `evaluate_output(results: Dict) -> Dict`

**Caching Infrastructure**:

- `@cache_result` decorator - Transparent caching with TTL
- `get_redis_client()` - Redis connection with fallback
- In-memory fallback cache with mock data
- 60-second TTL for Redis entries

**LLM Configuration**:

- L1: GPT-4o (2000 tokens, temperature 0.7)
- L3: GPT-3.5-turbo (1500 tokens, temperature 0.5)
- Retry logic with exponential backoff
- Timeout management (30 seconds default)

**When to Modify**:

- Add new L3 worker agents
- Change LLM models or parameters
- Modify system prompts
- Update extraction logic
- Change caching strategy
- Extend knowledge base

**Dependencies**: LangChain, Redis, Pydantic

### app/schemas.py (650 LOC)

**Purpose**: Pydantic data models for validation and type safety

**Core Models**:

- `InputMessage` - User message input validation
- `Task` - Execution task definition
- `ActionItem` - Action item from extraction
- `Risk` - Risk from extraction
- `Decision` - Decision from extraction
- `QnAPair` - Question-answer pair
- `L2TrackingOutput` - Tracking domain results
- `L2CommunicationOutput` - Communication domain results
- `ExecutionResult` - Execution metadata
- `CrossCuttingOutput` - Knowledge and evaluation results
- `OrchestrationState` - Complete state object flowing through graph

**Validation Features**:

- Field type checking
- Optional fields with defaults
- Enums for constrained values
- Custom validators where needed
- JSON schema generation

**When to Modify**:

- Add new extraction output types
- Change field validation rules
- Add new model fields
- Modify response structures
- Extend state object

**Dependencies**: Pydantic

### app/formatter.py (250 LOC)

**Purpose**: Convert OrchestrationState to human and machine-readable formats

**Key Classes**:

- `NionFormatter` - Output formatter

**Key Functions**:

- `generate_nion_map(state: OrchestrationState) -> str` - Plaintext NION Map
- `generate_json_output(state: OrchestrationState) -> Dict` - JSON output
- `_format_section()` - Section formatting helper
- `_format_execution_summary()` - Summary section generation

**Output Formats**:

1. **NION Map (Plaintext)**

   - Message metadata section
   - L1 plan section
   - L2/L3 execution results
   - Execution summary with timing
   - Professional ASCII formatting

2. **JSON Output**
   - Hierarchical structure
   - Complete execution metadata
   - Detailed timing information
   - Execution logs

**When to Modify**:

- Change output format or structure
- Add new output sections
- Modify plaintext layout
- Change JSON schema
- Add new fields to output

**Dependencies**: Pydantic

## Testing Files

### test_local.py

**Purpose**: Local integration test without FastAPI server

**What It Does**:

1. Initializes NionGraph
2. Creates test message
3. Processes through all layers (L1→L2→L3→Evaluator)
4. Generates NION Map output
5. Saves results to JSON file
6. Displays formatted output

**Run With**:

```powershell
python test_local.py
```

**Expected Output**:

- NION orchestration map
- orchestration_result.json file
- Success/error messages

**When to Use**:

- Quick validation without server
- Testing core logic changes
- Debugging orchestration flow
- Initial setup verification

### test_api.py

**Purpose**: Test all FastAPI endpoints

**What It Tests**:

1. Health check endpoint
2. /process endpoint (JSON)
3. /process/nion-map endpoint (plaintext)
4. /process/json endpoint (detailed JSON)
5. Error handling

**Run With** (requires server running):

```powershell
python test_api.py
```

**When to Use**:

- Validate API after deployment
- Test endpoint integration
- Verify response formats
- Check error handling

### setup.py

**Purpose**: Interactive environment setup wizard

**Features**:

1. Python version check (3.11+)
2. Dependency verification
3. Virtual environment creation
4. Environment configuration
5. Optional test execution
6. Optional server startup

**Run With**:

```powershell
python setup.py
```

## Configuration & Deployment Files

### requirements.txt

**Purpose**: Python package dependencies

**Packages**:

```
fastapi>=0.115.0         # REST API framework
uvicorn>=0.32.0          # ASGI server
pydantic>=2.9.0          # Data validation
pydantic-settings>=2.6.0 # Settings management
langchain>=0.3.7         # LLM framework
langchain-core>=0.3.15   # Core LLM utilities
langchain-google-genai>=2.0.1  # Gemini integration (if needed)
langgraph>=0.2.45        # Graph orchestration
redis>=5.2.0             # Redis client
python-dotenv>=1.0.1     # .env file support
```

**Install With**:

```powershell
pip install -r requirements.txt
```

### Dockerfile

**Purpose**: Docker image for containerization

**Build Stages**:

1. **Base Stage**: Python 3.11-slim with OS dependencies
2. **Builder Stage**: Install Python dependencies
3. **Final Stage**: Minimal runtime image (~400MB)

**Build With**:

```powershell
docker build -t nion-orchestrator:latest .
```

**Features**:

- Multi-stage build for optimization
- Health check included
- Non-root user (security)
- Logging configured
- Port 8000 exposed

### docker-compose.yml

**Purpose**: Local development with Redis + App

**Services**:

- `redis`: Cache service (Alpine image)
- `nion-app`: Application server

**Features**:

- Health checks for both services
- Named volumes for persistence
- Service discovery via DNS
- Logging configuration
- Network isolation

**Run With**:

```powershell
docker-compose up --build
```

### k8s-deployment.yaml

**Purpose**: Production Kubernetes deployment

**Resources** (11 total):

1. Namespace: nion-system
2. Redis Deployment (1 replica)
3. Redis Service (ClusterIP)
4. Application Deployment (2 replicas)
5. Application LoadBalancer Service
6. Application NodePort Service
7. ServiceAccount
8. ClusterRole (RBAC)
9. ClusterRoleBinding (RBAC)
10. ConfigMap (configuration)
11. Secret (API key)
12. HorizontalPodAutoscaler (2-5 replicas)
13. PodDisruptionBudget (HA)

**Deploy With**:

```powershell
kubectl apply -f k8s-deployment.yaml
```

### .env.template

**Purpose**: Environment variable template

**Variables**:

- `OPENAI_API_KEY` - OpenAI API key (required)
- `REDIS_HOST` - Redis hostname
- `REDIS_PORT` - Redis port
- `HOST` - FastAPI host
- `PORT` - FastAPI port
- `LOG_LEVEL` - Logging level

**Usage**: Copy to `.env` and fill in values

## Documentation Files

### README.md

**Content**:

- Project overview and architecture
- Quick start guide (3 options)
- API endpoints reference
- Docker deployment instructions
- Kubernetes deployment overview
- Implementation details
- Troubleshooting guide
- File structure
- Performance metrics

**Length**: ~500 lines

**When to Read**: First-time setup and comprehensive understanding

### START_HERE.md

**Content**:

- Quick project overview
- Key features summary
- Quick start (3 options)
- Common tasks
- Troubleshooting
- Documentation roadmap

**Length**: ~250 lines

**When to Read**: Quick overview before diving deeper

### EXECUTION_GUIDE.md

**Content**:

- Detailed step-by-step instructions
- 4 execution options (local, FastAPI, Docker, Kubernetes)
- Configuration details
- Monitoring and logging
- Performance monitoring
- Common configurations
- Best practices

**Length**: ~400 lines

**When to Read**: Before running the system in any environment

### API_EXAMPLES.md

**Content**:

- All 4 endpoints with detailed examples
- Request/response formats
- Error handling
- Status codes
- Common use cases
- Testing scripts
- Best practices

**Length**: ~350 lines

**When to Read**: Before integrating API into other systems

### IMPLEMENTATION_SUMMARY.md

**Content**:

- Technical architecture details
- Layer descriptions (L1, L2, L3)
- Data model reference
- LLM integration details
- Caching strategy
- Graph orchestration flow
- Performance characteristics
- Security considerations
- Error handling
- Testing strategy
- Extension points

**Length**: ~450 lines

**When to Read**: Deep technical understanding and customization

### PROJECT_INDEX.md

**Content**: This file - complete file guide and descriptions

**Length**: ~400 lines

**When to Read**: Understanding file organization and navigation

## Quick Navigation Guide

### I want to...

**Get started quickly**
→ Read START_HERE.md (5 min)

**Understand the architecture**
→ Read IMPLEMENTATION_SUMMARY.md (15 min)

**Run the system**
→ Read EXECUTION_GUIDE.md (10 min per option)

**Integrate API**
→ Read API_EXAMPLES.md (20 min)

**Deploy to production**
→ Review k8s-deployment.yaml
→ Read README.md deployment section

**Test locally**
→ Run: `python test_local.py`
→ Check EXECUTION_GUIDE.md "Option 1"

**Modify code**
→ Read IMPLEMENTATION_SUMMARY.md
→ Check specific file descriptions below
→ Review existing code

**Add new features**
→ IMPLEMENTATION_SUMMARY.md "Extension Points"
→ Modify appropriate module (agents.py, graph.py, etc.)
→ Update schemas.py for new models
→ Update formatter.py for new outputs

**Troubleshoot issues**
→ Check EXECUTION_GUIDE.md troubleshooting tables
→ Check EXECUTION_GUIDE.md logs section
→ Check API_EXAMPLES.md error handling

## File Size & Performance

| File             | Size          | Purpose           |
| ---------------- | ------------- | ----------------- |
| app/main.py      | 320 LOC       | FastAPI server    |
| app/graph.py     | 380 LOC       | LangGraph engine  |
| app/agents.py    | 450 LOC       | Worker agents     |
| app/schemas.py   | 650 LOC       | Data models       |
| app/formatter.py | 250 LOC       | Output formatting |
| **Total Core**   | **2,050 LOC** | **Application**   |

## Development Workflow

1. **Setup** (first time):

   - Clone or download repository
   - Read START_HERE.md
   - Run `python setup.py` OR manually setup venv

2. **Local Development**:

   - Edit code in `app/` directory
   - Run `python test_local.py` to validate
   - Fix issues based on output

3. **API Testing**:

   - Start server: `python -m uvicorn app.main:app --port 8000`
   - Run `python test_api.py`
   - Verify all endpoints work

4. **Docker Testing**:

   - Create .env file with API key
   - Run `docker-compose up --build`
   - Test with curl or test_api.py

5. **Kubernetes Deployment**:

   - Review and update k8s-deployment.yaml
   - Set API key in Secret
   - Run `kubectl apply -f k8s-deployment.yaml`
   - Monitor with kubectl logs/describe

6. **Production**:
   - Ensure all tests pass
   - Document any customizations
   - Monitor performance metrics
   - Implement monitoring/alerting

## Support & References

- **LangGraph Docs**: https://langchain-ai.github.io/langgraph/
- **LangChain Docs**: https://docs.langchain.com/
- **FastAPI Docs**: https://fastapi.tiangolo.com/
- **OpenAI API**: https://platform.openai.com/docs/
- **Docker Docs**: https://docs.docker.com/
- **Kubernetes Docs**: https://kubernetes.io/docs/

---

**Last Updated**: December 7, 2025
**Project Version**: 1.0
**Maintained By**: aiNions Development Team
