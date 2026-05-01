import json
import os
import requests
from typing import Dict, Any, List, Optional

class PolicyEngine:
    """
    Enforces Deontic Constraints using OPA (Law) and OpenFGA (Relationships).
    Implements CAAS 1 (ReBAC) and CAAS 2 (ABAC).
    """
    def __init__(self):
        self.opa_url = os.getenv("OPA_URL", "http://opa:8181/v1/data/kernel/authz/allow")
        self.fga_url = os.getenv("FGA_API_URL", "http://openfga:8081")
        
        # Load FGA Store/Model IDs from config if they exist
        try:
            with open(".fga_config.json", "r") as f:
                config = json.load(f)
                self.fga_store_id = config.get("store_id")
                self.fga_model_id = config.get("model_id")
        except:
            self.fga_store_id = None
            self.fga_model_id = None

    def evaluate_action(self, agent_id: str, action: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Performs dual-layer policy evaluation.
        """
        # 1. Ownership / Relationship Check (OpenFGA - CAAS 1)
        user_id = context.get("user_id", "anonymous")
        fga_result = self._check_relationships(user_id, agent_id, "can_act_as")
        if not fga_result["allowed"]:
            return {"allowed": False, "reason": f"FGA Violation: User {user_id} does not have 'can_act_as' relationship with Agent {agent_id}."}

        # 2. Deontic / Constitutional Check (OPA - CAAS 2)
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

    def _check_relationships(self, user_id: str, agent_id: str, relation: str) -> Dict[str, Any]:
        """
        Calls the real OpenFGA 'Check' API.
        """
        if not self.fga_store_id:
            # Fallback to local simulation if FGA is not setup yet
            print("FGA Not Configured. Using simulation mode.")
            return {"allowed": True} if user_id != "unauthorized" else {"allowed": False}

        check_url = f"{self.fga_url}/stores/{self.fga_store_id}/check"
        payload = {
            "tuple_key": {
                "user": f"user:{user_id}",
                "relation": relation,
                "object": f"agent:{agent_id}"
            },
            "authorization_model_id": self.fga_model_id
        }

        try:
            res = requests.post(check_url, json=payload, timeout=2)
            if res.status_code == 200:
                return {"allowed": res.json().get("allowed", False)}
        except Exception as e:
            print(f"FGA Check Error: {e}")

        # Default Deny on error in production
        return {"allowed": False, "reason": "FGA Service Unreachable"}
