# Cognitive Bias Framework: Auditing & Correcting Agent Heuristics

Agents, like humans, are susceptible to systematic errors in reasoning. This framework formalizes how the Agent Kernel identifies, labels, and mitigates **Cognitive Biases** within the agent's decision-making loop.

---

## 1. Core Bias Taxonomy
These are represented as `System 1 / Fast Thinking` failure modes in the `dual_process_theory`.

### A. Recency Bias
The tendency to over-weight the importance of the most recent observations or messages.
*   **Kernel Impact**: Skews the `epistemic_trust` ledger. If Source X was right once 5 minutes ago, the agent ignores Source X's failure history from last week.
*   **Relational Edge**: `[Agent] -AFFLICTED_BY-> [RecencyBias]`

### B. Confirmation Bias
The tendency to search for, interpret, and favor information that confirms the agent's existing `Belief` nodes.
*   **Kernel Impact**: Skews `active_probe` selection. The agent only probes for data that supports its current hypothesis.
*   **Relational Edge**: `[Agent] -EXHIBITS-> [ConfirmationBias]`

### C. Availability Heuristic
Overestimating the importance of information that is "easy to recall" (e.g., highly indexed in the Knowledge Graph or recently fetched in a RAG window).
*   **Kernel Impact**: Modifies `InformationForagingTheory`. The agent stops searching once it finds "easy" matches, even if higher-precision data exists further in the graph.

---

## 2. Detection & Mitigation via the Harness

The `watchdog_role` in a **Self-Improving Harness** is responsible for detecting these biases by analyzing the `lineage` and `audit_tracking` of actions.

### Detection Mechanism:
*   **Recency Detection**: The harness calculates the `TemporalWeighting` of the agent's sources. If the weight is heavily skewed toward the last $N$ events, a `RecencyBias` flag is raised.
*   **Confirmation Detection**: The harness monitors the diversity of `active_probe` targets. If probes are restricted to a single subgraph that confirms a prior belief, a `ConfirmationBias` alert is issued.

### Autonomous Mitigation:
When a bias is detected, the harness issues an `UpdateAction` to the agent's `CognitiveProfile` or `DualProcessTheory` artifact:
*   **The Patch**: "Temporarily suspend `allowed_heuristic: recency_prioritization`" or "Mandate `active_probe: diversity_check`".

---

## 3. Universal Schema Mapping

| Bias Type | Universal Schema Location | Mitigation Action |
| :--- | :--- | :--- |
| **Recency Bias** | `semantic_extension.attributes.time_decay_rate` | Increase decay rate for recent events. |
| **Confirmation Bias** | `semantic_extension.taxonomy.labels` (Gating) | Force switch to `deep_pathway` (Slow Thinking). |
| **Availability Heuristic** | `semantic_extension.attributes.foraging_depth` | Increase minimum required RAG search depth. |

## JSON-LD Example: Labeling a Biased Decision

```json
{
  "@context": "https://schema.org",
  "@type": "AssessAction",
  "name": "Audit Log: Bias Detection",
  "agent": { "@type": "SoftwareApplication", "name": "Watchdog-01" },
  "object": { "@type": "SoftwareApplication", "name": "Target-Worker-Agent" },
  "semantic_extension": {
    "taxonomy": {
      "labels": ["bias_audit", "recency_bias_detected"]
    },
    "attributes": {
      "bias_score": 0.82,
      "evidence": "Agent ignored 3 historical contradictions in favor of the most recent (and false) status report."
    },
    "ontology": {
      "relations": [
        {
          "subject": "urn:agnxxt:agent:target-worker",
          "predicate": "AFFLICTED_BY",
          "object": "urn:agnxxt:theory:recency-bias"
        }
      ]
    }
  }
}
```
