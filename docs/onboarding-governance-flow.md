# Automated Onboarding & Governance Flow: From Discovery to Provisioning

This document outlines the end-to-end lifecycle of setting up an organization within the Agent Kernel, moving from initial setup to individual user agent provisioning.

---

## Phase 1: System Bootstrap & Discovery
A single **Global Admin** initiates the setup.

1.  **Application Connection**: Admin connects organizational apps (e.g., Slack, GitHub, Jira, ERP).
2.  **Automated Discovery**: The kernel's `discovery_unit` crawls these apps to extract:
    *   **User Identities**: Who belongs to the organization.
    *   **Profiles & Attributes**: Roles, seniority, department, and past activity patterns.
    *   **Tool Access**: Which APIs and internal tools are currently utilized by which users.
    *   **Permissions**: Existing RBAC/ABAC rules from the source apps.
3.  **Ontology Mapping**: Discovered data is automatically ingested into the Knowledge Graph as `User`, `Role`, and `Artifact` nodes.

## Phase 2: Admin Approval & Policy Enforcement
The Admin reviews the discovered "World Model" before anything goes live.

1.  **Review Dashboard**: Discovered users and their predicted "Cognitive Profiles" are displayed.
2.  **Deontic Guardrail Injection**: Admin enforces **Org-wide Policies** (e.g., "No agent can access payroll data," "All financial actions require 2-person consensus").
3.  **Onboarding Approval**: Admin selectively approves users/departments for agent enablement.

## Phase 3: Targeted User Provisioning (The Outreach)
Once approved, the system reaches out to individual users.

1.  **Automated Outreach**: The kernel sends a `CommunicateAction` (e.g., via Slack or Email) to the user: *"Hello [Name], your department has been enabled for Agent Assistance. Let's set up your personal Worker-Agent."*
2.  **Needs-Based Configuration**: The user interacts with an onboarding bot to define:
    *   **Personal Objectives**: Short and long-term task goals.
    *   **Curiosity/Trust Levels**: Tuning their agent's `CognitiveProfile`.
3.  **Agent Activation**: The kernel deploys the user's customized `deployment_unit` (Worker/Assistant).

## Phase 4: Continuous Governance & Visibility
The Admin maintains total oversight of the decentralized agent network.

*   **Global Visibility**: Admin uses the `visual_dashboard` to see every agent-to-agent interaction across the org.
*   **Policy Enforcement**: If a user's personal agent attempts an action that violates an org-wide `DeonticConstraint`, the kernel's **RACF (Rogue Agent Containment Framework)** blocks it, regardless of the user's local settings.
*   **Audit Trail**: Every onboarding step and policy change is cryptographically signed and stored in the `audit_trail_browser`.

---

## Universal Schema Mapping

| Step | Schema.org `@type` | Semantic Extension |
| :--- | :--- | :--- |
| **Discovery** | `SearchAction` | `attributes.discovered_entities` |
| **Admin Approval** | `AssessAction` | `attributes.approval_status: approved` |
| **User Outreach** | `CommunicateAction`| `taxonomy.labels: ["onboarding_outreach"]` |
| **Policy Update** | `UpdateAction` | `attributes.deontic_constraint_delta` |

## JSON-LD Example: Admin Approval for Onboarding

```json
{
  "@context": "https://schema.org",
  "@type": "AssessAction",
  "name": "Admin Approval: Marketing Department Enablement",
  "agent": { "@type": "Person", "name": "Global-Admin-Alice" },
  "object": { "@type": "Organization", "name": "Marketing-Team" },
  "actionStatus": "CompletedActionStatus",
  "semantic_extension": {
    "taxonomy": { "labels": ["admin_governance", "provisioning_approval"] },
    "attributes": {
      "approved_users": ["user-id-01", "user-id-02"],
      "enforced_policies": ["urn:agnxxt:policy:no-external-data-egress"],
      "provisioning_trigger": "immediate_outreach"
    },
    "audit_tracking": {
      "created_by": "Global-Admin-Alice",
      "change_reason": "Marketing department authorized for AI-Agent rollout."
    }
  }
}
```
