# Architecture

## Overview

AGenNext Kernel is composed of five core layers:

```
[ Client / Agent ]
          ↓
[ Kernel API (FastAPI) ]
          ↓
[ Policy Engine (OPA) ]
          ↓
[ Kernel Engine ]
          ↓
[ Adapters (GitHub, Slack, Jira) ]
          ↓
[ Persistence (Postgres) ]
```

## Components

### Kernel API
Handles incoming requests, authentication, and routing.

### Policy Engine (OPA)
Evaluates whether an action is allowed before execution.

### Kernel Engine
Orchestrates task execution and decision lifecycle.

### Adapters
Connect to external systems safely.

### Persistence Layer
Stores decisions, identities, and audit logs.

## Key Principle

**No action is executed without policy evaluation.**
