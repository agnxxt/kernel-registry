# Kernel-Level Common Actions

Common kernel actions:
- connect (integration/connectors)
- automate (n8n workflows)
- flow (LangGraph execution)
- loop (agent loops/iterations)
- search (Google)
- message (WhatsApp)
- publish (blog publishing)
- post (social media)
- travel_book (Uber ride actions)
- schema_org (schema.org action envelopes)

## Execution model
1. Submit request to `kernel.action.request.v1`
2. Kernel executes provider adapter
3. Emit outcome to `kernel.action.result.v1`

## Policy hooks
Each action request should include:
- guardrail mode
- budget/cost limits
- approval requirements for high-risk operations

## Scope levels
- global
- org
- country
- local
- product
- project
- group
- individual

Use `action_scope` plus `scope_ref` to target execution boundaries.

## Additional provider adapters
### git
- `clone_repo`
- `fetch_repo`
- `open_pr`
- `list_branches`
- `read_file`

### docker
- `build_image`
- `run_container`
- `compose_up`
- `compose_down`
- `push_image`
- `pull_image`

### caddy
- `upsert_site`
- `reload_config`
- `add_reverse_proxy`
- `remove_site`
- `get_cert_status`
