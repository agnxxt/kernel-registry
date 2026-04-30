# Schema.org Unified Cognitive Mapping

The Agent Kernel strictly adheres to the principle of **One Universal Schema**. 

Instead of maintaining fragmented, custom JSON schemas for individual cognitive theories (like Active Inference or Dual Process Theory), the kernel represents **all cognitive operations as standard Schema.org Actions**. 

When a concept is not fully supported by Schema.org natively, we select the **closest standard type** (e.g., `AssessAction`, `ControlAction`) and inject our internal precision using a universal `semantic_extension` block.

## The Semantic Extension Block
The `semantic_extension` provides absolute rigor for enterprise and cognitive AI workloads by enforcing:
1. **Schema**: Explicit linking to internal structural rules and fallback references.
2. **Taxonomy & Ontology**: Hierarchical and relational categorization.
3. **Vocabulary**: Domain-specific term definitions and URIs.
4. **Attributes**: Custom cognitive state fields (e.g., trust scores, risk thresholds).
5. **Lineage**: Provenance tracking (where the data/belief came from and how it was transformed).
6. **Metadata**: Additional unstructured context.
7. **Versioning & Audit Tracking**: Strict mutation logs, timestamping, authorship, and cryptographic signatures.

## Universal Mapping Taxonomy

| Cognitive Concept | Schema.org `@type` | Semantic Rationale |
| :--- | :--- | :--- |
| `active_probe` | `AssessAction` | Probes are empirical assessments of a target's state or latency. |
| `epistemic_trust` | `AssessAction` | Evaluation of source credibility is a cognitive assessment. |
| `predictive_control` | `PlanAction` / `ControlAction` | Look-ahead simulations are part of the planning/control loop. |
| `active_inference` | `AssessAction` | Minimizing surprise requires constant assessment of world-model alignment. |
| `dual_process_theory`| `ControlAction` | Managing cognitive routing (Fast vs. Slow) is a meta-control action. |
| `bdi_architecture` | `PlanAction` | Intentions are formalized plans based on beliefs and desires. |
| `deontic_constraints`| `Policy` | Formal boundaries defining what is obligated, permitted, or forbidden, operating entirely independently of goal-seeking logic. |
| `consensus_topology` | `ActionAccessSpecification` | Defines structural redundancy and voting mechanisms (e.g., Majority Voting) requiring multi-agent agreement before execution. |
| `watchdog_role`      | `Role` | An independent oversight identity solely responsible for detecting error propagation ("hallucination snowballs") and triggering rollbacks. |
| `global_workspace`   | `CommunicateAction` | Implementation of "broadcast competition" where high-priority info is shared globally across subsystems. |
| `attention_schema`   | `ControlAction` | A model of the agent's own focus, enabling self-regulation of attentional states. |
| `meta_representation`| `AssessAction` | Evaluation or secondary representation of the agent's own primary cognitive outputs. |

## Universal JSON-LD Example

By wrapping our artifacts strictly within the universal Schema.org envelope, they remain machine-readable by standard semantic crawlers while providing the rigorous type safety, lineage, and audit trails required for internal kernel operations.

```json
{
  "@context": "https://schema.org",
  "@type": "AssessAction",
  "name": "Credibility Assessment of Peer Agent",
  "actionStatus": "CompletedActionStatus",
  "agent": { "@type": "SoftwareApplication", "name": "Auditor-01" },
  "object": { "@type": "SoftwareApplication", "name": "External-Data-Provider" },
  "semantic_extension": {
    "schema_definition": {
      "id": "urn:agnxxt:schema:epistemic-trust",
      "version": "2.0.0",
      "fallback_schema_org_type": "AssessAction"
    },
    "versioning": {
      "semantic_version": "1.1.0",
      "iteration_hash": "a1b2c3d4e5f6"
    },
    "taxonomy": {
      "labels": ["epistemic_trust", "cognitive_evaluation"]
    },
    "attributes": {
      "baseline_trust": 0.5,
      "assimilation_policy": "bayesian_update"
    },
    "lineage": {
      "source_artifacts": ["urn:agnxxt:event:interaction-1044"],
      "transformation_logic": "Bayesian update following action alignment check."
    },
    "audit_tracking": {
      "updated_by": "Auditor-01",
      "updated_at": "2026-04-29T10:00:00Z",
      "change_reason": "Source failed to act on reported information.",
      "cryptographic_signature": "sig_99x88y77z"
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
