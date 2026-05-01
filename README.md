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

Run end-to-end smoke test:
```bash
./ops/e2e-smoke.sh
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

## Deployment

The Agent Kernel Platform is designed for multi-cloud and hybrid environments.

### 1. Docker Compose (Quickstart)
Ideal for local testing and simulation.
```bash
docker compose up --build
```
*   **Kernel API**: http://localhost:8000
*   **Visual Control Plane**: http://localhost:3000
*   **MLflow Audit**: http://localhost:5000

### 2. Kubernetes (Production)
For distributed, high-availability deployments.
```bash
# Apply the core platform manifests
kubectl apply -f deploy/k8s/kernel-platform.yaml

# Apply specialized cognitive planes
kubectl apply -f deploy/k8s/model-runner/
kubectl apply -f deploy/k8s/secret-kernel.yaml
```

## Cognitive Features
This kernel implements state-of-the-art AI reliability frameworks:
- **RACF**: Rogue Agent Containment & Kill Switch.
- **Dual-Process Routing**: Fast vs. Slow thinking selection.
- **Epistemic Trust**: Dynamic credibility weighting.
- **Intelligent Authentication**: Reasoning-based access control.
- **Universal Schema**: Native Schema.org + JSON-LD interoperability.

