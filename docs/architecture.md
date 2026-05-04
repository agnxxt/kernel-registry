# Architecture

## Overview

AGenNext Kernel is the execution layer in the AgentNext runtime stack. It receives pre-validated execution requests from AGenNext Runner, performs the requested work, persists execution state, and returns results and traces.

Kernel is not the user-facing configuration system and is not the primary policy-enforcement boundary.

```text
Platform → defines policies, guardrails, tools, memory config, and framework options
Runner   → validates requests, loads config, and enforces policies at the runtime boundary
Kernel   → executes pre-validated work, persists state, and returns results/traces
```

---

## System Flow

```text
[ User / Agent / Application ]
              ↓
[ AGenNext Platform ]
  Defines policies, guardrails, tools, memory config, and framework options
              ↓
[ AGenNext Runner ]
  Validates input, loads Platform config, enforces policy, applies guardrails
              ↓
[ AGenNext Kernel API ]
  Accepts only pre-validated execution envelopes from Runner
              ↓
[ Kernel Execution Engine ]
  Runs tools, frameworks, memory operations, and external adapter calls
              ↓
[ Tenant-Scoped Persistence ]
  Stores execution state, memory records, traces, and audit correlation data
              ↓
[ Results / Streams / Traces returned to Runner ]
```

---

## Kernel Layers

AGenNext Kernel is composed of the following execution-focused layers:

```text
[ Kernel API ]
      ↓
[ Request Envelope Validator ]
      ↓
[ Tenant Context Resolver ]
      ↓
[ Execution Engine ]
      ↓
[ Runtime + Tool Adapters ]
      ↓
[ Memory, Trace, and Result Stores ]
```

---

## Components

### Kernel API

Accepts service-to-service requests from Runner.

Responsibilities:

- Authenticate Runner-originated requests
- Validate required envelope fields
- Route requests to execution, streaming, memory, and trace handlers
- Reject requests missing tenant context or Runner prevalidation metadata

### Request Envelope Validator

Verifies that Kernel received a complete execution envelope from Runner.

Responsibilities:

- Require `tenant_id`
- Require execution metadata where applicable
- Require prevalidation metadata from Runner
- Ensure request shape matches the target Kernel API

This validator checks execution readiness. It does not replace Runner policy enforcement.

### Tenant Context Resolver

Applies tenant boundaries to all execution-time operations.

Responsibilities:

- Bind executions to a tenant
- Scope memory reads and writes by tenant
- Scope trace lookup by tenant
- Prevent cross-tenant resource access

### Execution Engine

Runs pre-validated work.

Responsibilities:

- Execute framework operations
- Execute tool calls
- Coordinate adapter calls
- Produce structured results
- Emit trace events
- Persist execution state

### Runtime and Tool Adapters

Connect Kernel execution to implementation-specific systems.

Examples:

- GitHub adapter
- Slack adapter
- Jira adapter
- Framework runtime adapter
- Memory adapter

Runner owns the high-level adapter configuration and enforcement decisions. Kernel performs the execution using the config supplied in the validated request.

### Memory, Trace, and Result Stores

Persist execution artifacts.

Responsibilities:

- Store execution results
- Store tenant-scoped memory entries
- Store ordered trace events
- Preserve policy decision IDs or Runner request IDs for audit correlation

---

## Responsibility Boundaries

### Platform Defines

Platform owns user-facing configuration:

- OPA/Rego policies
- Guardrails
- Tool definitions
- Memory configuration
- Framework selection
- Tenant-level runtime configuration

### Runner Enforces

Runner owns runtime boundary enforcement:

- Loads Platform configuration
- Validates requests
- Applies policies
- Applies input and output guardrails
- Selects framework, memory, tool, and trace adapters
- Invokes Kernel only after validation succeeds

### Kernel Executes

Kernel owns execution:

- Runs pre-validated tasks
- Performs tenant-scoped memory operations
- Calls external-system adapters
- Records traces
- Returns results to Runner

---

## Data Model Concepts

### Execution

A single validated unit of work received from Runner.

Typical fields:

- `execution_id`
- `tenant_id`
- `runner_request_id`
- `status`
- `result`
- `trace_id`
- `created_at`
- `completed_at`

### Tenant Context

The isolation boundary for all Kernel work.

Typical fields:

- `tenant_id`
- `actor_id`
- `actor_type`
- `memory_scope`
- `execution_scope`

### Trace

An ordered record of execution events.

Typical fields:

- `trace_id`
- `execution_id`
- `tenant_id`
- `events[]`

### Memory Record

A tenant-scoped persisted memory entry.

Typical fields:

- `tenant_id`
- `scope`
- `key`
- `value`
- `created_at`
- `updated_at`

---

## Key Principles

1. **Runner validates before Kernel executes.**
   Kernel should not execute requests that lack Runner prevalidation metadata.

2. **Tenant context is mandatory.**
   Execution, memory, and trace operations must always be scoped to a tenant.

3. **Kernel does not duplicate Platform policy authoring.**
   Platform defines policies and runtime config.

4. **Kernel does not replace Runner enforcement.**
   Runner is the runtime enforcement boundary.

5. **Execution must be traceable.**
   Every execution should produce structured trace events and audit correlation metadata.

---

## Primary API Surfaces

- `POST /execute` — run a pre-validated task
- `POST /stream` — stream execution events and partial results
- `POST /memory` — perform tenant-scoped memory operations
- `GET /trace/{id}` — retrieve tenant-scoped execution traces

---

## Deprecated Architecture Language

Older documentation described Kernel as owning OPA policy evaluation directly.

That model has been superseded by the current split:

- Platform defines policy
- Runner enforces policy
- Kernel executes pre-validated work

Kernel may store policy decision IDs for audit correlation, but it is not the primary policy decision point.
