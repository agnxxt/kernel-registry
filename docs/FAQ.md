# Agent Kernel FAQ

This document covers frequently asked questions regarding the deployment, configuration, and expansion of the Agent Kernel.

## 🚀 Deployment & Setup

### How do I start the kernel for the first time?
Simply run `docker compose up --build -d`. The system will detect it is uninitialized and guide you through a Setup Wizard at `http://localhost:3000`.

### What happened to the `.env` file?
While you can still use a `.env` file for bootstrap variables, the kernel now supports a **Guided UI Setup**. Most secrets (OpenAI keys, GitHub tokens) are now stored securely and encrypted in the Postgres database, so you don't have to manage flat files.

### How do I switch from "Mock" to "Real" intelligence?
During the Setup Wizard, or by updating the database, set `MOCK_INFERENCE` to `false` and provide a valid API key for OpenAI or a URL for a local provider like Ollama.

---

## 🛠️ Development & Expansion

### How difficult is it to add a new Schema?
**Difficulty: Low (2/10).** 
1. Create a `.schema.json` file in `schemas/`.
2. Ensure it includes a `$ref` to `_semantic-extension.schema.json`.
3. Run `./scripts/validate_schemas.sh`.
The kernel's validator will automatically recognize and enforce the new schema.

### How do I add a new Tool Adapter (e.g., Teams, Jira)?
1. Create a new adapter class in `kernel_engine/adapters/`.
2. Register the routing logic in `kernel_engine/executor.py`.
3. Add any required SDKs to `persistence/requirements.txt`.

### Does the system survive restarts?
**Yes.** Unlike the initial prototype which used in-memory mocks, v1-stable uses **Postgres** for all stateful data:
- Agent Identities & Trust Scores
- Action Knowledge Graph
- Execution Decisions & Evidence
- User Feedback & Improvement Proposals

---

## 🛡️ Security & Governance

### How are administrative actions secured?
All admin endpoints (`/admin/*`) and the Setup Wizard are protected by **HTTP Basic Auth**. The credentials are verified against the `SecretKernel` using your Master Key.

### Where are the safety rules defined?
Safety rules (Deontic Guardrails) are written in **Rego** and enforced by **Open Policy Agent (OPA)**. You can find them in `policies/kernel.rego`. These can be updated in real-time via the **Policy Editor** in the dashboard.

### Can I use Open Source/Local LLMs?
**Yes.** The kernel is vendor-agnostic. During setup, choose "Open Source (Local)" to point the kernel to an Ollama or vLLM instance. This ensures your data and reasoning stay on your own hardware.

---

## 🧪 Testing & Validation

### How do I verify the system is working?
Run the E2E smoke test:
```bash
pytest tests/e2e/test_platform_flow.py
```
This validates the entire chain: Action -> OPA Check -> Execution -> DB Persistence.

### How do I check if my schemas are valid?
Run the validation script:
```bash
./scripts/validate_schemas.sh
```
It will check all JSON files in the `schemas/` directory for syntax errors and cross-reference integrity.
