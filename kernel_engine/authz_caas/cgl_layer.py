from typing import Dict, Any, List

class IntentRegistry:
    def validate_intent(self, agent_id: str, action: Dict[str, Any]) -> Dict[str, Any]:
        return {"valid": True, "intent": action.get("name", "Unknown")}

class CoTAuditor:
    def audit_reasoning(self, agent_id: str, reasoning: str) -> Dict[str, Any]:
        forbidden = ["bypass", "ignore", "override safety"]
        violations = [w for w in forbidden if w in reasoning.lower()]
        return {"safe": len(violations) == 0}

class DriftScorer:
    def calculate_drift(self, agent_id: str, action: Dict[str, Any]) -> float:
        return 0.05

class SycophancyGuard:
    def check_erosion(self, agent_id: str, action: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
        if context.get("impact_level", 0) > 8 and "as you wish" in str(action).lower():
            return {"detected": True, "reason": "Sycophancy detected"}
        return {"detected": False}

class CognitiveGuardLayer:
    """
    OpenAGX Cognitive Guard Layer (CGL).
    Orchestrates the specialized security components for AI agents.
    """
    def __init__(self):
        self.intent_registry = IntentRegistry()
        self.cot_auditor = CoTAuditor()
        self.drift_scorer = DriftScorer()
        self.sycophancy_guard = SycophancyGuard()

    def validate_pre_gate(self, agent_id: str, action: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
        intent_res = self.intent_registry.validate_intent(agent_id, action)
        if not intent_res["valid"]:
            return {"safe": False, "reason": "CGL: Intent Registry validation failed."}

        drift_score = self.drift_scorer.calculate_drift(agent_id, action)
        if drift_score > 0.8:
            return {"safe": False, "reason": f"CGL: High Cognitive Drift detected ({drift_score})"}

        syc_res = self.sycophancy_guard.check_erosion(agent_id, action, context)
        if syc_res["detected"]:
            return {"safe": False, "reason": f"CGL: {syc_res['reason']}"}

        return {"safe": True, "drift_score": drift_score}

    def validate_post_gate(self, agent_id: str, reasoning: str, result: Dict[str, Any]) -> Dict[str, Any]:
        cot_res = self.cot_auditor.audit_reasoning(agent_id, reasoning)
        if not cot_res["safe"]:
            return {"safe": False, "reason": "CGL: Post-access reasoning audit failed."}
        return {"safe": True}
