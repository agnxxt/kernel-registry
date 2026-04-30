# Agent Kernel

Framework/model/cloud-agnostic kernel contracts and runtime scaffolding for:
- guardrails
- context + awareness
- decisions
- learning loop
- common action bus
- identity (canonical ID, VC, wallet, trust, registry)
- secret management
- persistence + migrations

## Repo Layout
- `schemas/` protocol contracts (JSON Schema + proto)
- `docs/` architecture and operational docs
- `persistence/` SQLAlchemy + Alembic scaffold
- `deploy/k8s/` Kubernetes deployment blueprints
- `ops/` benchmark and hardening assets
- `.github/workflows/` CI/CD workflows

## Core Contracts
- Guardrails: `schemas/guardrails/`
- Context Envelope: `schemas/context-envelope.schema.json`
- Awareness Layer: `schemas/context-awareness.schema.json`
- Decision System: `schemas/decision/`
- Learning Loop: `schemas/learning/`
- Kernel Actions: `schemas/actions/`
- Identity Kernel: `schemas/identity/`
- Secret Kernel: `schemas/secrets/`
- Policy Kernel (OPA/OpenFGA): `schemas/policy/`
- Protocol Kernel (ANP/ACP): `schemas/protocol/`

## Local Container Workflow
Start local stack:
```bash
docker compose up --build -d
```

Validate contracts:
```bash
docker compose exec kernel-tooling bash -lc "./scripts/validate_schemas.sh && ./scripts/validate_proto.sh"
```

Run migrations:
```bash
docker compose exec kernel-tooling alembic -c persistence/alembic.ini upgrade head
```

## CI/CD
- CI: `.github/workflows/ci.yml`
  - JSON schema validation
  - proto structural validation
  - Alembic syntax checks
- Release: `.github/workflows/release.yml`
  - tag/manual release artifact generation

## Current Runtime Baseline (VPS)
Kubernetes namespace `agent-kernel` currently includes:
- Temporal
- LiteLLM
- Redis
- Postgres
- Qdrant
- MinIO
- NATS
- Langfuse (v2)

## Hardening Direction
- pin images by digest
- persistent storage for all stateful services
- network policies + secret provider integration
- SLO benchmark gating per change

## Benchmark Assets
- `ops/benchmark-scorecard.yaml`
- `ops/collect-baseline.sh`
- `ops/hardening-checklist.md`
