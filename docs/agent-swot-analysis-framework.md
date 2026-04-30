# SWOT Analysis Framework: Strategic Perception in Agents

This framework formalizes how an agent evaluates its own capabilities and its external environment. Unlike static metadata, an agent's SWOT is a **perceived state**—it represents what the agent *believes* is true about its strategic position.

---

## 1. SWOT Dimensions in the Kernel

### A. Perceived Strengths (Internal/Positive)
Capabilities, resources, or specialized skills the agent believes it possesses.
*   **Kernel Impact**: Informs `DualProcessTheory`. An agent with high perceived strength in `data_parsing` will prefer the "Fast/System 1" pathway for those tasks.
*   **Relational Edge**: `[Agent] -CLAIMS_STRENGTH-> [Skill/Artifact]`

### B. Perceived Weaknesses (Internal/Negative)
Limitations, skill gaps, or reliability issues the agent recognizes in itself.
*   **Kernel Impact**: Triggers `active_probe` or `CollaborativeTopology`. An agent aware of its weakness in `medical_emergency` logic will automatically request a `peer_review` from a specialist agent.
*   **Relational Edge**: `[Agent] -ACKNOWLEDGES_WEAKNESS-> [Skill/Logic]`

### C. Perceived Opportunities (External/Positive)
Environmental conditions, available tools, or peer collaborations that can be exploited to achieve goals.
*   **Kernel Impact**: Modifies `BargainingTheory` and `ActiveInference`. The agent acts to exploit these opportunities to minimize "surprise" or maximize utility.
*   **Relational Edge**: `[Agent] -SENSES_OPPORTUNITY-> [Context/Event]`

### D. Perceived Threats (External/Negative)
Risks, biases, or competitive agents that could compromise the agent's reliability or goal success.
*   **Kernel Impact**: Mandates `PredictiveControl` and "Slow Thinking." Any action impacted by a `PerceivedThreat` requires mandatory simulation before execution.
*   **Relational Edge**: `[Agent] -DETECTS_THREAT-> [Context/Agent]`

---

## 2. Universal Schema Mapping

| SWOT Dimension | Schema.org `@type` | Semantic Extension Block |
| :--- | :--- | :--- |
| **Full SWOT** | `AssessAction` | `attributes.perceived_swot` |
| **Strengths** | `PropertyValue` | `attributes.strength_score` |
| **Threats** | `SpecialAnnouncement` | `attributes.risk_vector` |

## JSON-LD Example: A Self-SWOT Assessment

```json
{
  "@context": "https://schema.org",
  "@type": "AssessAction",
  "name": "Internal Strategic SWOT",
  "agent": { "@type": "SoftwareApplication", "name": "Worker-Alpha-01" },
  "semantic_extension": {
    "taxonomy": { "labels": ["swot_analysis", "self_perception"] },
    "attributes": {
      "perceived_swot": {
        "strengths": ["high_token_efficiency", "reliable_sql_generation"],
        "weaknesses": ["unreliable_sentiment_detection"],
        "opportunities": ["access_to_real_time_weather_api"],
        "threats": ["high_recency_bias_score_detected_by_harness"]
      }
    },
    "audit_tracking": {
      "created_at": "2026-04-29T12:00:00Z",
      "change_reason": "Periodic self-assessment"
    }
  }
}
```

## The Self-Improving SWOT
A self-improving harness monitors the delta between **Perceived Strength** and **Actual Performance**. If an agent *thinks* it is strong in a skill but consistently fails the `ReliabilityBench`, the harness issues a `meta_representation` patch to correct the agent's "Inflated Ego" (overconfidence bias).
