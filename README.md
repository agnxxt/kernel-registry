# AGenNext Kernel

**Version: 1.0.4-stable**

AGenNext Kernel is the execution engine for AgentNext. It receives pre-validated requests from AGenNext Runner, executes the requested work, persists execution state, and returns results and traces.

Kernel does **not** own user-facing configuration or boundary policy enforcement. Those responsibilities are split across the platform:

```text
Platform → defines policies, guardrails, tools, memory config, and framework options
Runner   → validates requests, loads config, and enforces policies at the runtime boundary
Kernel   → executes pre-validated work, persists state, and returns results/traces
```

---

## What This Solves

AI agents need a reliable execution substrate after policy and guardrail checks have already passed.

AGenNext Kernel provides that substrate by handling:

- Controlled execution of pre-validated tasks
- Tenant-scoped execution context
- Persistent memory and execution state
- Traceable results for audit and observability
- Adapter-backed calls to external systems such as GitHub, Slack, and Jira

---

## Kernel Responsibilities

Kernel is responsible for execution-time behavior:

- Run validated agent tasks from Runner
- Execute tool calls and framework operations
- Apply tenant context to execution, memory, and trace operations
- Persist execution results, decisions, memory updates, and traces
- Return structured results to Runner

Kernel assumes Runner has already performed input validation, policy checks, guardrail enforcement, and configuration loading.

---

## Non-Responsibilities

Kernel should not duplicate responsibilities owned by Platform or Runner.

Kernel does **not**:

- Define OPA/Rego policies
- Own user-facing guardrail configuration
- Decide whether an unvalidated request is allowed
- Act as the primary policy-enforcement boundary
- Replace Runner framework, tool, memory, guardrail, or trace adapters

For policy authoring and runtime enforcement, use Platform and Runner respectively.

---

## Core Capabilities

- Execution API for pre-validated requests
- Streaming execution support
- Tenant-scoped memory operations
- Trace and audit retrieval
- External-system execution adapters
- Structured result handoff back to Runner

---

## API Surface

The Kernel API is expected to expose execution-focused endpoints:

- `POST /execute` — run a pre-validated task with platform-provided config
- `POST /stream` — stream execution events and partial results
- `POST /memory` — perform tenant-scoped memory operations
- `GET /trace/{id}` — retrieve execution traces

Requests should include tenant context and any pre-validated execution metadata supplied by Runner.

---

## Quickstart

```bash
docker compose up --build -d
```

---

## Related Repositories

- **AGenNext Platform** — defines policies, guardrails, tools, framework options, and user-facing configuration
- **AGenNext Runner** — enforces policies, validates requests, loads Platform config, and invokes Kernel
- **AGenNext Kernel** — executes pre-validated work and returns results/traces

---

## Docs

See the `/docs` folder for API and architecture details.

---

© 2026 Agent Kernel Team
