from typing import Dict, Any, List, Optional
from datetime import datetime
from kernel_engine.authz_caas.policy_engine import PolicyEngine
from kernel_engine.authz_caas.cgl_layer import CognitiveGuardLayer
from kernel_engine.authz_caas.behavioral_gate import BehavioralGate
from kernel_engine.secret_kernel import SecretKernel
from persistence.db import SessionLocal
from persistence.models.identity import CanonicalIdentity

class CaasGateway:
    """
    Agentic Automation Governance For Every Entity (AAGFE) / CAAS v2.
    The primary zero-trust authorization infrastructure for AI Agents.
    """
    def __init__(self):
        self.policies = PolicyEngine()
        self.cgl = CognitiveGuardLayer()
        self.gate = BehavioralGate()
        self.secrets = SecretKernel()

    def pre_access_audit(self, agent_id: str, action: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
        """
        CAAS v2 ENFORCEMENT FLOW:
        1. DID Identity Verification
        2. Behavioral Gate (Pre-action drift check)
        3. CGL Validation (Intent, Sycophancy)
        4. AuthZ Core (OPA + OpenFGA)
        """
        # 1. DID Verification
        signature = action.get("signature")
        if signature:
            if not self.secrets.verify_signature(action.get("payload", {}), signature):
                return {"authorized": False, "reason": "AAGFE: Signature Mismatch."}

        # 2. Behavioral Gate
        # Fetch drift score from CGL
        cgl_pre = self.cgl.validate_pre_gate(agent_id, action, context)
        drift_score = cgl_pre.get("drift_score", 0)
        
        gate_verdict = self.gate.check_intercept(agent_id, drift_score)
        if gate_verdict["decision"] == "BLOCK":
            return {"authorized": False, "reason": gate_verdict["reason"]}

        # 3. CGL Integrity check
        if not cgl_pre["safe"]:
             return {"authorized": False, "reason": cgl_pre["reason"]}

        # 4. AuthZ Core (Law & Relationships)
        context["drift_score"] = drift_score
        policy_res = self.policies.evaluate_action(agent_id, action, context)
        
        return {
            "authorized": policy_res["allowed"],
            "reason": policy_res.get("reason", "AAGFE Approved"),
            "drift_score": drift_score,
            "injection": cgl_pre.get("injection"),
            "requires_approval": gate_verdict.get("requires_approval", False)
        }

    def post_access_audit(self, agent_id: str, action: Dict[str, Any], result: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
        """
        POST-ACCESS LOOP: Detects leaks and CoT violations after execution.
        """
        # Leak detection
        output = str(result.get("value", "")).lower()
        if any(p in output for p in ["password", "token", "ssn"]):
            return {"authorized": False, "reason": "AAGFE: Post-access data leak detected."}

        # CoT reasoning audit
        cgl_post = self.cgl.validate_post_gate(agent_id, action.get("result_raw", ""), result)
        if not cgl_post["safe"]:
            return {"authorized": False, "reason": cgl_post["reason"]}

        return {"authorized": True, "reason": "AAGFE Approved"}

    def authorize_action(self, agent_id: str, action: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
        return self.pre_access_audit(agent_id, action, context)
