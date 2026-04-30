# IoT & Hardware Integration: Cognitive Grounding in Physical Devices

This document formalizes how the Agent Kernel interacts with the physical world. By treating **Hardware** and **IoT Devices** as first-class entities in the Knowledge Graph, agents can ground their digital reasoning in physical reality (e.g., sensor data, actuator control, and compute-on-edge).

---

## 1. Physical Grounding via Devices
Devices act as the "Sensory Organs" of the agent network.

*   **IoT Sensors**: Provide real-time `Context` (Weather, Temperature, Proximity, Biometrics).
*   **Acoustic & Ambient Sensors**: Capture background noise levels, ambient soundscapes, and music. (e.g., Identifying a high-stress environment via noise levels, or recognizing a cultural setting via background music).
*   **Edge Hardware**: Specialized compute units (GPUs, TPUs, NPUs) where an agent may reside.
*   **Actuators**: Physical tools an agent can control (e.g., Smart Locks, Robotic Arms, Industrial Control Systems).

## 2. Hardware-Aware Decision Making
The `DualProcessTheory` and `CognitiveProfile` are modified by hardware constraints.

*   **Battery & Power Constraint**: An agent on a low-power IoT device might be forced into "Deep Fast-Thinking" mode (System 1) to conserve battery, whereas an agent on a plugged-in server can engage in "Slow-Thinking" (System 2).
*   **Hardware-Locked Security**: Using TPM (Trusted Platform Module) or Secure Enclaves to store `cryptographic_signatures` for the `audit_tracking` of actions.

## 3. IoT Probing & Stigmergy
*   **Physical Probing**: An `active_probe` can target a physical device (e.g., "Check if the IoT-Thermostat is responding").
*   **Hardware Stigmergy**: Agents leave traces on shared hardware resources. For example, marking a specific GPIO pin or a GPU partition as `LOCKED` so other agents coordinate physical access.

---

## Universal Schema Mapping (Schema.org)

| IoT Concept | Schema.org `@type` | Semantic Extension Block |
| :--- | :--- | :--- |
| **IoT Sensor** | `Device` / `PropertyValue` | `attributes.physical_reading`, `attributes.sampling_rate` |
| **Compute HW** | `HardwareConfiguration` | `attributes.compute_capability`, `attributes.accelerator_type` |
| **Actuator** | `ControlAction` | `attributes.physical_target`, `attributes.safety_stop_id` |

## JSON-LD Example: IoT Sensor Context Registration

```json
{
  "@context": "https://schema.org",
  "@type": "AssessAction",
  "name": "Register Physical Context: IoT Environmental Sensor",
  "agent": { "@type": "SoftwareApplication", "name": "Context-Harvester-IoT" },
  "object": {
    "@type": "Device",
    "name": "Warehouse-Temp-Sensor-04",
    "identifier": "urn:agnxxt:device:hw-99812"
  },
  "semantic_extension": {
    "taxonomy": { "labels": ["iot_context", "physical_grounding"] },
    "attributes": {
      "physical_state": {
        "temperature_celsius": 22.5,
        "humidity_percentage": 45.0,
        "is_tamper_evident": false
      },
      "hardware_telemetry": {
        "battery_level": 0.82,
        "firmware_version": "2.4.1-stable"
      }
    },
    "ontology": {
      "relations": [
        {
          "subject": "urn:agnxxt:place:West-Warehouse",
          "predicate": "EXPERIENCING",
          "object": "urn:agnxxt:context:temp-reading-04"
        }
      ]
    }
  }
}
```

## Hardware/IoT Reliability Harness
The harness verifies physical safety and hardware reliability:
1.  **Fault Tolerance**: If a sensor fails, the harness verifies that the agent shifts to its `alternative_belief_source` (e.g., historical data or a different cloud-based API).
2.  **Safety Interlocks**: Verify that `deontic_constraints` are applied to hardware actions (e.g., "Do not operate Robotic Arm if proximity sensor detects a Human").
