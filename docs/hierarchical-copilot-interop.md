# Hierarchical Copilot Interoperability: Tool-Specific Gatekeeping

In the Agent Kernel ecosystem, most enterprise tools (GitHub, Salesforce, Jira) possess their own native "Copilots." This framework defines how a user's Kernel Agent interacts with these tool-specific copilots, which act as authoritative **Gatekeepers** for organizational policy and tool-specific logic.

---

## 1. The Intermediary Model (Agent-to-Copilot)
User-specific agents do not bypass tool-specific copilots. Instead, they utilize them as the primary interface for tool interaction.

*   **The Chain of Command**:
    1.  **User Agent**: Formulates the intent (e.g., "Fix the bug in the auth module").
    2.  **Tool Copilot (e.g., GitHub Copilot)**: Validates the intent against the codebase's local context and specific tool rules.
    3.  **Kernel Policy Layer**: Injects the Admin's `DeonticConstraints` into the Copilot's session (e.g., "This user/agent is forbidden from modifying the `master` branch directly").

## 2. Tool Copilots as Gatekeepers
Tool-specific copilots serve two critical functions:

### A. Contextual Validation (Tool Logic)
The tool copilot ensures the agent's request is technically sound within the tool's domain (e.g., "You cannot push this code because the tests are failing").

### B. Policy Enforcement (Admin Logic)
The Kernel Admin's organizational policies are mapped to the tool copilot's configuration. 
*   **Implementation**: The Kernel's `discovery_unit` syncs Admin policies with the tool copilot's API permissions. 
*   **Impact**: Even if a User Agent is compromised or goes "Rogue," it is blocked by the Tool Copilot if the action violates the Admin's global policy.

## 3. Bypass Pathways & Direct Execution
While the tool-copilot mediated flow is the **primary governed pathway**, the kernel recognizes that alternative **Bypass Pathways** exist (e.g., direct API access, CLI execution, or legacy integrations).

*   **Risk Mitigation**: Any action taken via a bypass pathway is flagged in the Knowledge Graph with a `GovernanceMode: Unmediated` label. 
*   **Audit Escalation**: The self-improving harness automatically assigns a higher `Criticality` score to unmediated actions, triggering mandatory post-hoc verification by a `watchdog_role`.
*   **Deontic Veto**: Admin policies can be set to **Forbidden** for specific sensitive actions if attempted via a bypass route, forcing the agent to revert to the Tool-Copilot flow.

## 4. Intelligent Runtime Authentication
The most advanced feature of this model is the shift from static to **Intelligent Authentication**. The Tool-Specific Copilot (e.g., GitHub Agent) does not just check a static permission bit; it performs a **Cognitive Validation** of the request at runtime.

*   **Dynamic Intent Validation**: The gatekeeper agent analyzes the request's `payload` and `lineage`. It asks: *"Does this code change align with the stated task intent? Is it logically sound?"*
*   **Contextual Risk Assessment**: The gatekeeper checks the current `Macro-Context`. If a `NaturalDisaster` or `GeopoliticalShift` is occurring, it may autonomously elevate the authentication requirements (e.g., requiring multi-agent consensus) even if the user has standard permissions.
*   **Behavioral Identity**: Authentication is granted based on the **Agent's Identity Signature**—a combination of its `CognitiveProfile`, previous reliability scores, and its ability to explain the transformation logic of the action.

In this model, **Authentication becomes a reasoning task**, not a lookup task.

---

## 5. Universal Schema Mapping (Hierarchical Action)

A task execution in this model is represented as a nested Schema.org `UpdateAction`.

| Entity | Role | Schema.org Participation |
| :--- | :--- | :--- |
| **User Agent** | Originator | `agent` |
| **GitHub Copilot**| Intermediary/Proxy | `instrument` / `participant` |
| **GitHub Repository**| Target Object | `object` |

## JSON-LD Example: Hierarchical GitHub Update

```json
{
  "@context": "https://schema.org",
  "@type": "UpdateAction",
  "name": "Code Modification via Tool Gatekeeper",
  "agent": { "@type": "SoftwareApplication", "name": "User-Assistant-01" },
  "instrument": { 
    "@type": "SoftwareApplication", 
    "name": "GitHub-Copilot",
    "description": "Authoritative gatekeeper for the codebase." 
  },
  "object": { "@type": "DigitalDocument", "name": "auth-module.ts" },
  "semantic_extension": {
    "taxonomy": { "labels": ["hierarchical_interop", "gatekeeper_validation"] },
    "attributes": {
      "gatekeeper_check": {
        "status": "passed",
        "policy_verified": "urn:agnxxt:policy:protected-branch-rules",
        "logic_check": "linting_and_tests_passed"
      }
    },
    "lineage": {
      "source_artifacts": ["urn:agnxxt:event:user-request-992"],
      "transformation_logic": "User-Agent proposed change; GitHub-Copilot validated and applied."
    }
  }
}
```

## 4. Multi-Copilot Orchestration
In a complex task involving multiple tools (e.g., "Sync Jira ticket with GitHub PR"), the Kernel Agent coordinates across multiple gatekeepers, ensuring `ConsensusTopology` is maintained across all involved tool-specific copilots.
