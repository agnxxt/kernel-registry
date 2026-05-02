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

## ⚖️ Why Not Just Use Agent Frameworks?

Frameworks focus on reasoning. This focuses on control.

---

## ⚡ Core Capabilities

- Policy enforcement (OPA)
- Persistent memory
- Controlled execution
- Observability

---

## 🌉 Runtime Bridges

AGenNext Kernel provides language-agnostic bridge templates for integrating external runtimes. See [integrations/runtime-bridges](/integrations/runtime-bridges/) for Python, Node.js, Go, Java, .NET, and Rust templates.

---

## 🚀 Quickstart

```bash
docker compose up --build -d
```

---

## 🛡️ Policy Example

```rego
package kernel

allow {
  input.task == "create_github_issue"
}
```

---

## 📚 Docs

See /docs folder

---

© 2026 Agent Kernel Team
