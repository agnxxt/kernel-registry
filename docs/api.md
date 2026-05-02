# API Documentation

## Authentication

All endpoints require Basic Auth:

```
Authorization: Basic base64(username:password)
```

---

## POST /execute

Execute an agent task.

### Request

```json
{
  "task": "Create a GitHub issue",
  "metadata": {
    "priority": "high"
  }
}
```

### Response

```json
{
  "status": "success",
  "decision_id": "uuid",
  "policy": "allowed"
}
```

---

## GET /decisions/{id}

Retrieve decision details.

### Response

```json
{
  "id": "uuid",
  "task": "...",
  "result": "...",
  "policy": "allowed"
}
```

---

## Notes

- Every request goes through OPA policy evaluation
- All decisions are persisted
- Full audit trail available
