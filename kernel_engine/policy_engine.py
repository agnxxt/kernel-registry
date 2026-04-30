import json
import os
from typing import Dict, Any, List

class PolicyEngine:
    """
    Enforces Deontic Constraints based on JSON-defined policies.
    Provides a transition path toward OPA/OpenFGA.
    """
    def __init__(self):
        policy_path = os.getenv("POLICY_PATH", "config/policies.json")
        try:
            with open(policy_path, "r") as f:
                self.config = json.load(f)
        except Exception:
            # Fallback to minimal safe policies
            self.config = {
                "global_policies": {
                    "max_token_per_action": 10000,
                    "restricted_objects": ["payroll"]
                },
                "deontic_guardrails": []
            }

    def evaluate_action(self, agent_id: str, action: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Performs a full policy evaluation (Allow/Deny).
        """
        global_policies = self.config.get("global_policies", {})
        
        # 1. Check Restricted Objects
        target = str(action.get("object", "")).lower()
        for restricted in global_policies.get("restricted_objects", []):
            if restricted in target:
                return {"allowed": False, "reason": f"Deontic Violation: Access to {restricted} is prohibited."}

        # 2. Check Dynamic Guardrails
        action_string = str(action).lower()
        # Simple evaluation of guardrail conditions
        for guard in self.config.get("deontic_guardrails", []):
            # This is a safe 'eval-like' check for demonstration
            # In real production, use OPA/Rego
            if "weather == 'Raining'" in guard["condition"] and context.get("weather") == "Raining":
                if "'walk' in action_string" in guard["condition"] and "walk" in action_string:
                    return {"allowed": False, "reason": guard["reason"]}

        # 3. Quota Check
        requested_tokens = action.get("runtime", {}).get("resource_governance", {}).get("token_budget", 0)
        if requested_tokens > global_policies.get("max_token_per_action", 10000):
             return {"allowed": False, "reason": "Quota Exceeded: Token budget exceeds global policy."}

        # 4. Relationship Check (FGA)
        if not context.get("is_authorized_owner", True):
             return {"allowed": False, "reason": "Authorization Failed: Invalid agent-user relationship."}

        return {"allowed": True, "policy_id": "urn:agnxxt:policy:dynamic-json"}
