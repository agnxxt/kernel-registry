# API Documentation

AGenNext Kernel exposes execution-focused APIs for requests that have already been validated and policy-checked by AGenNext Runner.

Kernel does not decide whether an arbitrary user request is allowed. Runner is the runtime enforcement boundary. Kernel receives trusted execution envelopes from Runner, executes the requested work, persists execution state, and returns results or traces.

```text
Platform → defines policies, guardrails, tools, memory config, and framework options
Runner   → validates requests, loads config, and enforces policies at the runtime boundary
Kernel   → executes pre-validated work, persists state, and returns results/traces
```

---

## Authentication

All endpoints require service-to-service authentication from Runner.

Current baseline:

```http
Authorization: Basic base64(username:password)
```

Production deployments should prefer a stronger service identity mechanism, such as signed internal tokens, mTLS, or gateway-issued credentials.

---

## Common Request Envelope

Execution requests should include tenant context, execution metadata, and a pre-validated payload from Runner.

```json
{
  "tenant_id": "tenant_123",
  "execution_id": "exec_abc123",
  "runner_request_id": "runreq_456",
  "actor": {
    "type": "agent",
    "id": "agent_support_bot"
  },
  "config": {
    "framework": "langgraph",
    "tools": ["github.create_issue"],
    "memory_scope": "tenant"
  },
  "payload": {
    "task": "Create a GitHub issue",
    "inputs": {
      "title": "Customer escalation",
      "body": "Create an issue from the validated support workflow."
    }
  },
  "prevalidation": {
    "validated_by": "AGenNext-Runner",
    "policy_result": "allowed",
    "policy_decision_id": "decision_789"
  }
}
```

Required fields:

- `tenant_id` — tenant boundary for execution, memory, and trace access
- `execution_id` — caller-provided or Kernel-generated execution identifier
- `payload` — pre-validated execution payload
- `prevalidation` — metadata proving Runner validated and allowed the request

---

## POST /execute

Run a pre-validated task and return a final execution result.

### Request

```json
{
  "tenant_id": "tenant_123",
  "execution_id": "exec_abc123",
  "runner_request_id": "runreq_456",
  "payload": {
    "task": "github.create_issue",
    "inputs": {
      "repo": "AGenNext/Platform",
      "title": "Wire Platform execute endpoint to Runner API",
      "body": "Proxy execution through Runner and Kernel."
    }
  },
  "prevalidation": {
    "validated_by": "AGenNext-Runner",
    "policy_result": "allowed",
    "policy_decision_id": "decision_789"
  }
}
```

### Response

```json
{
  "status": "success",
  "execution_id": "exec_abc123",
  "tenant_id": "tenant_123",
  "result": {
    "type": "github.issue",
    "id": "123",
    "url": "https://github.com/AGenNext/Platform/issues/123"
  },
  "trace_id": "trace_001"
}
```

### Error Response

```json
{
  "status": "error",
  "execution_id": "exec_abc123",
  "tenant_id": "tenant_123",
  "error": {
    "code": "EXECUTION_FAILED",
    "message": "The requested adapter failed during execution."
  },
  "trace_id": "trace_001"
}
```

---

## POST /stream

Run a pre-validated task and stream execution events or partial results.

### Request

```json
{
  "tenant_id": "tenant_123",
  "execution_id": "exec_stream_001",
  "payload": {
    "task": "framework.run",
    "inputs": {
      "framework": "langgraph",
      "workflow_id": "support_triage"
    }
  },
  "prevalidation": {
    "validated_by": "AGenNext-Runner",
    "policy_result": "allowed",
    "policy_decision_id": "decision_790"
  }
}
```

### Event Shape

```json
{
  "event": "step.completed",
  "execution_id": "exec_stream_001",
  "tenant_id": "tenant_123",
  "sequence": 3,
  "data": {
    "step": "tool.github.search_issues",
    "status": "success"
  }
}
```

---

## POST /memory

Perform tenant-scoped memory operations for pre-validated execution flows.

Runner decides whether the memory operation is allowed. Kernel performs the operation within the supplied tenant scope.

### Request

```json
{
  "tenant_id": "tenant_123",
  "operation": "write",
  "scope": "tenant",
  "key": "customer:acme:last_escalation",
  "value": {
    "summary": "Escalation issue created in GitHub",
    "execution_id": "exec_abc123"
  },
  "prevalidation": {
    "validated_by": "AGenNext-Runner",
    "policy_result": "allowed",
    "policy_decision_id": "decision_791"
  }
}
```

### Response

```json
{
  "status": "success",
  "tenant_id": "tenant_123",
  "operation": "write",
  "key": "customer:acme:last_escalation"
}
```

---

## GET /trace/{id}

Retrieve an execution trace.

Trace retrieval must be tenant-scoped. A caller may only retrieve traces for the tenant context supplied by Runner.

### Response

```json
{
  "trace_id": "trace_001",
  "tenant_id": "tenant_123",
  "execution_id": "exec_abc123",
  "status": "success",
  "events": [
    {
      "sequence": 1,
      "type": "execution.started",
      "timestamp": "2026-05-03T00:00:00Z"
    },
    {
      "sequence": 2,
      "type": "adapter.github.create_issue.completed",
      "timestamp": "2026-05-03T00:00:02Z"
    }
  ]
}
```

---

## Tenant Isolation Requirements

All execution, memory, and trace operations must be scoped by `tenant_id`.

Kernel must reject requests that:

- Omit tenant context
- Attempt to read or write resources outside the supplied tenant
- Provide inconsistent tenant values across execution metadata, memory scope, or trace lookup
- Lack Runner prevalidation metadata

---

## Notes

- Platform defines policy and runtime configuration.
- Runner validates input and enforces policy before invoking Kernel.
- Kernel executes only pre-validated work.
- Kernel persists execution state, memory operations, results, and traces.
- Policy decision IDs may be stored for audit correlation, but Kernel is not the primary policy decision point.


## Prevalidated Kernel Execution API

Kernel execution endpoints are intentionally narrow and execute only Runner-prevalidated work:

- `POST /execute`
- `POST /stream`
- `POST /memory`
- `GET /trace/{id}?tenant_id=<tenant>`

Required request envelope fields:
- `tenant_id`
- `payload`
- `prevalidation.validated_by == "AGenNext-Runner"`
- `authorization_result` and/or `policy_result` with an explicit allow result
- actor identity metadata (`type=agent`, `verified_by=AGenNext-Runner`, `identity_verified=true`) for actor execution flows

Kernel persists Runner-provided metadata for authorization (AuthZEN/OpenFGA/OPA), identity, protocol (A2A/ACP/Agent Client Protocol/Agent Network Protocol), memory, and trace/audit records. Kernel does **not** make primary authorization decisions and rejects missing or denied prevalidation metadata.


Production hardening controls in Kernel API include:
- Optional request signature verification (`X-Runner-Signature`) when `RUNNER_SHARED_SECRET` is configured.
- Payload and memory-key size guards.
- Idempotent execution support via `X-Idempotency-Key`.
- Durable local state persistence for execution, memory, trace, and idempotency records via SQLite.
