# CI/CD

## CI (PR + main)
Workflow: `.github/workflows/ci.yml`
- JSON schema validation
- Proto structural validation
- Alembic migration syntax checks

## Release
Workflow: `.github/workflows/release.yml`
- Trigger: `v*` tags or manual dispatch
- Produces build metadata artifact
- Placeholder step for image publish

## Next hardening steps
1. Add buf/protolint for strict proto linting.
2. Add JSON schema compatibility tests (backward checks).
3. Add ephemeral k3s/kind deploy smoke test.
4. Add signed artifact/container provenance (SLSA/cosign).
