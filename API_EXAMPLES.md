# API_EXAMPLES.md --- API Examples

## Health check

``` bash
curl http://localhost:8000/health
```

## Process message --- aiNion map

``` bash
curl -X POST http://localhost:8000/process/ainion-map   -H "Content-Type: application/json"   -d '{
    "message": "The customer demo went great!",
    "sender": "Sarah Chen",
    "project_id": "PRJ-ALPHA"
  }'
```

## Process message --- JSON response

``` bash
curl -X POST http://localhost:8000/process   -H "Content-Type: application/json"   -d '{
    "message": "We saw increased churn in Q3",
    "sender": "Product Team",
    "project_id": "PRJ-BETA"
  }'
```

## Example JSON schema

``` json
{
  "status": "ok",
  "request_id": "<uuid>",
  "results": {
    "action_items": [],
    "risks": [],
    "qna": []
  },
  "timing_ms": 1234
}
```
