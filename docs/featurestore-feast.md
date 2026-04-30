# Feature Store Integration (Feast)

Kernel-level feature store service uses Feast-compatible contracts.

## Kernel service
- gRPC service: `FeatureStoreKernel`
- Methods:
  - `GetOnlineFeatures`
  - `Materialize`

## Backing stores
- Online: Redis
- Offline: Postgres
- Registry: file/sqlite (bootstrap), then migrate to production backend as needed

## Audit
- Topic: `kernel.featurestore.audit.v1`
- Events: online fetch/materialize/deny

## Multi-tenant model
- `tenant_id` + `project` partitioning
- Keying for audit events: `tenant_id:project:entity_name:entity_id`
