import json
import time
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
    Consumes audit events from Redpanda and takes remediation actions.
    """
    def __init__(self):
        self.bus = EventBus()
        self.trust_manager = IdentityTrustManager()
        self.secrets = SecretKernel()
        # Initialize Slack for notifications
        slack_token = self.secrets.get_secret("urn:agnxxt:secret:slack-token")
        self.notifier = SlackAdapter(slack_token) if slack_token else None

    def run(self):
        """
        Main Loop: Consumes from 'kernel.audit.v1'
        (In this prototype, we simulate the consumer logic)
        """
        print("Watchdog Responder Online. Monitoring for violations...")
        while True:
            # Simulation: In production, this would be: 
            # for msg in consumer: self.process_event(msg)
            time.sleep(10)

    def process_violation(self, agent_id: str, action_id: str, reason: str, severity: str = "HIGH"):
        """
        Takes automated action when a violation is detected.
        """
        print(f"!!! CRITICAL VIOLATION DETECTED: Agent {agent_id} | Reason: {reason}")

        # 1. Lower Trust Score Immediately
        impact = 0.5 if severity == "HIGH" else 0.1
        self.trust_manager.update_trust(agent_id, outcome="betrayal", impact=impact)

        # 2. Lifecycle Suspension (Postgres)
        if severity == "HIGH":
            self._suspend_agent(agent_id)

        # 3. Notify Admin (Slack)
        if self.notifier:
            message = f"🚨 *KERNEL SECURITY ALERT* 🚨\n*Agent:* {agent_id}\n*Action:* {action_id}\n*Violation:* {reason}\n*Auto-Remediation:* Lifecycle Suspended."
            self.notifier.send_message(channel="security-alerts", text=message)

        # 4. Broadcast 'Rogue Alert' Gossip (Redpanda)
        self.bus.publish("kernel.gossip.v1", {
            "type": "ROGUE_ALERT",
            "agent_id": agent_id,
            "reason": reason,
            "action_id": action_id
        })

    def _suspend_agent(self, agent_id: str):
        """
        Updates the agent's lifecycle state to 'suspended' in the registry.
        """
        with SessionLocal() as session:
            # Find the artifact for this agent
            agent_record = session.query(RuntimeArtifact).filter_by(artifact_id=agent_id).first()
            if agent_record:
                agent_record.lifecycle_state = "suspended"
                session.commit()
                print(f"Agent {agent_id} has been SUSPENDED in registry.")

if __name__ == "__main__":
    responder = WatchdogResponder()
    responder.run()
