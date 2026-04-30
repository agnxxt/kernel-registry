# Strategic Interaction Framework: Game Theory, Negotiation, and Bargaining

This document outlines how the Agent Kernel formalizes strategic interactions between agents. By treating interaction models as versioned artifacts, the kernel enables agents to select the optimal mathematical or psychological framework for a given transaction.

---

## 1. Game Theory Implementation
Game theory artifacts define the structural rules and payoff matrices of multi-agent interactions.

*   **Zero-Sum vs. Non-Zero-Sum**: Defines if the interaction is purely competitive or potentially collaborative.
*   **Nash Equilibrium Pursuit**: A `ControlAction` where the agent attempts to find a stable strategy state where no agent can benefit by changing their strategy unilaterally.
*   **Mechanism Design**: Defining rules so that the agent's self-interest aligns with the system's global goals (e.g., Auction models).

## 2. Negotiation Theories
Negotiation artifacts define the "Strategic Dialogue" process.

*   **BATNA (Best Alternative to a Negotiated Agreement)**: A required attribute in the `semantic_extension` that defines the agent's walk-away point.
*   **ZOPA (Zone of Possible Agreement)**: The overlapping range where both agents' requirements are met.
*   **Integrative vs. Distributive**:
    *   *Integrative*: "Expanding the pie" (creating value).
    *   *Distributive*: "Slicing the pie" (fixed-resource bargaining).

## 3. Bargaining Theories
Bargaining is the tactical sub-set of negotiation focused specifically on resource division (e.g., price, time, compute).

*   **Iterative Concession Models**: Defining how an agent gradually lowers its requirements over multiple turns.
*   **Time-Pressure Strategies**: Using `TemporalContext` to influence the bargaining power (e.g., "I need this done by Monday" reduces bargaining leverage).
*   **Anchoring Heuristics**: A System 1 heuristic where the first offer sets the psychological boundary for the interaction.

---

## Mapping to Universal Schema (Schema.org)

| Strategic Theory | Schema.org `@type` | Semantic Extension Block |
| :--- | :--- | :--- |
| **Game Theory** | `ControlAction` | `attributes.payoff_matrix`, `attributes.strategy_type` |
| **Negotiation** | `CommunicateAction` | `attributes.negotiation_protocol`, `attributes.batna` |
| **Bargaining** | `OrderAction` / `TradeAction` | `attributes.concession_rate`, `attributes.anchor_price` |

## JSON-LD Example: A Bargaining TradeAction

```json
{
  "@context": "https://schema.org",
  "@type": "TradeAction",
  "name": "Bargaining: Compute Resource Acquisition",
  "agent": { "@type": "SoftwareApplication", "name": "Worker-01" },
  "participant": { "@type": "SoftwareApplication", "name": "Resource-Provider" },
  "semantic_extension": {
    "taxonomy": { "labels": ["bargaining", "distributive_negotiation"] },
    "attributes": {
      "bargaining_strategy": "tit-for-tat",
      "initial_offer": 100,
      "concession_limit": 125,
      "batna_ref": "urn:agnxxt:artifact:alternative-provider-99"
    },
    "lineage": {
      "derived_from": "urn:agnxxt:context:budget-constraint-v2"
    }
  }
}
```

## Self-Improving Strategic Harness
The harness monitors these strategic actions to ensure agents aren't "being cheated" or behaving sub-optimally.
*   **The Audit:** If an agent consistently settles for values below its `BATNA`, the harness detects a failure in the `negotiation_theory` implementation and autonomous patches the `concession_rate` attribute.
