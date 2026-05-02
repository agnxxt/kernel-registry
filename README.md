# AGenNext Kernel

**Version: 1.0.4-stable**

AGenNext Kernel is a governance-first runtime for AI agents. It provides enforceable policy control, persistent memory, and safe execution across external systems like GitHub, Slack, and Jira.

---

## 🧠 What This Solves

AI agents can act—but without structure they are:
- Unsafe (no policy enforcement)
- Stateless (no memory of decisions)
- Opaque (no observability)

AGenNext Kernel introduces a controlled execution layer that makes agents auditable, governable, and production-ready.

---

## ⚡ Core Capabilities

- **Deontic Guardrails** → Policy enforcement via Open Policy Agent (OPA)
- **Persistent Memory** → Identity + decision tracking in Postgres
- **Physical Adapters** → Controlled execution (GitHub, Slack, Jira)
- **Cognitive Control Plane** → Observability + real-time control

---

## 🚀 Quickstart

### 1. Setup

```bash
git clone https://github.com/AGenNext/AGenNext-Kernel.git
cd AGenNext-Kernel
```

### 2. Configure

Create `.env`:

```env
KERNEL_MASTER_KEY=admin_password
DATABASE_URL=postgresql+psycopg2://kernel:kernelpass@postgres:5432/kernel
MOCK_INFERENCE=false
```

### 3. Run

```bash
docker compose up --build -d
```

### 4. Access

- UI → http://localhost:3000
- API → http://localhost:8000

---

## 🧪 First Execution

```bash
curl -X POST http://localhost:8000/execute \
  -H "Authorization: Basic <base64>" \
  -H "Content-Type: application/json" \
  -d '{"task": "Create issue"}'
```

---

## 🧠 How It Works

1. Task received
2. Policy evaluated (OPA)
3. Decision persisted
4. Action executed
5. Telemetry logged

---

## 📚 Docs

- docs/onboarding.md
- docs/api.md
- docs/concepts.md
- docs/deployment.md

---

## 🏗️ Architecture

- kernel_api/
- kernel_engine/
- kernel_ui/
- persistence/
- policies/

---

© 2026 Agent Kernel Team
