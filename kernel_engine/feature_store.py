from typing import Dict, Any, List

class CognitiveFeatureStore:
    """
    Stores and retrieves pre-calculated cognitive features.
    Provides grounding data for DecisionStrategy and TheoryIdentifier.
    """
    def __init__(self):
        # Mock Feature Store
        self._features = {
            "agent-worker-01": {
                "avg_latency_ms": 120,
                "historical_hallucination_rate": 0.05,
                "common_biases": ["recency"],
                "skill_scores": {"sql": 0.95, "sentiment": 0.4}
            }
        }

    def get_agent_features(self, agent_id: str) -> Dict[str, Any]:
        """
        Retrieves the feature vector for a specific agent.
        """
        return self._features.get(agent_id, {
            "avg_latency_ms": 0,
            "historical_hallucination_rate": 0,
            "common_biases": [],
            "skill_scores": {}
        })

    def update_skill_score(self, agent_id: str, skill: str, delta: float):
        """
        Updates an agent's skill competency based on learning loop results.
        """
        if agent_id not in self._features:
            self._features[agent_id] = {"skill_scores": {}}
        
        scores = self._features[agent_id].setdefault("skill_scores", {})
        scores[skill] = max(0, min(1, scores.get(skill, 0.5) + delta))

