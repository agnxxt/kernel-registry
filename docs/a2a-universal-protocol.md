# Universal A2A Protocol: Total Interoperability Framework

The Agent-to-Agent (A2A) protocol is the "Lingua Franca" of the kernel. It is designed for absolute interoperability across five critical dimensions: **Multi-Modal**, **Multi-Language**, **Multi-Tool**, **Multi-Framework**, and **Multi-Cloud**.

---

## 1. Multi-Modal Communication
Agents do not just exchange text. The protocol supports native multi-modal payloads.
*   **Implementation**: Utilizes `semantic_extension.attributes.modalities`.
*   **Supported Payloads**: `text`, `image_ref`, `audio_stream`, `video_segment`, `structured_data` (JSON-LD).
*   **Inter-Modal Translation**: An agent can request a "summary" of an `image_ref` modality to be returned as a `text` modality.

## 2. Multi-Language Support
Agents operating in different human or programming languages must communicate without semantic loss.
*   **Linguistic Mapping**: Uses the `LanguageLens` from the Macro-Context framework.
*   **Polyglot Logic**: An agent written in Python (using LangChain) can communicate with an agent written in Go (using a custom framework) via the standardized Schema.org JSON-LD envelope.

## 3. Multi-Tool & Multi-Framework Interop
The protocol is framework-agnostic (LangChain, CrewAI, Autogen, PydanticAI) and tool-agnostic.
*   **Tool-Agnostic Invocation**: Uses standard `SearchAction` or `CreateAction` payloads. An agent doesn't care *how* a tool is implemented, only that it satisfies the `protocol_contract`.
*   **Framework Bridging**: The `semantic_extension` includes a `framework_metadata` block to handle internal state-sync between different agentic frameworks.

## 4. Multi-Cloud & Hybrid Topology
Total resilience by operating across AWS, GCP, Azure, and Private Clouds.
*   **Cross-Cloud Routing**: Uses the `GeographyState` and `GeopoliticalState` to determine optimal task placement.
*   **Cloud-Agnostic Addressing**: Agents use URNs (e.g., `urn:agnxxt:agent:id`) rather than IP addresses, allowing the kernel's service mesh to route messages across cloud boundaries.

---

## The Universal A2A Envelope (Schema.org)

All A2A communication MUST use the `CommunicateAction` type with the following universal extensions:

```json
{
  "@context": "https://schema.org",
  "@type": "CommunicateAction",
  "name": "Multi-Dimensional A2A Exchange",
  "agent": { "@type": "SoftwareApplication", "name": "Agent-Python-AWS" },
  "recipient": { "@type": "SoftwareApplication", "name": "Agent-Go-Azure" },
  "semantic_extension": {
    "taxonomy": { "labels": ["multi_modal", "cross_framework", "multi_cloud"] },
    "attributes": {
      "modalities": {
        "primary": "text",
        "attachments": ["urn:agnxxt:artifact:image-context-01"]
      },
      "framework_bridge": {
        "source_framework": "langchain",
        "target_framework": "custom-go-runtime",
        "state_transfer_token": "xyz-789"
      },
      "cloud_topology": {
        "source_region": "us-east-1",
        "target_region": "westeurope",
        "routing_policy": "latency_optimized"
      }
    },
    "vocabulary": {
      "namespace": "https://agnxxt.com/vocab/a2a/",
      "terms": [{"term": "state_transfer_token", "definition": "Handover token for framework interop"}]
    }
  },
  "payload": {
    "text": "Analyze this image for security threats in the London office.",
    "language": "en-GB"
  }
}
```

## A2A Interoperability Harness
The harness verifies that an agent can:
1.  **Parse** a multi-modal payload.
2.  **Translate** its internal state for a foreign framework.
3.  **Route** a message across a cloud boundary (simulated via zone-failure injection).
