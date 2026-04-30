# Agent Knowledge Graph: Entity Relations & Ontology

To fully realize the cognitive frameworks (Active Inference, Epistemic Trust, Stigmergy), the Knowledge Graph relies on a rigorously defined ontology. It is the **relations (edges)** between the **entities (nodes)** that give the system its semantic reasoning capabilities.

Below is the standard relational ontology mapping the interactions within the Agent Kernel.

## Core Entity Types (Nodes)
*   **`Agent`**: Autonomous software components (e.g., Critic, Worker).
*   **`User`**: Human operators or external stakeholders.
*   **`Action` / `Task`**: Executable units of work (mapped to Schema.org Actions).
*   **`Artifact`**: Digital resources, data objects, or tools.
*   **`Belief` / `Fact`**: Assertions about the world model.
*   **`Context`**: Environmental and situational states bounding the agent's reality.
    *   *Sub-types:* `Place`, `TimeState`, `WeatherCondition`, `Event` (e.g., Elections, Cricket Matches, Natural Disasters).

---

## Key Relational Domains (Edges)

### 1. Situational & Environmental Relations (Action/Agent $\leftrightarrow$ Context)
These relations ground the agent's operations in the real physical and socio-political world.
*   `[Action] -OCCURS_IN-> [Place]`: Binds a task to a geographic or virtual location.
*   `[Action] -IMPACTED_BY-> [Event / Weather]`: Links a task's success probability to external factors (e.g., a supply chain task impacted by a natural disaster).
*   `[Agent] -AWARE_OF-> [Event]`: Indicates the agent holds the current state of a public event (like an ongoing election or cricket match) in its active memory.
*   `[Event] -TRIGGERS-> [Action]`: A macro-event (like a market crash or a sports match ending) automatically initiates a pre-planned agent response.

### 2. Temporal Nuance & Intersection (TimeState $\leftrightarrow$ Context)
This ensures the agent recognizes that recurring time periods are unique based on their intersections.
*   `[TimeState] -CHARACTERIZED_BY-> [Event / Weather]`: Distinguishes "Monday (Normal)" from "Monday (Public Holiday)" or "Monday (Post-Disaster)".
*   `[TimeState] -HAS_HISTORICAL_ANOMALY-> [Fact]`: Allows the agent to recall specific patterns (e.g., "Mondays during this season usually have higher latency").
*   `[Action] -SCHEDULED_FOR-> [TimeState]`: Binds an action to a specific temporal window that is already enriched with situational context.

### 3. Contextual Overrides & Decision Constraints (Context $\leftrightarrow$ Strategy)
This prevents agents from blindly optimizing for a single variable (e.g., "cost") when environmental realities dictate otherwise.
*   `[Context/Weather] -INVALIDATES_HEURISTIC-> [DualProcess/Heuristic]`: Prevents the agent from using a "Fast" heuristic (e.g., "suggest walking to save money") if the environment (e.g., "Raining") makes it illogical or unsafe.
*   `[Context/Event] -MODIFIES_OBJECTIVE-> [CognitiveProfile/Objective]`: Temporarily changes the agent's short-term goal weighting (e.g., shifting priority from "cost optimization" to "safety/comfort" during a severe weather event).
*   `[Action] -REQUIRES_CONDITION-> [Context]`: An action cannot be proposed unless the environmental state permits it.

### 4. Criticality & Emergency Overrides (Context $\leftrightarrow$ Execution)
This ensures that during high-stakes events (e.g., medical emergencies), the agent's core execution engine shifts modes instantly.
*   `[EmergencyContext] -OVERRIDES_PATHWAY-> [DualProcess/Pathway]`: Instantly forces the agent into a "Max-Reliability / Zero-Latency" execution mode.
*   `[EmergencyContext] -SUSPENDS_CONSTRAINT-> [CognitiveProfile/Constraint]`: Temporarily ignores constraints like "cost-efficiency" or "token-budget" to prioritize speed and reach.
*   `[Action] -MODIFIES_TOPOLOGY-> [Broadcast/Parallel]`: Changes a standard sequential communication flow into a parallel broadcast across all available channels (`CommunicateAction`) to ensure maximum reach during a crisis.

### 5. Memory & Contextual Relations (Agent $\leftrightarrow$ History/Environment)
These relations define how an agent utilizes its past and its boundaries.
*   `[Agent] -RECALLS-> [EpisodicMemory/Lineage]`: The agent queries its own history to inform a current action.
*   `[Agent] -BOUND_BY-> [Context]`: Explicitly links an agent's current "Awareness" to specific situational constraints.
*   `[Belief] -CONSOLIDATES_INTO-> [LongTermMemory]`: The transition from active working belief to stable world-model fact.

### 6. Social & Trust Relations (Agent $\leftrightarrow$ Agent)
These relations define the "Organization Science" and "Epistemic Trust" of the network.
*   `[Agent A] -TRUSTS {weight: 0.8}-> [Agent B]`: Defines the dynamic credibility weighting.
*   `[Agent A] -DELEGATES_TO-> [Agent B]`: Establishes hierarchical task execution and responsibility.

### 7. Strategic & Interaction Relations (Agent $\leftrightarrow$ Agent)
These relations define the mathematical and tactical interactions between autonomous units.
*   `[Agent A] -NEGOTIATES_WITH-> [Agent B]`: Initiates a strategic dialogue using a `NegotiationTheory` artifact.
*   `[Agent A] -COMPETES_WITH-> [Agent B]`: Indicates a zero-sum `GameTheory` interaction for limited resources.

### 8. Macro-Context Relations (Action/Agent $\leftrightarrow$ WorldState)
These relations connect high-level global conditions to local agent execution.
*   `[Action/Agent] -SUBJECT_TO-> [Geopolitics/Regime]`: Enforces legal and regulatory compliance boundaries.
*   `[Agent] -ADHERES_TO-> [Culture]`: Binds an agent's communication and value system to a specific cultural lens.
*   `[Agent] -OPERATES_IN_SOCIETY-> [SocietyState]`: Connects agent behavior to societal norms and demographic realities.
*   `[Action] -COMMUNICATES_VIA-> [LanguageLens]`: Formalizes the linguistic medium and formality requirements of an interaction.
*   `[Place] -EXPERIENCING-> [Climate/Weather]`: Grounds a location in its atmospheric reality.
*   `[Bargaining/Trade] -CONSTRAINED_BY-> [Economy]`: Links micro-transactions to macro-economic indicators (e.g., volatility).

### 9. Epistemic & Lineage Relations (Agent $\leftrightarrow$ Belief/Fact)
These relations drive "Active Inference" and "Lineage Tracking".
*   `[Agent] -ASSERTS {confidence: 0.95}-> [Belief]`: The agent introduces a fact into the world model.
*   `[Agent] -OBSERVES-> [Context/Artifact]`: The agent registers an empirical reading (often the result of an `active_probe`).
*   `[Belief A] -DERIVES_FROM-> [Belief B]`: Absolute provenance tracing (Lineage). If Belief B is proven false, the graph invalidates Belief A automatically.
*   `[Agent] -VALIDATES-> [Belief]`: An agent confirms a peer's assertion, increasing the network's consensus score.

### 3. Operational & Stigmergic Relations (Agent $\leftrightarrow$ Action/Artifact)
These relations enable "Predictive Control" and environment-based coordination.
*   `[Agent] -PLANS-> [Action]`: Represents the "look-ahead" simulation phase of Predictive Control.
*   `[Agent] -EXECUTES-> [Action]`: The actual commitment to an action.
*   `[Action] -CONSUMES-> [Artifact]`: Indicates dependencies for a task.
*   `[Action] -PRODUCES-> [Artifact]`: Tracks the output and transformation of resources.
*   `[Agent] -LOCKS / TRACES-> [Artifact]`: **Stigmergy in action.** An agent leaves a marker on a resource so other agents know it is currently being operated on, preventing race conditions.

## Universal Schema Implementation
These relations are injected directly into the `semantic_extension.ontology.relations` block of our Schema.org payloads.

**Example: Stigmergy & Lineage in the Graph**
```json
"semantic_extension": {
  "ontology": {
    "relations": [
      {
        "subject": "urn:agnxxt:agent:Data-Parser-01",
        "predicate": "CONSUMES",
        "object": "urn:agnxxt:artifact:raw-dataset-99"
      },
      {
        "subject": "urn:agnxxt:agent:Data-Parser-01",
        "predicate": "ASSERTS",
        "object": "urn:agnxxt:belief:dataset-is-corrupted"
      }
    ]
  }
}
```

By defining these strict relations, the Knowledge Graph can automatically execute complex reasoning algorithms. For example, if an Agent's Trust score drops below a threshold, the graph can traverse the `ASSERTS` and `DERIVES_FROM` edges to instantly flag all downstream knowledge that was dependent on that compromised agent.
