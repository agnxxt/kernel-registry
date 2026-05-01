from typing import Dict, Any, List, Optional
from datetime import datetime
from kernel_engine.authz_caas.policy_engine import PolicyEngine
from kernel_engine.authz_caas.intent_registry import IntentRegistry
from kernel_engine.authz_caas.cot_auditor import CoTAuditor
from kernel_engine.authz_caas.drift_scorer import DriftScorer
from kernel_engine.secret_kernel import SecretKernel
from persistence.db import SessionLocal
from persistence.models.identity import CanonicalIdentity

class CaasGateway:
    """
    Continuous Autonomous Authorization System (CAAS).
    Implements 'Double-Gate' Decentralized Governance: Pre- and Post-Tool policy evaluation.
    """
    def __init__(self):
        self.policies = PolicyEngine()
        self.intent_registry = IntentRegistry()
        self.cot_auditor = CoTAuditor()
        self.drift_scorer = DriftScorer()
        self.secrets = SecretKernel()

    def pre_access_audit(self, agent_id: str, action: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
        """
        GATE 1: Evaluated BEFORE tool access.
        Checks Identity (DID), Sponsorship, Temporal Grants, and Deontic Rules.
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
            
            # Temporal Grant Validation
            now = datetime.utcnow()
            if identity.grant_expires_at and now > identity.grant_expires_at:
                return {"authorized": False, "reason": "Grant Expired: Temporal access revoked."}

            # Sponsorship Check
            if identity.domain in ["EXTERNAL", "VENDOR", "CUSTOMER"] and not identity.sponsor_id:
                return {"authorized": False, "reason": "CIAM Violation: Missing internal sponsor/handshake."}
            
            context["agent_domain"] = identity.domain
            context["has_sponsor"] = identity.sponsor_id is not None

        # 3. Intent & Drift Analysis
        intent_result = self.intent_registry.validate_intent(agent_id, action)
        if not intent_result["valid"]:
            return {"authorized": False, "reason": "Intent Registry: Task not approved."}

        drift_score = self.drift_scorer.calculate_drift(agent_id, action)
        context["drift_score"] = drift_score

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
        Audits tool output for data leaks, sycophancy, or unexpected state changes.
        """
        # 1. Inspect Result for Sensitive Data Leakage
        output_text = str(result.get("value", "")).lower()
        restricted_patterns = ["password", "token", "ssn", "secret"]
        for pattern in restricted_patterns:
            if pattern in output_text:
                return {
                    "authorized": False, 
                    "reason": f"Post-Audit Violation: Tool output contains restricted pattern '{pattern}'",
                    "phase": "POST_TOOL"
                }

        # 2. CoT Audit (Reasoning vs. Reality)
        reasoning = action.get("result_raw", "")
        if reasoning:
            cot_result = self.cot_auditor.audit_reasoning(agent_id, reasoning)
            if not cot_result["safe"]:
                 return {
                    "authorized": False, 
                    "reason": "Post-Audit Violation: Chain-of-Thought discrepancy detected.",
                    "phase": "POST_TOOL"
                 }

        return {
            "authorized": True, 
            "reason": "Post-Audit Approved",
            "phase": "POST_TOOL"
        }

    def authorize_action(self, agent_id: str, action: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
        # Legacy support for main.py refactor
        return self.pre_access_audit(agent_id, action, context)
