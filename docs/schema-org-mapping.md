# Schema.org Unified Cognitive Mapping

The Agent Kernel strictly adheres to the principle of **One Universal Schema**. 

Instead of maintaining fragmented, custom JSON schemas for individual cognitive theories (like Active Inference or Dual Process Theory), the kernel represents **all cognitive operations as standard Schema.org Actions**. The specific structural requirements of a cognitive theory are injected safely into the standard `semantic_extension` block defined in `schemas/_semantic-extension.schema.json`.

## Universal Mapping Taxonomy

| Cognitive Concept | Schema.org `@type` | Semantic Rationale |
| :--- | :--- | :--- |
| `active_probe` | `AssessAction` | Probes are empirical assessments of a target's state or latency. |
| `epistemic_trust` | `AssessAction` | Evaluation of source credibility is a cognitive assessment. |
| `predictive_control` | `PlanAction` / `ControlAction` | Look-ahead simulations are part of the planning/control loop. |
| `active_inference` | `AssessAction` | Minimizing surprise requires constant assessment of world-model alignment. |
| `dual_process_theory`| `ControlAction` | Managing cognitive routing (Fast vs. Slow) is a meta-control action. |
| `bdi_architecture` | `PlanAction` | Intentions are formalized plans based on beliefs and desires. |

## Universal JSON-LD Example

By wrapping our artifacts strictly within the universal Schema.org envelope, they remain machine-readable by standard semantic crawlers while providing the rigorous type safety required for internal kernel operations.

```json
{
  "@context": "https://schema.org",
  "@type": "AssessAction",
  "name": "Credibility Assessment of Peer Agent",
  "actionStatus": "CompletedActionStatus",
  "agent": { "@type": "SoftwareApplication", "name": "Auditor-01" },
  "object": { "@type": "SoftwareApplication", "name": "External-Data-Provider" },
  "semantic_extension": {
    "taxonomy": {
      "labels": ["epistemic_trust", "cognitive_evaluation"]
    },
    "attributes": {
      "baseline_trust": 0.5,
      "validation_reward": 0.05,
      "betrayal_penalty": 0.4,
      "assimilation_policy": "bayesian_update",
      "observation_feedback_loop": {
        "action_alignment_check": true
      }
    }
  },
  "result": {
    "@type": "PropertyValue",
    "name": "Trust Score Update",
    "value": 0.85
  }
}
```

## Schema References
- Universal Action Envelope: `schemas/actions/schemaorg-actions.schema.json`
- Extension Mechanism: `schemas/_semantic-extension.schema.json`
