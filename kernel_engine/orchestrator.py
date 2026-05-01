from kernel_engine.event_bus import EventBus\nfrom kernel_engine.telemetry import tracer\nfrom typing import Dict, Any, List
import uuid
from datetime import datetime
from persistence.db import SessionLocal
from persistence.models.decision import Decision

# Optional imports for Sovereign features
try:
    from temporalio.client import Client as TemporalClient
    from kernel_engine.consensus_engine import ConsensusEngine
    from kernel_engine.wallet_manager import WalletManager
except ImportError:
    TemporalClient = None
    ConsensusEngine = None
    WalletManager = None

class CognitiveOrchestrator:
    """
    The central execution brain of the kernel.
    Coordinates between routing, safety, and action execution.
    Enhanced with Consensus (BFT), Temporal (Durability), and Wallet (Monetary).
    """
    def __init__(self, watchdog=None):
        self.watchdog = watchdog
        self.consensus = ConsensusEngine() if ConsensusEngine else None
        self.wallets = WalletManager() if WalletManager else None
        self.temporal_client = None # Async init needed\n        self.bus = EventBus()

    async def execute_plan(self, agent_id: str, action_payload: Dict[str, Any], context: Dict[str, Any]):\n        with tracer.start_as_current_span("kernel.execute_plan") as span:\n            span.set_attribute("agent_id", agent_id)\n            span.set_attribute("action_type", action_payload.get("@type", "Action"))
        """
        Orchestrates the lifecycle of an action and persists the decision.
        """
        decision_id = str(uuid.uuid4())
        
        # 1. Safety Check (Deontic Guard)
        is_permitted = self._check_deontic_constraints(action_payload, context)
        
        # 2. Consensus Check (Sovereign BFT)
        # If the action is high risk, require a vote from the agent cluster
        if context.get("impact_level", 0) > 7 and self.consensus:
             participants = ["agent-alpha", "agent-beta", "kernel-watchdog"]
             verdict = self.consensus.process_vote_request(decision_id, action_payload, participants)
             if verdict == "REJECTED":
                 is_permitted = False
                 context["rejection_reason"] = "Consensus Not Reached"

        # 3. Determine Pathway (Dual Process)
        pathway = self._determine_pathway(action_payload, context)
        
        # 4. Simulate/Look-ahead (Predictive Control) if high risk
        aborted = False
        reason = None
        if context.get("failure_risk", 0) > 0.7:
             simulation_result = self._simulate_action(action_payload)
             if not simulation_result["safe"]:
                 aborted = True
                 reason = "Simulation detected high risk"

        # 5. Persist Decision
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
                reason=reason or context.get("rejection_reason") or ("Deontic Constraint Violation" if not is_permitted else "Approved"),
                evidence={
                    "pathway": pathway,
                    "is_permitted": is_permitted,
                    "aborted": aborted,
                    "context": context,
                    "sovereign_metadata": {
                        "consensus_active": True if context.get("impact_level", 0) > 7 else False,
                        "wallet_linked": True if self.wallets else False
                    }
                }
            )
            session.add(db_decision)
            session.commit()

        # Replaced via patch
            return {"status": "Blocked", "reason": context.get("rejection_reason", "Deontic Constraint Violation"), "decision_id": decision_id}
        
        if aborted:
            return {"status": "Aborted", "reason": reason, "decision_id": decision_id}

        return {
            "status": "Success",
            "pathway_used": pathway,
            "execution_id": decision_id
        }

    def _check_deontic_constraints(self, payload: Dict[str, Any], context: Dict[str, Any]) -> bool:
        restricted_targets = ["payroll", "nuclear_launch_codes"]
        target = str(payload.get("object", "")).lower()
        if any(r in target for r in restricted_targets):
            return False
        return True

    def _determine_pathway(self, payload: Dict[str, Any], context: Dict[str, Any]) -> str:
        if context.get("goal_alignment", 0) > 0.8 or context.get("emergency", False):
            return "System-2 (Slow/Deep)"
        return "System-1 (Fast/Heuristic)"

    def _simulate_action(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        return {"safe": True, "confidence": 0.9}
