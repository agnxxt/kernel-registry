# Identity Kernel Primitives

Kernel-level identity is based on two primitives:

1. Canonical ID (`canonical_id`)
- Stable internal ID across systems/scopes.
- Format: `cid:<namespace>:<id>`

2. Verifiable Credential (VC)
- Attestable claims bound to holder canonical ID.
- Includes issuer, proof type, status, and credential hash.

## Usage
- Every kernel action must carry `canonical_id`.
- Credentials are referenced in `verifiable_credentials` for authorization and trust checks.

## Blockchain Wallet
- Wallets are linked to canonical IDs.
- Verification status and chain/network are tracked.

## Trust Score
- Normalized score: `0..1` with tier classification.
- Versioned scoring model and evidence references.

## Registry
- Canonical registry record tracks lifecycle status (`active/suspended/revoked/archived`).

## Resource identity rule
Every kernel resource is an identity subject, not only agents and users. The canonical resource identity envelope is `schemas/identity/resource-identity.schema.json`, which applies to agents, humans, groups, roles, permissions, models, tools, workflows, tasks, runs, steps, decisions, options, actions, risks, constraints, assumptions, claims, evidence, policies, evaluations, outcomes, memories, artifacts, datasets, secrets, hooks, events, topics, schemas, services, deployments, approvals, competencies, capabilities, and authority levels.

This makes authorization and audit decisions graph-native: policy engines can evaluate `canonical_id`, `resource_type`, tenant, owner, parent, status, sensitivity classification, and relationship edges for every object in the kernel.
