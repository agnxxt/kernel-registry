# Decision System (Kernel Module)

## Purpose
Kernel-level decision control for high-risk actions:
- quorum approvals (M-of-N)
- SLA timeout and escalation
- immutable decision trail
- binding to run/step execution context

## Hook integration
- `pre_tool`: may submit decision request and block tool until status allows execution
- `post_completion`: submits final reasoning/evidence and writes decision audit event

## Status lifecycle
`PENDING -> APPROVED|REJECTED|EXPIRED|CANCELED`

## Verdicts
`ALLOW | WARN | BLOCK | ESCALATE`

## Topics
- `kernel.decision.request.v1`
- `kernel.decision.status.v1`
- `kernel.decision.audit.v1`

## Determinism notes
Each decision must be bound to:
- `run_id`
- `step_id`
- `trigger_event_id`
so replay and incident forensics remain stable.

## Identity-bearing decision graph registry
The decision system uses `docs/decision-identity-schema-registry.md` as the canonical schema registry for advanced decision logging. The registry upgrades flat decision logs into identity-bearing knowledge graph events with controlled taxonomies, explicit table/column coverage, lineage, policy bindings, evidence, risk, constraint, evaluation, outcome, and feedback dependencies.

Canonical machine-readable artifacts:
- `schemas/identity/resource-identity.schema.json`
- `schemas/decision/decision-taxonomy.schema.json`
- `schemas/decision/decision-taxonomy.v1.json`
- `schemas/decision/decision-knowledge-graph.schema.json`

The Redpanda `DecisionEvent` remains the stream event contract and may embed `identity`, `resource_identities`, and `knowledge_graph` projections for downstream graph stores and audit warehouses.
