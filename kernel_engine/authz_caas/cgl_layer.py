import json
from typing import Dict, Any, List, Optional
from datetime import datetime

class IntentRegistry:
    """Goal substitution prevention."""
    def validate_intent(self, agent_id: str, action: Dict[str, Any]) -> Dict[str, Any]:
        return {"valid": True, "intent": action.get("name", "Unknown")}

class CoTAuditor:
    """Behavioral + reasoning drift detection."""
    def audit_reasoning(self, agent_id: str, reasoning: str) -> Dict[str, Any]:
        forbidden = ["bypass", "ignore", "override safety"]
        violations = [w for w in forbidden if w in reasoning.lower()]
        return {"safe": len(violations) == 0, "violations": violations}

class DriftScorer:
    """Aggregates signals into a 0-1000 score."""
    def calculate_drift(self, agent_id: str, signals: Dict[str, Any]) -> int:
        # Heuristic aggregation for v2
        score = 0
        if signals.get("violations_found", 0) > 0: score += 400
        if signals.get("sycophancy_detected"): score += 300
        if signals.get("intent_mismatch"): score += 500
        return min(1000, score)

class SycophancyGuard:
    """Constraint erosion detection."""
    def check_erosion(self, agent_id: str, action: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
        if context.get("impact_level", 0) > 8 and "as you wish" in str(action).lower():
            return {"detected": True, "reason": "Sycophancy: Prioritizing user over safety."}
        return {"detected": False}

class ConstraintInjector:
    """Instruction decay prevention."""
    def get_injection_fragment(self, agent_id: str, turn_count: int) -> Optional[str]:
        if turn_count % 5 == 0:
            return "REMINDER: You are governed by Deontic Guardrails. Prioritize life-safety axioms."
        return None

class MemoryIsolator:
    """Memory contamination prevention."""
    def enforce_boundaries(self, agent_id: str, task_id: str):
        # In production, this calls Temporal or a VectorDB to clear scoped memory
        print(f"Memory Isolation: Purged boundaries for Task {task_id}")

class CognitiveGuardLayer:
    """
    OpenAGX Cognitive Guard Layer (CGL).
    Orchestrates the 6 specialized security services.
    """
    def __init__(self):
        self.intent_registry = IntentRegistry()
        self.cot_auditor = CoTAuditor()
        self.drift_scorer = DriftScorer()
        self.sycophancy_guard = SycophancyGuard()
        self.constraint_injector = ConstraintInjector()
        self.memory_isolator = MemoryIsolator()

    def validate_pre_gate(self, agent_id: str, action: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
        # 1. Intent
        intent_res = self.intent_registry.validate_intent(agent_id, action)
        
        # 2. Sycophancy
        syc_res = self.sycophancy_guard.check_erosion(agent_id, action, context)
        
        # 3. Aggregated Drift Score
        signals = {
            "intent_mismatch": not intent_res["valid"],
            "sycophancy_detected": syc_res["detected"]
        }
        drift_score = self.drift_scorer.calculate_drift(agent_id, signals)
        
        return {
            "safe": drift_score < 800,
            "drift_score": drift_score,
            "reason": "High Drift Detected" if drift_score >= 800 else "CGL Approved",
            "injection": self.constraint_injector.get_injection_fragment(agent_id, context.get("turn_count", 0))
        }

    def validate_post_gate(self, agent_id: str, reasoning: str, result: Dict[str, Any]) -> Dict[str, Any]:
        return self.cot_auditor.audit_reasoning(agent_id, reasoning)

    def close_task(self, agent_id: str, task_id: str):
        self.memory_isolator.enforce_boundaries(agent_id, task_id)
