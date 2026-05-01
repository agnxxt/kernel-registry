# Kernel Hardening Checklist

## Runtime
- [ ] All images pinned by digest
- [ ] Liveness/readiness/startup probes enabled
- [ ] Resource requests/limits set per workload
- [ ] PodDisruptionBudgets applied

## State
- [ ] Persistent volumes for Postgres/Redis/Qdrant/MinIO/NATS streams
- [ ] Backup schedule configured
- [ ] Restore drill documented and tested

## Reliability
- [ ] E2E smoke test included in release validation
- [ ] Retry + timeout + circuit-breaker defaults documented
- [ ] DLQ topics configured for async pipelines
- [ ] Idempotency keys required on mutating APIs

## Security
- [ ] NetworkPolicies enforced
- [ ] Secrets moved from plain env to secret store
- [ ] RBAC least privilege for service accounts

## Observability
- [ ] SLO dashboard created from benchmark scorecard
- [ ] Alert rules for error budget burn + restart storm
- [ ] Change-impact report generated after each deployment
