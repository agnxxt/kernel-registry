import json
import os
import requests
from typing import Dict, Any, List

class PolicyEngine:
    """
    Enforces Deontic Constraints using OPA (Law) and OpenFGA (Relationships).
    """
    def __init__(self):
        self.opa_url = os.getenv("OPA_URL", "http://opa:8181/v1/data/kernel/authz/allow")
        self.fga_url = os.getenv("FGA_URL", "http://openfga:8081")

    def evaluate_action(self, agent_id: str, action: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Performs dual-layer policy evaluation.
        """
        # 1. Ownership / Relationship Check (OpenFGA)
        # In a real system, we would call the FGA 'Check' API here.
        # e.g. "Can user X manage agent Y?"
        fga_result = self._check_relationships(agent_id, action, context)
        if not fga_result["allowed"]:
            return fga_result

        # 2. Deontic / Constitutional Check (OPA)
        input_data = {
            "input": {
                "agent_id": agent_id,
                "action": action,
                "context": context
            }
        }

        try:
            response = requests.post(self.opa_url, json=input_data, timeout=2)
            if response.status_code == 200:
                result = response.json().get("result", False)
                if result:
                    return {"allowed": True, "policy_id": "urn:agnxxt:policy:governed"}
                else:
                    return {"allowed": False, "reason": "Deontic Violation: OPA policy denied action."}
        except Exception as e:
            print(f"OPA Connection Error: {e}")
            
        # Hardcoded Fail-Safe
        target = str(action.get("object", "")).lower()
        if any(r in target for r in ["payroll", "nuclear"]):
             return {"allowed": False, "reason": "Fail-Safe: Restricted target detected."}

        return {"allowed": True, "policy_id": "urn:agnxxt:policy:fail-safe-allow"}

    def _check_relationships(self, agent_id: str, action: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Simulates the OpenFGA Relationship Check.
        """
        # For production: call OpenFGA check endpoint
        # For v1: assume owner is authorized if flag is set in context
        if not context.get("is_authorized_owner", True):
             return {"allowed": False, "reason": "FGA Violation: Invalid agent-user relationship."}
        
        return {"allowed": True}
