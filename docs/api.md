# API Documentation

## POST /execute

Execute an agent task.

### Request

```json
{
  "task": "string"
}
```

### Headers
- Authorization: Basic Auth

### Response

```json
{
  "status": "success",
  "decision_id": "uuid"
}
```

## Notes
- All requests are policy-evaluated
- Responses include traceable decisions
