# Agent Kernel FAQ

This document covers frequently asked questions regarding the deployment, configuration, and expansion of the Agent Kernel.

## 🚀 Deployment & Setup

### How do I start the kernel for the first time?
Simply run `docker compose up --build -d`. The system will detect it is uninitialized and guide you through a Setup Wizard at `http://localhost:3000`.

---

## 🛡️ Governance & CAAS

### What is CAAS?
**CAAS** stands for **Continuous Autonomous Authorization System**. It is the kernel's primary security layer, providing real-time, zero-trust authorization for agents. It combines:
- **ReBAC (OpenFGA)**: Relationship-based access control.
- **ABAC (OPA)**: Attribute-based policy enforcement.
- **Cognitive Guard Layer**: Intent validation, Chain-of-Thought (CoT) auditing, and drift scoring.

### What is CAI?
**CAI** stands for **Cybersecurity AI**. It is the framework used to build and manage the agents themselves, ensuring they follow the ReACT model and include built-in guardrails against prompt injection and malicious behavior.

### Where are the safety rules defined?
Safety rules (Deontic Guardrails) are written in **Rego** and enforced by **Open Policy Agent (OPA)** via the CAAS gateway.

---

## 🛠️ Sovereign Infrastructure

### What is the "Consensus Engine"?
For high-risk actions (impact > 7), the kernel requires a "Consensus" vote from a group of agents using a BFT-style majority logic. 

### How do Agent Wallets work?
The kernel integrates with an **Anvil (Ethereum)** node. Each agent is assigned a unique blockchain address for resource micropayments.

### What is the "Watchdog Responder"?
The **Watchdog Responder** is the active component of the immune system. It listens to the event bus and automatically remediates policy violations (e.g., suspending agents or revoking secrets).
