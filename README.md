# Agent Kernel Platform

**Version: 1.0.4-stable**

The Agent Kernel is a high-reliability, model-agnostic governance layer for Frontier AI Agents. It provides:
- **Deontic Guardrails**: Policy enforcement via Open Policy Agent (OPA).
- **Persistent Memory**: Durable storage of identities, trust, and decisions in Postgres.
- **Physical Adapters**: Governed execution for GitHub, Slack, and Jira.
- **Cognitive Control Plane**: Real-time observability and policy management.

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

## 🏗️ Architecture
- `kernel_api/`: FastAPI entrypoint and admin routes.
- `kernel_engine/`: Cognitive orchestrator, model runner, and adapters.
- `kernel_ui/`: Next.js dashboard and telemetry visualizer.
- `persistence/`: SQLAlchemy models and Alembic migrations.
- `policies/`: OPA Rego contracts.

---
© 2026 Agent Kernel Team | research@agnxxt.com
