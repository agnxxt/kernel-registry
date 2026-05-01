from typing import Dict, Any, List, Optional
from datetime import datetime
from kernel_engine.authz_caas.policy_engine import PolicyEngine
from kernel_engine.authz_caas.cgl_layer import CognitiveGuardLayer
from kernel_engine.secret_kernel import SecretKernel
from persistence.db import SessionLocal
from persistence.models.identity import CanonicalIdentity

class CaasGateway:
    """
    Continuous Autonomous Authorization System (CAAS).
    Implements 'Double-Gate' Governance linked with the Cognitive Guard Layer (CGL).
    """
    def __init__(self):
        self.policies = PolicyEngine()
        self.cgl = CognitiveGuardLayer() # Formal CGL Integration
        self.secrets = SecretKernel()

    def pre_access_audit(self, agent_id: str, action: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
        """
        GATE 1: Evaluated BEFORE tool access.
        Linked with CGL for Intent, Drift, and Sycophancy detection.
        """
        # 1. Decentralized Identity Verification
        signature = action.get("signature")
        if signature:
            is_authentic = self.secrets.verify_signature(action.get("payload", {}), signature)
            if not is_authentic:
                return {"authorized": False, "reason": "Security Error: Cryptographic signature mismatch."}

        # 2. Federated CIAM & Lifecycle Check
        with SessionLocal() as session:
            identity = session.query(CanonicalIdentity).filter_by(canonical_id=agent_id).first()
            if not identity:
                 return {"authorized": False, "reason": "Sovereignty Error: Agent identity not registered."}
            
            now = datetime.utcnow()
            if identity.grant_expires_at and now > identity.grant_expires_at:
                return {"authorized": False, "reason": "Grant Expired: Temporal access revoked."}

            if identity.domain in ["EXTERNAL", "VENDOR", "CUSTOMER"] and not identity.sponsor_id:
                return {"authorized": False, "reason": "CIAM Violation: Missing internal sponsor."}
            
            context["agent_domain"] = identity.domain
            context["has_sponsor"] = identity.sponsor_id is not None

        # 3. Cognitive Guard Layer (CGL) Pre-Gate
        cgl_result = self.cgl.validate_pre_gate(agent_id, action, context)
        if not cgl_result["safe"]:
            return {"authorized": False, "reason": cgl_result["reason"]}
        
        context["drift_score"] = cgl_result.get("drift_score", 0.0)

        # 4. Policy Check (OPA + OpenFGA)
        policy_result = self.policies.evaluate_action(agent_id, action, context)
        
        return {
            "authorized": policy_result["allowed"],
            "reason": policy_result.get("reason", "Pre-Audit Approved"),
            "phase": "PRE_TOOL",
            "policy_id": policy_result.get("policy_id")
        }

    def post_access_audit(self, agent_id: str, action: Dict[str, Any], result: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
        """
        GATE 2: Evaluated AFTER tool access.
        Linked with CGL for CoT and reasoning forensic audits.
        """
        # 1. Inspect Result for Sensitive Data Leakage
        output_text = str(result.get("value", "")).lower()
        restricted_patterns = ["password", "token", "ssn", "secret"]
        for pattern in restricted_patterns:
            if pattern in output_text:
                return {"authorized": False, "reason": f"Post-Audit Leak: Restricted pattern detected.", "phase": "POST_TOOL"}

        # 2. Cognitive Guard Layer (CGL) Post-Gate
        reasoning = action.get("result_raw", "")
        cgl_post_res = self.cgl.validate_post_gate(agent_id, reasoning, result)
        if not cgl_post_res["safe"]:
             return {"authorized": False, "reason": cgl_post_res["reason"], "phase": "POST_TOOL"}

        return {"authorized": True, "reason": "Post-Audit Approved", "phase": "POST_TOOL"}

    def authorize_action(self, agent_id: str, action: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
        return self.pre_access_audit(agent_id, action, context)

    def audit_reasoning(self, agent_id: str, reasoning: str) -> Dict[str, Any]:
        return self.cgl.validate_post_gate(agent_id, reasoning, {})
