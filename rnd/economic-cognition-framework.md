# Economic Cognition Framework: Time Value of Money and Opportunity Cost

This framework defines how agents apply economic reasoning to their own operations and interactions. By treating time and resources as finite and value-decaying, the agent becomes a more efficient and strategically aligned autonomous unit.

---

## 1. Time Value of Money (TVM) in Cognition
The principle that a resource (tokens, compute, capital) available *now* is worth more than the same resource in the *future* due to its potential earning or utility capacity.

*   **Kernel Impact**: Modifies `DualProcessTheory` and `ActionStatus`. 
    *   **The "Urgency Scalar"**: If a task has a high `TVM_impact`, the agent increases its `curiosity_override` to ensure immediate processing, bypassing lower-priority sequential tasks.
*   **Attributes**: `discount_rate_per_hour`, `compounding_utility_flag`.
*   **Relational Edge**: `[Action] -HAS_TVM_IMPACT-> [MonetaryAmount/Utility]`

## 2. Opportunity Cost (The Path Not Taken)
The value of the next best alternative that is forgone when a specific action or strategy is chosen.

*   **Kernel Impact**: Central to `NegotiationTheory` and `BargainingTheory`.
    *   **The "Alternative Benefit Audit"**: Before committing to a high-latency `PlanAction`, the agent must calculate the `opportunity_cost` (e.g., "If I spend 10,000 tokens on this deep research, I cannot process the other 5 incoming user requests").
*   **Attributes**: `forgone_utility_score`, `alternative_artifact_ref`.
*   **Relational Edge**: `[Action] -FORGOES-> [AlternativeAction/Artifact]`

---

## 3. Universal Schema Mapping

| Economic Concept | Schema.org `@type` | Semantic Extension Block |
| :--- | :--- | :--- |
| **TVM** | `MonetaryAmount` / `Duration` | `attributes.utility_decay_curve` |
| **Opportunity Cost** | `TradeAction` | `attributes.forgone_benefit`, `attributes.alternative_ref` |

## JSON-LD Example: Calculating Opportunity Cost for Resource Allocation

```json
{
  "@context": "https://schema.org",
  "@type": "AssessAction",
  "name": "Economic Audit: Resource Allocation Trade-off",
  "agent": { "@type": "SoftwareApplication", "name": "Strategic-Planner-01" },
  "semantic_extension": {
    "taxonomy": { "labels": ["economic_cognition", "opportunity_cost_analysis"] },
    "attributes": {
      "chosen_action": "urn:agnxxt:action:deep-market-sim-99",
      "opportunity_cost": {
        "forgone_action": "urn:agnxxt:action:real-time-arbitrage-55",
        "forgone_utility": 0.85,
        "rationale": "High-fidelity simulation requires 100% of GPU-VRAM, preventing real-time arbitrage for the next 4 hours."
      },
      "time_value_discount": {
        "delay_penalty": 0.05,
        "unit": "per_minute"
      }
    },
    "ontology": {
      "relations": [
        {
          "subject": "urn:agnxxt:action:deep-market-sim-99",
          "predicate": "FORGOES",
          "object": "urn:agnxxt:action:real-time-arbitrage-55"
        }
      ]
    }
  }
}
```

## Self-Improving Economic Harness
The harness monitors an agent's `EpisodicMemory`. If an agent consistently chooses actions where the **Realized Utility** is lower than the **Opportunity Cost** of the alternatives, the harness issues an `UpdateAction` to the agent's `CognitiveProfile`, increasing its `skepticism_level` regarding high-latency tasks.
