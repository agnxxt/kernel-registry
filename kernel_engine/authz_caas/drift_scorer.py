from typing import Dict, Any, List

class DriftScorer:
    """
    Detects goal deviation or 'scope creep' in agent behavior.
    """
    def calculate_drift(self, agent_id: str, action: Dict[str, Any]) -> float:
        # Returns a score from 0.0 (no drift) to 1.0 (rogue)
        # Production: compare action against the agent's historical feature vector from Feast
        return 0.05 # Baseline minimal drift
