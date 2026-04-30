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

## Production Quickstart
Prerequisites:
- Docker + Docker Compose
- Git

Run local baseline:
```bash
git clone https://github.com/agnxxt/kernel-registry.git
cd kernel-registry
docker compose up --build -d
```

Validate contracts:
```bash
docker compose exec kernel-tooling bash -lc "./scripts/validate_schemas.sh && ./scripts/validate_proto.sh"
```

Run DB migrations:
```bash
docker compose exec kernel-tooling alembic -c persistence/alembic.ini upgrade head
```

Stop stack:
```bash
docker compose down
```

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
- Runtime Artifact Registry: `schemas/runtime/`

## Reference Architecture
Control planes:
- Guardrail plane (intent checks, drift controls, constraint enforcement)
- Policy plane (OPA + OpenFGA)
- Identity plane (canonical ID, VC, wallet, trust, registry)
- Action plane (provider adapters: git, docker, caddy, and extensible providers)
- Learning/observability plane (learning loop + ML observability integration)

Data and protocol contracts:
- JSON Schema for payload validation
- Proto for service/event interfaces
- Extension model via semantic metadata and taxonomy overlays

Runtime targets:
- Local Docker Compose for development and validation
- Kubernetes manifests in `deploy/k8s/` for cluster deployment

## Deployment Paths
Local:
- `compose.yaml` boots Caddy, Postgres, and kernel-tooling baseline services.

Kubernetes:
- Use `deploy/k8s/` as base blueprints.
- Promote to environment overlays (dev/stage/prod) with image pinning and storage classes.

Ingress and edge:
- Caddy can be used as local/prototype ingress and reverse proxy.
- For production ingress, pair with managed LB/Ingress controller and TLS automation policy.

## CI/CD
- CI: `.github/workflows/ci.yml`
  - JSON schema validation
  - proto structural validation
  - Alembic syntax checks
- Release: `.github/workflows/release.yml`
  - tag/manual release artifact generation

## Operations Baseline
Health and validation:
- Schema and proto validation scripts must pass before merge.
- Migration checks run through Alembic config in `persistence/alembic.ini`.

Security and policy:
- Enforce pre-tool and post-completion hooks from guardrail contracts.
- Route authorization checks through OPA/OpenFGA policy contracts.

Reliability:
- Persist stateful services with durable volumes.
- Track baseline performance before and after stack changes.

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

## Next Build Priorities
1. Implement runtime services for policy-kernel and protocol-kernel contracts.
2. Add environment overlays (`kustomize` or Helm) for dev/stage/prod.
3. Add conformance tests for ANP/ACP and OPA/OpenFGA decision flows.
4. Add SLO gate checks in CI for regression detection.
