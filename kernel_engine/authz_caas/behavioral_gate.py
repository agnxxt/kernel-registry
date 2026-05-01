from typing import Dict, Any, List, Optional
from kernel_engine.event_bus import EventBus

class BehavioralGate:
    """
    The enforcement point for CAAS v2.
    Intercepts actions and blocks before the AuthZ core if drift is too high.
    """
    def __init__(self):
        self.bus = EventBus()
        self.warn_threshold = 400
        self.block_threshold = 800

    def check_intercept(self, agent_id: str, drift_score: int) -> Dict[str, Any]:
        """
        Determines if the action should be blocked, flagged, or passed.
        """
        # Publish drift event to Redpanda
        self.bus.publish("cognitive.drift.events", {
            "agent_id": agent_id,
            "drift_score": drift_score,
            "verdict": "BLOCK" if drift_score >= self.block_threshold else "PASS"
        })

        if drift_score >= self.block_threshold:
            return {
                "decision": "BLOCK",
                "reason": f"Security Critical: Cognitive drift score {drift_score} exceeds block threshold."
            }
        
        if drift_score >= self.warn_threshold:
            return {
                "decision": "WARN",
                "reason": f"Governance Alert: Cognitive drift score {drift_score} elevated. M-of-N review suggested.",
                "requires_approval": True
            }

        return {"decision": "PASS"}

