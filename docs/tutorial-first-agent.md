# Tutorial: Your First Governed Agent

## Goal
Create and execute your first policy-controlled task.

---

## Step 1: Start Kernel

```bash
docker compose up -d
```

---

## Step 2: Send Task

```bash
curl -X POST http://localhost:8000/execute \
  -H "Authorization: Basic <base64>" \
  -H "Content-Type: application/json" \
  -d '{"task": "Create GitHub issue: test"}'
```

---

## Step 3: Observe

Go to UI:
http://localhost:3000

You will see:
- Decision log
- Policy evaluation
- Execution result

---

## Step 4: Modify Policy

Go to:
http://localhost:3000/policies

Try blocking the action.

Re-run the request → it should fail.

---

## Outcome

You now have:
- Policy-controlled execution
- Audit trail
- Observability
