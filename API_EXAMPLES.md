# API Examples - Complete Reference

## Base URL

```
http://localhost:8000
```

## Endpoints Overview

| Endpoint            | Method | Content-Type     | Response Format |
| ------------------- | ------ | ---------------- | --------------- |
| `/health`           | GET    | -                | JSON            |
| `/process`          | POST   | application/json | JSON (standard) |
| `/process/nion-map` | POST   | application/json | Plain text      |
| `/process/json`     | POST   | application/json | JSON (detailed) |

## Request Format

All POST endpoints accept the same input structure:

```json
{
  "message": "string - the message content to process",
  "sender": "string - name of message sender",
  "project_id": "string - project identifier"
}
```

### Validation Rules

- `message`: Required, non-empty string (max 5000 characters)
- `sender`: Required, non-empty string (max 255 characters)
- `project_id`: Required, non-empty string (max 100 characters)

## Endpoint Details

### 1. Health Check

**Endpoint**: `GET /health`

**Purpose**: Verify service is running and healthy

**Request**:

```powershell
curl http://localhost:8000/health
```

**Response** (200 OK):

```json
{
  "status": "healthy",
  "timestamp": "2024-01-15T10:30:45.123456Z",
  "uptime_seconds": 1234.56
}
```

### 2. Process Message (Standard JSON)

**Endpoint**: `POST /process`

**Purpose**: Process message and return standard JSON response

**Request**:

```powershell
$body = @{
    message = "The customer demo went great! We got positive feedback."
    sender = "Sarah Chen"
    project_id = "PRJ-ALPHA"
} | ConvertTo-Json

curl -X POST http://localhost:8000/process `
  -H "Content-Type: application/json" `
  -d $body
```

**Response** (200 OK):

```json
{
  "status": "success",
  "request_id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
  "timestamp": "2024-01-15T10:30:45Z",
  "results": {
    "action_items": [
      {
        "action": "Follow up with customer on implementation timeline",
        "priority": "HIGH",
        "assignee": "Sarah Chen"
      },
      {
        "action": "Update project roadmap based on customer feedback",
        "priority": "MEDIUM",
        "assignee": "Product Team"
      }
    ],
    "risks": [
      {
        "risk_description": "Resource allocation may be tight",
        "severity": "MEDIUM",
        "mitigation_strategy": "Review and plan resource allocation in next sprint"
      }
    ],
    "qna_pairs": [
      {
        "question": "What feedback did the customer provide?",
        "answer": "The customer was very positive about the demo and features presented."
      },
      {
        "question": "What are next steps?",
        "answer": "Follow up on implementation timeline and update roadmap accordingly."
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

### 3. Process Message (NION Orchestration Map)

**Endpoint**: `POST /process/nion-map`

**Purpose**: Process message and return plaintext NION Orchestration Map

**Request**:

```powershell
$body = @{
    message = "We saw increased churn in Q3. Customer satisfaction scores dropped."
    sender = "Analytics Team"
    project_id = "PRJ-BETA"
} | ConvertTo-Json

curl -X POST http://localhost:8000/process/nion-map `
  -H "Content-Type: application/json" `
  -d $body
```

**Response** (200 OK - Content-Type: text/plain):

```
═══════════════════════════════════════════════════════════════════════════════
NION ORCHESTRATION MAP
═══════════════════════════════════════════════════════════════════════════════

MESSAGE METADATA
─────────────────────────────────────────────────────────────────────────────
Sender: Analytics Team
Project: PRJ-BETA
Timestamp: 2024-01-15T10:35:22Z
Request ID: b2c3d4e5-f6a7-8901-bcde-f12345678901

L1 ORCHESTRATION PLAN
─────────────────────────────────────────────────────────────────────────────
The message indicates a critical business issue (customer churn and satisfaction
decline). Immediate analysis required.

Delegation Plan:
  1. PRIORITY: Analyze root causes of churn (L2_Tracking)
  2. PRIORITY: Identify at-risk customer segments (L2_Communication)
  3. Extract risk factors and mitigation strategies (Cross-Knowledge)

L2/L3 EXECUTION RESULTS
─────────────────────────────────────────────────────────────────────────────

ACTION ITEMS:
  • Conduct customer interviews to understand churn reasons
    Priority: HIGH
    Assignee: Analytics Team Lead

  • Develop customer retention strategy
    Priority: HIGH
    Assignee: Product Management

  • Implement feedback loop mechanism
    Priority: MEDIUM
    Assignee: Engineering Team

IDENTIFIED RISKS:
  • Revenue impact from churn
    Severity: CRITICAL
    Mitigation: Accelerate retention initiatives, offer incentives to at-risk customers

  • Reputational damage
    Severity: HIGH
    Mitigation: Communicate improvements through customer success channel

  • Team morale if not addressed
    Severity: MEDIUM
    Mitigation: Transparent communication about action items

Q&A DOCUMENTATION:
  Q: Why is churn increasing?
  A: Based on available data, likely causes include competitive pressure and
     feature gaps. Customer satisfaction scores suggest experience issues.

  Q: What is the financial impact?
  A: Potential loss of 15-20% of active customer base if trend continues.
     Estimated quarterly revenue impact: $500K-$750K.

  Q: What immediate actions should be taken?
  A: Conduct urgent customer outreach, analyze competitive positioning,
     and accelerate feature development for top requests.

EXECUTION SUMMARY
─────────────────────────────────────────────────────────────────────────────
Status: SUCCESS
Total Tasks Executed: 3
Successful: 3
Failed: 0
Duration: 9.2 seconds

Confidence Scores:
  Action Items: 94% confidence
  Risks: 89% confidence
  Recommendations: 91% confidence

═══════════════════════════════════════════════════════════════════════════════
```

### 4. Process Message (Detailed JSON)

**Endpoint**: `POST /process/json`

**Purpose**: Process message and return detailed JSON with execution metadata

**Request**:

```powershell
$body = @{
    message = "Project milestone achieved - beta launch completed successfully"
    sender = "Dev Lead"
    project_id = "PRJ-GAMMA"
} | ConvertTo-Json

curl -X POST http://localhost:8000/process/json `
  -H "Content-Type: application/json" `
  -d $body
```

**Response** (200 OK):

```json
{
  "status": "success",
  "request_id": "c3d4e5f6-a7b8-9012-cdef-123456789012",
  "timestamp": "2024-01-15T10:40:30Z",
  "message_metadata": {
    "sender": "Dev Lead",
    "project_id": "PRJ-GAMMA",
    "message_summary": "Project milestone achieved - beta launch completed successfully",
    "received_at": "2024-01-15T10:40:30Z"
  },
  "l1_orchestration_plan": {
    "intent": "Positive milestone announcement",
    "priority": "MEDIUM",
    "task_routing": ["L2_Tracking", "L2_Communication", "Cross-Knowledge"],
    "plan_text": "Analyze success factors, extract action items for post-launch, document lessons learned."
  },
  "l2_execution_results": {
    "l2_tracking": {
      "action_items": [
        {
          "action": "Schedule post-launch retrospective meeting",
          "priority": "HIGH",
          "assignee": "Dev Lead",
          "due_date": "2024-01-22"
        },
        {
          "action": "Document lessons learned and best practices",
          "priority": "HIGH",
          "assignee": "Technical Writer"
        },
        {
          "action": "Plan next feature release based on beta feedback",
          "priority": "MEDIUM",
          "assignee": "Product Manager"
        }
      ],
      "risks": [
        {
          "risk_description": "Beta users may have feature requests beyond original scope",
          "severity": "MEDIUM",
          "mitigation_strategy": "Capture and prioritize feedback for roadmap"
        },
        {
          "risk_description": "Production stability may differ from beta environment",
          "severity": "MEDIUM",
          "mitigation_strategy": "Monitor production metrics closely post-launch"
        }
      ]
    },
    "l2_communication": {
      "qna_pairs": [
        {
          "question": "What was achieved in the beta launch?",
          "answer": "Successful launch of beta version with core features validated by users."
        },
        {
          "question": "What are the next steps?",
          "answer": "Conduct retrospective, gather user feedback, plan next release cycle."
        }
      ]
    },
    "cross_cutting": {
      "knowledge_retrieved": {
        "similar_projects": ["PRJ-ALPHA", "PRJ-BETA"],
        "lessons_learned": "Post-launch retrospectives are critical for team learning",
        "best_practices": "Establish feedback collection mechanism early"
      },
      "quality_evaluation": {
        "output_quality_score": 92,
        "confidence_level": "HIGH",
        "notes": "Clear milestone with actionable next steps"
      }
    }
  },
  "execution_logs": [
    "2024-01-15T10:40:30Z - Message received from Dev Lead",
    "2024-01-15T10:40:31Z - L1 analysis: Intent=positive_milestone",
    "2024-01-15T10:40:35Z - L2_Tracking execution completed",
    "2024-01-15T10:40:38Z - L2_Communication execution completed",
    "2024-01-15T10:40:39Z - Cross-Knowledge retrieval completed",
    "2024-01-15T10:40:40Z - Quality evaluation completed",
    "2024-01-15T10:40:40Z - Output formatting and response generation"
  ],
  "execution_metrics": {
    "total_tasks": 5,
    "successful": 5,
    "failed": 0,
    "l1_duration_ms": 3100,
    "l2_duration_ms": 4200,
    "evaluation_duration_ms": 1500,
    "total_duration_ms": 10200,
    "average_response_time_ms": 2040
  }
}
```

## Error Handling

### Invalid Request Format

**Request**:

```powershell
curl -X POST http://localhost:8000/process `
  -H "Content-Type: application/json" `
  -d '{"message":"test"}'  # Missing required fields
```

**Response** (422 Unprocessable Entity):

```json
{
  "detail": [
    {
      "type": "missing",
      "loc": ["body", "sender"],
      "msg": "Field required",
      "input": { "message": "test" }
    },
    {
      "type": "missing",
      "loc": ["body", "project_id"],
      "msg": "Field required",
      "input": { "message": "test" }
    }
  ]
}
```

### Internal Server Error

**Response** (500 Internal Server Error):

```json
{
  "status": "error",
  "error_code": "INTERNAL_SERVER_ERROR",
  "message": "An unexpected error occurred during processing",
  "request_id": "error-request-id-123",
  "details": "Check server logs for details"
}
```

### Rate Limit Exceeded

**Response** (429 Too Many Requests):

```json
{
  "status": "error",
  "error_code": "RATE_LIMIT_EXCEEDED",
  "message": "Too many requests. Please try again later.",
  "retry_after_seconds": 60
}
```

## Response Status Codes

| Code | Meaning               | Details                              |
| ---- | --------------------- | ------------------------------------ |
| 200  | OK                    | Request successful                   |
| 400  | Bad Request           | Invalid request format or parameters |
| 422  | Unprocessable Entity  | Validation error in request body     |
| 429  | Too Many Requests     | Rate limit exceeded                  |
| 500  | Internal Server Error | Server error during processing       |
| 503  | Service Unavailable   | Service temporarily unavailable      |

## Common Use Cases

### Use Case 1: Extract Action Items from Meeting Notes

```powershell
$body = @{
    message = "In today's meeting we discussed the Q1 roadmap. Sarah will handle customer requirements, John will manage technical architecture, and Mike will coordinate with the design team. Main deliverable is customer dashboard by end of March."
    sender = "Meeting Facilitator"
    project_id = "Q1-ROADMAP"
} | ConvertTo-Json

curl -X POST http://localhost:8000/process `
  -H "Content-Type: application/json" `
  -d $body
```

### Use Case 2: Assess Project Risks

```powershell
$body = @{
    message = "Our main vendor is experiencing supply chain issues and may not deliver components by our deadline. We're considering alternative vendors but they have longer lead times and higher costs."
    sender = "Supply Chain Manager"
    project_id = "SUPPLY-CHAIN"
} | ConvertTo-Json

curl -X POST http://localhost:8000/process/nion-map `
  -H "Content-Type: application/json" `
  -d $body
```

### Use Case 3: Document Decision and Q&A

```powershell
$body = @{
    message = "Decision: We're moving from on-premises deployment to cloud-based infrastructure using Azure. This allows better scalability and reduces maintenance overhead. Implementation timeline: Q2 2024. Key stakeholders: DevOps team, Security, and Finance."
    sender = "CTO"
    project_id = "CLOUD-MIGRATION"
} | ConvertTo-Json

curl -X POST http://localhost:8000/process/json `
  -H "Content-Type: application/json" `
  -d $body
```

## Best Practices

1. **Always provide complete input**: Include message, sender, and project_id
2. **Use meaningful project_ids**: Makes tracking and logging easier
3. **Capture full context**: Include relevant details in message
4. **Handle retries**: Implement exponential backoff for 429/503 errors
5. **Parse responses correctly**: Different endpoints return different formats
6. **Monitor timing**: Check execution_metrics for performance trends
7. **Log request_id**: Use for troubleshooting and audit trails
8. **Validate input**: Ensure message length is reasonable (<5000 chars)

## Testing Your Integration

### Simple Test Script

```powershell
# test-integration.ps1

$baseUrl = "http://localhost:8000"
$message = "Test message for integration"

# Test 1: Health check
$health = curl -s "$baseUrl/health" | ConvertFrom-Json
Write-Host "Health Status: $($health.status)"

# Test 2: Process message
$body = @{
    message = $message
    sender = "Test User"
    project_id = "TEST-001"
} | ConvertTo-Json

$response = curl -s -X POST "$baseUrl/process" `
    -H "Content-Type: application/json" `
    -d $body | ConvertFrom-Json

Write-Host "Request ID: $($response.request_id)"
Write-Host "Duration: $($response.execution_metrics.total_duration_ms)ms"
Write-Host "Status: $($response.status)"
```

---

For more examples and integration patterns, see **EXECUTION_GUIDE.md** and **README.md**.
