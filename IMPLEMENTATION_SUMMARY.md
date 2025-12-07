# aiNions Implementation Summary - Technical Architecture

## System Overview

The aiNions Orchestration Engine is built on a 3-layer hierarchical architecture using LangGraph for state management and conditional routing. The system processes messages through strategic planning (L1), domain coordination (L2), and semantic extraction (L3) layers.

## Core Architecture

### Layer 1: Orchestrator (Strategic Planning)

**Module**: `app.graph.NionGraph._node_l1_orchestrator()`  
**LLM**: GPT-4o  
**Responsibility**: Analyze message intent and create delegation plan

- Receives user message with metadata (sender, project_id)
- Analyzes content and determines required tasks
- Creates delegation plan routing to appropriate L2 domains
- Enforced isolation: Cannot directly access or call L3 agents
- Uses system prompt to enforce delegation-only behavior

### Layer 2: Coordinators (Domain Execution)

#### L2 Tracking Coordinator

**Module**: `app.graph.NionGraph._node_l2_tracking()`

- Coordinates L3 worker agents for task extraction:
  - `extract_action_items()` - Identifies actionable tasks
  - `extract_risks()` - Detects potential risks
  - `generate_qna()` - Creates documentation pairs

#### L2 Communication Coordinator

**Module**: `app.graph.NionGraph._node_l2_communication()`

- Handles communication-related tasks
- Coordinates with L3 workers for communication analysis
- Generates Q&A pairs for documentation

#### Cross-Cutting Layer

**Module**: `app.graph.NionGraph._node_cross_knowledge()`

- Knowledge retrieval: Fetches contextual information from cache
- Output evaluation: Assesses quality of extracted information
- Available to all layers (L1 and L2)

### Layer 3: Worker Agents (Semantic Extraction)

**Module**: `app.agents.L3Agents`  
**LLM**: GPT-3.5-turbo  
**Responsibility**: Perform fine-grained semantic extraction

All L3 agents are isolated from L1 and only callable from L2:

```python
class L3Agents:
    def extract_action_items(context: str) -> List[ActionItem]
    def extract_risks(context: str) -> List[Risk]
    def generate_qna(context: str) -> List[QnAPair]
```

### Evaluator Node

**Module**: `app.graph.NionGraph._node_evaluator()`

- Assesses execution quality
- Computes confidence scores
- Generates audit logs

## Data Models

**Module**: `app.schemas`

### Core Message Types

```python
class InputMessage(BaseModel):
    message: str           # User message content
    sender: str           # Message sender name
    project_id: str       # Project identifier

class OrchestrationState(BaseModel):
    input_message: InputMessage
    l1_plan: str         # L1 planning output
    l2_results: Dict     # L2 execution results
    evaluator_output: Dict
    execution_logs: List[str]
```

### Extraction Output Models

```python
class ActionItem(BaseModel):
    action: str
    priority: str        # HIGH, MEDIUM, LOW
    assignee: Optional[str]

class Risk(BaseModel):
    risk_description: str
    severity: str        # CRITICAL, HIGH, MEDIUM, LOW
    mitigation_strategy: str

class QnAPair(BaseModel):
    question: str
    answer: str
```

## LLM Integration

### Configuration

**Module**: `app.agents.LLMConfig`

```python
# L1 Orchestrator
ChatOpenAI(
    model="gpt-4o",
    temperature=0.7,
    max_tokens=2000
)

# L3 Workers
ChatOpenAI(
    model="gpt-3.5-turbo",
    temperature=0.5,
    max_tokens=1500
)
```

### API Integration

- Uses LangChain `ChatOpenAI` wrapper
- Environment variable: `OPENAI_API_KEY`
- Structured output validation via Pydantic models
- Error handling with retry logic
- Timeout management: 30-second default

## Caching Strategy

**Module**: `app.agents.cache_result decorator` and `CrossCuttingAgents.retrieve_knowledge()`

### Primary Cache: Redis

- **Connection**: Configurable via `REDIS_HOST`, `REDIS_PORT`
- **TTL**: 60 seconds for knowledge entries
- **Format**: JSON-serialized data

### Fallback: In-Memory Cache

- Automatic fallback if Redis unavailable
- Mock knowledge base provided
- No loss of functionality, performance may degrade

### Implementation

```python
@cache_result(ttl=60)
def retrieve_knowledge(project_id: str, context: str):
    # Redis lookup
    # Fallback to in-memory mock data
    # Return contextual knowledge
```

## Graph Orchestration

**Module**: `app.graph.NionGraph`

### State Flow

```
Input Message
       ↓
  L1 Orchestrator (gpt-4o)
  Creates delegation plan
       ↓
  Router: Conditional routing based on L1 plan
       ├─→ L2 Tracking
       ├─→ L2 Communication
       └─→ Cross-Knowledge
           ↓
  L3 Workers (gpt-3.5-turbo)
  Parallel execution of extraction tasks
           ↓
  Evaluator
  Quality assessment & logging
           ↓
  Formatter
  Convert to output format (plaintext or JSON)
```

### Conditional Routing

Router function analyzes L1 plan and determines:

- Which L2 coordinators to activate
- Execution order if sequential needed
- Cross-cutting concern involvement

## Output Formatting

**Module**: `app.formatter.NionFormatter`

### NION Orchestration Map (Plaintext)

```
═══════════════════════════════════════════════════
NION ORCHESTRATION MAP
═══════════════════════════════════════════════════

MESSAGE METADATA
─────────────────────────────────────────────────
Sender: [Sender Name]
Project: [Project ID]
Timestamp: [ISO 8601 Timestamp]

L1 PLAN
─────────────────────────────────────────────────
[Strategic planning output from GPT-4o]

L2/L3 EXECUTION RESULTS
─────────────────────────────────────────────────
[Results from all L2 coordinators and L3 workers]

EXECUTION SUMMARY
─────────────────────────────────────────────────
Success: [Boolean]
Duration: [Milliseconds]
Logs: [Audit trail]
```

### JSON Output

Hierarchical structure with:

- Message metadata
- L1 plan in text
- L2 results (tracking, communication)
- Cross-cutting results (knowledge, evaluation)
- Execution metrics

## API Layer

**Module**: `app.main.FastAPI`

### Endpoints

| Endpoint            | Method | Input        | Output                 |
| ------------------- | ------ | ------------ | ---------------------- |
| `/health`           | GET    | -            | Health status JSON     |
| `/process`          | POST   | InputMessage | Standard JSON response |
| `/process/nion-map` | POST   | InputMessage | Plaintext NION Map     |
| `/process/json`     | POST   | InputMessage | Detailed JSON response |

### Request/Response Cycle

1. Validate input with Pydantic
2. Initialize NionGraph
3. Invoke graph with message
4. Call formatter with results
5. Return formatted response

## Performance Characteristics

### Execution Timeline

| Component           | Time     | Notes                                   |
| ------------------- | -------- | --------------------------------------- |
| L1 Planning         | 2-5s     | GPT-4o strategic analysis               |
| L3 Extraction       | 3-7s     | 3 parallel worker tasks (gpt-3.5-turbo) |
| Knowledge Retrieval | 50-150ms | Redis hit or in-memory                  |
| Evaluation          | 500ms-1s | Quality assessment                      |
| Total End-to-End    | 5-12s    | Typical execution                       |

### Resource Usage

- **Per Request Memory**: ~100-200MB
- **Docker Image**: ~400MB (multi-stage build)
- **Model Context**: 2000 tokens (L1), 1500 tokens (L3)

## Deployment Architecture

### Docker Image

**Dockerfile**: Multi-stage build

1. **Stage 1 - Builder**: Python 3.11-slim, install dependencies
2. **Stage 2 - Runtime**: Minimal image with only runtime requirements

### Docker Compose

**docker-compose.yml**: Development environment

- Redis service (Alpine, port 6379)
- Application service (port 8000)
- Health checks for both services
- Environment variable injection

### Kubernetes Manifests

**k8s-deployment.yaml**: Production deployment

- Namespace: `nion-system`
- Deployment: 2 replicas (rolling update)
- Service: LoadBalancer + NodePort
- ConfigMap: Application configuration
- Secret: API key management (base64 encoded)
- HorizontalPodAutoscaler: 2-5 replicas based on CPU/Memory
- PodDisruptionBudget: HA and graceful degradation

## Security Considerations

1. **API Key Management**: Kubernetes Secret, not in image
2. **Non-root Container**: Runs as `appuser`, not root
3. **Resource Limits**: CPU and memory constraints
4. **Health Checks**: Liveness and readiness probes
5. **Network Isolation**: Pod network policies
6. **Logging**: Structured logs without PII by default

## Error Handling

### LLM Call Failures

- Retry logic with exponential backoff
- Timeout handling (30 seconds)
- Fallback responses with error flags
- Comprehensive error logging

### Cache Failures

- Redis unavailability triggers in-memory fallback
- No service interruption
- Transparent to client
- Performance degradation logged

### Input Validation

- Pydantic model validation on all inputs
- HTTP 422 for validation errors
- Clear error messages
- Request tracking via UUID

## Testing Strategy

### test_local.py

- Integration test without FastAPI
- Direct graph invocation
- Output verification
- NION Map format validation

### test_api.py

- Endpoint health checks
- Full request/response cycle
- All 4 endpoints tested
- Response format validation

## Extension Points

1. **Add L3 Worker**: Implement in `L3Agents` class
2. **Change Models**: Update initialization in `agents.py`
3. **Modify Output**: Edit `formatter.py`
4. **Add Cache**: Implement cache backend in `agents.py`
5. **Add Endpoint**: Extend FastAPI in `main.py`

## Code Statistics

| Module           | Lines     | Purpose                 |
| ---------------- | --------- | ----------------------- |
| app/main.py      | 320       | FastAPI server          |
| app/graph.py     | 380       | LangGraph orchestration |
| app/agents.py    | 450       | L3 workers + caching    |
| app/schemas.py   | 650       | Pydantic models         |
| app/formatter.py | 250       | Output formatting       |
| **Total**        | **2,050** | **Core application**    |

---

For additional details, see:

- **README.md** - Setup and deployment
- **EXECUTION_GUIDE.md** - Running the system
- **API_EXAMPLES.md** - API reference
- **PROJECT_INDEX.md** - File guide
