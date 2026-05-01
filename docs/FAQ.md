# Agent Kernel FAQ

This document covers frequently asked questions regarding the deployment, configuration, and expansion of the Agent Kernel.

## 🚀 Deployment & Setup

### How do I start the kernel for the first time?
Simply run `docker compose up --build -d`. The system will detect it is uninitialized and guide you through a Setup Wizard at `http://localhost:3000`.

### What happened to the `.env` file?
Most secrets (OpenAI keys, GitHub tokens) are now stored securely in **HashiCorp Vault**, with an encrypted Postgres fallback. You only need the `KERNEL_MASTER_KEY` to bootstrap.

---

## 🛠️ Sovereign Infrastructure

### What is the "Consensus Engine"?
For high-risk actions (impact > 7), the kernel requires a "Consensus" vote from a group of agents using a BFT-style majority logic. This prevents a single compromised agent from taking destructive actions.

### How do Agent Wallets work?
The kernel integrates with an **Anvil (Ethereum)** node. Each agent is assigned a unique blockchain address. This allows them to hold funds, pay for their own API usage, and participate in reputational staking.

### What is the "Watchdog Responder"?
The **Watchdog Responder** is the active component of the immune system. While OpenTelemetry collects data, the Responder listens to the event bus in real-time. If a violation is detected (e.g., an OPA block), it automatically:
1. **Lowers** the agent's trust score.
2. **Suspends** the agent's lifecycle in the registry.
3. **Notifies** admins via Slack/Webhooks.
4. **Broadcasts** a rogue alert to other agents.

---

## 🛡️ Security & Governance

### How are administrative actions secured?
All admin endpoints (`/admin/*`) are protected by **HTTP Basic Auth**, verified against the `SecretKernel` using your Master Key.

### Where are the safety rules defined?
Safety rules (Deontic Guardrails) are written in **Rego** and enforced by **Open Policy Agent (OPA)**. 
