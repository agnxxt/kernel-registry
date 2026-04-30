# Model Runner Kernel Service

Provider-agnostic inference execution service for kernel workloads.

## API
- `RunInference`
- `GetInferenceStatus`
- `CancelInference`
- `ListModels`

## Providers
- openai-compatible
- LiteLLM
- vLLM
- Ollama
- Anthropic
- Google
- Azure OpenAI
- custom adapters

## Eventing
- `kernel.inference.request.v1`
- `kernel.inference.result.v1`
- `kernel.inference.audit.v1`

## Integration
Default runtime path routes to LiteLLM gateway for provider portability.
