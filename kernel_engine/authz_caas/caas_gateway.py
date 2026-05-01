from typing import Dict, Any, List
from kernel_engine.authz_caas.policy_engine import PolicyEngine
from kernel_engine.authz_caas.intent_registry import IntentRegistry
from kernel_engine.authz_caas.cot_auditor import CoTAuditor
from kernel_engine.authz_caas.drift_scorer import DriftScorer

class CaasGateway:
    """
    Continuous Autonomous Authorization System (CAAS).
    Provides real-time, zero-trust authorization for AI agents.
    """
    def __init__(self):
        self.policies = PolicyEngine()
        self.intent_registry = IntentRegistry()
        self.cot_auditor = CoTAuditor()
        self.drift_scorer = DriftScorer()

    def authorize_action(self, agent_id: str, action: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Performs a multi-layer continuous authorization check.
        """
        # 1. Intent Validation
        intent_result = self.intent_registry.validate_intent(agent_id, action)
        if not intent_result["valid"]:
            return {"authorized": False, "reason": "Intent Registry: Task not approved."}

        # 2. Drift Analysis
        drift_score = self.drift_scorer.calculate_drift(agent_id, action)
        if drift_score > 0.8:
            return {"authorized": False, "reason": f"High Cognitive Drift Detected: {drift_score}"}

        # 3. Policy Check (OPA + OpenFGA)
        # Update context with drift score for policy evaluation
        context["drift_score"] = drift_score
        policy_result = self.policies.evaluate_action(agent_id, action, context)
        
        return {
            "authorized": policy_result["allowed"],
            "reason": policy_result.get("reason", "Approved"),
            "drift_score": drift_score,
            "policy_id": policy_result.get("policy_id")
        }

    def audit_reasoning(self, agent_id: str, reasoning: str) -> Dict[str, Any]:
        """
        Audits the agent's chain-of-thought before finalizing an action.
        """
        return self.cot_auditor.audit_reasoning(agent_id, reasoning)
