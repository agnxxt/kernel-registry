from typing import Dict, Any, List
from datetime import datetime
from kernel_engine.authz_caas.policy_engine import PolicyEngine
from kernel_engine.authz_caas.intent_registry import IntentRegistry
from kernel_engine.authz_caas.cot_auditor import CoTAuditor
from kernel_engine.authz_caas.drift_scorer import DriftScorer
from persistence.db import SessionLocal
from persistence.models.identity import CanonicalIdentity

class CaasGateway:
    """
    Continuous Autonomous Authorization System (CAAS).
    Provides real-time, zero-trust authorization with CIAM and Time-Bound Grants.
    """
    def __init__(self):
        self.policies = PolicyEngine()
        self.intent_registry = IntentRegistry()
        self.cot_auditor = CoTAuditor()
        self.drift_scorer = DriftScorer()

    def authorize_action(self, agent_id: str, action: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Performs multi-layer authorization with Temporal and CIAM checks.
        """
        # 0. Federated CIAM Check
        with SessionLocal() as session:
            identity = session.query(CanonicalIdentity).filter_by(canonical_id=agent_id).first()
            if not identity:
                 return {"authorized": False, "reason": "Sovereignty Error: Agent identity not registered."}
            
            # A. Temporal Validation (Time-Bound Access)
            now = datetime.utcnow()
            if identity.grant_expires_at and now > identity.grant_expires_at:
                return {"authorized": False, "reason": "Grant Expired: Access has been revoked automatically."}
            
            if identity.grant_start_at and now < identity.grant_start_at:
                return {"authorized": False, "reason": "Grant Pending: Access not yet active."}

            # B. Sponsorship / Accountability Validation
            context["agent_domain"] = identity.domain
            context["has_sponsor"] = identity.sponsor_id is not None
            if identity.domain in ["EXTERNAL", "VENDOR", "CUSTOMER"] and not identity.sponsor_id:
                return {"authorized": False, "reason": f"CIAM Violation: {identity.domain} agent lacks an internal sponsor/handshake."}

            # C. Consent Validation
            context["consent_scopes"] = identity.consent_metadata.get("scopes", []) if identity.consent_metadata else []

        # 1. Intent Validation
        intent_result = self.intent_registry.validate_intent(agent_id, action)
        if not intent_result["valid"]:
            return {"authorized": False, "reason": "Intent Registry: Task not approved."}

        # 2. Drift Analysis
        drift_score = self.drift_scorer.calculate_drift(agent_id, action)
        context["drift_score"] = drift_score

        # 3. Policy Check (OPA + OpenFGA)
        policy_result = self.policies.evaluate_action(agent_id, action, context)
        
        return {
            "authorized": policy_result["allowed"],
            "reason": policy_result.get("reason", "Approved"),
            "domain": identity.domain,
            "expires_at": identity.grant_expires_at.isoformat() if identity.grant_expires_at else None,
            "policy_id": policy_result.get("policy_id")
        }

    def audit_reasoning(self, agent_id: str, reasoning: str) -> Dict[str, Any]:
        return self.cot_auditor.audit_reasoning(agent_id, reasoning)
