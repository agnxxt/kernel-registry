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
