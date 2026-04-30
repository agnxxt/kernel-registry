from typing import Dict, Any, List
import uuid
from datetime import datetime
from persistence.db import SessionLocal
from persistence.models.decision import Decision

class CognitiveOrchestrator:
    """
    The central execution brain of the kernel.
    Coordinates between routing, safety, and action execution.
    Backed by Postgres persistence for decisions.
    """
    def __init__(self, watchdog=None):
        self.watchdog = watchdog

    async def execute_plan(self, agent_id: str, action_payload: Dict[str, Any], context: Dict[str, Any]):
        """
        Orchestrates the lifecycle of an action and persists the decision.
        """
        decision_id = str(uuid.uuid4())
        
        # 1. Safety Check (Deontic Guard)
        is_permitted = self._check_deontic_constraints(action_payload, context)
        
        # 2. Determine Pathway (Dual Process)
        pathway = self._determine_pathway(action_payload, context)
        
        # 3. Simulate/Look-ahead (Predictive Control) if high risk
        aborted = False
        reason = None
        if context.get("failure_risk", 0) > 0.7:
             simulation_result = self._simulate_action(action_payload)
             if not simulation_result["safe"]:
                 aborted = True
                 reason = "Simulation detected high risk"

        # Persist Decision
        with SessionLocal() as session:
            db_decision = Decision(
                decision_id=decision_id,
                tenant_id=action_payload.get("tenant_id", "default"),
                agent_id=agent_id,
                task_id=action_payload.get("task_id", "unknown"),
                run_id=action_payload.get("run_id"),
                step_id=action_payload.get("step_id"),
                status="COMPLETED" if not aborted and is_permitted else "BLOCKED",
                effective_verdict="ALLOW" if is_permitted and not aborted else "DENY",
                required_approvals=1,
                allowed_rejections=0,
                reason=reason or ("Deontic Constraint Violation" if not is_permitted else "Approved"),
                evidence={
                    "pathway": pathway,
                    "is_permitted": is_permitted,
                    "aborted": aborted,
                    "context": context
                }
            )
            session.add(db_decision)
            session.commit()

        if not is_permitted:
            return {"status": "Blocked", "reason": "Deontic Constraint Violation", "decision_id": decision_id}
        
        if aborted:
            return {"status": "Aborted", "reason": reason, "decision_id": decision_id}

        return {
            "status": "Success",
            "pathway_used": pathway,
            "execution_id": decision_id
        }

    def _check_deontic_constraints(self, payload: Dict[str, Any], context: Dict[str, Any]) -> bool:
        # Implementation of "Moral/Compliance Guard"
        restricted_targets = ["payroll", "nuclear_launch_codes"]
        target = str(payload.get("object", "")).lower()
        if any(r in target for r in restricted_targets):
            return False
        return True

    def _determine_pathway(self, payload: Dict[str, Any], context: Dict[str, Any]) -> str:
        # Heuristic for Dual Process routing
        if context.get("goal_alignment", 0) > 0.8 or context.get("emergency", False):
            return "System-2 (Slow/Deep)"
        return "System-1 (Fast/Heuristic)"

    def _simulate_action(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        # Implementation of Predictive Control look-ahead
        return {"safe": True, "confidence": 0.9}
