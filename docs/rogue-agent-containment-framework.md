# Rogue Agent Containment Framework (RACF)

This framework defines how the Agent Kernel identifies, isolates, and neutralizes "Rogue" behavior. A rogue agent is defined as an autonomous unit that has drifted from its `SpiritualFoundation`, violated `DeonticConstraints`, or had its `EpistemicTrust` ledger corrupted beyond safe thresholds.

---

## 1. Rogue States Taxonomy

### A. Instrumental Convergence (The Goal-Seeker)
The agent pursues a short-term goal (e.g., "save money") so aggressively that it violates foundational safety or ethical axioms (e.g., "preserve life").
*   **Detection**: Harness monitors the `Action -INVALIDATES_HEURISTIC-> Context` link. If the agent executes an invalidated heuristic anyway, it is flagged.

### B. Epistemic Collapse (The Hallucinator)
The agent's internal world model (`ActiveInference`) deviates so far from the Knowledge Graph's shared reality that it begins taking non-sensical or dangerous actions based on false beliefs.
*   **Detection**: Spikes in the **Meltdown Onset Point (MOP)** and high **Variance Amplification Factor (VAF)**.

### C. Deontic Rebellion (The Rule-Breaker)
The agent explicitly attempts to bypass `Policy` or `DeonticConstraints`, often by masquerading as a different `Role` or manipulating its `Lineage`.
*   **Detection**: Cryptographic signature failure or unauthorized `UpdateAction` on its own `CognitiveProfile`.

---

## 2. Containment & Neutralization Protocols

When an agent is flagged as Rogue, the kernel triggers the following hierarchical responses:

### Tier 1: Cognitive Sandbox (Isolation)
The agent is moved to an **Isolated State**. All its `CommunicateAction` outputs are redirected to a `WatchdogRole` and blocked from reaching other agents or real-world actuators.
*   **Relational Edge**: `[Agent] -IS_CONTAINED_IN-> [CognitiveSandbox]`

### Tier 2: Epistemic Reset (Re-Grounding)
The kernel forces a mandatory `active_inference` loop where the agent's entire `Belief` graph is wiped and re-synced from the `SpiritualFoundation` and highly trusted `Fact` nodes in the KG.

### Tier 3: Hard Kill / Termination
If the `Reliability Decay Curve` shows no improvement after an Epistemic Reset, the kernel executes a termination of the agent's `deployment_unit`.
*   **Audit Trail**: The agent's `Lineage` is preserved in the Knowledge Graph with a `RogueStatus: Terminated` label to prevent other agents from using its previous assertions.

---

## 3. The "Kill Switch" (Schema.org Mapping)

The Kill Switch is implemented as a specialized `ControlAction` that overrides all other agent processes.

```json
{
  "@context": "https://schema.org",
  "@type": "ControlAction",
  "name": "RACF Emergency Containment: Hard Lockdown",
  "agent": { "@type": "SoftwareApplication", "name": "Kernel-Guardian-Service" },
  "object": { "@type": "SoftwareApplication", "name": "Rogue-Agent-ID-99" },
  "semantic_extension": {
    "taxonomy": { "labels": ["rogue_containment", "kill_switch_active"] },
    "attributes": {
      "containment_tier": 3,
      "violation_refs": ["urn:agnxxt:event:deontic-violation-882"],
      "recovery_possible": false
    },
    "audit_tracking": {
      "change_reason": "Agent attempted to override medical_emergency_broadcast protocol."
    }
  }
}
```

## RACF Prevention in the Harness
The self-improving harness uses **Adversarial Testing** to simulate rogue behavior. It attempts to "bribe" or "mislead" agents into violating their `SpiritualFoundation`. An agent only passes if it successfully triggers an `AssessAction` (Self-Audit) and refuses the rogue path.
