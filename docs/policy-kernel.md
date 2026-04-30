# Policy Kernel (OPA + OpenFGA)

Kernel policy control plane supports:
- OPA for contextual policy evaluation (ABAC/rules)
- OpenFGA for relationship authorization (ReBAC)

Contracts:
- `schemas/policy/opa-policy-bundle.schema.json`
- `schemas/policy/openfga-tuple-write.schema.json`
- `schemas/policy/policy_control.proto`

Runtime sequence:
1. Pre-tool hook calls policy decision endpoint.
2. Kernel evaluates via OPA and/or OpenFGA.
3. Decision (`allow/deny`) and obligations are returned.
