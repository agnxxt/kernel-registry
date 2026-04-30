# Schema.org Alignment for Cognitive Artifacts

To ensure interoperability and semantic discoverability, we map our internal Cognitive and Reliability artifacts to formal **Schema.org** types. This allows the Agent Kernel to speak the "common language" of the web while maintaining high-precision engineering contracts.

## Mapping Taxonomy

| Kernel Artifact Kind | Schema.org Type | Semantic Rationale |
| :--- | :--- | :--- |
| `active_probe` | `AssessAction` | Probes are empirical assessments of a target's state or latency. |
| `epistemic_trust` | `AssessAction` | Evaluation of credibility is a form of cognitive assessment. |
| `predictive_control` | `PlanAction` / `ControlAction` | Look-ahead simulations are part of the planning and control loop. |
| `active_inference` | `AssessAction` | Minimizing surprise requires constant assessment of world-model alignment. |
| `dual_process_theory` | `ControlAction` | Managing cognitive routing (Fast vs. Slow) is a meta-control action. |
| `cognitive_profile` | `Intangible` / `PropertyValue` | The profile itself is an intangible set of properties defining the agent. |
| `bdi_architecture` | `PlanAction` | Intentions are formalized plans based on beliefs and desires. |

## JSON-LD Example

By wrapping our artifacts in a Schema.org envelope, they become machine-readable by standard semantic crawlers and registries.

```json
{
  "@context": "https://schema.org",
  "@type": "AssessAction",
  "name": "Credibility Assessment of Peer Agent",
  "agent": { "@type": "SoftwareApplication", "name": "Auditor-01" },
  "object": { "@type": "SoftwareApplication", "name": "External-Data-Provider" },
  "kernel_artifact": {
    "artifact_kind": "epistemic_trust",
    "mapping_logic": "Evaluation of trust score based on previous interaction consistency."
  },
  "actionStatus": "CompletedActionStatus",
  "result": {
    "name": "Trust Score Update",
    "value": 0.85
  }
}
```

## Schema Reference
- `schemas/runtime/schemaorg-cognitive-bridge.schema.json`
