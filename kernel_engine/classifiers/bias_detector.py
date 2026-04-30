from typing import Dict, Any, List

class BiasDetector:
    """
    Analyzes temporal weighting to detect Recency Bias autonomously.
    """
    def detect(self, trust_ledger: Dict[str, Any], action_history: List[Dict[str, Any]]) -> List[str]:
        found_biases = []
        
        # Heuristic: If the trust score for a source changed by > 0.5 
        # based on a single interaction, flag potential Recency Bias.
        for entity, data in trust_ledger.items():
            if data.get("interactions_count", 0) < 5 and data.get("score", 0) > 0.8:
                # High trust with low interaction count suggests "Early-Winner" recency bias
                found_biases.append("recency_bias_trust_skew")

        return found_biases
