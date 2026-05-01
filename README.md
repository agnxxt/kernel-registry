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

## Quickstart (Recommended)
Use the guided runner for a consistent, one-command setup:

```bash
./ops/guided-walkthrough.sh --mode local
```

Why this is recommended:
- Executes steps in safe order (validate -> start -> migrate -> smoke).
- Explains each step as it runs.
- Supports local and Kubernetes paths with the same interface.

### Guided options
- `--mode local|k8s`
  - `local`: Docker Compose lifecycle (dev/test).
  - `k8s`: Kubernetes manifest apply flow (production-style).
- `--validate-only`: run contract checks only.
- `--skip-migrations`: skip Alembic upgrade (local mode).
- `--skip-smoke`: skip endpoint smoke checks.
- `-h, --help`: print usage and examples.

Examples:
```bash
# Full local bring-up and validation
./ops/guided-walkthrough.sh --mode local

# Kubernetes apply walkthrough without endpoint smoke
./ops/guided-walkthrough.sh --mode k8s --skip-smoke

# Contracts-only validation
./ops/guided-walkthrough.sh --validate-only
```

## Manual Commands (Advanced / Non-guided)
Use this only if you need explicit step control.

Prerequisites:
- Docker + Docker Compose
- Git

```bash
git clone https://github.com/agnxxt/kernel-registry.git
cd kernel-registry

# Start local baseline
docker compose up --build -d

# Validate contracts
docker compose exec kernel-tooling bash -lc "./scripts/validate_schemas.sh && ./scripts/validate_proto.sh"

# Run DB migrations
docker compose exec kernel-tooling alembic -c persistence/alembic.ini upgrade head

# Run endpoint smoke test
./ops/e2e-smoke.sh

# Stop stack
docker compose down
```

## Quick Troubleshooting
| Symptom | Likely cause | Fix |
|---|---|---|
| `docker: command not found` | Docker is not installed/running | Install Docker Desktop/Engine and verify with `docker --version`. |
| `./ops/e2e-smoke.sh` fails with connection refused | Services are not started or not healthy yet | Run `docker compose ps`, wait for healthy services, then re-run smoke test. |
| `kubectl: command not found` | Kubernetes CLI is missing | Install `kubectl`, verify with `kubectl version --client`. |
| `Error from server (Forbidden)` on k8s apply | RBAC/namespace permissions insufficient | Use a context with apply rights for target namespace(s). |
| Migration command fails | DB container/tooling container not ready | Check `docker compose logs`, then retry migration step. |

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

## Deployment (Kubernetes Manual)

The Agent Kernel Platform is designed for multi-cloud and hybrid environments.

```bash
# Apply the core platform manifests
kubectl apply -f deploy/k8s/kernel-platform.yaml
kubectl apply -f deploy/k8s/production-hardening.yaml

# Apply specialized cognitive planes
kubectl apply -f deploy/k8s/model-runner/
kubectl apply -f deploy/k8s/secret-kernel.yaml
kubectl apply -f deploy/k8s/feast/
kubectl apply -f deploy/k8s/action-adapters.yaml
```

## Cognitive Features
This kernel implements state-of-the-art AI reliability frameworks:
- **RACF**: Rogue Agent Containment & Kill Switch.
- **Dual-Process Routing**: Fast vs. Slow thinking selection.
- **Epistemic Trust**: Dynamic credibility weighting.
- **Intelligent Authentication**: Reasoning-based access control.
- **Universal Schema**: Native Schema.org + JSON-LD interoperability.
