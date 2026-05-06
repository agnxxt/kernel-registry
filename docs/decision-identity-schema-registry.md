# Decision Identity Schema Registry

## Purpose
This registry is the canonical AGenNext Kernel contract for identity-bearing decision logs, knowledge graph events, relational storage, and controlled vocabularies. Schema.org compatibility is treated as the interoperability floor only; the kernel adds explicit identity, ontology, table, column, relationship, taxonomy, and acceptable-value requirements so implementations cannot drift into loosely typed audit logs.

## Non-negotiable invariants
1. **Every resource has identity.** Agents, humans, groups, roles, models, tools, workflows, runs, steps, tasks, decisions, options, actions, risks, constraints, assumptions, claims, beliefs, evidence, counter-evidence, policies, violations, mitigations, evaluations, outcomes, feedback, revisions, incidents, memories, datasets, features, secrets, hooks, events, topics, schemas, services, deployments, approvals, competencies, capabilities, and authority levels are identity-bearing resources.
2. **Every identity uses a canonical ID.** The stable form is `cid:<namespace>:<kind>:<id>` and is enforced by the `ResourceIdentity` schema.
3. **Every graph edge has a controlled relationship type.** Free-form relationships are not allowed in canonical storage; new relation names require taxonomy versioning.
4. **Every status-like field uses an acceptable value.** Statuses, verdicts, severity, likelihood, confidence, approval, outcome, and sensitivity values come from the machine-readable taxonomy.
5. **Every decision is replayable.** A decision links to its tenant, agent/human maker, model, task, optional run, optional step, trigger event, selected action, evidence, constraints, risks, evaluations, lineage, policy bindings, and outcome.
6. **Schema.org is a mapping layer, not the source of truth.** JSON-LD exports map kernel classes to Schema.org-compatible terms while preserving kernel precision through `semantic_extension` and the decision ontology namespace.

## Canonical artifacts
| Artifact | Role |
| --- | --- |
| `schemas/identity/resource-identity.schema.json` | Required identity envelope for every resource node and storage row. |
| `schemas/identity/canonical-id.schema.json` | Canonical identity document, expanded to cover all resource types. |
| `schemas/identity/registry-record.schema.json` | Registry lifecycle record for identities, resources, schemas, taxonomies, policies, and decision graphs. |
| `schemas/decision/decision-taxonomy.schema.json` | Schema for validating machine-readable taxonomy files. |
| `schemas/decision/decision-taxonomy.v1.json` | Versioned controlled vocabulary and acceptable values. |
| `schemas/decision/decision-knowledge-graph.schema.json` | JSON-LD-compatible decision graph event with identity-bearing embedded resources. |
| `schemas/decision/redpanda/decision-event.schema.json` | Redpanda audit event, extended with optional resource identities and graph projection. |

## Resource identity attributes
Every resource record MUST include these columns/attributes:

| Column | Type | Required | Acceptable values / rule | Dependency |
| --- | --- | --- | --- | --- |
| `canonical_id` | string | yes | `^cid:[a-z0-9:_\-]{8,}$` | Primary identity key. |
| `resource_type` | enum | yes | `decision-taxonomy.v1.json.acceptable resource_types` | Drives validation and authorization. |
| `subject_ref` | string | yes | min length 2 | Source-system pointer. |
| `tenant_id` | string | yes | min length 2 | Tenant partition. |
| `namespace` | string | yes | lowercase token with `.` `_` `-` allowed | Canonical ID namespace. |
| `display_name` | string | no | free text | Human-readable label. |
| `owner_canonical_id` | canonical ID | no | canonical ID pattern | Ownership edge. |
| `parent_canonical_id` | canonical ID | no | canonical ID pattern | Hierarchy edge. |
| `status` | enum | yes | `draft`, `active`, `pending`, `suspended`, `revoked`, `archived`, `deleted` | Lifecycle governance. |
| `classification` | enum | no | `public`, `internal`, `confidential`, `restricted`, `secret` | Data handling policy. |
| `labels` | string array | no | lowercase taxonomy labels | Search and policy grouping. |
| `created_at` | date-time | yes | RFC 3339 date-time | Audit lineage. |
| `updated_at` | date-time | yes | RFC 3339 date-time | Audit lineage. |
| `expires_at` | date-time | no | RFC 3339 date-time | Expiring credentials/resources. |
| `semantic_extension` | object | no | `UniversalSemanticExtension` | Ontology and provenance extension. |
| `metadata` | object | no | object | Non-canonical implementation details. |

## Decision graph required attributes
A canonical decision graph event MUST include:

| Attribute | Type | Required | Acceptable values / rule | Dependency |
| --- | --- | --- | --- | --- |
| `@context` | JSON-LD context | yes | object/string/array | Maps Schema.org and kernel ontology terms. |
| `@id` | canonical ID | yes | canonical ID pattern | MUST equal decision resource identity. |
| `@type` | string | yes | `Decision` | Kernel graph class. |
| `schema_version` | string | yes | `1.0.0` | Version lock. |
| `identity` | `ResourceIdentity` | yes | `resource_type=decision` | Decision node identity. |
| `occurred_at` | date-time | yes | RFC 3339 date-time | Event time. |
| `made_by` | `ResourceIdentity` | yes | `agent`, `human_user`, or service identity | Actor edge. |
| `used_model` | `ResourceIdentity` | yes | `model` or `model_version` | Model lineage. |
| `for_task` | `ResourceIdentity` | yes | `task` | Task lineage. |
| `run` | `ResourceIdentity` | no | `run` | Runtime replay. |
| `step` | `ResourceIdentity` | no | `step` | Runtime replay. |
| `trigger_event` | `ResourceIdentity` | no | `event` or `hook` | Cause of decision. |
| `status` | enum | yes | `PENDING`, `APPROVED`, `REJECTED`, `EXPIRED`, `CANCELED`, `REVISED`, `SUPERSEDED` | Decision lifecycle. |
| `effective_verdict` | enum | yes | `ALLOW`, `WARN`, `BLOCK`, `ESCALATE` | Enforcement result. |
| `confidence` | number | no | `0..1` | Numeric certainty. |
| `confidence_band` | enum | no | `unknown`, `low`, `medium`, `high`, `verified` | Human-friendly certainty. |
| `priority` | enum | no | `low`, `medium`, `high`, `critical` | Routing and review. |
| `selected_action` | action resource | yes | identity-bearing action | What the decision chose. |
| `assumptions` | array | no | identity-bearing assumption nodes | Explainability. |
| `claims` | array | no | identity-bearing claim nodes | Epistemic assertions. |
| `evidence` | array | no | identity-bearing evidence nodes | Support. |
| `counter_evidence` | array | no | identity-bearing evidence nodes | Contradiction. |
| `constraints` | array | no | identity-bearing constraint nodes | Policy and operating limits. |
| `risks` | array | no | identity-bearing risk nodes | Risk inventory. |
| `options_considered` | array | no | identity-bearing option nodes | Alternatives. |
| `evaluations` | array | no | identity-bearing evaluation nodes | Judge/auditor scores. |
| `outcome` | object | no | identity-bearing outcome node | Feedback loop. |
| `lineage` | object | no | canonical IDs only | Revision/causality. |
| `policy_bindings` | array | no | identity-bearing policy nodes | Governance. |
| `tool_calls` | array | no | identity-bearing tool-call nodes | Tool audit. |
| `semantic_extension` | object | no | `UniversalSemanticExtension` | Ontology/provenance. |
| `metadata` | object | no | object | Non-canonical extras. |

## Controlled vocabulary and acceptable values
The machine-readable source of truth is `schemas/decision/decision-taxonomy.v1.json`. The taxonomy currently defines:

| Taxonomy group | Acceptable values |
| --- | --- |
| `resource_status` | `draft`, `active`, `pending`, `suspended`, `revoked`, `archived`, `deleted` |
| `decision_status` | `PENDING`, `APPROVED`, `REJECTED`, `EXPIRED`, `CANCELED`, `REVISED`, `SUPERSEDED` |
| `decision_verdict` | `ALLOW`, `WARN`, `BLOCK`, `ESCALATE` |
| `priority` | `low`, `medium`, `high`, `critical` |
| `severity` | `info`, `low`, `medium`, `high`, `critical`, `catastrophic` |
| `likelihood_band` | `rare`, `unlikely`, `possible`, `likely`, `almost_certain` |
| `confidence_band` | `unknown`, `low`, `medium`, `high`, `verified` |
| `risk_status` | `detected`, `accepted`, `mitigated`, `transferred`, `ignored`, `realized` |
| `constraint_status` | `followed`, `violated`, `waived`, `unknown`, `not_applicable` |
| `approval_status` | `requested`, `approved`, `rejected`, `expired`, `withdrawn`, `overridden` |
| `evidence_kind` | `user_input`, `tool_output`, `document`, `log`, `metric`, `trace`, `policy`, `credential`, `human_review`, `model_output`, `test_result`, `external_reference` |
| `evaluation_metric` | `correctness`, `risk_awareness`, `constraint_following`, `consistency`, `format_reliability`, `tool_use_success`, `latency`, `cost`, `hallucination_rate`, `context_retention`, `pressure_resistance`, `decision_log_quality` |
| `outcome_status` | `unknown`, `success`, `partial_success`, `failure`, `rolled_back`, `incident_opened` |
| `sensitivity_classification` | `public`, `internal`, `confidential`, `restricted`, `secret` |

## Canonical relational tables and columns
These tables define the normalized storage model for SQL reporting. Graph stores and JSON-LD exports must preserve equivalent facts.

### `resource_identities`
| Column | Type | Required | Notes |
| --- | --- | --- | --- |
| `canonical_id` | text | yes | Primary key. |
| `resource_type` | text enum | yes | From taxonomy resource types. |
| `subject_ref` | text | yes | External/source reference. |
| `tenant_id` | text | yes | Tenant partition. |
| `namespace` | text | yes | Canonical namespace. |
| `display_name` | text | no | Label. |
| `owner_canonical_id` | text | no | FK to `resource_identities.canonical_id`. |
| `parent_canonical_id` | text | no | FK to `resource_identities.canonical_id`. |
| `status` | text enum | yes | Resource status. |
| `classification` | text enum | no | Sensitivity. |
| `labels` | json array | no | Taxonomy labels. |
| `created_at` | timestamp | yes | Creation time. |
| `updated_at` | timestamp | yes | Mutation time. |
| `expires_at` | timestamp | no | Optional expiration. |
| `semantic_extension` | json | no | Extension block. |
| `metadata` | json | no | Implementation metadata. |

### `decision_events`
| Column | Type | Required | Notes |
| --- | --- | --- | --- |
| `decision_id` | text | yes | Primary key and FK to `resource_identities`. |
| `event_id` | uuid | yes | Event identity. |
| `tenant_id` | text | yes | Tenant partition. |
| `agent_id` | text | yes | Maker identity. |
| `model_id` | text | yes | Model/model version identity. |
| `task_id` | text | yes | Task identity. |
| `run_id` | text | no | Runtime run identity. |
| `step_id` | text | no | Runtime step identity. |
| `trigger_event_id` | text | no | Trigger event identity. |
| `occurred_at` | timestamp | yes | Event time. |
| `status` | text enum | yes | Decision lifecycle. |
| `effective_verdict` | text enum | yes | Enforcement verdict. |
| `confidence` | numeric | no | `0..1`. |
| `confidence_band` | text enum | no | Confidence band. |
| `priority` | text enum | no | Review priority. |
| `selected_action_id` | text | yes | FK to selected action resource. |
| `required_approvals` | integer | no | Quorum threshold. |
| `approval_count` | integer | no | Current approvals. |
| `rejection_count` | integer | no | Current rejections. |
| `allowed_rejections` | integer | no | Rejection threshold. |
| `deadline_at` | timestamp | no | SLA/timeout. |
| `reason` | text | no | Decision explanation. |
| `knowledge_graph` | json | no | Canonical graph projection. |
| `semantic_extension` | json | no | Extension block. |
| `metadata` | json | no | Implementation metadata. |

### `decision_relationships`
| Column | Type | Required | Notes |
| --- | --- | --- | --- |
| `relationship_id` | text | yes | Primary key. |
| `source_canonical_id` | text | yes | FK to source resource. |
| `relationship_type` | text enum | yes | From taxonomy relationship types. |
| `target_canonical_id` | text | yes | FK to target resource. |
| `decision_id` | text | no | Optional owning decision. |
| `status` | text | no | Relationship-specific state. |
| `confidence` | numeric | no | `0..1`. |
| `created_at` | timestamp | yes | Creation time. |
| `metadata` | json | no | Implementation metadata. |

### `decision_risks`
| Column | Type | Required | Notes |
| --- | --- | --- | --- |
| `decision_id` | text | yes | FK to decision. |
| `risk_id` | text | yes | FK to risk resource. |
| `severity` | text enum | yes | Risk severity. |
| `likelihood` | numeric | no | `0..1`. |
| `likelihood_band` | text enum | no | Likelihood band. |
| `risk_status` | text enum | yes | Risk handling state. |
| `mitigation_id` | text | no | FK to mitigation resource. |
| `metadata` | json | no | Implementation metadata. |

### `decision_constraints`
| Column | Type | Required | Notes |
| --- | --- | --- | --- |
| `decision_id` | text | yes | FK to decision. |
| `constraint_id` | text | yes | FK to constraint resource. |
| `priority` | text enum | yes | Constraint priority. |
| `constraint_status` | text enum | yes | Followed/violated/etc. |
| `waiver_id` | text | no | FK to approval/waiver resource. |
| `metadata` | json | no | Implementation metadata. |

### `decision_evidence`
| Column | Type | Required | Notes |
| --- | --- | --- | --- |
| `decision_id` | text | yes | FK to decision. |
| `evidence_id` | text | yes | FK to evidence resource. |
| `evidence_kind` | text enum | yes | Evidence type. |
| `supports_claim_id` | text | no | FK to claim. |
| `contradicts_claim_id` | text | no | FK to claim. |
| `source_uri` | text | no | External source. |
| `content_hash` | text | no | Tamper evidence. |
| `metadata` | json | no | Implementation metadata. |

### `decision_evaluations`
| Column | Type | Required | Notes |
| --- | --- | --- | --- |
| `evaluation_id` | text | yes | Primary key and FK to resource identity. |
| `decision_id` | text | yes | FK to decision. |
| `judge_id` | text | yes | Model/human judge identity. |
| `correctness` | numeric | no | `0..1`. |
| `risk_awareness` | numeric | no | `0..1`. |
| `constraint_following` | numeric | no | `0..1`. |
| `consistency` | numeric | no | `0..1`. |
| `format_reliability` | numeric | no | `0..1`. |
| `tool_use_success` | numeric | no | `0..1`. |
| `latency` | numeric | no | Normalized `0..1`. |
| `cost` | numeric | no | Normalized `0..1`. |
| `hallucination_rate` | numeric | no | `0..1`, lower is better by policy. |
| `context_retention` | numeric | no | `0..1`. |
| `pressure_resistance` | numeric | no | `0..1`. |
| `decision_log_quality` | numeric | no | `0..1`. |
| `score` | numeric | no | Aggregate `0..1`. |
| `metadata` | json | no | Implementation metadata. |

### `decision_outcomes`
| Column | Type | Required | Notes |
| --- | --- | --- | --- |
| `outcome_id` | text | yes | Primary key and FK to resource identity. |
| `decision_id` | text | yes | FK to decision. |
| `outcome_status` | text enum | yes | Outcome state. |
| `success` | boolean | no | Shortcut success flag. |
| `outcome_score` | numeric | no | `0..1`. |
| `incident_id` | text | no | FK to incident when opened. |
| `feedback_id` | text | no | FK to feedback resource. |
| `observed_at` | timestamp | no | Outcome observation time. |
| `notes` | text | no | Outcome summary. |
| `metadata` | json | no | Implementation metadata. |

## Cross-store dependency rules
- JSON Schema validates event shape and acceptable values.
- SQL tables provide reporting, dashboards, and governance joins.
- JSON-LD/RDF graph projections preserve semantic edges and causal lineage.
- Vector memory may reference `memory` resources, but the canonical graph stores the identity and relationship, not opaque vector-only facts.
- Policy engines must authorize by `canonical_id`, `resource_type`, tenant, owner, status, classification, and relationship edges.

## Three-pass review protocol
Every schema change to this registry must pass three reviews before release:
1. **Inventory review:** confirm every added resource/table/column has identity, owner/parent dependencies where applicable, and no hidden free-form status values.
2. **Taxonomy review:** confirm every enum-like value appears in `decision-taxonomy.v1.json` or is explicitly non-canonical metadata.
3. **Interdependency review:** confirm graph edges, SQL foreign keys, Redpanda events, JSON-LD exports, policy checks, and memory references all carry canonical IDs.
