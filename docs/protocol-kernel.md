# Protocol Kernel (ANP + ACP)

Kernel protocol layer supports:
- ANP (agent-to-agent network envelopes)
- ACP (agent-client session/capability negotiation)

Contracts:
- `schemas/protocol/anp-envelope.schema.json`
- `schemas/protocol/acp-contract.schema.json`
- `schemas/protocol/agent_protocols.proto`

Baseline usage:
1. ACP session handshake establishes capabilities and auth mode.
2. ANP envelopes carry request/response/event traffic between agents.
3. Guardrail and policy metadata propagate through trace IDs.
