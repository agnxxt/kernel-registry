# Deployment Plan - Agent Kernel

## Status: Execution

## Phase 1: Planning
- [x] 1. Analyze Workspace: Multi-component application (FastAPI, Next.js, Postgres, OPA, MLflow).
- [x] 2. Gather Requirements: Production-ready, secure, scalable. Target: Azure.
- [x] 3. Scan Codebase: 
    - `kernel-api`: FastAPI (Python 3.12)
    - `kernel-ui`: Next.js (Node.js 24)
    - `postgres`: PostgreSQL 16
    - `opa`: Open Policy Agent
    - `mlflow`: MLflow v2.20.1
    - `caddy`: Reverse proxy (can be handled by ACA Ingress)
- [x] 4. Select Recipe: **AZD (Azure Developer CLI)** with **Bicep**.
- [x] 5. Plan Architecture:
    - **Azure Container Apps (ACA)** for `kernel-api`, `kernel-ui`, `mlflow`, and `opa`.
    - **Azure Database for PostgreSQL (Flexible Server)** for persistence.
    - **Azure Container Registry (ACR)** for image management.
    - **Managed Identity** for zero-trust authentication between components.
    - **Key Vault** for secret management.
    - **Log Analytics** for observability.
- [x] 6. Finalize Plan

## Phase 2: Execution
- [ ] 1. Research Components
- [ ] 2. Confirm Azure Context
- [ ] 3. Generate Artifacts
- [ ] 4. Harden Security
- [ ] 5. Functional Verification
- [ ] 6. Update Plan Status
- [ ] 7. Hand Off to Validation
