from typing import Dict, Any, List
from kernel_engine.authz_caas.policy_engine import PolicyEngine
from kernel_engine.authz_caas.intent_registry import IntentRegistry
from kernel_engine.authz_caas.cot_auditor import CoTAuditor
from kernel_engine.authz_caas.drift_scorer import DriftScorer
from persistence.db import SessionLocal
from persistence.models.identity import CanonicalIdentity

class CaasGateway:
    """
    Continuous Autonomous Authorization System (CAAS).
    Provides real-time, zero-trust authorization with Federated Sponsorship.
    """
    def __init__(self):
        self.policies = PolicyEngine()
        self.intent_registry = IntentRegistry()
        self.cot_auditor = CoTAuditor()
        self.drift_scorer = DriftScorer()

    def authorize_action(self, agent_id: str, action: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Performs multi-layer authorization with Sponsorship checks.
        """
        # 0. Federated Sponsorship Check
        with SessionLocal() as session:
            identity = session.query(CanonicalIdentity).filter_by(canonical_id=agent_id).first()
            if not identity:
                 return {"authorized": False, "reason": "Sovereignty Error: Agent identity not registered."}
            
            # Enrich context with sponsorship data
            context["agent_domain"] = identity.domain
            context["has_sponsor"] = identity.sponsor_id is not None
            
            # Rule: External/Vendor agents MUST have an internal sponsor
            if identity.domain in ["EXTERNAL", "VENDOR"] and not identity.sponsor_id:
                return {"authorized": False, "reason": f"Governance Violation: {identity.domain} agent lacks an internal sponsor."}

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
            "drift_score": drift_score,
            "policy_id": policy_result.get("policy_id")
        }

    def audit_reasoning(self, agent_id: str, reasoning: str) -> Dict[str, Any]:
        return self.cot_auditor.audit_reasoning(agent_id, reasoning)
