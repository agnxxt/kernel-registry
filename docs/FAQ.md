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

### What does Temporal.io do in the kernel?
Temporal handles **Durable Cognition**. If an agent needs to perform a task that takes days (e.g., "Wait for a GitHub PR to be merged"), Temporal ensures the state is preserved even if the kernel restarts.

### Is my data safe in the Secret Vault?
Yes. The kernel uses **HashiCorp Vault** as its primary secret engine. Dynamic secrets can be generated and revoked automatically, ensuring zero-trust access to external tools like Slack and Jira.

---

## 🛡️ Security & Governance

### How are administrative actions secured?
All admin endpoints (`/admin/*`) are protected by **HTTP Basic Auth**, verified against the `SecretKernel` using your Master Key.

### Where are the safety rules defined?
Safety rules (Deontic Guardrails) are written in **Rego** and enforced by **Open Policy Agent (OPA)**. 
