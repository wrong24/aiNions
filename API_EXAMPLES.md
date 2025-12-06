## NION API Examples - Complete Request/Response Guide

### Base URL

```
http://localhost:8000
```

### Authentication

None required (add if needed)

---

## 1. Health Check

### Request

```bash
curl http://localhost:8000/health
```

### Response (200 OK)

```json
{
  "status": "healthy",
  "timestamp": "2024-12-06T10:30:00Z",
  "service": "Nion Orchestration Engine"
}
```

---

## 2. Process Message (Standard Response)

### Endpoint

```
POST /process
```

### Request

```bash
curl -X POST http://localhost:8000/process \
  -H "Content-Type: application/json" \
  -d '{
    "message": "The customer demo went great! They loved it but asked if we could add real-time notifications. They'\''re willing to pay 20% more.",
    "sender": "Sarah Chen",
    "project_id": "PRJ-ALPHA",
    "message_id": "MSG-20241206-001"
  }'
```

### Response (200 OK)

```json
{
  "state_id": "abc-123-xyz-789",
  "status": "COMPLETED",
  "message": "Orchestration completed successfully",
  "execution_time_ms": 3456.78,
  "execution_results_count": 3
}
```

---

## 3. Process Message (NION MAP Format)

### Endpoint

```
POST /process/nion-map
```

### Request

```bash
curl -X POST http://localhost:8000/process/nion-map \
  -H "Content-Type: application/json" \
  -d '{
    "message": "The customer demo went great! They loved it but asked if we could add real-time notifications. They'\''re willing to pay 20% more.",
    "sender": "Sarah Chen",
    "project_id": "PRJ-ALPHA"
  }'
```

### Response (200 OK - Plain Text)

```
==================================================================================
NION ORCHESTRATION MAP
==================================================================================

MESSAGE METADATA
──────────────────────────────────────────────────────────────────────────────
  Message ID: AUTO-GENERATED
  Sender: Sarah Chen
  Project: PRJ-ALPHA
  Timestamp: 2024-12-06T10:30:00.123456Z
  State ID: abc-123-xyz-789
  Message: The customer demo went great! They loved it but asked if we...

=== L1 PLAN ===
──────────────────────────────────────────────────────────────────────────────
  [TASK-001] Domain: L2_Tracking
    Task ID: PLAN-001
    Description: Extract and track action items, risks, decisions from feature request
    Priority: P1
    Status: IN_PROGRESS

  [TASK-002] Domain: L2_Communication
    Task ID: PLAN-002
    Description: Document customer feedback and Q&A; prepare reporting
    Priority: P2
    Status: PENDING

  [TASK-003] Domain: L2_Learning
    Task ID: PLAN-003
    Description: Generate or update SOPs based on process insights
    Priority: P3
    Status: PENDING

=== L2/L3 EXECUTION ===
──────────────────────────────────────────────────────────────────────────────
  [L2_TRACKING_001] L2_Tracking
    Status: SUCCESS
    Duration: 2345.67ms
    ACTION ITEMS (3):
      • ACT-001: Implement real-time notifications feature
        Owner: Engineering Team, Priority: HIGH, Status: OPEN
        Due: 2025-01-15
      • ACT-002: Cost estimation for real-time infrastructure
        Owner: Sarah Chen, Priority: HIGH, Status: OPEN
        Due: 2025-01-08
      • ACT-003: Schedule customer feedback session
        Owner: Product Manager, Priority: MEDIUM, Status: OPEN
        Due: 2025-01-12

    RISKS (3):
      • RSK-001: Real-time infrastructure complexity
        Severity: HIGH, Owner: TBD
        Mitigation: Evaluate existing microservices framework and consider WebSocket implementation
      • RSK-002: Scope creep potential
        Severity: MEDIUM, Owner: TBD
        Mitigation: Document exact requirements before development
      • RSK-003: Budget increase approval dependency
        Severity: MEDIUM, Owner: TBD
        Mitigation: Prepare business case justifying ROI

    DECISIONS (1):
      • DEC-001: Customer approved 20% budget increase for real-time notifications
        Rationale: Customer satisfaction and feature adoption priority
        Impact: Enables feature roadmap acceleration; improves competitive positioning

  [L2_COMMUNICATION_001] L2_Communication
    Status: SUCCESS
    Duration: 1234.56ms
    Q&A RECORDS (2):
      Q: Are customers willing to fund real-time notifications?
      A: Yes, customer demo feedback indicates willingness to pay 20% premium
      Confidence: 0.95

      Q: What is the timeline for implementation?
      A: Implementation timeline depends on architecture validation; estimate 6-8 weeks
      Confidence: 0.85

  [CROSS_KNOWLEDGE_001] Cross_Knowledge
    Status: SUCCESS
    Duration: 145.23ms
    KNOWLEDGE CONTEXT:
      Project: Project Alpha - Real-time Customer Platform
      Budget: $150000
      Timeline: Q1-Q2 2025
      Team Size: 3
      Tech Stack: Python, React, PostgreSQL, Redis
      Constraints: Real-time features require WebSocket infrastructure and Redis caching.

=== EXECUTION SUMMARY ===
──────────────────────────────────────────────────────────────────────────────
  Total Tasks Executed: 3
  Successful: 3
  Failed: 0
  Partial: 0
  Overall Status: COMPLETED

=== EXECUTION LOGS ===
──────────────────────────────────────────────────────────────────────────────
  [L1] Created plan with 3 tasks
  [L2_Tracking] Completed: 3 actions, 3 risks
  [L2_Communication] Completed: 2 Q&A records
  [Cross_Knowledge] Retrieved context for PRJ-ALPHA
  [Evaluator] COMPLETED: 3/3 tasks successful

==================================================================================
```

### Response Headers

```
X-State-ID: abc-123-xyz-789
X-Execution-Time-Ms: 3725.89
X-Tasks-Executed: 3
```

---

## 4. Process Message (Detailed JSON)

### Endpoint

```
POST /process/json
```

### Request

```bash
curl -X POST http://localhost:8000/process/json \
  -H "Content-Type: application/json" \
  -d '{
    "message": "The customer demo went great! They loved it but asked if we could add real-time notifications. They'\''re willing to pay 20% more.",
    "sender": "Sarah Chen",
    "project_id": "PRJ-ALPHA",
    "message_id": "MSG-20241206-001"
  }' | jq .
```

### Response (200 OK - JSON)

```json
{
  "state_id": "abc-123-xyz-789",
  "message_metadata": {
    "message_id": "MSG-20241206-001",
    "sender": "Sarah Chen",
    "project_id": "PRJ-ALPHA",
    "timestamp": "2024-12-06T10:30:00.123456Z"
  },
  "plan": [
    {
      "task_id": "PLAN-001",
      "domain": "L2_Tracking",
      "description": "Extract and track action items, risks, decisions from feature request",
      "priority": 1,
      "status": "IN_PROGRESS"
    },
    {
      "task_id": "PLAN-002",
      "domain": "L2_Communication",
      "description": "Document customer feedback and Q&A; prepare reporting",
      "priority": 2,
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
        "domain": "L2_Tracking",
        "action_items": [
          {
            "id": "ACT-001",
            "title": "Implement real-time notifications feature",
            "owner": "Engineering Team",
            "priority": "HIGH",
            "due_date": "2025-01-15",
            "status": "OPEN"
          },
          {
            "id": "ACT-002",
            "title": "Cost estimation for real-time infrastructure",
            "owner": "Sarah Chen",
            "priority": "HIGH",
            "due_date": "2025-01-08",
            "status": "OPEN"
          },
          {
            "id": "ACT-003",
            "title": "Schedule customer feedback session",
            "owner": "Product Manager",
            "priority": "MEDIUM",
            "due_date": "2025-01-12",
            "status": "OPEN"
          }
        ],
        "risks": [
          {
            "id": "RSK-001",
            "title": "Real-time infrastructure complexity",
            "severity": "HIGH",
            "mitigation_strategy": "Evaluate existing microservices framework and consider WebSocket implementation",
            "owner": null
          },
          {
            "id": "RSK-002",
            "title": "Scope creep potential",
            "severity": "MEDIUM",
            "mitigation_strategy": "Document exact requirements before development",
            "owner": null
          },
          {
            "id": "RSK-003",
            "title": "Budget increase approval dependency",
            "severity": "MEDIUM",
            "mitigation_strategy": "Prepare business case justifying ROI",
            "owner": null
          }
        ],
        "decisions": [
          {
            "id": "DEC-001",
            "title": "Customer approved 20% budget increase for real-time notifications",
            "rationale": "Customer satisfaction and feature adoption priority",
            "impact": "Enables feature roadmap acceleration; improves competitive positioning"
          }
        ],
        "logs": []
      }
    },
    "L2_COMMUNICATION_001": {
      "task_id": "L2_COMMUNICATION_001",
      "task_type": "L2_Communication",
      "status": "SUCCESS",
      "duration_ms": 1234.56,
      "output": {
        "domain": "L2_Communication",
        "qna_records": [
          {
            "question": "Are customers willing to fund real-time notifications?",
            "answer": "Yes, customer demo feedback indicates willingness to pay 20% premium",
            "confidence": 0.95
          },
          {
            "question": "What is the implementation timeline?",
            "answer": "Estimated 6-8 weeks depending on architecture validation",
            "confidence": 0.85
          }
        ],
        "logs": []
      }
    },
    "CROSS_KNOWLEDGE_001": {
      "task_id": "CROSS_KNOWLEDGE_001",
      "task_type": "Cross_Knowledge",
      "status": "SUCCESS",
      "duration_ms": 145.23,
      "output": {
        "domain": "Cross_Knowledge",
        "knowledge_context": {
          "project_name": "Project Alpha - Real-time Customer Platform",
          "team_members": [
            "Sarah Chen (Product Manager)",
            "John Doe (Lead Engineer)",
            "Alice Smith (QA)"
          ],
          "budget": 150000,
          "timeline": "Q1-Q2 2025",
          "current_features": [
            "user_authentication",
            "dashboard",
            "analytics_reporting"
          ],
          "tech_stack": ["Python", "React", "PostgreSQL", "Redis"],
          "recent_updates": "Customer demo scheduled for Q4 2024. Positive feedback expected.",
          "constraints": "Real-time features require WebSocket infrastructure and Redis caching.",
          "precedents": "Similar feature (push_notifications) added in PRJ-BETA with 18% cost increase and 6-week timeline.",
          "stakeholders": [
            "Executive Team",
            "Engineering Team",
            "Customer Success"
          ],
          "risk_threshold": "HIGH",
          "approval_authority": "VP Product & Finance"
        },
        "cache_hit": false,
        "logs": []
      }
    }
  },
  "logs": [
    "[L1] Created plan with 3 tasks",
    "[L2_Tracking] Completed: 3 actions, 3 risks",
    "[L2_Communication] Completed: 2 Q&A records",
    "[Cross_Knowledge] Retrieved context for PRJ-ALPHA",
    "[Evaluator] COMPLETED: 3/3 tasks successful"
  ],
  "execution_time_ms": 3725.89
}
```

---

## Error Responses

### 500 Server Error

```json
{
  "detail": "Error processing message: OPENAI_API_KEY not set"
}
```

### 400 Bad Request

```json
{
  "detail": [
    {
      "type": "missing",
      "loc": ["body", "message"],
      "msg": "Field required"
    }
  ]
}
```

---

## Testing with Different Projects

### PRJ-BETA

```bash
curl -X POST http://localhost:8000/process/json \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Enterprise analytics phase 2 requires latency optimization",
    "sender": "Tom Wilson",
    "project_id": "PRJ-BETA"
  }'
```

---

## Performance Metrics

| Operation                    | Typical Duration |
| ---------------------------- | ---------------- |
| L1 Planning                  | 2-5 seconds      |
| L3 Action Extraction         | 1-3 seconds      |
| L3 Risk Extraction           | 1-3 seconds      |
| L3 Q&A Generation            | 1-2 seconds      |
| Cross-Knowledge (cache hit)  | 50-150ms         |
| Cross-Knowledge (cache miss) | 200-500ms        |
| Total Orchestration          | 4-10 seconds     |

---

## Rate Limiting

Currently none, but can be added via:

```python
from slowapi import Limiter
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter
@limiter.limit("100/minute")
async def process_message(...):
```

---

## WebHook Integration Example

```python
# Example for integrating as a webhook receiver
import asyncio
from app.schemas import InputMessage
from app.graph import NionGraph

async def handle_webhook(event_data):
    """Handle incoming webhook"""
    message = InputMessage(
        message=event_data['message'],
        sender=event_data['sender'],
        project_id=event_data['project_id']
    )

    graph = NionGraph()
    result = graph.invoke(message)

    # Send result to downstream system
    return result
```

---

## Batch Processing Example

```bash
#!/bin/bash

# Process multiple messages in sequence
messages=(
  '{"message":"Feature request 1","sender":"User1","project_id":"PRJ-ALPHA"}'
  '{"message":"Feature request 2","sender":"User2","project_id":"PRJ-BETA"}'
  '{"message":"Feature request 3","sender":"User3","project_id":"PRJ-ALPHA"}'
)

for msg in "${messages[@]}"; do
  echo "Processing: $msg"
  curl -X POST http://localhost:8000/process/nion-map \
    -H "Content-Type: application/json" \
    -d "$msg"
  echo "\n---\n"
  sleep 1
done
```
