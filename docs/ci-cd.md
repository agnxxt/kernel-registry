# CI/CD

## CI (PR + main)
Workflow: `.github/workflows/ci.yml`
- JSON schema validation
- Proto structural validation
- Buf proto linting (`buf lint`)
- JSON schema backward compatibility checks (`scripts/check_schema_compat.py`)
- Alembic migration syntax checks

## Main branch smoke
Workflow: `.github/workflows/ci.yml` (`smoke` job)
- Creates ephemeral `kind` cluster
- Runs server-side dry-run applies for platform manifests

## Release
Workflow: `.github/workflows/release.yml`
- Trigger: `v*` tags or manual dispatch
- Produces build metadata artifact
- Attests build provenance using GitHub artifact attestations (SLSA-aligned)
- Performs keyless `cosign` signature for build metadata archive
- Placeholder step for image publish

## Future hardening ideas
1. Enforce `buf breaking` checks against module history.
2. Add policy checks for Kubernetes manifests (Kyverno/OPA conftest).
3. Add container image SBOM generation and vulnerability gating.
4. Promote cosign signatures from build metadata to pushed container images.
