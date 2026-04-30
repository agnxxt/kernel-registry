# Secret Management as Kernel Service

`secret-kernel` is a first-class kernel control-plane service.

## Responsibility
- Multi-provider secret storage abstraction
- Access control by kernel scope
- Rotation/revocation lifecycle
- Immutable audit events

## Providers
- Vault
- AWS KMS
- GCP KMS
- Azure Key Vault
- Kubernetes Secrets (fallback)

## Scope model
- global
- org
- project
- agent
- task

## Security posture
- No plaintext secrets in app config repos
- Secret reads are policy-gated and auditable
- Rotation events published to `kernel.secrets.rotation.v1`
- Access events published to `kernel.secrets.audit.v1`
