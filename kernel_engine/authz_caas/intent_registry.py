from typing import Dict, Any, List

class IntentRegistry:
    """
    Validates task intent against registered organizational goals.
    """
    def validate_intent(self, agent_id: str, action: Dict[str, Any]) -> Dict[str, Any]:
        intent = action.get("name", "Unknown Task")
        # In production: check against a database of approved intents
        return {"valid": True, "intent": intent}

