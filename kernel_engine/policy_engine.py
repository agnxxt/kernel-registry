from typing import Dict, Any, List

class PolicyEngine:
    """
    Enforces Deontic Constraints using OPA (Open Policy Agent) patterns.
    Handles ABAC and Relationship-based access (OpenFGA).
    """
    def __init__(self):
        # Mocking a set of OPA-style Rego policies
        self.global_policies = {
            "no_cross_jurisdiction_transfer": True,
            "requires_mfa_for_master_push": True,
            "max_token_per_action": 10000
        }

    def evaluate_action(self, agent_id: str, action: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Performs a full policy evaluation (Allow/Deny).
        """
        # 1. Check Deontic Prohibitions from context
        if context.get("weather") == "Raining" and "walk" in str(action).lower():
            return {"allowed": False, "reason": "Safety Violation: Walking prohibited in rain."}

        # 2. Check Budget Constraints
        requested_tokens = action.get("runtime", {}).get("resource_governance", {}).get("token_budget", 0)
        if requested_tokens > self.global_policies["max_token_per_action"]:
             return {"allowed": False, "reason": "Quota Exceeded: Token budget exceeds global policy."}

        # 3. Relationship Check (FGA)
        # e.g. Does User X own Agent Y?
        if not context.get("is_authorized_owner", True):
             return {"allowed": False, "reason": "Authorization Failed: Invalid agent-user relationship."}

        return {"allowed": True, "policy_id": "urn:agnxxt:policy:default-allow"}

