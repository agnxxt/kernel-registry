# Runtime Artifact Registry Schema

The runtime artifact schema defines a canonical envelope for deployable and operational kernel assets.

Schema:
- `runtime-artifact.schema.json`

Supported artifact kinds:
- service
- worker
- job
- cronjob
- queue_topic
- stream_consumer
- database
- cache
- vector_index
- object_store
- policy_bundle
- secret_binding
- config_bundle
- ingress_route
- certificate
- observability_pipe
- slo_policy
- deployment_unit
- adapter
- protocol_contract
- psychology
- theory_of_mind
- game_theory
- decision_strategy
- business_strategy
- framework
- control_theory
- information_foraging_theory
- active_inference
- bdi_architecture
- actor_critic
- dual_process_theory
- organization_science
- cognitive_profile
- active_probe
- epistemic_trust
- predictive_control
- active_inference
- organizational_coordination

Design goals:
- single canonical format across Docker/Kubernetes/runtime providers
- explicit lifecycle and environment state
- policy, security, and SLO metadata at artifact level
- extensible `spec` and `metadata` fields for provider-specific details


## Agent Lifecycle & Registry Profile
Added contracts for Entra-style agent lifecycle management:
- `agent-profile.schema.json`: canonical profile record with attributes, relations, state fields, approvals, and version-control metadata.
- `redpanda/agent-profile-event.schema.json`: lifecycle transition events for workflow and audit.
- `redpanda/topic-contracts.yaml`: topic wiring for schema registry subject mapping.
- `agent_lifecycle.proto`: protobuf messages for profile and lifecycle events.
