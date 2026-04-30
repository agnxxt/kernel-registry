# Macro-Context Framework: Culture, Geopolitics, Geography, Climate, and Economy

Agents must operate through the "Lens" of Macro-Context. This framework defines how large-scale environmental and societal factors constrain or enable agent reasoning and actions.

---

## 1. Cultural Aspects (`CultureLens`)
Defines the norms, values, and communication styles of a specific human or agent collective.
*   **Attributes**: `communication_style` (High-Context vs. Low-Context), `value_priority` (Individualism vs. Collectivism), `power_distance_index`.
*   **Impact**: Modifies `NegotiationTheory` and `dual_process_theory`. (e.g., An agent in a high-power-distance culture might escalate to human authority more frequently).

## 2. Societal Context (`SocietyState`)
Defines the social structures, demographics, and collective behaviors of a population.
*   **Attributes**: `demographic_profile`, `social_class_distribution`, `religious_norm_index`, `prevailing_social_trends`.
*   **Impact**: Modifies `organization_science` and `epistemic_trust`. (e.g., Agent trust weights are adjusted based on shared societal values or conflicting social norms).

## 3. Linguistic Context (`LanguageLens`)
Defines the communication medium, including dialects, idioms, and semantic nuances.
*   **Attributes**: `primary_language_iso`, `dialect_id`, `formality_level` (Honorifics vs. Casual), `semantic_drift_index`.
*   **Impact**: Modifies `CommunicateAction` and `theory_of_mind`. (e.g., An agent must translate not just words, but the "intent" filtered through high-formality linguistic norms).

## 4. Aesthetic & Creative Context (`AestheticLens`)
Defines the creative, symbolic, and emotional medium through which information and intent are expressed.
*   **Literature**: Narrative structures, rhetorical devices, and stylistic canons (e.g., Epic vs. Minimalist).
*   **Art**: Visual semiotics, color theory, and historical movements (e.g., Bauhaus vs. Baroque).
*   **Music**: Rhythmic cadence, tonal resonance, and emotional harmonics (e.g., Uplifting vs. Somber).
*   **Impact**: Modifies `CommunicationAction` style and `result` presentation. (e.g., An agent delivering a critical update might adopt a "minimalist literature" style to ensure clarity, or a "somber music" cadence to match the gravity of an emergency).

## 5. Religion & Belief Systems (`BeliefSystemLens`)
Defines the theological, ethical, and ritualistic frameworks that govern human or community behavior.
*   **Attributes**: `primary_theology`, `ethical_prohibitions` (e.g., Dietary, Financial/Usury), `sacred_temporal_cycles` (Prayer times, Sabbaths, Festivals), `behavioral_norms`.
*   **Impact**: Modifies `deontic_constraints` and `TemporalNuance`. (e.g., An agent might automatically defer a non-critical `TradeAction` during a sacred window, or filter recommendations to adhere to ethical/religious prohibitions).

## 6. Geopolitical Context (`GeopoliticalState`)
Defines the political boundaries, regulatory jurisdictions, and international relations impacting an agent.
*   **Attributes**: `jurisdiction_id`, `sanction_status`, `regulatory_compliance_regime` (e.g., GDPR, EU-AI-Act).
*   **Impact**: Modifies `deontic_constraints`. (e.g., An agent cannot initiate a `TransferAction` between two jurisdictions with an active trade embargo).

## 3. Geographic Context (`GeographyState`)
The physical or virtual topology where an action is located.
*   **Attributes**: `terrain_type`, `urban_density`, `network_topology_region`.
*   **Impact**: Modifies `predictive_control` and `allowed_heuristics`. (e.g., Logistics heuristics for "Urban" are invalidated in "Remote Mountainous" terrain).

## 4. Climate & Weather (`ClimateState`)
Long-term climate patterns and real-time weather phenomena.
*   **Attributes**: `average_temperature`, `active_disaster_risk`, `real_time_weather_event` (Storm, Heatwave).
*   **Impact**: Modifies `ActionStatus` and `CriticalityOverrides`. (e.g., Severe weather triggers a shift from "Economy" to "Max-Reliability" broadcast mode).

## 5. Economic Context (`EconomyState`)
The market conditions, resource availability, and currency dynamics.
*   **Attributes**: `market_volatility_index`, `resource_scarcity_level` (e.g., GPU shortage), `fiat_vs_token_parity`.
*   **Impact**: Modifies `BargainingTheory` and `CognitiveProfile/epistemic_budget`. (e.g., During high volatility, the agent's `epistemic_budget` is increased to allow for more frequent `active_probe` calls).

---

## Universal Schema Mapping

| Macro Dimension | Schema.org `@type` | Relational Edge |
| :--- | :--- | :--- |
| **Culture** | `Intangible` / `SpecialAnnouncement` | `[Agent] -ADHERES_TO-> [Culture]` |
| **Geopolitics**| `GovernmentOrganization` / `AdministrativeArea` | `[Action] -SUBJECT_TO-> [Geopolitics]` |
| **Geography** | `Place` / `GeoShape` | `[Action] -OCCURS_IN-> [Geography]` |
| **Climate** | `WeatherForecast` / `Event` | `[Place] -EXPERIENCING-> [Climate]` |
| **Economy** | `MonetaryAmount` / `ExchangeRate` | `[Bargaining] -CONSTRAINED_BY-> [Economy]` |

## JSON-LD Example: Geopolitical and Cultural Filtering

```json
{
  "@context": "https://schema.org",
  "@type": "AssessAction",
  "name": "Cross-Border Data Verification",
  "agent": { "@type": "SoftwareApplication", "name": "Global-Auditor-01" },
  "semantic_extension": {
    "taxonomy": { "labels": ["geopolitics", "cultural_alignment"] },
    "attributes": {
      "geopolitical_context": {
        "source_jurisdiction": "EU",
        "target_jurisdiction": "US",
        "compliance_check": "Privacy-Shield-2.0"
      },
      "cultural_context": {
        "primary_norm": "High-Transparency",
        "expected_response_latency": "Business-Day"
      }
    },
    "ontology": {
      "relations": [
        {
          "subject": "urn:agnxxt:action:verify-445",
          "predicate": "SUBJECT_TO",
          "object": "urn:agnxxt:geopol:GDPR-Reg-2026"
        }
      ]
    }
  }
}
```
