# Cognitive Model Runner Architecture

The Model Runner is the execution engine responsible for the "Cognitive Realization" of agent intents. It bridges the kernel's high-level orchestration logic with actual LLM providers (OpenAI, Anthropic, Google, Azure, Ollama).

---

## 1. Multi-LLM & Provider Abstraction
The Model Runner is provider-agnostic, supporting a diverse ecosystem of models.
*   **Frontier Models**: High-reasoning models (e.g., GPT-4o, Claude 3.7) used for the **System 2 (Slow)** pathway.
*   **Efficiency Models**: Low-latency, cost-effective models (e.g., GPT-4o-mini, Haiku) used for the **System 1 (Fast)** pathway.
*   **Local Models**: Self-hosted models (Ollama/vLLM) used when the agent is in **Sovereign/Airgapped Mode**.

## 2. Kernel-Enforced Inference
The Model Runner does not just forward requests; it wraps every inference call in the kernel's safety and observability layer.

*   **Prompt Injection Guard**: Automatically injects the active `DeonticConstraints` and `SpiritualFoundation` axioms into the system prompt.
*   **Contextual Grounding**: Injects relevant `Fact` nodes from the Knowledge Graph into the model's context window (GraphRAG).
*   **Schema Enforcement**: Enforces that the model's output conforms to the structured JSON-LD format required for the next step in the `Lineage`.

## 3. Dynamic Model Routing
Driven by `DualProcessTheory`, the Model Runner dynamically selects the optimal model based on:
1.  **Complexity**: Higher risk/complexity $\rightarrow$ System 2 models.
2.  **Economics**: Low ROI + Tight Budget $\rightarrow$ System 1 models.
3.  **Availability**: If a provider is down, the Model Runner utilizes the `fallback_models` defined in the `RuntimeArtifact` schema.

---

## Universal Schema Mapping

| Model Runner Phase | Schema.org `@type` | Relational Edge |
| :--- | :--- | :--- |
| **Inference Request** | `SearchAction` / `AssessAction` | `[Agent] -INVOKES-> [Model]` |
| **Model Response** | `PropertyValue` | `[Model] -GENERATES-> [Belief]` |
| **Provider Selection**| `ControlAction` | `[Kernel] -ROUTES_TO-> [Provider]` |

## JSON-LD Example: Model Runner Execution

```json
{
  "@context": "https://schema.org",
  "@type": "AssessAction",
  "name": "Cognitive Inference: Financial Risk Analysis",
  "agent": { "@type": "SoftwareApplication", "name": "Model-Runner-Engine" },
  "instrument": { "@type": "SoftwareApplication", "name": "Claude-3-7-Sonnet" },
  "semantic_extension": {
    "taxonomy": { "labels": ["inference", "system_2_thinking"] },
    "attributes": {
      "inference_metadata": {
        "tokens_consumed": 1420,
        "latency_ms": 850,
        "provider": "anthropic",
        "grounding_refs": ["urn:agnxxt:fact:market-volatility-2026"]
      }
    },
    "lineage": {
      "source_artifacts": ["urn:agnxxt:action:user-query-552"],
      "transformation_logic": "Deep reasoning inference with GraphRAG grounding."
    }
  }
}
```

## Model Runner Reliability Harness
The harness verifies model-level reliability:
1.  **Hallucination Check**: Compares model output against Knowledge Graph facts.
2.  **Constraint Adherence**: Verifies the model refused to execute actions blocked by the injected Deontic Guardrails.
3.  **Cross-Model Consensus**: In high-stakes tasks, the Model Runner executes the request on two different models and requires agreement (BFT) before returning the result.
