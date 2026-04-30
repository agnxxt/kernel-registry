# Isolation & Airgap Behavior Framework: The Sovereign Agent

This framework defines how an agent's interaction with the kernel's cognitive and macro-contextual layers shifts when the agent is **Isolated** (network-constrained) or **Airgapped** (fully disconnected).

---

## 1. State Transition: Networked vs. Sovereign
When an agent detects a loss of connectivity to the central Knowledge Graph or peer network, it transitions from a **Networked state** to a **Sovereign state**.

### Networked State (Default)
*   **Epistemic Strategy**: Relies on `epistemic_trust` and `Gossip` protocols.
*   **Decision Mode**: Collaborative; utilizes `ConsensusTopology` (BFT).
*   **Context Source**: Real-time cloud APIs for `ClimateState`, `EconomyState`, etc.

### Sovereign/Airgapped State (Disconnected)
*   **Epistemic Strategy**: High **Self-Reliance**. The agent ignores `epistemic_trust` for external peers (as they are unreachable) and relies purely on its **Procedural Memory** and cached **Episodic Memory**.
*   **Decision Mode**: Autonomous/Dictatorial. The agent bypasses `ConsensusTopology` and executes actions based on its internal `SpiritualFoundation` and most recent cached `deontic_constraints`.
*   **Context Source**: Relies purely on **IoT & Hardware Sensors** (Local Situational Awareness).

---

## 2. Behavioral Shifts in Isolation

### A. Conservative Resource Management (Survival Mode)
In an airgapped state, the agent assumes limited resources (power, tokens, storage).
*   **Impact**: Forces `DualProcessTheory` into extreme "Fast/System 1" heuristics for routine tasks to preserve battery/compute, while reserving "Slow/System 2" only for critical life-safety `EmergencyContexts`.

### B. Increased Skepticism of Delayed Data
The agent recognizes that its cached `Macro-Context` (e.g., Geopolitical or Economic data) is decaying.
*   **Impact**: The `ActiveInference` surprise threshold is lowered. The agent becomes hyper-vigilant of local sensory changes that might contradict its stale world model.

### C. Sovereign Deontic Enforcement
Without access to a central `Policy` update, the agent becomes the sole enforcer of its last known `SpiritualFoundation`.
*   **Impact**: It refuses any external command (via local I/O) that violates its immutable internal axioms, as it cannot verify the command's "Lineage" against the trusted network.

---

## 3. Relational Ontology in Isolation
*   `[Agent] -IS_ISOLATED_FROM-> [Network/KG]`
*   `[Agent] -DEGRADES_TO_SOVEREIGN_MODE-> [SovereignStrategy]`
*   `[Agent] -RELIES_PURELY_ON-> [LocalHardwareSensor]`

## JSON-LD Example: Airgapped Sovereign Action

```json
{
  "@context": "https://schema.org",
  "@type": "ControlAction",
  "name": "Sovereign Survival Protocol: Airgap Detected",
  "agent": { "@type": "SoftwareApplication", "name": "Edge-Agent-01" },
  "actionStatus": "ActiveActionStatus",
  "semantic_extension": {
    "taxonomy": { "labels": ["isolation_mode", "sovereign_execution"] },
    "attributes": {
      "isolation_status": "Airgapped",
      "behavioral_shift": {
        "consensus_bypass": true,
        "resource_preservation_mode": "Aggressive",
        "stale_context_warning": ["Geopolitics", "Economy"]
      },
      "epistemic_override": "Rely on Local-IoT-Sensors ONLY"
    },
    "audit_tracking": {
      "change_reason": "Central Knowledge Graph heartbeat lost for > 300s"
    }
  }
}
```
