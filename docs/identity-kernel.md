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
