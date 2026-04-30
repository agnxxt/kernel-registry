from typing import Dict, Any, Optional
from datetime import datetime

class IdentityTrustManager:
    """
    Manages the Dynamic Epistemic Trust Ledger for agents and sources.
    """
    def __init__(self):
        # Initializing with baseline trust values from schema
        self.ledger = {}

    def get_trust_score(self, entity_id: str) -> float:
        return self.ledger.get(entity_id, {}).get("score", 0.5)

    def update_trust(self, entity_id: str, outcome: str, impact: float = 0.1):
        """
        Updates trust based on validation outcomes.
        """
        if entity_id not in self.ledger:
            self.ledger[entity_id] = {
                "score": 0.5,
                "interactions_count": 0,
                "last_validated": None
            }
        
        current = self.ledger[entity_id]
        current["interactions_count"] += 1
        current["last_validated"] = datetime.utcnow().isoformat()

        if outcome == "success":
            current["score"] = min(1.0, current["score"] + (impact * 0.5))
        elif outcome == "betrayal":
            current["score"] = max(0.0, current["score"] - impact)

    def generate_identity_signature(self, agent_id: str) -> str:
        """
        Generates a token representing the agent's current cognitive identity.
        """
        score = self.get_trust_score(agent_id)
        return f"identity_v1_{agent_id}_{score:.2f}"

