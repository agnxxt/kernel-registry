# Context Envelope

Context is derived and traceable across pipeline phases:
- data
- chunking
- retrieval
- inference
- decision
- execution

Every hook and decision event must carry immutable references:
- `tenant_id`
- `task_id`
- `run_id`
- `step_id`
- `trace_id`

This guarantees replayability and incident forensics.

## Awareness Layer
Adds first-class situational awareness:
- self awareness (capabilities, confidence, limits)
- environment awareness (tier, region, runtime health)
- risk awareness (risk level, guardrail mode, human review)
