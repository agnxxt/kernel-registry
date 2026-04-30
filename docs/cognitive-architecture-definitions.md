# Cognitive Architecture: Memory, Context, and Awareness

This document defines the three pillars of the Agent Kernel's cognitive architecture, mapping how data (Memory) meets reality (Context) to produce "active state" (Awareness).

---

## 1. Cognitive Memory (The Stored Self)
Memory in the Agent Kernel is not a flat database; it is a multi-modal, graph-based structure that records the agent's history and knowledge.

*   **Epistemic Memory (The "What")**: The collection of `Belief` and `Fact` nodes in the Knowledge Graph. This is the agent's world model.
*   **Procedural Memory (The "How")**: The `allowed_heuristics` and `decision_strategy` artifacts stored in the registry. It defines the agent's skills.
*   **Episodic Memory (The "Past")**: The `lineage` and `audit_tracking` of every `Action` the agent has ever taken. It allows the agent to "remember" its own mistakes or successes.
*   **Intuition (Implicit Reasoning)**: A specialized "Fast Pathway" where the agent acts on non-verbalized patterns or sub-symbolic drives. In the kernel, this is treated as a **High-Risk/High-Speed** mode that often generates "Actions Without Explanation."
*   **Decay & Consolidation**: Mechanisms that determine when a specific memory (a `Belief` node) loses `confidence` over time or is archived.

---

## 2. Context (The Bounding Reality)
Context is the total set of environmental and internal variables that bound an agent's current operation. It answers the question: *"Under what conditions am I acting?"*

### Dimensions of Context:
1.  **Temporal**: Time, date, day-of-week, and **Temporal Nuance** (e.g., "Monday during a storm").
2.  **Spatial**: Physical location (`Place`) or virtual network environment.
3.  **Environmental**: Weather, network latency, compute availability, system load.
4.  **Socio-Political**: Macro-events like `Elections`, `Cricket Matches`, or `Natural Disasters`.
5.  **Relational**: The current `epistemic_trust` ledger for all visible peers.
6.  **Deontic**: The active `Policy` and `deontic_constraints` (what is forbidden *right now*).
7.  **Economic**: Current token budget, cost-constraints, and time-to-delivery requirements.

---

## 3. Awareness (The Active Intersection)
Awareness is the **active, high-priority intersection** of Memory and Context. It is not static storage; it is the "Global Workspace" in motion.

### Components of Awareness:
*   **Situational Awareness**: The real-time mapping of `Sensory Input` (from `active_probe`) onto the `Context` model. It is the agent's current "read" on the room.
*   **Attentional Awareness**: Managed by the `attention_schema`. It is the subset of the total Context the agent is currently processing (e.g., "I am aware of the user's frustration but ignoring the network lag").
*   **Self-Awareness (Meta-Cognition)**: Managed by `meta_representation`. The agent's awareness of its own state (e.g., "I am aware that I am currently optimizing for speed over accuracy").
*   **Predictive Awareness**: The result of `active_inference`. The agent's awareness of the delta between what it expects and what it observes (**"Surprise Detection"**).

## Mapping to Universal Schema
| Pillar | Universal Schema Injection |
| :--- | :--- |
| **Memory** | `semantic_extension.lineage` and `semantic_extension.ontology` |
| **Context** | `semantic_extension.attributes` and Schema.org `Event`/`Place` |
| **Awareness** | `semantic_extension.taxonomy.labels` (active triggers) |
