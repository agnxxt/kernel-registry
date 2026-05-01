# Agent Kernel Platform

**Version: 1.0.4-stable**

The Agent Kernel is a high-reliability, model-agnostic governance layer for Frontier AI Agents. It provides:
- **Deontic Guardrails**: Policy enforcement via Open Policy Agent (OPA).
- **Persistent Memory**: Durable storage of identities, trust, and decisions in Postgres.
- **Physical Adapters**: Governed execution for GitHub, Slack, and Jira.
- **Cognitive Control Plane**: Real-time observability and policy management.

**[Read the Project FAQ](./docs/FAQ.md)**

## 🚀 Quickstart

### 1. Prerequisites
- Docker + Docker Compose
- OpenAI/Anthropic API Keys
- GitHub/Slack/Jira Tokens (optional for physical execution)

### 2. Configuration
Create a `.env` file in the root:
```env
KERNEL_MASTER_KEY=your_secure_admin_password
DATABASE_URL=postgresql+psycopg2://kernel:kernelpass@postgres:5432/kernel
GITHUB_TOKEN=your_github_token
SLACK_TOKEN=your_slack_token
JIRA_API_KEY=your_jira_key
JIRA_EMAIL=your_email
MOCK_INFERENCE=false
```

### 3. Launch
```bash
docker compose up --build -d
```

### 4. Access the Dashboard
- **Control Plane**: http://localhost:3000
- **Kernel API**: http://localhost:8000
- **Policy Editor**: http://localhost:3000/policies
- **Identity Manager**: http://localhost:3000/identity

*Note: Administrative endpoints require Basic Auth (Username: `admin`, Password: your `KERNEL_MASTER_KEY`).*

## 🛡️ Governance (OPA)
The kernel uses OPA to enforce safety. Policies are defined in `policies/kernel.rego`. You can update guardrails in real-time via the **Policy Editor** in the dashboard.

## 🧪 Testing
Run the full E2E cognitive lifecycle test:
```bash
pytest tests/e2e/test_platform_flow.py
```
Or verify authentication:
```bash
pytest tests/unit/test_auth.py
```

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
## 🏗️ Architecture
- `kernel_api/`: FastAPI entrypoint and admin routes.
- `kernel_engine/`: Cognitive orchestrator, model runner, and adapters.
- `kernel_ui/`: Next.js dashboard and telemetry visualizer.
- `persistence/`: SQLAlchemy models and Alembic migrations.
- `policies/`: OPA Rego contracts.
---
© 2026 Agent Kernel Team | research@agnxxt.com
