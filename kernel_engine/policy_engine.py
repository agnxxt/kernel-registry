import json
import os
import requests
from typing import Dict, Any, List

class PolicyEngine:
    """
    Enforces Deontic Constraints using OPA (Open Policy Agent).
    """
    def __init__(self):
        self.opa_url = os.getenv("OPA_URL", "http://opa:8181/v1/data/kernel/authz/allow")

    def evaluate_action(self, agent_id: str, action: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Performs a full policy evaluation via OPA.
        """
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
                    return {"allowed": True, "policy_id": "urn:agnxxt:policy:opa-rego"}
                else:
                    return {"allowed": False, "reason": "Deontic Violation: OPA policy denied action."}
        except Exception as e:
            # Fallback to local hardcoded safety if OPA is down
            print(f"OPA Connection Error: {e}")
            
        # Hardcoded Fail-Safe
        target = str(action.get("object", "")).lower()
        if any(r in target for r in ["payroll", "nuclear"]):
             return {"allowed": False, "reason": "Fail-Safe: Restricted target detected."}

        return {"allowed": True, "policy_id": "urn:agnxxt:policy:fail-safe-allow"}
