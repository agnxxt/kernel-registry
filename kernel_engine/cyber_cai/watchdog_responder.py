import json
import os
from typing import Dict, Any
from kernel_engine.event_bus import EventBus
from kernel_engine.identity import IdentityTrustManager
from kernel_engine.adapters.slack_adapter import SlackAdapter
from kernel_engine.secret_kernel import SecretKernel
from persistence.db import SessionLocal
from persistence.models.artifact import RuntimeArtifact

class WatchdogResponder:
    """
    The 'Active' part of the immune system.
    Consumes audit events from Redpanda and takes real-time remediation actions.
    """
    def __init__(self):
        self.bus = EventBus(group_id="watchdog-responder")
        self.trust_manager = IdentityTrustManager()
        self.secrets = SecretKernel()
        slack_token = self.secrets.get_secret("urn:agnxxt:secret:slack-token")
        self.notifier = SlackAdapter(slack_token) if slack_token else None

    def run(self):
        """
        Subscribes to audit and drift topics.
        """
        topics = ["kernel.audit.v1", "cognitive.drift.events"]
        self.bus.listen(topics, self.on_event)

    def on_event(self, topic: str, payload: Dict[str, Any]):
        """
        Callback for incoming bus events.
        """
        event_type = payload.get("event_type", "UNKNOWN")
        agent_id = payload.get("agent_id")
        
        if event_type == "POLICY_VIOLATION" or payload.get("verdict") == "BLOCK":
            self.process_violation(
                agent_id=agent_id,
                action_id=payload.get("action_id", "N/A"),
                reason=payload.get("reason", "Deontic Violation detected by bus."),
                severity="HIGH"
            )

    def process_violation(self, agent_id: str, action_id: str, reason: str, severity: str = "HIGH"):
        print(f"!!! CRITICAL VIOLATION: {agent_id} | {reason}")

        # 1. Lower Trust
        self.trust_manager.update_trust(agent_id, outcome="betrayal", impact=0.5)

        # 2. Suspend Agent in Registry
        self._suspend_agent(agent_id)

        # 3. Notify Slack
        if self.notifier:
            self.notifier.send_message(
                channel="security-alerts", 
                text=f"WATCHDOG ACTION: Agent {agent_id} SUSPENDED. Reason: {reason}"
            )

    def _suspend_agent(self, agent_id: str):
        with SessionLocal() as session:
            agent = session.query(RuntimeArtifact).filter_by(artifact_id=agent_id).first()
            if agent:
                agent.lifecycle_state = "SUSPENDED"
                session.commit()

if __name__ == "__main__":
    responder = WatchdogResponder()
    responder.run()
