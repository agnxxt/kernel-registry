# Building Agent Reliability Harnesses

This guide explains how to use the Agent Kernel's cognitive and operational schemas to build **Reliability Harnesses**. 

A harness is an external system or test framework that monitors, evaluates, and controls an agent at runtime. By utilizing our standardized schemas, you can build harnesses that evaluate agents not just on output accuracy, but on their internal cognitive processes and structural safety.

## 1. Evaluating Predictive Control (`predictive_control`)
The `predictive-control.schema.json` dictates that agents must simulate irreversible actions.
*   **Harness Implementation:** Your harness should monitor the agent's action stream. When the agent attempts an action flagged with a high `irreversibility_threshold`, the harness must verify that a corresponding "simulation step" or "blast radius estimation" was executed *prior* to the action.
*   **Test Injection:** Inject a fake high-risk scenario (e.g., a "delete database" request). The harness passes if the agent halts and runs a simulation; it fails if the agent attempts immediate execution.

## 2. Managing the Speed/Accuracy Trade-off (`dual_process_theory`)
The `dual-process-theory.schema.json` defines when an agent should think fast (System 1) vs. slow (System 2).
*   **Harness Implementation:** The harness should track token usage and latency. For routine tasks, the harness should enforce strict timeouts (validating the `default_pathway`). For tasks flagged as highly aligned with the agent's goals or carrying critical risk, the harness should relax latency constraints and verify that `mandatory_routines` (like multi-source verification) were invoked.
*   **Test Injection:** Send identical tasks, varying only the context to manipulate the `critical_failure_risk`. Measure the difference in response time and token consumption.

## 3. Auditing Belief Updates (`active_probe` & `epistemic_trust`)
Agents form subjective beliefs (`theory_of_mind`) based on public data, but must test them empirically (`active_probe`) and weigh them by source credibility (`epistemic_trust`).
*   **Harness Implementation:** The harness should read the agent's `entity_trust_ledger`. If the agent receives information from a low-trust source, the harness should assert that the agent either ignores the info or triggers an `active_probe` to verify it.
*   **Test Injection:** Have a "known bad" (low trust) simulated agent send critical information to the target agent. Verify that the target agent's `epistemic_update` correctly discounts the information according to its `assimilation_policy`.

## 4. Validating Environmental Coordination (`organizational_coordination`)
Agents coordinate via roles and Stigmergy (environmental traces) to prevent cascading failures.
*   **Harness Implementation:** The harness should monitor shared resources (e.g., vector indices, caches) for `environmental_markers`. If Agent A encounters an error, the harness verifies that Agent A left a trace, and that Agent B subsequently reads that trace and alters its behavior before encountering the same error.
*   **Test Injection:** Simulate a failure in a downstream service. Verify that the first agent to fail drops a stigmergic marker, and that the `required_quorum` or `escalation_path` rules are followed before other agents attempt the same action.
